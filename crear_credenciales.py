#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear archivo de credenciales de ejemplo
"""

import json
import os

def crear_archivo_credenciales():
    """Crear archivo credentials.json de ejemplo"""
    
    credenciales_ejemplo = {
        "type": "service_account",
        "project_id": "tu-proyecto-id",
        "private_key_id": "tu-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nTU_PRIVATE_KEY_AQUI\n-----END PRIVATE KEY-----\n",
        "client_email": "tu-service-account@tu-proyecto.iam.gserviceaccount.com",
        "client_id": "tu-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tu-service-account%40tu-proyecto.iam.gserviceaccount.com"
    }
    
    try:
        with open('credentials.json', 'w') as f:
            json.dump(credenciales_ejemplo, f, indent=2)
        
        print("✅ Archivo credentials.json creado exitosamente")
        print("\n⚠️  IMPORTANTE:")
        print("1. Reemplaza los valores con tus credenciales reales de Google")
        print("2. Obtén las credenciales desde Google Cloud Console")
        print("3. Asegúrate de que el service account tenga permisos de Google Sheets")
        print("4. Comparte tu hoja de cálculo con el email del service account")
        
        return True
    except Exception as e:
        print(f"❌ Error creando archivo: {e}")
        return False

if __name__ == "__main__":
    print("🔧 CREANDO ARCHIVO DE CREDENCIALES")
    print("=" * 50)
    
    if crear_archivo_credenciales():
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Editar credentials.json con tus credenciales reales")
        print("2. Reiniciar la aplicación")
        print("3. Probar autenticación")
    else:
        print("\n❌ No se pudo crear el archivo") 