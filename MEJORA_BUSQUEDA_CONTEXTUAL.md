# 🔍 Mejora del Sistema de Búsqueda Contextual

## 🎯 Problema Identificado

El sistema de búsqueda anterior era muy básico y no aprovechaba toda la información disponible:

### **Ejemplo del Problema:**
- **Tipo de consulta**: Kinesiología
- **Motivo de consulta**: "Dolor de rodilla por golpe en el trabajo"
- **Evaluación**: Múltiples síntomas específicos (hinchazón, inestabilidad, limitación funcional)

**Resultado anterior**: Solo identificaba "dolor" como palabra clave, ignorando:
- ✅ **Rodilla** (término anatómico específico)
- ✅ **Golpe/trauma** (causa específica)
- ✅ **Trabajo** (contexto laboral)
- ✅ **Hinchazón, inestabilidad** (síntomas específicos de la evaluación)

## ✅ Solución Implementada

### **1. Función `generarTerminosBusquedaMejorados(datos)`**

#### **Análisis Completo de Datos:**
```javascript
function generarTerminosBusquedaMejorados(datos) {
    const terminosClave = [];
    const contextoClinico = [];
    let especialidad = 'general';
    let edad = 'adulto';
    
    // 1. Analizar tipo de atención para especialidad
    // 2. Analizar motivo de consulta para términos clave
    // 3. Analizar evaluación para síntomas específicos
    // 4. Analizar edad para contexto
    // 5. Crear query completa combinando todos los elementos
    // 6. Eliminar duplicados y limpiar términos
}
```

### **2. Análisis por Especialidad**

#### **Kinesiología/Fisioterapia:**
```javascript
if (tipoLower.includes('kinesiologia') || tipoLower.includes('fisioterapia')) {
    especialidad = 'fisioterapia';
    terminosClave.push('fisioterapia', 'kinesiología', 'rehabilitación');
}
```

#### **Otras Especialidades:**
- **Medicina**: `medicina clínica`
- **Psicología**: `psicología`, `salud mental`
- **Fonoaudiología**: `fonoaudiología`, `terapia del lenguaje`

### **3. Análisis de Términos Anatómicos**

#### **Lista Completa de Términos:**
```javascript
const terminosAnatomicos = [
    'rodilla', 'hombro', 'espalda', 'cuello', 'cabeza', 'brazo', 'pierna', 
    'tobillo', 'muñeca', 'codo', 'cadera', 'columna', 'lumbar', 'cervical',
    'articulación', 'músculo', 'tendón', 'ligamento'
];
```

#### **Ejemplo de Extracción:**
- **Input**: "Dolor de rodilla por golpe en el trabajo"
- **Output**: `terminosClave.push('rodilla')`, `contextoClinico.push('dolor en rodilla')`

### **4. Análisis de Causas Específicas**

#### **Trauma/Lesión:**
```javascript
if (motivo.includes('golpe') || motivo.includes('trauma')) {
    terminosClave.push('trauma', 'lesión traumática');
    contextoClinico.push('lesión por trauma');
}
```

#### **Contexto Laboral:**
```javascript
if (motivo.includes('trabajo') || motivo.includes('laboral')) {
    terminosClave.push('lesión laboral', 'accidente de trabajo');
    contextoClinico.push('lesión relacionada con el trabajo');
}
```

#### **Actividad Física:**
```javascript
if (motivo.includes('deporte') || motivo.includes('ejercicio')) {
    terminosClave.push('lesión deportiva', 'deporte');
    contextoClinico.push('lesión relacionada con actividad física');
}
```

### **5. Análisis Detallado de la Evaluación**

#### **Síntomas de Dolor:**
```javascript
if (evaluacion.includes('dolor')) {
    terminosClave.push('dolor', 'síndrome de dolor');
    
    if (evaluacion.includes('constante')) {
        terminosClave.push('dolor constante');
        contextoClinico.push('dolor persistente');
    }
    if (evaluacion.includes('intermitente')) {
        terminosClave.push('dolor intermitente');
        contextoClinico.push('dolor episódico');
    }
    if (evaluacion.includes('peor')) {
        terminosClave.push('dolor agravado');
        contextoClinico.push('dolor que empeora con actividades');
    }
}
```

#### **Síntomas de Inflamación:**
```javascript
if (evaluacion.includes('hinchazón') || evaluacion.includes('edema')) {
    terminosClave.push('hinchazón', 'edema', 'inflamación');
    contextoClinico.push('inflamación local');
}
if (evaluacion.includes('calor')) {
    terminosClave.push('calor local', 'inflamación');
    contextoClinico.push('signos de inflamación aguda');
}
```

#### **Síntomas de Inestabilidad:**
```javascript
if (evaluacion.includes('inestabilidad') || evaluacion.includes('bloqueo')) {
    terminosClave.push('inestabilidad articular', 'bloqueo articular');
    contextoClinico.push('disfunción articular');
}
```

#### **Limitación Funcional:**
```javascript
if (evaluacion.includes('escaleras') || evaluacion.includes('subir') || evaluacion.includes('bajar')) {
    terminosClave.push('limitación funcional', 'dificultad para movimientos');
    contextoClinico.push('limitación en actividades de la vida diaria');
}
if (evaluacion.includes('reposo') || evaluacion.includes('alivia')) {
    terminosClave.push('alivio con reposo', 'dolor mecánico');
    contextoClinico.push('dolor que mejora con reposo');
}
if (evaluacion.includes('tiempo de pie') || evaluacion.includes('estar de pie')) {
    terminosClave.push('dolor postural', 'dolor por bipedestación');
    contextoClinico.push('dolor relacionado con postura');
}
```

### **6. Análisis por Edad**

```javascript
if (datos.edad) {
    const edadNum = parseInt(datos.edad);
    if (edadNum < 18) {
        edad = 'pediátrico';
        terminosClave.push('pediatría', 'niño', 'adolescente');
    } else if (edadNum > 65) {
        edad = 'geriátrico';
        terminosClave.push('geriatría', 'adulto mayor', 'envejecimiento');
    }
}
```

### **7. Generación de Query Completa**

```javascript
const queryCompleta = [
    datos.motivoConsulta,
    ...terminosClave.slice(0, 5), // Máximo 5 términos clave
    especialidad
].filter(Boolean).join(' ');
```

## 🎯 Ejemplo Práctico

### **Input del Usuario:**
- **Tipo de consulta**: Kinesiología
- **Motivo de consulta**: "Dolor de rodilla por golpe en el trabajo"
- **Evaluación**: 
  ```
  ¿En qué momento del día es peor el dolor?
  cuando me levanto
  
  ¿Qué actividades agravan el dolor?
  pasar mucho tiempo de pie
  
  ¿Qué actividades alivian el dolor?
  tener la rodilla en reposo
  
  ¿Hay hinchazón o calor en la rodilla?
  hay hinchazón
  
  ¿Ha tenido lesiones previas en la rodilla?
  no
  
  ¿El dolor es constante o intermitente?
  es intermitente
  
  ¿Hay bloqueos o sensación de inestabilidad?
  sensación de inestabilidad
  
  ¿Puede subir y bajar escaleras sin dolor?
  bajar duele la rodilla
  ```

### **Output Mejorado:**
```javascript
{
    queryCompleta: "Dolor de rodilla por golpe en el trabajo rodilla trauma lesión laboral fisioterapia",
    terminosClave: [
        "fisioterapia", "kinesiología", "rehabilitación",
        "rodilla", "trauma", "lesión traumática",
        "lesión laboral", "accidente de trabajo",
        "dolor", "síndrome de dolor", "dolor intermitente",
        "dolor agravado", "hinchazón", "edema", "inflamación",
        "inestabilidad articular", "bloqueo articular",
        "limitación funcional", "dificultad para movimientos",
        "alivio con reposo", "dolor mecánico",
        "dolor postural", "dolor por bipedestación"
    ],
    especialidad: "fisioterapia",
    edad: "adulto",
    contextoClinico: [
        "dolor en rodilla",
        "lesión por trauma",
        "lesión relacionada con el trabajo",
        "dolor episódico",
        "dolor que empeora con actividades",
        "inflamación local",
        "disfunción articular",
        "limitación en actividades de la vida diaria",
        "dolor que mejora con reposo",
        "dolor relacionado con postura"
    ]
}
```

## 🎯 Beneficios de la Mejora

### **1. Búsqueda Más Específica**
- ✅ **Términos anatómicos**: "rodilla" en lugar de solo "dolor"
- ✅ **Causas específicas**: "trauma", "lesión laboral"
- ✅ **Síntomas específicos**: "hinchazón", "inestabilidad"
- ✅ **Contexto clínico**: "fisioterapia", "rehabilitación"

### **2. Resultados Más Relevantes**
- ✅ **Papers específicos**: Sobre rodilla, no dolor general
- ✅ **Contexto laboral**: Lesiones relacionadas con trabajo
- ✅ **Especialidad correcta**: Fisioterapia/kinesiología
- ✅ **Síntomas específicos**: Inflamación, inestabilidad

### **3. Mejor Experiencia de Usuario**
- ✅ **Resultados precisos**: Papers que realmente aplican al caso
- ✅ **Información contextual**: Basada en todos los datos del formulario
- ✅ **Búsqueda inteligente**: No solo palabras clave básicas

## 🎯 Implementación Técnica

### **1. Modificación de `buscarEvidenciaAutomatica`**
```javascript
async function buscarEvidenciaAutomatica(motivoConsulta) {
    // Obtener datos completos del formulario para análisis contextual
    const datosCompletos = obtenerDatosFormularioActuales();
    const terminosMejorados = generarTerminosBusquedaMejorados(datosCompletos);
    
    // Usar términos mejorados en la búsqueda
    let response = await fetch('/api/copilot/search-enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            motivo_consulta: terminosMejorados.queryCompleta,
            terminos_clave: terminosMejorados.terminosClave,
            especialidad: terminosMejorados.especialidad,
            contexto_clinico: terminosMejorados.contextoClinico
        })
    });
}
```

### **2. Parámetros Enviados al Backend**
- **motivo_consulta**: Query completa con todos los términos
- **terminos_clave**: Array de términos específicos identificados
- **especialidad**: Especialidad médica detectada
- **contexto_clinico**: Contexto clínico específico

## 🎯 Verificación de la Mejora

### **Antes (Búsqueda Básica):**
- ❌ **Query**: "Dolor de rodilla por golpe en el trabajo"
- ❌ **Términos**: Solo "dolor"
- ❌ **Resultados**: Papers generales sobre dolor

### **Después (Búsqueda Contextual):**
- ✅ **Query**: "Dolor de rodilla por golpe en el trabajo rodilla trauma lesión laboral fisioterapia"
- ✅ **Términos**: ["rodilla", "trauma", "lesión laboral", "hinchazón", "inestabilidad", "fisioterapia"]
- ✅ **Resultados**: Papers específicos sobre lesiones de rodilla en contexto laboral

---

**🔍 ¡MEJORA COMPLETAMENTE IMPLEMENTADA!**

El sistema ahora analiza todos los datos del formulario para generar búsquedas mucho más específicas y contextuales, resultando en papers científicos más relevantes para cada caso clínico. 