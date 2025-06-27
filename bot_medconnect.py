#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Telegram independiente para MedConnect
Funciona directamente con Google Sheets sin necesidad de servidor web local
"""

import os
import json
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import requests
import time

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración del bot
TELEGRAM_BOT_TOKEN = "7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck"
GOOGLE_SHEETS_ID = "1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU"

# Credenciales de Google Service Account (reales)
GOOGLE_SERVICE_ACCOUNT_JSON = {
    "type": "service_account",
    "project_id": "sincere-mission-463804-h9",
    "private_key_id": "95d16ea62efca929d5ba7b73a14bb07e0b28eb48",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCkF61+dbK/uXup\nwh2Mwt8bLAEHgOgywXOMhDlR/Xhnyos3my8Q+ovx5rpYE822YqA/BhRVhYoBr1A2\nXkYimPiD514PZ/3eLw+flhAVGlOvbWULGDfZFQNFT1+yzbKds+HNjD6p3mr5lGcz\nnPJS2x4rzEQlJQVG8r5RbiM5vmKxGMBG41mzhlFUCenXta+jgdaRlVQWmjsxY3RM\nIIgiCi8/2UO1RebSyGHQ1SXVXcDuvzDlcNSreg/dZQmyDUlqje4uu4qDYf0p/oC/\nw7W6lzE22WrEsRSmGVVpxftXKNsCDOt8ubQbpko9kVj14Br0Bvh24VqTTW7HJ/wL\nIBcFva/nAgMBAAECggEAAyZZNDY6Kif7UbTiMFOFSNY9ZtF4o5DHEQlwuDwvVX6z\n0WtvKdpFWW1eYlZu+nNGNC9/sGyRy5p75a9FlWBuVMnaKl2Kp/srR5rv0BfjR1jI\nOcBLQiV/HJN7eMkuBozvZqysf0I/t2671GfM1v5Rw/F11WiygzwhnxqIHpGi/1c8\naDKZTFlw+xmv29tsrG32K0P7/aCQAgChV1j4TFuapSvH181B5Uv/FEixP2HcPHic\ntLHx064uVmtlN0QWgw5KM0z95qlXsdq3cYvqESh5OmQ9ALscBzZazyPztjzYGIHv\nuamL92Njd69vV5qc9rU7DlNq6o0oIEKNP+qiGWE8EQKBgQDYmnEtv31N+/erD4S2\ni3wehrYPfQY4I/MqnGhYPqY4RrsVrU8zRwnVyl8ilqB66rCpsZRp4sEDVITKwFua\nngOXIEw7RJXJfqaTUnBvbeDpz4X4lK5v+A8SwYRlK07qmep9soB79IMQeiMFVVz7\n5ojieJMVY7mtwy9nm9SBeS3FewKBgQDB8DWhyfbVpnxGm5FSqZjt7FD4kiPBaUop\n8f8TiQ6y2ODslwCH4nTN5sMHtPMTEvFkV4tRoG3ATep+tTGGRhGdJJOxzwckxh8X\nS0SzkCnJd06vclPjSqfDXteYKuyX0FGXysdWFIwOZ0QycvAUm+a7Ut1HolXAuiq9\ncisFeFkVhQKBgF4chI5nBA+tKcgWXwhdhJlS2KnUHa6o2A+sk5274sbS3Jini6Dw\n/bH5UuqZXbLqY8XnVV/IWSqUP3pEp8h/XXn9W4Ho49f/gmrCR/3yVOXh+AiwuTYH\nJq10jYzTi19dbsgclbzF2WiAWNUJaPQ+Dz2vO+DwSo3YH7G5wFRdDWkfAoGAMXCO\nC4+T+EU32zwfYOZRUR30Slne+Zhgyq6haxZ+g8NcG5QnE3z8b90LDPTpHoyusvjK\nUGXIdMSoKeMBHAzSwq+nYyW22X4UQPj0K55tuKlMitdnYUMP33NXHLicldsKYdrU\n1DHqvmU+8mlwoKBZwplORcuxdq8+5Aqtwvg6JY0CgYAxp/xa94PNFp4FO6LSQcNd\ngB4XZpj0AMlZqf70v7/0P1GU3aaSaLBEOUr4EzvyN7Jqd0WjSd0D+Z7R5XWFGbxu\nzuzj/OGWV0GDBppWfY4FwIYx9b564abDbhchqF0a3jYTMsUxk3J8cbLwoqzOU8sE\nym0W+E4k/xHFdwNtunoySw==\n-----END PRIVATE KEY-----\n",
    "client_email": "medconnect@sincere-mission-463804-h9.iam.gserviceaccount.com",
    "client_id": "109935890158775682198",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/medconnect%40sincere-mission-463804-h9.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

class MedConnectBot:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.sheets_id = GOOGLE_SHEETS_ID
        self.last_update_id = 0
        self.setup_google_sheets()
        
    def setup_google_sheets(self):
        """Configura la conexión con Google Sheets"""
        try:
            # Usar las credenciales del service account
            credentials = Credentials.from_service_account_info(
                GOOGLE_SERVICE_ACCOUNT_JSON,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            self.gc = gspread.authorize(credentials)
            self.spreadsheet = self.gc.open_by_key(self.sheets_id)
            logger.info("✅ Conexión con Google Sheets establecida")
            
        except Exception as e:
            logger.error(f"❌ Error conectando con Google Sheets: {e}")
            self.gc = None
            self.spreadsheet = None
    
    def log_interaction(self, user_id, username, message, response, action_type="message"):
        """Registra la interacción en Google Sheets"""
        try:
            if not self.spreadsheet:
                return
                
            worksheet = self.spreadsheet.worksheet('Interacciones_Bot')
            
            # Obtener el siguiente ID
            all_values = worksheet.get_all_values()
            next_id = len(all_values)  # El header cuenta como 1
            
            row_data = [
                next_id,
                user_id,
                username or 'Sin username',
                message,
                response,
                datetime.now().isoformat(),
                action_type,
                'processed'
            ]
            
            worksheet.append_row(row_data)
            logger.info(f"✅ Interacción registrada para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error registrando interacción: {e}")
    
    def send_message(self, chat_id, text):
        """Envía un mensaje a través del bot de Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            logger.info(f"✅ Mensaje enviado a chat {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return False
    
    def process_message(self, message):
        """Procesa los mensajes recibidos"""
        text = message.get('text', '').lower().strip()
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        username = message['from'].get('username', '')
        
        # Procesar comandos y mensajes
        if text.startswith('/start'):
            response = """¡Hola! 👋 Bienvenido a MedConnect

Soy tu asistente personal de salud. Puedo ayudarte con:

📋 Registrar consultas médicas
💊 Gestionar medicamentos  
🩺 Registrar exámenes
👨‍👩‍👧‍👦 Notificar a familiares
📊 Consultar tu historial

¿En qué puedo ayudarte hoy?

<i>Escribe palabras como "consulta", "medicamento", "examen" o "historial" para comenzar.</i>"""
        
        elif 'consulta' in text or 'médico' in text or 'doctor' in text:
            response = """📋 <b>Registrar Consulta Médica</b>

Para registrar una consulta médica, necesito la siguiente información:

1️⃣ <b>Fecha de la consulta</b> (ej: 15/06/2024)
2️⃣ <b>Nombre del médico</b>
3️⃣ <b>Especialidad</b> (ej: Cardiología, Medicina General)
4️⃣ <b>Diagnóstico</b> o motivo de consulta
5️⃣ <b>Tratamiento indicado</b>

¿Podrías proporcionarme esta información paso a paso?

<i>Ejemplo: "Consulta del 15/06/2024 con Dr. García, cardiólogo, por control de presión arterial, medicamento Losartán 50mg"</i>"""
        
        elif 'medicamento' in text or 'medicina' in text or 'pastilla' in text:
            response = """💊 <b>Registrar Medicamento</b>

Para registrar un medicamento, necesito:

1️⃣ <b>Nombre del medicamento</b>
2️⃣ <b>Dosis</b> (ej: 50mg, 10ml)
3️⃣ <b>Frecuencia</b> (ej: cada 8 horas, 2 veces al día)
4️⃣ <b>Médico que lo prescribió</b>
5️⃣ <b>Fecha de inicio</b>

¿Tienes esta información?

<i>Ejemplo: "Medicamento Losartán 50mg, cada 12 horas, prescrito por Dr. García, desde el 15/06/2024"</i>"""
        
        elif 'examen' in text or 'análisis' in text or 'laboratorio' in text:
            response = """🩺 <b>Registrar Examen</b>

Para registrar un examen médico, necesito:

1️⃣ <b>Tipo de examen</b> (ej: Análisis de sangre, Electrocardiograma)
2️⃣ <b>Fecha realizada</b>
3️⃣ <b>Laboratorio o centro médico</b>
4️⃣ <b>Resultados principales</b>
5️⃣ <b>Médico que lo solicitó</b>

¿Tienes esta información?

<i>Ejemplo: "Análisis de sangre del 10/06/2024 en Lab Central, colesterol 180, solicitado por Dr. García"</i>"""
        
        elif 'historial' in text or 'ver' in text or 'consultar' in text:
            response = """📊 <b>Consultar Historial Médico</b>

Tu información médica está guardada de forma segura. Puedes consultar:

🏥 <b>Últimas consultas médicas</b>
💊 <b>Medicamentos activos</b>
🩺 <b>Resultados de exámenes</b>
👨‍⚕️ <b>Médicos tratantes</b>

Para ver tu historial completo, visita:
🌐 <b>Portal Web:</b> https://medconnect.cl/patient

¿Qué información específica te gustaría consultar?

<i>También puedes preguntar: "¿cuáles son mis medicamentos?" o "¿cuándo fue mi última consulta?"</i>"""
        
        elif 'familia' in text or 'familiar' in text or 'compartir' in text:
            response = """👨‍👩‍👧‍👦 <b>Acceso Familiar</b>

Puedes autorizar a tus familiares para que accedan a tu información médica:

✅ <b>Beneficios:</b>
• Familiares pueden estar informados
• Apoyo en emergencias médicas
• Recordatorios de medicamentos
• Acompañamiento en consultas

📝 <b>Para autorizar acceso:</b>
Proporciona el nombre, parentesco y teléfono del familiar.

<i>Ejemplo: "Autorizar a María González, mi hija, teléfono +56912345678"</i>

🔒 <b>Tu privacidad está protegida.</b> Solo tú decides quién puede acceder."""
        
        elif 'ayuda' in text or 'help' in text:
            response = """❓ <b>Centro de Ayuda - MedConnect</b>

<b>Comandos disponibles:</b>
• /start - Mensaje de bienvenida
• "consulta" - Registrar consulta médica
• "medicamento" - Registrar medicamentos
• "examen" - Registrar exámenes
• "historial" - Ver tu información
• "familia" - Gestionar acceso familiar

<b>¿Cómo funciona?</b>
1️⃣ Escribe qué quieres hacer
2️⃣ Sigue las instrucciones
3️⃣ Tu información se guarda automáticamente

<b>Soporte técnico:</b>
📧 soporte@medconnect.cl
📱 WhatsApp: +56912345678

<b>Horario de atención:</b>
🕒 Lunes a Viernes: 8:00 - 18:00
🕒 Sábados: 9:00 - 13:00"""
        
        else:
            response = """🤔 No estoy seguro de cómo ayudarte con eso.

<b>Puedes preguntarme sobre:</b>
📋 <b>"consulta"</b> - Registrar consultas médicas
💊 <b>"medicamento"</b> - Gestionar medicamentos
🩺 <b>"examen"</b> - Registrar exámenes
📊 <b>"historial"</b> - Ver tu información médica
👨‍👩‍👧‍👦 <b>"familia"</b> - Acceso familiar

O escribe <b>/start</b> para ver todas las opciones.

<i>Tip: Usa palabras clave simples como "consulta", "medicina" o "examen"</i>"""
        
        # Enviar respuesta
        self.send_message(chat_id, response)
        
        # Registrar interacción
        self.log_interaction(user_id, username, message.get('text', ''), response)
    
    def get_updates(self):
        """Obtiene actualizaciones del bot"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {
                'offset': self.last_update_id + 1,
                'timeout': 30
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data['ok']:
                return data['result']
            else:
                logger.error(f"❌ Error en respuesta de Telegram: {data}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo actualizaciones: {e}")
            return []
    
    def run(self):
        """Ejecuta el bot en modo polling"""
        logger.info("🚀 Iniciando MedConnect Bot...")
        logger.info("📱 Bot disponible en: https://t.me/medconnect_bot")
        logger.info("⏹️  Presiona Ctrl+C para detener")
        
        try:
            while True:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    
                    if 'message' in update:
                        message = update['message']
                        logger.info(f"📨 Mensaje recibido de {message['from'].get('username', 'usuario')}: {message.get('text', '')}")
                        self.process_message(message)
                
                time.sleep(1)  # Pequeña pausa para no saturar la API
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"❌ Error ejecutando bot: {e}")

if __name__ == "__main__":
    bot = MedConnectBot()
    bot.run() 