#!/bin/bash
# MedConnect - Script de inicio para Railway
# Activa el entorno virtual y lanza la aplicación

set -e

echo "🚀 Iniciando MedConnect..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "✅ Activando entorno virtual..."
    source venv/bin/activate
else
    echo "⚠️ No se encontró entorno virtual, usando Python del sistema"
fi

# Verificar que las dependencias estén instaladas
echo "📋 Verificando dependencias..."
python -c "import flask, gspread, requests, gunicorn" || {
    echo "❌ Error: Faltan dependencias críticas"
    exit 1
}

echo "🌐 Iniciando servidor con gunicorn..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info 