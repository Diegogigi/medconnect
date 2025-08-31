#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir indentación en auth_manager.py
"""


def fix_indentation():
    """Corregir indentación específica"""
    print("🔧 Corrigiendo indentación en auth_manager.py...")

    try:
        with open("auth_manager.py", "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Corregir líneas específicas
        for i, line in enumerate(lines):
            if i == 56:  # línea 57 (índice 56)
                if "GOOGLE_CREDS = json.loads(credentials_json)" in line:
                    lines[i] = (
                        "                GOOGLE_CREDS = json.loads(credentials_json)\n"
                    )
                    print(f"✅ Corregida línea {i+1}")
            elif i == 57:  # línea 58 (índice 57)
                if "logger.info" in line and "Credenciales cargadas" in line:
                    lines[i] = (
                        '                logger.info("✅ Credenciales cargadas desde variable de entorno JSON")\n'
                    )
                    print(f"✅ Corregida línea {i+1}")

        with open("auth_manager.py", "w", encoding="utf-8") as f:
            f.writelines(lines)

        print("✅ Indentación corregida")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    fix_indentation()
