#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir problemas de esquema de base de datos
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_database_schema():
    """Corregir problemas de esquema de base de datos"""

    # Obtener DATABASE_URL del entorno
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("❌ DATABASE_URL no encontrada en variables de entorno")
        return False
    
    # Reemplazar host interno de Railway con host externo
    if "postgres.railway.internal" in database_url:
        database_url = database_url.replace("postgres.railway.internal", "containers-us-west-146.railway.app")
        logger.info("🔄 Usando URL externa de Railway")

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        logger.info("✅ Conectado a la base de datos")

        # 1. Agregar columnas faltantes a usuarios
        logger.info("🔧 Agregando columnas faltantes a tabla usuarios...")

        alter_queries = [
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS activo BOOLEAN DEFAULT true;",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS rut TEXT;",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS edad INTEGER;",
        ]

        for query in alter_queries:
            try:
                cursor.execute(query)
                logger.info(f"✅ Ejecutado: {query}")
            except Exception as e:
                logger.warning(f"⚠️ Error ejecutando {query}: {e}")

        # 2. Corregir tipos de datos
        logger.info("🔧 Corregiendo tipos de datos...")

        type_queries = [
            "ALTER TABLE usuarios ALTER COLUMN telefono TYPE TEXT USING telefono::TEXT;",
            "ALTER TABLE pacientes_profesional ALTER COLUMN profesional_id TYPE BIGINT USING CASE WHEN profesional_id THEN 1 ELSE 0 END;",
            "ALTER TABLE pacientes_profesional ALTER COLUMN telefono TYPE TEXT USING telefono::TEXT;",
        ]

        for query in type_queries:
            try:
                cursor.execute(query)
                logger.info(f"✅ Ejecutado: {query}")
            except Exception as e:
                logger.warning(f"⚠️ Error ejecutando {query}: {e}")

        # 3. Definir estructura de tabla pacientes si está vacía
        logger.info("🔧 Verificando tabla pacientes...")

        cursor.execute(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'pacientes'
            ORDER BY ordinal_position;
        """
        )
        columns = cursor.fetchall()

        if not columns:
            logger.info("🔧 Creando estructura para tabla pacientes...")
            create_pacientes_query = """
                CREATE TABLE IF NOT EXISTS pacientes (
                    id SERIAL PRIMARY KEY,
                    usuario_id BIGINT REFERENCES usuarios(id),
                    fecha_nacimiento DATE,
                    genero TEXT,
                    telefono TEXT,
                    direccion TEXT,
                    antecedentes_medicos TEXT,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            try:
                cursor.execute(create_pacientes_query)
                logger.info("✅ Tabla pacientes creada con estructura correcta")
            except Exception as e:
                logger.warning(f"⚠️ Error creando tabla pacientes: {e}")
        else:
            logger.info(f"ℹ️ Tabla pacientes ya tiene {len(columns)} columnas")

        # 4. Verificar estructura final
        logger.info("🔍 Verificando estructura final...")

        # Verificar usuarios
        cursor.execute(
            """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios'
            ORDER BY ordinal_position;
        """
        )
        usuarios_columns = cursor.fetchall()
        logger.info(f"📋 Tabla usuarios tiene {len(usuarios_columns)} columnas:")
        for col in usuarios_columns:
            logger.info(f"  - {col['column_name']}: {col['data_type']}")

        # Verificar pacientes_profesional
        cursor.execute(
            """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'pacientes_profesional'
            ORDER BY ordinal_position;
        """
        )
        pacientes_prof_columns = cursor.fetchall()
        logger.info(
            f"📋 Tabla pacientes_profesional tiene {len(pacientes_prof_columns)} columnas:"
        )
        for col in pacientes_prof_columns:
            logger.info(f"  - {col['column_name']}: {col['data_type']}")

        # Commit cambios
        conn.commit()
        logger.info("✅ Todos los cambios guardados en la base de datos")

        return True

    except Exception as e:
        logger.error(f"❌ Error corrigiendo esquema: {e}")
        if "conn" in locals():
            conn.rollback()
        return False

    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    logger.info("🚀 Iniciando corrección de esquema de base de datos...")
    success = fix_database_schema()

    if success:
        logger.info("✅ Corrección de esquema completada exitosamente")
    else:
        logger.error("❌ Error en la corrección de esquema")
