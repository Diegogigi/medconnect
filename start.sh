#!/bin/bash
# Archivo de inicio simplificado para Railway

echo "🚀 Iniciando MedConnect..."

# Verificar variables de entorno críticas
echo "🔍 Verificando variables de entorno..."

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY no configurada"
    echo "🔧 Configura esta variable en Railway Dashboard"
    exit 1
else
    echo "✅ OPENROUTER_API_KEY configurada correctamente"
fi

if [ -z "$FLASK_ENV" ]; then
    echo "⚠️ FLASK_ENV no configurada, usando 'production'"
    export FLASK_ENV=production
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️ SECRET_KEY no configurada, generando una..."
    export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
fi

if [ -z "$PORT" ]; then
    echo "⚠️ PORT no configurada, usando 5000"
    export PORT=5000
fi

echo "✅ Variables de entorno configuradas"
echo "🔧 FLASK_ENV: $FLASK_ENV"
echo "🔧 PORT: $PORT"
if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "🔧 OPENROUTER_API_KEY: ${OPENROUTER_API_KEY:0:10}..."
else
    echo "🔧 OPENROUTER_API_KEY: No configurada"
fi

# Iniciar la aplicación
echo "🚀 Iniciando aplicación con Gunicorn..."

# Verificar si Gunicorn está disponible
if command -v gunicorn &> /dev/null; then
    echo "✅ Gunicorn encontrado, iniciando en modo producción..."
    gunicorn -k gthread -w 2 -b 0.0.0.0:$PORT app:app --timeout 120 --log-level info
else
    echo "⚠️ Gunicorn no encontrado, usando Flask en modo desarrollo..."
    python app.py
fi 