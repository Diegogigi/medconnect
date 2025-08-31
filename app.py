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
    print(f"[INFO] PostgreSQLDBManager inicializado: {'Conectado' if postgres_db.is_connected() else 'Modo fallback'}")
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
    PREFERRED_URL_SCHEME = "https" if "medconnect.cl" in os.environ.get("CUSTOM_DOMAIN","") else "http"
    
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
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
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
    """Página principal - Landing page simple"""
    try:
        # Intentar usar el template original
        return render_template("index.html")
    except Exception as e:
        logger.error(f"❌ Error cargando template index.html: {e}")
        # Fallback a página simple
        html = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MedConnect - Gestión Médica Familiar</title>
            <style>
                body { 
                    font-family: 'Inter', Arial, sans-serif; 
                    margin: 0; 
                    padding: 0; 
                    background: linear-gradient(135deg, #0066cc 0%, #6366f1 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container { 
                    background: white; 
                    padding: 40px; 
                    border-radius: 16px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                    width: 90%;
                }
                h1 { 
                    color: #0066cc; 
                    margin-bottom: 20px;
                    font-size: 2.5em;
                }
                p { 
                    color: #6b7280; 
                    margin-bottom: 30px;
                    line-height: 1.6;
                }
                .btn { 
                    background: linear-gradient(135deg, #0066cc 0%, #6366f1 100%);
                    color: white; 
                    padding: 15px 30px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    display: inline-block; 
                    margin: 10px;
                    font-weight: 600;
                    transition: transform 0.2s;
                }
                .btn:hover { 
                    transform: translateY(-2px);
                }
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .feature {
                    padding: 20px;
                    background: #f8fafc;
                    border-radius: 8px;
                    border-left: 4px solid #0066cc;
                }
                .feature h3 {
                    color: #0066cc;
                    margin-bottom: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏥 MedConnect</h1>
                <p>Sistema integral de gestión médica familiar con Asistente de IA inteligente</p>
                
                <div class="features">
                    <div class="feature">
                        <h3>📅 Gestión de Citas</h3>
                        <p>Organiza y gestiona citas médicas familiares</p>
                    </div>
                    <div class="feature">
                        <h3>💊 Control de Medicamentos</h3>
                        <p>Monitorea tratamientos y medicamentos</p>
                    </div>
                    <div class="feature">
                        <h3>🤖 IA Asistente</h3>
                        <p>Asistente inteligente para consultas médicas</p>
                    </div>
                </div>
                
                <a href="/login" class="btn">Iniciar Sesión</a>
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
                return render_template("login.html", message="Credenciales inválidas", success=False)
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
            return redirect(url_for("professional_dashboard"))
        return redirect(url_for("patient_dashboard"))

    except Exception as e:
        diag = diagnose_login_error(e)
        logger.error(f"[LOGIN] {diag['debug_info']}")
        try:
            return render_template("login.html", message=diag["user_message"], success=False)
        except Exception as template_error:
            logger.error(f"❌ Error renderizando login con error: {template_error}")
            return _login_fallback_html(diag["user_message"], False)

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
            "tipo_usuario": user_type
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
    # Si tienes profesional_id en session, podrías cargar agenda
    return (
        render_template("professional_dashboard.html")
        if os.path.exists(os.path.join("templates", "professional_dashboard.html"))
        else "Profesional"
    )


# ---------- API PERFIL ----------
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


# ---------- MAIN ----------
if __name__ == "__main__":
    # Solo para desarrollo local (no se ejecuta con Gunicorn)
    logger.info(f"🌐 Iniciando Flask en modo desarrollo - puerto: {app.config['PORT']}")
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=True)
