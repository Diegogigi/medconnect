#!/usr/bin/env python3
"""
Script para arreglar el problema del puerto y arranque
"""


def fix_port_and_startup():
    """Arregla el problema del puerto y arranque"""

    print("🔧 Arreglando puerto y arranque...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la configuración del puerto
    old_port_config = 'PORT = int(os.environ.get("PORT", "5000"))'
    new_port_config = (
        'PORT = int(os.environ.get("PORT", "8000"))  # Default coherente con PaaS'
    )

    if old_port_config in content:
        content = content.replace(old_port_config, new_port_config)

    # Buscar el final del archivo para agregar el arranque correcto
    if 'if __name__ == "__main__":' in content:
        # Reemplazar el bloque de arranque existente
        old_startup = """if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))"""

        new_startup = """if __name__ == "__main__":
    # Usa SIEMPRE la config ya cargada (y loguea el puerto)
    logger.info(f"🌐 Binding Flask en 0.0.0.0:{app.config['PORT']}")
    app.run(host="0.0.0.0", port=app.config["PORT"])"""

        if old_startup in content:
            content = content.replace(old_startup, new_startup)
        else:
            # Buscar solo la línea de app.run
            old_run = 'app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))'
            new_run = """    # Usa SIEMPRE la config ya cargada (y loguea el puerto)
    logger.info(f"🌐 Binding Flask en 0.0.0.0:{app.config['PORT']}")
    app.run(host="0.0.0.0", port=app.config["PORT"])"""

            if old_run in content:
                content = content.replace(old_run, new_run)
    else:
        # Agregar el bloque de arranque al final
        content += """

if __name__ == "__main__":
    # Usa SIEMPRE la config ya cargada (y loguea el puerto)
    logger.info(f"🌐 Binding Flask en 0.0.0.0:{app.config['PORT']}")
    app.run(host="0.0.0.0", port=app.config["PORT"])
"""

    # Escribir el archivo actualizado
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Puerto y arranque arreglados")
    print("🔧 Ahora usa puerto 8000 por defecto (coherente con PaaS)")
    print("🔧 Logging del puerto agregado")


if __name__ == "__main__":
    fix_port_and_startup()
