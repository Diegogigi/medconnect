"""
Configuración general para MedConnect
Manejo de variables de entorno y configuración del sistema
"""
import os
from dotenv import load_dotenv
from datetime import timedelta

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base para MedConnect"""
    
    # Configuración de la aplicación
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'medconnect-secret-key-2024'
    
    # Configuración del dominio
    DOMAIN = os.environ.get('DOMAIN') or 'medconnect.cl'
    BASE_URL = f"https://{DOMAIN}"
    
    # Configuración de Telegram Bot
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_BOT_ID = os.environ.get('TELEGRAM_BOT_ID')
    TELEGRAM_WEBHOOK_URL = f"{BASE_URL}/webhook"
    
    # Configuración de Google Sheets
    GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID')
    GOOGLE_CREDENTIALS_FILE = os.environ.get('GOOGLE_CREDENTIALS_FILE')
    
    # Configuración de la base de datos (Google Sheets como respaldo)
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///medconnect.db'
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Configuración de CORS para el frontend
    CORS_ORIGINS = [
        f"https://{DOMAIN}",
        f"https://www.{DOMAIN}",
        "http://localhost:3000",  # Para desarrollo local
        "http://127.0.0.1:3000"
    ]
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # Configuración de email (para notificaciones)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de la aplicación
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Configuración para desarrollo local"""
    DEBUG = True
    BASE_URL = "http://localhost:5000"
    TELEGRAM_WEBHOOK_URL = f"{BASE_URL}/webhook"
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Configuración para producción en Railway"""
    DEBUG = False
    
    # Configuración específica de Railway
    PORT = int(os.environ.get('PORT', 5000))
    
    # Configuración de SSL/TLS
    SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    
    # Configuración de logging para producción
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuración de hojas de Google Sheets
SHEETS_CONFIG = {
    'patients': {
        'name': 'Pacientes',
        'columns': [
            'id', 'nombre', 'edad', 'telefono', 'email', 
            'fecha_registro', 'plan', 'estado'
        ]
    },
    'consultations': {
        'name': 'Consultas',
        'columns': [
            'id', 'patient_id', 'doctor', 'specialty', 'date', 
            'diagnosis', 'treatment', 'notes', 'status'
        ]
    },
    'medications': {
        'name': 'Medicamentos',
        'columns': [
            'id', 'patient_id', 'medication', 'dosage', 'frequency',
            'start_date', 'end_date', 'prescribed_by', 'status'
        ]
    },
    'exams': {
        'name': 'Examenes',
        'columns': [
            'id', 'patient_id', 'exam_type', 'date', 'results',
            'lab', 'doctor', 'file_url', 'status'
        ]
    },
    'family_members': {
        'name': 'Familiares',
        'columns': [
            'id', 'patient_id', 'name', 'relationship', 'phone',
            'email', 'access_level', 'emergency_contact', 'status'
        ]
    },
    'bot_interactions': {
        'name': 'Interacciones_Bot',
        'columns': [
            'id', 'user_id', 'username', 'message', 'response',
            'timestamp', 'action_type', 'status'
        ]
    }
}

# Configuración de Railway
RAILWAY_CONFIG = {
    'build_command': 'pip install -r requirements.txt',
    'start_command': 'python app.py',
    'environment': 'production',
    'auto_deploy': True,
    'domain': 'medconnect.cl'
}

# Configuración estandarizada de Google Sheets para MedConnect
SHEETS_STANDARD_CONFIG = {
    # Hoja principal de usuarios (pacientes)
    'Usuarios': [
        'user_id', 'telegram_id', 'nombre', 'apellido', 'edad', 
        'rut', 'telefono', 'email', 'direccion', 'fecha_registro', 
        'estado', 'plan'
    ],
    
    # Hoja de profesionales médicos
    'Profesionales': [
        'profesional_id', 'nombre', 'apellido', 'especialidad', 'email', 'telefono',
        'direccion', 'numero_registro', 'anos_experiencia', 'calificacion',
        'fecha_registro', 'estado', 'disponible'
    ],
    
    # Hoja principal de atenciones médicas
    'Atenciones_Medicas': [
        'atencion_id', 'profesional_id', 'profesional_nombre', 'paciente_id', 
        'paciente_nombre', 'paciente_rut', 'paciente_edad', 'fecha_hora', 
        'tipo_atencion', 'motivo_consulta', 'diagnostico', 'tratamiento', 
        'observaciones', 'fecha_registro', 'estado', 'requiere_seguimiento', 
        'tiene_archivos'
    ],
    
    # Hoja de medicamentos
    'Medicamentos': [
        'medicamento_id', 'user_id', 'atencion_id', 'nombre_medicamento',
        'dosis', 'frecuencia', 'duracion', 'indicaciones',
        'fecha_inicio', 'fecha_fin', 'estado'
    ],
    
    # Hoja de exámenes médicos
    'Examenes': [
        'examen_id', 'user_id', 'atencion_id', 'tipo_examen',
        'nombre_examen', 'fecha_solicitud', 'fecha_realizacion',
        'resultado', 'archivo_url', 'observaciones', 'estado'
    ],
    
    # Hoja de familiares autorizados
    'Familiares_Autorizados': [
        'familiar_id', 'user_id', 'nombre_familiar', 'parentesco',
        'telefono', 'email', 'telegram_id', 'permisos', 
        'fecha_autorizacion', 'estado', 'notificaciones'
    ],
    
    # Hoja de recordatorios
    'Recordatorios': [
        'reminder_id', 'user_id', 'tipo', 'titulo', 'mensaje',
        'fecha_programada', 'hora_programada', 'frecuencia',
        'notificar_familiares', 'fecha_creacion', 'estado'
    ],
    
    # Hoja de logs de acceso
    'Logs_Acceso': [
        'log_id', 'user_id', 'accion', 'detalle', 'ip_address',
        'timestamp', 'resultado'
    ],
    
    # Hoja de agenda/citas (para profesionales)
    'Agenda': [
        'cita_id', 'profesional_id', 'paciente_id', 'fecha', 'hora_inicio',
        'hora_fin', 'tipo_cita', 'motivo', 'estado', 'notas',
        'recordatorio_enviado', 'fecha_creacion'
    ],
    
    # Hoja de especialidades médicas
    'Especialidades': [
        'especialidad_id', 'nombre', 'descripcion', 'icono', 'estado'
    ],
    
    # Hoja de pacientes por profesional
    'Pacientes_Profesional': [
        'paciente_id', 'profesional_id', 'nombre_completo', 'rut', 'edad',
        'fecha_nacimiento', 'genero', 'telefono', 'email', 'direccion',
        'antecedentes_medicos', 'fecha_primera_consulta', 'ultima_consulta',
        'num_atenciones', 'estado_relacion', 'fecha_registro', 'notas'
    ],
    
    # Hoja de archivos adjuntos
    'Archivos_Adjuntos': [
        'archivo_id', 'atencion_id', 'nombre_archivo', 'tipo_archivo',
        'ruta_archivo', 'fecha_subida', 'tamaño', 'estado'
    ]
}

# Configuración según el entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default']) 