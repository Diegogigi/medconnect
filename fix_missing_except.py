#!/usr/bin/env python3
"""
Script para agregar el except faltante para el try de las importaciones
"""


def fix_missing_except():
    """Agrega el except faltante"""

    print("🔧 Agregando except faltante para el try de importaciones...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar donde agregar el except faltante
    # Después de "logger.info("[OK] Todas las importaciones completadas exitosamente")"
    # y antes de "# Configurar PostgreSQL"

    target_text = (
        '    logger.info("[OK] Todas las importaciones completadas exitosamente")'
    )
    replacement_text = """    logger.info("[OK] Todas las importaciones completadas exitosamente")

except Exception as e:
    logger.error(f"[ERROR] Error durante las importaciones: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback
    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    raise"""

    # Reemplazar
    content = content.replace(target_text, replacement_text)

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Except faltante agregado correctamente")


if __name__ == "__main__":
    fix_missing_except()
