#!/usr/bin/env python3
"""
Script para solucionar el problema de login en la versión oficial de Railway
"""

import os
import sys


def fix_production_railway_login():
    """Soluciona el problema de login en Railway"""

    print("🔧 Solucionando problema de login en Railway...")
    print("=" * 60)

    # 1. Verificar variables de entorno críticas
    print("\n1️⃣ Verificando variables de entorno críticas...")

    critical_vars = {
        "DATABASE_URL": "Conexión a PostgreSQL",
        "SECRET_KEY": "Clave secreta para sesiones",
        "FLASK_ENV": "Entorno de Flask",
        "OPENROUTER_API_KEY": "API Key para IA",
    }

    missing_vars = []
    for var, description in critical_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: Configurada")
        else:
            print(f"  ❌ {var}: NO CONFIGURADA")
            missing_vars.append(var)

    if missing_vars:
        print(f"\n⚠️ Variables faltantes: {', '.join(missing_vars)}")
        print("🔧 Configura estas variables en Railway Dashboard")

    # 2. Crear script de configuración para Railway
    print("\n2️⃣ Creando script de configuración para Railway...")

    railway_config = """# 🚀 CONFIGURACIÓN RAILWAY - MEDCONNECT
# Copia estas variables en Railway Dashboard > Variables

# 🔗 BASE DE DATOS (CRÍTICA)
DATABASE_URL=postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway

# 🔑 AUTENTICACIÓN (CRÍTICA)
SECRET_KEY=medconnect-secret-key-2025-railway-production-ultra-secure

# 🌐 ENTORNO (CRÍTICA)
FLASK_ENV=production

# 🤖 IA (CRÍTICA)
OPENROUTER_API_KEY=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

# 🌐 PUERTO (CRÍTICA)
PORT=5000

# 🔒 SEGURIDAD (OPCIONAL)
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# 🌍 CORS (OPCIONAL)
CORS_ORIGINS=https://medconnect.cl,https://www.medconnect.cl

# 📊 LOGGING (OPCIONAL)
LOG_LEVEL=INFO
"""

    with open("railway_variables.txt", "w", encoding="utf-8") as f:
        f.write(railway_config)

    print("  ✅ Archivo railway_variables.txt creado")

    # 3. Crear script de verificación de base de datos
    print("\n3️⃣ Creando script de verificación de base de datos...")

    db_verification = '''#!/usr/bin/env python3
"""
Script para verificar la conexión a PostgreSQL en Railway
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def verify_railway_database():
    """Verifica la conexión a PostgreSQL en Railway"""
    
    print("🔍 Verificando conexión a PostgreSQL en Railway...")
    print("=" * 50)
    
    # Obtener DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL no configurada")
        print("🔧 Configura DATABASE_URL en Railway Dashboard")
        return False
    
    print(f"✅ DATABASE_URL encontrada: {database_url[:50]}...")
    
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Conexión a PostgreSQL exitosa")
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cursor.fetchall()
        print(f"📋 Tablas encontradas: {len(tables)}")
        
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Verificar tabla de usuarios
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        user_count = cursor.fetchone()['count']
        print(f"👥 Usuarios en la base de datos: {user_count}")
        
        # Verificar usuarios de prueba
        cursor.execute("""
            SELECT email, tipo_usuario, activo 
            FROM usuarios 
            WHERE email IN ('diego.castro.lagos@gmail.com', 'rodrigoandressilvabreve@gmail.com')
        """)
        
        test_users = cursor.fetchall()
        print(f"🧪 Usuarios de prueba encontrados: {len(test_users)}")
        
        for user in test_users:
            status = "✅ Activo" if user['activo'] else "❌ Inactivo"
            print(f"  - {user['email']} ({user['tipo_usuario']}) - {status}")
        
        cursor.close()
        conn.close()
        
        print("\\n🎉 Base de datos verificada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    verify_railway_database()
'''

    with open("verify_railway_db.py", "w", encoding="utf-8") as f:
        f.write(db_verification)

    print("  ✅ Archivo verify_railway_db.py creado")

    # 4. Crear script de migración de usuarios
    print("\n4️⃣ Creando script de migración de usuarios...")

    migration_script = '''#!/usr/bin/env python3
"""
Script para migrar usuarios de prueba a PostgreSQL en Railway
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt

def migrate_test_users():
    """Migra usuarios de prueba a PostgreSQL"""
    
    print("🔄 Migrando usuarios de prueba a PostgreSQL...")
    print("=" * 50)
    
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL no configurada")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Usuarios de prueba
        test_users = [
            {
                "email": "diego.castro.lagos@gmail.com",
                "password": "password123",
                "nombre": "Diego",
                "apellido": "Castro",
                "tipo_usuario": "profesional",
                "telefono": "+56912345678",
                "especialidad": "Medicina General"
            },
            {
                "email": "rodrigoandressilvabreve@gmail.com",
                "password": "password123",
                "nombre": "Rodrigo",
                "apellido": "Silva",
                "tipo_usuario": "paciente",
                "telefono": "+56987654321",
                "especialidad": None
            }
        ]
        
        for user in test_users:
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (user["email"],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"⚠️ Usuario {user['email']} ya existe")
                continue
            
            # Hash de la contraseña
            password_hash = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insertar usuario
            cursor.execute("""
                INSERT INTO usuarios (
                    email, password_hash, nombre, apellido, tipo_usuario,
                    telefono, especialidad, activo, fecha_creacion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                )
            """, (
                user["email"], password_hash, user["nombre"], user["apellido"],
                user["tipo_usuario"], user["telefono"], user["especialidad"], True
            ))
            
            print(f"✅ Usuario {user['email']} creado")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\\n🎉 Migración de usuarios completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        return False

if __name__ == "__main__":
    migrate_test_users()
'''

    with open("migrate_test_users.py", "w", encoding="utf-8") as f:
        f.write(migration_script)

    print("  ✅ Archivo migrate_test_users.py creado")

    # 5. Crear instrucciones de solución
    print("\n5️⃣ Creando instrucciones de solución...")

    solution_instructions = """# 🚀 SOLUCIÓN PROBLEMA LOGIN RAILWAY

## 📋 **PROBLEMA IDENTIFICADO:**
La versión oficial en Railway no puede hacer login porque:
1. ❌ Variables de entorno no configuradas correctamente
2. ❌ Base de datos PostgreSQL no tiene usuarios de prueba
3. ❌ Conexión a base de datos falla

## ✅ **SOLUCIÓN PASO A PASO:**

### **Paso 1: Configurar Variables en Railway**
1. Ve a Railway Dashboard
2. Selecciona tu proyecto MedConnect
3. Ve a la pestaña "Variables"
4. Agrega estas variables (copia desde railway_variables.txt):

```
DATABASE_URL=postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway
SECRET_KEY=medconnect-secret-key-2025-railway-production-ultra-secure
FLASK_ENV=production
OPENROUTER_API_KEY=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
PORT=5000
```

### **Paso 2: Verificar Base de Datos**
1. Ejecuta: `python verify_railway_db.py`
2. Verifica que la conexión funcione
3. Verifica que existan las tablas necesarias

### **Paso 3: Migrar Usuarios de Prueba**
1. Ejecuta: `python migrate_test_users.py`
2. Esto creará los usuarios de prueba en PostgreSQL

### **Paso 4: Probar Login**
1. Ve a https://www.medconnect.cl/login
2. Intenta login con:
   - Email: diego.castro.lagos@gmail.com
   - Password: password123

## 🔍 **VERIFICACIÓN:**
- ✅ Variables configuradas en Railway
- ✅ Base de datos conectada
- ✅ Usuarios de prueba creados
- ✅ Login funcionando

## 🚨 **IMPORTANTE:**
- No compartas las credenciales de la base de datos
- Mantén seguras las variables de entorno
- Haz backup regular de la base de datos
"""

    with open("SOLUCION_RAILWAY_LOGIN.md", "w", encoding="utf-8") as f:
        f.write(solution_instructions)

    print("  ✅ Archivo SOLUCION_RAILWAY_LOGIN.md creado")

    print("\n" + "=" * 60)
    print("🎉 Scripts de solución creados exitosamente")
    print("\n📋 Próximos pasos:")
    print("1. Configura las variables en Railway Dashboard")
    print("2. Ejecuta: python verify_railway_db.py")
    print("3. Ejecuta: python migrate_test_users.py")
    print("4. Prueba el login en https://www.medconnect.cl")
    print("\n📁 Archivos creados:")
    print("  - railway_variables.txt")
    print("  - verify_railway_db.py")
    print("  - migrate_test_users.py")
    print("  - SOLUCION_RAILWAY_LOGIN.md")


if __name__ == "__main__":
    fix_production_railway_login()
