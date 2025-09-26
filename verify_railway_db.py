#!/usr/bin/env python3
"""
Script para verificar la conexión a PostgreSQL en Railway
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def verify_railway_database():
    """Verifica la conexión a PostgreSQL en Railway"""
    
    print("🔍 Verificando conexión a PostgreSQL en Railway...")
    print("=" * 50)
    
    # Obtener DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL no configurada")
        print("🔧 Configura DATABASE_URL en Railway Dashboard")
        return False
    
    print(f"✅ DATABASE_URL encontrada: {database_url[:50]}...")
    
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión a PostgreSQL exitosa")
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cursor.fetchall()
        print(f"📋 Tablas encontradas: {len(tables)}")
        
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Verificar tabla de usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        user_count = cursor.fetchone()['count']
        print(f"👥 Usuarios en la base de datos: {user_count}")
        
        # Verificar usuarios de prueba
        cursor.execute("""
            SELECT email, tipo_usuario, activo 
            FROM usuarios 
            WHERE email IN ('diego.castro.lagos@gmail.com', 'rodrigoandressilvabreve@gmail.com')
        """)
        
        test_users = cursor.fetchall()
        print(f"🧪 Usuarios de prueba encontrados: {len(test_users)}")
        
        for user in test_users:
            status = "✅ Activo" if user['activo'] else "❌ Inactivo"
            print(f"  - {user['email']} ({user['tipo_usuario']}) - {status}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Base de datos verificada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    verify_railway_database()
