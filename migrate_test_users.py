#!/usr/bin/env python3
"""
Script para migrar usuarios de prueba a PostgreSQL en Railway
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt

def migrate_test_users():
    """Migra usuarios de prueba a PostgreSQL"""
    
    print("🔄 Migrando usuarios de prueba a PostgreSQL...")
    print("=" * 50)
    
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL no configurada")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Usuarios de prueba
        test_users = [
            {
                "email": "diego.castro.lagos@gmail.com",
                "password": "password123",
                "nombre": "Diego",
                "apellido": "Castro",
                "tipo_usuario": "profesional",
                "telefono": "+56912345678",
                "especialidad": "Medicina General"
            },
            {
                "email": "rodrigoandressilvabreve@gmail.com",
                "password": "password123",
                "nombre": "Rodrigo",
                "apellido": "Silva",
                "tipo_usuario": "paciente",
                "telefono": "+56987654321",
                "especialidad": None
            }
        ]
        
        for user in test_users:
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (user["email"],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"⚠️ Usuario {user['email']} ya existe")
                continue
            
            # Hash de la contraseña
            password_hash = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insertar usuario
            cursor.execute("""
                INSERT INTO usuarios (
                    email, password_hash, nombre, apellido, tipo_usuario,
                    telefono, especialidad, activo, fecha_creacion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
            """, (
                user["email"], password_hash, user["nombre"], user["apellido"],
                user["tipo_usuario"], user["telefono"], user["especialidad"], True
            ))
            
            print(f"✅ Usuario {user['email']} creado")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 Migración de usuarios completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        return False

if __name__ == "__main__":
    migrate_test_users()
