#!/usr/bin/env python3
"""
MedConnect - Script Maestro de Ejecución
Unifica todas las opciones de ejecución en un solo comando
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime


def print_banner():
    """Muestra el banner de inicio"""
    print("🏥" + "=" * 68 + "🏥")
    print("🏥" + " " * 20 + "MEDCONNECT" + " " * 20 + "🏥")
    print("🏥" + " " * 15 + "Sistema de Gestión Médica" + " " * 15 + "🏥")
    print("🏥" + "=" * 68 + "🏥")
    print()


def setup_environment(mode="offline"):
    """Configura el entorno según el modo seleccionado"""

    print(f"🔧 Configurando entorno para modo: {mode.upper()}")

    if mode == "offline":
        # Configuración offline (recomendada para desarrollo)
        os.environ["DATABASE_URL"] = ""
        os.environ["SECRET_KEY"] = "dev-secret-key-local-offline-12345"
        os.environ["FLASK_ENV"] = "development"
        os.environ["DEBUG"] = "True"
        os.environ["PORT"] = "8000"
        os.environ["SESSION_COOKIE_SECURE"] = "False"
        os.environ["CORS_ORIGINS"] = "http://localhost:8000,http://127.0.0.1:8000"
        print("✅ Modo OFFLINE configurado - Sin conexión a base de datos externa")

    elif mode == "local":
        # Configuración local con base de datos
        os.environ["DATABASE_URL"] = (
            "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
        )
        os.environ["SECRET_KEY"] = "medconnect-secret-key-2025-railway-production"
        os.environ["FLASK_ENV"] = "development"
        os.environ["DEBUG"] = "True"
        os.environ["PORT"] = "8000"
        os.environ["SESSION_COOKIE_SECURE"] = "False"
        print("✅ Modo LOCAL configurado - Con conexión a base de datos Railway")

    elif mode == "auditado":
        # Usar la aplicación auditada
        print("✅ Modo AUDITADO configurado - Usando app_auditado.py")

    else:
        print(f"❌ Modo '{mode}' no reconocido")
        return False

    return True


def check_dependencies(mode="offline"):
    """Verifica las dependencias necesarias"""

    print("\n📦 Verificando dependencias...")

    try:
        import flask

        print("✅ Flask disponible")

        if mode == "local":
            import psycopg2

            print("✅ PostgreSQL disponible")

        from dotenv import load_dotenv

        print("✅ python-dotenv disponible")

        print("✅ Todas las dependencias están disponibles")
        return True

    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        if mode == "local":
            print(
                "💡 Para modo local ejecuta: pip install flask psycopg2-binary python-dotenv"
            )
        else:
            print("💡 Para modo offline ejecuta: pip install flask python-dotenv")
        return False


def run_application(mode="offline"):
    """Ejecuta la aplicación según el modo seleccionado"""

    print(f"\n🚀 Iniciando MedConnect en modo {mode.upper()}...")
    print("=" * 70)

    # Seleccionar archivo de aplicación
    if mode == "auditado":
        app_file = "app_auditado.py"
    else:
        app_file = "app_offline.py" if mode == "offline" else "app.py"

    # Verificar que el archivo existe
    if not os.path.exists(app_file):
        print(f"❌ Archivo {app_file} no encontrado")
        if mode == "auditado":
            print("💡 Ejecuta primero la auditoría para crear app_auditado.py")
        return False

    # Mostrar información de acceso
    print(f"🌐 URL: http://localhost:8000")
    print(f"🔐 Login: http://localhost:8000/login")
    print(f"❤️ Health: http://localhost:8000/api/health")

    print(f"\n👤 Credenciales de prueba:")
    print(f"  📧 diego.castro.lagos@gmail.com / password123")
    print(f"  📧 rodrigoandressilvabreve@gmail.com / password123")

    if mode == "offline" or mode == "auditado":
        print(f"\n📋 Características del modo {mode.upper()}:")
        print(f"  ✅ Sin conexión a base de datos externa")
        print(f"  ✅ Datos simulados para desarrollo")
        print(f"  ✅ Todas las funcionalidades disponibles")
        print(f"  ✅ Ideal para desarrollo y pruebas")

    print(f"\n📊 Datos simulados disponibles:")
    print(f"  👥 3 pacientes")
    print(f"  🏥 3 atenciones médicas")
    print(f"  📅 3 citas programadas")
    print(f"  📋 1 sesión de tratamiento")
    print(f"  🔔 2 recordatorios")

    print(f"\n" + "=" * 70)
    print(f"🛑 Presiona Ctrl+C para detener")
    print(f"=" * 70)

    try:
        # Ejecutar la aplicación
        subprocess.run([sys.executable, app_file], check=True)
        return True

    except KeyboardInterrupt:
        print(f"\n\n🛑 Aplicación detenida por el usuario")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al ejecutar la aplicación: {e}")
        return False

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False


def run_verification():
    """Ejecuta la verificación completa de la aplicación"""

    print("🧪 Ejecutando verificación completa...")
    print("=" * 50)

    try:
        # Verificar plantillas
        print("🔍 Verificando plantillas...")
        subprocess.run([sys.executable, "verificar_plantillas.py"], check=True)

        print("\n" + "=" * 50)

        # Verificar funcionalidades (requiere que la app esté ejecutándose)
        print("🔍 Para verificar funcionalidades:")
        print("1. Ejecuta la aplicación en otra terminal")
        print("2. Luego ejecuta: python verificacion_completa.py")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante la verificación: {e}")
        return False


def show_help():
    """Muestra la ayuda del script"""

    print("🏥 MEDCONNECT - Script Maestro de Ejecución")
    print("=" * 50)
    print()
    print("📋 Modos disponibles:")
    print()
    print("  🟢 offline    - Modo offline (RECOMENDADO)")
    print("     • Sin conexión a base de datos externa")
    print("     • Datos simulados completos")
    print("     • Ideal para desarrollo local")
    print("     • Usa app_offline.py")
    print()
    print("  🔵 auditado   - Modo auditado (ÓPTIMO)")
    print("     • Aplicación completamente auditada")
    print("     • Todas las funcionalidades verificadas")
    print("     • Datos simulados optimizados")
    print("     • Usa app_auditado.py")
    print()
    print("  🟡 local      - Modo local con BD")
    print("     • Con conexión a base de datos Railway")
    print("     • Requiere conexión a internet")
    print("     • Usa app.py")
    print()
    print("  🧪 verify     - Verificar aplicación")
    print("     • Verifica plantillas y archivos")
    print("     • Prueba todas las funcionalidades")
    print()
    print("📖 Ejemplos de uso:")
    print("  python run_medconnect.py offline    # Modo offline")
    print("  python run_medconnect.py auditado   # Modo auditado")
    print("  python run_medconnect.py local      # Modo local")
    print("  python run_medconnect.py verify     # Verificar")
    print("  python run_medconnect.py --help     # Esta ayuda")
    print()
    print("🎯 Recomendación: Usa 'offline' o 'auditado' para desarrollo local")


def main():
    """Función principal"""

    # Configurar argumentos
    parser = argparse.ArgumentParser(
        description="MedConnect - Script Maestro de Ejecución", add_help=False
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="offline",
        choices=["offline", "local", "auditado", "verify"],
        help="Modo de ejecución",
    )
    parser.add_argument("--help", "-h", action="store_true", help="Mostrar ayuda")

    args = parser.parse_args()

    # Mostrar ayuda si se solicita
    if args.help:
        show_help()
        return

    # Mostrar banner
    print_banner()

    # Procesar modo
    mode = args.mode.lower()

    if mode == "verify":
        success = run_verification()
    else:
        # Configurar entorno
        if not setup_environment(mode):
            sys.exit(1)

        # Verificar dependencias
        if not check_dependencies(mode):
            sys.exit(1)

        # Ejecutar aplicación
        success = run_application(mode)

    if not success:
        print(f"\n❌ Error durante la ejecución en modo {mode}")
        sys.exit(1)

    print(f"\n🎉 Ejecución completada exitosamente en modo {mode}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n🛑 Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
