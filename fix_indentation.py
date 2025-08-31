#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir problemas de indentación
"""


def fix_auth_manager():
    """Corregir auth_manager.py"""
    print("🔧 Corrigiendo auth_manager.py...")

    try:
        # Leer el archivo
        with open("auth_manager.py", "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Corregir las líneas problemáticas
        fixed_lines = []
        for i, line in enumerate(lines):
            line_num = i + 1

            # Corregir línea 57 si tiene indentación incorrecta
            if line_num == 57 and not line.startswith("                "):
                if "GOOGLE_CREDS = json.loads(credentials_json)" in line:
                    fixed_lines.append(
                        "                GOOGLE_CREDS = json.loads(credentials_json)\n"
                    )
                    print(f"✅ Corregida línea {line_num}")
                    continue

            # Corregir línea 58 si tiene indentación incorrecta
            if line_num == 58 and not line.startswith("                "):
                if "logger.info" in line and "Credenciales cargadas" in line:
                    fixed_lines.append(
                        '                logger.info("✅ Credenciales cargadas desde variable de entorno JSON")\n'
                    )
                    print(f"✅ Corregida línea {line_num}")
                    continue

            fixed_lines.append(line)

        # Escribir el archivo corregido
        with open("auth_manager.py", "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)

        print("✅ auth_manager.py corregido")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    fix_auth_manager()
