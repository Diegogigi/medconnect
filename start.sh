#!/bin/bash
# MedConnect - Script de inicio optimizado para Railway

set -e

echo "🚀 Iniciando MedConnect..."

# Activar entorno virtual
if [ -d "venv" ]; then
    echo "✅ Activando entorno virtual..."
    source venv/bin/activate
fi

# Verificación rápida de dependencias críticas
python -c "import flask, gspread, gunicorn" 2>/dev/null || {
    echo "❌ Error: Faltan dependencias críticas"
    exit 1
}

echo "🌐 Iniciando servidor..."
exec gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --log-level info \
    --access-logfile - \
    --error-logfile - 