#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar la hoja de Usuarios en Google Sheets
"""

import gspread
from google.oauth2.service_account import Credentials
import json

# Configuración
GOOGLE_SHEETS_ID = "1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU"

# Cargar credenciales
with open('sincere-mission-463804-h9-95d16ea62efc.json', 'r') as f:
    GOOGLE_CREDS = json.load(f)

def setup_users_sheet():
    """Configura la hoja de Usuarios en Google Sheets"""
    try:
        # Conectar con Google Sheets
        credentials = Credentials.from_service_account_info(
            GOOGLE_CREDS, 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(GOOGLE_SHEETS_ID)
        
        # Verificar si la hoja 'Usuarios' ya existe
        try:
            worksheet = spreadsheet.worksheet('Usuarios')
            print("✅ La hoja 'Usuarios' ya existe")
        except gspread.exceptions.WorksheetNotFound:
            # Crear la hoja 'Usuarios'
            worksheet = spreadsheet.add_worksheet(title='Usuarios', rows=1000, cols=15)
            print("✅ Hoja 'Usuarios' creada")
        
        # Configurar encabezados
        headers = [
            'id', 'email', 'password_hash', 'nombre', 'apellido', 
            'telefono', 'fecha_nacimiento', 'genero', 'direccion',
            'ciudad', 'fecha_registro', 'ultimo_acceso', 'estado', 
            'tipo_usuario', 'verificado'
        ]
        
        # Establecer encabezados
        worksheet.update('A1:O1', [headers])
        
        # Formatear encabezados
        worksheet.format('A1:O1', {
            'backgroundColor': {'red': 0.36, 'green': 0.24, 'blue': 0.56},
            'textFormat': {'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}, 'bold': True}
        })
        
        # Agregar datos de ejemplo
        sample_data = [
            [
                1, 'maria.gonzalez@email.com', '$2b$12$example_hash', 'María', 'González',
                '+56912345678', '1945-03-15', 'Femenino', 'Av. Providencia 123',
                'Santiago', '2024-06-23T00:00:00', '2024-06-23T01:30:00', 'activo',
                'paciente', 'true'
            ],
            [
                2, 'carlos.pinto@email.com', '$2b$12$example_hash2', 'Carlos', 'Pinto',
                '+56987654321', '1950-08-22', 'Masculino', 'Los Leones 456',
                'Santiago', '2024-06-23T00:00:00', '2024-06-23T01:00:00', 'activo',
                'profesional', 'true'
            ],
            [
                3, 'ana.silva@email.com', '$2b$12$example_hash3', 'Ana', 'Silva',
                '+56911111111', '1955-12-10', 'Femenino', 'Las Condes 789',
                'Santiago', '2024-06-23T00:00:00', '', 'activo',
                'paciente', 'false'
            ]
        ]
        
        # Agregar datos de ejemplo
        for i, row in enumerate(sample_data, start=2):
            worksheet.update(f'A{i}:O{i}', [row])
        
        print(f"✅ Configuración completada")
        print(f"📊 Hoja: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}")
        print(f"👥 {len(sample_data)} usuarios de ejemplo agregados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Configurando hoja de Usuarios...")
    setup_users_sheet() 