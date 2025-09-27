#!/usr/bin/env python3
"""
Script robusto para crear la tabla pacientes_profesional en Railway PostgreSQL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def create_patients_professional_table_robust():
    """Crea la tabla pacientes_profesional en Railway PostgreSQL de forma robusta"""
    
    print("🔧 Creando tabla pacientes_profesional en Railway PostgreSQL...")
    print("=" * 60)
    
    # Variables de conexión a Railway
    database_url = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"
    
    print(f"🔗 Conectando a Railway PostgreSQL...")
    print(f"   URL: {database_url[:50]}...")
    
    try:
        # Conectar a PostgreSQL con configuración robusta
        conn = psycopg2.connect(
            database_url,
            connect_timeout=10,
            application_name="medconnect_patients_table_creation"
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión a PostgreSQL exitosa")
        
        # Verificar conexión
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 PostgreSQL version: {version[:50]}...")
        
        # Verificar si la tabla ya existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'pacientes_profesional'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        print(f"📋 Tabla pacientes_profesional existe: {table_exists}")
        
        if table_exists:
            print("⚠️ La tabla 'pacientes_profesional' ya existe")
            
            # Verificar estructura de la tabla
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'pacientes_profesional'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"📋 Columnas existentes: {len(columns)}")
            for col in columns:
                print(f"  - {col['column_name']} ({col['data_type']}) - Nullable: {col['is_nullable']}")
                
        else:
            print("🔧 Creando tabla pacientes_profesional...")
            
            # Crear tabla pacientes_profesional
            cursor.execute("""
                CREATE TABLE pacientes_profesional (
                    id SERIAL PRIMARY KEY,
                    profesional_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    paciente_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    fecha_primera_atencion DATE,
                    total_atenciones INTEGER DEFAULT 0,
                    ultima_atencion DATE,
                    notas_generales TEXT,
                    estado_relacion VARCHAR(20) DEFAULT 'activo' CHECK (estado_relacion IN ('activo', 'inactivo')),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Evitar duplicados
                    UNIQUE(profesional_id, paciente_id)
                );
            """)
            
            print("✅ Tabla pacientes_profesional creada")
            
            # Crear índices para optimizar consultas
            try:
                cursor.execute("""
                    CREATE INDEX idx_pacientes_prof_profesional ON pacientes_profesional(profesional_id);
                """)
                print("✅ Índice para profesional_id creado")
            except Exception as e:
                print(f"⚠️ Error creando índice profesional_id: {e}")
            
            try:
                cursor.execute("""
                    CREATE INDEX idx_pacientes_prof_paciente ON pacientes_profesional(paciente_id);
                """)
                print("✅ Índice para paciente_id creado")
            except Exception as e:
                print(f"⚠️ Error creando índice paciente_id: {e}")
        
        # Verificar usuarios existentes
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
            SELECT COUNT(*) as total_relaciones
            FROM pacientes_profesional;
        """)
        
        total_relaciones = cursor.fetchone()['total_relaciones']
        print(f"\n🔗 Relaciones profesionales-pacientes existentes: {total_relaciones}")
        
        if total_relaciones > 0:
            cursor.execute("""
                SELECT 
                    pp.id,
                    p.nombre as profesional_nombre,
                    p.apellido as profesional_apellido,
                    pac.nombre as paciente_nombre,
                    pac.apellido as paciente_apellido,
                    pp.estado_relacion,
                    pp.fecha_creacion
                FROM pacientes_profesional pp
                JOIN usuarios p ON pp.profesional_id = p.id
                JOIN usuarios pac ON pp.paciente_id = pac.id
                ORDER BY pp.fecha_creacion DESC
                LIMIT 10;
            """)
            
            relaciones = cursor.fetchall()
            print(f"📋 Últimas {len(relaciones)} relaciones:")
            for rel in relaciones:
                print(f"  - {rel['profesional_nombre']} {rel['profesional_apellido']} -> {rel['paciente_nombre']} {rel['paciente_apellido']} ({rel['estado_relacion']})")
        
        # Confirmar cambios
        conn.commit()
        print(f"\n✅ Cambios confirmados en la base de datos")
        
        cursor.close()
        conn.close()
        
        print(f"\n🎉 Tabla pacientes_profesional verificada/creada exitosamente")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión a PostgreSQL: {e}")
        print(f"🔧 Verifica que la base de datos esté disponible")
        return False
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def show_usage_instructions():
    """Muestra instrucciones de uso"""
    
    print(f"\n📋 INSTRUCCIONES DE USO:")
    print("=" * 50)
    
    print(f"\n1️⃣ Para agregar un paciente a un profesional:")
    print(f"   INSERT INTO pacientes_profesional (profesional_id, paciente_id)")
    print(f"   VALUES (ID_PROFESIONAL, ID_PACIENTE);")
    
    print(f"\n2️⃣ Para obtener pacientes de un profesional:")
    print(f"   SELECT u.* FROM usuarios u")
    print(f"   INNER JOIN pacientes_profesional pp ON u.id = pp.paciente_id")
    print(f"   WHERE pp.profesional_id = ID_PROFESIONAL;")
    
    print(f"\n3️⃣ Para desactivar una relación:")
    print(f"   UPDATE pacientes_profesional")
    print(f"   SET estado_relacion = 'inactivo'")
    print(f"   WHERE profesional_id = ID_PROFESIONAL AND paciente_id = ID_PACIENTE;")

if __name__ == "__main__":
    print("🚀 CREACIÓN TABLA PACIENTES_PROFESIONAL ROBUSTA")
    print("=" * 60)
    
    success = create_patients_professional_table_robust()
    
    if success:
        show_usage_instructions()
        print(f"\n🎉 ¡PROCESO COMPLETADO!")
        print(f"🔧 La tabla pacientes_profesional está lista para usar")
    else:
        print(f"\n❌ Error en el proceso")
        print(f"🔧 Revisa la conexión a la base de datos")
        sys.exit(1)
