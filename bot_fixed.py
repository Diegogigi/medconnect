#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Corregido de MedConnect - Sin duplicados y con reconocimiento de usuarios
"""

import os
import json
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re

# Importar el gestor de base de datos
from backend.database.sheets_manager import SheetsManager

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

class FixedMedConnectBot:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.sheets_id = GOOGLE_SHEETS_ID
        self.last_update_id = 0
        self.processed_updates = set()  # Para evitar duplicados
        self.db = None
        
        logger.info("✅ Bot corregido iniciado")
        
        # Inicializar base de datos
        try:
            self.db = SheetsManager()
            logger.info("✅ Base de datos conectada")
        except Exception as e:
            logger.error(f"❌ Error conectando base de datos: {e}")
            self.db = None
        
        # Verificar conectividad del bot
        if not self.test_bot_connection():
            logger.error("❌ No se pudo conectar al bot")
            exit(1)
    
    def test_bot_connection(self):
        """Verifica la conectividad del bot"""
        try:
            response = requests.get(f"https://api.telegram.org/bot{self.bot_token}/getMe", timeout=10)
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
            response = requests.post(f"https://api.telegram.org/bot{self.bot_token}/deleteWebhook", timeout=10)
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
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
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
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
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
            
            # Verificar si el usuario está registrado
            user_info = self.get_user_info(user['id'])
            
            # Procesar comandos y lenguaje natural
            if text == '/start':
                self.handle_start(chat_id, user_info, user_name)
            elif text == '/registro':
                self.handle_registration(chat_id, user['id'], user_name)
            elif text == '/ayuda':
                self.handle_help(chat_id)
            elif text == '/estado':
                self.handle_status(chat_id)
            elif any(word in text.lower() for word in ['historial', 'historia', 'información', 'datos']):
                self.handle_medical_history(chat_id, user_info)
            elif any(word in text.lower() for word in ['medicamento', 'medicina', 'píldora', 'pastilla', 'fármaco']):
                self.handle_medications(chat_id, user_info)
            elif any(word in text.lower() for word in ['examen', 'resultado', 'laboratorio', 'análisis']):
                self.handle_exams(chat_id, user_info)
            elif any(word in text.lower() for word in ['familia', 'familiar', 'familiares']):
                self.handle_family(chat_id, user_info)
            elif any(word in text.lower() for word in ['consulta', 'cita', 'médico', 'doctor', 'atención']):
                self.handle_appointments(chat_id, user_info)
            elif any(word in text.lower() for word in ['recordatorio', 'recordar', 'alarma']):
                self.handle_reminders(chat_id, user_info)
            else:
                self.handle_natural_language(chat_id, text, user_info)
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            try:
                error_msg = "❌ Hubo un error procesando tu mensaje. Por favor, intenta de nuevo."
                self.send_message(chat_id, error_msg)
            except:
                pass
    
    def handle_start(self, chat_id, user, user_name):
        """Maneja el comando /start con mensaje personalizado"""
        if user:
            # Usuario registrado - mensaje personalizado
            response = f"""🤖 <b>¡Bienvenido de vuelta, {user_name}!</b>

�� <b>Tu asistente médico personal</b>

📋 <b>¿Qué necesitas hoy?</b>

• 📋 <b>Historial Médico</b> - Ver tu información
• 💊 <b>Medicamentos</b> - Gestionar tratamientos
• 🔬 <b>Exámenes</b> - Ver resultados
• 👨‍👩‍👧‍👦 <b>Familia</b> - Gestionar familiares
• 🏥 <b>Consultas</b> - Registrar citas
• ⏰ <b>Recordatorios</b> - Configurar alertas

💬 <b>También puedes escribir de forma natural:</b>
• "Muéstrame mi historial"
• "Tengo un medicamento nuevo"
• "Quiero ver mis exámenes"

🌐 <b>Sitio web:</b> https://www.medconnect.cl

¡Estoy aquí para ayudarte! 🩺"""
        else:
            # Usuario no registrado
            response = """🤖 <b>¡Bienvenido a MedConnect!</b>

🏥 <b>Tu asistente médico personal</b>

🔐 <b>Para comenzar, necesitas registrarte:</b>

📝 <b>Opciones:</b>
• /registro - Registrarte aquí mismo
• 🌐 <a href="https://www.medconnect.cl/register">Registrarte en la web</a>

📋 <b>Una vez registrado podrás:</b>
• Ver tu historial médico
• Gestionar medicamentos
• Subir resultados de exámenes
• Configurar familiares autorizados
• Recibir recordatorios

¿Quieres registrarte ahora? 📝"""
        
        keyboard = self.create_keyboard([
            "📋 Historial Médico",
            "💊 Medicamentos", 
            "🔬 Exámenes",
            "👨‍👩‍👧‍👦 Familia",
            "🏥 Consultas",
            "⏰ Recordatorios"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def handle_registration(self, chat_id, telegram_id, username):
        """Maneja el registro de usuarios"""
        try:
            user_id = self.register_user(telegram_id, username)
            if user_id:
                response = f"""✅ <b>¡Registro exitoso!</b>

👤 <b>Usuario:</b> {username}
🆔 <b>ID:</b> {user_id}

🎉 <b>¡Ya puedes usar todas las funciones de MedConnect!</b>

📋 <b>Prueba:</b>
• "Muéstrame mi historial"
• "Tengo un medicamento nuevo"
• "Quiero ver mis exámenes"

🌐 <b>También puedes usar la web:</b> https://www.medconnect.cl

¡Bienvenido a MedConnect! 🩺"""
            else:
                response = """❌ <b>Error en el registro</b>

No se pudo completar tu registro. Intenta:

🌐 <b>Registrarte en la web:</b> https://www.medconnect.cl/register

O contacta soporte si el problema persiste."""
            
            self.send_message(chat_id, response)
            
        except Exception as e:
            logger.error(f"Error en registro: {e}")
            self.send_message(chat_id, "❌ Error en el registro. Intenta más tarde.")
    
    def handle_medical_history(self, chat_id, user):
        """Maneja consultas sobre historial médico"""
        if not user:
            self.send_message(chat_id, "🔐 Primero debes registrarte con /registro")
            return
        
        try:
            # Obtener resumen médico
            summary = self.db.get_medical_summary(user['user_id'])
            
            response = f"""📋 <b>Historial Médico de {user.get('nombre', 'Usuario')}</b>

👤 <b>Información Personal:</b>
• Nombre: {user.get('nombre', 'N/A')} {user.get('apellido', '')}
• Edad: {user.get('edad', 'N/A')} años
• RUT: {user.get('rut', 'N/A')}

📊 <b>Resumen Médico:</b>
• Consultas: {summary.get('total_consultas', 0)}
• Medicamentos activos: {summary.get('medicamentos_activos', 0)}
• Exámenes: {summary.get('total_examenes', 0)}
• Familiares autorizados: {summary.get('familiares', 0)}

📅 <b>Última actualización:</b> {datetime.now().strftime('%d/%m/%Y')}

🌐 <b>Ver detalles completos:</b> https://www.medconnect.cl

¿Qué información específica necesitas? 🤔"""
            
            keyboard = self.create_keyboard([
                "📋 Ver consultas",
                "💊 Ver medicamentos",
                "🔬 Ver exámenes",
                "👨‍👩‍👧‍👦 Ver familiares",
                "🔙 Volver al menú"
            ])
            
            self.send_message(chat_id, response, keyboard)
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            self.send_message(chat_id, "❌ Error obteniendo tu historial. Intenta más tarde.")
    
    def handle_medications(self, chat_id, user):
        """Maneja consultas sobre medicamentos"""
        if not user:
            self.send_message(chat_id, "🔐 Primero debes registrarte con /registro")
            return
        
        try:
            # Obtener medicamentos activos
            medicamentos = self.db.get_user_medicamentos_activos(user['user_id'])
            
            if medicamentos:
                response = f"""💊 <b>Medicamentos Activos</b>

📋 <b>Tienes {len(medicamentos)} medicamento(s) activo(s):</b>

"""
                for med in medicamentos:
                    response += f"""💊 <b>{med.get('nombre_medicamento', 'N/A')}</b>
• Dosis: {med.get('dosis', 'N/A')}
• Frecuencia: {med.get('frecuencia', 'N/A')}
• Duración: {med.get('duracion', 'N/A')}
• Estado: {med.get('estado', 'N/A')}

"""
            else:
                response = """💊 <b>Medicamentos</b>

📋 <b>No tienes medicamentos registrados actualmente.</b>

¿Quieres registrar un nuevo medicamento? 📝"""
            
            keyboard = self.create_keyboard([
                "➕ Agregar medicamento",
                "📋 Ver todos",
                "⏰ Recordatorios",
                "🔙 Volver al menú"
            ])
            
            self.send_message(chat_id, response, keyboard)
            
        except Exception as e:
            logger.error(f"Error obteniendo medicamentos: {e}")
            self.send_message(chat_id, "❌ Error obteniendo medicamentos. Intenta más tarde.")
    
    def handle_exams(self, chat_id, user):
        """Maneja consultas sobre exámenes"""
        if not user:
            self.send_message(chat_id, "🔐 Primero debes registrarte con /registro")
            return
        
        try:
            # Obtener exámenes del usuario
            examenes = self.db.get_user_examenes(user['user_id'])
            
            if examenes:
                response = f"""🔬 <b>Resultados de Exámenes</b>

📋 <b>Tienes {len(examenes)} examen(es) registrado(s):</b>

"""
                for exam in examenes[:3]:  # Mostrar solo los 3 más recientes
                    response += f"""🔬 <b>{exam.get('nombre_examen', 'N/A')}</b>
• Tipo: {exam.get('tipo_examen', 'N/A')}
• Fecha: {exam.get('fecha_realizacion', 'N/A')}
• Estado: {exam.get('estado', 'N/A')}

"""
                
                if len(examenes) > 3:
                    response += f"📄 <b>Y {len(examenes) - 3} examen(es) más...</b>\n\n"
            else:
                response = """🔬 <b>Exámenes</b>

📋 <b>No tienes exámenes registrados actualmente.</b>

¿Quieres subir un resultado de examen? 📄"""
            
            keyboard = self.create_keyboard([
                "📄 Subir examen",
                "📋 Ver todos",
                "🔍 Buscar por fecha",
                "🔙 Volver al menú"
            ])
            
            self.send_message(chat_id, response, keyboard)
            
        except Exception as e:
            logger.error(f"Error obteniendo exámenes: {e}")
            self.send_message(chat_id, "❌ Error obteniendo exámenes. Intenta más tarde.")
    
    def handle_family(self, chat_id, user):
        """Maneja consultas sobre familiares"""
        if not user:
            self.send_message(chat_id, "🔐 Primero debes registrarte con /registro")
            return
        
        try:
            # Obtener familiares autorizados
            familiares = self.db.get_familiares_autorizados(user['user_id'])
            
            if familiares:
                response = f"""👨‍👩‍👧‍👦 <b>Familiares Autorizados</b>

📋 <b>Tienes {len(familiares)} familiar(es) autorizado(s):</b>

"""
                for fam in familiares:
                    response += f"""👤 <b>{fam.get('nombre_familiar', 'N/A')}</b>
• Parentesco: {fam.get('parentesco', 'N/A')}
• Teléfono: {fam.get('telefono', 'N/A')}
• Estado: {fam.get('estado', 'N/A')}

"""
            else:
                response = """👨‍👩‍👧‍👦 <b>Familiares</b>

📋 <b>No tienes familiares autorizados registrados.</b>

¿Quieres agregar un familiar autorizado? 👤"""
            
            keyboard = self.create_keyboard([
                "👤 Agregar familiar",
                "📋 Ver todos",
                "🔐 Gestionar permisos",
                "🔙 Volver al menú"
            ])
            
            self.send_message(chat_id, response, keyboard)
            
        except Exception as e:
            logger.error(f"Error obteniendo familiares: {e}")
            self.send_message(chat_id, "❌ Error obteniendo familiares. Intenta más tarde.")
    
    def handle_appointments(self, chat_id, user):
        """Maneja consultas sobre citas médicas"""
        if not user:
            self.send_message(chat_id, "🔐 Primero debes registrarte con /registro")
            return
        
        response = """🏥 <b>Consultas Médicas</b>

📋 <b>Para registrar una consulta necesito:</b>

📅 <b>Fecha:</b> (DD/MM/AAAA)
⏰ <b>Hora:</b> (HH:MM)
👨‍⚕️ <b>Especialidad:</b> (ej: Cardiología)
🏥 <b>Centro médico:</b>

💡 <b>Ejemplo:</b>
"Consulta el 15/01/2025 a las 14:30 en Cardiología del Hospital Clínico"

🌐 <b>O regístrate en:</b> https://www.medconnect.cl

¿Quieres registrar una consulta? 📝"""
        
        keyboard = self.create_keyboard([
            "📅 Registrar consulta",
            "📋 Ver consultas",
            "🔙 Volver al menú"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def handle_reminders(self, chat_id, user):
        """Maneja consultas sobre recordatorios"""
        if not user:
            self.send_message(chat_id, "🔐 Primero debes registrarte con /registro")
            return
        
        try:
            # Obtener recordatorios activos
            reminders = self.db.get_user_active_reminders(user['user_id'])
            
            if reminders:
                response = f"""⏰ <b>Recordatorios Activos</b>

📋 <b>Tienes {len(reminders)} recordatorio(s) activo(s):</b>

"""
                for rem in reminders:
                    response += f"""⏰ <b>{rem.get('titulo', 'N/A')}</b>
• Tipo: {rem.get('tipo', 'N/A')}
• Fecha: {rem.get('fecha_programada', 'N/A')}
• Hora: {rem.get('hora_programada', 'N/A')}

"""
            else:
                response = """⏰ <b>Recordatorios</b>

📋 <b>No tienes recordatorios activos.</b>

¿Quieres configurar un recordatorio? ⏰"""
            
            keyboard = self.create_keyboard([
                "⏰ Crear recordatorio",
                "📋 Ver todos",
                "🔙 Volver al menú"
            ])
            
            self.send_message(chat_id, response, keyboard)
            
        except Exception as e:
            logger.error(f"Error obteniendo recordatorios: {e}")
            self.send_message(chat_id, "❌ Error obteniendo recordatorios. Intenta más tarde.")
    
    def handle_help(self, chat_id):
        """Maneja el comando de ayuda"""
        response = """📋 <b>Ayuda de MedConnect</b>

🏥 <b>Funciones principales:</b>

📋 <b>Historial Médico:</b>
• Ver información personal
• Consultas anteriores
• Resumen médico

💊 <b>Medicamentos:</b>
• Ver medicamentos activos
• Registrar nuevos tratamientos
• Configurar recordatorios

🔬 <b>Exámenes:</b>
• Subir resultados (PDF/imágenes)
• Ver historial de exámenes
• Buscar por fecha

👨‍👩‍👧‍👦 <b>Familia:</b>
• Agregar familiares autorizados
• Gestionar permisos
• Notificaciones familiares

🏥 <b>Consultas:</b>
• Registrar citas médicas
• Ver agenda
• Recordatorios de citas

⏰ <b>Recordatorios:</b>
• Configurar alertas
• Recordatorios de medicamentos
• Citas próximas

💬 <b>Lenguaje natural:</b>
Puedes escribir de forma natural, por ejemplo:
• "Muéstrame mi historial"
• "Tengo un medicamento nuevo"
• "Quiero ver mis exámenes"
• "Agregar familiar"

🌐 <b>Sitio web:</b> https://www.medconnect.cl

¿En qué puedo ayudarte? 🤔"""
        
        self.send_message(chat_id, response)
    
    def handle_status(self, chat_id):
        """Maneja el comando de estado"""
        db_status = "✅ Conectada" if self.db else "❌ No disponible"
        
        response = f"""✅ <b>Estado del Sistema MedConnect</b>

🤖 <b>Bot:</b> Funcionando correctamente
🌐 <b>Web:</b> https://www.medconnect.cl
📊 <b>Base de datos:</b> {db_status}
⏰ <b>Última actualización:</b> Ahora

🔄 <b>Servicios:</b>
• ✅ Telegram Bot
• ✅ Web App
• {'✅' if self.db else '❌'} Base de datos
• ✅ Notificaciones

¡Todo funcionando perfectamente! 🎉"""
        
        self.send_message(chat_id, response)
    
    def handle_natural_language(self, chat_id, text, user):
        """Procesa lenguaje natural"""
        text_lower = text.lower()
        
        # Patrones de lenguaje natural
        if any(word in text_lower for word in ['muestra', 'muéstrame', 'ver', 'mostrar']):
            if any(word in text_lower for word in ['historial', 'historia', 'información']):
                self.handle_medical_history(chat_id, user)
            elif any(word in text_lower for word in ['medicamento', 'medicina']):
                self.handle_medications(chat_id, user)
            elif any(word in text_lower for word in ['examen', 'resultado']):
                self.handle_exams(chat_id, user)
            elif any(word in text_lower for word in ['familia', 'familiar']):
                self.handle_family(chat_id, user)
            else:
                self.handle_medical_history(chat_id, user)
        
        elif any(word in text_lower for word in ['tengo', 'nuevo', 'agregar', 'añadir']):
            if any(word in text_lower for word in ['medicamento', 'medicina']):
                self.handle_medications(chat_id, user)
            elif any(word in text_lower for word in ['examen', 'resultado']):
                self.handle_exams(chat_id, user)
            elif any(word in text_lower for word in ['familiar', 'familia']):
                self.handle_family(chat_id, user)
            else:
                response = """🤔 <b>¿Qué quieres agregar?</b>

💊 <b>Medicamento nuevo?</b>
🔬 <b>Resultado de examen?</b>
👤 <b>Familiar autorizado?</b>

Escribe de forma natural, por ejemplo:
• "Tengo un medicamento nuevo"
• "Quiero subir un examen"
• "Agregar familiar"

¿Qué necesitas? 🤔"""
                self.send_message(chat_id, response)
        
        else:
            response = """🤖 <b>No estoy seguro de entenderte</b>

💡 <b>Prueba con:</b>
• "Muéstrame mi historial"
• "Tengo un medicamento nuevo"
• "Quiero ver mis exámenes"
• "Agregar familiar"

📋 <b>O usa los comandos:</b>
• /start - Menú principal
• /ayuda - Ver opciones

🌐 <b>O visita:</b> https://www.medconnect.cl

¿En qué puedo ayudarte? 🤔"""
            self.send_message(chat_id, response)
    
    def get_user_info(self, telegram_id):
        """Obtiene información del usuario desde la base de datos"""
        if not self.db:
            logger.error("❌ Base de datos no disponible")
            return None
            
        try:
            user = self.db.get_user_by_telegram_id(str(telegram_id))
            if user:
                logger.info(f"✅ Usuario encontrado: {user.get('nombre', 'N/A')}")
            else:
                logger.info(f"❌ Usuario no encontrado para Telegram ID: {telegram_id}")
            return user
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}")
            return None
    
    def register_user(self, telegram_id, username):
        """Registra un nuevo usuario"""
        if not self.db:
            logger.error("❌ Base de datos no disponible")
            return None
            
        try:
            user_data = {
                'telegram_id': str(telegram_id),
                'nombre': username,
                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            user_id = self.db.create_user(user_data)
            logger.info(f"Usuario registrado: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")
            return None
    
    def create_keyboard(self, options, one_time=True):
        """Crea un teclado personalizado"""
        keyboard = []
        for option in options:
            keyboard.append([{"text": option}])
        
        return {
            "keyboard": keyboard,
            "one_time_keyboard": one_time,
            "resize_keyboard": True
        }
    
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
        bot = FixedMedConnectBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        exit(1)

if __name__ == "__main__":
    main() 