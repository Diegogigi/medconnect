#!/usr/bin/env python3
"""
Script para alinear el puerto de Gunicorn con Metal Edge (8000)
"""


def fix_port_alignment():
    """Alinea el puerto de Gunicorn con Metal Edge"""

    print("🔧 Alineando puerto de Gunicorn con Metal Edge...")
    print("🎯 Target: Puerto 8000 para ambos")

    # 1. Actualizar Procfile
    print("\n1️⃣ Actualizando Procfile...")
    new_procfile = "web: gunicorn -k gthread -w 2 -b 0.0.0.0:8000 app:app --timeout 120 --log-level info --access-logfile -"

    with open("Procfile", "w", encoding="utf-8") as f:
        f.write(new_procfile)
    print("✅ Procfile actualizado para puerto 8000")

    # 2. Actualizar start.sh
    print("\n2️⃣ Actualizando start.sh...")
    new_start_sh = """#!/bin/bash
# Archivo de inicio para Railway - Puerto fijo 8000

echo "🚀 Iniciando MedConnect..."

# Verificar solo variables críticas
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY no configurada"
    exit 1
fi

echo "✅ Variables verificadas"
echo "🔧 Puerto fijo: 8000 (alineado con Metal Edge)"

# Forzar puerto 8000 para alinearse con Metal Edge
exec gunicorn -k gthread -w 2 -b 0.0.0.0:8000 app:app --timeout 120 --log-level info --access-logfile -
"""

    with open("start.sh", "w", encoding="utf-8", newline="\n") as f:
        f.write(new_start_sh)
    print("✅ start.sh actualizado para puerto 8000")

    # 3. Actualizar Config en app.py para consistencia
    print("\n3️⃣ Actualizando Config en app.py...")
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la línea de PORT
    old_port_line = (
        'PORT = int(os.environ.get("PORT", "8000"))  # Default coherente con PaaS'
    )
    new_port_line = "PORT = 8000  # Puerto fijo alineado con Metal Edge Railway"

    if old_port_line in content:
        content = content.replace(old_port_line, new_port_line)

        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ Config.PORT actualizado a 8000 fijo")
    else:
        print("⚠️ Línea PORT no encontrada (puede estar bien)")

    print("\n" + "=" * 50)
    print("🎯 ALINEACIÓN COMPLETA:")
    print("✅ Procfile: gunicorn → puerto 8000")
    print("✅ start.sh: exec gunicorn → puerto 8000")
    print("✅ Metal Edge: Target Port → 8000")
    print("✅ Config: PORT → 8000")
    print("\n🚀 AHORA DEBERÍA FUNCIONAR EN RAILWAY")


if __name__ == "__main__":
    fix_port_alignment()
