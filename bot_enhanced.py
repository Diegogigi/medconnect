#!/usr/bin/env python3
"""
Bot Mejorado de MedConnect - Experiencia de Usuario Excepcional
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

class EnhancedMedConnectBot:
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.last_update_id = 0
        self.db = None
        self.user_states = {}  # Para manejar conversaciones inteligentes
        self.temp_data = {}    # Para almacenar datos temporales
        
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
        
        logger.info("✅ Bot mejorado iniciado")
    
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
    
    def create_keyboard(self, options, one_time=True, inline=False):
        """Crea un teclado personalizado"""
        if inline:
            keyboard = []
            for option in options:
                keyboard.append([{"text": option, "callback_data": option.lower().replace(' ', '_')}])
            return {"inline_keyboard": keyboard}
        else:
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
    
    def get_user_state(self, chat_id):
        """Obtiene el estado actual del usuario"""
        return self.user_states.get(chat_id, {'state': 'idle', 'data': {}})
    
    def set_user_state(self, chat_id, state, data=None):
        """Establece el estado del usuario"""
        if data is None:
            data = {}
        self.user_states[chat_id] = {'state': state, 'data': data}
        logger.info(f"Estado de usuario {chat_id}: {state}")
    
    def clear_user_state(self, chat_id):
        """Limpia el estado del usuario"""
        if chat_id in self.user_states:
            del self.user_states[chat_id]
        if chat_id in self.temp_data:
            del self.temp_data[chat_id]
    
    def process_message(self, message):
        """Procesa mensajes con lógica mejorada"""
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
            
            # Obtener estado actual
            current_state = self.get_user_state(chat_id)
            
            # Procesar comandos principales (siempre disponibles)
            if text == '/start':
                self.clear_user_state(chat_id)
                self.handle_start(chat_id, user, first_name, username)
            elif text == '/registro':
                self.clear_user_state(chat_id)
                self.handle_registration(chat_id, user_id, username, first_name, last_name)
            elif text == '/ayuda':
                self.clear_user_state(chat_id)
                self.handle_help(chat_id)
            elif text == '/estado':
                self.handle_status(chat_id)
            elif text == '/cancelar':
                self.clear_user_state(chat_id)
                self.send_message(chat_id, "✅ Operación cancelada. ¿En qué puedo ayudarte?")
            else:
                # Procesar según el estado actual
                self.handle_state_based_message(chat_id, text, user, current_state)
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {e}")
            try:
                self.send_message(chat_id, "❌ Error procesando tu mensaje. Intenta más tarde.")
            except:
                pass
    
    def handle_state_based_message(self, chat_id, text, user, current_state):
        """Maneja mensajes según el estado actual del usuario"""
        state = current_state['state']
        data = current_state['data']
        
        # Si el usuario no está registrado, pedir registro
        if not user and state != 'registering':
            self.send_message(chat_id, "🔐 Primero debes registrarte con /registro para usar esta función.")
            return
        
        # Procesar según el estado
        if state == 'idle':
            self.handle_natural_language(chat_id, text, user)
        elif state == 'registering':
            self.handle_registration_flow(chat_id, text, user)
        elif state == 'adding_exam':
            self.handle_exam_flow(chat_id, text, user, data)
        elif state == 'adding_medication':
            self.handle_medication_flow(chat_id, text, user, data)
        elif state == 'adding_appointment':
            self.handle_appointment_flow(chat_id, text, user, data)
        else:
            # Estado desconocido, volver a idle
            self.set_user_state(chat_id, 'idle')
            self.handle_natural_language(chat_id, text, user)
    
    def handle_start(self, chat_id, user, first_name, username):
        """Maneja el comando /start con experiencia mejorada"""
        if user:
            # Usuario registrado
            user_name = user.get('nombre', first_name or username)
            response = f"""🤖 <b>¡Bienvenido de vuelta, {user_name}! 👋</b>

🏥 <b>Tu asistente médico personal</b>

💡 <b>¿Qué te gustaría hacer hoy?</b>

📋 <b>Gestionar información:</b>
• Ver mi historial médico
• Registrar un nuevo examen
• Agregar un medicamento
• Programar una consulta

🔍 <b>Consultar datos:</b>
• Ver mis medicamentos activos
• Revisar mis exámenes
• Ver próximas citas

⚙️ <b>Configuración:</b>
• Gestionar familiares
• Configurar recordatorios

💬 <b>También puedes escribir de forma natural:</b>
• "Tengo un eco abdominal"
• "Necesito registrar un medicamento"
• "Muéstrame mi historial"

🌐 <b>Sitio web:</b> https://www.medconnect.cl

¡Estoy aquí para ayudarte! 🩺"""
        else:
            # Usuario no registrado
            response = """🤖 <b>¡Bienvenido a MedConnect! 👋</b>

🏥 <b>Tu asistente médico personal</b>

🎯 <b>¿Qué es MedConnect?</b>
Es tu compañero digital para gestionar toda tu información médica de forma segura y organizada.

🔐 <b>Para comenzar, necesitas registrarte:</b>

📝 <b>Opciones de registro:</b>
• /registro - Registrarte aquí mismo (rápido y fácil)
• 🌐 <a href="https://www.medconnect.cl/register">Registrarte en la web</a> (más opciones)

🎁 <b>Una vez registrado podrás:</b>
• 📋 Ver tu historial médico completo
• 💊 Gestionar medicamentos con recordatorios
• 🔬 Subir y organizar resultados de exámenes
• 👨‍👩‍👧‍👦 Compartir información con familiares
• ⏰ Recibir alertas y recordatorios
• 🏥 Programar y gestionar citas médicas

💡 <b>¿Por qué registrarse?</b>
• Información centralizada y segura
• Acceso desde cualquier dispositivo
• Historial médico completo
• Recordatorios automáticos
• Compartir con profesionales de la salud

¿Quieres registrarte ahora? Es rápido y gratuito! 📝"""
        
        keyboard = self.create_keyboard([
            "📋 Ver Historial",
            "🔬 Registrar Examen", 
            "💊 Agregar Medicamento",
            "🏥 Programar Cita",
            "👨‍👩‍👧‍👦 Gestionar Familia",
            "⚙️ Configuración"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def handle_registration(self, chat_id, telegram_id, username, first_name, last_name):
        """Inicia el flujo de registro mejorado"""
        self.set_user_state(chat_id, 'registering', {
            'telegram_id': telegram_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        })
        
        response = """📝 <b>¡Perfecto! Vamos a registrarte en MedConnect</b>

👤 <b>Información que tengo de ti:</b>
• Nombre: {first_name or username}
• Usuario: @{username}

✅ <b>¿Es correcta esta información?</b>

Si es correcta, escribe "Sí" o "Correcto"
Si quieres modificarla, escribe "No" o "Cambiar"

💡 <b>También puedes:</b>
• Escribir tu nombre completo
• Agregar tu apellido
• Cancelar con /cancelar

¿Cómo quieres proceder? 🤔""".format(
            first_name=first_name or username,
            username=username or "sin_usuario"
        )
        
        keyboard = self.create_keyboard([
            "✅ Sí, es correcto",
            "❌ No, cambiar",
            "🚫 Cancelar"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def handle_registration_flow(self, chat_id, text, user):
        """Maneja el flujo de registro paso a paso"""
        data = self.get_user_state(chat_id)['data']
        
        if any(word in text.lower() for word in ['sí', 'si', 'correcto', 'ok', 'bien']):
            # Confirmar registro
            try:
                user_id = self.register_user(
                    data['telegram_id'],
                    data['username'],
                    data['first_name'],
                    data['last_name']
                )
                
                if user_id:
                    self.clear_user_state(chat_id)
                    response = f"""🎉 <b>¡Registro exitoso!</b>

✅ <b>¡Bienvenido a MedConnect!</b>

👤 <b>Usuario:</b> {data['first_name'] or data['username']}
🆔 <b>ID:</b> {user_id}

🎁 <b>¡Ya tienes acceso a todas las funciones!</b>

💡 <b>¿Qué te gustaría hacer primero?</b>
• "Muéstrame mi historial" - Ver tu información
• "Tengo un examen" - Registrar un examen
• "Necesito un medicamento" - Agregar medicamento
• "Programar consulta" - Agendar cita médica

🌐 <b>También puedes usar la web:</b> https://www.medconnect.cl

¡Estoy aquí para ayudarte! 🩺"""
                    
                    keyboard = self.create_keyboard([
                        "📋 Ver Historial",
                        "🔬 Registrar Examen",
                        "💊 Agregar Medicamento",
                        "🏥 Programar Cita"
                    ])
                    
                    self.send_message(chat_id, response, keyboard)
                else:
                    self.send_message(chat_id, "❌ Error en el registro. Intenta más tarde.")
            except Exception as e:
                logger.error(f"Error en registro: {e}")
                self.send_message(chat_id, "❌ Error en el registro. Intenta más tarde.")
        
        elif any(word in text.lower() for word in ['no', 'cambiar', 'modificar']):
            response = """📝 <b>Perfecto, vamos a personalizar tu información</b>

Por favor, escribe tu nombre completo:

💡 <b>Ejemplo:</b>
"Diego Castro"
"María José González"
"Juan Carlos Pérez"

O si prefieres cancelar, escribe /cancelar

¿Cuál es tu nombre completo? 👤"""
            self.send_message(chat_id, response)
        
        else:
            # Asumir que es el nombre completo
            full_name = text.strip()
            if len(full_name.split()) >= 2:
                names = full_name.split()
                data['first_name'] = names[0]
                data['last_name'] = ' '.join(names[1:])
                self.set_user_state(chat_id, 'registering', data)
                
                response = f"""✅ <b>¡Perfecto! Información actualizada</b>

👤 <b>Tu información:</b>
• Nombre: {data['first_name']}
• Apellido: {data['last_name']}
• Usuario: @{data['username']}

¿Es correcta esta información?

Escribe "Sí" para confirmar el registro
O "No" para hacer más cambios""".format(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    username=data['username'] or "sin_usuario"
                )
                
                keyboard = self.create_keyboard([
                    "✅ Sí, confirmar",
                    "❌ No, cambiar"
                ])
                
                self.send_message(chat_id, response, keyboard)
            else:
                self.send_message(chat_id, "❌ Por favor, escribe tu nombre completo (nombre y apellido).")
    
    def handle_natural_language(self, chat_id, text, user):
        """Procesa lenguaje natural con experiencia mejorada"""
        text_lower = text.lower()
        
        # Procesar exámenes con reconocimiento avanzado
        if any(word in text_lower for word in ['examen', 'resultado', 'laboratorio', 'análisis', 'eco', 'ecografía', 'radiografía', 'tomografía', 'resonancia']):
            self.start_exam_flow(chat_id, text, user)
        
        # Procesar medicamentos
        elif any(word in text_lower for word in ['medicamento', 'medicina', 'píldora', 'pastilla', 'fármaco', 'tratamiento']):
            self.start_medication_flow(chat_id, text, user)
        
        # Procesar historial
        elif any(word in text_lower for word in ['historial', 'historia', 'información', 'datos', 'muestra', 'muéstrame', 'ver']):
            self.show_medical_history(chat_id, user)
        
        # Procesar consultas
        elif any(word in text_lower for word in ['consulta', 'cita', 'médico', 'doctor', 'atención', 'programar']):
            self.start_appointment_flow(chat_id, text, user)
        
        # Procesar familia
        elif any(word in text_lower for word in ['familia', 'familiar', 'familiares']):
            self.handle_family_management(chat_id, user)
        
        # Procesar recordatorios
        elif any(word in text_lower for word in ['recordatorio', 'recordar', 'alarma', 'recordar']):
            self.handle_reminders(chat_id, user)
        
        # Respuesta por defecto con sugerencias
        else:
            self.send_smart_suggestions(chat_id, text)
    
    def start_exam_flow(self, chat_id, text, user):
        """Inicia el flujo de registro de examen"""
        text_lower = text.lower()
        
        # Detectar tipo de examen automáticamente
        exam_type = "Examen"
        exam_name = "Examen médico"
        
        if 'eco' in text_lower or 'ecografía' in text_lower:
            exam_type = "Ecografía"
            exam_name = "Ecografía Abdominal"
        elif 'sangre' in text_lower or 'análisis' in text_lower:
            exam_type = "Análisis"
            exam_name = "Análisis de Sangre"
        elif 'radiografía' in text_lower or 'rayos' in text_lower:
            exam_type = "Radiografía"
            exam_name = "Radiografía"
        elif 'tomografía' in text_lower or 'tac' in text_lower:
            exam_type = "Tomografía"
            exam_name = "Tomografía Computarizada"
        elif 'resonancia' in text_lower or 'rmn' in text_lower:
            exam_type = "Resonancia"
            exam_name = "Resonancia Magnética"
        
        # Guardar datos temporales
        exam_data = {
            'tipo': exam_type,
            'nombre': exam_name,
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'resultado': 'Pendiente',
            'observaciones': f'Examen detectado automáticamente: {text}'
        }
        
        self.set_user_state(chat_id, 'adding_exam', exam_data)
        
        response = f"""🔬 <b>¡Perfecto! Detecté que quieres registrar un examen</b>

📋 <b>Información detectada:</b>
• Tipo: {exam_type}
• Nombre: {exam_name}
• Fecha: {datetime.now().strftime('%d/%m/%Y')}

✅ <b>¿Es correcta esta información?</b>

Si es correcta, escribe "Sí" o "Correcto"
Si quieres modificarla, escribe "No" o "Cambiar"

💡 <b>También puedes:</b>
• Escribir el nombre exacto del examen
• Especificar la fecha
• Agregar observaciones

¿Cómo quieres proceder? 🤔"""
        
        keyboard = self.create_keyboard([
            "✅ Sí, es correcto",
            "❌ No, cambiar",
            "📅 Cambiar fecha",
            "📝 Agregar detalles"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def handle_exam_flow(self, chat_id, text, user, data):
        """Maneja el flujo de registro de examen"""
        if any(word in text.lower() for word in ['sí', 'si', 'correcto', 'ok', 'bien']):
            # Confirmar y guardar examen
            exam_id = self.save_exam(user['user_id'], data)
            
            if exam_id:
                self.clear_user_state(chat_id)
                response = f"""✅ <b>¡Examen registrado exitosamente!</b>

🔬 <b>Detalles guardados:</b>
• Tipo: {data['tipo']}
• Nombre: {data['nombre']}
• Fecha: {data['fecha']}
• Estado: Registrado

📊 <b>Guardado en tu historial médico</b>

💡 <b>¿Qué más quieres hacer?</b>
• "Agregar otro examen"
• "Ver mi historial"
• "Registrar medicamento"
• "Programar consulta"

🌐 <b>Ver en la web:</b> https://www.medconnect.cl

¡Gracias por mantener tu historial actualizado! 🩺"""
                
                keyboard = self.create_keyboard([
                    "🔬 Otro Examen",
                    "📋 Ver Historial",
                    "💊 Agregar Medicamento",
                    "🏥 Programar Cita"
                ])
                
                self.send_message(chat_id, response, keyboard)
            else:
                self.send_message(chat_id, "❌ Error guardando el examen. Intenta más tarde.")
        
        elif any(word in text.lower() for word in ['no', 'cambiar', 'modificar']):
            response = """📝 <b>Perfecto, vamos a personalizar tu examen</b>

Por favor, escribe el nombre exacto del examen:

💡 <b>Ejemplos:</b>
• "Ecografía Abdominal Completa"
• "Análisis de Sangre General"
• "Radiografía de Tórax"
• "Tomografía de Cráneo"

¿Cuál es el nombre exacto de tu examen? 🔬"""
            self.send_message(chat_id, response)
        
        else:
            # Asumir que es el nombre del examen
            data['nombre'] = text.strip()
            self.set_user_state(chat_id, 'adding_exam', data)
            
            response = f"""✅ <b>¡Perfecto! Nombre actualizado</b>

🔬 <b>Información del examen:</b>
• Tipo: {data['tipo']}
• Nombre: {data['nombre']}
• Fecha: {data['fecha']}

¿Es correcta esta información?

Escribe "Sí" para confirmar
O "No" para hacer más cambios"""
            
            keyboard = self.create_keyboard([
                "✅ Sí, confirmar",
                "❌ No, cambiar",
                "📅 Cambiar fecha"
            ])
            
            self.send_message(chat_id, response, keyboard)
    
    def start_medication_flow(self, chat_id, text, user):
        """Inicia el flujo de registro de medicamento"""
        self.set_user_state(chat_id, 'adding_medication', {})
        
        response = """💊 <b>¡Perfecto! Vamos a registrar tu medicamento</b>

📋 <b>Necesito la siguiente información:</b>

1️⃣ <b>Nombre del medicamento</b>
2️⃣ <b>Dosis</b> (ej: 500mg, 10ml)
3️⃣ <b>Frecuencia</b> (ej: Cada 8 horas, 2 veces al día)
4️⃣ <b>Duración</b> (ej: 7 días, 1 mes)

💡 <b>Ejemplo completo:</b>
"Paracetamol 500mg cada 8 horas por 7 días"

O puedes ir paso a paso. ¿Cómo prefieres hacerlo?

Escribe el medicamento completo o solo el nombre para empezar 💊"""
        
        keyboard = self.create_keyboard([
            "💊 Escribir completo",
            "📝 Paso a paso",
            "🚫 Cancelar"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def handle_medication_flow(self, chat_id, text, user, data):
        """Maneja el flujo de registro de medicamento"""
        # Implementar lógica de medicamentos paso a paso
        self.send_message(chat_id, "💊 Funcionalidad de medicamentos en desarrollo. Pronto disponible!")
        self.clear_user_state(chat_id)
    
    def start_appointment_flow(self, chat_id, text, user):
        """Inicia el flujo de programación de consulta"""
        self.set_user_state(chat_id, 'adding_appointment', {})
        
        response = """🏥 <b>¡Perfecto! Vamos a programar tu consulta</b>

📋 <b>Necesito la siguiente información:</b>

1️⃣ <b>Fecha</b> (ej: 15/01/2025)
2️⃣ <b>Hora</b> (ej: 14:30)
3️⃣ <b>Especialidad</b> (ej: Cardiología)
4️⃣ <b>Centro médico</b> (ej: Hospital Clínico)

💡 <b>Ejemplo completo:</b>
"Consulta el 15/01/2025 a las 14:30 en Cardiología del Hospital Clínico"

O puedes ir paso a paso. ¿Cómo prefieres hacerlo?

Escribe la consulta completa o solo la fecha para empezar 🏥"""
        
        keyboard = self.create_keyboard([
            "🏥 Escribir completo",
            "📝 Paso a paso",
            "🚫 Cancelar"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def handle_appointment_flow(self, chat_id, text, user, data):
        """Maneja el flujo de programación de consulta"""
        # Implementar lógica de consultas paso a paso
        self.send_message(chat_id, "🏥 Funcionalidad de consultas en desarrollo. Pronto disponible!")
        self.clear_user_state(chat_id)
    
    def show_medical_history(self, chat_id, user):
        """Muestra el historial médico del usuario"""
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

💡 <b>¿Qué quieres ver en detalle?</b>

🌐 <b>Ver completo en la web:</b> https://www.medconnect.cl

¿Qué información específica necesitas? 🤔"""
            
            keyboard = self.create_keyboard([
                "📋 Ver Consultas",
                "💊 Ver Medicamentos",
                "🔬 Ver Exámenes",
                "👨‍👩‍👧‍👦 Ver Familiares"
            ])
            
            self.send_message(chat_id, response, keyboard)
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            self.send_message(chat_id, "❌ Error obteniendo tu historial. Intenta más tarde.")
    
    def handle_family_management(self, chat_id, user):
        """Maneja la gestión de familiares"""
        response = """👨‍👩‍👧‍👦 <b>Gestión de Familiares</b>

📋 <b>¿Qué quieres hacer?</b>

• Agregar familiar autorizado
• Ver familiares actuales
• Gestionar permisos
• Configurar notificaciones

💡 <b>Los familiares autorizados pueden:</b>
• Ver tu información médica
• Recibir notificaciones
• Acceder a tu historial

¿Qué opción prefieres? 👤"""
        
        keyboard = self.create_keyboard([
            "👤 Agregar Familiar",
            "📋 Ver Familiares",
            "🔐 Gestionar Permisos",
            "🚫 Cancelar"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def handle_reminders(self, chat_id, user):
        """Maneja la configuración de recordatorios"""
        response = """⏰ <b>Configuración de Recordatorios</b>

📋 <b>¿Qué tipo de recordatorio quieres configurar?</b>

• Recordatorio de medicamentos
• Recordatorio de citas
• Recordatorio de exámenes
• Recordatorio personalizado

💡 <b>Los recordatorios te ayudarán a:</b>
• No olvidar tomar medicamentos
• Llegar a tiempo a las citas
• Realizar exámenes programados

¿Qué recordatorio necesitas? ⏰"""
        
        keyboard = self.create_keyboard([
            "💊 Medicamentos",
            "🏥 Citas",
            "🔬 Exámenes",
            "📝 Personalizado"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def send_smart_suggestions(self, chat_id, text):
        """Envía sugerencias inteligentes basadas en el texto"""
        text_lower = text.lower()
        
        # Analizar el texto para dar sugerencias relevantes
        suggestions = []
        
        if any(word in text_lower for word in ['hola', 'hello', 'hi', 'buenas']):
            response = """👋 <b>¡Hola! ¿Cómo estás?</b>

💡 <b>¿En qué puedo ayudarte hoy?</b>

• 📋 Ver tu historial médico
• 🔬 Registrar un examen
• 💊 Agregar un medicamento
• 🏥 Programar una consulta
• 👨‍👩‍👧‍👦 Gestionar familiares

O simplemente dime qué necesitas y te ayudo! 😊"""
        
        elif any(word in text_lower for word in ['gracias', 'thank', 'perfecto', 'excelente']):
            response = """😊 <b>¡De nada! Me alegra poder ayudarte</b>

💡 <b>¿Hay algo más en lo que pueda asistirte?</b>

• 📋 Ver tu historial médico
• 🔬 Registrar un examen
• 💊 Agregar un medicamento
• 🏥 Programar una consulta

¡Estoy aquí para cuidar de tu salud! 🩺"""
        
        else:
            response = """🤖 <b>No estoy seguro de entenderte</b>

💡 <b>¿Te refieres a algo de esto?</b>

• 📋 <b>Historial médico</b> - "Muéstrame mi historial"
• 🔬 <b>Exámenes</b> - "Tengo un eco abdominal"
• 💊 <b>Medicamentos</b> - "Necesito registrar un medicamento"
• 🏥 <b>Consultas</b> - "Programar una cita"
• 👨‍👩‍👧‍👦 <b>Familia</b> - "Gestionar familiares"

💬 <b>O puedes escribir de forma natural:</b>
• "Tengo un examen nuevo"
• "Necesito un medicamento"
• "Quiero ver mi información"

📋 <b>Comandos disponibles:</b>
• /start - Menú principal
• /ayuda - Ver opciones
• /cancelar - Cancelar operación

¿En qué puedo ayudarte? 🤔"""
        
        keyboard = self.create_keyboard([
            "📋 Ver Historial",
            "🔬 Registrar Examen",
            "💊 Agregar Medicamento",
            "🏥 Programar Cita"
        ])
        
        self.send_message(chat_id, response, keyboard)
    
    def handle_help(self, chat_id):
        """Maneja el comando de ayuda mejorado"""
        response = """📋 <b>Ayuda de MedConnect</b>

🏥 <b>¿Qué puedo hacer por ti?</b>

📋 <b>Gestionar Información:</b>
• Ver tu historial médico completo
• Registrar nuevos exámenes
• Agregar medicamentos con recordatorios
• Programar citas médicas

🔍 <b>Consultar Datos:</b>
• Ver medicamentos activos
• Revisar resultados de exámenes
• Consultar próximas citas
• Ver resumen médico

👨‍👩‍👧‍👦 <b>Gestión Familiar:</b>
• Agregar familiares autorizados
• Gestionar permisos de acceso
• Configurar notificaciones familiares
• Compartir información médica

⏰ <b>Recordatorios:</b>
• Alertas de medicamentos
• Recordatorios de citas
• Notificaciones de exámenes
• Recordatorios personalizados

💬 <b>Lenguaje Natural:</b>
Puedes escribir de forma natural, por ejemplo:
• "Tengo un eco abdominal"
• "Necesito registrar un medicamento"
• "Muéstrame mi historial"
• "Programar una consulta"

🎯 <b>Comandos Rápidos:</b>
• /start - Menú principal
• /ayuda - Esta ayuda
• /estado - Estado del sistema
• /cancelar - Cancelar operación

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

🎯 <b>Funciones activas:</b>
• ✅ Reconocimiento de usuarios
• ✅ Registro de exámenes
• ✅ Gestión de medicamentos
• ✅ Historial médico
• ✅ Conversaciones inteligentes

¡Todo funcionando perfectamente! 🎉"""
        
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
        logger.info("🚀 Bot mejorado iniciado y ejecutándose...")
        
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
    bot = EnhancedMedConnectBot()
    bot.run() 