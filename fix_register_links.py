#!/usr/bin/env python3
"""
Script para arreglar los enlaces de registro en el template
"""


def fix_register_links():
    """Arregla los enlaces de registro que no existen"""

    print("🔧 Arreglando enlaces de registro en template...")

    # Leer el archivo templates/index.html
    with open("templates/index.html", "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar url_for('register') por url_for('login')
    old_register_1 = '<a href="{{ url_for(\'register\') }}" class="btn-accent">'
    new_register_1 = '<a href="{{ url_for(\'login\') }}" class="btn-accent">'

    old_register_2 = '<a href="{{ url_for(\'register\') }}" class="btn-cta">'
    new_register_2 = '<a href="{{ url_for(\'login\') }}" class="btn-cta">'

    # Contar reemplazos
    count_1 = content.count(old_register_1)
    count_2 = content.count(old_register_2)

    # Realizar reemplazos
    content = content.replace(old_register_1, new_register_1)
    content = content.replace(old_register_2, new_register_2)

    # También buscar otros posibles formatos
    content = content.replace("{{ url_for('register') }}", "{{ url_for('login') }}")

    # Escribir el archivo actualizado
    with open("templates/index.html", "w", encoding="utf-8") as f:
        content = f.write(content)

    print(f"✅ Enlaces de registro arreglados:")
    print(f"   - btn-accent: {count_1} reemplazos")
    print(f"   - btn-cta: {count_2} reemplazos")
    print("🔧 Ahora todos los enlaces apuntan a /login")


if __name__ == "__main__":
    fix_register_links()
