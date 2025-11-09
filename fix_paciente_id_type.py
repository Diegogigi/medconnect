#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el tipo de dato de paciente_id en atenciones_medicas
Cambia de INTEGER a TEXT para soportar IDs tipo "PAC_XXXXX"

INSTRUCCIONES:
1. Sube este archivo a tu proyecto en Railway
2. Ejecuta: python fix_paciente_id_type.py
3. Verifica que se complete exitosamente
4. Reinicia tu aplicación
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_paciente_id_type():
    """Cambiar el tipo de paciente_id de INTEGER a TEXT"""
    try:
        # Conectar a la base de datos
        database_url = os.environ.get("DATABASE_URL")
        
        if not database_url:
            logger.error("❌ DATABASE_URL no configurada")
            logger.info("💡 Este script debe ejecutarse en Railway donde DATABASE_URL está configurada")
            return False
        
        logger.info("🔗 Conectando a la base de datos...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar el tipo actual de la columna
        logger.info("🔍 Verificando tipo actual de paciente_id...")
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'atenciones_medicas' 
            AND column_name = 'paciente_id'
        """)
        
        result = cursor.fetchone()
        if result:
            current_type = result['data_type']
            logger.info(f"📊 Tipo actual de paciente_id: {current_type}")
            
            if current_type == 'text' or current_type == 'character varying':
                logger.info("✅ La columna ya es de tipo TEXT, no se necesita migración")
                cursor.close()
                conn.close()
                return True
        else:
            logger.error("❌ No se encontró la columna paciente_id en atenciones_medicas")
            cursor.close()
            conn.close()
            return False
        
        # Cambiar el tipo de dato
        logger.info("🔧 Cambiando tipo de paciente_id a TEXT...")
        
        # Primero, eliminar cualquier foreign key constraint
        logger.info("🔧 Buscando y eliminando constraints...")
        cursor.execute("""
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'atenciones_medicas'
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name LIKE '%paciente%'
        """)
        
        constraints = cursor.fetchall()
        for constraint in constraints:
            constraint_name = constraint['constraint_name']
            logger.info(f"🔧 Eliminando constraint: {constraint_name}")
            cursor.execute(f"""
                ALTER TABLE atenciones_medicas 
                DROP CONSTRAINT IF EXISTS {constraint_name}
            """)
        
        # Cambiar el tipo de la columna
        logger.info("🔧 Alterando tipo de columna a TEXT...")
        cursor.execute("""
            ALTER TABLE atenciones_medicas 
            ALTER COLUMN paciente_id TYPE TEXT USING paciente_id::TEXT
        """)
        
        # Commit los cambios
        conn.commit()
        logger.info("✅ Tipo de paciente_id cambiado exitosamente a TEXT")
        
        # Verificar el cambio
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'atenciones_medicas' 
            AND column_name = 'paciente_id'
        """)
        
        result = cursor.fetchone()
        if result:
            new_type = result['data_type']
            logger.info(f"✅ Nuevo tipo de paciente_id: {new_type}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error corrigiendo tipo de paciente_id: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🔧 INICIANDO CORRECCIÓN DE TIPO DE DATO")
    logger.info("=" * 60)
    
    success = fix_paciente_id_type()
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ CORRECCIÓN COMPLETADA EXITOSAMENTE")
        logger.info("=" * 60)
    else:
        logger.error("=" * 60)
        logger.error("❌ ERROR EN LA CORRECCIÓN")
        logger.error("=" * 60)

