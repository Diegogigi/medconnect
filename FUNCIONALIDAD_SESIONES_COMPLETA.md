# 📋 FUNCIONALIDAD DE SESIONES - MEDCONNECT

## 🎯 Descripción General

Se ha implementado una funcionalidad completa para registrar y gestionar sesiones asociadas a atenciones médicas, con un límite de **1 a 15 sesiones** por atención. Esta funcionalidad permite a los profesionales de la salud llevar un control detallado del progreso de sus pacientes.

## ✅ Funcionalidades Implementadas

### 🔧 Backend (Flask)

#### Endpoints API:
- `POST /api/guardar-sesion` - Crear nueva sesión
- `GET /api/get-sesiones/<atencion_id>` - Obtener sesiones de una atención
- `GET /api/get-sesion/<sesion_id>` - Obtener sesión específica
- `DELETE /api/eliminar-sesion/<sesion_id>` - Eliminar sesión

#### Funciones Auxiliares:
- `get_sesiones_atencion()` - Obtener todas las sesiones de una atención
- `get_sesion_by_id()` - Obtener sesión por ID
- `guardar_sesion_sheets()` - Guardar en Google Sheets
- `eliminar_sesion_sheets()` - Eliminar de Google Sheets
- `get_sheet_id()` - Obtener ID de hoja de Google Sheets

### 🎨 Frontend (JavaScript)

#### Funciones JavaScript:
- `registrarSesion()` - Abrir modal para nueva sesión
- `verificarLimiteSesiones()` - Verificar límite de 15 sesiones
- `guardarSesion()` - Guardar sesión en backend
- `verSesionesAtencion()` - Mostrar sesiones de una atención
- `mostrarModalSesiones()` - Modal con lista de sesiones
- `verDetalleSesion()` - Ver detalle de sesión específica
- `eliminarSesion()` - Eliminar sesión
- `getProgresoColor()` - Colores para badges de progreso
- `getEstadoColor()` - Colores para badges de estado

### 🎨 Interfaz de Usuario

#### Modal de Registro de Sesión:
- **Campos requeridos:**
  - Fecha y hora de sesión
  - Duración (15-180 minutos)
  - Tipo de sesión (evaluación, tratamiento, seguimiento, etc.)
  - Objetivos de la sesión
  - Actividades realizadas
  - Progreso del paciente
  - Estado de la sesión

- **Campos opcionales:**
  - Observaciones
  - Recomendaciones
  - Plan para próxima sesión

#### Modal de Lista de Sesiones:
- Tabla con todas las sesiones de la atención
- Contador de sesiones (X/15)
- Botones de acción (Ver, Editar, Eliminar)
- Badges de colores para progreso y estado

#### Modal de Detalle de Sesión:
- Información completa de la sesión
- Formato organizado por secciones
- Botón para editar sesión

## 📊 Estructura de Datos

### Sesión en Google Sheets:
```javascript
{
  id: "uuid-unico",
  atencion_id: "id-atencion",
  fecha_sesion: "2025-01-31T14:30",
  duracion: 60,
  tipo_sesion: "evaluacion",
  objetivos: "Evaluar progreso...",
  actividades: "Evaluación física...",
  observaciones: "Paciente muestra mejoría...",
  progreso: "bueno",
  estado: "completada",
  recomendaciones: "Continuar ejercicios...",
  proxima_sesion: "Seguimiento en 2 semanas",
  fecha_creacion: "2025-01-31T14:30:00",
  profesional_id: "id-profesional"
}
```

### Tipos de Sesión:
- `evaluacion` - Evaluación inicial o de seguimiento
- `tratamiento` - Sesión de tratamiento
- `seguimiento` - Control de progreso
- `reeducacion` - Reeducación funcional
- `terapia` - Terapia específica
- `control` - Control rutinario

### Niveles de Progreso:
- `excelente` - Progreso excepcional
- `muy_bueno` - Progreso muy satisfactorio
- `bueno` - Progreso satisfactorio
- `regular` - Progreso moderado
- `necesita_mejora` - Requiere más trabajo

### Estados de Sesión:
- `completada` - Sesión finalizada
- `pendiente` - Sesión programada
- `cancelada` - Sesión cancelada
- `reprogramada` - Sesión reprogramada

## 🔒 Validaciones y Límites

### Límite de Sesiones:
- **Mínimo:** 1 sesión por atención
- **Máximo:** 15 sesiones por atención
- **Validación:** Se verifica antes de crear nueva sesión
- **Feedback:** Mensaje informativo con contador actual

### Validaciones de Datos:
- **Campos requeridos:** Todos los campos obligatorios deben estar completos
- **Duración:** Entre 15 y 180 minutos
- **Fecha:** Formato ISO válido
- **Tipo de sesión:** Debe ser uno de los valores permitidos
- **Progreso:** Debe ser uno de los niveles definidos
- **Estado:** Debe ser uno de los estados permitidos

## 🎨 Diseño y UX

### Colores de Badges:
- **Progreso:**
  - Excelente: Verde (`success`)
  - Muy Bueno: Azul claro (`info`)
  - Bueno: Azul (`primary`)
  - Regular: Amarillo (`warning`)
  - Necesita Mejora: Rojo (`danger`)

- **Estado:**
  - Completada: Verde (`success`)
  - Pendiente: Amarillo (`warning`)
  - Cancelada: Rojo (`danger`)
  - Reprogramada: Azul claro (`info`)

### Animaciones y Transiciones:
- Modal con animación suave de entrada/salida
- Indicadores de carga durante operaciones
- Feedback visual inmediato para acciones
- Transiciones suaves entre estados

## 🔧 Integración con Google Sheets

### Hoja "Sesiones":
- **Columnas:** A-N (14 columnas)
- **Estructura:**
  - A: ID de sesión
  - B: ID de atención
  - C: Fecha y hora de sesión
  - D: Duración (minutos)
  - E: Tipo de sesión
  - F: Objetivos
  - G: Actividades
  - H: Observaciones
  - I: Progreso
  - J: Estado
  - K: Recomendaciones
  - L: Próxima sesión
  - M: Fecha de creación
  - N: ID de profesional

### Operaciones:
- **Crear:** Insertar nueva fila
- **Leer:** Obtener todas las filas de una atención
- **Actualizar:** Modificar fila existente
- **Eliminar:** Eliminar fila específica

## 🧪 Pruebas y Validación

### Script de Pruebas (`test_sesiones.py`):
- **Prueba funcionalidad básica:** Crear, leer, eliminar sesiones
- **Prueba límite de sesiones:** Verificar límite de 15 sesiones
- **Validación de datos:** Verificar campos requeridos
- **Integración con API:** Probar todos los endpoints

### Casos de Prueba:
1. **Crear sesión exitosa**
2. **Verificar límite de sesiones**
3. **Consultar sesiones de atención**
4. **Ver detalle de sesión**
5. **Eliminar sesión**
6. **Validar campos requeridos**
7. **Probar límite máximo (15 sesiones)**

## 📱 Interfaz de Usuario

### Botón "Registrar Sesión":
- Ubicado en el historial de atenciones
- Icono: `fas fa-clipboard-list`
- Color: Verde (`btn-success`)
- Tooltip: "Registrar Sesión"

### Modal de Registro:
- **Tamaño:** Modal grande (`modal-lg`)
- **Campos organizados:** En filas de 2 columnas
- **Validación:** Campos requeridos marcados
- **Fecha automática:** Se establece la fecha/hora actual
- **Duración predeterminada:** 60 minutos

### Modal de Lista de Sesiones:
- **Tamaño:** Modal extra grande (`modal-xl`)
- **Tabla responsive:** Con scroll horizontal
- **Contador:** Badge con número de sesiones
- **Botón agregar:** Para nueva sesión desde la lista

## 🔄 Flujo de Trabajo

### 1. Registrar Nueva Sesión:
1. Usuario hace clic en "Registrar Sesión"
2. Se abre modal con formulario
3. Se verifica límite de sesiones
4. Usuario completa formulario
5. Se valida información
6. Se guarda en Google Sheets
7. Se actualiza historial de atenciones
8. Se muestra confirmación

### 2. Ver Sesiones de Atención:
1. Usuario hace clic en "Ver Sesiones"
2. Se cargan sesiones desde API
3. Se muestra modal con lista
4. Se ordenan por fecha (más reciente primero)
5. Se muestran badges de progreso y estado

### 3. Ver Detalle de Sesión:
1. Usuario hace clic en "Ver Detalle"
2. Se carga información de la sesión
3. Se muestra modal con información completa
4. Se organiza por secciones
5. Se incluye botón para editar

### 4. Eliminar Sesión:
1. Usuario hace clic en "Eliminar"
2. Se muestra confirmación
3. Se elimina de Google Sheets
4. Se actualiza lista de sesiones
5. Se muestra confirmación

## 🚀 Instalación y Configuración

### Requisitos:
- Flask con Google Sheets API configurado
- Hoja "Sesiones" creada en Google Sheets
- Credenciales de Google Service Account

### Configuración:
1. **Crear hoja "Sesiones"** en Google Sheets
2. **Configurar encabezados** en las columnas A-N
3. **Verificar permisos** de Service Account
4. **Probar endpoints** con script de pruebas

### Archivos Modificados:
- `templates/professional.html` - Agregado botón y modal
- `static/js/professional.js` - Funciones JavaScript
- `app.py` - Endpoints y funciones auxiliares
- `sesiones_manager.py` - Módulo de gestión (opcional)

## 📈 Métricas y Estadísticas

### Datos Recopilados:
- **Número de sesiones** por atención
- **Tipos de sesión** más comunes
- **Duración promedio** de sesiones
- **Progreso del paciente** por sesión
- **Frecuencia de sesiones** por profesional

### Reportes Posibles:
- Sesiones por período
- Progreso promedio por paciente
- Tipos de sesión más efectivos
- Duración promedio por tipo de sesión

## 🔮 Mejoras Futuras

### Funcionalidades Adicionales:
- **Plantillas de sesión** predefinidas
- **Fotos/videos** de la sesión
- **Firma digital** del profesional
- **Exportar sesiones** a PDF
- **Calendario de sesiones** integrado
- **Recordatorios** automáticos
- **Notas de voz** durante la sesión

### Optimizaciones:
- **Caché** de sesiones frecuentes
- **Búsqueda avanzada** en sesiones
- **Filtros** por tipo, fecha, progreso
- **Estadísticas** en tiempo real
- **Dashboard** de sesiones

## ✅ Estado Actual

### ✅ Implementado:
- [x] Registro de sesiones (1-15 por atención)
- [x] Verificación de límite de sesiones
- [x] Consulta de sesiones por atención
- [x] Detalle de sesión individual
- [x] Eliminación de sesiones
- [x] Validación de datos requeridos
- [x] Integración con Google Sheets
- [x] Interfaz de usuario completa
- [x] Script de pruebas
- [x] Documentación completa

### 🔄 En Desarrollo:
- [ ] Edición de sesiones existentes
- [ ] Plantillas de sesión
- [ ] Exportación a PDF
- [ ] Estadísticas avanzadas

## 📞 Soporte

Para cualquier pregunta o problema con la funcionalidad de sesiones:

1. **Revisar logs** de la aplicación
2. **Ejecutar script de pruebas** (`test_sesiones.py`)
3. **Verificar configuración** de Google Sheets
4. **Comprobar permisos** de Service Account

---

**Desarrollado para MedConnect**  
**Versión:** 1.0  
**Fecha:** Enero 2025  
**Autor:** Sistema de Gestión Médica 