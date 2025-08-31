#!/bin/bash
# Archivo de inicio para Railway - SOLO verificaciones mínimas

echo "🚀 Iniciando MedConnect..."

# Verificar solo variables críticas
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY no configurada"
    exit 1
fi

echo "✅ Variables verificadas"

# Railway debería usar Procfile automáticamente
# Si no, usar el comando directamente
exec gunicorn -k gthread -w 2 -b 0.0.0.0:$PORT app:app --timeout 120 --log-level info
