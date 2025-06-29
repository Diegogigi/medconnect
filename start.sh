#!/bin/bash
# MedConnect - Script de inicio optimizado para Railway

echo "🏥 === INICIANDO MEDCONNECT ==="
echo "📅 Fecha: $(date)"
echo ""

# Verificar variables de entorno críticas
echo "🔍 === VERIFICANDO VARIABLES DE ENTORNO ==="
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN no configurado"
    exit 1
else
    echo "✅ TELEGRAM_BOT_TOKEN configurado"
fi

if [ -z "$GOOGLE_SHEETS_ID" ]; then
    echo "❌ GOOGLE_SHEETS_ID no configurado"
    exit 1
else
    echo "✅ GOOGLE_SHEETS_ID configurado"
fi

if [ -z "$GOOGLE_SERVICE_ACCOUNT_JSON" ]; then
    echo "❌ GOOGLE_SERVICE_ACCOUNT_JSON no configurado"
    exit 1
else
    echo "✅ GOOGLE_SERVICE_ACCOUNT_JSON configurado"
    echo "📝 JSON length: ${#GOOGLE_SERVICE_ACCOUNT_JSON} caracteres"
fi

echo ""
echo "🚀 === INICIANDO SERVICIOS ==="

# Instalar dependencias si es necesario
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Ejecutar aplicación web y bot en paralelo
echo "🌐 Iniciando aplicación web..."
gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 --keep-alive 2 --daemon

echo "🤖 Iniciando bot de DIAGNÓSTICO..."
python bot_debug.py &

# Mantener el script corriendo
wait 