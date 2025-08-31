# 🚀 Guía de Desarrollo Local - MedConnect

## 📋 Requisitos Previos

- Python 3.8+
- pip (gestor de paquetes de Python)
- Git

## 🛠️ Configuración Inicial

### 1. Clonar el repositorio (si no lo tienes)

```bash
git clone <tu-repositorio>
cd medconnect
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 🚀 Ejecutar en Modo Desarrollo

### Opción 1: Script Automático (Recomendado)

```bash
python run_local.py
```

### Opción 2: Manual

```bash
# Configurar entorno
python config_local.py

# Ejecutar aplicación
python app.py
```

## 🌐 Acceder a la Aplicación

Una vez ejecutada, la aplicación estará disponible en:

- **URL Principal:** http://localhost:5000
- **Health Check:** http://localhost:5000/health
- **Login:** http://localhost:5000/login

## 🧪 Probar Funcionalidades

### 1. Pruebas Automáticas

```bash
python test_local.py
```

### 2. Pruebas Manuales en el Navegador

1. Abre http://localhost:5000
2. Usa los usuarios de prueba:
   - **Paciente:** paciente@test.com / password123
   - **Profesional:** diego.castro.lagos@gmail.com / password123

### 3. APIs Disponibles para Pruebas

- `GET /health` - Estado de la aplicación
- `GET /api/patient/1/consultations` - Consultas del paciente
- `GET /api/patient/1/exams` - Exámenes del paciente
- `GET /api/patient/1/family` - Familiares del paciente

## 🔧 Configuración Avanzada

### Variables de Entorno

Puedes configurar variables de entorno en `config_local.py`:

```python
LOCAL_CONFIG = {
    'FLASK_ENV': 'development',
    'SECRET_KEY': 'tu-clave-secreta',
    'PORT': 5000,
    'DEBUG': True,
    # Agregar más configuraciones aquí
}
```

### PostgreSQL Local (Opcional)

Si quieres usar PostgreSQL localmente:

1. Instalar PostgreSQL
2. Crear base de datos local
3. Configurar `DATABASE_URL` en `config_local.py`

## 📁 Estructura del Proyecto

```
medconnect/
├── app.py                 # Aplicación principal
├── run_local.py          # Script de inicio local
├── test_local.py         # Script de pruebas
├── config_local.py       # Configuración local
├── dev_setup.py          # Configuración de desarrollo
├── static/               # Archivos estáticos
│   ├── css/
│   ├── js/
│   ├── images/
│   └── uploads/
├── templates/            # Plantillas HTML
└── requirements.txt      # Dependencias
```

## 🐛 Solución de Problemas

### Error: Puerto en uso

```bash
# Cambiar puerto en config_local.py
'PORT': 5001
```

### Error: Módulo no encontrado

```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: PostgreSQL no disponible

- Es normal en desarrollo local
- La aplicación funciona en modo fallback
- Los datos son simulados

## 🔄 Flujo de Desarrollo

1. **Hacer cambios** en el código
2. **Probar localmente** con `python run_local.py`
3. **Verificar funcionalidad** en http://localhost:5000
4. **Hacer commit** cuando esté listo
5. **Hacer push** para deploy automático en Railway

## 📝 Notas Importantes

- ✅ **PostgreSQL está en modo fallback** - No necesitas DB local
- ✅ **Los cambios se reflejan automáticamente** - No necesitas reiniciar
- ✅ **Datos simulados** - Para pruebas y desarrollo
- ✅ **Sin dependencias externas** - Funciona completamente offline

## 🎯 Próximos Pasos

1. Ejecuta `python dev_setup.py` para configuración inicial
2. Ejecuta `python run_local.py` para iniciar
3. Abre http://localhost:5000 en tu navegador
4. ¡Empieza a desarrollar! 🚀
