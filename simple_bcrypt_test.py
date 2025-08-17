#!/usr/bin/env python3
"""
Test simple de bcrypt para diagnosticar el problema de hashes
"""

import bcrypt

def test_bcrypt_hash_validation():
    """Probar la validación de hashes bcrypt"""
    print("🔍 DIAGNÓSTICO SIMPLE: bcrypt")
    print("=" * 40)
    
    # Función is_valid_bcrypt_hash copiada de auth_manager.py
    def is_valid_bcrypt_hash(hash_string):
        """Verificar si un string es un hash bcrypt válido"""
        try:
            if not hash_string or len(hash_string) != 60:
                return False
            if not hash_string.startswith(('$2a$', '$2b$', '$2x$', '$2y$')):
                return False
            valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./$')
            if not all(c in valid_chars for c in hash_string):
                return False
            return True
        except Exception:
            return False
    
    # Función hash_password copiada de auth_manager.py
    def hash_password(password):
        """Hashear contraseña"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Probar con varias contraseñas
    test_passwords = ["MiContraseñaTest123", "password", "MedConnect2025!"]
    
    for password in test_passwords:
        print(f"\n🧪 Probando: '{password}'")
        
        try:
            # Generar hash
            hashed = hash_password(password)
            print(f"   Hash: {hashed}")
            print(f"   Longitud: {len(hashed)}")
            print(f"   Prefijo: {hashed[:4]}")
            
            # Validar hash
            is_valid = is_valid_bcrypt_hash(hashed)
            print(f"   ¿Válido?: {is_valid}")
            
            # Verificar contraseña
            verification = bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            print(f"   ¿Verifica?: {verification}")
            
            if not is_valid:
                print(f"   ❌ PROBLEMA: Hash recién creado considerado inválido")
                
                # Analizar por qué falla
                print("   🔍 Análisis:")
                if len(hashed) != 60:
                    print(f"      - Longitud incorrecta: {len(hashed)} (debe ser 60)")
                if not hashed.startswith(('$2a$', '$2b$', '$2x$', '$2y$')):
                    print(f"      - Prefijo incorrecto: {hashed[:4]}")
                
                valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./$')
                invalid_chars = set(hashed) - valid_chars
                if invalid_chars:
                    print(f"      - Caracteres inválidos: {invalid_chars}")
            else:
                print("   ✅ Hash válido")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*40)
    print("🎯 Si algún hash recién creado es 'inválido',")
    print("   ese es el problema que causa el mensaje temporal.")

if __name__ == "__main__":
    test_bcrypt_hash_validation() 