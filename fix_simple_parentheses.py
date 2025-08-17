#!/usr/bin/env python3
"""
Script simple para corregir el problema específico de llaves en professional.html
"""


def fix_specific_issue():
    """Corrige el problema específico de llaves desbalanceadas"""

    print("🔧 Corrigiendo problema específico de llaves en professional.html...")

    # Leer el archivo
    with open("templates/professional.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Contar llaves antes
    open_braces = content.count("{")
    close_braces = content.count("}")
    print(
        f"📊 Antes - Llaves de apertura: {open_braces}, Llaves de cierre: {close_braces}"
    )

    # Buscar y corregir el patrón problemático específico
    # El problema está en la función toggleSidebar donde hay un } else { sin llave de apertura

    # Buscar el patrón específico
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Buscar la línea problemática
        if "} else {" in line and "toggleIcon" in lines[i - 1]:
            print(f"🔧 Encontrado problema en línea {i+1}")
            # Verificar si la línea anterior tiene el patrón problemático
            prev_line = lines[i - 1].strip()
            if prev_line.endswith("}"):
                # Agregar la llave de apertura faltante
                fixed_line = (
                    "                            }\n                        } else {"
                )
                print(f"🔧 Corregido patrón en línea {i+1}")
            else:
                fixed_line = line
        else:
            fixed_line = line

        fixed_lines.append(fixed_line)

    # Unir las líneas
    content_fixed = "\n".join(fixed_lines)

    # Contar llaves después
    open_braces_fixed = content_fixed.count("{")
    close_braces_fixed = content_fixed.count("}")
    print(
        f"📊 Después - Llaves de apertura: {open_braces_fixed}, Llaves de cierre: {close_braces_fixed}"
    )

    # Guardar el archivo
    with open("templates/professional.html", "w", encoding="utf-8") as f:
        f.write(content_fixed)

    print("✅ Archivo guardado")

    # Verificar si se corrigió
    if open_braces_fixed == close_braces_fixed:
        print("✅ Problema corregido - Las llaves están balanceadas")
        return True
    else:
        print("⚠️ Aún hay problemas de llaves desbalanceadas")
        return False


if __name__ == "__main__":
    fix_specific_issue()
