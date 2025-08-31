#!/usr/bin/env python3
"""
Script para arreglar el arranque con Gunicorn
"""


def fix_gunicorn_startup():
    """Arregla el arranque para que funcione con Gunicorn"""

    print("🔧 Arreglando arranque para Gunicorn...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar el bloque de arranque
    old_startup = """if __name__ == "__main__":
    # Usa SIEMPRE la config ya cargada (y loguea el puerto)
    logger.info(f"🌐 Binding Flask en 0.0.0.0:{app.config['PORT']}")
    app.run(host="0.0.0.0", port=app.config["PORT"])"""

    new_startup = """if __name__ == "__main__":
    # Solo para desarrollo local (no se ejecuta con Gunicorn)
    logger.info(f"🌐 Iniciando Flask en modo desarrollo - puerto: {app.config['PORT']}")
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=True)"""

    # Reemplazar en el contenido
    if old_startup in content:
        content = content.replace(old_startup, new_startup)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Arranque arreglado para Gunicorn")
        print("🔧 Ahora Gunicorn manejará el arranque en producción")
        print("🔧 Flask.run() solo se ejecuta en desarrollo local")
    else:
        print("❌ No se encontró el bloque de arranque")


if __name__ == "__main__":
    fix_gunicorn_startup()
