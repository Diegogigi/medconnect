#!/usr/bin/env python3
"""
Script para corregir las relaciones de pacientes con profesionales
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def fix_patients_relations():
    """Corrige las relaciones de pacientes con profesionales"""
    
    print("🔧 Corrigiendo relaciones de pacientes...")
    print("=" * 60)
    
    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión exitosa")
        
        # 1. Verificar relaciones actuales
        print(f"\n1️⃣ Verificando relaciones actuales...")
        cursor.execute("""
            SELECT profesional_id, paciente_id, nombre_completo, estado_relacion
            FROM pacientes_profesional
            ORDER BY paciente_id;
        """)
        
        relations = cursor.fetchall()
        print(f"  📊 Relaciones encontradas: {len(relations)}")
        for rel in relations:
            print(f"    - Prof: {rel['profesional_id']}, Paciente: {rel['paciente_id']}, Estado: {rel['estado_relacion']}")
        
        # 2. Obtener IDs de profesionales
        print(f"\n2️⃣ Obteniendo IDs de profesionales...")
        cursor.execute("""
            SELECT id, email, nombre, apellido
            FROM usuarios 
            WHERE tipo_usuario = 'profesional'
            ORDER BY id;
        """)
        
        professionals = cursor.fetchall()
        print(f"  👨‍⚕️ Profesionales encontrados: {len(professionals)}")
        for prof in professionals:
            print(f"    - ID: {prof['id']}, {prof['nombre']} {prof['apellido']} ({prof['email']})")
        
        if len(professionals) == 0:
            print(f"  ❌ No hay profesionales en la base de datos")
            return False
        
        # 3. Asignar relaciones a Diego Castro (ID: 13)
        print(f"\n3️⃣ Asignando relaciones a Diego Castro (ID: 13)...")
        diego_id = 13
        
        # Verificar si Diego existe
        cursor.execute("""
            SELECT id, email, nombre, apellido
            FROM usuarios 
            WHERE id = %s;
        """, (diego_id,))
        
        diego = cursor.fetchone()
        if not diego:
            print(f"  ❌ Diego Castro (ID: 13) no encontrado")
            return False
        
        print(f"  ✅ Diego Castro encontrado: {diego['nombre']} {diego['apellido']}")
        
        # Actualizar relaciones con profesional_id = 13
        cursor.execute("""
            UPDATE pacientes_profesional 
            SET profesional_id = %s
            WHERE profesional_id IS NULL;
        """, (diego_id,))
        
        updated_rows = cursor.rowcount
        print(f"  📊 Relaciones actualizadas: {updated_rows}")
        
        # 4. Verificar relaciones después de la actualización
        print(f"\n4️⃣ Verificando relaciones después de la actualización...")
        cursor.execute("""
            SELECT profesional_id, paciente_id, nombre_completo, estado_relacion
            FROM pacientes_profesional
            ORDER BY paciente_id;
        """)
        
        relations = cursor.fetchall()
        print(f"  📊 Relaciones actualizadas: {len(relations)}")
        for rel in relations:
            print(f"    - Prof: {rel['profesional_id']}, Paciente: {rel['paciente_id']}, Estado: {rel['estado_relacion']}")
        
        # 5. Probar consulta del endpoint
        print(f"\n5️⃣ Probando consulta del endpoint...")
        try:
            query = """
                SELECT DISTINCT 
                    pp.paciente_id as id,
                    pp.nombre_completo,
                    pp.email,
                    pp.telefono,
                    pp.fecha_nacimiento,
                    pp.genero,
                    pp.direccion,
                    pp.fecha_primera_consulta as fecha_primera_atencion,
                    pp.ultima_consulta as ultima_atencion,
                    pp.notas as notas_generales,
                    pp.estado_relacion
                FROM pacientes_profesional pp
                WHERE pp.profesional_id = %s 
                AND (pp.estado_relacion = 'activo' OR pp.estado_relacion IS NULL)
                ORDER BY pp.nombre_completo
            """
            
            cursor.execute(query, (diego_id,))
            result = cursor.fetchall()
            print(f"  📊 Pacientes para Diego Castro: {len(result)}")
            
            if result:
                for row in result:
                    print(f"    - {row['nombre_completo']} ({row['email']}) - Estado: {row['estado_relacion']}")
            else:
                print(f"    📋 No hay pacientes para Diego Castro")
                
        except Exception as e:
            print(f"  ❌ Error en consulta: {e}")
        
        # Confirmar cambios
        conn.commit()
        print(f"\n✅ Cambios confirmados en la base de datos")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 ¡Relaciones corregidas exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CORRECCIÓN RELACIONES PACIENTES")
    print("=" * 60)
    
    success = fix_patients_relations()
    
    if success:
        print(f"\n🎉 ¡Relaciones corregidas!")
        print(f"🔧 Ahora prueba el endpoint de pacientes en https://www.medconnect.cl")
    else:
        print(f"\n❌ Error corrigiendo relaciones")
        print(f"🔧 Revisa los logs para más detalles")
