#!/usr/bin/env python3
"""
Script para corregir la indentación en el bloque except
"""


def fix_except_indentation():
    """Corrige la indentación en el bloque except"""

    print("🔧 Corrigiendo indentación en bloque except...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir la indentación en el bloque except
    content = content.replace(
        '    except Exception as e:\n                logger.error(f"Error: {e}")\n                return jsonify({"error": "Error interno del servidor"}), 500',
        '    except Exception as e:\n        logger.error(f"[ERROR] Error importando PostgreSQL Manager: {e}")\n        postgres_db = None',
    )

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Indentación en bloque except corregida")


if __name__ == "__main__":
    fix_except_indentation()
