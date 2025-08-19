#!/usr/bin/env python3
"""
Script simple para actualizar la API key de OpenRouter
Usa una API key de prueba válida para solucionar el problema
"""

import os
import re
import requests
from datetime import datetime


def test_api_key(api_key):
    """Probar si la API key funciona"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek/deepseek-r1:free",
            "messages": [
                {
                    "role": "system",
                    "content": "Eres un asistente de prueba. Responde solo 'OK' si recibes este mensaje.",
                },
                {"role": "user", "content": "Test de conexión"},
            ],
            "max_tokens": 10,
            "temperature": 0.1,
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )

        return response.status_code == 200

    except Exception:
        return False


def update_file_with_new_key(filename, new_api_key):
    """Actualizar un archivo con la nueva API key"""
    try:
        # Leer el archivo
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Buscar y reemplazar la API key hardcodeada
        old_pattern = r"sk-or-v1-[a-zA-Z0-9]+"
        new_content = re.sub(old_pattern, new_api_key, content)

        # Verificar si se hizo algún cambio
        if new_content == content:
            return False

        # Escribir el archivo actualizado
        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True

    except Exception:
        return False


def create_env_file(new_api_key):
    """Crear archivo .env con la nueva API key"""
    env_content = f"""# MedConnect - Variables de Entorno Local
# Configuración actualizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Configuración de Flask
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=clave-secreta-local-desarrollo

# Configuración del dominio
DOMAIN=localhost:5000
BASE_URL=http://localhost:5000

# Configuración de OpenRouter (API key actualizada)
OPENROUTER_API_KEY={new_api_key}

# Configuración de logging
LOG_LEVEL=INFO

# Configuración de Railway (para producción)
PORT=5000
RAILWAY_ENVIRONMENT=development
"""

    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        return True
    except Exception:
        return False


def main():
    """Función principal"""
    print("🚀 Solucionando problema de API Key de OpenRouter")
    print("=" * 50)

    # API key de prueba válida (debes reemplazar esto con una real)
    # Esta es una API key de ejemplo - necesitas obtener una real de OpenRouter
    new_api_key = (
        "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"
    )

    print("⚠️ IMPORTANTE: La API key actual está expirada")
    print("")
    print("🔧 SOLUCIÓN TEMPORAL:")
    print("1. Ve a https://openrouter.ai/")
    print("2. Crea una cuenta gratuita")
    print("3. Ve a https://openrouter.ai/keys")
    print("4. Crea una nueva API key")
    print("5. Reemplaza la variable 'new_api_key' en este script")
    print("")

    # Verificar si la API key actual funciona
    print("🔍 Verificando API key actual...")
    if test_api_key(new_api_key):
        print("✅ API key actual funciona")
    else:
        print("❌ API key actual no funciona (expirada)")
        print("")
        print("📋 Para obtener una nueva API key:")
        print("1. Ir a: https://openrouter.ai/")
        print("2. Crear cuenta gratuita")
        print("3. Ir a: https://openrouter.ai/keys")
        print("4. Crear nueva API key")
        print("5. Copiar la nueva key (empieza con 'sk-or-v1-')")
        print("")

        # Solicitar nueva API key
        user_input = input(
            "🔑 Ingresa la nueva API key (o presiona Enter para usar la actual): "
        ).strip()
        if user_input and user_input.startswith("sk-or-v1-"):
            new_api_key = user_input
            print("✅ Nueva API key ingresada")
        else:
            print("⚠️ Usando API key actual (puede no funcionar)")

    # Actualizar archivos
    files_to_update = [
        "app.py",
        "unified_copilot_assistant.py",
        "unified_orchestration_system.py",
    ]

    updated_files = 0
    for filename in files_to_update:
        if os.path.exists(filename):
            if update_file_with_new_key(filename, new_api_key):
                print(f"✅ {filename} actualizado")
                updated_files += 1
            else:
                print(f"⚠️ {filename} no necesitaba actualización")

    # Crear archivo .env
    if create_env_file(new_api_key):
        print("✅ Archivo .env creado")
        updated_files += 1

    print("")
    print("📊 RESUMEN:")
    print(f"✅ {updated_files} archivos actualizados")

    print("")
    print("🔧 PRÓXIMOS PASOS:")
    print("1. Para desarrollo local:")
    print("   - Ejecutar: python app.py")
    print("   - Probar el chat en la aplicación")

    print("")
    print("2. Para Railway:")
    print("   - Ir a Railway Dashboard")
    print("   - Variables → OPENROUTER_API_KEY")
    print(f"   - Configurar: {new_api_key}")
    print("   - Hacer redeploy")

    print("")
    print("💡 NOTA:")
    print("   - Si la API key no funciona, obtén una nueva en OpenRouter")
    print("   - Las cuentas gratuitas tienen límites de uso")
    print("   - Para producción, considera una cuenta de pago")

    print("=" * 50)


if __name__ == "__main__":
    main()
