# Sección de Reportes - Perfil Profesional

## Descripción

Se ha agregado una nueva sección de **Reportes y Estadísticas** en el perfil del profesional que permite generar y visualizar diferentes tipos de reportes sobre su actividad médica.

## Características Implementadas

### 1. Interfaz de Usuario
- **Filtros de Reporte**: Permite seleccionar período (7, 30, 90, 365 días) y tipo de reporte
- **Botones de Acción Rápida**: Semanal, Mensual, Anual
- **Visualización de Estadísticas**: Tarjetas con métricas clave
- **Gráficos de Tendencia**: Gráficos lineales usando Chart.js
- **Tabla de Datos**: Vista detallada de los datos del reporte
- **Exportación**: Botones para exportar en PDF, Excel y CSV

### 2. Tipos de Reportes Disponibles

#### 📊 Atenciones
- Fecha de la atención
- Nombre del paciente
- Tipo de atención
- Estado de la atención
- Duración

#### 👥 Pacientes
- Nombre completo
- Edad
- Género
- Última consulta
- Total de atenciones

#### 💰 Ingresos (Simulado)
- Fecha del ingreso
- Concepto
- Monto
- Estado del pago

#### 📈 Productividad (Simulado)
- Fecha
- Número de atenciones
- Horas trabajadas
- Eficiencia
- Calificación

### 3. Funcionalidades de Exportación

#### PDF
- Genera reportes en formato PDF usando ReportLab
- Incluye estadísticas y datos tabulares
- Descarga automática con nombre personalizado

#### Excel
- Crea archivos Excel con múltiples hojas
- Hoja "Datos" con información detallada
- Hoja "Estadísticas" con métricas resumidas

#### CSV
- Exporta datos en formato CSV
- Compatible con Excel y otras herramientas

## Endpoints del Backend

### Generar Reporte
```
POST /api/professional/reports
Content-Type: application/json

{
    "periodo": 30,
    "tipo": "atenciones"
}
```

### Exportar Reporte
```
POST /api/professional/reports/export
Content-Type: application/json

{
    "periodo": 30,
    "tipo": "atenciones",
    "formato": "pdf"
}
```

## Estructura de Datos

### Respuesta de Reporte
```json
{
    "estadisticas": {
        "total": 15,
        "promedio": 2.1,
        "maximo": 8,
        "crecimiento": 12,
        "tendencia": [3, 5, 2, 7, 4, 6, 8]
    },
    "datos": [
        {
            "fecha": "2025-07-01T10:30",
            "paciente": "Juan Pérez",
            "tipo": "Consulta General",
            "estado": "Completada",
            "duracion": "30 min"
        }
    ]
}
```

## Funciones JavaScript Implementadas

### `generarReporte(tipo)`
Genera reportes predefinidos (semanal, mensual, anual)

### `generarReportePersonalizado(periodo, tipo)`
Genera reportes personalizados con filtros específicos

### `mostrarEstadisticas(estadisticas, tipo)`
Muestra las estadísticas en tarjetas y gráficos

### `mostrarTablaDatos(datos, tipo)`
Renderiza la tabla de datos según el tipo de reporte

### `exportarReporte(formato)`
Exporta el reporte en el formato especificado

## Dependencias Agregadas

### Frontend
- **Chart.js**: Para gráficos de tendencia
- **Bootstrap**: Para componentes de UI

### Backend
- **pandas**: Para manipulación de datos
- **openpyxl**: Para generación de Excel
- **reportlab**: Para generación de PDF

## Instrucciones de Uso

### Para el Profesional

1. **Acceder a Reportes**:
   - Ir al perfil profesional
   - Bajar hasta la sección "Reportes y Estadísticas"

2. **Generar Reporte Rápido**:
   - Hacer clic en "Semanal", "Mensual" o "Anual"
   - El reporte se generará automáticamente

3. **Generar Reporte Personalizado**:
   - Seleccionar período en el filtro
   - Elegir tipo de reporte
   - Hacer clic en "Generar Reporte"

4. **Exportar Reporte**:
   - Una vez generado el reporte
   - Hacer clic en PDF, Excel o CSV
   - El archivo se descargará automáticamente

### Para el Desarrollador

1. **Agregar Nuevos Tipos de Reporte**:
   - Modificar `obtenerHeadersTabla()` en JavaScript
   - Agregar función `obtener_datos_*()` en Python
   - Actualizar `generate_professional_reports()`

2. **Personalizar Gráficos**:
   - Modificar `crearGraficoTendencia()` en JavaScript
   - Cambiar colores, tipos de gráfico, etc.

3. **Agregar Nuevos Formatos de Exportación**:
   - Crear función `generar_*_reporte()` en Python
   - Actualizar `export_professional_report()`

## Consideraciones Técnicas

### Rate Limiting
- Los reportes usan el sistema de cache de SheetsManager
- Se implementan reintentos automáticos
- Se respetan los límites de Google Sheets API

### Rendimiento
- Los datos se cargan de forma asíncrona
- Se muestran spinners de carga
- Los gráficos se renderizan solo cuando hay datos

### Seguridad
- Todos los endpoints requieren autenticación
- Los datos se filtran por profesional_id
- No se exponen datos de otros profesionales

## Próximas Mejoras

1. **Reportes Avanzados**:
   - Comparación entre períodos
   - Análisis de tendencias
   - Predicciones basadas en datos históricos

2. **Visualizaciones Mejoradas**:
   - Gráficos de barras para comparaciones
   - Gráficos de pastel para distribuciones
   - Mapas de calor para patrones temporales

3. **Integración con Calendario**:
   - Reportes basados en eventos del calendario
   - Análisis de disponibilidad
   - Métricas de ocupación

4. **Notificaciones Automáticas**:
   - Reportes semanales automáticos
   - Alertas de métricas importantes
   - Resúmenes por email

## Solución de Problemas

### Error: "No se pueden cargar los datos"
- Verificar conexión con Google Sheets
- Revisar logs del servidor
- Comprobar permisos del profesional

### Error: "No se puede exportar"
- Verificar que las dependencias estén instaladas
- Comprobar espacio en disco
- Revisar permisos de escritura

### Gráficos no se muestran
- Verificar que Chart.js esté cargado
- Comprobar que hay datos en `tendencia`
- Revisar consola del navegador

### Reportes vacíos
- Verificar que el profesional tenga datos
- Comprobar el rango de fechas
- Revisar filtros aplicados 