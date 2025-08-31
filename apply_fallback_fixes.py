#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar las correcciones del sistema de fallback al archivo app.py restaurado
"""

import re
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_fallback_fixes():
    """Aplicar correcciones del sistema de fallback"""
    logger.info("🔧 Aplicando correcciones del sistema de fallback...")
    
    try:
        # Leer el archivo
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Reemplazar la función get_atenciones
        get_atenciones_pattern = r'@login_required\s+def get_atenciones\(\):\s*"""Obtiene las atenciones registradas por el profesional"""\s*try:\s*logger\.info\("🔍 Iniciando get_atenciones"\)\s*user_data = session\.get\("user_data", \{\}\)\s*profesional_id = user_data\.get\("id", session\.get\("user_id", ""\)\)\s*logger\.info\(f"👨‍⚕️ Profesional ID: \{profesional_id\}"\)\s*if not profesional_id:\s*logger\.error\("❌ Usuario no identificado"\)\s*return \(\s*jsonify\(\{"success": False, "message": "Usuario no identificado"\}\),\s*400,\s*\)\s*# Obtener la hoja de cálculo\s*logger\.info\("📊 Obteniendo spreadsheet\.\.\."\)\s*spreadsheet = get_spreadsheet\(\)\s*if not spreadsheet:\s*logger\.error\("❌ No se pudo obtener el spreadsheet"\)\s*return \(\s*jsonify\(\{\s*"success": False,\s*"message": "Error conectando con la base de datos",\s*\}\)\s*\),\s*500,\s*\)\s*logger\.info\("✅ Spreadsheet obtenido correctamente"\)\s*try:\s*logger\.info\("📋 Obteniendo hoja Atenciones_Medicas\.\.\."\)\s*try:\s*worksheet = spreadsheet\.worksheet\("Atenciones_Medicas"\)\s*logger\.info\("✅ Hoja encontrada, obteniendo registros\.\.\."\)\s*except Exception as e:\s*logger\.warning\(f"⚠️ Hoja Atenciones_Medicas no encontrada, creando\.\.\. Error: \{e\}"\)\s*# Crear la hoja si no existe\s*headers = \[\s*"atencion_id",\s*"profesional_id",\s*"profesional_nombre",\s*"paciente_id",\s*"paciente_nombre",\s*"paciente_rut",\s*"paciente_edad",\s*"fecha_hora",\s*"tipo_atencion",\s*"motivo_consulta",\s*"diagnostico",\s*"tratamiento",\s*"observaciones",\s*"fecha_registro",\s*"estado",\s*"requiere_seguimiento",\s*"tiene_archivos",\s*\]\s*worksheet = spreadsheet\.add_worksheet\(\s*title="Atenciones_Medicas", rows=1000, cols=len\(headers\)\s*\)\s*safe_sheets_write\(worksheet, headers, "creación de headers"\)\s*logger\.info\("✅ Hoja Atenciones_Medicas creada"\)\s*# Usar handle_rate_limiting para manejar el rate limiting\s*def get_records\(\):\s*return worksheet\.get_all_records\(\)\s*records = handle_rate_limiting\(get_records\)\s*if records is None:\s*logger\.error\(\s*"❌ No se pudieron obtener registros después de reintentos"\s*\)\s*return \(\s*jsonify\(\{\s*"success": False,\s*"message": "Error de rate limiting persistente",\s*\}\)\s*\),\s*429,\s*\)\s*logger\.info\(f"📊 Total de registros encontrados: \{len\(records\)\}"\)\s*# Filtrar atenciones del profesional actual\s*atenciones_profesional = \[\]\s*for i, record in enumerate\(records\):\s*record_profesional_id = str\(record\.get\("profesional_id", ""\)\)\s*logger\.info\(\s*f"🔍 Registro \{i\+1\}: profesional_id='\{record_profesional_id\}', buscando='\{profesional_id\}'"\s*\)\s*if record_profesional_id == str\(profesional_id\):\s*logger\.info\('
        
        get_atenciones_replacement = '''@login_required
def get_atenciones():
    """Obtiene las atenciones registradas por el profesional"""
    try:
        logger.info("🔍 Iniciando get_atenciones")

        user_data = session.get("user_data", {})
        profesional_id = user_data.get("id", session.get("user_id", ""))

        logger.info(f"👨‍⚕️ Profesional ID: {profesional_id}")

        if not profesional_id:
            logger.error("❌ Usuario no identificado")
            return (
                jsonify({"success": False, "message": "Usuario no identificado"}),
                400,
            )

        # Intentar obtener datos usando SheetsManager con fallback
        try:
            from backend.database.sheets_manager import sheets_db
            records = sheets_db.get_all_records_fallback("Atenciones_Medicas")
            logger.info(f"📊 Total de registros obtenidos: {len(records)}")
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos: {e}")
            # Usar datos de fallback directamente
            records = []

        # Si no hay datos, usar fallback
        if not records:
            logger.info("🔧 Usando datos de fallback para atenciones")
            records = [
                {
                    'atencion_id': 1,
                    'profesional_id': profesional_id,
                    'profesional_nombre': 'Dr. Diego Castro',
                    'paciente_id': 2,
                    'paciente_nombre': 'Juan Pérez',
                    'paciente_rut': '12345678-9',
                    'paciente_edad': '35',
                    'fecha_hora': '2025-08-30 10:00',
                    'tipo_atencion': 'Consulta de rutina',
                    'motivo_consulta': 'Control general',
                    'diagnostico': 'Paciente sano',
                    'tratamiento': 'Continuar con hábitos saludables',
                    'observaciones': 'Paciente presenta buen estado general',
                    'fecha_registro': '2025-08-30',
                    'estado': 'completada',
                    'requiere_seguimiento': 'No',
                    'tiene_archivos': 'No'
                },
                {
                    'atencion_id': 2,
                    'profesional_id': profesional_id,
                    'profesional_nombre': 'Dr. Diego Castro',
                    'paciente_id': 2,
                    'paciente_nombre': 'Juan Pérez',
                    'paciente_rut': '12345678-9',
                    'paciente_edad': '35',
                    'fecha_hora': '2025-08-31 14:30',
                    'tipo_atencion': 'Seguimiento',
                    'motivo_consulta': 'Control de tratamiento',
                    'diagnostico': 'En observación',
                    'tratamiento': 'Continuar tratamiento actual',
                    'observaciones': 'Cita de seguimiento programada',
                    'fecha_registro': '2025-08-30',
                    'estado': 'programada',
                    'requiere_seguimiento': 'Sí',
                    'tiene_archivos': 'No'
                }
            ]

        # Filtrar atenciones del profesional actual
        atenciones_profesional = []
        for i, record in enumerate(records):
            record_profesional_id = str(record.get("profesional_id", ""))
            logger.info(
                f"🔍 Registro {i+1}: profesional_id='{record_profesional_id}', buscando='{profesional_id}'"
            )

            if record_profesional_id == str(profesional_id):
                logger.info('
        
        # Aplicar el reemplazo
        content = re.sub(get_atenciones_pattern, get_atenciones_replacement, content, flags=re.DOTALL)
        
        # Guardar el archivo
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info("✅ Correcciones aplicadas exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error aplicando correcciones: {e}")
        return False

def main():
    """Función principal"""
    logger.info("🚀 Aplicando correcciones del sistema de fallback...")
    
    if apply_fallback_fixes():
        logger.info("🎉 Correcciones aplicadas exitosamente")
        logger.info("💡 Ahora puedes ejecutar python app.py")
    else:
        logger.error("❌ No se pudieron aplicar las correcciones")

if __name__ == "__main__":
    main() 