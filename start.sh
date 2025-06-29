#!/bin/bash
# MedConnect - Script de inicio optimizado para Railway

echo "🏥 === INICIANDO MEDCONNECT ==="
echo "📅 Fecha: $(date)"
echo ""

# Verificar variables de entorno críticas
echo "🔍 === VERIFICANDO VARIABLES DE ENTORNO ==="
if [ -z "$PORT" ]; then
    echo "❌ Error: Variable PORT no configurada"
    exit 1
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ Error: Variable TELEGRAM_BOT_TOKEN no configurada"
    exit 1
fi

echo "✅ Variables de entorno verificadas"
echo "🌐 Puerto: $PORT"
echo "🤖 Bot Token: ${TELEGRAM_BOT_TOKEN:0:10}..."

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
echo "🔧 Puerto configurado: $PORT"
echo "🌐 Railway requiere puerto 8080 para exposición pública"

# Ejecutar aplicación web y bot en paralelo
echo "🌐 Iniciando aplicación web en puerto $PORT..."
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --keep-alive 2 &
GUNICORN_PID=$!

echo "🤖 Iniciando bot corregido de Telegram..."
python bot_fixed.py &
BOT_PID=$!

echo "✅ Servicios iniciados:"
echo "   🌐 Web App (PID: $GUNICORN_PID)"
echo "   🤖 Bot (PID: $BOT_PID)"

# Función para limpiar procesos al salir
cleanup() {
    echo "🛑 Deteniendo servicios..."
    kill $GUNICORN_PID 2>/dev/null
    kill $BOT_PID 2>/dev/null
    exit 0
}

# Capturar señales de terminación
trap cleanup SIGTERM SIGINT

# Esperar a que los procesos terminen
wait 