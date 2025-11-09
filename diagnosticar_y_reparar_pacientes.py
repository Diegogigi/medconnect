#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico y reparación para pacientes
Verifica y corrige problemas con el campo nombre_completo
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def diagnosticar_pacientes():
    """Diagnosticar problemas con pacientes en la base de datos"""
    try:
        # Conectar a la base de datos
        database_url = os.environ.get("DATABASE_URL")
        
        if not database_url:
            logger.error("❌ DATABASE_URL no configurada")
            logger.info("💡 Este script debe ejecutarse en Railway donde DATABASE_URL está configurada")
            return False
        
        logger.info("=" * 70)
        logger.info("🔍 INICIANDO DIAGNÓSTICO DE PACIENTES")
        logger.info("=" * 70)
        logger.info("")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Verificar estructura de la tabla
        logger.info("📋 1. Verificando estructura de la tabla pacientes_profesional...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'pacientes_profesional'
            ORDER BY ordinal_position
        """)
        
        columnas = cursor.fetchall()
        logger.info(f"   ✅ Tabla tiene {len(columnas)} columnas:")
        for col in columnas:
            logger.info(f"      - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        logger.info("")
        
        # 2. Contar total de pacientes
        logger.info("📊 2. Estadísticas de pacientes...")
        cursor.execute("SELECT COUNT(*) as total FROM pacientes_profesional")
        total = cursor.fetchone()['total']
        logger.info(f"   ✅ Total de pacientes en la base de datos: {total}")
        
        # 3. Pacientes con nombre_completo vacío o NULL
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM pacientes_profesional 
            WHERE nombre_completo IS NULL OR nombre_completo = ''
        """)
        sin_nombre = cursor.fetchone()['count']
        logger.info(f"   {'⚠️' if sin_nombre > 0 else '✅'} Pacientes SIN nombre_completo: {sin_nombre}")
        
        # 4. Mostrar pacientes sin nombre
        if sin_nombre > 0:
            logger.info("")
            logger.info("   📝 Detalles de pacientes sin nombre:")
            cursor.execute("""
                SELECT paciente_id, profesional_id, rut, email, telefono, fecha_registro
                FROM pacientes_profesional 
                WHERE nombre_completo IS NULL OR nombre_completo = ''
                ORDER BY fecha_registro DESC
            """)
            pacientes_sin_nombre = cursor.fetchall()
            for p in pacientes_sin_nombre:
                logger.info(f"      - ID: {p['paciente_id']}")
                logger.info(f"        Profesional: {p['profesional_id']}")
                logger.info(f"        RUT: {p['rut'] or 'Sin RUT'}")
                logger.info(f"        Email: {p['email'] or 'Sin email'}")
                logger.info(f"        Teléfono: {p['telefono'] or 'Sin teléfono'}")
                logger.info(f"        Fecha registro: {p['fecha_registro']}")
                logger.info("")
        
        # 5. Verificar si hay duplicados
        logger.info("🔄 3. Verificando duplicados...")
        cursor.execute("""
            SELECT rut, COUNT(*) as count
            FROM pacientes_profesional
            WHERE rut IS NOT NULL AND rut != ''
            GROUP BY rut
            HAVING COUNT(*) > 1
        """)
        duplicados = cursor.fetchall()
        if duplicados:
            logger.info(f"   ⚠️ Se encontraron {len(duplicados)} RUTs duplicados:")
            for dup in duplicados:
                logger.info(f"      - RUT: {dup['rut']} ({dup['count']} veces)")
        else:
            logger.info("   ✅ No se encontraron duplicados")
        logger.info("")
        
        # 6. Verificar integridad de datos
        logger.info("🔍 4. Verificando integridad de datos...")
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE nombre_completo IS NOT NULL AND nombre_completo != '') as con_nombre,
                COUNT(*) FILTER (WHERE rut IS NOT NULL AND rut != '') as con_rut,
                COUNT(*) FILTER (WHERE email IS NOT NULL AND email != '') as con_email,
                COUNT(*) FILTER (WHERE telefono IS NOT NULL) as con_telefono,
                COUNT(*) FILTER (WHERE edad IS NOT NULL) as con_edad
            FROM pacientes_profesional
        """)
        stats = cursor.fetchone()
        logger.info(f"   ✅ Pacientes con nombre_completo: {stats['con_nombre']}/{total}")
        logger.info(f"   ✅ Pacientes con RUT: {stats['con_rut']}/{total}")
        logger.info(f"   ✅ Pacientes con email: {stats['con_email']}/{total}")
        logger.info(f"   ✅ Pacientes con teléfono: {stats['con_telefono']}/{total}")
        logger.info(f"   ✅ Pacientes con edad: {stats['con_edad']}/{total}")
        logger.info("")
        
        # 7. Mostrar los últimos 5 pacientes registrados
        logger.info("📅 5. Últimos 5 pacientes registrados:")
        cursor.execute("""
            SELECT paciente_id, nombre_completo, rut, email, fecha_registro
            FROM pacientes_profesional
            ORDER BY fecha_registro DESC
            LIMIT 5
        """)
        ultimos = cursor.fetchall()
        for p in ultimos:
            logger.info(f"   - {p['nombre_completo'] or 'SIN NOMBRE'} (RUT: {p['rut'] or 'Sin RUT'})")
            logger.info(f"     ID: {p['paciente_id']}, Fecha: {p['fecha_registro']}")
        logger.info("")
        
        cursor.close()
        conn.close()
        
        logger.info("=" * 70)
        logger.info("✅ DIAGNÓSTICO COMPLETADO")
        logger.info("=" * 70)
        logger.info("")
        
        # Preguntar si desea reparar
        if sin_nombre > 0:
            logger.info("⚠️  Se encontraron pacientes sin nombre_completo.")
            logger.info("💡 Ejecuta 'reparar_pacientes()' para corregirlos automáticamente.")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en diagnóstico: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return False


def reparar_pacientes():
    """Reparar pacientes con nombre_completo vacío"""
    try:
        database_url = os.environ.get("DATABASE_URL")
        
        if not database_url:
            logger.error("❌ DATABASE_URL no configurada")
            return False
        
        logger.info("=" * 70)
        logger.info("🔧 INICIANDO REPARACIÓN DE PACIENTES")
        logger.info("=" * 70)
        logger.info("")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar pacientes sin nombre
        cursor.execute("""
            SELECT paciente_id, rut, email
            FROM pacientes_profesional
            WHERE nombre_completo IS NULL OR nombre_completo = ''
        """)
        
        pacientes_sin_nombre = cursor.fetchall()
        
        if not pacientes_sin_nombre:
            logger.info("✅ No hay pacientes sin nombre para reparar")
            cursor.close()
            conn.close()
            return True
        
        logger.info(f"🔧 Reparando {len(pacientes_sin_nombre)} pacientes...")
        logger.info("")
        
        reparados = 0
        for p in pacientes_sin_nombre:
            nombre_generado = None
            
            # Intentar generar nombre desde email
            if p['email']:
                nombre_generado = p['email'].split('@')[0].replace('.', ' ').title()
            # O desde RUT
            elif p['rut']:
                nombre_generado = f"Paciente RUT {p['rut']}"
            # O desde ID
            else:
                nombre_generado = f"Paciente {p['paciente_id']}"
            
            # Actualizar
            cursor.execute("""
                UPDATE pacientes_profesional
                SET nombre_completo = %s
                WHERE paciente_id = %s
            """, (nombre_generado, p['paciente_id']))
            
            reparados += 1
            logger.info(f"   ✅ Reparado: {p['paciente_id']} -> {nombre_generado}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"✅ REPARACIÓN COMPLETADA: {reparados} pacientes actualizados")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en reparación: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    # Ejecutar diagnóstico
    success = diagnosticar_pacientes()
    
    if success:
        logger.info("")
        logger.info("💡 Para reparar pacientes sin nombre, ejecuta:")
        logger.info("   python -c 'from diagnosticar_y_reparar_pacientes import reparar_pacientes; reparar_pacientes()'")

