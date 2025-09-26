#!/usr/bin/env python3
"""
MedConnect - Versión OFFLINE para desarrollo local
Esta versión funciona sin conexión a base de datos externa
"""

import os
import sys
import logging
import time
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

# Datos simulados para desarrollo offline
USUARIOS_SIMULADOS = {
    "diego.castro.lagos@gmail.com": {
        "id": 1,
        "nombre": "Diego",
        "apellido": "Castro",
        "email": "diego.castro.lagos@gmail.com",
        "password": "password123",  # En producción esto estaría hasheado
        "tipo_usuario": "profesional",
        "telefono": "56979712175",
        "especialidad": "Kinesiología",
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
    },
}

PACIENTES_SIMULADOS = [
    {
        "id": "PAC_001",
        "nombre": "Giselle Arratia",
        "rut": "18145296-k",
        "edad": 34,
        "telefono": "56978784574",
        "email": "giselle.arratia@gmail.com",
        "estado": "activo",
    },
    {
        "id": "PAC_002",
        "nombre": "Roberto Reyes",
        "rut": "17675599-8",
        "edad": 34,
        "telefono": "56971714520",
        "email": "r.reyes@gmail.com",
        "estado": "activo",
    },
]

ATENCIONES_SIMULADAS = [
    {
        "id": "ATN_001",
        "paciente_nombre": "Giselle Arratia",
        "fecha": "2025-08-03",
        "motivo": "Dolor Lumbar",
        "diagnostico": "Eva 8/10, Kendall 3",
        "tratamiento": "Terapia Fortalecimiento del core",
        "estado": "completada",
    },
    {
        "id": "ATN_002",
        "paciente_nombre": "Roberto Reyes",
        "fecha": "2025-08-04",
        "motivo": "Dolor en la rodilla",
        "diagnostico": "Eva 7/10, Kendall 4",
        "tratamiento": "Crioterapia, Fortalecimiento muscular",
        "estado": "completada",
    },
]

# Variables globales
start_time = time.time()

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

        # Verificar credenciales en datos simulados
        if email in USUARIOS_SIMULADOS:
            usuario = USUARIOS_SIMULADOS[email]
            if usuario["password"] == password:
                # Iniciar sesión
                session["user_id"] = usuario["id"]
                session["user_email"] = email
                session["user_name"] = f"{usuario['nombre']} {usuario['apellido']}"
                session["user_type"] = usuario["tipo_usuario"]

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
        # En modo offline, solo mostrar mensaje
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
def professional():
    """Dashboard profesional"""
    if "user_id" not in session:
        flash("Debes iniciar sesión para acceder", "error")
        return redirect(url_for("login"))

    # Obtener datos del usuario
    user_email = session.get("user_email")
    usuario = USUARIOS_SIMULADOS.get(user_email, {})

    return render_template(
        "professional.html",
        usuario=usuario,
        pacientes=PACIENTES_SIMULADOS,
        atenciones=ATENCIONES_SIMULADAS,
    )


# ==================== API ENDPOINTS ====================


@app.route("/api/health")
def health_check():
    """Health check"""
    return jsonify(
        {
            "status": "healthy",
            "mode": "offline",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - start_time,
            "database": "simulated",
        }
    )


@app.route("/api/patients")
def api_patients():
    """API para obtener pacientes"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    return jsonify(
        {
            "success": True,
            "data": PACIENTES_SIMULADOS,
            "total": len(PACIENTES_SIMULADOS),
        }
    )


@app.route("/api/consultations")
def api_consultations():
    """API para obtener consultas"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    return jsonify(
        {
            "success": True,
            "data": ATENCIONES_SIMULADAS,
            "total": len(ATENCIONES_SIMULADAS),
        }
    )


@app.route("/api/reports")
def api_reports():
    """API para obtener informes"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    # Generar informes simulados
    reports_data = [
        {
            "id": "RPT_001",
            "titulo": "Resumen Mensual",
            "fecha": "2025-08-01",
            "tipo": "mensual",
            "total_pacientes": len(PACIENTES_SIMULADOS),
            "total_atenciones": len(ATENCIONES_SIMULADAS),
            "estado": "completado",
        },
        {
            "id": "RPT_002",
            "titulo": "Atenciones del Mes",
            "fecha": "2025-08-01",
            "tipo": "atenciones",
            "total_atenciones": len(ATENCIONES_SIMULADAS),
            "estado": "completado",
        },
    ]

    return jsonify({"success": True, "data": reports_data, "total": len(reports_data)})


@app.route("/api/schedule")
def api_schedule():
    """API para obtener agenda"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    # Generar agenda simulada
    schedule_data = [
        {
            "id": "SCH_001",
            "fecha": "2025-09-08",
            "hora": "09:00",
            "paciente": "Giselle Arratia",
            "tipo": "Consulta",
            "estado": "programada",
        },
        {
            "id": "SCH_002",
            "fecha": "2025-09-08",
            "hora": "11:00",
            "paciente": "Roberto Reyes",
            "tipo": "Seguimiento",
            "estado": "programada",
        },
    ]

    return jsonify(
        {"success": True, "data": schedule_data, "total": len(schedule_data)}
    )


@app.route("/profile")
def profile():
    """Página de perfil del usuario"""
    if "user_id" not in session:
        flash("Debes iniciar sesión para acceder", "error")
        return redirect(url_for("login"))

    # Obtener datos del usuario
    user_email = session.get("user_email")
    usuario = USUARIOS_SIMULADOS.get(user_email, {})

    return render_template("profile.html", usuario=usuario)


@app.route("/reports")
def reports():
    """Página de informes"""
    if "user_id" not in session:
        flash("Debes iniciar sesión para acceder", "error")
        return redirect(url_for("login"))

    # Obtener datos del usuario
    user_email = session.get("user_email")
    usuario = USUARIOS_SIMULADOS.get(user_email, {})

    return render_template(
        "reports.html", usuario=usuario, atenciones=ATENCIONES_SIMULADAS
    )


@app.route("/patients")
def patients():
    """Página de pacientes"""
    if "user_id" not in session:
        flash("Debes iniciar sesión para acceder", "error")
        return redirect(url_for("login"))

    # Obtener datos del usuario
    user_email = session.get("user_email")
    usuario = USUARIOS_SIMULADOS.get(user_email, {})

    return render_template(
        "patients.html", usuario=usuario, pacientes=PACIENTES_SIMULADOS
    )


@app.route("/consultations")
def consultations():
    """Página de consultas"""
    if "user_id" not in session:
        flash("Debes iniciar sesión para acceder", "error")
        return redirect(url_for("login"))

    # Obtener datos del usuario
    user_email = session.get("user_email")
    usuario = USUARIOS_SIMULADOS.get(user_email, {})

    return render_template(
        "consultations.html", usuario=usuario, atenciones=ATENCIONES_SIMULADAS
    )


@app.route("/schedule")
def schedule():
    """Página de agenda"""
    if "user_id" not in session:
        flash("Debes iniciar sesión para acceder", "error")
        return redirect(url_for("login"))

    # Obtener datos del usuario
    user_email = session.get("user_email")
    usuario = USUARIOS_SIMULADOS.get(user_email, {})

    return render_template("schedule.html", usuario=usuario)


@app.route("/api/get-atenciones")
def api_get_atenciones():
    """API para obtener atenciones (alias de consultations)"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    return jsonify(
        {
            "success": True,
            "data": ATENCIONES_SIMULADAS,
            "total": len(ATENCIONES_SIMULADAS),
        }
    )


@app.route("/api/professional/patients")
def api_professional_patients():
    """API para obtener pacientes del profesional"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    return jsonify(
        {
            "success": True,
            "data": PACIENTES_SIMULADOS,
            "total": len(PACIENTES_SIMULADOS),
        }
    )


@app.route("/api/professional/schedule")
def api_professional_schedule():
    """API para obtener agenda del profesional"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    # Obtener parámetros de consulta
    fecha = request.args.get("fecha", "2025-09-07")
    vista = request.args.get("vista", "diaria")

    # Generar agenda simulada con formato correcto
    schedule_data = [
        {
            "cita_id": "CITA_20250907_090000",
            "fecha": fecha,
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
            "fecha": fecha,
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
            "fecha": fecha,
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

    # Formato de respuesta estándar
    response_data = {
        "success": True,
        "data": schedule_data,
        "total": len(schedule_data),
        "fecha": fecha,
        "vista": vista,
        "message": "Agenda cargada exitosamente",
    }

    return jsonify(response_data)


@app.route("/api/test-atencion")
def api_test_atencion():
    """API de prueba para atenciones"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    return jsonify(
        {
            "success": True,
            "message": "API de prueba funcionando",
            "data": ATENCIONES_SIMULADAS[0] if ATENCIONES_SIMULADAS else {},
        }
    )


@app.route("/api/copilot/chat", methods=["POST"])
def api_copilot_chat():
    """API para chat con Copilot (simulado)"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json()
    message = data.get("message", "") if data else ""

    # Respuesta simulada del Copilot
    responses = [
        "Hola, soy tu asistente de IA. ¿En qué puedo ayudarte?",
        "Puedo ayudarte con información médica y gestión de pacientes.",
        "¿Necesitas ayuda con alguna consulta específica?",
        "Estoy aquí para asistirte en tu trabajo médico.",
        "¿Hay algo en particular que te gustaría saber?",
    ]

    import random

    response = random.choice(responses)

    return jsonify(
        {
            "success": True,
            "response": response,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/health")
def health():
    """Health check alternativo"""
    return jsonify(
        {
            "status": "healthy",
            "mode": "offline",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - start_time,
            "database": "simulated",
        }
    )


@app.route("/api/agenda")
def api_agenda():
    """API alternativa para agenda"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    # Obtener parámetros de consulta
    fecha = request.args.get("fecha", "2025-09-07")

    # Usar los mismos datos que professional/schedule
    schedule_data = [
        {
            "cita_id": "CITA_20250907_090000",
            "fecha": fecha,
            "hora_inicio": "09:00",
            "hora_fin": "10:00",
            "paciente_nombre": "Giselle Arratia",
            "tipo_atencion": "kinesiologia",
            "motivo": "Seguimiento dolor lumbar",
            "estado": "programada",
        },
        {
            "cita_id": "CITA_20250907_110000",
            "fecha": fecha,
            "hora_inicio": "11:00",
            "hora_fin": "11:45",
            "paciente_nombre": "Roberto Reyes",
            "tipo_atencion": "kinesiologia",
            "motivo": "Seguimiento dolor rodilla",
            "estado": "programada",
        },
    ]

    return jsonify(
        {
            "success": True,
            "data": schedule_data,
            "total": len(schedule_data),
            "fecha": fecha,
        }
    )


@app.route("/api/citas")
def api_citas():
    """API para citas"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    # Datos de citas simuladas
    citas_data = [
        {
            "id": "CITA_001",
            "fecha": "2025-09-07",
            "hora": "09:00",
            "paciente": "Giselle Arratia",
            "tipo": "Consulta",
            "estado": "programada",
            "motivo": "Seguimiento",
        },
        {
            "id": "CITA_002",
            "fecha": "2025-09-07",
            "hora": "11:00",
            "paciente": "Roberto Reyes",
            "tipo": "Seguimiento",
            "estado": "programada",
            "motivo": "Evaluación",
        },
    ]

    return jsonify({"success": True, "data": citas_data, "total": len(citas_data)})


@app.route("/api/user/profile")
def api_user_profile():
    """API para obtener perfil del usuario"""
    if "user_id" not in session:
        return jsonify({"error": "No autorizado"}), 401

    user_email = session.get("user_email")
    usuario = USUARIOS_SIMULADOS.get(user_email, {})

    return jsonify({"success": True, "data": usuario})


# ==================== ARCHIVOS ESTÁTICOS ====================


@app.route("/favicon.ico")
def favicon():
    """Favicon"""
    return "", 204


# ==================== MANEJO DE ERRORES ====================


@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    return jsonify({"error": "Página no encontrada"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500"""
    return jsonify({"error": "Error interno del servidor"}), 500


# ==================== INICIO DE LA APLICACIÓN ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    print("🚀 Iniciando MedConnect en modo OFFLINE...")
    print("=" * 60)
    print(f"🌐 URL: http://localhost:{port}")
    print(f"🔐 Login: http://localhost:{port}/login")
    print(f"❤️ Health: http://localhost:{port}/api/health")
    print("\n👤 Credenciales de prueba:")
    print("  📧 diego.castro.lagos@gmail.com / password123")
    print("  📧 rodrigoandressilvabreve@gmail.com / password123")
    print("\n📋 Características del modo offline:")
    print("  ✅ Sin conexión a base de datos externa")
    print("  ✅ Datos simulados para desarrollo")
    print("  ✅ Todas las funcionalidades disponibles")
    print("  ✅ Ideal para desarrollo y pruebas")
    print("\n" + "=" * 60)
    print("🛑 Presiona Ctrl+C para detener")
    print("=" * 60)

    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
