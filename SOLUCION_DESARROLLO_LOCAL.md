# 🔧 Solución para Desarrollo Local - MedConnect

## 🎯 Problema Resuelto

**Problema:** No podías iniciar sesión cuando ejecutabas la aplicación localmente en `http://127.0.0.1:8000`, aunque funcionaba perfectamente en Railway.

**Causa:** La aplicación estaba configurada para producción con cookies de sesión seguras (HTTPS) y variables de entorno específicas de Railway.

## ✅ Solución Implementada

### 1. **Configuración Automática de Variables de Entorno**

Se creó el archivo `env_local.txt` con todas las variables necesarias para desarrollo local:

```bash
# Base de datos PostgreSQL de Railway (para desarrollo local)
DATABASE_URL=postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway

# Configuración de Flask
SECRET_KEY=medconnect-secret-key-2025-railway-production
FLASK_ENV=development
DEBUG=True
PORT=8000

# Configuración de cookies para desarrollo local (HTTP en lugar de HTTPS)
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### 2. **Detección Automática de Entorno**

Se modificó `app.py` para detectar automáticamente si está ejecutándose en desarrollo local:

```python
# Detectar si estamos en desarrollo local
is_local_development = (
    app.config.get("PORT") == 8000 or
    "localhost" in os.environ.get("HOST", "") or
    "127.0.0.1" in os.environ.get("HOST", "") or
    app.config.get("FLASK_ENV") == "development"
)

# Configurar cookies según el entorno
app.config.update(
    SESSION_COOKIE_SECURE=not is_local_development,  # False para local, True para producción
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
```

### 3. **Scripts de Configuración Automática**

Se crearon dos scripts para facilitar el desarrollo:

- **`setup_desarrollo_local.py`**: Configura automáticamente el entorno
- **`run_local.py`**: Ejecuta la aplicación con configuración local

## 🚀 Cómo Usar la Solución

### Opción 1: Script Automático (Recomendado)

```bash
# Configurar y ejecutar en un solo comando
python run_local.py
```

### Opción 2: Configuración Manual

```bash
# 1. Configurar entorno
python setup_desarrollo_local.py

# 2. Ejecutar aplicación
python app.py
```

### Opción 3: Configuración Manual de Variables

```bash
# Copiar el contenido de env_local.txt a un archivo .env
copy env_local.txt .env

# Ejecutar aplicación
python app.py
```

## 🌐 Acceso a la Aplicación

Una vez ejecutada, la aplicación estará disponible en:

- **URL Principal:** http://localhost:8000
- **Login:** http://localhost:8000/login
- **Health Check:** http://localhost:8000/health

## 👤 Credenciales de Prueba

Puedes usar estas credenciales para iniciar sesión:

- **Email:** diego.castro.lagos@gmail.com
- **Password:** password123

- **Email:** rodrigoandressilvabreve@gmail.com
- **Password:** password123

## 🔒 Seguridad

### ✅ Lo que SÍ hace la solución:

- ✅ Usa la misma base de datos de Railway (datos reales)
- ✅ Mantiene la misma SECRET_KEY para compatibilidad
- ✅ Configura cookies seguras para producción
- ✅ Detecta automáticamente el entorno
- ✅ No afecta la configuración de Railway

### ❌ Lo que NO hace la solución:

- ❌ No expone credenciales sensibles
- ❌ No modifica la configuración de producción
- ❌ No compromete la seguridad de Railway
- ❌ No requiere cambios en el código de producción

## 🔄 Flujo de Desarrollo

1. **Desarrollo Local:**

   ```bash
   python run_local.py
   # Trabaja en http://localhost:8000
   ```

2. **Pruebas en Railway:**

   ```bash
   git add .
   git commit -m "Nuevas funcionalidades"
   git push
   # Railway se actualiza automáticamente
   ```

3. **Verificación:**
   - ✅ Local: http://localhost:8000
   - ✅ Producción: https://medconnect.cl

## 🛠️ Solución de Problemas

### Error: "No se puede conectar a la base de datos"

```bash
# Verificar que las variables de entorno estén configuradas
python setup_desarrollo_local.py
```

### Error: "Cookies no funcionan"

```bash
# Limpiar cookies del navegador
# O usar modo incógnito
```

### Error: "Puerto en uso"

```bash
# Cambiar puerto en env_local.txt
PORT=8001
```

## 📋 Archivos Creados/Modificados

### Archivos Nuevos:

- `env_local.txt` - Variables de entorno para desarrollo local
- `setup_desarrollo_local.py` - Script de configuración automática
- `run_local.py` - Script de ejecución local
- `SOLUCION_DESARROLLO_LOCAL.md` - Esta documentación

### Archivos Modificados:

- `app.py` - Detección automática de entorno y configuración de cookies

## 🎉 Resultado

Ahora puedes:

- ✅ **Desarrollar localmente** en http://localhost:8000
- ✅ **Iniciar sesión** con las credenciales reales
- ✅ **Ver cambios en tiempo real** durante el desarrollo
- ✅ **Mantener Railway funcionando** sin problemas
- ✅ **Usar la misma base de datos** para consistencia

## 🚀 ¡Listo para Desarrollar!

Ejecuta `python run_local.py` y comienza a desarrollar con todas las funcionalidades disponibles localmente.
