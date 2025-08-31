#!/usr/bin/env python3
"""
Script para arreglar el template patient.html
"""


def fix_patient_template():
    """Arregla el template patient.html para manejar mejor la variable user"""

    print("🔧 Arreglando template patient.html...")

    # Leer el archivo templates/patient.html
    with open("templates/patient.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la línea problemática
    old_script = """    <!-- Script del usuario -->
    <script>
        // Pasar ID del usuario al JavaScript
        window.currentUserId = {% if user and user.id %}{{ user.id }}{% else %}null{% endif %};
    </script>"""

    new_script = """    <!-- Script del usuario -->
    <script>
        // Pasar ID del usuario al JavaScript con validación robusta
        window.currentUserId = {% if user and user.id is defined and user.id %}{{ user.id }}{% else %}null{% endif %};
        window.currentUserEmail = {% if user and user.email is defined and user.email %}"{{ user.email }}"{% else %}null{% endif %};
        window.currentUserName = {% if user and user.nombre is defined and user.nombre %}"{{ user.nombre }}"{% else %}null{% endif %};
        window.currentUserType = {% if user and user.tipo_usuario is defined and user.tipo_usuario %}"{{ user.tipo_usuario }}"{% else %}"paciente"{% endif %};
    </script>"""

    # Reemplazar en el contenido
    if old_script in content:
        content = content.replace(old_script, new_script)

        # Escribir el archivo actualizado
        with open("templates/patient.html", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Template patient.html arreglado")
        print("🔧 Validación robusta de variables de usuario")
    else:
        print("❌ No se encontró el script problemático")
        print("🔍 Verificando si ya está arreglado...")

        # Verificar si ya tiene la validación robusta
        if "user.id is defined" in content:
            print("✅ Ya tiene validación robusta")
        else:
            print("⚠️ Necesita configuración manual")


if __name__ == "__main__":
    fix_patient_template()
