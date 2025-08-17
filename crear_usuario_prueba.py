#!/usr/bin/env python3
"""
Script para crear un usuario de prueba en la base de datos
"""

import requests
import json

def verificar_usuarios_existentes():
    """Verifica si hay usuarios en la base de datos"""
    print("🔍 VERIFICANDO USUARIOS EXISTENTES")
    print("=" * 50)
    
    try:
        # Intentar acceder a la página de registro para ver si hay usuarios
        response = requests.get("http://localhost:5000/register", timeout=10)
        
        if response.status_code == 200:
            print("✅ Página de registro accesible")
            
            # Verificar si hay algún mensaje sobre usuarios existentes
            html_content = response.text
            if "usuario existente" in html_content.lower() or "ya registrado" in html_content.lower():
                print("💡 Parece que ya hay usuarios registrados")
                return True
            else:
                print("💡 No se detectaron usuarios existentes")
                return False
        else:
            print(f"❌ Error accediendo a registro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def crear_usuario_prueba():
    """Crea un usuario de prueba"""
    print("\n👤 CREANDO USUARIO DE PRUEBA")
    print("=" * 40)
    
    # Datos del usuario de prueba
    usuario_data = {
        'nombre': 'Profesional',
        'apellido': 'Prueba',
        'email': 'profesional.prueba@test.com',
        'password': '123456',
        'confirm_password': '123456',
        'tipo_usuario': 'profesional',
        'telefono': '123456789',
        'especialidad': 'kinesiologia'
    }
    
    try:
        print("📋 Datos del usuario:")
        for key, value in usuario_data.items():
            if key != 'password' and key != 'confirm_password':
                print(f"   {key}: {value}")
        
        # Crear usuario
        response = requests.post(
            "http://localhost:5000/register",
            data=usuario_data,
            timeout=10
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Verificar si el registro fue exitoso
            html_content = response.text
            
            if "exitoso" in html_content.lower() or "registrado" in html_content.lower():
                print("✅ Usuario creado exitosamente")
                return True
            elif "error" in html_content.lower() or "ya existe" in html_content.lower():
                print("⚠️ Usuario ya existe o hubo un error")
                print("💡 Intentando con credenciales existentes")
                return True
            else:
                print("❓ Respuesta ambigua del registro")
                print("💡 Verificando manualmente...")
                return False
        else:
            print(f"❌ Error en registro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return False

def probar_login_usuario_prueba():
    """Prueba el login con el usuario creado"""
    print("\n🔐 PROBANDO LOGIN CON USUARIO DE PRUEBA")
    print("=" * 50)
    
    session = requests.Session()
    
    # Datos de login
    login_data = {
        'email': 'profesional.prueba@test.com',
        'password': '123456',
        'tipo_usuario': 'profesional'
    }
    
    try:
        print("📋 Intentando login...")
        response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Login exitoso - Redirect recibido")
            return session
        elif response.status_code == 200:
            # Verificar contenido de la respuesta
            if "dashboard" in response.text.lower() or "professional" in response.text.lower():
                print("✅ Login exitoso - Página de dashboard detectada")
                return session
            else:
                print("❌ Login falló - Página de login detectada")
                return None
        else:
            print(f"❌ Login falló - Status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def probar_endpoint_con_usuario():
    """Prueba el endpoint de términos con el usuario autenticado"""
    print("\n🔍 PROBANDO ENDPOINT CON USUARIO AUTENTICADO")
    print("=" * 60)
    
    # Probar login
    session = probar_login_usuario_prueba()
    if not session:
        print("❌ No se pudo autenticar")
        return False
    
    # Probar endpoint
    try:
        response = session.post(
            "http://localhost:5000/api/copilot/generate-search-terms",
            json={
                'condicion': 'Dolor lumbar de 3 semanas',
                'especialidad': 'kinesiologia',
                'edad': 70
            },
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    terminos = data.get('terminos_disponibles', {})
                    print("✅ Endpoint funcionando correctamente")
                    print(f"📋 Términos generados: {len(terminos.get('terminos_recomendados', []))} recomendados")
                    return True
                else:
                    print(f"❌ Error en endpoint: {data.get('message')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print(f"Respuesta: {response.text[:200]}...")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 CONFIGURACIÓN DE USUARIO DE PRUEBA")
    print("=" * 50)
    
    # Verificar usuarios existentes
    usuarios_existen = verificar_usuarios_existentes()
    
    if not usuarios_existen:
        # Crear usuario de prueba
        usuario_creado = crear_usuario_prueba()
        if not usuario_creado:
            print("❌ No se pudo crear el usuario de prueba")
            return
    else:
        print("✅ Usuarios existentes detectados")
    
    # Probar login y endpoint
    print("\n🧪 PROBANDO FUNCIONALIDAD")
    print("=" * 30)
    
    resultado = probar_endpoint_con_usuario()
    
    if resultado:
        print("\n✅ CONFIGURACIÓN EXITOSA")
        print("💡 Ahora puedes probar en el frontend:")
        print("   1. Ve a http://localhost:5000")
        print("   2. Inicia sesión con:")
        print("      Email: profesional.prueba@test.com")
        print("      Password: 123456")
        print("      Tipo: profesional")
        print("   3. Ve a la sección de atención")
        print("   4. Llena un diagnóstico")
        print("   5. Haz clic en 'Sugerir Tratamiento con IA'")
        print("   6. Deberías ver los términos de búsqueda")
    else:
        print("\n❌ CONFIGURACIÓN FALLÓ")
        print("❌ Revisa los errores anteriores")

if __name__ == "__main__":
    main() 