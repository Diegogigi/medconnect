#!/usr/bin/env python3
"""
Script simple para desplegar a Railway usando Git
"""

import os
import subprocess
import sys
from datetime import datetime

def git_deploy_railway():
    """Despliega usando Git a Railway"""
    
    print("🚀 Desplegando a Railway con Git...")
    print("=" * 50)
    
    # 1. Verificar estado de Git
    print("\n1️⃣ Verificando estado de Git...")
    
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            print("📝 Archivos modificados encontrados:")
            print(result.stdout)
        else:
            print("✅ No hay cambios pendientes")
    except Exception as e:
        print(f"❌ Error verificando Git: {e}")
        return False
    
    # 2. Agregar todos los archivos
    print("\n2️⃣ Agregando archivos...")
    
    try:
        subprocess.run(["git", "add", "."], check=True)
        print("✅ Archivos agregados")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error agregando archivos: {e}")
        return False
    
    # 3. Crear commit
    print("\n3️⃣ Creando commit...")
    
    try:
        commit_message = f"🔧 Fix Railway login issue - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("✅ Commit creado")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando commit: {e}")
        return False
    
    # 4. Push a Railway
    print("\n4️⃣ Desplegando a Railway...")
    
    try:
        # Intentar push a origin (Railway)
        result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Despliegue exitoso a Railway")
            return True
        else:
            print(f"❌ Error en push: {result.stderr}")
            
            # Intentar con la rama actual
            current_branch = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True).stdout.strip()
            result = subprocess.run(["git", "push", "origin", current_branch], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Despliegue exitoso a Railway")
                return True
            else:
                print(f"❌ Error en push: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Error desplegando: {e}")
        return False

def show_next_steps():
    """Muestra los próximos pasos"""
    
    print("\n" + "=" * 50)
    print("🎉 DESPLIEGUE COMPLETADO")
    print("\n📋 PRÓXIMOS PASOS:")
    print("\n1️⃣ Configurar Variables en Railway:")
    print("   Ve a Railway Dashboard > Variables")
    print("   Agrega estas variables:")
    print()
    print("   DATABASE_URL=postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway")
    print("   SECRET_KEY=medconnect-secret-key-2025-railway-production-ultra-secure")
    print("   FLASK_ENV=production")
    print("   OPENROUTER_API_KEY=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")
    print("   PORT=5000")
    
    print("\n2️⃣ Verificar Despliegue:")
    print("   - Ve a Railway Dashboard")
    print("   - Revisa los logs")
    print("   - Espera 2-3 minutos para que se procese")
    
    print("\n3️⃣ Probar Aplicación:")
    print("   - Ve a https://www.medconnect.cl")
    print("   - Prueba el login")
    print("   - Verifica funcionalidades")
    
    print("\n4️⃣ Si hay problemas:")
    print("   - Revisa los logs de Railway")
    print("   - Verifica las variables de entorno")
    print("   - Ejecuta los scripts de verificación")

if __name__ == "__main__":
    print("🚀 DESPLIEGUE GIT A RAILWAY")
    print("=" * 50)
    
    success = git_deploy_railway()
    
    if success:
        show_next_steps()
    else:
        print("\n❌ Error en el despliegue")
        print("🔧 Revisa los errores y vuelve a intentar")
        sys.exit(1)
