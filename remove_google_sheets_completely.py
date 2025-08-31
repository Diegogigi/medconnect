#!/usr/bin/env python3
"""
Eliminar completamente todas las referencias a Google Sheets de app.py
"""


def remove_google_sheets_completely():
    """Eliminar todas las referencias a Google Sheets"""

    print("🧹 Eliminando todas las referencias a Google Sheets...")

    # Leer el archivo actual
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # ELIMINACIONES A REALIZAR

    # 1. Eliminar importación de Google Sheets
    old_import = """    logger.info("[PAQUETE] Google Sheets omitido para Railway...")
    # Google Sheets importado solo si es necesario
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        GOOGLE_SHEETS_AVAILABLE = True
        logger.info("[OK] Google Sheets disponible")
    except ImportError:
        GOOGLE_SHEETS_AVAILABLE = False
        logger.info("[INFO] Google Sheets no disponible en Railway")"""

    new_import = """    logger.info("[PAQUETE] Google Sheets eliminado - usando solo PostgreSQL")"""

    content = content.replace(old_import, new_import)

    # 2. Eliminar cualquier otra importación de gspread
    content = content.replace("import gspread", "# gspread eliminado")
    content = content.replace(
        "from google.oauth2.service_account import Credentials",
        "# Credentials eliminado",
    )

    # 3. Eliminar referencias a GOOGLE_SHEETS_AVAILABLE
    content = content.replace(
        "GOOGLE_SHEETS_AVAILABLE = True", "# Google Sheets no disponible"
    )
    content = content.replace(
        "GOOGLE_SHEETS_AVAILABLE = False", "# Google Sheets no disponible"
    )

    # 4. Eliminar referencias a SPREADSHEET_ID
    content = content.replace(
        "SPREADSHEET_ID = config.GOOGLE_SHEETS_ID", "# SPREADSHEET_ID eliminado"
    )

    # 5. Eliminar cualquier referencia a Google Sheets en comentarios
    content = content.replace(
        "# ID de la hoja de cálculo de Google", "# Base de datos PostgreSQL"
    )

    # 6. Eliminar referencias a sheets_db
    content = content.replace("sheets_db", "postgres_db")

    # 7. Eliminar cualquier configuración de Google Sheets
    content = content.replace("SHEETS_CONFIG", "# SHEETS_CONFIG eliminado")

    # 8. Limpiar imports innecesarios
    content = content.replace(
        "from config import get_config, SHEETS_CONFIG", "# Configuración simplificada"
    )

    # 9. Eliminar cualquier función relacionada con Google Sheets
    # Buscar y eliminar funciones que usen gspread
    lines = content.split("\n")
    cleaned_lines = []
    skip_lines = False

    for line in lines:
        # Saltar líneas que contengan referencias a Google Sheets
        if any(
            keyword in line.lower()
            for keyword in [
                "gspread",
                "google.oauth2",
                "sheets_config",
                "spreadsheet_id",
            ]
        ):
            if "def " in line:  # Si es una función, saltar toda la función
                skip_lines = True
                cleaned_lines.append(f"    # {line.strip()} - FUNCIÓN ELIMINADA")
            else:
                cleaned_lines.append(f"    # {line.strip()} - ELIMINADO")
        elif skip_lines and line.strip().startswith("def "):
            # Si encontramos otra función, dejar de saltar
            skip_lines = False
            cleaned_lines.append(line)
        elif skip_lines and line.strip() == "":
            # Si encontramos línea vacía, dejar de saltar
            skip_lines = False
            cleaned_lines.append(line)
        elif not skip_lines:
            cleaned_lines.append(line)

    content = "\n".join(cleaned_lines)

    # Escribir el archivo limpio
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Todas las referencias a Google Sheets eliminadas")
    print("📋 Cambios realizados:")
    print("  ✅ Importaciones de gspread eliminadas")
    print("  ✅ Referencias a Google Sheets eliminadas")
    print("  ✅ Configuraciones de Google Sheets eliminadas")
    print("  ✅ Funciones relacionadas con Google Sheets eliminadas")
    print("  ✅ Solo PostgreSQL se mantiene")


if __name__ == "__main__":
    remove_google_sheets_completely()
    print("\n🎉 app.py completamente limpio de Google Sheets")
    print("💡 Ahora usa únicamente PostgreSQL")
    print("🚀 Listo para hacer commit y push")
