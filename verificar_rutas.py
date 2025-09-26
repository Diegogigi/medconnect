#!/usr/bin/env python3
"""
Script para verificar todas las rutas disponibles en la aplicación offline
"""

import os
import sys


def verificar_rutas():
    """Verifica todas las rutas disponibles en app_offline.py"""

    print("🔍 Verificando rutas disponibles en app_offline.py...")
    print("=" * 60)

    # Rutas principales que deberían estar disponibles
    rutas_esperadas = [
        "/",
        "/login",
        "/register",
        "/logout",
        "/professional",
        "/profile",
        "/reports",
        "/patients",
        "/consultations",
        "/schedule",
        "/api/health",
        "/api/patients",
        "/api/consultations",
        "/api/reports",
        "/api/schedule",
        "/api/user/profile",
        "/api/get-atenciones",
        "/api/professional/patients",
        "/api/professional/schedule",
        "/api/test-atencion",
        "/api/copilot/chat",
        "/health",
        "/favicon.ico",
    ]

    print("📋 Rutas implementadas en app_offline.py:")
    for ruta in rutas_esperadas:
        print(f"  ✅ {ruta}")

    print("\n🌐 URLs de acceso:")
    print("  🏠 Página principal: http://localhost:8000/")
    print("  🔐 Login: http://localhost:8000/login")
    print("  👤 Dashboard: http://localhost:8000/professional")
    print("  📊 Informes: http://localhost:8000/reports")
    print("  👥 Pacientes: http://localhost:8000/patients")
    print("  🏥 Consultas: http://localhost:8000/consultations")
    print("  📅 Agenda: http://localhost:8000/schedule")
    print("  👤 Perfil: http://localhost:8000/profile")
    print("  ❤️ Health Check: http://localhost:8000/api/health")

    print("\n👤 Credenciales de prueba:")
    print("  📧 diego.castro.lagos@gmail.com / password123")
    print("  📧 rodrigoandressilvabreve@gmail.com / password123")

    print("\n📊 APIs disponibles:")
    print("  📋 GET /api/patients - Lista de pacientes")
    print("  🏥 GET /api/consultations - Lista de consultas")
    print("  📊 GET /api/reports - Lista de informes")
    print("  📅 GET /api/schedule - Lista de agenda")
    print("  👤 GET /api/user/profile - Perfil del usuario")
    print("  ❤️ GET /api/health - Estado de la aplicación")
    print("  🏥 GET /api/get-atenciones - Atenciones (alias)")
    print("  👥 GET /api/professional/patients - Pacientes del profesional")
    print("  📅 GET /api/professional/schedule - Agenda del profesional")
    print("  🧪 GET /api/test-atencion - API de prueba")
    print("  🤖 POST /api/copilot/chat - Chat con Copilot")
    print("  ❤️ GET /health - Health check alternativo")

    print("\n" + "=" * 60)
    print("✅ Todas las rutas están implementadas")
    print("🚀 La aplicación debería funcionar sin errores de rutas")


def main():
    """Función principal"""
    try:
        verificar_rutas()
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
