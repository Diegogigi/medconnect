# 🚀 MedConnect - Despliegue Final en Railway

## ✅ Estado Actual: LISTO PARA DESPLEGAR

### 📊 **Google Sheets Configurado**
- **Nombre**: bd_medconnect
- **ID**: `1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU`
- **URL**: https://docs.google.com/spreadsheets/d/1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU
- **Hojas creadas**: ✅ Pacientes, Consultas, Medicamentos, Examenes, Familiares, Interacciones_Bot
- **Datos de ejemplo**: ✅ Agregados
- **Service Account**: ✅ Configurado

### 🤖 **Bot de Telegram Configurado**
- **Token**: `7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck`
- **ID**: `1071410995`
- **Username**: `@medconnect_bot`
- **Estado**: ✅ Listo para webhook

### 🔧 **Aplicación Flask**
- **Backend**: ✅ Configurado
- **Templates**: ✅ Estructurados
- **Static files**: ✅ Organizados
- **Configuración**: ✅ Completa

---

## 🚀 **Pasos para Desplegar en Railway**

### 1. **Instalar Railway CLI**
```bash
# Windows (PowerShell)
npm install -g @railway/cli

# Verificar instalación
railway --version
```

### 2. **Inicializar Proyecto en Railway**
```bash
# En la carpeta medconnect
railway login
railway init
```

### 3. **Configurar Variables de Entorno en Railway**

En el dashboard de Railway, configurar estas variables:

```env
# Aplicación
FLASK_ENV=production
SECRET_KEY=medconnect-secret-key-2024
DOMAIN=medconnect.cl

# Telegram Bot
TELEGRAM_BOT_TOKEN=7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck
TELEGRAM_BOT_ID=1071410995

# Google Sheets (YA CONFIGURADO)
GOOGLE_SHEETS_ID=1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"sincere-mission-463804-h9","private_key_id":"95d16ea62efca929d5ba7b73a14bb07e0b28eb48","private_key":"-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCkF61+dbK/uXup\nwh2Mwt8bLAEHgOgywXOMhDlR/Xhnyos3my8Q+ovx5rpYE822YqA/BhRVhYoBr1A2\nXkYimPiD514PZ/3eLw+flhAVGlOvbWULGDfZFQNFT1+yzbKds+HNjD6p3mr5lGcz\nnPJS2x4rzEQlJQVG8r5RbiM5vmKxGMBG41mzhlFUCenXta+jgdaRlVQWmjsxY3RM\nIIgiCi8/2UO1RebSyGHQ1SXVXcDuvzDlcNSreg/dZQmyDUlqje4uu4qDYf0p/oC/\nw7W6lzE22WrEsRSmGVVpxftXKNsCDOt8ubQbpko9kVj14Br0Bvh24VqTTW7HJ/wL\nIBcFva/nAgMBAAECggEAAyZZNDY6Kif7UbTiMFOFSNY9ZtF4o5DHEQlwuDwvVX6z\n0WtvKdpFWW1eYlZu+nNGNC9/sGyRy5p75a9FlWBuVMnaKl2Kp/srR5rv0BfjR1jI\nOcBLQiV/HJN7eMkuBozvZqysf0I/t2671GfM1v5Rw/F11WiygzwhnxqIHpGi/1c8\naDKZTFlw+xmv29tsrG32K0P7/aCQAgChV1j4TFuapSvH181B5Uv/FEixP2HcPHic\ntLHx064uVmtlN0QWgw5KM0z95qlXsdq3cYvqESh5OmQ9ALscBzZazyPztjzYGIHv\nuamL92Njd69vV5qc9rU7DlNq6o0oIEKNP+qiGWE8EQKBgQDYmnEtv31N+/erD4S2\ni3wehrYPfQY4I/MqnGhYPqY4RrsVrU8zRwnVyl8ilqB66rCpsZRp4sEDVITKwFua\nngOXIEw7RJXJfqaTUnBvbeDpz4X4lK5v+A8SwYRlK07qmep9soB79IMQeiMFVVz7\n5ojieJMVY7mtwy9nm9SBeS3FewKBgQDB8DWhyfbVpnxGm5FSqZjt7FD4kiPBaUop\n8f8TiQ6y2ODslwCH4nTN5sMHtPMTEvFkV4tRoG3ATep+tTGGRhGdJJOxzwckxh8X\nS0SzkCnJd06vclPjSqfDXteYKuyX0FGXysdWFIwOZ0QycvAUm+a7Ut1HolXAuiq9\ncisFeFkVhQKBgF4chI5nBA+tKcgWXwhdhJlS2KnUHa6o2A+sk5274sbS3Jini6Dw\n/bH5UuqZXbLqY8XnVV/IWSqUP3pEp8h/XXn9W4Ho49f/gmrCR/3yVOXh+AiwuTYH\nJq10jYzTi19dbsgclbzF2WiAWNUJaPQ+Dz2vO+DwSo3YH7G5wFRdDWkfAoGAMXCO\nC4+T+EU32zwfYOZRUR30Slne+Zhgyq6haxZ+g8NcG5QnE3z8b90LDPTpHoyusvjK\nUGXIdMSoKeMBHAzSwq+nYyW22X4UQPj0K55tuKlMitdnYUMP33NXHLicldsKYdrU\n1DHqvmU+8mlwoKBZwplORcuxdq8+5Aqtwvg6JY0CgYAxp/xa94PNFp4FO6LSQcNd\ngB4XZpj0AMlZqf70v7/0P1GU3aaSaLBEOUr4EzvyN7Jqd0WjSd0D+Z7R5XWFGbxu\nzuzj/OGWV0GDBppWfY4FwIYx9b564abDbhchqF0a3jYTMsUxk3J8cbLwoqzOU8sE\nym0W+E4k/xHFdwNtunoySw==\n-----END PRIVATE KEY-----\n","client_email":"medconnect@sincere-mission-463804-h9.iam.gserviceaccount.com","client_id":"109935890158775682198","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/medconnect%40sincere-mission-463804-h9.iam.gserviceaccount.com","universe_domain":"googleapis.com"}
```

### 4. **Desplegar la Aplicación**
```bash
# Desde la carpeta medconnect
railway up
```

### 5. **Configurar Dominio**
En Railway Dashboard:
1. Ir a Settings > Domains
2. Agregar custom domain: `medconnect.cl`
3. Configurar DNS en tu proveedor:
   ```
   CNAME medconnect.cl -> tu-app.railway.app
   ```

### 6. **Configurar Webhook del Bot**
Una vez desplegada la aplicación:

**Opción A - Automática:**
```bash
curl -X GET "https://medconnect.cl/setup-webhook"
```

**Opción B - Manual:**
```bash
curl -X POST "https://api.telegram.org/bot7618933472:AAEYCYi9Sso9YVP9aB8dLWvlZ-1hxqgdhck/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://medconnect.cl/webhook"}'
```

---

## ✅ **Verificación Post-Despliegue**

### 1. **Health Check**
```bash
curl https://medconnect.cl/health
```
Debería responder: `{"status": "healthy", ...}`

### 2. **Páginas Web**
- ✅ https://medconnect.cl/ (Landing page)
- ✅ https://medconnect.cl/patient (Dashboard paciente)
- ✅ https://medconnect.cl/profile (Perfil usuario)

### 3. **Bot de Telegram**
1. Buscar `@medconnect_bot` en Telegram
2. Enviar `/start`
3. Verificar respuesta automática
4. Comprobar que se registre en Google Sheets

### 4. **Google Sheets**
- Verificar que las interacciones del bot aparezcan en "Interacciones_Bot"
- Comprobar que los datos de ejemplo estén presentes

---

## 📊 **Estructura Final de Archivos**

```
medconnect/
├── app.py                          # ✅ Aplicación Flask principal
├── config.py                       # ✅ Configuración completa
├── requirements.txt                # ✅ Dependencias
├── Procfile                        # ✅ Railway startup
├── railway.json                    # ✅ Railway config
├── service-account.json           # ✅ Credenciales Google
├── .gitignore                     # ✅ Archivos a ignorar
├── templates/                     # ✅ Templates Flask
│   ├── index.html
│   ├── patient.html
│   ├── profile.html
│   └── otros...
├── static/                        # ✅ Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
└── scripts de configuración       # ✅ Herramientas
    ├── setup_sheets.py
    ├── find_sheet.py
    └── config_bd_medconnect.py
```

---

## 🔧 **Comandos Útiles Railway**

```bash
# Ver logs en tiempo real
railway logs

# Ver variables de entorno
railway variables

# Redeploy
railway up

# Conectar a shell
railway shell

# Ver información del proyecto
railway status
```

---

## 🎯 **URLs Finales**

### Aplicación Web
- **Landing**: https://medconnect.cl/
- **Dashboard**: https://medconnect.cl/patient
- **Perfil**: https://medconnect.cl/profile

### API Endpoints
- **Health**: https://medconnect.cl/health
- **Webhook**: https://medconnect.cl/webhook
- **Setup Webhook**: https://medconnect.cl/setup-webhook

### Recursos
- **Google Sheets**: https://docs.google.com/spreadsheets/d/1UvnO2lpZSyv13Hf2eG--kQcTff5BBh7jrZ6taFLJypU
- **Telegram Bot**: https://t.me/medconnect_bot

---

## 🚨 **Troubleshooting**

### Error 500 en la aplicación
```bash
# Ver logs
railway logs

# Verificar variables de entorno
railway variables
```

### Bot no responde
1. Verificar webhook: `https://medconnect.cl/setup-webhook`
2. Probar manualmente: `/start` en @medconnect_bot
3. Revisar logs de Railway

### Error Google Sheets
1. Verificar que la hoja esté compartida con el service account
2. Comprobar el ID de la hoja en las variables de entorno
3. Verificar las credenciales JSON

---

## 🎉 **¡LISTO PARA PRODUCCIÓN!**

Tu aplicación MedConnect está completamente configurada y lista para desplegar en Railway con:

- ✅ **Backend Flask** funcional
- ✅ **Google Sheets** como base de datos
- ✅ **Bot de Telegram** integrado
- ✅ **Interfaz moderna** con colores oficiales
- ✅ **Dominio personalizado** medconnect.cl
- ✅ **Datos de ejemplo** incluidos

**Próximo paso**: Ejecutar `railway up` y configurar el dominio. 