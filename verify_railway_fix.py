#!/usr/bin/env python3
"""
Script para verificar que el fix de Railway esté funcionando
"""


def verify_railway_fix():
    """Verifica que el fix de Railway esté funcionando"""

    print("🔍 Verificando fix de Railway...")
    print("=" * 50)

    # Verificar que app.py tenga las variables por defecto
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    print("📋 Verificando configuración en app.py:")

    # Verificar variables críticas
    checks = [
        (
            "DATABASE_URL",
            "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@postgres.railway.internal:5432/railway",
        ),
        (
            "OPENROUTER_API_KEY",
            "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",
        ),
        ("SECRET_KEY", "medconnect-secret-key-2025-railway-production"),
        ("FLASK_ENV", "production"),
        ("PORT", "5000"),
    ]

    all_ok = True
    for var_name, expected_value in checks:
        if expected_value in content:
            print(f"  ✅ {var_name}: Configurada")
        else:
            print(f"  ❌ {var_name}: No encontrada")
            all_ok = False

    print()

    # Verificar que postgresql_db_manager.py tenga mejor logging
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        db_content = f.read()

    print("📋 Verificando postgresql_db_manager.py:")
    if 'logger.info(f"📋 Variables encontradas:")' in db_content:
        print("  ✅ Logging mejorado configurado")
    else:
        print("  ❌ Logging mejorado no encontrado")
        all_ok = False

    print()
    print("=" * 50)

    if all_ok:
        print("🎉 ¡Fix de Railway completado!")
        print("✅ Todas las variables están configuradas por defecto")
        print("🚀 Railway debería funcionar correctamente ahora")
        print()
        print("📝 Próximos pasos:")
        print("1. Railway redeployará automáticamente")
        print("2. Los errores 502 deberían desaparecer")
        print("3. PostgreSQL se conectará correctamente")
        print("4. La aplicación estará disponible en www.medconnect.cl")
    else:
        print("⚠️ Algunos problemas detectados")
        print("🔧 Revisa la configuración")


if __name__ == "__main__":
    verify_railway_fix()
