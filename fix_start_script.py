#!/usr/bin/env python3
"""
Script para arreglar start.sh para usar Gunicorn
"""


def fix_start_script():
    """Arregla start.sh para usar Gunicorn en producción"""

    print("🔧 Arreglando start.sh para usar Gunicorn...")

    # Leer el archivo start.sh
    with open("start.sh", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la línea de inicio
    old_start = '# Iniciar la aplicación\necho "🚀 Iniciando aplicación Flask..."\npython app.py'

    new_start = """# Iniciar la aplicación
echo "🚀 Iniciando aplicación con Gunicorn..."

# Verificar si Gunicorn está disponible
if command -v gunicorn &> /dev/null; then
    echo "✅ Gunicorn encontrado, iniciando en modo producción..."
    gunicorn -k gthread -w 2 -b 0.0.0.0:$PORT app:app --timeout 120 --log-level info
else
    echo "⚠️ Gunicorn no encontrado, usando Flask en modo desarrollo..."
    python app.py
fi"""

    # Reemplazar en el contenido
    if old_start in content:
        content = content.replace(old_start, new_start)

        # Escribir el archivo actualizado
        with open("start.sh", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ start.sh arreglado para usar Gunicorn")
        print("🔧 Ahora usará Gunicorn en producción")
        print("🔧 Fallback a Flask si Gunicorn no está disponible")
    else:
        print("❌ No se encontró la línea de inicio original")


if __name__ == "__main__":
    fix_start_script()
