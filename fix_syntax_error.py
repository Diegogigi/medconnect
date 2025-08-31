#!/usr/bin/env python3
"""
Script para corregir el error de sintaxis en app.py
"""


def fix_syntax_error():
    """Corrige el error de sintaxis en app.py"""

    print("🔧 Corrigiendo error de sintaxis en app.py...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir el bloque try-except mal estructurado
    # Buscar el patrón problemático
    problematic_pattern = """except Exception as e:
    logger.error(f"[ERROR] Error durante las importaciones: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback

    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    raise"""

    fixed_pattern = """    except Exception as e:
        logger.error(f"[ERROR] Error cargando Copilot Health: {e}")

except Exception as e:
    logger.error(f"[ERROR] Error durante las importaciones: {e}")
    logger.error(f"[ERROR] Tipo de error: {type(e).__name__}")
    import traceback

    logger.error(f"[ERROR] Traceback completo: {traceback.format_exc()}")
    raise"""

    # Reemplazar
    content = content.replace(problematic_pattern, fixed_pattern)

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Error de sintaxis corregido en app.py")


if __name__ == "__main__":
    fix_syntax_error()
