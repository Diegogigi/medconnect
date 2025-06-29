#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Telegram para MedConnect - Versión Simplificada y Corregida
"""

import os
import json
import logging
import requests
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID')

# Verificar variables críticas
if not TELEGRAM_BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
    exit(1)

if not GOOGLE_SHEETS_ID:
    logger.error("❌ GOOGLE_SHEETS_ID no configurado")
    exit(1)

logger.info("✅ Variables de entorno cargadas")

class MedConnectBotFixed:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.sheets_id = GOOGLE_SHEETS_ID
        self.last_update_id = 0
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        logger.info("🏥 MedConnect Bot inicializado")
        
        # Verificar conectividad del bot
        if not self.test_bot_connection():
            logger.error("❌ No se pudo conectar al bot")
            exit(1)
    
    def test_bot_connection(self):
        """Verifica la conectividad del bot"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info['ok']:
                    info = bot_info['result']
                    logger.info(f"✅ Bot conectado: @{info['username']} ({info['first_name']})")
                    return True
            
            logger.error(f"❌ Error de conectividad: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error conectando al bot: {e}")
            return False
    
    def clear_webhook(self):
        """Elimina webhook para usar polling"""
        try:
            response = requests.post(f"{self.base_url}/deleteWebhook", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Webhook eliminado, usando polling")
                return True
            else:
                logger.error(f"❌ Error eliminando webhook: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error en clear_webhook: {e}")
            return False
    
    def send_message(self, chat_id, text, parse_mode='HTML'):
        """Envía un mensaje al chat"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result['ok']:
                    logger.info(f"✅ Mensaje enviado a {chat_id}")
                    return True
                else:
                    logger.error(f"❌ Error en respuesta: {result}")
                    return False
            else:
                logger.error(f"❌ Error HTTP: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return False
    
    def get_updates(self):
        """Obtiene actualizaciones pendientes"""
        url = f"{self.base_url}/getUpdates"
        params = {
            'offset': self.last_update_id + 1,
            'timeout': 2
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    return data['result']
                else:
                    logger.error(f"❌ Error en getUpdates: {data}")
                    return []
            else:
                logger.error(f"❌ Error HTTP getUpdates: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo updates: {e}")
            return []
    
    def process_message(self, message):
        """Procesa un mensaje recibido"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            user = message.get('from', {})
            user_name = user.get('first_name', 'Usuario')
            
            logger.info(f"📨 Mensaje de {user_name} ({chat_id}): {text}")
            
            # Respuestas principales
            if text.lower() == '/start':
                response = f"""¡Hola {user_name}! 👋

🏥 <b>Bienvenido a MedConnect</b>

Soy tu asistente médico personal. Puedo ayudarte con:

📋 <b>Registrar consultas médicas</b>
💊 <b>Gestionar medicamentos</b>
🩺 <b>Registrar exámenes</b>
📊 <b>Ver tu historial médico</b>

<b>Comandos disponibles:</b>
/start - Mostrar este menú
/ayuda - Obtener ayuda
/estado - Ver estado del bot

💬 También puedes escribirme en lenguaje natural!"""
                
                self.send_message(chat_id, response)
                
            elif text.lower() in ['/ayuda', '/help', 'ayuda']:
                response = """🤖 <b>¿Cómo puedo ayudarte?</b>

<b>Puedes hacer esto:</b>
• Escribir "consulta" para registrar una consulta médica
• Escribir "medicamento" para agregar medicamentos
• Escribir "examen" para registrar exámenes
• Escribir "historial" para ver tu información

<b>Ejemplos:</b>
• "Tengo una consulta con el cardiólogo mañana"
• "Necesito registrar un medicamento"
• "Me hicieron un examen de sangre"

¡Escribe de forma natural y yo te entenderé! 😊"""
                
                self.send_message(chat_id, response)
                
            elif text.lower() == '/estado':
                response = f"""🔧 <b>Estado del Bot</b>

✅ Bot funcionando correctamente
📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
🔗 Conectado a Google Sheets: {'✅' if self.sheets_id else '❌'}
🤖 Modo: Polling activo

<b>ID del chat:</b> {chat_id}
<b>Tu nombre:</b> {user_name}"""
                
                self.send_message(chat_id, response)
                
            elif any(word in text.lower() for word in ['hola', 'hello', 'hi', 'buenas']):
                response = f"¡Hola {user_name}! 👋\n\n¿En qué puedo ayudarte hoy? Puedes usar /start para ver el menú principal."
                self.send_message(chat_id, response)
                
            elif any(word in text.lower() for word in ['consulta', 'medico', 'doctor', 'cita']):
                response = """📋 <b>Registrar Consulta Médica</b>

Para registrar una consulta, necesito estos datos:
• Fecha y hora
• Especialidad o tipo de consulta
• Nombre del médico (opcional)
• Motivo de la consulta

¿Puedes proporcionarme esta información?"""
                
                self.send_message(chat_id, response)
                
            elif any(word in text.lower() for word in ['medicamento', 'medicina', 'pastilla', 'farmaco']):
                response = """💊 <b>Registrar Medicamento</b>

Para registrar un medicamento, necesito:
• Nombre del medicamento
• Dosis (mg, ml, etc.)
• Frecuencia (cada cuánto tiempo)
• Duración del tratamiento

¿Cuál es el medicamento que quieres registrar?"""
                
                self.send_message(chat_id, response)
                
            elif any(word in text.lower() for word in ['examen', 'analisis', 'laboratorio', 'estudio']):
                response = """🔬 <b>Registrar Examen Médico</b>

Para registrar un examen, necesito:
• Tipo de examen
• Fecha realizada
• Resultados (si los tienes)
• Médico que lo solicitó

¿Qué tipo de examen registramos?"""
                
                self.send_message(chat_id, response)
                
            elif any(word in text.lower() for word in ['historial', 'ver', 'mostrar', 'consultar']):
                response = """📊 <b>Tu Historial Médico</b>

Aquí tienes acceso a:
• Consultas registradas
• Medicamentos actuales
• Exámenes realizados
• Información personal

🌐 Para ver tu historial completo, visita:
https://medconnect.cl

¿Qué información específica necesitas?"""
                
                self.send_message(chat_id, response)
                
            elif any(word in text.lower() for word in ['gracias', 'thank', 'perfecto', 'excelente']):
                response = f"¡De nada, {user_name}! 😊\n\nEstoy aquí para ayudarte con tu salud. ¿Necesitas algo más?"
                self.send_message(chat_id, response)
                
            else:
                # Respuesta por defecto
                response = f"""Hola {user_name}! 👋

Recibí tu mensaje: "{text}"

Para ayudarte mejor, puedes:
• Usar /start para ver el menú principal
• Usar /ayuda para obtener ayuda
• Escribir palabras como "consulta", "medicamento" o "examen"

¿En qué puedo ayudarte? 🤖"""
                
                self.send_message(chat_id, response)
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            try:
                error_msg = "❌ Hubo un error procesando tu mensaje. Por favor, intenta de nuevo."
                self.send_message(chat_id, error_msg)
            except:
                pass
    
    def run(self):
        """Ejecuta el bot"""
        logger.info("🚀 === INICIANDO MEDCONNECT BOT ===")
        
        # Limpiar webhook
        self.clear_webhook()
        
        logger.info("🔄 Bot iniciado en modo polling")
        logger.info("💬 Listo para recibir mensajes...")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    
                    if 'message' in update:
                        self.process_message(update['message'])
                
                # Pausa corta entre consultas
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot detenido por usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en loop principal: {e}")
                time.sleep(5)  # Pausa más larga en caso de error

def main():
    """Función principal"""
    try:
        bot = MedConnectBotFixed()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        exit(1)

if __name__ == "__main__":
    main() 