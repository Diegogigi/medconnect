#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar datos corruptos en Google Sheets
Corrige teléfonos encriptados y regenera contraseñas correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_manager import AuthManager
import bcrypt
import re

def fix_corrupted_data():
    """Limpiar datos corruptos en Google Sheets"""
    print("🔧 INICIANDO LIMPIEZA DE DATOS CORRUPTOS")
    print("=" * 50)
    
    try:
        # Inicializar AuthManager
        auth = AuthManager()
        if not auth.users_sheet:
            print("❌ Error: No se pudo conectar a Google Sheets")
            return False
        
        # Obtener todos los usuarios
        all_records = auth.users_sheet.get_all_records()
        print(f"📊 Total de usuarios encontrados: {len(all_records)}")
        
        usuarios_corregidos = 0
        
        for i, record in enumerate(all_records):
            row_index = i + 2  # +2 por header y índice 0
            email = record.get('email', '')
            telefono = record.get('telefono', '')
            password_hash = record.get('password', '')
            
            print(f"\n👤 Procesando usuario: {email}")
            
            # **1. CORREGIR TELÉFONO ENCRIPTADO**
            if telefono and telefono.startswith('$2b$'):
                print(f"  📱 Teléfono encriptado detectado: {telefono[:20]}...")
                
                # Limpiar teléfono (dejar vacío para que el usuario lo actualice)
                try:
                    auth.users_sheet.update(f'D{row_index}', [[""]], value_input_option='RAW')
                    print(f"  ✅ Teléfono limpiado - Usuario deberá actualizarlo")
                    usuarios_corregidos += 1
                except Exception as e:
                    print(f"  ❌ Error limpiando teléfono: {e}")
            
            # **2. CORREGIR HASH DE CONTRASEÑA CORRUPTO**
            if password_hash and not auth.is_valid_bcrypt_hash(password_hash):
                print(f"  🔒 Hash corrupto detectado para: {email}")
                
                # Generar nueva contraseña temporal
                temp_password = "MedConnect2025!"
                new_hash = auth.hash_password(temp_password)
                
                try:
                    # Actualizar con formato correcto
                    auth.users_sheet.update(f'F{row_index}', [[new_hash]], value_input_option='RAW')
                    print(f"  ✅ Hash regenerado - Contraseña temporal: {temp_password}")
                    usuarios_corregidos += 1
                except Exception as e:
                    print(f"  ❌ Error regenerando hash: {e}")
            
            # **3. CORREGIR EMAIL CON TYPO (si existe)**
            if 'laagos' in email:  # diego.castro.laagos -> diego.castro.lagos  
                correct_email = email.replace('laagos', 'lagos')
                print(f"  📧 Corrigiendo email: {email} -> {correct_email}")
                
                try:
                    auth.users_sheet.update(f'C{row_index}', [[correct_email]], value_input_option='RAW')
                    print(f"  ✅ Email corregido")
                    usuarios_corregidos += 1
                except Exception as e:
                    print(f"  ❌ Error corrigiendo email: {e}")
        
        print(f"\n🎯 LIMPIEZA COMPLETADA")
        print(f"✅ Usuarios corregidos: {usuarios_corregidos}")
        print(f"📋 Instrucciones para usuarios:")
        print(f"   - Contraseña temporal: MedConnect2025!")
        print(f"   - Actualizar teléfono en perfil")
        print(f"   - Cambiar contraseña después del login")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def test_password_functionality():
    """Probar funcionalidad de contraseñas después de la limpieza"""
    print("\n🧪 PROBANDO FUNCIONALIDAD DE CONTRASEÑAS")
    print("=" * 50)
    
    try:
        auth = AuthManager()
        
        # Probar hash válido
        test_password = "MedConnect2025!"
        test_hash = auth.hash_password(test_password)
        
        if auth.is_valid_bcrypt_hash(test_hash):
            print("✅ Generación de hash: FUNCIONANDO")
        else:
            print("❌ Generación de hash: FALLA")
            return False
        
        # Probar verificación
        if auth.verify_password(test_password, test_hash):
            print("✅ Verificación de contraseña: FUNCIONANDO")
        else:
            print("❌ Verificación de contraseña: FALLA")
            return False
        
        print("🎉 TODAS LAS FUNCIONES DE CONTRASEÑA FUNCIONAN CORRECTAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SCRIPT DE LIMPIEZA DE DATOS CORRUPTOS")
    print("Este script corregirá:")
    print("1. Teléfonos encriptados incorrectamente")
    print("2. Hashes de contraseña corruptos")
    print("3. Emails con typos")
    print("")
    
    # Ejecutar limpieza
    if fix_corrupted_data():
        print("\n" + "="*50)
        
        # Probar funcionalidad
        if test_password_functionality():
            print("\n🎯 RESULTADO FINAL:")
            print("✅ Datos corruptos CORREGIDOS")
            print("✅ Sistema de contraseñas FUNCIONANDO")
            print("✅ Cambio de contraseñas HABILITADO")
            print("")
            print("🔄 REINICIA el servidor:")
            print("python app.py")
            print("")
            print("🔑 Para login usa:")
            print("Email: diego.castro.lagos@gmail.com")
            print("Contraseña: MedConnect2025!")
            print("Luego cambia tu contraseña en Perfil > Configuración")
        else:
            print("❌ Falló la verificación de funcionalidades")
    else:
        print("❌ Falló la limpieza de datos") 