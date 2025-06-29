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

# Configurar puerto para Railway
export PORT=${PORT:-5000}
echo "🔧 Puerto configurado: $PORT"

# Ejecutar aplicación web y bot en paralelo
echo "🌐 Iniciando aplicación web en puerto $PORT..."
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keep-alive 2 &
GUNICORN_PID=$!

echo "🤖 Iniciando bot OFICIAL de MedConnect..."
python bot.py &
BOT_PID=$!

echo "✅ Web app PID: $GUNICORN_PID"
echo "✅ Bot PID: $BOT_PID"

# Función para manejar señales
cleanup() {
    echo "🛑 Deteniendo servicios..."
    kill $GUNICORN_PID $BOT_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Mantener ambos procesos corriendo
echo "🔄 Servicios iniciados, monitoreando..."
wait 