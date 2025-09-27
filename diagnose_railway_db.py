#!/usr/bin/env python3
"""
Script de diagnóstico para Railway PostgreSQL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def diagnose_railway_database():
    """Diagnostica la conexión y estructura de la base de datos"""
    
    print("🔍 Diagnóstico de Railway PostgreSQL...")
    print("=" * 60)
    
    # Variables de conexión a Railway
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    
    print(f"🔗 Conectando a Railway PostgreSQL...")
    print(f"   URL: {database_url[:50]}...")
    
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión a PostgreSQL exitosa")
        
        # 1. Verificar versión de PostgreSQL
        print(f"\n1️⃣ Verificando versión de PostgreSQL...")
        try:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            if result:
                version = result[0]
                print(f"   ✅ Versión: {version[:100]}...")
            else:
                print(f"   ⚠️ No se pudo obtener la versión")
        except Exception as e:
            print(f"   ❌ Error obteniendo versión: {e}")
        
        # 2. Verificar tablas existentes
        print(f"\n2️⃣ Verificando tablas existentes...")
        try:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"   📋 Tablas encontradas: {len(tables)}")
            for table in tables:
                print(f"     - {table['table_name']}")
        except Exception as e:
            print(f"   ❌ Error obteniendo tablas: {e}")
        
        # 3. Verificar tabla usuarios
        print(f"\n3️⃣ Verificando tabla usuarios...")
        try:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'usuarios'
                );
            """)
            result = cursor.fetchone()
            usuarios_exists = result[0] if result else False
            print(f"   📋 Tabla usuarios existe: {usuarios_exists}")
            
            if usuarios_exists:
                # Verificar columnas de usuarios
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'usuarios'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                print(f"   📋 Columnas en usuarios: {len(columns)}")
                for col in columns:
                    print(f"     - {col['column_name']} ({col['data_type']})")
                
                # Verificar usuarios existentes
                cursor.execute("""
                    SELECT id, email, nombre, apellido, tipo_usuario, activo
                    FROM usuarios 
                    ORDER BY tipo_usuario, apellido, nombre;
                """)
                users = cursor.fetchall()
                print(f"   👥 Usuarios encontrados: {len(users)}")
                for user in users:
                    status = "✅" if user['activo'] else "❌"
                    print(f"     {status} {user['nombre']} {user['apellido']} ({user['tipo_usuario']}) - {user['email']}")
        except Exception as e:
            print(f"   ❌ Error verificando tabla usuarios: {e}")
        
        # 4. Verificar tabla pacientes_profesional
        print(f"\n4️⃣ Verificando tabla pacientes_profesional...")
        try:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'pacientes_profesional'
                );
            """)
            result = cursor.fetchone()
            pp_exists = result[0] if result else False
            print(f"   📋 Tabla pacientes_profesional existe: {pp_exists}")
            
            if pp_exists:
                # Verificar columnas de pacientes_profesional
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'pacientes_profesional'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                print(f"   📋 Columnas en pacientes_profesional: {len(columns)}")
                for col in columns:
                    print(f"     - {col['column_name']} ({col['data_type']})")
                
                # Verificar relaciones existentes
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM pacientes_profesional;
                """)
                result = cursor.fetchone()
                total = result['total'] if result else 0
                print(f"   🔗 Relaciones existentes: {total}")
        except Exception as e:
            print(f"   ❌ Error verificando tabla pacientes_profesional: {e}")
        
        # 5. Verificar permisos
        print(f"\n5️⃣ Verificando permisos...")
        try:
            cursor.execute("""
                SELECT current_user, session_user;
            """)
            user_info = cursor.fetchone()
            print(f"   👤 Usuario actual: {user_info['current_user']}")
            print(f"   👤 Usuario de sesión: {user_info['session_user']}")
        except Exception as e:
            print(f"   ❌ Error verificando permisos: {e}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Diagnóstico completado exitosamente")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión a PostgreSQL: {e}")
        return False
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO RAILWAY DATABASE")
    print("=" * 60)
    
    success = diagnose_railway_database()
    
    if success:
        print(f"\n🎉 ¡Diagnóstico exitoso!")
    else:
        print(f"\n❌ Error en el diagnóstico")
        sys.exit(1)
