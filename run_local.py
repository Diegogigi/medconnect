#!/usr/bin/env python3
"""
Script para ejecutar la aplicación localmente en modo desarrollo
"""

import os
import sys
from config_local import setup_local_environment


def run_local():
    """Ejecuta la aplicación en modo desarrollo local"""

    print("🚀 Iniciando MedConnect en modo desarrollo local...")

    # Configurar entorno local
    setup_local_environment()

    # Verificar que estamos en el directorio correcto
    if not os.path.exists("app.py"):
        print("❌ Error: No se encontró app.py en el directorio actual")
        print("   Asegúrate de estar en el directorio raíz del proyecto")
        return

    print("📋 Configuración local:")
    print(f"   - Puerto: {os.environ.get('PORT', 5000)}")
    print(f"   - Modo: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"   - Debug: {os.environ.get('DEBUG', 'True')}")
    print(
        f"   - PostgreSQL: {'Deshabilitado' if not os.environ.get('DATABASE_URL') else 'Configurado'}"
    )

    print("\n🌐 La aplicación estará disponible en:")
    print("   - http://localhost:5000")
    print("   - http://127.0.0.1:5000")

    print("\n📝 Notas importantes:")
    print("   - PostgreSQL está en modo fallback (datos simulados)")
    print("   - Los cambios se reflejan automáticamente")
    print("   - Presiona Ctrl+C para detener")

    print("\n🚀 Iniciando servidor...")
    print("-" * 50)

    # Importar y ejecutar la aplicación
    try:
        from app import app

        app.run(
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000)),
            debug=True,
            use_reloader=True,
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error iniciando la aplicación: {e}")
        print("   Verifica que todas las dependencias estén instaladas")


if __name__ == "__main__":
    run_local()
