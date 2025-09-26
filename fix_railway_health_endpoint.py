#!/usr/bin/env python3
"""
Script para solucionar el problema del endpoint /api/health en Railway
"""


def fix_railway_health_endpoint():
    """Soluciona el problema del endpoint de health en Railway"""

    print("🔧 Solucionando endpoint /api/health en Railway...")
    print("=" * 60)

    # Crear endpoint de health mejorado
    health_endpoint_code = '''@app.route("/api/health", methods=["GET"])
def api_health():
    """Endpoint de health check para Railway"""
    try:
        # Verificar estado de la base de datos
        db_status = "disconnected"
        db_mode = "unknown"
        
        if postgres_db and postgres_db.is_connected():
            db_status = "connected"
            db_mode = "postgresql"
        elif auth_manager and hasattr(auth_manager, 'use_fallback') and auth_manager.use_fallback:
            db_status = "fallback"
            db_mode = "simulated"
        else:
            db_status = "disconnected"
            db_mode = "unknown"
        
        # Información del sistema
        health_data = {
            "status": "healthy" if db_status in ["connected", "fallback"] else "unhealthy",
            "database": db_mode,
            "mode": "production",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - start_time if 'start_time' in globals() else 0,
            "version": "1.0.0",
            "environment": os.environ.get("FLASK_ENV", "production"),
            "railway": True
        }
        
        status_code = 200 if health_data["status"] == "healthy" else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"❌ Error en health check: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """Endpoint de health check simple para Railway"""
    try:
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
'''

    with open("health_endpoint_fix.py", "w", encoding="utf-8") as f:
        f.write(health_endpoint_code)

    print("✅ Código del endpoint de health creado")

    # Crear script de verificación de login
    print("\n🔍 Creando script de verificación de login...")

    login_test_script = '''#!/usr/bin/env python3
"""
Script para probar el login en la versión oficial de Railway
"""

import requests
import json

def test_railway_login():
    """Prueba el login en la versión oficial de Railway"""
    
    print("🧪 Probando login en Railway...")
    print("=" * 50)
    
    # URL de login
    login_url = "https://www.medconnect.cl/login"
    
    # Datos de prueba
    test_credentials = [
        {
            "email": "diego.castro.lagos@gmail.com",
            "password": "password123",
            "expected_type": "profesional"
        },
        {
            "email": "rodrigoandressilvabreve@gmail.com", 
            "password": "password123",
            "expected_type": "paciente"
        }
    ]
    
    for creds in test_credentials:
        print(f"\\n🔐 Probando login con: {creds['email']}")
        
        try:
            # Crear sesión
            session = requests.Session()
            
            # Obtener página de login
            response = session.get(login_url)
            
            if response.status_code != 200:
                print(f"  ❌ Error obteniendo página de login: {response.status_code}")
                continue
            
            print(f"  ✅ Página de login cargada correctamente")
            
            # Intentar login
            login_data = {
                "email": creds["email"],
                "password": creds["password"]
            }
            
            login_response = session.post(login_url, data=login_data, allow_redirects=False)
            
            print(f"  📊 Status del login: {login_response.status_code}")
            
            if login_response.status_code == 302:
                redirect_url = login_response.headers.get('Location', '')
                print(f"  ✅ Login exitoso - Redirigiendo a: {redirect_url}")
                
                # Verificar redirección
                if "/professional" in redirect_url:
                    print(f"  ✅ Redirección correcta para profesional")
                elif "/patient" in redirect_url:
                    print(f"  ✅ Redirección correcta para paciente")
                else:
                    print(f"  ⚠️ Redirección inesperada: {redirect_url}")
                    
            elif login_response.status_code == 200:
                # Verificar si hay mensaje de error en el HTML
                if "Credenciales inválidas" in login_response.text:
                    print(f"  ❌ Login fallido - Credenciales inválidas")
                elif "Error" in login_response.text:
                    print(f"  ❌ Login fallido - Error en el sistema")
                else:
                    print(f"  ⚠️ Login no procesado correctamente")
            else:
                print(f"  ❌ Error inesperado: {login_response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error probando login: {e}")
    
    print("\\n" + "=" * 50)
    print("📋 Resumen de pruebas:")
    print("1. Si todos los logins son exitosos: ✅ Sistema funcionando")
    print("2. Si hay errores de credenciales: ❌ Usuarios no existen en BD")
    print("3. Si hay errores 500: ❌ Problema de configuración")
    print("4. Si hay timeouts: ⏰ Aplicación no responde")

if __name__ == "__main__":
    test_railway_login()
'''

    with open("test_railway_login.py", "w", encoding="utf-8") as f:
        f.write(login_test_script)

    print("✅ Script de prueba de login creado")

    # Crear instrucciones finales
    print("\n📋 Creando instrucciones finales...")

    final_instructions = """# 🚀 SOLUCIÓN FINAL PROBLEMA LOGIN RAILWAY

## 🎯 **PROBLEMA IDENTIFICADO:**
La aplicación en Railway funciona pero:
1. ❌ Endpoint /api/health no existe (404)
2. ❌ Posible problema de autenticación con base de datos
3. ❌ Usuarios de prueba no existen en PostgreSQL

## ✅ **SOLUCIÓN COMPLETA:**

### **Paso 1: Configurar Variables en Railway Dashboard**
Copia estas variables exactas en Railway > Variables:

```
DATABASE_URL=postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway
SECRET_KEY=medconnect-secret-key-2025-railway-production-ultra-secure
FLASK_ENV=production
OPENROUTER_API_KEY=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
PORT=5000
```

### **Paso 2: Agregar Endpoint de Health**
1. Agrega el código de `health_endpoint_fix.py` a tu `app.py`
2. Esto solucionará el error 404 en /api/health

### **Paso 3: Verificar Base de Datos**
1. Ejecuta: `python verify_railway_db.py`
2. Verifica que PostgreSQL esté conectado
3. Verifica que existan las tablas

### **Paso 4: Migrar Usuarios de Prueba**
1. Ejecuta: `python migrate_test_users.py`
2. Esto creará los usuarios de prueba

### **Paso 5: Probar Login**
1. Ejecuta: `python test_railway_login.py`
2. Esto probará el login automáticamente

### **Paso 6: Verificar Funcionamiento**
1. Ve a https://www.medconnect.cl/login
2. Intenta login con:
   - Email: diego.castro.lagos@gmail.com
   - Password: password123

## 🔍 **VERIFICACIÓN FINAL:**
- ✅ Variables configuradas en Railway
- ✅ Endpoint /api/health funcionando
- ✅ Base de datos PostgreSQL conectada
- ✅ Usuarios de prueba creados
- ✅ Login funcionando correctamente

## 🚨 **IMPORTANTE:**
- Guarda las credenciales de la base de datos
- No compartas las variables de entorno
- Haz backup regular de la base de datos
"""

    with open("SOLUCION_FINAL_RAILWAY.md", "w", encoding="utf-8") as f:
        f.write(final_instructions)

    print("✅ Instrucciones finales creadas")

    print("\n" + "=" * 60)
    print("🎉 Solución completa creada")
    print("\n📁 Archivos creados:")
    print("  - health_endpoint_fix.py")
    print("  - test_railway_login.py")
    print("  - SOLUCION_FINAL_RAILWAY.md")
    print("\n🔧 Próximos pasos:")
    print("1. Configura las variables en Railway Dashboard")
    print("2. Agrega el endpoint de health a app.py")
    print("3. Ejecuta los scripts de verificación")
    print("4. Prueba el login en https://www.medconnect.cl")


if __name__ == "__main__":
    fix_railway_health_endpoint()
