#!/usr/bin/env python3
"""
MedConnect - Aplicación OFFLINE Auditada y Optimizada
Versión completamente funcional para desarrollo local
"""

import os
import sys
import logging
import time
import random
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
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
    )
    from flask_cors import CORS

    logger.info("✅ Flask importado correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando Flask: {e}")
    sys.exit(1)

# Configurar variables de entorno para modo offline
os.environ["DATABASE_URL"] = ""
os.environ["SECRET_KEY"] = "dev-secret-key-local-offline-12345"
os.environ["FLASK_ENV"] = "development"
os.environ["DEBUG"] = "True"
os.environ["PORT"] = "8000"
os.environ["SESSION_COOKIE_SECURE"] = "False"

# Inicializar Flask
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-secret-key-local-offline-12345"
)
app.config["FLASK_ENV"] = "development"
app.config["DEBUG"] = True

# Configurar cookies para desarrollo local
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Configurar CORS
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"])

# ==================== DATOS SIMULADOS COMPLETOS ====================

# Usuarios profesionales
USUARIOS_SIMULADOS = {
    "diego.castro.lagos@gmail.com": {
        "id": 1,
        "nombre": "Diego",
        "apellido": "Castro",
        "email": "diego.castro.lagos@gmail.com",
        "password": "password123",
        "tipo_usuario": "profesional",
        "telefono": "56979712175",
        "especialidad": "Kinesiología",
        "numero_registro": "FP101015",
        "institucion": "Universidad Las Ámericas",
        "anos_experiencia": 5,
        "calificacion": "Excelente",
        "direccion_consulta": "Centro Médico Talcahuano",
        "horario_atencion": "Lunes a Viernes 8:00-18:00",
        "idiomas": "Español, Inglés",
        "profesion": "Licenciado en Kinesiología",
        "estado": "activo",
        "disponible": True,
        "verificado": True,
    },
    "rodrigoandressilvabreve@gmail.com": {
        "id": 2,
        "nombre": "Rodrigo Andres",
        "apellido": "Silva Breve",
        "email": "rodrigoandressilvabreve@gmail.com",
        "password": "password123",
        "tipo_usuario": "profesional",
        "telefono": "987042150",
        "especialidad": "Traumatología",
        "numero_registro": "624365",
        "institucion": "Universidad de las Américas",
        "anos_experiencia": 5,
        "calificacion": "Muy Bueno",
        "direccion_consulta": "Las Amapolas 157 Villa Radiata Arauco",
        "horario_atencion": "10:00 - 20:00",
        "idiomas": "Español",
        "profesion": "Kinesiólogo",
        "estado": "activo",
        "disponible": True,
        "verificado": True,
    },
}

# Pacientes
PACIENTES_SIMULADOS = [
    {
        "id": "PAC_20250804_031213",
        "nombre": "Giselle",
        "apellido": "Arratia",
        "nombre_completo": "Giselle Arratia",
        "rut": "18145296-k",
        "edad": 34,
        "fecha_nacimiento": "1992-06-25",
        "genero": "Femenino",
        "telefono": "56978784574",
        "email": "giselle.arratia@gmail.com",
        "direccion": "Pasaje El Boldo 8654, Pudahuel, Santiago",
        "antecedentes_medicos": "HTA, EPOC",
        "fecha_primera_consulta": "2025-08-03",
        "ultima_consulta": "2025-08-03",
        "num_atenciones": 1,
        "estado_relacion": "activo",
        "fecha_registro": "2025-08-04",
        "notas": "Paciente con dolor lumbar crónico",
    },
    {
        "id": "PAC_20250804_003952",
        "nombre": "Roberto",
        "apellido": "Reyes",
        "nombre_completo": "Roberto Reyes",
        "rut": "17675599-8",
        "edad": 34,
        "fecha_nacimiento": "1992-02-04",
        "genero": "Masculino",
        "telefono": "56971714520",
        "email": "r.reyes@gmail.com",
        "direccion": "Los Reyes 1452, depto 123, Las Condes",
        "antecedentes_medicos": "Diabetes, HTA, Lesión meniscal",
        "fecha_primera_consulta": "2025-08-04",
        "ultima_consulta": "2025-08-04",
        "num_atenciones": 3,
        "estado_relacion": "activo",
        "fecha_registro": "2025-08-04",
        "notas": "Paciente con lesión deportiva",
    },
    {
        "id": "PAC_20250808_235925",
        "nombre": "Francisco",
        "apellido": "Reyes",
        "nombre_completo": "Francisco Reyes",
        "rut": "17675598-6",
        "edad": 35,
        "fecha_nacimiento": None,
        "genero": None,
        "telefono": None,
        "email": None,
        "direccion": None,
        "antecedentes_medicos": None,
        "fecha_primera_consulta": "2025-08-08",
        "ultima_consulta": "2025-08-08",
        "num_atenciones": 1,
        "estado_relacion": "activo",
        "fecha_registro": "2025-08-08",
        "notas": "Paciente creado automáticamente desde atención",
    },
]

# Atenciones médicas
ATENCIONES_SIMULADAS = [
    {
        "atencion_id": "ATN_20250804_031425",
        "profesional_id": 1,
        "profesional_nombre": "Diego Castro",
        "paciente_id": "PAC_20250804_031213",
        "paciente_nombre": "Giselle Arratia",
        "paciente_rut": "18145296-k",
        "paciente_edad": 34,
        "fecha_hora": "2025-08-03 23:13:00",
        "tipo_atencion": "kinesiologia",
        "motivo_consulta": "Dolor Lumbar por fuerza mal realizada al levantar caja en el trabajo",
        "diagnostico": "Eva 8/10, Kendall 3",
        "tratamiento": "Terapia Fortalecimiento del core, Fisioterapia, Crioterapia",
        "fecha_registro": "2025-08-04 03:14:25",
        "estado": "completada",
        "requiere_seguimiento": False,
        "tiene_archivos": "No",
    },
    {
        "atencion_id": "ATN_20250804_012642",
        "profesional_id": 1,
        "profesional_nombre": "Diego Castro",
        "paciente_id": "PAC_20250804_003952",
        "paciente_nombre": "Roberto Reyes",
        "paciente_rut": "17675599-8",
        "paciente_edad": 34,
        "fecha_hora": "2025-08-04 01:17:00",
        "tipo_atencion": "kinesiologia",
        "motivo_consulta": "Dolor en la rodilla por golpe en trabajo",
        "diagnostico": "Eva 7/10, Kendall 4, sensación de inestabilidad",
        "tratamiento": "Crioterapia, Fortalecimiento muscular",
        "fecha_registro": "2025-08-04 01:26:42",
        "estado": "completada",
        "requiere_seguimiento": False,
        "tiene_archivos": "Sí",
    },
    {
        "atencion_id": "ATN_20250808_235924",
        "profesional_id": 1,
        "profesional_nombre": "Diego Castro",
        "paciente_id": "PAC_20250808_235925",
        "paciente_nombre": "Francisco Reyes",
        "paciente_rut": "17675598-6",
        "paciente_edad": 35,
        "fecha_hora": "2025-08-08 23:40:00",
        "tipo_atencion": "kinesiologia",
        "motivo_consulta": "Dolor en la espalda en la zona lumbar por golpe en el trabajo",
        "diagnostico": "Eva 6/10, localización en L5/S1, irradiación a miembro inferior izquierdo",
        "tratamiento": "Terapia manual, electroterapia, ejercicios terapéuticos",
        "fecha_registro": "2025-08-08 23:59:24",
        "estado": "completada",
        "requiere_seguimiento": False,
        "tiene_archivos": "No",
    },
]

# Citas/Agenda
CITAS_SIMULADAS = [
    {
        "cita_id": "CITA_20250907_090000",
        "fecha": "2025-09-07",
        "hora_inicio": "09:00",
        "hora_fin": "10:00",
        "paciente_id": "PAC_20250804_031213",
        "paciente_nombre": "Giselle Arratia",
        "paciente_rut": "18145296-k",
        "tipo_atencion": "kinesiologia",
        "motivo": "Seguimiento dolor lumbar",
        "estado": "programada",
        "profesional_id": 1,
        "duracion": 60,
        "notas": "Continuar con terapia de fortalecimiento",
        "fecha_creacion": "2025-09-07T08:00:00Z",
    },
    {
        "cita_id": "CITA_20250907_110000",
        "fecha": "2025-09-07",
        "hora_inicio": "11:00",
        "hora_fin": "11:45",
        "paciente_id": "PAC_20250804_003952",
        "paciente_nombre": "Roberto Reyes",
        "paciente_rut": "17675599-8",
        "tipo_atencion": "kinesiologia",
        "motivo": "Seguimiento dolor rodilla",
        "estado": "programada",
        "profesional_id": 1,
        "duracion": 45,
        "notas": "Evaluar progreso del tratamiento",
        "fecha_creacion": "2025-09-07T08:00:00Z",
    },
    {
        "cita_id": "CITA_20250907_140000",
        "fecha": "2025-09-07",
        "hora_inicio": "14:00",
        "hora_fin": "14:30",
        "paciente_id": "PAC_20250804_031213",
        "paciente_nombre": "Giselle Arratia",
        "paciente_rut": "18145296-k",
        "tipo_atencion": "kinesiologia",
        "motivo": "Sesión de terapia",
        "estado": "programada",
        "profesional_id": 1,
        "duracion": 30,
        "notas": "Ejercicios de fortalecimiento del core",
        "fecha_creacion": "2025-09-07T08:00:00Z",
    },
]

# Sesiones de tratamiento
SESIONES_SIMULADAS = [
    {
        "id": "2f8f9c42-eca2-4501-b8ce-a398fbd8b9ab",
        "atencion_id": "ATN_20250804_031425",
        "fecha_sesion": "2025-08-04 05:42:00",
        "duracion": 60,
        "tipo_sesion": "tratamiento",
        "objetivos": "Modulación del dolor",
        "actividades": "Crioterapia, movilidad pasiva, bicicleta 15 min carga liviana",
        "observaciones": "Usuario presenta dolor aún en el movimiento pasivo 7/10",
        "progreso": "regular",
        "estado": "completada",
        "recomendaciones": "Se recomienda seguir con tratamiento en el hogar",
        "proxima_sesion": "La otra semana el mismo día",
        "fecha_creacion": "2025-08-04 01:48:46",
        "profesional_id": 1,
    }
]

# Recordatorios
RECORDATORIOS_SIMULADOS = [
    {
        "recordatorio_id": "8f684378-928b-4dc2-8590-c0244466a059",
        "profesional_id": 1,
        "tipo": "confirmacion",
        "paciente_id": "PAC_20250804_003952",
        "titulo": "Llamar a Paciente para confirmar cita",
        "mensaje": "No sabía si iba a tener permiso en el trabajo",
        "fecha": "2025-08-04",
        "hora": "2025-08-31 09:30:00",
        "prioridad": "alta",
        "repetir": False,
        "tipo_repeticion": "diario",
        "estado": "activo",
        "fecha_creacion": "2025-08-04 01:00:29",
    },
    {
        "recordatorio_id": "09213281-06e0-4cc6-af7e-01d8ffaeacd6",
        "profesional_id": 1,
        "tipo": "confirmacion",
        "paciente_id": "PAC_20250804_031213",
        "titulo": "Llamar a Paciente para confirmar cita",
        "mensaje": "Recordar esto",
        "fecha": "2025-08-12",
        "hora": "2025-08-31 14:40:00",
        "prioridad": "media",
        "repetir": False,
        "tipo_repeticion": "diario",
        "estado": "activo",
        "fecha_creacion": "2025-08-12 01:36:39",
    },
]

# Variables globales
start_time = time.time()

# ==================== FUNCIONES AUXILIARES ====================


def require_auth(f):
    """Decorador para requerir autenticación"""

    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


def get_current_user():
    """Obtiene el usuario actual de la sesión"""
    if "user_email" not in session:
        return None
    return USUARIOS_SIMULADOS.get(session["user_email"], {})


def generate_response(success=True, data=None, message="", total=None):
    """Genera respuesta JSON estándar"""
    response = {"success": success}
    if data is not None:
        response["data"] = data
    if message:
        response["message"] = message
    if total is not None:
        response["total"] = total
    return jsonify(response)


# ==================== RUTAS PRINCIPALES ====================


@app.route("/")
def index():
    """Página principal"""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Página de login"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Verificar credenciales
        if email in USUARIOS_SIMULADOS:
            usuario = USUARIOS_SIMULADOS[email]
            if usuario["password"] == password:
                # Iniciar sesión
                session["user_id"] = usuario["id"]
                session["user_email"] = email
                session["user_name"] = f"{usuario['nombre']} {usuario['apellido']}"
                session["user_type"] = usuario["tipo_usuario"]
                session["user_especialidad"] = usuario.get("especialidad", "")

                flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("professional"))
            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Página de registro"""
    if request.method == "POST":
        flash(
            "El registro está deshabilitado en modo offline. Usa las credenciales de prueba.",
            "info",
        )
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Cerrar sesión"""
    session.clear()
    flash("Sesión cerrada exitosamente", "info")
    return redirect(url_for("login"))


@app.route("/professional")
@require_auth
def professional():
    """Dashboard profesional"""
    usuario = get_current_user()

    # Estadísticas del dashboard
    stats = {
        "total_pacientes": len(PACIENTES_SIMULADOS),
        "total_atenciones": len(ATENCIONES_SIMULADAS),
        "citas_hoy": len(
            [
                c
                for c in CITAS_SIMULADAS
                if c["fecha"] == datetime.now().strftime("%Y-%m-%d")
            ]
        ),
        "recordatorios_pendientes": len(
            [r for r in RECORDATORIOS_SIMULADOS if r["estado"] == "activo"]
        ),
    }

    return render_template(
        "professional.html",
        usuario=usuario,
        pacientes=PACIENTES_SIMULADOS,
        atenciones=ATENCIONES_SIMULADAS,
        citas=CITAS_SIMULADAS,
        stats=stats,
    )


@app.route("/profile")
@require_auth
def profile():
    """Página de perfil del usuario"""
    usuario = get_current_user()
    return render_template("profile.html", usuario=usuario)


@app.route("/reports")
@require_auth
def reports():
    """Página de informes"""
    usuario = get_current_user()
    return render_template(
        "reports.html", usuario=usuario, atenciones=ATENCIONES_SIMULADAS
    )


@app.route("/patients")
@require_auth
def patients():
    """Página de pacientes"""
    usuario = get_current_user()
    return render_template(
        "patients.html", usuario=usuario, pacientes=PACIENTES_SIMULADOS
    )


@app.route("/consultations")
@require_auth
def consultations():
    """Página de consultas"""
    usuario = get_current_user()
    return render_template(
        "consultations.html", usuario=usuario, atenciones=ATENCIONES_SIMULADAS
    )


@app.route("/schedule")
@require_auth
def schedule():
    """Página de agenda"""
    usuario = get_current_user()
    return render_template("schedule.html", usuario=usuario, citas=CITAS_SIMULADAS)


# ==================== API ENDPOINTS ====================


@app.route("/api/health")
def health_check():
    """Health check"""
    return generate_response(
        data={
            "status": "healthy",
            "mode": "offline",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - start_time,
            "database": "simulated",
            "version": "1.0.0",
        }
    )


@app.route("/health")
def health_alt():
    """Health check alternativo"""
    return health_check()


@app.route("/api/patients")
@require_auth
def api_patients():
    """API para obtener pacientes"""
    return generate_response(
        data=PACIENTES_SIMULADOS,
        total=len(PACIENTES_SIMULADOS),
        message="Pacientes obtenidos exitosamente",
    )


@app.route("/api/consultations")
@require_auth
def api_consultations():
    """API para obtener consultas"""
    return generate_response(
        data=ATENCIONES_SIMULADAS,
        total=len(ATENCIONES_SIMULADAS),
        message="Consultas obtenidas exitosamente",
    )


@app.route("/api/get-atenciones")
@require_auth
def api_get_atenciones():
    """API para obtener atenciones (alias de consultations)"""
    return api_consultations()


@app.route("/api/professional/patients")
@require_auth
def api_professional_patients():
    """API para obtener pacientes del profesional"""
    return generate_response(
        data=PACIENTES_SIMULADOS,
        total=len(PACIENTES_SIMULADOS),
        message="Pacientes del profesional obtenidos exitosamente",
    )


@app.route("/api/professional/schedule")
@require_auth
def api_professional_schedule():
    """API para obtener agenda del profesional"""
    fecha = request.args.get("fecha", datetime.now().strftime("%Y-%m-%d"))
    vista = request.args.get("vista", "diaria")

    # Filtrar citas por fecha si se especifica
    citas_filtradas = [c for c in CITAS_SIMULADAS if c["fecha"] == fecha]

    return generate_response(
        data=citas_filtradas,
        total=len(citas_filtradas),
        message="Agenda cargada exitosamente",
        fecha=fecha,
        vista=vista,
    )


@app.route("/api/schedule")
@require_auth
def api_schedule():
    """API para obtener agenda"""
    return generate_response(
        data=CITAS_SIMULADAS,
        total=len(CITAS_SIMULADAS),
        message="Agenda obtenida exitosamente",
    )


@app.route("/api/agenda")
@require_auth
def api_agenda():
    """API alternativa para agenda"""
    fecha = request.args.get("fecha", datetime.now().strftime("%Y-%m-%d"))
    citas_filtradas = [c for c in CITAS_SIMULADAS if c["fecha"] == fecha]

    return generate_response(
        data=citas_filtradas,
        total=len(citas_filtradas),
        message="Agenda obtenida exitosamente",
    )


@app.route("/api/citas")
@require_auth
def api_citas():
    """API para citas"""
    return generate_response(
        data=CITAS_SIMULADAS,
        total=len(CITAS_SIMULADAS),
        message="Citas obtenidas exitosamente",
    )


@app.route("/api/reports")
@require_auth
def api_reports():
    """API para obtener informes"""
    reports_data = [
        {
            "id": "RPT_001",
            "titulo": "Resumen Mensual",
            "fecha": "2025-08-01",
            "tipo": "mensual",
            "total_pacientes": len(PACIENTES_SIMULADOS),
            "total_atenciones": len(ATENCIONES_SIMULADAS),
            "total_citas": len(CITAS_SIMULADAS),
            "estado": "completado",
        },
        {
            "id": "RPT_002",
            "titulo": "Atenciones del Mes",
            "fecha": "2025-08-01",
            "tipo": "atenciones",
            "total_atenciones": len(ATENCIONES_SIMULADAS),
            "atenciones_completadas": len(
                [a for a in ATENCIONES_SIMULADAS if a["estado"] == "completada"]
            ),
            "estado": "completado",
        },
        {
            "id": "RPT_003",
            "titulo": "Pacientes Activos",
            "fecha": "2025-08-01",
            "tipo": "pacientes",
            "total_pacientes": len(PACIENTES_SIMULADOS),
            "pacientes_activos": len(
                [p for p in PACIENTES_SIMULADOS if p["estado_relacion"] == "activo"]
            ),
            "estado": "completado",
        },
    ]

    return generate_response(
        data=reports_data,
        total=len(reports_data),
        message="Informes obtenidos exitosamente",
    )


@app.route("/api/sessions")
@require_auth
def api_sessions():
    """API para obtener sesiones de tratamiento"""
    return generate_response(
        data=SESIONES_SIMULADAS,
        total=len(SESIONES_SIMULADAS),
        message="Sesiones obtenidas exitosamente",
    )


@app.route("/api/reminders")
@require_auth
def api_reminders():
    """API para obtener recordatorios"""
    return generate_response(
        data=RECORDATORIOS_SIMULADOS,
        total=len(RECORDATORIOS_SIMULADOS),
        message="Recordatorios obtenidos exitosamente",
    )


@app.route("/api/test-atencion")
@require_auth
def api_test_atencion():
    """API de prueba para atenciones"""
    return generate_response(
        data=ATENCIONES_SIMULADAS[0] if ATENCIONES_SIMULADAS else {},
        message="API de prueba funcionando correctamente",
    )


@app.route("/api/copilot/chat", methods=["POST"])
@require_auth
def api_copilot_chat():
    """API para chat con Copilot (simulado)"""
    data = request.get_json()
    message = data.get("message", "") if data else ""

    # Respuestas simuladas del Copilot
    responses = [
        "Hola, soy tu asistente de IA. ¿En qué puedo ayudarte?",
        "Puedo ayudarte con información médica y gestión de pacientes.",
        "¿Necesitas ayuda con alguna consulta específica?",
        "Estoy aquí para asistirte en tu trabajo médico.",
        "¿Hay algo en particular que te gustaría saber?",
        "Puedo ayudarte a revisar el historial de tus pacientes.",
        "¿Te gustaría que revise alguna cita programada?",
        "Estoy disponible para consultas sobre tratamientos.",
    ]

    response = random.choice(responses)

    return generate_response(
        data={
            "response": response,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "type": "assistant",
        },
        message="Respuesta del asistente generada",
    )


@app.route("/api/user/profile")
@require_auth
def api_user_profile():
    """API para obtener perfil del usuario"""
    usuario = get_current_user()
    return generate_response(data=usuario, message="Perfil obtenido exitosamente")


@app.route("/api/dashboard/stats")
@require_auth
def api_dashboard_stats():
    """API para estadísticas del dashboard"""
    stats = {
        "total_pacientes": len(PACIENTES_SIMULADOS),
        "total_atenciones": len(ATENCIONES_SIMULADAS),
        "citas_hoy": len(
            [
                c
                for c in CITAS_SIMULADAS
                if c["fecha"] == datetime.now().strftime("%Y-%m-%d")
            ]
        ),
        "citas_semana": len(
            [
                c
                for c in CITAS_SIMULADAS
                if c["fecha"]
                >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            ]
        ),
        "recordatorios_pendientes": len(
            [r for r in RECORDATORIOS_SIMULADOS if r["estado"] == "activo"]
        ),
        "atenciones_completadas": len(
            [a for a in ATENCIONES_SIMULADAS if a["estado"] == "completada"]
        ),
        "pacientes_activos": len(
            [p for p in PACIENTES_SIMULADOS if p["estado_relacion"] == "activo"]
        ),
    }

    return generate_response(data=stats, message="Estadísticas obtenidas exitosamente")


# ==================== ARCHIVOS ESTÁTICOS ====================


@app.route("/favicon.ico")
def favicon():
    """Favicon"""
    return "", 204


# ==================== MANEJO DE ERRORES ====================


@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    return generate_response(success=False, message="Página no encontrada"), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500"""
    return generate_response(success=False, message="Error interno del servidor"), 500


# ==================== INICIO DE LA APLICACIÓN ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    print("🚀 Iniciando MedConnect - Versión Auditada y Optimizada...")
    print("=" * 70)
    print(f"🌐 URL: http://localhost:{port}")
    print(f"🔐 Login: http://localhost:{port}/login")
    print(f"❤️ Health: http://localhost:{port}/api/health")
    print("\n👤 Credenciales de prueba:")
    print("  📧 diego.castro.lagos@gmail.com / password123")
    print("  📧 rodrigoandressilvabreve@gmail.com / password123")
    print("\n📋 Funcionalidades disponibles:")
    print("  ✅ Dashboard profesional completo")
    print("  ✅ Gestión de pacientes")
    print("  ✅ Historial de atenciones")
    print("  ✅ Sistema de citas/agenda")
    print("  ✅ Informes y estadísticas")
    print("  ✅ Sesiones de tratamiento")
    print("  ✅ Recordatorios")
    print("  ✅ Chat con asistente IA")
    print("  ✅ APIs completas")
    print("\n📊 Datos simulados:")
    print(f"  👥 {len(PACIENTES_SIMULADOS)} pacientes")
    print(f"  🏥 {len(ATENCIONES_SIMULADAS)} atenciones")
    print(f"  📅 {len(CITAS_SIMULADOS)} citas")
    print(f"  📋 {len(SESIONES_SIMULADAS)} sesiones")
    print(f"  🔔 {len(RECORDATORIOS_SIMULADOS)} recordatorios")
    print("\n" + "=" * 70)
    print("🛑 Presiona Ctrl+C para detener")
    print("=" * 70)

    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
