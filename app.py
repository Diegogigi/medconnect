# MedConnect - Aplicación Principal Flask
# Backend para plataforma de gestión médica con Google Sheets y Telegram Bot

import os
import sys
import logging
import time

# Configurar logging temprano para debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

logger.info("🚀 Iniciando importaciones de MedConnect...")

try:
    logger.info("📦 Importando Flask...")
    from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, make_response, send_from_directory, send_file, abort
    logger.info("✅ Flask importado exitosamente")
    
    logger.info("📦 Importando Flask-CORS...")
    from flask_cors import CORS
    logger.info("✅ Flask-CORS importado exitosamente")
    
    logger.info("📦 Importando bibliotecas estándar...")
    import requests
    import json
    import pdfkit
    import tempfile
    from io import BytesIO
    from datetime import datetime, timedelta
    logger.info("✅ Bibliotecas estándar importadas")
    
    logger.info("📦 Importando Google Sheets...")
    import gspread
    from google.oauth2.service_account import Credentials
    logger.info("✅ Google Sheets importado exitosamente")
    
    logger.info("📦 Importando módulos locales...")
    from config import get_config, SHEETS_CONFIG
    from auth_manager import AuthManager
    from backend.database.sheets_manager import sheets_db
    logger.info("✅ Módulos locales importados")
    
    logger.info("📦 Importando otras dependencias...")
    from werkzeug.utils import secure_filename
    import uuid
    from werkzeug.security import generate_password_hash, check_password_hash
    import secrets
    logger.info("✅ Todas las importaciones completadas exitosamente")
    
except Exception as e:
    logger.error(f"❌ Error durante las importaciones: {e}")
    logger.error(f"❌ Tipo de error: {type(e).__name__}")
    import traceback
    logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
    raise

logger.info("🔧 Verificando variables de entorno...")
required_vars = ['GOOGLE_SHEETS_ID', 'TELEGRAM_BOT_TOKEN']
for var in required_vars:
    if os.environ.get(var):
        logger.info(f"✅ {var}: Configurada")
    else:
        logger.warning(f"⚠️ {var}: NO configurada")

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Configurar archivos estáticos para producción
# Múltiples métodos para asegurar que funcione en Railway
try:
    # Método 1: WhiteNoise (preferido)
    from whitenoise import WhiteNoise
    app.wsgi_app = WhiteNoise(
        app.wsgi_app, 
        root=os.path.join(app.root_path, 'static'),
        prefix='/static/',
        max_age=31536000  # Cache por 1 año
    )
    logger.info("✅ WhiteNoise configurado para archivos estáticos")
except Exception as e:
    logger.error(f"❌ Error configurando WhiteNoise: {e}")

# Método 2: Configurar Flask para servir archivos estáticos directamente
app.static_folder = 'static'
app.static_url_path = '/static'

logger.info(f"📁 Static folder: {app.static_folder}")
logger.info(f"🌐 Static URL path: {app.static_url_path}")

# Configurar CORS
CORS(app, origins=config.CORS_ORIGINS)

# Configuración para subida de archivos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuración de Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_sheets_client():
    """Inicializa el cliente de Google Sheets"""
    try:
        # Verificar si existe archivo de credenciales local
        credentials_file = app.config.get('GOOGLE_CREDENTIALS_FILE')
        if credentials_file and os.path.exists(credentials_file):
            creds = Credentials.from_service_account_file(
                credentials_file, 
                scopes=SCOPES
            )
        else:
            # Para Railway, usar variables de entorno (método preferido)
            service_account_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '{}')
            if service_account_json != '{}':
                service_account_info = json.loads(service_account_json)
                creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
            else:
                logger.error("❌ No se encontraron credenciales de Google Sheets")
                return None
        
        client = gspread.authorize(creds)
        logger.info("✅ Cliente de Google Sheets inicializado correctamente")
        return client
    except Exception as e:
        logger.error(f"Error inicializando Google Sheets: {e}")
        return None

# Cliente global de Google Sheets
sheets_client = get_google_sheets_client()

# Funciones auxiliares para las vistas de agenda
def obtener_rango_semana(fecha_str):
    """Obtiene el rango de fechas de la semana que contiene la fecha dada"""
    from datetime import datetime, timedelta
    
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
    # Obtener el lunes de la semana (día 0)
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    return inicio_semana.strftime('%Y-%m-%d'), fin_semana.strftime('%Y-%m-%d')

def obtener_rango_mes(fecha_str):
    """Obtiene el rango de fechas del mes que contiene la fecha dada"""
    from datetime import datetime
    import calendar
    
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
    # Primer día del mes
    inicio_mes = fecha.replace(day=1)
    # Último día del mes
    ultimo_dia = calendar.monthrange(fecha.year, fecha.month)[1]
    fin_mes = fecha.replace(day=ultimo_dia)
    
    return inicio_mes.strftime('%Y-%m-%d'), fin_mes.strftime('%Y-%m-%d')

def organizar_agenda_semanal(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por día de la semana"""
    from datetime import datetime, timedelta
    
    agenda = {}
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Inicializar estructura
    inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    for i in range(7):
        fecha_dia = (inicio + timedelta(days=i)).strftime('%Y-%m-%d')
        agenda[fecha_dia] = {
            'dia_semana': dias_semana[i],
            'fecha': fecha_dia,
            'citas': []
        }
    
    # Agrupar citas por día
    for cita in citas:
        fecha_cita = cita['fecha']
        if fecha_cita in agenda:
            agenda[fecha_cita]['citas'].append(cita)
    
    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]['citas'].sort(key=lambda x: x['hora'])
    
    return agenda

def organizar_agenda_mensual(citas, fecha_inicio, fecha_fin):
    """Organiza las citas por día del mes"""
    from datetime import datetime, timedelta
    
    agenda = {}
    
    # Inicializar estructura para todos los días del mes
    inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    
    fecha_actual = inicio
    while fecha_actual <= fin:
        fecha_str = fecha_actual.strftime('%Y-%m-%d')
        agenda[fecha_str] = {
            'fecha': fecha_str,
            'dia': fecha_actual.day,
            'es_hoy': fecha_str == datetime.now().strftime('%Y-%m-%d'),
            'citas': []
        }
        fecha_actual += timedelta(days=1)
    
    # Agrupar citas por día
    for cita in citas:
        fecha_cita = cita['fecha']
        if fecha_cita in agenda:
            agenda[fecha_cita]['citas'].append(cita)
    
    # Ordenar citas por hora
    for fecha in agenda:
        agenda[fecha]['citas'].sort(key=lambda x: x['hora'])
    
    return agenda

def calcular_estadisticas_semana(citas):
    """Calcula estadísticas para la vista semanal"""
    total = len(citas)
    confirmadas = len([c for c in citas if c['estado'] == 'confirmada'])
    pendientes = len([c for c in citas if c['estado'] == 'pendiente'])
    canceladas = len([c for c in citas if c['estado'] == 'cancelada'])
    
    return {
        'total_citas': total,
        'confirmadas': confirmadas,
        'pendientes': pendientes,
        'canceladas': canceladas
    }

def calcular_estadisticas_mes(citas):
    """Calcula estadísticas para la vista mensual"""
    from datetime import datetime
    
    total = len(citas)
    confirmadas = len([c for c in citas if c['estado'] == 'confirmada'])
    pendientes = len([c for c in citas if c['estado'] == 'pendiente'])
    canceladas = len([c for c in citas if c['estado'] == 'cancelada'])
    
    # Agrupar por semana
    citas_por_semana = {}
    for cita in citas:
        fecha_cita = datetime.strptime(cita['fecha'], '%Y-%m-%d')
        semana = fecha_cita.isocalendar()[1]  # Número de semana del año
        if semana not in citas_por_semana:
            citas_por_semana[semana] = 0
        citas_por_semana[semana] += 1
    
    return {
        'total_citas': total,
        'confirmadas': confirmadas,
        'pendientes': pendientes,
        'canceladas': canceladas,
        'citas_por_semana': citas_por_semana
    }

# Inicializar AuthManager con debugging detallado
logger.info("🔍 Iniciando inicialización de AuthManager...")

try:
    # Verificar variables de entorno antes de crear AuthManager
    env_check = {
        'GOOGLE_SERVICE_ACCOUNT_JSON': bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')),
        'GOOGLE_SHEETS_ID': bool(os.environ.get('GOOGLE_SHEETS_ID')),
        'TELEGRAM_BOT_TOKEN': bool(os.environ.get('TELEGRAM_BOT_TOKEN'))
    }
    logger.info(f"🔧 Variables de entorno en app.py: {env_check}")
    
    # Verificar contenido de JSON
    json_content = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '')
    if json_content:
        logger.info(f"📝 JSON length: {len(json_content)} chars")
        logger.info(f"📝 JSON preview: {json_content[:100]}...")
        
        # Verificar que es JSON válido
        try:
            test_json = json.loads(json_content)
            logger.info(f"✅ JSON válido, proyecto: {test_json.get('project_id', 'N/A')}")
        except json.JSONDecodeError as je:
            logger.error(f"❌ JSON inválido: {je}")
    
    # Intentar crear AuthManager
    logger.info("🚀 Creando instancia de AuthManager...")
    auth_manager = AuthManager()
    logger.info("✅ AuthManager inicializado correctamente")
    
except Exception as e:
    logger.error(f"❌ Error inicializando AuthManager: {e}")
    logger.error(f"❌ Tipo de error: {type(e).__name__}")
    import traceback
    logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
    auth_manager = None

def get_spreadsheet():
    """Obtiene la hoja de cálculo principal"""
    if sheets_client:
        try:
            return sheets_client.open_by_key(app.config['GOOGLE_SHEETS_ID'])
        except Exception as e:
            logger.error(f"Error abriendo spreadsheet: {e}")
    return None

def get_current_user():
    """Obtiene los datos del usuario actual desde la sesión"""
    user_data = session.get('user_data', {})
    logger.info(f"🔍 Datos del usuario en sesión: {user_data}")
    return user_data

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Genera un nombre único para el archivo"""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return unique_filename

# Hacer la función disponible en todas las plantillas
@app.context_processor
def inject_user():
    """Inyecta los datos del usuario en todas las plantillas"""
    return dict(current_user=get_current_user())

# Decorador para rutas que requieren autenticación
def login_required(f):
    """Decorador para rutas que requieren login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de autenticación
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro de usuarios"""
    if not auth_manager:
        flash('Sistema de autenticación no disponible', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            user_data = {
                'email': request.form.get('email', '').strip().lower(),
                'password': request.form.get('password', ''),
                'nombre': request.form.get('nombre', '').strip(),
                'apellido': request.form.get('apellido', '').strip(),
                'telefono': request.form.get('telefono', '').strip(),
                'fecha_nacimiento': request.form.get('fecha_nacimiento', ''),
                'genero': request.form.get('genero', ''),
                'direccion': request.form.get('direccion', '').strip(),
                'ciudad': request.form.get('ciudad', '').strip(),
                'tipo_usuario': request.form.get('tipo_usuario', '').strip()
            }
            
            # Agregar campos específicos para profesionales
            if user_data['tipo_usuario'] == 'profesional':
                user_data.update({
                    'profesion': request.form.get('profesion', '').strip(),
                    'especialidad': request.form.get('especialidad', '').strip(),
                    'numero_registro': request.form.get('numero_registro', '').strip(),
                    'anos_experiencia': request.form.get('anos_experiencia', '0').strip(),
                    'institucion': request.form.get('institucion', '').strip(),
                    'titulo': request.form.get('titulo', '').strip(),
                    'ano_egreso': request.form.get('ano_egreso', '').strip(),
                    'idiomas': request.form.get('idiomas', 'Español').strip(),
                    'direccion_consulta': request.form.get('direccion_consulta', '').strip(),
                    'horario_atencion': request.form.get('horario_atencion', '').strip(),
                    'areas_especializacion': request.form.get('areas_especializacion', '').strip(),
                    'certificaciones': request.form.get('certificaciones', '').strip()
                })
            
            # Validar confirmación de contraseña
            confirm_password = request.form.get('confirm_password', '')
            if user_data['password'] != confirm_password:
                return render_template('register.html', 
                                     message='Las contraseñas no coinciden', 
                                     success=False)
            
            # Registrar usuario
            success, message = auth_manager.register_user(user_data)
            
            if success:
                logger.info(f"✅ Usuario registrado exitosamente: {user_data['email']}")
                return render_template('register.html', 
                                     message=message, 
                                     success=True)
            else:
                return render_template('register.html', 
                                     message=message, 
                                     success=False)
                
        except Exception as e:
            logger.error(f"❌ Error en registro: {e}")
            return render_template('register.html', 
                                 message='Error interno del servidor', 
                                 success=False)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    logger.info("🔍 Accediendo a página de login...")
    
    if not auth_manager:
        logger.error("❌ AuthManager no disponible")
        return render_template('login.html', 
                             message='Sistema de autenticación temporalmente no disponible. Intenta más tarde.', 
                             success=False)
    
    logger.info("✅ AuthManager disponible")
    
    # Si ya está logueado, redirigir al dashboard
    if 'user_id' in session:
        user_type = session.get('user_type', 'paciente')
        logger.info(f"🔄 Usuario ya logueado, redirigiendo a dashboard: {user_type}")
        if user_type == 'profesional':
            return redirect(url_for('professional_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            if not email or not password:
                return render_template('login.html', 
                                     message='Email y contraseña son requeridos', 
                                     success=False)
            
            # Intentar login
            success, message, user_data = auth_manager.login_user(email, password)
            
            if success and user_data:
                # Crear sesión con información completa del usuario
                session['user_id'] = user_data['id']
                session['user_email'] = user_data['email']
                session['user_name'] = f"{user_data['nombre']} {user_data['apellido']}"
                session['user_type'] = user_data['tipo_usuario']
                session['user_data'] = user_data
                session['just_logged_in'] = True  # Flag para mostrar mensaje de bienvenida
                
                logger.info(f"✅ Login exitoso: {email}")
                
                # Redirigir según tipo de usuario
                if user_data['tipo_usuario'] == 'profesional':
                    return redirect(url_for('professional_dashboard'))
                else:
                    return redirect(url_for('patient_dashboard'))
            else:
                return render_template('login.html', 
                                     message=message, 
                                     success=False)
                
        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            return render_template('login.html', 
                                 message='Error interno del servidor', 
                                 success=False)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    try:
        user_email = session.get('user_email', 'Usuario')
        logger.info(f"🔄 Iniciando logout para: {user_email}")
        
        # Limpiar sesión completamente múltiples veces
        session.clear()
        session.permanent = False
        
        # Forzar eliminación de claves específicas
        for key in ['user_id', 'user_email', 'user_name', 'user_type', 'user_data']:
            session.pop(key, None)
        
        logger.info(f"✅ Sesión limpiada completamente para: {user_email}")
        logger.info(f"🔍 Sesión después del clear: {dict(session)}")
        
        # NO usar flash ya que requiere sesión
        # En su lugar, usar parámetro URL
        
        # Crear respuesta con headers anti-cache muy fuertes
        response = make_response(redirect('/?logout=success'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
        
        # Eliminar cookies de sesión explícitamente
        response.set_cookie('session', '', expires=0)
        response.set_cookie('session', '', expires=0, domain='.medconnect.cl')
        response.set_cookie('session', '', expires=0, path='/')
        
        logger.info("🔄 Redirigiendo a página principal con headers anti-cache...")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en logout: {e}")
        # En caso de error, limpiar toda la sesión y redirigir
        try:
            session.clear()
            session.permanent = False
            logger.info("✅ Sesión limpiada después del error")
        except Exception as clear_error:
            logger.error(f"❌ Error limpiando sesión: {clear_error}")
        
        # Respuesta de error también con headers anti-cache
        response = make_response(redirect('/?logout=error'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'  
        response.headers['Expires'] = '-1'
        
        logger.info("🔄 Redirigiendo a página principal después del error...")
        return response

# Rutas principales del frontend
@app.route('/')
def index():
    """Página principal - Landing page"""
    try:
        # Verificar si venimos de un logout
        logout_param = request.args.get('logout')
        if logout_param in ['success', 'error']:
            logger.info(f"🔄 Detectado logout: {logout_param} - Forzando limpieza de sesión")
            # Forzar limpieza total de sesión
            session.clear()
            session.permanent = False
            for key in ['user_id', 'user_email', 'user_name', 'user_type', 'user_data']:
                session.pop(key, None)
            
            # Forzar variables a None
            user_id = None
            user_name = None
            user_type = None
            
            logger.info("🔄 Sesión forzada a None después de logout")
        else:
            # Obtener datos de sesión de forma segura
            user_id = session.get('user_id')
            user_name = session.get('user_name')
            user_type = session.get('user_type')
        
        # Log para debugging
        logger.info(f"🔍 Index - user_id: {user_id}, user_name: {user_name}, user_type: {user_type}")
        logger.info(f"🔍 Sesión completa: {dict(session)}")
        
        # Crear respuesta sin cache con headers muy fuertes
        response = make_response(render_template('index.html', 
                                               user_id=user_id,
                                               user_name=user_name, 
                                               user_type=user_type,
                                               logout_message=logout_param))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Si venimos de logout, eliminar cookies adicionales
        if logout_param:
            response.set_cookie('session', '', expires=0)
            response.set_cookie('session', '', expires=0, domain='.medconnect.cl')
            response.set_cookie('session', '', expires=0, path='/')
        
        return response
    except Exception as e:
        logger.error(f"Error en index: {e}")
        return render_template('index.html', user_id=None, user_name=None, user_type=None)

@app.route('/patient')
@login_required
def patient_dashboard():
    """Dashboard para pacientes"""
    try:
        user_data = session.get('user_data', {})
        just_logged_in = session.pop('just_logged_in', False)  # Obtener y remover el flag
        
        # Log para debugging
        if just_logged_in:
            logger.info(f"🎉 Mostrando mensaje de bienvenida para paciente: {user_data.get('nombre', 'Usuario')}")
        
        return render_template('patient.html', 
                             user=user_data, 
                             just_logged_in=just_logged_in)
    except Exception as e:
        logger.error(f"Error en dashboard paciente: {e}")
        return render_template('patient.html', user={}, just_logged_in=False)

def infer_gender_from_name(nombre):
    """Infiere el género basado en el nombre"""
    # Lista de terminaciones comunes para nombres femeninos en español
    terminaciones_femeninas = ['a', 'na', 'ia', 'la', 'ra', 'da', 'ta', 'ina', 'ela', 'isa', 'ana', 'elle', 'ella']
    # Excepciones conocidas (nombres masculinos que terminan en 'a')
    excepciones_masculinas = ['juan pablo', 'jose maria', 'luca', 'matias', 'tobias', 'elias']
    
    if not nombre:
        return 'M'  # valor por defecto
        
    nombre = nombre.lower().strip()
    
    # Verificar excepciones primero
    if nombre in excepciones_masculinas:
        return 'M'
        
    # Verificar terminaciones femeninas
    for terminacion in terminaciones_femeninas:
        if nombre.endswith(terminacion):
            return 'F'
            
    return 'M'  # Si no coincide con patrones femeninos, asumir masculino

def get_gendered_profession(profesion, genero=None, nombre=None):
    """Retorna la profesión con el género correcto"""
    profesiones = {
        'FONOAUDIOLOGÍA': {'M': 'Fonoaudiólogo', 'F': 'Fonoaudióloga'},
        'KINESIOLOGÍA': {'M': 'Kinesiólogo', 'F': 'Kinesióloga'},
        'TERAPIA OCUPACIONAL': {'M': 'Terapeuta Ocupacional', 'F': 'Terapeuta Ocupacional'},
        'PSICOLOGÍA': {'M': 'Psicólogo', 'F': 'Psicóloga'},
        'NUTRICIÓN': {'M': 'Nutricionista', 'F': 'Nutricionista'},
        'MEDICINA': {'M': 'Doctor', 'F': 'Doctora'},
        'ENFERMERÍA': {'M': 'Enfermero', 'F': 'Enfermera'}
    }
    
    if not profesion:
        return ''
        
    profesion = profesion.upper()
    if profesion not in profesiones:
        return profesion
        
    # Si no hay género explícito, intentar inferirlo del nombre
    if not genero and nombre:
        genero = infer_gender_from_name(nombre)
        logger.info(f"🔍 Género inferido del nombre '{nombre}': {genero}")
    
    # Normalizar el género a 'M' o 'F'
    if genero:
        genero = genero.upper()
        if genero.startswith('M'):  # Matches 'M' or 'MASCULINO'
            genero = 'M'
        elif genero.startswith('F'):  # Matches 'F' or 'FEMENINO'
            genero = 'F'
        else:
            genero = 'M'  # Default to M for other values
    else:
        genero = 'M'  # Default to M if no gender provided
        
    logger.info(f"🔍 Usando género normalizado: {genero} para profesión: {profesion}")
    
    profesion_gendered = profesiones[profesion].get(genero, profesiones[profesion]['M'])
    logger.info(f"🔍 Profesión con género generada: {profesion_gendered}")
    
    return profesion_gendered

@app.route('/professional')
@login_required
def professional_dashboard():
    """Ruta para el dashboard del profesional"""
    try:
        user_data = get_current_user()
        profesional_id = user_data.get('id')
        
        logger.info(f"🔍 Datos iniciales del usuario: {user_data}")
        
        # Cargar datos completos del profesional
        if profesional_id:
            professional_data = auth_manager.get_professional_by_id(profesional_id)
            if professional_data:
                # Actualizar datos del usuario con información de la hoja
                user_data.update({
                    'profesion': professional_data.get('Profesion', ''),
                    'especialidad': professional_data.get('Especialidad', ''),
                    'numero_registro': professional_data.get('Numero_Registro', ''),
                    'disponible': str(professional_data.get('Disponible', 'true')).lower() == 'true',
                    'genero': professional_data.get('genero', '')  # Obtenido de la hoja de usuarios
                })
                
                logger.info(f"🔍 Datos después de actualizar con professional_data: {user_data}")
                
                # Si no hay género explícito, intentar inferirlo del nombre
                if not user_data['genero']:
                    user_data['genero'] = infer_gender_from_name(user_data.get('nombre', ''))
                    logger.info(f"🔍 Género inferido del nombre: {user_data['genero']}")
                    
                # Obtener la profesión con el género correcto
                user_data['profesion_gendered'] = get_gendered_profession(
                    user_data['profesion'], 
                    user_data['genero']
                )
                logger.info(f"🔍 Profesión con género: {user_data['profesion_gendered']}")
                
                # Actualizar la sesión con los datos actualizados
                session['user_data'] = user_data
                logger.info(f"🔍 Sesión actualizada con nuevos datos: {session['user_data']}")
        
        return render_template(
            'professional.html',
                             user=user_data, 
            just_logged_in=session.pop('just_logged_in', False)
        )
        
    except Exception as e:
        logger.error(f"Error en dashboard profesional: {e}")
        return render_template('professional.html', user={}, just_logged_in=False)

@app.route('/profile')
@login_required
def profile():
    """Página de perfil del usuario"""
    logger.info("🔍 INICIANDO función profile()")
    try:
        user_data = session.get('user_data', {})
        logger.info(f"🔍 Datos del usuario en perfil: {user_data}")
        logger.info(f"🔍 Sesión completa: {dict(session)}")
        
        # Verificar si es un profesional
        if user_data.get('tipo_usuario') == 'profesional':
            # Agregar campos adicionales para el perfil profesional
            professional_data = user_data.copy()
            professional_data.update({
                'calificacion': 4.5,  # Valor por defecto
                'total_pacientes': 0,
                'atenciones_mes': 0,
                'tiempo_respuesta': '24h',
                'disponible': True,
                'numero_registro': 'Por completar',
                'especialidad': 'Por completar',
                'subespecialidades': 'Por completar',
                'anos_experiencia': 0,
                'idiomas': ['Español'],
                'direccion_consulta': user_data.get('direccion', 'Por completar'),
                'horario_atencion': 'Lunes a Viernes 9:00 - 18:00',
                'certificaciones': [],
                'areas_especializacion': []
            })
            
            # Intentar obtener datos reales desde Google Sheets
            try:
                user_id = user_data.get('id')
                if user_id:
                    # Obtener datos completos del profesional
                    professional_sheet_data = auth_manager.get_professional_by_id(user_id)
                    if professional_sheet_data:
                        # Mapear campos específicos
                        field_mapping = {
                            'Numero_Registro': 'numero_registro',
                            'Especialidad': 'especialidad',
                            'Anos_Experiencia': 'anos_experiencia',
                            'Calificacion': 'calificacion',
                            'Direccion_Consulta': 'direccion_consulta',
                            'Horario_Atencion': 'horario_atencion',
                            'Idiomas': 'idiomas_str',
                            'Areas_Especializacion': 'areas_especializacion_str',
                            'Disponible': 'disponible_str',
                            'Profesion': 'profesion'
                        }
                        
                        for sheet_field, local_field in field_mapping.items():
                            if sheet_field in professional_sheet_data:
                                professional_data[local_field] = professional_sheet_data[sheet_field]
                        
                        # Procesar campos especiales
                        if 'idiomas_str' in professional_data:
                            idiomas_str = professional_data['idiomas_str'] or 'Español'
                            professional_data['idiomas'] = [idioma.strip() for idioma in idiomas_str.split(',') if idioma.strip()]
                        
                        if 'areas_especializacion_str' in professional_data:
                            areas_str = professional_data['areas_especializacion_str'] or ''
                            professional_data['areas_especializacion'] = [area.strip() for area in areas_str.split(',') if area.strip()]
                        
                        if 'disponible_str' in professional_data:
                            professional_data['disponible'] = str(professional_data['disponible_str']).lower() == 'true'
                        
                        # Convertir tipos de datos
                        if 'anos_experiencia' in professional_data:
                            try:
                                professional_data['anos_experiencia'] = int(professional_data['anos_experiencia'] or 0)
                            except:
                                professional_data['anos_experiencia'] = 0
                        
                        if 'calificacion' in professional_data:
                            try:
                                professional_data['calificacion'] = float(professional_data['calificacion'] or 4.5)
                            except:
                                professional_data['calificacion'] = 4.5
                    
                    # Obtener certificaciones del profesional
                    certificaciones = auth_manager.get_professional_certifications(user_id)
                    professional_data['certificaciones'] = certificaciones
                
            except Exception as e:
                logger.warning(f"Error accediendo a datos profesionales: {e}")
            
            return render_template('profile_professional.html', user=professional_data)
        
        # Crear respuesta sin cache
        response = make_response(render_template('profile.html', user=user_data))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        logger.error(f"❌ Error en perfil: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return render_template('profile.html', user={})

@app.route('/services')
@login_required
def services():
    """Página de servicios del profesional"""
    if session.get('user_type') != 'profesional':
        flash('Acceso denegado: Solo para profesionales médicos', 'error')
        return redirect(url_for('index'))
    
    user_data = session.get('user_data', {})
    return render_template('services.html', user=user_data)

@app.route('/requests')
@login_required
def requests():
    """Página de solicitudes del profesional"""
    if session.get('user_type') != 'profesional':
        flash('Acceso denegado: Solo para profesionales médicos', 'error')
        return redirect(url_for('index'))
    
    user_data = session.get('user_data', {})
    return render_template('requests.html', user=user_data)



@app.route('/chat')
@login_required
def chat():
    """Página de chat del profesional"""
    if session.get('user_type') != 'profesional':
        flash('Acceso denegado: Solo para profesionales médicos', 'error')
        return redirect(url_for('index'))
    
    user_data = session.get('user_data', {})
    return render_template('chat.html', user=user_data)

# API Routes para el frontend
@app.route('/api/patient/<patient_id>/consultations')
def get_patient_consultations(patient_id):
    """Obtiene las consultas de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Leer datos de la hoja Consultas manualmente para evitar errores de headers
        try:
            worksheet = spreadsheet.worksheet('Consultas')
            all_values = worksheet.get_all_values()
            
            consultations = []
            
            if len(all_values) > 1:
                headers = all_values[0]
                logger.info(f"📋 Headers de Consultas: {headers}")
                
                # Headers reales: ['id', 'patient_id', 'doctor', 'specialty', 'date', 'diagnosis', 'treatment', 'notes', 'status']
                for row in all_values[1:]:
                    if len(row) >= len(headers) and any(cell.strip() for cell in row):
                        # Verificar si pertenece al paciente
                        patient_id_cell = row[1] if len(row) > 1 else ''
                        
                        if str(patient_id_cell) == str(patient_id):
                            # Transformar al formato esperado por la plataforma web
                            consultation_formatted = {
                                'id': row[0] if len(row) > 0 else '',  # id
                                'patient_id': patient_id,
                                'doctor': row[2] if len(row) > 2 else '',  # doctor
                                'specialty': row[3] if len(row) > 3 else '',  # specialty
                                'date': convert_date_format(row[4] if len(row) > 4 else ''),  # date
                                'diagnosis': row[5] if len(row) > 5 else '',  # diagnosis
                                'treatment': row[6] if len(row) > 6 else '',  # treatment
                                'notes': row[7] if len(row) > 7 else '',  # notes
                                'status': row[8] if len(row) > 8 else 'completada'  # status
                            }
                            
                            consultations.append(consultation_formatted)
            
            logger.info(f"🔍 Consultas encontradas para paciente {patient_id}: {len(consultations)}")
            
            return jsonify({'consultations': consultations})
            
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Consultas' no encontrada")
            return jsonify({'consultations': []})
            
    except Exception as e:
        logger.error(f"Error obteniendo consultas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/medications')
def get_patient_medications(patient_id):
    """Obtiene los medicamentos de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Leer datos de la hoja Medicamentos manualmente para evitar errores de headers
        try:
            worksheet = spreadsheet.worksheet('Medicamentos')
            all_values = worksheet.get_all_values()
            
            medications = []
            
            if len(all_values) > 1:
                headers = all_values[0]
                logger.info(f"📋 Headers de Medicamentos: {headers}")
                
                # Headers reales: ['id', 'patient_id', 'medication', 'dosage', 'frequency', 'start_date', 'end_date', 'prescribed_by', 'status']
                for row in all_values[1:]:
                    if len(row) >= len(headers) and any(cell.strip() for cell in row):
                        # Verificar si pertenece al paciente
                        patient_id_cell = row[1] if len(row) > 1 else ''
                        
                        if str(patient_id_cell) == str(patient_id):
                            # Transformar al formato esperado por la plataforma web
                            medication_formatted = {
                                'id': row[0] if len(row) > 0 else '',  # id
                                'patient_id': patient_id,
                                'name': row[2] if len(row) > 2 else '',  # medication
                                'dosage': row[3] if len(row) > 3 else '',  # dosage
                                'frequency': row[4] if len(row) > 4 else '',  # frequency
                                'prescribing_doctor': row[7] if len(row) > 7 else '',  # prescribed_by
                                'start_date': convert_date_format(row[5] if len(row) > 5 else ''),  # start_date
                                'end_date': convert_date_format(row[6] if len(row) > 6 else ''),  # end_date
                                'instructions': '',  # No disponible en la estructura actual
                                'status': row[8] if len(row) > 8 else 'activo'  # status
                            }
                            
                            medications.append(medication_formatted)
            
            logger.info(f"🔍 Medicamentos encontrados para paciente {patient_id}: {len(medications)}")
            
            return jsonify({'medications': medications})
            
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Medicamentos' no encontrada")
            return jsonify({'medications': []})
            
    except Exception as e:
        logger.error(f"Error obteniendo medicamentos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/exams')
def get_patient_exams(patient_id):
    """Obtiene los exámenes de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Leer datos de la hoja 'Examenes' (nueva estructura)
        try:
            examenes_worksheet = spreadsheet.worksheet('Examenes')
            all_exam_values = examenes_worksheet.get_all_values()
            
            patient_exams = []
            
            if len(all_exam_values) > 1:
                headers = all_exam_values[0]
                logger.info(f"📋 Headers de Examenes: {headers}")
                
                # Headers reales: ['id', 'patient_id', 'exam_type', 'date', 'results', 'lab', 'doctor', 'file_url', 'status']
                for row in all_exam_values[1:]:
                    if len(row) >= len(headers) and any(cell.strip() for cell in row):
                        # Verificar si pertenece al paciente
                        patient_id_cell = row[1] if len(row) > 1 else ''
                        
                        if str(patient_id_cell) == str(patient_id):
                            # Transformar al formato esperado por la plataforma web
                            original_date = row[3] if len(row) > 3 else ''
                            converted_date = convert_date_format(original_date)
                            logger.info(f"📅 Fecha original: '{original_date}' → Convertida: '{converted_date}'")
                            
                            exam_formatted = {
                                'id': row[0] if len(row) > 0 else '',  # id
                                'patient_id': patient_id,
                                'exam_type': row[2] if len(row) > 2 else '',  # exam_type
                                'date': converted_date,  # date
                                'results': row[4] if len(row) > 4 else '',  # results
                                'lab': row[5] if len(row) > 5 else '',  # lab
                                'doctor': row[6] if len(row) > 6 else '',  # doctor
                                'file_url': row[7] if len(row) > 7 else '',  # file_url
                                'status': row[8] if len(row) > 8 else 'completado'  # status
                            }
                            
                            patient_exams.append(exam_formatted)
            
            logger.info(f"🔍 Exámenes encontrados para paciente {patient_id}: {len(patient_exams)}")
            
            if patient_exams:
                return jsonify({'exams': patient_exams})
                
        except gspread.WorksheetNotFound:
            logger.info("📝 Hoja 'Examenes' no encontrada, intentando con estructura antigua")
        
        # Si no hay resultados en la nueva hoja, probar con la hoja antigua
        try:
            worksheet = spreadsheet.worksheet(SHEETS_CONFIG['exams']['name'])
            
            # Obtener datos usando la estructura antigua como respaldo
            all_records = worksheet.get_all_records()
            
            patient_exams = []
            for record in all_records:
                if str(record.get('patient_id', '')) == str(patient_id):
                    original_date = record.get('date', '')
                    converted_date = convert_date_format(original_date)
                    logger.info(f"📅 Fecha original (antigua): '{original_date}' → Convertida: '{converted_date}'")
                    
                    exam_formatted = {
                        'id': record.get('id', ''),
                        'patient_id': record.get('patient_id', ''),
                        'exam_type': record.get('exam_type', ''),
                        'date': converted_date,
                        'results': record.get('results', ''),
                        'lab': record.get('lab', ''),
                        'doctor': record.get('doctor', ''),
                        'file_url': record.get('file_url', ''),
                        'status': record.get('status', 'completado')
                    }
                    patient_exams.append(exam_formatted)
            
            logger.info(f"🔍 Exámenes encontrados en estructura antigua para paciente {patient_id}: {len(patient_exams)}")
            
            return jsonify({'exams': patient_exams})
            
        except gspread.WorksheetNotFound:
            logger.warning("📝 Ninguna hoja de exámenes encontrada")
            return jsonify({'exams': []})
            
    except Exception as e:
        logger.error(f"Error obteniendo exámenes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/family')
def get_patient_family(patient_id):
    """Obtiene los familiares de un paciente"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        worksheet = spreadsheet.worksheet(SHEETS_CONFIG['family_members']['name'])
        records = worksheet.get_all_records()
        
        # Filtrar por patient_id
        patient_family = [r for r in records if str(r.get('patient_id')) == str(patient_id)]
        
        logger.info(f"🔍 Familiares encontrados para paciente {patient_id}: {len(patient_family)}")
        
        return jsonify({'family': patient_family})
    except Exception as e:
        logger.error(f"Error obteniendo familiares: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# APIs para eliminar datos
@app.route('/api/patient/<patient_id>/consultations/<consultation_id>', methods=['DELETE'])
@login_required
def delete_consultation(patient_id, consultation_id):
    """Elimina una consulta médica"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Usar la hoja 'Consultas' que existe realmente
        try:
            worksheet = spreadsheet.worksheet('Consultas')
            all_values = worksheet.get_all_values()
            
            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(all_values[1:], start=2):  # Start from row 2 (after headers)
                    if len(row) > 1 and str(row[0]) == str(consultation_id) and str(row[1]) == str(patient_id):
                        row_to_delete = i
                        break
            
            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(f"✅ Consulta {consultation_id} eliminada para paciente {patient_id}")
                return jsonify({'success': True, 'message': 'Consulta eliminada exitosamente'})
            else:
                return jsonify({'error': 'Consulta no encontrada'}), 404
                
        except gspread.WorksheetNotFound:
            return jsonify({'error': 'Hoja de consultas no encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Error eliminando consulta: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/medications/<medication_id>', methods=['DELETE'])
@login_required
def delete_medication(patient_id, medication_id):
    """Elimina un medicamento"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Usar la hoja 'Medicamentos' que existe realmente
        try:
            worksheet = spreadsheet.worksheet('Medicamentos')
            all_values = worksheet.get_all_values()
            
            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(all_values[1:], start=2):  # Start from row 2 (after headers)
                    if len(row) > 1 and str(row[0]) == str(medication_id) and str(row[1]) == str(patient_id):
                        row_to_delete = i
                        break
            
            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(f"✅ Medicamento {medication_id} eliminado para paciente {patient_id}")
                return jsonify({'success': True, 'message': 'Medicamento eliminado exitosamente'})
            else:
                return jsonify({'error': 'Medicamento no encontrado'}), 404
                
        except gspread.WorksheetNotFound:
            return jsonify({'error': 'Hoja de medicamentos no encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Error eliminando medicamento: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/exams/<exam_id>', methods=['DELETE'])
@login_required
def delete_exam(patient_id, exam_id):
    """Elimina un examen"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        # Usar la hoja 'Examenes' que existe realmente
        try:
            worksheet = spreadsheet.worksheet('Examenes')
            all_values = worksheet.get_all_values()
            
            # Buscar la fila a eliminar
            row_to_delete = None
            if len(all_values) > 1:
                for i, row in enumerate(all_values[1:], start=2):  # Start from row 2 (after headers)
                    if len(row) > 1 and str(row[0]) == str(exam_id) and str(row[1]) == str(patient_id):
                        row_to_delete = i
                        break
            
            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(f"✅ Examen {exam_id} eliminado para paciente {patient_id}")
                return jsonify({'success': True, 'message': 'Examen eliminado exitosamente'})
            else:
                return jsonify({'error': 'Examen no encontrado'}), 404
                
        except gspread.WorksheetNotFound:
            return jsonify({'error': 'Hoja de exámenes no encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Error eliminando examen: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/family/<family_id>', methods=['DELETE'])
@login_required
def delete_family_member(patient_id, family_id):
    """Elimina un familiar"""
    try:
        # Verificar que el usuario solo pueda eliminar sus propios datos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        worksheet = spreadsheet.worksheet(SHEETS_CONFIG['family_members']['name'])
        records = worksheet.get_all_records()
        
        # Buscar la fila a eliminar
        row_to_delete = None
        for i, record in enumerate(records, start=2):  # Start from row 2 (after headers)
            if str(record.get('id')) == str(family_id) and str(record.get('patient_id')) == str(patient_id):
                row_to_delete = i
                break
        
        if row_to_delete:
            worksheet.delete_rows(row_to_delete)
            logger.info(f"✅ Familiar {family_id} eliminado para paciente {patient_id}")
            return jsonify({'success': True, 'message': 'Familiar eliminado exitosamente'})
        else:
            return jsonify({'error': 'Familiar no encontrado'}), 404
            
    except Exception as e:
        logger.error(f"Error eliminando familiar: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# APIs para actualizar información del perfil
@app.route('/api/profile/personal', methods=['PUT'])
@login_required
def update_personal_info():
    """Actualiza la información personal del usuario"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Validar campos requeridos
        required_fields = ['nombre', 'apellido', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'El campo {field} es requerido'}), 400
        
        # Validar formato de email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Formato de email inválido'}), 400
        
        # Validar teléfono si se proporciona
        if data.get('telefono'):
            try:
                telefono = int(data['telefono'])
                if telefono <= 0:
                    return jsonify({'error': 'Teléfono debe ser un número positivo'}), 400
            except ValueError:
                return jsonify({'error': 'Teléfono debe ser un número válido'}), 400
        
        # Actualizar en Google Sheets
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        worksheet = spreadsheet.worksheet(SHEETS_CONFIG['users']['name'])
        records = worksheet.get_all_records()
        
        # Buscar el usuario
        user_row = None
        for i, record in enumerate(records, start=2):
            if record.get('id') == user_id:
                user_row = i
                break
        
        if not user_row:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Preparar datos para actualizar
        update_data = {
            'nombre': data['nombre'],
            'apellido': data['apellido'],
            'email': data['email'],
            'telefono': data.get('telefono', ''),
            'fecha_nacimiento': data.get('fecha_nacimiento', ''),
            'genero': data.get('genero', ''),
            'direccion': data.get('direccion', ''),
            'ciudad': data.get('ciudad', '')
        }
        
        # Actualizar fila en Google Sheets
        headers = worksheet.row_values(1)
        for field, value in update_data.items():
            if field in headers:
                col_index = headers.index(field) + 1
                worksheet.update_cell(user_row, col_index, value)
        
        # Actualizar sesión
        user_data = session.get('user_data', {})
        user_data.update(update_data)
        session['user_data'] = user_data
        session['user_email'] = data['email']
        session['user_name'] = f"{data['nombre']} {data['apellido']}"
        
        logger.info(f"✅ Información personal actualizada para usuario {user_id}")
        return jsonify({'success': True, 'message': 'Información personal actualizada exitosamente'})
        
    except Exception as e:
        logger.error(f"Error actualizando información personal: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/profile/medical', methods=['PUT'])
@login_required
def update_medical_info():
    """Actualiza la información médica del usuario"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Por ahora, simular actualización exitosa
        # En una implementación real, aquí se actualizaría una tabla de información médica
        logger.info(f"✅ Información médica actualizada para usuario {user_id}")
        return jsonify({'success': True, 'message': 'Información médica actualizada exitosamente'})
        
    except Exception as e:
        logger.error(f"Error actualizando información médica: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/profile/notifications', methods=['PUT'])
@login_required
def update_notification_settings():
    """Actualiza las configuraciones de notificaciones"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Por ahora, simular actualización exitosa
        # En una implementación real, aquí se guardarían las preferencias de notificación
        logger.info(f"✅ Configuraciones de notificación actualizadas para usuario {user_id}")
        return jsonify({'success': True, 'message': 'Configuraciones de notificación actualizadas exitosamente'})
        
    except Exception as e:
        logger.error(f"Error actualizando configuraciones de notificación: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Webhook para Telegram Bot
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Webhook para recibir mensajes del bot de Telegram"""
    try:
        data = request.get_json()
        logger.info(f"📨 Webhook recibido: {data}")
        
        # Procesar mensaje del bot
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user_id = message['from']['id']
            username = message['from'].get('username', 'Sin username')
            
            logger.info(f"👤 Usuario: {username} ({user_id}) - Mensaje: {text}")
            
            # Registrar interacción en Google Sheets
            log_bot_interaction(user_id, username, text, chat_id)
            
            # Procesar comando o mensaje
            response = process_telegram_message(text, chat_id, user_id)
            
            # Enviar respuesta
            if response:
                success = send_telegram_message(chat_id, response)
                logger.info(f"📤 Respuesta enviada: {success}")
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        logger.error(f"❌ Error en webhook: {e}")
        return jsonify({'error': 'Error procesando webhook'}), 500

@app.route('/test-bot', methods=['GET'])
def test_bot():
    """Endpoint para probar el bot de Telegram"""
    try:
        # Información del bot
        bot_info = {
            'bot_token_configured': bool(config.TELEGRAM_BOT_TOKEN),
            'webhook_url': 'https://www.medconnect.cl/webhook',
            'sheets_id': config.GOOGLE_SHEETS_ID[:20] + '...' if config.GOOGLE_SHEETS_ID else None
        }
        
        # Probar envío de mensaje de prueba
        test_message = "🤖 Bot de MedConnect funcionando correctamente!\n\n✅ Webhook configurado\n✅ Conexión establecida"
        
        return jsonify({
            'status': 'Bot configurado correctamente',
            'bot_info': bot_info,
            'test_message': test_message,
            'instructions': 'Envía un mensaje al bot @Medconn_bot en Telegram para probarlo'
        })
        
    except Exception as e:
        logger.error(f"❌ Error probando bot: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/bot-stats', methods=['GET'])
def bot_stats():
    """Estadísticas del bot"""
    try:
        if not auth_manager:
            return jsonify({'error': 'AuthManager no disponible'}), 500
            
        # Obtener estadísticas de interacciones del bot
        try:
            interactions = auth_manager.get_sheet_data('Interacciones_Bot')
            
            stats = {
                'total_interactions': len(interactions) if interactions else 0,
                'unique_users': len(set(row.get('user_id', '') for row in interactions)) if interactions else 0,
                'recent_interactions': interactions[-5:] if interactions else []
            }
            
            return jsonify({
                'status': 'success',
                'stats': stats,
                'bot_username': '@Medconn_bot'
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error getting stats',
                'error': str(e),
                'bot_username': '@Medconn_bot'
            })
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        return jsonify({'error': str(e)}), 500

def log_bot_interaction(user_id, username, message, chat_id):
    """Registra la interacción del bot en Google Sheets"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return
        
        worksheet = spreadsheet.worksheet(SHEETS_CONFIG['bot_interactions']['name'])
        
        # Preparar datos
        row_data = [
            len(worksheet.get_all_values()) + 1,  # ID auto-incrementado
            user_id,
            username,
            message,
            '',  # Response se llenará después
            datetime.now().isoformat(),
            'message',
            'processed'
        ]
        
        worksheet.append_row(row_data)
        logger.info(f"Interacción registrada para usuario {user_id}")
    except Exception as e:
        logger.error(f"Error registrando interacción: {e}")

# Diccionario para almacenar contexto de conversaciones
user_contexts = {}

# Palabras clave para reconocimiento de intenciones
INTENT_KEYWORDS = {
    'consulta': ['consulta', 'médico', 'doctor', 'cita', 'visita', 'chequeo', 'revisión', 'control'],
    'medicamento': ['medicamento', 'medicina', 'pastilla', 'píldora', 'remedio', 'fármaco', 'droga', 'tratamiento', 'nuevo medicamento', 'empezar medicamento', 'comenzar tratamiento', 'recetaron', 'prescribieron', 'como va', 'efectos', 'reacción', 'funciona', 'mejora', 'empeora'],
    'examen': ['examen', 'análisis', 'estudio', 'prueba', 'laboratorio', 'radiografía', 'ecografía', 'resonancia', 'me hice', 'ya me hice', 'tengo resultados', 'salieron', 'completé', 'terminé examen', 'tengo que hacerme', 'debo hacerme', 'programado', 'agendado', 'próximo examen', 'me van a hacer'],
    'historial': ['historial', 'historia', 'registro', 'datos', 'información', 'ver', 'mostrar', 'consultar'],
    'saludo': ['hola', 'buenos', 'buenas', 'saludos', 'hey', 'qué tal', 'cómo estás'],
    'despedida': ['adiós', 'chao', 'hasta luego', 'nos vemos', 'bye', 'gracias'],
    'ayuda': ['ayuda', 'help', 'auxilio', 'socorro', 'no entiendo', 'qué puedes hacer'],
    'emergencia': ['emergencia', 'urgente', 'grave', 'dolor fuerte', 'sangre', 'desmayo', 'accidente'],
    'recordatorio': ['recordar', 'recordatorio', 'alerta', 'avisar', 'notificar', 'programar aviso'],
    'cita_futura': ['próxima cita', 'agendar cita', 'programar cita', 'reservar hora', 'pedir hora'],
    'seguimiento': ['cómo voy', 'evolución', 'progreso', 'mejorando', 'empeorando', 'seguimiento']
}

# Respuestas variadas para hacer el bot más humano
RESPONSE_VARIATIONS = {
    'greeting': [
        "¡Hola! 😊 ¿Cómo estás hoy?",
        "¡Qué bueno verte! 👋 ¿En qué puedo ayudarte?",
        "¡Hola! Espero que tengas un buen día 🌟",
        "¡Saludos! ¿Cómo te sientes hoy?"
    ],
    'not_understood': [
        "Disculpa, no estoy seguro de entender. ¿Podrías explicarme de otra manera?",
        "Hmm, no capté bien eso. ¿Puedes ser más específico?",
        "No estoy seguro de cómo ayudarte con eso. ¿Podrías reformular tu pregunta?",
        "Perdón, no entendí bien. ¿Te refieres a algo relacionado con tu salud?"
    ],
    'encouragement': [
        "¡Perfecto! 👍",
        "¡Excelente! 🌟",
        "¡Muy bien! ✨",
        "¡Genial! 🎉"
    ]
}

def detect_intent(text):
    """Detecta la intención del usuario basándose en palabras clave"""
    text_lower = text.lower()
    
    # Contar coincidencias por categoría
    intent_scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            intent_scores[intent] = score
    
    # Retornar la intención con mayor puntaje
    if intent_scores:
        return max(intent_scores, key=intent_scores.get)
    
    return 'unknown'

def get_user_context(user_id):
    """Obtiene el contexto de conversación del usuario"""
    return user_contexts.get(user_id, {})

def set_user_context(user_id, context_key, value):
    """Establece contexto de conversación para el usuario"""
    if user_id not in user_contexts:
        user_contexts[user_id] = {}
    user_contexts[user_id][context_key] = value

def get_random_response(category):
    """Obtiene una respuesta aleatoria de una categoría"""
    import random
    return random.choice(RESPONSE_VARIATIONS.get(category, ["¡Perfecto!"]))

def process_telegram_message(text, chat_id, user_id):
    """Procesa mensajes del bot de Telegram con lenguaje natural mejorado"""
    original_text = text
    text = text.lower().strip()
    
    # Intentar obtener información del usuario registrado
    user_info = get_telegram_user_info(user_id)
    user_name = user_info.get('nombre', 'Usuario') if user_info else 'Usuario'
    
    # Obtener contexto de conversación
    context = get_user_context(user_id)
    
    # Comando /start
    if text.startswith('/start'):
        if user_info:
            nombre = user_info.get('nombre', 'Usuario')
            apellido = user_info.get('apellido', '')
            nombre_completo = f"{nombre} {apellido}".strip()
            
            saludos = [
                f"¡Hola {nombre_completo}! 👋 ¡Qué alegría verte de nuevo! 😊",
                f"¡{nombre_completo}! 🌟 ¡Bienvenido de vuelta a MedConnect!",
                f"¡Hola {nombre}! 👨‍⚕️ Listo para ayudarte con tu salud hoy"
            ]
            
            import random
            saludo = random.choice(saludos)
            
            return f"""{saludo}

Como usuario registrado, estoy aquí para ayudarte con:

📋 **Consultas médicas** - Registra tus visitas al doctor
💊 **Medicamentos** - Lleva control de tus tratamientos  
🩺 **Exámenes** - Guarda resultados de laboratorio
👨‍👩‍👧‍👦 **Familiares** - Notifica a tus seres queridos
📊 **Historial** - Consulta toda tu información médica

Solo dime algo como:
• "Quiero registrar una consulta"
• "Necesito anotar un medicamento"
• "Tengo resultados de exámenes"
• "Muéstrame mi historial"

¿En qué puedo ayudarte hoy? 🤔"""
        else:
            return """¡Hola! 👋 Soy tu asistente personal de salud de MedConnect 🏥

Me encanta conocerte y estoy aquí para ayudarte a cuidar tu bienestar. 

📱 **¿Ya eres parte de la familia MedConnect?**
Si ya tienes cuenta, es súper fácil conectarnos:

1️⃣ Ve a tu perfil: https://medconnect.cl/profile
2️⃣ Haz clic en "Generar Código"
3️⃣ Comparte conmigo el código: `/codigo MED123456`

📝 **¿Primera vez aquí?**
¡Genial! Regístrate en: https://medconnect.cl/register

Una vez conectados, podremos:
📋 Registrar tus consultas médicas
💊 Organizar tus medicamentos  
🩺 Guardar resultados de exámenes
👨‍👩‍👧‍👦 Mantener informada a tu familia
📊 Crear tu historial médico personalizado

¿Hay algo en lo que pueda ayudarte mientras tanto? 😊"""
    
    # Comando /codigo
    elif text.startswith('/codigo'):
        return handle_telegram_code_linking(text, user_id)
    
    # Detectar intención del mensaje
    intent = detect_intent(text)
    
    # Manejar emergencias con prioridad
    if intent == 'emergencia':
        return """🚨 **EMERGENCIA DETECTADA** 🚨

Si estás en una situación de emergencia médica:

📞 **LLAMA INMEDIATAMENTE:**
• **131** - SAMU (Ambulancia)
• **133** - Bomberos
• **132** - Carabineros

🏥 **Ve al servicio de urgencias más cercano**

⚠️ **Recuerda:** Soy un asistente virtual y no puedo reemplazar la atención médica profesional en emergencias.

Una vez que estés seguro, estaré aquí para ayudarte con el seguimiento. 💙"""
    
    # Saludos
    elif intent == 'saludo' and not text.startswith('/'):
        greeting = get_random_response('greeting')
        if user_info:
            return f"{greeting} {user_name}! ¿En qué puedo ayudarte con tu salud hoy? 😊"
        else:
            return f"""{greeting}

Soy tu asistente de salud de MedConnect. Puedo ayudarte a:
📋 Registrar información médica
💊 Organizar medicamentos
🩺 Guardar exámenes
📊 Consultar tu historial

¿Te gustaría vincular tu cuenta primero? Solo necesitas ir a https://medconnect.cl/profile y generar un código. 

¿O prefieres que te ayude con algo específico? 🤔"""
    
    # Despedidas
    elif intent == 'despedida':
        despedidas = [
            f"¡Hasta pronto {user_name}! 👋 Cuídate mucho y no dudes en escribirme cuando necesites algo. 💙",
            f"¡Que tengas un excelente día {user_name}! 🌟 Estaré aquí cuando me necesites. 😊",
            f"¡Nos vemos pronto {user_name}! 👋 Recuerda cuidar tu salud. ¡Hasta la próxima! 💚"
        ]
        import random
        return random.choice(despedidas)
    
    # Consultas médicas
    elif intent == 'consulta':
        set_user_context(user_id, 'current_task', 'consulta')
        
        if user_info:
            encouragement = get_random_response('encouragement')
            return f"""{encouragement} {user_name}, veo que quieres registrar una consulta médica. 📋

Para crear un registro completo, me gustaría que me compartieras:

🩺 **Detalles de la consulta:**
1️⃣ ¿Cuándo fue? (fecha)
2️⃣ ¿Con qué doctor te atendiste?
3️⃣ ¿Cuál es su especialidad?
4️⃣ ¿Qué diagnóstico te dieron?
5️⃣ ¿Te recetaron algún tratamiento?

Puedes contarme todo junto o paso a paso, como prefieras. Lo importante es que quede bien registrado en tu historial personal. 😊

¿Empezamos? 🤔"""
        else:
            return """📋 ¡Me encanta que quieras registrar tu consulta médica! Es súper importante llevar un buen control.

Para poder guardar esta información en tu historial personal, necesitaríamos conectar tu cuenta primero.

**Datos que necesito para la consulta:**
1️⃣ Fecha de la consulta
2️⃣ Nombre del médico
3️⃣ Especialidad
4️⃣ Diagnóstico recibido
5️⃣ Tratamiento indicado

💡 **¿Tienes cuenta en MedConnect?**
Ve a https://medconnect.cl/profile, genera tu código y compártelo conmigo.

Mientras tanto, puedes contarme los detalles y los guardaré temporalmente. ¿Te parece? 😊"""
    
    # Medicamentos
    elif intent == 'medicamento':
        set_user_context(user_id, 'current_task', 'medicamento')
        
        if user_info:
            encouragement = get_random_response('encouragement')
            return f"""{encouragement} {user_name}! Organizar tus medicamentos es fundamental para tu salud. 💊

Para registrar correctamente tu medicamento, necesito conocer:

💉 **Información del medicamento:**
1️⃣ ¿Cómo se llama?
2️⃣ ¿Qué dosis tomas? (ej: 50mg, 1 tableta)
3️⃣ ¿Cada cuánto tiempo? (ej: cada 8 horas, 2 veces al día)
4️⃣ ¿Qué médico te lo recetó?
5️⃣ ¿Para qué es? (opcional)

Cuéntame todo lo que sepas y lo organizaremos en tu perfil para que nunca se te olvide. 😊

¿Cuál es el medicamento? 🤔"""
        else:
            return """💊 ¡Qué responsable eres cuidando tu tratamiento! Me parece genial que quieras registrar tus medicamentos.

**Para un registro completo necesito:**
1️⃣ Nombre del medicamento
2️⃣ Dosis que tomas
3️⃣ Frecuencia (cada cuánto tiempo)
4️⃣ Médico que lo recetó
5️⃣ Para qué es el tratamiento

💡 **Para guardarlo en tu historial permanente:**
Necesitarías vincular tu cuenta desde https://medconnect.cl/profile

Pero puedes contarme los detalles ahora y te ayudo a organizarlos. ¿Cuál es el medicamento? 😊"""
    
    # Exámenes
    elif intent == 'examen':
        set_user_context(user_id, 'current_task', 'examen')
        
        if user_info:
            encouragement = get_random_response('encouragement')
            return f"""{encouragement} {user_name}! Los exámenes son súper importantes para monitorear tu salud. 🩺

Para registrar tu examen correctamente, me gustaría saber:

🔬 **Detalles del examen:**
1️⃣ ¿Qué tipo de examen fue? (sangre, orina, radiografía, etc.)
2️⃣ ¿Cuándo te lo hiciste?
3️⃣ ¿En qué laboratorio o centro médico?
4️⃣ ¿Cuáles fueron los resultados principales?
5️⃣ ¿Algún valor fuera de lo normal?

Si tienes los resultados en papel o digital, también puedes subir la imagen a tu perfil web más tarde.

¿Me cuentas sobre tu examen? 🤔"""
        else:
            return """🩺 ¡Excelente que quieras registrar tus exámenes! Es clave para el seguimiento de tu salud.

**Información que necesito:**
1️⃣ Tipo de examen realizado
2️⃣ Fecha cuando te lo hiciste
3️⃣ Laboratorio o centro médico
4️⃣ Resultados principales
5️⃣ Valores importantes o anormales

💡 **Para mantener un historial completo:**
Te recomiendo vincular tu cuenta en https://medconnect.cl/profile

Mientras tanto, cuéntame sobre tu examen y te ayudo a organizarlo. ¿Qué examen te hiciste? 😊"""
    
    # Historial
    elif intent == 'historial':
        if user_info:
            return f"""📊 ¡Hola {user_name}! Tu historial médico está siempre disponible para ti.

**Para ver toda tu información completa:**
🌐 Visita tu dashboard: https://medconnect.cl/patient

**Ahí encontrarás:**
✅ Todas tus consultas médicas organizadas
✅ Lista completa de medicamentos actuales
✅ Resultados de exámenes con fechas
✅ Información de familiares registrados
✅ Gráficos y estadísticas de tu salud

**También puedes preguntarme directamente:**
• "¿Cuáles son mis últimas consultas?"
• "¿Qué medicamentos estoy tomando?"
• "¿Cuándo fue mi último examen?"
• "¿Tengo alguna cita próxima?"

¿Qué te gustaría consultar específicamente? 🤔"""
        else:
            return """📊 ¡Me encantaría mostrarte tu historial médico! Pero primero necesitamos conectar tu cuenta.

**Una vez vinculada, tendrás acceso a:**
✅ Historial completo de consultas
✅ Registro de todos tus medicamentos
✅ Resultados de exámenes organizados
✅ Información de contactos de emergencia
✅ Estadísticas de tu salud

**¿Ya tienes cuenta en MedConnect?**
🔗 Ve a: https://medconnect.cl/profile y genera tu código

**¿Primera vez aquí?**
📝 Regístrate en: https://medconnect.cl/register

Una vez conectados, podrás consultar toda tu información médica cuando quieras. ¿Te ayudo con la vinculación? 😊"""
    
    # Ayuda
    elif intent == 'ayuda' or text in ['help', '/help']:
        if user_info:
            return f"""🤝 ¡Por supuesto {user_name}! Estoy aquí para ayudarte.

**Esto es lo que puedo hacer por ti:**

📋 **Consultas médicas**
• "Registrar una consulta"
• "Anotar visita al doctor"

💊 **Medicamentos**  
• "Agregar un medicamento"
• "Registrar tratamiento"

🩺 **Exámenes**
• "Guardar resultados de examen"
• "Registrar análisis de laboratorio"

📊 **Historial**
• "Ver mi historial"
• "Mostrar mis datos médicos"

🆘 **Comandos especiales:**
• `/start` - Menú principal
• `/codigo MED123456` - Vincular cuenta

Solo háblame naturalmente, como "Quiero registrar una consulta" o "Necesito anotar un medicamento". ¡Entiendo el lenguaje cotidiano! 😊

¿En qué te ayudo ahora? 🤔"""
        else:
            return """🤝 ¡Claro! Te explico todo lo que puedo hacer por ti.

**Mis funcionalidades principales:**

📋 **Registro médico**
• Consultas con doctores
• Medicamentos y tratamientos
• Resultados de exámenes
• Información de familiares

📊 **Consulta de información**
• Historial médico completo
• Medicamentos actuales
• Próximas citas

🔗 **Vinculación de cuenta**
• Conectar con tu perfil de MedConnect
• Sincronizar información

**Para aprovechar al máximo:**
1️⃣ Vincula tu cuenta: https://medconnect.cl/profile
2️⃣ Genera tu código de vinculación
3️⃣ Compártelo conmigo: `/codigo MED123456`

¡Habla conmigo naturalmente! Entiendo frases como "quiero registrar una consulta" o "muéstrame mi historial".

¿Te ayudo con algo específico? 😊"""
    
    # Mensajes no entendidos
    else:
        not_understood = get_random_response('not_understood')
        
        if user_info:
            return f"""{not_understood}

{user_name}, puedo ayudarte con:
📋 **Consultas médicas** - "registrar consulta"
💊 **Medicamentos** - "anotar medicamento"  
🩺 **Exámenes** - "guardar examen"
📊 **Historial** - "ver mi historial"

O escribe `/start` para ver el menú completo.

¿Podrías decirme de otra manera en qué te ayudo? 😊"""
        else:
            return f"""{not_understood}

Puedo ayudarte con temas de salud como:
📋 Registrar consultas médicas
💊 Organizar medicamentos
🩺 Guardar exámenes
📊 Consultar historial médico

💡 **Tip:** Para una experiencia completa, vincula tu cuenta desde https://medconnect.cl/profile

¿Hay algo específico sobre tu salud en lo que pueda ayudarte? 🤔"""

def get_telegram_user_info(telegram_user_id):
    """Obtiene información del usuario registrado por su ID de Telegram"""
    try:
        if not auth_manager:
            return None
            
        user_info = auth_manager.get_user_by_telegram_id(telegram_user_id)
        return user_info
    except Exception as e:
        logger.error(f"Error obteniendo info de usuario Telegram {telegram_user_id}: {e}")
        return None

def handle_account_linking(text, telegram_user_id):
    """Maneja la vinculación de cuenta de Telegram"""
    try:
        parts = text.split()
        if len(parts) < 2:
            return """❌ Formato incorrecto. 

**Uso correcto:**
`/vincular tu-email@ejemplo.com`

**Ejemplo:**
`/vincular maria.gonzalez@gmail.com`

Asegúrate de usar el mismo email con el que te registraste en MedConnect."""
        
        email = parts[1].strip()
        
        # Validar formato de email básico
        if '@' not in email or '.' not in email:
            return """❌ El email no parece válido.

**Formato esperado:**
`/vincular tu-email@ejemplo.com`

Por favor verifica e intenta de nuevo."""
        
        if not auth_manager:
            return "❌ Sistema de autenticación no disponible temporalmente. Intenta más tarde."
        
        # Verificar si el usuario existe
        user_data = auth_manager.get_user_by_email(email)
        if not user_data:
            return f"""❌ No encontré ninguna cuenta con el email: `{email}`

**¿Posibles soluciones:**
1. Verifica que escribiste correctamente tu email
2. Si aún no tienes cuenta, regístrate en: https://medconnect.cl/register
3. Intenta de nuevo: `/vincular tu-email-correcto@ejemplo.com`"""
        
        # Intentar vincular la cuenta
        success, message, user_info = auth_manager.link_telegram_account(email, telegram_user_id)
        
        if success and user_info:
            nombre = user_info.get('nombre', 'Usuario')
            apellido = user_info.get('apellido', '')
            return f"""✅ ¡Cuenta vinculada exitosamente!

¡Hola {nombre} {apellido}! 🎉

Tu cuenta de Telegram ahora está conectada con MedConnect. A partir de ahora:

✨ **Experiencia personalizada**
📋 Historial médico completo
💊 Seguimiento de medicamentos
🩺 Registro de exámenes
👨‍👩‍👧‍👦 Notificaciones familiares

Escribe `/start` para comenzar con tu experiencia personalizada."""
        else:
            return f"""❌ {message}

**Si el problema persiste:**
1. Verifica tu email: `{email}`
2. Contacta soporte si necesitas ayuda
3. O intenta registrarte en: https://medconnect.cl/register"""
            
    except Exception as e:
        logger.error(f"Error en vinculación de cuenta: {e}")
        return """❌ Error interno al vincular cuenta.

Por favor intenta de nuevo en unos minutos o contacta soporte."""

def send_telegram_message(telegram_id, message):
    """Envía un mensaje a través del bot de Telegram"""
    try:
        # Token del bot
        BOT_TOKEN = "7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck"  # Token correcto del bot
        
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': str(telegram_id),  # Asegurar que sea string
            'text': message,
            'parse_mode': 'HTML'
        }
        
        import requests  # Asegurar import local
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"✅ Mensaje enviado a Telegram ID: {telegram_id}")
            return True
        else:
            logger.error(f"❌ Error enviando mensaje a Telegram: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje de Telegram: {e}")
        return False

# Configurar webhook del bot
@app.route('/setup-webhook')
def setup_webhook():
    """Configura el webhook del bot de Telegram"""
    try:
        url = f"https://api.telegram.org/bot{app.config['TELEGRAM_BOT_TOKEN']}/setWebhook"
        data = {
            'url': app.config['TELEGRAM_WEBHOOK_URL']
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return jsonify({
            'status': 'success',
            'webhook_url': app.config['TELEGRAM_WEBHOOK_URL'],
            'response': response.json()
        })
    except Exception as e:
        logger.error(f"Error configurando webhook: {e}")
        return jsonify({'error': str(e)}), 500

# Ruta de salud para Railway
@app.route('/health')
def health_check():
    """Health check para Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/debug-static')
def debug_static():
    """Endpoint para debuggear archivos estáticos"""
    try:
        static_path = os.path.join(app.root_path, 'static')
        debug_info = {
            'static_directory': static_path,
            'static_exists': os.path.exists(static_path),
            'app_root_path': app.root_path,
            'whitenoise_active': hasattr(app, 'wsgi_app') and 'WhiteNoise' in str(type(app.wsgi_app)),
            'auth_manager_available': auth_manager is not None,
            'environment': {
                'FLASK_ENV': os.environ.get('FLASK_ENV'),
                'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT'),
                'PORT': os.environ.get('PORT'),
                'GOOGLE_SHEETS_ID': bool(os.environ.get('GOOGLE_SHEETS_ID')),
                'TELEGRAM_BOT_TOKEN': bool(os.environ.get('TELEGRAM_BOT_TOKEN')),
                'GOOGLE_SERVICE_ACCOUNT_JSON': bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))
            },
            'files': []
        }
        
        # Listar archivos críticos
        critical_files = [
            'css/styles.css',
            'js/app.js', 
            'images/logo.png'
        ]
        
        for file_rel_path in critical_files:
            file_path = os.path.join(static_path, file_rel_path)
            debug_info['files'].append({
                'path': file_rel_path,
                'full_path': file_path,
                'exists': os.path.exists(file_path),
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            })
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/test-complete')
def test_complete():
    """Página de diagnóstico completa"""
    logger.info("🔍 Accediendo a página de diagnóstico completa")
    
    # Verificar estado del sistema
    auth_status = "✅ Disponible" if auth_manager else "❌ No disponible"
    
    # Verificar archivos estáticos
    static_files = []
    critical_files = ['css/styles.css', 'js/app.js', 'images/logo.png']
    for file_path in critical_files:
        full_path = os.path.join(app.root_path, 'static', file_path)
        static_files.append({
            'path': file_path,
            'exists': os.path.exists(full_path),
            'size': os.path.getsize(full_path) if os.path.exists(full_path) else 0
        })
    
    # Verificar variables de entorno
    env_vars = {
        'GOOGLE_SERVICE_ACCOUNT_JSON': bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')),
        'GOOGLE_SHEETS_ID': bool(os.environ.get('GOOGLE_SHEETS_ID')),
        'TELEGRAM_BOT_TOKEN': bool(os.environ.get('TELEGRAM_BOT_TOKEN')),
        'PORT': os.environ.get('PORT', 'No definido')
    }
    
    html = f'''
     <!DOCTYPE html>
     <html>
     <head>
         <title>MedConnect - Diagnóstico Completo</title>
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
             <h1>🏥 MedConnect - Diagnóstico Completo</h1>
             
             <div class="status {'success' if auth_manager else 'error'}">
                 <strong>🔐 AuthManager:</strong> {auth_status}
             </div>
             
             <h2>🔧 Variables de Entorno</h2>
             <table>
                 <tr><th>Variable</th><th>Estado</th></tr>'''
    
    for var, status in env_vars.items():
        status_icon = "✅" if status else "❌"
        html += f'<tr><td>{var}</td><td>{status_icon} {status}</td></tr>'
    
    html += f'''
             </table>
             
             <h2>📁 Archivos Estáticos</h2>
             <table>
                 <tr><th>Archivo</th><th>Existe</th><th>Tamaño</th></tr>'''
    
    for file_info in static_files:
        exists_icon = "✅" if file_info['exists'] else "❌"
        size_text = f"{file_info['size']} bytes" if file_info['exists'] else "N/A"
        html += f'<tr><td>{file_info["path"]}</td><td>{exists_icon}</td><td>{size_text}</td></tr>'
    
    html += f'''
             </table>
             
             <h2>🔗 Pruebas Funcionales</h2>
             <a href="/" class="btn">🏠 Página Principal</a>
             <a href="/login" class="btn">🔐 Login</a>
             <a href="/register" class="btn">📝 Registro</a>
             <a href="/debug-static" class="btn">🔧 Debug JSON</a>
             
             <h2>🖼️ Prueba Visual</h2>
             <div class="status info">
                 <strong>Logo:</strong><br>
                 <img src="/static/images/logo.png" alt="Logo" style="max-width: 150px;" 
                      onload="document.getElementById('img-status').innerHTML='✅ Imagen cargada correctamente'"
                      onerror="document.getElementById('img-status').innerHTML='❌ Error cargando imagen'">
                 <div id="img-status">⏳ Cargando imagen...</div>
             </div>
             
             <h2>🎨 Prueba CSS</h2>
             <link rel="stylesheet" href="/static/css/styles.css">
             <div class="hero" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center;">
                 <h3>Si ves este gradiente y texto centrado, CSS funciona ✅</h3>
             </div>
             
             <h2>📜 Información del Sistema</h2>
             <div class="code">
                 <strong>Ruta de la app:</strong> {app.root_path}<br>
                 <strong>Carpeta static:</strong> {app.static_folder}<br>
                 <strong>URL static:</strong> {app.static_url_path}<br>
                 <strong>WhiteNoise:</strong> {'✅ Activo' if hasattr(app, 'wsgi_app') and 'WhiteNoise' in str(type(app.wsgi_app)) else '❌ No activo'}
             </div>
             
             <script>
                 // Verificar JavaScript
                 document.addEventListener('DOMContentLoaded', function() {{
                     const jsStatus = document.createElement('div');
                     jsStatus.className = 'status success';
                     jsStatus.innerHTML = '✅ JavaScript funcionando correctamente';
                     document.body.appendChild(jsStatus);
                 }});
             </script>
         </div>
     </body>
     </html>
     '''
    return html

# Ruta para favicon
@app.route('/favicon.ico')
def favicon():
    """Servir favicon"""
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'), 'logo.png', mimetype='image/png')

# Ruta para servir archivos estáticos en producción
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servir archivos estáticos en producción (CSS, JS, imágenes)"""
    try:
        static_path = os.path.join(app.root_path, 'static')
        file_path = os.path.join(static_path, filename)
        
        logger.info(f"📁 Solicitando archivo estático: {filename}")
        logger.info(f"📂 Ruta completa: {file_path}")
        logger.info(f"📋 Archivo existe: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            # Determinar tipo MIME basado en la extensión
            mimetype = None
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                mimetype = f'image/{filename.split(".")[-1].lower()}'
                if mimetype == 'image/jpg':
                    mimetype = 'image/jpeg'
            elif filename.lower().endswith('.css'):
                mimetype = 'text/css'
            elif filename.lower().endswith('.js'):
                mimetype = 'application/javascript'
            elif filename.lower().endswith('.ico'):
                mimetype = 'image/x-icon'
            
            # Crear respuesta con headers apropiados
            response = send_from_directory(static_path, filename, mimetype=mimetype)
            
            # Agregar headers de cache para mejor rendimiento
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico')):
                response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 año para imágenes
            elif filename.lower().endswith(('.css', '.js')):
                response.headers['Cache-Control'] = 'public, max-age=86400'  # 1 día para CSS/JS
            
            logger.info(f"✅ Archivo servido exitosamente: {filename} (tipo: {mimetype})")
            return response
        else:
            logger.error(f"❌ Archivo no encontrado: {file_path}")
            return "Archivo no encontrado", 404
            
    except Exception as e:
        logger.error(f"❌ Error sirviendo archivo estático {filename}: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return "Error interno del servidor", 500

# Rutas para manejo de archivos médicos
@app.route('/uploads/medical_files/<filename>')
@login_required
def uploaded_file(filename):
    """Servir archivos médicos subidos"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/uploads/certifications/<filename>')
@login_required
def certification_file(filename):
    """Servir archivos de certificaciones"""
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'certifications'), filename)

@app.route('/api/patient/<patient_id>/exams/upload', methods=['POST'])
@login_required
def upload_exam_file(patient_id):
    """Subir archivo para un examen"""
    try:
        # Verificar que el usuario solo pueda subir sus propios archivos
        if str(session.get('user_id')) != str(patient_id):
            return jsonify({'error': 'No autorizado'}), 403
        
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        file = request.files['file']
        exam_id = request.form.get('exam_id')
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not exam_id:
            return jsonify({'error': 'ID de examen requerido'}), 400
        
        if file and allowed_file(file.filename):
            # Generar nombre único para el archivo
            filename = generate_unique_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Guardar archivo
            file.save(filepath)
            
            # Actualizar la base de datos con la URL del archivo
            spreadsheet = get_spreadsheet()
            if not spreadsheet:
                # Si no se puede actualizar la BD, eliminar el archivo
                os.remove(filepath)
                return jsonify({'error': 'Error conectando con la base de datos'}), 500
            
            try:
                worksheet = spreadsheet.worksheet('Examenes')
                all_values = worksheet.get_all_values()
                
                # Buscar la fila del examen
                exam_row = None
                if len(all_values) > 1:
                    for i, row in enumerate(all_values[1:], start=2):
                        if len(row) > 1 and str(row[0]) == str(exam_id) and str(row[1]) == str(patient_id):
                            exam_row = i
                            break
                
                if exam_row:
                    # Obtener URLs existentes de archivos
                    current_file_urls = all_values[exam_row - 1][7] if len(all_values[exam_row - 1]) > 7 else ''
                    
                    # Agregar nueva URL a las existentes
                    new_file_url = f"/uploads/medical_files/{filename}"
                    
                    if current_file_urls and current_file_urls.strip():
                        # Si ya hay archivos, agregar el nuevo separado por coma
                        updated_file_urls = f"{current_file_urls},{new_file_url}"
                    else:
                        # Si no hay archivos, usar solo el nuevo
                        updated_file_urls = new_file_url
                    
                    # Actualizar la columna file_url (columna 8, índice H)
                    worksheet.update_cell(exam_row, 8, updated_file_urls)
                    
                    logger.info(f"✅ Archivo agregado al examen {exam_id}: {filename}")
                    logger.info(f"📎 URLs de archivos actualizadas: {updated_file_urls}")
                    
                    return jsonify({
                        'success': True, 
                        'message': 'Archivo subido exitosamente',
                        'file_url': new_file_url,
                        'all_file_urls': updated_file_urls,
                        'filename': filename
                    })
                else:
                    # Si no se encuentra el examen, eliminar el archivo
                    os.remove(filepath)
                    return jsonify({'error': 'Examen no encontrado'}), 404
                    
            except gspread.WorksheetNotFound:
                os.remove(filepath)
                return jsonify({'error': 'Hoja de exámenes no encontrada'}), 404
        else:
            return jsonify({'error': 'Tipo de archivo no permitido. Formatos permitidos: PDF, PNG, JPG, JPEG, GIF, BMP, TIFF, DCM, DICOM, DOC, DOCX, TXT'}), 400
            
    except Exception as e:
        logger.error(f"Error subiendo archivo: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/api/admin/link-existing-users', methods=['POST'])
@login_required
def link_existing_users():
    """Función de administración para vincular usuarios existentes con sus datos del bot"""
    try:
        # Solo permitir a administradores (por ahora cualquier usuario logueado puede usar esto)
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        users_worksheet = spreadsheet.worksheet('Usuarios')
        all_records = users_worksheet.get_all_records()
        
        results = {
            'users_checked': 0,
            'users_linked': 0,
            'duplicates_found': 0,
            'errors': []
        }
        
        # Buscar usuarios duplicados o sin vincular
        web_users = []  # Usuarios de la plataforma web
        bot_users = []  # Usuarios creados por el bot
        
        for record in all_records:
            user_id = record.get('id') or record.get('user_id', '')
            telegram_id = record.get('telegram_id', '')
            
            if str(user_id).startswith('USR_'):
                # Usuario creado por el bot
                bot_users.append(record)
            else:
                # Usuario de la plataforma web
                web_users.append(record)
            
            results['users_checked'] += 1
        
        # Intentar vincular usuarios basándose en telegram_id
        for bot_user in bot_users:
            bot_telegram_id = bot_user.get('telegram_id', '')
            bot_user_id = bot_user.get('user_id', '')
            
            if bot_telegram_id:
                # Buscar si hay un usuario web que debería estar vinculado a este telegram_id
                matching_web_user = None
                for web_user in web_users:
                    web_telegram_id = web_user.get('telegram_id', '')
                    
                    # Si el usuario web tiene el mismo telegram_id, ya está vinculado
                    if web_telegram_id == bot_telegram_id:
                        matching_web_user = web_user
                        break
                
                # Si encontramos un usuario web con el mismo telegram_id, reportar
                if matching_web_user:
                    results['users_linked'] += 1
                    logger.info(f"✅ Usuario ya vinculado: {matching_web_user.get('nombre')} con telegram_id {bot_telegram_id}")
                else:
                    # Reportar usuario del bot sin vincular
                    results['duplicates_found'] += 1
                    logger.info(f"⚠️ Usuario del bot sin vincular: {bot_user_id} con telegram_id {bot_telegram_id}")
        
        return jsonify({
            'success': True,
            'message': 'Análisis de vinculación completado',
            'results': results,
            'web_users': len(web_users),
            'bot_users': len(bot_users),
            'recommendation': 'Los usuarios pueden vincular sus cuentas manualmente desde la plataforma web'
        })
        
    except Exception as e:
        logger.error(f"Error analizando usuarios: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/user/link-telegram', methods=['POST'])
@login_required
def link_telegram():
    """Vincula la cuenta web del usuario con su cuenta de Telegram"""
    logger.info("🔍 Iniciando link_telegram...")
    try:
        logger.info("📝 Obteniendo datos del request...")
        data = request.get_json()
        logger.info(f"📊 Datos recibidos: {data}")
        
        telegram_id = data.get('telegram_id', '').strip()
        logger.info(f"📱 Telegram ID: {telegram_id}")
        
        if not telegram_id:
            logger.warning("❌ Telegram ID vacío")
            return jsonify({'error': 'ID de Telegram requerido'}), 400
        
        # Obtener el ID del usuario web actual
        user_id = session.get('user_id')
        logger.info(f"👤 User ID de la sesión: {user_id}")
        
        if not user_id:
            logger.warning("❌ Usuario no autenticado")
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        logger.info("🔗 Conectando con Google Sheets...")
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            logger.error("❌ Error conectando con Google Sheets")
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        logger.info("👤 Obteniendo información del usuario actual...")
        # Verificar que auth_manager esté disponible
        if not auth_manager:
            logger.error("❌ AuthManager no disponible")
            return jsonify({'error': 'Sistema de autenticación no disponible'}), 500
        
        # Obtener información del usuario actual
        try:
            user_info = auth_manager.get_user_by_id(user_id)
            logger.info(f"📝 User info obtenida: {user_info}")
        except Exception as e:
            logger.error(f"❌ Error obteniendo user_info: {e}")
            return jsonify({'error': f'Error obteniendo información del usuario: {str(e)}'}), 500
        
        if not user_info:
            logger.error("❌ Usuario no encontrado en la base de datos")
            return jsonify({'error': 'Información de usuario no encontrada'}), 404
        
        user_name = f"{user_info.get('nombre', '')} {user_info.get('apellido', '')}".strip()
        if not user_name:
            user_name = user_info.get('email', 'Usuario')
        
        logger.info(f"✅ Nombre del usuario: {user_name}")
        
        # Actualizar la hoja de Usuarios para agregar el telegram_id
        try:
            logger.info("📄 Accediendo a la hoja de Usuarios...")
            users_worksheet = spreadsheet.worksheet('Usuarios')
            all_records = users_worksheet.get_all_records()
            logger.info(f"📊 Total de registros de usuarios: {len(all_records)}")
            
            user_row = None
            for i, record in enumerate(all_records, start=2):  # Start from row 2 (after headers)
                record_id = record.get('id') or record.get('user_id', '')
                if str(record_id) == str(user_id):
                    user_row = i
                    logger.info(f"✅ Usuario encontrado en fila: {user_row}")
                    break
            
            if user_row:
                logger.info("🔍 Buscando columna telegram_id...")
                # Buscar la columna telegram_id
                headers = users_worksheet.row_values(1)
                telegram_col = None
                
                if 'telegram_id' in headers:
                    telegram_col = headers.index('telegram_id') + 1
                    logger.info(f"✅ Columna telegram_id encontrada en posición: {telegram_col}")
                else:
                    # Agregar la columna telegram_id si no existe
                    logger.info("➕ Agregando columna telegram_id...")
                    users_worksheet.update_cell(1, len(headers) + 1, 'telegram_id')
                    telegram_col = len(headers) + 1
                    logger.info(f"✅ Columna telegram_id agregada en posición: {telegram_col}")
                
                logger.info(f"💾 Actualizando telegram_id en fila {user_row}, columna {telegram_col}...")
                # Actualizar el telegram_id del usuario
                users_worksheet.update_cell(user_row, telegram_col, telegram_id)
                
                logger.info(f"✅ Usuario {user_id} ({user_name}) vinculado con Telegram ID: {telegram_id}")
                
                # 🚀 ENVIAR MENSAJE DE BIENVENIDA AUTOMÁTICO
                welcome_message = f"""🎉 <b>¡Cuenta Vinculada Exitosamente!</b>

¡Hola <b>{user_name}</b>! 👋

Tu cuenta de MedConnect ha sido vinculada con Telegram correctamente.

✅ <b>Cuenta Web:</b> {user_info.get('email', 'N/A')}
✅ <b>Telegram ID:</b> <code>{telegram_id}</code>

Ahora puedes:
📋 Registrar consultas, medicamentos y exámenes desde Telegram
📊 Ver todo tu historial en la plataforma web
🔄 Los datos se sincronizan automáticamente

<i>¡Gracias por usar MedConnect!</i> 💙"""
                
                logger.info("📨 Enviando mensaje de bienvenida...")
                # Intentar enviar el mensaje
                message_sent = send_telegram_message(telegram_id, welcome_message)
                logger.info(f"📤 Mensaje enviado: {message_sent}")
                
                # Verificar si ya hay datos del bot para este telegram_id
                try:
                    logger.info("🔍 Buscando exámenes del bot...")
                    examenes_worksheet = spreadsheet.worksheet('Examenes')
                    
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
                    
                    # Buscar exámenes guardados por usuarios del bot con este telegram_id
                    bot_user_ids = []
                    for user_record in all_records:
                        if str(user_record.get('telegram_id', '')) == str(telegram_id):
                            bot_user_id = user_record.get('user_id', '')
                            if str(bot_user_id).startswith('USR_'):
                                bot_user_ids.append(bot_user_id)
                    
                    exams_found = 0
                    for exam_record in examenes_records:
                        if exam_record.get('user_id', '') in bot_user_ids:
                            exams_found += 1
                    
                    logger.info(f"📊 Exámenes encontrados: {exams_found}, Bot users: {len(bot_user_ids)}")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Cuenta de Telegram vinculada exitosamente',
                        'telegram_id': telegram_id,
                        'user_name': user_name,
                        'exams_found': exams_found,
                        'bot_users_found': len(bot_user_ids),
                        'welcome_message_sent': message_sent
                    })
                    
                except gspread.WorksheetNotFound:
                    logger.warning("⚠️ Hoja de Examenes no encontrada")
                    return jsonify({
                        'success': True,
                        'message': 'Cuenta de Telegram vinculada exitosamente',
                        'telegram_id': telegram_id,
                        'user_name': user_name,
                        'exams_found': 0,
                        'bot_users_found': 0,
                        'welcome_message_sent': message_sent
                    })
            else:
                logger.error(f"❌ Usuario {user_id} no encontrado en la hoja de Usuarios")
                return jsonify({'error': 'Usuario no encontrado'}), 404
                
        except Exception as e:
            logger.error(f"❌ Error vinculando Telegram: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error en link_telegram: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/user/telegram-status')
@login_required
def get_telegram_status():
    """Obtiene el estado de vinculación con Telegram del usuario actual"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        users_worksheet = spreadsheet.worksheet('Usuarios')
        all_records = users_worksheet.get_all_records()
        
        telegram_id = None
        for record in all_records:
            if str(record.get('id', '')) == str(user_id):
                telegram_id = record.get('telegram_id', '')
                break
        
        # Convertir telegram_id a string si es necesario
        if telegram_id and not isinstance(telegram_id, str):
            telegram_id = str(telegram_id)
        
        is_linked = bool(telegram_id and telegram_id.strip())
        
        # Si está vinculado, verificar si hay datos del bot
        exams_count = 0
        if is_linked:
            try:
                examenes_worksheet = spreadsheet.worksheet('Examenes')
                
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
                    if str(user_record.get('telegram_id', '')) == str(telegram_id):
                        bot_user_id = user_record.get('user_id', '')
                        if bot_user_id.startswith('USR_'):
                            bot_user_ids.append(bot_user_id)
                
                for exam_record in examenes_records:
                    if exam_record.get('user_id', '') in bot_user_ids:
                        exams_count += 1
                        
            except gspread.WorksheetNotFound:
                pass
        
        return jsonify({
            'is_linked': is_linked,
            'telegram_id': telegram_id if is_linked else None,
            'exams_from_bot': exams_count
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado Telegram: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/patient/<patient_id>/stats')
def get_patient_stats(patient_id):
    """Obtiene las estadísticas del paciente para el dashboard"""
    try:
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500
        
        stats = {
            'consultations': 0,
            'medications': 0,
            'exams': 0,
            'health_score': 95  # Valor base, se puede calcular dinámicamente
        }
        
        # Contar consultas
        try:
            consultations_worksheet = spreadsheet.worksheet('Consultas')
            all_values = consultations_worksheet.get_all_values()
            
            if len(all_values) > 1:
                for row in all_values[1:]:
                    if len(row) > 1 and str(row[1]) == str(patient_id):
                        stats['consultations'] += 1
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Consultas' no encontrada")
        
        # Contar medicamentos activos
        try:
            medications_worksheet = spreadsheet.worksheet('Medicamentos')
            all_values = medications_worksheet.get_all_values()
            
            if len(all_values) > 1:
                for row in all_values[1:]:
                    if len(row) > 1 and str(row[1]) == str(patient_id):
                        # Solo contar medicamentos activos
                        status = row[8] if len(row) > 8 else 'activo'
                        if status.lower() == 'activo':
                            stats['medications'] += 1
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Medicamentos' no encontrada")
        
        # Contar exámenes
        try:
            exams_worksheet = spreadsheet.worksheet('Examenes')
            all_values = exams_worksheet.get_all_values()
            
            if len(all_values) > 1:
                for row in all_values[1:]:
                    if len(row) > 1 and str(row[1]) == str(patient_id):
                        stats['exams'] += 1
        except gspread.WorksheetNotFound:
            logger.warning("📝 Hoja 'Examenes' no encontrada")
        
        # Calcular puntuación de salud básica
        # Fórmula simple: base 85% + bonificaciones
        health_score = 85
        
        # Bonificación por tener consultas recientes
        if stats['consultations'] > 0:
            health_score += min(stats['consultations'] * 2, 10)  # Máximo +10%
        
        # Bonificación por seguir tratamiento
        if stats['medications'] > 0:
            health_score += min(stats['medications'] * 3, 5)  # Máximo +5%
        
        # Asegurar que no exceda 100%
        stats['health_score'] = min(health_score, 100)
        
        logger.info(f"📊 Estadísticas para paciente {patient_id}: {stats}")
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

def convert_date_format(date_str):
    """Convierte fecha de DD/MM/YYYY a YYYY-MM-DD para compatibilidad web"""
    if not date_str or date_str.strip() == '':
        return ''
    
    try:
        # Si ya está en formato YYYY-MM-DD, dejarlo como está
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str
        
        # Si está en formato DD/MM/YYYY, convertir
        if len(date_str) == 10 and date_str[2] == '/' and date_str[5] == '/':
            day, month, year = date_str.split('/')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Si está en formato D/M/YYYY o variaciones, normalizar
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                day, month, year = parts
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Si no coincide con ningún patrón conocido, devolver como está
        return date_str
        
    except Exception as e:
        logger.warning(f"⚠️ Error convirtiendo fecha '{date_str}': {e}")
        return date_str

# Configuración mejorada para producción
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Configuración para dominio personalizado
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN', 'localhost:5000')
app.config['SERVER_NAME'] = None  # Permitir cualquier host
app.config['PREFERRED_URL_SCHEME'] = 'https' if 'medconnect.cl' in CUSTOM_DOMAIN else 'http'

# Configuración de seguridad para HTTPS
if app.config['PREFERRED_URL_SCHEME'] == 'https':
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

@app.route('/debug-env')
def debug_env():
    """Endpoint para debugging de variables de entorno"""
    import os
    import json
    
    # Obtener todas las variables de entorno
    all_env_vars = dict(os.environ)
    
    # Variables específicas que necesitamos
    target_vars = {
        'GOOGLE_SERVICE_ACCOUNT_JSON': os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', 'NO ENCONTRADA'),
        'GOOGLE_SHEETS_ID': os.environ.get('GOOGLE_SHEETS_ID', 'NO ENCONTRADA'),
        'TELEGRAM_BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN', 'NO ENCONTRADA'),
        'PORT': os.environ.get('PORT', 'NO ENCONTRADA'),
        'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT', 'NO ENCONTRADA'),
        'RAILWAY_PROJECT_ID': os.environ.get('RAILWAY_PROJECT_ID', 'NO ENCONTRADA'),
        'RAILWAY_SERVICE_ID': os.environ.get('RAILWAY_SERVICE_ID', 'NO ENCONTRADA'),
    }
    
    # Filtrar variables de Railway para ver si está funcionando
    railway_vars = {k: v for k, v in all_env_vars.items() if k.startswith('RAILWAY')}
    
    # Crear respuesta HTML
    html = f'''
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
            <h1>🔍 Debug Variables de Entorno - MedConnect</h1>
            
            <div class="section info">
                <h2>📊 Resumen</h2>
                <p><strong>Total de variables:</strong> {len(all_env_vars)}</p>
                <p><strong>Variables de Railway:</strong> {len(railway_vars)}</p>
                <p><strong>Entorno detectado:</strong> {'Railway' if railway_vars else 'Local/Otro'}</p>
            </div>
            
            <div class="section {'success' if target_vars['GOOGLE_SERVICE_ACCOUNT_JSON'] != 'NO ENCONTRADA' else 'error'}">
                <h2>🎯 Variables Objetivo</h2>
                <table>
                    <tr><th>Variable</th><th>Estado</th><th>Valor (primeros 50 chars)</th></tr>'''
    
    for var, value in target_vars.items():
        status_icon = "✅" if value != 'NO ENCONTRADA' else "❌"
        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        html += f'<tr><td>{var}</td><td>{status_icon}</td><td>{display_value}</td></tr>'
    
    html += f'''
                </table>
            </div>
            
            <div class="section info">
                <h2>🚂 Variables de Railway</h2>
                <table>
                    <tr><th>Variable</th><th>Valor</th></tr>'''
    
    if railway_vars:
        for var, value in railway_vars.items():
            html += f'<tr><td>{var}</td><td>{str(value)[:100]}...</td></tr>'
    else:
        html += '<tr><td colspan="2">❌ No se encontraron variables de Railway</td></tr>'
    
    html += f'''
                </table>
            </div>
            
            <div class="section info">
                <h2>🔧 Todas las Variables (primeras 20)</h2>
                <table>
                    <tr><th>Variable</th><th>Valor (primeros 50 chars)</th></tr>'''
    
    # Mostrar solo las primeras 20 variables para no sobrecargar
    for i, (var, value) in enumerate(list(all_env_vars.items())[:20]):
        display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        html += f'<tr><td>{var}</td><td>{display_value}</td></tr>'
    
    if len(all_env_vars) > 20:
        html += f'<tr><td colspan="2">... y {len(all_env_vars) - 20} variables más</td></tr>'
    
    html += f'''
                </table>
            </div>
            
            <div class="section">
                <h2>🔗 Navegación</h2>
                <a href="/test-complete" class="btn">🏠 Volver al Diagnóstico Principal</a>
                <a href="/debug-static" class="btn">📁 Debug Archivos Estáticos</a>
                <a href="/" class="btn">🏠 Página Principal</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/debug-auth')
def debug_auth():
    """Endpoint específico para debugging de AuthManager"""
    import traceback
    
    debug_info = {
        'auth_manager_status': 'Available' if auth_manager else 'Not Available',
        'variables_check': {},
        'credentials_test': {},
        'connection_test': {},
        'error_details': []
    }
    
    # 1. Verificar variables de entorno
    debug_info['variables_check'] = {
        'GOOGLE_SERVICE_ACCOUNT_JSON': {
            'exists': bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')),
            'length': len(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '')),
            'starts_with': os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON', '')[:50] + '...' if os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') else 'N/A'
        },
        'GOOGLE_SHEETS_ID': {
            'exists': bool(os.environ.get('GOOGLE_SHEETS_ID')),
            'value': os.environ.get('GOOGLE_SHEETS_ID', 'N/A')
        }
    }
    
    # 2. Probar carga de credenciales
    try:
        json_content = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        if json_content:
            import json
            creds_dict = json.loads(json_content)
            debug_info['credentials_test'] = {
                'json_parse': 'SUCCESS',
                'project_id': creds_dict.get('project_id', 'N/A'),
                'client_email': creds_dict.get('client_email', 'N/A'),
                'has_private_key': bool(creds_dict.get('private_key'))
            }
        else:
            debug_info['credentials_test'] = {
                'json_parse': 'FAILED - No JSON content',
                'error': 'GOOGLE_SERVICE_ACCOUNT_JSON is empty'
            }
    except Exception as e:
        debug_info['credentials_test'] = {
            'json_parse': 'FAILED',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    
    # 3. Probar conexión a Google Sheets
    try:
        if debug_info['credentials_test'].get('json_parse') == 'SUCCESS':
            from google.oauth2.service_account import Credentials
            import gspread
            
            json_content = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
            creds_dict = json.loads(json_content)
            
            credentials = Credentials.from_service_account_info(
                creds_dict, 
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            gc = gspread.authorize(credentials)
            
            sheets_id = os.environ.get('GOOGLE_SHEETS_ID', '1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU')
            spreadsheet = gc.open_by_key(sheets_id)
            
            debug_info['connection_test'] = {
                'gspread_auth': 'SUCCESS',
                'spreadsheet_open': 'SUCCESS',
                'spreadsheet_title': spreadsheet.title,
                'worksheets': [ws.title for ws in spreadsheet.worksheets()]
            }
            
            # Probar acceso a hoja de usuarios
            try:
                users_sheet = spreadsheet.worksheet('Usuarios')
                debug_info['connection_test']['users_sheet'] = 'SUCCESS'
                debug_info['connection_test']['users_sheet_rows'] = len(users_sheet.get_all_values())
            except Exception as e:
                debug_info['connection_test']['users_sheet'] = f'FAILED: {str(e)}'
                
        else:
            debug_info['connection_test'] = {
                'status': 'SKIPPED - Credentials test failed'
            }
            
    except Exception as e:
        debug_info['connection_test'] = {
            'status': 'FAILED',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    
    # 4. Intentar crear AuthManager en tiempo real
    try:
        from auth_manager import AuthManager
        test_auth = AuthManager()
        debug_info['live_auth_test'] = {
            'status': 'SUCCESS',
            'instance_created': True
        }
    except Exception as e:
        debug_info['live_auth_test'] = {
            'status': 'FAILED',
            'error': str(e),
            'traceback': traceback.format_exc()
        }
    
    # Crear respuesta HTML
    html = f'''
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
            <h1>🔍 Debug AuthManager - MedConnect</h1>
            
            <div class="section {'success' if auth_manager else 'error'}">
                <h2>📊 Estado Actual</h2>
                <p><strong>AuthManager:</strong> {debug_info['auth_manager_status']}</p>
            </div>
            
            <div class="section info">
                <h2>🔧 Variables de Entorno</h2>
                <pre>{json.dumps(debug_info['variables_check'], indent=2)}</pre>
            </div>
            
            <div class="section {'success' if debug_info['credentials_test'].get('json_parse') == 'SUCCESS' else 'error'}">
                <h2>🔑 Prueba de Credenciales</h2>
                <pre>{json.dumps(debug_info['credentials_test'], indent=2)}</pre>
            </div>
            
            <div class="section {'success' if debug_info['connection_test'].get('gspread_auth') == 'SUCCESS' else 'error'}">
                <h2>🌐 Prueba de Conexión</h2>
                <pre>{json.dumps(debug_info['connection_test'], indent=2)}</pre>
            </div>
            
            <div class="section {'success' if debug_info['live_auth_test'].get('status') == 'SUCCESS' else 'error'}">
                <h2>🚀 Prueba en Vivo de AuthManager</h2>
                <pre>{json.dumps(debug_info['live_auth_test'], indent=2)}</pre>
            </div>
            
            <div class="section">
                <h2>🔗 Navegación</h2>
                <a href="/test-complete" class="btn">🏠 Diagnóstico Principal</a>
                <a href="/debug-env" class="btn">🔧 Debug Variables</a>
                <a href="/" class="btn">🏠 Página Principal</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/test-images')
def test_images():
    """Endpoint para probar las imágenes de la landing page"""
    import os
    
    # Verificar existencia de archivos
    static_path = os.path.join(app.root_path, 'static')
    logo_path = os.path.join(static_path, 'images', 'logo.png')
    imagen2_path = os.path.join(static_path, 'images', 'Imagen2.png')
    css_path = os.path.join(static_path, 'css', 'styles.css')
    
    files_status = {
        'logo.png': {
            'exists': os.path.exists(logo_path),
            'size': os.path.getsize(logo_path) if os.path.exists(logo_path) else 0,
            'path': logo_path
        },
        'Imagen2.png': {
            'exists': os.path.exists(imagen2_path),
            'size': os.path.getsize(imagen2_path) if os.path.exists(imagen2_path) else 0,
            'path': imagen2_path
        },
        'styles.css': {
            'exists': os.path.exists(css_path),
            'size': os.path.getsize(css_path) if os.path.exists(css_path) else 0,
            'path': css_path
        }
    }
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Imágenes - MedConnect</title>
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
            <h1>🖼️ Test de Imágenes - MedConnect</h1>
            
            <div class="test-section">
                <h2>📊 Estado de Archivos</h2>
                <pre>{json.dumps(files_status, indent=2)}</pre>
            </div>
            
            <div class="test-section">
                <h2>🖼️ Prueba Visual - Logo</h2>
                <p><strong>URL Flask:</strong> {url_for('static', filename='images/logo.png')}</p>
                <p><strong>URL Directa:</strong> /static/images/logo.png</p>
                <img src="{url_for('static', filename='images/logo.png')}" alt="Logo Flask" 
                     onload="document.getElementById('logo-flask').innerHTML='✅ Cargado con Flask'"
                     onerror="document.getElementById('logo-flask').innerHTML='❌ Error con Flask'">
                <div id="logo-flask">⏳ Cargando...</div>
                
                <img src="/static/images/logo.png" alt="Logo Directo"
                     onload="document.getElementById('logo-direct').innerHTML='✅ Cargado directo'"
                     onerror="document.getElementById('logo-direct').innerHTML='❌ Error directo'">
                <div id="logo-direct">⏳ Cargando...</div>
            </div>
            
            <div class="test-section">
                <h2>🖼️ Prueba Visual - Imagen2</h2>
                <p><strong>URL Flask:</strong> {url_for('static', filename='images/Imagen2.png')}</p>
                <img src="{url_for('static', filename='images/Imagen2.png')}" alt="Imagen2 Flask"
                     onload="document.getElementById('img2-flask').innerHTML='✅ Cargado con Flask'"
                     onerror="document.getElementById('img2-flask').innerHTML='❌ Error con Flask'">
                <div id="img2-flask">⏳ Cargando...</div>
            </div>
            
            <div class="test-section">
                <h2>🎨 Prueba CSS</h2>
                <p><strong>URL CSS:</strong> {url_for('static', filename='css/styles.css')}</p>
                <link rel="stylesheet" href="{url_for('static', filename='css/styles.css')}">
                <div class="hero" style="padding: 20px; margin: 10px 0;">
                    <h3>Si este texto tiene estilos aplicados, CSS funciona ✅</h3>
                </div>
            </div>
            
            <div class="test-section">
                <h2>🔧 URLs de Prueba Directa</h2>
                <a href="/static/images/logo.png" target="_blank" class="btn">🖼️ Ver Logo</a>
                <a href="/static/images/Imagen2.png" target="_blank" class="btn">🖼️ Ver Imagen2</a>
                <a href="/static/css/styles.css" target="_blank" class="btn">🎨 Ver CSS</a>
            </div>
            
            <div class="test-section">
                <h2>🔗 Navegación</h2>
                <a href="/" class="btn">🏠 Landing Page</a>
                <a href="/test-complete" class="btn">🔧 Diagnóstico Completo</a>
                <a href="/debug-static" class="btn">📁 Debug Estáticos</a>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/landing-test')
def landing_test():
    """Endpoint para probar la landing page con template simplificado"""
    return '''
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
                <h2>🧪 Prueba de Elementos Básicos</h2>
                <p><strong>Logo en navegación:</strong> Debería aparecer arriba ⬆️</p>
                <p><strong>CSS aplicado:</strong> Esta sección debería tener borde azul y fondo gris</p>
            </div>
            
            <div class="test-section">
                <h2>🖼️ Prueba de Imágenes</h2>
                <p><strong>Logo principal:</strong></p>
                <img src="/static/images/logo.png" alt="Logo" style="max-width: 200px; border: 1px solid #ddd;">
                
                <p><strong>Imagen2:</strong></p>
                <img src="/static/images/Imagen2.png" alt="Imagen2" style="max-width: 300px; border: 1px solid #ddd;">
            </div>
            
            <div class="test-section">
                <h2>🎨 Prueba de Estilos CSS</h2>
                <div class="hero" style="padding: 30px; text-align: center;">
                    <h1>Bienvenido a <span class="highlight">MedConnect</span></h1>
                    <p class="hero-subtitle">Tu plataforma integral de gestión médica familiar</p>
                    <div class="hero-buttons">
                        <a href="/register" class="btn btn-primary">Registrarse</a>
                        <a href="/login" class="btn btn-secondary">Iniciar Sesión</a>
                    </div>
                </div>
            </div>
            
            <div class="test-section">
                <h2>🔗 Comparación</h2>
                <a href="/" style="padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;">🏠 Landing Page Original</a>
                <a href="/test-images" style="padding: 10px 20px; background: #28a745; color: white; text-decoration: none; border-radius: 5px;">🖼️ Test de Imágenes</a>
            </div>
        </div>
    </body>
    </html>
    '''

# Almacén temporal de códigos de vinculación (en producción usaría Redis)
telegram_link_codes = {}

@app.route('/api/user/generate-telegram-code', methods=['POST'])
@login_required
def generate_telegram_code():
    """Genera un código único para vincular Telegram"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        # Generar código único
        import random
        import string
        code = 'MED' + ''.join(random.choices(string.digits, k=6))
        
        # Verificar que el código no exista (muy improbable)
        while code in telegram_link_codes:
            code = 'MED' + ''.join(random.choices(string.digits, k=6))
        
        # Guardar código con expiración (15 minutos)
        from datetime import datetime, timedelta
        expiration = datetime.now() + timedelta(minutes=15)
        
        telegram_link_codes[code] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'expires_at': expiration
        }
        
        # Limpiar códigos expirados
        clean_expired_codes()
        
        logger.info(f"✅ Código generado para usuario {user_id}: {code}")
        
        return jsonify({
            'success': True,
            'code': code,
            'expires_in_minutes': 15,
            'instructions': f'Envía este mensaje al bot: /codigo {code}'
        })
        
    except Exception as e:
        logger.error(f"❌ Error generando código: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

def clean_expired_codes():
    """Limpia códigos expirados del almacén temporal"""
    try:
        from datetime import datetime
        now = datetime.now()
        expired_codes = [code for code, data in telegram_link_codes.items() 
                        if data['expires_at'] < now]
        
        for code in expired_codes:
            del telegram_link_codes[code]
            
        if expired_codes:
            logger.info(f"🧹 Limpiados {len(expired_codes)} códigos expirados")
            
    except Exception as e:
        logger.error(f"❌ Error limpiando códigos: {e}")

def handle_telegram_code_linking(text, telegram_user_id):
    """Maneja la vinculación por código"""
    try:
        parts = text.split()
        if len(parts) < 2:
            return """❌ Formato incorrecto.

**Uso correcto:**
`/codigo MED123456`

**¿Dónde obtengo mi código?**
1. Ve a tu perfil en: https://medconnect.cl/profile
2. En la sección "Conectar Telegram" haz clic en "Generar Código"
3. Envía el código aquí

El código expira en 15 minutos."""
        
        code = parts[1].strip().upper()
        
        # Limpiar códigos expirados primero
        clean_expired_codes()
        
        # Verificar si el código existe y es válido
        if code not in telegram_link_codes:
            return f"""❌ Código inválido o expirado: `{code}`

**¿Qué hacer?**
1. Ve a tu perfil: https://medconnect.cl/profile
2. Genera un nuevo código
3. Envíalo inmediatamente (expira en 15 minutos)

**Formato correcto:** `/codigo MED123456`"""
        
        code_data = telegram_link_codes[code]
        user_id = code_data['user_id']
        
        # Eliminar el código usado
        del telegram_link_codes[code]
        
        if not auth_manager:
            return "❌ Sistema de autenticación no disponible temporalmente."
        
        # Obtener información del usuario
        user_info = auth_manager.get_user_by_id(user_id)
        if not user_info:
            return "❌ Usuario no encontrado en el sistema."
        
        # Vincular la cuenta
        success, message, updated_user = auth_manager.link_telegram_by_user_id(user_id, telegram_user_id)
        
        if success and updated_user:
            nombre = updated_user.get('nombre', 'Usuario')
            apellido = updated_user.get('apellido', '')
            
            logger.info(f"✅ Cuenta vinculada: Usuario {user_id} con Telegram {telegram_user_id}")
            
            return f"""🎉 ¡Cuenta vinculada exitosamente!

¡Hola <b>{nombre} {apellido}</b>! 👋

Tu cuenta de MedConnect está ahora conectada con Telegram.

✅ <b>Beneficios activados:</b>
📋 Registro de consultas médicas
💊 Gestión de medicamentos
🩺 Seguimiento de exámenes
📊 Acceso a tu historial completo
👨‍👩‍👧‍👦 Notificaciones familiares

<i>Escribe /start para comenzar tu experiencia personalizada.</i>"""
        else:
            logger.error(f"❌ Error vinculando cuenta: {message}")
            return f"❌ Error vinculando cuenta: {message}"
            
    except Exception as e:
        logger.error(f"❌ Error en vinculación por código: {e}")
        return "❌ Error interno. Intenta generar un nuevo código."

@app.route('/api/user/unlink-telegram', methods=['POST'])
@login_required
def unlink_telegram():
    """Desvincula la cuenta de Telegram del usuario"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        if not auth_manager:
            return jsonify({'error': 'Sistema de autenticación no disponible'}), 500
        
        # Obtener información del usuario
        user_info = auth_manager.get_user_by_id(user_id)
        if not user_info:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Verificar si tiene Telegram vinculado
        if not user_info.get('telegram_id'):
            return jsonify({'error': 'No hay cuenta de Telegram vinculada'}), 400
        
        # Desvincular (actualizar a vacío)
        success, message, updated_user = auth_manager.link_telegram_by_user_id(user_id, '', '')
        
        if success:
            logger.info(f"✅ Telegram desvinculado para usuario {user_id}")
            return jsonify({
                'success': True,
                'message': 'Cuenta de Telegram desvinculada exitosamente'
            })
        else:
            return jsonify({'error': message}), 500
            
    except Exception as e:
        logger.error(f"❌ Error desvinculando Telegram: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/update-professional-profile', methods=['POST'])
@login_required
def update_professional_profile():
    """Actualiza el perfil del profesional"""
    try:
        if session.get('user_type') != 'profesional':
            return jsonify({'error': 'Acceso denegado: Solo para profesionales'}), 403

        user_data = session.get('user_data', {})
        user_id = user_data.get('id')
        
        if not user_id:
            return jsonify({'error': 'Usuario no identificado'}), 400
        
        form_data = request.form.to_dict()
        logger.info(f"🔄 Actualizando perfil profesional - Usuario: {user_id}, Datos: {form_data}")
        
        # Validar datos requeridos según la sección
        if 'especialidad' in form_data:
            # Sección profesional
            required_fields = ['especialidad', 'numero_registro']
            for field in required_fields:
                if not form_data.get(field, '').strip():
                    return jsonify({'error': f'El campo {field} es requerido'}), 400

        if 'email' in form_data:
            # Sección contacto
            required_fields = ['email', 'telefono']
            for field in required_fields:
                if not form_data.get(field, '').strip():
                    return jsonify({'error': f'El campo {field} es requerido'}), 400

        # Usar auth_manager para actualizar el profesional
        success, message = auth_manager.update_professional_profile(user_id, form_data)
            
        if success:
            # Actualizar datos en la sesión si la actualización fue exitosa
            updated_data = auth_manager.get_professional_by_id(user_id)
            if updated_data:
                # Combinar datos actualizados con datos de sesión
                user_data.update(updated_data)
                session['user_data'] = user_data
            
            logger.info(f"✅ Perfil profesional actualizado - Usuario: {user_id}")
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400

    except Exception as e:
        logger.error(f"❌ Error en update_professional_profile: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/add-specialization-area', methods=['POST'])
@login_required
def add_specialization_area():
    """Agrega un área de especialización al perfil del profesional"""
    try:
        if session.get('user_type') != 'profesional':
            return jsonify({'error': 'Acceso denegado: Solo para profesionales'}), 403

        user_data = session.get('user_data', {})
        form_data = request.form.to_dict()
        
        # Validar datos requeridos
        if not form_data.get('nombre'):
            return jsonify({'error': 'El nombre del área es requerido'}), 400

        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'error': 'Error conectando con la base de datos'}), 500

        try:
            worksheet = spreadsheet.worksheet('Profesionales')
            # Buscar al profesional por email
            cell = worksheet.find(user_data.get('email'))
            
            if cell:
                # Obtener áreas actuales
                areas_cell = worksheet.cell(cell.row, 13)  # Columna M para áreas
                areas_actuales = areas_cell.value.split('\n') if areas_cell.value else []
                
                # Agregar nueva área
                nueva_area = form_data.get('nombre')
                if form_data.get('descripcion'):
                    nueva_area += f": {form_data.get('descripcion')}"
                
                areas_actuales.append(nueva_area)
                
                # Actualizar en Google Sheets
                worksheet.update_cell(cell.row, 13, '\n'.join(areas_actuales))
                
                # Actualizar datos en la sesión
                professional_data = user_data.copy()
                professional_data['areas_especializacion'] = areas_actuales
                session['user_data'] = professional_data

                return jsonify({
                    'message': 'Área de especialización agregada correctamente',
                    'areas': areas_actuales
                })
            else:
                return jsonify({'error': 'Profesional no encontrado'}), 404

        except Exception as e:
            logger.error(f"Error agregando área de especialización: {e}")
            return jsonify({'error': 'Error al actualizar la base de datos'}), 500

    except Exception as e:
        logger.error(f"Error en add_specialization_area: {e}")
        return jsonify({'error': 'Error al agregar el área de especialización'}), 500

# === RUTAS PARA GESTIÓN DE ATENCIONES ===

@app.route('/api/test-atencion', methods=['GET'])
@login_required
def test_atencion():
    """Ruta de prueba para verificar el sistema de atenciones"""
    try:
        logger.info("🧪 Iniciando test_atencion")
        
        user_data = session.get('user_data', {})
        logger.info(f"👤 Usuario de prueba: {user_data}")
        
        # Probar conexión con Google Sheets
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con Google Sheets'})
        
        # Probar acceso a la hoja
        try:
            worksheet = spreadsheet.worksheet('Atenciones_Medicas')
            records = worksheet.get_all_records()
            logger.info(f"📊 Registros en hoja: {len(records)}")
        except Exception as e:
            logger.warning(f"⚠️ Hoja no existe, será creada: {e}")
            records = []
        
        return jsonify({
            'success': True,
            'message': 'Sistema funcionando correctamente',
            'user_id': user_data.get('id', session.get('user_id', '')),
            'user_email': user_data.get('email', ''),
            'total_records': len(records),
            'sheets_connected': True
        })
        
    except Exception as e:
        logger.error(f"❌ Error en test_atencion: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/register-atencion', methods=['POST'])
@login_required
def register_atencion():
    """Registra una nueva atención médica, incluyendo archivos."""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400

        # Verificar si es JSON o FormData
        if request.content_type and 'application/json' in request.content_type:
            # Datos JSON (sin archivos)
            data = request.get_json()
            archivos = []
            logger.info(f"📋 Datos JSON recibidos: {data}")
        else:
            # Datos de formulario (con posibles archivos)
            data = request.form.to_dict()
            archivos = request.files.getlist('files[]')
            logger.info(f"📋 Datos de formulario recibidos: {data}")
            logger.info(f"📄 Archivos recibidos: {len(archivos)}")

        # Obtener el nombre del profesional
        try:
            spreadsheet = get_spreadsheet()
            profesionales_sheet = spreadsheet.worksheet('Profesionales')
            profesionales_records = profesionales_sheet.get_all_records()
            
            profesional_nombre = "Profesional"
            for prof in profesionales_records:
                if str(prof.get('profesional_id', '')) == str(profesional_id):
                    profesional_nombre = f"{prof.get('nombre', '')} {prof.get('apellido', '')}".strip()
                    break
        except Exception as e:
            logger.warning(f"No se pudo obtener nombre del profesional: {e}")
            profesional_nombre = "Profesional"

        # Agregar datos faltantes
        data['profesional_id'] = profesional_id
        data['profesional_nombre'] = profesional_nombre
        data['tiene_archivos'] = 'Sí' if archivos else 'No'

        # Registrar la atención en la hoja de cálculo
        atencion_id, nueva_fila = sheets_db.registrar_atencion(data)

        # Si la atención se registró y hay archivos, procesarlos
        if atencion_id and archivos:
            logger.info(f"📎 Procesando {len(archivos)} archivos para atención {atencion_id}...")
            
            # Crear subdirectorio para la atención
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
                        tamaño = os.path.getsize(file_path)
                        
                        # Registrar archivo en la hoja de cálculo
                        archivo_data = {
                            'atencion_id': atencion_id,
                            'nombre_archivo': filename,
                            'tipo_archivo': archivo.mimetype,
                            'ruta_archivo': os.path.join('uploads', atencion_id, filename),
                            'tamaño': tamaño
                        }
                        sheets_db.registrar_archivo_adjunto(archivo_data)
                        logger.info(f"✅ Archivo '{filename}' guardado y registrado.")
                    except Exception as e:
                        logger.error(f"❌ Error procesando archivo {archivo.filename}: {e}")
                        continue
            
        logger.info(f"✅ Atención {atencion_id} registrada exitosamente.")
        return jsonify({
                'success': True, 
                'message': 'Atención registrada exitosamente',
            'atencion_id': atencion_id,
            'atencion': nueva_fila
        })
            
    except Exception as e:
        logger.error(f"❌ Error en register_atencion: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': f'Error interno del servidor: {e}'}), 500

@app.route('/api/get-atenciones', methods=['GET'])
@login_required
def get_atenciones():
    """Obtiene las atenciones registradas por el profesional"""
    try:
        logger.info("🔍 Iniciando get_atenciones")
        
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        logger.info(f"👤 Datos del usuario: {user_data}")
        logger.info(f"👨‍⚕️ Profesional ID: {profesional_id}")
        
        if not profesional_id:
            logger.error("❌ Usuario no identificado")
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        logger.info("📊 Obteniendo spreadsheet...")
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            logger.error("❌ No se pudo obtener el spreadsheet")
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        logger.info("✅ Spreadsheet obtenido correctamente")
        
        try:
            logger.info("📄 Obteniendo hoja Atenciones_Medicas...")
            worksheet = spreadsheet.worksheet('Atenciones_Medicas')
            logger.info("✅ Hoja encontrada, obteniendo registros...")
            
            records = worksheet.get_all_records()
            logger.info(f"📋 Total de registros encontrados: {len(records)}")
            
            # Filtrar atenciones del profesional actual
            atenciones_profesional = []
            for i, record in enumerate(records):
                record_profesional_id = str(record.get('profesional_id', ''))
                logger.info(f"🔍 Registro {i+1}: profesional_id='{record_profesional_id}', buscando='{profesional_id}'")
                
                if record_profesional_id == str(profesional_id):
                    logger.info(f"✅ Atención encontrada para el profesional: {record.get('atencion_id', '')}")
                    atenciones_profesional.append({
                        'atencion_id': record.get('atencion_id', ''),
                        'paciente_nombre': record.get('paciente_nombre', ''),
                        'paciente_rut': record.get('paciente_rut', ''),
                        'paciente_edad': record.get('paciente_edad', ''),
                        'fecha_hora': record.get('fecha_hora', ''),
                        'tipo_atencion': record.get('tipo_atencion', ''),
                        'motivo_consulta': record.get('motivo_consulta', ''),
                        'diagnostico': record.get('diagnostico', ''),
                        'tratamiento': record.get('tratamiento', ''),
                        'fecha_registro': record.get('fecha_registro', ''),
                        'estado': record.get('estado', '')
                    })
            
            logger.info(f"📊 Total atenciones del profesional: {len(atenciones_profesional)}")
            
            # Ordenar por fecha más reciente
            atenciones_profesional.sort(
                key=lambda x: x.get('fecha_registro', ''), 
                reverse=True
            )
            
            logger.info("✅ Atenciones procesadas y ordenadas")
            
            return jsonify({
                'success': True,
                'atenciones': atenciones_profesional,
                'total': len(atenciones_profesional)
            })
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo atenciones: {e}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return jsonify({'success': False, 'message': f'Error al consultar la base de datos: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error en get_atenciones: {e}")
        import traceback
        logger.error(f"❌ Traceback completo: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/get-atencion/<atencion_id>', methods=['GET'])
@login_required
def get_atencion(atencion_id):
    """Obtiene los detalles de una atención específica"""
    try:
        logger.info(f"🔍 Obteniendo detalles de atención: {atencion_id}")
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            logger.error("❌ Usuario no identificado")
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            logger.error("❌ Error conectando con la base de datos")
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Atenciones_Medicas')
            records = worksheet.get_all_records()
            
            # Buscar el registro
            atencion = None
            for record in records:
                if str(record.get('atencion_id', '')) == str(atencion_id):
                    atencion = record
                    break
            
            if not atencion:
                logger.error("❌ Atención no encontrada")
                return jsonify({'success': False, 'message': 'Atención no encontrada'}), 404
            
            # Verificar que el profesional tiene acceso a esta atención
            if str(atencion.get('profesional_id', '')) != str(profesional_id):
                logger.error("❌ Acceso no autorizado a la atención")
                return jsonify({'success': False, 'message': 'No tiene permisos para ver esta atención'}), 403
            
            try:
                # Obtener archivos adjuntos
                archivos = sheets_db.get_archivos_atencion(atencion_id)
                logger.info(f"📎 Archivos encontrados: {len(archivos)}")
            except Exception as e:
                logger.error(f"❌ Error obteniendo archivos adjuntos: {e}")
                archivos = []
            
            return jsonify({
                'success': True,
                'atencion': {
                    'atencion_id': atencion.get('atencion_id', ''),
                    'paciente_id': atencion.get('paciente_id', ''),
                    'paciente_nombre': atencion.get('paciente_nombre', ''),
                    'paciente_rut': atencion.get('paciente_rut', ''),
                    'paciente_edad': atencion.get('paciente_edad', ''),
                    'fecha_hora': atencion.get('fecha_hora', ''),
                    'tipo_atencion': atencion.get('tipo_atencion', ''),
                    'motivo_consulta': atencion.get('motivo_consulta', ''),
                    'diagnostico': atencion.get('diagnostico', ''),
                    'tratamiento': atencion.get('tratamiento', ''),
                    'observaciones': atencion.get('observaciones', ''),
                    'estado': atencion.get('estado', ''),
                    'tiene_archivos': atencion.get('tiene_archivos', False)
                },
                'archivos': archivos
            })
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo atención: {e}")
            return jsonify({'success': False, 'message': 'Error al consultar la base de datos'}), 500
            
    except Exception as e:
        logger.error(f"❌ Error en get_atencion: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@app.route('/api/update-atencion/<atencion_id>', methods=['PUT'])
@login_required
def update_atencion(atencion_id):
    """Actualiza una atención específica"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener datos del formulario
        data = request.get_json()
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Atenciones_Medicas')
            records = worksheet.get_all_records()
            
            # Buscar y actualizar el registro
            for i, record in enumerate(records, start=2):  # start=2 porque la fila 1 son headers
                if (record.get('atencion_id') == atencion_id and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    
                    # Actualizar los campos específicos
                    if 'fecha_hora' in data:
                        worksheet.update_cell(i, 7, data['fecha_hora'])
                    if 'tipo_atencion' in data:
                        worksheet.update_cell(i, 8, data['tipo_atencion'])
                    if 'motivo_consulta' in data:
                        worksheet.update_cell(i, 9, data['motivo_consulta'])
                    if 'diagnostico' in data:
                        worksheet.update_cell(i, 10, data['diagnostico'])
                    if 'tratamiento' in data:
                        worksheet.update_cell(i, 11, data['tratamiento'])
                    if 'observaciones' in data:
                        worksheet.update_cell(i, 12, data['observaciones'])
                    if 'requiere_seguimiento' in data:
                        worksheet.update_cell(i, 15, 'Sí' if data['requiere_seguimiento'] else 'No')
                    
                    logger.info(f"Atención {atencion_id} actualizada por profesional {profesional_id}")
                    return jsonify({'success': True, 'message': 'Atención actualizada exitosamente'})
            
            return jsonify({'success': False, 'message': 'Atención no encontrada'}), 404
            
        except Exception as e:
            logger.error(f"Error actualizando atención: {e}")
            return jsonify({'success': False, 'message': 'Error al actualizar en la base de datos'}), 500
            
    except Exception as e:
        logger.error(f"Error en update_atencion: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@app.route('/api/professional/patients', methods=['GET'])
@login_required
def get_professional_patients():
    """Obtiene la lista de pacientes del profesional"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            # Intentar obtener o crear la hoja
            try:
                worksheet = spreadsheet.worksheet('Pacientes_Profesional')
            except:
                # Si no existe, crearla
                headers = ['paciente_id', 'profesional_id', 'nombre_completo', 'rut', 'edad',
                          'fecha_nacimiento', 'genero', 'telefono', 'email', 'direccion',
                          'antecedentes_medicos', 'fecha_primera_consulta', 'ultima_consulta',
                          'num_atenciones', 'estado_relacion', 'fecha_registro', 'notas']
                worksheet = spreadsheet.add_worksheet(title='Pacientes_Profesional', rows=1000, cols=len(headers))
                worksheet.append_row(headers)
                logger.info("✅ Hoja Pacientes_Profesional creada")
            
            records = worksheet.get_all_records()
            
            # Filtrar pacientes del profesional actual
            pacientes_profesional = []
            for record in records:
                if str(record.get('profesional_id', '')) == str(profesional_id):
                    # Debug: log del record original
                    logger.info(f"🔍 Record original de Google Sheets: {record}")
                    
                    # Procesar cada campo de manera segura
                    paciente_data = {}
                    
                    # Campos que deben ser strings
                    string_fields = ['paciente_id', 'nombre_completo', 'rut', 'fecha_nacimiento', 
                                   'genero', 'telefono', 'email', 'direccion', 'antecedentes_medicos',
                                   'fecha_primera_consulta', 'ultima_consulta', 'estado_relacion', 
                                   'fecha_registro', 'notas']
                    
                    for field in string_fields:
                        value = record.get(field, '')
                        # Convertir a string si no es None
                        if value is not None:
                            paciente_data[field] = str(value)
                        else:
                            paciente_data[field] = ''
                        logger.info(f"🔍 Campo {field}: valor='{value}', tipo={type(value)}, procesado='{paciente_data[field]}'")
                    
                    # Campos numéricos
                    edad_value = record.get('edad', '')
                    if edad_value is not None and str(edad_value).strip() != '':
                        try:
                            paciente_data['edad'] = str(int(float(str(edad_value))))
                        except (ValueError, TypeError):
                            paciente_data['edad'] = str(edad_value) if edad_value else ''
                    else:
                        paciente_data['edad'] = ''
                    
                    num_atenciones_value = record.get('num_atenciones', 0)
                    if num_atenciones_value is not None and str(num_atenciones_value).strip() != '':
                        try:
                            paciente_data['num_atenciones'] = int(float(str(num_atenciones_value)))
                        except (ValueError, TypeError):
                            paciente_data['num_atenciones'] = 0
                    else:
                        paciente_data['num_atenciones'] = 0
                    
                    logger.info(f"🔍 Paciente procesado: {paciente_data}")
                    pacientes_profesional.append(paciente_data)
            
            # Ordenar por fecha de registro más reciente
            pacientes_profesional.sort(
                key=lambda x: x.get('fecha_registro', ''), 
                reverse=True
            )
            
            logger.info(f"📊 Total pacientes del profesional {profesional_id}: {len(pacientes_profesional)}")
            
            return jsonify({
                'success': True,
                'pacientes': pacientes_profesional,
                'total': len(pacientes_profesional)
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo pacientes: {e}")
            return jsonify({'success': False, 'message': f'Error al consultar la base de datos: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en get_professional_patients: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/patients', methods=['POST'])
@login_required
def add_professional_patient():
    """Agrega un nuevo paciente al profesional"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"📝 Datos del nuevo paciente: {data}")
        
        # Validar campos requeridos
        required_fields = ['nombre_completo', 'rut']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'El campo {field} es requerido'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Pacientes_Profesional')
            
            # Verificar si el paciente ya existe para este profesional
            records = worksheet.get_all_records()
            for record in records:
                if (str(record.get('profesional_id', '')) == str(profesional_id) and 
                    record.get('rut', '').strip().lower() == data.get('rut', '').strip().lower()):
                    return jsonify({'success': False, 'message': 'Este paciente ya está registrado en tu lista'}), 400
            
            # Generar ID único para el paciente
            paciente_id = f"PAC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Preparar datos para insertar
            nuevo_paciente = [
                paciente_id,
                profesional_id,
                data.get('nombre_completo', ''),
                data.get('rut', ''),
                data.get('edad', ''),
                data.get('fecha_nacimiento', ''),
                data.get('genero', ''),
                data.get('telefono', ''),
                data.get('email', ''),
                data.get('direccion', ''),
                data.get('antecedentes_medicos', ''),
                '',  # fecha_primera_consulta (se actualiza con la primera atención)
                '',  # ultima_consulta
                0,   # num_atenciones
                'activo',  # estado_relacion
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                data.get('notas', '')
            ]
            
            # Insertar en Google Sheets
            worksheet.append_row(nuevo_paciente)
            logger.info(f"✅ Paciente {paciente_id} agregado al profesional {profesional_id}")
            
            return jsonify({
                'success': True,
                'message': 'Paciente agregado exitosamente',
                'paciente_id': paciente_id
            })
            
        except Exception as e:
            logger.error(f"Error agregando paciente: {e}")
            return jsonify({'success': False, 'message': f'Error al agregar en la base de datos: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en add_professional_patient: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/patients/<paciente_id>', methods=['GET'])
@login_required
def get_professional_patient(paciente_id):
    """Obtiene los detalles de un paciente específico"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Pacientes_Profesional')
            records = worksheet.get_all_records()
            
            # Buscar el paciente
            for record in records:
                if (record.get('paciente_id') == paciente_id and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    
                    # También obtener el historial de atenciones del paciente
                    atenciones_worksheet = spreadsheet.worksheet('Atenciones_Medicas')
                    atenciones_records = atenciones_worksheet.get_all_records()
                    
                    atenciones_paciente = []
                    for atencion in atenciones_records:
                        if (str(atencion.get('profesional_id', '')) == str(profesional_id) and 
                            atencion.get('paciente_rut', '').strip().lower() == record.get('rut', '').strip().lower()):
                            atenciones_paciente.append({
                                'atencion_id': atencion.get('atencion_id', ''),
                                'fecha_hora': atencion.get('fecha_hora', ''),
                                'tipo_atencion': atencion.get('tipo_atencion', ''),
                                'motivo_consulta': atencion.get('motivo_consulta', ''),
                                'diagnostico': atencion.get('diagnostico', ''),
                                'estado': atencion.get('estado', '')
                            })
                    
                    return jsonify({
                        'success': True,
                        'paciente': record,
                        'atenciones': atenciones_paciente,
                        'total_atenciones': len(atenciones_paciente)
                    })
            
            return jsonify({'success': False, 'message': 'Paciente no encontrado'}), 404
            
        except Exception as e:
            logger.error(f"Error obteniendo paciente: {e}")
            return jsonify({'success': False, 'message': f'Error al consultar la base de datos: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en get_professional_patient: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/patients/<paciente_id>', methods=['PUT'])
@login_required
def update_professional_patient(paciente_id):
    """Actualiza la información de un paciente"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener datos del formulario
        data = request.get_json()
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Pacientes_Profesional')
            records = worksheet.get_all_records()
            
            # Buscar y actualizar el paciente
            for i, record in enumerate(records, start=2):  # start=2 porque la fila 1 son headers
                if (record.get('paciente_id') == paciente_id and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    
                    # Actualizar los campos específicos
                    if 'nombre_completo' in data:
                        worksheet.update_cell(i, 3, data['nombre_completo'])
                    if 'rut' in data:
                        worksheet.update_cell(i, 4, data['rut'])
                    if 'edad' in data:
                        worksheet.update_cell(i, 5, data['edad'])
                    if 'fecha_nacimiento' in data:
                        worksheet.update_cell(i, 6, data['fecha_nacimiento'])
                    if 'genero' in data:
                        worksheet.update_cell(i, 7, data['genero'])
                    if 'telefono' in data:
                        worksheet.update_cell(i, 8, data['telefono'])
                    if 'email' in data:
                        worksheet.update_cell(i, 9, data['email'])
                    if 'direccion' in data:
                        worksheet.update_cell(i, 10, data['direccion'])
                    if 'antecedentes_medicos' in data:
                        worksheet.update_cell(i, 11, data['antecedentes_medicos'])
                    if 'notas' in data:
                        worksheet.update_cell(i, 17, data['notas'])
                    
                    logger.info(f"Paciente {paciente_id} actualizado por profesional {profesional_id}")
                    return jsonify({'success': True, 'message': 'Paciente actualizado exitosamente'})
            
            return jsonify({'success': False, 'message': 'Paciente no encontrado'}), 404
            
        except Exception as e:
            logger.error(f"Error actualizando paciente: {e}")
            return jsonify({'success': False, 'message': f'Error al actualizar en la base de datos: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en update_professional_patient: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/patients/<paciente_id>', methods=['DELETE'])
@login_required
def remove_professional_patient(paciente_id):
    """Elimina un paciente de la lista del profesional"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Pacientes_Profesional')
            records = worksheet.get_all_records()
            
            # Buscar el paciente para eliminar la relación
            for i, record in enumerate(records, start=2):  # start=2 porque la fila 1 son headers
                if (record.get('paciente_id') == paciente_id and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    
                    # Eliminar la fila
                    worksheet.delete_rows(i)
                    logger.info(f"Relación profesional-paciente eliminada: {profesional_id} - {paciente_id}")
                    return jsonify({'success': True, 'message': 'Paciente eliminado de tu lista exitosamente'})
            
            return jsonify({'success': False, 'message': 'Paciente no encontrado'}), 404
            
        except Exception as e:
            logger.error(f"Error eliminando relación profesional-paciente: {e}")
            return jsonify({'success': False, 'message': f'Error al eliminar de la base de datos: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en remove_professional_patient: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/delete-atencion/<atencion_id>', methods=['DELETE'])
@login_required
def delete_atencion(atencion_id):
    """Elimina una atención específica"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Atenciones_Medicas')
            
            # Buscar la atención
            records = worksheet.get_all_records()
            row_to_delete = None
            
            for i, record in enumerate(records, start=2):  # start=2 porque la fila 1 son headers
                if (record.get('atencion_id') == atencion_id and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    row_to_delete = i
                    break
            
            if row_to_delete:
                worksheet.delete_rows(row_to_delete)
                logger.info(f"Atención {atencion_id} eliminada por profesional {profesional_id}")
                return jsonify({
                    'success': True,
                    'message': 'Atención eliminada exitosamente'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Atención no encontrada o no tienes permisos para eliminarla'
                }), 404
                
        except Exception as e:
            logger.error(f"Error eliminando atención: {e}")
            return jsonify({'success': False, 'message': 'Error al eliminar de la base de datos'}), 500
            
    except Exception as e:
        logger.error(f"Error en delete_atencion: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@app.route('/api/update-professional-status/<int:professional_id>', methods=['PUT'])
@login_required
def update_professional_status(professional_id):
    """Actualizar estado y disponibilidad de un profesional"""
    try:
        # Verificar que el usuario actual sea administrador o el mismo profesional
        current_user = session.get('user_data', {})
        if current_user.get('tipo_usuario') != 'profesional' and current_user.get('id') != professional_id:
            # Aquí podrías agregar lógica para verificar si es administrador
            pass
        
        # Obtener datos del formulario
        estado = request.json.get('estado')
        disponible = request.json.get('disponible')
        
        if not estado and not disponible:
            return jsonify({'error': 'Se debe proporcionar al menos estado o disponible'}), 400
        
        # Actualizar en la base de datos
        success, message = auth_manager.update_professional_status(
            professional_id, 
            estado=estado, 
            disponible=disponible
        )
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error actualizando estado de profesional: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/get-professional/<int:professional_id>', methods=['GET'])
@login_required
def get_professional_details(professional_id):
    """Obtener detalles completos de un profesional"""
    try:
        professional_data = auth_manager.get_professional_by_id(professional_id)
        
        if professional_data:
            return jsonify(professional_data), 200
        else:
            return jsonify({'error': 'Profesional no encontrado'}), 404
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo profesional: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/add-certification', methods=['POST'])
@login_required
def add_certification():
    """Agregar certificación a un profesional"""
    try:
        # Obtener datos del usuario actual
        user_data = session.get('user_data', {})
        user_id = user_data.get('id')
        
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        # Verificar que sea un profesional
        if user_data.get('tipo_usuario') != 'profesional':
            return jsonify({'error': 'Solo los profesionales pueden agregar certificaciones'}), 403
        
        # Obtener datos del formulario
        titulo = request.form.get('titulo', '').strip()
        institucion = request.form.get('institucion', '').strip()
        ano = request.form.get('ano', '').strip()
        
        # Validar campos requeridos
        if not titulo or not institucion or not ano:
            return jsonify({'error': 'Título, institución y año son requeridos'}), 400
        
        # Manejar archivo si se subió
        archivo_url = ''
        if 'certificado' in request.files:
            file = request.files['certificado']
            if file and file.filename:
                if allowed_file(file.filename):
                    # Generar nombre único para el archivo
                    filename = generate_unique_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'certifications', filename)
                    
                    # Crear directorio si no existe
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Guardar archivo
                    file.save(file_path)
                    archivo_url = f'/uploads/certifications/{filename}'
                    logger.info(f"✅ Archivo de certificación guardado: {archivo_url}")
                else:
                    return jsonify({'error': 'Tipo de archivo no permitido. Solo PDF'}), 400
        
        # Agregar certificación a Google Sheets
        success, message = auth_manager.add_professional_certification(
            user_id, titulo, institucion, ano, archivo_url
        )
        
        if success:
            logger.info(f"✅ Certificación agregada para profesional ID: {user_id}")
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"❌ Error agregando certificación: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/get-certifications/<int:professional_id>', methods=['GET'])
@login_required
def get_professional_certifications(professional_id):
    """Obtener certificaciones de un profesional"""
    try:
        # Verificar que el usuario actual sea el mismo profesional o un administrador
        current_user = session.get('user_data', {})
        if current_user.get('id') != professional_id:
            # Aquí podrías agregar lógica para verificar si es administrador
            pass
        
        # Obtener certificaciones
        certifications = auth_manager.get_professional_certifications(professional_id)
        
        return jsonify({'certifications': certifications}), 200
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo certificaciones: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/atencion-pdf/<atencion_id>')
@login_required
def generar_pdf_atencion(atencion_id):
    """Genera un PDF con los detalles de la atención médica usando ReportLab"""
    try:
        # Obtener datos de la atención
        user_data = get_current_user()
        if not user_data:
            return jsonify({'error': 'Usuario no autenticado'}), 401

        # Obtener el cliente de Google Sheets y la hoja de cálculo
        sheets_client = get_google_sheets_client()
        if not sheets_client:
            logger.error("Error: No se pudo obtener el cliente de Google Sheets")
            return jsonify({'error': 'Error interno del servidor'}), 500

        spreadsheet = sheets_client.open_by_key(app.config['GOOGLE_SHEETS_ID'])
        
        try:
            worksheet = spreadsheet.worksheet('Atenciones_Medicas')
            records = worksheet.get_all_records()
            atencion = None
            
            for record in records:
                if str(record.get('atencion_id', '')) == str(atencion_id):
                    atencion = record
                    break
            
            if not atencion:
                return jsonify({'error': 'Atención no encontrada'}), 404

        except Exception as e:
            logger.error(f"Error obteniendo atención: {e}")
            return jsonify({'error': 'Error interno del servidor'}), 500

        try:
            # Importar las dependencias necesarias para ReportLab
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from PIL import Image as PILImage

            # Colores del proyecto
            COLOR_PRIMARY = colors.HexColor('#2C3E50')  # Azul oscuro
            COLOR_SECONDARY = colors.HexColor('#3498DB')  # Azul claro
            COLOR_ACCENT = colors.HexColor('#E74C3C')  # Rojo
            COLOR_TEXT = colors.HexColor('#2C3E50')  # Texto principal
            COLOR_SUBTEXT = colors.HexColor('#7F8C8D')  # Texto secundario

            # Crear un buffer para el PDF
            buffer = BytesIO()

            # Crear el documento PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=100,  # Aumentado para el logo
                bottomMargin=72
            )

            # Obtener estilos
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=COLOR_PRIMARY
            ))
            styles.add(ParagraphStyle(
                name='SectionTitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
                textColor=COLOR_SECONDARY,
                borderColor=COLOR_SECONDARY,
                borderWidth=1,
                borderPadding=5,
                borderRadius=5
            ))
            styles.add(ParagraphStyle(
                name='Label',
                parent=styles['Normal'],
                fontSize=11,
                textColor=COLOR_TEXT,
                fontName='Helvetica-Bold'
            ))
            # Modificar el estilo Normal existente en lugar de crear uno nuevo
            styles['Normal'].fontSize = 10
            styles['Normal'].textColor = COLOR_TEXT
            styles['Normal'].alignment = TA_LEFT
            styles['Normal'].leading = 14

            # Lista de elementos para el PDF
            elements = []

            # Agregar logo
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'logo.png')
            if os.path.exists(logo_path):
                logo = Image(logo_path)
                logo.drawHeight = 0.5*inch
                logo.drawWidth = 0.5*inch
                elements.append(logo)
                elements.append(Spacer(1, 20))

            # Título
            elements.append(Paragraph('Registro de Atención Médica', styles['CustomTitle']))
            elements.append(Spacer(1, 20))

            # Información del Paciente
            elements.append(Paragraph('Información del Paciente', styles['SectionTitle']))
            patient_data = [
                ['Nombre:', atencion.get('paciente_nombre', '')],
                ['RUT:', atencion.get('paciente_rut', '')],
                ['Edad:', f"{atencion.get('paciente_edad', '')} años"]
            ]

            # Estilo común para las tablas
            table_style = TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), COLOR_SECONDARY),
                ('TEXTCOLOR', (1, 0), (-1, -1), COLOR_TEXT),
                ('GRID', (0, 0), (-1, -1), 0.5, COLOR_SUBTEXT),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8F9FA')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ])

            t = Table(patient_data, colWidths=[150, 350])
            t.setStyle(table_style)
            elements.append(t)
            elements.append(Spacer(1, 20))

            # Detalles de la Atención
            elements.append(Paragraph('Detalles de la Atención', styles['SectionTitle']))
            attention_data = [
                ['Fecha y Hora:', atencion.get('fecha_hora', '')],
                ['Tipo de Atención:', atencion.get('tipo_atencion', '')],
                ['Profesional:', f"{user_data.get('nombre', '')} {user_data.get('apellido', '')}"]
            ]
            t = Table(attention_data, colWidths=[150, 350])
            t.setStyle(table_style)
            elements.append(t)
            elements.append(Spacer(1, 20))

            # Evaluación Clínica
            elements.append(Paragraph('Evaluación Clínica', styles['SectionTitle']))
            
            # Motivo de Consulta
            elements.append(Paragraph('Motivo de Consulta:', styles['Label']))
            elements.append(Paragraph(atencion.get('motivo_consulta', ''), styles['Normal']))
            elements.append(Spacer(1, 10))
            
            # Diagnóstico
            elements.append(Paragraph('Diagnóstico:', styles['Label']))
            elements.append(Paragraph(atencion.get('diagnostico', ''), styles['Normal']))
            elements.append(Spacer(1, 10))
            
            # Plan de Tratamiento
            elements.append(Paragraph('Plan de Tratamiento:', styles['Label']))
            elements.append(Paragraph(atencion.get('tratamiento', ''), styles['Normal']))
            elements.append(Spacer(1, 10))
            
            # Observaciones
            elements.append(Paragraph('Observaciones Adicionales:', styles['Label']))
            elements.append(Paragraph(atencion.get('observaciones', 'Sin observaciones adicionales'), styles['Normal']))
            elements.append(Spacer(1, 20))

            # Agregar imagen de la atención si existe
            imagen_path = atencion.get('imagen_path')
            if imagen_path and os.path.exists(os.path.join('static', imagen_path)):
                elements.append(Paragraph('Imagen Adjunta:', styles['SectionTitle']))
                img = Image(os.path.join('static', imagen_path))
                
                # Calcular dimensiones manteniendo la proporción
                desired_width = 400  # Ancho deseado en puntos
                img_ratio = img.imageHeight / float(img.imageWidth)
                img.drawWidth = desired_width
                img.drawHeight = desired_width * img_ratio
                
                # Centrar la imagen
                elements.append(img)
                elements.append(Spacer(1, 20))

            # Pie de página
            elements.append(Spacer(1, 40))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=COLOR_SUBTEXT,
                alignment=TA_CENTER
            )
            elements.append(Paragraph(
                f'Documento generado por MedConnect - Sistema de Gestión de Atenciones Médicas<br/>'
                f'Fecha de emisión: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                footer_style
            ))

            # Generar el PDF
            doc.build(elements)

            # Preparar el PDF para enviar
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'atencion_{atencion_id}.pdf'
            )

        except Exception as e:
            logger.error(f"Error generando PDF con ReportLab: {e}")
            return jsonify({'error': 'Error generando el PDF'}), 500

    except Exception as e:
        logger.error(f"Error general generando PDF: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/archivos/<atencion_id>')
@login_required
def get_archivos_atencion(atencion_id):
    """Obtiene los archivos adjuntos de una atención"""
    try:
        archivos = sheets_db.get_archivos_atencion(atencion_id)
        return jsonify({
            'success': True,
            'archivos': archivos
        })
    except Exception as e:
        logger.error(f"Error obteniendo archivos: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/archivos/upload', methods=['POST'])
@login_required
def upload_archivos():
    """Sube archivos adjuntos para una atención"""
    try:
        logger.info("🔍 Iniciando subida de archivos")
        
        if 'files[]' not in request.files:
            logger.error("❌ No se enviaron archivos")
            return jsonify({'success': False, 'error': 'No se enviaron archivos'}), 400

        atencion_id = request.form.get('atencion_id')
        if not atencion_id:
            logger.error("❌ No se especificó la atención")
            return jsonify({'success': False, 'error': 'No se especificó la atención'}), 400

        logger.info(f"📂 Procesando archivos para atención {atencion_id}")
        files = request.files.getlist('files[]')
        uploaded_files = []

        # Crear directorio base si no existe
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Crear subdirectorio para la atención
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

                    logger.info(f"💾 Guardando archivo: {filename}")
                    file.save(file_path)
                    
                    # Registrar en la base de datos
                    archivo_data = {
                        'atencion_id': atencion_id,
                        'nombre_archivo': filename,
                        'tipo_archivo': file.content_type,
                        'ruta_archivo': os.path.join('uploads', atencion_id, filename),
                        'tamaño': os.path.getsize(file_path)
                    }
                    
                    logger.info("📝 Registrando archivo en la base de datos")
                    archivo_id = sheets_db.registrar_archivo_adjunto(archivo_data)
                    uploaded_files.append({
                        'archivo_id': archivo_id,
                        'nombre_archivo': filename
                    })
                    logger.info(f"✅ Archivo {filename} subido y registrado correctamente")
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando archivo {file.filename}: {e}")
                    continue
            else:
                logger.warning(f"⚠️ Archivo no permitido o vacío: {file.filename if file else 'Sin archivo'}")

        # Actualizar el estado de archivos en la atención
        if uploaded_files:
            try:
                spreadsheet = get_spreadsheet()
                worksheet = spreadsheet.worksheet('Atenciones_Medicas')
                records = worksheet.get_all_records()
                
                for i, record in enumerate(records, start=2):
                    if str(record.get('atencion_id', '')) == str(atencion_id):
                        worksheet.update_cell(i, 17, 'Sí')  # Columna tiene_archivos
                        logger.info(f"✅ Estado de archivos actualizado para atención {atencion_id}")
                        break
            except Exception as e:
                logger.warning(f"⚠️ No se pudo actualizar estado de archivos: {e}")

            return jsonify({
                'success': True,
                'message': f'{len(uploaded_files)} archivos subidos correctamente',
                'archivos': uploaded_files
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo procesar ningún archivo'
            }), 400

    except Exception as e:
        logger.error(f"❌ Error subiendo archivos: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/archivos/<archivo_id>', methods=['DELETE'])
@login_required
def delete_archivo(archivo_id):
    """Elimina un archivo adjunto"""
    try:
        if sheets_db.delete_archivo(archivo_id):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        logger.error(f"Error eliminando archivo: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/archivos/<archivo_id>/download')
@login_required
def download_archivo(archivo_id):
    """Descarga un archivo adjunto"""
    try:
        # Obtener información del archivo
        archivo = sheets_db.get_archivo_by_id(archivo_id)
        if not archivo:
            return jsonify({'success': False, 'message': 'Archivo no encontrado'}), 404
            
        # Construir la ruta del archivo
        ruta_archivo = archivo.get('ruta_archivo', '')
        
        # Si la ruta incluye 'uploads', usar directamente; si no, construir la ruta
        if ruta_archivo.startswith('uploads'):
            file_path = os.path.join(app.root_path, 'static', ruta_archivo)
        else:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], ruta_archivo)
            
        logger.info(f"🔍 Buscando archivo en: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"❌ Archivo no encontrado en: {file_path}")
            return jsonify({'success': False, 'message': 'Archivo no encontrado en el servidor'}), 404
            
        # Enviar archivo
        return send_file(
            file_path,
            as_attachment=True,
            download_name=archivo.get('nombre_archivo'),
            mimetype=archivo.get('tipo_archivo')
        )
            
    except Exception as e:
        logger.error(f"Error descargando archivo: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

@app.route('/api/archivos/<archivo_id>/view')
@login_required
def view_archivo(archivo_id):
    """Sirve un archivo adjunto para visualización (no descarga)"""
    try:
        # Obtener información del archivo
        archivo = sheets_db.get_archivo_by_id(archivo_id)
        if not archivo:
            logger.error(f"❌ Archivo no encontrado: {archivo_id}")
            abort(404)
            
        # Construir la ruta del archivo
        ruta_archivo = archivo.get('ruta_archivo', '')
        
        # Si la ruta incluye 'uploads', usar directamente; si no, construir la ruta
        if ruta_archivo.startswith('uploads'):
            file_path = os.path.join(app.root_path, 'static', ruta_archivo)
        elif ruta_archivo.startswith('static'):
            file_path = os.path.join(app.root_path, ruta_archivo)
        else:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], ruta_archivo)
            
        logger.info(f"🔍 Sirviendo archivo para visualización: {file_path}")
        
        # Probar rutas alternativas si no existe (como en el endpoint temporal que funciona)
        if not os.path.exists(file_path):
            rutas_alternativas = [
                ruta_archivo,  # Ruta directa
                os.path.join('static', 'uploads', atencion_id, archivo.get('nombre_archivo', '')),  # Ruta reconstruida
                os.path.join(app.root_path, 'static', 'uploads', atencion_id, archivo.get('nombre_archivo', '')),
                f'static/uploads/{atencion_id}/{archivo.get("nombre_archivo", "")}'
            ]
            
            for ruta_alt in rutas_alternativas:
                if os.path.exists(ruta_alt):
                    logger.info(f"✅ Archivo encontrado en ruta alternativa: {ruta_alt}")
                    file_path = ruta_alt
                    break
            else:
                logger.error(f"❌ Archivo no encontrado en ninguna ruta: {file_path}")
                abort(404)
            
        # Verificar que el usuario tiene acceso a esta atención
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        atencion_id = archivo.get('atencion_id', '')
        
        # Verificar permisos de acceso a la atención
        try:
            spreadsheet = get_spreadsheet()
            worksheet = spreadsheet.worksheet('Atenciones_Medicas')
            records = worksheet.get_all_records()
            
            tiene_acceso = False
            for record in records:
                if (str(record.get('atencion_id', '')) == str(atencion_id) and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    tiene_acceso = True
                    break
                    
            if not tiene_acceso:
                logger.warning(f"⚠️ Acceso denegado al archivo {archivo_id} para profesional {profesional_id}")
                abort(403)
                
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            abort(500)
            
        # Servir el archivo para visualización (sin forzar descarga)
        return send_file(
            file_path,
            as_attachment=False,  # Clave: no forzar descarga
            mimetype=archivo.get('tipo_archivo')
        )
            
    except Exception as e:
        logger.error(f"Error sirviendo archivo para visualización: {e}")
        abort(500)

@app.route('/api/test-archivo/<archivo_id>')
def test_view_archivo(archivo_id):
    """Endpoint de prueba sin autenticación para verificar servido de archivos"""
    try:
        logger.info(f"🧪 Test endpoint llamado para archivo: {archivo_id}")
        
        # Obtener información del archivo
        archivo = sheets_db.get_archivo_by_id(archivo_id)
        if not archivo:
            logger.error(f"❌ Archivo no encontrado: {archivo_id}")
            return jsonify({'error': 'Archivo no encontrado'}), 404
            
        logger.info(f"📄 Información del archivo: {archivo}")
        logger.info(f"🔍 Tipo de archivo: {type(archivo)}")
        logger.info(f"🔍 Keys del archivo: {list(archivo.keys()) if archivo else 'None'}")
        
        # Construir la ruta del archivo
        ruta_archivo = archivo.get('ruta_archivo', '')
        logger.info(f"🔍 ruta_archivo: {ruta_archivo} (tipo: {type(ruta_archivo)})")
        
        # Asegurar que ruta_archivo sea string
        ruta_archivo = str(ruta_archivo) if ruta_archivo else ''
        
        # Si la ruta incluye 'uploads', usar directamente; si no, construir la ruta
        if ruta_archivo.startswith('uploads'):
            file_path = os.path.join(app.root_path, 'static', ruta_archivo)
        elif ruta_archivo.startswith('static'):
            file_path = os.path.join(app.root_path, ruta_archivo)
        else:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], ruta_archivo)
            
        logger.info(f"🔍 Buscando archivo en: {file_path}")
        logger.info(f"🔍 app.root_path: {app.root_path}")
        logger.info(f"🔍 UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER', 'Not set')}")
        
        # Probar rutas alternativas si no existe
        if not os.path.exists(file_path):
            rutas_alternativas = [
                ruta_archivo,  # Ruta directa
                os.path.join('static', 'uploads', 'ATN_20250701_152633', 'test_image.jpg'),  # Ruta reconstruida
                os.path.join(app.root_path, 'static', 'uploads', 'ATN_20250701_152633', 'test_image.jpg'),
                'static/uploads/ATN_20250701_152633/test_image.jpg'
            ]
            
            for ruta_alt in rutas_alternativas:
                logger.info(f"🔍 Probando ruta alternativa: {ruta_alt}")
                if os.path.exists(ruta_alt):
                    logger.info(f"✅ ¡Archivo encontrado en ruta alternativa!: {ruta_alt}")
                    file_path = ruta_alt
                    break
            else:
                logger.error(f"❌ Archivo no encontrado en ninguna ruta")
                logger.error(f"❌ Rutas probadas: {[file_path] + rutas_alternativas}")
                return jsonify({'error': 'Archivo físico no encontrado'}), 404
            
        logger.info(f"✅ Archivo encontrado, sirviendo...")
        
        # Crear respuesta personalizada para evitar descarga forzada
        response = make_response(send_file(
            file_path,
            as_attachment=False,  # No forzar descarga
            mimetype=archivo.get('tipo_archivo')
        ))
        
        # Headers específicos para evitar descarga automática
        response.headers['Content-Disposition'] = 'inline'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Cache-Control'] = 'no-cache'
        
        return response
            
    except Exception as e:
        logger.error(f"❌ Error en test endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/atenciones/<atencion_id>/<filename>')
@login_required
def serve_atencion_file(atencion_id, filename):
    """Sirve archivos adjuntos de atenciones para visualización"""
    try:
        # Verificar que el archivo existe
        file_path = os.path.join(UPLOAD_FOLDER, atencion_id, filename)
        if not os.path.exists(file_path):
            abort(404)
            
        # Verificar que el usuario tiene acceso a esta atención
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        # Obtener información de la atención para verificar permisos
        try:
            spreadsheet = get_spreadsheet()
            worksheet = spreadsheet.worksheet('Atenciones_Medicas')
            records = worksheet.get_all_records()
            
            tiene_acceso = False
            for record in records:
                if (str(record.get('atencion_id', '')) == str(atencion_id) and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    tiene_acceso = True
                    break
                    
            if not tiene_acceso:
                abort(403)
                
        except Exception as e:
            logger.error(f"Error verificando permisos: {e}")
            abort(500)
            
        # Servir el archivo
        return send_from_directory(
            os.path.join(UPLOAD_FOLDER, atencion_id), 
            filename
        )
        
    except Exception as e:
        logger.error(f"Error sirviendo archivo: {e}")
        abort(500)

# ====== AGENDA Y CITAS ======

@app.route('/api/professional/schedule', methods=['GET'])
@login_required
def get_professional_schedule():
    """Obtiene la agenda del profesional"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener fecha solicitada (por defecto hoy)
        fecha_solicitada = request.args.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        vista = request.args.get('vista', 'diaria')  # diaria, semanal, mensual
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            # Obtener o crear la hoja de citas
            try:
                worksheet = spreadsheet.worksheet('Citas_Agenda')
            except:
                # Si no existe, crearla
                headers = ['cita_id', 'profesional_id', 'paciente_id', 'paciente_nombre', 'paciente_rut',
                          'fecha', 'hora', 'tipo_atencion', 'estado', 'notas', 'fecha_creacion', 'recordatorio']
                worksheet = spreadsheet.add_worksheet(title='Citas_Agenda', rows=1000, cols=len(headers))
                worksheet.append_row(headers)
                logger.info("✅ Hoja Citas_Agenda creada")
            
            records = worksheet.get_all_records()
            
            # Filtrar citas del profesional y fecha
            citas_del_dia = []
            for record in records:
                if (str(record.get('profesional_id', '')) == str(profesional_id) and 
                    record.get('fecha', '') == fecha_solicitada):
                    citas_del_dia.append({
                        'cita_id': record.get('cita_id', ''),
                        'paciente_nombre': record.get('paciente_nombre', ''),
                        'paciente_rut': record.get('paciente_rut', ''),
                        'hora': record.get('hora', ''),
                        'tipo_atencion': record.get('tipo_atencion', ''),
                        'estado': record.get('estado', ''),
                        'notas': record.get('notas', ''),
                        'recordatorio': record.get('recordatorio', '')
                    })
            
            # Generar horarios disponibles (8:00 - 18:00, cada 30 minutos)
            horarios_disponibles = []
            hora_inicio = 8
            hora_fin = 18
            
            for hora in range(hora_inicio, hora_fin):
                for minuto in [0, 30]:
                    hora_str = f"{hora:02d}:{minuto:02d}"
                    
                    # Verificar si ya hay una cita en este horario
                    ocupado = any(cita['hora'] == hora_str for cita in citas_del_dia)
                    
                    if not ocupado:
                        horarios_disponibles.append(hora_str)
            
            # Estadísticas del día
            total_citas = len(citas_del_dia)
            confirmadas = len([c for c in citas_del_dia if c['estado'] == 'confirmada'])
            pendientes = len([c for c in citas_del_dia if c['estado'] == 'pendiente'])
            disponibles = len(horarios_disponibles)
            
            if vista == 'diaria':
                return jsonify({
                    'success': True,
                    'vista': 'diaria',
                    'fecha': fecha_solicitada,
                    'citas': citas_del_dia,
                    'horarios_disponibles': horarios_disponibles,
                    'estadisticas': {
                        'total_citas': total_citas,
                        'confirmadas': confirmadas,
                        'pendientes': pendientes,
                        'disponibles': disponibles
                    }
                })
            elif vista == 'semanal':
                # Obtener citas de la semana
                fecha_inicio, fecha_fin = obtener_rango_semana(fecha_solicitada)
                citas_semana = []
                
                for record in records:
                    if (str(record.get('profesional_id', '')) == str(profesional_id) and 
                        fecha_inicio <= record.get('fecha', '') <= fecha_fin):
                        citas_semana.append({
                            'cita_id': record.get('cita_id', ''),
                            'paciente_nombre': record.get('paciente_nombre', ''),
                            'paciente_rut': record.get('paciente_rut', ''),
                            'fecha': record.get('fecha', ''),
                            'hora': record.get('hora', ''),
                            'tipo_atencion': record.get('tipo_atencion', ''),
                            'estado': record.get('estado', ''),
                            'notas': record.get('notas', '')
                        })
                
                agenda_semanal = organizar_agenda_semanal(citas_semana, fecha_inicio, fecha_fin)
                
                return jsonify({
                    'success': True,
                    'vista': 'semanal',
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'agenda_semanal': agenda_semanal,
                    'estadisticas': calcular_estadisticas_semana(citas_semana)
                })
            elif vista == 'mensual':
                # Obtener citas del mes
                fecha_inicio, fecha_fin = obtener_rango_mes(fecha_solicitada)
                citas_mes = []
                
                for record in records:
                    if (str(record.get('profesional_id', '')) == str(profesional_id) and 
                        fecha_inicio <= record.get('fecha', '') <= fecha_fin):
                        citas_mes.append({
                            'cita_id': record.get('cita_id', ''),
                            'paciente_nombre': record.get('paciente_nombre', ''),
                            'paciente_rut': record.get('paciente_rut', ''),
                            'fecha': record.get('fecha', ''),
                            'hora': record.get('hora', ''),
                            'tipo_atencion': record.get('tipo_atencion', ''),
                            'estado': record.get('estado', ''),
                            'notas': record.get('notas', '')
                        })
                
                agenda_mensual = organizar_agenda_mensual(citas_mes, fecha_inicio, fecha_fin)
                
                return jsonify({
                    'success': True,
                    'vista': 'mensual',
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'agenda_mensual': agenda_mensual,
                    'estadisticas': calcular_estadisticas_mes(citas_mes)
                })
            
        except Exception as e:
            logger.error(f"Error obteniendo agenda: {e}")
            return jsonify({'success': False, 'message': f'Error al consultar la agenda: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en get_professional_schedule: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/schedule', methods=['POST'])
@login_required
def create_appointment():
    """Crea una nueva cita en la agenda"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"📝 Datos de la nueva cita: {data}")
        
        # Validar campos requeridos
        required_fields = ['paciente_id', 'fecha', 'hora', 'tipo_atencion']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'El campo {field} es requerido'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            # Obtener información del paciente
            pacientes_worksheet = spreadsheet.worksheet('Pacientes_Profesional')
            pacientes_records = pacientes_worksheet.get_all_records()
            
            paciente_info = None
            for record in pacientes_records:
                if (record.get('paciente_id') == data.get('paciente_id') and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    paciente_info = record
                    break
            
            if not paciente_info:
                return jsonify({'success': False, 'message': 'Paciente no encontrado'}), 404
            
            # Obtener hoja de citas
            try:
                worksheet = spreadsheet.worksheet('Citas_Agenda')
            except:
                # Si no existe, crearla
                headers = ['cita_id', 'profesional_id', 'paciente_id', 'paciente_nombre', 'paciente_rut',
                          'fecha', 'hora', 'tipo_atencion', 'estado', 'notas', 'fecha_creacion', 'recordatorio']
                worksheet = spreadsheet.add_worksheet(title='Citas_Agenda', rows=1000, cols=len(headers))
                worksheet.append_row(headers)
                logger.info("✅ Hoja Citas_Agenda creada")
            
            # Verificar disponibilidad del horario
            records = worksheet.get_all_records()
            for record in records:
                if (str(record.get('profesional_id', '')) == str(profesional_id) and 
                    record.get('fecha', '') == data.get('fecha') and 
                    record.get('hora', '') == data.get('hora')):
                    return jsonify({'success': False, 'message': 'El horario ya está ocupado'}), 400
            
            # Generar ID único para la cita
            cita_id = f"CITA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Preparar datos para insertar
            nueva_cita = [
                cita_id,
                profesional_id,
                data.get('paciente_id', ''),
                paciente_info.get('nombre_completo', ''),
                paciente_info.get('rut', ''),
                data.get('fecha', ''),
                data.get('hora', ''),
                data.get('tipo_atencion', ''),
                'pendiente',  # estado por defecto
                data.get('notas', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                data.get('recordatorio', 'no')
            ]
            
            # Insertar en Google Sheets
            worksheet.append_row(nueva_cita)
            logger.info(f"✅ Cita {cita_id} creada exitosamente")
            
            return jsonify({
                'success': True,
                'message': 'Cita agendada exitosamente',
                'cita_id': cita_id,
                'cita': {
                    'cita_id': cita_id,
                    'paciente_nombre': paciente_info.get('nombre_completo', ''),
                    'paciente_rut': paciente_info.get('rut', ''),
                    'fecha': data.get('fecha', ''),
                    'hora': data.get('hora', ''),
                    'tipo_atencion': data.get('tipo_atencion', ''),
                    'estado': 'pendiente',
                    'notas': data.get('notas', '')
                }
            })
            
        except Exception as e:
            logger.error(f"Error creando cita: {e}")
            return jsonify({'success': False, 'message': f'Error al crear la cita: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en create_appointment: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/schedule/<cita_id>', methods=['PUT'])
@login_required
def update_appointment(cita_id):
    """Actualiza una cita existente"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"📝 Actualizando cita {cita_id}: {data}")
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Citas_Agenda')
            records = worksheet.get_all_records()
            
            # Buscar la cita
            for i, record in enumerate(records):
                if (record.get('cita_id') == cita_id and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    
                    # Actualizar campos específicos
                    if 'estado' in data:
                        worksheet.update(f'I{i+2}', [[data['estado']]])  # Columna I es estado
                    if 'notas' in data:
                        worksheet.update(f'J{i+2}', [[data['notas']]])  # Columna J es notas
                    if 'recordatorio' in data:
                        worksheet.update(f'L{i+2}', [[data['recordatorio']]])  # Columna L es recordatorio
                    
                    logger.info(f"✅ Cita {cita_id} actualizada exitosamente")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Cita actualizada exitosamente'
                    })
            
            return jsonify({'success': False, 'message': 'Cita no encontrada'}), 404
            
        except Exception as e:
            logger.error(f"Error actualizando cita: {e}")
            return jsonify({'success': False, 'message': f'Error al actualizar la cita: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en update_appointment: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/schedule/<cita_id>', methods=['DELETE'])
@login_required
def delete_appointment(cita_id):
    """Elimina una cita de la agenda"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Citas_Agenda')
            records = worksheet.get_all_records()
            
            # Buscar la cita
            for i, record in enumerate(records):
                if (record.get('cita_id') == cita_id and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    
                    # Eliminar la fila (i+2 porque las filas empiezan en 1 y hay header)
                    worksheet.delete_rows(i+2)
                    logger.info(f"✅ Cita {cita_id} eliminada exitosamente")
                    
                    return jsonify({
                        'success': True,
                        'message': 'Cita eliminada exitosamente'
                    })
            
            return jsonify({'success': False, 'message': 'Cita no encontrada'}), 404
            
        except Exception as e:
            logger.error(f"Error eliminando cita: {e}")
            return jsonify({'success': False, 'message': f'Error al eliminar la cita: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en delete_appointment: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/working-hours', methods=['GET'])
@login_required
def get_working_hours():
    """Obtiene el horario de trabajo del profesional"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            # Obtener o crear la hoja de horarios
            try:
                worksheet = spreadsheet.worksheet('Horarios_Profesional')
            except:
                # Si no existe, crearla con horario por defecto
                headers = ['profesional_id', 'dia_semana', 'hora_inicio', 'hora_fin', 'disponible', 'notas']
                worksheet = spreadsheet.add_worksheet(title='Horarios_Profesional', rows=1000, cols=len(headers))
                worksheet.append_row(headers)
                
                # Crear horario por defecto (Lunes a Viernes, 8:00 - 18:00)
                dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
                for dia in dias_semana:
                    worksheet.append_row([profesional_id, dia, '08:00', '18:00', 'true', ''])
                
                logger.info("✅ Hoja Horarios_Profesional creada con horario por defecto")
            
            records = worksheet.get_all_records()
            
            # Filtrar horarios del profesional
            horarios = []
            for record in records:
                if str(record.get('profesional_id', '')) == str(profesional_id):
                    horarios.append({
                        'dia_semana': record.get('dia_semana', ''),
                        'hora_inicio': record.get('hora_inicio', ''),
                        'hora_fin': record.get('hora_fin', ''),
                        'disponible': record.get('disponible', 'true') == 'true',
                        'notas': record.get('notas', '')
                    })
            
            return jsonify({
                'success': True,
                'horarios': horarios
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo horarios: {e}")
            return jsonify({'success': False, 'message': f'Error al consultar los horarios: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en get_working_hours: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/reminders', methods=['GET'])
@login_required
def get_reminders():
    """Obtiene los recordatorios del profesional"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            # Obtener o crear la hoja de recordatorios
            try:
                worksheet = spreadsheet.worksheet('Recordatorios_Profesional')
            except:
                # Si no existe, crearla
                headers = ['recordatorio_id', 'profesional_id', 'tipo', 'paciente_id', 'titulo', 'mensaje',
                          'fecha', 'hora', 'prioridad', 'repetir', 'tipo_repeticion', 'estado', 'fecha_creacion']
                worksheet = spreadsheet.add_worksheet(title='Recordatorios_Profesional', rows=1000, cols=len(headers))
                worksheet.append_row(headers)
                logger.info("✅ Hoja Recordatorios_Profesional creada")
            
            records = worksheet.get_all_records()
            
            # Filtrar recordatorios del profesional y activos
            recordatorios = []
            for record in records:
                if (str(record.get('profesional_id', '')) == str(profesional_id) and 
                    record.get('estado', '') == 'activo'):
                    recordatorios.append({
                        'id': record.get('recordatorio_id', ''),
                        'tipo': record.get('tipo', ''),
                        'paciente_id': record.get('paciente_id', ''),
                        'titulo': record.get('titulo', ''),
                        'mensaje': record.get('mensaje', ''),
                        'fecha': record.get('fecha', ''),
                        'hora': record.get('hora', ''),
                        'prioridad': record.get('prioridad', 'media'),
                        'repetir': record.get('repetir', 'false').lower() == 'true',
                        'tipo_repeticion': record.get('tipo_repeticion', ''),
                        'estado': record.get('estado', 'activo')
                    })
            
            return jsonify({
                'success': True,
                'recordatorios': recordatorios
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo recordatorios: {e}")
            return jsonify({'success': False, 'message': f'Error al consultar los recordatorios: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en get_reminders: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/reminders', methods=['POST'])
@login_required
def create_reminder():
    """Crea un nuevo recordatorio"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"📝 Creando recordatorio: {data}")
        
        # Validar campos requeridos
        required_fields = ['tipo', 'titulo', 'mensaje', 'fecha', 'hora', 'prioridad']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'El campo {field} es requerido'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            # Obtener hoja de recordatorios
            try:
                worksheet = spreadsheet.worksheet('Recordatorios_Profesional')
            except:
                # Si no existe, crearla
                headers = ['recordatorio_id', 'profesional_id', 'tipo', 'paciente_id', 'titulo', 'mensaje',
                          'fecha', 'hora', 'prioridad', 'repetir', 'tipo_repeticion', 'estado', 'fecha_creacion']
                worksheet = spreadsheet.add_worksheet(title='Recordatorios_Profesional', rows=1000, cols=len(headers))
                worksheet.append_row(headers)
                logger.info("✅ Hoja Recordatorios_Profesional creada")
            
            # Generar ID único
            recordatorio_id = str(uuid.uuid4())
            
            # Crear nueva fila
            nueva_fila = [
                recordatorio_id,
                profesional_id,
                data.get('tipo', ''),
                data.get('paciente_id', ''),
                data.get('titulo', ''),
                data.get('mensaje', ''),
                data.get('fecha', ''),
                data.get('hora', ''),
                data.get('prioridad', 'media'),
                str(data.get('repetir', False)).lower(),
                data.get('tipo_repeticion', ''),
                'activo',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            worksheet.append_row(nueva_fila)
            
            logger.info(f"✅ Recordatorio creado exitosamente: {recordatorio_id}")
            
            return jsonify({
                'success': True,
                'message': 'Recordatorio creado exitosamente',
                'recordatorio_id': recordatorio_id
            })
            
        except Exception as e:
            logger.error(f"Error creando recordatorio: {e}")
            return jsonify({'success': False, 'message': f'Error al crear el recordatorio: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en create_reminder: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/reminders/<recordatorio_id>', methods=['GET'])
@login_required
def get_reminder(recordatorio_id):
    """Obtiene un recordatorio específico"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Recordatorios_Profesional')
            records = worksheet.get_all_records()
            
            # Buscar el recordatorio específico
            recordatorio = None
            for record in records:
                if (str(record.get('recordatorio_id', '')) == str(recordatorio_id) and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    recordatorio = {
                        'id': record.get('recordatorio_id', ''),
                        'tipo': record.get('tipo', ''),
                        'paciente_id': record.get('paciente_id', ''),
                        'titulo': record.get('titulo', ''),
                        'mensaje': record.get('mensaje', ''),
                        'fecha': record.get('fecha', ''),
                        'hora': record.get('hora', ''),
                        'prioridad': record.get('prioridad', 'media'),
                        'repetir': record.get('repetir', 'false').lower() == 'true',
                        'tipo_repeticion': record.get('tipo_repeticion', ''),
                        'estado': record.get('estado', 'activo')
                    }
                    break
            
            if not recordatorio:
                return jsonify({'success': False, 'message': 'Recordatorio no encontrado'}), 404
            
            return jsonify({
                'success': True,
                'recordatorio': recordatorio
            })
            
        except Exception as e:
            logger.error(f"Error obteniendo recordatorio: {e}")
            return jsonify({'success': False, 'message': f'Error al consultar el recordatorio: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en get_reminder: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/reminders/<recordatorio_id>', methods=['PUT'])
@login_required
def update_reminder(recordatorio_id):
    """Actualiza un recordatorio existente"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"📝 Actualizando recordatorio {recordatorio_id}: {data}")
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Recordatorios_Profesional')
            records = worksheet.get_all_records()
            
            # Buscar y actualizar el recordatorio
            encontrado = False
            for i, record in enumerate(records):
                if (str(record.get('recordatorio_id', '')) == str(recordatorio_id) and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    
                    # Actualizar campos
                    worksheet.update(f'C{i+2}', [[data.get('tipo', '')]])  # tipo
                    worksheet.update(f'D{i+2}', [[data.get('paciente_id', '')]])  # paciente_id
                    worksheet.update(f'E{i+2}', [[data.get('titulo', '')]])  # titulo
                    worksheet.update(f'F{i+2}', [[data.get('mensaje', '')]])  # mensaje
                    worksheet.update(f'G{i+2}', [[data.get('fecha', '')]])  # fecha
                    worksheet.update(f'H{i+2}', [[data.get('hora', '')]])  # hora
                    worksheet.update(f'I{i+2}', [[data.get('prioridad', 'media')]])  # prioridad
                    worksheet.update(f'J{i+2}', [[str(data.get('repetir', False)).lower()]])  # repetir
                    worksheet.update(f'K{i+2}', [[data.get('tipo_repeticion', '')]])  # tipo_repeticion
                    
                    encontrado = True
                    break
            
            if not encontrado:
                return jsonify({'success': False, 'message': 'Recordatorio no encontrado'}), 404
            
            logger.info(f"✅ Recordatorio {recordatorio_id} actualizado exitosamente")
            
            return jsonify({
                'success': True,
                'message': 'Recordatorio actualizado exitosamente'
            })
            
        except Exception as e:
            logger.error(f"Error actualizando recordatorio: {e}")
            return jsonify({'success': False, 'message': f'Error al actualizar el recordatorio: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en update_reminder: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/reminders/<recordatorio_id>', methods=['DELETE'])
@login_required
def delete_reminder(recordatorio_id):
    """Elimina un recordatorio (marca como inactivo)"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Recordatorios_Profesional')
            records = worksheet.get_all_records()
            
            # Buscar y marcar como inactivo el recordatorio
            encontrado = False
            for i, record in enumerate(records):
                if (str(record.get('recordatorio_id', '')) == str(recordatorio_id) and 
                    str(record.get('profesional_id', '')) == str(profesional_id)):
                    
                    # Marcar como inactivo
                    worksheet.update(f'L{i+2}', [['inactivo']])  # estado
                    
                    encontrado = True
                    break
            
            if not encontrado:
                return jsonify({'success': False, 'message': 'Recordatorio no encontrado'}), 404
            
            logger.info(f"✅ Recordatorio {recordatorio_id} eliminado exitosamente")
            
            return jsonify({
                'success': True,
                'message': 'Recordatorio eliminado exitosamente'
            })
            
        except Exception as e:
            logger.error(f"Error eliminando recordatorio: {e}")
            return jsonify({'success': False, 'message': f'Error al eliminar el recordatorio: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en delete_reminder: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

@app.route('/api/professional/working-hours', methods=['POST'])
@login_required
def update_working_hours():
    """Actualiza el horario de trabajo del profesional"""
    try:
        user_data = session.get('user_data', {})
        profesional_id = user_data.get('id', session.get('user_id', ''))
        
        if not profesional_id:
            return jsonify({'success': False, 'message': 'Usuario no identificado'}), 400
        
        # Obtener datos del formulario
        data = request.get_json()
        logger.info(f"📝 Actualizando horarios del profesional {profesional_id}: {data}")
        
        # Obtener la hoja de cálculo
        spreadsheet = get_spreadsheet()
        if not spreadsheet:
            return jsonify({'success': False, 'message': 'Error conectando con la base de datos'}), 500
        
        try:
            worksheet = spreadsheet.worksheet('Horarios_Profesional')
            records = worksheet.get_all_records()
            
            # Actualizar horarios existentes
            for horario in data.get('horarios', []):
                dia_semana = horario.get('dia_semana')
                
                # Buscar si ya existe el horario para este día
                encontrado = False
                for i, record in enumerate(records):
                    if (str(record.get('profesional_id', '')) == str(profesional_id) and 
                        record.get('dia_semana', '') == dia_semana):
                        
                        # Actualizar horario existente
                        worksheet.update(f'C{i+2}', [[horario.get('hora_inicio', '')]])  # Columna C es hora_inicio
                        worksheet.update(f'D{i+2}', [[horario.get('hora_fin', '')]])    # Columna D es hora_fin
                        worksheet.update(f'E{i+2}', [[str(horario.get('disponible', True)).lower()]])  # Columna E es disponible
                        worksheet.update(f'F{i+2}', [[horario.get('notas', '')]])      # Columna F es notas
                        
                        encontrado = True
                        break
                
                # Si no existe, crear nuevo horario
                if not encontrado:
                    nueva_fila = [
                        profesional_id,
                        dia_semana,
                        horario.get('hora_inicio', ''),
                        horario.get('hora_fin', ''),
                        str(horario.get('disponible', True)).lower(),
                        horario.get('notas', '')
                    ]
                    worksheet.append_row(nueva_fila)
            
            logger.info(f"✅ Horarios del profesional {profesional_id} actualizados exitosamente")
            
            return jsonify({
                'success': True,
                'message': 'Horarios actualizados exitosamente'
            })
            
        except Exception as e:
            logger.error(f"Error actualizando horarios: {e}")
            return jsonify({'success': False, 'message': f'Error al actualizar los horarios: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error en update_working_hours: {e}")
        return jsonify({'success': False, 'message': f'Error interno del servidor: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Iniciando MedConnect en puerto {port}")
    logger.info(f"Modo debug: {debug}")
    logger.info(f"Dominio configurado: {app.config['DOMAIN']}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

 