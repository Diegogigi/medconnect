#!/usr/bin/env python3
"""
Reparar hashes vacíos/corruptos en Google Sheets
"""

import bcrypt
from auth_manager import AuthManager

def inspect_and_fix_hashes():
    """Inspeccionar y reparar todos los hashes vacíos/corruptos"""
    print("🔍 INSPECCIONAR Y REPARAR HASHES EN GOOGLE SHEETS")
    print("=" * 60)
    
    try:
        # Conectar a AuthManager
        auth = AuthManager()
        print("✅ Conectado a AuthManager")
        
        # Obtener todos los registros
        all_records = auth.users_sheet.get_all_records()
        print(f"📊 Total de usuarios encontrados: {len(all_records)}")
        
        # Contraseña temporal para usuarios sin hash
        temp_password = "MedConnect2025!"
        temp_hash = auth.hash_password(temp_password)
        
        print(f"\n🔒 Hash temporal generado: {temp_hash[:30]}...")
        
        # Inspeccionar cada usuario
        fixed_count = 0
        
        for i, record in enumerate(all_records):
            row_index = i + 2  # +2 por header y índice 0
            email = record.get('email', 'Sin email')
            stored_hash = record.get('password', '')
            
            print(f"\n👤 Usuario {i+1}: {email}")
            print(f"   Hash actual: '{stored_hash}'")
            print(f"   Longitud hash: {len(stored_hash)}")
            
            # Verificar si el hash está vacío o corrupto
            needs_fix = False
            
            if not stored_hash:
                print("   ❌ PROBLEMA: Hash completamente vacío")
                needs_fix = True
            elif len(stored_hash) < 20:
                print("   ❌ PROBLEMA: Hash demasiado corto")
                needs_fix = True
            elif not stored_hash.startswith('$'):
                print("   ❌ PROBLEMA: Hash no parece bcrypt")
                needs_fix = True
            else:
                print("   ✅ Hash parece válido")
            
            # Reparar si es necesario
            if needs_fix:
                try:
                    print(f"   🔧 REPARANDO: Aplicando hash temporal")
                    
                    # Actualizar en Google Sheets
                    cell_range = f'F{row_index}'
                    auth.users_sheet.update(cell_range, [[temp_hash]], value_input_option='RAW')
                    
                    print(f"   ✅ REPARADO: Hash actualizado en fila {row_index}")
                    print(f"   🔑 Contraseña temporal: {temp_password}")
                    fixed_count += 1
                    
                except Exception as e:
                    print(f"   ❌ ERROR reparando: {e}")
            
        print(f"\n📊 RESUMEN:")
        print(f"   Total usuarios: {len(all_records)}")
        print(f"   Usuarios reparados: {fixed_count}")
        print(f"   Contraseña temporal para reparados: {temp_password}")
        
        if fixed_count > 0:
            print(f"\n🎯 INSTRUCCIONES PARA USUARIOS:")
            print(f"   1. Usar contraseña temporal: {temp_password}")
            print(f"   2. Cambiar contraseña en el perfil después del login")
            print(f"   3. La función de cambio de contraseña ya está implementada")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

def test_hash_generation():
    """Probar que la generación de hashes funciona"""
    print("\n🧪 PROBAR GENERACIÓN DE HASHES")
    print("=" * 40)
    
    try:
        auth = AuthManager()
        
        test_passwords = ["MedConnect2025!", "test123", "password"]
        
        for password in test_passwords:
            hash_generated = auth.hash_password(password)
            print(f"Contraseña: {password}")
            print(f"Hash: {hash_generated}")
            print(f"Longitud: {len(hash_generated)}")
            
            # Verificar que el hash funciona
            verification = auth.verify_password(password, hash_generated)
            print(f"Verificación: {verification}")
            print()
            
    except Exception as e:
        print(f"❌ Error probando hashes: {e}")

if __name__ == "__main__":
    test_hash_generation()
    print("\n" + "="*60)
    
    confirm = input("¿Proceder a inspeccionar y reparar hashes? (y/N): ")
    if confirm.lower() == 'y':
        inspect_and_fix_hashes()
    else:
        print("Operación cancelada.") 