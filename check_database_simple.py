#!/usr/bin/env python3
"""
Script simple para verificar el estado de la base de datos
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def check_database_simple():
    """Verifica el estado simple de la base de datos"""
    
    print("🔍 Verificando estado de la base de datos...")
    print("=" * 60)
    
    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión exitosa")
        
        # 1. Verificar tabla usuarios
        print(f"\n1️⃣ Verificando tabla usuarios...")
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM usuarios;
        """)
        
        result = cursor.fetchone()
        total_users = result['total'] if result else 0
        print(f"  📊 Total usuarios: {total_users}")
        
        # 2. Verificar usuarios profesionales
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM usuarios 
            WHERE tipo_usuario = 'profesional';
        """)
        
        result = cursor.fetchone()
        total_professionals = result['total'] if result else 0
        print(f"  👨‍⚕️ Profesionales: {total_professionals}")
        
        # 3. Verificar si existe tabla pacientes_profesional
        print(f"\n2️⃣ Verificando tabla pacientes_profesional...")
        try:
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM pacientes_profesional;
            """)
            
            result = cursor.fetchone()
            total_relations = result['total'] if result else 0
            print(f"  📊 Total relaciones: {total_relations}")
            
            if total_relations > 0:
                # Mostrar algunas relaciones
                cursor.execute("""
                    SELECT profesional_id, paciente_id, nombre_completo, estado_relacion
                    FROM pacientes_profesional
                    LIMIT 5;
                """)
                
                relations = cursor.fetchall()
                print(f"  🔗 Primeras relaciones:")
                for rel in relations:
                    print(f"    - Prof: {rel['profesional_id']}, Paciente: {rel['paciente_id']}, Estado: {rel['estado_relacion']}")
            
        except Exception as e:
            print(f"  ❌ Tabla pacientes_profesional no existe o error: {e}")
        
        # 4. Probar consulta específica para Diego Castro
        print(f"\n3️⃣ Probando consulta para Diego Castro (ID: 13)...")
        try:
            # Consulta simple primero
            cursor.execute("""
                SELECT id, email, nombre, apellido, tipo_usuario
                FROM usuarios 
                WHERE id = 13;
            """)
            
            user = cursor.fetchone()
            if user:
                print(f"  ✅ Diego Castro encontrado: {user['nombre']} {user['apellido']}")
            else:
                print(f"  ❌ Diego Castro no encontrado")
                
        except Exception as e:
            print(f"  ❌ Error consultando Diego Castro: {e}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Verificación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN BASE DE DATOS")
    print("=" * 60)
    
    success = check_database_simple()
    
    if success:
        print(f"\n🎉 ¡Verificación exitosa!")
    else:
        print(f"\n❌ Error en la verificación")
