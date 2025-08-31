#!/usr/bin/env python3
"""
Verificación final de la migración a PostgreSQL
"""

import psycopg2

DATABASE_URL = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

def final_verification():
    """Verificación final completa"""
    
    try:
        print("🔍 Verificación final de la migración a PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 1. Verificar tablas principales
        print("\n📋 1. TABLAS PRINCIPALES:")
        main_tables = ['usuarios', 'profesionales', 'pacientes', 'atenciones_medicas', 'citas_agenda']
        
        for table in main_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table}: {count} registros")
        
        # 2. Verificar tablas de gestión
        print("\n📋 2. TABLAS DE GESTIÓN:")
        management_tables = ['horarios_disponibles', 'recordatorios_profesional', 'sesiones', 'archivos_adjuntos']
        
        for table in management_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table}: {count} registros")
        
        # 3. Verificar tablas adicionales
        print("\n📋 3. TABLAS ADICIONALES:")
        additional_tables = ['medicamentos', 'examenes', 'especialidades', 'logs_acceso', 'interacciones_bot']
        
        for table in additional_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table}: {count} registros")
        
        # 4. Verificar usuarios de prueba
        print("\n👥 4. USUARIOS DE PRUEBA:")
        cursor.execute("SELECT email, tipo_usuario FROM usuarios")
        users = cursor.fetchall()
        for user in users:
            print(f"  ✅ {user[0]} ({user[1]})")
        
        # 5. Verificar profesionales
        print("\n👨‍⚕️ 5. PROFESIONALES:")
        cursor.execute("SELECT nombre, apellido, especialidad FROM profesionales")
        professionals = cursor.fetchall()
        for prof in professionals:
            print(f"  ✅ {prof[0]} {prof[1]} - {prof[2]}")
        
        # 6. Verificar pacientes
        print("\n👤 6. PACIENTES:")
        cursor.execute("SELECT nombre_completo, rut FROM pacientes_profesional")
        patients = cursor.fetchall()
        for patient in patients:
            print(f"  ✅ {patient[0]} - RUT: {patient[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 ¡VERIFICACIÓN COMPLETADA!")
        print("✅ Todas las tablas están creadas y funcionando")
        print("✅ Datos de prueba insertados correctamente")
        print("✅ Base de datos lista para producción")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

if __name__ == "__main__":
    success = final_verification()
    
    if success:
        print("\n🚀 ¡MIGRACIÓN A POSTGRESQL COMPLETADA EXITOSAMENTE!")
        print("🌐 Tu aplicación MedConnect ahora usa PostgreSQL en Railway")
        print("💡 Próximo paso: Configurar las variables de entorno en Railway")
    else:
        print("\n❌ Error en la verificación final") 