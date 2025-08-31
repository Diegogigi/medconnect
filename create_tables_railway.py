#!/usr/bin/env python3
"""
Script para crear tablas en PostgreSQL de Railway
Ejecutar desde local con las credenciales de Railway
"""

import os
import sys
from postgresql_db_manager import PostgreSQLManager


def main():
    print("🚀 Iniciando creación de tablas en PostgreSQL de Railway...")

    try:
        # Crear instancia del manager
        db_manager = PostgreSQLManager()

        # Verificar conexión
        print("🔍 Verificando conexión a PostgreSQL...")
        if db_manager.test_connection():
            print("✅ Conexión exitosa a PostgreSQL")
        else:
            print("❌ Error de conexión")
            return False

        # Crear tablas
        print("🔧 Creando tablas...")
        success = db_manager.create_all_tables()

        if success:
            print("✅ Todas las tablas creadas exitosamente")

            # Listar tablas creadas
            tables = db_manager.list_tables()
            print(f"📋 Tablas disponibles: {tables}")

            # Insertar datos de prueba
            print("📝 Insertando datos de prueba...")
            db_manager.insert_sample_data()
            print("✅ Datos de prueba insertados")

            return True
        else:
            print("❌ Error creando tablas")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 ¡Migración a PostgreSQL completada exitosamente!")
        print("🌐 Tu aplicación ahora usa PostgreSQL en Railway")
    else:
        print("\n❌ Error en la migración")
        sys.exit(1)
