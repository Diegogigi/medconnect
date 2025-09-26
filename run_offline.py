#!/usr/bin/env python3
"""
Script para ejecutar MedConnect en modo OFFLINE
Ideal para desarrollo local sin conexión a la base de datos de Railway
"""

import os
import sys
import subprocess


def run_offline():
    """Ejecuta la aplicación en modo offline"""

    print("🚀 Iniciando MedConnect en modo OFFLINE...")
    print("=" * 60)

    # 1. Configurar entorno offline
    print("🔧 Configurando entorno offline...")
    try:
        from config_desarrollo_offline import configurar_desarrollo_offline

        configurar_desarrollo_offline()
    except ImportError:
        print(
            "⚠️ No se pudo importar config_desarrollo_offline, usando configuración manual..."
        )
        # Configuración manual offline
        os.environ["DATABASE_URL"] = ""
        os.environ["SECRET_KEY"] = "dev-secret-key-local-offline-12345"
        os.environ["FLASK_ENV"] = "development"
        os.environ["DEBUG"] = "True"
        os.environ["PORT"] = "8000"
        os.environ["SESSION_COOKIE_SECURE"] = "False"
        os.environ["CORS_ORIGINS"] = "http://localhost:8000,http://127.0.0.1:8000"

    # 2. Verificar dependencias básicas
    print("\n📦 Verificando dependencias básicas...")
    try:
        import flask
        from dotenv import load_dotenv

        print("✅ Dependencias básicas disponibles")
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("💡 Ejecuta: pip install flask python-dotenv")
        return False

    # 3. Ejecutar aplicación
    print("\n🚀 Iniciando aplicación en modo offline...")
    print("🌐 La aplicación estará disponible en: http://localhost:8000")
    print("🔐 Login: http://localhost:8000/login")
    print("❤️ Health Check: http://localhost:8000/health")
    print("\n👤 Credenciales de prueba (datos simulados):")
    print("  📧 diego.castro.lagos@gmail.com / password123")
    print("  📧 rodrigoandressilvabreve@gmail.com / password123")
    print("\n📋 Modo OFFLINE activado:")
    print("  ✅ Sin conexión a base de datos externa")
    print("  ✅ Datos simulados para desarrollo")
    print("  ✅ Todas las funcionalidades disponibles")
    print("\n" + "=" * 60)
    print("🛑 Presiona Ctrl+C para detener la aplicación")
    print("=" * 60)

    try:
        # Ejecutar app.py
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Aplicación detenida por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al ejecutar la aplicación: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

    return True


def main():
    """Función principal"""
    try:
        success = run_offline()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
