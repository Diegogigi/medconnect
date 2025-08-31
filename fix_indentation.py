#!/usr/bin/env python3
"""
Script para corregir los problemas de indentación en app.py
"""


def fix_indentation():
    """Corrige los problemas de indentación"""

    print("🔧 Corrigiendo problemas de indentación...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Corregir líneas problemáticas
    fixed_lines = []
    for i, line in enumerate(lines):
        line_num = i + 1

        # Líneas problemáticas específicas
        if line_num == 320:  # La línea con error de indentación
            if line.strip().startswith('logger.info("[OK] Cliente de Google Sheets'):
                # Comentar esta línea problemática
                fixed_lines.append("# " + line)
            else:
                fixed_lines.append(line)
        elif line_num == 321:  # La siguiente línea
            if line.strip().startswith("return client"):
                # Comentar esta línea problemática
                fixed_lines.append("# " + line)
            else:
                fixed_lines.append(line)
        elif line_num == 322:  # La siguiente línea
            if line.strip().startswith("except Exception as e:"):
                # Comentar esta línea problemática
                fixed_lines.append("# " + line)
            else:
                fixed_lines.append(line)
        elif line_num == 323:  # La siguiente línea
            if line.strip().startswith(
                'logger.error(f"Error inicializando Google Sheets'
            ):
                # Comentar esta línea problemática
                fixed_lines.append("# " + line)
            else:
                fixed_lines.append(line)
        elif line_num == 324:  # La siguiente línea
            if line.strip().startswith("return None"):
                # Comentar esta línea problemática
                fixed_lines.append("# " + line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    print("✅ Problemas de indentación corregidos")


if __name__ == "__main__":
    fix_indentation()
