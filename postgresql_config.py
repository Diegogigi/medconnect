#!/usr/bin/env python3
"""
Configuración para PostgreSQL
"""

import os

def get_postgresql_config():
    """Obtener configuración de PostgreSQL"""
    return {
        'host': os.environ.get('PGHOST', 'localhost'),
        'port': os.environ.get('PGPORT', '5432'),
        'database': os.environ.get('PGDATABASE', 'railway'),
        'user': os.environ.get('PGUSER', 'postgres'),
        'password': os.environ.get('PGPASSWORD', ''),
        'database_url': os.environ.get('DATABASE_URL')
    }

def get_config():
    """Obtener configuración general"""
    return {
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key'),
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'development'),
        'PORT': int(os.environ.get('PORT', 5000)),
        'OPENROUTER_API_KEY': os.environ.get('OPENROUTER_API_KEY'),
        'postgresql': get_postgresql_config()
    }
