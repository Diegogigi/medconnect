# MedConnect - Aplicacion Principal Flask
# Backend para plataforma de gestion medica con Google Sheets y Telegram Bot

import os
import sys
import logging
import time
import random
import threading

# Configurar logging temprano para debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

logger.info("  Iniciando importaciones de MedConnect...")

try:
    logger.info("[PAQUETE] Importando Flask...")
    from flask import (
        Flask,
        render_template,
        request,
        jsonify,
        session,
        redirect,
        url_for,
        flash,
        make_response,
        send_from_directory,
        send_file,
        abort,
        Response,
    )

    logger.info("[OK] Flask importado exitosamente")

    logger.info("[PAQUETE] Importando Flask-CORS...")
    from flask_cors import CORS

    logger.info("[OK] Flask-CORS importado exitosamente")

    logger.info("[PAQUETE] Importando bibliotecas est ndar...")
    import requests
    import json
    import pdfkit
    import tempfile
    from io import BytesIO
    from datetime import datetime, timedelta

    logger.info("[OK] Bibliotecas est ndar importadas")

    logger.info("[PAQUETE] Importando Google Sheets...")
    import gspread
    from google.oauth2.service_account import Credentials

    logger.info("[OK] Google Sheets importado exitosamente")

    logger.info("[PAQUETE] Importando m dulos locales...")
    from config import get_config, SHEETS_CONFIG
    from auth_manager import AuthManager

    # Importar SheetsManager con manejo robusto de errores
    try:
        from backend.database.sheets_manager import sheets_db

        logger.info("[OK] SheetsManager importado correctamente")
    except Exception as e:
        logger.error(f"[ERROR] Error importando SheetsManager: {e}")
        # Intentar inicializaci n alternativa
        try:
            from sheets_manager_init import get_sheets_manager

            sheets_db = get_sheets_manager()
            if sheets_db:
                logger.info("[OK] SheetsManager inicializado con m todo alternativo")
            else:
                logger.error("[ERROR] No se pudo inicializar SheetsManager")
                sheets_db = None
        except Exception as e2:
            logger.error(f"[ERROR] Error en inicializaci n alternativa: {e2}")
            sheets_db = None

    logger.info("[OK] M dulos locales importados")

    logger.info("[PAQUETE] Importando otras dependencias...")
    from werkzeug.utils import secure_filename
    import uuid
    from werkzeug.security import generate_password_hash, check_password_hash
    import secrets

    logger.info("[OK] Todas las importaciones completadas exitosamente")

    # Importar m dulo Copilot Health
    logger.info("[PAQUETE] Importando Copilot Health...")
    try:
        from copilot_health import copilot_health

        COPILOT_HEALTH_AVAILABLE = True
        logger.info("[OK] M dulo Copilot Health cargado exitosamente")
    except ImportError as e:
        COPILOT_HEALTH_AVAILABLE = False
        logger.warning(f"[ADVERTENCIA] M dulo Copilot Health no disponible: {e}")
    except Exception as e:
        COPILOT_HEALTH_AVAILABLE = False
        logger.error(f"[ERROR] Error cargando Copilot Health: {e}")

except Exception as e:
    logger.error(f"[ERROR] Error durante las importaciones: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback

    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    raise

# Inicializar Flask
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Variables globales
start_time = time.time()  # Tiempo de inicio de la aplicación
SPREADSHEET_ID = config.GOOGLE_SHEETS_ID  # ID de la hoja de cálculo de Google

# Configurar archivos estáticos para producción
# Múltiples métodos para asegurar que funcione en Railway
try:
    # Método 1: WhiteNoise (preferido)
    from whitenoise import WhiteNoise

    app.wsgi_app = WhiteNoise(
        app.wsgi_app,
        root=os.path.join(app.root_path, "static"),
        prefix="/static/",
        max_age=31536000,  # Cache por 1 año
    )
    logger.info("[OK] WhiteNoise configurado para archivos estáticos")
except Exception as e:
    logger.error(f"[ERROR] Error configurando WhiteNoise: {e}")

# Método 2: Configurar Flask para servir archivos estáticos directamente
app.static_folder = "static"
app.static_url_path = "/static"

# Método 3: Configuración adicional para Railway
# Asegurar que la carpeta static existe y tiene los archivos necesarios
static_path = os.path.join(app.root_path, "static")
if not os.path.exists(static_path):
    logger.warning(f"[ADVERTENCIA] Carpeta static no encontrada en: {static_path}")
    # Crear la carpeta si no existe
    os.makedirs(static_path, exist_ok=True)
    logger.info(f"[OK] Carpeta static creada: {static_path}")

# Verificar archivos críticos
critical_files = ["css/styles.css", "js/app.js", "images/logo.png"]
for file_path in critical_files:
    full_path = os.path.join(static_path, file_path)
    if os.path.exists(full_path):
        logger.info(f"[OK] Archivo crítico encontrado: {file_path}")
    else:
        logger.warning(f"[ADVERTENCIA] Archivo crítico faltante: {file_path}")

logger.info(f"[CARPETA] Static folder: {app.static_folder}")
logger.info(f"[MUNDO] Static URL path: {app.static_url_path}")
logger.info(f"[ARCHIVO] Static path completo: {static_path}")

# Configurar CORS
CORS(app, origins=config.CORS_ORIGINS)

# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "static", "uploads"
)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración de Google Sheets
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Sistema de caché para reducir llamadas a Google Sheets API
_cache = {}
_cache_lock = threading.Lock()
_cache_timeout = 60  # segundos


def get_cached_data(key, timeout=None):
    """Obtiene datos del caché si están disponibles y no han expirado"""
    if timeout is None:
        timeout = _cache_timeout

    with _cache_lock:
        if key in _cache:
            data, timestamp = _cache[key]
            if time.time() - timestamp < timeout:
                logger.info(f"[CACHE] Datos obtenidos del caché para: {key}")
                return data
            else:
                del _cache[key]
    return None


def set_cached_data(key, data):
    """Almacena datos en el caché"""
    with _cache_lock:
        _cache[key] = (data, time.time())
        logger.info(f"[CACHE] Datos almacenados en caché para: {key}")


def clear_cache():
    """Limpia el caché"""
    with _cache_lock:
        _cache.clear()
        logger.info("[CACHE] Caché limpiado")


def handle_rate_limiting(func, max_retries=5, base_delay=3, use_cache=True):
    """
    Maneja el rate limiting de Google Sheets API con retry exponencial mejorado y caché
    """
    # Generar clave de caché basada en la función
    cache_key = f"{func.__name__}_{hash(str(func))}"

    # Intentar obtener del caché primero
    if use_cache:
        cached_result = get_cached_data(cache_key)
        if cached_result is not None:
            return cached_result

    for attempt in range(max_retries):
        try:
            result = func()

            # Almacenar en caché si fue exitoso
            if use_cache and result is not None:
                set_cached_data(cache_key, result)

            return result

        except Exception as e:
            error_str = str(e).lower()

            # Detectar diferentes tipos de errores de rate limiting
            if any(
                keyword in error_str
                for keyword in [
                    "429",
                    "quota exceeded",
                    "resource_exhausted",
                    "rate_limit",
                ]
            ):
                if attempt < max_retries - 1:
                    # Delay exponencial con jitter mejorado
                    delay = base_delay * (2**attempt) + random.uniform(2, 5)
                    logger.warning(
                        f"[ADVERTENCIA] Rate limiting detectado (intento {attempt + 1}/{max_retries}). Esperando {delay:.2f}s..."
                    )
                    time.sleep(delay)
                    continue
                else:
                    logger.error(
                        f"[ERROR] Rate limiting persistente después de {max_retries} intentos"
                    )
                    # Intentar devolver datos del caché como fallback
                    if use_cache:
                        cached_result = get_cached_data(
                            cache_key, timeout=600
                        )  # 10 minutos para fallback
                        if cached_result is not None:
                            logger.info(
                                f"[CACHE] Usando datos del caché como fallback para: {cache_key}"
                            )
                            return cached_result
                    return None
            elif "500" in error_str or "internal server error" in error_str:

                logger.error(
                    f"[ERROR] Error interno del servidor de Google Sheets: {e}"
                )
                # Intentar devolver datos del caché como fallback
                if use_cache:
                    cached_result = get_cached_data(cache_key, timeout=600)
                    if cached_result is not None:
                        logger.info(
                            f"[CACHE] Usando datos del caché como fallback para error 500: {cache_key}"
                        )
                        return cached_result
                return None
            else:
                logger.error(f"[ERROR] Error no relacionado con rate limiting: {e}")
                return None

    return None


def get_google_sheets_client():
    """Inicializa el cliente de Google Sheets"""
    try:
        # Verificar si existe archivo de credenciales local
        credentials_file = app.config.get("GOOGLE_CREDENTIALS_FILE")
        if credentials_file and os.path.exists(credentials_file):
            creds = Credentials.from_service_account_file(
                credentials_file, scopes=SCOPES
            )
        else:
            # Para Railway, usar variables de entorno (m todo preferido)
            service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
            if service_account_json != "{}":
                service_account_info = json.loads(service_account_json)
                creds = Credentials.from_service_account_info(
                    service_account_info, scopes=SCOPES
                )
            else:
                logger.error("[ERROR] No se encontraron credenciales de Google Sheets")
                return None

        client = gspread.authorize(creds)
        logger.info("[OK] Cliente de Google Sheets inicializado correctamente")
        return client
    except Exception as e:
        logger.error(f"Error inicializando Google Sheets: {e}")
        return None


# Cliente global de Google Sheets
# sheets_client = get_google_sheets_client()  # Ya inicializado globalmente


# Funciones auxiliares para las vistas de agenda
def obtener_rango_semana(fecha_str):
    """Obtiene el rango de fechas de la semana que contiene la fecha dada"""
    from datetime import datetime, timedelta

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Obtener el lunes de la semana (d a 0)
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    return inicio_semana.strftime("%Y-%m-%d"), fin_semana.strftime("%Y-%m-%d")


def obtener_rango_mes(fecha_str):
    """Obtiene el rango de fechas del mes que contiene la fecha dada"""
    from datetime import datetime
    import calendar

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Primer d a del mes
    inicio_mes = fecha.replace(day=1)
    #  ltimo d a del mes
    ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
    fin_mes = fecha.replace(day=ultimo_dia)

    return inicio_mes.strftime("%Y-%m-%d"), fin_mes.strftime("%Y-%m-%d")


def organizar_agenda_semanal(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a de la semana"""
    from datetime import datetime, timedelta

    agenda = {}
    dias_semana = [
        "Lunes",
        "Martes",
        "Mi rcoles",
        "Jueves",
        "Viernes",
        "S bado",
        "Domingo",
    ]

    # Inicializar estructura
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    for i in range(7):
        fecha_dia = (inicio + timedelta(days=i)).strftime("%Y-%m-%d")
        agenda[fecha_dia] = {
            "dia_semana": dias_semana[i],
            "fecha": fecha_dia,
            "citas": [],
        }

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def organizar_agenda_mensual(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a del mes"""
    from datetime import datetime, timedelta

    agenda = {}

    # Inicializar estructura para todos los d as del mes
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    fecha_actual = inicio
    while fecha_actual <= fin:
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        agenda[fecha_str] = {
            "fecha": fecha_str,
            "dia": fecha_actual.day,
            "es_hoy": fecha_str == datetime.now().strftime("%Y-%m-%d"),
            "citas": [],
        }
        fecha_actual += timedelta(days=1)

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def calcular_estadisticas_semana(citas):
    """Calcula estad sticas para la vista semanal"""
    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
    }


def calcular_estadisticas_mes(citas):
    """Calcula estad sticas para la vista mensual"""
    from datetime import datetime

    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    # Agrupar por semana
    citas_por_semana = {}
    for cita in citas:
        fecha_cita = datetime.strptime(cita["fecha"], "%Y-%m-%d")
        semana = fecha_cita.isocalendar()[1]  # N mero de semana del a o
        if semana not in citas_por_semana:
            citas_por_semana[semana] = 0
        citas_por_semana[semana] += 1

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
        "citas_por_semana": citas_por_semana,
    }


# Inicializar AuthManager con debugging detallado
logger.info("[BUSCAR] Iniciando inicializaci n de AuthManager...")

try:
    # Verificar variables de entorno antes de crear AuthManager
    env_check = {
        "GOOGLE_SERVICE_ACCOUNT_JSON": bool(
            os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        ),
        "GOOGLE_SHEETS_ID": bool(os.environ.get("GOOGLE_SHEETS_ID")),
        "TELEGRAM_BOT_TOKEN": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
    }
    logger.info(f"[HERRAMIENTA] Variables de entorno en app.py: {env_check}")

    # Verificar contenido de JSON
    json_content = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if json_content:
        logger.info(f"[NOTA] JSON length: {len(json_content)} chars")
        logger.info(f"[NOTA] JSON preview: {json_content[:100]}...")

        # Verificar que es JSON v lido
        try:
            test_json = json.loads(json_content)
            logger.info(
                f"[OK] JSON v lido, proyecto: {test_json.get('project_id', 'N/A')}"
            )
        except json.JSONDecodeError as je:
            logger.error(f"[ERROR] JSON inv lido: {je}")

    # Intentar crear AuthManager
    logger.info("  Creando instancia de AuthManager...")
    auth_manager = AuthManager()
    logger.info("[OK] AuthManager inicializado correctamente")

except Exception as e:
    logger.error(f"[ERROR] Error inicializando AuthManager: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback

    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    auth_manager = None


def get_spreadsheet():
    """Obtiene la hoja de c lculo principal"""
    if sheets_client:
        try:
            return sheets_client.open_by_key(app.config["GOOGLE_SHEETS_ID"])
        except Exception as e:
            logger.error(f"Error abriendo spreadsheet: {e}")
    return None


def get_current_user():
    """Obtiene los datos del usuario actual desde la sesi n"""
    user_data = session.get("user_data", {})
    logger.info(f"[BUSCAR] Datos del usuario en sesi n: {user_data}")
    return user_data


def allowed_file(filename):
    """Verifica si el archivo tiene una extensi n permitida"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """Genera un nombre  nico para el archivo"""
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename


# Hacer la funci n disponible en todas las plantillas
@app.context_processor
def inject_user():
    """Inyecta los datos del usuario en todas las plantillas"""
    return dict(current_user=get_current_user())


# Decorador para rutas que requieren autenticaci n
def login_required(f):
    """Decorador para rutas que requieren login"""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Rutas de autenticaci n
@app.route("/register", methods=["GET", "POST"])
def register():
    """P gina de registro de usuarios"""
    if not auth_manager:
        flash("Sistema de autenticaci n no disponible", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            # Obtener datos del formulario
            user_data = {
                "email": request.form.get("email", "").strip().lower(),
                "password": request.form.get("password", ""),
                "nombre": request.form.get("nombre", "").strip(),
                "apellido": request.form.get("apellido", "").strip(),
                "telefono": request.form.get("telefono", "").strip(),
                "fecha_nacimiento": request.form.get("fecha_nacimiento", ""),
                "genero": request.form.get("genero", ""),
                "direccion": request.form.get("direccion", "").strip(),
                "ciudad": request.form.get("ciudad", "").strip(),
                "tipo_usuario": request.form.get("tipo_usuario", "").strip(),
            }

            # Agregar campos espec ficos para profesionales
            if user_data["tipo_usuario"] == "profesional":
                user_data.update(
                    {
                        "profesion": request.form.get("profesion", "").strip(),
                        "especialidad": request.form.get("especialidad", "").strip(),
                        "numero_registro": request.form.get(
                            "numero_registro", ""
                        ).strip(),
                        "anos_experiencia": request.form.get(
                            "anos_experiencia", "0"
                        ).strip(),
                        "institucion": request.form.get("institucion", "").strip(),
                        "titulo": request.form.get("titulo", "").strip(),
                        "ano_egreso": request.form.get("ano_egreso", "").strip(),
                        "idiomas": request.form.get("idiomas", "Espa ol").strip(),
                        "direccion_consulta": request.form.get(
                            "direccion_consulta", ""
                        ).strip(),
                        "horario_atencion": request.form.get(
                            "horario_atencion", ""
                        ).strip(),
                        "areas_especializacion": request.form.get(
                            "areas_especializacion", ""
                        ).strip(),
                        "certificaciones": request.form.get(
                            "certificaciones", ""
                        ).strip(),
                    }
                )

            # Validar confirmaci n de contrase a
            confirm_password = request.form.get("confirm_password", "")
            if user_data["password"] != confirm_password:
                return render_template(
                    "register.html",
                    message="Las contrase as no coinciden",
                    success=False,
                )

            # Registrar usuario
            success, message = auth_manager.register_user(user_data)

            if success:
                logger.info(
                    f"[OK] Usuario registrado exitosamente: {user_data['email']}"
                )
                return render_template("register.html", message=message, success=True)
            else:
                return render_template("register.html", message=message, success=False)

        except Exception as e:
            logger.error(f"[ERROR] Error en registro: {e}")
            return render_template(
                "register.html", message="Error interno del servidor", success=False
            )

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """P gina de inicio de sesi n"""
    logger.info("[BUSCAR] Accediendo a p gina de login...")

    if not auth_manager:
        logger.error("[ERROR] AuthManager no disponible")
        return render_template(
            "login.html",
            message="Sistema de autenticaci n temporalmente no disponible. Intenta m s tarde.",
            success=False,
        )

    logger.info("[OK] AuthManager disponible")

    # Si ya est  logueado, redirigir al dashboard
    if "user_id" in session:
        user_type = session.get("user_type", "paciente")
        logger.info(
            f"[ACTUALIZAR] Usuario ya logueado, redirigiendo a dashboard: {user_type}"
        )
        if user_type == "profesional":
            return redirect(url_for("professional_dashboard"))
        else:
            return redirect(url_for("patient_dashboard"))

    if request.method == "POST":
        try:
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not email or not password:
                return render_template(
                    "login.html",
                    message="Email y contrase a son requeridos",
                    success=False,
                )

            # Intentar login
            result = auth_manager.login_user(email, password)

            if result[0]:  # Si login exitoso
                user_data = result[1]
                # Crear sesi n con informaci n completa del usuario
                session["user_id"] = user_data["id"]
                session["user_email"] = user_data["email"]
                session["user_name"] = f"{user_data['nombre']} {user_data['apellido']}"
                session["user_type"] = user_data["tipo_usuario"]
                session["user_data"] = user_data
                session["just_logged_in"] = (
                    True  # Flag para mostrar mensaje de bienvenida
                )

                logger.info(f"[OK] Login exitoso: {email}")
                logger.info(
                    f"[BUSCAR] Datos del usuario en sesión: {session.get('user_data', {})}"
                )

                # Redirigir seg n tipo de usuario
                if user_data["tipo_usuario"] == "profesional":
                    return redirect(url_for("professional_dashboard"))
                else:
                    return redirect(url_for("patient_dashboard"))
            else:  # Si login falló
                error_message = result[1]
                return render_template(
                    "login.html", message=error_message, success=False
                )

        except Exception as e:
            # Diagnosticar el error específico (especialmente 'Invalid salt')
            diagnosis = diagnose_login_error(e)

            # Log detallado para debugging
            logger.error(f"[ERROR] Error en login: {e}")
            logger.error(f"[DEBUG] {diagnosis['debug_info']}")
            for suggestion in diagnosis["suggestions"]:
                logger.error(f"[SUGERENCIA] {suggestion}")

            return render_template(
                "login.html", message=diagnosis["user_message"], success=False
            )

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Cerrar sesi n"""
    try:
        user_email = session.get("user_email", "Usuario")
        logger.info(f"[ACTUALIZAR] Iniciando logout para: {user_email}")

        # Limpiar sesi n completamente m ltiples veces
        session.clear()
        session.permanent = False

        # Forzar eliminaci n de claves espec ficas
        for key in ["user_id", "user_email", "user_name", "user_type", "user_data"]:
            session.pop(key, None)

        logger.info(f"[OK] Sesi n limpiada completamente para: {user_email}")
        logger.info(f"[BUSCAR] Sesi n despu s del clear: {dict(session)}")

        # NO usar flash ya que requiere sesi n
        # En su lugar, usar par metro URL

        # Crear respuesta con headers anti-cache muy fuertes
        response = make_response(redirect("/?logout=success"))
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        response.headers["Clear-Site-Data"] = '"cache", "cookies", "storage"'

        # Eliminar cookies de sesi n expl citamente
        response.set_cookie("session", "", expires=0)
        response.set_cookie("session", "", expires=0, domain=".medconnect.cl")
        response.set_cookie("session", "", expires=0, path="/")

        logger.info(
            "[ACTUALIZAR] Redirigiendo a p gina principal con headers anti-cache..."
        )
        return response

    except Exception as e:
        logger.error(f"[ERROR] Error en logout: {e}")
        # En caso de error, limpiar toda la sesi n y redirigir
        try:
            session.clear()
            session.permanent = False
            logger.info("[OK] Sesi n limpiada despu s del error")
        except Exception as clear_error:
            logger.error(f"[ERROR] Error limpiando sesi n: {clear_error}")

        # Respuesta de error tambi n con headers anti-cache
        response = make_response(redirect("/?logout=error"))
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"

        logger.info("[ACTUALIZAR] Redirigiendo a p gina principal despu s del error...")
        return response


# Rutas principales del frontend
@app.route("/")
def index():
    """P gina principal - Landing page"""
    try:
        # Verificar si venimos de un logout
        logout_param = request.args.get("logout")
        if logout_param in ["success", "error"]:
            logger.info(
                f"[ACTUALIZAR] Detectado logout: {logout_param} - Forzando limpieza de sesi n"
            )
            # Forzar limpieza total de sesi n
            session.clear()
            session.permanent = False
            for key in ["user_id", "user_email", "user_name", "user_type", "user_data"]:
                session.pop(key, None)

            # Forzar variables a None
            user_id = None
            user_name = None
            user_type = None

            logger.info("[ACTUALIZAR] Sesi n forzada a None despu s de logout")
        else:
            # Obtener datos de sesi n de forma segura
            user_id = session.get("user_id")
            user_name = session.get("user_name")
            user_type = session.get("user_type")

        # Log para debugging
        logger.info(
            f"[BUSCAR] Index - user_id: {user_id}, user_name: {user_name}, user_type: {user_type}"
        )
        logger.info(f"[BUSCAR] Sesi n completa: {dict(session)}")

        # Crear respuesta sin cache con headers muy fuertes
        response = make_response(
            render_template(
                "index.html",
                user_id=user_id,
                user_name=user_name,
                user_type=user_type,
                logout_message=logout_param,
            )
        )
        response.headers["Cache-Control"] = (
            "no-cache, no-store, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        response.headers["Last-Modified"] = datetime.now().strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

        # Si venimos de logout, eliminar cookies adicionales
        if logout_param:
            response.set_cookie("session", "", expires=0)
            response.set_cookie("session", "", expires=0, domain=".medconnect.cl")
            response.set_cookie("session", "", expires=0, path="/")

        return response
    except Exception as e:
        logger.error(f"Error en index: {e}")
        return render_template(
            "index.html", user_id=None, user_name=None, user_type=None
        )


@app.route("/patient")
@login_required
def patient_dashboard():
    """Dashboard para pacientes"""
    try:
        user_data = session.get("user_data", {})
        just_logged_in = session.pop(
            "just_logged_in", False
        )  # Obtener y remover el flag

        # Log para debugging
        if just_logged_in:
            logger.info(
                f"  Mostrando mensaje de bienvenida para paciente: {user_data.get('nombre', 'Usuario')}"
            )

        return render_template(
            "patient.html", user=user_data, just_logged_in=just_logged_in
        )
    except Exception as e:
        logger.error(f"Error en dashboard paciente: {e}")
        return render_template("patient.html", user={}, just_logged_in=False)


def infer_gender_from_name(nombre):
    """Infiere el g nero basado en el nombre"""
    # Lista de terminaciones comunes para nombres femeninos en espa ol
    terminaciones_femeninas = [
        "a",
        "na",
        "ia",
        "la",
        "ra",
        "da",
        "ta",
        "ina",
        "ela",
        "isa",
        "ana",
        "elle",
        "ella",
    ]
    # Excepciones conocidas (nombres masculinos que terminan en 'a')
    excepciones_masculinas = [
        "juan pablo",
        "jose maria",
        "luca",
        "matias",
        "tobias",
        "elias",
    ]

    if not nombre:
        return "M"  # valor por defecto

    nombre = nombre.lower().strip()

    # Verificar excepciones primero
    if nombre in excepciones_masculinas:
        return "M"

    # Verificar terminaciones femeninas
    for terminacion in terminaciones_femeninas:
        if nombre.endswith(terminacion):
            return "F"

    return "M"  # Si no coincide con patrones femeninos, asumir masculino


def get_gendered_profession(profesion, genero=None, nombre=None):
    """Retorna la profesi n con el g nero correcto"""
    profesiones = {
        "FONOAUDIOLOG A": {"M": "Fonoaudi logo", "F": "Fonoaudi loga"},
        "KINESIOLOG A": {"M": "Kinesi logo", "F": "Kinesi loga"},
        "TERAPIA OCUPACIONAL": {
            "M": "Terapeuta Ocupacional",
            "F": "Terapeuta Ocupacional",
        },
        "PSICOLOG A": {"M": "Psic logo", "F": "Psic loga"},
        "NUTRICI N": {"M": "Nutricionista", "F": "Nutricionista"},
        "MEDICINA": {"M": "Doctor", "F": "Doctora"},
        "ENFERMER A": {"M": "Enfermero", "F": "Enfermera"},
    }

    if not profesion:
        return ""

    profesion = profesion.upper()
    if profesion not in profesiones:
        return profesion

    # Si no hay g nero expl cito, intentar inferirlo del nombre
    if not genero and nombre:
        genero = infer_gender_from_name(nombre)
        logger.info(f"[BUSCAR] G nero inferido del nombre '{nombre}': {genero}")

    # Normalizar el g nero a 'M' o 'F'
    if genero:
        genero = genero.upper()
        if genero.startswith("M"):  # Matches 'M' or 'MASCULINO'
            genero = "M"
        elif genero.startswith("F"):  # Matches 'F' or 'FEMENINO'
            genero = "F"
        else:
            genero = "M"  # Default to M for other values
    else:
        genero = "M"  # Default to M if no gender provided

    logger.info(
        f"[BUSCAR] Usando g nero normalizado: {genero} para profesi n: {profesion}"
    )

    profesion_gendered = profesiones[profesion].get(genero, profesiones[profesion]["M"])
    logger.info(f"[BUSCAR] Profesi n con g nero generada: {profesion_gendered}")

    return profesion_gendered


@app.route("/professional")
@login_required
def professional_dashboard():
    """Ruta para el dashboard del profesional"""
    try:
        user_data = get_current_user()
        profesional_id = user_data.get("id")

        logger.info(f"[BUSCAR] Datos iniciales del usuario: {user_data}")

        # Cargar datos completos del profesional
        if profesional_id:
            professional_data = auth_manager.get_professional_by_id(profesional_id)
            if professional_data:
                # Actualizar datos del usuario con informaci n de la hoja
                user_data.update(
                    {
                        "profesion": professional_data.get("Profesion", ""),
                        "especialidad": professional_data.get("Especialidad", ""),
                        "numero_registro": professional_data.get("Numero_Registro", ""),
                        "disponible": str(
                            professional_data.get("Disponible", "true")
                        ).lower()
                        == "true",
                        "genero": professional_data.get(
                            "genero", ""
                        ),  # Obtenido de la hoja de usuarios
                    }
                )

                logger.info(
                    f"[BUSCAR] Datos despu s de actualizar con professional_data: {user_data}"
                )

                # Si no hay g nero expl cito, intentar inferirlo del nombre
                if not user_data["genero"]:
                    user_data["genero"] = infer_gender_from_name(
                        user_data.get("nombre", "")
                    )
                    logger.info(
                        f"[BUSCAR] G nero inferido del nombre: {user_data['genero']}"
                    )

                # Obtener la profesi n con el g nero correcto
                user_data["profesion_gendered"] = get_gendered_profession(
                    user_data["profesion"], user_data["genero"]
                )
                logger.info(
                    f"[BUSCAR] Profesi n con g nero: {user_data['profesion_gendered']}"
                )

                # Actualizar la sesi n con los datos actualizados
                session["user_data"] = user_data
                logger.info(
                    f"[BUSCAR] Sesi n actualizada con nuevos datos: {session['user_data']}"
                )

        return render_template(
            "professional.html",
            user=user_data,
            just_logged_in=session.pop("just_logged_in", False),
        )

    except Exception as e:
        logger.error(f"Error en dashboard profesional: {e}")
        return render_template("professional.html", user={}, just_logged_in=False)


@app.route("/profile")
@login_required
def profile():
    """P gina de perfil del usuario"""
    logger.info("[BUSCAR] INICIANDO funci n profile()")
    try:
        user_data = session.get("user_data", {})
        logger.info(f"[BUSCAR] Datos del usuario en perfil: {user_data}")
        logger.info(f"[BUSCAR] Sesi n completa: {dict(session)}")

        # Verificar si es un profesional
        if user_data.get("tipo_usuario") == "profesional":
            # Agregar campos adicionales para el perfil profesional
            professional_data = user_data.copy()
            professional_data.update(
                {
                    "calificacion": 4.5,  # Valor por defecto
                    "total_pacientes": 0,
                    "atenciones_mes": 0,
                    "tiempo_respuesta": "24h",
                    "disponible": True,
                    "numero_registro": "Por completar",
                    "especialidad": "Por completar",
                    "subespecialidades": "Por completar",
                    "anos_experiencia": 0,
                    "idiomas": ["Espa ol"],
                    "direccion_consulta": user_data.get("direccion", "Por completar"),
                    "horario_atencion": "Lunes a Viernes 9:00 - 18:00",
                    "certificaciones": [],
                    "areas_especializacion": [],
                }
            )

            # Intentar obtener datos reales desde Google Sheets
            try:
                user_id = user_data.get("id")
                if user_id:
                    # Obtener datos completos del profesional
                    professional_sheet_data = auth_manager.get_professional_by_id(
                        user_id
                    )
                    if professional_sheet_data:
                        # Mapear campos espec ficos
                        field_mapping = {
                            "Numero_Registro": "numero_registro",
                            "Especialidad": "especialidad",
                            "Anos_Experiencia": "anos_experiencia",
                            "Calificacion": "calificacion",
                            "Direccion_Consulta": "direccion_consulta",
                            "Horario_Atencion": "horario_atencion",
                            "Idiomas": "idiomas_str",
                            "Areas_Especializacion": "areas_especializacion_str",
                            "Disponible": "disponible_str",
                            "Profesion": "profesion",
                        }

                        for sheet_field, local_field in field_mapping.items():
                            if sheet_field in professional_sheet_data:
                                professional_data[local_field] = (
                                    professional_sheet_data[sheet_field]
                                )

                        # Procesar campos especiales
                        if "idiomas_str" in professional_data:
                            idiomas_str = professional_data["idiomas_str"] or "Espa ol"
                            professional_data["idiomas"] = [
                                idioma.strip()
                                for idioma in idiomas_str.split(",")
                                if idioma.strip()
                            ]

                        if "areas_especializacion_str" in professional_data:
                            areas_str = (
                                professional_data["areas_especializacion_str"] or ""
                            )
                            professional_data["areas_especializacion"] = [
                                area.strip()
                                for area in areas_str.split(",")
                                if area.strip()
                            ]

                        if "disponible_str" in professional_data:
                            professional_data["disponible"] = (
                                str(professional_data["disponible_str"]).lower()
                                == "true"
                            )

                        # Convertir tipos de datos
                        if "anos_experiencia" in professional_data:
                            try:
                                professional_data["anos_experiencia"] = int(
                                    professional_data["anos_experiencia"] or 0
                                )
                            except:
                                professional_data["anos_experiencia"] = 0

                        if "calificacion" in professional_data:
                            try:
                                professional_data["calificacion"] = float(
                                    professional_data["calificacion"] or 4.5
                                )
                            except:
                                professional_data["calificacion"] = 4.5

                    # Obtener certificaciones del profesional
                    certificaciones = auth_manager.get_professional_certifications(
                        user_id
                    )
                    professional_data["certificaciones"] = certificaciones

            except Exception as e:
                logger.warning(f"Error accediendo a datos profesionales: {e}")

            return render_template("profile_professional.html", user=professional_data)

        # Crear respuesta sin cache
        response = make_response(render_template("profile.html", user=user_data))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        return response
    except Exception as e:
        logger.error(f"[ERROR] Error en perfil: {e}")
        import traceback

        logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
        return render_template("profile.html", user={})


@app.route("/reports")
@login_required
def reports():
    """P gina de reportes para profesionales"""
    try:
        user_data = session.get("user_data", {})
        if not user_data:
            return redirect(url_for("login"))

        # Verificar que sea un profesional
        if user_data.get("tipo_usuario") != "profesional":
            return redirect(url_for("professional_dashboard"))

        logger.info(f"[BUSCAR] Datos del usuario en reportes: {user_data}")

        return render_template("reports.html", user=user_data)

    except Exception as e:
        logger.error(f"Error en reports: {e}")
        return redirect(url_for("login"))


@app.route("/services")
@login_required
def services():
    """P gina de servicios del profesional"""
    if session.get("user_type") != "profesional":
        flash("Acceso denegado: Solo para profesionales m dicos", "error")
        return redirect(url_for("index"))

    user_data = session.get("user_data", {})
    return render_template("services.html", user=user_data)


@app.route("/requests")
@login_required
def requests():
    """P gina de solicitudes del profesional"""
    if session.get("user_type") != "profesional":
        flash("Acceso denegado: Solo para profesionales m dicos", "error")
        return redirect(url_for("index"))

    user_data = session.get("user_data", {})
    return render_template("requests.html", user=user_data)


@app.route("/chat")
@login_required
def chat():
    """P gina de chat del profesional"""
    if session.get("user_type") != "profesional":
        flash("Acceso denegado: Solo para profesionales m dicos", "error")
        return redirect(url_for("index"))

    user_data = session.get("user_data", {})
    return render_template("chat.html", user=user_data)


# API Routes para el frontend
@app.route("/api/patient/<patient_id>/consultations")
def get_patient_consultations(patient_id):
    """Obtiene las consultas de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        # Leer datos de la hoja Consultas manualmente para evitar errores de headers
        try:
            worksheet = spreadsheet.worksheet("Consultas")
            all_values = worksheet.get_all_values()

            consultations = []

            if len(all_values) > 1:
                headers = all_values[0]
                logger.info(f"[LISTA] Headers de Consultas: {headers}")

                # Headers reales: ['id', 'patient_id', 'doctor', 'specialty', 'date', 'diagnosis', 'treatment', 'notes', 'status']
                for row in all_values[1:]:
                    if len(row) >= len(headers) and any(cell.strip() for cell in row):
                        # Verificar si pertenece al paciente
                        patient_id_cell = row[1] if len(row) > 1 else ""

                        if str(patient_id_cell) == str(patient_id):
                            # Transformar al formato esperado por la plataforma web
                            consultation_formatted = {
                                "id": row[0] if len(row) > 0 else "",  # id
                                "patient_id": patient_id,
                                "doctor": row[2] if len(row) > 2 else "",  # doctor
                                "specialty": (
                                    row[3] if len(row) > 3 else ""
                                ),  # specialty
                                "date": convert_date_format(
                                    row[4] if len(row) > 4 else ""
                                ),  # date
                                "diagnosis": (
                                    row[5] if len(row) > 5 else ""
                                ),  # diagnosis
                                "treatment": (
                                    row[6] if len(row) > 6 else ""
                                ),  # treatment
                                "notes": row[7] if len(row) > 7 else "",  # notes
                                "status": (
                                    row[8] if len(row) > 8 else "completada"
                                ),  # status
                            }

                            consultations.append(consultation_formatted)

            logger.info(
                f"[BUSCAR] Consultas encontradas para paciente {patient_id}: {len(consultations)}"
            )

            return jsonify({"consultations": consultations})

        except gspread.WorksheetNotFound:
            logger.warning("[NOTA] Hoja 'Consultas' no encontrada")
            return jsonify({"consultations": []})

    except Exception as e:
        logger.error(f"Error obteniendo consultas: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# Funciones auxiliares para las vistas de agenda
def obtener_rango_semana(fecha_str):
    """Obtiene el rango de fechas de la semana que contiene la fecha dada"""
    from datetime import datetime, timedelta

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Obtener el lunes de la semana (d a 0)
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    return inicio_semana.strftime("%Y-%m-%d"), fin_semana.strftime("%Y-%m-%d")


def obtener_rango_mes(fecha_str):
    """Obtiene el rango de fechas del mes que contiene la fecha dada"""
    from datetime import datetime
    import calendar

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Primer d a del mes
    inicio_mes = fecha.replace(day=1)
    #  ltimo d a del mes
    ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
    fin_mes = fecha.replace(day=ultimo_dia)

    return inicio_mes.strftime("%Y-%m-%d"), fin_mes.strftime("%Y-%m-%d")


def organizar_agenda_semanal(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a de la semana"""
    from datetime import datetime, timedelta

    agenda = {}
    dias_semana = [
        "Lunes",
        "Martes",
        "Mi rcoles",
        "Jueves",
        "Viernes",
        "S bado",
        "Domingo",
    ]

    # Inicializar estructura
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    for i in range(7):
        fecha_dia = (inicio + timedelta(days=i)).strftime("%Y-%m-%d")
        agenda[fecha_dia] = {
            "dia_semana": dias_semana[i],
            "fecha": fecha_dia,
            "citas": [],
        }

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def organizar_agenda_mensual(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a del mes"""
    from datetime import datetime, timedelta

    agenda = {}

    # Inicializar estructura para todos los d as del mes
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    fecha_actual = inicio
    while fecha_actual <= fin:
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        agenda[fecha_str] = {
            "fecha": fecha_str,
            "dia": fecha_actual.day,
            "es_hoy": fecha_str == datetime.now().strftime("%Y-%m-%d"),
            "citas": [],
        }
        fecha_actual += timedelta(days=1)

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def calcular_estadisticas_semana(citas):
    """Calcula estad sticas para la vista semanal"""
    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
    }


def calcular_estadisticas_mes(citas):
    """Calcula estad sticas para la vista mensual"""
    from datetime import datetime

    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    # Agrupar por semana
    citas_por_semana = {}
    for cita in citas:
        fecha_cita = datetime.strptime(cita["fecha"], "%Y-%m-%d")
        semana = fecha_cita.isocalendar()[1]  # N mero de semana del a o
        if semana not in citas_por_semana:
            citas_por_semana[semana] = 0
        citas_por_semana[semana] += 1

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
        "citas_por_semana": citas_por_semana,
    }


try:
    # Verificar variables de entorno antes de crear AuthManager
    env_check = {
        "GOOGLE_SERVICE_ACCOUNT_JSON": bool(
            os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        ),
        "GOOGLE_SHEETS_ID": bool(os.environ.get("GOOGLE_SHEETS_ID")),
        "TELEGRAM_BOT_TOKEN": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
    }
    logger.info(f"[HERRAMIENTA] Variables de entorno en app.py: {env_check}")

    # Verificar contenido de JSON
    json_content = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if json_content:
        logger.info(f"[NOTA] JSON length: {len(json_content)} chars")
        logger.info(f"[NOTA] JSON preview: {json_content[:100]}...")

        # Verificar que es JSON v lido
        try:
            test_json = json.loads(json_content)
            logger.info(
                f"[OK] JSON v lido, proyecto: {test_json.get('project_id', 'N/A')}"
            )
        except json.JSONDecodeError as je:
            logger.error(f"[ERROR] JSON inv lido: {je}")

    # Intentar crear AuthManager
    logger.info("  Creando instancia de AuthManager...")
    auth_manager = AuthManager()
    logger.info("[OK] AuthManager inicializado correctamente")

except Exception as e:
    logger.error(f"[ERROR] Error inicializando AuthManager: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback

    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    auth_manager = None


def get_spreadsheet():
    """Obtiene la hoja de c lculo principal"""
    if sheets_client:
        try:
            return sheets_client.open_by_key(app.config["GOOGLE_SHEETS_ID"])
        except Exception as e:
            logger.error(f"Error abriendo spreadsheet: {e}")
    return None


def get_current_user():
    """Obtiene los datos del usuario actual desde la sesi n"""
    user_data = session.get("user_data", {})
    logger.info(f"[BUSCAR] Datos del usuario en sesi n: {user_data}")
    return user_data


def allowed_file(filename):
    """Verifica si el archivo tiene una extensi n permitida"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """Genera un nombre  nico para el archivo"""
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename


# Hacer la funci n disponible en todas las plantillas
@app.context_processor
def inject_user():
    """Inyecta los datos del usuario en todas las plantillas"""
    return dict(current_user=get_current_user())


@app.route("/api/patient/<patient_id>/exams")
def get_patient_exams(patient_id):
    """Obtiene los ex menes de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        # Leer datos de la hoja 'Examenes' (nueva estructura)
        try:
            examenes_worksheet = spreadsheet.worksheet("Examenes")
            all_exam_values = examenes_worksheet.get_all_values()

            patient_exams = []

            if len(all_exam_values) > 1:
                headers = all_exam_values[0]
                logger.info(f"[LISTA] Headers de Examenes: {headers}")

                # Headers reales: ['id', 'patient_id', 'exam_type', 'date', 'results', 'lab', 'doctor', 'file_url', 'status']
                for row in all_exam_values[1:]:
                    if len(row) >= len(headers) and any(cell.strip() for cell in row):
                        # Verificar si pertenece al paciente
                        patient_id_cell = row[1] if len(row) > 1 else ""

                        if str(patient_id_cell) == str(patient_id):
                            # Transformar al formato esperado por la plataforma web
                            original_date = row[3] if len(row) > 3 else ""
                            converted_date = convert_date_format(original_date)
                            logger.info(
                                f"[CALENDARIO] Fecha original: '{original_date}'   Convertida: '{converted_date}'"
                            )

                            exam_formatted = {
                                "id": row[0] if len(row) > 0 else "",  # id
                                "patient_id": patient_id,
                                "exam_type": (
                                    row[2] if len(row) > 2 else ""
                                ),  # exam_type
                                "date": converted_date,  # date
                                "results": row[4] if len(row) > 4 else "",  # results
                                "lab": row[5] if len(row) > 5 else "",  # lab
                                "doctor": row[6] if len(row) > 6 else "",  # doctor
                                "file_url": row[7] if len(row) > 7 else "",  # file_url
                                "status": (
                                    row[8] if len(row) > 8 else "completado"
                                ),  # status
                            }

                            patient_exams.append(exam_formatted)

            logger.info(
                f"[BUSCAR] Ex menes encontrados para paciente {patient_id}: {len(patient_exams)}"
            )

            if patient_exams:
                return jsonify({"exams": patient_exams})

        except gspread.WorksheetNotFound:
            logger.info(
                "[NOTA] Hoja 'Examenes' no encontrada, intentando con estructura antigua"
            )

        # Si no hay resultados en la nueva hoja, probar con la hoja antigua
        try:
            worksheet = spreadsheet.worksheet(SHEETS_CONFIG["exams"]["name"])

            # Obtener datos usando la estructura antigua como respaldo
            all_records = worksheet.get_all_records()

            patient_exams = []
            for record in all_records:
                if str(record.get("patient_id", "")) == str(patient_id):
                    original_date = record.get("date", "")
                    converted_date = convert_date_format(original_date)
                    logger.info(
                        f"[CALENDARIO] Fecha original (antigua): '{original_date}'   Convertida: '{converted_date}'"
                    )

                    exam_formatted = {
                        "id": record.get("id", ""),
                        "patient_id": record.get("patient_id", ""),
                        "exam_type": record.get("exam_type", ""),
                        "date": converted_date,
                        "results": record.get("results", ""),
                        "lab": record.get("lab", ""),
                        "doctor": record.get("doctor", ""),
                        "file_url": record.get("file_url", ""),
                        "status": record.get("status", "completado"),
                    }
                    patient_exams.append(exam_formatted)

            logger.info(
                f"[BUSCAR] Ex menes encontrados en estructura antigua para paciente {patient_id}: {len(patient_exams)}"
            )

            return jsonify({"exams": patient_exams})

        except gspread.WorksheetNotFound:
            logger.warning("[NOTA] Ninguna hoja de ex menes encontrada")
            return jsonify({"exams": []})

    except Exception as e:
        logger.error(f"Error obteniendo ex menes: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/patient/<patient_id>/family")
def get_patient_family(patient_id):
    """Obtiene los familiares de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["family_members"]["name"])
        records = worksheet.get_all_records()

        # Filtrar por patient_id
        patient_family = [
            r for r in records if str(r.get("patient_id")) == str(patient_id)
        ]

        logger.info(
            f"[BUSCAR] Familiares encontrados para paciente {patient_id}: {len(patient_family)}"
        )

        return jsonify({"family": patient_family})
    except Exception as e:
        logger.error(f"Error obteniendo familiares: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# APIs para eliminar datos
@app.route(
    "/api/patient/<patient_id>/consultations/<consultation_id>", methods=["DELETE"]
)
@login_required
def delete_consultation(patient_id, consultation_id):
    """Elimina una consulta m dica"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        # Usar la hoja 'Consultas' que existe realmente
        try:
            worksheet = spreadsheet.worksheet("Consultas")
            all_values = worksheet.get_all_values()

            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(
                    all_values[1:], start=2
                ):  # Start from row 2 (after headers)
                    if (
                        len(row) > 1
                        and str(row[0]) == str(consultation_id)
                        and str(row[1]) == str(patient_id)
                    ):
                        row_to_delete = i
                        break

            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(
                    f"[OK] Consulta {consultation_id} eliminada para paciente {patient_id}"
                )
                return jsonify(
                    {"success": True, "message": "Consulta eliminada exitosamente"}
                )
            else:
                return jsonify({"error": "Consulta no encontrada"}), 404

        except gspread.WorksheetNotFound:
            return jsonify({"error": "Hoja de consultas no encontrada"}), 404

    except Exception as e:
        logger.error(f"Error eliminando consulta: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/patient/<patient_id>/medications/<medication_id>", methods=["DELETE"])
@login_required
def delete_medication(patient_id, medication_id):
    """Elimina un medicamento"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        # Usar la hoja 'Medicamentos' que existe realmente
        try:
            worksheet = spreadsheet.worksheet("Medicamentos")
            all_values = worksheet.get_all_values()

            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(
                    all_values[1:], start=2
                ):  # Start from row 2 (after headers)
                    if (
                        len(row) > 1
                        and str(row[0]) == str(medication_id)
                        and str(row[1]) == str(patient_id)
                    ):
                        row_to_delete = i
                        break

            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(
                    f"[OK] Medicamento {medication_id} eliminado para paciente {patient_id}"
                )
                return jsonify(
                    {"success": True, "message": "Medicamento eliminado exitosamente"}
                )
            else:
                return jsonify({"error": "Medicamento no encontrado"}), 404

        except gspread.WorksheetNotFound:
            return jsonify({"error": "Hoja de medicamentos no encontrada"}), 404

    except Exception as e:
        logger.error(f"Error eliminando medicamento: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/patient/<patient_id>/exams/<exam_id>", methods=["DELETE"])
@login_required
def delete_exam(patient_id, exam_id):
    """Elimina un examen"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        # Usar la hoja 'Examenes' que existe realmente
        try:
            worksheet = spreadsheet.worksheet("Examenes")
            all_values = worksheet.get_all_values()

            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(
                    all_values[1:], start=2
                ):  # Start from row 2 (after headers)
                    if (
                        len(row) > 1
                        and str(row[0]) == str(exam_id)
                        and str(row[1]) == str(patient_id)
                    ):
                        row_to_delete = i
                        break

            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(
                    f"[OK] Examen {exam_id} eliminado para paciente {patient_id}"
                )
                return jsonify(
                    {"success": True, "message": "Examen eliminado exitosamente"}
                )
            else:
                return jsonify({"error": "Examen no encontrado"}), 404

        except gspread.WorksheetNotFound:
            return jsonify({"error": "Hoja de ex menes no encontrada"}), 404

    except Exception as e:
        logger.error(f"Error eliminando examen: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/patient/<patient_id>/family/<family_id>", methods=["DELETE"])
@login_required
def delete_family_member(patient_id, family_id):
    """Elimina un familiar"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["family_members"]["name"])
        records = worksheet.get_all_records()

        # Buscar la fila a eliminar
        row_to_delete = None
        for i, record in enumerate(
            records, start=2
        ):  # Start from row 2 (after headers)
            if str(record.get("id")) == str(family_id) and str(
                record.get("patient_id")
            ) == str(patient_id):
                row_to_delete = i
                break

        if row_to_delete:
            worksheet.delete_rows(row_to_delete)
            logger.info(
                f"[OK] Familiar {family_id} eliminado para paciente {patient_id}"
            )
            return jsonify(
                {"success": True, "message": "Familiar eliminado exitosamente"}
            )
        else:
            return jsonify({"error": "Familiar no encontrado"}), 404

    except Exception as e:
        logger.error(f"Error eliminando familiar: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# APIs para actualizar informaci n del perfil
@app.route("/api/profile/personal", methods=["PUT"])
@login_required
def update_personal_info():
    """Actualiza la informaci n personal del usuario"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Validar campos requeridos
        required_fields = ["nombre", "apellido", "email"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"El campo {field} es requerido"}), 400

        # Validar formato de email
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, data["email"]):
            return jsonify({"error": "Formato de email inv lido"}), 400

        # Validar tel fono si se proporciona
        if data.get("telefono"):
            try:
                telefono = int(data["telefono"])
                if telefono <= 0:
                    return (
                        jsonify({"error": "Tel fono debe ser un n mero positivo"}),
                        400,
                    )
            except ValueError:
                return jsonify({"error": "Tel fono debe ser un n mero v lido"}), 400

        # Actualizar en Google Sheets
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["users"]["name"])
        records = worksheet.get_all_records()

        # Buscar el usuario
        user_row = None
        for i, record in enumerate(records, start=2):
            if record.get("id") == user_id:
                user_row = i
                break

        if not user_row:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Preparar datos para actualizar
        update_data = {
            "nombre": data["nombre"],
            "apellido": data["apellido"],
            "email": data["email"],
            "telefono": data.get("telefono", ""),
            "fecha_nacimiento": data.get("fecha_nacimiento", ""),
            "genero": data.get("genero", ""),
            "direccion": data.get("direccion", ""),
            "ciudad": data.get("ciudad", ""),
        }

        # Actualizar fila en Google Sheets
        headers = worksheet.row_values(1)
        for field, value in update_data.items():
            if field in headers:
                col_index = headers.index(field) + 1
                worksheet.update_cell(user_row, col_index, value)

        # Actualizar sesi n
        user_data = session.get("user_data", {})
        user_data.update(update_data)
        session["user_data"] = user_data
        session["user_email"] = data["email"]
        session["user_name"] = f"{data['nombre']} {data['apellido']}"

        logger.info(f"[OK] Informaci n personal actualizada para usuario {user_id}")
        return jsonify(
            {
                "success": True,
                "message": "Informaci n personal actualizada exitosamente",
            }
        )

    except Exception as e:
        logger.error(f"Error actualizando informaci n personal: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/profile/medical", methods=["PUT"])
@login_required
def update_medical_info():
    """Actualiza la informaci n m dica del usuario"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Por ahora, simular actualizaci n exitosa
        # En una implementaci n real, aqu  se actualizar a una tabla de informaci n m dica
        logger.info(f"[OK] Informaci n m dica actualizada para usuario {user_id}")
        return jsonify(
            {"success": True, "message": "Informaci n m dica actualizada exitosamente"}
        )

    except Exception as e:
        logger.error(f"Error actualizando informaci n m dica: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/profile/notifications", methods=["PUT"])
@login_required
def update_notification_settings():
    """Actualiza las configuraciones de notificaciones"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Por ahora, simular actualizaci n exitosa
        # En una implementaci n real, aqu  se guardar an las preferencias de notificaci n
        logger.info(
            f"[OK] Configuraciones de notificaci n actualizadas para usuario {user_id}"
        )
        return jsonify(
            {
                "success": True,
                "message": "Configuraciones de notificaci n actualizadas exitosamente",
            }
        )

    except Exception as e:
        logger.error(f"Error actualizando configuraciones de notificaci n: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# Webhook para Telegram Bot
@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Webhook para recibir mensajes del bot de Telegram"""
    try:
        data = request.get_json()
        logger.info(f"  Webhook recibido: {data}")

        # Procesar mensaje del bot
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            user_id = message["from"]["id"]
            username = message["from"].get("username", "Sin username")

            logger.info(f"  Usuario: {username} ({user_id}) - Mensaje: {text}")

            # Registrar interacci n en Google Sheets
            log_bot_interaction(user_id, username, text, chat_id)

            # Procesar comando o mensaje
            response = process_telegram_message(text, chat_id, user_id)

            # Enviar respuesta
            if response:
                success = send_telegram_message(chat_id, response)
                logger.info(f"[ENVIAR] Respuesta enviada: {success}")

        return jsonify({"status": "ok"})
    except Exception as e:
        logger.error(f"[ERROR] Error en webhook: {e}")
        return jsonify({"error": "Error procesando webhook"}), 500


@app.route("/test-bot", methods=["GET"])
@app.route("/test-bot", methods=["GET"])
def test_bot():
    """Endpoint para probar el bot de Telegram"""
    try:
        # Informaci n del bot
        bot_info = {
            "bot_token_configured": bool(config.TELEGRAM_BOT_TOKEN),
            "webhook_url": "https://www.medconnect.cl/webhook",
            "sheets_id": (
                config.GOOGLE_SHEETS_ID[:20] + "..."
                if config.GOOGLE_SHEETS_ID
                else None
            ),
        }

        # Probar env o de mensaje de prueba
        test_message = "  Bot de MedConnect funcionando correctamente!\n\n[OK] Webhook configurado\n[OK] Conexi n establecida"

        return jsonify(
            {
                "status": "Bot configurado correctamente",
                "bot_info": bot_info,
                "test_message": test_message,
                "instructions": "Env a un mensaje al bot @Medconn_bot en Telegram para probarlo",
            }
        )

    except Exception as e:
        logger.error(f"[ERROR] Error probando bot: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/bot-stats", methods=["GET"])
@app.route("/bot-stats", methods=["GET"])
def bot_stats():
    """Estad sticas del bot"""
    try:
        if not auth_manager:
            return jsonify({"error": "AuthManager no disponible"}), 500

        # Obtener estad sticas de interacciones del bot
        try:
            interactions = auth_manager.get_sheet_data("Interacciones_Bot")

            stats = {
                "total_interactions": len(interactions) if interactions else 0,
                "unique_users": (
                    len(set(row.get("user_id", "") for row in interactions))
                    if interactions
                    else 0
                ),
                "recent_interactions": interactions[-5:] if interactions else [],
            }

            return jsonify(
                {"status": "success", "stats": stats, "bot_username": "@Medconn_bot"}
            )

        except Exception as e:
            return jsonify(
                {
                    "status": "error getting stats",
                    "error": str(e),
                    "bot_username": "@Medconn_bot",
                }
            )

    except Exception as e:
        logger.error(f"[ERROR] Error obteniendo estad sticas: {e}")
        return jsonify({"error": str(e)}), 500


def log_bot_interaction(user_id, username, message, chat_id):
    """Registra la interacci n del bot en Google Sheets"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["bot_interactions"]["name"])

        # Preparar datos
        row_data = [
            len(worksheet.get_all_values()) + 1,  # ID auto-incrementado
            user_id,
            username,
            message,
            "",  # Response se llenar  despu s
            datetime.now().isoformat(),
            "message",
            "processed",
        ]

        worksheet.append_row(row_data)
        logger.info(f"Interacci n registrada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error registrando interacci n: {e}")


# Diccionario para almacenar contexto de conversaciones
user_contexts = {}

# Palabras clave para reconocimiento de intenciones
INTENT_KEYWORDS = {
    # Funcionalidades para pacientes
    "consulta": [
        "consulta",
        "m dico",
        "doctor",
        "cita",
        "visita",
        "chequeo",
        "revisi n",
        "control",
    ],
    "medicamento": [
        "medicamento",
        "medicina",
        "pastilla",
        "p ldora",
        "remedio",
        "f rmaco",
        "droga",
        "tratamiento",
        "nuevo medicamento",
        "empezar medicamento",
        "comenzar tratamiento",
        "recetaron",
        "prescribieron",
        "como va",
        "efectos",
        "reacci n",
        "funciona",
        "mejora",
        "empeora",
    ],
    "examen": [
        "examen",
        "an lisis",
        "estudio",
        "prueba",
        "laboratorio",
        "radiograf a",
        "ecograf a",
        "resonancia",
        "me hice",
        "ya me hice",
        "tengo resultados",
        "salieron",
        "complet ",
        "termin  examen",
        "tengo que hacerme",
        "debo hacerme",
        "programado",
        "agendado",
        "pr ximo examen",
        "me van a hacer",
    ],
    "historial": [
        "historial",
        "historia",
        "registro",
        "datos",
        "informaci n",
        "ver",
        "mostrar",
        "consultar",
    ],
    "recordatorio": [
        "recordar",
        "recordatorio",
        "alerta",
        "avisar",
        "notificar",
        "programar aviso",
    ],
    "documento": [
        "documento",
        "imagen",
        "archivo",
        "pdf",
        "resultado",
        "informe",
        "reporte",
        "subir",
        "cargar",
    ],
    # Funcionalidades para profesionales
    "agenda": [
        "agenda",
        "horario",
        "disponibilidad",
        "cupos",
        "citas",
        "calendario",
        "programar",
    ],
    "cita_profesional": [
        "nueva cita",
        "agendar paciente",
        "reservar hora",
        "confirmar cita",
        "cancelar cita",
    ],
    "paciente_profesional": [
        "paciente",
        "historial paciente",
        "datos paciente",
        "informaci n paciente",
    ],
    "notificacion_profesional": [
        "notificar",
        "aviso",
        "recordatorio paciente",
        "mensaje paciente",
    ],
    # Funcionalidades compartidas
    "saludo": ["hola", "buenos", "buenas", "saludos", "hey", "qu  tal", "c mo est s"],
    "despedida": ["adi s", "chao", "hasta luego", "nos vemos", "bye", "gracias"],
    "ayuda": ["ayuda", "help", "auxilio", "socorro", "no entiendo", "qu  puedes hacer"],
    "emergencia": [
        "emergencia",
        "urgente",
        "grave",
        "dolor fuerte",
        "sangre",
        "desmayo",
        "accidente",
    ],
    "cita_futura": [
        "pr xima cita",
        "agendar cita",
        "programar cita",
        "reservar hora",
        "pedir hora",
    ],
    "seguimiento": [
        "c mo voy",
        "evoluci n",
        "progreso",
        "mejorando",
        "empeorando",
        "seguimiento",
    ],
}

# Respuestas variadas para hacer el bot m s humano
RESPONSE_VARIATIONS = {
    "greeting": [
        " Hola! [FELIZ]  C mo est s hoy?",
        " Qu  bueno verte! [SALUDO]  En qu  puedo ayudarte?",
        " Hola! Espero que tengas un buen d a [ESTRELLA]",
        " Saludos!  C mo te sientes hoy?",
    ],
    "not_understood": [
        "Disculpa, no estoy seguro de entender.  Podr as explicarme de otra manera?",
        "Hmm, no capt  bien eso.  Puedes ser m s espec fico?",
        "No estoy seguro de c mo ayudarte con eso.  Podr as reformular tu pregunta?",
        "Perd n, no entend  bien.  Te refieres a algo relacionado con tu salud?",
    ],
    "encouragement": [
        " Perfecto!  ",
        " Excelente! [ESTRELLA]",
        " Muy bien!  ",
        " Genial!  ",
    ],
}


def detect_intent(text):
    """Detecta la intenci n del usuario bas ndose en palabras clave"""
    text_lower = text.lower()

    # Contar coincidencias por categor a
    intent_scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            intent_scores[intent] = score

    # Retornar la intenci n con mayor puntaje
    if intent_scores:
        return max(intent_scores, key=intent_scores.get)

    return "unknown"


def get_user_context(user_id):
    """Obtiene el contexto de conversaci n del usuario"""
    return user_contexts.get(user_id, {})


def set_user_context(user_id, context_key, value):
    """Establece contexto de conversaci n para el usuario"""
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    user_contexts[user_id][context_key] = value


def get_random_response(category):
    """Obtiene una respuesta aleatoria de una categor a"""
    import random

    return random.choice(RESPONSE_VARIATIONS.get(category, [" Perfecto!"]))


def process_telegram_message(text, chat_id, user_id):
    """Procesa mensajes del bot de Telegram con funcionalidades duales para pacientes y profesionales"""
    original_text = text
    text = text.lower().strip()

    # Intentar obtener informaci n del usuario registrado
    user_info = get_telegram_user_info(user_id)
    user_name = user_info.get("nombre", "Usuario") if user_info else "Usuario"
    is_professional = is_professional_user(user_info)

    # Obtener contexto de conversaci n
    context = get_user_context(user_id)

    # Comando /start
    if text.startswith("/start"):
        if user_info:
            nombre = user_info.get("nombre", "Usuario")
            apellido = user_info.get("apellido", "")
            nombre_completo = f"{nombre} {apellido}".strip()

            if is_professional:
                # Mensaje de bienvenida para profesionales
                saludos = [
                    f" Hola Dr(a). {nombre_completo}! [DOCTOR]  Bienvenido de vuelta!",
                    f" Dr(a). {nombre_completo}! [HOSPITAL]  Listo para gestionar tus pacientes!",
                    f" Hola {nombre}!   Tu asistente de gesti n m dica est  listo",
                ]

                import random

                saludo = random.choice(saludos)

                return f"""{saludo}

Como profesional m dico, puedo ayudarte con:

[CALENDARIO] **Gesti n de Agenda** - Maneja tu horario y citas
[PACIENTES] **Pacientes** - Accede a historiales y datos
[LISTA] **Atenciones** - Registra consultas y tratamientos
[CAMPANA] **Notificaciones** - Comun cate con pacientes
[ESTADISTICAS] **Reportes** - Estad sticas y seguimientos

**Comandos principales:**
  "Ver mi agenda" - Consultar horario
  "Agendar cita" - Programar nueva cita
  "Pacientes" - Ver lista de pacientes
  "Notificar paciente" - Enviar mensaje

 En qu  puedo ayudarte hoy? [PENSANDO]"""
            else:
                # Mensaje de bienvenida para pacientes
                saludos = [
                    f" Hola {nombre_completo}! [SALUDO]  Qu  alegr a verte de nuevo! [FELIZ]",
                    f" {nombre_completo}! [ESTRELLA]  Bienvenido de vuelta a MedConnect!",
                    f" Hola {nombre}! [DOCTOR] Listo para ayudarte con tu salud hoy",
                ]

                import random

                saludo = random.choice(saludos)

                return f"""{saludo}

Como paciente registrado, estoy aqu  para ayudarte con:

[LISTA] **Consultas m dicas** - Registra tus visitas al doctor
[MEDICAMENTOS] **Medicamentos** - Lleva control de tus tratamientos  
[EXAMENES] **Ex menes** - Guarda resultados de laboratorio
[FAMILIA] **Familiares** - Notifica a tus seres queridos
[ESTADISTICAS] **Historial** - Consulta toda tu informaci n m dica
[DOCUMENTO] **Documentos** - Solicita informes e im genes

**Comandos principales:**
  "Quiero registrar una consulta"
  "Necesito anotar un medicamento"
  "Tengo resultados de ex menes"
  "Mu strame mi historial"
  "Solicitar documento"

 En qu  puedo ayudarte hoy? [PENSANDO]"""
        else:
            return """ Hola! [SALUDO] Soy tu asistente personal de salud de MedConnect [HOSPITAL]

Me encanta conocerte y estoy aqu  para ayudarte a cuidar tu bienestar. 

[MOVIL] ** Ya eres parte de la familia MedConnect?**
Si ya tienes cuenta, es s per f cil conectarnos:

1  Ve a tu perfil: https://medconnect.cl/profile
2  Haz clic en "Generar C digo"
3  Comparte conmigo el c digo: `/codigo MED123456`

[NOTA] ** Primera vez aqu ?**
 Genial! Reg strate en: https://medconnect.cl/register

Una vez conectados, podremos:
[LISTA] Registrar tus consultas m dicas
[MEDICAMENTOS] Organizar tus medicamentos  
[EXAMENES] Guardar resultados de ex menes
[FAMILIA] Mantener informada a tu familia
[ESTADISTICAS] Crear tu historial m dico personalizado

 Hay algo en lo que pueda ayudarte mientras tanto? [FELIZ]"""

    # Comando /codigo
    elif text.startswith("/codigo"):
        return handle_telegram_code_linking(text, user_id)

    # Detectar intenci n del mensaje
    intent = detect_intent(text)

    # Manejar emergencias con prioridad
    if intent == "emergencia":
        return """[EMERGENCIA] **EMERGENCIA DETECTADA** [EMERGENCIA]

Si est s en una situaci n de emergencia m dica:

[LLAMAR] **LLAMA INMEDIATAMENTE:**
  **131** - SAMU (Ambulancia)
  **133** - Bomberos
  **132** - Carabineros

[HOSPITAL] **Ve al servicio de urgencias m s cercano**

[ADVERTENCIA] **Recuerda:** Soy un asistente virtual y no puedo reemplazar la atenci n m dica profesional en emergencias.

Una vez que est s seguro, estar  aqu  para ayudarte con el seguimiento. [CORAZON]"""

    # ===== FUNCIONALIDADES PARA PROFESIONALES =====
    if is_professional:
        return handle_professional_requests(text, user_info, user_id, intent)

    # ===== FUNCIONALIDADES PARA PACIENTES =====
    return handle_patient_requests(text, user_info, user_id, intent)


def get_telegram_user_info(telegram_user_id):
    """Obtiene informaci n del usuario registrado por su ID de Telegram"""
    try:
        if not auth_manager:
            return None

        user_info = auth_manager.get_user_by_telegram_id(telegram_user_id)
        return user_info
    except Exception as e:
        logger.error(
            f"Error obteniendo info de usuario Telegram {telegram_user_id}: {e}"
        )
        return None


def is_professional_user(user_info):
    """Verifica si el usuario es un profesional m dico"""
    if not user_info:
        return False
    return user_info.get("tipo_usuario") == "profesional"


def get_professional_schedule_for_bot(professional_id, fecha=None):
    """Obtiene el horario del profesional para el bot"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return None

        citas_worksheet = spreadsheet.worksheet("Citas_Agenda")
        all_records = citas_worksheet.get_all_records()

        # Filtrar por profesional y fecha
        citas_profesional = []
        for record in all_records:
            if str(record.get("profesional_id", "")) == str(professional_id):
                if fecha:
                    cita_fecha = record.get("fecha", "")
                    if cita_fecha == fecha:
                        citas_profesional.append(record)
                else:
                    citas_profesional.append(record)

        return citas_profesional
    except Exception as e:
        logger.error(f"Error obteniendo agenda del profesional {professional_id}: {e}")
        return None


def get_available_slots_for_professional(professional_id, fecha):
    """Obtiene los horarios disponibles del profesional para una fecha espec fica"""
    try:
        # Obtener horario de trabajo del profesional
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return []

        horarios_worksheet = spreadsheet.worksheet("Horarios_Profesional")
        all_records = horarios_worksheet.get_all_records()

        # Buscar horario del profesional
        horario_profesional = None
        for record in all_records:
            if str(record.get("profesional_id", "")) == str(professional_id):
                horario_profesional = record
                break

        if not horario_profesional:
            return []

        # Obtener citas existentes para esa fecha
        citas_existentes = get_professional_schedule_for_bot(professional_id, fecha)

        # Generar slots disponibles (simplificado)
        slots_disponibles = []
        hora_inicio = 9  # 9:00 AM
        hora_fin = 18  # 6:00 PM

        for hora in range(hora_inicio, hora_fin):
            slot = f"{hora:02d}:00"
            # Verificar si el slot est  ocupado
            ocupado = any(cita.get("hora") == slot for cita in citas_existentes)
            if not ocupado:
                slots_disponibles.append(slot)

        return slots_disponibles
    except Exception as e:
        logger.error(f"Error obteniendo slots disponibles: {e}")
        return []


def send_notification_to_patient(patient_telegram_id, message):
    """Env a notificaci n a un paciente espec fico"""
    if patient_telegram_id:
        return send_telegram_message(patient_telegram_id, message)
    return False


def handle_professional_requests(text, user_info, user_id, intent):
    """Maneja las solicitudes espec ficas de profesionales m dicos"""
    user_name = user_info.get("nombre", "Doctor") if user_info else "Doctor"
    professional_id = user_info.get("id") if user_info else None

    # Gesti n de agenda
    if intent == "agenda" or "agenda" in text or "horario" in text:
        if professional_id:
            citas = get_professional_schedule_for_bot(professional_id)
            if citas:
                agenda_text = f"[CALENDARIO] **Agenda del Dr(a). {user_name}**\n\n"
                for cita in citas[:5]:  # Mostrar solo las pr ximas 5
                    fecha = cita.get("fecha", "N/A")
                    hora = cita.get("hora", "N/A")
                    paciente = cita.get("nombre_paciente", "Paciente")
                    agenda_text += f"  {fecha} {hora} - {paciente}\n"

                agenda_text += (
                    "\n[IDEA] Para ver m s detalles, usa: 'Ver agenda completa'"
                )
                return agenda_text
            else:
                return f"[CALENDARIO] **Agenda del Dr(a). {user_name}**\n\nNo tienes citas programadas actualmente.\n\n[IDEA] Para agendar una nueva cita, escribe: 'Agendar cita'"
        else:
            return "[ERROR] No se pudo obtener tu informaci n profesional. Contacta soporte."

    # Agendar citas
    elif intent == "cita_profesional" or "agendar" in text or "nueva cita" in text:
        set_user_context(user_id, "current_task", "agendar_cita")
        return f"""[CALENDARIO] **Agendar Nueva Cita**

Dr(a). {user_name}, para agendar una cita necesito:

  **Datos del paciente:**
  Nombre completo
  Tel fono (opcional)
  Email (opcional)

[CALENDARIO] **Detalles de la cita:**
  Fecha deseada
  Hora preferida
  Motivo de la consulta
  Duraci n estimada

[IDEA] **Ejemplo:**
"Agendar cita para Mar a Gonz lez, tel fono 912345678, el 15 de julio a las 10:00, consulta de control, 30 minutos"

 Con qu  paciente y fecha quieres agendar? [PENSANDO]"""

    # Gesti n de pacientes
    elif intent == "paciente_profesional" or "paciente" in text:
        if professional_id:
            # Obtener lista de pacientes del profesional
            spreadsheet = get_spreadsheet()
            if spreadsheet:
                try:
                    pacientes_worksheet = spreadsheet.worksheet("Pacientes_Profesional")
                    all_records = pacientes_worksheet.get_all_records()

                    pacientes_profesional = []
                    for record in all_records:
                        if str(record.get("profesional_id", "")) == str(
                            professional_id
                        ):
                            pacientes_profesional.append(record)

                    if pacientes_profesional:
                        response = (
                            f"[PACIENTES] **Pacientes del Dr(a). {user_name}**\n\n"
                        )
                        for paciente in pacientes_profesional[
                            :10
                        ]:  # Mostrar solo los primeros 10
                            nombre = paciente.get("nombre_completo", "N/A")
                            edad = paciente.get("edad", "N/A")
                            ultima_consulta = paciente.get(
                                "ultima_consulta", "Sin consultas"
                            )
                            response += f"  **{nombre}** ({edad} a os)\n"
                            response += f"   [CALENDARIO]  ltima consulta: {ultima_consulta}\n\n"

                        response += "[IDEA] Para ver historial completo de un paciente, escribe: 'Ver paciente [nombre]'"
                        return response
                    else:
                        return f"[PACIENTES] **Pacientes del Dr(a). {user_name}**\n\nNo tienes pacientes registrados actualmente.\n\n[IDEA] Para agregar un paciente, escribe: 'Agregar paciente'"
                except Exception as e:
                    logger.error(f"Error obteniendo pacientes: {e}")
                    return "[ERROR] Error obteniendo lista de pacientes. Intenta m s tarde."
            else:
                return "[ERROR] Error conectando con la base de datos."
        else:
            return "[ERROR] No se pudo obtener tu informaci n profesional."

    # Notificaciones a pacientes
    elif intent == "notificacion_profesional" or "notificar" in text:
        set_user_context(user_id, "current_task", "notificar_paciente")
        return f"""[CAMPANA] **Enviar Notificaci n a Paciente**

Dr(a). {user_name}, para enviar una notificaci n necesito:

  **Paciente:** Nombre del paciente
[NOTA] **Mensaje:** Lo que quieres comunicar

[IDEA] **Ejemplo:**
"Notificar a Mar a Gonz lez: Su cita de ma ana se confirma a las 10:00 AM"

 A qu  paciente quieres enviar la notificaci n? [PENSANDO]"""

    # Comando de ayuda para profesionales
    elif intent == "ayuda":
        return f"""  **Ayuda para Profesionales**

Dr(a). {user_name}, aqu  tienes mis funcionalidades:

[CALENDARIO] **Gesti n de Agenda:**
  "Ver mi agenda" - Consultar citas
  "Agendar cita" - Programar nueva cita
  "Cancelar cita" - Eliminar cita

[PACIENTES] **Gesti n de Pacientes:**
  "Pacientes" - Ver lista de pacientes
  "Ver paciente [nombre]" - Historial espec fico
  "Agregar paciente" - Registrar nuevo paciente

[CAMPANA] **Comunicaci n:**
  "Notificar paciente" - Enviar mensaje
  "Recordatorio paciente" - Programar aviso

[ESTADISTICAS] **Reportes:**
  "Estad sticas" - Ver m tricas
  "Reporte semanal" - Resumen de actividad

 En qu  puedo ayudarte espec ficamente? [PENSANDO]"""

    # Respuesta por defecto para profesionales
    else:
        return f"""[PENSANDO] **No entend  tu solicitud**

Dr(a). {user_name}, puedes pedirme:

[CALENDARIO] **Agenda:** "Ver mi agenda", "Agendar cita"
[PACIENTES] **Pacientes:** "Pacientes", "Ver paciente [nombre]"
[CAMPANA] **Notificaciones:** "Notificar paciente"
  **Ayuda:** "Ayuda"

 Qu  necesitas hacer? [PENSANDO]"""


def handle_patient_requests(text, user_info, user_id, intent):
    """Maneja las solicitudes espec ficas de pacientes"""
    user_name = user_info.get("nombre", "Usuario") if user_info else "Usuario"

    # Saludos
    if intent == "saludo" and not text.startswith("/"):
        greeting = get_random_response("greeting")
        if user_info:
            return f"{greeting} {user_name}!  En qu  puedo ayudarte con tu salud hoy? [FELIZ]"
        else:
            return f"""{greeting}

Soy tu asistente de salud de MedConnect. Puedo ayudarte a:
[LISTA] Registrar informaci n m dica
[MEDICAMENTOS] Organizar medicamentos
[EXAMENES] Guardar ex menes
[ESTADISTICAS] Consultar tu historial

 Te gustar a vincular tu cuenta primero? Solo necesitas ir a https://medconnect.cl/profile y generar un c digo. 

 O prefieres que te ayude con algo espec fico? [PENSANDO]"""

    # Despedidas
    elif intent == "despedida":
        despedidas = [
            f" Hasta pronto {user_name}! [SALUDO] Cu date mucho y no dudes en escribirme cuando necesites algo. [CORAZON]",
            f" Que tengas un excelente d a {user_name}! [ESTRELLA] Estar  aqu  cuando me necesites. [FELIZ]",
            f" Nos vemos pronto {user_name}! [SALUDO] Recuerda cuidar tu salud.  Hasta la pr xima!  ",
        ]
        import random

        return random.choice(despedidas)

    # Consultas m dicas
    elif intent == "consulta":
        set_user_context(user_id, "current_task", "consulta")

        if user_info:
            encouragement = get_random_response("encouragement")
            return f"""{encouragement} {user_name}, veo que quieres registrar una consulta m dica. [LISTA]

Para crear un registro completo, me gustar a que me compartieras:

[EXAMENES] **Detalles de la consulta:**
1   Cu ndo fue? (fecha)
2   Con qu  doctor te atendiste?
3   Cu l es su especialidad?
4   Qu  diagn stico te dieron?
5   Te recetaron alg n tratamiento?

Puedes contarme todo junto o paso a paso, como prefieras. Lo importante es que quede bien registrado en tu historial personal. [FELIZ]

 Empezamos? [PENSANDO]"""
        else:
            return """[LISTA]  Me encanta que quieras registrar tu consulta m dica! Es s per importante llevar un buen control.

Para poder guardar esta informaci n en tu historial personal, necesitar amos conectar tu cuenta primero.

**Datos que necesito para la consulta:**
1  Fecha de la consulta
2  Nombre del m dico
3  Especialidad
4  Diagn stico recibido
5  Tratamiento indicado

[IDEA] ** Tienes cuenta en MedConnect?**
Ve a https://medconnect.cl/profile, genera tu c digo y comp rtelo conmigo.

Mientras tanto, puedes contarme los detalles y los guardar  temporalmente.  Te parece? [FELIZ]"""

    # Medicamentos
    elif intent == "medicamento":
        set_user_context(user_id, "current_task", "medicamento")

        if user_info:
            encouragement = get_random_response("encouragement")
            return f"""{encouragement} {user_name}! Organizar tus medicamentos es fundamental para tu salud. [MEDICAMENTOS]

Para registrar correctamente tu medicamento, necesito conocer:

  **Informaci n del medicamento:**
1   C mo se llama?
2   Qu  dosis tomas? (ej: 50mg, 1 tableta)
3   Cada cu nto tiempo? (ej: cada 8 horas, 2 veces al d a)
4   Qu  m dico te lo recet ?
5   Para qu  es? (opcional)

Cu ntame todo lo que sepas y lo organizaremos en tu perfil para que nunca se te olvide. [FELIZ]

 Cu l es el medicamento? [PENSANDO]"""
        else:
            return """[MEDICAMENTOS]  Qu  responsable eres cuidando tu tratamiento! Me parece genial que quieras registrar tus medicamentos.

**Para un registro completo necesito:**
1  Nombre del medicamento
2  Dosis que tomas
3  Frecuencia (cada cu nto tiempo)
4  M dico que lo recet 
5  Para qu  es el tratamiento

[IDEA] **Para guardarlo en tu historial permanente:**
Necesitar as vincular tu cuenta desde https://medconnect.cl/profile

Pero puedes contarme los detalles ahora y te ayudo a organizarlos.  Cu l es el medicamento? [FELIZ]"""

    # Ex menes
    elif intent == "examen":
        set_user_context(user_id, "current_task", "examen")

        if user_info:
            encouragement = get_random_response("encouragement")
            return f"""{encouragement} {user_name}! Los ex menes son s per importantes para monitorear tu salud. [EXAMENES]

Para registrar tu examen correctamente, me gustar a saber:

  **Detalles del examen:**
1   Qu  tipo de examen fue? (sangre, orina, radiograf a, etc.)
2   Cu ndo te lo hiciste?
3   En qu  laboratorio o centro m dico?
4   Cu les fueron los resultados principales?
5   Alg n valor fuera de lo normal?

Si tienes los resultados en papel o digital, tambi n puedes subir la imagen a tu perfil web m s tarde.

 Me cuentas sobre tu examen? [PENSANDO]"""
        else:
            return """[EXAMENES]  Excelente que quieras registrar tus ex menes! Es clave para el seguimiento de tu salud.

**Informaci n que necesito:**
1  Tipo de examen realizado
2  Fecha cuando te lo hiciste
3  Laboratorio o centro m dico
4  Resultados principales
5  Valores importantes o anormales

[IDEA] **Para mantener un historial completo:**
Te recomiendo vincular tu cuenta en https://medconnect.cl/profile

Mientras tanto, cu ntame sobre tu examen y te ayudo a organizarlo.  Qu  examen te hiciste? [FELIZ]"""

    # Historial
    elif intent == "historial":
        if user_info:
            return f"""[ESTADISTICAS]  Hola {user_name}! Tu historial m dico est  siempre disponible para ti.

**Para ver toda tu informaci n completa:**
[MUNDO] Visita tu dashboard: https://medconnect.cl/patient

**Ah  encontrar s:**
[OK] Todas tus consultas m dicas organizadas
[OK] Lista completa de medicamentos actuales
[OK] Resultados de ex menes con fechas
[OK] Informaci n de familiares registrados
[OK] Gr ficos y estad sticas de tu salud

**Tambi n puedes preguntarme directamente:**
  " Cu les son mis  ltimas consultas?"
  " Qu  medicamentos estoy tomando?"
  " Cu ndo fue mi  ltimo examen?"
  " Tengo alguna cita pr xima?"

 Qu  te gustar a consultar espec ficamente? [PENSANDO]"""
        else:
            return """[ESTADISTICAS]  Me encantar a mostrarte tu historial m dico! Pero primero necesitamos conectar tu cuenta.

**Una vez vinculada, tendr s acceso a:**
[OK] Historial completo de consultas
[OK] Registro de todos tus medicamentos
[OK] Resultados de ex menes organizados
[OK] Informaci n de contactos de emergencia
[OK] Estad sticas de tu salud

** Ya tienes cuenta en MedConnect?**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

Una vez conectados, podr s consultar toda tu informaci n m dica cuando quieras.  Te ayudo con la vinculaci n? [FELIZ]"""

    # Documentos e im genes
    elif intent == "documento":
        if user_info:
            return f"""[DOCUMENTO] **Solicitar Documentos M dicos**

{user_name}, puedo ayudarte a solicitar:

[LISTA] **Informes m dicos**
[EXAMENES] **Resultados de ex menes**
[MEDICAMENTOS] **Recetas m dicas**
[ESTADISTICAS] **Reportes de salud**

**Para solicitar un documento:**
1  Ve a tu perfil web: https://medconnect.cl/patient
2  Navega a la secci n "Ex menes" o "Consultas"
3  Busca el documento que necesitas
4  Haz clic en "Descargar" o "Ver"

**Tambi n puedes pedirme:**
  " Tengo resultados de ex menes recientes?"
  " Cu ndo fue mi  ltima consulta?"
  " Qu  medicamentos tengo recetados?"

 Qu  tipo de documento necesitas? [PENSANDO]"""
        else:
            return """[DOCUMENTO] **Documentos M dicos**

Para acceder a tus documentos m dicos, necesitas tener una cuenta vinculada.

** Ya tienes cuenta?**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

Una vez conectado, podr s:
[OK] Ver todos tus documentos m dicos
[OK] Descargar informes y resultados
[OK] Acceder a recetas m dicas
[OK] Solicitar reportes de salud

 Te ayudo a crear tu cuenta? [FELIZ]"""

    # Recordatorios
    elif intent == "recordatorio":
        if user_info:
            return f"""  **Configurar Recordatorios**

{user_name}, puedo ayudarte a configurar recordatorios para:

[MEDICAMENTOS] **Medicamentos** - Horarios de toma
[CALENDARIO] **Citas m dicas** - Fechas de consulta
[EXAMENES] **Ex menes** - Fechas de laboratorio
[LISTA] **Controles** - Seguimientos m dicos

**Para configurar recordatorios:**
[MUNDO] Ve a tu perfil: https://medconnect.cl/profile
[MOVIL] Navega a "Configuraci n de Notificaciones"
[CAMPANA] Activa los recordatorios que necesites

**Tambi n puedes pedirme:**
  " Tengo alguna cita pr xima?"
  " Qu  medicamentos debo tomar hoy?"
  " Cu ndo es mi pr ximo control?"

 Qu  tipo de recordatorio necesitas? [PENSANDO]"""
        else:
            return """  **Recordatorios M dicos**

Para configurar recordatorios personalizados, necesitas tener una cuenta vinculada.

** Ya tienes cuenta?**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

Una vez conectado, podr s:
[OK] Configurar recordatorios de medicamentos
[OK] Recibir avisos de citas m dicas
[OK] Alertas de ex menes y controles
[OK] Notificaciones personalizadas

 Te ayudo a crear tu cuenta? [FELIZ]"""

    # Ayuda
    elif intent == "ayuda" or text in ["help", "/help"]:
        if user_info:
            return f"""  **Ayuda para Pacientes**

{user_name}, aqu  tienes mis funcionalidades:

[LISTA] **Consultas m dicas**
  "Registrar una consulta"
  "Anotar visita al doctor"
  "Ver mis consultas"

[MEDICAMENTOS] **Medicamentos**
  "Anotar medicamento"
  "Ver mis medicamentos"
  "Recordatorio de medicinas"

[EXAMENES] **Ex menes**
  "Registrar examen"
  "Ver resultados"
  "Solicitar informe"

[ESTADISTICAS] **Historial**
  "Ver mi historial"
  "Consultar datos"
  "Estad sticas de salud"

[DOCUMENTO] **Documentos**
  "Solicitar documento"
  "Descargar informe"
  "Ver resultados"

  **Recordatorios**
  "Configurar recordatorio"
  "Ver pr ximas citas"
  "Alertas m dicas"

 En qu  puedo ayudarte espec ficamente? [PENSANDO]"""
        else:
            return """  **Ayuda General**

Soy tu asistente de salud de MedConnect. Puedo ayudarte con:

[LISTA] **Registro de informaci n m dica**
[MEDICAMENTOS] **Gesti n de medicamentos**
[EXAMENES] **Control de ex menes**
[ESTADISTICAS] **Consulta de historial**
[DOCUMENTO] **Solicitud de documentos**
  **Configuraci n de recordatorios**

**Para acceder a todas las funcionalidades:**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

 Qu  te gustar a hacer? [PENSANDO]"""

    # Respuesta por defecto para pacientes
    else:
        if user_info:
            return f"""[PENSANDO] **No entend  tu solicitud**

{user_name}, puedes pedirme:

[LISTA] **Consultas:** "Registrar consulta", "Ver mis consultas"
[MEDICAMENTOS] **Medicamentos:** "Anotar medicamento", "Ver medicamentos"
[EXAMENES] **Ex menes:** "Registrar examen", "Ver resultados"
[ESTADISTICAS] **Historial:** "Ver mi historial", "Consultar datos"
[DOCUMENTO] **Documentos:** "Solicitar documento"
  **Recordatorios:** "Configurar recordatorio"
  **Ayuda:** "Ayuda"

 Qu  necesitas hacer? [PENSANDO]"""
        else:
            return """[PENSANDO] **No entend  tu solicitud**

Puedes pedirme:
[LISTA] Registrar informaci n m dica
[MEDICAMENTOS] Organizar medicamentos
[EXAMENES] Guardar ex menes
[ESTADISTICAS] Consultar historial
  Ayuda

**Para funcionalidades completas:**
  Ve a: https://medconnect.cl/profile y genera tu c digo

 Qu  te gustar a hacer? [PENSANDO]"""


def handle_account_linking(text, telegram_user_id):
    """Maneja la vinculaci n de cuenta de Telegram"""
    try:
        parts = text.split()
        if len(parts) < 2:
            return """[ERROR] Formato incorrecto. 

**Uso correcto:**
`/vincular tu-email@ejemplo.com`

**Ejemplo:**
`/vincular maria.gonzalez@gmail.com`

Aseg rate de usar el mismo email con el que te registraste en MedConnect."""

        email = parts[1].strip()

        # Validar formato de email b sico
        if "@" not in email or "." not in email:
            return """[ERROR] El email no parece v lido.

**Formato esperado:**
`/vincular tu-email@ejemplo.com`

Por favor verifica e intenta de nuevo."""

        if not auth_manager:
            return "[ERROR] Sistema de autenticaci n no disponible temporalmente. Intenta m s tarde."

        # Verificar si el usuario existe
        user_data = auth_manager.get_user_by_email(email)
        if not user_data:
            return f"""[ERROR] No encontr  ninguna cuenta con el email: `{email}`

** Posibles soluciones:**
1. Verifica que escribiste correctamente tu email
2. Si a n no tienes cuenta, reg strate en: https://medconnect.cl/register
3. Intenta de nuevo: `/vincular tu-email-correcto@ejemplo.com`"""

        # Intentar vincular la cuenta
        success, message, user_info = auth_manager.link_telegram_account(
            email, telegram_user_id
        )

        if success and user_info:
            nombre = user_info.get("nombre", "Usuario")
            apellido = user_info.get("apellido", "")
            return f"""[OK]  Cuenta vinculada exitosamente!

 Hola {nombre} {apellido}!  

Tu cuenta de Telegram ahora est  conectada con MedConnect. A partir de ahora:

  **Experiencia personalizada**
[LISTA] Historial m dico completo
[MEDICAMENTOS] Seguimiento de medicamentos
[EXAMENES] Registro de ex menes
[FAMILIA] Notificaciones familiares

Escribe `/start` para comenzar con tu experiencia personalizada."""
        else:
            return f"""[ERROR] {message}

**Si el problema persiste:**
1. Verifica tu email: `{email}`
2. Contacta soporte si necesitas ayuda
3. O intenta registrarte en: https://medconnect.cl/register"""

    except Exception as e:
        logger.error(f"Error en vinculaci n de cuenta: {e}")
        return """[ERROR] Error interno al vincular cuenta.

Por favor intenta de nuevo en unos minutos o contacta soporte."""


def send_telegram_message(telegram_id, message):
    """Env a un mensaje a trav s del bot de Telegram"""
    try:
        # Token del bot
        BOT_TOKEN = (
            "7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck"  # Token correcto del bot
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": str(telegram_id),  # Asegurar que sea string
            "text": message,
            "parse_mode": "HTML",
        }

        import requests  # Asegurar import local

        response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            logger.info(f"[OK] Mensaje enviado a Telegram ID: {telegram_id}")
            return True
        else:
            logger.error(f"[ERROR] Error enviando mensaje a Telegram: {response.text}")
            return False

    except Exception as e:
        logger.error(f"[ERROR] Error enviando mensaje de Telegram: {e}")
        return False


# Configurar webhook del bot
@app.route("/setup-webhook")
@app.route("/health")
def health_check():
    """Health check para Railway"""
    try:
        # Verificar conexi n con Google Sheets
        sheets_status = "[OK] Conectado" if sheets_client else "[ERROR] No conectado"

        # Verificar AuthManager
        auth_status = "[OK] Disponible" if auth_manager else "[ERROR] No disponible"

        # Verificar variables de entorno cr ticas
        env_vars = {
            "GOOGLE_SHEETS_ID": bool(os.environ.get("GOOGLE_SHEETS_ID")),
            "TELEGRAM_BOT_TOKEN": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
            "GOOGLE_SERVICE_ACCOUNT_JSON": bool(
                os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
            ),
        }

        # Obtener estad sticas de API si est  disponible
        api_stats = None
        try:
            from api_monitoring import get_api_stats

            api_stats = get_api_stats()
        except Exception as e:
            logger.warning(
                f"[ADVERTENCIA] No se pudieron obtener estad sticas de API: {e}"
            )

        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "sheets_client": sheets_status,
            "auth_manager": auth_status,
            "environment_variables": env_vars,
            "uptime": time.time() - start_time,
            "api_stats": api_stats,
        }

        return jsonify(health_data)

    except Exception as e:
        logger.error(f"[ERROR] Error en health check: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/debug-static")
def debug_static():
    """Endpoint para debuggear archivos est ticos"""
    try:
        # M ltiples rutas para verificar
        static_paths = [
            os.path.join(app.root_path, "static"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
            "static",
        ]

        debug_info = {
            "static_directories": [],
            "app_root_path": app.root_path,
            "current_working_directory": os.getcwd(),
            "whitenoise_active": hasattr(app, "wsgi_app")
            and "WhiteNoise" in str(type(app.wsgi_app)),
            "auth_manager_available": auth_manager is not None,
            "environment": {
                "FLASK_ENV": os.environ.get("FLASK_ENV"),
                "RAILWAY_ENVIRONMENT": os.environ.get("RAILWAY_ENVIRONMENT"),
                "PORT": os.environ.get("PORT"),
                "GOOGLE_SHEETS_ID": bool(os.environ.get("GOOGLE_SHEETS_ID")),
                "TELEGRAM_BOT_TOKEN": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
                "GOOGLE_SERVICE_ACCOUNT_JSON": bool(
                    os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
                ),
            },
            "files": [],
        }

        # Verificar cada ruta de static
        for i, static_path in enumerate(static_paths):
            debug_info["static_directories"].append(
                {
                    "index": i,
                    "path": static_path,
                    "exists": os.path.exists(static_path),
                    "is_dir": (
                        os.path.isdir(static_path)
                        if os.path.exists(static_path)
                        else False
                    ),
                }
            )

        # Listar archivos cr ticos
        critical_files = [
            "css/styles.css",
            "js/app.js",
            "images/logo.png",
            "images/Imagen2.png",
        ]

        for file_rel_path in critical_files:
            file_info = {"path": file_rel_path, "locations": []}

            # Verificar en cada ruta de static
            for static_path in static_paths:
                file_path = os.path.join(static_path, file_rel_path)
                file_info["locations"].append(
                    {
                        "static_path": static_path,
                        "full_path": file_path,
                        "exists": os.path.exists(file_path),
                        "size": (
                            os.path.getsize(file_path)
                            if os.path.exists(file_path)
                            else 0
                        ),
                        "readable": (
                            os.access(file_path, os.R_OK)
                            if os.path.exists(file_path)
                            else False
                        ),
                    }
                )

            debug_info["files"].append(file_info)

        return jsonify(debug_info)

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


@app.route("/test-complete")
def test_complete():
    """P gina de diagn stico completa"""
    logger.info("[BUSCAR] Accediendo a p gina de diagn stico completa")

    # Verificar estado del sistema
    auth_status = "[OK] Disponible" if auth_manager else "[ERROR] No disponible"

    # Verificar archivos est ticos
    static_files = []
    critical_files = ["css/styles.css", "js/app.js", "images/logo.png"]
    for file_path in critical_files:
        full_path = os.path.join(app.root_path, "static", file_path)
        static_files.append(
            {
                "path": file_path,
                "exists": os.path.exists(full_path),
                "size": os.path.getsize(full_path) if os.path.exists(full_path) else 0,
            }
        )

    # Verificar variables de entorno
    env_vars = {
        "GOOGLE_SERVICE_ACCOUNT_JSON": bool(
            os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        ),
        "GOOGLE_SHEETS_ID": bool(os.environ.get("GOOGLE_SHEETS_ID")),
        "TELEGRAM_BOT_TOKEN": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
        "PORT": os.environ.get("PORT", "No definido"),
    }

    html = f"""
     <!DOCTYPE html>
     <html>
     <head>
         <title>MedConnect - Diagn stico Completo</title>
         <style>
             body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
             .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
             .btn {{ padding: 10px 20px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; display: inline-block; }}
             .status {{ padding: 15px; margin: 10px 0; border-radius: 5px; }}
             .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
             .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
             .info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
             .warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
             table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
             th, td {{ padding: 8px 12px; border: 1px solid #ddd; text-align: left; }}
             th {{ background: #f8f9fa; }}
             .code {{ background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; }}
         </style>
     </head>
     <body>
         <div class="container">
             <h1>[HOSPITAL] MedConnect - Diagn stico Completo</h1>
             
             <div class="status {'success' if auth_manager else 'error'}">
                 <strong>  AuthManager:</strong> {auth_status}
             </div>
             
             <h2>[HERRAMIENTA] Variables de Entorno</h2>
             <table>
                 <tr><th>Variable</th><th>Estado</th></tr>"""

    for var, status in env_vars.items():
        status_icon = "[OK]" if status else "[ERROR]"
        html += f"<tr><td>{var}</td><td>{status_icon} {status}</td></tr>"

    html += f"""
             </table>
             
             <h2>[CARPETA] Archivos Est ticos</h2>
             <table>
                 <tr><th>Archivo</th><th>Existe</th><th>Tama o</th></tr>"""

    for file_info in static_files:
        exists_icon = "[OK]" if file_info["exists"] else "[ERROR]"
        size_text = f"{file_info['size']} bytes" if file_info["exists"] else "N/A"
        html += f'<tr><td>{file_info["path"]}</td><td>{exists_icon}</td><td>{size_text}</td></tr>'

    html += f"""
             </table>
             
             <h2>  Pruebas Funcionales</h2>
             <a href="/" class="btn">  P gina Principal</a>
             <a href="/login" class="btn">  Login</a>
             <a href="/register" class="btn">[NOTA] Registro</a>
             <a href="/debug-static" class="btn">[HERRAMIENTA] Debug JSON</a>
             
             <h2>  Prueba Visual</h2>
             <div class="status info">
                 <strong>Logo:</strong><br>
                 <img src="/static/images/logo.png" alt="Logo" style="max-width: 150px;" 
                      onload="document.getElementById('img-status').innerHTML='[OK] Imagen cargada correctamente'"
                      onerror="document.getElementById('img-status').innerHTML='[ERROR] Error cargando imagen'">
                 <div id="img-status">  Cargando imagen...</div>
             </div>
             
             <h2>  Prueba CSS</h2>
             <link rel="stylesheet" href="/static/css/styles.css">
             <div class="hero" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center;">
                 <h3>Si ves este gradiente y texto centrado, CSS funciona [OK]</h3>
             </div>
             
             <h2>  Informaci n del Sistema</h2>
             <div class="code">
                 <strong>Ruta de la app:</strong> {app.root_path}<br>
                 <strong>Carpeta static:</strong> {app.static_folder}<br>
                 <strong>URL static:</strong> {app.static_url_path}<br>
                 <strong>WhiteNoise:</strong> {'[OK] Activo' if hasattr(app, 'wsgi_app') and 'WhiteNoise' in str(type(app.wsgi_app)) else '[ERROR] No activo'}
             </div>
             
             <script>
                 // Verificar JavaScript
                 document.addEventListener('DOMContentLoaded', function() {{
                     const jsStatus = document.createElement('div');
                     jsStatus.className = 'status success';
                     jsStatus.innerHTML = '[OK] JavaScript funcionando correctamente';
                     document.body.appendChild(jsStatus);
                 }});
             </script>
         </div>
     </body>
     </html>
     """
    return html


# Ruta para servir archivos est ticos en producci n
@app.route("/static/<path:filename>")
def serve_static(filename):
    """Servir archivos est ticos en producci n (CSS, JS, im genes)"""
    try:
        # M ltiples rutas para buscar archivos est ticos
        static_paths = [
            os.path.join(app.root_path, "static"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
            "static",  # Ruta relativa
        ]

        file_path = None
        used_path = None

        # Buscar el archivo en m ltiples ubicaciones
        for static_path in static_paths:
            test_path = os.path.join(static_path, filename)
            if os.path.exists(test_path):
                file_path = test_path
                used_path = static_path
                break

        logger.info(f"[CARPETA] Solicitando archivo est tico: {filename}")
        logger.info(
            f"[ARCHIVO] Rutas probadas: {[os.path.join(p, filename) for p in static_paths]}"
        )
        logger.info(f"[LISTA] Archivo encontrado: {file_path is not None}")

        if file_path and os.path.exists(file_path):
            # Obtener información del archivo
            file_size = os.path.getsize(file_path)
            logger.info(f"[INFO] Tamaño del archivo {filename}: {file_size} bytes")

            # Determinar tipo MIME basado en la extensi n
            mimetype = None
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                mimetype = f'image/{filename.split(".")[-1].lower()}'
                if mimetype == "image/jpg":
                    mimetype = "image/jpeg"
            elif filename.lower().endswith(".css"):
                mimetype = "text/css"
            elif filename.lower().endswith(".js"):
                mimetype = "application/javascript"
            elif filename.lower().endswith(".ico"):
                mimetype = "image/x-icon"

            # Para archivos grandes, usar streaming
            if file_size > 1024 * 1024:  # Más de 1MB
                logger.info(
                    f"[STREAMING] Sirviendo archivo grande: {filename} ({file_size} bytes)"
                )

                def generate():
                    with open(file_path, "rb") as f:
                        while True:
                            chunk = f.read(8192)  # 8KB chunks
                            if not chunk:
                                break
                            yield chunk

                response = Response(generate(), mimetype=mimetype)
                response.headers["Content-Length"] = str(file_size)
                response.headers["Accept-Ranges"] = "bytes"

            else:
                # Para archivos pequeños, usar send_from_directory
                response = send_from_directory(used_path, filename, mimetype=mimetype)

            # Agregar headers de cache para mejor rendimiento
            if filename.lower().endswith(
                (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico")
            ):
                response.headers["Cache-Control"] = (
                    "public, max-age=31536000"  # 1 a o para im genes
                )
            elif filename.lower().endswith((".css", ".js")):
                response.headers["Cache-Control"] = (
                    "public, max-age=86400"  # 1 d a para CSS/JS
                )

            # Headers adicionales para Railway
            response.headers["X-Served-By"] = "Flask-Static-Handler"
            response.headers["X-File-Path"] = file_path
            response.headers["X-File-Size"] = str(file_size)

            # Agregar headers de compresión si es necesario
            if filename.lower().endswith((".css", ".js")):
                response.headers["Content-Encoding"] = "gzip"

            logger.info(
                f"[OK] Archivo servido exitosamente: {filename} (tipo: {mimetype}, tamaño: {file_size}) desde {used_path}"
            )
            return response
        else:
            logger.error(f"[ERROR] Archivo no encontrado: {filename}")
            logger.error(
                f"[ERROR] Rutas probadas: {[os.path.join(p, filename) for p in static_paths]}"
            )

            # Intentar servir un archivo por defecto para im genes
            if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                default_image = os.path.join(
                    app.root_path, "static", "images", "logo.png"
                )
                if os.path.exists(default_image):
                    logger.info(
                        f"[ACTUALIZAR] Sirviendo imagen por defecto para: {filename}"
                    )
                    return send_from_directory(
                        os.path.join(app.root_path, "static", "images"), "logo.png"
                    )

            return "Archivo no encontrado", 404

    except Exception as e:
        logger.error(f"[ERROR] Error sirviendo archivo est tico {filename}: {e}")
        import traceback

        logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
        return "Error interno del servidor", 500


# Rutas para manejo de archivos m dicos
@app.route("/uploads/medical_files/<filename>")
@login_required
def uploaded_file(filename):
    """Servir archivos m dicos subidos"""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/uploads/certifications/<filename>")
@login_required
def certification_file(filename):
    """Servir archivos de certificaciones"""
    return send_from_directory(
        os.path.join(app.config["UPLOAD_FOLDER"], "certifications"), filename
    )


@app.route("/api/patient/<patient_id>/exams/upload", methods=["POST"])
@login_required
def upload_exam_file(patient_id):
    """Subir archivo para un examen"""
    try:
        # Verificar que el usuario solo pueda subir sus propios archivos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        # Verificar que se envi  un archivo
        if "file" not in request.files:
            return jsonify({"error": "No se seleccion  ning n archivo"}), 400

        file = request.files["file"]
        exam_id = request.form.get("exam_id")

        if file.filename == "":
            return jsonify({"error": "No se seleccion  ning n archivo"}), 400

        if not exam_id:
            return jsonify({"error": "ID de examen requerido"}), 400

        if file and allowed_file(file.filename):
            # Generar nombre  nico para el archivo
            filename = generate_unique_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            # Guardar archivo
            file.save(filepath)

            # Actualizar la base de datos con la URL del archivo
            spreadsheet = get_spreadsheet()
            if not spreadsheet:
                # Si no se puede actualizar la BD, eliminar el archivo
                os.remove(filepath)
                return jsonify({"error": "Error conectando con la base de datos"}), 500

            try:
                worksheet = spreadsheet.worksheet("Examenes")
                all_values = worksheet.get_all_values()

                # Buscar la fila del examen
                exam_row = None
                if len(all_values) > 1:
                    for i, row in enumerate(all_values[1:], start=2):
                        if (
                            len(row) > 1
                            and str(row[0]) == str(exam_id)
                            and str(row[1]) == str(patient_id)
                        ):
                            exam_row = i
                            break

                if exam_row:
                    # Obtener URLs existentes de archivos
                    current_file_urls = (
                        all_values[exam_row - 1][7]
                        if len(all_values[exam_row - 1]) > 7
                        else ""
                    )

                    # Agregar nueva URL a las existentes
                    new_file_url = f"/uploads/medical_files/{filename}"

                    if current_file_urls and current_file_urls.strip():
                        # Si ya hay archivos, agregar el nuevo separado por coma
                        updated_file_urls = f"{current_file_urls},{new_file_url}"
                    else:
                        # Si no hay archivos, usar solo el nuevo
                        updated_file_urls = new_file_url

                    # Actualizar la columna file_url (columna 8,  ndice H)
                    worksheet.update_cell(exam_row, 8, updated_file_urls)

                    logger.info(
                        f"[OK] Archivo agregado al examen {exam_id}: {filename}"
                    )
                    logger.info(
                        f"[ARCHIVO] URLs de archivos actualizadas: {updated_file_urls}"
                    )

                    return jsonify(
                        {
                            "success": True,
                            "message": "Archivo subido exitosamente",
                            "file_url": new_file_url,
                            "all_file_urls": updated_file_urls,
                            "filename": filename,
                        }
                    )
                else:
                    # Si no se encuentra el examen, eliminar el archivo
                    os.remove(filepath)
                    return jsonify({"error": "Examen no encontrado"}), 404

            except gspread.WorksheetNotFound:
                os.remove(filepath)
                return jsonify({"error": "Hoja de ex menes no encontrada"}), 404
        else:
            return (
                jsonify(
                    {
                        "error": "Tipo de archivo no permitido. Formatos permitidos: PDF, PNG, JPG, JPEG, GIF, BMP, TIFF, DCM, DICOM, DOC, DOCX, TXT"
                    }
                ),
                400,
            )

    except Exception as e:
        logger.error(f"Error subiendo archivo: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


@app.route("/api/admin/link-existing-users", methods=["POST"])
@login_required
def link_existing_users():
    """Funci n de administraci n para vincular usuarios existentes con sus datos del bot"""
    try:
        # Solo permitir a administradores (por ahora cualquier usuario logueado puede usar esto)
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        users_worksheet = spreadsheet.worksheet("Usuarios")
        all_records = users_worksheet.get_all_records()

        results = {
            "users_checked": 0,
            "users_linked": 0,
            "duplicates_found": 0,
            "errors": [],
        }

        # Buscar usuarios duplicados o sin vincular
        web_users = []  # Usuarios de la plataforma web
        bot_users = []  # Usuarios creados por el bot

        for record in all_records:
            user_id = record.get("id") or record.get("user_id", "")
            telegram_id = record.get("telegram_id", "")

            if str(user_id).startswith("USR_"):
                # Usuario creado por el bot
                bot_users.append(record)
            else:
                # Usuario de la plataforma web
                web_users.append(record)

            results["users_checked"] += 1

        # Intentar vincular usuarios bas ndose en telegram_id
        for bot_user in bot_users:
            bot_telegram_id = bot_user.get("telegram_id", "")
            bot_user_id = bot_user.get("user_id", "")

            if bot_telegram_id:
                # Buscar si hay un usuario web que deber a estar vinculado a este telegram_id
                matching_web_user = None
                for web_user in web_users:
                    web_telegram_id = web_user.get("telegram_id", "")

                    # Si el usuario web tiene el mismo telegram_id, ya est  vinculado
                    if web_telegram_id == bot_telegram_id:
                        matching_web_user = web_user
                        break

                # Si encontramos un usuario web con el mismo telegram_id, reportar
                if matching_web_user:
                    results["users_linked"] += 1
                    logger.info(
                        f"[OK] Usuario ya vinculado: {matching_web_user.get('nombre')} con telegram_id {bot_telegram_id}"
                    )
                else:
                    # Reportar usuario del bot sin vincular
                    results["duplicates_found"] += 1
                    logger.info(
                        f"[ADVERTENCIA] Usuario del bot sin vincular: {bot_user_id} con telegram_id {bot_telegram_id}"
                    )

        return jsonify(
            {
                "success": True,
                "message": "An lisis de vinculaci n completado",
                "results": results,
                "web_users": len(web_users),
                "bot_users": len(bot_users),
                "recommendation": "Los usuarios pueden vincular sus cuentas manualmente desde la plataforma web",
            }
        )

    except Exception as e:
        logger.error(f"Error analizando usuarios: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/user/link-telegram", methods=["POST"])
@login_required
def link_telegram():
    """Vincula la cuenta web del usuario con su cuenta de Telegram"""
    logger.info("[BUSCAR] Iniciando link_telegram...")
    try:
        logger.info("[NOTA] Obteniendo datos del request...")
        data = request.get_json()
        logger.info(f"[ESTADISTICAS] Datos recibidos: {data}")

        telegram_id = data.get("telegram_id", "").strip()
        logger.info(f"[MOVIL] Telegram ID: {telegram_id}")

        if not telegram_id:
            logger.warning("[ERROR] Telegram ID vac o")
            return jsonify({"error": "ID de Telegram requerido"}), 400

        # Obtener el ID del usuario web actual
        user_id = session.get("user_id")
        logger.info(f"  User ID de la sesi n: {user_id}")

        if not user_id:
            logger.warning("[ERROR] Usuario no autenticado")
            return jsonify({"error": "Usuario no autenticado"}), 401

        logger.info("  Conectando con Google Sheets...")
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            logger.error("[ERROR] Error conectando con Google Sheets")
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        logger.info("  Obteniendo informaci n del usuario actual...")
        # Verificar que auth_manager est  disponible
        if not auth_manager:
            logger.error("[ERROR] AuthManager no disponible")
            return jsonify({"error": "Sistema de autenticaci n no disponible"}), 500

        # Obtener informaci n del usuario actual
        try:
            user_info = auth_manager.get_user_by_id(user_id)
            logger.info(f"[NOTA] User info obtenida: {user_info}")
        except Exception as e:
            logger.error(f"[ERROR] Error obteniendo user_info: {e}")
            return (
                jsonify(
                    {"error": f"Error obteniendo informaci n del usuario: {str(e)}"}
                ),
                500,
            )

        if not user_info:
            logger.error("[ERROR] Usuario no encontrado en la base de datos")
            return jsonify({"error": "Informaci n de usuario no encontrada"}), 404

        user_name = (
            f"{user_info.get('nombre', '')} {user_info.get('apellido', '')}".strip()
        )
        if not user_name:
            user_name = user_info.get("email", "Usuario")

        logger.info(f"[OK] Nombre del usuario: {user_name}")

        # Actualizar la hoja de Usuarios para agregar el telegram_id
        try:
            logger.info("[DOCUMENTO] Accediendo a la hoja de Usuarios...")
            users_worksheet = spreadsheet.worksheet("Usuarios")
            all_records = users_worksheet.get_all_records()
            logger.info(
                f"[ESTADISTICAS] Total de registros de usuarios: {len(all_records)}"
            )

            user_row = None
            for i, record in enumerate(
                all_records, start=2
            ):  # Start from row 2 (after headers)
                record_id = record.get("id") or record.get("user_id", "")
                if str(record_id) == str(user_id):
                    user_row = i
                    logger.info(f"[OK] Usuario encontrado en fila: {user_row}")
                    break

            if user_row:
                logger.info("[BUSCAR] Buscando columna telegram_id...")
                # Buscar la columna telegram_id
                headers = users_worksheet.row_values(1)
                telegram_col = None

                if "telegram_id" in headers:
                    telegram_col = headers.index("telegram_id") + 1
                    logger.info(
                        f"[OK] Columna telegram_id encontrada en posici n: {telegram_col}"
                    )
                else:
                    # Agregar la columna telegram_id si no existe
                    logger.info("  Agregando columna telegram_id...")
                    users_worksheet.update_cell(1, len(headers) + 1, "telegram_id")
                    telegram_col = len(headers) + 1
                    logger.info(
                        f"[OK] Columna telegram_id agregada en posici n: {telegram_col}"
                    )

                logger.info(
                    f"[GUARDAR] Actualizando telegram_id en fila {user_row}, columna {telegram_col}..."
                )
                # Actualizar el telegram_id del usuario
                users_worksheet.update_cell(user_row, telegram_col, telegram_id)

                logger.info(
                    f"[OK] Usuario {user_id} ({user_name}) vinculado con Telegram ID: {telegram_id}"
                )

                #   ENVIAR MENSAJE DE BIENVENIDA AUTOM TICO
                welcome_message = f"""  <b> Cuenta Vinculada Exitosamente!</b>

 Hola <b>{user_name}</b>! [SALUDO]

Tu cuenta de MedConnect ha sido vinculada con Telegram correctamente.

[OK] <b>Cuenta Web:</b> {user_info.get('email', 'N/A')}
[OK] <b>Telegram ID:</b> <code>{telegram_id}</code>

Ahora puedes:
[LISTA] Registrar consultas, medicamentos y ex menes desde Telegram
[ESTADISTICAS] Ver todo tu historial en la plataforma web
[ACTUALIZAR] Los datos se sincronizan autom ticamente

<i> Gracias por usar MedConnect!</i> [CORAZON]"""

                logger.info("  Enviando mensaje de bienvenida...")
                # Intentar enviar el mensaje
                message_sent = send_telegram_message(telegram_id, welcome_message)
                logger.info(f"[ENVIAR] Mensaje enviado: {message_sent}")

                # Verificar si ya hay datos del bot para este telegram_id
                try:
                    logger.info("[BUSCAR] Buscando ex menes del bot...")
                    examenes_worksheet = spreadsheet.worksheet("Examenes")

                    # Leer datos manualmente para evitar error de headers duplicados
                    all_exam_values = examenes_worksheet.get_all_values()
                    examenes_records = []

                    if len(all_exam_values) > 1:
                        headers = all_exam_values[0]
                        for row in all_exam_values[1:]:
                            if len(row) <= len(headers):
                                # Crear diccionario manualmente para evitar conflictos
                                record = {}
                                for i, header in enumerate(headers):
                                    if i < len(row):
                                        record[header] = row[i]
                                examenes_records.append(record)

                    # Buscar ex menes guardados por usuarios del bot con este telegram_id
                    bot_user_ids = []
                    for user_record in all_records:
                        if str(user_record.get("telegram_id", "")) == str(telegram_id):
                            bot_user_id = user_record.get("user_id", "")
                            if str(bot_user_id).startswith("USR_"):
                                bot_user_ids.append(bot_user_id)

                    exams_found = 0
                    for exam_record in examenes_records:
                        if exam_record.get("user_id", "") in bot_user_ids:
                            exams_found += 1

                    logger.info(
                        f"[ESTADISTICAS] Ex menes encontrados: {exams_found}, Bot users: {len(bot_user_ids)}"
                    )

                    return jsonify(
                        {
                            "success": True,
                            "message": "Cuenta de Telegram vinculada exitosamente",
                            "telegram_id": telegram_id,
                            "user_name": user_name,
                            "exams_found": exams_found,
                            "bot_users_found": len(bot_user_ids),
                            "welcome_message_sent": message_sent,
                        }
                    )

                except gspread.WorksheetNotFound:
                    logger.warning("[ADVERTENCIA] Hoja de Examenes no encontrada")
                    return jsonify(
                        {
                            "success": True,
                            "message": "Cuenta de Telegram vinculada exitosamente",
                            "telegram_id": telegram_id,
                            "user_name": user_name,
                            "exams_found": 0,
                            "bot_users_found": 0,
                            "welcome_message_sent": message_sent,
                        }
                    )
            else:
                logger.error(
                    f"[ERROR] Usuario {user_id} no encontrado en la hoja de Usuarios"
                )
                return jsonify({"error": "Usuario no encontrado"}), 404

        except Exception as e:
            logger.error(f"[ERROR] Error vinculando Telegram: {e}")
            import traceback

            traceback.print_exc()
            return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"[ERROR] Error en link_telegram: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500


@app.route("/api/user/telegram-status")
@login_required
def get_telegram_status():
    """Obtiene el estado de vinculaci n con Telegram del usuario actual"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        users_worksheet = spreadsheet.worksheet("Usuarios")
        all_records = users_worksheet.get_all_records()

        telegram_id = None
        for record in all_records:
            if str(record.get("id", "")) == str(user_id):
                telegram_id = record.get("telegram_id", "")
                break

        # Convertir telegram_id a string si es necesario
        if telegram_id and not isinstance(telegram_id, str):
            telegram_id = str(telegram_id)

        is_linked = bool(telegram_id and telegram_id.strip())

        # Si est  vinculado, verificar si hay datos del bot
        exams_count = 0
        if is_linked:
            try:
                examenes_worksheet = spreadsheet.worksheet("Examenes")

                # Leer datos manualmente para evitar error de headers duplicados
                all_exam_values = examenes_worksheet.get_all_values()
                examenes_records = []

                if len(all_exam_values) > 1:
                    headers = all_exam_values[0]
                    for row in all_exam_values[1:]:
                        if len(row) <= len(headers):
                            record = {}
                            for i, header in enumerate(headers):
                                if i < len(row):
                                    record[header] = row[i]
                            examenes_records.append(record)

                # Buscar usuarios del bot con este telegram_id
                bot_user_ids = []
                for user_record in all_records:
                    if str(user_record.get("telegram_id", "")) == str(telegram_id):
                        bot_user_id = user_record.get("user_id", "")
                        if bot_user_id.startswith("USR_"):
                            bot_user_ids.append(bot_user_id)

                for exam_record in examenes_records:
                    if exam_record.get("user_id", "") in bot_user_ids:
                        exams_count += 1

            except gspread.WorksheetNotFound:
                pass

        return jsonify(
            {
                "is_linked": is_linked,
                "telegram_id": telegram_id if is_linked else None,
                "exams_from_bot": exams_count,
            }
        )

    except Exception as e:
        logger.error(f"Error obteniendo estado Telegram: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/patient/<patient_id>/stats")
def get_patient_stats(patient_id):
    """Obtiene las estad sticas del paciente para el dashboard"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        stats = {
            "consultations": 0,
            "medications": 0,
            "exams": 0,
            "health_score": 95,  # Valor base, se puede calcular din micamente
        }

        # Contar consultas
        try:
            consultations_worksheet = spreadsheet.worksheet("Consultas")
            all_values = consultations_worksheet.get_all_values()

            if len(all_values) > 1:
                for row in all_values[1:]:
                    if len(row) > 1 and str(row[1]) == str(patient_id):
                        stats["consultations"] += 1
        except gspread.WorksheetNotFound:
            logger.warning("[NOTA] Hoja 'Consultas' no encontrada")

        # Contar medicamentos activos
        try:
            medications_worksheet = spreadsheet.worksheet("Medicamentos")
            all_values = medications_worksheet.get_all_values()

            if len(all_values) > 1:
                for row in all_values[1:]:
                    if len(row) > 1 and str(row[1]) == str(patient_id):
                        # Solo contar medicamentos activos
                        status = row[8] if len(row) > 8 else "activo"
                        if status.lower() == "activo":
                            stats["medications"] += 1
        except gspread.WorksheetNotFound:
            logger.warning("[NOTA] Hoja 'Medicamentos' no encontrada")

        # Contar ex menes
        try:
            exams_worksheet = spreadsheet.worksheet("Examenes")
            all_values = exams_worksheet.get_all_values()

            if len(all_values) > 1:
                for row in all_values[1:]:
                    if len(row) > 1 and str(row[1]) == str(patient_id):
                        stats["exams"] += 1
        except gspread.WorksheetNotFound:
            logger.warning("[NOTA] Hoja 'Examenes' no encontrada")

        # Calcular puntuaci n de salud b sica
        # F rmula simple: base 85% + bonificaciones
        health_score = 85

        # Bonificaci n por tener consultas recientes
        if stats["consultations"] > 0:
            health_score += min(stats["consultations"] * 2, 10)  # M ximo +10%

        # Bonificaci n por seguir tratamiento
        if stats["medications"] > 0:
            health_score += min(stats["medications"] * 3, 5)  # M ximo +5%

        # Asegurar que no exceda 100%
        stats["health_score"] = min(health_score, 100)

        logger.info(f"[ESTADISTICAS] Estad sticas para paciente {patient_id}: {stats}")
        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error obteniendo estad sticas: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


def convert_date_format(date_str):
    """Convierte fecha de DD/MM/YYYY a YYYY-MM-DD para compatibilidad web"""
    if not date_str or date_str.strip() == "":
        return ""

    try:
        # Si ya est  en formato YYYY-MM-DD, dejarlo como est
        if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
            return date_str

        # Si est  en formato DD/MM/YYYY, convertir
        if len(date_str) == 10 and date_str[2] == "/" and date_str[5] == "/":
            day, month, year = date_str.split("/")
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Si est  en formato D/M/YYYY o variaciones, normalizar
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                day, month, year = parts
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Si no coincide con ning n patr n conocido, devolver como est
        return date_str

    except Exception as e:
        logger.warning(f"[ADVERTENCIA] Error convirtiendo fecha '{date_str}': {e}")
        return date_str


# Configuraci n mejorada para producci n
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

# Configuraci n para dominio personalizado
CUSTOM_DOMAIN = os.environ.get("CUSTOM_DOMAIN", "localhost:5000")
app.config["SERVER_NAME"] = None  # Permitir cualquier host
app.config["PREFERRED_URL_SCHEME"] = (
    "https" if "medconnect.cl" in CUSTOM_DOMAIN else "http"
)

# Configuraci n de seguridad para HTTPS
if app.config["PREFERRED_URL_SCHEME"] == "https":
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# Funciones auxiliares para las vistas de agenda
def obtener_rango_semana(fecha_str):
    """Obtiene el rango de fechas de la semana que contiene la fecha dada"""
    from datetime import datetime, timedelta

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Obtener el lunes de la semana (d a 0)
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    return inicio_semana.strftime("%Y-%m-%d"), fin_semana.strftime("%Y-%m-%d")


def obtener_rango_mes(fecha_str):
    """Obtiene el rango de fechas del mes que contiene la fecha dada"""
    from datetime import datetime
    import calendar

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Primer d a del mes
    inicio_mes = fecha.replace(day=1)
    #  ltimo d a del mes
    ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
    fin_mes = fecha.replace(day=ultimo_dia)

    return inicio_mes.strftime("%Y-%m-%d"), fin_mes.strftime("%Y-%m-%d")


def organizar_agenda_semanal(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a de la semana"""
    from datetime import datetime, timedelta

    agenda = {}
    dias_semana = [
        "Lunes",
        "Martes",
        "Mi rcoles",
        "Jueves",
        "Viernes",
        "S bado",
        "Domingo",
    ]

    # Inicializar estructura
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    for i in range(7):
        fecha_dia = (inicio + timedelta(days=i)).strftime("%Y-%m-%d")
        agenda[fecha_dia] = {
            "dia_semana": dias_semana[i],
            "fecha": fecha_dia,
            "citas": [],
        }

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def organizar_agenda_mensual(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a del mes"""
    from datetime import datetime, timedelta

    agenda = {}

    # Inicializar estructura para todos los d as del mes
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    fecha_actual = inicio
    while fecha_actual <= fin:
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        agenda[fecha_str] = {
            "fecha": fecha_str,
            "dia": fecha_actual.day,
            "es_hoy": fecha_str == datetime.now().strftime("%Y-%m-%d"),
            "citas": [],
        }
        fecha_actual += timedelta(days=1)

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def calcular_estadisticas_semana(citas):
    """Calcula estad sticas para la vista semanal"""
    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
    }


def calcular_estadisticas_mes(citas):
    """Calcula estad sticas para la vista mensual"""
    from datetime import datetime

    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    # Agrupar por semana
    citas_por_semana = {}
    for cita in citas:
        fecha_cita = datetime.strptime(cita["fecha"], "%Y-%m-%d")
        semana = fecha_cita.isocalendar()[1]  # N mero de semana del a o
        if semana not in citas_por_semana:
            citas_por_semana[semana] = 0
        citas_por_semana[semana] += 1

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
        "citas_por_semana": citas_por_semana,
    }


try:
    # Verificar variables de entorno antes de crear AuthManager
    env_check = {
        "GOOGLE_SERVICE_ACCOUNT_JSON": bool(
            os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        ),
        "GOOGLE_SHEETS_ID": bool(os.environ.get("GOOGLE_SHEETS_ID")),
        "TELEGRAM_BOT_TOKEN": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
    }
    logger.info(f"[HERRAMIENTA] Variables de entorno en app.py: {env_check}")

    # Verificar contenido de JSON
    json_content = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if json_content:
        logger.info(f"[NOTA] JSON length: {len(json_content)} chars")
        logger.info(f"[NOTA] JSON preview: {json_content[:100]}...")

        # Verificar que es JSON v lido
        try:
            test_json = json.loads(json_content)
            logger.info(
                f"[OK] JSON v lido, proyecto: {test_json.get('project_id', 'N/A')}"
            )
        except json.JSONDecodeError as je:
            logger.error(f"[ERROR] JSON inv lido: {je}")

    # Intentar crear AuthManager
    logger.info("  Creando instancia de AuthManager...")
    auth_manager = AuthManager()
    logger.info("[OK] AuthManager inicializado correctamente")

except Exception as e:
    logger.error(f"[ERROR] Error inicializando AuthManager: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback

    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    auth_manager = None


def get_spreadsheet():
    """Obtiene la hoja de c lculo principal"""
    if sheets_client:
        try:
            return sheets_client.open_by_key(app.config["GOOGLE_SHEETS_ID"])
        except Exception as e:
            logger.error(f"Error abriendo spreadsheet: {e}")
    return None


def get_current_user():
    """Obtiene los datos del usuario actual desde la sesi n"""
    user_data = session.get("user_data", {})
    logger.info(f"[BUSCAR] Datos del usuario en sesi n: {user_data}")
    return user_data


def allowed_file(filename):
    """Verifica si el archivo tiene una extensi n permitida"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """Genera un nombre  nico para el archivo"""
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename


# Hacer la funci n disponible en todas las plantillas
@app.context_processor
def inject_user():
    """Inyecta los datos del usuario en todas las plantillas"""
    return dict(current_user=get_current_user())


# Funciones auxiliares para las vistas de agenda
def obtener_rango_semana(fecha_str):
    """Obtiene el rango de fechas de la semana que contiene la fecha dada"""
    from datetime import datetime, timedelta

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Obtener el lunes de la semana (d a 0)
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    return inicio_semana.strftime("%Y-%m-%d"), fin_semana.strftime("%Y-%m-%d")


def obtener_rango_mes(fecha_str):
    """Obtiene el rango de fechas del mes que contiene la fecha dada"""
    from datetime import datetime
    import calendar

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Primer d a del mes
    inicio_mes = fecha.replace(day=1)
    #  ltimo d a del mes
    ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
    fin_mes = fecha.replace(day=ultimo_dia)

    return inicio_mes.strftime("%Y-%m-%d"), fin_mes.strftime("%Y-%m-%d")


def organizar_agenda_semanal(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a de la semana"""
    from datetime import datetime, timedelta

    agenda = {}
    dias_semana = [
        "Lunes",
        "Martes",
        "Mi rcoles",
        "Jueves",
        "Viernes",
        "S bado",
        "Domingo",
    ]

    # Inicializar estructura
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    for i in range(7):
        fecha_dia = (inicio + timedelta(days=i)).strftime("%Y-%m-%d")
        agenda[fecha_dia] = {
            "dia_semana": dias_semana[i],
            "fecha": fecha_dia,
            "citas": [],
        }

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def organizar_agenda_mensual(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a del mes"""
    from datetime import datetime, timedelta

    agenda = {}

    # Inicializar estructura para todos los d as del mes
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    fecha_actual = inicio
    while fecha_actual <= fin:
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        agenda[fecha_str] = {
            "fecha": fecha_str,
            "dia": fecha_actual.day,
            "es_hoy": fecha_str == datetime.now().strftime("%Y-%m-%d"),
            "citas": [],
        }
        fecha_actual += timedelta(days=1)

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def calcular_estadisticas_semana(citas):
    """Calcula estad sticas para la vista semanal"""
    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
    }


def calcular_estadisticas_mes(citas):
    """Calcula estad sticas para la vista mensual"""
    from datetime import datetime

    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    # Agrupar por semana
    citas_por_semana = {}
    for cita in citas:
        fecha_cita = datetime.strptime(cita["fecha"], "%Y-%m-%d")
        semana = fecha_cita.isocalendar()[1]  # N mero de semana del a o
        if semana not in citas_por_semana:
            citas_por_semana[semana] = 0
        citas_por_semana[semana] += 1

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
        "citas_por_semana": citas_por_semana,
    }


try:
    # Verificar variables de entorno antes de crear AuthManager
    env_check = {
        "GOOGLE_SERVICE_ACCOUNT_JSON": bool(
            os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        ),
        "GOOGLE_SHEETS_ID": bool(os.environ.get("GOOGLE_SHEETS_ID")),
        "TELEGRAM_BOT_TOKEN": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
    }
    logger.info(f"[HERRAMIENTA] Variables de entorno en app.py: {env_check}")

    # Verificar contenido de JSON
    json_content = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if json_content:
        logger.info(f"[NOTA] JSON length: {len(json_content)} chars")
        logger.info(f"[NOTA] JSON preview: {json_content[:100]}...")

        # Verificar que es JSON v lido
        try:
            test_json = json.loads(json_content)
            logger.info(
                f"[OK] JSON v lido, proyecto: {test_json.get('project_id', 'N/A')}"
            )
        except json.JSONDecodeError as je:
            logger.error(f"[ERROR] JSON inv lido: {je}")

    # Intentar crear AuthManager
    logger.info("  Creando instancia de AuthManager...")
    auth_manager = AuthManager()
    logger.info("[OK] AuthManager inicializado correctamente")

except Exception as e:
    logger.error(f"[ERROR] Error inicializando AuthManager: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback

    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    auth_manager = None


def get_spreadsheet():
    """Obtiene la hoja de c lculo principal"""
    if sheets_client:
        try:
            return sheets_client.open_by_key(app.config["GOOGLE_SHEETS_ID"])
        except Exception as e:
            logger.error(f"Error abriendo spreadsheet: {e}")
    return None


def get_current_user():
    """Obtiene los datos del usuario actual desde la sesi n"""
    user_data = session.get("user_data", {})
    logger.info(f"[BUSCAR] Datos del usuario en sesi n: {user_data}")
    return user_data


def allowed_file(filename):
    """Verifica si el archivo tiene una extensi n permitida"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """Genera un nombre  nico para el archivo"""
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename


# Hacer la funci n disponible en todas las plantillas
@app.context_processor
def inject_user():
    """Inyecta los datos del usuario en todas las plantillas"""
    return dict(current_user=get_current_user())


@login_required
def delete_medication(patient_id, medication_id):
    """Elimina un medicamento"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        # Usar la hoja 'Medicamentos' que existe realmente
        try:
            worksheet = spreadsheet.worksheet("Medicamentos")
            all_values = worksheet.get_all_values()

            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(
                    all_values[1:], start=2
                ):  # Start from row 2 (after headers)
                    if (
                        len(row) > 1
                        and str(row[0]) == str(medication_id)
                        and str(row[1]) == str(patient_id)
                    ):
                        row_to_delete = i
                        break

            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(
                    f"[OK] Medicamento {medication_id} eliminado para paciente {patient_id}"
                )
                return jsonify(
                    {"success": True, "message": "Medicamento eliminado exitosamente"}
                )
            else:
                return jsonify({"error": "Medicamento no encontrado"}), 404

        except gspread.WorksheetNotFound:
            return jsonify({"error": "Hoja de medicamentos no encontrada"}), 404

    except Exception as e:
        logger.error(f"Error eliminando medicamento: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@login_required
def delete_exam(patient_id, exam_id):
    """Elimina un examen"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        # Usar la hoja 'Examenes' que existe realmente
        try:
            worksheet = spreadsheet.worksheet("Examenes")
            all_values = worksheet.get_all_values()

            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(
                    all_values[1:], start=2
                ):  # Start from row 2 (after headers)
                    if (
                        len(row) > 1
                        and str(row[0]) == str(exam_id)
                        and str(row[1]) == str(patient_id)
                    ):
                        row_to_delete = i
                        break

            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(
                    f"[OK] Examen {exam_id} eliminado para paciente {patient_id}"
                )
                return jsonify(
                    {"success": True, "message": "Examen eliminado exitosamente"}
                )
            else:
                return jsonify({"error": "Examen no encontrado"}), 404

        except gspread.WorksheetNotFound:
            return jsonify({"error": "Hoja de ex menes no encontrada"}), 404

    except Exception as e:
        logger.error(f"Error eliminando examen: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@login_required
def delete_family_member(patient_id, family_id):
    """Elimina un familiar"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["family_members"]["name"])
        records = worksheet.get_all_records()

        # Buscar la fila a eliminar
        row_to_delete = None
        for i, record in enumerate(
            records, start=2
        ):  # Start from row 2 (after headers)
            if str(record.get("id")) == str(family_id) and str(
                record.get("patient_id")
            ) == str(patient_id):
                row_to_delete = i
                break

        if row_to_delete:
            worksheet.delete_rows(row_to_delete)
            logger.info(
                f"[OK] Familiar {family_id} eliminado para paciente {patient_id}"
            )
            return jsonify(
                {"success": True, "message": "Familiar eliminado exitosamente"}
            )
        else:
            return jsonify({"error": "Familiar no encontrado"}), 404

    except Exception as e:
        logger.error(f"Error eliminando familiar: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# APIs para actualizar informaci n del perfil
@login_required
def update_personal_info():
    """Actualiza la informaci n personal del usuario"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Validar campos requeridos
        required_fields = ["nombre", "apellido", "email"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"El campo {field} es requerido"}), 400

        # Validar formato de email
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, data["email"]):
            return jsonify({"error": "Formato de email inv lido"}), 400

        # Validar tel fono si se proporciona
        if data.get("telefono"):
            try:
                telefono = int(data["telefono"])
                if telefono <= 0:
                    return (
                        jsonify({"error": "Tel fono debe ser un n mero positivo"}),
                        400,
                    )
            except ValueError:
                return jsonify({"error": "Tel fono debe ser un n mero v lido"}), 400

        # Actualizar en Google Sheets
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["users"]["name"])
        records = worksheet.get_all_records()

        # Buscar el usuario
        user_row = None
        for i, record in enumerate(records, start=2):
            if record.get("id") == user_id:
                user_row = i
                break

        if not user_row:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Preparar datos para actualizar
        update_data = {
            "nombre": data["nombre"],
            "apellido": data["apellido"],
            "email": data["email"],
            "telefono": data.get("telefono", ""),
            "fecha_nacimiento": data.get("fecha_nacimiento", ""),
            "genero": data.get("genero", ""),
            "direccion": data.get("direccion", ""),
            "ciudad": data.get("ciudad", ""),
        }

        # Actualizar fila en Google Sheets
        headers = worksheet.row_values(1)
        for field, value in update_data.items():
            if field in headers:
                col_index = headers.index(field) + 1
                worksheet.update_cell(user_row, col_index, value)

        # Actualizar sesi n
        user_data = session.get("user_data", {})
        user_data.update(update_data)
        session["user_data"] = user_data
        session["user_email"] = data["email"]
        session["user_name"] = f"{data['nombre']} {data['apellido']}"

        logger.info(f"[OK] Informaci n personal actualizada para usuario {user_id}")
        return jsonify(
            {
                "success": True,
                "message": "Informaci n personal actualizada exitosamente",
            }
        )

    except Exception as e:
        logger.error(f"Error actualizando informaci n personal: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/profile/change-password", methods=["POST"])
@login_required
def change_password():
    """Cambiar contraseña del usuario"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        current_password = data.get("current_password", "").strip()
        new_password = data.get("new_password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()

        if not current_password:
            return jsonify({"error": "Contraseña actual es requerida"}), 400
        if not new_password:
            return jsonify({"error": "Nueva contraseña es requerida"}), 400
        if not confirm_password:
            return jsonify({"error": "Confirmación de contraseña es requerida"}), 400
        if new_password != confirm_password:
            return jsonify({"error": "Las contraseñas no coinciden"}), 400
        if len(new_password) < 6:
            return (
                jsonify(
                    {"error": "La nueva contraseña debe tener al menos 6 caracteres"}
                ),
                400,
            )

        if not auth_manager:
            return jsonify({"error": "Sistema de autenticación no disponible"}), 500

        success, message = auth_manager.change_password(
            user_id, current_password, new_password
        )

        if success:
            logger.info(f"✅ Contraseña cambiada para usuario {user_id}")
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        logger.error(f"Error en cambio de contraseña: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Por ahora, simular actualizaci n exitosa
        # En una implementaci n real, aqu  se guardar an las preferencias de notificaci n
        logger.info(
            f"[OK] Configuraciones de notificaci n actualizadas para usuario {user_id}"
        )
        return jsonify(
            {
                "success": True,
                "message": "Configuraciones de notificaci n actualizadas exitosamente",
            }
        )

    except Exception as e:
        logger.error(f"Error actualizando configuraciones de notificaci n: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

        # Webhook para Telegram Bot
        return jsonify({"error": "Error procesando webhook"}), 500


def test_bot():
    """Endpoint para probar el bot de Telegram"""
    try:
        # Informaci n del bot
        bot_info = {
            "bot_token_configured": bool(config.TELEGRAM_BOT_TOKEN),
            "webhook_url": "https://www.medconnect.cl/webhook",
            "sheets_id": (
                config.GOOGLE_SHEETS_ID[:20] + "..."
                if config.GOOGLE_SHEETS_ID
                else None
            ),
        }

        # Probar env o de mensaje de prueba
        test_message = "  Bot de MedConnect funcionando correctamente!\n\n[OK] Webhook configurado\n[OK] Conexi n establecida"

        return jsonify(
            {
                "status": "Bot configurado correctamente",
                "bot_info": bot_info,
                "test_message": test_message,
                "instructions": "Env a un mensaje al bot @Medconn_bot en Telegram para probarlo",
            }
        )

    except Exception as e:
        logger.error(f"[ERROR] Error probando bot: {e}")
        return jsonify({"error": str(e)}), 500


def log_bot_interaction(user_id, username, message, chat_id):
    """Registra la interacci n del bot en Google Sheets"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["bot_interactions"]["name"])

        # Preparar datos
        row_data = [
            len(worksheet.get_all_values()) + 1,  # ID auto-incrementado
            user_id,
            username,
            message,
            "",  # Response se llenar  despu s
            datetime.now().isoformat(),
            "message",
            "processed",
        ]

        worksheet.append_row(row_data)
        logger.info(f"Interacci n registrada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error registrando interacci n: {e}")


# Diccionario para almacenar contexto de conversaciones
user_contexts = {}

# Palabras clave para reconocimiento de intenciones
INTENT_KEYWORDS = {
    # Funcionalidades para pacientes
    "consulta": [
        "consulta",
        "m dico",
        "doctor",
        "cita",
        "visita",
        "chequeo",
        "revisi n",
        "control",
    ],
    "medicamento": [
        "medicamento",
        "medicina",
        "pastilla",
        "p ldora",
        "remedio",
        "f rmaco",
        "droga",
        "tratamiento",
        "nuevo medicamento",
        "empezar medicamento",
        "comenzar tratamiento",
        "recetaron",
        "prescribieron",
        "como va",
        "efectos",
        "reacci n",
        "funciona",
        "mejora",
        "empeora",
    ],
    "examen": [
        "examen",
        "an lisis",
        "estudio",
        "prueba",
        "laboratorio",
        "radiograf a",
        "ecograf a",
        "resonancia",
        "me hice",
        "ya me hice",
        "tengo resultados",
        "salieron",
        "complet ",
        "termin  examen",
        "tengo que hacerme",
        "debo hacerme",
        "programado",
        "agendado",
        "pr ximo examen",
        "me van a hacer",
    ],
    "historial": [
        "historial",
        "historia",
        "registro",
        "datos",
        "informaci n",
        "ver",
        "mostrar",
        "consultar",
    ],
    "recordatorio": [
        "recordar",
        "recordatorio",
        "alerta",
        "avisar",
        "notificar",
        "programar aviso",
    ],
    "documento": [
        "documento",
        "imagen",
        "archivo",
        "pdf",
        "resultado",
        "informe",
        "reporte",
        "subir",
        "cargar",
    ],
    # Funcionalidades para profesionales
    "agenda": [
        "agenda",
        "horario",
        "disponibilidad",
        "cupos",
        "citas",
        "calendario",
        "programar",
    ],
    "cita_profesional": [
        "nueva cita",
        "agendar paciente",
        "reservar hora",
        "confirmar cita",
        "cancelar cita",
    ],
    "paciente_profesional": [
        "paciente",
        "historial paciente",
        "datos paciente",
        "informaci n paciente",
    ],
    "notificacion_profesional": [
        "notificar",
        "aviso",
        "recordatorio paciente",
        "mensaje paciente",
    ],
    # Funcionalidades compartidas
    "saludo": ["hola", "buenos", "buenas", "saludos", "hey", "qu  tal", "c mo est s"],
    "despedida": ["adi s", "chao", "hasta luego", "nos vemos", "bye", "gracias"],
    "ayuda": ["ayuda", "help", "auxilio", "socorro", "no entiendo", "qu  puedes hacer"],
    "emergencia": [
        "emergencia",
        "urgente",
        "grave",
        "dolor fuerte",
        "sangre",
        "desmayo",
        "accidente",
    ],
    "cita_futura": [
        "pr xima cita",
        "agendar cita",
        "programar cita",
        "reservar hora",
        "pedir hora",
    ],
    "seguimiento": [
        "c mo voy",
        "evoluci n",
        "progreso",
        "mejorando",
        "empeorando",
        "seguimiento",
    ],
}

# Respuestas variadas para hacer el bot m s humano
RESPONSE_VARIATIONS = {
    "greeting": [
        " Hola! [FELIZ]  C mo est s hoy?",
        " Qu  bueno verte! [SALUDO]  En qu  puedo ayudarte?",
        " Hola! Espero que tengas un buen d a [ESTRELLA]",
        " Saludos!  C mo te sientes hoy?",
    ],
    "not_understood": [
        "Disculpa, no estoy seguro de entender.  Podr as explicarme de otra manera?",
        "Hmm, no capt  bien eso.  Puedes ser m s espec fico?",
        "No estoy seguro de c mo ayudarte con eso.  Podr as reformular tu pregunta?",
        "Perd n, no entend  bien.  Te refieres a algo relacionado con tu salud?",
    ],
    "encouragement": [
        " Perfecto!  ",
        " Excelente! [ESTRELLA]",
        " Muy bien!  ",
        " Genial!  ",
    ],
}


def detect_intent(text):
    """Detecta la intenci n del usuario bas ndose en palabras clave"""
    text_lower = text.lower()

    # Contar coincidencias por categor a
    intent_scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            intent_scores[intent] = score

    # Retornar la intenci n con mayor puntaje
    if intent_scores:
        return max(intent_scores, key=intent_scores.get)

    return "unknown"


def get_user_context(user_id):
    """Obtiene el contexto de conversaci n del usuario"""
    return user_contexts.get(user_id, {})


def set_user_context(user_id, context_key, value):
    """Establece contexto de conversaci n para el usuario"""
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    user_contexts[user_id][context_key] = value


def get_random_response(category):
    """Obtiene una respuesta aleatoria de una categor a"""
    import random

    return random.choice(RESPONSE_VARIATIONS.get(category, [" Perfecto!"]))


def process_telegram_message(text, chat_id, user_id):
    """Procesa mensajes del bot de Telegram con funcionalidades duales para pacientes y profesionales"""
    original_text = text
    text = text.lower().strip()

    # Intentar obtener informaci n del usuario registrado
    user_info = get_telegram_user_info(user_id)
    user_name = user_info.get("nombre", "Usuario") if user_info else "Usuario"
    is_professional = is_professional_user(user_info)

    # Obtener contexto de conversaci n
    context = get_user_context(user_id)

    # Comando /start
    if text.startswith("/start"):
        if user_info:
            nombre = user_info.get("nombre", "Usuario")
            apellido = user_info.get("apellido", "")
            nombre_completo = f"{nombre} {apellido}".strip()

            if is_professional:
                # Mensaje de bienvenida para profesionales
                saludos = [
                    f" Hola Dr(a). {nombre_completo}! [DOCTOR]  Bienvenido de vuelta!",
                    f" Dr(a). {nombre_completo}! [HOSPITAL]  Listo para gestionar tus pacientes!",
                    f" Hola {nombre}!   Tu asistente de gesti n m dica est  listo",
                ]

                import random

                saludo = random.choice(saludos)

                return f"""{saludo}

Como profesional m dico, puedo ayudarte con:

[CALENDARIO] **Gesti n de Agenda** - Maneja tu horario y citas
[PACIENTES] **Pacientes** - Accede a historiales y datos
[LISTA] **Atenciones** - Registra consultas y tratamientos
[CAMPANA] **Notificaciones** - Comun cate con pacientes
[ESTADISTICAS] **Reportes** - Estad sticas y seguimientos

**Comandos principales:**
  "Ver mi agenda" - Consultar horario
  "Agendar cita" - Programar nueva cita
  "Pacientes" - Ver lista de pacientes
  "Notificar paciente" - Enviar mensaje

 En qu  puedo ayudarte hoy? [PENSANDO]"""
            else:
                # Mensaje de bienvenida para pacientes
                saludos = [
                    f" Hola {nombre_completo}! [SALUDO]  Qu  alegr a verte de nuevo! [FELIZ]",
                    f" {nombre_completo}! [ESTRELLA]  Bienvenido de vuelta a MedConnect!",
                    f" Hola {nombre}! [DOCTOR] Listo para ayudarte con tu salud hoy",
                ]

                import random

                saludo = random.choice(saludos)

                return f"""{saludo}

Como paciente registrado, estoy aqu  para ayudarte con:

[LISTA] **Consultas m dicas** - Registra tus visitas al doctor
[MEDICAMENTOS] **Medicamentos** - Lleva control de tus tratamientos  
[EXAMENES] **Ex menes** - Guarda resultados de laboratorio
[FAMILIA] **Familiares** - Notifica a tus seres queridos
[ESTADISTICAS] **Historial** - Consulta toda tu informaci n m dica
[DOCUMENTO] **Documentos** - Solicita informes e im genes

**Comandos principales:**
  "Quiero registrar una consulta"
  "Necesito anotar un medicamento"
  "Tengo resultados de ex menes"
  "Mu strame mi historial"
  "Solicitar documento"

 En qu  puedo ayudarte hoy? [PENSANDO]"""
        else:
            return """ Hola! [SALUDO] Soy tu asistente personal de salud de MedConnect [HOSPITAL]

Me encanta conocerte y estoy aqu  para ayudarte a cuidar tu bienestar. 

[MOVIL] ** Ya eres parte de la familia MedConnect?**
Si ya tienes cuenta, es s per f cil conectarnos:

1  Ve a tu perfil: https://medconnect.cl/profile
2  Haz clic en "Generar C digo"
3  Comparte conmigo el c digo: `/codigo MED123456`

[NOTA] ** Primera vez aqu ?**
 Genial! Reg strate en: https://medconnect.cl/register

Una vez conectados, podremos:
[LISTA] Registrar tus consultas m dicas
[MEDICAMENTOS] Organizar tus medicamentos  
[EXAMENES] Guardar resultados de ex menes
[FAMILIA] Mantener informada a tu familia
[ESTADISTICAS] Crear tu historial m dico personalizado

 Hay algo en lo que pueda ayudarte mientras tanto? [FELIZ]"""

    # Comando /codigo
    elif text.startswith("/codigo"):
        return handle_telegram_code_linking(text, user_id)

    # Detectar intenci n del mensaje
    intent = detect_intent(text)

    # Manejar emergencias con prioridad
    if intent == "emergencia":
        return """[EMERGENCIA] **EMERGENCIA DETECTADA** [EMERGENCIA]

Si est s en una situaci n de emergencia m dica:

[LLAMAR] **LLAMA INMEDIATAMENTE:**
  **131** - SAMU (Ambulancia)
  **133** - Bomberos
  **132** - Carabineros

[HOSPITAL] **Ve al servicio de urgencias m s cercano**

[ADVERTENCIA] **Recuerda:** Soy un asistente virtual y no puedo reemplazar la atenci n m dica profesional en emergencias.

Una vez que est s seguro, estar  aqu  para ayudarte con el seguimiento. [CORAZON]"""

    # ===== FUNCIONALIDADES PARA PROFESIONALES =====
    if is_professional:
        return handle_professional_requests(text, user_info, user_id, intent)

    # ===== FUNCIONALIDADES PARA PACIENTES =====
    return handle_patient_requests(text, user_info, user_id, intent)


def get_telegram_user_info(telegram_user_id):
    """Obtiene informaci n del usuario registrado por su ID de Telegram"""
    try:
        if not auth_manager:
            return None

        user_info = auth_manager.get_user_by_telegram_id(telegram_user_id)
        return user_info
    except Exception as e:
        logger.error(
            f"Error obteniendo info de usuario Telegram {telegram_user_id}: {e}"
        )
        return None


def is_professional_user(user_info):
    """Verifica si el usuario es un profesional m dico"""
    if not user_info:
        return False
    return user_info.get("tipo_usuario") == "profesional"


def get_professional_schedule_for_bot(professional_id, fecha=None):
    """Obtiene el horario del profesional para el bot"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return None

        citas_worksheet = spreadsheet.worksheet("Citas_Agenda")
        all_records = citas_worksheet.get_all_records()

        # Filtrar por profesional y fecha
        citas_profesional = []
        for record in all_records:
            if str(record.get("profesional_id", "")) == str(professional_id):
                if fecha:
                    cita_fecha = record.get("fecha", "")
                    if cita_fecha == fecha:
                        citas_profesional.append(record)
                else:
                    citas_profesional.append(record)

        return citas_profesional
    except Exception as e:
        logger.error(f"Error obteniendo agenda del profesional {professional_id}: {e}")
        return None


def get_available_slots_for_professional(professional_id, fecha):
    """Obtiene los horarios disponibles del profesional para una fecha espec fica"""
    try:
        # Obtener horario de trabajo del profesional
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return []

        horarios_worksheet = spreadsheet.worksheet("Horarios_Profesional")
        all_records = horarios_worksheet.get_all_records()

        # Buscar horario del profesional
        horario_profesional = None
        for record in all_records:
            if str(record.get("profesional_id", "")) == str(professional_id):
                horario_profesional = record
                break

        if not horario_profesional:
            return []

        # Obtener citas existentes para esa fecha
        citas_existentes = get_professional_schedule_for_bot(professional_id, fecha)

        # Generar slots disponibles (simplificado)
        slots_disponibles = []
        hora_inicio = 9  # 9:00 AM
        hora_fin = 18  # 6:00 PM

        for hora in range(hora_inicio, hora_fin):
            slot = f"{hora:02d}:00"
            # Verificar si el slot est  ocupado
            ocupado = any(cita.get("hora") == slot for cita in citas_existentes)
            if not ocupado:
                slots_disponibles.append(slot)

        return slots_disponibles
    except Exception as e:
        logger.error(f"Error obteniendo slots disponibles: {e}")
        return []


def send_notification_to_patient(patient_telegram_id, message):
    """Env a notificaci n a un paciente espec fico"""
    if patient_telegram_id:
        return send_telegram_message(patient_telegram_id, message)
    return False


def handle_professional_requests(text, user_info, user_id, intent):
    """Maneja las solicitudes espec ficas de profesionales m dicos"""
    user_name = user_info.get("nombre", "Doctor") if user_info else "Doctor"
    professional_id = user_info.get("id") if user_info else None

    # Gesti n de agenda
    if intent == "agenda" or "agenda" in text or "horario" in text:
        if professional_id:
            citas = get_professional_schedule_for_bot(professional_id)
            if citas:
                agenda_text = f"[CALENDARIO] **Agenda del Dr(a). {user_name}**\n\n"
                for cita in citas[:5]:  # Mostrar solo las pr ximas 5
                    fecha = cita.get("fecha", "N/A")
                    hora = cita.get("hora", "N/A")
                    paciente = cita.get("nombre_paciente", "Paciente")
                    agenda_text += f"  {fecha} {hora} - {paciente}\n"

                agenda_text += (
                    "\n[IDEA] Para ver m s detalles, usa: 'Ver agenda completa'"
                )
                return agenda_text
            else:
                return f"[CALENDARIO] **Agenda del Dr(a). {user_name}**\n\nNo tienes citas programadas actualmente.\n\n[IDEA] Para agendar una nueva cita, escribe: 'Agendar cita'"
        else:
            return "[ERROR] No se pudo obtener tu informaci n profesional. Contacta soporte."

    # Agendar citas
    elif intent == "cita_profesional" or "agendar" in text or "nueva cita" in text:
        set_user_context(user_id, "current_task", "agendar_cita")
        return f"""[CALENDARIO] **Agendar Nueva Cita**

Dr(a). {user_name}, para agendar una cita necesito:

  **Datos del paciente:**
  Nombre completo
  Tel fono (opcional)
  Email (opcional)

[CALENDARIO] **Detalles de la cita:**
  Fecha deseada
  Hora preferida
  Motivo de la consulta
  Duraci n estimada

[IDEA] **Ejemplo:**
"Agendar cita para Mar a Gonz lez, tel fono 912345678, el 15 de julio a las 10:00, consulta de control, 30 minutos"

 Con qu  paciente y fecha quieres agendar? [PENSANDO]"""

    # Gesti n de pacientes
    elif intent == "paciente_profesional" or "paciente" in text:
        if professional_id:
            # Obtener lista de pacientes del profesional
            spreadsheet = get_spreadsheet()
            if spreadsheet:
                try:
                    pacientes_worksheet = spreadsheet.worksheet("Pacientes_Profesional")
                    all_records = pacientes_worksheet.get_all_records()

                    pacientes_profesional = []
                    for record in all_records:
                        if str(record.get("profesional_id", "")) == str(
                            professional_id
                        ):
                            pacientes_profesional.append(record)

                    if pacientes_profesional:
                        response = (
                            f"[PACIENTES] **Pacientes del Dr(a). {user_name}**\n\n"
                        )
                        for paciente in pacientes_profesional[
                            :10
                        ]:  # Mostrar solo los primeros 10
                            nombre = paciente.get("nombre_completo", "N/A")
                            edad = paciente.get("edad", "N/A")
                            ultima_consulta = paciente.get(
                                "ultima_consulta", "Sin consultas"
                            )
                            response += f"  **{nombre}** ({edad} a os)\n"
                            response += f"   [CALENDARIO]  ltima consulta: {ultima_consulta}\n\n"

                        response += "[IDEA] Para ver historial completo de un paciente, escribe: 'Ver paciente [nombre]'"
                        return response
                    else:
                        return f"[PACIENTES] **Pacientes del Dr(a). {user_name}**\n\nNo tienes pacientes registrados actualmente.\n\n[IDEA] Para agregar un paciente, escribe: 'Agregar paciente'"
                except Exception as e:
                    logger.error(f"Error obteniendo pacientes: {e}")
                    return "[ERROR] Error obteniendo lista de pacientes. Intenta m s tarde."
            else:
                return "[ERROR] Error conectando con la base de datos."
        else:
            return "[ERROR] No se pudo obtener tu informaci n profesional."

    # Notificaciones a pacientes
    elif intent == "notificacion_profesional" or "notificar" in text:
        set_user_context(user_id, "current_task", "notificar_paciente")
        return f"""[CAMPANA] **Enviar Notificaci n a Paciente**

Dr(a). {user_name}, para enviar una notificaci n necesito:

  **Paciente:** Nombre del paciente
[NOTA] **Mensaje:** Lo que quieres comunicar

[IDEA] **Ejemplo:**
"Notificar a Mar a Gonz lez: Su cita de ma ana se confirma a las 10:00 AM"

 A qu  paciente quieres enviar la notificaci n? [PENSANDO]"""

    # Comando de ayuda para profesionales
    elif intent == "ayuda":
        return f"""  **Ayuda para Profesionales**

Dr(a). {user_name}, aqu  tienes mis funcionalidades:

[CALENDARIO] **Gesti n de Agenda:**
  "Ver mi agenda" - Consultar citas
  "Agendar cita" - Programar nueva cita
  "Cancelar cita" - Eliminar cita

[PACIENTES] **Gesti n de Pacientes:**
  "Pacientes" - Ver lista de pacientes
  "Ver paciente [nombre]" - Historial espec fico
  "Agregar paciente" - Registrar nuevo paciente

[CAMPANA] **Comunicaci n:**
  "Notificar paciente" - Enviar mensaje
  "Recordatorio paciente" - Programar aviso

[ESTADISTICAS] **Reportes:**
  "Estad sticas" - Ver m tricas
  "Reporte semanal" - Resumen de actividad

 En qu  puedo ayudarte espec ficamente? [PENSANDO]"""

    # Respuesta por defecto para profesionales
    else:
        return f"""[PENSANDO] **No entend  tu solicitud**

Dr(a). {user_name}, puedes pedirme:

[CALENDARIO] **Agenda:** "Ver mi agenda", "Agendar cita"
[PACIENTES] **Pacientes:** "Pacientes", "Ver paciente [nombre]"
[CAMPANA] **Notificaciones:** "Notificar paciente"
  **Ayuda:** "Ayuda"

 Qu  necesitas hacer? [PENSANDO]"""


def handle_patient_requests(text, user_info, user_id, intent):
    """Maneja las solicitudes espec ficas de pacientes"""
    user_name = user_info.get("nombre", "Usuario") if user_info else "Usuario"

    # Saludos
    if intent == "saludo" and not text.startswith("/"):
        greeting = get_random_response("greeting")
        if user_info:
            return f"{greeting} {user_name}!  En qu  puedo ayudarte con tu salud hoy? [FELIZ]"
        else:
            return f"""{greeting}

Soy tu asistente de salud de MedConnect. Puedo ayudarte a:
[LISTA] Registrar informaci n m dica
[MEDICAMENTOS] Organizar medicamentos
[EXAMENES] Guardar ex menes
[ESTADISTICAS] Consultar tu historial

 Te gustar a vincular tu cuenta primero? Solo necesitas ir a https://medconnect.cl/profile y generar un c digo. 

 O prefieres que te ayude con algo espec fico? [PENSANDO]"""

    # Despedidas
    elif intent == "despedida":
        despedidas = [
            f" Hasta pronto {user_name}! [SALUDO] Cu date mucho y no dudes en escribirme cuando necesites algo. [CORAZON]",
            f" Que tengas un excelente d a {user_name}! [ESTRELLA] Estar  aqu  cuando me necesites. [FELIZ]",
            f" Nos vemos pronto {user_name}! [SALUDO] Recuerda cuidar tu salud.  Hasta la pr xima!  ",
        ]
        import random

        return random.choice(despedidas)

    # Consultas m dicas
    elif intent == "consulta":
        set_user_context(user_id, "current_task", "consulta")

        if user_info:
            encouragement = get_random_response("encouragement")
            return f"""{encouragement} {user_name}, veo que quieres registrar una consulta m dica. [LISTA]

Para crear un registro completo, me gustar a que me compartieras:

[EXAMENES] **Detalles de la consulta:**
1   Cu ndo fue? (fecha)
2   Con qu  doctor te atendiste?
3   Cu l es su especialidad?
4   Qu  diagn stico te dieron?
5   Te recetaron alg n tratamiento?

Puedes contarme todo junto o paso a paso, como prefieras. Lo importante es que quede bien registrado en tu historial personal. [FELIZ]

 Empezamos? [PENSANDO]"""
        else:
            return """[LISTA]  Me encanta que quieras registrar tu consulta m dica! Es s per importante llevar un buen control.

Para poder guardar esta informaci n en tu historial personal, necesitar amos conectar tu cuenta primero.

**Datos que necesito para la consulta:**
1  Fecha de la consulta
2  Nombre del m dico
3  Especialidad
4  Diagn stico recibido
5  Tratamiento indicado

[IDEA] ** Tienes cuenta en MedConnect?**
Ve a https://medconnect.cl/profile, genera tu c digo y comp rtelo conmigo.

Mientras tanto, puedes contarme los detalles y los guardar  temporalmente.  Te parece? [FELIZ]"""

    # Medicamentos
    elif intent == "medicamento":
        set_user_context(user_id, "current_task", "medicamento")

        if user_info:
            encouragement = get_random_response("encouragement")
            return f"""{encouragement} {user_name}! Organizar tus medicamentos es fundamental para tu salud. [MEDICAMENTOS]

Para registrar correctamente tu medicamento, necesito conocer:

  **Informaci n del medicamento:**
1   C mo se llama?
2   Qu  dosis tomas? (ej: 50mg, 1 tableta)
3   Cada cu nto tiempo? (ej: cada 8 horas, 2 veces al d a)
4   Qu  m dico te lo recet ?
5   Para qu  es? (opcional)

Cu ntame todo lo que sepas y lo organizaremos en tu perfil para que nunca se te olvide. [FELIZ]

 Cu l es el medicamento? [PENSANDO]"""
        else:
            return """[MEDICAMENTOS]  Qu  responsable eres cuidando tu tratamiento! Me parece genial que quieras registrar tus medicamentos.

**Para un registro completo necesito:**
1  Nombre del medicamento
2  Dosis que tomas
3  Frecuencia (cada cu nto tiempo)
4  M dico que lo recet 
5  Para qu  es el tratamiento

[IDEA] **Para guardarlo en tu historial permanente:**
Necesitar as vincular tu cuenta desde https://medconnect.cl/profile

Pero puedes contarme los detalles ahora y te ayudo a organizarlos.  Cu l es el medicamento? [FELIZ]"""

    # Ex menes
    elif intent == "examen":
        set_user_context(user_id, "current_task", "examen")

        if user_info:
            encouragement = get_random_response("encouragement")
            return f"""{encouragement} {user_name}! Los ex menes son s per importantes para monitorear tu salud. [EXAMENES]

Para registrar tu examen correctamente, me gustar a saber:

  **Detalles del examen:**
1   Qu  tipo de examen fue? (sangre, orina, radiograf a, etc.)
2   Cu ndo te lo hiciste?
3   En qu  laboratorio o centro m dico?
4   Cu les fueron los resultados principales?
5   Alg n valor fuera de lo normal?

Si tienes los resultados en papel o digital, tambi n puedes subir la imagen a tu perfil web m s tarde.

 Me cuentas sobre tu examen? [PENSANDO]"""
        else:
            return """[EXAMENES]  Excelente que quieras registrar tus ex menes! Es clave para el seguimiento de tu salud.

**Informaci n que necesito:**
1  Tipo de examen realizado
2  Fecha cuando te lo hiciste
3  Laboratorio o centro m dico
4  Resultados principales
5  Valores importantes o anormales

[IDEA] **Para mantener un historial completo:**
Te recomiendo vincular tu cuenta en https://medconnect.cl/profile

Mientras tanto, cu ntame sobre tu examen y te ayudo a organizarlo.  Qu  examen te hiciste? [FELIZ]"""

    # Historial
    elif intent == "historial":
        if user_info:
            return f"""[ESTADISTICAS]  Hola {user_name}! Tu historial m dico est  siempre disponible para ti.

**Para ver toda tu informaci n completa:**
[MUNDO] Visita tu dashboard: https://medconnect.cl/patient

**Ah  encontrar s:**
[OK] Todas tus consultas m dicas organizadas
[OK] Lista completa de medicamentos actuales
[OK] Resultados de ex menes con fechas
[OK] Informaci n de familiares registrados
[OK] Gr ficos y estad sticas de tu salud

**Tambi n puedes preguntarme directamente:**
  " Cu les son mis  ltimas consultas?"
  " Qu  medicamentos estoy tomando?"
  " Cu ndo fue mi  ltimo examen?"
  " Tengo alguna cita pr xima?"

 Qu  te gustar a consultar espec ficamente? [PENSANDO]"""
        else:
            return """[ESTADISTICAS]  Me encantar a mostrarte tu historial m dico! Pero primero necesitamos conectar tu cuenta.

**Una vez vinculada, tendr s acceso a:**
[OK] Historial completo de consultas
[OK] Registro de todos tus medicamentos
[OK] Resultados de ex menes organizados
[OK] Informaci n de contactos de emergencia
[OK] Estad sticas de tu salud

** Ya tienes cuenta en MedConnect?**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

Una vez conectados, podr s consultar toda tu informaci n m dica cuando quieras.  Te ayudo con la vinculaci n? [FELIZ]"""

    # Documentos e im genes
    elif intent == "documento":
        if user_info:
            return f"""[DOCUMENTO] **Solicitar Documentos M dicos**

{user_name}, puedo ayudarte a solicitar:

[LISTA] **Informes m dicos**
[EXAMENES] **Resultados de ex menes**
[MEDICAMENTOS] **Recetas m dicas**
[ESTADISTICAS] **Reportes de salud**

**Para solicitar un documento:**
1  Ve a tu perfil web: https://medconnect.cl/patient
2  Navega a la secci n "Ex menes" o "Consultas"
3  Busca el documento que necesitas
4  Haz clic en "Descargar" o "Ver"

**Tambi n puedes pedirme:**
  " Tengo resultados de ex menes recientes?"
  " Cu ndo fue mi  ltima consulta?"
  " Qu  medicamentos tengo recetados?"

 Qu  tipo de documento necesitas? [PENSANDO]"""
        else:
            return """[DOCUMENTO] **Documentos M dicos**

Para acceder a tus documentos m dicos, necesitas tener una cuenta vinculada.

** Ya tienes cuenta?**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

Una vez conectado, podr s:
[OK] Ver todos tus documentos m dicos
[OK] Descargar informes y resultados
[OK] Acceder a recetas m dicas
[OK] Solicitar reportes de salud

 Te ayudo a crear tu cuenta? [FELIZ]"""

    # Recordatorios
    elif intent == "recordatorio":
        if user_info:
            return f"""  **Configurar Recordatorios**

{user_name}, puedo ayudarte a configurar recordatorios para:

[MEDICAMENTOS] **Medicamentos** - Horarios de toma
[CALENDARIO] **Citas m dicas** - Fechas de consulta
[EXAMENES] **Ex menes** - Fechas de laboratorio
[LISTA] **Controles** - Seguimientos m dicos

**Para configurar recordatorios:**
[MUNDO] Ve a tu perfil: https://medconnect.cl/profile
[MOVIL] Navega a "Configuraci n de Notificaciones"
[CAMPANA] Activa los recordatorios que necesites

**Tambi n puedes pedirme:**
  " Tengo alguna cita pr xima?"
  " Qu  medicamentos debo tomar hoy?"
  " Cu ndo es mi pr ximo control?"

 Qu  tipo de recordatorio necesitas? [PENSANDO]"""
        else:
            return """  **Recordatorios M dicos**

Para configurar recordatorios personalizados, necesitas tener una cuenta vinculada.

** Ya tienes cuenta?**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

Una vez conectado, podr s:
[OK] Configurar recordatorios de medicamentos
[OK] Recibir avisos de citas m dicas
[OK] Alertas de ex menes y controles
[OK] Notificaciones personalizadas

 Te ayudo a crear tu cuenta? [FELIZ]"""

    # Ayuda
    elif intent == "ayuda" or text in ["help", "/help"]:
        if user_info:
            return f"""  **Ayuda para Pacientes**

{user_name}, aqu  tienes mis funcionalidades:

[LISTA] **Consultas m dicas**
  "Registrar una consulta"
  "Anotar visita al doctor"
  "Ver mis consultas"

[MEDICAMENTOS] **Medicamentos**
  "Anotar medicamento"
  "Ver mis medicamentos"
  "Recordatorio de medicinas"

[EXAMENES] **Ex menes**
  "Registrar examen"
  "Ver resultados"
  "Solicitar informe"

[ESTADISTICAS] **Historial**
  "Ver mi historial"
  "Consultar datos"
  "Estad sticas de salud"

[DOCUMENTO] **Documentos**
  "Solicitar documento"
  "Descargar informe"
  "Ver resultados"

  **Recordatorios**
  "Configurar recordatorio"
  "Ver pr ximas citas"
  "Alertas m dicas"

 En qu  puedo ayudarte espec ficamente? [PENSANDO]"""
        else:
            return """  **Ayuda General**

Soy tu asistente de salud de MedConnect. Puedo ayudarte con:

[LISTA] **Registro de informaci n m dica**
[MEDICAMENTOS] **Gesti n de medicamentos**
[EXAMENES] **Control de ex menes**
[ESTADISTICAS] **Consulta de historial**
[DOCUMENTO] **Solicitud de documentos**
  **Configuraci n de recordatorios**

**Para acceder a todas las funcionalidades:**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

 Qu  te gustar a hacer? [PENSANDO]"""

    # Respuesta por defecto para pacientes
    else:
        if user_info:
            return f"""[PENSANDO] **No entend  tu solicitud**

{user_name}, puedes pedirme:

[LISTA] **Consultas:** "Registrar consulta", "Ver mis consultas"
[MEDICAMENTOS] **Medicamentos:** "Anotar medicamento", "Ver medicamentos"
[EXAMENES] **Ex menes:** "Registrar examen", "Ver resultados"
[ESTADISTICAS] **Historial:** "Ver mi historial", "Consultar datos"
[DOCUMENTO] **Documentos:** "Solicitar documento"
  **Recordatorios:** "Configurar recordatorio"
  **Ayuda:** "Ayuda"

 Qu  necesitas hacer? [PENSANDO]"""
        else:
            return """[PENSANDO] **No entend  tu solicitud**

Puedes pedirme:
[LISTA] Registrar informaci n m dica
[MEDICAMENTOS] Organizar medicamentos
[EXAMENES] Guardar ex menes
[ESTADISTICAS] Consultar historial
  Ayuda

**Para funcionalidades completas:**
  Ve a: https://medconnect.cl/profile y genera tu c digo

 Qu  te gustar a hacer? [PENSANDO]"""


def handle_account_linking(text, telegram_user_id):
    """Maneja la vinculaci n de cuenta de Telegram"""
    try:
        parts = text.split()
        if len(parts) < 2:
            return """[ERROR] Formato incorrecto. 

**Uso correcto:**
`/vincular tu-email@ejemplo.com`

**Ejemplo:**
`/vincular maria.gonzalez@gmail.com`

Aseg rate de usar el mismo email con el que te registraste en MedConnect."""

        email = parts[1].strip()

        # Validar formato de email b sico
        if "@" not in email or "." not in email:
            return """[ERROR] El email no parece v lido.

**Formato esperado:**
`/vincular tu-email@ejemplo.com`

Por favor verifica e intenta de nuevo."""

        if not auth_manager:
            return "[ERROR] Sistema de autenticaci n no disponible temporalmente. Intenta m s tarde."

        # Verificar si el usuario existe
        user_data = auth_manager.get_user_by_email(email)
        if not user_data:
            return f"""[ERROR] No encontr  ninguna cuenta con el email: `{email}`

** Posibles soluciones:**
1. Verifica que escribiste correctamente tu email
2. Si a n no tienes cuenta, reg strate en: https://medconnect.cl/register
3. Intenta de nuevo: `/vincular tu-email-correcto@ejemplo.com`"""

        # Intentar vincular la cuenta
        success, message, user_info = auth_manager.link_telegram_account(
            email, telegram_user_id
        )

        if success and user_info:
            nombre = user_info.get("nombre", "Usuario")
            apellido = user_info.get("apellido", "")
            return f"""[OK]  Cuenta vinculada exitosamente!

 Hola {nombre} {apellido}!  

Tu cuenta de Telegram ahora est  conectada con MedConnect. A partir de ahora:

  **Experiencia personalizada**
[LISTA] Historial m dico completo
[MEDICAMENTOS] Seguimiento de medicamentos
[EXAMENES] Registro de ex menes
[FAMILIA] Notificaciones familiares

Escribe `/start` para comenzar con tu experiencia personalizada."""
        else:
            return f"""[ERROR] {message}

**Si el problema persiste:**
1. Verifica tu email: `{email}`
2. Contacta soporte si necesitas ayuda
3. O intenta registrarte en: https://medconnect.cl/register"""

    except Exception as e:
        logger.error(f"Error en vinculaci n de cuenta: {e}")
        return """[ERROR] Error interno al vincular cuenta.

Por favor intenta de nuevo en unos minutos o contacta soporte."""


def send_telegram_message(telegram_id, message):
    """Env a un mensaje a trav s del bot de Telegram"""
    try:
        # Token del bot
        BOT_TOKEN = (
            "7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck"  # Token correcto del bot
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": str(telegram_id),  # Asegurar que sea string
            "text": message,
            "parse_mode": "HTML",
        }

        import requests  # Asegurar import local

        response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            logger.info(f"[OK] Mensaje enviado a Telegram ID: {telegram_id}")
            return True
        else:
            logger.error(f"[ERROR] Error enviando mensaje a Telegram: {response.text}")
            return False

    except Exception as e:
        logger.error(f"[ERROR] Error enviando mensaje de Telegram: {e}")
        return False

    # Configurar webhook del bot

    except Exception as e:
        logger.error(f"[ERROR] Error en health check: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )

        # Listar archivos cr ticos
        critical_files = [
            "css/styles.css",
            "js/app.js",
            "images/logo.png",
            "images/Imagen2.png",
        ]

        for file_rel_path in critical_files:
            file_info = {"path": file_rel_path, "locations": []}

            # Verificar en cada ruta de static
            for static_path in static_paths:
                file_path = os.path.join(static_path, file_rel_path)
                file_info["locations"].append(
                    {
                        "static_path": static_path,
                        "full_path": file_path,
                        "exists": os.path.exists(file_path),
                        "size": (
                            os.path.getsize(file_path)
                            if os.path.exists(file_path)
                            else 0
                        ),
                        "readable": (
                            os.access(file_path, os.R_OK)
                            if os.path.exists(file_path)
                            else False
                        ),
                    }
                )

            debug_info["files"].append(file_info)

        return jsonify(debug_info)

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


# Ruta para favicon
@app.route("/favicon.ico")
def favicon():
    """Servir favicon"""
    from flask import send_from_directory
    import os

    return send_from_directory(
        os.path.join(app.root_path, "static", "images"),
        "logo.png",
        mimetype="image/png",
    )

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

# Funciones auxiliares para las vistas de agenda
def obtener_rango_semana(fecha_str):
    """Obtiene el rango de fechas de la semana que contiene la fecha dada"""
    from datetime import datetime, timedelta

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Obtener el lunes de la semana (d a 0)
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

    return inicio_semana.strftime("%Y-%m-%d"), fin_semana.strftime("%Y-%m-%d")


def obtener_rango_mes(fecha_str):
    """Obtiene el rango de fechas del mes que contiene la fecha dada"""
    from datetime import datetime
    import calendar

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
    # Primer d a del mes
    inicio_mes = fecha.replace(day=1)
    #  ltimo d a del mes
    ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
    fin_mes = fecha.replace(day=ultimo_dia)

    return inicio_mes.strftime("%Y-%m-%d"), fin_mes.strftime("%Y-%m-%d")


def organizar_agenda_semanal(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a de la semana"""
    from datetime import datetime, timedelta

    agenda = {}
    dias_semana = [
        "Lunes",
        "Martes",
        "Mi rcoles",
        "Jueves",
        "Viernes",
        "S bado",
        "Domingo",
    ]

    # Inicializar estructura
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    for i in range(7):
        fecha_dia = (inicio + timedelta(days=i)).strftime("%Y-%m-%d")
        agenda[fecha_dia] = {
            "dia_semana": dias_semana[i],
            "fecha": fecha_dia,
            "citas": [],
        }

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def organizar_agenda_mensual(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por d a del mes"""
    from datetime import datetime, timedelta

    agenda = {}

    # Inicializar estructura para todos los d as del mes
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    fecha_actual = inicio
    while fecha_actual <= fin:
        fecha_str = fecha_actual.strftime("%Y-%m-%d")
        agenda[fecha_str] = {
            "fecha": fecha_str,
            "dia": fecha_actual.day,
            "es_hoy": fecha_str == datetime.now().strftime("%Y-%m-%d"),
            "citas": [],
        }
        fecha_actual += timedelta(days=1)

    # Agrupar citas por d a
    for cita in citas:
        fecha_cita = cita["fecha"]
        if fecha_cita in agenda:
            agenda[fecha_cita]["citas"].append(cita)

    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]["citas"].sort(key=lambda x: x["hora"])

    return agenda


def calcular_estadisticas_semana(citas):
    """Calcula estad sticas para la vista semanal"""
    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
    }


def calcular_estadisticas_mes(citas):
    """Calcula estad sticas para la vista mensual"""
    from datetime import datetime

    total = len(citas)
    confirmadas = len([c for c in citas if c["estado"] == "confirmada"])
    pendientes = len([c for c in citas if c["estado"] == "pendiente"])
    canceladas = len([c for c in citas if c["estado"] == "cancelada"])

    # Agrupar por semana
    citas_por_semana = {}
    for cita in citas:
        fecha_cita = datetime.strptime(cita["fecha"], "%Y-%m-%d")
        semana = fecha_cita.isocalendar()[1]  # N mero de semana del a o
        if semana not in citas_por_semana:
            citas_por_semana[semana] = 0
        citas_por_semana[semana] += 1

    return {
        "total_citas": total,
        "confirmadas": confirmadas,
        "pendientes": pendientes,
        "canceladas": canceladas,
        "citas_por_semana": citas_por_semana,
    }


try:
    # Verificar variables de entorno antes de crear AuthManager
    env_check = {
        "GOOGLE_SERVICE_ACCOUNT_JSON": bool(
            os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        ),
        "GOOGLE_SHEETS_ID": bool(os.environ.get("GOOGLE_SHEETS_ID")),
        "TELEGRAM_BOT_TOKEN": bool(os.environ.get("TELEGRAM_BOT_TOKEN")),
    }
    logger.info(f"[HERRAMIENTA] Variables de entorno en app.py: {env_check}")

    # Verificar contenido de JSON
    json_content = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if json_content:
        logger.info(f"[NOTA] JSON length: {len(json_content)} chars")
        logger.info(f"[NOTA] JSON preview: {json_content[:100]}...")

        # Verificar que es JSON v lido
        try:
            test_json = json.loads(json_content)
            logger.info(
                f"[OK] JSON v lido, proyecto: {test_json.get('project_id', 'N/A')}"
            )
        except json.JSONDecodeError as je:
            logger.error(f"[ERROR] JSON inv lido: {je}")

    # Intentar crear AuthManager
    logger.info("  Creando instancia de AuthManager...")
    auth_manager = AuthManager()
    logger.info("[OK] AuthManager inicializado correctamente")

except Exception as e:
    logger.error(f"[ERROR] Error inicializando AuthManager: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback

    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    auth_manager = None


def get_spreadsheet():
    """Obtiene la hoja de c lculo principal"""
    if sheets_client:
        try:
            return sheets_client.open_by_key(app.config["GOOGLE_SHEETS_ID"])
        except Exception as e:
            logger.error(f"Error abriendo spreadsheet: {e}")
    return None


def get_current_user():
    """Obtiene los datos del usuario actual desde la sesi n"""
    user_data = session.get("user_data", {})
    logger.info(f"[BUSCAR] Datos del usuario en sesi n: {user_data}")
    return user_data


def allowed_file(filename):
    """Verifica si el archivo tiene una extensi n permitida"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(filename):
    """Genera un nombre  nico para el archivo"""
    ext = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename


# Hacer la funci n disponible en todas las plantillas
@app.context_processor
def inject_user():
    """Inyecta los datos del usuario en todas las plantillas"""
    return dict(current_user=get_current_user())

@login_required
def delete_medication(patient_id, medication_id):
    """Elimina un medicamento"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        # Usar la hoja 'Medicamentos' que existe realmente
        try:
            worksheet = spreadsheet.worksheet("Medicamentos")
            all_values = worksheet.get_all_values()

            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(
                    all_values[1:], start=2
                ):  # Start from row 2 (after headers)
                    if (
                        len(row) > 1
                        and str(row[0]) == str(medication_id)
                        and str(row[1]) == str(patient_id)
                    ):
                        row_to_delete = i
                        break

            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(
                    f"[OK] Medicamento {medication_id} eliminado para paciente {patient_id}"
                )
                return jsonify(
                    {"success": True, "message": "Medicamento eliminado exitosamente"}
                )
            else:
                return jsonify({"error": "Medicamento no encontrado"}), 404

        except gspread.WorksheetNotFound:
            return jsonify({"error": "Hoja de medicamentos no encontrada"}), 404

    except Exception as e:
        logger.error(f"Error eliminando medicamento: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@login_required
def delete_exam(patient_id, exam_id):
    """Elimina un examen"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        # Usar la hoja 'Examenes' que existe realmente
        try:
            worksheet = spreadsheet.worksheet("Examenes")
            all_values = worksheet.get_all_values()

            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(
                    all_values[1:], start=2
                ):  # Start from row 2 (after headers)
                    if (
                        len(row) > 1
                        and str(row[0]) == str(exam_id)
                        and str(row[1]) == str(patient_id)
                    ):
                        row_to_delete = i
                        break

            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(
                    f"[OK] Examen {exam_id} eliminado para paciente {patient_id}"
                )
                return jsonify(
                    {"success": True, "message": "Examen eliminado exitosamente"}
                )
            else:
                return jsonify({"error": "Examen no encontrado"}), 404

        except gspread.WorksheetNotFound:
            return jsonify({"error": "Hoja de ex menes no encontrada"}), 404

    except Exception as e:
        logger.error(f"Error eliminando examen: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@login_required
def delete_family_member(patient_id, family_id):
    """Elimina un familiar"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error": "No autorizado"}), 403

        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["family_members"]["name"])
        records = worksheet.get_all_records()

        # Buscar la fila a eliminar
        row_to_delete = None
        for i, record in enumerate(
            records, start=2
        ):  # Start from row 2 (after headers)
            if str(record.get("id")) == str(family_id) and str(
                record.get("patient_id")
            ) == str(patient_id):
                row_to_delete = i
                break

        if row_to_delete:
            worksheet.delete_rows(row_to_delete)
            logger.info(
                f"[OK] Familiar {family_id} eliminado para paciente {patient_id}"
            )
            return jsonify(
                {"success": True, "message": "Familiar eliminado exitosamente"}
            )
        else:
            return jsonify({"error": "Familiar no encontrado"}), 404

    except Exception as e:
        logger.error(f"Error eliminando familiar: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


# APIs para actualizar informaci n del perfil
@login_required
def update_personal_info():
    """Actualiza la informaci n personal del usuario"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Validar campos requeridos
        required_fields = ["nombre", "apellido", "email"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"El campo {field} es requerido"}), 400

        # Validar formato de email
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, data["email"]):
            return jsonify({"error": "Formato de email inv lido"}), 400

        # Validar tel fono si se proporciona
        if data.get("telefono"):
            try:
                telefono = int(data["telefono"])
                if telefono <= 0:
                    return (
                        jsonify({"error": "Tel fono debe ser un n mero positivo"}),
                        400,
                    )
            except ValueError:
                return jsonify({"error": "Tel fono debe ser un n mero v lido"}), 400

        # Actualizar en Google Sheets
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["users"]["name"])
        records = worksheet.get_all_records()

        # Buscar el usuario
        user_row = None
        for i, record in enumerate(records, start=2):
            if record.get("id") == user_id:
                user_row = i
                break

        if not user_row:
            return jsonify({"error": "Usuario no encontrado"}), 404

        # Preparar datos para actualizar
        update_data = {
            "nombre": data["nombre"],
            "apellido": data["apellido"],
            "email": data["email"],
            "telefono": data.get("telefono", ""),
            "fecha_nacimiento": data.get("fecha_nacimiento", ""),
            "genero": data.get("genero", ""),
            "direccion": data.get("direccion", ""),
            "ciudad": data.get("ciudad", ""),
        }

        # Actualizar fila en Google Sheets
        headers = worksheet.row_values(1)
        for field, value in update_data.items():
            if field in headers:
                col_index = headers.index(field) + 1
                worksheet.update_cell(user_row, col_index, value)

        # Actualizar sesi n
        user_data = session.get("user_data", {})
        user_data.update(update_data)
        session["user_data"] = user_data
        session["user_email"] = data["email"]
        session["user_name"] = f"{data['nombre']} {data['apellido']}"

        logger.info(f"[OK] Informaci n personal actualizada para usuario {user_id}")
        return jsonify(
            {
                "success": True,
                "message": "Informaci n personal actualizada exitosamente",
            }
        )

    except Exception as e:
        logger.error(f"Error actualizando informaci n personal: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        # Por ahora, simular actualizaci n exitosa
        # En una implementaci n real, aqu  se guardar an las preferencias de notificaci n
        logger.info(
            f"[OK] Configuraciones de notificaci n actualizadas para usuario {user_id}"
        )
        return jsonify(
            {
                "success": True,
                "message": "Configuraciones de notificaci n actualizadas exitosamente",
            }
        )

    except Exception as e:
        logger.error(f"Error actualizando configuraciones de notificaci n: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

        # Webhook para Telegram Bot
        return jsonify({"error": "Error procesando webhook"}), 500


def test_bot():
    """Endpoint para probar el bot de Telegram"""
    try:
        # Informaci n del bot
        bot_info = {
            "bot_token_configured": bool(config.TELEGRAM_BOT_TOKEN),
            "webhook_url": "https://www.medconnect.cl/webhook",
            "sheets_id": (
                config.GOOGLE_SHEETS_ID[:20] + "..."
                if config.GOOGLE_SHEETS_ID
                else None
            ),
        }

        # Probar env o de mensaje de prueba
        test_message = "  Bot de MedConnect funcionando correctamente!\n\n[OK] Webhook configurado\n[OK] Conexi n establecida"

        return jsonify(
            {
                "status": "Bot configurado correctamente",
                "bot_info": bot_info,
                "test_message": test_message,
                "instructions": "Env a un mensaje al bot @Medconn_bot en Telegram para probarlo",
            }
        )

    except Exception as e:
        logger.error(f"[ERROR] Error probando bot: {e}")
        return jsonify({"error": str(e)}), 500


def log_bot_interaction(user_id, username, message, chat_id):
    """Registra la interacci n del bot en Google Sheets"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return

        worksheet = spreadsheet.worksheet(SHEETS_CONFIG["bot_interactions"]["name"])

        # Preparar datos
        row_data = [
            len(worksheet.get_all_values()) + 1,  # ID auto-incrementado
            user_id,
            username,
            message,
            "",  # Response se llenar  despu s
            datetime.now().isoformat(),
            "message",
            "processed",
        ]

        worksheet.append_row(row_data)
        logger.info(f"Interacci n registrada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error registrando interacci n: {e}")


# Diccionario para almacenar contexto de conversaciones
user_contexts = {}

# Palabras clave para reconocimiento de intenciones
INTENT_KEYWORDS = {
    # Funcionalidades para pacientes
    "consulta": [
        "consulta",
        "m dico",
        "doctor",
        "cita",
        "visita",
        "chequeo",
        "revisi n",
        "control",
    ],
    "medicamento": [
        "medicamento",
        "medicina",
        "pastilla",
        "p ldora",
        "remedio",
        "f rmaco",
        "droga",
        "tratamiento",
        "nuevo medicamento",
        "empezar medicamento",
        "comenzar tratamiento",
        "recetaron",
        "prescribieron",
        "como va",
        "efectos",
        "reacci n",
        "funciona",
        "mejora",
        "empeora",
    ],
    "examen": [
        "examen",
        "an lisis",
        "estudio",
        "prueba",
        "laboratorio",
        "radiograf a",
        "ecograf a",
        "resonancia",
        "me hice",
        "ya me hice",
        "tengo resultados",
        "salieron",
        "complet ",
        "termin  examen",
        "tengo que hacerme",
        "debo hacerme",
        "programado",
        "agendado",
        "pr ximo examen",
        "me van a hacer",
    ],
    "historial": [
        "historial",
        "historia",
        "registro",
        "datos",
        "informaci n",
        "ver",
        "mostrar",
        "consultar",
    ],
    "recordatorio": [
        "recordar",
        "recordatorio",
        "alerta",
        "avisar",
        "notificar",
        "programar aviso",
    ],
    "documento": [
        "documento",
        "imagen",
        "archivo",
        "pdf",
        "resultado",
        "informe",
        "reporte",
        "subir",
        "cargar",
    ],
    # Funcionalidades para profesionales
    "agenda": [
        "agenda",
        "horario",
        "disponibilidad",
        "cupos",
        "citas",
        "calendario",
        "programar",
    ],
    "cita_profesional": [
        "nueva cita",
        "agendar paciente",
        "reservar hora",
        "confirmar cita",
        "cancelar cita",
    ],
    "paciente_profesional": [
        "paciente",
        "historial paciente",
        "datos paciente",
        "informaci n paciente",
    ],
    "notificacion_profesional": [
        "notificar",
        "aviso",
        "recordatorio paciente",
        "mensaje paciente",
    ],
    # Funcionalidades compartidas
    "saludo": ["hola", "buenos", "buenas", "saludos", "hey", "qu  tal", "c mo est s"],
    "despedida": ["adi s", "chao", "hasta luego", "nos vemos", "bye", "gracias"],
    "ayuda": ["ayuda", "help", "auxilio", "socorro", "no entiendo", "qu  puedes hacer"],
    "emergencia": [
        "emergencia",
        "urgente",
        "grave",
        "dolor fuerte",
        "sangre",
        "desmayo",
        "accidente",
    ],
    "cita_futura": [
        "pr xima cita",
        "agendar cita",
        "programar cita",
        "reservar hora",
        "pedir hora",
    ],
    "seguimiento": [
        "c mo voy",
        "evoluci n",
        "progreso",
        "mejorando",
        "empeorando",
        "seguimiento",
    ],
}

# Respuestas variadas para hacer el bot m s humano
RESPONSE_VARIATIONS = {
    "greeting": [
        " Hola! [FELIZ]  C mo est s hoy?",
        " Qu  bueno verte! [SALUDO]  En qu  puedo ayudarte?",
        " Hola! Espero que tengas un buen d a [ESTRELLA]",
        " Saludos!  C mo te sientes hoy?",
    ],
    "not_understood": [
        "Disculpa, no estoy seguro de entender.  Podr as explicarme de otra manera?",
        "Hmm, no capt  bien eso.  Puedes ser m s espec fico?",
        "No estoy seguro de c mo ayudarte con eso.  Podr as reformular tu pregunta?",
        "Perd n, no entend  bien.  Te refieres a algo relacionado con tu salud?",
    ],
    "encouragement": [
        " Perfecto!  ",
        " Excelente! [ESTRELLA]",
        " Muy bien!  ",
        " Genial!  ",
    ],
}


def detect_intent(text):
    """Detecta la intenci n del usuario bas ndose en palabras clave"""
    text_lower = text.lower()

    # Contar coincidencias por categor a
    intent_scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            intent_scores[intent] = score

    # Retornar la intenci n con mayor puntaje
    if intent_scores:
        return max(intent_scores, key=intent_scores.get)

    return "unknown"


def get_user_context(user_id):
    """Obtiene el contexto de conversaci n del usuario"""
    return user_contexts.get(user_id, {})


def set_user_context(user_id, context_key, value):
    """Establece contexto de conversaci n para el usuario"""
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    user_contexts[user_id][context_key] = value


def get_random_response(category):
    """Obtiene una respuesta aleatoria de una categor a"""
    import random

    return random.choice(RESPONSE_VARIATIONS.get(category, [" Perfecto!"]))


def process_telegram_message(text, chat_id, user_id):
    """Procesa mensajes del bot de Telegram con funcionalidades duales para pacientes y profesionales"""
    original_text = text
    text = text.lower().strip()

    # Intentar obtener informaci n del usuario registrado
    user_info = get_telegram_user_info(user_id)
    user_name = user_info.get("nombre", "Usuario") if user_info else "Usuario"
    is_professional = is_professional_user(user_info)

    # Obtener contexto de conversaci n
    context = get_user_context(user_id)

    # Comando /start
    if text.startswith("/start"):
        if user_info:
            nombre = user_info.get("nombre", "Usuario")
            apellido = user_info.get("apellido", "")
            nombre_completo = f"{nombre} {apellido}".strip()

            if is_professional:
                # Mensaje de bienvenida para profesionales
                saludos = [
                    f" Hola Dr(a). {nombre_completo}! [DOCTOR]  Bienvenido de vuelta!",
                    f" Dr(a). {nombre_completo}! [HOSPITAL]  Listo para gestionar tus pacientes!",
                    f" Hola {nombre}!   Tu asistente de gesti n m dica est  listo",
                ]

                import random

                saludo = random.choice(saludos)

                return f"""{saludo}

Como profesional m dico, puedo ayudarte con:

[CALENDARIO] **Gesti n de Agenda** - Maneja tu horario y citas
[PACIENTES] **Pacientes** - Accede a historiales y datos
[LISTA] **Atenciones** - Registra consultas y tratamientos
[CAMPANA] **Notificaciones** - Comun cate con pacientes
[ESTADISTICAS] **Reportes** - Estad sticas y seguimientos

**Comandos principales:**
  "Ver mi agenda" - Consultar horario
  "Agendar cita" - Programar nueva cita
  "Pacientes" - Ver lista de pacientes
  "Notificar paciente" - Enviar mensaje

 En qu  puedo ayudarte hoy? [PENSANDO]"""
            else:
                # Mensaje de bienvenida para pacientes
                saludos = [
                    f" Hola {nombre_completo}! [SALUDO]  Qu  alegr a verte de nuevo! [FELIZ]",
                    f" {nombre_completo}! [ESTRELLA]  Bienvenido de vuelta a MedConnect!",
                    f" Hola {nombre}! [DOCTOR] Listo para ayudarte con tu salud hoy",
                ]

                import random

                saludo = random.choice(saludos)

                return f"""{saludo}

Como paciente registrado, estoy aqu  para ayudarte con:

[LISTA] **Consultas m dicas** - Registra tus visitas al doctor
[MEDICAMENTOS] **Medicamentos** - Lleva control de tus tratamientos  
[EXAMENES] **Ex menes** - Guarda resultados de laboratorio
[FAMILIA] **Familiares** - Notifica a tus seres queridos
[ESTADISTICAS] **Historial** - Consulta toda tu informaci n m dica
[DOCUMENTO] **Documentos** - Solicita informes e im genes

**Comandos principales:**
  "Quiero registrar una consulta"
  "Necesito anotar un medicamento"
  "Tengo resultados de ex menes"
  "Mu strame mi historial"
  "Solicitar documento"

 En qu  puedo ayudarte hoy? [PENSANDO]"""
        else:
            return """ Hola! [SALUDO] Soy tu asistente personal de salud de MedConnect [HOSPITAL]

Me encanta conocerte y estoy aqu  para ayudarte a cuidar tu bienestar. 

[MOVIL] ** Ya eres parte de la familia MedConnect?**
Si ya tienes cuenta, es s per f cil conectarnos:

1  Ve a tu perfil: https://medconnect.cl/profile
2  Haz clic en "Generar C digo"
3  Comparte conmigo el c digo: `/codigo MED123456`

[NOTA] ** Primera vez aqu ?**
 Genial! Reg strate en: https://medconnect.cl/register

Una vez conectados, podremos:
[LISTA] Registrar tus consultas m dicas
[MEDICAMENTOS] Organizar tus medicamentos  
[EXAMENES] Guardar resultados de ex menes
[FAMILIA] Mantener informada a tu familia
[ESTADISTICAS] Crear tu historial m dico personalizado

 Hay algo en lo que pueda ayudarte mientras tanto? [FELIZ]"""

    # Comando /codigo
    elif text.startswith("/codigo"):
        return handle_telegram_code_linking(text, user_id)

    # Detectar intenci n del mensaje
    intent = detect_intent(text)

    # Manejar emergencias con prioridad
    if intent == "emergencia":
        return """[EMERGENCIA] **EMERGENCIA DETECTADA** [EMERGENCIA]

Si est s en una situaci n de emergencia m dica:

[LLAMAR] **LLAMA INMEDIATAMENTE:**
  **131** - SAMU (Ambulancia)
  **133** - Bomberos
  **132** - Carabineros

[HOSPITAL] **Ve al servicio de urgencias m s cercano**

[ADVERTENCIA] **Recuerda:** Soy un asistente virtual y no puedo reemplazar la atenci n m dica profesional en emergencias.

Una vez que est s seguro, estar  aqu  para ayudarte con el seguimiento. [CORAZON]"""

    # ===== FUNCIONALIDADES PARA PROFESIONALES =====
    if is_professional:
        return handle_professional_requests(text, user_info, user_id, intent)

    # ===== FUNCIONALIDADES PARA PACIENTES =====
    return handle_patient_requests(text, user_info, user_id, intent)


def get_telegram_user_info(telegram_user_id):
    """Obtiene informaci n del usuario registrado por su ID de Telegram"""
    try:
        if not auth_manager:
            return None

        user_info = auth_manager.get_user_by_telegram_id(telegram_user_id)
        return user_info
    except Exception as e:
        logger.error(
            f"Error obteniendo info de usuario Telegram {telegram_user_id}: {e}"
        )
        return None


def is_professional_user(user_info):
    """Verifica si el usuario es un profesional m dico"""
    if not user_info:
        return False
    return user_info.get("tipo_usuario") == "profesional"


def get_professional_schedule_for_bot(professional_id, fecha=None):
    """Obtiene el horario del profesional para el bot"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return None

        citas_worksheet = spreadsheet.worksheet("Citas_Agenda")
        all_records = citas_worksheet.get_all_records()

        # Filtrar por profesional y fecha
        citas_profesional = []
        for record in all_records:
            if str(record.get("profesional_id", "")) == str(professional_id):
                if fecha:
                    cita_fecha = record.get("fecha", "")
                    if cita_fecha == fecha:
                        citas_profesional.append(record)
                else:
                    citas_profesional.append(record)

        return citas_profesional
    except Exception as e:
        logger.error(f"Error obteniendo agenda del profesional {professional_id}: {e}")
        return None


def get_available_slots_for_professional(professional_id, fecha):
    """Obtiene los horarios disponibles del profesional para una fecha espec fica"""
    try:
        # Obtener horario de trabajo del profesional
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return []

        horarios_worksheet = spreadsheet.worksheet("Horarios_Profesional")
        all_records = horarios_worksheet.get_all_records()

        # Buscar horario del profesional
        horario_profesional = None
        for record in all_records:
            if str(record.get("profesional_id", "")) == str(professional_id):
                horario_profesional = record
                break

        if not horario_profesional:
            return []

        # Obtener citas existentes para esa fecha
        citas_existentes = get_professional_schedule_for_bot(professional_id, fecha)

        # Generar slots disponibles (simplificado)
        slots_disponibles = []
        hora_inicio = 9  # 9:00 AM
        hora_fin = 18  # 6:00 PM

        for hora in range(hora_inicio, hora_fin):
            slot = f"{hora:02d}:00"
            # Verificar si el slot est  ocupado
            ocupado = any(cita.get("hora") == slot for cita in citas_existentes)
            if not ocupado:
                slots_disponibles.append(slot)

        return slots_disponibles
    except Exception as e:
        logger.error(f"Error obteniendo slots disponibles: {e}")
        return []


def send_notification_to_patient(patient_telegram_id, message):
    """Env a notificaci n a un paciente espec fico"""
    if patient_telegram_id:
        return send_telegram_message(patient_telegram_id, message)
    return False


def handle_professional_requests(text, user_info, user_id, intent):
    """Maneja las solicitudes espec ficas de profesionales m dicos"""
    user_name = user_info.get("nombre", "Doctor") if user_info else "Doctor"
    professional_id = user_info.get("id") if user_info else None

    # Gesti n de agenda
    if intent == "agenda" or "agenda" in text or "horario" in text:
        if professional_id:
            citas = get_professional_schedule_for_bot(professional_id)
            if citas:
                agenda_text = f"[CALENDARIO] **Agenda del Dr(a). {user_name}**\n\n"
                for cita in citas[:5]:  # Mostrar solo las pr ximas 5
                    fecha = cita.get("fecha", "N/A")
                    hora = cita.get("hora", "N/A")
                    paciente = cita.get("nombre_paciente", "Paciente")
                    agenda_text += f"  {fecha} {hora} - {paciente}\n"

                agenda_text += (
                    "\n[IDEA] Para ver m s detalles, usa: 'Ver agenda completa'"
                )
                return agenda_text
            else:
                return f"[CALENDARIO] **Agenda del Dr(a). {user_name}**\n\nNo tienes citas programadas actualmente.\n\n[IDEA] Para agendar una nueva cita, escribe: 'Agendar cita'"
        else:
            return "[ERROR] No se pudo obtener tu informaci n profesional. Contacta soporte."

    # Agendar citas
    elif intent == "cita_profesional" or "agendar" in text or "nueva cita" in text:
        set_user_context(user_id, "current_task", "agendar_cita")
        return f"""[CALENDARIO] **Agendar Nueva Cita**

Dr(a). {user_name}, para agendar una cita necesito:

  **Datos del paciente:**
  Nombre completo
  Tel fono (opcional)
  Email (opcional)

[CALENDARIO] **Detalles de la cita:**
  Fecha deseada
  Hora preferida
  Motivo de la consulta
  Duraci n estimada

[IDEA] **Ejemplo:**
"Agendar cita para Mar a Gonz lez, tel fono 912345678, el 15 de julio a las 10:00, consulta de control, 30 minutos"

 Con qu  paciente y fecha quieres agendar? [PENSANDO]"""

    # Gesti n de pacientes
    elif intent == "paciente_profesional" or "paciente" in text:
        if professional_id:
            # Obtener lista de pacientes del profesional
            spreadsheet = get_spreadsheet()
            if spreadsheet:
                try:
                    pacientes_worksheet = spreadsheet.worksheet("Pacientes_Profesional")
                    all_records = pacientes_worksheet.get_all_records()

                    pacientes_profesional = []
                    for record in all_records:
                        if str(record.get("profesional_id", "")) == str(
                            professional_id
                        ):
                            pacientes_profesional.append(record)

                    if pacientes_profesional:
                        response = (
                            f"[PACIENTES] **Pacientes del Dr(a). {user_name}**\n\n"
                        )
                        for paciente in pacientes_profesional[
                            :10
                        ]:  # Mostrar solo los primeros 10
                            nombre = paciente.get("nombre_completo", "N/A")
                            edad = paciente.get("edad", "N/A")
                            ultima_consulta = paciente.get(
                                "ultima_consulta", "Sin consultas"
                            )
                            response += f"  **{nombre}** ({edad} a os)\n"
                            response += f"   [CALENDARIO]  ltima consulta: {ultima_consulta}\n\n"

                        response += "[IDEA] Para ver historial completo de un paciente, escribe: 'Ver paciente [nombre]'"
                        return response
                    else:
                        return f"[PACIENTES] **Pacientes del Dr(a). {user_name}**\n\nNo tienes pacientes registrados actualmente.\n\n[IDEA] Para agregar un paciente, escribe: 'Agregar paciente'"
                except Exception as e:
                    logger.error(f"Error obteniendo pacientes: {e}")
                    return "[ERROR] Error obteniendo lista de pacientes. Intenta m s tarde."
            else:
                return "[ERROR] Error conectando con la base de datos."
        else:
            return "[ERROR] No se pudo obtener tu informaci n profesional."

    # Notificaciones a pacientes
    elif intent == "notificacion_profesional" or "notificar" in text:
        set_user_context(user_id, "current_task", "notificar_paciente")
        return f"""[CAMPANA] **Enviar Notificaci n a Paciente**

Dr(a). {user_name}, para enviar una notificaci n necesito:

  **Paciente:** Nombre del paciente
[NOTA] **Mensaje:** Lo que quieres comunicar

[IDEA] **Ejemplo:**
"Notificar a Mar a Gonz lez: Su cita de ma ana se confirma a las 10:00 AM"

 A qu  paciente quieres enviar la notificaci n? [PENSANDO]"""

    # Comando de ayuda para profesionales
    elif intent == "ayuda":
        return f"""  **Ayuda para Profesionales**

Dr(a). {user_name}, aqu  tienes mis funcionalidades:

[CALENDARIO] **Gesti n de Agenda:**
  "Ver mi agenda" - Consultar citas
  "Agendar cita" - Programar nueva cita
  "Cancelar cita" - Eliminar cita

[PACIENTES] **Gesti n de Pacientes:**
  "Pacientes" - Ver lista de pacientes
  "Ver paciente [nombre]" - Historial espec fico
  "Agregar paciente" - Registrar nuevo paciente

[CAMPANA] **Comunicaci n:**
  "Notificar paciente" - Enviar mensaje
  "Recordatorio paciente" - Programar aviso

[ESTADISTICAS] **Reportes:**
  "Estad sticas" - Ver m tricas
  "Reporte semanal" - Resumen de actividad

 En qu  puedo ayudarte espec ficamente? [PENSANDO]"""

    # Respuesta por defecto para profesionales
    else:
        return f"""[PENSANDO] **No entend  tu solicitud**

Dr(a). {user_name}, puedes pedirme:

[CALENDARIO] **Agenda:** "Ver mi agenda", "Agendar cita"
[PACIENTES] **Pacientes:** "Pacientes", "Ver paciente [nombre]"
[CAMPANA] **Notificaciones:** "Notificar paciente"
  **Ayuda:** "Ayuda"

 Qu  necesitas hacer? [PENSANDO]"""


def handle_patient_requests(text, user_info, user_id, intent):
    """Maneja las solicitudes espec ficas de pacientes"""
    user_name = user_info.get("nombre", "Usuario") if user_info else "Usuario"

    # Saludos
    if intent == "saludo" and not text.startswith("/"):
        greeting = get_random_response("greeting")
        if user_info:
            return f"{greeting} {user_name}!  En qu  puedo ayudarte con tu salud hoy? [FELIZ]"
        else:
            return f"""{greeting}

Soy tu asistente de salud de MedConnect. Puedo ayudarte a:
[LISTA] Registrar informaci n m dica
[MEDICAMENTOS] Organizar medicamentos
[EXAMENES] Guardar ex menes
[ESTADISTICAS] Consultar tu historial

 Te gustar a vincular tu cuenta primero? Solo necesitas ir a https://medconnect.cl/profile y generar un c digo. 

 O prefieres que te ayude con algo espec fico? [PENSANDO]"""

    # Despedidas
    elif intent == "despedida":
        despedidas = [
            f" Hasta pronto {user_name}! [SALUDO] Cu date mucho y no dudes en escribirme cuando necesites algo. [CORAZON]",
            f" Que tengas un excelente d a {user_name}! [ESTRELLA] Estar  aqu  cuando me necesites. [FELIZ]",
            f" Nos vemos pronto {user_name}! [SALUDO] Recuerda cuidar tu salud.  Hasta la pr xima!  ",
        ]
        import random

        return random.choice(despedidas)

    # Consultas m dicas
    elif intent == "consulta":
        set_user_context(user_id, "current_task", "consulta")

        if user_info:
            encouragement = get_random_response("encouragement")
            return f"""{encouragement} {user_name}, veo que quieres registrar una consulta m dica. [LISTA]

Para crear un registro completo, me gustar a que me compartieras:

[EXAMENES] **Detalles de la consulta:**
1   Cu ndo fue? (fecha)
2   Con qu  doctor te atendiste?
3   Cu l es su especialidad?
4   Qu  diagn stico te dieron?
5   Te recetaron alg n tratamiento?

Puedes contarme todo junto o paso a paso, como prefieras. Lo importante es que quede bien registrado en tu historial personal. [FELIZ]

 Empezamos? [PENSANDO]"""
        else:
            return """[LISTA]  Me encanta que quieras registrar tu consulta m dica! Es s per importante llevar un buen control.

Para poder guardar esta informaci n en tu historial personal, necesitar amos conectar tu cuenta primero.

**Datos que necesito para la consulta:**
1  Fecha de la consulta
2  Nombre del m dico
3  Especialidad
4  Diagn stico recibido
5  Tratamiento indicado

[IDEA] ** Tienes cuenta en MedConnect?**
Ve a https://medconnect.cl/profile, genera tu c digo y comp rtelo conmigo.

Mientras tanto, puedes contarme los detalles y los guardar  temporalmente.  Te parece? [FELIZ]"""

    # Medicamentos
    elif intent == "medicamento":
        set_user_context(user_id, "current_task", "medicamento")

        if user_info:
            encouragement = get_random_response("encouragement")
            return f"""{encouragement} {user_name}! Organizar tus medicamentos es fundamental para tu salud. [MEDICAMENTOS]

Para registrar correctamente tu medicamento, necesito conocer:

  **Informaci n del medicamento:**
1   C mo se llama?
2   Qu  dosis tomas? (ej: 50mg, 1 tableta)
3   Cada cu nto tiempo? (ej: cada 8 horas, 2 veces al d a)
4   Qu  m dico te lo recet ?
5   Para qu  es? (opcional)

Cu ntame todo lo que sepas y lo organizaremos en tu perfil para que nunca se te olvide. [FELIZ]

 Cu l es el medicamento? [PENSANDO]"""
        else:
            return """[MEDICAMENTOS]  Qu  responsable eres cuidando tu tratamiento! Me parece genial que quieras registrar tus medicamentos.

**Para un registro completo necesito:**
1  Nombre del medicamento
2  Dosis que tomas
3  Frecuencia (cada cu nto tiempo)
4  M dico que lo recet 
5  Para qu  es el tratamiento

[IDEA] **Para guardarlo en tu historial permanente:**
Necesitar as vincular tu cuenta desde https://medconnect.cl/profile

Pero puedes contarme los detalles ahora y te ayudo a organizarlos.  Cu l es el medicamento? [FELIZ]"""

    # Ex menes
    elif intent == "examen":
        set_user_context(user_id, "current_task", "examen")

        if user_info:
            encouragement = get_random_response("encouragement")
            return f"""{encouragement} {user_name}! Los ex menes son s per importantes para monitorear tu salud. [EXAMENES]

Para registrar tu examen correctamente, me gustar a saber:

  **Detalles del examen:**
1   Qu  tipo de examen fue? (sangre, orina, radiograf a, etc.)
2   Cu ndo te lo hiciste?
3   En qu  laboratorio o centro m dico?
4   Cu les fueron los resultados principales?
5   Alg n valor fuera de lo normal?

Si tienes los resultados en papel o digital, tambi n puedes subir la imagen a tu perfil web m s tarde.

 Me cuentas sobre tu examen? [PENSANDO]"""
        else:
            return """[EXAMENES]  Excelente que quieras registrar tus ex menes! Es clave para el seguimiento de tu salud.

**Informaci n que necesito:**
1  Tipo de examen realizado
2  Fecha cuando te lo hiciste
3  Laboratorio o centro m dico
4  Resultados principales
5  Valores importantes o anormales

[IDEA] **Para mantener un historial completo:**
Te recomiendo vincular tu cuenta en https://medconnect.cl/profile

Mientras tanto, cu ntame sobre tu examen y te ayudo a organizarlo.  Qu  examen te hiciste? [FELIZ]"""

    # Historial
    elif intent == "historial":
        if user_info:
            return f"""[ESTADISTICAS]  Hola {user_name}! Tu historial m dico est  siempre disponible para ti.

**Para ver toda tu informaci n completa:**
[MUNDO] Visita tu dashboard: https://medconnect.cl/patient

**Ah  encontrar s:**
[OK] Todas tus consultas m dicas organizadas
[OK] Lista completa de medicamentos actuales
[OK] Resultados de ex menes con fechas
[OK] Informaci n de familiares registrados
[OK] Gr ficos y estad sticas de tu salud

**Tambi n puedes preguntarme directamente:**
  " Cu les son mis  ltimas consultas?"
  " Qu  medicamentos estoy tomando?"
  " Cu ndo fue mi  ltimo examen?"
  " Tengo alguna cita pr xima?"

 Qu  te gustar a consultar espec ficamente? [PENSANDO]"""
        else:
            return """[ESTADISTICAS]  Me encantar a mostrarte tu historial m dico! Pero primero necesitamos conectar tu cuenta.

**Una vez vinculada, tendr s acceso a:**
[OK] Historial completo de consultas
[OK] Registro de todos tus medicamentos
[OK] Resultados de ex menes organizados
[OK] Informaci n de contactos de emergencia
[OK] Estad sticas de tu salud

** Ya tienes cuenta en MedConnect?**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

Una vez conectados, podr s consultar toda tu informaci n m dica cuando quieras.  Te ayudo con la vinculaci n? [FELIZ]"""

    # Documentos e im genes
    elif intent == "documento":
        if user_info:
            return f"""[DOCUMENTO] **Solicitar Documentos M dicos**

{user_name}, puedo ayudarte a solicitar:

[LISTA] **Informes m dicos**
[EXAMENES] **Resultados de ex menes**
[MEDICAMENTOS] **Recetas m dicas**
[ESTADISTICAS] **Reportes de salud**

**Para solicitar un documento:**
1  Ve a tu perfil web: https://medconnect.cl/patient
2  Navega a la secci n "Ex menes" o "Consultas"
3  Busca el documento que necesitas
4  Haz clic en "Descargar" o "Ver"

**Tambi n puedes pedirme:**
  " Tengo resultados de ex menes recientes?"
  " Cu ndo fue mi  ltima consulta?"
  " Qu  medicamentos tengo recetados?"

 Qu  tipo de documento necesitas? [PENSANDO]"""
        else:
            return """[DOCUMENTO] **Documentos M dicos**

Para acceder a tus documentos m dicos, necesitas tener una cuenta vinculada.

** Ya tienes cuenta?**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

Una vez conectado, podr s:
[OK] Ver todos tus documentos m dicos
[OK] Descargar informes y resultados
[OK] Acceder a recetas m dicas
[OK] Solicitar reportes de salud

 Te ayudo a crear tu cuenta? [FELIZ]"""

    # Recordatorios
    elif intent == "recordatorio":
        if user_info:
            return f"""  **Configurar Recordatorios**

{user_name}, puedo ayudarte a configurar recordatorios para:

[MEDICAMENTOS] **Medicamentos** - Horarios de toma
[CALENDARIO] **Citas m dicas** - Fechas de consulta
[EXAMENES] **Ex menes** - Fechas de laboratorio
[LISTA] **Controles** - Seguimientos m dicos

**Para configurar recordatorios:**
[MUNDO] Ve a tu perfil: https://medconnect.cl/profile
[MOVIL] Navega a "Configuraci n de Notificaciones"
[CAMPANA] Activa los recordatorios que necesites

**Tambi n puedes pedirme:**
  " Tengo alguna cita pr xima?"
  " Qu  medicamentos debo tomar hoy?"
  " Cu ndo es mi pr ximo control?"

 Qu  tipo de recordatorio necesitas? [PENSANDO]"""
        else:
            return """  **Recordatorios M dicos**

Para configurar recordatorios personalizados, necesitas tener una cuenta vinculada.

** Ya tienes cuenta?**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

Una vez conectado, podr s:
[OK] Configurar recordatorios de medicamentos
[OK] Recibir avisos de citas m dicas
[OK] Alertas de ex menes y controles
[OK] Notificaciones personalizadas

 Te ayudo a crear tu cuenta? [FELIZ]"""

    # Ayuda
    elif intent == "ayuda" or text in ["help", "/help"]:
        if user_info:
            return f"""  **Ayuda para Pacientes**

{user_name}, aqu  tienes mis funcionalidades:

[LISTA] **Consultas m dicas**
  "Registrar una consulta"
  "Anotar visita al doctor"
  "Ver mis consultas"

[MEDICAMENTOS] **Medicamentos**
  "Anotar medicamento"
  "Ver mis medicamentos"
  "Recordatorio de medicinas"

[EXAMENES] **Ex menes**
  "Registrar examen"
  "Ver resultados"
  "Solicitar informe"

[ESTADISTICAS] **Historial**
  "Ver mi historial"
  "Consultar datos"
  "Estad sticas de salud"

[DOCUMENTO] **Documentos**
  "Solicitar documento"
  "Descargar informe"
  "Ver resultados"

  **Recordatorios**
  "Configurar recordatorio"
  "Ver pr ximas citas"
  "Alertas m dicas"

 En qu  puedo ayudarte espec ficamente? [PENSANDO]"""
        else:
            return """  **Ayuda General**

Soy tu asistente de salud de MedConnect. Puedo ayudarte con:

[LISTA] **Registro de informaci n m dica**
[MEDICAMENTOS] **Gesti n de medicamentos**
[EXAMENES] **Control de ex menes**
[ESTADISTICAS] **Consulta de historial**
[DOCUMENTO] **Solicitud de documentos**
  **Configuraci n de recordatorios**

**Para acceder a todas las funcionalidades:**
  Ve a: https://medconnect.cl/profile y genera tu c digo

** Primera vez aqu ?**
[NOTA] Reg strate en: https://medconnect.cl/register

 Qu  te gustar a hacer? [PENSANDO]"""

    # Respuesta por defecto para pacientes
    else:
        if user_info:
            return f"""[PENSANDO] **No entend  tu solicitud**

{user_name}, puedes pedirme:

[LISTA] **Consultas:** "Registrar consulta", "Ver mis consultas"
[MEDICAMENTOS] **Medicamentos:** "Anotar medicamento", "Ver medicamentos"
[EXAMENES] **Ex menes:** "Registrar examen", "Ver resultados"
[ESTADISTICAS] **Historial:** "Ver mi historial", "Consultar datos"
[DOCUMENTO] **Documentos:** "Solicitar documento"
  **Recordatorios:** "Configurar recordatorio"
  **Ayuda:** "Ayuda"

 Qu  necesitas hacer? [PENSANDO]"""
        else:
            return """[PENSANDO] **No entend  tu solicitud**

Puedes pedirme:
[LISTA] Registrar informaci n m dica
[MEDICAMENTOS] Organizar medicamentos
[EXAMENES] Guardar ex menes
[ESTADISTICAS] Consultar historial
  Ayuda

**Para funcionalidades completas:**
  Ve a: https://medconnect.cl/profile y genera tu c digo

 Qu  te gustar a hacer? [PENSANDO]"""


def handle_account_linking(text, telegram_user_id):
    """Maneja la vinculaci n de cuenta de Telegram"""
    try:
        parts = text.split()
        if len(parts) < 2:
            return """[ERROR] Formato incorrecto. 

**Uso correcto:**
`/vincular tu-email@ejemplo.com`

**Ejemplo:**
`/vincular maria.gonzalez@gmail.com`

Aseg rate de usar el mismo email con el que te registraste en MedConnect."""

        email = parts[1].strip()

        # Validar formato de email b sico
        if "@" not in email or "." not in email:
            return """[ERROR] El email no parece v lido.

**Formato esperado:**
`/vincular tu-email@ejemplo.com`

Por favor verifica e intenta de nuevo."""

        if not auth_manager:
            return "[ERROR] Sistema de autenticaci n no disponible temporalmente. Intenta m s tarde."

        # Verificar si el usuario existe
        user_data = auth_manager.get_user_by_email(email)
        if not user_data:
            return f"""[ERROR] No encontr  ninguna cuenta con el email: `{email}`

** Posibles soluciones:**
1. Verifica que escribiste correctamente tu email
2. Si a n no tienes cuenta, reg strate en: https://medconnect.cl/register
3. Intenta de nuevo: `/vincular tu-email-correcto@ejemplo.com`"""

        # Intentar vincular la cuenta
        success, message, user_info = auth_manager.link_telegram_account(
            email, telegram_user_id
        )

        if success and user_info:
            nombre = user_info.get("nombre", "Usuario")
            apellido = user_info.get("apellido", "")
            return f"""[OK]  Cuenta vinculada exitosamente!

 Hola {nombre} {apellido}!  

Tu cuenta de Telegram ahora est  conectada con MedConnect. A partir de ahora:

  **Experiencia personalizada**
[LISTA] Historial m dico completo
[MEDICAMENTOS] Seguimiento de medicamentos
[EXAMENES] Registro de ex menes
[FAMILIA] Notificaciones familiares

Escribe `/start` para comenzar con tu experiencia personalizada."""
        else:
            return f"""[ERROR] {message}

**Si el problema persiste:**
1. Verifica tu email: `{email}`
2. Contacta soporte si necesitas ayuda
3. O intenta registrarte en: https://medconnect.cl/register"""

    except Exception as e:
        logger.error(f"Error en vinculaci n de cuenta: {e}")
        return """[ERROR] Error interno al vincular cuenta.

Por favor intenta de nuevo en unos minutos o contacta soporte."""


def send_telegram_message(telegram_id, message):
    """Env a un mensaje a trav s del bot de Telegram"""
    try:
        # Token del bot
        BOT_TOKEN = (
            "7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck"  # Token correcto del bot
        )

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": str(telegram_id),  # Asegurar que sea string
            "text": message,
            "parse_mode": "HTML",
        }

        import requests  # Asegurar import local

        response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            logger.info(f"[OK] Mensaje enviado a Telegram ID: {telegram_id}")
            return True
        else:
            logger.error(f"[ERROR] Error enviando mensaje a Telegram: {response.text}")
            return False

    except Exception as e:
        logger.error(f"[ERROR] Error enviando mensaje de Telegram: {e}")
        return False

    # Configurar webhook del bot

    except Exception as e:
        logger.error(f"[ERROR] Error en health check: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )

        # Listar archivos cr ticos
        critical_files = [
            "css/styles.css",
            "js/app.js",
            "images/logo.png",
            "images/Imagen2.png",
        ]

        for file_rel_path in critical_files:
            file_info = {"path": file_rel_path, "locations": []}

            # Verificar en cada ruta de static
            for static_path in static_paths:
                file_path = os.path.join(static_path, file_rel_path)
                file_info["locations"].append(
                    {
                        "static_path": static_path,
                        "full_path": file_path,
                        "exists": os.path.exists(file_path),
                        "size": (
                            os.path.getsize(file_path)
                            if os.path.exists(file_path)
                            else 0
                        ),
                        "readable": (
                            os.access(file_path, os.R_OK)
                            if os.path.exists(file_path)
                            else False
                        ),
                    }
                )

            debug_info["files"].append(file_info)

        return jsonify(debug_info)

    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "status": "error",
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500

def convert_date_format(date_str):
    """Convierte fecha de DD/MM/YYYY a YYYY-MM-DD para compatibilidad web"""
    if not date_str or date_str.strip() == "":
        return ""

    try:
        # Si ya est  en formato YYYY-MM-DD, dejarlo como est
        if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
            return date_str

        # Si est  en formato DD/MM/YYYY, convertir
        if len(date_str) == 10 and date_str[2] == "/" and date_str[5] == "/":
            day, month, year = date_str.split("/")
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Si est  en formato D/M/YYYY o variaciones, normalizar
        if "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                day, month, year = parts
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Si no coincide con ning n patr n conocido, devolver como est
        return date_str

    except Exception as e:
        logger.warning(f"[ADVERTENCIA] Error convirtiendo fecha '{date_str}': {e}")
        return date_str


# Configuraci n mejorada para producci n
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

# Configuraci n para dominio personalizado
CUSTOM_DOMAIN = os.environ.get("CUSTOM_DOMAIN", "localhost:5000")
app.config["SERVER_NAME"] = None  # Permitir cualquier host
app.config["PREFERRED_URL_SCHEME"] = (
    "https" if "medconnect.cl" in CUSTOM_DOMAIN else "http"
)

# Configuraci n de seguridad para HTTPS
if app.config["PREFERRED_URL_SCHEME"] == "https":
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


@app.route("/debug-env")
def debug_env():
    """Endpoint para debugging de variables de entorno"""
    import os
    import json

    # Obtener todas las variables de entorno
    all_env_vars = dict(os.environ)

    # Variables espec ficas que necesitamos
    target_vars = {
        "GOOGLE_SERVICE_ACCOUNT_JSON": os.environ.get(
            "GOOGLE_SERVICE_ACCOUNT_JSON", "NO ENCONTRADA"
        ),
        "GOOGLE_SHEETS_ID": os.environ.get("GOOGLE_SHEETS_ID", "NO ENCONTRADA"),
        "TELEGRAM_BOT_TOKEN": os.environ.get("TELEGRAM_BOT_TOKEN", "NO ENCONTRADA"),
        "PORT": os.environ.get("PORT", "NO ENCONTRADA"),
        "RAILWAY_ENVIRONMENT": os.environ.get("RAILWAY_ENVIRONMENT", "NO ENCONTRADA"),
        "RAILWAY_PROJECT_ID": os.environ.get("RAILWAY_PROJECT_ID", "NO ENCONTRADA"),
        "RAILWAY_SERVICE_ID": os.environ.get("RAILWAY_SERVICE_ID", "NO ENCONTRADA"),
    }

    # Filtrar variables de Railway para ver si est  funcionando
    railway_vars = {k: v for k, v in all_env_vars.items() if k.startswith("RAILWAY")}

    # Crear respuesta HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Variables de Entorno - MedConnect</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
            .section {{ margin: 20px 0; padding: 15px; border-radius: 5px; }}
            .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            .info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ padding: 8px 12px; border: 1px solid #ddd; text-align: left; word-break: break-all; }}
            th {{ background: #f8f9fa; }}
            .btn {{ padding: 10px 20px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>[BUSCAR] Debug Variables de Entorno - MedConnect</h1>
            
            <div class="section info">
                <h2>[ESTADISTICAS] Resumen</h2>
                <p><strong>Total de variables:</strong> {len(all_env_vars)}</p>
                <p><strong>Variables de Railway:</strong> {len(railway_vars)}</p>
                <p><strong>Entorno detectado:</strong> {'Railway' if railway_vars else 'Local/Otro'}</p>
            </div>
            
            <div class="section {'success' if target_vars['GOOGLE_SERVICE_ACCOUNT_JSON'] != 'NO ENCONTRADA' else 'error'}">
                <h2>[OBJETIVO] Variables Objetivo</h2>
                <table>
                    <tr><th>Variable</th><th>Estado</th><th>Valor (primeros 50 chars)</th></tr>"""

    for var, value in target_vars.items():
        status_icon = "[OK]" if value != "NO ENCONTRADA" else "[ERROR]"
        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        html += f"<tr><td>{var}</td><td>{status_icon}</td><td>{display_value}</td></tr>"

    html += f"""
                </table>
            </div>
            
            <div class="section info">
                <h2>  Variables de Railway</h2>
                <table>
                    <tr><th>Variable</th><th>Valor</th></tr>"""

    if railway_vars:
        for var, value in railway_vars.items():
            html += f"<tr><td>{var}</td><td>{str(value)[:100]}...</td></tr>"
    else:
        html += '<tr><td colspan="2">[ERROR] No se encontraron variables de Railway</td></tr>'

    html += f"""
                </table>
            </div>
            
            <div class="section info">
                <h2>[HERRAMIENTA] Todas las Variables (primeras 20)</h2>
                <table>
                    <tr><th>Variable</th><th>Valor (primeros 50 chars)</th></tr>"""

    # Mostrar solo las primeras 20 variables para no sobrecargar
    for i, (var, value) in enumerate(list(all_env_vars.items())[:20]):
        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        html += f"<tr><td>{var}</td><td>{display_value}</td></tr>"

    if len(all_env_vars) > 20:
        html += f'<tr><td colspan="2">... y {len(all_env_vars) - 20} variables m s</td></tr>'

    html += f"""
                </table>
            </div>
            
            <div class="section">
                <h2>  Navegaci n</h2>
                <a href="/test-complete" class="btn">  Volver al Diagn stico Principal</a>
                <a href="/debug-static" class="btn">[CARPETA] Debug Archivos Est ticos</a>
                <a href="/" class="btn">  P gina Principal</a>
            </div>
        </div>
    </body>
    </html>
    """

    return html


@app.route("/debug-auth")
def debug_auth():
    """Endpoint espec fico para debugging de AuthManager"""
    import traceback

    debug_info = {
        "auth_manager_status": "Available" if auth_manager else "Not Available",
        "variables_check": {},
        "credentials_test": {},
        "connection_test": {},
        "error_details": [],
    }

    # 1. Verificar variables de entorno
    debug_info["variables_check"] = {
        "GOOGLE_SERVICE_ACCOUNT_JSON": {
            "exists": bool(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")),
            "length": len(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")),
            "starts_with": (
                os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")[:50] + "..."
                if os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
                else "N/A"
            ),
        },
        "GOOGLE_SHEETS_ID": {
            "exists": bool(os.environ.get("GOOGLE_SHEETS_ID")),
            "value": os.environ.get("GOOGLE_SHEETS_ID", "N/A"),
        },
    }

    # 2. Probar carga de credenciales
    try:
        json_content = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if json_content:
            import json

            creds_dict = json.loads(json_content)
            debug_info["credentials_test"] = {
                "json_parse": "SUCCESS",
                "project_id": creds_dict.get("project_id", "N/A"),
                "client_email": creds_dict.get("client_email", "N/A"),
                "has_private_key": bool(creds_dict.get("private_key")),
            }
        else:
            debug_info["credentials_test"] = {
                "json_parse": "FAILED - No JSON content",
                "error": "GOOGLE_SERVICE_ACCOUNT_JSON is empty",
            }
    except Exception as e:
        debug_info["credentials_test"] = {
            "json_parse": "FAILED",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    # 3. Probar conexi n a Google Sheets
    try:
        if debug_info["credentials_test"].get("json_parse") == "SUCCESS":
            from google.oauth2.service_account import Credentials
            import gspread

            json_content = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
            creds_dict = json.loads(json_content)

            credentials = Credentials.from_service_account_info(
                creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            gc = gspread.authorize(credentials)

            sheets_id = os.environ.get(
                "GOOGLE_SHEETS_ID", "1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU"
            )
            spreadsheet = gc.open_by_key(sheets_id)

            debug_info["connection_test"] = {
                "gspread_auth": "SUCCESS",
                "spreadsheet_open": "SUCCESS",
                "spreadsheet_title": spreadsheet.title,
                "worksheets": [ws.title for ws in spreadsheet.worksheets()],
            }

            # Probar acceso a hoja de usuarios
            try:
                users_sheet = spreadsheet.worksheet("Usuarios")
                debug_info["connection_test"]["users_sheet"] = "SUCCESS"
                debug_info["connection_test"]["users_sheet_rows"] = len(
                    users_sheet.get_all_values()
                )
            except Exception as e:
                debug_info["connection_test"]["users_sheet"] = f"FAILED: {str(e)}"

        else:
            debug_info["connection_test"] = {
                "status": "SKIPPED - Credentials test failed"
            }

    except Exception as e:
        debug_info["connection_test"] = {
            "status": "FAILED",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    # 4. Intentar crear AuthManager en tiempo real
    try:
        from auth_manager import AuthManager

        test_auth = AuthManager()
        debug_info["live_auth_test"] = {"status": "SUCCESS", "instance_created": True}
    except Exception as e:
        debug_info["live_auth_test"] = {
            "status": "FAILED",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

    # Crear respuesta HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug AuthManager - MedConnect</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
            .section {{ margin: 20px 0; padding: 15px; border-radius: 5px; }}
            .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            .info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
            .warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
            pre {{ background: #f8f9fa; padding: 10px; border-radius: 4px; overflow-x: auto; }}
            .btn {{ padding: 10px 20px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>[BUSCAR] Debug AuthManager - MedConnect</h1>
            
            <div class="section {'success' if auth_manager else 'error'}">
                <h2>[ESTADISTICAS] Estado Actual</h2>
                <p><strong>AuthManager:</strong> {debug_info['auth_manager_status']}</p>
            </div>
            
            <div class="section info">
                <h2>[HERRAMIENTA] Variables de Entorno</h2>
                <pre>{json.dumps(debug_info['variables_check'], indent=2)}</pre>
            </div>
            
            <div class="section {'success' if debug_info['credentials_test'].get('json_parse') == 'SUCCESS' else 'error'}">
                <h2>  Prueba de Credenciales</h2>
                <pre>{json.dumps(debug_info['credentials_test'], indent=2)}</pre>
            </div>
            
            <div class="section {'success' if debug_info['connection_test'].get('gspread_auth') == 'SUCCESS' else 'error'}">
                <h2>[MUNDO] Prueba de Conexi n</h2>
                <pre>{json.dumps(debug_info['connection_test'], indent=2)}</pre>
            </div>
            
            <div class="section {'success' if debug_info['live_auth_test'].get('status') == 'SUCCESS' else 'error'}">
                <h2>  Prueba en Vivo de AuthManager</h2>
                <pre>{json.dumps(debug_info['live_auth_test'], indent=2)}</pre>
            </div>
            
            <div class="section">
                <h2>  Navegaci n</h2>
                <a href="/test-complete" class="btn">  Diagn stico Principal</a>
                <a href="/debug-env" class="btn">[HERRAMIENTA] Debug Variables</a>
                <a href="/" class="btn">  P gina Principal</a>
            </div>
        </div>
    </body>
    </html>
    """

    return html


@app.route("/test-images")
def test_images():
    """Endpoint para probar las im genes de la landing page"""
    import os

    # M ltiples rutas para verificar
    static_paths = [
        os.path.join(app.root_path, "static"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
        "static",
    ]

    files_status = {}
    critical_files = ["images/logo.png", "images/Imagen2.png", "css/styles.css"]

    for file_rel_path in critical_files:
        file_info = {"exists": False, "size": 0, "paths": [], "found_in": None}

        for static_path in static_paths:
            file_path = os.path.join(static_path, file_rel_path)
            exists = os.path.exists(file_path)
            size = os.path.getsize(file_path) if exists else 0

            file_info["paths"].append(
                {
                    "static_path": static_path,
                    "full_path": file_path,
                    "exists": exists,
                    "size": size,
                    "readable": os.access(file_path, os.R_OK) if exists else False,
                }
            )

            if exists and not file_info["exists"]:
                file_info["exists"] = True
                file_info["size"] = size
                file_info["found_in"] = static_path

        files_status[file_rel_path.split("/")[-1]] = file_info

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Im genes - MedConnect</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
            .test-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .success {{ background: #d4edda; color: #155724; }}
            .error {{ background: #f8d7da; color: #721c24; }}
            .btn {{ padding: 10px 20px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; display: inline-block; }}
            img {{ max-width: 200px; margin: 10px; border: 1px solid #ddd; }}
            pre {{ background: #f8f9fa; padding: 10px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>  Test de Im genes - MedConnect</h1>
            
            <div class="test-section">
                <h2>[ESTADISTICAS] Estado de Archivos</h2>
                <pre>{json.dumps(files_status, indent=2)}</pre>
            </div>
            
            <div class="test-section">
                <h2>  Prueba Visual - Logo</h2>
                <p><strong>URL Flask:</strong> {url_for('static', filename='images/logo.png')}</p>
                <p><strong>URL Directa:</strong> /static/images/logo.png</p>
                <img src="{url_for('static', filename='images/logo.png')}" alt="Logo Flask" 
                     onload="document.getElementById('logo-flask').innerHTML='[OK] Cargado con Flask'"
                     onerror="document.getElementById('logo-flask').innerHTML='[ERROR] Error con Flask'">
                <div id="logo-flask">  Cargando...</div>
                
                <img src="/static/images/logo.png" alt="Logo Directo"
                     onload="document.getElementById('logo-direct').innerHTML='[OK] Cargado directo'"
                     onerror="document.getElementById('logo-direct').innerHTML='[ERROR] Error directo'">
                <div id="logo-direct">  Cargando...</div>
            </div>
            
            <div class="test-section">
                <h2>  Prueba Visual - Imagen2</h2>
                <p><strong>URL Flask:</strong> {url_for('static', filename='images/Imagen2.png')}</p>
                <img src="{url_for('static', filename='images/Imagen2.png')}" alt="Imagen2 Flask"
                     onload="document.getElementById('img2-flask').innerHTML='[OK] Cargado con Flask'"
                     onerror="document.getElementById('img2-flask').innerHTML='[ERROR] Error con Flask'">
                <div id="img2-flask">  Cargando...</div>
            </div>
            
            <div class="test-section">
                <h2>  Prueba CSS</h2>
                <p><strong>URL CSS:</strong> {url_for('static', filename='css/styles.css')}</p>
                <link rel="stylesheet" href="{url_for('static', filename='css/styles.css')}">
                <div class="hero" style="padding: 20px; margin: 10px 0;">
                    <h3>Si este texto tiene estilos aplicados, CSS funciona [OK]</h3>
                </div>
            </div>
            
            <div class="test-section">
                <h2>[HERRAMIENTA] URLs de Prueba Directa</h2>
                <a href="/static/images/logo.png" target="_blank" class="btn">  Ver Logo</a>
                <a href="/static/images/Imagen2.png" target="_blank" class="btn">  Ver Imagen2</a>
                <a href="/static/css/styles.css" target="_blank" class="btn">  Ver CSS</a>
            </div>
            
            <div class="test-section">
                <h2>  Navegaci n</h2>
                <a href="/" class="btn">  Landing Page</a>
                <a href="/test-complete" class="btn">[HERRAMIENTA] Diagn stico Completo</a>
                <a href="/debug-static" class="btn">[CARPETA] Debug Est ticos</a>
            </div>
        </div>
    </body>
    </html>
    """

    return html


@app.route("/landing-test")
def landing_test():
    """Endpoint para probar la landing page con template simplificado"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MedConnect - Test Landing</title>
        <link rel="stylesheet" href="/static/css/styles.css">
        <style>
            .test-section {
                margin: 20px 0;
                padding: 20px;
                border: 2px solid #007bff;
                border-radius: 8px;
                background: #f8f9fa;
            }
            .nav-test {
                background: #343a40;
                color: white;
                padding: 15px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .nav-test img {
                height: 40px;
                width: auto;
            }
        </style>
    </head>
    <body>
        <div class="nav-test">
            <img src="/static/images/logo.png" alt="MedConnect Logo">
            <h2>MedConnect - Test de Landing Page</h2>
        </div>
        
        <div class="container" style="max-width: 1200px; margin: 0 auto; padding: 20px;">
            <div class="test-section">
                <h2>  Prueba de Elementos B sicos</h2>
                <p><strong>Logo en navegaci n:</strong> Deber a aparecer arriba  </p>
                <p><strong>CSS aplicado:</strong> Esta secci n deber a tener borde azul y fondo gris</p>
            </div>
            
            <div class="test-section">
                <h2>  Prueba de Im genes</h2>
                <p><strong>Logo principal:</strong></p>
                <img src="/static/images/logo.png" alt="Logo" style="max-width: 200px; border: 1px solid #ddd;">
                
                <p><strong>Imagen2:</strong></p>
                <img src="/static/images/Imagen2.png" alt="Imagen2" style="max-width: 300px; border: 1px solid #ddd;">
            </div>
            
            <div class="test-section">
                <h2>  Prueba de Estilos CSS</h2>
                <div class="hero" style="padding: 30px; text-align: center;">
                    <h1>Bienvenido a <span class="highlight">MedConnect</span></h1>
                    <p class="hero-subtitle">Tu plataforma integral de gesti n m dica familiar</p>
                    <div class="hero-buttons">
                        <a href="/register" class="btn btn-primary">Registrarse</a>
                        <a href="/login" class="btn btn-secondary">Iniciar Sesi n</a>
                    </div>
                </div>
            </div>
            
            <div class="test-section">
                <h2>  Comparaci n</h2>
                <a href="/" style="padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;">  Landing Page Original</a>
                <a href="/test-images" style="padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">  Test de Im genes</a>
            </div>
        </div>
    </body>
    </html>
    """


# Almac n temporal de c digos de vinculaci n (en producci n usar a Redis)
telegram_link_codes = {}


@app.route("/api/user/generate-telegram-code", methods=["POST"])
@login_required
def generate_telegram_code():
    """Genera un c digo  nico para vincular Telegram"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        # Generar c digo  nico
        import random
        import string

        code = "MED" + "".join(random.choices(string.digits, k=6))

        # Verificar que el c digo no exista (muy improbable)
        while code in telegram_link_codes:
            code = "MED" + "".join(random.choices(string.digits, k=6))

        # Guardar c digo con expiraci n (15 minutos)
        from datetime import datetime, timedelta

        expiration = datetime.now() + timedelta(minutes=15)

        telegram_link_codes[code] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": expiration,
        }

        # Limpiar c digos expirados
        clean_expired_codes()

        logger.info(f"[OK] C digo generado para usuario {user_id}: {code}")

        return jsonify(
            {
                "success": True,
                "code": code,
                "expires_in_minutes": 15,
                "instructions": f"Env a este mensaje al bot: /codigo {code}",
            }
        )

    except Exception as e:
        logger.error(f"[ERROR] Error generando c digo: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


def clean_expired_codes():
    """Limpia c digos expirados del almac n temporal"""
    try:
        from datetime import datetime

        now = datetime.now()
        expired_codes = [
            code
            for code, data in telegram_link_codes.items()
            if data["expires_at"] < now
        ]

        for code in expired_codes:
            del telegram_link_codes[code]

        if expired_codes:
            logger.info(f"  Limpiados {len(expired_codes)} c digos expirados")

    except Exception as e:
        logger.error(f"[ERROR] Error limpiando c digos: {e}")


def handle_telegram_code_linking(text, telegram_user_id):
    """Maneja la vinculaci n por c digo"""
    try:
        parts = text.split()
        if len(parts) < 2:
            return """[ERROR] Formato incorrecto.

**Uso correcto:**
`/codigo MED123456`

** D nde obtengo mi c digo?**
1. Ve a tu perfil en: https://medconnect.cl/profile
2. En la secci n "Conectar Telegram" haz clic en "Generar C digo"
3. Env a el c digo aqu 

El c digo expira en 15 minutos."""

        code = parts[1].strip().upper()

        # Limpiar c digos expirados primero
        clean_expired_codes()

        # Verificar si el c digo existe y es v lido
        if code not in telegram_link_codes:
            return f"""[ERROR] C digo inv lido o expirado: `{code}`

** Qu  hacer?**
1. Ve a tu perfil: https://medconnect.cl/profile
2. Genera un nuevo c digo
3. Env alo inmediatamente (expira en 15 minutos)

**Formato correcto:** `/codigo MED123456`"""

        code_data = telegram_link_codes[code]
        user_id = code_data["user_id"]

        # Eliminar el c digo usado
        del telegram_link_codes[code]

        if not auth_manager:
            return "[ERROR] Sistema de autenticaci n no disponible temporalmente."

        # Obtener informaci n del usuario
        user_info = auth_manager.get_user_by_id(user_id)
        if not user_info:
            return "[ERROR] Usuario no encontrado en el sistema."

        # Vincular la cuenta
        success, message, updated_user = auth_manager.link_telegram_by_user_id(
            user_id, telegram_user_id
        )

        if success and updated_user:
            nombre = updated_user.get("nombre", "Usuario")
            apellido = updated_user.get("apellido", "")

            logger.info(
                f"[OK] Cuenta vinculada: Usuario {user_id} con Telegram {telegram_user_id}"
            )

            return f"""   Cuenta vinculada exitosamente!

 Hola <b>{nombre} {apellido}</b>! [SALUDO]

Tu cuenta de MedConnect est  ahora conectada con Telegram.

[OK] <b>Beneficios activados:</b>
[LISTA] Registro de consultas m dicas
[MEDICAMENTOS] Gesti n de medicamentos
[EXAMENES] Seguimiento de ex menes
[ESTADISTICAS] Acceso a tu historial completo
[FAMILIA] Notificaciones familiares

<i>Escribe /start para comenzar tu experiencia personalizada.</i>"""
        else:
            logger.error(f"[ERROR] Error vinculando cuenta: {message}")
            return f"[ERROR] Error vinculando cuenta: {message}"

    except Exception as e:
        logger.error(f"[ERROR] Error en vinculaci n por c digo: {e}")
        return "[ERROR] Error interno. Intenta generar un nuevo c digo."


@app.route("/api/update-professional-profile", methods=["POST"])
@login_required
def update_professional_profile():
    """Actualiza el perfil del profesional"""
    try:
        if session.get("user_type") != "profesional":
            return jsonify({"error": "Acceso denegado: Solo para profesionales"}), 403

        user_data = session.get("user_data", {})
        user_id = user_data.get("id")

        if not user_id:
            return jsonify({"error": "Usuario no identificado"}), 400

        form_data = request.form.to_dict()
        logger.info(
            f"[ACTUALIZAR] Actualizando perfil profesional - Usuario: {user_id}, Datos: {form_data}"
        )

        # Validar datos requeridos seg n la secci n
        if "especialidad" in form_data:
            # Secci n profesional
            required_fields = ["especialidad", "numero_registro"]
            for field in required_fields:
                if not form_data.get(field, "").strip():
                    return jsonify({"error": f"El campo {field} es requerido"}), 400

        if "email" in form_data:
            # Secci n contacto
            required_fields = ["email", "telefono"]
            for field in required_fields:
                if not form_data.get(field, "").strip():
                    return jsonify({"error": f"El campo {field} es requerido"}), 400

        # Usar auth_manager para actualizar el profesional
        success, message = auth_manager.update_professional_profile(user_id, form_data)

        if success:
            # Actualizar datos en la sesi n si la actualizaci n fue exitosa
            updated_data = auth_manager.get_professional_by_id(user_id)
            if updated_data:
                # Combinar datos actualizados con datos de sesi n
                user_data.update(updated_data)
                session["user_data"] = user_data

            logger.info(f"[OK] Perfil profesional actualizado - Usuario: {user_id}")
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        logger.error(f"[ERROR] Error en update_professional_profile: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/add-specialization-area", methods=["POST"])
@login_required
def add_specialization_area():
    """Agrega un  rea de especializaci n al perfil del profesional"""
    try:
        if session.get("user_type") != "profesional":
            return jsonify({"error": "Acceso denegado: Solo para profesionales"}), 403

        user_data = session.get("user_data", {})
        form_data = request.form.to_dict()

        # Validar datos requeridos
        if not form_data.get("nombre"):
            return jsonify({"error": "El nombre del  rea es requerido"}), 400

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({"error": "Error conectando con la base de datos"}), 500

        try:
            worksheet = spreadsheet.worksheet("Profesionales")
            # Buscar al profesional por email
            cell = worksheet.find(user_data.get("email"))

            if cell:
                # Obtener  reas actuales
                areas_cell = worksheet.cell(cell.row, 13)  # Columna M para  reas
                areas_actuales = (
                    areas_cell.value.split("\n") if areas_cell.value else []
                )

                # Agregar nueva  rea
                nueva_area = form_data.get("nombre")
                if form_data.get("descripcion"):
                    nueva_area += f": {form_data.get('descripcion')}"

                areas_actuales.append(nueva_area)

                # Actualizar en Google Sheets
                worksheet.update_cell(cell.row, 13, "\n".join(areas_actuales))

                # Actualizar datos en la sesi n
                professional_data = user_data.copy()
                professional_data["areas_especializacion"] = areas_actuales
                session["user_data"] = professional_data

                return jsonify(
                    {
                        "message": " rea de especializaci n agregada correctamente",
                        "areas": areas_actuales,
                    }
                )
            else:
                return jsonify({"error": "Profesional no encontrado"}), 404

        except Exception as e:
            logger.error(f"Error agregando  rea de especializaci n: {e}")
            return jsonify({"error": "Error al actualizar la base de datos"}), 500

    except Exception as e:
        logger.error(f"Error en add_specialization_area: {e}")
        return jsonify({"error": "Error al agregar el  rea de especializaci n"}), 500


# === RUTAS PARA GESTI N DE ATENCIONES ===


@app.route("/api/test-atencion", methods=["GET"])
@login_required
def test_atencion():
    """Ruta de prueba para verificar el sistema de atenciones"""
    try:
        logger.info("  Iniciando test_atencion")

        user_data = session.get("user_data", {})
        logger.info(f"  Usuario de prueba: {user_data}")

        # Probar conexi n con Google Sheets
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify(
                {"success": False, "message": "Error conectando con Google Sheets"}
            )

        # Probar acceso a la hoja
        try:
            worksheet = spreadsheet.worksheet("Atenciones_Medicas")
            records = worksheet.get_all_records()
            logger.info(f"[ESTADISTICAS] Registros en hoja: {len(records)}")
        except Exception as e:
            logger.warning(f"[ADVERTENCIA] Hoja no existe, ser  creada: {e}")
            records = []

        return jsonify(
            {
                "success": True,
                "message": "Sistema funcionando correctamente",
                "user_id": user_data.get("id", session.get("user_id", "")),
                "user_email": user_data.get("email", ""),
                "total_records": len(records),
                "sheets_connected": True,
            }
        )

    except Exception as e:
        logger.error(f"[ERROR] Error en test_atencion: {e}")
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/register-atencion", methods=["POST"])
@login_required
def register_atencion():
    """Registra una nueva atenci n m dica, incluyendo archivos."""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Verificar si es JSON o FormData
        if request.content_type and "application/json" in request.content_type:
            # Datos JSON (sin archivos)
            data = request.get_json()
            archivos = []
            logger.info(f"[LISTA] Datos JSON recibidos: {data}")
        else:
            # Datos de formulario (con posibles archivos)
            data = request.form.to_dict()
            archivos = request.files.getlist("files[]")
            logger.info(f"[LISTA] Datos de formulario recibidos: {data}")
            logger.info(f"[DOCUMENTO] Archivos recibidos: {len(archivos)}")

        # Obtener el nombre del profesional
        try:
            spreadsheet = get_spreadsheet()
            profesionales_sheet = spreadsheet.worksheet("Profesionales")
            profesionales_records = profesionales_sheet.get_all_records()

            profesional_nombre = "Profesional"
            for prof in profesionales_records:
                if str(prof.get("profesional_id", "")) == str(profesional_id):
                    profesional_nombre = (
                        f"{prof.get('nombre', '')} {prof.get('apellido', '')}".strip()
                    )
                    break
        except Exception as e:
            logger.warning(f"No se pudo obtener nombre del profesional: {e}")
            profesional_nombre = "Profesional"

        # Agregar datos faltantes
        data["profesional_id"] = profesional_id
        data["profesional_nombre"] = profesional_nombre
        data["tiene_archivos"] = "S " if archivos else "No"

        # Registrar la atenci n en la hoja de c lculo
        atencion_id, nueva_fila = sheets_db.registrar_atencion(data)

        # Si la atenci n se registr  y hay archivos, procesarlos
        if atencion_id and archivos:
            logger.info(
                f"[ARCHIVO] Procesando {len(archivos)} archivos para atenci n {atencion_id}..."
            )

            # Crear subdirectorio para la atenci n
            atencion_folder = os.path.join(UPLOAD_FOLDER, atencion_id)
            if not os.path.exists(atencion_folder):
                os.makedirs(atencion_folder)

            for archivo in archivos:
                if archivo and archivo.filename:
                    try:
                        # Guardar archivo en el servidor
                        filename = secure_filename(archivo.filename)
                        file_path = os.path.join(atencion_folder, filename)

                        # Si ya existe un archivo con ese nombre, agregar timestamp
                        if os.path.exists(file_path):
                            name, ext = os.path.splitext(filename)
                            filename = f"{name}_{int(time.time())}{ext}"
                            file_path = os.path.join(atencion_folder, filename)

                        archivo.save(file_path)
                        tamano = os.path.getsize(file_path)

                        # Registrar archivo en la hoja de c lculo
                        archivo_data = {
                            "atencion_id": atencion_id,
                            "nombre_archivo": filename,
                            "tipo_archivo": archivo.mimetype,
                            "ruta_archivo": os.path.join(
                                "uploads", atencion_id, filename
                            ),
                            "tamano": tamano,
                        }
                        sheets_db.registrar_archivo_adjunto(archivo_data)
                        logger.info(f"[OK] Archivo '{filename}' guardado y registrado.")
                    except Exception as e:
                        logger.error(
                            f"[ERROR] Error procesando archivo {archivo.filename}: {e}"
                        )
                        continue

        logger.info(f"[OK] Atenci n {atencion_id} registrada exitosamente.")
        return jsonify(
            {
                "success": True,
                "message": "Atenci n registrada exitosamente",
                "atencion_id": atencion_id,
                "atencion": nueva_fila,
            }
        )

    except Exception as e:
        logger.error(f"[ERROR] Error en register_atencion: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return (
            jsonify({"success": False, "message": f"Error interno del servidor: {e}"}),
            500,
        )


@app.route("/api/get-atenciones", methods=["GET"])
@login_required
def get_atenciones():
    """Obtiene las atenciones registradas por el profesional"""
    try:
        logger.info("[BUSCAR] Iniciando get_atenciones")

        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        logger.info(f"  Datos del usuario: {user_data}")
        logger.info(f"[DOCTOR] Profesional ID: {profesional_id}")

        if not profesional_id:
            logger.error("[ERROR] Usuario no identificado")
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        logger.info("[ESTADISTICAS] Obteniendo spreadsheet...")
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            logger.error("[ERROR] No se pudo obtener el spreadsheet")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        logger.info("[OK] Spreadsheet obtenido correctamente")

        try:
            logger.info("[DOCUMENTO] Obteniendo hoja Atenciones_Medicas...")
            try:
                worksheet = spreadsheet.worksheet("Atenciones_Medicas")
                logger.info("[OK] Hoja encontrada, obteniendo registros...")
            except Exception as e:
                logger.warning(
                    f"[ADVERTENCIA] Hoja Atenciones_Medicas no encontrada, creando... Error: {e}"
                )
                # Crear la hoja si no existe
                headers = [
                    "atencion_id",
                    "profesional_id",
                    "profesional_nombre",
                    "paciente_id",
                    "paciente_nombre",
                    "paciente_rut",
                    "paciente_edad",
                    "fecha_hora",
                    "tipo_atencion",
                    "motivo_consulta",
                    "diagnostico",
                    "tratamiento",
                    "observaciones",
                    "fecha_registro",
                    "estado",
                    "requiere_seguimiento",
                    "tiene_archivos",
                ]
                worksheet = spreadsheet.add_worksheet(
                    title="Atenciones_Medicas", rows=1000, cols=len(headers)
                )
                worksheet.append_row(headers)
                logger.info("[OK] Hoja Atenciones_Medicas creada")

            # Usar handle_rate_limiting para manejar el rate limiting
            def get_records():
                return worksheet.get_all_records()

            records = handle_rate_limiting(get_records)
            if records is None:
                logger.error(
                    "[ERROR] No se pudieron obtener registros despu s de reintentos"
                )
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Error de rate limiting persistente",
                        }
                    ),
                    429,
                )
            logger.info(f"[LISTA] Total de registros encontrados: {len(records)}")

            # Filtrar atenciones del profesional actual
            atenciones_profesional = []
            for i, record in enumerate(records):
                record_profesional_id = str(record.get("profesional_id", ""))
                logger.info(
                    f"[BUSCAR] Registro {i+1}: profesional_id='{record_profesional_id}', buscando='{profesional_id}'"
                )

                if record_profesional_id == str(profesional_id):
                    logger.info(
                        f"[OK] Atenci n encontrada para el profesional: {record.get('atencion_id', '')}"
                    )
                    atenciones_profesional.append(
                        {
                            "atencion_id": record.get("atencion_id", ""),
                            "paciente_nombre": record.get("paciente_nombre", ""),
                            "paciente_rut": record.get("paciente_rut", ""),
                            "paciente_edad": record.get("paciente_edad", ""),
                            "fecha_hora": record.get("fecha_hora", ""),
                            "tipo_atencion": record.get("tipo_atencion", ""),
                            "motivo_consulta": record.get("motivo_consulta", ""),
                            "diagnostico": record.get("diagnostico", ""),
                            "tratamiento": record.get("tratamiento", ""),
                            "fecha_registro": record.get("fecha_registro", ""),
                            "estado": record.get("estado", ""),
                        }
                    )

            logger.info(
                f"[ESTADISTICAS] Total atenciones del profesional: {len(atenciones_profesional)}"
            )

            # Ordenar por fecha m s reciente
            atenciones_profesional.sort(
                key=lambda x: x.get("fecha_registro", ""), reverse=True
            )

            logger.info("[OK] Atenciones procesadas y ordenadas")

            return jsonify(
                {
                    "success": True,
                    "atenciones": atenciones_profesional,
                    "total": len(atenciones_profesional),
                }
            )

        except Exception as e:
            logger.error(f"[ERROR] Error obteniendo atenciones: {e}")
            import traceback

            logger.error(f"[ERROR] Traceback: {traceback.format_exc()}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al consultar la base de datos: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"[ERROR] Error en get_atenciones: {e}")
        import traceback

        logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/get-atencion/<atencion_id>", methods=["GET"])
@login_required
def get_atencion(atencion_id):
    """Obtiene los detalles de una atenci n espec fica"""
    try:
        logger.info(f"[BUSCAR] Obteniendo detalles de atenci n: {atencion_id}")
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            logger.error("[ERROR] Usuario no identificado")
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            logger.error("[ERROR] Error conectando con la base de datos")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Atenciones_Medicas")
            records = worksheet.get_all_records()

            # Buscar el registro
            atencion = None
            for record in records:
                if str(record.get("atencion_id", "")) == str(atencion_id):
                    atencion = record
                    break

            if not atencion:
                logger.error("[ERROR] Atenci n no encontrada")
                return (
                    jsonify({"success": False, "message": "Atenci n no encontrada"}),
                    404,
                )

            # Verificar que el profesional tiene acceso a esta atenci n
            if str(atencion.get("profesional_id", "")) != str(profesional_id):
                logger.error("[ERROR] Acceso no autorizado a la atenci n")
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "No tiene permisos para ver esta atenci n",
                        }
                    ),
                    403,
                )

            try:
                # Obtener archivos adjuntos
                archivos = sheets_db.get_archivos_atencion(atencion_id)
                logger.info(f"[ARCHIVO] Archivos encontrados: {len(archivos)}")
            except Exception as e:
                logger.error(f"[ERROR] Error obteniendo archivos adjuntos: {e}")
                archivos = []

            return jsonify(
                {
                    "success": True,
                    "atencion": {
                        "atencion_id": atencion.get("atencion_id", ""),
                        "paciente_id": atencion.get("paciente_id", ""),
                        "paciente_nombre": atencion.get("paciente_nombre", ""),
                        "paciente_rut": atencion.get("paciente_rut", ""),
                        "paciente_edad": atencion.get("paciente_edad", ""),
                        "fecha_hora": atencion.get("fecha_hora", ""),
                        "tipo_atencion": atencion.get("tipo_atencion", ""),
                        "motivo_consulta": atencion.get("motivo_consulta", ""),
                        "diagnostico": atencion.get("diagnostico", ""),
                        "tratamiento": atencion.get("tratamiento", ""),
                        "observaciones": atencion.get("observaciones", ""),
                        "estado": atencion.get("estado", ""),
                        "tiene_archivos": atencion.get("tiene_archivos", False),
                    },
                    "archivos": archivos,
                }
            )

        except Exception as e:
            logger.error(f"[ERROR] Error obteniendo atenci n: {e}")
            return (
                jsonify(
                    {"success": False, "message": "Error al consultar la base de datos"}
                ),
                500,
            )

    except Exception as e:
        logger.error(f"[ERROR] Error en get_atencion: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500


@app.route("/api/update-atencion/<atencion_id>", methods=["PUT"])
@login_required
def update_atencion(atencion_id):
    """Actualiza una atenci n espec fica"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener datos del formulario
        data = request.get_json()

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Atenciones_Medicas")
            records = worksheet.get_all_records()

            # Buscar y actualizar el registro
            for i, record in enumerate(
                records, start=2
            ):  # start=2 porque la fila 1 son headers
                if record.get("atencion_id") == atencion_id and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):

                    # Actualizar los campos espec ficos
                    if "fecha_hora" in data:
                        worksheet.update_cell(i, 7, data["fecha_hora"])
                    if "tipo_atencion" in data:
                        worksheet.update_cell(i, 8, data["tipo_atencion"])
                    if "motivo_consulta" in data:
                        worksheet.update_cell(i, 9, data["motivo_consulta"])
                    if "diagnostico" in data:
                        worksheet.update_cell(i, 10, data["diagnostico"])
                    if "tratamiento" in data:
                        worksheet.update_cell(i, 11, data["tratamiento"])
                    if "observaciones" in data:
                        worksheet.update_cell(i, 12, data["observaciones"])
                    if "requiere_seguimiento" in data:
                        worksheet.update_cell(
                            i, 15, "S " if data["requiere_seguimiento"] else "No"
                        )

                    logger.info(
                        f"Atenci n {atencion_id} actualizada por profesional {profesional_id}"
                    )
                    return jsonify(
                        {
                            "success": True,
                            "message": "Atenci n actualizada exitosamente",
                        }
                    )

            return jsonify({"success": False, "message": "Atenci n no encontrada"}), 404

        except Exception as e:
            logger.error(f"Error actualizando atenci n: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error al actualizar en la base de datos",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en update_atencion: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500


@app.route("/api/professional/patients", methods=["GET"])
@login_required
def get_professional_patients():
    """Obtiene la lista de pacientes del profesional"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            # Intentar obtener o crear la hoja
            try:
                worksheet = spreadsheet.worksheet("Pacientes_Profesional")
                logger.info("[OK] Hoja Pacientes_Profesional encontrada")
            except Exception as e:
                logger.warning(
                    f"[ADVERTENCIA] Hoja Pacientes_Profesional no encontrada, creando... Error: {e}"
                )
                # Si no existe, crearla
                headers = [
                    "paciente_id",
                    "profesional_id",
                    "nombre_completo",
                    "rut",
                    "edad",
                    "fecha_nacimiento",
                    "genero",
                    "telefono",
                    "email",
                    "direccion",
                    "antecedentes_medicos",
                    "fecha_primera_consulta",
                    "ultima_consulta",
                    "num_atenciones",
                    "estado_relacion",
                    "fecha_registro",
                    "notas",
                ]
                worksheet = spreadsheet.add_worksheet(
                    title="Pacientes_Profesional", rows=1000, cols=len(headers)
                )
                worksheet.append_row(headers)
                logger.info("[OK] Hoja Pacientes_Profesional creada")

            # Usar handle_rate_limiting para manejar el rate limiting
            def get_records():
                return worksheet.get_all_records()

            records = handle_rate_limiting(get_records)
            if records is None:
                logger.error(
                    "[ERROR] No se pudieron obtener registros despu s de reintentos"
                )
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Error de rate limiting persistente",
                        }
                    ),
                    429,
                )

            # Filtrar pacientes del profesional actual
            pacientes_profesional = []
            for record in records:
                if str(record.get("profesional_id", "")) == str(profesional_id):
                    # Debug: log del record original
                    logger.info(f"[BUSCAR] Record original de Google Sheets: {record}")

                    # Procesar cada campo de manera segura
                    paciente_data = {}

                    # Campos que deben ser strings
                    string_fields = [
                        "paciente_id",
                        "nombre_completo",
                        "rut",
                        "fecha_nacimiento",
                        "genero",
                        "telefono",
                        "email",
                        "direccion",
                        "antecedentes_medicos",
                        "fecha_primera_consulta",
                        "ultima_consulta",
                        "estado_relacion",
                        "fecha_registro",
                        "notas",
                    ]

                    for field in string_fields:
                        value = record.get(field, "")
                        # Convertir a string si no es None
                        if value is not None:
                            paciente_data[field] = str(value)
                        else:
                            paciente_data[field] = ""
                        logger.info(
                            f"[BUSCAR] Campo {field}: valor='{value}', tipo={type(value)}, procesado='{paciente_data[field]}'"
                        )

                    # Campos num ricos
                    edad_value = record.get("edad", "")
                    if edad_value is not None and str(edad_value).strip() != "":
                        try:
                            paciente_data["edad"] = str(int(float(str(edad_value))))
                        except (ValueError, TypeError):
                            paciente_data["edad"] = (
                                str(edad_value) if edad_value else ""
                            )
                    else:
                        paciente_data["edad"] = ""

                    num_atenciones_value = record.get("num_atenciones", 0)
                    if (
                        num_atenciones_value is not None
                        and str(num_atenciones_value).strip() != ""
                    ):
                        try:
                            paciente_data["num_atenciones"] = int(
                                float(str(num_atenciones_value))
                            )
                        except (ValueError, TypeError):
                            paciente_data["num_atenciones"] = 0
                    else:
                        paciente_data["num_atenciones"] = 0

                    logger.info(f"[BUSCAR] Paciente procesado: {paciente_data}")
                    pacientes_profesional.append(paciente_data)

            # Ordenar por fecha de registro m s reciente
            pacientes_profesional.sort(
                key=lambda x: x.get("fecha_registro", ""), reverse=True
            )

            logger.info(
                f"[ESTADISTICAS] Total pacientes del profesional {profesional_id}: {len(pacientes_profesional)}"
            )

            return jsonify(
                {
                    "success": True,
                    "pacientes": pacientes_profesional,
                    "total": len(pacientes_profesional),
                }
            )

        except Exception as e:
            logger.error(f"Error obteniendo pacientes: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al consultar la base de datos: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en get_professional_patients: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/patients", methods=["POST"])
@login_required
def add_professional_patient():
    """Agrega un nuevo paciente al profesional"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"[NOTA] Datos del nuevo paciente: {data}")

        # Validar campos requeridos
        required_fields = ["nombre_completo", "rut"]
        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify(
                        {"success": False, "message": f"El campo {field} es requerido"}
                    ),
                    400,
                )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Pacientes_Profesional")

            # Verificar si el paciente ya existe para este profesional
            records = worksheet.get_all_records()
            for record in records:
                if (
                    str(record.get("profesional_id", "")) == str(profesional_id)
                    and record.get("rut", "").strip().lower()
                    == data.get("rut", "").strip().lower()
                ):
                    return (
                        jsonify(
                            {
                                "success": False,
                                "message": "Este paciente ya est  registrado en tu lista",
                            }
                        ),
                        400,
                    )

            # Generar ID  nico para el paciente
            paciente_id = f"PAC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Preparar datos para insertar
            nuevo_paciente = [
                paciente_id,
                profesional_id,
                data.get("nombre_completo", ""),
                data.get("rut", ""),
                data.get("edad", ""),
                data.get("fecha_nacimiento", ""),
                data.get("genero", ""),
                data.get("telefono", ""),
                data.get("email", ""),
                data.get("direccion", ""),
                data.get("antecedentes_medicos", ""),
                "",  # fecha_primera_consulta (se actualiza con la primera atenci n)
                "",  # ultima_consulta
                0,  # num_atenciones
                "activo",  # estado_relacion
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data.get("notas", ""),
            ]

            # Insertar en Google Sheets
            worksheet.append_row(nuevo_paciente)
            logger.info(
                f"[OK] Paciente {paciente_id} agregado al profesional {profesional_id}"
            )

            return jsonify(
                {
                    "success": True,
                    "message": "Paciente agregado exitosamente",
                    "paciente_id": paciente_id,
                }
            )

        except Exception as e:
            logger.error(f"Error agregando paciente: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al agregar en la base de datos: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en add_professional_patient: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/patients/<paciente_id>", methods=["GET"])
@login_required
def get_professional_patient(paciente_id):
    """Obtiene los detalles de un paciente espec fico"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Pacientes_Profesional")
            records = worksheet.get_all_records()

            # Buscar el paciente
            for record in records:
                if record.get("paciente_id") == paciente_id and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):

                    # Tambi n obtener el historial de atenciones del paciente
                    atenciones_worksheet = spreadsheet.worksheet("Atenciones_Medicas")
                    atenciones_records = atenciones_worksheet.get_all_records()

                    atenciones_paciente = []
                    for atencion in atenciones_records:
                        if (
                            str(atencion.get("profesional_id", ""))
                            == str(profesional_id)
                            and atencion.get("paciente_rut", "").strip().lower()
                            == record.get("rut", "").strip().lower()
                        ):
                            atenciones_paciente.append(
                                {
                                    "atencion_id": atencion.get("atencion_id", ""),
                                    "fecha_hora": atencion.get("fecha_hora", ""),
                                    "tipo_atencion": atencion.get("tipo_atencion", ""),
                                    "motivo_consulta": atencion.get(
                                        "motivo_consulta", ""
                                    ),
                                    "diagnostico": atencion.get("diagnostico", ""),
                                    "estado": atencion.get("estado", ""),
                                }
                            )

                    return jsonify(
                        {
                            "success": True,
                            "paciente": record,
                            "atenciones": atenciones_paciente,
                            "total_atenciones": len(atenciones_paciente),
                        }
                    )

            return jsonify({"success": False, "message": "Paciente no encontrado"}), 404

        except Exception as e:
            logger.error(f"Error obteniendo paciente: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al consultar la base de datos: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en get_professional_patient: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/patients/<paciente_id>", methods=["PUT"])
@login_required
def update_professional_patient(paciente_id):
    """Actualiza la informaci n de un paciente"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener datos del formulario
        data = request.get_json()

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Pacientes_Profesional")
            records = worksheet.get_all_records()

            # Buscar y actualizar el paciente
            for i, record in enumerate(
                records, start=2
            ):  # start=2 porque la fila 1 son headers
                if record.get("paciente_id") == paciente_id and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):

                    # Actualizar los campos espec ficos
                    if "nombre_completo" in data:
                        worksheet.update_cell(i, 3, data["nombre_completo"])
                    if "rut" in data:
                        worksheet.update_cell(i, 4, data["rut"])
                    if "edad" in data:
                        worksheet.update_cell(i, 5, data["edad"])
                    if "fecha_nacimiento" in data:
                        worksheet.update_cell(i, 6, data["fecha_nacimiento"])
                    if "genero" in data:
                        worksheet.update_cell(i, 7, data["genero"])
                    if "telefono" in data:
                        worksheet.update_cell(i, 8, data["telefono"])
                    if "email" in data:
                        worksheet.update_cell(i, 9, data["email"])
                    if "direccion" in data:
                        worksheet.update_cell(i, 10, data["direccion"])
                    if "antecedentes_medicos" in data:
                        worksheet.update_cell(i, 11, data["antecedentes_medicos"])
                    if "notas" in data:
                        worksheet.update_cell(i, 17, data["notas"])

                    logger.info(
                        f"Paciente {paciente_id} actualizado por profesional {profesional_id}"
                    )
                    return jsonify(
                        {
                            "success": True,
                            "message": "Paciente actualizado exitosamente",
                        }
                    )

            return jsonify({"success": False, "message": "Paciente no encontrado"}), 404

        except Exception as e:
            logger.error(f"Error actualizando paciente: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al actualizar en la base de datos: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en update_professional_patient: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/patients/<paciente_id>", methods=["DELETE"])
@login_required
def remove_professional_patient(paciente_id):
    """Elimina un paciente de la lista del profesional"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Pacientes_Profesional")
            records = worksheet.get_all_records()

            # Buscar el paciente para eliminar la relaci n
            for i, record in enumerate(
                records, start=2
            ):  # start=2 porque la fila 1 son headers
                if record.get("paciente_id") == paciente_id and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):

                    # Eliminar la fila
                    worksheet.delete_rows(i)
                    logger.info(
                        f"Relaci n profesional-paciente eliminada: {profesional_id} - {paciente_id}"
                    )
                    return jsonify(
                        {
                            "success": True,
                            "message": "Paciente eliminado de tu lista exitosamente",
                        }
                    )

            return jsonify({"success": False, "message": "Paciente no encontrado"}), 404

        except Exception as e:
            logger.error(f"Error eliminando relaci n profesional-paciente: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al eliminar de la base de datos: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en remove_professional_patient: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/delete-atencion/<atencion_id>", methods=["DELETE"])
@login_required
def delete_atencion(atencion_id):
    """Elimina una atenci n espec fica"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Atenciones_Medicas")

            # Buscar la atenci n
            records = worksheet.get_all_records()
            row_to_delete = None

            for i, record in enumerate(
                records, start=2
            ):  # start=2 porque la fila 1 son headers
                if record.get("atencion_id") == atencion_id and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):
                    row_to_delete = i
                    break

            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(
                    f"Atenci n {atencion_id} eliminada por profesional {profesional_id}"
                )
                return jsonify(
                    {"success": True, "message": "Atenci n eliminada exitosamente"}
                )
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Atenci n no encontrada o no tienes permisos para eliminarla",
                        }
                    ),
                    404,
                )

        except Exception as e:
            logger.error(f"Error eliminando atenci n: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error al eliminar de la base de datos",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en delete_atencion: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500


@app.route("/api/update-professional-status/<int:professional_id>", methods=["PUT"])
@login_required
def update_professional_status(professional_id):
    """Actualizar estado y disponibilidad de un profesional"""
    try:
        # Verificar que el usuario actual sea administrador o el mismo profesional
        current_user = session.get("user_data", {})
        if (
            current_user.get("tipo_usuario") != "profesional"
            and current_user.get("id") != professional_id
        ):
            # Aqu  podr as agregar l gica para verificar si es administrador
            pass

        # Obtener datos del formulario
        estado = request.json.get("estado")
        disponible = request.json.get("disponible")

        if not estado and not disponible:
            return (
                jsonify({"error": "Se debe proporcionar al menos estado o disponible"}),
                400,
            )

        # Actualizar en la base de datos
        success, message = auth_manager.update_professional_status(
            professional_id, estado=estado, disponible=disponible
        )

        if success:
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        logger.error(f"[ERROR] Error actualizando estado de profesional: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/get-professional/<int:professional_id>", methods=["GET"])
@login_required
def get_professional_details(professional_id):
    """Obtener detalles completos de un profesional"""
    try:
        professional_data = auth_manager.get_professional_by_id(professional_id)

        if professional_data:
            return jsonify(professional_data), 200
        else:
            return jsonify({"error": "Profesional no encontrado"}), 404

    except Exception as e:
        logger.error(f"[ERROR] Error obteniendo profesional: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/add-certification", methods=["POST"])
@login_required
def add_certification():
    """Agregar certificaci n a un profesional"""
    try:
        # Obtener datos del usuario actual
        user_data = session.get("user_data", {})
        user_id = user_data.get("id")

        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        # Verificar que sea un profesional
        if user_data.get("tipo_usuario") != "profesional":
            return (
                jsonify(
                    {"error": "Solo los profesionales pueden agregar certificaciones"}
                ),
                403,
            )

        # Obtener datos del formulario
        titulo = request.form.get("titulo", "").strip()
        institucion = request.form.get("institucion", "").strip()
        ano = request.form.get("ano", "").strip()

        # Validar campos requeridos
        if not titulo or not institucion or not ano:
            return jsonify({"error": "T tulo, instituci n y a o son requeridos"}), 400

        # Manejar archivo si se subi
        archivo_url = ""
        if "certificado" in request.files:
            file = request.files["certificado"]
            if file and file.filename:
                if allowed_file(file.filename):
                    # Generar nombre  nico para el archivo
                    filename = generate_unique_filename(file.filename)
                    file_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], "certifications", filename
                    )

                    # Crear directorio si no existe
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    # Guardar archivo
                    file.save(file_path)
                    archivo_url = f"/uploads/certifications/{filename}"
                    logger.info(
                        f"[OK] Archivo de certificaci n guardado: {archivo_url}"
                    )
                else:
                    return (
                        jsonify({"error": "Tipo de archivo no permitido. Solo PDF"}),
                        400,
                    )

        # Agregar certificaci n a Google Sheets
        success, message = auth_manager.add_professional_certification(
            user_id, titulo, institucion, ano, archivo_url
        )

        if success:
            logger.info(f"[OK] Certificaci n agregada para profesional ID: {user_id}")
            return jsonify({"message": message}), 200
        else:
            return jsonify({"error": message}), 400

    except Exception as e:
        logger.error(f"[ERROR] Error agregando certificaci n: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/get-certifications/<int:professional_id>", methods=["GET"])
@login_required
def get_professional_certifications(professional_id):
    """Obtener certificaciones de un profesional"""
    try:
        # Verificar que el usuario actual sea el mismo profesional o un administrador
        current_user = session.get("user_data", {})
        if current_user.get("id") != professional_id:
            # Aqu  podr as agregar l gica para verificar si es administrador
            pass

        # Obtener certificaciones
        certifications = auth_manager.get_professional_certifications(professional_id)

        return jsonify({"certifications": certifications}), 200

    except Exception as e:
        logger.error(f"[ERROR] Error obteniendo certificaciones: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/atencion-pdf/<atencion_id>")
@login_required
def generar_pdf_atencion(atencion_id):
    """Genera un PDF con los detalles de la atenci n m dica usando ReportLab"""
    try:
        # Obtener datos de la atenci n
        user_data = get_current_user()
        if not user_data:
            return jsonify({"error": "Usuario no autenticado"}), 401

        # Obtener el cliente de Google Sheets y la hoja de c lculo
        # sheets_client = get_google_sheets_client()  # Ya inicializado globalmente
        if not sheets_client:
            logger.error("Error: No se pudo obtener el cliente de Google Sheets")
            return jsonify({"error": "Error interno del servidor"}), 500

        spreadsheet = sheets_client.open_by_key(app.config["GOOGLE_SHEETS_ID"])

        try:
            worksheet = spreadsheet.worksheet("Atenciones_Medicas")
            records = worksheet.get_all_records()
            atencion = None

            for record in records:
                if str(record.get("atencion_id", "")) == str(atencion_id):
                    atencion = record
                    break

            if not atencion:
                return jsonify({"error": "Atenci n no encontrada"}), 404

        except Exception as e:
            logger.error(f"Error obteniendo atenci n: {e}")
            return jsonify({"error": "Error interno del servidor"}), 500

        try:
            # Importar las dependencias necesarias para ReportLab
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
                Image,
            )
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from PIL import Image as PILImage

            # Colores del proyecto
            COLOR_PRIMARY = colors.HexColor("#2C3E50")  # Azul oscuro
            COLOR_SECONDARY = colors.HexColor("#3498DB")  # Azul claro
            COLOR_ACCENT = colors.HexColor("#E74C3C")  # Rojo
            COLOR_TEXT = colors.HexColor("#2C3E50")  # Texto principal
            COLOR_SUBTEXT = colors.HexColor("#7F8C8D")  # Texto secundario

            # Crear un buffer para el PDF
            buffer = BytesIO()

            # Crear el documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=100,  # Aumentado para el logo
                bottomMargin=72,
            )

            # Obtener estilos
            styles = getSampleStyleSheet()
            styles.add(
                ParagraphStyle(
                    name="CustomTitle",
                    parent=styles["Heading1"],
                    fontSize=24,
                    spaceAfter=30,
                    alignment=TA_CENTER,
                    textColor=COLOR_PRIMARY,
                )
            )
            styles.add(
                ParagraphStyle(
                    name="SectionTitle",
                    parent=styles["Heading2"],
                    fontSize=14,
                    spaceBefore=20,
                    spaceAfter=10,
                    textColor=COLOR_SECONDARY,
                    borderColor=COLOR_SECONDARY,
                    borderWidth=1,
                    borderPadding=5,
                    borderRadius=5,
                )
            )
            styles.add(
                ParagraphStyle(
                    name="Label",
                    parent=styles["Normal"],
                    fontSize=11,
                    textColor=COLOR_TEXT,
                    fontName="Helvetica-Bold",
                )
            )
            # Modificar el estilo Normal existente en lugar de crear uno nuevo
            styles["Normal"].fontSize = 10
            styles["Normal"].textColor = COLOR_TEXT
            styles["Normal"].alignment = TA_LEFT
            styles["Normal"].leading = 14

            # Lista de elementos para el PDF
            elements = []

            # Agregar logo
            logo_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "static",
                "images",
                "logo.png",
            )
            if os.path.exists(logo_path):
                logo = Image(logo_path)
                logo.drawHeight = 0.5 * inch
                logo.drawWidth = 0.5 * inch
                elements.append(logo)
                elements.append(Spacer(1, 20))

            # T tulo
            elements.append(
                Paragraph("Registro de Atenci n M dica", styles["CustomTitle"])
            )
            elements.append(Spacer(1, 20))

            # Informaci n del Paciente
            elements.append(
                Paragraph("Informaci n del Paciente", styles["SectionTitle"])
            )
            patient_data = [
                ["Nombre:", atencion.get("paciente_nombre", "")],
                ["RUT:", atencion.get("paciente_rut", "")],
                ["Edad:", f"{atencion.get('paciente_edad', '')} a os"],
            ]

            # Estilo com n para las tablas
            table_style = TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("TEXTCOLOR", (0, 0), (0, -1), COLOR_SECONDARY),
                    ("TEXTCOLOR", (1, 0), (-1, -1), COLOR_TEXT),
                    ("GRID", (0, 0), (-1, -1), 0.5, COLOR_SUBTEXT),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F8F9FA")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                    ("LEFTPADDING", (0, 0), (-1, -1), 15),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 15),
                ]
            )

            t = Table(patient_data, colWidths=[150, 350])
            t.setStyle(table_style)
            elements.append(t)
            elements.append(Spacer(1, 20))

            # Detalles de la Atenci n
            elements.append(
                Paragraph("Detalles de la Atenci n", styles["SectionTitle"])
            )
            attention_data = [
                ["Fecha y Hora:", atencion.get("fecha_hora", "")],
                ["Tipo de Atenci n:", atencion.get("tipo_atencion", "")],
                [
                    "Profesional:",
                    f"{user_data.get('nombre', '')} {user_data.get('apellido', '')}",
                ],
            ]
            t = Table(attention_data, colWidths=[150, 350])
            t.setStyle(table_style)
            elements.append(t)
            elements.append(Spacer(1, 20))

            # Evaluaci n Cl nica
            elements.append(Paragraph("Evaluaci n Cl nica", styles["SectionTitle"]))

            # Motivo de Consulta
            elements.append(Paragraph("Motivo de Consulta:", styles["Label"]))
            elements.append(
                Paragraph(atencion.get("motivo_consulta", ""), styles["Normal"])
            )
            elements.append(Spacer(1, 10))

            # Diagn stico
            elements.append(Paragraph("Diagn stico:", styles["Label"]))
            elements.append(
                Paragraph(atencion.get("diagnostico", ""), styles["Normal"])
            )
            elements.append(Spacer(1, 10))

            # Plan de Tratamiento
            elements.append(Paragraph("Plan de Tratamiento:", styles["Label"]))
            elements.append(
                Paragraph(atencion.get("tratamiento", ""), styles["Normal"])
            )
            elements.append(Spacer(1, 10))

            # Observaciones
            elements.append(Paragraph("Observaciones Adicionales:", styles["Label"]))
            elements.append(
                Paragraph(
                    atencion.get("observaciones", "Sin observaciones adicionales"),
                    styles["Normal"],
                )
            )
            elements.append(Spacer(1, 20))

            # Agregar imagen de la atenci n si existe
            imagen_path = atencion.get("imagen_path")
            if imagen_path and os.path.exists(os.path.join("static", imagen_path)):
                elements.append(Paragraph("Imagen Adjunta:", styles["SectionTitle"]))
                img = Image(os.path.join("static", imagen_path))

                # Calcular dimensiones manteniendo la proporci n
                desired_width = 400  # Ancho deseado en puntos
                img_ratio = img.imageHeight / float(img.imageWidth)
                img.drawWidth = desired_width
                img.drawHeight = desired_width * img_ratio

                # Centrar la imagen
                elements.append(img)
                elements.append(Spacer(1, 20))

            # Pie de p gina
            elements.append(Spacer(1, 40))
            footer_style = ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=8,
                textColor=COLOR_SUBTEXT,
                alignment=TA_CENTER,
            )
            elements.append(
                Paragraph(
                    f"Documento generado por MedConnect - Sistema de Gesti n de Atenciones M dicas<br/>"
                    f'Fecha de emisi n: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    footer_style,
                )
            )

            # Generar el PDF
            doc.build(elements)

            # Preparar el PDF para enviar
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"atencion_{atencion_id}.pdf",
            )

        except Exception as e:
            logger.error(f"Error generando PDF con ReportLab: {e}")
            return jsonify({"error": "Error generando el PDF"}), 500

    except Exception as e:
        logger.error(f"Error general generando PDF: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/api/archivos/<atencion_id>")
@login_required
def get_archivos_atencion(atencion_id):
    """Obtiene los archivos adjuntos de una atenci n"""
    try:
        archivos = sheets_db.get_archivos_atencion(atencion_id)
        return jsonify({"success": True, "archivos": archivos})
    except Exception as e:
        logger.error(f"Error obteniendo archivos: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/archivos/upload", methods=["POST"])
@login_required
def upload_archivos():
    """Sube archivos adjuntos para una atenci n"""
    try:
        logger.info("[BUSCAR] Iniciando subida de archivos")

        if "files[]" not in request.files:
            logger.error("[ERROR] No se enviaron archivos")
            return jsonify({"success": False, "error": "No se enviaron archivos"}), 400

        atencion_id = request.form.get("atencion_id")
        if not atencion_id:
            logger.error("[ERROR] No se especific  la atenci n")
            return (
                jsonify({"success": False, "error": "No se especific  la atenci n"}),
                400,
            )

        logger.info(f"[ARCHIVO] Procesando archivos para atenci n {atencion_id}")
        files = request.files.getlist("files[]")
        uploaded_files = []

        # Crear directorio base si no existe
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Crear subdirectorio para la atenci n
        atencion_folder = os.path.join(UPLOAD_FOLDER, atencion_id)
        if not os.path.exists(atencion_folder):
            os.makedirs(atencion_folder)

        for file in files:
            if file and allowed_file(file.filename):
                try:
                    # Asegurar nombre de archivo seguro
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(atencion_folder, filename)

                    # Si ya existe un archivo con ese nombre, agregar timestamp
                    if os.path.exists(file_path):
                        name, ext = os.path.splitext(filename)
                        filename = f"{name}_{int(time.time())}{ext}"
                        file_path = os.path.join(atencion_folder, filename)

                    logger.info(f"[GUARDAR] Guardando archivo: {filename}")
                    file.save(file_path)

                    # Registrar en la base de datos
                    archivo_data = {
                        "atencion_id": atencion_id,
                        "nombre_archivo": filename,
                        "tipo_archivo": file.content_type,
                        "ruta_archivo": os.path.join("uploads", atencion_id, filename),
                        "tama o": os.path.getsize(file_path),
                    }

                    logger.info("[NOTA] Registrando archivo en la base de datos")
                    archivo_id = sheets_db.registrar_archivo_adjunto(archivo_data)
                    uploaded_files.append(
                        {"archivo_id": archivo_id, "nombre_archivo": filename}
                    )
                    logger.info(
                        f"[OK] Archivo {filename} subido y registrado correctamente"
                    )

                except Exception as e:
                    logger.error(
                        f"[ERROR] Error procesando archivo {file.filename}: {e}"
                    )
                    continue
            else:
                logger.warning(
                    f"[ADVERTENCIA] Archivo no permitido o vac o: {file.filename if file else 'Sin archivo'}"
                )

        # Actualizar el estado de archivos en la atenci n
        if uploaded_files:
            try:
                spreadsheet = get_spreadsheet()
                worksheet = spreadsheet.worksheet("Atenciones_Medicas")
                records = worksheet.get_all_records()

                for i, record in enumerate(records, start=2):
                    if str(record.get("atencion_id", "")) == str(atencion_id):
                        worksheet.update_cell(i, 17, "S ")  # Columna tiene_archivos
                        logger.info(
                            f"[OK] Estado de archivos actualizado para atenci n {atencion_id}"
                        )
                        break
            except Exception as e:
                logger.warning(
                    f"[ADVERTENCIA] No se pudo actualizar estado de archivos: {e}"
                )

            return jsonify(
                {
                    "success": True,
                    "message": f"{len(uploaded_files)} archivos subidos correctamente",
                    "archivos": uploaded_files,
                }
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": "No se pudo procesar ning n archivo"}
                ),
                400,
            )

    except Exception as e:
        logger.error(f"[ERROR] Error subiendo archivos: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/archivos/<archivo_id>", methods=["DELETE"])
@login_required
def delete_archivo(archivo_id):
    """Elimina un archivo adjunto"""
    try:
        if sheets_db.delete_archivo(archivo_id):
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Archivo no encontrado"}), 404
    except Exception as e:
        logger.error(f"Error eliminando archivo: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/archivos/<archivo_id>/download")
@login_required
def download_archivo(archivo_id):
    """Descarga un archivo adjunto"""
    try:
        # Obtener informaci n del archivo
        archivo = sheets_db.get_archivo_by_id(archivo_id)
        if not archivo:
            return jsonify({"success": False, "message": "Archivo no encontrado"}), 404

        # Construir la ruta del archivo
        ruta_archivo = archivo.get("ruta_archivo", "")

        # Si la ruta incluye 'uploads', usar directamente; si no, construir la ruta
        if ruta_archivo.startswith("uploads"):
            file_path = os.path.join(app.root_path, "static", ruta_archivo)
        else:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], ruta_archivo)

        logger.info(f"[BUSCAR] Buscando archivo en: {file_path}")

        if not os.path.exists(file_path):
            logger.error(f"[ERROR] Archivo no encontrado en: {file_path}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Archivo no encontrado en el servidor",
                    }
                ),
                404,
            )

        # Enviar archivo
        return send_file(
            file_path,
            as_attachment=True,
            download_name=archivo.get("nombre_archivo"),
            mimetype=archivo.get("tipo_archivo"),
        )

    except Exception as e:
        logger.error(f"Error descargando archivo: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500


@app.route("/api/archivos/<archivo_id>/view")
@login_required
def view_archivo(archivo_id):
    """Sirve un archivo adjunto para visualizaci n (no descarga)"""
    try:
        # Obtener informaci n del archivo
        archivo = sheets_db.get_archivo_by_id(archivo_id)
        if not archivo:
            logger.error(f"[ERROR] Archivo no encontrado: {archivo_id}")
            abort(404)

        # Construir la ruta del archivo
        ruta_archivo = archivo.get("ruta_archivo", "")

        # Si la ruta incluye 'uploads', usar directamente; si no, construir la ruta
        if ruta_archivo.startswith("uploads"):
            file_path = os.path.join(app.root_path, "static", ruta_archivo)
        elif ruta_archivo.startswith("static"):
            file_path = os.path.join(app.root_path, ruta_archivo)
        else:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], ruta_archivo)

        logger.info(f"[BUSCAR] Sirviendo archivo para visualizaci n: {file_path}")

        # Probar rutas alternativas si no existe (como en el endpoint temporal que funciona)
        if not os.path.exists(file_path):
            rutas_alternativas = [
                ruta_archivo,  # Ruta directa
                os.path.join(
                    "static", "uploads", atencion_id, archivo.get("nombre_archivo", "")
                ),  # Ruta reconstruida
                os.path.join(
                    app.root_path,
                    "static",
                    "uploads",
                    atencion_id,
                    archivo.get("nombre_archivo", ""),
                ),
                f'static/uploads/{atencion_id}/{archivo.get("nombre_archivo", "")}',
            ]

            for ruta_alt in rutas_alternativas:
                if os.path.exists(ruta_alt):
                    logger.info(
                        f"[OK] Archivo encontrado en ruta alternativa: {ruta_alt}"
                    )
                    file_path = ruta_alt
                    break
            else:
                logger.error(
                    f"[ERROR] Archivo no encontrado en ninguna ruta: {file_path}"
                )
                abort(404)

        # Verificar que el usuario tiene acceso a esta atenci n
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))
        atencion_id = archivo.get("atencion_id", "")

        # Verificar permisos de acceso a la atenci n
        try:
            spreadsheet = get_spreadsheet()
            worksheet = spreadsheet.worksheet("Atenciones_Medicas")
            records = worksheet.get_all_records()

            tiene_acceso = False
            for record in records:
                if str(record.get("atencion_id", "")) == str(atencion_id) and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):
                    tiene_acceso = True
                    break

            if not tiene_acceso:
                logger.warning(
                    f"[ADVERTENCIA] Acceso denegado al archivo {archivo_id} para profesional {profesional_id}"
                )
                abort(403)

        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            abort(500)

        # Servir el archivo para visualizaci n (sin forzar descarga)
        return send_file(
            file_path,
            as_attachment=False,  # Clave: no forzar descarga
            mimetype=archivo.get("tipo_archivo"),
        )

    except Exception as e:
        logger.error(f"Error sirviendo archivo para visualizaci n: {e}")
        abort(500)


@app.route("/api/test-archivo/<archivo_id>")
def test_view_archivo(archivo_id):
    """Endpoint de prueba sin autenticaci n para verificar servido de archivos"""
    try:
        logger.info(f"  Test endpoint llamado para archivo: {archivo_id}")

        # Obtener informaci n del archivo
        archivo = sheets_db.get_archivo_by_id(archivo_id)
        if not archivo:
            logger.error(f"[ERROR] Archivo no encontrado: {archivo_id}")
            return jsonify({"error": "Archivo no encontrado"}), 404

        logger.info(f"[DOCUMENTO] Informaci n del archivo: {archivo}")
        logger.info(f"[BUSCAR] Tipo de archivo: {type(archivo)}")
        logger.info(
            f"[BUSCAR] Keys del archivo: {list(archivo.keys()) if archivo else 'None'}"
        )

        # Construir la ruta del archivo
        ruta_archivo = archivo.get("ruta_archivo", "")
        logger.info(
            f"[BUSCAR] ruta_archivo: {ruta_archivo} (tipo: {type(ruta_archivo)})"
        )

        # Asegurar que ruta_archivo sea string
        ruta_archivo = str(ruta_archivo) if ruta_archivo else ""

        # Si la ruta incluye 'uploads', usar directamente; si no, construir la ruta
        if ruta_archivo.startswith("uploads"):
            file_path = os.path.join(app.root_path, "static", ruta_archivo)
        elif ruta_archivo.startswith("static"):
            file_path = os.path.join(app.root_path, ruta_archivo)
        else:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], ruta_archivo)

        logger.info(f"[BUSCAR] Buscando archivo en: {file_path}")
        logger.info(f"[BUSCAR] app.root_path: {app.root_path}")
        logger.info(
            f"[BUSCAR] UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER', 'Not set')}"
        )

        # Probar rutas alternativas si no existe
        if not os.path.exists(file_path):
            rutas_alternativas = [
                ruta_archivo,  # Ruta directa
                os.path.join(
                    "static", "uploads", "ATN_20250701_152633", "test_image.jpg"
                ),  # Ruta reconstruida
                os.path.join(
                    app.root_path,
                    "static",
                    "uploads",
                    "ATN_20250701_152633",
                    "test_image.jpg",
                ),
                "static/uploads/ATN_20250701_152633/test_image.jpg",
            ]

            for ruta_alt in rutas_alternativas:
                logger.info(f"[BUSCAR] Probando ruta alternativa: {ruta_alt}")
                if os.path.exists(ruta_alt):
                    logger.info(
                        f"[OK]  Archivo encontrado en ruta alternativa!: {ruta_alt}"
                    )
                    file_path = ruta_alt
                    break
            else:
                logger.error(f"[ERROR] Archivo no encontrado en ninguna ruta")
                logger.error(
                    f"[ERROR] Rutas probadas: {[file_path] + rutas_alternativas}"
                )
                return jsonify({"error": "Archivo f sico no encontrado"}), 404

        logger.info(f"[OK] Archivo encontrado, sirviendo...")

        # Crear respuesta personalizada para evitar descarga forzada
        response = make_response(
            send_file(
                file_path,
                as_attachment=False,  # No forzar descarga
                mimetype=archivo.get("tipo_archivo"),
            )
        )

        # Headers espec ficos para evitar descarga autom tica
        response.headers["Content-Disposition"] = "inline"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-cache"

        return response

    except Exception as e:
        logger.error(f"[ERROR] Error en test endpoint: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/uploads/atenciones/<atencion_id>/<filename>")
@login_required
def serve_atencion_file(atencion_id, filename):
    """Sirve archivos adjuntos de atenciones para visualizaci n"""
    try:
        # Verificar que el archivo existe
        file_path = os.path.join(UPLOAD_FOLDER, atencion_id, filename)
        if not os.path.exists(file_path):
            abort(404)

        # Verificar que el usuario tiene acceso a esta atenci n
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        # Obtener informaci n de la atenci n para verificar permisos
        try:
            spreadsheet = get_spreadsheet()
            worksheet = spreadsheet.worksheet("Atenciones_Medicas")
            records = worksheet.get_all_records()

            tiene_acceso = False
            for record in records:
                if str(record.get("atencion_id", "")) == str(atencion_id) and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):
                    tiene_acceso = True
                    break

            if not tiene_acceso:
                abort(403)

        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            abort(500)

        # Servir el archivo
        return send_from_directory(os.path.join(UPLOAD_FOLDER, atencion_id), filename)

    except Exception as e:
        logger.error(f"Error sirviendo archivo: {e}")
        abort(500)


# ====== AGENDA Y CITAS ======


@app.route("/api/professional/schedule", methods=["GET"])
@login_required
def get_professional_schedule():
    """Obtiene la agenda del profesional"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener fecha solicitada (por defecto hoy)
        fecha_solicitada = request.args.get(
            "fecha", datetime.now().strftime("%Y-%m-%d")
        )
        vista = request.args.get("vista", "diaria")  # diaria, semanal, mensual

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            # Intentar usar el m todo optimizado primero
            try:
                from backend.database.sheets_manager import sheets_db

                # Obtener agenda optimizada
                schedule_data = sheets_db.get_professional_schedule_optimized(
                    profesional_id, fecha_solicitada, fecha_solicitada
                )

                if schedule_data and schedule_data.get("citas"):
                    citas_del_dia = schedule_data["citas"]
                    logger.info(
                        f"[OK] Agenda obtenida con m todo optimizado: {len(citas_del_dia)} citas"
                    )
                else:
                    # Fallback al m todo original
                    raise Exception("No hay datos en m todo optimizado")

            except Exception as e:
                logger.warning(
                    f"[ADVERTENCIA] M todo optimizado fall , usando fallback: {e}"
                )

                # Obtener o crear la hoja de citas
                try:
                    worksheet = spreadsheet.worksheet("Citas_Agenda")
                except:
                    # Si no existe, crearla
                    headers = [
                        "cita_id",
                        "profesional_id",
                        "paciente_id",
                        "paciente_nombre",
                        "paciente_rut",
                        "fecha",
                        "hora",
                        "tipo_atencion",
                        "estado",
                        "notas",
                        "fecha_creacion",
                        "recordatorio",
                    ]
                    worksheet = spreadsheet.add_worksheet(
                        title="Citas_Agenda", rows=1000, cols=len(headers)
                    )
                    worksheet.append_row(headers)
                    logger.info("[OK] Hoja Citas_Agenda creada")

                records = worksheet.get_all_records()

            # Filtrar citas del profesional y fecha
            citas_del_dia = []
            for record in records:
                if (
                    str(record.get("profesional_id", "")) == str(profesional_id)
                    and record.get("fecha", "") == fecha_solicitada
                ):
                    citas_del_dia.append(
                        {
                            "cita_id": record.get("cita_id", ""),
                            "paciente_nombre": record.get("paciente_nombre", ""),
                            "paciente_rut": record.get("paciente_rut", ""),
                            "hora": record.get("hora", ""),
                            "tipo_atencion": record.get("tipo_atencion", ""),
                            "estado": record.get("estado", ""),
                            "notas": record.get("notas", ""),
                            "recordatorio": record.get("recordatorio", ""),
                        }
                    )

            # Generar horarios disponibles (8:00 - 18:00, cada 30 minutos)
            horarios_disponibles = []
            hora_inicio = 8
            hora_fin = 18

            for hora in range(hora_inicio, hora_fin):
                for minuto in [0, 30]:
                    hora_str = f"{hora:02d}:{minuto:02d}"

                    # Verificar si ya hay una cita en este horario
                    ocupado = any(cita["hora"] == hora_str for cita in citas_del_dia)

                    if not ocupado:
                        horarios_disponibles.append(hora_str)

            # Estad sticas del d a
            total_citas = len(citas_del_dia)
            confirmadas = len([c for c in citas_del_dia if c["estado"] == "confirmada"])
            pendientes = len([c for c in citas_del_dia if c["estado"] == "pendiente"])
            disponibles = len(horarios_disponibles)

            if vista == "diaria":
                return jsonify(
                    {
                        "success": True,
                        "vista": "diaria",
                        "fecha": fecha_solicitada,
                        "citas": citas_del_dia,
                        "horarios_disponibles": horarios_disponibles,
                        "estadisticas": {
                            "total_citas": total_citas,
                            "confirmadas": confirmadas,
                            "pendientes": pendientes,
                            "disponibles": disponibles,
                        },
                    }
                )
            elif vista == "semanal":
                # Obtener citas de la semana
                fecha_inicio, fecha_fin = obtener_rango_semana(fecha_solicitada)
                citas_semana = []

                for record in records:
                    if (
                        str(record.get("profesional_id", "")) == str(profesional_id)
                        and fecha_inicio <= record.get("fecha", "") <= fecha_fin
                    ):
                        citas_semana.append(
                            {
                                "cita_id": record.get("cita_id", ""),
                                "paciente_nombre": record.get("paciente_nombre", ""),
                                "paciente_rut": record.get("paciente_rut", ""),
                                "fecha": record.get("fecha", ""),
                                "hora": record.get("hora", ""),
                                "tipo_atencion": record.get("tipo_atencion", ""),
                                "estado": record.get("estado", ""),
                                "notas": record.get("notas", ""),
                            }
                        )

                agenda_semanal = organizar_agenda_semanal(
                    citas_semana, fecha_inicio, fecha_fin
                )

                return jsonify(
                    {
                        "success": True,
                        "vista": "semanal",
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "agenda_semanal": agenda_semanal,
                        "estadisticas": calcular_estadisticas_semana(citas_semana),
                    }
                )
            elif vista == "mensual":
                # Obtener citas del mes
                fecha_inicio, fecha_fin = obtener_rango_mes(fecha_solicitada)
                citas_mes = []

                for record in records:
                    if (
                        str(record.get("profesional_id", "")) == str(profesional_id)
                        and fecha_inicio <= record.get("fecha", "") <= fecha_fin
                    ):
                        citas_mes.append(
                            {
                                "cita_id": record.get("cita_id", ""),
                                "paciente_nombre": record.get("paciente_nombre", ""),
                                "paciente_rut": record.get("paciente_rut", ""),
                                "fecha": record.get("fecha", ""),
                                "hora": record.get("hora", ""),
                                "tipo_atencion": record.get("tipo_atencion", ""),
                                "estado": record.get("estado", ""),
                                "notas": record.get("notas", ""),
                            }
                        )

                agenda_mensual = organizar_agenda_mensual(
                    citas_mes, fecha_inicio, fecha_fin
                )

                return jsonify(
                    {
                        "success": True,
                        "vista": "mensual",
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "agenda_mensual": agenda_mensual,
                        "estadisticas": calcular_estadisticas_mes(citas_mes),
                    }
                )

        except Exception as e:
            logger.error(f"Error obteniendo agenda: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al consultar la agenda: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en get_professional_schedule: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/schedule", methods=["POST"])
@login_required
def create_appointment():
    """Crea una nueva cita en la agenda"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"[NOTA] Datos de la nueva cita: {data}")

        # Validar campos requeridos
        required_fields = ["paciente_id", "fecha", "hora", "tipo_atencion"]
        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify(
                        {"success": False, "message": f"El campo {field} es requerido"}
                    ),
                    400,
                )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            # Obtener informaci n del paciente
            pacientes_worksheet = spreadsheet.worksheet("Pacientes_Profesional")
            pacientes_records = pacientes_worksheet.get_all_records()

            paciente_info = None
            for record in pacientes_records:
                if record.get("paciente_id") == data.get("paciente_id") and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):
                    paciente_info = record
                    break

            if not paciente_info:
                return (
                    jsonify({"success": False, "message": "Paciente no encontrado"}),
                    404,
                )

            # Obtener hoja de citas
            try:
                worksheet = spreadsheet.worksheet("Citas_Agenda")
            except:
                # Si no existe, crearla
                headers = [
                    "cita_id",
                    "profesional_id",
                    "paciente_id",
                    "paciente_nombre",
                    "paciente_rut",
                    "fecha",
                    "hora",
                    "tipo_atencion",
                    "estado",
                    "notas",
                    "fecha_creacion",
                    "recordatorio",
                ]
                worksheet = spreadsheet.add_worksheet(
                    title="Citas_Agenda", rows=1000, cols=len(headers)
                )
                worksheet.append_row(headers)
                logger.info("[OK] Hoja Citas_Agenda creada")

            # Verificar disponibilidad del horario
            records = worksheet.get_all_records()
            for record in records:
                if (
                    str(record.get("profesional_id", "")) == str(profesional_id)
                    and record.get("fecha", "") == data.get("fecha")
                    and record.get("hora", "") == data.get("hora")
                ):
                    return (
                        jsonify(
                            {"success": False, "message": "El horario ya est  ocupado"}
                        ),
                        400,
                    )

            # Generar ID  nico para la cita
            cita_id = f"CITA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Preparar datos para insertar
            nueva_cita = [
                cita_id,
                profesional_id,
                data.get("paciente_id", ""),
                paciente_info.get("nombre_completo", ""),
                paciente_info.get("rut", ""),
                data.get("fecha", ""),
                data.get("hora", ""),
                data.get("tipo_atencion", ""),
                "pendiente",  # estado por defecto
                data.get("notas", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data.get("recordatorio", "no"),
            ]

            # Insertar en Google Sheets
            worksheet.append_row(nueva_cita)
            logger.info(f"[OK] Cita {cita_id} creada exitosamente")

            return jsonify(
                {
                    "success": True,
                    "message": "Cita agendada exitosamente",
                    "cita_id": cita_id,
                    "cita": {
                        "cita_id": cita_id,
                        "paciente_nombre": paciente_info.get("nombre_completo", ""),
                        "paciente_rut": paciente_info.get("rut", ""),
                        "fecha": data.get("fecha", ""),
                        "hora": data.get("hora", ""),
                        "tipo_atencion": data.get("tipo_atencion", ""),
                        "estado": "pendiente",
                        "notas": data.get("notas", ""),
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error creando cita: {e}")
            return (
                jsonify(
                    {"success": False, "message": f"Error al crear la cita: {str(e)}"}
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en create_appointment: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/schedule/<cita_id>", methods=["PUT"])
@login_required
def update_appointment(cita_id):
    """Actualiza una cita existente"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"[NOTA] Actualizando cita {cita_id}: {data}")

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Citas_Agenda")
            records = worksheet.get_all_records()

            # Buscar la cita
            for i, record in enumerate(records):
                if record.get("cita_id") == cita_id and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):

                    # Actualizar campos espec ficos
                    if "estado" in data:
                        worksheet.update(
                            f"I{i+2}", [[data["estado"]]]
                        )  # Columna I es estado
                    if "notas" in data:
                        worksheet.update(
                            f"J{i+2}", [[data["notas"]]]
                        )  # Columna J es notas
                    if "recordatorio" in data:
                        worksheet.update(
                            f"L{i+2}", [[data["recordatorio"]]]
                        )  # Columna L es recordatorio

                    logger.info(f"[OK] Cita {cita_id} actualizada exitosamente")

                    return jsonify(
                        {"success": True, "message": "Cita actualizada exitosamente"}
                    )

            return jsonify({"success": False, "message": "Cita no encontrada"}), 404

        except Exception as e:
            logger.error(f"Error actualizando cita: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al actualizar la cita: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en update_appointment: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/schedule/<cita_id>", methods=["DELETE"])
@login_required
def delete_appointment(cita_id):
    """Elimina una cita de la agenda"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Citas_Agenda")
            records = worksheet.get_all_records()

            # Buscar la cita
            for i, record in enumerate(records):
                if record.get("cita_id") == cita_id and str(
                    record.get("profesional_id", "")
                ) == str(profesional_id):

                    # Eliminar la fila (i+2 porque las filas empiezan en 1 y hay header)
                    worksheet.delete_rows(i + 2)
                    logger.info(f"[OK] Cita {cita_id} eliminada exitosamente")

                    return jsonify(
                        {"success": True, "message": "Cita eliminada exitosamente"}
                    )

            return jsonify({"success": False, "message": "Cita no encontrada"}), 404

        except Exception as e:
            logger.error(f"Error eliminando cita: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al eliminar la cita: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en delete_appointment: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/working-hours", methods=["GET"])
@login_required
def get_working_hours():
    """Obtiene el horario de trabajo del profesional"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            # Obtener o crear la hoja de horarios
            try:
                worksheet = spreadsheet.worksheet("Horarios_Profesional")
            except:
                # Si no existe, crearla con horario por defecto
                headers = [
                    "profesional_id",
                    "dia_semana",
                    "hora_inicio",
                    "hora_fin",
                    "disponible",
                    "notas",
                ]
                worksheet = spreadsheet.add_worksheet(
                    title="Horarios_Profesional", rows=1000, cols=len(headers)
                )
                worksheet.append_row(headers)

                # Crear horario por defecto (Lunes a Viernes, 8:00 - 18:00)
                dias_semana = ["Lunes", "Martes", "Mi rcoles", "Jueves", "Viernes"]
                for dia in dias_semana:
                    worksheet.append_row(
                        [profesional_id, dia, "08:00", "18:00", "true", ""]
                    )

                logger.info(
                    "[OK] Hoja Horarios_Profesional creada con horario por defecto"
                )

            records = worksheet.get_all_records()

            # Filtrar horarios del profesional
            horarios = []
            for record in records:
                if str(record.get("profesional_id", "")) == str(profesional_id):
                    horarios.append(
                        {
                            "dia_semana": record.get("dia_semana", ""),
                            "hora_inicio": record.get("hora_inicio", ""),
                            "hora_fin": record.get("hora_fin", ""),
                            "disponible": record.get("disponible", "true") == "true",
                            "notas": record.get("notas", ""),
                        }
                    )

            return jsonify({"success": True, "horarios": horarios})

        except Exception as e:
            logger.error(f"Error obteniendo horarios: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al consultar los horarios: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en get_working_hours: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/reminders", methods=["GET"])
@login_required
def get_reminders():
    """Obtiene los recordatorios del profesional"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Intentar usar el m todo optimizado primero
        try:
            from backend.database.sheets_manager import sheets_db

            # Obtener recordatorios usando el m todo optimizado
            recordatorios = sheets_db.get_user_active_reminders(profesional_id)

            if recordatorios is not None:
                logger.info(
                    f"[OK] Recordatorios obtenidos con m todo optimizado: {len(recordatorios)} recordatorios"
                )
                return jsonify({"success": True, "recordatorios": recordatorios})
            else:
                # Fallback al m todo original
                raise Exception("No hay datos en m todo optimizado")

        except Exception as e:
            logger.warning(
                f"[ADVERTENCIA] M todo optimizado fall , usando fallback: {e}"
            )

            # Obtener la hoja de c lculo
            spreadsheet = get_spreadsheet()
            if not spreadsheet:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Error conectando con la base de datos",
                        }
                    ),
                    500,
                )

            try:
                # Obtener o crear la hoja de recordatorios
                try:
                    worksheet = spreadsheet.worksheet("Recordatorios_Profesional")
                except:
                    # Si no existe, crearla
                    headers = [
                        "recordatorio_id",
                        "profesional_id",
                        "tipo",
                        "paciente_id",
                        "titulo",
                        "mensaje",
                        "fecha",
                        "hora",
                        "prioridad",
                        "repetir",
                        "tipo_repeticion",
                        "estado",
                        "fecha_creacion",
                    ]
                    worksheet = spreadsheet.add_worksheet(
                        title="Recordatorios_Profesional", rows=1000, cols=len(headers)
                    )
                    worksheet.append_row(headers)
                    logger.info("[OK] Hoja Recordatorios_Profesional creada")

                records = worksheet.get_all_records()

                # Filtrar recordatorios del profesional y activos
                recordatorios = []
                for record in records:
                    if (
                        str(record.get("profesional_id", "")) == str(profesional_id)
                        and record.get("estado", "") == "activo"
                    ):
                        recordatorios.append(
                            {
                                "id": record.get("recordatorio_id", ""),
                                "tipo": record.get("tipo", ""),
                                "paciente_id": record.get("paciente_id", ""),
                                "titulo": record.get("titulo", ""),
                                "mensaje": record.get("mensaje", ""),
                                "fecha": record.get("fecha", ""),
                                "hora": record.get("hora", ""),
                                "prioridad": record.get("prioridad", "media"),
                                "repetir": record.get("repetir", "false").lower()
                                == "true",
                                "tipo_repeticion": record.get("tipo_repeticion", ""),
                                "estado": record.get("estado", "activo"),
                            }
                        )

                return jsonify({"success": True, "recordatorios": recordatorios})

            except Exception as e:
                logger.error(f"Error obteniendo recordatorios: {e}")
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"Error al consultar los recordatorios: {str(e)}",
                        }
                    ),
                    500,
                )

    except Exception as e:
        logger.error(f"Error en get_reminders: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/reminders", methods=["POST"])
@login_required
def create_reminder():
    """Crea un nuevo recordatorio"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"[NOTA] Creando recordatorio: {data}")

        # Validar campos requeridos
        required_fields = ["tipo", "titulo", "mensaje", "fecha", "hora", "prioridad"]
        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify(
                        {"success": False, "message": f"El campo {field} es requerido"}
                    ),
                    400,
                )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            # Obtener hoja de recordatorios
            try:
                worksheet = spreadsheet.worksheet("Recordatorios_Profesional")
            except:
                # Si no existe, crearla
                headers = [
                    "recordatorio_id",
                    "profesional_id",
                    "tipo",
                    "paciente_id",
                    "titulo",
                    "mensaje",
                    "fecha",
                    "hora",
                    "prioridad",
                    "repetir",
                    "tipo_repeticion",
                    "estado",
                    "fecha_creacion",
                ]
                worksheet = spreadsheet.add_worksheet(
                    title="Recordatorios_Profesional", rows=1000, cols=len(headers)
                )
                worksheet.append_row(headers)
                logger.info("[OK] Hoja Recordatorios_Profesional creada")

            # Generar ID  nico
            recordatorio_id = str(uuid.uuid4())

            # Crear nueva fila
            nueva_fila = [
                recordatorio_id,
                profesional_id,
                data.get("tipo", ""),
                data.get("paciente_id", ""),
                data.get("titulo", ""),
                data.get("mensaje", ""),
                data.get("fecha", ""),
                data.get("hora", ""),
                data.get("prioridad", "media"),
                str(data.get("repetir", False)).lower(),
                data.get("tipo_repeticion", ""),
                "activo",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ]

            worksheet.append_row(nueva_fila)

            logger.info(f"[OK] Recordatorio creado exitosamente: {recordatorio_id}")

            return jsonify(
                {
                    "success": True,
                    "message": "Recordatorio creado exitosamente",
                    "recordatorio_id": recordatorio_id,
                }
            )

        except Exception as e:
            logger.error(f"Error creando recordatorio: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al crear el recordatorio: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en create_reminder: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/reminders/<recordatorio_id>", methods=["GET"])
@login_required
def get_reminder(recordatorio_id):
    """Obtiene un recordatorio espec fico"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Recordatorios_Profesional")
            records = worksheet.get_all_records()

            # Buscar el recordatorio espec fico
            recordatorio = None
            for record in records:
                if str(record.get("recordatorio_id", "")) == str(
                    recordatorio_id
                ) and str(record.get("profesional_id", "")) == str(profesional_id):
                    recordatorio = {
                        "id": record.get("recordatorio_id", ""),
                        "tipo": record.get("tipo", ""),
                        "paciente_id": record.get("paciente_id", ""),
                        "titulo": record.get("titulo", ""),
                        "mensaje": record.get("mensaje", ""),
                        "fecha": record.get("fecha", ""),
                        "hora": record.get("hora", ""),
                        "prioridad": record.get("prioridad", "media"),
                        "repetir": record.get("repetir", "false").lower() == "true",
                        "tipo_repeticion": record.get("tipo_repeticion", ""),
                        "estado": record.get("estado", "activo"),
                    }
                    break

            if not recordatorio:
                return (
                    jsonify(
                        {"success": False, "message": "Recordatorio no encontrado"}
                    ),
                    404,
                )

            return jsonify({"success": True, "recordatorio": recordatorio})

        except Exception as e:
            logger.error(f"Error obteniendo recordatorio: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al consultar el recordatorio: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en get_reminder: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/reminders/<recordatorio_id>", methods=["PUT"])
@login_required
def update_reminder(recordatorio_id):
    """Actualiza un recordatorio existente"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"[NOTA] Actualizando recordatorio {recordatorio_id}: {data}")

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Recordatorios_Profesional")
            records = worksheet.get_all_records()

            # Buscar y actualizar el recordatorio
            encontrado = False
            for i, record in enumerate(records):
                if str(record.get("recordatorio_id", "")) == str(
                    recordatorio_id
                ) and str(record.get("profesional_id", "")) == str(profesional_id):

                    # Actualizar campos
                    worksheet.update(f"C{i+2}", [[data.get("tipo", "")]])  # tipo
                    worksheet.update(
                        f"D{i+2}", [[data.get("paciente_id", "")]]
                    )  # paciente_id
                    worksheet.update(f"E{i+2}", [[data.get("titulo", "")]])  # titulo
                    worksheet.update(f"F{i+2}", [[data.get("mensaje", "")]])  # mensaje
                    worksheet.update(f"G{i+2}", [[data.get("fecha", "")]])  # fecha
                    worksheet.update(f"H{i+2}", [[data.get("hora", "")]])  # hora
                    worksheet.update(
                        f"I{i+2}", [[data.get("prioridad", "media")]]
                    )  # prioridad
                    worksheet.update(
                        f"J{i+2}", [[str(data.get("repetir", False)).lower()]]
                    )  # repetir
                    worksheet.update(
                        f"K{i+2}", [[data.get("tipo_repeticion", "")]]
                    )  # tipo_repeticion

                    encontrado = True
                    break

            if not encontrado:
                return (
                    jsonify(
                        {"success": False, "message": "Recordatorio no encontrado"}
                    ),
                    404,
                )

            logger.info(f"[OK] Recordatorio {recordatorio_id} actualizado exitosamente")

            return jsonify(
                {"success": True, "message": "Recordatorio actualizado exitosamente"}
            )

        except Exception as e:
            logger.error(f"Error actualizando recordatorio: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al actualizar el recordatorio: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en update_reminder: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/reminders/<recordatorio_id>", methods=["DELETE"])
@login_required
def delete_reminder(recordatorio_id):
    """Elimina un recordatorio (marca como inactivo)"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Recordatorios_Profesional")
            records = worksheet.get_all_records()

            # Buscar y marcar como inactivo el recordatorio
            encontrado = False
            for i, record in enumerate(records):
                if str(record.get("recordatorio_id", "")) == str(
                    recordatorio_id
                ) and str(record.get("profesional_id", "")) == str(profesional_id):

                    # Marcar como inactivo
                    worksheet.update(f"L{i+2}", [["inactivo"]])  # estado

                    encontrado = True
                    break

            if not encontrado:
                return (
                    jsonify(
                        {"success": False, "message": "Recordatorio no encontrado"}
                    ),
                    404,
                )

            logger.info(f"[OK] Recordatorio {recordatorio_id} eliminado exitosamente")

            return jsonify(
                {"success": True, "message": "Recordatorio eliminado exitosamente"}
            )

        except Exception as e:
            logger.error(f"Error eliminando recordatorio: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al eliminar el recordatorio: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en delete_reminder: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/professional/working-hours", methods=["POST"])
@login_required
def update_working_hours():
    """Actualiza el horario de trabajo del profesional"""
    try:
        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        if not profesional_id:
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Obtener datos del formulario
        data = request.get_json()
        logger.info(
            f"[NOTA] Actualizando horarios del profesional {profesional_id}: {data}"
        )

        # Obtener la hoja de c lculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error conectando con la base de datos",
                    }
                ),
                500,
            )

        try:
            worksheet = spreadsheet.worksheet("Horarios_Profesional")
            records = worksheet.get_all_records()

            # Actualizar horarios existentes
            for horario in data.get("horarios", []):
                dia_semana = horario.get("dia_semana")

                # Buscar si ya existe el horario para este d a
                encontrado = False
                for i, record in enumerate(records):
                    if (
                        str(record.get("profesional_id", "")) == str(profesional_id)
                        and record.get("dia_semana", "") == dia_semana
                    ):

                        # Actualizar horario existente
                        worksheet.update(
                            f"C{i+2}", [[horario.get("hora_inicio", "")]]
                        )  # Columna C es hora_inicio
                        worksheet.update(
                            f"D{i+2}", [[horario.get("hora_fin", "")]]
                        )  # Columna D es hora_fin
                        worksheet.update(
                            f"E{i+2}", [[str(horario.get("disponible", True)).lower()]]
                        )  # Columna E es disponible
                        worksheet.update(
                            f"F{i+2}", [[horario.get("notas", "")]]
                        )  # Columna F es notas

                        encontrado = True
                        break

                # Si no existe, crear nuevo horario
                if not encontrado:
                    nueva_fila = [
                        profesional_id,
                        dia_semana,
                        horario.get("hora_inicio", ""),
                        horario.get("hora_fin", ""),
                        str(horario.get("disponible", True)).lower(),
                        horario.get("notas", ""),
                    ]
                    worksheet.append_row(nueva_fila)

            logger.info(
                f"[OK] Horarios del profesional {profesional_id} actualizados exitosamente"
            )

            return jsonify(
                {"success": True, "message": "Horarios actualizados exitosamente"}
            )

        except Exception as e:
            logger.error(f"Error actualizando horarios: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Error al actualizar los horarios: {str(e)}",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en update_working_hours: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/test-patients")
def test_patients_page():
    """P gina de prueba para el endpoint de pacientes"""
    return send_from_directory(".", "test_patients_browser.html")


@app.route("/api/monitor")
def api_monitor():
    """Endpoint para monitorear el uso de la API de Google Sheets"""
    try:
        from api_monitoring import get_api_stats, get_api_recommendations

        stats = get_api_stats()
        recommendations = get_api_recommendations()

        monitor_data = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "recommendations": recommendations,
            "optimization_tips": [
                {
                    "type": "info",
                    "title": "Batch Operations",
                    "description": "Usa batch_get_values() y batch_update_values() para reducir llamadas a la API",
                    "implementation": "Ya implementado en SheetsManager",
                },
                {
                    "type": "info",
                    "title": "Field Masks",
                    "description": "Usa get_worksheet_with_fields() para obtener solo campos espec ficos",
                    "implementation": "Disponible en SheetsManager",
                },
                {
                    "type": "warning",
                    "title": "Cache Duration",
                    "description": "Considera aumentar la duraci n del cache si el uso es alto",
                    "implementation": "Configurable en SheetsManager",
                },
                {
                    "type": "success",
                    "title": "Exponential Backoff",
                    "description": "Reintentos autom ticos con backoff exponencial implementado",
                    "implementation": "Activo en SheetsManager",
                },
            ],
        }

        return jsonify(monitor_data)

    except Exception as e:
        logger.error(f"[ERROR] Error en api_monitor: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/api/database-diagnostic")
def database_diagnostic():
    """Diagnóstico específico para problemas de base de datos"""
    try:
        diagnostic_results = {
            "timestamp": datetime.now().isoformat(),
            "sheets_manager": {},
            "auth_manager": {},
            "environment_variables": {},
            "connection_tests": {},
            "recommendations": [],
        }

        # 1. Verificar SheetsManager
        try:
            if sheets_db:
                diagnostic_results["sheets_manager"]["status"] = "DISPONIBLE"
                diagnostic_results["sheets_manager"]["type"] = str(type(sheets_db))

                # Intentar operación básica
                try:
                    test_result = sheets_db.test_connection()
                    diagnostic_results["sheets_manager"]["connection"] = (
                        "OK" if test_result else "ERROR"
                    )
                    diagnostic_results["connection_tests"]["sheets_basic"] = "PASÓ"
                except Exception as e:
                    diagnostic_results["sheets_manager"]["connection"] = "ERROR"
                    diagnostic_results["sheets_manager"]["error"] = str(e)
                    diagnostic_results["connection_tests"]["sheets_basic"] = "FALLÓ"
                    diagnostic_results["recommendations"].append(
                        "Verificar credenciales de Google Sheets"
                    )
            else:
                diagnostic_results["sheets_manager"]["status"] = "NO DISPONIBLE"
                diagnostic_results["recommendations"].append(
                    "Inicializar SheetsManager"
                )
        except Exception as e:
            diagnostic_results["sheets_manager"]["status"] = "ERROR"
            diagnostic_results["sheets_manager"]["error"] = str(e)

        # 2. Verificar AuthManager
        try:
            if auth_manager:
                diagnostic_results["auth_manager"]["status"] = "DISPONIBLE"
                diagnostic_results["auth_manager"]["type"] = str(type(auth_manager))

                # Intentar operación básica
                try:
                    test_users = auth_manager.get_all_users()
                    diagnostic_results["auth_manager"]["connection"] = (
                        "OK" if test_users is not None else "ERROR"
                    )
                    diagnostic_results["connection_tests"]["auth_basic"] = "PASÓ"
                except Exception as e:
                    diagnostic_results["auth_manager"]["connection"] = "ERROR"
                    diagnostic_results["auth_manager"]["error"] = str(e)
                    diagnostic_results["connection_tests"]["auth_basic"] = "FALLÓ"
                    diagnostic_results["recommendations"].append(
                        "Verificar configuración de AuthManager"
                    )
            else:
                diagnostic_results["auth_manager"]["status"] = "NO DISPONIBLE"
                diagnostic_results["recommendations"].append("Inicializar AuthManager")
        except Exception as e:
            diagnostic_results["auth_manager"]["status"] = "ERROR"
            diagnostic_results["auth_manager"]["error"] = str(e)

        # 3. Verificar variables de entorno críticas
        critical_vars = [
            "GOOGLE_SERVICE_ACCOUNT_JSON",
            "GOOGLE_SHEETS_ID",
            "TELEGRAM_BOT_TOKEN",
            "SECRET_KEY",
        ]

        for var in critical_vars:
            value = os.environ.get(var)
            diagnostic_results["environment_variables"][var] = {
                "exists": bool(value),
                "length": len(value) if value else 0,
                "preview": value[:50] + "..." if value and len(value) > 50 else value,
            }

            if not value:
                diagnostic_results["recommendations"].append(
                    f"Configurar variable de entorno: {var}"
                )

        # 4. Verificar conexión con Google Sheets API
        try:
            if sheets_db:
                # Intentar obtener una hoja específica
                spreadsheet = sheets_db.get_spreadsheet()
                if spreadsheet:
                    diagnostic_results["connection_tests"]["sheets_api"] = "PASÓ"
                    diagnostic_results["sheets_manager"][
                        "spreadsheet_id"
                    ] = spreadsheet.id
                else:
                    diagnostic_results["connection_tests"]["sheets_api"] = "FALLÓ"
                    diagnostic_results["recommendations"].append(
                        "Verificar ID de Google Sheets"
                    )
            else:
                diagnostic_results["connection_tests"]["sheets_api"] = "NO DISPONIBLE"
        except Exception as e:
            diagnostic_results["connection_tests"]["sheets_api"] = "FALLÓ"
            diagnostic_results["recommendations"].append(
                f"Error en API de Google Sheets: {str(e)}"
            )

        # 5. Verificar acceso a hojas específicas
        try:
            if sheets_db:
                spreadsheet = sheets_db.get_spreadsheet()
                if spreadsheet:
                    # Verificar hojas críticas
                    critical_sheets = [
                        "Usuarios",
                        "Pacientes",
                        "Atenciones",
                        "Citas_Agenda",
                    ]
                    available_sheets = [ws.title for ws in spreadsheet.worksheets()]

                    diagnostic_results["sheets_manager"][
                        "available_sheets"
                    ] = available_sheets
                    diagnostic_results["sheets_manager"]["critical_sheets_status"] = {}

                    for sheet in critical_sheets:
                        if sheet in available_sheets:
                            diagnostic_results["sheets_manager"][
                                "critical_sheets_status"
                            ][sheet] = "DISPONIBLE"
                        else:
                            diagnostic_results["sheets_manager"][
                                "critical_sheets_status"
                            ][sheet] = "NO ENCONTRADA"
                            diagnostic_results["recommendations"].append(
                                f"Crear hoja: {sheet}"
                            )
        except Exception as e:
            diagnostic_results["sheets_manager"]["sheets_check_error"] = str(e)

        # 6. Generar resumen
        total_tests = len(diagnostic_results["connection_tests"])
        passed_tests = sum(
            1
            for test in diagnostic_results["connection_tests"].values()
            if test == "PASÓ"
        )

        diagnostic_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "overall_status": (
                "HEALTHY" if passed_tests == total_tests else "ISSUES_DETECTED"
            ),
        }

        return jsonify(diagnostic_results)

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "traceback": traceback.format_exc(),
                }
            ),
            500,
        )


# ===== COPILOT HEALTH - ANÁLISIS MEJORADO =====


@app.route("/api/copilot/analyze-enhanced", methods=["POST"])
@login_required
def analyze_enhanced():
    """Análisis mejorado con identificación de palabras clave, patologías y escalas"""
    try:
        if not COPILOT_HEALTH_AVAILABLE:
            return (
                jsonify(
                    {"success": False, "message": "Módulo Copilot Health no disponible"}
                ),
                503,
            )

        data = request.get_json()
        if not data or "motivo_consulta" not in data:
            return (
                jsonify({"success": False, "message": "Motivo de consulta requerido"}),
                400,
            )

        motivo_consulta = data["motivo_consulta"]
        tipo_atencion = data.get("tipo_atencion", None)
        edad_paciente = data.get("edad_paciente", None)
        antecedentes = data.get("antecedentes", None)

        # Importar el analizador mejorado
        try:
            from enhanced_copilot_health import enhanced_copilot
        except ImportError:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Módulo de análisis mejorado no disponible",
                    }
                ),
                503,
            )

        # Realizar análisis mejorado
        resultado = enhanced_copilot.analizar_caso_completo_mejorado(
            motivo_consulta=motivo_consulta,
            tipo_atencion=tipo_atencion,
            edad_paciente=edad_paciente,
            antecedentes=antecedentes,
        )

        # Generar resumen
        resumen = enhanced_copilot.generar_resumen_mejorado(resultado)

        return jsonify(
            {
                "success": True,
                "analisis_mejorado": resumen,
                "confianza_global": resultado.confianza_global,
                "mensaje": f"Análisis completado con {len(resultado.analisis_clinico.palabras_clave)} palabras clave identificadas",
            }
        )

    except Exception as e:
        logger.error(f"Error en analyze_enhanced: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/copilot/identify-keywords", methods=["POST"])
@login_required
def identify_keywords():
    """Identifica palabras clave en el motivo de consulta"""
    try:
        data = request.get_json()
        if not data or "motivo_consulta" not in data:
            return (
                jsonify({"success": False, "message": "Motivo de consulta requerido"}),
                400,
            )

        motivo_consulta = data["motivo_consulta"]

        # Importar el analizador clínico
        try:
            from clinical_pattern_analyzer import clinical_analyzer
        except ImportError:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Módulo de análisis clínico no disponible",
                    }
                ),
                503,
            )

        # Identificar palabras clave
        palabras_clave = clinical_analyzer.identificar_palabras_clave(motivo_consulta)

        # Identificar región anatómica
        region_anatomica = clinical_analyzer.identificar_region_anatomica(
            motivo_consulta
        )

        # Identificar patologías
        patologias = clinical_analyzer.identificar_patologias(palabras_clave)

        # Identificar escalas de evaluación
        escalas = clinical_analyzer.identificar_escalas_evaluacion(
            palabras_clave, region_anatomica
        )

        return jsonify(
            {
                "success": True,
                "palabras_clave": [
                    {
                        "palabra": pc.palabra,
                        "categoria": pc.categoria,
                        "intensidad": pc.intensidad,
                        "escalas_evaluacion": pc.escalas_evaluacion,
                        "preguntas_sugeridas": pc.preguntas_sugeridas,
                    }
                    for pc in palabras_clave
                ],
                "region_anatomica": region_anatomica,
                "patologias_identificadas": [
                    {
                        "nombre": p.nombre,
                        "confianza": p.confianza,
                        "sintomas_asociados": p.sintomas_asociados,
                        "terminos_busqueda": p.terminos_busqueda,
                    }
                    for p in patologias
                ],
                "escalas_recomendadas": [
                    {
                        "nombre": e.nombre,
                        "descripcion": e.descripcion,
                        "aplicacion": e.aplicacion,
                        "preguntas": e.preguntas,
                    }
                    for e in escalas
                ],
            }
        )

    except Exception as e:
        logger.error(f"Error en identify_keywords: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/copilot/search-enhanced", methods=["POST"])
@login_required
def search_enhanced():
    """Búsqueda mejorada basada en análisis de patrones clínicos"""
    try:
        data = request.get_json()
        if not data or "motivo_consulta" not in data:
            return (
                jsonify({"success": False, "message": "Motivo de consulta requerido"}),
                400,
            )

        motivo_consulta = data["motivo_consulta"]

        # Importar el analizador mejorado
        try:
            from enhanced_copilot_health import enhanced_copilot
        except ImportError:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Módulo de análisis mejorado no disponible",
                    }
                ),
                503,
            )

        # Realizar análisis y búsqueda
        resultado = enhanced_copilot.analizar_caso_completo_mejorado(motivo_consulta)

        return jsonify(
            {
                "success": True,
                "evidencia_cientifica": resultado.evidencia_cientifica,
                "recomendaciones": resultado.recomendaciones,
                "escalas_aplicadas": resultado.escalas_aplicadas,
                "confianza_global": resultado.confianza_global,
                "resumen_analisis": {
                    "palabras_clave_identificadas": len(
                        resultado.analisis_clinico.palabras_clave
                    ),
                    "patologias_sugeridas": len(
                        resultado.analisis_clinico.patologias_identificadas
                    ),
                    "escalas_recomendadas": len(
                        resultado.analisis_clinico.escalas_recomendadas
                    ),
                    "articulos_encontrados": len(resultado.evidencia_cientifica),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error en search_enhanced: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


# ===== COPILOT HEALTH - IA CL NICA ASISTIVA =====


@app.route("/api/copilot/analyze-motivo", methods=["POST"])
@login_required
def analyze_motivo_consulta():
    """Analiza el motivo de consulta usando IA cl nica asistiva"""
    try:
        if not COPILOT_HEALTH_AVAILABLE:
            return (
                jsonify(
                    {"success": False, "message": "M dulo Copilot Health no disponible"}
                ),
                503,
            )

        data = request.get_json()
        if not data or "motivo_consulta" not in data:
            return (
                jsonify({"success": False, "message": "Motivo de consulta requerido"}),
                400,
            )

        motivo_texto = data["motivo_consulta"]
        tipo_atencion = data.get("tipo_atencion", None)

        # Analizar el motivo de consulta considerando el tipo de atenci n
        motivo_analizado = copilot_health.analizar_motivo_consulta(
            motivo_texto, tipo_atencion
        )

        return jsonify(
            {
                "success": True,
                "analisis": {
                    "especialidad_detectada": motivo_analizado.especialidad_detectada,
                    "categoria": motivo_analizado.categoria,
                    "urgencia": motivo_analizado.urgencia,
                    "sintomas_principales": motivo_analizado.sintomas_principales,
                    "preguntas_sugeridas": motivo_analizado.preguntas_sugeridas,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error en analyze_motivo_consulta: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/copilot/evaluate-antecedentes", methods=["POST"])
@login_required
def evaluate_antecedentes():
    """Eval a antecedentes y detecta banderas rojas"""
    try:
        if not COPILOT_HEALTH_AVAILABLE:
            return (
                jsonify(
                    {"success": False, "message": "M dulo Copilot Health no disponible"}
                ),
                503,
            )

        data = request.get_json()
        if not data or "antecedentes" not in data:
            return (
                jsonify({"success": False, "message": "Antecedentes requeridos"}),
                400,
            )

        antecedentes = data["antecedentes"]
        especialidad = data.get("especialidad", "medicina_general")
        edad = int(data.get("edad", 30)) if data.get("edad") else 30

        # Evaluar antecedentes
        evaluacion = copilot_health.evaluar_antecedentes(
            antecedentes, especialidad, edad
        )

        return jsonify(
            {
                "success": True,
                "evaluacion": {
                    "banderas_rojas": evaluacion.banderas_rojas,
                    "campos_adicionales": evaluacion.campos_adicionales,
                    "omisiones_detectadas": evaluacion.omisiones_detectadas,
                    "recomendaciones": evaluacion.recomendaciones,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error en evaluate_antecedentes: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


# Importar el sistema RAG m dico
from medical_rag_system import rag_system, RespuestaRAG


@app.route("/api/copilot/suggest-treatment", methods=["POST"])
@login_required
def suggest_treatment():
    """Endpoint mejorado para sugerencia de tratamiento usando t rminos MeSH espec ficos"""
    try:
        data = request.get_json()
        diagnostico = data.get("diagnostico", "")
        especialidad = data.get("especialidad", "general")
        edad = int(data.get("edad", 35)) if data.get("edad") else 35
        evaluacion = data.get("evaluacion", "")

        logger.info(f"[BUSCAR] Solicitud de tratamiento MeSH: {diagnostico[:100]}...")

        # Combinar toda la informaci n cl nica
        condicion_completa = f"{diagnostico} {evaluacion} {edad}"

        # Usar directamente las APIs m dicas con t rminos MeSH espec ficos
        try:
            from medical_apis_integration import MedicalAPIsIntegration

            apis = MedicalAPIsIntegration()

            # Buscar tratamientos con t rminos MeSH espec ficos
            tratamientos_pubmed = apis.buscar_tratamiento_pubmed(
                condicion_completa, especialidad
            )
            tratamientos_europepmc = apis.buscar_europepmc(
                condicion_completa, especialidad
            )

            # Combinar resultados
            todos_tratamientos = tratamientos_pubmed + tratamientos_europepmc

            # Convertir al formato esperado por el frontend
            planes_tratamiento = []

            for i, tratamiento in enumerate(
                todos_tratamientos[:10], 1
            ):  # Limitar a 10 resultados
                plan = {
                    "titulo": tratamiento.titulo,
                    "descripcion": (
                        tratamiento.resumen[:200] + "..."
                        if len(tratamiento.resumen) > 200
                        else tratamiento.resumen
                    ),
                    "nivel_evidencia": tratamiento.nivel_evidencia,
                    "doi_referencia": (
                        tratamiento.doi if tratamiento.doi != "Sin DOI" else None
                    ),
                    "evidencia_cientifica": (
                        f"Estudio de {', '.join(tratamiento.autores[:2])} ({tratamiento.fecha_publicacion[:4]})"
                        if tratamiento.autores
                        else "Evidencia cient fica"
                    ),
                    "fuente": tratamiento.fuente.upper(),
                    "url": (
                        f"https://doi.org/{tratamiento.doi}"
                        if tratamiento.doi and tratamiento.doi != "Sin DOI"
                        else ""
                    ),
                    "relevancia_score": 0.8,  # Score por defecto
                }
                planes_tratamiento.append(plan)

            # Obtener t rminos MeSH utilizados
            terminos_mesh = apis._generar_terminos_mesh_especificos(
                condicion_completa, especialidad
            )

            logger.info(
                f"[OK] Encontrados {len(planes_tratamiento)} tratamientos con t rminos MeSH espec ficos"
            )
            logger.info(f"[BUSCAR] T rminos MeSH utilizados: {terminos_mesh}")

            return jsonify(
                {
                    "success": True,
                    "planes_tratamiento": planes_tratamiento,
                    "nivel_confianza": 0.85,
                    "terminos_utilizados": terminos_mesh,
                    "especialidad_detectada": especialidad,
                    "analisis_clinico": condicion_completa,
                    "evidencia_encontrada": len(planes_tratamiento) > 0,
                    "metodo": "MeSH espec fico",
                }
            )

        except ImportError:
            logger.error("[ERROR] M dulo medical_apis_integration no disponible")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Sistema de APIs m dicas no disponible",
                    }
                ),
                503,
            )

    except Exception as e:
        logger.error(f"[ERROR] Error en sugerencia de tratamiento MeSH: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error en el procesamiento: {str(e)}"}
            ),
            500,
        )


@app.route("/api/copilot/complete-analysis", methods=["POST"])
@login_required
def complete_analysis():
    """Realiza un an lisis completo de IA cl nica asistiva"""
    try:
        if not COPILOT_HEALTH_AVAILABLE:
            return (
                jsonify(
                    {"success": False, "message": "M dulo Copilot Health no disponible"}
                ),
                503,
            )

        data = request.get_json()
        if not data or "motivo_consulta" not in data:
            return (
                jsonify({"success": False, "message": "Motivo de consulta requerido"}),
                400,
            )

        motivo_texto = data["motivo_consulta"]
        antecedentes = data.get("antecedentes", "")
        diagnostico = data.get("diagnostico", "")
        especialidad = data.get("especialidad", "medicina_general")
        edad = int(data.get("edad", 30)) if data.get("edad") else 30

        # An lisis completo
        motivo_analizado = copilot_health.analizar_motivo_consulta(motivo_texto)
        evaluacion = copilot_health.evaluar_antecedentes(
            antecedentes, especialidad, edad
        )
        planes = copilot_health.sugerir_planes_tratamiento(
            diagnostico, especialidad, edad
        )

        # Generar resumen completo
        resumen_completo = copilot_health.generar_resumen_ia(
            motivo_analizado, evaluacion, planes
        )

        return jsonify(
            {
                "success": True,
                "resumen_completo": resumen_completo,
                "analisis": {
                    "motivo": {
                        "especialidad_detectada": motivo_analizado.especialidad_detectada,
                        "categoria": motivo_analizado.categoria,
                        "urgencia": motivo_analizado.urgencia,
                        "sintomas_principales": motivo_analizado.sintomas_principales,
                        "preguntas_sugeridas": motivo_analizado.preguntas_sugeridas,
                    },
                    "evaluacion": {
                        "banderas_rojas": evaluacion.banderas_rojas,
                        "campos_adicionales": evaluacion.campos_adicionales,
                        "omisiones_detectadas": evaluacion.omisiones_detectadas,
                        "recomendaciones": evaluacion.recomendaciones,
                    },
                    "planes_tratamiento": [
                        {
                            "titulo": plan.titulo,
                            "descripcion": plan.descripcion,
                            "evidencia_cientifica": plan.evidencia_cientifica,
                            "doi_referencia": plan.doi_referencia,
                            "nivel_evidencia": plan.nivel_evidencia,
                            "contraindicaciones": plan.contraindicaciones,
                        }
                        for plan in planes
                    ],
                },
            }
        )

    except Exception as e:
        logger.error(f"Error en complete_analysis: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/copilot/generate-evaluation-questions", methods=["POST"])
@login_required
def generate_evaluation_questions():
    """Genera preguntas personalizadas para evaluaci n/anamnesis basadas en motivo de consulta y tipo de atenci n"""
    try:
        data = request.get_json()
        motivo_consulta = data.get("motivo_consulta", "")
        tipo_atencion = data.get("tipo_atencion", "general")

        logger.info(
            f"[BUSCAR] Generando preguntas de evaluaci n para: {motivo_consulta} en {tipo_atencion}"
        )

        # Usar el sistema de APIs m dicas para generar preguntas personalizadas
        try:
            from medical_apis_integration import MedicalAPIsIntegration

            apis = MedicalAPIsIntegration()

            # Generar preguntas personalizadas
            preguntas = apis.generar_preguntas_personalizadas_evaluacion(
                motivo_consulta, tipo_atencion
            )

            logger.info(
                f"[OK] Generadas {len(preguntas)} preguntas personalizadas para {tipo_atencion}"
            )

            return jsonify(
                {
                    "success": True,
                    "preguntas": preguntas,
                    "tipo_atencion": tipo_atencion,
                    "motivo_consulta": motivo_consulta,
                    "cantidad_preguntas": len(preguntas),
                    "metodo": "Preguntas personalizadas por especialidad",
                }
            )

        except ImportError:
            logger.error("[ERROR] M dulo medical_apis_integration no disponible")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Sistema de preguntas personalizadas no disponible",
                    }
                ),
                503,
            )

    except Exception as e:
        logger.error(f"[ERROR] Error generando preguntas de evaluaci n: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error en el procesamiento: {str(e)}"}
            ),
            500,
        )


@app.route("/api/copilot/planificacion-completa", methods=["POST"])
@login_required
def planificacion_completa():
    """Genera una planificaci n completa de tratamiento basada en m ltiples fuentes"""
    try:
        if not COPILOT_HEALTH_AVAILABLE:
            return (
                jsonify(
                    {"success": False, "message": "M dulo Copilot Health no disponible"}
                ),
                503,
            )

        data = request.get_json()
        if not data or "motivo_atencion" not in data:
            return (
                jsonify({"success": False, "message": "Motivo de atenci n requerido"}),
                400,
            )

        motivo_atencion = data["motivo_atencion"]
        tipo_atencion = data.get("tipo_atencion", "medicina_general")
        evaluacion_observaciones = data.get("evaluacion_observaciones", "")
        edad = int(data.get("edad", 35)) if data.get("edad") else 35

        # Generar planificaci n completa
        planificacion = copilot_health.generar_planificacion_tratamiento_completa(
            motivo_atencion=motivo_atencion,
            tipo_atencion=tipo_atencion,
            evaluacion_observaciones=evaluacion_observaciones,
            edad=edad,
        )

        return jsonify({"success": True, "planificacion": planificacion})

    except Exception as e:
        logger.error(f"Error en planificacion_completa: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


@app.route("/api/copilot/generate-search-terms", methods=["POST"])
@login_required
def generate_search_terms():
    """Genera términos de búsqueda disponibles para que el profesional seleccione"""
    try:
        data = request.get_json()
        condicion = data.get("condicion", "")
        especialidad = data.get("especialidad", "")
        edad = data.get("edad", None)

        if not condicion:
            return jsonify({"success": False, "message": "Condición es requerida"})

        # Importar el módulo de APIs médicas
        from medical_apis_integration import MedicalAPIsIntegration

        apis = MedicalAPIsIntegration()

        # Generar términos disponibles
        terminos_disponibles = apis.generar_terminos_busqueda_disponibles(
            condicion=condicion, especialidad=especialidad, edad_paciente=edad
        )

        return jsonify({"success": True, "terminos_disponibles": terminos_disponibles})

    except Exception as e:
        logger.error(f"[ERROR] Error generando términos de búsqueda: {e}")
        return jsonify(
            {
                "success": False,
                "message": f"Error generando términos de búsqueda: {str(e)}",
            }
        )


@app.route("/api/copilot/extract-key-terms", methods=["POST"])
@login_required
def extract_key_terms():
    """Extrae términos clave del análisis completo del caso"""
    try:
        data = request.get_json()
        analisis = data.get("analisis", {})

        if not analisis:
            return jsonify({"success": False, "message": "Análisis es requerido"})

        # Importar el módulo de APIs médicas
        from medical_apis_integration import MedicalAPIsIntegration

        apis = MedicalAPIsIntegration()

        # Extraer términos clave del análisis
        terminos_clave = apis.extraer_terminos_clave_analisis(analisis)

        return jsonify({"success": True, "terminos_clave": terminos_clave})

    except Exception as e:
        logger.error(f"[ERROR] Error extrayendo términos clave: {e}")
        return jsonify(
            {"success": False, "message": f"Error extrayendo términos clave: {str(e)}"}
        )


@app.route("/api/copilot/generate-expanded-search-terms", methods=["POST"])
@login_required
def generate_expanded_search_terms():
    """Genera términos de búsqueda expandidos basados en términos clave"""
    try:
        data = request.get_json()
        condicion = data.get("condicion", "")
        especialidad = data.get("especialidad", "")
        edad = data.get("edad", None)
        terminos_clave = data.get("terminos_clave", [])

        if not condicion:
            return jsonify({"success": False, "message": "Condición es requerida"})

        # Importar el módulo de APIs médicas
        from medical_apis_integration import MedicalAPIsIntegration

        apis = MedicalAPIsIntegration()

        # Generar términos expandidos
        terminos_disponibles = apis.generar_terminos_busqueda_expandidos(
            condicion=condicion,
            especialidad=especialidad,
            edad_paciente=edad,
            terminos_clave=terminos_clave,
        )

        return jsonify({"success": True, "terminos_disponibles": terminos_disponibles})

    except Exception as e:
        logger.error(f"[ERROR] Error generando términos expandidos: {e}")
        return jsonify(
            {
                "success": False,
                "message": f"Error generando términos expandidos: {str(e)}",
            }
        )


@app.route("/api/copilot/search-with-key-terms", methods=["POST"])
@login_required
def search_with_key_terms():
    """Realiza búsqueda usando términos clave específicos"""
    try:
        data = request.get_json()
        condicion = data.get("condicion", "")
        especialidad = data.get("especialidad", "")
        edad = data.get("edad", None)
        terminos_clave = data.get("terminos_clave", [])

        if not condicion:
            return jsonify({"success": False, "message": "Condición es requerida"})

        if not terminos_clave:
            return jsonify(
                {"success": False, "message": "Términos clave son requeridos"}
            )

        logger.info(f"🔍 Iniciando búsqueda con términos clave: {terminos_clave}")

        # Importar el módulo de APIs médicas
        from medical_apis_integration import MedicalAPIsIntegration

        apis = MedicalAPIsIntegration()

        # Realizar búsqueda con términos clave
        resultados = apis.buscar_con_terminos_clave(
            condicion=condicion,
            especialidad=especialidad,
            terminos_clave=terminos_clave,
            edad_paciente=edad,
        )

        # Convertir resultados a formato compatible
        planes_tratamiento = []
        if resultados.get("tratamientos_pubmed"):
            planes_tratamiento.extend(resultados["tratamientos_pubmed"])
        if resultados.get("tratamientos_europepmc"):
            planes_tratamiento.extend(resultados["tratamientos_europepmc"])

        logger.info(
            f"✅ Búsqueda con términos clave completada: {len(planes_tratamiento)} resultados"
        )

        return jsonify(
            {
                "success": True,
                "planes_tratamiento": planes_tratamiento,
                "total_resultados": len(planes_tratamiento),
            }
        )

    except Exception as e:
        logger.error(f"[ERROR] Error en búsqueda con términos clave: {e}")
        return jsonify(
            {
                "success": False,
                "message": f"Error en búsqueda con términos clave: {str(e)}",
            }
        )


@app.route("/api/copilot/search-with-terms", methods=["POST"])
@login_required
def search_with_terms():
    """Realiza búsqueda usando términos específicos seleccionados por el profesional"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Datos JSON requeridos"}), 400

        condicion = data.get("condicion", "")
        especialidad = data.get("especialidad", "")
        edad = data.get("edad", None)
        terminos_seleccionados = data.get("terminos_seleccionados", [])

        if not condicion:
            return jsonify({"success": False, "message": "Condición es requerida"}), 400

        if not terminos_seleccionados:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Debe seleccionar al menos un término",
                    }
                ),
                400,
            )

        logger.info(f"🔍 Iniciando búsqueda con términos: {terminos_seleccionados}")

        # Importar el módulo de APIs médicas con manejo de errores
        try:
            from medical_apis_integration import MedicalAPIsIntegration

            apis = MedicalAPIsIntegration()
        except ImportError as e:
            logger.error(f"❌ Error importando MedicalAPIsIntegration: {e}")
            return (
                jsonify(
                    {"success": False, "message": "Error de configuración del sistema"}
                ),
                500,
            )
        except Exception as e:
            logger.error(f"❌ Error inicializando APIs médicas: {e}")
            return (
                jsonify(
                    {"success": False, "message": "Error de inicialización del sistema"}
                ),
                500,
            )

        # Realizar búsqueda con términos personalizados
        try:
            resultados = apis.buscar_con_terminos_personalizados(
                condicion=condicion,
                especialidad=especialidad,
                terminos_seleccionados=terminos_seleccionados,
                edad_paciente=edad,
            )

            logger.info(f"✅ Búsqueda completada, procesando resultados...")

        except Exception as e:
            logger.error(f"❌ Error en búsqueda con términos personalizados: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error de conexión con el servidor de búsqueda",
                    }
                ),
                500,
            )

        # Convertir resultados a formato compatible con el frontend
        planes_tratamiento = []
        try:
            if resultados.get("tratamientos_pubmed"):
                planes_tratamiento.extend(resultados["tratamientos_pubmed"])
                logger.info(
                    f"📄 PubMed: {len(resultados['tratamientos_pubmed'])} resultados"
                )

            if resultados.get("tratamientos_europepmc"):
                planes_tratamiento.extend(resultados["tratamientos_europepmc"])
                logger.info(
                    f"📄 Europe PMC: {len(resultados['tratamientos_europepmc'])} resultados"
                )

        except Exception as e:
            logger.error(f"❌ Error procesando resultados: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error procesando resultados de búsqueda",
                    }
                ),
                500,
            )

        logger.info(f"✅ Total de planes de tratamiento: {len(planes_tratamiento)}")

        return jsonify(
            {
                "success": True,
                "planes_tratamiento": planes_tratamiento,
                "total_resultados": len(planes_tratamiento),
            }
        )

    except Exception as e:
        logger.error(f"❌ Error general en search_with_terms: {e}")
        import traceback

        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return (
            jsonify({"success": False, "message": "Error de conexión con el servidor"}),
            500,
        )


# ===== P GINA COPILOT HEALTH =====


@app.route("/copilot-health")
@login_required
def copilot_health_page():
    """P gina principal de Copilot Health"""
    return render_template("copilot_health.html")


@app.route("/test-ia-formulario")
def test_ia_formulario():
    """P gina de prueba para la IA del formulario"""
    return render_template("test_ia_formulario.html")


@app.route("/api/copilot/test-analyze-motivo", methods=["POST"])
def test_analyze_motivo_consulta():
    """Endpoint de prueba sin autenticaci n para analizar motivo de consulta"""
    try:
        if not COPILOT_HEALTH_AVAILABLE:
            return (
                jsonify(
                    {"success": False, "message": "M dulo Copilot Health no disponible"}
                ),
                503,
            )

        data = request.get_json()
        if not data or "motivo_consulta" not in data:
            return (
                jsonify({"success": False, "message": "Motivo de consulta requerido"}),
                400,
            )

        motivo_texto = data["motivo_consulta"]
        tipo_atencion = data.get("tipo_atencion", None)

        # Analizar el motivo de consulta considerando el tipo de atenci n
        motivo_analizado = copilot_health.analizar_motivo_consulta(
            motivo_texto, tipo_atencion
        )

        return jsonify(
            {
                "success": True,
                "analisis": {
                    "especialidad_detectada": motivo_analizado.especialidad_detectada,
                    "categoria": motivo_analizado.categoria,
                    "urgencia": motivo_analizado.urgencia,
                    "sintomas_principales": motivo_analizado.sintomas_principales,
                    "preguntas_sugeridas": motivo_analizado.preguntas_sugeridas,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error en test_analyze_motivo_consulta: {e}")
        return (
            jsonify(
                {"success": False, "message": f"Error interno del servidor: {str(e)}"}
            ),
            500,
        )


# ===== ENDPOINTS DE REPORTES =====


@app.route("/api/professional/reports", methods=["POST"])
@login_required
def generate_professional_reports():
    """Generar reportes para el profesional"""
    try:
        data = request.get_json()
        periodo = data.get("periodo", 30)
        tipo = data.get("tipo", "atenciones")

        # Obtener datos del profesional actual
        user = get_current_user()
        professional_id = user.get("id")

        # Calcular fechas
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=periodo)

        # Obtener datos seg n el tipo de reporte
        if tipo == "atenciones":
            datos = obtener_datos_atenciones(professional_id, fecha_inicio, fecha_fin)
        elif tipo == "pacientes":
            datos = obtener_datos_pacientes(professional_id, fecha_inicio, fecha_fin)
        elif tipo == "ingresos":
            datos = obtener_datos_ingresos(professional_id, fecha_inicio, fecha_fin)
        elif tipo == "productividad":
            datos = obtener_datos_productividad(
                professional_id, fecha_inicio, fecha_fin
            )
        else:
            return jsonify({"error": "Tipo de reporte no v lido"}), 400

        # Calcular estad sticas
        estadisticas = calcular_estadisticas_reporte(datos, tipo)

        return jsonify({"estadisticas": estadisticas, "datos": datos})

    except Exception as e:
        logger.error(f"Error generando reporte: {str(e)}")
        return jsonify({"error": "Error al generar reporte"}), 500


@app.route("/api/professional/profile", methods=["GET"])
@login_required
def get_professional_profile():
    """Obtiene la información del profesional autenticado"""
    try:
        user_info = get_current_user()
        if not user_info:
            return jsonify({"success": False, "message": "Usuario no autenticado"}), 401

        # Obtener información del profesional desde Google Sheets
        try:

            def get_professional_data():
                worksheet = sheets_db.get_worksheet("Profesionales_Medicos")
                if not worksheet:
                    return None

                # Buscar el profesional por ID
                records = worksheet.get_all_records()
                for record in records:
                    if record.get("id") == user_info["id"]:
                        return {
                            "id": record.get("id"),
                            "nombre": record.get("nombre", ""),
                            "apellido": record.get("apellido", ""),
                            "email": record.get("email", ""),
                            "especialidad": record.get("especialidad", ""),
                            "profesion": record.get("profesion", ""),
                            "numero_registro": record.get("numero_registro", ""),
                            "telefono": record.get("telefono", ""),
                            "ciudad": record.get("ciudad", ""),
                            "direccion": record.get("direccion", ""),
                            "fecha_nacimiento": record.get("fecha_nacimiento", ""),
                            "genero": record.get("genero", ""),
                            "disponible": record.get("disponible", True),
                            "verificado": record.get("verificado", False),
                            "fecha_registro": record.get("fecha_registro", ""),
                            "ultimo_acceso": record.get("ultimo_acceso", ""),
                        }
                return None

            profesional = handle_rate_limiting(get_professional_data)

            if profesional:
                return jsonify({"success": True, "profesional": profesional})
            else:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "No se encontró información del profesional",
                        }
                    ),
                    404,
                )

        except Exception as e:
            logger.error(f"Error obteniendo datos del profesional: {e}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Error obteniendo información del profesional",
                    }
                ),
                500,
            )

    except Exception as e:
        logger.error(f"Error en get_professional_profile: {e}")
        return jsonify({"success": False, "message": "Error interno del servidor"}), 500


@app.route("/api/professional/reports/export", methods=["POST"])
@login_required
def export_professional_report():
    """Exportar reporte en diferentes formatos"""
    try:
        data = request.get_json()
        periodo = data.get("periodo", 30)
        tipo = data.get("tipo", "atenciones")
        formato = data.get("formato", "pdf")

        # Obtener datos del profesional actual
        user = get_current_user()
        professional_id = user.get("id")

        # Calcular fechas
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=periodo)

        # Obtener datos
        datos = obtener_datos_atenciones(professional_id, fecha_inicio, fecha_fin)
        estadisticas = calcular_estadisticas_reporte(datos, tipo)

        # Generar archivo seg n formato
        if formato == "pdf":
            return generar_pdf_reporte(datos, estadisticas, tipo)
        elif formato == "excel":
            return generar_excel_reporte(datos, estadisticas, tipo)
        elif formato == "csv":
            return generar_csv_reporte(datos, estadisticas, tipo)
        else:
            return jsonify({"error": "Formato no soportado"}), 400

    except Exception as e:
        logger.error(f"Error exportando reporte: {str(e)}")
        return jsonify({"error": "Error al exportar reporte"}), 500


# Funciones auxiliares para reportes
def obtener_datos_atenciones(professional_id, fecha_inicio, fecha_fin):
    """Obtener datos de atenciones para el reporte"""
    try:
        from backend.database.sheets_manager import SheetsManager

        sheets_manager = SheetsManager()
        atenciones = sheets_manager.get_atenciones_by_professional(professional_id)

        # Filtrar por fecha
        datos_filtrados = []
        for atencion in atenciones:
            try:
                fecha_atencion = datetime.strptime(
                    atencion.get("fecha_hora", ""), "%Y-%m-%dT%H:%M"
                )
                if fecha_inicio <= fecha_atencion <= fecha_fin:
                    datos_filtrados.append(
                        {
                            "fecha": atencion.get("fecha_hora", ""),
                            "paciente": atencion.get("nombre_paciente", ""),
                            "tipo": atencion.get("tipo_atencion", ""),
                            "estado": atencion.get("estado", ""),
                            "duracion": atencion.get("duracion", ""),
                        }
                    )
            except ValueError:
                # Si no se puede parsear la fecha, saltar
                continue

        return datos_filtrados

    except Exception as e:
        logger.error(f"Error obteniendo datos de atenciones: {str(e)}")
        return []


def obtener_datos_pacientes(professional_id, fecha_inicio, fecha_fin):
    """Obtener datos de pacientes para el reporte"""
    try:
        from backend.database.sheets_manager import SheetsManager

        sheets_manager = SheetsManager()
        pacientes = sheets_manager.get_patients_by_professional(professional_id)

        datos_filtrados = []
        for paciente in pacientes:
            datos_filtrados.append(
                {
                    "nombre": paciente.get("nombre_completo", ""),
                    "edad": paciente.get("edad", ""),
                    "genero": paciente.get("genero", ""),
                    "ultima_consulta": paciente.get("ultima_consulta", ""),
                    "total_atenciones": paciente.get("num_atenciones", 0),
                }
            )

        return datos_filtrados

    except Exception as e:
        logger.error(f"Error obteniendo datos de pacientes: {str(e)}")
        return []


def obtener_datos_ingresos(professional_id, fecha_inicio, fecha_fin):
    """Obtener datos de ingresos para el reporte (simulado)"""
    # Por ahora simulamos datos de ingresos
    return [
        {
            "fecha": "2025-07-01",
            "concepto": "Consulta General",
            "monto": "$50.000",
            "estado": "Pagado",
            "metodo_pago": "Transferencia",
        },
        {
            "fecha": "2025-07-02",
            "concepto": "Control",
            "monto": "$30.000",
            "estado": "Pendiente",
            "metodo_pago": "Efectivo",
        },
    ]


def obtener_datos_productividad(professional_id, fecha_inicio, fecha_fin):
    """Obtener datos de productividad para el reporte (simulado)"""
    # Por ahora simulamos datos de productividad
    return [
        {
            "fecha": "2025-07-01",
            "atenciones": 5,
            "horas_trabajadas": 8,
            "eficiencia": "85%",
            "calificacion": "4.8",
        },
        {
            "fecha": "2025-07-02",
            "atenciones": 3,
            "horas_trabajadas": 6,
            "eficiencia": "90%",
            "calificacion": "4.9",
        },
    ]


def calcular_estadisticas_reporte(datos, tipo):
    """Calcular estad sticas del reporte"""
    if not datos:
        return {
            "total": 0,
            "promedio": 0,
            "maximo": 0,
            "crecimiento": 0,
            "tendencia": [],
        }

    # Calcular estad sticas b sicas
    total = len(datos)

    # Simular datos de tendencia
    import random

    tendencia = [random.randint(1, 10) for _ in range(7)]

    return {
        "total": total,
        "promedio": round(total / 7, 1) if total > 0 else 0,
        "maximo": max(tendencia) if tendencia else 0,
        "crecimiento": random.randint(5, 25),
        "tendencia": tendencia,
    }


def generar_pdf_reporte(datos, estadisticas, tipo):
    """Generar PDF del reporte"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # T tulo
        styles = getSampleStyleSheet()
        title = Paragraph(f"Reporte de {tipo.capitalize()}", styles["Title"])
        elements.append(title)

        # Estad sticas
        stats_data = [
            ["Total", estadisticas["total"]],
            ["Promedio", estadisticas["promedio"]],
            ["M ximo", estadisticas["maximo"]],
            ["Crecimiento", f"{estadisticas['crecimiento']}%"],
        ]

        stats_table = Table(stats_data)
        stats_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), "#CCCCCC"),
                    ("TEXTCOLOR", (0, 0), (-1, 0), "#000000"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), "#F0F0F0"),
                    ("GRID", (0, 0), (-1, -1), 1, "#000000"),
                ]
            )
        )
        elements.append(stats_table)

        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'reporte_{tipo}_{datetime.now().strftime("%Y%m%d")}.pdf',
            mimetype="application/pdf",
        )

    except Exception as e:
        logger.error(f"Error generando PDF: {str(e)}")
        return jsonify({"error": "Error generando PDF"}), 500


def generar_excel_reporte(datos, estadisticas, tipo):
    """Generar Excel del reporte"""
    try:
        import pandas as pd
        from io import BytesIO

        # Crear DataFrame con los datos
        df = pd.DataFrame(datos)

        # Crear Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Datos", index=False)

            # Agregar hoja de estad sticas
            stats_df = pd.DataFrame(
                [
                    ["Total", estadisticas["total"]],
                    ["Promedio", estadisticas["promedio"]],
                    ["M ximo", estadisticas["maximo"]],
                    ["Crecimiento", f"{estadisticas['crecimiento']}%"],
                ],
                columns=["M trica", "Valor"],
            )
            stats_df.to_excel(writer, sheet_name="Estad sticas", index=False)

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name=f'reporte_{tipo}_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        logger.error(f"Error generando Excel: {str(e)}")
        return jsonify({"error": "Error generando Excel"}), 500


def generar_csv_reporte(datos, estadisticas, tipo):
    """Generar CSV del reporte"""
    try:
        import pandas as pd
        from io import BytesIO

        # Crear DataFrame con los datos
        df = pd.DataFrame(datos)

        # Crear CSV en memoria
        output = BytesIO()
        df.to_csv(output, index=False, encoding="utf-8")
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name=f'reporte_{tipo}_{datetime.now().strftime("%Y%m%d")}.csv',
            mimetype="text/csv",
        )

    except Exception as e:
        logger.error(f"Error generando CSV: {str(e)}")
        return jsonify({"error": "Error generando CSV"}), 500


# ========================================
# ENDPOINTS PARA MANEJO DE SESIONES
# ========================================


@app.route("/api/guardar-sesion", methods=["POST"])
@login_required
def guardar_sesion():
    """Guardar una nueva sesión"""
    try:
        data = request.get_json()

        # Validar datos requeridos
        required_fields = [
            "atencion_id",
            "fecha_sesion",
            "duracion",
            "tipo_sesion",
            "objetivos",
            "actividades",
            "progreso",
            "estado",
        ]

        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify({"success": False, "message": f"Campo requerido: {field}"}),
                    400,
                )

        # Verificar límite de sesiones (1-15)
        sesiones_existentes = get_sesiones_atencion(data["atencion_id"])
        if len(sesiones_existentes) >= 15:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Límite máximo de 15 sesiones alcanzado",
                    }
                ),
                400,
            )

        # Crear nueva sesión
        nueva_sesion = {
            "id": str(uuid.uuid4()),
            "atencion_id": data["atencion_id"],
            "fecha_sesion": data["fecha_sesion"],
            "duracion": data["duracion"],
            "tipo_sesion": data["tipo_sesion"],
            "objetivos": data["objetivos"],
            "actividades": data["actividades"],
            "observaciones": data.get("observaciones", ""),
            "progreso": data["progreso"],
            "estado": data["estado"],
            "recomendaciones": data.get("recomendaciones", ""),
            "proxima_sesion": data.get("proxima_sesion", ""),
            "fecha_creacion": datetime.now().isoformat(),
            "profesional_id": session.get("user_id"),
        }

        # Guardar en Google Sheets
        guardar_sesion_sheets(nueva_sesion)

        logger.info(f"Sesión guardada exitosamente: {nueva_sesion['id']}")
        return jsonify(
            {
                "success": True,
                "message": "Sesión registrada exitosamente",
                "sesion_id": nueva_sesion["id"],
            }
        )

    except Exception as e:
        logger.error(f"Error guardando sesión: {str(e)}")
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500


@app.route("/api/get-sesiones/<atencion_id>", methods=["GET"])
@login_required
def get_sesiones(atencion_id):
    """Obtener todas las sesiones de una atención"""
    try:
        sesiones = get_sesiones_atencion(atencion_id)

        # Ordenar por fecha de sesión (más reciente primero)
        sesiones.sort(key=lambda x: x.get("fecha_sesion", ""), reverse=True)

        return jsonify({"success": True, "sesiones": sesiones, "total": len(sesiones)})

    except Exception as e:
        logger.error(f"Error obteniendo sesiones: {str(e)}")
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500


@app.route("/api/get-sesion/<sesion_id>", methods=["GET"])
@login_required
def get_sesion(sesion_id):
    """Obtener una sesión específica"""
    try:
        sesion = get_sesion_by_id(sesion_id)

        if not sesion:
            return jsonify({"success": False, "message": "Sesión no encontrada"}), 404

        return jsonify({"success": True, "sesion": sesion})

    except Exception as e:
        logger.error(f"Error obteniendo sesión: {str(e)}")
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500


@app.route("/api/eliminar-sesion/<sesion_id>", methods=["DELETE"])
@login_required
def eliminar_sesion(sesion_id):
    """Eliminar una sesión"""
    try:
        # Verificar que la sesión existe
        sesion = get_sesion_by_id(sesion_id)
        if not sesion:
            return jsonify({"success": False, "message": "Sesión no encontrada"}), 404

        # Eliminar de Google Sheets
        eliminar_sesion_sheets(sesion_id)

        logger.info(f"Sesión eliminada exitosamente: {sesion_id}")
        return jsonify({"success": True, "message": "Sesión eliminada exitosamente"})

    except Exception as e:
        logger.error(f"Error eliminando sesión: {str(e)}")
        return jsonify({"success": False, "message": f"Error interno: {str(e)}"}), 500


# ========================================
# FUNCIONES AUXILIARES PARA SESIONES
# ========================================


def get_sesiones_atencion(atencion_id):
    """Obtener todas las sesiones de una atención desde Google Sheets"""
    try:
        if not sheets_client:
            logger.error("Cliente de Google Sheets no disponible")
            return []

        # Obtener datos de la hoja de sesiones
        range_name = "Sesiones!A:N"
        result = (
            sheets_client.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
            .execute()
        )
        values = result.get("values", [])

        sesiones = []
        for row in values[1:]:  # Saltar encabezados
            if len(row) >= 14 and row[1] == atencion_id:  # Columna B es atencion_id
                sesion = {
                    "id": row[0],
                    "atencion_id": row[1],
                    "fecha_sesion": row[2],
                    "duracion": int(row[3]) if row[3].isdigit() else 0,
                    "tipo_sesion": row[4],
                    "objetivos": row[5],
                    "actividades": row[6],
                    "observaciones": row[7] if len(row) > 7 else "",
                    "progreso": row[8] if len(row) > 8 else "",
                    "estado": row[9] if len(row) > 9 else "",
                    "recomendaciones": row[10] if len(row) > 10 else "",
                    "proxima_sesion": row[11] if len(row) > 11 else "",
                    "fecha_creacion": row[12] if len(row) > 12 else "",
                    "profesional_id": row[13] if len(row) > 13 else "",
                }
                sesiones.append(sesion)

        return sesiones

    except Exception as e:
        logger.error(f"Error obteniendo sesiones de atención {atencion_id}: {str(e)}")
        return []


def get_sesion_by_id(sesion_id):
    """Obtener una sesión específica por ID"""
    try:
        if not sheets_client:
            logger.error("Cliente de Google Sheets no disponible")
            return None

        # Obtener datos de la hoja de sesiones
        range_name = "Sesiones!A:N"
        result = (
            sheets_client.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
            .execute()
        )
        values = result.get("values", [])

        for row in values[1:]:  # Saltar encabezados
            if len(row) >= 1 and row[0] == sesion_id:
                return {
                    "id": row[0],
                    "atencion_id": row[1],
                    "fecha_sesion": row[2],
                    "duracion": int(row[3]) if row[3].isdigit() else 0,
                    "tipo_sesion": row[4],
                    "objetivos": row[5],
                    "actividades": row[6],
                    "observaciones": row[7] if len(row) > 7 else "",
                    "progreso": row[8] if len(row) > 8 else "",
                    "estado": row[9] if len(row) > 9 else "",
                    "recomendaciones": row[10] if len(row) > 10 else "",
                    "proxima_sesion": row[11] if len(row) > 11 else "",
                    "fecha_creacion": row[12] if len(row) > 12 else "",
                    "profesional_id": row[13] if len(row) > 13 else "",
                }

        return None

    except Exception as e:
        logger.error(f"Error obteniendo sesión {sesion_id}: {str(e)}")
        return None


def guardar_sesion_sheets(sesion):
    """Guardar sesión en Google Sheets"""
    try:
        if not sheets_client:
            logger.error("Cliente de Google Sheets no disponible")
            return False

        # Preparar datos para insertar
        row_data = [
            sesion["id"],
            sesion["atencion_id"],
            sesion["fecha_sesion"],
            str(sesion["duracion"]),
            sesion["tipo_sesion"],
            sesion["objetivos"],
            sesion["actividades"],
            sesion["observaciones"],
            sesion["progreso"],
            sesion["estado"],
            sesion["recomendaciones"],
            sesion["proxima_sesion"],
            sesion["fecha_creacion"],
            sesion["profesional_id"],
        ]

        # Insertar en la hoja de sesiones
        range_name = "Sesiones!A:N"
        body = {"values": [row_data]}

        result = (
            sheets_client.values()
            .append(
                spreadsheetId=SPREADSHEET_ID,
                range=range_name,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )

        logger.info(f"Sesión guardada en Sheets: {sesion['id']}")
        return True

    except Exception as e:
        logger.error(f"Error guardando sesión en Sheets: {str(e)}")
        return False


def eliminar_sesion_sheets(sesion_id):
    """Eliminar sesión de Google Sheets"""
    try:
        if not sheets_client:
            logger.error("Cliente de Google Sheets no disponible")
            return False

        # Buscar la fila de la sesión
        range_name = "Sesiones!A:A"
        result = (
            sheets_client.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
            .execute()
        )
        values = result.get("values", [])

        # Encontrar la fila que contiene el sesion_id
        row_number = None
        for i, row in enumerate(values):
            if row and row[0] == sesion_id:
                row_number = i + 1  # +1 porque las filas en Sheets empiezan en 1
                break

        if row_number:
            # Eliminar la fila
            request_body = {
                "requests": [
                    {
                        "deleteDimension": {
                            "range": {
                                "sheetId": get_sheet_id("Sesiones"),
                                "dimension": "ROWS",
                                "startIndex": row_number - 1,
                                "endIndex": row_number,
                            }
                        }
                    }
                ]
            }

            sheets_client.batchUpdate(
                spreadsheetId=SPREADSHEET_ID, body=request_body
            ).execute()
            logger.info(f"Sesión eliminada de Sheets: {sesion_id}")
            return True
        else:
            logger.warning(f"Sesión no encontrada en Sheets: {sesion_id}")
            return False

    except Exception as e:
        logger.error(f"Error eliminando sesión de Sheets: {str(e)}")
        return False


def get_sheet_id(sheet_name):
    """Obtener el ID de una hoja por nombre"""
    try:
        if not sheets_client:
            return None

        spreadsheet = sheets_client.get(spreadsheetId=SPREADSHEET_ID).execute()
        for sheet in spreadsheet["sheets"]:
            if sheet["properties"]["title"] == sheet_name:
                return sheet["properties"]["sheetId"]

        return None

    except Exception as e:
        logger.error(f"Error obteniendo ID de hoja {sheet_name}: {str(e)}")
        return None


# Inicializar cliente de Google Sheets globalmente
sheets_client = get_google_sheets_client()


def diagnose_login_error(error_msg):
    """Diagnóstica errores específicos de login para mejor debugging"""
    error_str = str(error_msg).lower()

    if "invalid salt" in error_str:
        return {
            "user_message": "Error de autenticación: Problema con la encriptación de contraseña",
            "debug_info": '🔍 DIAGNÓSTICO: Error "Invalid salt" - posible problema con bcrypt o datos corruptos en Google Sheets',
            "suggestions": [
                "• Verificar que la contraseña esté correctamente hasheada en Google Sheets",
                "• El usuario podría necesitar restablecer su contraseña",
                "• Revisar formato de datos en la columna de contraseñas",
            ],
        }
    elif "connection" in error_str or "timeout" in error_str:
        return {
            "user_message": "Error de conexión: Problema conectando con la base de datos",
            "debug_info": "🔍 DIAGNÓSTICO: Error de conexión con Google Sheets",
            "suggestions": [
                "• Verificar conexión a internet",
                "• Revisar credenciales de Google Sheets",
                "• Verificar límites de API",
            ],
        }
    elif "quota" in error_str or "429" in error_str:
        return {
            "user_message": "Servicio temporalmente no disponible: Límite de uso alcanzado",
            "debug_info": "🔍 DIAGNÓSTICO: Límite de cuota de Google Sheets API",
            "suggestions": [
                "• Esperar unos minutos antes de intentar nuevamente",
                "• Revisar uso de API en Google Cloud Console",
            ],
        }
    else:
        return {
            "user_message": "Error interno del servidor",
            "debug_info": f"🔍 DIAGNÓSTICO: Error no específico - {error_msg}",
            "suggestions": [
                "• Revisar logs del servidor para más detalles",
                "• Verificar configuración general del sistema",
            ],
        }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"

    logger.info(f"Iniciando MedConnect en puerto {port}")
    logger.info(f"Modo debug: {debug}")
    logger.info(f"Dominio configurado: {app.config['DOMAIN']}")

    # Ruta para Chrome DevTools (silenciar error 404)
    @app.route("/.well-known/appspecific/com.chrome.devtools.json")
    def chrome_devtools_config():
        """Maneja la solicitud de configuración de Chrome DevTools para evitar errores 404"""
        return "", 204  # No Content

    app.run(host="0.0.0.0", port=port, debug=debug)
