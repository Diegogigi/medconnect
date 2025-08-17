#!/usr/bin/env python3
"""
Script para corregir exactamente el problema de llaves en la línea 4215
"""


def fix_exact_line():
    """Corrige exactamente el problema en la línea 4215"""

    print("🔧 Corrigiendo problema exacto en línea 4215...")

    # Leer el archivo
    with open("templates/professional.html", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Verificar la línea 4215 (índice 4214)
    if len(lines) > 4214:
        line_4215 = lines[4214].strip()
        print(f"📝 Línea 4215 actual: {line_4215}")

        # Buscar el patrón problemático
        if "} else {" in line_4215:
            print("🔧 Encontrado patrón problemático")

            # Buscar la línea anterior para ver el contexto
            line_4214 = lines[4213].strip()
            print(f"📝 Línea 4214: {line_4214}")

            # Verificar si la línea anterior termina con }
            if line_4214.endswith("}"):
                print("🔧 Línea anterior termina con }, agregando llave faltante")

                # Corregir la línea 4215
                lines[4214] = lines[4214].rstrip() + "\n                            }\n"
                lines[4215] = "                        } else {\n"

                print("✅ Líneas corregidas")
            else:
                print("⚠️ Línea anterior no termina con }")
        else:
            print("✅ No se encontró el patrón problemático en línea 4215")
    else:
        print("❌ El archivo no tiene suficientes líneas")
        return False

    # Guardar el archivo
    with open("templates/professional.html", "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("✅ Archivo guardado")

    # Verificar el resultado
    with open("templates/professional.html", "r", encoding="utf-8") as f:
        content = f.read()

    open_braces = content.count("{")
    close_braces = content.count("}")

    print(f"📊 Llaves de apertura: {open_braces}")
    print(f"📊 Llaves de cierre: {close_braces}")
    print(f"📊 Diferencia: {open_braces - close_braces}")

    if open_braces == close_braces:
        print("✅ Problema corregido - Las llaves están balanceadas")
        return True
    else:
        print("⚠️ Aún hay problemas de llaves desbalanceadas")
        return False


if __name__ == "__main__":
    fix_exact_line()
