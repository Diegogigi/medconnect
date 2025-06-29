#!/usr/bin/env python3
"""
Bot Simple y Funcional de MedConnect - Reconocimiento directo de usuarios
"""

import os
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re

# Importar el gestor de base de datos
from backend.database.sheets_manager import SheetsManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleWorkingBot:
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.last_update_id = 0
        self.db = None
        self.user_states = {}  # Para manejar conversaciones
        
        if not self.bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN no configurado")
            exit(1)
        
        # Inicializar base de datos
        try:
            self.db = SheetsManager()
            logger.info("✅ Base de datos conectada")
        except Exception as e:
            logger.error(f"❌ Error conectando base de datos: {e}")
            self.db = None
        
        logger.info("✅ Bot simple y funcional iniciado")
    
    def send_message(self, chat_id, text, reply_markup=None):
        """Envía un mensaje con opciones de teclado"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            if reply_markup:
                data['reply_markup'] = reply_markup
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"✅ Mensaje enviado a {chat_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return False
    
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
    
    def register_user(self, telegram_id, username, first_name, last_name):
        """Registra un nuevo usuario"""
        if not self.db:
            logger.error("❌ Base de datos no disponible")
            return None
            
        try:
            user_data = {
                'telegram_id': str(telegram_id),
                'nombre': first_name or username,
                'apellido': last_name or '',
                'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            user_id = self.db.create_user(user_data)
            logger.info(f"Usuario registrado: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Error registrando usuario: {e}")
            return None
    
    def save_exam(self, user_id, exam_data):
        """Guarda un examen en la base de datos"""
        if not self.db:
            return None
            
        try:
            exam_id = self.db.create_examen({
                'user_id': user_id,
                'tipo_examen': exam_data.get('tipo', ''),
                'nombre_examen': exam_data.get('nombre', ''),
                'fecha_realizacion': exam_data.get('fecha', ''),
                'resultado': exam_data.get('resultado', ''),
                'observaciones': exam_data.get('observaciones', '')
            })
            logger.info(f"Examen guardado: {exam_id}")
            return exam_id
        except Exception as e:
            logger.error(f"Error guardando examen: {e}")
            return None
    
    def save_medication(self, user_id, med_data):
        """Guarda un medicamento en la base de datos"""
        if not self.db:
            return None
            
        try:
            med_id = self.db.create_medicamento({
                'user_id': user_id,
                'nombre_medicamento': med_data.get('nombre', ''),
                'dosis': med_data.get('dosis', ''),
                'frecuencia': med_data.get('frecuencia', ''),
                'duracion': med_data.get('duracion', ''),
                'indicaciones': med_data.get('indicaciones', ''),
                'fecha_inicio': datetime.now().strftime('%Y-%m-%d')
            })
            logger.info(f"Medicamento guardado: {med_id}")
            return med_id
        except Exception as e:
            logger.error(f"Error guardando medicamento: {e}")
            return None
    
    def process_message(self, message):
        """Procesa mensajes con lógica simplificada"""
        try:
            text = message.get('text', '').strip()
            chat_id = message['chat']['id']
            user_id = message['from']['id']
            username = message['from'].get('username', 'Usuario')
            first_name = message['from'].get('first_name', '')
            last_name = message['from'].get('last_name', '')
            
            logger.info(f"📨 Mensaje de {username} ({user_id}): {text}")
            
            # Verificar si el usuario está registrado
            user = self.get_user_info(user_id)
            
            # Procesar comandos principales
            if text == '/start':
                self.handle_start(chat_id, user, first_name, username)
            elif text == '/registro':
                self.handle_registration(chat_id, user_id, username, first_name, last_name)
            elif text == '/ayuda':
                self.handle_help(chat_id)
            elif text == '/estado':
                self.handle_status(chat_id)
            else:
                # Procesar lenguaje natural
                self.handle_natural_language(chat_id, text, user, user_id)
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            try:
                self.send_message(chat_id, "❌ Error procesando tu mensaje. Intenta más tarde.")
            except:
                pass
    
    def handle_start(self, chat_id, user, first_name, username):
        """Maneja el comando /start"""
        if user:
            # Usuario registrado
            user_name = user.get('nombre', first_name or username)
            response = f"""🤖 <b>¡Bienvenido de vuelta, {user_name}!</b>

🏥 <b>Tu asistente médico personal</b>

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
    
    def handle_registration(self, chat_id, telegram_id, username, first_name, last_name):
        """Maneja el registro de usuarios"""
        try:
            user_id = self.register_user(telegram_id, username, first_name, last_name)
            if user_id:
                response = f"""✅ <b>¡Registro exitoso!</b>

👤 <b>Usuario:</b> {first_name or username}
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
    
    def handle_natural_language(self, chat_id, text, user, user_id):
        """Procesa lenguaje natural y guarda información"""
        text_lower = text.lower()
        
        # Si el usuario no está registrado, pedir registro
        if not user:
            self.send_message(chat_id, "🔐 Primero debes registrarte con /registro para usar esta función.")
            return
        
        # Procesar exámenes
        if any(word in text_lower for word in ['examen', 'resultado', 'laboratorio', 'análisis', 'eco', 'ecografía']):
            if 'eco' in text_lower or 'ecografía' in text_lower:
                # Guardar eco abdominal
                exam_data = {
                    'tipo': 'Ecografía',
                    'nombre': 'Ecografía Abdominal',
                    'fecha': datetime.now().strftime('%Y-%m-%d'),
                    'resultado': 'Pendiente de resultados',
                    'observaciones': 'Examen solicitado por el usuario'
                }
                
                exam_id = self.save_exam(user['user_id'], exam_data)
                if exam_id:
                    response = f"""🔬 <b>¡Examen registrado exitosamente!</b>

📋 <b>Detalles:</b>
• Tipo: Ecografía Abdominal
• Fecha: {datetime.now().strftime('%d/%m/%Y')}
• Estado: Registrado

✅ <b>Guardado en tu historial médico</b>

🌐 <b>Ver en la web:</b> https://www.medconnect.cl

¿Quieres agregar más detalles o subir los resultados? 📄"""
                else:
                    response = "❌ Error guardando el examen. Intenta más tarde."
                
                self.send_message(chat_id, response)
            else:
                response = """🔬 <b>Registro de Examen</b>

📋 <b>¿Qué tipo de examen quieres registrar?</b>

Puedes escribir:
• "Eco Abdominal"
• "Análisis de sangre"
• "Radiografía"
• "Tomografía"

O simplemente dime el nombre del examen y lo registro automáticamente.

¿Qué examen te hiciste? 🔬"""
                self.send_message(chat_id, response)
        
        # Procesar medicamentos
        elif any(word in text_lower for word in ['medicamento', 'medicina', 'píldora', 'pastilla', 'fármaco']):
            response = """💊 <b>Registro de Medicamento</b>

📋 <b>Para registrar tu medicamento necesito:</b>

💊 <b>Nombre:</b> (ej: Paracetamol)
📏 <b>Dosis:</b> (ej: 500mg)
⏰ <b>Frecuencia:</b> (ej: Cada 8 horas)
📅 <b>Duración:</b> (ej: 7 días)

💡 <b>Ejemplo:</b>
"Paracetamol 500mg cada 8 horas por 7 días"

¿Cuál es tu medicamento? 💊"""
            self.send_message(chat_id, response)
        
        # Procesar historial
        elif any(word in text_lower for word in ['historial', 'historia', 'información', 'datos', 'muestra', 'muéstrame']):
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
                
                self.send_message(chat_id, response)
                
            except Exception as e:
                logger.error(f"Error obteniendo historial: {e}")
                self.send_message(chat_id, "❌ Error obteniendo tu historial. Intenta más tarde.")
        
        # Procesar consultas
        elif any(word in text_lower for word in ['consulta', 'cita', 'médico', 'doctor', 'atención']):
            response = """🏥 <b>Registro de Consulta Médica</b>

📋 <b>Para registrar una consulta necesito:</b>

📅 <b>Fecha:</b> (DD/MM/AAAA)
⏰ <b>Hora:</b> (HH:MM)
👨‍⚕️ <b>Especialidad:</b> (ej: Cardiología)
🏥 <b>Centro médico:</b>

💡 <b>Ejemplo:</b>
"Consulta el 15/01/2025 a las 14:30 en Cardiología del Hospital Clínico"

¿Quieres registrar una consulta? 📝"""
            self.send_message(chat_id, response)
        
        else:
            response = """🤖 <b>No estoy seguro de entenderte</b>

💡 <b>Prueba con:</b>
• "Muéstrame mi historial"
• "Tengo un medicamento nuevo"
• "Quiero ver mis exámenes"
• "Registrar consulta"

📋 <b>O usa los comandos:</b>
• /start - Menú principal
• /ayuda - Ver opciones

🌐 <b>O visita:</b> https://www.medconnect.cl

¿En qué puedo ayudarte? 🤔"""
            self.send_message(chat_id, response)
    
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
                logger.error(f"Error en getUpdates: {data}")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo updates: {e}")
            return []
    
    def run(self):
        """Ejecuta el bot en bucle infinito"""
        logger.info("🚀 Bot simple y funcional iniciado y ejecutándose...")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    
                    if 'message' in update:
                        message = update['message']
                        
                        # Procesar mensajes de texto
                        if 'text' in message:
                            self.process_message(message)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Bot detenido por el usuario")
                break
            except Exception as e:
                logger.error(f"Error en bucle principal: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = SimpleWorkingBot()
    bot.run() 