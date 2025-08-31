#!/usr/bin/env python3
"""
Script para asegurar que Railway use el comando correcto de Gunicorn
"""


def fix_railway_startup():
    """Asegura que Railway use el comando correcto"""

    print("🔧 Asegurando comando correcto para Railway...")

    # El Procfile ya está correcto, pero vamos a simplificar start.sh
    # para que no interfiera

    simplified_start_sh = """#!/bin/bash
# Archivo de inicio para Railway - SOLO verificaciones mínimas

echo "🚀 Iniciando MedConnect..."

# Verificar solo variables críticas
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY no configurada"
    exit 1
fi

echo "✅ Variables verificadas"

# Railway debería usar Procfile automáticamente
# Si no, usar el comando directamente
exec gunicorn -k gthread -w 2 -b 0.0.0.0:$PORT app:app --timeout 120 --log-level info
"""

    # Escribir start.sh simplificado
    with open("start.sh", "w", encoding="utf-8", newline="\n") as f:
        f.write(simplified_start_sh)

    print("✅ start.sh simplificado")
    print("🔧 Ahora usa directamente el comando de Gunicorn")

    # Verificar que el Procfile esté correcto
    with open("Procfile", "r", encoding="utf-8") as f:
        procfile_content = f.read().strip()

    expected_procfile = "web: gunicorn -k gthread -w 2 -b 0.0.0.0:$PORT app:app --timeout 120 --log-level info"

    if procfile_content == expected_procfile:
        print("✅ Procfile está correcto")
    else:
        print("⚠️ Actualizando Procfile...")
        with open("Procfile", "w", encoding="utf-8") as f:
            f.write(expected_procfile)
        print("✅ Procfile actualizado")


if __name__ == "__main__":
    fix_railway_startup()
