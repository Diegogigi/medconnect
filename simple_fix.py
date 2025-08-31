#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para aplicar correcciones del sistema de fallback
"""

import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Función principal"""
    logger.info("🚀 Aplicando correcciones simples...")

    # Verificar que el archivo existe
    if not os.path.exists("app.py"):
        logger.error("❌ app.py no encontrado")
        return

    # Verificar sintaxis
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar que se puede importar
        exec(compile(content, "app.py", "exec"))
        logger.info("✅ app.py tiene sintaxis correcta")

        # Probar la aplicación
        logger.info("🧪 Probando la aplicación...")
        os.system("python app.py")

    except SyntaxError as e:
        logger.error(f"❌ Error de sintaxis: {e}")
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
