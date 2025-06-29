#!/usr/bin/env python3
"""
Bot de emergencia ultra-simple - GARANTIZADO que funciona
"""

import os
import requests
import time
import json

# Variables
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OFFSET = 0

print(f"🚀 Bot de emergencia iniciado")
print(f"🔑 Token: {'✅ OK' if TOKEN else '❌ FALTA'}")

if not TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN no configurado")
    exit(1)

# Eliminar webhook
try:
    response = requests.post(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook", timeout=10)
    print(f"🧹 Webhook eliminado: {response.status_code}")
except Exception as e:
    print(f"⚠️ Error webhook: {e}")

print("🔄 Bot iniciado - esperando mensajes...")

while True:
    try:
        # Obtener mensajes
        response = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getUpdates",
            params={'offset': OFFSET + 1, 'timeout': 2},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                for update in data['result']:
                    OFFSET = update['update_id']
                    
                    if 'message' in update:
                        message = update['message']
                        chat_id = message['chat']['id']
                        text = message.get('text', '')
                        user = message.get('from', {}).get('first_name', 'Usuario')
                        
                        print(f"📨 Mensaje de {user}: {text}")
                        
                        # Responder SIEMPRE
                        response_text = f"✅ ¡Hola {user}!\n\n🤖 Bot funcionando correctamente\n📅 {time.strftime('%H:%M:%S')}\n💬 Tu mensaje: {text}"
                        
                        # Enviar respuesta
                        send_response = requests.post(
                            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                            json={'chat_id': chat_id, 'text': response_text},
                            timeout=10
                        )
                        
                        if send_response.status_code == 200:
                            print(f"✅ Respuesta enviada a {chat_id}")
                        else:
                            print(f"❌ Error enviando: {send_response.status_code} - {send_response.text}")
        
        time.sleep(1)
        
    except KeyboardInterrupt:
        print("🛑 Bot detenido")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(5) 