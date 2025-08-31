#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y corregir errores de sintaxis en app.py
"""

import ast
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_syntax(file_path):
    """Verificar sintaxis de un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Intentar parsear el código
        ast.parse(content)
        logger.info(f"✅ Sintaxis correcta en {file_path}")
        return True
        
    except SyntaxError as e:
        logger.error(f"❌ Error de sintaxis en {file_path}:")
        logger.error(f"   Línea {e.lineno}: {e.text}")
        logger.error(f"   Error: {e.msg}")
        return False
    except Exception as e:
        logger.error(f"❌ Error verificando sintaxis: {e}")
        return False

def main():
    """Función principal"""
    logger.info("🔍 Verificando sintaxis de app.py...")
    
    # Verificar app.py
    if check_syntax("app.py"):
        logger.info("🎉 app.py tiene sintaxis correcta")
    else:
        logger.error("❌ app.py tiene errores de sintaxis que deben corregirse")

if __name__ == "__main__":
    main() 