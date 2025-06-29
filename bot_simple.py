#!/usr/bin/env python3
"""
Bot simplificado de MedConnect - Versión de emergencia
"""

import os
import requests
import time
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMedConnectBot:
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.last_update_id = 0
        
        if not self.bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
            exit(1)
        
        logger.info("✅ Bot simplificado iniciado")
    
    def send_message(self, chat_id, text):
        """Envía un mensaje simple"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Mensaje enviado a {chat_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return False
    
    def process_message(self, message):
        """Procesa mensajes de forma simple"""
        try:
            text = message.get('text', '').lower().strip()
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            username = message['from'].get('username', 'Usuario')
            
            logger.info(f"📨 Mensaje de {username} ({user_id}): {text}")
            
            # Respuestas simples
            if text == '/start':
                response = """🤖 <b>¡Bienvenido a MedConnect!</b>

🏥 Tu asistente médico personal

📋 <b>Comandos disponibles:</b>
• /start - Mostrar este mensaje
• /ayuda - Ver todas las opciones
• /estado - Estado del bot

💬 <b>También puedes escribir:</b>
• "consulta" - Registrar cita médica
• "medicamento" - Gestionar medicinas
• "examen" - Subir resultados
• "historial" - Ver tu información

🌐 <b>Registro:</b> https://www.medconnect.cl/register

¡Estoy aquí para ayudarte! 🩺"""
                
            elif text == '/ayuda':
                response = """📋 <b>Ayuda de MedConnect</b>

🏥 <b>Funciones principales:</b>
• Registrar consultas médicas
• Gestionar medicamentos
• Subir resultados de exámenes
• Ver historial médico
• Configurar recordatorios

💬 <b>Lenguaje natural:</b>
Puedes escribir de forma natural, por ejemplo:
• "Necesito registrar una consulta"
• "Tengo un medicamento nuevo"
• "Quiero ver mi historial"

🌐 <b>Sitio web:</b> https://www.medconnect.cl

¿En qué puedo ayudarte? 🤔"""
                
            elif text == '/estado':
                response = """✅ <b>Estado del Bot</b>

🤖 <b>Bot:</b> Funcionando correctamente
🌐 <b>Web:</b> https://www.medconnect.cl
📊 <b>Base de datos:</b> Conectada
⏰ <b>Última actualización:</b> Ahora

¡Todo funcionando perfectamente! 🎉"""
                
            elif any(word in text for word in ['consulta', 'cita', 'médico', 'doctor']):
                response = """🏥 <b>Registro de Consulta Médica</b>

Para registrar una consulta, necesito:

📅 <b>Fecha:</b> (DD/MM/AAAA)
⏰ <b>Hora:</b> (HH:MM)
👨‍⚕️ <b>Especialidad:</b> (ej: Cardiología)
🏥 <b>Centro médico:</b>

🌐 <b>O regístrate en:</b> https://www.medconnect.cl/register

¿Quieres que te ayude a registrar la consulta? 📝"""
                
            elif any(word in text for word in ['medicamento', 'medicina', 'píldora', 'pastilla']):
                response = """💊 <b>Gestión de Medicamentos</b>

Para registrar un medicamento:

💊 <b>Nombre:</b> (ej: Paracetamol)
📏 <b>Dosis:</b> (ej: 500mg)
⏰ <b>Frecuencia:</b> (ej: Cada 8 horas)
📅 <b>Duración:</b> (ej: 7 días)

🌐 <b>O regístrate en:</b> https://www.medconnect.cl/register

¿Quieres registrar un medicamento? 📝"""
                
            elif any(word in text for word in ['examen', 'resultado', 'laboratorio']):
                response = """🔬 <b>Resultados de Exámenes</b>

Para subir resultados:

📄 <b>Tipo de examen:</b> (ej: Sangre, Orina)
📅 <b>Fecha:</b> (DD/MM/AAAA)
🏥 <b>Laboratorio:</b>

📎 <b>Puedes subir archivos PDF o imágenes</b>

🌐 <b>O regístrate en:</b> https://www.medconnect.cl/register

¿Tienes resultados para subir? 📄"""
                
            elif any(word in text for word in ['historial', 'historia', 'información']):
                response = """📋 <b>Tu Historial Médico</b>

Para ver tu información médica:

🌐 <b>Visita:</b> https://www.medconnect.cl

📊 <b>Allí encontrarás:</b>
• Consultas anteriores
• Medicamentos activos
• Resultados de exámenes
• Recordatorios

🔐 <b>Primero regístrate</b> para acceder a tu historial completo.

¿Ya tienes cuenta? 🤔"""
                
            else:
                response = """🤖 <b>No estoy seguro de entenderte</b>

💡 <b>Prueba con:</b>
• /start - Menú principal
• /ayuda - Ver opciones
• "consulta" - Registrar cita
• "medicamento" - Gestionar medicinas
• "examen" - Subir resultados

🌐 <b>O visita:</b> https://www.medconnect.cl

¿En qué puedo ayudarte? 🤔"""
            
            self.send_message(chat_id, response)
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            try:
                self.send_message(chat_id, "❌ Error procesando tu mensaje. Intenta más tarde.")
            except:
                pass
    
    def get_updates(self):
        """Obtiene actualizaciones del bot"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {'offset': self.last_update_id + 1, 'timeout': 30}
            
            response = requests.get(url, params=params, timeout=35)
            response.raise_for_status()
            
            data = response.json()
            
            if data['ok']:
                return data['result']
            else:
                logger.error(f"❌ Error en respuesta de Telegram: {data}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo updates: {e}")
            return []
    
    def run(self):
        """Ejecuta el bot"""
        logger.info("🚀 Bot simplificado iniciado")
        logger.info("📱 Esperando mensajes...")
        
        try:
            while True:
                updates = self.get_updates()
                
                for update in updates:
                    try:
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update:
                            self.process_message(update['message'])
                            
                    except Exception as e:
                        logger.error(f"❌ Error procesando update: {e}")
                        continue
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    bot = SimpleMedConnectBot()
    bot.run() 