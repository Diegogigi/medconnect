#!/usr/bin/env python3
"""
Bot de prueba simplificado para diagnosticar problemas de respuesta
"""

import os
import sys
import logging
import requests
import time
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleBotTest:
    def __init__(self):
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.last_update_id = 0
        
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
            sys.exit(1)
        
        logger.info(f"✅ Bot inicializado con token: {self.token[:10]}...")
    
    def send_message(self, chat_id, text):
        """Envía un mensaje"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                logger.info(f"✅ Mensaje enviado a {chat_id}")
                return True
            else:
                logger.error(f"❌ Error enviando mensaje: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error en send_message: {e}")
            return False
    
    def get_updates(self):
        """Obtiene actualizaciones del bot"""
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {
            'offset': self.last_update_id + 1,
            'timeout': 1
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    return data['result']
                else:
                    logger.error(f"❌ Error en API: {data}")
                    return []
            else:
                logger.error(f"❌ Error HTTP: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"❌ Error obteniendo updates: {e}")
            return []
    
    def process_message(self, message):
        """Procesa un mensaje recibido"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '')
            user = message.get('from', {})
            
            logger.info(f"📨 Mensaje recibido de {user.get('first_name', 'Unknown')}: {text}")
            
            # Respuestas simples
            if text.lower() in ['/start', 'hola', 'hello']:
                response = f"¡Hola {user.get('first_name', 'Usuario')}! 👋\n\n✅ Bot funcionando correctamente\n🤖 Versión de prueba simplificada"
                self.send_message(chat_id, response)
            elif text.lower() == '/test':
                response = "🔧 Test exitoso! El bot está respondiendo correctamente."
                self.send_message(chat_id, response)
            else:
                response = f"📨 Recibí tu mensaje: \"{text}\"\n\n✅ Bot funcionando correctamente"
                self.send_message(chat_id, response)
                
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
    
    def test_bot_info(self):
        """Prueba información del bot"""
        url = f"https://api.telegram.org/bot{self.token}/getMe"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info['ok']:
                    info = bot_info['result']
                    logger.info(f"✅ Bot conectado:")
                    logger.info(f"   📝 Nombre: {info['first_name']}")
                    logger.info(f"   📝 Username: @{info['username']}")
                    logger.info(f"   📝 ID: {info['id']}")
                    return True
                else:
                    logger.error(f"❌ Error del bot: {bot_info}")
                    return False
            else:
                logger.error(f"❌ Error HTTP: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error consultando bot info: {e}")
            return False
    
    def clear_webhook(self):
        """Limpia el webhook para usar polling"""
        url = f"https://api.telegram.org/bot{self.token}/deleteWebhook"
        
        try:
            response = requests.post(url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Webhook eliminado, usando polling")
                return True
            else:
                logger.error(f"❌ Error eliminando webhook: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error en clear_webhook: {e}")
            return False
    
    def run(self):
        """Ejecuta el bot en modo polling"""
        logger.info("🚀 === INICIANDO BOT DE PRUEBA ===")
        
        # Verificar conectividad
        if not self.test_bot_info():
            logger.error("❌ No se pudo conectar al bot")
            return
        
        # Limpiar webhook
        self.clear_webhook()
        
        logger.info("🔄 Iniciando polling...")
        logger.info("💬 Envía un mensaje al bot para probar")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    
                    if 'message' in update:
                        self.process_message(update['message'])
                
                time.sleep(1)  # Pausa corta entre consultas
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot detenido por usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en loop principal: {e}")
                time.sleep(5)

def main():
    """Función principal"""
    bot = SimpleBotTest()
    bot.run()

if __name__ == "__main__":
    main() 