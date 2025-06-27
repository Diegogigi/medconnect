#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Telegram independiente para MedConnect
Funciona directamente con Google Sheets
"""

import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import requests
import time
import subprocess
import sys

# Configuración de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot_supervisor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuración del bot
TELEGRAM_BOT_TOKEN = "7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck"
GOOGLE_SHEETS_ID = "1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU"

# Credenciales de Google Service Account
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
    
    def log_interaction(self, user_id, username, message, response):
        """Registra la interacción en Google Sheets"""
        try:
            if not self.spreadsheet:
                return
                
            worksheet = self.spreadsheet.worksheet('Interacciones_Bot')
            all_values = worksheet.get_all_values()
            next_id = len(all_values)
            
            row_data = [
                next_id,
                user_id,
                username or 'Sin username',
                message,
                response,
                datetime.now().isoformat(),
                'message',
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
        
        if text.startswith('/start'):
            response = """¡Hola! 👋 Bienvenido a MedConnect

Soy tu asistente personal de salud. Puedo ayudarte con:

📋 Registrar consultas médicas
💊 Gestionar medicamentos  
🩺 Registrar exámenes
👨‍👩‍👧‍👦 Notificar a familiares
📊 Consultar tu historial

¿En qué puedo ayudarte hoy?

<i>Escribe "consulta", "medicamento", "examen" o "historial"</i>"""
        
        elif 'consulta' in text or 'médico' in text or 'doctor' in text:
            response = """📋 <b>Registrar Consulta Médica</b>

Para registrar una consulta médica, necesito:

1️⃣ <b>Fecha de la consulta</b> (ej: 15/06/2024)
2️⃣ <b>Nombre del médico</b>
3️⃣ <b>Especialidad</b> (ej: Cardiología)
4️⃣ <b>Diagnóstico</b> o motivo
5️⃣ <b>Tratamiento indicado</b>

<i>Ejemplo: "Consulta del 15/06/2024 con Dr. García, cardiólogo, control presión arterial"</i>"""
        
        elif 'medicamento' in text or 'medicina' in text:
            response = """💊 <b>Registrar Medicamento</b>

Para registrar un medicamento, necesito:

1️⃣ <b>Nombre del medicamento</b>
2️⃣ <b>Dosis</b> (ej: 50mg)
3️⃣ <b>Frecuencia</b> (ej: cada 12 horas)
4️⃣ <b>Médico que lo prescribió</b>
5️⃣ <b>Fecha de inicio</b>

<i>Ejemplo: "Losartán 50mg, cada 12 horas, Dr. García, desde 15/06/2024"</i>"""
        
        elif 'examen' in text or 'análisis' in text:
            response = """🩺 <b>Registrar Examen</b>

Para registrar un examen, necesito:

1️⃣ <b>Tipo de examen</b>
2️⃣ <b>Fecha realizada</b>
3️⃣ <b>Laboratorio</b>
4️⃣ <b>Resultados principales</b>
5️⃣ <b>Médico que lo solicitó</b>

<i>Ejemplo: "Análisis de sangre, 10/06/2024, Lab Central, colesterol 180"</i>"""
        
        elif 'historial' in text or 'ver' in text:
            response = """📊 <b>Consultar Historial</b>

Tu información está guardada de forma segura.

Para ver tu historial completo:
🌐 https://medconnect.cl/patient

¿Qué información específica necesitas?
• Últimas consultas
• Medicamentos activos  
• Resultados de exámenes"""
        
        else:
            response = """🤔 No estoy seguro de cómo ayudarte.

<b>Puedes preguntarme sobre:</b>
📋 "consulta" - Registrar consultas
💊 "medicamento" - Gestionar medicamentos  
🩺 "examen" - Registrar exámenes
📊 "historial" - Ver información

O escribe /start para ver todas las opciones."""
        
        self.send_message(chat_id, response)
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
                logger.error(f"❌ Error en respuesta: {data}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo actualizaciones: {e}")
            return []
    
    def run(self):
        """Ejecuta el bot"""
        logger.info("🚀 Iniciando MedConnect Bot...")
        logger.info("📱 Bot: https://t.me/medconnect_bot")
        logger.info("⏹️  Ctrl+C para detener")
        
        try:
            while True:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    
                    if 'message' in update:
                        message = update['message']
                        user = message['from'].get('username', 'usuario')
                        text = message.get('text', '')
                        logger.info(f"📨 Mensaje de {user}: {text}")
                        self.process_message(message)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Bot detenido")
        except Exception as e:
            logger.error(f"❌ Error: {e}")

class BotSupervisor:
    def __init__(self, max_restarts=10, restart_delay=30):
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self.restart_count = 0
        self.start_time = datetime.now()
        
    def run_bot(self):
        """Ejecuta el bot en un subproceso"""
        try:
            logger.info("🚀 Iniciando bot de MedConnect...")
            
            # Ejecutar el bot
            process = subprocess.Popen(
                [sys.executable, 'bot.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Monitorear la salida del bot
            for line in iter(process.stdout.readline, ''):
                print(line.rstrip())
                
            # Esperar a que termine el proceso
            return_code = process.wait()
            logger.info(f"Bot terminó con código: {return_code}")
            
            return return_code
            
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo supervisor...")
            return 0
        except Exception as e:
            logger.error(f"❌ Error ejecutando bot: {e}")
            return 1
    
    def should_restart(self):
        """Determina si el bot debe reiniciarse"""
        if self.restart_count >= self.max_restarts:
            logger.error(f"❌ Máximo de reinicios alcanzado ({self.max_restarts})")
            return False
            
        # Reiniciar si ha fallado menos del máximo
        return True
    
    def run_with_supervision(self):
        """Ejecuta el bot con supervisión y reinicios automáticos"""
        logger.info("🎯 Supervisor de MedConnect Bot iniciado")
        logger.info(f"📊 Configuración: máx. {self.max_restarts} reinicios, retraso {self.restart_delay}s")
        
        while True:
            try:
                return_code = self.run_bot()
                
                # Si terminó normalmente (Ctrl+C), salir
                if return_code == 0:
                    logger.info("✅ Bot detenido normalmente")
                    break
                
                # Si falló, decidir si reiniciar
                self.restart_count += 1
                logger.warning(f"⚠️ Bot falló (reinicio {self.restart_count}/{self.max_restarts})")
                
                if not self.should_restart():
                    break
                
                logger.info(f"🔄 Reiniciando en {self.restart_delay} segundos...")
                time.sleep(self.restart_delay)
                
                # Incrementar el retraso gradualmente para evitar loops rápidos
                self.restart_delay = min(self.restart_delay * 1.2, 300)  # Máximo 5 minutos
                
            except KeyboardInterrupt:
                logger.info("🛑 Supervisor detenido por el usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error crítico en supervisor: {e}")
                time.sleep(60)  # Esperar más tiempo en errores críticos
        
        uptime = datetime.now() - self.start_time
        logger.info(f"📊 Supervisor terminado. Tiempo activo: {uptime}")

def main():
    """Función principal"""
    try:
        supervisor = BotSupervisor()
        supervisor.run_with_supervision()
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 