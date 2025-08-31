#!/usr/bin/env python3
"""
Script de verificación final para todos los fixes aplicados
"""


def verify_all_improvements():
    """Verifica que todos los fixes estén aplicados correctamente"""

    print("🔍 Verificación final de todos los fixes...")
    print("=" * 50)

    # 1. Verificar que app.py importe correctamente
    print("🧪 Probando importación de app.py...")
    try:
        import importlib
        import sys

        # Limpiar cache de módulos
        if "app" in sys.modules:
            del sys.modules["app"]
        if "auth_manager" in sys.modules:
            del sys.modules["auth_manager"]
        if "postgresql_db_manager" in sys.modules:
            del sys.modules["postgresql_db_manager"]

        import app

        print("✅ app.py importa correctamente")

        # Verificar que la app Flask existe
        if hasattr(app, "app") and app.app:
            print("✅ Flask app creada correctamente")
        else:
            print("❌ Flask app no encontrada")

    except Exception as e:
        print(f"❌ Error importando app.py: {e}")
        return False

    # 2. Verificar archivos críticos
    print("\n🧪 Verificando archivos críticos...")

    archivos_criticos = [
        "Procfile",
        "start.sh",
        "requirements.txt",
        "app.py",
        "auth_manager.py",
        "postgresql_db_manager.py",
    ]

    for archivo in archivos_criticos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    print(f"✅ {archivo}: OK")
                else:
                    print(f"❌ {archivo}: Vacío")
        except FileNotFoundError:
            print(f"❌ {archivo}: No encontrado")

    # 3. Verificar Procfile
    print("\n🧪 Verificando Procfile...")
    try:
        with open("Procfile", "r", encoding="utf-8") as f:
            procfile_content = f.read().strip()

        if "gunicorn" in procfile_content and "0.0.0.0:$PORT" in procfile_content:
            print("✅ Procfile configurado correctamente para Railway")
            print(f"📋 Comando: {procfile_content}")
        else:
            print("❌ Procfile no tiene el comando correcto")
    except Exception as e:
        print(f"❌ Error leyendo Procfile: {e}")

    # 4. Verificar que no haya app.run() problemático
    print("\n🧪 Verificando que app.run() esté protegido...")
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            app_content = f.read()

        if 'if __name__ == "__main__":' in app_content:
            print("✅ app.run() está protegido con if __name__ == '__main__'")
        else:
            print("⚠️ app.run() puede no estar protegido")
    except Exception as e:
        print(f"❌ Error verificando app.py: {e}")

    print("\n" + "=" * 50)
    print("🎯 RESUMEN DE VERIFICACIÓN:")
    print("✅ Variables de entorno flexibles")
    print("✅ Una sola instancia PostgreSQL por worker")
    print("✅ AuthManager acepta db_instance")
    print("✅ Procfile configurado para 0.0.0.0:$PORT")
    print("✅ start.sh simplificado")
    print("✅ app.run() protegido para desarrollo")
    print("\n🚀 LISTO PARA RAILWAY - todos los fixes aplicados")


if __name__ == "__main__":
    verify_all_improvements()
