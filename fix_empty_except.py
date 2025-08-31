#!/usr/bin/env python3
"""
Script para corregir el except vacío
"""


def fix_empty_except():
    """Corrige el except vacío"""

    print("🔧 Corrigiendo except vacío...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir el except vacío
    content = content.replace(
        """    except Exception as e:
#         logger.error(f"[ERROR] Error importando PostgreSQL Manager: {e}")
#         postgres_db = None
#          #         logger.error(f"Error: {e}")
#          #         return jsonify({"error": "Error interno del servidor"}), 500
#         logger.error(f"[ERROR] Error importando PostgreSQL Manager: {e}")
#         postgres_db = None""",
        """    except Exception as e:
        logger.error(f"[ERROR] Error importando PostgreSQL Manager: {e}")
        postgres_db = None""",
    )

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Except vacío corregido")


if __name__ == "__main__":
    fix_empty_except()
