#!/usr/bin/env python3
"""
Script simple para probar la consulta SQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def test_simple_sql():
    """Prueba simple de la consulta SQL"""
    
    print("🧪 Probando consulta SQL simple...")
    print("=" * 60)
    
    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión exitosa")
        
        # Consulta simple
        print(f"\n🔍 Ejecutando consulta simple...")
        cursor.execute("""
            SELECT profesional_id, paciente_id, nombre_completo, email, estado_relacion
            FROM pacientes_profesional
            WHERE profesional_id = 13;
        """)
        
        result = cursor.fetchall()
        print(f"📊 Resultados: {len(result)}")
        
        for row in result:
            print(f"  - {row['nombre_completo']} ({row['email']}) - Estado: {row['estado_relacion']}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 ¡Consulta exitosa!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBA SQL SIMPLE")
    print("=" * 60)
    
    success = test_simple_sql()
    
    if success:
        print(f"\n🎉 ¡SQL funciona!")
    else:
        print(f"\n❌ Error en SQL")
