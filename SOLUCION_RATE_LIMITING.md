# Solución para Rate Limiting de Google Sheets API

## Problema Identificado

```
Quota exceeded for quota metric 'Read requests' and limit 'Read requests per minute per user' 
of service 'sheets.googleapis.com' for consumer 'project_number:57008822340'
```

El error indica que has superado el límite de **60 solicitudes de lectura por minuto** por usuario en Google Sheets API.

## Soluciones Implementadas

### 1. **Rate Limiting Automático**
- ✅ Implementado en `SheetsManager`
- ✅ Límite conservador: 50 requests/minuto (por debajo del límite de 60)
- ✅ Espera automática cuando se alcanza el límite

### 2. **Sistema de Cache**
- ✅ Cache de 30 segundos para datos frecuentemente accedidos
- ✅ Reduce llamadas a la API
- ✅ Limpieza automática de cache expirado

### 3. **Retry con Exponential Backoff**
- ✅ Reintentos automáticos con espera progresiva
- ✅ Manejo específico de errores 429 (rate limit)
- ✅ Hasta 3 intentos con esperas de 2, 4, 8 segundos

### 4. **Inicialización Robusta**
- ✅ Script `sheets_manager_init.py` para inicialización con fallbacks
- ✅ Configuración alternativa si falla la inicialización principal
- ✅ Logging detallado para debugging

## Configuración Recomendada

### Variables de Entorno en Railway

Asegúrate de que estas variables estén configuradas:

```
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
GOOGLE_SHEETS_ID=tu_sheet_id
FLASK_ENV=production
RAILWAY_ENVIRONMENT=production
```

### Límites de API

**Límites actuales de Google Sheets API:**
- **Read requests**: 60 por minuto por usuario
- **Write requests**: 300 por minuto por usuario
- **Requests per 100 seconds per user**: 300

**Configuración implementada:**
- **Límite conservador**: 50 requests/minuto
- **Cache duration**: 30 segundos
- **Retry attempts**: 3 con exponential backoff

## Monitoreo y Debugging

### Endpoints de Debug

1. **`/health`** - Estado general de la aplicación
2. **`/debug-env`** - Variables de entorno
3. **`/debug-auth`** - Estado de autenticación

### Logs a Monitorear

```bash
# Buscar estos patrones en los logs:
✅ SheetsManager importado correctamente
⚠️ Rate limit alcanzado, esperando X segundos
📋 Datos obtenidos del cache
💾 Datos guardados en cache
```

## Optimizaciones Adicionales

### 1. **Reducir Frecuencia de Llamadas**

- Cache más largo para datos estáticos
- Llamadas en lote cuando sea posible
- Evitar polling innecesario

### 2. **Implementar Paginación**

- Cargar datos en chunks
- Lazy loading para listas largas
- Paginación en el frontend

### 3. **Usar Webhooks (si es posible)**

- Notificaciones push en lugar de polling
- Reducir llamadas de verificación

## Troubleshooting

### Si sigues viendo errores 429:

1. **Verificar logs de Railway**:
   ```bash
   # En Railway Dashboard > Logs
   # Buscar patrones de rate limiting
   ```

2. **Revisar configuración de cache**:
   ```python
   # En sheets_manager.py
   self.cache_duration = 60  # Aumentar a 60 segundos
   self.max_requests_per_minute = 40  # Reducir a 40
   ```

3. **Implementar cache persistente**:
   ```python
   # Usar Redis o archivo local para cache
   import pickle
   # Guardar cache en archivo
   ```

### Comandos Útiles

```bash
# Verificar estado de la aplicación
curl https://tu-app.railway.app/health

# Ver logs en tiempo real
railway logs --follow

# Reiniciar aplicación
railway up
```

## Solución de Emergencia

Si la aplicación no puede conectarse debido a rate limiting:

1. **Esperar 1-2 minutos** para que se resetee el contador
2. **Reiniciar la aplicación** en Railway
3. **Verificar que no hay múltiples instancias** ejecutándose

## Verificación Final

Después de implementar estas soluciones:

1. ✅ No más errores 429 en los logs
2. ✅ Aplicación responde correctamente
3. ✅ Cache funciona (menos llamadas a API)
4. ✅ Rate limiting automático activo

## Contacto con Google

Si necesitas aumentar los límites:

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Selecciona tu proyecto
3. Ve a "APIs & Services" > "Quotas"
4. Solicita aumento de límites para Google Sheets API

**Nota**: Los aumentos de límites pueden tardar varios días en ser aprobados. 