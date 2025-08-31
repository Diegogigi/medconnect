#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para restaurar una versión funcional de app.py
"""

import shutil
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def restore_app():
    """Restaurar app.py desde un backup funcional"""
    logger.info("🔧 Restaurando app.py desde backup...")

    # Lista de backups disponibles
    backups = [
        "app_backup_SUCCESS_TOTAL.py",
        "app_backup_EXITO_TOTAL.py",
        "app_backup_PERFECCION_FINAL.py",
        "app_backup_final_success.py",
        "app_backup_final.py",
    ]

    for backup in backups:
        if os.path.exists(backup):
            logger.info(f"📁 Encontrado backup: {backup}")
            try:
                # Hacer backup del archivo actual
                if os.path.exists("app.py"):
                    shutil.copy("app.py", "app.py.broken")
                    logger.info(
                        "📁 Backup del archivo actual creado como app.py.broken"
                    )

                # Restaurar desde backup
                shutil.copy(backup, "app.py")
                logger.info(f"✅ app.py restaurado desde {backup}")
                return True

            except Exception as e:
                logger.error(f"❌ Error restaurando desde {backup}: {e}")
                continue

    logger.error("❌ No se encontraron backups válidos")
    return False


def main():
    """Función principal"""
    logger.info("🚀 Iniciando restauración de app.py...")

    if restore_app():
        logger.info("🎉 Restauración completada exitosamente")
        logger.info("💡 Ahora puedes ejecutar python app.py")
    else:
        logger.error("❌ No se pudo restaurar app.py")


if __name__ == "__main__":
    main()
 