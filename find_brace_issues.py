#!/usr/bin/env python3
"""
Script para encontrar problemas específicos de llaves desbalanceadas
"""


def find_brace_issues():
    """Encuentra problemas específicos de llaves desbalanceadas"""

    print("🔍 Buscando problemas de llaves desbalanceadas...")

    # Leer el archivo
    with open("templates/professional.html", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Buscar patrones problemáticos
    issues = []

    for i, line in enumerate(lines):
        line_num = i + 1
        line_content = line.strip()

        # Buscar } else { sin llave de apertura
        if "} else {" in line_content:
            # Verificar contexto
            context_start = max(0, i - 3)
            context_end = min(len(lines), i + 3)
            context = lines[context_start:context_end]

            # Verificar si hay un if correspondiente
            has_if = any("if (" in ctx for ctx in context)
            if not has_if:
                issues.append(f"Línea {line_num}: }} else {{ sin if correspondiente")
                print(f"🔍 Línea {line_num}: {line_content}")
                print("   Contexto:")
                for j, ctx in enumerate(context):
                    print(f"   {context_start + j + 1}: {ctx.strip()}")
                print()

    # Buscar llaves sueltas
    brace_count = 0
    for i, line in enumerate(lines):
        line_num = i + 1
        for char in line:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count < 0:
                    issues.append(f"Línea {line_num}: Llave de cierre sin apertura")

    print(f"📊 Total de problemas encontrados: {len(issues)}")

    if issues:
        print("❌ Problemas encontrados:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ No se encontraron problemas específicos")

    return issues


if __name__ == "__main__":
    find_brace_issues()
