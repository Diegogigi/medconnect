#!/usr/bin/env python3
"""
Script para corregir errores críticos en app.py que causan 502 Bad Gateway
"""

import re
import os


def fix_critical_app_errors():
    """Corrige todos los errores críticos en app.py"""

    print("🔧 Corrigiendo errores críticos en app.py...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. ELIMINAR TODAS LAS LLAMADAS A get_spreadsheet()
    print("  - Eliminando llamadas a get_spreadsheet()...")

    # Patrón para encontrar líneas que usan get_spreadsheet()
    pattern = r"^\s*spreadsheet\s*=\s*get_spreadsheet\(\)\s*$"
    content = re.sub(
        pattern,
        "        # spreadsheet = get_spreadsheet()  # ELIMINADO - USAR POSTGRESQL",
        content,
        flags=re.MULTILINE,
    )

    # 2. CORREGIR REFERENCIAS A config NO DEFINIDO
    print("  - Corrigiendo referencias a config...")

    # Reemplazar config.TELEGRAM_BOT_TOKEN con os.environ.get
    content = re.sub(
        r"config\.TELEGRAM_BOT_TOKEN", 'os.environ.get("TELEGRAM_BOT_TOKEN")', content
    )

    # 3. ELIMINAR REFERENCIAS A Credentials
    print("  - Eliminando referencias a Credentials...")

    # Comentar la línea problemática
    content = re.sub(
        r"credentials = Credentials\.from_service_account_info\(",
        "# credentials = Credentials.from_service_account_info(  # ELIMINADO",
        content,
    )

    # 4. LIMPIAR COMENTARIOS MAL FORMATEADOS
    print("  - Limpiando comentarios mal formateados...")

    # Reemplazar comentarios problemáticos
    content = re.sub(
        r"# # except # gspread eliminado\.WorksheetNotFound: - ELIMINADO - ELIMINADO",
        "        except Exception as e:  # WorksheetNotFound handled as general exception",
        content,
    )

    # 5. AGREGAR FUNCIÓN get_spreadsheet() SIMULADA PARA EVITAR ERRORES
    print("  - Agregando función get_spreadsheet() simulada...")

    # Buscar donde agregar la función simulada (después de las importaciones)
    import_section_end = content.find("# Inicializar Flask")
    if import_section_end != -1:
        simulated_function = '''
# Función simulada para evitar errores - usar PostgreSQL en su lugar
def get_spreadsheet():
    """Función simulada - usar PostgreSQL en su lugar"""
    logger.warning("[ADVERTENCIA] get_spreadsheet() llamada - usar PostgreSQL en su lugar")
    return None

'''
        content = (
            content[:import_section_end]
            + simulated_function
            + content[import_section_end:]
        )

    # 6. AGREGAR RUTAS BÁSICAS PARA EVITAR 404s
    print("  - Agregando rutas básicas...")

    # Buscar el final del archivo para agregar rutas básicas
    if 'if __name__ == "__main__":' in content:
        basic_routes = '''
# Rutas básicas para evitar errores 404
@app.route("/robots.txt")
def robots_txt():
    """Robots.txt para SEO"""
    return "User-agent: *\\nDisallow: /", 200, {"Content-Type": "text/plain"}

@app.route("/favicon.ico")
def favicon():
    """Favicon"""
    return send_from_directory("static/images", "favicon.ico")

@app.route("/health")
def health_check():
    """Health check para Railway"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/webhook", methods=["GET"])
def webhook_get():
    """Webhook GET method"""
    return jsonify({"error": "Method not allowed"}), 405

'''
        # Insertar antes del if __name__ == "__main__"
        main_start = content.find('if __name__ == "__main__":')
        content = content[:main_start] + basic_routes + content[main_start:]

    # 7. CORREGIR IMPORTS FALTANTES
    print("  - Corrigiendo imports...")

    # Agregar import de datetime si no existe
    if "from datetime import datetime" not in content:
        datetime_import = "from datetime import datetime, timedelta\n"
        # Buscar donde insertar (después de otros imports de datetime)
        datetime_pos = content.find("from datetime import datetime, timedelta")
        if datetime_pos == -1:
            # Insertar después de los imports estándar
            std_imports_end = content.find(
                'logger.info("[OK] Bibliotecas est ndar importadas")'
            )
            if std_imports_end != -1:
                insert_pos = content.find("\n", std_imports_end) + 1
                content = content[:insert_pos] + datetime_import + content[insert_pos:]

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Errores críticos corregidos en app.py")
    print("📝 Cambios realizados:")
    print("   - Eliminadas llamadas a get_spreadsheet()")
    print("   - Corregidas referencias a config")
    print("   - Eliminadas referencias a Credentials")
    print("   - Limpiados comentarios mal formateados")
    print("   - Agregada función get_spreadsheet() simulada")
    print("   - Agregadas rutas básicas (/robots.txt, /favicon.ico, /health)")
    print("   - Corregidos imports faltantes")


if __name__ == "__main__":
    fix_critical_app_errors()
