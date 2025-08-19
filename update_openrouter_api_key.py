#!/usr/bin/env python3
"""
Script para actualizar la API key de OpenRouter y solucionar problemas de conexión
"""

import os
import requests
import json
import re
from datetime import datetime


def get_new_openrouter_api_key():
    """Obtener una nueva API key de OpenRouter"""
    print("🔑 OBTENIENDO NUEVA API KEY DE OPENROUTER")
    print("=" * 50)

    print("📋 Pasos para obtener una nueva API key:")
    print("")
    print("1️⃣ Ir a OpenRouter:")
    print("   https://openrouter.ai/")
    print("")
    print("2️⃣ Hacer click en 'Sign Up' o 'Login'")
    print("")
    print("3️⃣ Una vez logueado, ir a:")
    print("   https://openrouter.ai/keys")
    print("")
    print("4️⃣ Hacer click en 'Create Key'")
    print("")
    print("5️⃣ Copiar la nueva API key (empieza con 'sk-or-v1-')")
    print("")

    # Solicitar la nueva API key al usuario
    new_api_key = input("🔑 Ingresa la nueva API key de OpenRouter: ").strip()

    if not new_api_key:
        print("❌ No se ingresó una API key")
        return None

    if not new_api_key.startswith("sk-or-v1-"):
        print(
            "❌ La API key no tiene el formato correcto (debe empezar con 'sk-or-v1-')"
        )
        return None

    return new_api_key


def test_api_key(api_key):
    """Probar si la API key funciona"""
    print(f"\n🔍 Probando API key: {api_key[:10]}...{api_key[-10:]}")
    print("=" * 50)

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

        if response.status_code == 200:
            print("✅ API key válida y funcionando")
            return True
        else:
            print(f"❌ API key inválida: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error probando API key: {e}")
        return False


def update_app_py_with_new_key(new_api_key):
    """Actualizar app.py con la nueva API key"""
    print(f"\n📝 Actualizando app.py con nueva API key...")
    print("=" * 50)

    try:
        # Leer el archivo app.py
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Buscar y reemplazar la API key hardcodeada
        old_pattern = r"sk-or-v1-[a-zA-Z0-9]+"
        new_content = re.sub(old_pattern, new_api_key, content)

        # Verificar si se hizo algún cambio
        if new_content == content:
            print("⚠️ No se encontró API key hardcodeada para reemplazar")
            return False

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ app.py actualizado exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error actualizando app.py: {e}")
        return False


def update_unified_copilot_assistant(new_api_key):
    """Actualizar unified_copilot_assistant.py con la nueva API key"""
    print(f"\n📝 Actualizando unified_copilot_assistant.py...")
    print("=" * 50)

    try:
        # Leer el archivo
        with open("unified_copilot_assistant.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Buscar y reemplazar la API key hardcodeada
        old_pattern = r"sk-or-v1-[a-zA-Z0-9]+"
        new_content = re.sub(old_pattern, new_api_key, content)

        # Verificar si se hizo algún cambio
        if new_content == content:
            print("⚠️ No se encontró API key hardcodeada para reemplazar")
            return False

        # Escribir el archivo actualizado
        with open("unified_copilot_assistant.py", "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ unified_copilot_assistant.py actualizado exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error actualizando unified_copilot_assistant.py: {e}")
        return False


def update_unified_orchestration_system(new_api_key):
    """Actualizar unified_orchestration_system.py con la nueva API key"""
    print(f"\n📝 Actualizando unified_orchestration_system.py...")
    print("=" * 50)

    try:
        # Leer el archivo
        with open("unified_orchestration_system.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Buscar y reemplazar la API key hardcodeada
        old_pattern = r"sk-or-v1-[a-zA-Z0-9]+"
        new_content = re.sub(old_pattern, new_api_key, content)

        # Verificar si se hizo algún cambio
        if new_content == content:
            print("⚠️ No se encontró API key hardcodeada para reemplazar")
            return False

        # Escribir el archivo actualizado
        with open("unified_orchestration_system.py", "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ unified_orchestration_system.py actualizado exitosamente")
        return True

    except Exception as e:
        print(f"❌ Error actualizando unified_orchestration_system.py: {e}")
        return False


def create_env_file_with_new_key(new_api_key):
    """Crear archivo .env con la nueva API key"""
    print(f"\n📝 Creando archivo .env con nueva API key...")
    print("=" * 50)

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
        print("✅ Archivo .env creado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando .env: {e}")
        return False


def generate_railway_instructions(new_api_key):
    """Generar instrucciones para configurar Railway"""
    print(f"\n🚂 INSTRUCCIONES PARA CONFIGURAR RAILWAY")
    print("=" * 50)

    print("1️⃣ Ir a Railway Dashboard:")
    print("   https://railway.app/dashboard")

    print("\n2️⃣ Seleccionar tu proyecto MedConnect")

    print("\n3️⃣ Ir a la pestaña 'Variables'")

    print("\n4️⃣ Agregar o actualizar la variable:")
    print(f"   OPENROUTER_API_KEY = {new_api_key}")

    print("\n5️⃣ Otras variables recomendadas:")
    print("   RAILWAY_ENVIRONMENT = production")
    print("   FLASK_ENV = production")
    print("   SECRET_KEY = tu-clave-secreta-super-segura-aqui")

    print("\n6️⃣ Hacer click en 'Deploy' para aplicar los cambios")

    print("\n7️⃣ Esperar que el deploy termine y verificar los logs")


def main():
    """Función principal"""
    print("🚀 Actualización de API Key de OpenRouter")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Obtener nueva API key
    new_api_key = get_new_openrouter_api_key()

    if not new_api_key:
        print("❌ No se pudo obtener la API key")
        return

    # 2. Probar la nueva API key
    if not test_api_key(new_api_key):
        print("❌ La API key no funciona. Verifica que sea correcta.")
        return

    # 3. Actualizar archivos
    files_updated = 0

    if update_app_py_with_new_key(new_api_key):
        files_updated += 1

    if update_unified_copilot_assistant(new_api_key):
        files_updated += 1

    if update_unified_orchestration_system(new_api_key):
        files_updated += 1

    # 4. Crear archivo .env
    if create_env_file_with_new_key(new_api_key):
        files_updated += 1

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE LA ACTUALIZACIÓN")
    print("=" * 60)

    print(f"✅ API key probada y funcionando")
    print(f"✅ {files_updated} archivos actualizados")

    print("\n🔧 PRÓXIMOS PASOS:")
    print("1. Para desarrollo local:")
    print("   - El archivo .env ya está configurado")
    print("   - Ejecutar: python app.py")

    print("\n2. Para Railway:")
    generate_railway_instructions(new_api_key)

    print("\n3. Verificar funcionamiento:")
    print("   - Probar el chat en la aplicación")
    print("   - Verificar que no aparezcan errores de conexión")

    print("\n💡 NOTA IMPORTANTE:")
    print("   - La API key anterior estaba expirada o inválida")
    print("   - La nueva API key debería resolver el problema")
    print("   - Recuerda configurar la variable en Railway para producción")

    print("=" * 60)


if __name__ == "__main__":
    main()
