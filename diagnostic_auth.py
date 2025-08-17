#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para problemas de autenticación en MedConnect
"""

import os
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnosticar_credenciales():
    """Diagnosticar el estado de las credenciales de Google"""
    print("🔍 DIAGNÓSTICO DE CREDENCIALES GOOGLE")
    print("=" * 50)
    
    # 1. Verificar variables de entorno
    print("\n📋 Variables de entorno:")
    env_vars = {
        'GOOGLE_SERVICE_ACCOUNT_JSON': os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'),
        'GOOGLE_CREDENTIALS_FILE': os.environ.get('GOOGLE_CREDENTIALS_FILE'),
        'GOOGLE_SHEETS_ID': os.environ.get('GOOGLE_SHEETS_ID')
    }
    
    for var, value in env_vars.items():
        if value:
            print(f"✅ {var}: Configurada")
            if var == 'GOOGLE_SERVICE_ACCOUNT_JSON':
                try:
                    json.loads(value)
                    print("   ✅ JSON válido")
                except:
                    print("   ❌ JSON inválido")
        else:
            print(f"❌ {var}: No configurada")
    
    # 2. Verificar archivos de credenciales
    print("\n📁 Archivos de credenciales:")
    possible_files = [
        'credentials.json',
        'service-account.json',
        'google-credentials.json',
        'medconnect-credentials.json'
    ]
    
    found_files = []
    for file_path in possible_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}: Existe")
            found_files.append(file_path)
            try:
                with open(file_path, 'r') as f:
                    creds = json.load(f)
                print(f"   ✅ JSON válido")
                if 'type' in creds:
                    print(f"   📄 Tipo: {creds['type']}")
                if 'project_id' in creds:
                    print(f"   🏢 Proyecto: {creds['project_id']}")
            except Exception as e:
                print(f"   ❌ Error leyendo archivo: {e}")
        else:
            print(f"❌ {file_path}: No existe")
    
    # 3. Recomendaciones
    print("\n💡 RECOMENDACIONES:")
    if not env_vars['GOOGLE_SERVICE_ACCOUNT_JSON'] and not found_files:
        print("❌ No se encontraron credenciales")
        print("   → Crear archivo credentials.json con las credenciales de Google")
        print("   → O configurar variable GOOGLE_SERVICE_ACCOUNT_JSON")
    elif found_files:
        print("✅ Se encontraron archivos de credenciales")
        print("   → Verificar que el archivo tenga permisos correctos")
        print("   → Verificar que las credenciales sean válidas")
    elif env_vars['GOOGLE_SERVICE_ACCOUNT_JSON']:
        print("✅ Variable de entorno configurada")
        print("   → Verificar que el JSON sea válido")
        print("   → Verificar que las credenciales tengan permisos de Google Sheets")

def crear_archivo_credenciales_ejemplo():
    """Crear un archivo de credenciales de ejemplo"""
    print("\n📝 CREANDO ARCHIVO DE CREDENCIALES DE EJEMPLO")
    print("=" * 50)
    
    ejemplo_creds = {
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
            json.dump(ejemplo_creds, f, indent=2)
        print("✅ Archivo credentials.json creado")
        print("⚠️  IMPORTANTE: Reemplaza los valores con tus credenciales reales")
        print("   → Obtén las credenciales desde Google Cloud Console")
        print("   → Asegúrate de que el service account tenga permisos de Google Sheets")
    except Exception as e:
        print(f"❌ Error creando archivo: {e}")

def verificar_conectividad_google():
    """Verificar conectividad con Google Sheets"""
    print("\n🌐 VERIFICANDO CONECTIVIDAD CON GOOGLE")
    print("=" * 50)
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Intentar cargar credenciales
        if os.path.exists('credentials.json'):
            print("📄 Intentando conectar con credentials.json...")
            try:
                with open('credentials.json', 'r') as f:
                    creds_data = json.load(f)
                
                credentials = Credentials.from_service_account_info(
                    creds_data, 
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
                
                gc = gspread.authorize(credentials)
                print("✅ Conexión exitosa con Google Sheets")
                
                # Intentar abrir una hoja de prueba
                try:
                    sheets = gc.openall()
                    print(f"✅ Hojas disponibles: {len(sheets)}")
                except Exception as e:
                    print(f"⚠️  No se pudieron listar hojas: {e}")
                    
            except Exception as e:
                print(f"❌ Error conectando con Google Sheets: {e}")
        else:
            print("❌ No se encontró archivo credentials.json")
            
    except ImportError:
        print("❌ Librerías de Google no instaladas")
        print("   → Ejecuta: pip install gspread google-auth")

if __name__ == "__main__":
    print("🔧 DIAGNÓSTICO DE AUTENTICACIÓN MEDCONNECT")
    print("=" * 60)
    
    diagnosticar_credenciales()
    verificar_conectividad_google()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN:")
    print("1. Verifica que exista credentials.json con credenciales válidas")
    print("2. Asegúrate de que el service account tenga permisos de Google Sheets")
    print("3. Verifica que el ID de la hoja de cálculo sea correcto")
    print("4. Revisa los logs del servidor para más detalles")
    
    respuesta = input("\n¿Quieres crear un archivo credentials.json de ejemplo? (s/n): ")
    if respuesta.lower() == 's':
        crear_archivo_credenciales_ejemplo() 