# 🚨 Plan de Contingencia - Límites de Costos Railway

## 💰 **Configuración de Límites Establecida:**
- **Límite duro:** $4.50 (Railway cierra TODO automáticamente)
- **Límite suave:** $3.00 (Alerta por email)
- **Presupuesto incluido:** $5.00/mes
- **Uso estimado MedConnect:** $2-4/mes

---

## 📧 **ESCENARIO 1: LÍMITE SUAVE ($3.00) - ALERTA EMAIL**

### ⚠️ **Qué significa:**
- Has usado $3.00 de los $5.00 incluidos
- Recibes email de alerta
- **Servicios siguen funcionando** normalmente
- Tienes $1.50 restantes antes del límite duro

### ✅ **ACCIONES INMEDIATAS:**

#### **1. Diagnóstico rápido:**
```bash
# Ve a Railway Dashboard → Usage
# Revisa métricas por proyecto:
- Memoria: ¿>2GB constante?
- CPU: ¿>50% por horas?
- Bandwidth: ¿Tráfico inusual?
- Builds: ¿Compilaciones excesivas?
```

#### **2. Identificar culpable:**
- **MedConnect:** ¿Bot enviando mensajes masivos?
- **Otros proyectos:** ¿Alguno consumiendo más de lo normal?
- **Logs:** ¿Errores repetitivos que consuman recursos?

#### **3. Soluciones rápidas:**
```bash
# Pausar proyectos no esenciales
1. Railway → Proyecto → Settings → Pause

# Revisar logs del bot
2. Railway → MedConnect → Logs → Buscar errores

# Optimizar recursos
3. Verificar loops infinitos en código
4. Reducir frecuencia de polling si existe
```

### 🔧 **Optimizaciones código:**
```python
# En bot.py - Reducir uso de recursos
import time
import logging

# Agregar delays entre operaciones
time.sleep(0.1)  # Entre mensajes

# Optimizar logs
logging.basicConfig(level=logging.WARNING)  # Solo errores importantes
```

---

## 🛑 **ESCENARIO 2: LÍMITE DURO ($4.50) - RAILWAY CIERRA TODO**

### ⚠️ **Qué pasa:**
- **TODOS los servicios se PAUSAN** automáticamente
- **MedConnect se detiene** (web + bot)
- **NO hay cobros adicionales** ✅
- **Usuarios no pueden acceder** al sistema

### 🚀 **PLAN DE REACTIVACIÓN:**

#### **Opción A: Esperar nuevo ciclo (Recomendado)**
```bash
# Esperar hasta el día 26 del próximo mes
# Los $5.00 se renuevan automáticamente
# Reactivar servicios manualmente
```

#### **Opción B: Aumentar límite (Si es urgente)**
```bash
# Railway → Billing → Increase limit
# Costo adicional: $0.50-2.00 por el resto del mes
# Solo si es crítico para el negocio
```

#### **Opción C: Migración temporal**
```bash
# Activar bot local mientras tanto:
cd C:\Users\hp\Desktop\medconnect
python run_bot.py

# Web app en Render.com (gratuito):
# 1. Conectar GitHub a Render
# 2. Deploy solo la web app
# 3. Pausar bot en Render (solo local)
```

---

## 📊 **MONITOREO PREVENTIVO DIARIO**

### **🕐 Rutina diaria (2 minutos):**
1. **Railway Dashboard** → **Usage**
2. **Verificar uso actual:** ¿<$2.50?
3. **Revisar proyectos:** ¿Alguno anormal?
4. **Logs rápidos:** ¿Errores nuevos?

### **📈 Señales de alerta temprana:**
- ✅ **Normal:** <$1.00/día ($30/mes)
- ⚠️ **Vigilar:** $1.00-1.50/día
- 🚨 **Actuar:** >$1.50/día

### **🔔 Configurar alertas adicionales:**
```bash
# En Railway → Project → Settings → Notifications
# Agregar webhook Discord/Slack si tienes
# Email adicional para alertas críticas
```

---

## 🆘 **ALTERNATIVAS DE EMERGENCIA**

### **1. Bot local (Inmediato):**
```bash
# En tu PC mientras solucionas:
cd C:\Users\hp\Desktop\medconnect
python run_bot.py
# Solo bot funcionando, web app pausada
```

### **2. Render.com (Gratuito):**
- **Pros:** Gratuito, fácil deploy
- **Contras:** Duerme después 15min inactividad
- **Uso:** Solo web app, bot local

### **3. Railway Pro ($20/mes):**
- **Solo si es crítico** para el negocio
- **Recursos ilimitados** prácticamente
- **Downgrade después** si no es necesario

### **4. VPS alternativo:**
- **DigitalOcean:** $5/mes básico
- **Linode:** $5/mes básico
- **AWS Free Tier:** 12 meses gratis

---

## 🔧 **OPTIMIZACIONES CÓDIGO PREVENTIVAS**

### **Bot optimizado:**
```python
# En bot.py
import time
from functools import lru_cache

# Cache para reducir llamadas a Sheets
@lru_cache(maxsize=100)
def get_user_data(user_id):
    # Cache por 5 minutos
    pass

# Delays entre operaciones
def send_message_safe(chat_id, text):
    time.sleep(0.1)  # Evitar rate limits
    bot.send_message(chat_id, text)

# Logs optimizados
logging.basicConfig(level=logging.WARNING)
```

### **Web app optimizada:**
```python
# En app.py
from flask_caching import Cache

# Cache para reducir carga
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=300)  # 5 minutos
def get_patient_data():
    # Cache consultas frecuentes
    pass
```

---

## 📞 **CONTACTOS DE EMERGENCIA**

### **Soporte Railway:**
- **Discord:** https://discord.gg/railway
- **Docs:** https://docs.railway.app
- **Support:** https://railway.app/support

### **Alternativas rápidas:**
- **Render:** https://render.com
- **Heroku:** https://heroku.com
- **DigitalOcean:** https://digitalocean.com

---

## 📋 **CHECKLIST DE EMERGENCIA**

### **Al recibir alerta $3.00:**
- [ ] Revisar Railway Usage Dashboard
- [ ] Identificar proyecto que más consume
- [ ] Pausar proyectos no esenciales
- [ ] Revisar logs por errores
- [ ] Optimizar código si es necesario

### **Si llega a límite $4.50:**
- [ ] Evaluar criticidad del servicio
- [ ] Activar bot local si es urgente
- [ ] Decidir: esperar vs aumentar límite
- [ ] Comunicar a usuarios si es necesario
- [ ] Planificar optimizaciones para próximo mes

### **Prevención mensual:**
- [ ] Revisar uso del mes anterior
- [ ] Optimizar código si uso >$3/mes
- [ ] Considerar alternativas si crece mucho
- [ ] Actualizar límites si es necesario

---

**💡 Recuerda:** Es mejor ser conservador con los límites. $4.50 es seguro para MedConnect y evita sorpresas en la factura. 