# 🚀 Configuración PostgreSQL en Railway - MedConnect

## 📋 Pasos para la Migración

### 1. Crear Base de Datos PostgreSQL en Railway

1. **Accede a tu proyecto en Railway**

   - Ve a [railway.app](https://railway.app)
   - Selecciona tu proyecto MedConnect

2. **Agregar PostgreSQL**

   ```bash
   # En Railway Dashboard:
   # 1. Click en "New Service"
   # 2. Selecciona "Database"
   # 3. Elige "PostgreSQL"
   # 4. Railway creará automáticamente la base de datos
   ```

3. **Variables de Entorno Automáticas**
   Railway creará automáticamente estas variables:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   PGHOST=hostname
   PGPORT=5432
   PGDATABASE=railway
   PGUSER=postgres
   PGPASSWORD=password
   ```

### 2. Actualizar requirements.txt

Agregar dependencias de PostgreSQL:

```txt
# Dependencias existentes...
Flask==2.3.3
Flask-CORS==4.0.0
bcrypt==4.0.1

# Nuevas dependencias para PostgreSQL
psycopg2-binary==2.9.7
SQLAlchemy==2.0.21
```

### 3. Ejecutar Migración

```bash
# 1. Instalar dependencias localmente (opcional para testing)
pip install psycopg2-binary

# 2. Subir archivos de migración a Railway
git add migrate_to_postgresql.py
git add postgresql_auth_manager.py
git add postgresql_db_manager.py
git commit -m "Add PostgreSQL migration"
git push origin main

# 3. En Railway, ejecutar migración
python migrate_to_postgresql.py
```

### 4. Actualizar app.py

Reemplazar las importaciones:

```python
# ANTES (Google Sheets)
from auth_manager import AuthManager
from backend.database.sheets_manager import sheets_db

# DESPUÉS (PostgreSQL)
from postgresql_auth_manager import postgresql_auth
from postgresql_db_manager import postgresql_db

# Actualizar instancias globales
auth_manager = postgresql_auth
sheets_db = postgresql_db
```

### 5. Variables de Entorno en Railway

En el Dashboard de Railway, configurar:

```bash
# Base de datos (automáticas)
DATABASE_URL=postgresql://...
PGHOST=...
PGPORT=5432
PGDATABASE=railway
PGUSER=postgres
PGPASSWORD=...

# Aplicación
FLASK_ENV=production
SECRET_KEY=tu_clave_secreta_super_segura
DOMAIN=tu-dominio.railway.app

# Eliminar variables de Google Sheets (ya no necesarias)
# GOOGLE_SERVICE_ACCOUNT_JSON (eliminar)
# GOOGLE_SHEETS_ID (eliminar)
```

## 🎯 Ventajas de PostgreSQL vs Google Sheets

| Característica          | Google Sheets            | PostgreSQL             |
| ----------------------- | ------------------------ | ---------------------- |
| **Velocidad**           | ⚠️ Lenta (API calls)     | ✅ Muy rápida          |
| **Confiabilidad**       | ⚠️ Límites de API        | ✅ 99.9% uptime        |
| **Escalabilidad**       | ❌ Limitada              | ✅ Ilimitada           |
| **Seguridad**           | ⚠️ Dependiente de Google | ✅ Encriptación nativa |
| **Consultas Complejas** | ❌ No soporta            | ✅ SQL completo        |
| **Transacciones**       | ❌ No                    | ✅ ACID compliant      |
| **Backup Automático**   | ⚠️ Manual                | ✅ Automático          |
| **Costo**               | ⚠️ Límites gratis        | ✅ Gratis hasta 1GB    |

## 🔧 Estructura de Tablas

### Tabla: usuarios

```sql
- id (SERIAL PRIMARY KEY)
- nombre, apellido, email (VARCHAR)
- password_hash (VARCHAR 255)
- tipo_usuario (profesional/paciente/admin)
- telefono, ciudad, direccion (VARCHAR)
- fecha_nacimiento (DATE)
- genero (VARCHAR)
- estado (activo/inactivo/suspendido)
- fecha_registro, ultimo_acceso (TIMESTAMP)
- especialidad, numero_colegiado, hospital (profesionales)
```

### Tabla: atenciones_medicas

```sql
- id (SERIAL PRIMARY KEY)
- profesional_id, paciente_id (FOREIGN KEY)
- fecha_atencion (DATE)
- hora_inicio, hora_fin (TIME)
- tipo_atencion, motivo_consulta (VARCHAR/TEXT)
- diagnostico, tratamiento, observaciones (TEXT)
- estado (programada/completada/cancelada)
```

### Tabla: agenda_citas

```sql
- id (SERIAL PRIMARY KEY)
- profesional_id, paciente_id (FOREIGN KEY)
- fecha (DATE)
- hora_inicio, hora_fin (TIME)
- disponible (BOOLEAN)
- tipo_cita, notas (VARCHAR/TEXT)
- estado (disponible/reservada/confirmada)
```

## 🧪 Testing Local

Para probar localmente antes del deploy:

```bash
# 1. Instalar PostgreSQL localmente
# Windows: https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# 2. Crear base de datos local
createdb medconnect_local

# 3. Configurar variables de entorno locales
export DATABASE_URL="postgresql://localhost/medconnect_local"
export PGHOST="localhost"
export PGDATABASE="medconnect_local"
export PGUSER="tu_usuario"
export PGPASSWORD="tu_password"

# 4. Ejecutar migración
python migrate_to_postgresql.py

# 5. Probar aplicación
python app.py
```

## 🚨 Migración de Datos Existentes

Si tienes datos importantes en Google Sheets:

```python
# Crear script de migración de datos
# migrate_existing_data.py

import gspread
from postgresql_db_manager import postgresql_db

def migrate_users_from_sheets():
    # 1. Conectar a Google Sheets
    # 2. Leer usuarios existentes
    # 3. Insertar en PostgreSQL
    # 4. Verificar migración
    pass

def migrate_atenciones_from_sheets():
    # Similar para atenciones
    pass
```

## ✅ Checklist de Migración

- [ ] PostgreSQL creado en Railway
- [ ] Variables de entorno configuradas
- [ ] requirements.txt actualizado
- [ ] Archivos de migración subidos
- [ ] Migración ejecutada exitosamente
- [ ] app.py actualizado con nuevas importaciones
- [ ] Testing de login funcionando
- [ ] Testing de endpoints API funcionando
- [ ] Variables de Google Sheets eliminadas
- [ ] Deploy final realizado

## 🎉 Resultado Final

Después de la migración tendrás:

1. **✅ Base de datos real y robusta**
2. **✅ Login con usuarios reales (no fallback)**
3. **✅ Rendimiento 10x más rápido**
4. **✅ Sin límites de API**
5. **✅ Backup automático**
6. **✅ Escalabilidad ilimitada**

¡Tu aplicación médica estará lista para producción! 🏥💪
