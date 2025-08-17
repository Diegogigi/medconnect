# 🔧 Solución para Rate Limiting de Google Sheets

## 🚨 Problema Identificado

**Error 429 - Rate Limit Exceeded:**

```
Quota exceeded for quota metric 'Write requests' and limit 'Write requests per minute per user' of service 'sheets.googleapis.com'
```

## 📊 Límites de Google Sheets

### **Límites por Usuario:**

- **60 escrituras por minuto** por usuario
- **300 escrituras por 100 segundos** por usuario

### **Límites por Proyecto:**

- **300 escrituras por minuto** por proyecto

## 🛠️ Soluciones Implementadas

### **1. Sistema de Rate Limiting**

**Archivo:** `rate_limiter.py`

**Características:**

- ✅ Control automático de solicitudes
- ✅ Espera inteligente cuando se alcanza el límite
- ✅ Reintentos automáticos en caso de error 429
- ✅ Monitoreo en tiempo real del uso

### **2. Optimizaciones Recomendadas**

#### **A. Reducir Operaciones de Escritura:**

```javascript
// ❌ MAL: Múltiples escrituras individuales
for (let i = 0; i < 100; i++) {
  worksheet.append_row([data[i]]);
}

// ✅ BIEN: Una sola escritura en lote
worksheet.append_rows(data);
```

#### **B. Implementar Caché:**

```python
# Cachear datos para reducir lecturas
@rate_limited_sheets_operation
def get_cached_data():
    if cache.is_valid():
        return cache.get_data()
    else:
        data = sheets.get_data()
        cache.set_data(data)
        return data
```

#### **C. Agrupar Operaciones:**

```python
# Agrupar múltiples cambios en una sola operación
def batch_update_schedule(changes):
    with rate_limiter:
        worksheet.batch_update(changes)
```

## 🔍 Diagnóstico del Problema

### **Posibles Causas:**

1. **Operaciones Excesivas:**

   - Múltiples usuarios escribiendo simultáneamente
   - Bucle infinito en sincronización
   - Operaciones redundantes

2. **Falta de Optimización:**

   - Escrituras individuales en lugar de lotes
   - Sin caché de datos
   - Sin control de frecuencia

3. **Problemas de Código:**
   - Funciones que se ejecutan repetidamente
   - Eventos que se disparan múltiples veces
   - Sincronización excesiva

## 🚀 Implementación Inmediata

### **Paso 1: Aplicar Rate Limiter**

```python
from rate_limiter import rate_limited_sheets_operation

@rate_limited_sheets_operation
def update_schedule(data):
    # Tu código de actualización aquí
    worksheet.append_row(data)
```

### **Paso 2: Optimizar Operaciones**

```python
# En lugar de múltiples append_row
def batch_update_appointments(appointments):
    if not appointments:
        return

    # Agrupar todos los datos
    rows = []
    for appointment in appointments:
        rows.append([
            appointment['id'],
            appointment['date'],
            appointment['time'],
            # ... otros campos
        ])

    # Una sola operación de escritura
    worksheet.append_rows(rows)
```

### **Paso 3: Implementar Caché**

```python
import time

class SheetsCache:
    def __init__(self, ttl_seconds=300):  # 5 minutos
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
        return None

    def set(self, key, data):
        self.cache[key] = (data, time.time())

# Usar caché
cache = SheetsCache()
```

## 📈 Monitoreo

### **Verificar Uso Actual:**

```python
from rate_limiter import sheets_rate_limiter

status = sheets_rate_limiter.get_status()
print(f"Solicitudes actuales: {status['current_requests']}")
print(f"Solicitudes disponibles: {status['available_requests']}")
```

### **Logs de Actividad:**

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sheets_operations')

def log_sheets_operation(operation, success=True):
    logger.info(f"Google Sheets {operation}: {'✅' if success else '❌'}")
```

## 🔄 Plan de Acción

### **Inmediato (Hoy):**

1. ✅ Implementar rate limiter
2. ✅ Aplicar a funciones críticas
3. ✅ Monitorear uso

### **Corto Plazo (Esta Semana):**

1. 🔄 Optimizar operaciones de escritura
2. 🔄 Implementar caché
3. 🔄 Revisar código por bucles infinitos

### **Mediano Plazo (Próximo Mes):**

1. 🔄 Migrar a operaciones en lote
2. 🔄 Implementar base de datos local
3. 🔄 Optimizar sincronización

## 🆘 En Caso de Emergencia

### **Si el Error Persiste:**

1. **Pausar Operaciones:**

   ```python
   # Pausar todas las escrituras por 5 minutos
   time.sleep(300)
   ```

2. **Verificar Uso:**

   ```python
   # Verificar estado del rate limiter
   status = sheets_rate_limiter.get_status()
   print(status)
   ```

3. **Contactar Soporte:**
   - Solicitar aumento de cuota: https://cloud.google.com/docs/quotas/help/request_increase
   - Documentar el problema con logs

## 📞 Contacto de Soporte

- **Google Cloud Console:** https://console.cloud.google.com
- **Solicitar Aumento de Cuota:** https://cloud.google.com/docs/quotas/help/request_increase
- **Documentación:** https://developers.google.com/sheets/api/limits
