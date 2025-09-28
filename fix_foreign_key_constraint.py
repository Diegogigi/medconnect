#!/usr/bin/env python3
"""
Script para corregir la restricción de clave foránea
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def fix_foreign_key_constraint():
    """Corrige la restricción de clave foránea"""
    
    print("🔧 Corrigiendo restricción de clave foránea...")
    print("=" * 60)
    
    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión exitosa")
        
        # 1. Verificar restricción actual
        print(f"\n1️⃣ Verificando restricción actual...")
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
        print(f"  📊 Restricciones encontradas: {len(constraints)}")
        for constraint in constraints:
            print(f"    - {constraint['constraint_name']}: {constraint['column_name']} -> {constraint['foreign_table_name']}.{constraint['foreign_column_name']}")
        
        # 2. Eliminar restricción existente
        if constraints:
            print(f"\n2️⃣ Eliminando restricción existente...")
            constraint_name = constraints[0]['constraint_name']
            print(f"  🗑️ Eliminando restricción: {constraint_name}")
            
            cursor.execute(f"""
                ALTER TABLE pacientes_profesional 
                DROP CONSTRAINT {constraint_name};
            """)
            
            print(f"  ✅ Restricción eliminada")
        
        # 3. Crear nueva restricción que apunte a usuarios.id
        print(f"\n3️⃣ Creando nueva restricción...")
        cursor.execute("""
            ALTER TABLE pacientes_profesional 
            ADD CONSTRAINT pacientes_profesional_profesional_id_fkey 
            FOREIGN KEY (profesional_id) REFERENCES usuarios(id);
        """)
        
        print(f"  ✅ Nueva restricción creada: profesionales_id -> usuarios.id")
        
        # 4. Verificar que la nueva restricción funciona
        print(f"\n4️⃣ Verificando nueva restricción...")
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
        
        new_constraints = cursor.fetchall()
        print(f"  📊 Nueva restricción:")
        for constraint in new_constraints:
            print(f"    - {constraint['constraint_name']}: {constraint['column_name']} -> {constraint['foreign_table_name']}.{constraint['foreign_column_name']}")
        
        # 5. Ahora actualizar las relaciones
        print(f"\n5️⃣ Actualizando relaciones...")
        cursor.execute("""
            UPDATE pacientes_profesional 
            SET profesional_id = 13
            WHERE profesional_id IS NULL;
        """)
        
        updated_rows = cursor.rowcount
        print(f"  📊 Relaciones actualizadas: {updated_rows}")
        
        # 6. Verificar relaciones después de la actualización
        print(f"\n6️⃣ Verificando relaciones actualizadas...")
        cursor.execute("""
            SELECT profesional_id, paciente_id, nombre_completo, estado_relacion
            FROM pacientes_profesional
            ORDER BY paciente_id;
        """)
        
        relations = cursor.fetchall()
        print(f"  📊 Relaciones actualizadas: {len(relations)}")
        for rel in relations:
            print(f"    - Prof: {rel['profesional_id']}, Paciente: {rel['paciente_id']}, Estado: {rel['estado_relacion']}")
        
        # Confirmar cambios
        conn.commit()
        print(f"\n✅ Cambios confirmados en la base de datos")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 ¡Restricción corregida exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CORRECCIÓN RESTRICCIÓN CLAVE FORÁNEA")
    print("=" * 60)
    
    success = fix_foreign_key_constraint()
    
    if success:
        print(f"\n🎉 ¡Restricción corregida!")
        print(f"🔧 Ahora prueba el endpoint de pacientes en https://www.medconnect.cl")
    else:
        print(f"\n❌ Error corrigiendo restricción")
        print(f"🔧 Revisa los logs para más detalles")
