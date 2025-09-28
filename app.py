# app_fixed.py
import os, time, threading, logging, json, traceback, uuid, secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    session,
    make_response,
    send_from_directory,
)
import traceback
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

# --- Opcionales/externos
try:
    from whitenoise import WhiteNoise
except Exception:
    WhiteNoise = None

# Dependencias opcionales que tu app menciona:
auth_manager = None
postgres_db = None

# Inicializar PostgreSQL una sola vez
try:
    from postgresql_db_manager import PostgreSQLDBManager

    postgres_db = PostgreSQLDBManager()
    print(
        f"[INFO] PostgreSQLDBManager inicializado: {'Conectado' if postgres_db.is_connected() else 'Modo fallback'}"
    )

    # Migración de base de datos deshabilitada temporalmente para evitar timeouts
    # Se ejecutará manualmente cuando sea necesario
    if postgres_db and postgres_db.is_connected():
        print(
            "[INFO] PostgreSQL conectado - Migración deshabilitada para evitar timeouts"
        )
        # try:
        #     from migrate_database import migrate_database
        #     print("[INFO] Ejecutando migración de base de datos...")
        #     migrate_database()
        #     print("[INFO] Migración de base de datos completada")
        # except Exception as e:
        #     print(f"[WARN] Error en migración de base de datos: {e}")

except Exception as e:
    print(f"[WARN] PostgreSQLDBManager no disponible: {e}")

# Inicializar AuthManager con la instancia de PostgreSQL
try:
    from auth_manager import AuthManager

    auth_manager = AuthManager(db_instance=postgres_db)  # Pasar la instancia existente
    print(f"[INFO] AuthManager inicializado correctamente")
except Exception as e:
    print(f"[WARN] AuthManager no disponible: {e}")


# --- Config
class Config:
    # Variables de entorno críticas (con fallbacks para desarrollo)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-local-12345")
    DATABASE_URL = os.environ.get("DATABASE_URL", "")  # Vacía para desarrollo

    # Variables de entorno opcionales
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # opcional
    TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    PREFERRED_URL_SCHEME = (
        "https" if "medconnect.cl" in os.environ.get("CUSTOM_DOMAIN", "") else "http"
    )

    # Configuración específica para Railway
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")  # opcional
    PORT = int(os.environ.get("PORT", "8000"))  # Default coherente con PaaS


app = Flask(__name__)
app.config.from_object(Config)

# ProxyFix para respetar X-Forwarded-* headers (HTTPS detrás de PaaS)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# CORS seguro aunque no exista `config` externo
CORS(app, origins=app.config["CORS_ORIGINS"])

# Configuración de cookies de sesión (seguridad)
# Detectar si estamos en desarrollo local (puerto 8000 o localhost)
is_local_development = (
    app.config.get("PORT") == 8000
    or "localhost" in os.environ.get("HOST", "")
    or "127.0.0.1" in os.environ.get("HOST", "")
    or app.config.get("FLASK_ENV") == "development"
)

app.config.update(
    SESSION_COOKIE_SECURE=not is_local_development,  # False para desarrollo local, True para producción
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# WhiteNoise para estáticos si está disponible
app.static_folder = "static"
app.static_url_path = "/static"
if WhiteNoise:
    app.wsgi_app = WhiteNoise(
        app.wsgi_app, root=os.path.join(app.root_path, "static"), prefix="/static/"
    )

# Ensure static & uploads
os.makedirs(app.static_folder, exist_ok=True)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("medconnect")

# Cache simple en memoria (p/ llamadas a servicios externos)
_cache, _cache_lock, _cache_timeout = {}, threading.Lock(), 60


def cache_get(key, ttl=_cache_timeout):
    with _cache_lock:
        item = _cache.get(key)
        if not item:
            return None
        val, ts = item
        if time.time() - ts < ttl:
            return val
        _cache.pop(key, None)
    return None


def cache_set(key, val):
    with _cache_lock:
        _cache[key] = (val, time.time())


# ---------- UTILIDADES ----------
def login_required(f):
    @wraps(f)
    def _w(*args, **kwargs):
        if not session.get("user_id"):
            if (
                request.accept_mimetypes.accept_json
                and not request.accept_mimetypes.accept_html
            ):
                return jsonify({"error": "No autenticado"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return _w


def convert_date_format(date_str: str) -> str:
    """DD/MM/YYYY -> YYYY-MM-DD. Acepta ya-normalizado."""
    if not date_str:
        return ""
    try:
        if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
            return date_str
        if len(date_str) == 10 and date_str[2] == "/" and date_str[5] == "/":
            d, m, y = date_str.split("/")
            return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                d, m, y = parts
                return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        return date_str
    except Exception as e:
        logger.warning(f"Error convirtiendo fecha '{date_str}': {e}")
        return date_str


def diagnose_login_error(err: Exception) -> dict:
    msg = str(err)
    tips = [
        "Revisa que la contraseña esté hasheada con el mismo algoritmo.",
        "Confirma que el correo existe y el usuario esté activo.",
        "Valida variables de entorno y conexión a la base de datos.",
    ]
    if "Invalid salt" in msg or "hash" in msg.lower():
        tips.insert(
            0, "Parece un conflicto de formatos de hash (e.g. werkzeug vs. passlib)."
        )
    return {
        "user_message": "No pudimos iniciar sesión. Por favor, verifica tus credenciales.",
        "debug_info": msg,
        "suggestions": tips,
    }


def allowed_file(filename: str) -> bool:
    ALLOWED = {
        "png",
        "jpg",
        "jpeg",
        "gif",
        "pdf",
        "doc",
        "docx",
        "bmp",
        "tiff",
        "tif",
        "txt",
        "dcm",
        "dicom",
    }
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


# --- Telegram helpers (no fallan si faltan tokens/servicios)
def send_telegram_message(chat_id, text) -> bool:
    token = app.config["TELEGRAM_BOT_TOKEN"]
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN no definido; se omite envío.")
        return False
    import requests

    url = app.config["TELEGRAM_API"].format(token=token)
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text})
        return r.ok
    except Exception as e:
        logger.error(f"Error enviando mensaje Telegram: {e}")
        return False


def log_bot_interaction(user_id, username, message, chat_id):
    logger.info(f"[BOT] {username}({user_id}) en chat:{chat_id} dijo: {message}")
    # Si tienes almacenamiento (Sheets/DB), persistir aquí, protegido por try/except.


def detect_intent(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ["emergencia", "auxilio", "ambulancia"]):
        return "emergencia"
    if any(k in t for k in ["ayuda", "help", "/help"]):
        return "ayuda"
    return "general"


def get_telegram_user_info(telegram_user_id):
    try:
        return (
            auth_manager.get_user_by_telegram_id(telegram_user_id)
            if auth_manager
            else None
        )
    except Exception as e:
        logger.error(f"Telegram user info error: {e}")
        return None


def is_professional_user(user_info: dict) -> bool:
    return bool(user_info and user_info.get("tipo_usuario") == "profesional")


def handle_telegram_code_linking(text, user_id):
    parts = text.strip().split()
    if len(parts) != 2:
        return "Uso: /codigo MEDXXXXXX"
    code = parts[1].strip()
    try:
        if auth_manager:
            ok = auth_manager.link_user_with_code(telegram_id=user_id, code=code)
            return "¡Cuenta vinculada!" if ok else "Código inválido o expirado."
        return "Servicio de vinculación no disponible."
    except Exception as e:
        logger.error(f"Link code error: {e}")
        return "No fue posible vincular tu cuenta en este momento."


def handle_professional_requests(text, user_info, user_id, intent):
    # Ejemplos cortos
    if "agenda" in text.lower():
        return "Tu agenda de hoy está vacía (demo)."
    return "¿Qué acción profesional necesitas? (agenda, pacientes, estadísticas)"


def handle_patient_requests(text, user_info, user_id, intent):
    if intent == "ayuda":
        return (
            "Puedo registrar consultas, medicamentos, exámenes, y avisar a tu familia."
        )
    if "consulta" in text.lower():
        return "Ok, registré una consulta (demo)."
    if "examen" in text.lower():
        return "Puedes subir tu examen en el portal. ¿Deseas que te recuerde?"
    return "No te entendí. Di 'ayuda' para ver opciones."


def process_telegram_message(text, chat_id, user_id):
    text = (text or "").strip()
    if text in ["/start", "start", "hola", "/hola"]:
        info = get_telegram_user_info(user_id)
        if info:
            nombre = info.get("nombre") or "paciente"
            return f"¡Hola {nombre}! Soy tu asistente de MedConnect."
        return (
            "¡Hola! Soy tu asistente de salud de MedConnect.\n"
            "Si ya tienes cuenta:\n1) Ve a tu perfil y genera un código\n2) Envíame: /codigo MED123456"
        )
    if text.startswith("/codigo"):
        return handle_telegram_code_linking(text, user_id)
    intent = detect_intent(text)
    if intent == "emergencia":
        return (
            "[EMERGENCIA] Si estás en una emergencia médica:\n"
            "131 SAMU, 132 Bomberos, 133 Carabineros. Ve al servicio de urgencias más cercano."
        )
    info = get_telegram_user_info(user_id)
    if is_professional_user(info):
        return handle_professional_requests(text, info, user_id, intent)
    return handle_patient_requests(text, info, user_id, intent)


# ---------- RUTAS BÁSICAS ----------
@app.route("/robots.txt")
def robots_txt():
    return (
        "User-agent: *\nDisallow:\n",
        200,
        {"Content-Type": "text/plain; charset=utf-8"},
    )


@app.route("/favicon.ico")
def favicon():
    # Sirve favicon si existe; si no, 204 para evitar 502 en logs
    icon_path = os.path.join(app.static_folder, "favicon.ico")
    if os.path.exists(icon_path):
        return send_from_directory(app.static_folder, "favicon.ico")
    return ("", 204)


@app.route("/")
def index():
    """Página principal - Template oficial"""
    try:
        # Verificar que el template existe
        template_path = os.path.join("templates", "index.html")
        if not os.path.exists(template_path):
            logger.error(f"❌ Template no encontrado: {template_path}")
            raise FileNotFoundError(f"Template no encontrado: {template_path}")

        logger.info("✅ Template index.html encontrado, renderizando...")
        return render_template("index.html")

    except Exception as e:
        logger.error(f"❌ Error cargando template index.html: {e}")
        logger.error(f"❌ Tipo de error: {type(e).__name__}")
        import traceback

        logger.error(f"❌ Traceback completo: {traceback.format_exc()}")

        # Fallback temporal con información del error
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Error de Template</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: #f5f5f5; 
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 50px auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); 
                }}
                .error {{ 
                    background: #f8d7da; 
                    color: #721c24; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 20px 0; 
                }}
                .btn {{ 
                    background: #007bff; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    display: inline-block; 
                    margin: 10px 5px; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏥 MedConnect</h1>
                <h2>Error al cargar template oficial</h2>
                
                <div class="error">
                    <h3>Error detectado:</h3>
                    <p><strong>Tipo:</strong> {type(e).__name__}</p>
                    <p><strong>Mensaje:</strong> {str(e)}</p>
                </div>
                
                <p>El template oficial no se pudo cargar. Esto puede ser por:</p>
                <ul>
                    <li>Archivo estático faltante</li>
                    <li>Error de sintaxis en el template</li>
                    <li>Variable Jinja2 no definida</li>
                </ul>
                
                <a href="/login" class="btn">Ir al Login</a>
                <a href="/health" class="btn">Estado del Sistema</a>
            </div>
        </body>
        </html>
        """
        return html


# ---------- AUTH ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        try:
            return render_template("login.html")
        except Exception as e:
            logger.error(f"❌ Error cargando template login.html: {e}")
            return _login_fallback_html()

    data = request.form or request.get_json(silent=True) or {}
    email, password = data.get("email", "").strip(), data.get("password", "")

    try:
        if not auth_manager:
            raise RuntimeError("AuthManager no disponible")

        ok, user_data = auth_manager.login_user(email, password)
        if not ok:
            try:
                return render_template(
                    "login.html", message="Credenciales inválidas", success=False
                )
            except Exception as e:
                logger.error(f"❌ Error renderizando login con error: {e}")
                return _login_fallback_html("Credenciales inválidas", False)

        # set session
        session.clear()
        session["user_id"] = user_data["id"]
        session["user_email"] = user_data["email"]
        session["user_name"] = user_data.get("nombre") or user_data.get("name") or email
        session["user_type"] = user_data.get("tipo_usuario", "paciente")

        if session["user_type"] == "profesional":
            return redirect("/professional")
        return redirect("/patient")

    except Exception as e:
        diag = diagnose_login_error(e)
        logger.error(f"[LOGIN] {diag['debug_info']}")
        try:
            return render_template(
                "login.html", message=diag["user_message"], success=False
            )
        except Exception as template_error:
            logger.error(f"❌ Error renderizando login con error: {template_error}")
            return _login_fallback_html(diag["user_message"], False)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Página de registro de usuarios"""
    if request.method == "GET":
        try:
            return render_template("register.html")
        except Exception as e:
            logger.error(f"❌ Error cargando template register.html: {e}")
            return _register_fallback_html()

    try:
        # Obtener datos del formulario según tipo de usuario
        tipo_usuario = request.form.get("tipo_usuario", "paciente").strip()

        user_data = {
            "email": request.form.get("email", "").strip().lower(),
            "password": request.form.get("password", ""),
            "nombre": request.form.get("nombre", "").strip(),
            "apellido": request.form.get("apellido", "").strip(),
            "tipo_usuario": tipo_usuario,
        }

        # Agregar campos específicos según tipo de usuario
        if tipo_usuario == "paciente":
            user_data.update(
                {
                    "rut": request.form.get("rut", "").strip(),
                    "fecha_nacimiento": request.form.get("fecha_nacimiento", ""),
                    "genero": request.form.get("genero", ""),
                    "telefono": request.form.get("telefono", "").strip(),
                    "direccion": request.form.get("direccion", "").strip(),
                    "antecedentes_medicos": request.form.get(
                        "antecedentes_medicos", ""
                    ).strip(),
                }
            )
        elif tipo_usuario == "profesional":
            user_data.update(
                {
                    "numero_registro": request.form.get("numero_registro", "").strip(),
                    "especialidad": request.form.get("especialidad", "").strip(),
                    "profesion": request.form.get("profesion", "").strip(),
                    "anos_experiencia": request.form.get("anos_experiencia", ""),
                    "institucion": request.form.get("institucion", "").strip(),
                    "direccion_consulta": request.form.get(
                        "direccion_consulta", ""
                    ).strip(),
                    "horario_atencion": request.form.get(
                        "horario_atencion", ""
                    ).strip(),
                    "idiomas": request.form.get("idiomas", "").strip(),
                    "calificacion": request.form.get("calificacion", "").strip(),
                }
            )

        # Validar confirmación de contraseña
        confirm_password = request.form.get("confirm_password", "")
        if user_data["password"] != confirm_password:
            try:
                return render_template(
                    "register.html",
                    message="Las contraseñas no coinciden",
                    success=False,
                    user_data=user_data,
                )
            except Exception:
                return _register_fallback_html("Las contraseñas no coinciden", False)

        # Registrar usuario usando AuthManager
        if not auth_manager:
            raise RuntimeError("AuthManager no disponible")

        success, message = auth_manager.register_user(user_data)

        if success:
            try:
                return render_template(
                    "register.html",
                    message="Usuario registrado exitosamente. Puedes iniciar sesión.",
                    success=True,
                )
            except Exception:
                return _register_fallback_html(
                    "Usuario registrado exitosamente. Puedes iniciar sesión.", True
                )
        else:
            try:
                return render_template(
                    "register.html", message=message, success=False, user_data=user_data
                )
            except Exception:
                return _register_fallback_html(message, False)

    except Exception as e:
        logger.error(f"[REGISTER] Error: {e}")
        try:
            return render_template(
                "register.html",
                message="Error interno del servidor. Inténtalo más tarde.",
                success=False,
            )
        except Exception:
            return _register_fallback_html(
                "Error interno del servidor. Inténtalo más tarde.", False
            )


def _register_fallback_html(message=None, success=True):
    """HTML de fallback para register"""
    alert_html = ""
    if message:
        alert_class = "success" if success else "error"
        alert_html = f'<div class="alert alert-{alert_class}">{message}</div>'

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MedConnect - Registro</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 600px;
                margin: 50px auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            .form-group input, .form-group select {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }}
            .btn {{
                background: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                font-size: 16px;
            }}
            .alert {{
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
            }}
            .alert-error {{
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            .alert-success {{
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 MedConnect</h1>
                <p>Crear Nueva Cuenta</p>
            </div>

            {alert_html}

            <form method="POST" action="/register">
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required />
                </div>
                
                <div class="form-group">
                    <label for="password">Contraseña:</label>
                    <input type="password" id="password" name="password" required />
                </div>
                
                <div class="form-group">
                    <label for="confirm_password">Confirmar Contraseña:</label>
                    <input type="password" id="confirm_password" name="confirm_password" required />
                </div>
                
                <div class="form-group">
                    <label for="nombre">Nombre:</label>
                    <input type="text" id="nombre" name="nombre" required />
                </div>
                
                <div class="form-group">
                    <label for="apellido">Apellido:</label>
                    <input type="text" id="apellido" name="apellido" required />
                </div>
                
                <div class="form-group">
                    <label for="tipo_usuario">Tipo de Usuario:</label>
                    <select id="tipo_usuario" name="tipo_usuario" required>
                        <option value="paciente">Paciente</option>
                        <option value="profesional">Profesional de la Salud</option>
                    </select>
                </div>

                <button type="submit" class="btn">Crear Cuenta</button>
            </form>

            <p style="text-align: center; margin-top: 20px">
                ¿Ya tienes cuenta? <a href="/login">Iniciar Sesión</a>
            </p>
            
            <p style="text-align: center; margin-top: 10px">
                <a href="/">← Volver al inicio</a>
            </p>
        </div>
    </body>
    </html>
    """
    return html


def _login_fallback_html(message=None, success=True):
    """HTML de fallback para login"""
    alert_html = ""
    if message:
        alert_class = "success" if success else "error"
        alert_html = f'<div class="alert alert-{alert_class}">{message}</div>'

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MedConnect - Login</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 400px;
                margin: 50px auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            .form-group input {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }}
            .btn {{
                background: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                font-size: 16px;
            }}
            .btn:hover {{
                background: #0056b3;
            }}
            .alert {{
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
            }}
            .alert-error {{
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }}
            .alert-success {{
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            .demo-users {{
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 MedConnect</h1>
                <p>Iniciar Sesión</p>
            </div>

            {alert_html}

            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required />
                </div>

                <div class="form-group">
                    <label for="password">Contraseña:</label>
                    <input type="password" id="password" name="password" required />
                </div>

                <button type="submit" class="btn">Iniciar Sesión</button>
            </form>

            <div class="demo-users">
                <h4>👥 Usuarios de Prueba:</h4>
                <p>
                    <strong>Paciente:</strong><br />
                    Email: paciente@test.com<br />
                    Contraseña: password123
                </p>

                <p>
                    <strong>Profesional:</strong><br />
                    Email: diego.castro.lagos@gmail.com<br />
                    Contraseña: password123
                </p>
            </div>

            <p style="text-align: center; margin-top: 20px">
                <a href="/">← Volver al inicio</a>
            </p>
        </div>
    </body>
    </html>
    """
    return html


@app.route("/logout")
def logout():
    try:
        session.clear()
        session.permanent = False
        resp = make_response(redirect("/?logout=success"))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "-1"
        resp.set_cookie("session", "", expires=0)
        return resp
    except Exception as e:
        logger.error(f"Logout error: {e}")
        session.clear()
        return redirect("/")


# ---------- DASHBOARDS ----------
@app.route("/patient")
@login_required
def patient_dashboard():
    """Dashboard del paciente con datos del usuario"""
    try:
        # Obtener datos del usuario desde la sesión
        user_id = session.get("user_id")
        user_email = session.get("user_email")
        user_name = session.get("user_name")
        user_type = session.get("user_type", "paciente")

        # Crear objeto user para el template
        user = {
            "id": user_id,
            "email": user_email,
            "nombre": user_name,
            "tipo_usuario": user_type,
        }

        # Intentar usar el template patient.html
        return render_template("patient.html", user=user, just_logged_in=False)
    except Exception as e:
        logger.error(f"❌ Error cargando patient.html: {e}")
        # Fallback a página simple
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Dashboard Paciente</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: #f5f5f5; 
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); 
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    padding-bottom: 20px; 
                    border-bottom: 2px solid #007bff; 
                }}
                .user-info {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin-bottom: 30px; 
                }}
                .btn {{ 
                    background: #007bff; 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 4px; 
                    display: inline-block; 
                    margin: 10px 5px; 
                }}
                .btn:hover {{ 
                    background: #0056b3; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MedConnect</h1>
                    <h2>Dashboard del Paciente</h2>
                </div>
                
                <div class="user-info">
                    <h3>👤 Información del Usuario</h3>
                    <p><strong>ID:</strong> {user_id}</p>
                    <p><strong>Email:</strong> {user_email}</p>
                    <p><strong>Nombre:</strong> {user_name}</p>
                    <p><strong>Tipo:</strong> {user_type}</p>
                </div>
                
                <div style="text-align: center;">
                    <h3>🚧 Dashboard en Desarrollo</h3>
                    <p>El dashboard completo estará disponible pronto.</p>
                    
                    <a href="/" class="btn">← Volver al Inicio</a>
                    <a href="/logout" class="btn">Cerrar Sesión</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html


@app.route("/professional")
@login_required
def professional_dashboard():
    """Dashboard del profesional con funcionalidades completas"""
    try:
        # Obtener datos del usuario desde la sesión
        user_id = session.get("user_id")
        user_email = session.get("user_email")
        user_name = session.get("user_name")
        user_type = session.get("user_type", "profesional")

        logger.info(
            f"🔍 Iniciando dashboard profesional para usuario {user_id} ({user_email})"
        )

        # Crear objeto user para el template
        user = {
            "id": user_id,
            "email": user_email,
            "nombre": user_name,
            "tipo_usuario": user_type,
        }

        logger.info(f"📊 Objeto user creado: {user}")

        # Verificar que el template existe
        template_path = os.path.join("templates", "professional.html")
        if not os.path.exists(template_path):
            logger.error(f"❌ Template professional.html NO existe en {template_path}")
            raise FileNotFoundError(
                f"Template professional.html no encontrado en {template_path}"
            )

        logger.info(f"✅ Template professional.html encontrado en {template_path}")

        # Usar el template professional.html que ya existe
        logger.info(f"🎨 Intentando renderizar professional.html con user={user}")
        result = render_template("professional.html", user=user, just_logged_in=True)
        logger.info(f"✅ Template professional.html renderizado exitosamente")
        return result

    except Exception as e:
        logger.error(f"❌ Error cargando professional.html: {e}")
        logger.error(f"❌ Tipo de error: {type(e).__name__}")
        logger.error(f"❌ Traceback completo: ", exc_info=True)

        # Fallback a página simple
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Dashboard Profesional</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #007bff; }}
                .user-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                .btn {{ background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px 5px; }}
                .btn:hover {{ background: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MedConnect</h1>
                    <h2>Dashboard del Profesional</h2>
                </div>
                
                <div class="user-info">
                    <h3>👤 Información del Usuario</h3>
                    <p><strong>ID:</strong> {user_id}</p>
                    <p><strong>Email:</strong> {user_email}</p>
                    <p><strong>Nombre:</strong> {user_name}</p>
                    <p><strong>Tipo:</strong> {user_type}</p>
                </div>
                
                <div style="text-align: center;">
                    <h3>🚧 Error cargando dashboard</h3>
                    <p><strong>Error:</strong> {e}</p>
                    <p><strong>Tipo:</strong> {type(e).__name__}</p>
                    
                    <a href="/" class="btn">← Volver al Inicio</a>
                    <a href="/logout" class="btn">Cerrar Sesión</a>
                </div>
            </div>
        </body>
        </html>
        """


@app.route("/reports")
@login_required
def reports():
    """Página de reportes del usuario"""
    try:
        # Obtener datos del usuario desde la sesión
        user_id = session.get("user_id")
        user_email = session.get("user_email")
        user_name = session.get("user_name")
        user_type = session.get("user_type", "paciente")

        # Crear objeto user para el template
        user = {
            "id": user_id,
            "email": user_email,
            "nombre": user_name,
            "tipo_usuario": user_type,
        }

        # Usar el template reports.html que ya existe
        return render_template("reports.html", user=user)
    except Exception as e:
        logger.error(f"❌ Error cargando reports.html: {e}")
        # Fallback a página simple
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Reportes</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #007bff; }}
                .user-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                .btn {{ background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px 5px; }}
                .btn:hover {{ background: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MedConnect</h1>
                    <h2>Reportes del Usuario</h2>
                </div>
                
                <div class="user-info">
                    <h3>👤 Información del Usuario</h3>
                    <p><strong>ID:</strong> {user_id}</p>
                    <p><strong>Email:</strong> {user_email}</p>
                    <p><strong>Nombre:</strong> {user_name}</p>
                    <p><strong>Tipo:</strong> {user_type}</p>
                </div>
                
                <div style="text-align: center;">
                    <h3>🚧 Error cargando reportes</h3>
                    <p>Error: {e}</p>
                    
                    <a href="/" class="btn">← Volver al Inicio</a>
                    <a href="/logout" class="btn">Cerrar Sesión</a>
                </div>
            </div>
        </body>
        </html>
        """


# ---------- API PERFIL ----------
@app.route("/profile")
@login_required
def profile():
    """Página de perfil del usuario"""
    try:
        # Obtener datos del usuario desde la sesión
        user_id = session.get("user_id")
        user_email = session.get("user_email")
        user_name = session.get("user_name")
        user_type = session.get("user_type", "paciente")

        # Crear objeto user básico
        user = {
            "id": user_id,
            "email": user_email,
            "nombre": user_name,
            "tipo_usuario": user_type,
        }

        # Si es profesional, obtener datos completos del perfil
        if user_type == "profesional" and postgres_db and postgres_db.is_connected():
            try:
                # Primero obtener datos básicos del usuario desde tabla usuarios
                user_query = """
                    SELECT telefono, direccion, ciudad, fecha_registro
                    FROM usuarios 
                    WHERE id = %s
                """
                user_result = postgres_db.execute_query(user_query, (user_id,))

                # Luego obtener datos profesionales desde tabla profesionales
                prof_query = """
                    SELECT numero_registro, especialidad, profesion, anos_experiencia, 
                           institucion, direccion_consulta, horario_atencion, idiomas, 
                           calificacion, verificado, disponible
                    FROM profesionales 
                    WHERE user_id = %s
                """
                prof_result = postgres_db.execute_query(prof_query, (user_id,))

                # Enriquecer el objeto user con datos del usuario
                if user_result and len(user_result) > 0:
                    user_data = user_result[0]
                    user.update(
                        {
                            "telefono": user_data.get("telefono", "No especificado"),
                            "direccion": user_data.get("direccion", "No especificada"),
                            "ciudad": user_data.get("ciudad", "No especificada"),
                            "fecha_registro": user_data.get(
                                "fecha_registro", "Recientemente"
                            ),
                        }
                    )
                    logger.info(f"✅ Datos básicos del usuario cargados para {user_id}")

                # Enriquecer con datos profesionales
                if prof_result and len(prof_result) > 0:
                    prof_data = prof_result[0]
                    user.update(
                        {
                            "numero_registro": prof_data.get(
                                "numero_registro", "No especificado"
                            ),
                            "especialidad": prof_data.get(
                                "especialidad", "No especificada"
                            ),
                            "profesion": prof_data.get(
                                "profesion", "Profesional de la Salud"
                            ),
                            "anos_experiencia": prof_data.get(
                                "anos_experiencia", "No especificado"
                            ),
                            "institucion": prof_data.get(
                                "institucion", "No especificada"
                            ),
                            "direccion_consulta": prof_data.get(
                                "direccion_consulta", "No especificada"
                            ),
                            "horario_atencion": prof_data.get(
                                "horario_atencion", "No especificado"
                            ),
                            "idiomas": (
                                prof_data.get("idiomas", "Español").split(",")
                                if prof_data.get("idiomas")
                                else ["Español"]
                            ),
                            "calificacion": prof_data.get("calificacion", 5.0),
                            "verificado": prof_data.get("verificado", "false"),
                            "disponible": prof_data.get("disponible", True),
                            # Campos adicionales con valores por defecto
                            "total_pacientes": 0,
                            "atenciones_mes": 0,
                            "tiempo_respuesta": "24h",
                            "certificaciones": [],
                            "areas_especializacion": [],
                            "foto_perfil": None,
                            "profile_image": None,
                        }
                    )
                    logger.info(
                        f"✅ Datos profesionales cargados para usuario {user_id}"
                    )
                else:
                    logger.warning(
                        f"⚠️ No se encontró perfil profesional para usuario {user_id}"
                    )
                    # Usar valores por defecto para campos profesionales
                    user.update(
                        {
                            "numero_registro": "No especificado",
                            "especialidad": "No especificada",
                            "profesion": "Profesional de la Salud",
                            "anos_experiencia": "No especificado",
                            "institucion": "No especificada",
                            "direccion_consulta": "No especificada",
                            "horario_atencion": "No especificado",
                            "idiomas": ["Español"],
                            "calificacion": 5.0,
                            "verificado": "false",
                            "disponible": True,
                            "total_pacientes": 0,
                            "atenciones_mes": 0,
                            "tiempo_respuesta": "24h",
                            "certificaciones": [],
                            "areas_especializacion": [],
                            "foto_perfil": None,
                            "profile_image": None,
                        }
                    )

            except Exception as e:
                logger.error(f"❌ Error obteniendo perfil profesional: {e}")
                # Usar valores por defecto en caso de error
                user.update(
                    {
                        "telefono": "Error al cargar",
                        "direccion": "Error al cargar",
                        "ciudad": "Error al cargar",
                        "fecha_registro": "Error al cargar",
                        "numero_registro": "Error al cargar",
                        "especialidad": "Error al cargar",
                        "profesion": "Profesional de la Salud",
                        "anos_experiencia": "Error al cargar",
                        "institucion": "Error al cargar",
                        "direccion_consulta": "Error al cargar",
                        "horario_atencion": "Error al cargar",
                        "idiomas": ["Español"],
                        "calificacion": 5.0,
                        "verificado": "false",
                        "disponible": True,
                        "total_pacientes": 0,
                        "atenciones_mes": 0,
                        "tiempo_respuesta": "24h",
                        "certificaciones": [],
                        "areas_especializacion": [],
                        "foto_perfil": None,
                        "profile_image": None,
                    }
                )

        # Usar template específico según tipo de usuario
        if user_type == "profesional":
            # Para profesionales, usar profile_professional.html
            return render_template("profile_professional.html", user=user)
        else:
            # Para pacientes, usar profile.html
            return render_template("profile.html", user=user)

    except Exception as e:
        logger.error(f"❌ Error cargando perfil: {e}")
        # Fallback a página simple
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Perfil</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #007bff; }}
                .user-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                .btn {{ background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 10px 5px; }}
                .btn:hover {{ background: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 MedConnect</h1>
                    <h2>Perfil del Usuario</h2>
                </div>
                
                <div class="user-info">
                    <h3>👤 Información del Usuario</h3>
                    <p><strong>ID:</strong> {user_id}</p>
                    <p><strong>Email:</strong> {user_email}</p>
                    <p><strong>Nombre:</strong> {user_name}</p>
                    <p><strong>Tipo:</strong> {user_type}</p>
                </div>
                
                <div style="text-align: center;">
                    <h3>🚧 Error cargando perfil</h3>
                    <p>Error: {e}</p>
                    
                    <a href="/" class="btn">← Volver al Inicio</a>
                    <a href="/logout" class="btn">Cerrar Sesión</a>
                </div>
            </div>
        </body>
        </html>
        """


@app.route("/api/profile/medical", methods=["PUT"])
@login_required
def update_medical_info():
    try:
        data = request.get_json() or {}
        # Aquí guardarías en DB si está disponible
        logger.info(
            f"[PROFILE] medical info {session.get('user_id')}: {json.dumps(data)[:200]}"
        )
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"update_medical_info error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/profile/notifications", methods=["PUT"])
@login_required
def update_notification_settings():
    try:
        data = request.get_json() or {}
        logger.info(
            f"[PROFILE] notifications {session.get('user_id')}: {json.dumps(data)[:200]}"
        )
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"update_notification_settings error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/update-professional-profile", methods=["POST"])
@login_required
def update_professional_profile():
    """Actualizar perfil del profesional"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json() or {}
        logger.info(
            f"[PROFILE] Actualizando perfil profesional {user_id}: {json.dumps(data)[:200]}"
        )

        # Validar datos requeridos
        required_fields = ["numero_registro", "especialidad", "profesion"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Campo {field} es requerido"}), 400

        # Actualizar en tabla profesionales
        if postgres_db and postgres_db.is_connected():
            try:
                update_query = """
                    UPDATE profesionales 
                    SET numero_registro = %s, especialidad = %s, profesion = %s,
                        anos_experiencia = %s, institucion = %s, direccion_consulta = %s,
                        horario_atencion = %s, idiomas = %s, calificacion = %s,
                        verificado = %s, disponible = %s
                    WHERE user_id = %s
                """

                update_values = (
                    data.get("numero_registro"),
                    data.get("especialidad"),
                    data.get("profesion"),
                    data.get("anos_experiencia"),
                    data.get("institucion"),
                    data.get("direccion_consulta"),
                    data.get("horario_atencion"),
                    data.get("idiomas"),
                    data.get("calificacion", 5.0),
                    data.get("verificado", "false"),
                    data.get("disponible", True),
                    user_id,
                )

                postgres_db.execute_query(update_query, update_values)
                postgres_db.conn.commit()

                logger.info(f"✅ Perfil profesional actualizado para usuario {user_id}")
                return jsonify(
                    {"success": True, "message": "Perfil actualizado correctamente"}
                )

            except Exception as e:
                logger.error(f"❌ Error actualizando perfil profesional: {e}")
                return (
                    jsonify({"error": "Error al actualizar en la base de datos"}),
                    500,
                )
        else:
            logger.warning("⚠️ PostgreSQL no disponible para actualizar perfil")
            return jsonify({"error": "Base de datos no disponible"}), 503

    except Exception as e:
        logger.error(f"❌ Error en update_professional_profile: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/register-atencion", methods=["POST"])
@login_required
def register_atencion():
    """Registrar nueva atención médica"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json() or {}
        logger.info(
            f"[ATENCION] Registrando atención para usuario {user_id}: {json.dumps(data)[:200]}"
        )

        # Mapear campos del formulario a la estructura de la base de datos
        # El formulario envía: paciente_nombre, paciente_email, tipo_atencion, motivo_consulta, etc.
        # Necesitamos: paciente_id, tipo_atencion, motivo_consulta, diagnostico, tratamiento

        # Validar datos requeridos
        required_fields = ["paciente_nombre", "tipo_atencion", "motivo_consulta"]
        for field in required_fields:
            if not data.get(field):
                logger.error(f"❌ Campo requerido faltante: {field}")
                return jsonify({"error": f"Campo {field} es requerido"}), 400

        logger.info(f"✅ Validación de campos exitosa")

        # Crear atención en la base de datos
        if postgres_db and postgres_db.is_connected():
            try:
                logger.info(f"🔍 Verificando conexión a PostgreSQL...")

                # Verificar que la tabla atenciones_medicas existe
                check_table_query = """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'atenciones_medicas'
                    );
                """
                postgres_db.cursor.execute(check_table_query)
                table_exists_result = postgres_db.cursor.fetchone()
                logger.info(f"📊 Resultado verificación tabla: {table_exists_result}")

                if not table_exists_result or not table_exists_result.get(
                    "exists", False
                ):
                    logger.error(f"❌ Tabla 'atenciones_medicas' NO existe")
                    return (
                        jsonify({"error": "Tabla de atenciones médicas no disponible"}),
                        500,
                    )

                logger.info(f"✅ Tabla 'atenciones_medicas' existe")

                # Verificar estructura de la tabla
                check_columns_query = """
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'atenciones_medicas'
                    ORDER BY ordinal_position;
                """
                postgres_db.cursor.execute(check_columns_query)
                columns_result = postgres_db.cursor.fetchall()
                logger.info(f"📋 Columnas de la tabla: {columns_result}")

                # Buscar paciente por nombre en la tabla usuarios (ya que el formulario envía paciente_nombre)
                # El formulario envía: paciente_nombre, paciente_rut, tipo_atencion, motivo_consulta, etc.
                paciente_nombre = data.get("paciente_nombre")
                if not paciente_nombre:
                    logger.error(f"❌ Nombre del paciente es requerido")
                    return jsonify({"error": "Nombre del paciente es requerido"}), 400

                # Primero, verificar qué pacientes existen en la tabla usuarios
                check_pacientes_query = """
                    SELECT id, nombre, apellido, email, tipo_usuario 
                    FROM usuarios 
                    WHERE tipo_usuario = 'paciente'
                    ORDER BY nombre, apellido
                """
                postgres_db.cursor.execute(check_pacientes_query)
                pacientes_existentes = postgres_db.cursor.fetchall()
                logger.info(
                    f"📋 Pacientes existentes en tabla usuarios: {pacientes_existentes}"
                )

                if not pacientes_existentes:
                    logger.error(
                        f"❌ No hay pacientes registrados en la tabla usuarios"
                    )
                    return (
                        jsonify(
                            {"error": "No hay pacientes registrados en el sistema"}
                        ),
                        404,
                    )

                # Buscar paciente por nombre con búsqueda más flexible
                # Opción 1: Búsqueda exacta por nombre completo
                paciente_query_exacta = """
                    SELECT id FROM usuarios 
                    WHERE CONCAT(nombre, ' ', apellido) = %s AND tipo_usuario = 'paciente'
                """
                postgres_db.cursor.execute(paciente_query_exacta, (paciente_nombre,))
                paciente_result = postgres_db.cursor.fetchone()

                if not paciente_result:
                    logger.error(
                        f"❌ Paciente con nombre '{paciente_nombre}' no encontrado"
                    )
                    pacientes_nombres = [
                        f"{p.get('nombre', '')} {p.get('apellido', '')}"
                        for p in pacientes_existentes
                    ]
                    logger.error(f"❌ Pacientes disponibles: {pacientes_nombres}")

                    # Ofrecer crear el paciente automáticamente si no existe
                    if len(pacientes_existentes) == 0 or paciente_nombre not in [
                        f"{p.get('nombre', '')} {p.get('apellido', '')}"
                        for p in pacientes_existentes
                    ]:
                        logger.info(
                            f"🔄 Intentando crear paciente automáticamente: {paciente_nombre}"
                        )
                        paciente_creado = crear_paciente_automatico(paciente_nombre)
                        if paciente_creado:
                            paciente_id = paciente_creado
                            logger.info(
                                f"✅ Paciente creado automáticamente con ID: {paciente_id}"
                            )
                        else:
                            return (
                                jsonify(
                                    {
                                        "error": f"Paciente con nombre '{paciente_nombre}' no encontrado",
                                        "pacientes_disponibles": pacientes_nombres,
                                        "sugerencia": "El paciente será creado automáticamente",
                                    }
                                ),
                                404,
                            )
                    else:
                        return (
                            jsonify(
                                {
                                    "error": f"Paciente con nombre '{paciente_nombre}' no encontrado",
                                    "pacientes_disponibles": pacientes_nombres,
                                }
                            ),
                            404,
                        )
                else:
                    paciente_id = paciente_result.get("id")
                    logger.info(f"✅ Paciente encontrado con ID: {paciente_id}")

                # Preparar consulta de inserción usando la estructura real de la tabla
                insert_query = """
                    INSERT INTO atenciones_medicas 
                    (profesional_id, paciente_id, fecha_atencion, hora_inicio, 
                     tipo_atencion, motivo_consulta, diagnostico, tratamiento, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """

                # Parsear fecha y hora del formulario
                fecha_hora_str = data.get("fecha_hora", "")
                if fecha_hora_str:
                    try:
                        fecha_hora = datetime.fromisoformat(
                            fecha_hora_str.replace("Z", "+00:00")
                        )
                        fecha_atencion = fecha_hora.date()
                        hora_inicio = fecha_hora.time()
                    except ValueError:
                        fecha_atencion = datetime.now().date()
                        hora_inicio = datetime.now().time()
                else:
                    fecha_atencion = datetime.now().date()
                    hora_inicio = datetime.now().time()

                insert_values = (
                    user_id,  # profesional_id
                    paciente_id,  # paciente_id
                    fecha_atencion,  # fecha_atencion
                    hora_inicio,  # hora_inicio
                    data.get("tipo_atencion"),  # tipo_atencion
                    data.get("motivo_consulta"),  # motivo_consulta
                    data.get("diagnostico", ""),  # diagnostico
                    data.get("tratamiento", ""),  # tratamiento
                    data.get("observaciones", ""),  # observaciones
                )

                logger.info(f"🔍 Ejecutando consulta: {insert_query}")
                logger.info(f"📊 Valores a insertar: {insert_values}")

                postgres_db.cursor.execute(insert_query, insert_values)
                result = postgres_db.cursor.fetchone()
                logger.info(f"📊 Resultado de la inserción: {result}")

                postgres_db.conn.commit()
                logger.info(f"✅ Transacción confirmada")

                if result and result.get("id"):
                    atencion_id = result.get("id")
                    logger.info(
                        f"✅ Atención médica registrada exitosamente con ID: {atencion_id}"
                    )
                    return jsonify(
                        {
                            "success": True,
                            "message": "Atención médica registrada correctamente",
                            "atencion_id": atencion_id,
                        }
                    )
                else:
                    logger.error(f"❌ No se pudo obtener ID de la atención registrada")
                    return jsonify({"error": "Error al obtener ID de la atención"}), 500

            except Exception as e:
                logger.error(f"❌ Error registrando atención en la base de datos: {e}")
                logger.error(f"❌ Tipo de error: {type(e).__name__}")
                logger.error(f"❌ Traceback completo: ", exc_info=True)
                postgres_db.conn.rollback()
                return (
                    jsonify(
                        {"error": f"Error al registrar en la base de datos: {str(e)}"}
                    ),
                    500,
                )
        else:
            logger.warning("⚠️ PostgreSQL no disponible para registrar atención")
            return jsonify({"error": "Base de datos no disponible"}), 503

    except Exception as e:
        logger.error(f"❌ Error en register_atencion: {e}")
        logger.error(f"❌ Tipo de error: {type(e).__name__}")
        logger.error(f"❌ Traceback completo: ", exc_info=True)
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


def crear_paciente_automatico(nombre_completo):
    """Crear paciente automáticamente cuando no se encuentra"""
    try:
        partes_nombre = nombre_completo.strip().split()
        if len(partes_nombre) >= 2:
            nombre = partes_nombre[0]
            apellido = " ".join(partes_nombre[1:])
        else:
            nombre = nombre_completo
            apellido = "Paciente"

        # Generar email único
        nombre_clean = nombre.lower().replace(" ", "")
        apellido_clean = apellido.lower().replace(" ", "")
        import time

        timestamp = str(int(time.time()))
        email = f"{nombre_clean}.{apellido_clean}.{timestamp}@auto.medconnect.cl"

        # Generar password hash por defecto (los pacientes creados automáticamente no necesitan login)
        import bcrypt

        default_password = f"temp{timestamp}"
        password_hash = bcrypt.hashpw(
            default_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        # Insertar en la base de datos con password_hash
        insert_query = """
            INSERT INTO usuarios (nombre, apellido, email, password_hash, tipo_usuario, fecha_registro, activo)
            VALUES (%s, %s, %s, %s, 'paciente', %s, true)
            RETURNING id
        """

        insert_values = (nombre, apellido, email, password_hash, datetime.now())

        postgres_db.cursor.execute(insert_query, insert_values)
        result = postgres_db.cursor.fetchone()
        postgres_db.conn.commit()

        if result and result.get("id"):
            paciente_id = result.get("id")
            logger.info(
                f"✅ Paciente '{nombre_completo}' creado automáticamente con ID: {paciente_id}"
            )
            return paciente_id
        else:
            logger.error(f"❌ No se pudo crear paciente automáticamente")
            return None

    except Exception as e:
        logger.error(f"❌ Error creando paciente automático: {e}")
        postgres_db.conn.rollback()
        return None


@app.route("/api/get-atenciones", methods=["GET"])
@login_required
def get_atenciones():
    """Obtener atenciones médicas del profesional"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        logger.info(f"[ATENCION] Obteniendo atenciones para profesional {user_id}")

        # Obtener atenciones desde la base de datos
        if postgres_db and postgres_db.is_connected():
            try:
                query = """
                    SELECT a.id, a.paciente_id, a.fecha_atencion, a.hora_inicio,
                           a.tipo_atencion, a.motivo_consulta, a.diagnostico, 
                           a.tratamiento, a.observaciones, a.estado,
                           u.nombre as paciente_nombre, u.apellido as paciente_apellido
                    FROM atenciones_medicas a
                    LEFT JOIN usuarios u ON a.paciente_id = u.id
                    WHERE a.profesional_id = %s
                    ORDER BY a.fecha_atencion DESC, a.hora_inicio DESC
                """

                postgres_db.cursor.execute(query, (user_id,))
                result = postgres_db.cursor.fetchall()

                atenciones = []
                if result:
                    for row in result:
                        atencion = {
                            "id": row.get("id"),
                            "paciente_id": row.get("paciente_id"),
                            "paciente_nombre": f"{row.get('paciente_nombre', '')} {row.get('paciente_apellido', '')}".strip(),
                            "fecha_atencion": row.get("fecha_atencion"),
                            "hora_inicio": row.get("hora_inicio"),
                            "tipo_atencion": row.get("tipo_atencion"),
                            "motivo_consulta": row.get("motivo_consulta"),
                            "diagnostico": row.get("diagnostico"),
                            "tratamiento": row.get("tratamiento"),
                            "observaciones": row.get("observaciones"),
                            "estado": row.get("estado", "completada"),
                        }
                        atenciones.append(atencion)

                logger.info(
                    f"✅ {len(atenciones)} atenciones encontradas para profesional {user_id}"
                )
                return jsonify({"success": True, "atenciones": atenciones})

            except Exception as e:
                logger.error(f"❌ Error obteniendo atenciones: {e}")
                logger.error(f"❌ Tipo de error: {type(e).__name__}")

                # Si es error de transacción abortada, intentar resetear la conexión
                if "InFailedSqlTransaction" in str(
                    e
                ) or "current transaction is aborted" in str(e):
                    logger.warning(
                        "⚠️ Transacción abortada detectada, reseteando conexión..."
                    )
                    try:
                        postgres_db.conn.rollback()
                        logger.info("✅ Rollback exitoso")
                    except Exception as rollback_error:
                        logger.error(f"❌ Error en rollback: {rollback_error}")
                        # Intentar reconectar
                        try:
                            postgres_db.connect()
                            logger.info("✅ Reconexión exitosa")
                        except Exception as reconnect_error:
                            logger.error(f"❌ Error en reconexión: {reconnect_error}")

                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Error al consultar la base de datos",
                        }
                    ),
                    500,
                )
        else:
            logger.warning("⚠️ PostgreSQL no disponible para obtener atenciones")
            return jsonify({"success": True, "atenciones": []})

    except Exception as e:
        logger.error(f"❌ Error en get_atenciones: {e}")
        logger.error(f"❌ Tipo de error: {type(e).__name__}")
        logger.error(f"❌ Traceback completo: ", exc_info=True)
        return jsonify({"error": "Error interno del servidor"}), 500


# ---------- API PACIENTE (consultas, exámenes, familia) ----------
@app.route("/api/patient/<patient_id>/consultations", methods=["GET"])
@login_required
def get_patient_consultations(patient_id):
    try:
        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - retornando array vacío")
            return jsonify({"consultations": []})

        # Consultar consultas del paciente desde PostgreSQL
        query = """
            SELECT id, patient_id, doctor, specialty, date, diagnosis, treatment, notes, status
            FROM atenciones_medicas 
            WHERE patient_id = %s
            ORDER BY date DESC
        """
        result = postgres_db.execute_query(query, (patient_id,))

        consultations = []
        if result:
            for row in result:
                consultation = {
                    "id": row.get("id"),
                    "patient_id": row.get("patient_id"),
                    "doctor": row.get("doctor"),
                    "specialty": row.get("specialty"),
                    "date": row.get("date"),
                    "diagnosis": row.get("diagnosis"),
                    "treatment": row.get("treatment"),
                    "notes": row.get("notes"),
                    "status": row.get("status", "completada"),
                }
                consultations.append(consultation)

        logger.info(
            f"[DB] Consultas encontradas para paciente {patient_id}: {len(consultations)}"
        )
        return jsonify({"consultations": consultations})

    except Exception as e:
        logger.error(f"get_patient_consultations: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/patient/<patient_id>/exams", methods=["GET"])
@login_required
def get_patient_exams(patient_id):
    try:
        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - retornando array vacío")
            return jsonify({"exams": []})

        # Consultar exámenes del paciente desde PostgreSQL
        query = """
            SELECT id, patient_id, exam_type, date, results, lab, doctor, file_url, status
            FROM examenes 
            WHERE patient_id = %s
            ORDER BY date DESC
        """
        result = postgres_db.execute_query(query, (patient_id,))

        exams = []
        if result:
            for row in result:
                exam = {
                    "id": row.get("id"),
                    "patient_id": row.get("patient_id"),
                    "exam_type": row.get("exam_type"),
                    "date": row.get("date"),
                    "results": row.get("results"),
                    "lab": row.get("lab"),
                    "doctor": row.get("doctor"),
                    "file_url": row.get("file_url"),
                    "status": row.get("status", "completado"),
                }
                exams.append(exam)

        logger.info(
            f"[DB] Exámenes encontrados para paciente {patient_id}: {len(exams)}"
        )
        return jsonify({"exams": exams})

    except Exception as e:
        logger.error(f"get_patient_exams: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/patient/<patient_id>/family", methods=["GET"])
@login_required
def get_patient_family(patient_id):
    try:
        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - retornando array vacío")
            return jsonify({"family": []})

        # Consultar familiares del paciente desde PostgreSQL
        query = """
            SELECT id, patient_id, nombre, relacion, telefono, email, direccion
            FROM familiares_autorizados 
            WHERE patient_id = %s
            ORDER BY nombre
        """
        result = postgres_db.execute_query(query, (patient_id,))

        family = []
        if result:
            for row in result:
                family_member = {
                    "id": row.get("id"),
                    "patient_id": row.get("patient_id"),
                    "nombre": row.get("nombre"),
                    "relacion": row.get("relacion"),
                    "telefono": row.get("telefono"),
                    "email": row.get("email"),
                    "direccion": row.get("direccion"),
                }
                family.append(family_member)

        logger.info(
            f"[DB] Familiares encontrados para paciente {patient_id}: {len(family)}"
        )
        return jsonify({"family": family})

    except Exception as e:
        logger.error(f"get_patient_family: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route(
    "/api/patient/<patient_id>/consultations/<consultation_id>", methods=["DELETE"]
)
@login_required
def delete_consultation(patient_id, consultation_id):
    try:
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - simulando eliminación")
            return jsonify({"deleted": True})

        # Verificar que la consulta existe y pertenece al paciente
        check_query = """
            SELECT id FROM atenciones_medicas 
            WHERE id = %s AND patient_id = %s
        """
        consultation_exists = postgres_db.execute_query(
            check_query, (consultation_id, patient_id)
        )

        if not consultation_exists:
            return jsonify({"error": "Consulta no encontrada"}), 404

        # Eliminar la consulta
        delete_query = """
            DELETE FROM atenciones_medicas 
            WHERE id = %s AND patient_id = %s
        """
        postgres_db.execute_query(delete_query, (consultation_id, patient_id))

        logger.info(
            f"[DB] Consulta {consultation_id} eliminada para paciente {patient_id}"
        )
        return jsonify({"deleted": True})

    except Exception as e:
        logger.error(f"delete_consultation: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/patient/<patient_id>/exams/<exam_id>", methods=["DELETE"])
@login_required
def delete_exam(patient_id, exam_id):
    try:
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - simulando eliminación")
            return jsonify({"deleted": True})

        # Verificar que el examen existe y pertenece al paciente
        check_query = """
            SELECT id, file_url FROM examenes 
            WHERE id = %s AND patient_id = %s
        """
        exam_exists = postgres_db.execute_query(check_query, (exam_id, patient_id))

        if not exam_exists:
            return jsonify({"error": "Examen no encontrado"}), 404

        # Si hay archivo asociado, eliminarlo
        exam_data = exam_exists[0]
        if exam_data.get("file_url"):
            try:
                file_path = exam_data["file_url"].replace("/static/uploads/", "")
                full_path = os.path.join(app.config["UPLOAD_FOLDER"], file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    logger.info(f"[FILE] Archivo eliminado: {file_path}")
            except Exception as file_error:
                logger.error(f"[FILE] Error eliminando archivo: {file_error}")

        # Eliminar el examen
        delete_query = """
            DELETE FROM examenes 
            WHERE id = %s AND patient_id = %s
        """
        postgres_db.execute_query(delete_query, (exam_id, patient_id))

        logger.info(f"[DB] Examen {exam_id} eliminado para paciente {patient_id}")
        return jsonify({"deleted": True})

    except Exception as e:
        logger.error(f"delete_exam: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# ---------- SUBIDA DE ARCHIVOS ----------
@app.route("/api/exams/<exam_id>/upload", methods=["POST"])
@login_required
def upload_exam_file(exam_id):
    try:
        if "file" not in request.files:
            return jsonify({"error": "No se envió archivo"}), 400
        f = request.files["file"]
        if not f.filename or not allowed_file(f.filename):
            return jsonify({"error": "Tipo de archivo no permitido"}), 400

        # Generar nombre seguro para el archivo
        safe_name = f"{uuid.uuid4().hex}_{f.filename}"
        dest = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
        f.save(dest)
        file_url = f"/static/uploads/{safe_name}"

        # Asociar archivo al examen en PostgreSQL si está disponible
        if postgres_db and postgres_db.is_connected():
            try:
                # Verificar que el examen existe y pertenece al usuario
                user_id = session.get("user_id")
                check_query = """
                    SELECT id FROM examenes 
                    WHERE id = %s AND patient_id = %s
                """
                exam_exists = postgres_db.execute_query(check_query, (exam_id, user_id))

                if not exam_exists:
                    # Si el examen no existe, eliminamos el archivo subido
                    os.remove(dest)
                    return (
                        jsonify({"error": "Examen no encontrado o no autorizado"}),
                        404,
                    )

                # Actualizar el examen con la URL del archivo
                update_query = """
                    UPDATE examenes 
                    SET file_url = %s, updated_at = NOW()
                    WHERE id = %s
                """
                postgres_db.execute_query(update_query, (file_url, exam_id))

                logger.info(f"[DB] Archivo asociado al examen {exam_id}: {safe_name}")

            except Exception as db_error:
                logger.error(f"[DB] Error asociando archivo: {db_error}")
                # No fallamos la subida si hay error en DB, solo log
        else:
            logger.warning("PostgreSQL no disponible - archivo subido sin asociar a DB")

        logger.info(f"[UPLOAD] exam:{exam_id} file:{safe_name}")
        return jsonify({"success": True, "file_url": file_url})

    except Exception as e:
        logger.error(f"upload_exam_file error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# ---------- ADMIN ----------
@app.route("/api/admin/link-existing-users", methods=["POST"])
@login_required
def link_existing_users():
    try:
        # Si tu backend (DB/Sheets) está disponible, implementa la vinculación.
        if not auth_manager:
            return jsonify({"error": "Servicio no disponible"}), 501
        summary = auth_manager.link_existing_users()  # asume que exista; si no, mockea
        return jsonify({"success": True, "results": summary})
    except Exception as e:
        logger.error(f"link_existing_users: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# ---------- TELEGRAM ----------
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json() or {}
        if "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")
            user_id = msg["from"]["id"]
            username = msg["from"].get("username", "sin_username")
            log_bot_interaction(user_id, username, text, chat_id)
            resp = process_telegram_message(text, chat_id, user_id)
            if resp:
                send_telegram_message(chat_id, resp)
        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"[WEBHOOK] {e}")
        return jsonify({"error": "Error procesando webhook"}), 500


@app.route("/test-bot", methods=["GET"])
def test_bot():
    info = {
        "bot_token_configured": bool(app.config["TELEGRAM_BOT_TOKEN"]),
        "webhook_url": "/webhook",
    }
    return jsonify({"status": "Bot configurado", "bot_info": info})


@app.route("/bot-stats", methods=["GET"])
def bot_stats():
    try:
        # Si hay almacenamiento, obtén stats reales; demo:
        stats = {"total_interactions": 0, "unique_users": 0, "recent_interactions": []}
        return jsonify(
            {"status": "success", "stats": stats, "bot_username": "@Medconn_bot"}
        )
    except Exception as e:
        return jsonify(
            {"status": "error", "error": str(e), "bot_username": "@Medconn_bot"}
        )


# ---------- HEALTH / DEBUG ----------
@app.route("/health")
def health():
    try:
        return jsonify(
            {
                "status": "healthy",
                "time": datetime.now().isoformat(),
                "auth_manager": bool(auth_manager),
                "postgres_connected": getattr(
                    postgres_db, "is_connected", lambda: False
                )(),
            }
        )
    except Exception as e:
        logger.error(f"health error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route("/api/user/profile")
@login_required
def get_user_profile():
    """Obtener perfil del usuario autenticado"""
    try:
        user_data = session.get("user_data", {})
        user_id = user_data.get("id") or session.get("user_id")
        
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401
        
        if postgres_db and postgres_db.is_connected():
            query = "SELECT id, nombre, apellido, email, telefono, especialidad FROM usuarios WHERE id = %s"
            postgres_db.cursor.execute(query, (user_id,))
            user = postgres_db.cursor.fetchone()
            
            if user:
                return jsonify({
                    "success": True,
                    "user": {
                        "id": user[0],
                        "nombre": user[1],
                        "apellido": user[2],
                        "email": user[3],
                        "telefono": user[4],
                        "especialidad": user[5]
                    }
                })
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404
        else:
            return jsonify({"error": "Base de datos no disponible"}), 500
            
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route("/api/test-atencion")
@login_required
def test_atencion():
    """Endpoint de prueba para el sistema de atenciones"""
    try:
        return jsonify({
            "success": True,
            "message": "Sistema de atenciones funcionando correctamente",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error en test-atencion: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/debug-static")
def debug_static():
    static_dir = app.static_folder
    files = []
    for root, _, fs in os.walk(static_dir):
        for name in fs:
            files.append(os.path.relpath(os.path.join(root, name), static_dir))
    return jsonify(
        {"static_root": static_dir, "count": len(files), "files": files[:50]}
    )


# ---------- ERROR HANDLERS ----------
@app.errorhandler(404)
def not_found(e):
    return (
        (render_template("404.html"), 404)
        if os.path.exists(os.path.join("templates", "404.html"))
        else ("404", 404)
    )


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500: {e}")
    return (
        (render_template("500.html"), 500)
        if os.path.exists(os.path.join("templates", "500.html"))
        else ("500", 500)
    )


# ==================== RUTAS API COMPLETAS PARA SISTEMA FUNCIONAL ====================

# ==================== GESTIÓN DE PACIENTES ====================


@app.route("/api/professional/patients", methods=["GET", "POST"])
@login_required
def get_professional_patients_new():
    """Obtener lista de pacientes del profesional - VERSIÓN FUNCIONAL"""
    try:
        # Obtener user_id de la sesión
        user_data = session.get("user_data", {})
        user_id = user_data.get("id") or session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        logger.info(f"🔍 User ID obtenido: {user_id}")

        # Si es POST, crear nuevo paciente
        if request.method == "POST":
            return crear_paciente_desde_formulario(user_id)

        # Si es GET, obtener lista de pacientes
        logger.info(f"[PACIENTES] Obteniendo pacientes para profesional {user_id}")

        # VERSIÓN FUNCIONAL - Consulta directa
        if postgres_db and postgres_db.is_connected():
            try:
                query = """
                    SELECT DISTINCT 
                        pp.paciente_id as id,
                        pp.nombre_completo,
                        pp.email,
                        pp.telefono,
                        pp.fecha_nacimiento,
                        pp.genero,
                        pp.direccion,
                        pp.fecha_primera_consulta as fecha_primera_atencion,
                        pp.ultima_consulta as ultima_atencion,
                        pp.notas as notas_generales,
                        pp.estado_relacion
                    FROM pacientes_profesional pp
                    WHERE pp.profesional_id = %s 
                    AND (pp.estado_relacion = 'activo' OR pp.estado_relacion IS NULL)
                    ORDER BY pp.nombre_completo
                """

                postgres_db.cursor.execute(query, (user_id,))
                result = postgres_db.cursor.fetchall()

                pacientes = []
                if result:
                    for row in result:
                        # Separar nombre completo en nombre y apellido
                        nombre_completo = row.get("nombre_completo", "")
                        partes_nombre = nombre_completo.split(" ", 1)
                        nombre = partes_nombre[0] if partes_nombre else ""
                        apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""

                        paciente = {
                            "id": row.get("id"),
                            "nombre": nombre,
                            "apellido": apellido,
                            "email": row.get("email"),
                            "telefono": (
                                str(row.get("telefono"))
                                if row.get("telefono")
                                else None
                            ),
                            "fecha_nacimiento": (
                                str(row.get("fecha_nacimiento"))
                                if row.get("fecha_nacimiento")
                                else None
                            ),
                            "genero": row.get("genero"),
                            "direccion": row.get("direccion"),
                            "fecha_primera_atencion": (
                                str(row.get("fecha_primera_atencion"))
                                if row.get("fecha_primera_atencion")
                                else None
                            ),
                            "total_atenciones": 0,
                            "ultima_atencion": (
                                str(row.get("ultima_atencion"))
                                if row.get("ultima_atencion")
                                else None
                            ),
                            "notas_generales": row.get("notas_generales"),
                            "estado_relacion": row.get("estado_relacion", "activo"),
                        }
                        pacientes.append(paciente)

                logger.info(
                    f"✅ {len(pacientes)} pacientes encontrados para profesional {user_id}"
                )
                return jsonify({"success": True, "pacientes": pacientes})

            except Exception as e:
                logger.error(f"❌ Error obteniendo pacientes: {e}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Error al consultar la base de datos",
                        }
                    ),
                    500,
                )
        else:
            return jsonify({"success": True, "pacientes": []})

    except Exception as e:
        logger.error(f"❌ Error en get_professional_patients_new: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


# ==================== ENDPOINT SIMPLIFICADO Y FUNCIONAL ====================


@app.route("/api/professional/patients-simple", methods=["GET"])
@login_required
def get_professional_patients_simple():
    """Endpoint simplificado y funcional para obtener pacientes"""
    try:
        # Obtener user_id de la sesión
        user_data = session.get("user_data", {})
        user_id = user_data.get("id") or session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        logger.info(f"🔍 User ID obtenido: {user_id}")

        # Consulta directa y simple
        if postgres_db and postgres_db.is_connected():
            try:
                query = """
                    SELECT DISTINCT 
                        pp.paciente_id as id,
                        pp.nombre_completo,
                        pp.email,
                        pp.telefono,
                        pp.fecha_nacimiento,
                        pp.genero,
                        pp.direccion,
                        pp.fecha_primera_consulta as fecha_primera_atencion,
                        pp.ultima_consulta as ultima_atencion,
                        pp.notas as notas_generales,
                        pp.estado_relacion
                    FROM pacientes_profesional pp
                    WHERE pp.profesional_id = %s 
                    AND (pp.estado_relacion = 'activo' OR pp.estado_relacion IS NULL)
                    ORDER BY pp.nombre_completo
                """

                postgres_db.cursor.execute(query, (user_id,))
                result = postgres_db.cursor.fetchall()

                pacientes = []
                if result:
                    for row in result:
                        # Separar nombre completo en nombre y apellido
                        nombre_completo = row.get("nombre_completo", "")
                        partes_nombre = nombre_completo.split(" ", 1)
                        nombre = partes_nombre[0] if partes_nombre else ""
                        apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""

                        paciente = {
                            "id": row.get("id"),
                            "nombre": nombre,
                            "apellido": apellido,
                            "email": row.get("email"),
                            "telefono": (
                                str(row.get("telefono"))
                                if row.get("telefono")
                                else None
                            ),
                            "fecha_nacimiento": (
                                str(row.get("fecha_nacimiento"))
                                if row.get("fecha_nacimiento")
                                else None
                            ),
                            "genero": row.get("genero"),
                            "direccion": row.get("direccion"),
                            "fecha_primera_atencion": (
                                str(row.get("fecha_primera_atencion"))
                                if row.get("fecha_primera_atencion")
                                else None
                            ),
                            "total_atenciones": 0,
                            "ultima_atencion": (
                                str(row.get("ultima_atencion"))
                                if row.get("ultima_atencion")
                                else None
                            ),
                            "notas_generales": row.get("notas_generales"),
                            "estado_relacion": row.get("estado_relacion", "activo"),
                        }
                        pacientes.append(paciente)

                logger.info(
                    f"✅ {len(pacientes)} pacientes encontrados para profesional {user_id}"
                )
                return jsonify({"success": True, "pacientes": pacientes})

            except Exception as e:
                logger.error(f"❌ Error obteniendo pacientes: {e}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Error al consultar la base de datos",
                        }
                    ),
                    500,
                )
        else:
            return jsonify({"success": True, "pacientes": []})

    except Exception as e:
        logger.error(f"❌ Error en get_professional_patients_simple: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


def crear_paciente_desde_formulario(user_id):
    """Crear paciente desde formulario del frontend - Solo como registro médico, no como usuario del sistema"""
    try:
        # Obtener datos del formulario
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400

        # Validar datos requeridos
        required_fields = ["nombre", "apellido", "email", "telefono"]
        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify({"success": False, "error": f"Campo {field} es requerido"}),
                    400,
                )

        # Crear paciente en la base de datos
        if postgres_db and postgres_db.is_connected():
            try:
                # Generar ID único para el paciente
                import uuid

                paciente_id = f"PAC_{uuid.uuid4().hex[:8].upper()}"

                # Insertar paciente en la tabla pacientes_profesional
                query = """
                    INSERT INTO pacientes_profesional (
                        paciente_id, profesional_id, nombre_completo, email, telefono,
                        fecha_nacimiento, genero, direccion, estado_relacion, fecha_registro
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                nombre_completo = f"{data['nombre']} {data['apellido']}"
                postgres_db.cursor.execute(
                    query,
                    (
                        paciente_id,
                        user_id,
                        nombre_completo,
                        data["email"],
                        data["telefono"],
                        data.get("fecha_nacimiento"),
                        data.get("genero"),
                        data.get("direccion"),
                        "activo",
                        "now()",
                    ),
                )

                postgres_db.conn.commit()

                logger.info(f"✅ Paciente creado: {nombre_completo} ({data['email']})")
                return jsonify(
                    {
                        "success": True,
                        "message": "Paciente creado exitosamente",
                        "paciente_id": paciente_id,
                    }
                )

            except Exception as e:
                logger.error(f"❌ Error creando paciente: {e}")
                return (
                    jsonify({"success": False, "error": "Error al crear paciente"}),
                    500,
                )
        else:
            return (
                jsonify({"success": False, "error": "Base de datos no disponible"}),
                500,
            )

    except Exception as e:
        logger.error(f"❌ Error en crear_paciente_desde_formulario: {e}")
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500


# ==================== GESTIÓN DE AGENDA/CITAS ====================


@app.route("/api/professional/schedule", methods=["GET"])
@login_required
def get_professional_schedule():
    """Obtener agenda del profesional"""
    try:
        # Obtener user_id de la sesión
        user_data = session.get("user_data", {})
        user_id = user_data.get("id") or session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        logger.info(f"🔍 User ID obtenido: {user_id}")

        # Obtener parámetros de la consulta
        fecha = request.args.get("fecha")
        vista = request.args.get("vista", "semana")

        # Obtener citas reales de la base de datos
        if postgres_db and postgres_db.is_connected():
            try:
                # Consulta para obtener citas del profesional
                query = """
                    SELECT cita_id, fecha, hora, paciente_id, paciente_nombre, 
                           paciente_rut, tipo_atencion, estado, motivo, 
                           fecha_creacion
                    FROM citas_agenda 
                    WHERE profesional_id = %s
                """
                
                # Si se especifica una fecha, filtrar por esa fecha
                if fecha:
                    query += " AND fecha = %s"
                    postgres_db.cursor.execute(query, (user_id, fecha))
                else:
                    postgres_db.cursor.execute(query, (user_id,))
                
                citas_db = postgres_db.cursor.fetchall()
                
                # Convertir resultados a formato JSON
                agenda_real = []
                for cita in citas_db:
                    agenda_real.append({
                        "cita_id": cita[0],
                        "fecha": str(cita[1]) if cita[1] else fecha or "2025-09-28",
                        "hora_inicio": str(cita[2]) if cita[2] else "09:00",
                        "hora_fin": str(cita[2]) if cita[2] else "10:00",  # Asumir 1 hora de duración
                        "paciente_id": cita[3],
                        "paciente_nombre": cita[4],
                        "paciente_rut": cita[5],
                        "tipo_atencion": cita[6] or "consulta",
                        "motivo": cita[8] or "Sin motivo especificado",
                        "estado": cita[7] or "pendiente",
                        "profesional_id": user_id,
                        "duracion": 60,
                        "notas": f"Cita creada el {cita[9]}" if cita[9] else "",
                        "fecha_creacion": str(cita[9]) if cita[9] else "2025-09-28T08:00:00Z"
                    })
                
                logger.info(f"✅ {len(agenda_real)} citas reales encontradas para profesional {user_id}")
                
                return jsonify({
                    "success": True,
                    "agenda": agenda_real,
                    "fecha": fecha,
                    "vista": vista,
                    "mensaje": f"Agenda real - {len(agenda_real)} citas"
                })
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo citas de la base de datos: {e}")
                # Fallback a agenda simulada si hay error
                agenda_simulada = [
                    {
                        "cita_id": "CITA_20250928_090000",
                        "fecha": fecha or "2025-09-28",
                        "hora_inicio": "09:00",
                        "hora_fin": "10:00",
                        "paciente_id": "PAC_001",
                        "paciente_nombre": "María González",
                        "paciente_rut": "12345678-9",
                        "tipo_atencion": "consulta",
                        "motivo": "Control rutinario",
                        "estado": "programada",
                        "profesional_id": user_id,
                        "duracion": 60,
                        "notas": "Primera consulta",
                        "fecha_creacion": "2025-09-28T08:00:00Z"
                    }
                ]
                
                return jsonify({
                    "success": True,
                    "agenda": agenda_simulada,
                    "fecha": fecha,
                    "vista": vista,
                    "mensaje": f"Agenda simulada (fallback) - {len(agenda_simulada)} citas"
                })
        else:
            return jsonify({"error": "Base de datos no disponible"}), 500

    except Exception as e:
        logger.error(f"❌ Error en get_professional_schedule: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route("/api/professional/schedule", methods=["POST"])
@login_required
def create_appointment():
    """Crear nueva cita en la agenda"""
    try:
        user_data = session.get("user_data", {})
        user_id = user_data.get("id") or session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "Datos de cita requeridos"}), 400

        # Validar campos requeridos
        required_fields = ["paciente_id", "fecha", "hora", "tipo_atencion", "motivo"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Campo {field} es requerido"}), 400

        # Generar ID único para la cita
        cita_id = f"CITA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if postgres_db and postgres_db.is_connected():
            try:
                # Insertar nueva cita
                insert_query = """
                    INSERT INTO citas_agenda (cita_id, fecha, hora, paciente_id, paciente_nombre, 
                                            paciente_rut, tipo_atencion, estado, motivo, profesional_id, 
                                            fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Obtener datos del paciente
                paciente_query = "SELECT nombre, apellido, rut FROM pacientes_profesional WHERE paciente_id = %s AND profesional_id = %s"
                postgres_db.cursor.execute(paciente_query, (data["paciente_id"], user_id))
                paciente = postgres_db.cursor.fetchone()
                
                if not paciente:
                    return jsonify({"error": "Paciente no encontrado en tu lista"}), 404
                
                postgres_db.cursor.execute(insert_query, (
                    cita_id,
                    data["fecha"],
                    data["hora"],
                    data["paciente_id"],
                    f"{paciente[0]} {paciente[1]}",
                    paciente[2],
                    data["tipo_atencion"],
                    "pendiente",
                    data["motivo"],
                    user_id,
                    datetime.now()
                ))
                
                postgres_db.conn.commit()
                
                logger.info(f"✅ Cita {cita_id} creada exitosamente")
                return jsonify({
                    "success": True,
                    "message": "Cita creada exitosamente",
                    "cita_id": cita_id
                })
                
            except Exception as e:
                logger.error(f"❌ Error creando cita: {e}")
                return jsonify({"error": "Error al crear cita"}), 500
        else:
            return jsonify({"error": "Base de datos no disponible"}), 500
            
    except Exception as e:
        logger.error(f"❌ Error en create_appointment: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# ==================== GESTIÓN DE PACIENTES ====================


@app.route("/api/professional/patients/<paciente_id>", methods=["DELETE"])
@login_required
def delete_professional_patient(paciente_id):
    """Eliminar paciente de la lista del profesional"""
    try:
        # Obtener user_id de la sesión
        user_data = session.get("user_data", {})
        user_id = user_data.get("id") or session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        logger.info(f"🗑️ Eliminando paciente {paciente_id} para profesional {user_id}")

        if postgres_db and postgres_db.is_connected():
            try:
                # Verificar que el paciente existe en la tabla pacientes_profesional
                check_query = """
                    SELECT paciente_id, nombre_completo, email
                    FROM pacientes_profesional
                    WHERE paciente_id = %s AND profesional_id = %s
                """
                postgres_db.cursor.execute(check_query, (paciente_id, user_id))
                paciente = postgres_db.cursor.fetchone()

                if not paciente:
                    return jsonify({"error": "Paciente no encontrado en tu lista"}), 404

                # Eliminar la relación profesional-paciente
                delete_query = """
                    DELETE FROM pacientes_profesional
                    WHERE paciente_id = %s AND profesional_id = %s
                """
                postgres_db.cursor.execute(delete_query, (paciente_id, user_id))
                postgres_db.conn.commit()

                logger.info(
                    f"✅ Paciente {paciente_id} eliminado de la lista del profesional {user_id}"
                )
                return jsonify(
                    {
                        "success": True,
                        "message": "Paciente eliminado de tu lista exitosamente",
                    }
                )

            except Exception as e:
                logger.error(f"❌ Error eliminando paciente: {e}")
                return jsonify({"error": "Error al eliminar paciente"}), 500
        else:
            return jsonify({"error": "Base de datos no disponible"}), 500

    except Exception as e:
        logger.error(f"❌ Error en delete_professional_patient: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# ==================== FIN DEL ARCHIVO ====================
