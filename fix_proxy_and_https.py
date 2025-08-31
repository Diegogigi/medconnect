#!/usr/bin/env python3
"""
Script para agregar ProxyFix y mejorar configuración HTTPS
"""


def fix_proxy_and_https():
    """Agrega ProxyFix y mejora configuración HTTPS"""

    print("🔧 Agregando ProxyFix y configuración HTTPS...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Agregar import de ProxyFix
    if "from werkzeug.middleware.proxy_fix import ProxyFix" not in content:
        # Buscar la línea después de los imports de Flask
        flask_imports = "from flask import ("
        if flask_imports in content:
            # Encontrar el final de los imports de Flask
            start_pos = content.find(flask_imports)
            end_pos = content.find(")", start_pos) + 1

            # Agregar ProxyFix después de los imports de Flask
            before_imports = content[:end_pos]
            after_imports = content[end_pos:]

            proxy_import = """
from werkzeug.middleware.proxy_fix import ProxyFix"""

            content = before_imports + proxy_import + after_imports

    # Buscar donde se crea la app Flask
    app_creation = "app = Flask(__name__)"
    if app_creation in content:
        # Agregar ProxyFix después de crear la app
        old_app_section = """app = Flask(__name__)
app.config.from_object(Config)"""

        new_app_section = """app = Flask(__name__)
app.config.from_object(Config)

# ProxyFix para respetar X-Forwarded-* headers (HTTPS detrás de PaaS)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)"""

        if old_app_section in content:
            content = content.replace(old_app_section, new_app_section)

    # Mejorar configuración de cookies de sesión
    if "SESSION_COOKIE_SECURE" not in content:
        # Buscar después de la configuración de CORS
        cors_section = 'CORS(app, origins=app.config["CORS_ORIGINS"])'
        if cors_section in content:
            # Agregar configuración de cookies después de CORS
            old_cors = cors_section
            new_cors = """CORS(app, origins=app.config["CORS_ORIGINS"])

# Configuración de cookies de sesión (seguridad)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)"""

            if old_cors in content:
                content = content.replace(old_cors, new_cors)

    # Escribir el archivo actualizado
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ ProxyFix agregado")
    print("✅ Configuración HTTPS mejorada")
    print("✅ Cookies de sesión endurecidas")


if __name__ == "__main__":
    fix_proxy_and_https()
