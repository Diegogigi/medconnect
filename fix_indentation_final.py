#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script definitivo para corregir indentación en auth_manager.py
"""


def fix_auth_manager_indentation():
    """Corregir indentación específica en auth_manager.py"""
    print("🔧 Corrigiendo indentación en auth_manager.py...")

    try:
        # Leer el archivo
        with open("auth_manager.py", "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Corregir líneas específicas
        fixed = False
        for i, line in enumerate(lines):
            # Línea 57 (índice 56) - debe tener 16 espacios de indentación
            if i == 56 and "GOOGLE_CREDS = json.loads(credentials_json)" in line:
                if not line.startswith("                "):  # 16 espacios
                    lines[i] = (
                        "                GOOGLE_CREDS = json.loads(credentials_json)\n"
                    )
                    print(f"✅ Corregida línea {i+1}: GOOGLE_CREDS = json.loads...")
                    fixed = True

            # Línea 58 (índice 57) - debe tener 16 espacios de indentación
            elif i == 57 and "logger.info" in line and "Credenciales cargadas" in line:
                if not line.startswith("                "):  # 16 espacios
                    lines[i] = (
                        '                logger.info("✅ Credenciales cargadas desde variable de entorno JSON")\n'
                    )
                    print(f"✅ Corregida línea {i+1}: logger.info...")
                    fixed = True

        if fixed:
            # Escribir el archivo corregido
            with open("auth_manager.py", "w", encoding="utf-8") as f:
                f.writelines(lines)
            print("✅ Archivo auth_manager.py corregido exitosamente")
        else:
            print("ℹ️ No se encontraron problemas de indentación")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def verify_syntax():
    """Verificar que el archivo tenga sintaxis correcta"""
    print("🧪 Verificando sintaxis de auth_manager.py...")

    try:
        import ast

        with open("auth_manager.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Intentar parsear el archivo
        ast.parse(content)
        print("✅ Sintaxis correcta")
        return True

    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        print(f"   Línea {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error verificando sintaxis: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando corrección de indentación...")

    if fix_auth_manager_indentation():
        if verify_syntax():
            print("🎉 ¡Corrección completada exitosamente!")
            print("💡 Ahora puedes ejecutar: python app.py")
        else:
            print("⚠️ Hay errores de sintaxis adicionales")
    else:
        print("❌ No se pudo corregir la indentación")
