#!/usr/bin/env python3
"""
Script de prueba de conexión a PostgreSQL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_postgresql_connection():
    """Prueba la conexión a PostgreSQL"""
    
    print("🧪 Probando conexión a PostgreSQL...")
    
    try:
        # Obtener variables de entorno
        database_url = os.environ.get("DATABASE_URL")
        pghost = os.environ.get("PGHOST")
        pgdatabase = os.environ.get("PGDATABASE")
        pguser = os.environ.get("PGUSER")
        pgpassword = os.environ.get("PGPASSWORD")
        pgport = os.environ.get("PGPORT")
        
        print(f"📋 Variables encontradas:")
        print(f"   DATABASE_URL: {'✅' if database_url else '❌'}")
        print(f"   PGHOST: {pghost or 'No configurado'}")
        print(f"   PGDATABASE: {pgdatabase or 'No configurado'}")
        print(f"   PGUSER: {pguser or 'No configurado'}")
        print(f"   PGPASSWORD: {'✅' if pgpassword else '❌'}")
        print(f"   PGPORT: {pgport or 'No configurado'}")
        
        # Intentar conexión
        if database_url:
            print("🔗 Conectando usando DATABASE_URL...")
            print(f"   URL: {database_url[:50]}..." if len(database_url) > 50 else f"   URL: {database_url}")
            conn = psycopg2.connect(database_url)
        else:
            print("🔗 Conectando usando variables individuales...")
            conn = psycopg2.connect(
                host=pghost or "localhost",
                database=pgdatabase or "medconnect",
                user=pguser or "postgres",
                password=pgpassword or "",
                port=pgport or "5432",
            )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Probar consulta simple
        print("🔍 Probando consulta simple...")
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL conectado: {version['version'][:50]}...")
        
        # Verificar tablas
        print("🔍 Verificando tablas...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('profesionales', 'pacientes_profesional')
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"📋 Tablas encontradas:")
        for table in tables:
            print(f"   ✅ {table['table_name']}")
        
        if not tables:
            print("   ❌ No se encontraron las tablas necesarias")
        
        # Probar inserción de prueba
        print("🔍 Probando inserción de prueba...")
        try:
            cursor.execute("""
                INSERT INTO profesionales 
                (email, nombre, apellido, estado, disponible, unnamed_21, unnamed_22)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, ('test@test.com', 'Test', 'User', 'activo', True))
            
            # Verificar inserción
            cursor.execute("SELECT COUNT(*) as count FROM profesionales WHERE email = %s", ('test@test.com',))
            count = cursor.fetchone()['count']
            print(f"✅ Inserción exitosa: {count} registro(s)")
            
            # Limpiar prueba
            cursor.execute("DELETE FROM profesionales WHERE email = %s", ('test@test.com',))
            conn.commit()
            print("✅ Prueba limpiada")
            
        except Exception as e:
            print(f"❌ Error en inserción de prueba: {e}")
            conn.rollback()
        
        cursor.close()
        conn.close()
        print("✅ Conexión cerrada correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    test_postgresql_connection()
