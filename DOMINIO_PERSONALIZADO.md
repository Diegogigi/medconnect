# 🌐 Configuración Dominio Personalizado: www.medconnect.cl

## 🎯 Objetivo
Configurar **www.medconnect.cl** como dominio personalizado para el despliegue de MedConnect en Railway.

## 📋 Pasos de Configuración

### 1️⃣ **Configuración en Railway**

#### Agregar Dominio Personalizado:
1. Ve a tu proyecto en Railway
2. **Settings** → **Domains**
3. Click **+ Custom Domain**
4. Ingresa: `www.medconnect.cl`
5. Railway te proporcionará el target CNAME

### 2️⃣ **Configuración DNS**

#### En tu proveedor de dominio (ej: GoDaddy, Namecheap, etc.):

**Para www.medconnect.cl:**
```dns
Tipo: CNAME
Nombre: www
Valor: tu-proyecto-railway.up.railway.app
TTL: 300 (5 minutos)
```

**Para medconnect.cl (dominio raíz):**
```dns
Tipo: A
Nombre: @ (o vacío)
Valor: [IP proporcionada por Railway]
TTL: 300
```

### 3️⃣ **Variables de Entorno**

Agregar en Railway → Variables:
```env
CUSTOM_DOMAIN=www.medconnect.cl
FLASK_ENV=production
PREFERRED_URL_SCHEME=https
```

### 4️⃣ **Verificación DNS**

#### Comandos de verificación:
```bash
# Verificar CNAME para www
nslookup www.medconnect.cl

# Verificar A record para dominio raíz
nslookup medconnect.cl

# Verificar propagación DNS
dig www.medconnect.cl

# Verificar SSL
curl -I https://www.medconnect.cl
```

#### Herramientas online:
- **DNS Checker:** https://dnschecker.org/
- **What's My DNS:** https://www.whatsmydns.net/
- **SSL Checker:** https://www.ssllabs.com/ssltest/

### 5️⃣ **Configuración SSL/HTTPS**

Railway proporciona **SSL automático**:
- ✅ Certificado Let's Encrypt gratuito
- ✅ Renovación automática
- ✅ Redirección HTTP → HTTPS
- ✅ HSTS headers incluidos

### 6️⃣ **Configuración de Cookies Seguras**

El código ya incluye configuración segura:
```python
# En app.py
if app.config['PREFERRED_URL_SCHEME'] == 'https':
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

### 7️⃣ **SEO y Meta Tags**

Ya configurado en `templates/index.html`:
```html
<title>MedConnect - Gestión Médica Familiar | www.medconnect.cl</title>
<meta name="description" content="Sistema integral de gestión médica familiar con bot de Telegram. Gestiona citas, medicamentos y salud familiar desde www.medconnect.cl">
<link rel="canonical" href="https://www.medconnect.cl/">

<!-- Open Graph -->
<meta property="og:url" content="https://www.medconnect.cl/">
<meta property="og:title" content="MedConnect - Gestión Médica Familiar">
<meta property="og:image" content="https://www.medconnect.cl/static/images/logo.png">
```

## 🕐 Tiempos de Propagación

- **DNS:** 5-15 minutos (TTL 300)
- **SSL Certificate:** 5-10 minutos
- **Propagación global:** 24-48 horas (máximo)

## 🔍 Verificación Final

### Checklist de verificación:
- [ ] DNS CNAME configurado correctamente
- [ ] SSL certificate activo (candado verde)
- [ ] Redirección HTTP → HTTPS funcionando
- [ ] Bot de Telegram respondiendo
- [ ] Aplicación web cargando correctamente
- [ ] Meta tags SEO mostrándose correctamente

### URLs a probar:
```
✅ https://www.medconnect.cl/
✅ https://www.medconnect.cl/login
✅ https://www.medconnect.cl/register
✅ http://www.medconnect.cl/ (debe redirigir a HTTPS)
```

## 🚨 Solución de Problemas

### DNS no resuelve:
1. **Verificar configuración:** Revisar CNAME y A records
2. **Esperar propagación:** Hasta 24-48 horas
3. **Limpiar cache DNS:** `ipconfig /flushdns` (Windows)

### SSL no funciona:
1. **Verificar dominio:** Debe estar correctamente configurado en Railway
2. **Esperar certificado:** Railway genera automáticamente
3. **Verificar logs:** Railway → Deployments → Logs

### Aplicación no carga:
1. **Verificar variables:** `CUSTOM_DOMAIN` configurada
2. **Verificar Procfile:** Web service corriendo
3. **Revisar logs:** Errores de aplicación

### Bot no responde:
1. **Webhook URL:** Debe usar HTTPS con dominio personalizado
2. **Verificar token:** `TELEGRAM_BOT_TOKEN` correcto
3. **Logs del bot:** Revisar errores de conectividad

## 📊 Monitoreo

### Herramientas recomendadas:
- **Uptime Robot:** Monitoreo gratuito 24/7
- **Google Search Console:** SEO y indexación
- **Google Analytics:** Tráfico y usuarios
- **Railway Metrics:** Uso de recursos

### Configurar monitoreo:
```bash
# Ping automático cada 5 minutos
curl -I https://www.medconnect.cl/

# Verificar bot
curl -X POST https://api.telegram.org/bot[TOKEN]/getMe
```

## 🎯 Beneficios del Dominio Personalizado

### Para usuarios:
- ✅ **Confianza:** Dominio profesional medconnect.cl
- ✅ **Memorabilidad:** Fácil de recordar y compartir
- ✅ **Branding:** Identidad de marca consistente

### Para SEO:
- ✅ **Indexación:** Mejor posicionamiento en Google
- ✅ **Autoridad:** Dominio propio vs subdominio
- ✅ **Analytics:** Métricas más precisas

### Para negocio:
- ✅ **Profesionalismo:** Imagen corporativa sólida
- ✅ **Marketing:** URLs de marketing más efectivas
- ✅ **Credibilidad:** Mayor confianza de usuarios

## 📞 Soporte

### En caso de problemas:
1. **Railway Support:** https://railway.app/support
2. **DNS Provider:** Soporte de tu registrador de dominio
3. **Documentación:** https://docs.railway.app/deploy/custom-domains

### Contacto del proyecto:
- **Email:** medconnect.contacto@gmail.com
- **GitHub:** https://github.com/medconn/medconnect
- **Dominio:** https://www.medconnect.cl 