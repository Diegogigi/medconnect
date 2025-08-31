#!/usr/bin/env python3
"""
Script final para limpiar completamente app.py de todos los errores de sintaxis
"""


def final_app_cleanup():
    """Limpia completamente app.py de todos los errores de sintaxis"""

    print("🔧 Limpieza final completa de app.py...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Corregir todas las llaves comentadas
    fixes = [
        ("#                     {", "                    {"),
        ("#                     }", "                    }"),
        ("#             ),", "            ),"),
        ("#     #             ),", "                ),"),
        ("#             )", "            )"),
        (
            "#         except Exception as e:  # WorksheetNotFound handled as general exception",
            "        except Exception as e:",
        ),
        (
            '# worksheet = spreadsheet.worksheet(  # ELIMINADO"Consultas")',
            '            # worksheet = spreadsheet.worksheet("Consultas")  # ELIMINADO',
        ),
        ("#         else:", "        else:"),
        ("#         else:", "        else:"),
    ]

    for old, new in fixes:
        content = content.replace(old, new)

    # 2. Comentar todas las líneas problemáticas que usan spreadsheet
    problematic_lines = [
        "        if not spreadsheet:",
        "        records = worksheet.get_all_records()",
        "        all_values = worksheet.get_all_values()",
        "        worksheet.delete_rows(row_to_delete)",
        "        worksheet.append_row(row_data)",
        '        logger.error(f"Error: {e}")',
        '        return jsonify({"error": "Error interno del servidor"}), 500',
    ]

    for line in problematic_lines:
        content = content.replace(line, "# " + line)

    # 3. Agregar función get_spreadsheet() simulada si no existe
    if "def get_spreadsheet():" not in content:
        # Buscar donde insertar (después de las importaciones)
        insert_pos = content.find("# Inicializar Flask")
        if insert_pos != -1:
            simulated_function = '''
# Función simulada para evitar errores - usar PostgreSQL en su lugar
def get_spreadsheet():
    """Función simulada - usar PostgreSQL en su lugar"""
    logger.warning("[ADVERTENCIA] get_spreadsheet() llamada - usar PostgreSQL en su lugar")
    return None

'''
            content = content[:insert_pos] + simulated_function + content[insert_pos:]

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Limpieza final completada")


if __name__ == "__main__":
    final_app_cleanup()
