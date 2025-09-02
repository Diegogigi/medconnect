#!/usr/bin/env python3
"""
Script para configurar desarrollo local y verificar Railway
"""


def fix_local_development():
    """Configura desarrollo local y verifica Railway"""

    print("🔧 Configurando desarrollo local...")

    # 1. Crear archivo .env para desarrollo local
    print("\n1️⃣ Creando archivo .env para desarrollo local...")

    env_content = """# Variables de entorno para desarrollo local
# Copia estas variables desde Railway y ajusta según tu configuración local

# DATABASE_URL=postgresql://postgres:password@localhost:5432/medconnect
PGHOST=localhost
PGDATABASE=medconnect
PGUSER=postgres
PGPASSWORD=tu_password_aqui
PGPORT=5432

# Variables de Railway (para referencia)
# DATABASE_URL=postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@postgres.railway.internal:5432/railway
# PGHOST=postgres.railway.internal
# PGDATABASE=railway
# PGUSER=postgres
# PGPASSWORD=SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd
# PGPORT=5432

# Otras variables
SECRET_KEY=dev-secret-key-local-12345
OPENROUTER_API_KEY=tu_api_key_aqui
FLASK_ENV=development
"""

    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)

    print("✅ Archivo .env creado")

    # 2. Crear script para cargar variables de entorno
    print("\n2️⃣ Creando script para cargar variables de entorno...")

    load_env_script = '''#!/usr/bin/env python3
"""
Script para cargar variables de entorno desde archivo .env
"""

import os
from dotenv import load_dotenv

def load_environment():
    """Carga variables de entorno desde archivo .env"""
    
    # Cargar variables desde .env si existe
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ Variables de entorno cargadas desde .env")
    else:
        print("⚠️ Archivo .env no encontrado")
    
    # Mostrar variables actuales
    print("📋 Variables de entorno actuales:")
    database_url = os.environ.get("DATABASE_URL")
    pghost = os.environ.get("PGHOST")
    pgdatabase = os.environ.get("PGDATABASE")
    pguser = os.environ.get("PGUSER")
    pgpassword = os.environ.get("PGPASSWORD")
    pgport = os.environ.get("PGPORT")
    
    print(f"   DATABASE_URL: {'✅ Configurada' if database_url else '❌ No configurada'}")
    print(f"   PGHOST: {pghost or 'No configurado'}")
    print(f"   PGDATABASE: {pgdatabase or 'No configurado'}")
    print(f"   PGUSER: {pguser or 'No configurado'}")
    print(f"   PGPASSWORD: {'✅ Configurada' if pgpassword else '❌ No configurada'}")
    print(f"   PGPORT: {pgport or 'No configurado'}")

if __name__ == "__main__":
    load_environment()
'''

    with open("load_env.py", "w", encoding="utf-8") as f:
        f.write(load_env_script)

    print("✅ Script load_env.py creado")

    # 3. Crear script de verificación para Railway
    print("\n3️⃣ Creando script de verificación para Railway...")

    railway_check_script = '''#!/usr/bin/env python3
"""
Script para verificar configuración en Railway
"""

import os
import requests
import json

def check_railway_deployment():
    """Verifica el estado del deployment en Railway"""
    
    print("🚀 Verificando deployment en Railway...")
    
    try:
        # Intentar hacer una petición a la aplicación
        response = requests.get('https://www.medconnect.cl/health', timeout=10)
        
        if response.status_code == 200:
            print("✅ Aplicación respondiendo correctamente")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
        else:
            print(f"⚠️ Aplicación respondiendo con status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando a la aplicación: {e}")
    
    print("\\n📋 Para verificar Railway:")
    print("1. Ve a https://railway.app/dashboard")
    print("2. Selecciona tu proyecto MedConnect")
    print("3. Ve a la pestaña 'Variables'")
    print("4. Verifica que DATABASE_URL esté configurada")
    print("5. Ve a la pestaña 'Deployments'")
    print("6. Revisa los logs del último deployment")

if __name__ == "__main__":
    check_railway_deployment()
'''

    with open("check_railway.py", "w", encoding="utf-8") as f:
        f.write(railway_check_script)

    print("✅ Script check_railway.py creado")

    print("\n4️⃣ Instrucciones para desarrollo local:")
    print("   1. Instalar python-dotenv: pip install python-dotenv")
    print("   2. Configurar PostgreSQL local o usar Railway")
    print("   3. Editar .env con tus credenciales")
    print("   4. Ejecutar: python load_env.py")
    print("   5. Ejecutar: python test_connection.py")

    print("\n5️⃣ Para Railway:")
    print("   1. Ejecutar: python check_railway.py")
    print("   2. Verificar variables de entorno en Railway")
    print("   3. Revisar logs de deployment")


if __name__ == "__main__":
    fix_local_development()
