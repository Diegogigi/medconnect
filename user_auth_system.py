#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de autenticación para base de datos existente con usuarios reales
Adaptado para la estructura específica del usuario
"""

import sqlite3
import bcrypt
import os
import logging
import glob

logger = logging.getLogger(__name__)

class UserAuthSystem:
    def __init__(self):
        self.db_path = None
        self.table_name = None
        self.columns = []
        self.initialize()
    
    def initialize(self):
        """Inicializar y encontrar la base de datos automáticamente"""
        try:
            # Buscar base de datos existente
            db_info = self.find_user_database()
            if db_info:
                self.db_path = db_info['db_file']
                self.table_name = db_info['table_name']
                self.columns = db_info['columns']
                logger.info(f"✅ Sistema inicializado con {self.db_path} - tabla {self.table_name}")
                print(f"✅ Sistema de autenticación inicializado con {self.db_path}")
            else:
                # Usar base de datos por defecto
                self.db_path = "medconnect_users.db"
                self.table_name = "usuarios"
                self.create_default_table()
                logger.info("✅ Sistema inicializado con base de datos por defecto")
                print("✅ Sistema inicializado con base de datos por defecto")
        except Exception as e:
            logger.error(f"❌ Error inicializando sistema: {e}")
            print(f"❌ Error inicializando sistema: {e}")
    
    def find_user_database(self):
        """Buscar base de datos de usuarios existente"""
        # Buscar archivos de base de datos
        db_files = []
        
        # Patrones de búsqueda
        patterns = ["*.db", "*.sqlite", "*.sqlite3"]
        
        for pattern in patterns:
            files = glob.glob(pattern, recursive=False)
            db_files.extend(files)
        
        print(f"📊 Archivos de base de datos encontrados: {db_files}")
        
        # Analizar cada base de datos
        for db_file in db_files:
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Obtener lista de tablas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [t[0] for t in cursor.fetchall()]
                
                print(f"🔍 Analizando {db_file} - Tablas: {tables}")
                
                # Buscar tabla que pueda contener usuarios
                for table in tables:
                    if any(keyword in table.lower() for keyword in ['user', 'usuario', 'auth']):
                        # Verificar estructura
                        cursor.execute(f"PRAGMA table_info({table});")
                        columns_info = cursor.fetchall()
                        column_names = [col[1] for col in columns_info]
                        
                        print(f"📋 Estructura de {table}: {column_names}")
                        
                        # Verificar si tiene campos típicos de usuarios
                        has_email = any('email' in col.lower() for col in column_names)
                        has_password = any(keyword in ' '.join(column_names).lower() 
                                         for keyword in ['password', 'hash'])
                        
                        if has_email and has_password:
                            # Contar registros
                            cursor.execute(f"SELECT COUNT(*) FROM {table};")
                            count = cursor.fetchone()[0]
                            
                            print(f"✅ ¡Tabla de usuarios encontrada en {db_file}! {count} registros")
                            
                            conn.close()
                            return {
                                'db_file': db_file,
                                'table_name': table,
                                'columns': column_names,
                                'count': count
                            }
                
                conn.close()
                
            except Exception as e:
                print(f"❌ Error analizando {db_file}: {e}")
        
        return None
    
    def create_default_table(self):
        """Crear tabla por defecto si no existe"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    tipo_usuario TEXT DEFAULT 'paciente',
                    telefono TEXT,
                    direccion TEXT,
                    ciudad TEXT,
                    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                    estado TEXT DEFAULT 'activo'
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.columns = ['id', 'email', 'password_hash', 'nombre', 'apellido', 
                          'tipo_usuario', 'telefono', 'direccion', 'ciudad', 
                          'fecha_registro', 'estado']
            
        except Exception as e:
            logger.error(f"❌ Error creando tabla por defecto: {e}")
    
    def authenticate_user(self, email, password):
        """Autenticar usuario con soporte para bcrypt"""
        if not self.db_path or not self.table_name:
            return {'success': False, 'message': 'Sistema no inicializado'}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query adaptado a diferentes estructuras de tabla
            # Primero intentar con los campos que mencionaste
            possible_queries = [
                # Para tu estructura específica
                f"""SELECT id, email, password_hash, nombre, apellido, telefono, 
                          fecha_nacimiento, genero, direccion, ciudad, tipo_usuario, estado
                   FROM {self.table_name} WHERE email = ? AND estado = 'activo'""",
                
                # Para estructura simplificada
                f"""SELECT id, email, password_hash, nombre, apellido, tipo_usuario
                   FROM {self.table_name} WHERE email = ?""",
                
                # Para cualquier estructura con campos básicos
                f"""SELECT * FROM {self.table_name} WHERE email = ?"""
            ]
            
            result = None
            used_query = None
            
            for query in possible_queries:
                try:
                    cursor.execute(query, (email,))
                    result = cursor.fetchone()
                    if result:
                        used_query = query
                        break
                except sqlite3.OperationalError:
                    continue
            
            if not result:
                conn.close()
                return {'success': False, 'message': 'Usuario no encontrado'}
            
            # El hash de contraseña debería estar en la posición 2 (índice 2)
            stored_hash = result[2] if len(result) > 2 else None
            
            if not stored_hash:
                conn.close()
                return {'success': False, 'message': 'Error en datos de usuario'}
            
            # Verificar contraseña con bcrypt
            password_valid = False
            
            try:
                if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
                    password_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
                else:
                    # Fallback para otros tipos de hash
                    import hashlib
                    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
                    password_valid = (stored_hash == sha256_hash) or (stored_hash == password)
            except Exception as e:
                logger.error(f"Error verificando contraseña: {e}")
                conn.close()
                return {'success': False, 'message': 'Error verificando contraseña'}
            
            if password_valid:
                # Construir datos del usuario basado en los resultados
                user_data = {
                    'id': result[0],
                    'email': result[1],
                    'nombre': result[3] if len(result) > 3 else 'Usuario',
                    'apellido': result[4] if len(result) > 4 else 'Desconocido',
                    'telefono': result[5] if len(result) > 5 else None,
                    'fecha_nacimiento': result[6] if len(result) > 6 else None,
                    'genero': result[7] if len(result) > 7 else None,
                    'direccion': result[8] if len(result) > 8 else None,
                    'ciudad': result[9] if len(result) > 9 else None,
                    'tipo_usuario': result[10] if len(result) > 10 else 'paciente',
                    'estado': result[11] if len(result) > 11 else 'activo'
                }
                
                # Actualizar último acceso si es posible
                try:
                    cursor.execute(f"UPDATE {self.table_name} SET ultimo_acceso = datetime('now') WHERE id = ?", 
                                 (user_data['id'],))
                    conn.commit()
                except:
                    pass  # No importa si no existe la columna ultimo_acceso
                
                conn.close()
                
                logger.info(f"✅ Login exitoso: {email} (ID: {user_data['id']})")
                return {'success': True, 'user': user_data}
            else:
                conn.close()
                return {'success': False, 'message': 'Email o contraseña incorrectos'}
                
        except Exception as e:
            logger.error(f"❌ Error autenticando: {e}")
            return {'success': False, 'message': f'Error de autenticación: {str(e)}'}
    
    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        if not self.db_path or not self.table_name:
            return None
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result and len(result) >= 5:  # Al menos id, email, hash, nombre, apellido
                user_data = {
                    'id': result[0],
                    'email': result[1],
                    'nombre': result[3],
                    'apellido': result[4],
                    'telefono': result[5] if len(result) > 5 else None,
                    'fecha_nacimiento': result[6] if len(result) > 6 else None,
                    'genero': result[7] if len(result) > 7 else None,
                    'direccion': result[8] if len(result) > 8 else None,
                    'ciudad': result[9] if len(result) > 9 else None,
                    'tipo_usuario': result[10] if len(result) > 10 else 'paciente',
                    'estado': result[11] if len(result) > 11 else 'activo'
                }
                
                conn.close()
                return user_data
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario: {e}")
            return None
    
    def register_user(self, user_data):
        """Registrar nuevo usuario con bcrypt"""
        if not self.db_path or not self.table_name:
            return {'success': False, 'message': 'Sistema no inicializado'}
        
        try:
            # Validar campos requeridos
            if not user_data.get('email') or not user_data.get('password'):
                return {'success': False, 'message': 'Email y contraseña son requeridos'}
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si usuario existe
            cursor.execute(f"SELECT id FROM {self.table_name} WHERE email = ?", (user_data['email'],))
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'message': 'El email ya está registrado'}
            
            # Hash de contraseña con bcrypt
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Intentar inserción con estructura completa
            try:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} (
                        email, password_hash, nombre, apellido, telefono, fecha_nacimiento,
                        genero, direccion, ciudad, tipo_usuario, estado, verificado
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'activo', 0)
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
            except sqlite3.OperationalError:
                # Fallback con estructura básica
                cursor.execute(f"""
                    INSERT INTO {self.table_name} (
                        email, password_hash, nombre, apellido, tipo_usuario
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    user_data['email'],
                    password_hash,
                    user_data.get('nombre', ''),
                    user_data.get('apellido', ''),
                    user_data.get('tipo_usuario', 'paciente')
                ))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Usuario registrado: {user_data['email']} (ID: {user_id})")
            return {'success': True, 'user_id': user_id, 'message': 'Usuario registrado exitosamente'}
            
        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return {'success': False, 'message': f'Error en registro: {str(e)}'}

# Instancia global
user_auth = UserAuthSystem() 