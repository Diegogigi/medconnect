#!/usr/bin/env python3
"""
Script para desplegar las actualizaciones a Railway
"""

import os
import subprocess
import sys
from datetime import datetime

def deploy_to_railway():
    """Despliega las actualizaciones a Railway"""
    
    print("🚀 Desplegando actualizaciones a Railway...")
    print("=" * 60)
    
    # 1. Verificar que estamos en un repositorio git
    print("\n1️⃣ Verificando repositorio Git...")
    
    try:
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ No estás en un repositorio Git")
            print("🔧 Inicializa Git primero: git init")
            return False
        print("✅ Repositorio Git encontrado")
    except FileNotFoundError:
        print("❌ Git no está instalado")
        print("🔧 Instala Git desde: https://git-scm.com/")
        return False
    
    # 2. Agregar todos los archivos nuevos
    print("\n2️⃣ Agregando archivos al repositorio...")
    
    try:
        # Agregar archivos de solución
        files_to_add = [
            "railway_variables.txt",
            "verify_railway_db.py", 
            "migrate_test_users.py",
            "test_railway_login.py",
            "health_endpoint_fix.py",
            "check_railway_status.py",
            "fix_production_railway_login.py",
            "fix_railway_health_endpoint.py",
            "SOLUCION_RAILWAY_LOGIN.md",
            "SOLUCION_FINAL_RAILWAY.md"
        ]
        
        for file in files_to_add:
            if os.path.exists(file):
                subprocess.run(["git", "add", file], check=True)
                print(f"  ✅ {file} agregado")
            else:
                print(f"  ⚠️ {file} no encontrado")
        
        # Agregar todos los cambios
        subprocess.run(["git", "add", "."], check=True)
        print("✅ Todos los archivos agregados")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error agregando archivos: {e}")
        return False
    
    # 3. Hacer commit
    print("\n3️⃣ Creando commit...")
    
    try:
        commit_message = f"🔧 Solución problema login Railway - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("✅ Commit creado exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando commit: {e}")
        return False
    
    # 4. Verificar rama actual
    print("\n4️⃣ Verificando rama actual...")
    
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        current_branch = result.stdout.strip()
        print(f"✅ Rama actual: {current_branch}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error verificando rama: {e}")
        return False
    
    # 5. Push a Railway
    print("\n5️⃣ Desplegando a Railway...")
    
    try:
        # Intentar push a Railway
        result = subprocess.run(["git", "push", "railway", "main"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Despliegue exitoso a Railway")
        else:
            # Intentar con la rama actual
            result = subprocess.run(["git", "push", "railway", current_branch], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Despliegue exitoso a Railway")
            else:
                print("❌ Error en despliegue a Railway")
                print(f"Error: {result.stderr}")
                return False
                
    except subprocess.CalledProcessError as e:
        print(f"❌ Error desplegando a Railway: {e}")
        return False
    
    # 6. Verificar despliegue
    print("\n6️⃣ Verificando despliegue...")
    
    print("⏳ Esperando que Railway procese el despliegue...")
    print("🔍 Puedes verificar el progreso en Railway Dashboard")
    
    # 7. Instrucciones finales
    print("\n" + "=" * 60)
    print("🎉 DESPLIEGUE COMPLETADO")
    print("\n📋 Próximos pasos:")
    print("1. Ve a Railway Dashboard")
    print("2. Configura las variables de entorno:")
    print("   - DATABASE_URL")
    print("   - SECRET_KEY") 
    print("   - FLASK_ENV=production")
    print("   - OPENROUTER_API_KEY")
    print("   - PORT=5000")
    print("3. Ejecuta los scripts de verificación")
    print("4. Prueba el login en https://www.medconnect.cl")
    
    print("\n📁 Archivos desplegados:")
    for file in files_to_add:
        if os.path.exists(file):
            print(f"  ✅ {file}")
    
    return True

def check_railway_connection():
    """Verifica la conexión con Railway"""
    
    print("🔍 Verificando conexión con Railway...")
    
    try:
        # Verificar si Railway CLI está instalado
        result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI instalado")
            return True
        else:
            print("❌ Railway CLI no instalado")
            print("🔧 Instala Railway CLI: npm install -g @railway/cli")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI no encontrado")
        print("🔧 Instala Railway CLI: npm install -g @railway/cli")
        return False

def show_railway_setup_instructions():
    """Muestra instrucciones para configurar Railway"""
    
    print("\n📋 INSTRUCCIONES PARA CONFIGURAR RAILWAY:")
    print("=" * 50)
    
    print("\n1️⃣ Variables de Entorno (CRÍTICAS):")
    print("Ve a Railway Dashboard > Variables y agrega:")
    print()
    print("DATABASE_URL=postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway")
    print("SECRET_KEY=medconnect-secret-key-2025-railway-production-ultra-secure")
    print("FLASK_ENV=production")
    print("OPENROUTER_API_KEY=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")
    print("PORT=5000")
    
    print("\n2️⃣ Verificar Despliegue:")
    print("- Ve a Railway Dashboard")
    print("- Revisa los logs de despliegue")
    print("- Verifica que no haya errores")
    
    print("\n3️⃣ Probar Aplicación:")
    print("- Ve a https://www.medconnect.cl")
    print("- Prueba el login con las credenciales de prueba")
    print("- Verifica que todas las funcionalidades funcionen")

if __name__ == "__main__":
    print("🚀 DESPLIEGUE A RAILWAY - MEDCONNECT")
    print("=" * 60)
    
    # Verificar conexión con Railway
    if not check_railway_connection():
        print("\n⚠️ Railway CLI no está disponible")
        print("🔧 Instala Railway CLI primero:")
        print("   npm install -g @railway/cli")
        print("   railway login")
        print("   railway link")
        sys.exit(1)
    
    # Ejecutar despliegue
    success = deploy_to_railway()
    
    if success:
        show_railway_setup_instructions()
        print("\n🎉 ¡Despliegue completado exitosamente!")
    else:
        print("\n❌ Error en el despliegue")
        print("🔧 Revisa los errores y vuelve a intentar")
        sys.exit(1)
