#!/usr/bin/env python3
"""
Diagnóstico del bug de registro - Por qué usuarios nuevos reciben mensaje de contraseña temporal
"""

import bcrypt
import logging
from auth_manager import AuthManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_bcrypt_functions():
    """Probar las funciones de bcrypt paso a paso"""
    print("🔍 DIAGNÓSTICO: Funciones de bcrypt")
    print("=" * 50)
    
    # Crear instancia de AuthManager
    try:
        auth = AuthManager()
        print("✅ AuthManager inicializado correctamente")
    except Exception as e:
        print(f"❌ Error inicializando AuthManager: {e}")
        return
    
    # Probar hash_password
    test_password = "MiContraseñaTest123"
    print(f"\n🧪 Probando hash_password con: '{test_password}'")
    
    try:
        hashed = auth.hash_password(test_password)
        print(f"✅ Hash generado: {hashed}")
        print(f"   Longitud: {len(hashed)}")
        print(f"   Comienza con: {hashed[:4]}")
        
        # Probar is_valid_bcrypt_hash inmediatamente
        is_valid = auth.is_valid_bcrypt_hash(hashed)
        print(f"   ¿Es válido según is_valid_bcrypt_hash? {is_valid}")
        
        if not is_valid:
            print("❌ ¡PROBLEMA ENCONTRADO! El hash recién creado es considerado inválido")
            print("   Esto explica por qué los usuarios nuevos reciben el mensaje temporal")
            
            # Analizar por qué falla
            print(f"\n🔍 Análisis detallado del hash:")
            print(f"   - Longitud: {len(hashed)} (debe ser 60)")
            print(f"   - Prefijo: {hashed[:4]} (debe empezar con $2a$, $2b$, $2x$ o $2y$)")
            
            # Verificar caracteres
            valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./$')
            invalid_chars = set(hashed) - valid_chars
            if invalid_chars:
                print(f"   - Caracteres inválidos encontrados: {invalid_chars}")
        else:
            print("✅ Hash considerado válido")
        
        # Probar verify_password
        verification = auth.verify_password(test_password, hashed)
        print(f"   ¿Verificación exitosa? {verification}")
        
    except Exception as e:
        print(f"❌ Error en hash_password: {e}")

def test_registration_simulation():
    """Simular el proceso completo de registro + login"""
    print("\n🎭 SIMULACIÓN: Registro + Login inmediato")
    print("=" * 50)
    
    try:
        auth = AuthManager()
        
        # Simular datos de registro
        user_data = {
            'email': 'test.diagnostico@gmail.com',
            'password': 'MiContraseñaTest123',
            'nombre': 'Usuario',
            'apellido': 'Prueba',
            'telefono': '+56912345678',
            'tipo_usuario': 'paciente'
        }
        
        print(f"📝 Simulando registro con:")
        print(f"   Email: {user_data['email']}")
        print(f"   Contraseña: {user_data['password']}")
        
        # Paso 1: Hashear contraseña (como en register_user)
        hashed_password = auth.hash_password(user_data['password'])
        print(f"\n1️⃣ Hash generado durante registro: {hashed_password}")
        
        # Paso 2: Simular lo que pasa en login_user
        print(f"\n2️⃣ Simulando login inmediato...")
        
        # Verificar si el hash sería considerado válido
        is_valid = auth.is_valid_bcrypt_hash(hashed_password)
        print(f"   ¿Hash considerado válido en login? {is_valid}")
        
        if not is_valid:
            print("❌ ¡PROBLEMA CONFIRMADO!")
            print("   El hash creado en registro es rechazado en login")
            print("   Por eso aparece el mensaje de contraseña temporal")
        else:
            # Probar verificación de contraseña
            verification = auth.verify_password(user_data['password'], hashed_password)
            print(f"   ¿Contraseña verificada correctamente? {verification}")
            
            if verification:
                print("✅ El proceso debería funcionar correctamente")
            else:
                print("❌ Problema en verify_password")
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")

def analyze_is_valid_bcrypt_hash():
    """Analizar la función is_valid_bcrypt_hash en detalle"""
    print("\n🔬 ANÁLISIS: Función is_valid_bcrypt_hash")
    print("=" * 50)
    
    try:
        auth = AuthManager()
        
        # Crear varios hashes de prueba
        test_passwords = ["password123", "test", "MedConnect2025!", "MiContraseñaTest123"]
        
        for password in test_passwords:
            print(f"\n🧪 Probando con: '{password}'")
            hashed = auth.hash_password(password)
            
            print(f"   Hash: {hashed}")
            print(f"   Longitud: {len(hashed)}")
            print(f"   Prefijo: {hashed[:4]}")
            
            # Verificar cada condición de is_valid_bcrypt_hash
            checks = {
                "No vacío": bool(hashed),
                "Longitud = 60": len(hashed) == 60,
                "Prefijo válido": hashed.startswith(('$2a$', '$2b$', '$2x$', '$2y$')),
                "Caracteres válidos": True  # Verificaremos esto por separado
            }
            
            # Verificar caracteres
            valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./$')
            invalid_chars = set(hashed) - valid_chars
            checks["Caracteres válidos"] = len(invalid_chars) == 0
            
            if invalid_chars:
                print(f"   ⚠️ Caracteres inválidos: {invalid_chars}")
            
            # Resultado final
            is_valid = auth.is_valid_bcrypt_hash(hashed)
            print(f"   Resultado is_valid_bcrypt_hash: {is_valid}")
            
            # Mostrar qué checks fallan
            failed_checks = [check for check, result in checks.items() if not result]
            if failed_checks:
                print(f"   ❌ Checks que fallan: {failed_checks}")
            else:
                print("   ✅ Todos los checks pasan")
                
    except Exception as e:
        print(f"❌ Error en análisis: {e}")

if __name__ == "__main__":
    test_bcrypt_functions()
    test_registration_simulation()
    analyze_is_valid_bcrypt_hash()
    
    print("\n" + "="*50)
    print("🎯 CONCLUSIÓN:")
    print("Si este diagnóstico muestra que los hashes recién creados")
    print("son considerados 'inválidos', entonces tenemos el bug.")
    print("La solución será corregir is_valid_bcrypt_hash o hash_password.") 