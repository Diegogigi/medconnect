#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para encontrar la hoja bd_medconnect en Google Drive
"""

import gspread
from google.oauth2.service_account import Credentials
import json

# Configuración
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SERVICE_ACCOUNT_FILE = 'service-account.json'

def get_google_client():
    """Inicializa el cliente de Google Sheets"""
    try:
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, 
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"❌ Error inicializando Google Sheets: {e}")
        return None

def find_medconnect_sheet():
    """Busca la hoja bd_medconnect"""
    client = get_google_client()
    if not client:
        return None
    
    print("🔍 Buscando hojas de cálculo...")
    
    try:
        # Obtener todas las hojas de cálculo
        spreadsheets = client.openall()
        
        print(f"📊 Encontradas {len(spreadsheets)} hojas de cálculo:")
        print("-" * 60)
        
        target_sheet = None
        
        for i, sheet in enumerate(spreadsheets, 1):
            print(f"{i}. {sheet.title}")
            print(f"   ID: {sheet.id}")
            print(f"   URL: https://docs.google.com/spreadsheets/d/{sheet.id}")
            
            # Buscar específicamente bd_medconnect
            if 'bd_medconnect' in sheet.title.lower() or 'medconnect' in sheet.title.lower():
                target_sheet = sheet
                print("   ⭐ ¡Esta podría ser la hoja que buscamos!")
            
            print()
        
        if target_sheet:
            print(f"🎯 Hoja objetivo encontrada: {target_sheet.title}")
            print(f"📋 ID: {target_sheet.id}")
            return target_sheet
        else:
            print("❌ No se encontró una hoja con 'bd_medconnect' o 'medconnect' en el nombre")
            return None
            
    except Exception as e:
        print(f"❌ Error buscando hojas: {e}")
        return None

def check_sheet_structure(sheet):
    """Verifica la estructura de la hoja"""
    print(f"\n🔍 Verificando estructura de '{sheet.title}'...")
    
    try:
        # Obtener todas las hojas de trabajo
        worksheets = sheet.worksheets()
        
        print(f"📊 Hojas de trabajo encontradas ({len(worksheets)}):")
        for ws in worksheets:
            print(f"  - {ws.title} ({ws.row_count} filas x {ws.col_count} columnas)")
            
            # Mostrar encabezados si existen
            try:
                headers = ws.row_values(1)
                if headers:
                    print(f"    Encabezados: {', '.join(headers[:5])}{'...' if len(headers) > 5 else ''}")
            except:
                print("    Sin encabezados o vacía")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 MedConnect - Buscador de Hojas de Google Sheets")
    print("=" * 60)
    
    # Verificar credenciales
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            creds_data = json.load(f)
            print(f"✅ Credenciales encontradas para: {creds_data.get('client_email')}")
    except Exception as e:
        print(f"❌ Error con credenciales: {e}")
        return
    
    # Buscar la hoja
    sheet = find_medconnect_sheet()
    
    if sheet:
        # Verificar estructura
        check_sheet_structure(sheet)
        
        print(f"\n✅ Para usar esta hoja en Railway, configura:")
        print(f"GOOGLE_SHEETS_ID={sheet.id}")
        
        # Preguntar si configurar la hoja
        setup = input(f"\n¿Configurar la estructura de '{sheet.title}' para MedConnect? (s/n): ").strip().lower()
        if setup in ['s', 'si', 'sí', 'y', 'yes']:
            print("🔄 Configurando estructura...")
            # Aquí podrías llamar a la función de configuración
            print("ℹ️  Ejecuta: python setup_sheets.py y elige opción 2 con el ID mostrado arriba")
    else:
        print("\n💡 Opciones:")
        print("1. Verifica que la hoja 'bd_medconnect' esté compartida con:")
        print(f"   medconnect@sincere-mission-463804-h9.iam.gserviceaccount.com")
        print("2. O crea una nueva hoja ejecutando: python setup_sheets.py")

if __name__ == "__main__":
    main() 