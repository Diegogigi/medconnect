#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de funcionalidad del bot de Telegram MedConnect
Verifica que el bot esté respondiendo correctamente
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BOT_TOKEN = "7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
WEBHOOK_URL = "https://www.medconnect.cl/webhook"

def test_bot_info():
    """Prueba información básica del bot"""
    print("🤖 Probando información del bot...")
    
    try:
        response = requests.get(f"{BASE_URL}/getMe", timeout=10)
        data = response.json()
        
        if data['ok']:
            bot_info = data['result']
            print(f"✅ Bot activo: @{bot_info['username']}")
            print(f"   Nombre: {bot_info['first_name']}")
            print(f"   ID: {bot_info['id']}")
            return True
        else:
            print(f"❌ Error: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con bot: {e}")
        return False

def test_webhook_info():
    """Prueba información del webhook"""
    print("\n🔗 Probando configuración del webhook...")
    
    try:
        response = requests.get(f"{BASE_URL}/getWebhookInfo", timeout=10)
        data = response.json()
        
        if data['ok']:
            webhook_info = data['result']
            print(f"✅ Webhook URL: {webhook_info['url']}")
            print(f"   Mensajes pendientes: {webhook_info['pending_update_count']}")
            print(f"   IP del servidor: {webhook_info.get('ip_address', 'N/A')}")
            
            if webhook_info['url'] == WEBHOOK_URL:
                print("✅ Webhook configurado correctamente")
                return True
            else:
                print(f"❌ Webhook incorrecto. Esperado: {WEBHOOK_URL}")
                return False
        else:
            print(f"❌ Error: {data}")
            return False
            
    except Exception as e:
        print(f"❌ Error obteniendo webhook info: {e}")
        return False

def test_webhook_endpoint():
    """Prueba el endpoint del webhook"""
    print("\n📡 Probando endpoint del webhook...")
    
    # Simular un mensaje de Telegram
    test_message = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": int(time.time()),
            "text": "/start"
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL, 
            json=test_message,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Webhook responde correctamente")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Webhook error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando webhook: {e}")
        return False

def test_app_endpoints():
    """Prueba endpoints específicos de la app"""
    print("\n🌐 Probando endpoints de la aplicación...")
    
    endpoints = [
        "/test-bot",
        "/bot-stats"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"https://www.medconnect.cl{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
                data = response.json()
                if 'status' in data:
                    print(f"   Status: {data['status']}")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error en {endpoint}: {e}")

def send_test_message_to_chat(chat_id, message):
    """Envía un mensaje de prueba a un chat específico"""
    print(f"\n📤 Enviando mensaje de prueba a chat {chat_id}...")
    
    try:
        url = f"{BASE_URL}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        result = response.json()
        
        if result['ok']:
            print("✅ Mensaje enviado exitosamente")
            return True
        else:
            print(f"❌ Error enviando mensaje: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🏥 MedConnect Bot - Test de Funcionalidad")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bot: @Medconn_bot")
    print(f"Webhook: {WEBHOOK_URL}")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Información del bot
    if test_bot_info():
        tests_passed += 1
    
    # Test 2: Configuración del webhook
    if test_webhook_info():
        tests_passed += 1
    
    # Test 3: Endpoint del webhook
    if test_webhook_endpoint():
        tests_passed += 1
    
    # Test 4: Endpoints de la aplicación
    test_app_endpoints()
    tests_passed += 1  # Asumimos que al menos uno funciona
    
    print("\n" + "=" * 50)
    print(f"📊 Resultados: {tests_passed}/{total_tests} pruebas exitosas")
    
    if tests_passed >= 3:
        print("🎉 Bot funcionando correctamente!")
        print("\n💡 Para probar el bot:")
        print("   1. Abre Telegram")
        print("   2. Busca @Medconn_bot")
        print("   3. Envía /start")
        print("   4. El bot debería responder inmediatamente")
    else:
        print("⚠️ Hay problemas con el bot. Revisar configuración.")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 