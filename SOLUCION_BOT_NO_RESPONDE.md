# 🤖 SOLUCIÓN: Bot No Responde

## 📋 Diagnóstico del Problema

El bot no responde debido a varios problemas de configuración:

1. **Token hardcodeado interfería** con variables de Railway
2. **Bot no se ejecutaba** en Railway (solo web app)
3. **Credenciales mal configuradas** 
4. **Variables de entorno no se leían correctamente**

## ✅ Soluciones Implementadas

### 1. Configuración Corregida
- ✅ Eliminados valores por defecto de `config.py`
- ✅ Bot ahora lee `GOOGLE_SERVICE_ACCOUNT_JSON` correctamente
- ✅ Procfile actualizado para ejecutar bot + web app

### 2. Scripts de Diagnóstico Creados
- `check_railway_env.py` - Verificar variables en Railway
- `test_bot_connectivity.py` - Diagnóstico completo del bot

## 🚀 Pasos para Activar el Bot

### PASO 1: Verificar Variables en Railway

Ve a tu proyecto en Railway → Variables y confirma que tienes:

```
TELEGRAM_BOT_TOKEN=tu_token_aqui
GOOGLE_SHEETS_ID=tu_sheet_id_aqui  
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

### PASO 2: Verificar Variables
```bash
# En Railway, ve a tu proyecto y ejecuta este comando en la consola:
python check_railway_env.py
```

### PASO 3: Redeploy
1. Ve a Railway → Deployments
2. Click en "Redeploy" 
3. O haz un push a tu repositorio

### PASO 4: Verificar Logs
En Railway → Logs, deberías ver:
```
✅ TELEGRAM_BOT_TOKEN configurado
✅ GOOGLE_SHEETS_ID configurado  
✅ GOOGLE_SERVICE_ACCOUNT_JSON configurado
🌐 Iniciando aplicación web...
🤖 Iniciando bot de Telegram...
```

## 🔍 Diagnóstico Completo

Si el bot sigue sin responder, ejecuta:
```bash
python test_bot_connectivity.py
```

Esto verificará:
- ✅ Variables de entorno
- ✅ Conectividad del bot
- ✅ Google Sheets
- ✅ Webhook
- ✅ Funcionalidad básica

## 🚨 Problemas Comunes

### Bot Token Inválido
**Síntoma**: Error 401 Unauthorized
**Solución**: 
1. Ve a @BotFather en Telegram
2. Ejecuta `/mybots` → Selecciona tu bot → API Token
3. Copia el token exacto (ejemplo: `123456789:ABCdef...`)

### JSON de Credenciales Inválido
**Síntoma**: Error JSON decode
**Solución**:
1. Ve a Google Cloud Console
2. Descarga el JSON del service account
3. Copia TODO el contenido (no comprimas)
4. Pega en `GOOGLE_SERVICE_ACCOUNT_JSON`

### Bot No Recibe Mensajes
**Síntoma**: Bot conecta pero no responde
**Solución**:
1. Revisa que el webhook no esté configurado
2. Ejecuta en Telegram: `/start` con tu bot
3. Verifica logs de Railway

## 📞 Verificación Rápida

Envía un mensaje a tu bot en Telegram:
```
/start
```

Si funciona, deberías recibir el mensaje de bienvenida.

## 🔧 Comandos de Emergencia

### Resetear Webhook
```bash
curl -X POST "https://api.telegram.org/bot[TOKEN]/deleteWebhook"
```

### Verificar Bot Status
```bash
curl "https://api.telegram.org/bot[TOKEN]/getMe"
```

## 📱 Contacto de Soporte

Si sigues teniendo problemas:
1. Copia los logs de Railway
2. Ejecuta `python test_bot_connectivity.py`
3. Comparte los resultados

---

**✅ Con estos cambios, el bot debería funcionar correctamente en Railway.** 