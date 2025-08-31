#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de autenticación local con SQLite
Reemplaza el sistema temporal con almacenamiento real de usuarios
"""

import sqlite3
import hashlib
import os
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LocalAuthSystem:
    def __init__(self, db_path="medconnect_users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar la base de datos SQLite con las tablas necesarias"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    tipo_usuario TEXT NOT NULL CHECK (tipo_usuario IN ('paciente', 'profesional')),
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT 1,
                    telefono TEXT,
                    direccion TEXT,
                    fecha_nacimiento DATE,
                    especialidad TEXT,
                    numero_colegiado TEXT,
                    hospital TEXT,
                    datos_adicionales TEXT
                )
            ''')
            
            # Tabla de sesiones de pacientes (historial médico básico)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sesiones_paciente (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    fecha_sesion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    motivo_consulta TEXT,
                    diagnostico TEXT,
                    tratamiento TEXT,
                    notas TEXT,
                    profesional_id INTEGER,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                    FOREIGN KEY (profesional_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de citas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS citas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paciente_id INTEGER,
                    profesional_id INTEGER,
                    fecha_cita DATETIME,
                    estado TEXT DEFAULT 'programada',
                    motivo TEXT,
                    notas TEXT,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (paciente_id) REFERENCES usuarios (id),
                    FOREIGN KEY (profesional_id) REFERENCES usuarios (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Base de datos local inicializada correctamente")
            
            # Crear usuarios de ejemplo si no existen
            self.create_sample_users()
            
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
    
    def hash_password(self, password):
        """Crear hash seguro de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_sample_users(self):
        """Crear usuarios de ejemplo para pruebas"""
        sample_users = [
            {
                'email': 'admin@test.com',
                'password': 'admin123',
                'nombre': 'Dr. Juan',
                'apellido': 'Pérez',
                'tipo_usuario': 'profesional',
                'especialidad': 'Medicina General',
                'numero_colegiado': 'MED-001',
                'hospital': 'Hospital Central'
            },
            {
                'email': 'doctor@medconnect.com',
                'password': 'doctor123',
                'nombre': 'Dra. María',
                'apellido': 'González',
                'tipo_usuario': 'profesional',
                'especialidad': 'Cardiología',
                'numero_colegiado': 'CARD-002',
                'hospital': 'Clínica Cardiovascular'
            },
            {
                'email': 'user@test.com',
                'password': 'user123',
                'nombre': 'Ana',
                'apellido': 'López',
                'tipo_usuario': 'paciente',
                'telefono': '+1234567890',
                'direccion': 'Calle Principal 123',
                'fecha_nacimiento': '1985-05-15'
            },
            {
                'email': 'paciente@medconnect.com',
                'password': 'paciente123',
                'nombre': 'Carlos',
                'apellido': 'Rodríguez',
                'tipo_usuario': 'paciente',
                'telefono': '+0987654321',
                'direccion': 'Avenida Central 456',
                'fecha_nacimiento': '1990-08-22'
            }
        ]
        
        for user_data in sample_users:
            if not self.user_exists(user_data['email']):
                self.register_user(user_data)
                logger.info(f"✅ Usuario de ejemplo creado: {user_data['email']}")
    
    def user_exists(self, email):
        """Verificar si un usuario ya existe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
            
        except Exception as e:
            logger.error(f"❌ Error verificando usuario: {e}")
            return False
    
    def register_user(self, user_data):
        """Registrar un nuevo usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Validar datos requeridos
            required_fields = ['email', 'password', 'nombre', 'apellido', 'tipo_usuario']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    return {'success': False, 'message': f'Campo requerido: {field}'}
            
            # Verificar si el usuario ya existe
            if self.user_exists(user_data['email']):
                return {'success': False, 'message': 'El email ya está registrado'}
            
            # Hash de la contraseña
            password_hash = self.hash_password(user_data['password'])
            
            # Insertar usuario
            cursor.execute('''
                INSERT INTO usuarios (
                    email, password_hash, nombre, apellido, tipo_usuario,
                    telefono, direccion, fecha_nacimiento, especialidad,
                    numero_colegiado, hospital, datos_adicionales
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data['email'],
                password_hash,
                user_data['nombre'],
                user_data['apellido'],
                user_data['tipo_usuario'],
                user_data.get('telefono'),
                user_data.get('direccion'),
                user_data.get('fecha_nacimiento'),
                user_data.get('especialidad'),
                user_data.get('numero_colegiado'),
                user_data.get('hospital'),
                json.dumps(user_data.get('datos_adicionales', {}))
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Usuario registrado: {user_data['email']} (ID: {user_id})")
            return {'success': True, 'user_id': user_id, 'message': 'Usuario registrado exitosamente'}
            
        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return {'success': False, 'message': f'Error en el registro: {str(e)}'}
    
    def authenticate_user(self, email, password):
        """Autenticar usuario con email y contraseña"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                SELECT id, email, nombre, apellido, tipo_usuario, telefono, direccion,
                       fecha_nacimiento, especialidad, numero_colegiado, hospital,
                       datos_adicionales, activo
                FROM usuarios 
                WHERE email = ? AND password_hash = ? AND activo = 1
            ''', (email, password_hash))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                user_data = {
                    'id': result[0],
                    'email': result[1],
                    'nombre': result[2],
                    'apellido': result[3],
                    'tipo_usuario': result[4],
                    'telefono': result[5],
                    'direccion': result[6],
                    'fecha_nacimiento': result[7],
                    'especialidad': result[8],
                    'numero_colegiado': result[9],
                    'hospital': result[10],
                    'datos_adicionales': json.loads(result[11] or '{}'),
                    'activo': result[12]
                }
                
                logger.info(f"✅ Login exitoso: {email} (ID: {user_data['id']})")
                return {'success': True, 'user': user_data}
            else:
                logger.warning(f"❌ Login fallido: {email}")
                return {'success': False, 'message': 'Email o contraseña incorrectos'}
                
        except Exception as e:
            logger.error(f"❌ Error autenticando usuario: {e}")
            return {'success': False, 'message': f'Error de autenticación: {str(e)}'}
    
    def get_user_by_id(self, user_id):
        """Obtener datos completos de un usuario por ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, nombre, apellido, tipo_usuario, telefono, direccion,
                       fecha_nacimiento, especialidad, numero_colegiado, hospital,
                       datos_adicionales, fecha_registro, activo
                FROM usuarios 
                WHERE id = ? AND activo = 1
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'email': result[1],
                    'nombre': result[2],
                    'apellido': result[3],
                    'tipo_usuario': result[4],
                    'telefono': result[5],
                    'direccion': result[6],
                    'fecha_nacimiento': result[7],
                    'especialidad': result[8],
                    'numero_colegiado': result[9],
                    'hospital': result[10],
                    'datos_adicionales': json.loads(result[11] or '{}'),
                    'fecha_registro': result[12],
                    'activo': result[13]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario: {e}")
            return None
    
    def get_patient_sessions(self, patient_id):
        """Obtener historial de sesiones de un paciente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.id, s.fecha_sesion, s.motivo_consulta, s.diagnostico,
                       s.tratamiento, s.notas, u.nombre, u.apellido, u.especialidad
                FROM sesiones_paciente s
                LEFT JOIN usuarios u ON s.profesional_id = u.id
                WHERE s.usuario_id = ?
                ORDER BY s.fecha_sesion DESC
            ''', (patient_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in results:
                sessions.append({
                    'id': row[0],
                    'fecha_sesion': row[1],
                    'motivo_consulta': row[2],
                    'diagnostico': row[3],
                    'tratamiento': row[4],
                    'notas': row[5],
                    'profesional_nombre': f"{row[6] or ''} {row[7] or ''}".strip(),
                    'profesional_especialidad': row[8]
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo sesiones del paciente: {e}")
            return []
    
    def get_professional_patients(self, professional_id):
        """Obtener lista de pacientes de un profesional"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT u.id, u.nombre, u.apellido, u.email, u.telefono,
                       MAX(s.fecha_sesion) as ultima_sesion
                FROM usuarios u
                JOIN sesiones_paciente s ON u.id = s.usuario_id
                WHERE s.profesional_id = ? AND u.activo = 1
                GROUP BY u.id, u.nombre, u.apellido, u.email, u.telefono
                ORDER BY ultima_sesion DESC
            ''', (professional_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            patients = []
            for row in results:
                patients.append({
                    'id': row[0],
                    'nombre': row[1],
                    'apellido': row[2],
                    'email': row[3],
                    'telefono': row[4],
                    'ultima_sesion': row[5]
                })
            
            return patients
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pacientes del profesional: {e}")
            return []
    
    def add_patient_session(self, session_data):
        """Agregar una nueva sesión para un paciente"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sesiones_paciente (
                    usuario_id, motivo_consulta, diagnostico, tratamiento,
                    notas, profesional_id
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session_data['usuario_id'],
                session_data.get('motivo_consulta'),
                session_data.get('diagnostico'),
                session_data.get('tratamiento'),
                session_data.get('notas'),
                session_data.get('profesional_id')
            ))
            
            session_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Sesión agregada: ID {session_id}")
            return {'success': True, 'session_id': session_id}
            
        except Exception as e:
            logger.error(f"❌ Error agregando sesión: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_all_professionals(self):
        """Obtener lista de todos los profesionales activos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nombre, apellido, especialidad, hospital, email
                FROM usuarios 
                WHERE tipo_usuario = 'profesional' AND activo = 1
                ORDER BY nombre, apellido
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            professionals = []
            for row in results:
                professionals.append({
                    'id': row[0],
                    'nombre': row[1],
                    'apellido': row[2],
                    'especialidad': row[3],
                    'hospital': row[4],
                    'email': row[5]
                })
            
            return professionals
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo profesionales: {e}")
            return []

# Instancia global del sistema de autenticación local
local_auth = LocalAuthSystem() 