#!/usr/bin/env python3
"""
Script para corregir el bloque except problemático
"""


def fix_except_block():
    """Corrige el bloque except problemático"""

    print("🔧 Corrigiendo bloque except problemático...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir el bloque except problemático
    content = content.replace(
        """        except Exception as e:
        logger.error(f"[ERROR] Error importando PostgreSQL Manager: {e}")
        postgres_db = None""",
        """        except Exception as e:
            logger.error(f"[ERROR] Error importando PostgreSQL Manager: {e}")
            postgres_db = None""",
    )

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Bloque except corregido")


if __name__ == "__main__":
    fix_except_block()
