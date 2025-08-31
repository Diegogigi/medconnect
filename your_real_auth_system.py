#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de autenticación con tus usuarios reales
"""

import sqlite3
import bcrypt
import logging

logger = logging.getLogger(__name__)

class YourRealAuthSystem:
    def __init__(self):
        self.db_path = "your_real_users.db"
        self.table_name = "usuarios"
        print("✅ Sistema de autenticación inicializado con tus usuarios reales")
    
    def authenticate_user(self, email, password):
        """Autenticar usuario con bcrypt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, password_hash, nombre, apellido, telefono, 
                       fecha_nacimiento, genero, direccion, ciudad, tipo_usuario, estado
                FROM usuarios WHERE email = ? AND estado = 'activo'
            """, (email,))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return {'success': False, 'message': 'Usuario no encontrado'}
            
            stored_hash = result[2]
            
            # Verificar contraseña con bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                user_data = {
                    'id': result[0],
                    'email': result[1],
                    'nombre': result[3],
                    'apellido': result[4],
                    'telefono': result[5],
                    'fecha_nacimiento': result[6],
                    'genero': result[7],
                    'direccion': result[8],
                    'ciudad': result[9],
                    'tipo_usuario': result[10],
                    'estado': result[11]
                }
                
                # Actualizar último acceso
                cursor.execute("UPDATE usuarios SET ultimo_acceso = datetime('now') WHERE id = ?", 
                             (user_data['id'],))
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Login exitoso: {email} ({user_data['nombre']} {user_data['apellido']})")
                return {'success': True, 'user': user_data}
            else:
                conn.close()
                return {'success': False, 'message': 'Email o contraseña incorrectos'}
                
        except Exception as e:
            logger.error(f"❌ Error autenticando: {e}")
            return {'success': False, 'message': f'Error de autenticación: {str(e)}'}
    
    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, email, nombre, apellido, telefono, fecha_nacimiento,
                       genero, direccion, ciudad, tipo_usuario, estado, fecha_registro
                FROM usuarios WHERE id = ? AND estado = 'activo'
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'email': result[1],
                    'nombre': result[2],
                    'apellido': result[3],
                    'telefono': result[4],
                    'fecha_nacimiento': result[5],
                    'genero': result[6],
                    'direccion': result[7],
                    'ciudad': result[8],
                    'tipo_usuario': result[9],
                    'estado': result[10],
                    'fecha_registro': result[11]
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario: {e}")
            return None
    
    def register_user(self, user_data):
        """Registrar nuevo usuario"""
        try:
            if not user_data.get('email') or not user_data.get('password'):
                return {'success': False, 'message': 'Email y contraseña son requeridos'}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si usuario existe
            cursor.execute("SELECT id FROM usuarios WHERE email = ?", (user_data['email'],))
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'message': 'El email ya está registrado'}
            
            # Hash de contraseña
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO usuarios (
                    email, password_hash, nombre, apellido, telefono, fecha_nacimiento,
                    genero, direccion, ciudad, tipo_usuario, estado
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo')
            """, (
                user_data['email'],
                password_hash,
                user_data.get('nombre', ''),
                user_data.get('apellido', ''),
                user_data.get('telefono'),
                user_data.get('fecha_nacimiento'),
                user_data.get('genero'),
                user_data.get('direccion'),
                user_data.get('ciudad'),
                user_data.get('tipo_usuario', 'paciente')
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Usuario registrado: {user_data['email']}")
            return {'success': True, 'user_id': user_id, 'message': 'Usuario registrado exitosamente'}
            
        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return {'success': False, 'message': f'Error en registro: {str(e)}'}

# Instancia global
your_real_auth = YourRealAuthSystem()
