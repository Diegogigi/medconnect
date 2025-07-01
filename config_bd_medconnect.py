#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar específicamente la hoja bd_medconnect
"""

import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
from config import SHEETS_STANDARD_CONFIG

# Configuración
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SERVICE_ACCOUNT_FILE = 'service-account.json'
SHEET_ID = '1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU'

# Usar configuración estandarizada
SHEETS_CONFIG = SHEETS_STANDARD_CONFIG

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

def setup_bd_medconnect():
    """Configura la hoja bd_medconnect"""
    print("🚀 Configurando bd_medconnect para MedConnect")
    print("=" * 50)
    
    client = get_google_client()
    if not client:
        return False
    
    try:
        # Abrir la hoja existente
        spreadsheet = client.open_by_key(SHEET_ID)
        print(f"✅ Hoja encontrada: {spreadsheet.title}")
        print(f"📋 ID: {spreadsheet.id}")
        
        # Verificar hojas existentes
        existing_worksheets = [ws.title for ws in spreadsheet.worksheets()]
        print(f"📊 Hojas existentes: {', '.join(existing_worksheets)}")
        
        # Configurar cada hoja necesaria
        for sheet_name, columns in SHEETS_CONFIG.items():
            print(f"\n🔄 Configurando hoja '{sheet_name}'...")
            
            try:
                # Verificar si la hoja ya existe
                if sheet_name in existing_worksheets:
                    worksheet = spreadsheet.worksheet(sheet_name)
                    print(f"   ℹ️  Hoja '{sheet_name}' ya existe, actualizando encabezados...")
                else:
                    # Crear nueva hoja
                    worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(columns))
                    print(f"   ✅ Hoja '{sheet_name}' creada")
                
                # Configurar encabezados
                worksheet.clear()  # Limpiar contenido existente
                worksheet.insert_row(columns, 1)
                
                # Formatear encabezados
                header_range = f"A1:{chr(65 + len(columns) - 1)}1"
                worksheet.format(header_range, {
                    "backgroundColor": {"red": 0.36, "green": 0.24, "blue": 0.56},  # Color MedConnect
                    "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
                    "horizontalAlignment": "CENTER"
                })
                
                print(f"   ✅ Encabezados configurados ({len(columns)} columnas)")
                
            except Exception as e:
                print(f"   ❌ Error configurando '{sheet_name}': {e}")
        
        # Eliminar hoja por defecto si existe y no es necesaria
        try:
            default_sheets = ['Hoja 1', 'Sheet1', 'Hoja1']
            for default_name in default_sheets:
                if default_name in existing_worksheets and default_name not in SHEETS_CONFIG:
                    default_sheet = spreadsheet.worksheet(default_name)
                    spreadsheet.del_worksheet(default_sheet)
                    print(f"🗑️  Hoja por defecto '{default_name}' eliminada")
        except Exception as e:
            print(f"ℹ️  No se pudo eliminar hoja por defecto: {e}")
        
        # Agregar datos de ejemplo
        add_sample_data(spreadsheet)
        
        print(f"\n🎉 ¡Configuración completa!")
        print(f"📋 ID para Railway: {SHEET_ID}")
        print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando hoja: {e}")
        return False

def add_sample_data(spreadsheet):
    """Agrega datos de ejemplo"""
    print(f"\n📝 Agregando datos de ejemplo...")
    
    try:
        # Datos de ejemplo para Profesionales
        profesionales_sheet = spreadsheet.worksheet('Profesionales')
        sample_profesionales = [
            [1, 'Carlos', 'Mendoza', 'Cardiología', 'carlos.mendoza@medconnect.com', 
             '+56 9 8765 4321', 'Av. Providencia 1234', 'foto1.jpg', 'true', 'true',
             datetime.now().strftime('%Y-%m-%d'), '09:00', '18:00', 'L,M,X,J,V', 'Activo'],
            [2, 'Ana', 'Rodríguez', 'Traumatología', 'ana.rodriguez@medconnect.com',
             '+56 9 1234 5678', 'Av. Las Condes 5678', 'foto2.jpg', 'true', 'true',
             datetime.now().strftime('%Y-%m-%d'), '08:00', '17:00', 'L,M,J,V', 'Activo']
        ]
        
        for i, profesional in enumerate(sample_profesionales, start=2):
            profesionales_sheet.insert_row(profesional, i)
        print("   ✅ Datos agregados a 'Profesionales'")
        
        # Datos de ejemplo para Atenciones_Medicas
        atenciones_sheet = spreadsheet.worksheet('Atenciones_Medicas')
        sample_atenciones = [
            [1, 1, 1, '2024-03-15 10:00', 'Consulta', 'Control rutinario',
             'Hipertensión controlada', 'Mantener medicación actual', 'Paciente estable',
             'archivo1.pdf', False, 'Completada', datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            [2, 1, 2, '2024-03-15 11:00', 'Control', 'Seguimiento tratamiento',
             'Evolución favorable', 'Ajuste de medicación', 'Próximo control en 1 mes',
             'archivo2.pdf', True, 'En Seguimiento', datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        for i, atencion in enumerate(sample_atenciones, start=2):
            atenciones_sheet.insert_row(atencion, i)
        print("   ✅ Datos agregados a 'Atenciones_Medicas'")
        
        # Datos de ejemplo para Agenda
        agenda_sheet = spreadsheet.worksheet('Agenda')
        sample_agenda = [
            [1, 1, 1, '2024-03-20', '10:00', '10:30', 'Control',
             'Seguimiento tratamiento', 'Programada', 'Control mensual', False,
             datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            [2, 1, 2, '2024-03-20', '11:00', '11:30', 'Primera Vez',
             'Consulta inicial', 'Programada', '', False,
             datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        for i, cita in enumerate(sample_agenda, start=2):
            agenda_sheet.insert_row(cita, i)
        print("   ✅ Datos agregados a 'Agenda'")
        
        # Datos de ejemplo para Horarios Disponibles
        horarios_sheet = spreadsheet.worksheet('Horarios_Disponibles')
        sample_horarios = [
            [1, 1, 'Lunes', '09:00', '18:00', 30, 'Activo'],
            [2, 1, 'Martes', '09:00', '18:00', 30, 'Activo'],
            [3, 1, 'Miércoles', '09:00', '18:00', 30, 'Activo'],
            [4, 1, 'Jueves', '09:00', '18:00', 30, 'Activo'],
            [5, 1, 'Viernes', '09:00', '18:00', 30, 'Activo']
        ]
        
        for i, horario in enumerate(sample_horarios, start=2):
            horarios_sheet.insert_row(horario, i)
        print("   ✅ Datos agregados a 'Horarios_Disponibles'")
        
        # Datos de ejemplo para Especialidades
        especialidades_sheet = spreadsheet.worksheet('Especialidades')
        sample_especialidades = [
            [1, 'Cardiología', 'Especialidad en enfermedades del corazón', 'heart', 'Activo'],
            [2, 'Traumatología', 'Especialidad en sistema músculo-esquelético', 'bone', 'Activo'],
            [3, 'Pediatría', 'Especialidad en atención infantil', 'baby', 'Activo']
        ]
        
        for i, especialidad in enumerate(sample_especialidades, start=2):
            especialidades_sheet.insert_row(especialidad, i)
        print("   ✅ Datos agregados a 'Especialidades'")
        
    except Exception as e:
        print(f"   ⚠️  Algunos datos de ejemplo no se pudieron agregar: {e}")

def main():
    """Función principal"""
    print("🔧 MedConnect - Configurador Automático bd_medconnect")
    print("=" * 60)
    
    # Verificar credenciales
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            creds_data = json.load(f)
            print(f"✅ Credenciales: {creds_data.get('client_email')}")
    except Exception as e:
        print(f"❌ Error con credenciales: {e}")
        return
    
    print(f"🎯 Configurando hoja ID: {SHEET_ID}")
    
    # Configurar la hoja
    if setup_bd_medconnect():
        print(f"\n🚀 ¡Listo para Railway!")
        print(f"📝 Variable de entorno necesaria:")
        print(f"GOOGLE_SHEETS_ID={SHEET_ID}")
    else:
        print(f"\n❌ Error en la configuración")

if __name__ == "__main__":
    main() 