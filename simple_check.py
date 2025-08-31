#!/usr/bin/env python3
"""
Script simple para verificar PostgreSQL
"""

import psycopg2

DATABASE_URL = "postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway"

try:
    print("🔍 Conectando a PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    print("✅ Conexión exitosa")

    # Verificar tablas
    cursor.execute(
        """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """
    )

    tables = cursor.fetchall()
    print(f"📋 Tablas encontradas: {len(tables)}")

    for table in tables:
        print(f"  - {table[0]}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
