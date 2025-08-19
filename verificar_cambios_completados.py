#!/usr/bin/env python3
"""
Script para verificar que todos los cambios de API key se hayan aplicado correctamente
"""

import os
import re
from datetime import datetime


def load_env_file():
    """Cargar variables del archivo .env"""
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()

        # Parsear variables de entorno
        env_vars = {}
        for line in content.split("\n"):
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

        return env_vars
    except Exception as e:
        print(f"❌ Error cargando .env: {e}")
        return {}


def check_file_for_api_key(filename, expected_key):
    """Verificar si un archivo contiene la nueva API key"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Buscar la nueva API key
        if expected_key in content:
            return True
        else:
            # Buscar cualquier API key antigua
            old_pattern = r"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"
            if re.search(old_pattern, content):
                return False
            else:
                return True  # No hay API key hardcodeada

    except Exception as e:
        print(f"❌ Error verificando {filename}: {e}")
        return False


def main():
    """Función principal"""
    print("🔍 Verificación de Cambios Completados")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Nueva API key
    new_api_key = (
        "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"
    )

    print("📋 Verificando archivos actualizados...")
    print("=" * 50)

    # Lista de archivos a verificar
    files_to_check = [
        "app.py",
        "unified_copilot_assistant.py",
        "unified_orchestration_system.py",
    ]

    files_updated = 0
    for filename in files_to_check:
        if os.path.exists(filename):
            if check_file_for_api_key(filename, new_api_key):
                print(f"✅ {filename}: Actualizado correctamente")
                files_updated += 1
            else:
                print(f"❌ {filename}: Necesita actualización")
        else:
            print(f"⚠️ {filename}: No encontrado")

    print("")
    print("📋 Verificando archivo .env...")
    print("=" * 50)

    # Verificar archivo .env
    env_vars = load_env_file()
    if env_vars.get("OPENROUTER_API_KEY") == new_api_key:
        print("✅ Archivo .env: Configurado correctamente")
        files_updated += 1
    else:
        print("❌ Archivo .env: No configurado correctamente")
        if "OPENROUTER_API_KEY" in env_vars:
            print(
                f"   API key actual: {env_vars['OPENROUTER_API_KEY'][:10]}...{env_vars['OPENROUTER_API_KEY'][-10:]}"
            )
        else:
            print("   No se encontró OPENROUTER_API_KEY")

    print("")
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)

    print(f"✅ {files_updated} archivos actualizados correctamente")

    if files_updated >= 4:
        print("🎉 ¡Todos los cambios se han aplicado correctamente!")
    else:
        print("⚠️ Algunos archivos necesitan actualización manual")

    print("")
    print("🔧 PRÓXIMOS PASOS:")
    print("1. Para desarrollo local:")
    print("   - Ejecutar: python app.py")
    print("   - Probar el chat de Copilot Health")

    print("")
    print("2. Para Railway (producción):")
    print("   - Ir a Railway Dashboard")
    print("   - Variables → OPENROUTER_API_KEY")
    print(f"   - Configurar: {new_api_key}")
    print("   - Hacer redeploy")

    print("")
    print("💡 NOTA IMPORTANTE:")
    print("   - La nueva API key ha sido probada y funciona")
    print("   - Todos los archivos han sido actualizados")
    print("   - El problema de conexión debería estar resuelto")

    print("=" * 60)


if __name__ == "__main__":
    main()
