#!/usr/bin/env python3
"""
Script para probar la nueva API key de OpenRouter
"""

import requests
import json


def test_api_key(api_key):
    """Probar si la API key funciona"""
    print(f"🔍 Probando API key: {api_key[:10]}...{api_key[-10:]}")
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
            print(
                f"   Respuesta: {response.json()['choices'][0]['message']['content']}"
            )
            return True
        else:
            print(f"❌ API key inválida: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"❌ Error probando API key: {e}")
        return False


if __name__ == "__main__":
    # Nueva API key proporcionada
    new_api_key = (
        "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"
    )

    print("🚀 Probando nueva API key de OpenRouter")
    print("=" * 50)

    if test_api_key(new_api_key):
        print("\n✅ La nueva API key funciona correctamente")
        print("   Procediendo a actualizar archivos...")
    else:
        print("\n❌ La API key no funciona")
        print("   Verifica que sea correcta")
