#!/usr/bin/env python3
"""
Script para verificar la estructura de la base de datos
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def check_database_structure():
    """Verifica la estructura de la base de datos"""
    
    print("🔍 Verificando estructura de la base de datos...")
    print("=" * 60)
    
    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión exitosa")
        
        # 1. Listar todas las tablas
        print(f"\n1️⃣ Listando todas las tablas...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"  📊 Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"    - {table['table_name']}")
        
        # 2. Verificar estructura de pacientes_profesional
        print(f"\n2️⃣ Verificando estructura de pacientes_profesional...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'pacientes_profesional'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"  📊 Columnas en pacientes_profesional: {len(columns)}")
        for col in columns:
            print(f"    - {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
        
        # 3. Verificar restricciones de clave foránea
        print(f"\n3️⃣ Verificando restricciones de clave foránea...")
        cursor.execute("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name = 'pacientes_profesional';
        """)
        
        constraints = cursor.fetchall()
        print(f"  📊 Restricciones de clave foránea: {len(constraints)}")
        for constraint in constraints:
            print(f"    - {constraint['column_name']} -> {constraint['foreign_table_name']}.{constraint['foreign_column_name']}")
        
        # 4. Verificar si existe tabla profesionales
        print(f"\n4️⃣ Verificando tabla profesionales...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'profesionales'
            );
        """)
        
        result = cursor.fetchone()
        profesionales_exists = result[0] if result else False
        print(f"  📊 Tabla profesionales existe: {profesionales_exists}")
        
        if profesionales_exists:
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM profesionales;
            """)
            
            result = cursor.fetchone()
            total_profesionales = result['total'] if result else 0
            print(f"  📊 Total registros en profesionales: {total_profesionales}")
        
        # 5. Verificar datos actuales en pacientes_profesional
        print(f"\n5️⃣ Verificando datos actuales...")
        cursor.execute("""
            SELECT profesional_id, paciente_id, nombre_completo, estado_relacion
            FROM pacientes_profesional
            ORDER BY paciente_id;
        """)
        
        relations = cursor.fetchall()
        print(f"  📊 Relaciones actuales: {len(relations)}")
        for rel in relations:
            print(f"    - Prof: {rel['profesional_id']}, Paciente: {rel['paciente_id']}, Estado: {rel['estado_relacion']}")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Verificación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN ESTRUCTURA BASE DE DATOS")
    print("=" * 60)
    
    success = check_database_structure()
    
    if success:
        print(f"\n🎉 ¡Verificación exitosa!")
    else:
        print(f"\n❌ Error en la verificación")
