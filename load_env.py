#!/usr/bin/env python3
"""
Script para cargar variables de entorno desde archivo .env
"""

import os
from dotenv import load_dotenv

def load_environment():
    """Carga variables de entorno desde archivo .env"""
    
    # Cargar variables desde .env si existe
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ Variables de entorno cargadas desde .env")
    else:
        print("⚠️ Archivo .env no encontrado")
    
    # Mostrar variables actuales
    print("📋 Variables de entorno actuales:")
    database_url = os.environ.get("DATABASE_URL")
    pghost = os.environ.get("PGHOST")
    pgdatabase = os.environ.get("PGDATABASE")
    pguser = os.environ.get("PGUSER")
    pgpassword = os.environ.get("PGPASSWORD")
    pgport = os.environ.get("PGPORT")
    
    print(f"   DATABASE_URL: {'✅ Configurada' if database_url else '❌ No configurada'}")
    print(f"   PGHOST: {pghost or 'No configurado'}")
    print(f"   PGDATABASE: {pgdatabase or 'No configurado'}")
    print(f"   PGUSER: {pguser or 'No configurado'}")
    print(f"   PGPASSWORD: {'✅ Configurada' if pgpassword else '❌ No configurada'}")
    print(f"   PGPORT: {pgport or 'No configurado'}")

if __name__ == "__main__":
    load_environment()
