#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar la columna RUT a la tabla usuarios si no existe
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_rut_column():
    """Agregar columna RUT a la tabla usuarios si no existe"""
    try:
        # Conectar a PostgreSQL usando la URL de Railway
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("❌ DATABASE_URL no está configurada")
            return False

        # Reemplazar el host interno por el externo si es necesario
        if "postgres.railway.internal" in database_url:
            database_url = database_url.replace(
                "postgres.railway.internal", "containers-us-west-146.railway.app"
            )
            logger.info("🔄 Usando URL externa de Railway")

        logger.info(f"🔗 Conectando a: {database_url[:50]}...")
        conn = psycopg2.connect(database_url)

        conn.autocommit = True
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        logger.info("🔗 Conectado a PostgreSQL")

        # Verificar si la columna RUT ya existe
        check_column_query = """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios' AND column_name = 'rut';
        """

        cursor.execute(check_column_query)
        result = cursor.fetchone()

        if result:
            logger.info("✅ La columna 'rut' ya existe en la tabla usuarios")
        else:
            logger.info("➕ Agregando columna 'rut' a la tabla usuarios...")

            # Agregar la columna RUT
            add_column_query = """
                ALTER TABLE usuarios 
                ADD COLUMN rut VARCHAR(20);
            """

            cursor.execute(add_column_query)
            logger.info("✅ Columna 'rut' agregada exitosamente")

            # Agregar comentario a la columna
            comment_query = """
                COMMENT ON COLUMN usuarios.rut IS 'RUT del usuario (formato: 12345678-9)';
            """
            cursor.execute(comment_query)
            logger.info("✅ Comentario agregado a la columna 'rut'")

        # Verificar la estructura final de la tabla
        structure_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'usuarios'
            ORDER BY ordinal_position;
        """

        cursor.execute(structure_query)
        columns = cursor.fetchall()

        logger.info("📋 Estructura actual de la tabla usuarios:")
        for col in columns:
            logger.info(
                f"   - {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})"
            )

        cursor.close()
        conn.close()

        logger.info("🎉 Proceso completado exitosamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    add_rut_column()
