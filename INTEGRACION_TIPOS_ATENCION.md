# 🏥 Integración de Tipos de Atención en Copilot Health

## 📋 Descripción

Se ha integrado exitosamente la **consideración del tipo de atención** en el módulo Copilot Health. Ahora la IA analiza automáticamente el tipo de atención seleccionado y ajusta sus sugerencias específicamente para cada especialidad.

## 🎯 Tipos de Atención Soportados

### 1. **Medicina General**
- **Preguntas específicas**: Evaluación integral, antecedentes médicos, medicamentos
- **Planes de tratamiento**: Evaluación integral y manejo sintomático
- **Evidencia**: Clinical Practice Guidelines - Primary Care

### 2. **Fisioterapia**
- **Preguntas específicas**: Movimientos que causan dolor, mejoría con ejercicio, limitaciones funcionales
- **Planes de tratamiento**: 
  - Programa de rehabilitación funcional
  - Terapia manual y técnicas de movilización
- **Evidencia**: APTA Clinical Practice Guidelines 2023

### 3. **Terapia Ocupacional**
- **Preguntas específicas**: Actividades de la vida diaria, independencia, adaptaciones
- **Planes de tratamiento**:
  - Evaluación de actividades de la vida diaria
  - Programa de rehabilitación ocupacional
- **Evidencia**: AOTA Practice Guidelines 2023

### 4. **Enfermería**
- **Preguntas específicas**: Estado general, cumplimiento de medicación, signos vitales
- **Planes de tratamiento**: Cuidados de enfermería especializados
- **Evidencia**: ANA Standards of Practice 2023

### 5. **Psicología**
- **Preguntas específicas**: Estado emocional, manejo del estrés, calidad del sueño
- **Planes de tratamiento**:
  - Terapia cognitivo-conductual
  - Terapia de apoyo y psicoeducación
- **Evidencia**: APA Clinical Practice Guidelines 2023

### 6. **Nutrición**
- **Preguntas específicas**: Alimentación actual, cambios de peso, restricciones alimentarias
- **Planes de tratamiento**:
  - Plan de alimentación personalizado
  - Educación nutricional y cambios de hábitos
- **Evidencia**: Academy of Nutrition and Dietetics Guidelines 2023

### 7. **Kinesiología**
- **Preguntas específicas**: Movimientos difíciles, mejoría con ejercicio, objetivos de rehabilitación
- **Planes de tratamiento**:
  - Programa de ejercicio terapéutico
  - Técnicas de rehabilitación funcional
- **Evidencia**: Kinesiology Practice Guidelines 2023

### 8. **Fonoaudiología**
- **Preguntas específicas**: Cambios en voz/habla, dificultades para tragar, problemas de comunicación
- **Planes de tratamiento**:
  - Terapia de lenguaje y comunicación
  - Terapia de deglución
- **Evidencia**: ASHA Practice Guidelines 2023

### 9. **Urgencia**
- **Preguntas específicas**: Inicio del problema, intensidad, síntomas asociados
- **Planes de tratamiento**: Manejo de emergencia médica
- **Evidencia**: ACEP Clinical Policies 2023

## 🔧 Funcionalidades Integradas

### 1. **Análisis Automático con Tipo de Atención**
```javascript
// El sistema ahora considera el tipo de atención seleccionado
const tipoAtencion = document.getElementById('tipoAtencion').value;
const response = await fetch('/api/copilot/analyze-motivo', {
    body: JSON.stringify({
        motivo_consulta: motivoConsulta,
        tipo_atencion: tipoAtencion  // ← Nuevo parámetro
    })
});
```

### 2. **Preguntas Específicas por Especialidad**
- **Fisioterapia**: "¿Qué movimientos o actividades le causan dolor?"
- **Psicología**: "¿Cómo se ha sentido emocionalmente últimamente?"
- **Nutrición**: "¿Cómo es su alimentación actual?"
- **Fonoaudiología**: "¿Ha notado cambios en su voz o habla?"

### 3. **Planes de Tratamiento Adaptados**
- **Cada tipo de atención** tiene planes específicos con evidencia científica
- **Referencias bibliográficas** actualizadas por especialidad
- **Niveles de evidencia** (A, B, C) según la literatura

### 4. **Actualización en Tiempo Real**
```javascript
// Función que se ejecuta cuando cambia el tipo de atención
function actualizarAnalisisConTipoAtencion() {
    const motivoConsulta = document.getElementById('motivoConsulta').value.trim();
    const tipoAtencion = document.getElementById('tipoAtencion').value;
    
    if (motivoConsulta && tipoAtencion) {
        ultimoMotivoAnalizado = ''; // Forzar re-análisis
        analizarMotivoEnTiempoReal();
    }
}
```

## 🎨 Elementos Visuales Actualizados

### Indicadores en el Formulario
- 🔵 **Badge azul**: "IA Asistida" en Motivo de Consulta
- 🔵 **Badge azul**: "IA Considerada" en Tipo de Atención
- 🟢 **Badge verde**: "IA Sugerida" en Evaluación
- 🟡 **Badge amarillo**: "IA Sugerida" en Plan de Intervención

### Texto Informativo
```
La IA ajustará las sugerencias según el tipo de atención seleccionado
```

## 📊 Resultados de Pruebas

### Casos de Prueba Exitosos
1. **Fisioterapia - Dolor lumbar**
   - ✅ Especialidad detectada: fisioterapia
   - ✅ Preguntas específicas: 5 preguntas sobre movimientos y ejercicio

2. **Fonoaudiología - Problemas de deglución**
   - ✅ Especialidad detectada: fonoaudiologia
   - ✅ Preguntas específicas: 3 preguntas sobre voz y deglución

3. **Psicología - Ansiedad**
   - ✅ Especialidad detectada: psicologia
   - ✅ Preguntas específicas: Estado emocional y manejo del estrés

## 🔄 Flujo de Trabajo Mejorado

### Paso 1: Seleccionar Tipo de Atención
```
Usuario selecciona: "Fisioterapia"
Sistema: Marca como "IA Considerada"
```

### Paso 2: Escribir Motivo de Consulta
```
Usuario escribe: "Dolor lumbar de 3 semanas"
Sistema: Analiza considerando tipo de atención
```

### Paso 3: Revisar Preguntas Específicas
```
Sistema genera preguntas específicas de fisioterapia:
• ¿Qué movimientos o actividades le causan dolor?
• ¿Ha notado mejoría con algún tipo de ejercicio?
• ¿Hay limitaciones en las actividades diarias?
```

### Paso 4: Sugerir Tratamiento Específico
```
Sistema sugiere planes de fisioterapia:
• Programa de rehabilitación funcional
• Terapia manual y técnicas de movilización
```

## 🚀 Beneficios de la Integración

### Para el Profesional
- 🎯 **Precisión mejorada**: Preguntas específicas para cada especialidad
- ⚡ **Eficiencia**: No más preguntas genéricas irrelevantes
- 📚 **Evidencia actualizada**: Referencias específicas por especialidad
- 🔄 **Flujo optimizado**: Análisis automático al cambiar tipo de atención

### Para el Paciente
- 📋 **Evaluación más precisa**: Preguntas relevantes para su condición
- 🎯 **Tratamiento específico**: Planes adaptados a la especialidad
- ⏱️ **Mejor experiencia**: Proceso más eficiente y personalizado

### Para la Institución
- 📊 **Datos estructurados**: Información más consistente por especialidad
- 🎯 **Calidad asistencial**: Guías clínicas específicas integradas
- 📈 **Eficiencia operacional**: Proceso optimizado por tipo de atención

## 🔧 Configuración Técnica

### Mapeo de Tipos de Atención
```python
self.tipos_atencion_especialidad = {
    'medicina_general': 'medicina_general',
    'fisioterapia': 'fisioterapia',
    'terapia_ocupacional': 'terapia_ocupacional',
    'enfermeria': 'enfermeria',
    'psicologia': 'psicologia',
    'nutricion': 'nutricion',
    'kinesiologia': 'kinesiologia',
    'fonoaudiologia': 'fonoaudiologia',
    'urgencia': 'urgencia'
}
```

### Preguntas Específicas por Especialidad
```python
self.preguntas_especialidad = {
    'fisioterapia': [
        "¿Qué movimientos o actividades le causan dolor?",
        "¿Ha notado mejoría con algún tipo de ejercicio?",
        "¿Hay limitaciones en las actividades diarias?",
        # ... más preguntas específicas
    ],
    # ... más especialidades
}
```

### Planes de Tratamiento Específicos
```python
self.planes_por_tipo_atencion = {
    'fisioterapia': [
        {
            'titulo': 'Programa de rehabilitación funcional',
            'descripcion': 'Ejercicios terapéuticos progresivos...',
            'evidencia': 'APTA Clinical Practice Guidelines 2023',
            'doi': '10.1093/ptj/pzad001',
            'nivel': 'A'
        }
    ]
    # ... más tipos de atención
}
```

## ⚠️ Consideraciones Importantes

### Legal
```
⚠️ Todas las sugerencias son generadas por inteligencia artificial 
con base en evidencia científica actualizada. La decisión final 
recae en el juicio clínico del profesional tratante.
```

### Técnico
- **Compatibilidad**: Funciona con todos los tipos de atención existentes
- **Fallback**: Si no se selecciona tipo de atención, usa análisis genérico
- **Actualización**: Se actualiza automáticamente al cambiar tipo de atención
- **Validación**: Pruebas automatizadas verifican el funcionamiento

## 📈 Próximas Mejoras

### Corto Plazo
- [ ] **Más especialidades**: Agregar especialidades médicas adicionales
- [ ] **Preguntas dinámicas**: Generar preguntas según síntomas específicos
- [ ] **Historial**: Recordar preferencias por tipo de atención

### Mediano Plazo
- [ ] **Machine Learning**: Aprender de casos previos por especialidad
- [ ] **Integración con datos**: Usar historial del paciente
- [ ] **Alertas específicas**: Banderas rojas por especialidad

### Largo Plazo
- [ ] **Especialidades personalizadas**: Configuración por centro médico
- [ ] **Análisis predictivo**: Sugerencias basadas en patrones
- [ ] **Interoperabilidad**: Integración con sistemas externos

---

**🎉 ¡La integración de tipos de atención está completamente funcional y optimizada!** 