# 🔧 Solución: Error de Conexión con OpenRouter API

## 🚨 **Problema Identificado**

El sistema está mostrando el siguiente error:

```
❌ ERROR DE CONEXIÓN:
No se pudo conectar con OpenRouter después de probar múltiples modelos.
Posibles causas:
API key incorrecta o expirada
Problema de red
Servicio temporalmente no disponible
Límite de uso alcanzado
```

## 🔍 **Diagnóstico Realizado**

### **Causa Principal:**

- **API Key expirada o inválida**: La API key hardcodeada en el código (`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`) ya no es válida
- **Error 401 - User not found**: Confirma que la API key ha expirado o fue revocada

### **Archivos Afectados:**

- `app.py` (línea 22120)
- `unified_copilot_assistant.py` (línea 201)
- `unified_orchestration_system.py` (línea 755)

---

## ✅ **Solución Paso a Paso**

### **1️⃣ Obtener Nueva API Key de OpenRouter**

1. **Ir a OpenRouter:**

   ```
   https://openrouter.ai/
   ```

2. **Crear cuenta gratuita:**

   - Click en "Sign Up"
   - Completar registro con email
   - Verificar email

3. **Obtener API Key:**
   - Ir a: https://openrouter.ai/keys
   - Click en "Create Key"
   - Copiar la nueva API key (empieza con `sk-or-v1-`)

### **2️⃣ Actualizar Código Local**

**Opción A: Usar Script Automático**

```bash
python fix_openrouter_api_key_simple.py
```

**Opción B: Actualización Manual**

1. **Actualizar `app.py`:**

   ```python
   # Línea 22120 - Reemplazar la API key hardcodeada
   api_key = (
       os.getenv("OPENROUTER_API_KEY")
       or "TU_NUEVA_API_KEY_AQUI"
   )
   ```

2. **Actualizar `unified_copilot_assistant.py`:**

   ```python
   # Línea 201 - Reemplazar la API key hardcodeada
   self.openrouter_api_key = (
       os.getenv("OPENROUTER_API_KEY")
       or "TU_NUEVA_API_KEY_AQUI"
   )
   ```

3. **Actualizar `unified_orchestration_system.py`:**
   ```python
   # Línea 755 - Reemplazar la API key hardcodeada
   api_key = (
       os.getenv("OPENROUTER_API_KEY")
       or "TU_NUEVA_API_KEY_AQUI"
   )
   ```

### **3️⃣ Configurar Variables de Entorno**

**Para Desarrollo Local:**

```bash
# Crear archivo .env
OPENROUTER_API_KEY=tu_nueva_api_key_aqui
FLASK_ENV=development
SECRET_KEY=clave-secreta-local
```

**Para Railway (Producción):**

1. Ir a Railway Dashboard
2. Seleccionar proyecto MedConnect
3. Ir a pestaña "Variables"
4. Agregar:
   ```
   OPENROUTER_API_KEY=tu_nueva_api_key_aqui
   RAILWAY_ENVIRONMENT=production
   FLASK_ENV=production
   SECRET_KEY=clave-secreta-super-segura
   ```
5. Hacer redeploy

---

## 🧪 **Verificación de la Solución**

### **1️⃣ Probar Conexión Local**

```bash
# Ejecutar script de verificación
python check_railway_env.py

# O probar directamente
python -c "
import requests
headers = {'Authorization': 'Bearer TU_NUEVA_API_KEY'}
response = requests.post('https://openrouter.ai/api/v1/chat/completions',
                        headers=headers,
                        json={'model': 'deepseek/deepseek-r1:free',
                              'messages': [{'role': 'user', 'content': 'test'}]})
print('✅ Conexión exitosa' if response.status_code == 200 else '❌ Error')
"
```

### **2️⃣ Probar en la Aplicación**

1. Iniciar servidor: `python app.py`
2. Ir a la aplicación web
3. Probar el chat de Copilot Health
4. Verificar que no aparezcan errores de conexión

### **3️⃣ Verificar en Railway**

1. Hacer redeploy en Railway
2. Verificar logs de Railway
3. Probar la aplicación en producción

---

## 🔧 **Scripts de Ayuda Creados**

### **1️⃣ `check_railway_env.py`**

- Diagnóstico completo del entorno
- Verificación de variables de entorno
- Prueba de conectividad con OpenRouter

### **2️⃣ `fix_openrouter_connection.py`**

- Diagnóstico detallado del problema
- Instrucciones paso a paso
- Verificación de endpoints

### **3️⃣ `update_openrouter_api_key.py`**

- Actualización automática de API keys
- Prueba de validez de la nueva key
- Actualización de todos los archivos

### **4️⃣ `fix_openrouter_api_key_simple.py`**

- Solución rápida y simple
- Actualización automática
- Instrucciones claras

---

## 🚨 **Problemas Comunes y Soluciones**

### **Error 401 - User not found**

- **Causa:** API key expirada o inválida
- **Solución:** Obtener nueva API key de OpenRouter

### **Error 429 - Rate limit exceeded**

- **Causa:** Límite de uso alcanzado
- **Solución:** Esperar o actualizar a cuenta de pago

### **Error de conectividad**

- **Causa:** Problema de red o firewall
- **Solución:** Verificar conectividad a openrouter.ai

### **Variables de entorno no cargadas**

- **Causa:** Archivo .env no existe o mal configurado
- **Solución:** Crear archivo .env con las variables correctas

---

## 📋 **Checklist de Verificación**

- [ ] Nueva API key obtenida de OpenRouter
- [ ] API key probada y funcionando
- [ ] Archivos de código actualizados
- [ ] Archivo .env creado (desarrollo local)
- [ ] Variables configuradas en Railway (producción)
- [ ] Redeploy realizado en Railway
- [ ] Chat de Copilot Health funcionando
- [ ] No aparecen errores de conexión

---

## 💡 **Recomendaciones Adicionales**

### **1️⃣ Seguridad**

- Nunca committear API keys al repositorio
- Usar variables de entorno siempre
- Rotar API keys periódicamente

### **2️⃣ Monitoreo**

- Configurar alertas para errores de API
- Monitorear uso de cuota de OpenRouter
- Revisar logs regularmente

### **3️⃣ Backup**

- Mantener múltiples API keys como respaldo
- Documentar proceso de actualización
- Tener plan de contingencia

---

## 🆘 **Soporte Adicional**

Si el problema persiste:

1. **Verificar estado de OpenRouter:**

   - https://status.openrouter.ai/

2. **Revisar documentación:**

   - https://openrouter.ai/docs

3. **Contactar soporte:**

   - https://openrouter.ai/support

4. **Alternativas de IA:**
   - OpenAI GPT (requiere API key de OpenAI)
   - Anthropic Claude (requiere API key de Anthropic)
   - Hugging Face (modelos locales)

---

**✅ Con esta solución, el problema de conexión con OpenRouter debería estar resuelto completamente.**
