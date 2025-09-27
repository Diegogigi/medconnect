#!/usr/bin/env python3
"""
Script simple para verificar la tabla pacientes_profesional
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def check_patients_table():
    """Verifica la estructura de la tabla pacientes_profesional"""
    
    print("🔍 Verificando tabla pacientes_profesional...")
    
    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión exitosa")
        
        # Verificar estructura de la tabla
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'pacientes_profesional'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\n📋 Columnas en pacientes_profesional: {len(columns)}")
        for col in columns:
            print(f"  - {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
        
        # Verificar usuarios
        cursor.execute("""
            SELECT id, email, nombre, apellido, tipo_usuario 
            FROM usuarios 
            WHERE tipo_usuario IN ('profesional', 'paciente')
            ORDER BY tipo_usuario, apellido, nombre;
        """)
        
        users = cursor.fetchall()
        print(f"\n👥 Usuarios encontrados: {len(users)}")
        
        profesionales = [u for u in users if u['tipo_usuario'] == 'profesional']
        pacientes = [u for u in users if u['tipo_usuario'] == 'paciente']
        
        print(f"  - Profesionales: {len(profesionales)}")
        for prof in profesionales:
            print(f"    * {prof['nombre']} {prof['apellido']} ({prof['email']}) - ID: {prof['id']}")
            
        print(f"  - Pacientes: {len(pacientes)}")
        for pac in pacientes:
            print(f"    * {pac['nombre']} {pac['apellido']} ({pac['email']}) - ID: {pac['id']}")
        
        # Verificar relaciones existentes
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM pacientes_profesional;
        """)
        
        result = cursor.fetchone()
        total = result['total'] if result else 0
        print(f"\n🔗 Relaciones existentes: {total}")
        
        if total > 0:
            cursor.execute("""
                SELECT 
                    pp.id,
                    p.nombre as profesional_nombre,
                    p.apellido as profesional_apellido,
                    pac.nombre as paciente_nombre,
                    pac.apellido as paciente_apellido,
                    pp.estado_relacion
                FROM pacientes_profesional pp
                JOIN usuarios p ON pp.profesional_id = p.id
                JOIN usuarios pac ON pp.paciente_id = pac.id
                ORDER BY pp.id
                LIMIT 5;
            """)
            
            relaciones = cursor.fetchall()
            print(f"📋 Primeras {len(relaciones)} relaciones:")
            for rel in relaciones:
                print(f"  - {rel['profesional_nombre']} {rel['profesional_apellido']} -> {rel['paciente_nombre']} {rel['paciente_apellido']} ({rel['estado_relacion']})")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Verificación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_patients_table()
