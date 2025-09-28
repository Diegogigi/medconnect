#!/usr/bin/env python3
"""
Script para ejecutar la migración de base de datos manualmente
"""

import os
import sys


def run_migration_manual():
    """Ejecuta la migración de base de datos manualmente"""

    print("🔧 Ejecutando migración de base de datos manualmente...")
    print("=" * 60)

    try:
        from migrate_database import migrate_database

        print("✅ Módulo de migración importado correctamente")
        print("🚀 Iniciando migración...")

        success = migrate_database()

        if success:
            print("✅ Migración completada exitosamente")
            return True
        else:
            print("❌ Error en la migración")
            return False

    except ImportError as e:
        print(f"❌ Error importando módulo de migración: {e}")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando migración: {e}")
        return False


if __name__ == "__main__":
    print("🚀 MIGRACIÓN MANUAL DE BASE DE DATOS")
    print("=" * 60)

    success = run_migration_manual()

    if success:
        print("\n🎉 ¡Migración completada!")
        print("🔧 La base de datos está lista para usar")
    else:
        print("\n❌ Error en la migración")
        print("🔧 Revisa los logs para más detalles")
        sys.exit(1)
