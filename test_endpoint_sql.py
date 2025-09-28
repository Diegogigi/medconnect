#!/usr/bin/env python3
"""
Script para probar la consulta SQL del endpoint con el user_id correcto
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def test_endpoint_sql():
    """Prueba la consulta SQL del endpoint"""
    
    print("🧪 Probando consulta SQL del endpoint...")
    print("=" * 60)
    
    # Conectar a Railway PostgreSQL
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión exitosa")
        
        # User ID de Diego Castro (ID: 13)
        user_id = 13
        print(f"🔍 Probando con user_id: {user_id}")
        
        # 1. Verificar que la tabla existe
        print(f"\n1️⃣ Verificando tabla...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'pacientes_profesional'
            );
        """)
        
        result = cursor.fetchone()
        table_exists = result[0] if result and result[0] is not None else False
        print(f"  📊 Tabla existe: {table_exists}")
        
        if not table_exists:
            print(f"  ❌ La tabla pacientes_profesional no existe")
            return False
        
        # 2. Probar la consulta exacta del endpoint
        print(f"\n2️⃣ Probando consulta del endpoint...")
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
            
            print(f"  🔍 Ejecutando consulta...")
            cursor.execute(query, (user_id,))
            result = cursor.fetchall()
            
            print(f"  📊 Resultados: {len(result)}")
            
            if result:
                print(f"  ✅ Consulta exitosa - Pacientes encontrados:")
                for row in result:
                    print(f"    - {row['nombre_completo']} ({row['email']}) - Estado: {row['estado_relacion']}")
            else:
                print(f"  📋 No hay pacientes para este profesional")
                
        except Exception as e:
            print(f"  ❌ Error en consulta: {e}")
            print(f"  🔍 Tipo de error: {type(e).__name__}")
            return False
        
        # 3. Probar procesamiento de resultados
        print(f"\n3️⃣ Probando procesamiento de resultados...")
        try:
            pacientes = []
            if result:
                for row in result:
                    # Procesar nombre_completo
                    nombre_completo = row.get("nombre_completo", "")
                    partes_nombre = nombre_completo.split(" ", 1)
                    nombre = partes_nombre[0] if partes_nombre else ""
                    apellido = partes_nombre[1] if len(partes_nombre) > 1 else ""
                    
                    paciente = {
                        "id": row.get("id"),
                        "nombre": nombre,
                        "apellido": apellido,
                        "email": row.get("email"),
                        "telefono": str(row.get("telefono")) if row.get("telefono") else None,
                        "fecha_nacimiento": (str(row.get("fecha_nacimiento")) if row.get("fecha_nacimiento") else None),
                        "genero": row.get("genero"),
                        "direccion": row.get("direccion"),
                        "fecha_primera_atencion": (str(row.get("fecha_primera_atencion")) if row.get("fecha_primera_atencion") else None),
                        "total_atenciones": 0,
                        "ultima_atencion": (str(row.get("ultima_atencion")) if row.get("ultima_atencion") else None),
                        "notas_generales": row.get("notas_generales"),
                        "estado_relacion": row.get("estado_relacion", "activo"),
                    }
                    pacientes.append(paciente)
            
            print(f"  📊 Pacientes procesados: {len(pacientes)}")
            for paciente in pacientes:
                print(f"    - {paciente['nombre']} {paciente['apellido']} ({paciente['email']})")
                
        except Exception as e:
            print(f"  ❌ Error procesando resultados: {e}")
            return False
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 ¡Consulta SQL funciona correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PRUEBA CONSULTA SQL ENDPOINT")
    print("=" * 60)
    
    success = test_endpoint_sql()
    
    if success:
        print(f"\n🎉 ¡Consulta SQL funciona!")
        print(f"🔧 El problema puede estar en el manejo de la sesión o en el código del endpoint")
    else:
        print(f"\n❌ Error en la consulta SQL")
        print(f"🔧 Revisa la estructura de la base de datos")
