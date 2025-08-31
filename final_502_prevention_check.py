#!/usr/bin/env python3
"""
Verificación final para prevenir errores 502
"""

import os


def check_templates():
    """Verificar que existan los templates necesarios"""

    print("🔍 Verificando templates...")

    required_templates = [
        "templates/index.html",
        "templates/login.html",
        "templates/professional.html",
        "templates/patient.html",
        "templates/404.html",
        "templates/500.html",
    ]

    missing_templates = []

    for template in required_templates:
        if os.path.exists(template):
            print(f"  ✅ {template}")
        else:
            print(f"  ❌ {template} - FALTANTE")
            missing_templates.append(template)

    return missing_templates


def check_critical_imports():
    """Verificar imports críticos en app.py"""

    print("\n🔍 Verificando imports críticos...")

    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar que NO hay referencias problemáticas
        problematic_refs = [
            "gspread",
            "google.oauth2",
            "SHEETS_CONFIG",
            "config.CORS_ORIGINS",
            "sheets_client",
            "get_google_sheets_client",
        ]

        found_problems = []

        for ref in problematic_refs:
            if ref in content:
                print(f"  ⚠️ Referencia problemática encontrada: {ref}")
                found_problems.append(ref)
            else:
                print(f"  ✅ {ref} - NO encontrado (correcto)")

        # Verificar que SÍ hay elementos necesarios
        required_elements = [
            "CORS(app)",
            "postgres_db",
            "PostgreSQLDBManager",
            "@app.route('/health')",
            "@app.route('/robots.txt')",
            "@app.route('/favicon.ico')",
        ]

        for element in required_elements:
            if element in content:
                print(f"  ✅ {element} - Encontrado")
            else:
                print(f"  ❌ {element} - FALTANTE")
                found_problems.append(element)

        return found_problems

    except Exception as e:
        print(f"  ❌ Error verificando app.py: {e}")
        return ["Error reading app.py"]


def create_missing_templates():
    """Crear templates faltantes básicos"""

    print("\n🔧 Creando templates faltantes...")

    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)

    # Template básico para 404
    if not os.path.exists("templates/404.html"):
        with open("templates/404.html", "w", encoding="utf-8") as f:
            f.write(
                """<!DOCTYPE html>
<html>
<head>
    <title>404 - Página no encontrada</title>
</head>
<body>
    <h1>404 - Página no encontrada</h1>
    <p>La página que buscas no existe.</p>
    <a href="/">Volver al inicio</a>
</body>
</html>"""
            )
        print("  ✅ templates/404.html creado")

    # Template básico para 500
    if not os.path.exists("templates/500.html"):
        with open("templates/500.html", "w", encoding="utf-8") as f:
            f.write(
                """<!DOCTYPE html>
<html>
<head>
    <title>500 - Error del servidor</title>
</head>
<body>
    <h1>500 - Error del servidor</h1>
    <p>Ha ocurrido un error interno.</p>
    <a href="/">Volver al inicio</a>
</body>
</html>"""
            )
        print("  ✅ templates/500.html creado")


def final_verification():
    """Verificación final completa"""

    print("🚀 VERIFICACIÓN FINAL PARA PREVENIR ERRORES 502")
    print("=" * 50)

    # 1. Verificar templates
    missing_templates = check_templates()

    # 2. Verificar imports críticos
    found_problems = check_critical_imports()

    # 3. Crear templates faltantes básicos
    create_missing_templates()

    # 4. Resumen
    print("\n📋 RESUMEN:")
    print(f"  Templates faltantes: {len(missing_templates)}")
    print(f"  Problemas encontrados: {len(found_problems)}")

    if len(missing_templates) == 0 and len(found_problems) == 0:
        print("\n🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ La aplicación debería funcionar sin errores 502")
        print("✅ Todos los elementos críticos están presentes")
        print("✅ No hay referencias problemáticas")
        return True
    else:
        print("\n⚠️ PROBLEMAS DETECTADOS:")
        if missing_templates:
            print(f"  Templates faltantes: {missing_templates}")
        if found_problems:
            print(f"  Referencias problemáticas: {found_problems}")
        return False


if __name__ == "__main__":
    success = final_verification()

    if success:
        print("\n🚀 ¡LISTO PARA DEPLOY!")
        print("💡 Puedes hacer commit y push con confianza")
    else:
        print("\n🔧 Necesitas corregir los problemas antes del deploy")
