#!/usr/bin/env python3
"""
Script para verificar que todas las mejoras estén implementadas
"""


def verify_all_improvements():
    """Verifica que todas las mejoras estén implementadas"""

    print("🔍 Verificando todas las mejoras implementadas...")
    print("=" * 60)

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    improvements = [
        {
            "name": "Puerto 8000 por defecto",
            "check": 'PORT = int(os.environ.get("PORT", "8000"))',
            "critical": True,
        },
        {
            "name": "ProxyFix para HTTPS",
            "check": "from werkzeug.middleware.proxy_fix import ProxyFix",
            "critical": True,
        },
        {
            "name": "ProxyFix aplicado",
            "check": "app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)",
            "critical": True,
        },
        {
            "name": "Cookies de sesión seguras",
            "check": "SESSION_COOKIE_SECURE=True",
            "critical": False,
        },
        {
            "name": "Secrets no hard-coded",
            "check": 'SECRET_KEY = os.environ["SECRET_KEY"]',
            "critical": True,
        },
        {
            "name": "DATABASE_URL requerida",
            "check": 'DATABASE_URL = os.environ["DATABASE_URL"]',
            "critical": True,
        },
        {
            "name": "Manejo de errores mejorado",
            "check": "import traceback",
            "critical": False,
        },
        {
            "name": "Logging de errores 500",
            "check": 'logger.error("500: %s\\n%s", error, traceback.format_exc())',
            "critical": False,
        },
        {
            "name": "Arranque con logging",
            "check": "logger.info(f\"🌐 Binding Flask en 0.0.0.0:{app.config['PORT']}\")",
            "critical": True,
        },
    ]

    all_critical_ok = True
    total_improvements = len(improvements)
    implemented_improvements = 0

    print("📋 Verificando mejoras:")
    for improvement in improvements:
        if improvement["check"] in content:
            status = "✅"
            implemented_improvements += 1
        else:
            status = "❌"
            if improvement["critical"]:
                all_critical_ok = False

        critical_mark = "🔴" if improvement["critical"] else "🟡"
        print(f"  {status} {critical_mark} {improvement['name']}")

    print()
    print("=" * 60)

    # Verificar Procfile
    try:
        with open("Procfile", "r", encoding="utf-8") as f:
            procfile_content = f.read()

        if "gunicorn" in procfile_content:
            print("✅ Procfile configurado con Gunicorn")
            implemented_improvements += 1
        else:
            print("❌ Procfile no configurado correctamente")
            all_critical_ok = False
    except FileNotFoundError:
        print("❌ Procfile no encontrado")
        all_critical_ok = False

    print()
    print(
        f"📊 Resumen: {implemented_improvements}/{total_improvements + 1} mejoras implementadas"
    )

    if all_critical_ok:
        print("🎉 ¡Todas las mejoras críticas están implementadas!")
        print("✅ La aplicación debería funcionar correctamente en Railway")
        print("🚀 Los errores 502 deberían estar resueltos")
        print()
        print("📝 Próximos pasos:")
        print("1. Railway redeployará automáticamente")
        print("2. Verifica que las variables de entorno estén configuradas")
        print("3. Monitorea los logs de Railway")
        print("4. Prueba la aplicación en www.medconnect.cl")
    else:
        print("⚠️ Algunas mejoras críticas faltan")
        print("🔧 Revisa las mejoras marcadas con ❌")

    return all_critical_ok


if __name__ == "__main__":
    verify_all_improvements()
