#!/usr/bin/env python3
"""
Script de diagnóstico para desarrollo local
"""

import os
import sys
import traceback
from dotenv import load_dotenv

def diagnosticar_problema():
    """Diagnostica problemas en el desarrollo local"""
    
    print("🔍 Diagnóstico de MedConnect - Desarrollo Local")
    print("=" * 60)
    
    # 1. Verificar variables de entorno
    print("1️⃣ Verificando variables de entorno...")
    load_dotenv("env_local.txt")
    
    variables_criticas = [
        "DATABASE_URL",
        "SECRET_KEY", 
        "FLASK_ENV",
        "PORT"
    ]
    
    for var in variables_criticas:
        valor = os.environ.get(var)
        if valor:
            print(f"  ✅ {var}: {valor[:50]}{'...' if len(valor) > 50 else ''}")
        else:
            print(f"  ❌ {var}: No configurada")
    
    # 2. Verificar dependencias
    print("\n2️⃣ Verificando dependencias...")
    dependencias = [
        "flask",
        "psycopg2", 
        "dotenv",
        "werkzeug",
        "flask_cors"
    ]
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"  ✅ {dep}: Disponible")
        except ImportError:
            print(f"  ❌ {dep}: No disponible")
    
    # 3. Verificar archivos críticos
    print("\n3️⃣ Verificando archivos críticos...")
    archivos = [
        "app.py",
        "env_local.txt",
        "setup_desarrollo_local.py",
        "run_local.py"
    ]
    
    for archivo in archivos:
        if os.path.exists(archivo):
            print(f"  ✅ {archivo}: Existe")
        else:
            print(f"  ❌ {archivo}: No existe")
    
    # 4. Intentar importar módulos de la aplicación
    print("\n4️⃣ Verificando módulos de la aplicación...")
    try:
        # Cambiar al directorio del proyecto
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Intentar importar app
        print("  🔄 Intentando importar app.py...")
        import app
        print("  ✅ app.py: Importado correctamente")
        
        # Verificar que Flask se haya inicializado
        if hasattr(app, 'app'):
            print("  ✅ Flask app: Inicializada")
            print(f"  📊 Puerto configurado: {app.app.config.get('PORT', 'No configurado')}")
        else:
            print("  ❌ Flask app: No inicializada")
            
    except Exception as e:
        print(f"  ❌ Error al importar app.py: {e}")
        print(f"  📋 Traceback: {traceback.format_exc()}")
    
    # 5. Verificar puerto
    print("\n5️⃣ Verificando puerto...")
    import socket
    
    puerto = int(os.environ.get("PORT", 8000))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    resultado = sock.connect_ex(('localhost', puerto))
    sock.close()
    
    if resultado == 0:
        print(f"  ⚠️ Puerto {puerto}: Ya está en uso")
    else:
        print(f"  ✅ Puerto {puerto}: Disponible")
    
    # 6. Recomendaciones
    print("\n6️⃣ Recomendaciones:")
    print("  💡 Si hay errores de importación, ejecuta: pip install -r requirements.txt")
    print("  💡 Si el puerto está en uso, cambia PORT en env_local.txt")
    print("  💡 Si hay errores de app.py, revisa la sintaxis del archivo")
    
    print("\n" + "=" * 60)
    print("🔍 Diagnóstico completado")

def probar_ejecucion_directa():
    """Prueba ejecutar la aplicación directamente"""
    
    print("\n🚀 Probando ejecución directa...")
    print("=" * 60)
    
    try:
        # Configurar entorno
        load_dotenv("env_local.txt")
        
        # Importar y ejecutar
        import app
        
        print("✅ Aplicación importada correctamente")
        print("🌐 Iniciando servidor...")
        print("🛑 Presiona Ctrl+C para detener")
        
        # Ejecutar la aplicación
        app.app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"❌ Error al ejecutar: {e}")
        print(f"📋 Traceback: {traceback.format_exc()}")

def main():
    """Función principal"""
    try:
        diagnosticar_problema()
        
        respuesta = input("\n¿Quieres probar ejecutar la aplicación directamente? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            probar_ejecucion_directa()
            
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
