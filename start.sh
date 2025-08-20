#!/bin/bash
# Archivo de inicio simplificado para Railway

echo "🚀 Iniciando MedConnect..."

# Verificar variables de entorno críticas
echo "🔍 Verificando variables de entorno..."

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY no configurada"
    echo "🔧 Configura esta variable en Railway Dashboard"
    exit 1
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
echo "🔧 OPENROUTER_API_KEY: ${OPENROUTER_API_KEY:0:10}..."

# Iniciar la aplicación
echo "🚀 Iniciando aplicación Flask..."
python app.py 