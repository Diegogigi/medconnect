#!/usr/bin/env python3
"""
Script para debuggear variables de entorno en Railway
"""

import os


def debug_railway_environment():
    """Debuggear variables de entorno en Railway"""

    print("🔍 DEBUG: Variables de entorno en Railway")
    print("=" * 60)

    # Verificar DATABASE_URL específicamente
    database_url = os.environ.get("DATABASE_URL")
    print(f"📋 DATABASE_URL:")
    if database_url:
        print(
            f"   ✅ Encontrada: {database_url[:50]}..."
            if len(database_url) > 50
            else f"   ✅ Encontrada: {database_url}"
        )

        # Verificar si es URL de Railway
        if "railway" in database_url:
            print("   🚂 URL de Railway detectada")
        elif "postgres" in database_url:
            print("   🗄️ URL de PostgreSQL detectada")
        else:
            print("   ⚠️ URL no reconocida")
    else:
        print("   ❌ NO ENCONTRADA")

    print()

    # Verificar variables individuales de PostgreSQL
    print("📋 Variables individuales de PostgreSQL:")
    pghost = os.environ.get("PGHOST")
    pgdatabase = os.environ.get("PGDATABASE")
    pguser = os.environ.get("PGUSER")
    pgpassword = os.environ.get("PGPASSWORD")
    pgport = os.environ.get("PGPORT")

    print(f"   PGHOST: {pghost or 'No configurado'}")
    print(f"   PGDATABASE: {pgdatabase or 'No configurado'}")
    print(f"   PGUSER: {pguser or 'No configurado'}")
    print(f"   PGPASSWORD: {'Configurada' if pgpassword else 'No configurada'}")
    print(f"   PGPORT: {pgport or 'No configurado'}")

    print()

    # Verificar otras variables importantes
    print("📋 Otras variables importantes:")
    secret_key = os.environ.get("SECRET_KEY")
    flask_env = os.environ.get("FLASK_ENV")
    port = os.environ.get("PORT")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")

    print(f"   SECRET_KEY: {'Configurada' if secret_key else 'No configurada'}")
    print(f"   FLASK_ENV: {flask_env or 'No configurado'}")
    print(f"   PORT: {port or 'No configurado'}")
    print(
        f"   OPENROUTER_API_KEY: {'Configurada' if openrouter_key else 'No configurada'}"
    )

    print()

    # Mostrar todas las variables que contengan "DATABASE" o "POSTGRES"
    print("📋 Todas las variables que contengan 'DATABASE' o 'POSTGRES':")
    db_vars = {
        k: v
        for k, v in os.environ.items()
        if "DATABASE" in k.upper() or "POSTGRES" in k.upper()
    }

    if db_vars:
        for key, value in db_vars.items():
            if "PASSWORD" in key.upper():
                display_value = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"   {key}: {display_value}")
    else:
        print("   No se encontraron variables relacionadas con base de datos")

    print()
    print("=" * 60)

    # Recomendaciones
    if not database_url:
        print("❌ PROBLEMA: DATABASE_URL no está configurada")
        print("🔧 SOLUCIÓN: Configura DATABASE_URL en Railway Dashboard")
        print(
            "   Valor esperado: postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@postgres.railway.internal:5432/railway"
        )
    else:
        print("✅ DATABASE_URL está configurada")
        print("🔍 Si sigue fallando, verifica que la URL sea correcta")


if __name__ == "__main__":
    debug_railway_environment()
