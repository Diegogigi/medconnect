#!/usr/bin/env python3
"""
Bot de diagnóstico ultra-simplificado para identificar el problema exacto
"""

import os
import sys
import logging
import requests
import time
import json

# Configurar logging muy detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BotDebug:
    def __init__(self):
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.last_update_id = 0
        
        # Log inicial
        logger.info("🔍 === INICIANDO DIAGNÓSTICO DEL BOT ===")
        logger.info(f"🔑 Token disponible: {'SÍ' if self.token else 'NO'}")
        
        if self.token:
            logger.info(f"🔑 Token length: {len(self.token)} caracteres")
            logger.info(f"🔑 Token preview: {self.token[:20]}...")
        else:
            logger.error("❌ TELEGRAM_BOT_TOKEN no encontrado")
            sys.exit(1)
    
    def test_api_connection(self):
        """Prueba la conexión básica a la API"""
        logger.info("🌐 === PROBANDO CONEXIÓN A API DE TELEGRAM ===")
        
        url = f"https://api.telegram.org/bot{self.token}/getMe"
        
        try:
            logger.info(f"📡 Haciendo request a: {url}")
            response = requests.get(url, timeout=10)
            
            logger.info(f"📈 Status code: {response.status_code}")
            logger.info(f"📄 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Response JSON: {json.dumps(data, indent=2)}")
                
                if data.get('ok'):
                    bot_info = data['result']
                    logger.info(f"✅ Bot conectado exitosamente:")
                    logger.info(f"   📝 ID: {bot_info['id']}")
                    logger.info(f"   📝 Nombre: {bot_info['first_name']}")
                    logger.info(f"   📝 Username: @{bot_info['username']}")
                    return True
                else:
                    logger.error(f"❌ API response not ok: {data}")
                    return False
            else:
                logger.error(f"❌ HTTP Error: {response.status_code}")
                logger.error(f"❌ Response text: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception en API test: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            return False
    
    def test_send_message(self, chat_id, text):
        """Prueba enviar un mensaje con logging detallado"""
        logger.info(f"📤 === PROBANDO ENVÍO DE MENSAJE ===")
        logger.info(f"📤 Chat ID: {chat_id}")
        logger.info(f"📤 Texto: {text}")
        
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text
        }
        
        logger.info(f"📡 URL: {url}")
        logger.info(f"📦 Data: {json.dumps(data, indent=2)}")
        
        try:
            logger.info("🚀 Enviando request...")
            response = requests.post(url, json=data, timeout=15)
            
            logger.info(f"📈 Status code: {response.status_code}")
            logger.info(f"📄 Response headers: {dict(response.headers)}")
            logger.info(f"📄 Response text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Response JSON: {json.dumps(result, indent=2)}")
                
                if result.get('ok'):
                    logger.info("✅ MENSAJE ENVIADO EXITOSAMENTE!")
                    return True
                else:
                    logger.error(f"❌ API returned ok=false: {result}")
                    return False
            else:
                logger.error(f"❌ HTTP Error: {response.status_code}")
                logger.error(f"❌ Response text: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Exception enviando mensaje: {e}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return False
    
    def get_updates(self):
        """Obtiene updates con logging detallado"""
        logger.debug("🔄 Obteniendo updates...")
        
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        params = {
            'offset': self.last_update_id + 1,
            'timeout': 2
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    updates = data['result']
                    if updates:
                        logger.info(f"📨 Recibidos {len(updates)} updates")
                    return updates
                else:
                    logger.error(f"❌ Error en getUpdates: {data}")
                    return []
            else:
                logger.error(f"❌ HTTP Error getUpdates: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo updates: {e}")
            return []
    
    def clear_webhook_debug(self):
        """Elimina webhook con logging detallado"""
        logger.info("🧹 === ELIMINANDO WEBHOOK ===")
        
        url = f"https://api.telegram.org/bot{self.token}/deleteWebhook"
        
        try:
            response = requests.post(url, timeout=10)
            logger.info(f"📈 Status code: {response.status_code}")
            logger.info(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    logger.info("✅ Webhook eliminado exitosamente")
                    return True
                else:
                    logger.error(f"❌ Error eliminando webhook: {result}")
                    return False
            else:
                logger.error(f"❌ HTTP Error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en deleteWebhook: {e}")
            return False
    
    def run_diagnostic(self):
        """Ejecuta diagnóstico completo"""
        logger.info("🏥 === INICIANDO DIAGNÓSTICO COMPLETO ===")
        
        # Test 1: Conexión API
        if not self.test_api_connection():
            logger.error("❌ FALLO: No se pudo conectar a la API")
            return False
        
        # Test 2: Eliminar webhook
        self.clear_webhook_debug()
        
        # Test 3: Obtener updates iniciales
        logger.info("📨 === OBTENIENDO UPDATES INICIALES ===")
        initial_updates = self.get_updates()
        
        if initial_updates:
            for update in initial_updates:
                self.last_update_id = update['update_id']
                logger.info(f"📨 Update {update['update_id']}: {json.dumps(update, indent=2)}")
        
        # Test 4: Loop principal con logging
        logger.info("🔄 === INICIANDO LOOP DE MENSAJES ===")
        logger.info("💬 Envía un mensaje al bot para probar...")
        
        message_count = 0
        while message_count < 10:  # Solo procesar 10 mensajes para diagnóstico
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    message_count += 1
                    
                    logger.info(f"📨 === PROCESANDO UPDATE {update['update_id']} ===")
                    logger.info(f"📨 Update completo: {json.dumps(update, indent=2)}")
                    
                    if 'message' in update:
                        message = update['message']
                        chat_id = message['chat']['id']
                        text = message.get('text', '')
                        user = message.get('from', {})
                        
                        logger.info(f"📨 Mensaje de {user.get('first_name', 'Unknown')}: {text}")
                        logger.info(f"📨 Chat ID: {chat_id}")
                        
                        # Intentar responder
                        response_text = f"🔍 DIAGNÓSTICO: Recibí tu mensaje '{text}' a las {time.strftime('%H:%M:%S')}"
                        
                        logger.info(f"📤 Intentando responder...")
                        success = self.test_send_message(chat_id, response_text)
                        
                        if success:
                            logger.info("✅ ÉXITO: Mensaje enviado correctamente!")
                        else:
                            logger.error("❌ FALLO: No se pudo enviar el mensaje")
                            
                            # Intentar respuesta más simple
                            logger.info("🔄 Intentando respuesta más simple...")
                            simple_response = "Test"
                            if self.test_send_message(chat_id, simple_response):
                                logger.info("✅ Respuesta simple funcionó")
                            else:
                                logger.error("❌ Ni siquiera la respuesta simple funciona")
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                logger.info("🛑 Diagnóstico interrumpido por usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en loop principal: {e}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
                time.sleep(5)
        
        logger.info("🏁 === DIAGNÓSTICO COMPLETADO ===")

def main():
    """Función principal"""
    bot = BotDebug()
    bot.run_diagnostic()

if __name__ == "__main__":
    main() 