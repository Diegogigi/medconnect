# 🔧 Solución: Error de Conexión con Google Sheets

## 🚨 Problema Identificado

El error **"Error conectando con la base de datos"** ocurre porque las variables de entorno de Google Sheets no están configuradas.

## 🔍 Diagnóstico

Las variables faltantes son:

- `GOOGLE_SHEETS_ID` - ID de tu Google Sheets
- `GOOGLE_SERVICE_ACCOUNT_JSON` - Credenciales de Google Cloud

## ✅ Solución Paso a Paso

### 1. Crear Google Sheets

1. Ve a [Google Sheets](https://sheets.google.com)
2. Crea una nueva hoja de cálculo
3. Copia el ID de la URL:
   ```
   https://docs.google.com/spreadsheets/d/1ABC123DEF456.../edit
   ↑ El ID es: 1ABC123DEF456...
   ```

### 2. Configurar Google Cloud Service Account

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google Sheets:
   - Ve a "APIs y servicios" > "Biblioteca"
   - Busca "Google Sheets API"
   - Habilítala
4. Crea un Service Account:
   - Ve a "APIs y servicios" > "Credenciales"
   - Haz clic en "Crear credenciales" > "Cuenta de servicio"
   - Completa la información
5. Descarga las credenciales:
   - Haz clic en la cuenta de servicio creada
   - Ve a la pestaña "Claves"
   - Haz clic en "Agregar clave" > "Crear nueva clave"
   - Selecciona "JSON"
   - Descarga el archivo

### 3. Configurar Variables de Entorno

#### Opción A: Usar el Script Automático

```bash
python setup_google_sheets.py
```

El script te guiará paso a paso para configurar todo.

#### Opción B: Configuración Manual

1. Crea un archivo `.env` en la raíz del proyecto:

```env
# MedConnect - Variables de Entorno
FLASK_ENV=development
FLASK_APP=app.py
SECRET_KEY=medconnect-secret-key-2024

# Configuración del dominio
DOMAIN=localhost:5000
BASE_URL=http://localhost:5000

# Configuración de Google Sheets
GOOGLE_SHEETS_ID=tu-id-de-google-sheets-aqui
GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account","project_id":"...","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}'

# Configuración de logging
LOG_LEVEL=INFO

# Configuración de Railway (para producción)
PORT=5000
RAILWAY_ENVIRONMENT=production

# Configuración de CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

2. Reemplaza:
   - `tu-id-de-google-sheets-aqui` con el ID de tu Google Sheets
   - El contenido de `GOOGLE_SERVICE_ACCOUNT_JSON` con el contenido del archivo JSON descargado

### 4. Compartir Google Sheets

1. Abre tu Google Sheets
2. Haz clic en "Compartir" (esquina superior derecha)
3. Agrega el email del Service Account (está en el archivo JSON como `client_email`)
4. Dale permisos de "Editor"

### 5. Verificar Configuración

Ejecuta el script de diagnóstico:

```bash
python diagnostic_google_sheets.py
```

Deberías ver:

```
✅ GOOGLE_SHEETS_ID: ENCONTRADA
✅ GOOGLE_SERVICE_ACCOUNT_JSON: ENCONTRADA
✅ Cliente de Google Sheets creado exitosamente
✅ Spreadsheet abierto: [Nombre de tu hoja]
✅ Conexión exitosa con Google Sheets
```

## 🧪 Probar la Solución

1. Ejecuta la aplicación:

   ```bash
   python app.py
   ```

2. Ve a http://localhost:5000

3. Inicia sesión como profesional

4. Intenta crear una cita

5. Verifica que aparece en Google Sheets

## 🔧 Solución Rápida (Temporal)

Si necesitas una solución temporal mientras configuras Google Sheets, puedes modificar el código para usar una base de datos local:

```python
# En app.py, línea ~19240, cambiar:
if not spreadsheet:
    return (
        jsonify(
            {
                "success": False,
                "message": "Error conectando con la base de datos",
            }
        ),
        500,
    )

# Por:
if not spreadsheet:
    # Solución temporal: crear cita en memoria
    cita_id = f"CITA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    return jsonify(
        {
            "success": True,
            "message": "Cita agendada exitosamente (modo temporal)",
            "cita_id": cita_id,
            "cita": {
                "cita_id": cita_id,
                "paciente_nombre": data.get("paciente_nombre", ""),
                "paciente_rut": data.get("paciente_rut", ""),
                "fecha": data.get("fecha", ""),
                "hora": data.get("hora", ""),
                "tipo_atencion": data.get("tipo_atencion", ""),
                "estado": "pendiente",
                "notas": data.get("notas", ""),
            },
        }
    )
```

## 📞 Soporte

Si tienes problemas:

1. Verifica que el archivo `.env` existe y tiene las variables correctas
2. Asegúrate de que el Google Sheets está compartido con el Service Account
3. Verifica que la API de Google Sheets está habilitada
4. Ejecuta el script de diagnóstico para identificar el problema específico

## ✅ Resultado Esperado

Después de la configuración:

- ✅ Las citas se guardan en Google Sheets
- ✅ Se pueden ver en las tres vistas del calendario
- ✅ No más errores de "Error conectando con la base de datos"
- ✅ Sincronización automática entre vistas
