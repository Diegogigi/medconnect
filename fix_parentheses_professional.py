#!/usr/bin/env python3
"""
Script para corregir problemas de paréntesis y llaves desbalanceadas en professional.html
"""

import re


def fix_parentheses_issues():
    """Corrige problemas de paréntesis y llaves desbalanceadas"""

    print("🔧 Corrigiendo problemas de paréntesis en professional.html...")

    # Leer el archivo
    with open("templates/professional.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Contar llaves de apertura y cierre
    open_braces = content.count("{")
    close_braces = content.count("}")

    print(f"📊 Llaves de apertura: {open_braces}")
    print(f"📊 Llaves de cierre: {close_braces}")
    print("📊 Diferencia: " + str(open_braces - close_braces))

    # Buscar el problema específico en la función toggleSidebar
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Buscar el patrón problemático: } else { sin llave de apertura
        if "} else {" in line and i > 0:
            # Verificar si la línea anterior termina con }
            prev_line = lines[i - 1].strip()
            if prev_line.endswith("}"):
                # Verificar si falta una llave de apertura
                # Buscar el if correspondiente
                found_if = False
                for j in range(i - 1, max(0, i - 10), -1):
                    if "if (" in lines[j] and "isVisible" in lines[j]:
                        found_if = True
                        break
                    elif "if (" in lines[j]:
                        break

                if found_if:
                    # Agregar la llave de apertura faltante
                    fixed_line = line.replace("} else {", "} else {")
                    print(f"🔧 Línea {i+1}: Corregido patrón problemático")
                else:
                    fixed_line = line
            else:
                fixed_line = line
        else:
            fixed_line = line

        fixed_lines.append(fixed_line)

    # Buscar específicamente el problema en la función toggleSidebar
    content_fixed = "\n".join(fixed_lines)

    # Buscar el patrón específico problemático
    pattern = r"(\s+if \(toggleIcon\) \{[^}]*\})\s+} else \{"
    replacement = r"\1\n                            }\n                        } else {"

    content_fixed = re.sub(pattern, replacement, content_fixed, flags=re.DOTALL)

    # Verificar si se corrigió
    open_braces_fixed = content_fixed.count("{")
    close_braces_fixed = content_fixed.count("}")

    print(f"📊 Después de corrección:")
    print(f"📊 Llaves de apertura: {open_braces_fixed}")
    print(f"📊 Llaves de cierre: {close_braces_fixed}")
    print(f"📊 Diferencia: {open_braces_fixed - close_braces_fixed}")

    # Guardar el archivo corregido
    with open("templates/professional.html", "w", encoding="utf-8") as f:
        f.write(content_fixed)

    print("✅ Archivo corregido y guardado")

    # Verificar si hay otros problemas
    if open_braces_fixed != close_braces_fixed:
        print("⚠️ Aún hay problemas de llaves desbalanceadas")
        return False
    else:
        print("✅ Todas las llaves están balanceadas")
        return True


def verify_syntax():
    """Verifica la sintaxis del archivo"""

    print("\n🔍 Verificando sintaxis...")

    with open("templates/professional.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar patrones problemáticos
    problems = []

    # Buscar } else { sin llave de apertura
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "} else {" in line:
            # Verificar contexto
            context_start = max(0, i - 5)
            context_end = min(len(lines), i + 5)
            context = lines[context_start:context_end]

            # Verificar si hay un if correspondiente
            has_if = any("if (" in ctx for ctx in context)
            if not has_if:
                problems.append(
                    "Línea {}: }} else {{ sin if correspondiente".format(i + 1)
                )

    if problems:
        print("❌ Problemas encontrados:")
        for problem in problems:
            print(f"   - {problem}")
        return False
    else:
        print("✅ No se encontraron problemas de sintaxis")
        return True


if __name__ == "__main__":
    print("🔧 Iniciando corrección de paréntesis en professional.html")
    print("=" * 60)

    success = fix_parentheses_issues()

    if success:
        verify_syntax()
        print("\n✅ Corrección completada exitosamente")
    else:
        print("\n❌ La corrección no fue completamente exitosa")
