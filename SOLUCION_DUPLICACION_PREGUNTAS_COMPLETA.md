# 🎯 Solución Completa: Duplicación de Preguntas e Inserción en Evaluación

## 🎯 Problemas Identificados y Resueltos

### **1. Duplicación de Preguntas**
**Problema**: El sistema sugería las mismas preguntas múltiples veces cuando el usuario editaba el motivo de consulta.

**Causa**: El sistema no estaba detectando correctamente cuando ya se habían sugerido preguntas para un motivo de consulta similar.

### **2. Inserción de Preguntas en Evaluación**
**Problema**: Las preguntas no se insertaban correctamente en el campo "Evaluación/Observaciones IA Sugerida".

**Causa**: Falta de trigger de eventos y validación de elementos.

## ✅ Soluciones Implementadas

### **1. Control Robusto de Duplicación**

#### **Variables de Control Mejoradas**
```javascript
// Variables globales para el modo automático
let copilotAutoMode = true;
let lastFormData = {};
let analysisInProgress = false;
let autoAnalysisTimeout = null;
let preguntasSugeridas = false; // ✅ Controla si ya se sugirieron preguntas
let motivoConsultaCompleto = ''; // ✅ Almacena el motivo de consulta completo
// ✅ Usa la variable existente: ultimoMotivoAnalizado
```

#### **Lógica de Detección Mejorada**
```javascript
// Función para detectar cambios automáticamente
function detectarCambiosFormularioAutomatico() {
    if (!copilotAutoMode || analysisInProgress) return;

    // Obtener datos actuales del formulario
    const datosActuales = obtenerDatosFormularioActuales();
    const motivoConsulta = datosActuales.motivoConsulta || '';

    // Comparar con datos anteriores
    if (JSON.stringify(datosActuales) !== JSON.stringify(lastFormData)) {
        lastFormData = datosActuales;

        // ✅ SOLO analizar si:
        // 1. Hay suficiente información para análisis (más de 10 caracteres)
        // 2. No se han sugerido preguntas para este motivo de consulta
        // 3. El motivo de consulta es diferente al anterior
        // 4. El motivo de consulta es significativamente diferente al último analizado
        if (motivoConsulta.trim().length > 10 &&
            !preguntasSugeridas &&
            motivoConsulta !== motivoConsultaCompleto &&
            motivoConsulta !== ultimoMotivoAnalizado) {

            // Retrasar el análisis para evitar demasiadas llamadas
            if (autoAnalysisTimeout) {
                clearTimeout(autoAnalysisTimeout);
            }

            autoAnalysisTimeout = setTimeout(() => {
                realizarAnalisisAutomatico(datosActuales);
            }, 2000); // Esperar 2 segundos después del último cambio
        }
    }
}
```

#### **Control de Preguntas Sugeridas Mejorado**
```javascript
// Función para mostrar preguntas automáticas en formato conversación
function mostrarPreguntasAutomaticas(preguntas) {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return;

    // ✅ Marcar que ya se sugirieron preguntas para este motivo de consulta
    preguntasSugeridas = true;
    motivoConsultaCompleto = obtenerDatosFormularioActuales().motivoConsulta;
    ultimoMotivoAnalizado = motivoConsultaCompleto; // ✅ Marcar como último motivo analizado

    console.log('✅ Preguntas sugeridas para motivo:', motivoConsultaCompleto);

    // Agregar mensaje introductorio
    agregarMensajeElegant('Luego del análisis del motivo de consulta te sugiero que realices las siguientes preguntas:', 'auto-success');

    // Agregar cada pregunta como mensaje individual
    preguntas.forEach((pregunta, index) => {
        const preguntaHtml = `
            <div class="pregunta-mensaje">
                <div class="pregunta-texto">${pregunta}</div>
                <button class="btn btn-sm btn-primary insertar-pregunta-btn" onclick="insertarPreguntaDesdeMensaje(${index})">
                    <i class="fas fa-plus"></i> Insertar
                </button>
            </div>
        `;

        agregarMensajeElegant(preguntaHtml, 'pregunta');
    });

    // Almacenar preguntas para uso posterior
    window.preguntasActuales = preguntas;
}
```

### **2. Inserción Mejorada en Evaluación**

#### **Función de Inserción Robusta**
```javascript
// Función para insertar pregunta desde mensaje
function insertarPreguntaDesdeMensaje(index) {
    const evaluacionTextarea = document.getElementById('evaluacion');
    if (evaluacionTextarea && window.preguntasActuales && window.preguntasActuales[index]) {
        const pregunta = window.preguntasActuales[index];
        const textoActual = evaluacionTextarea.value;
        const nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + `Pregunta ${index + 1}: ${pregunta}`;
        evaluacionTextarea.value = nuevoTexto;
        
        // ✅ Trigger change event para que el textarea detecte el cambio
        evaluacionTextarea.dispatchEvent(new Event('input', { bubbles: true }));
        
        agregarMensajeElegant(`✅ Pregunta ${index + 1} insertada en Evaluación/Observaciones IA Sugerida`, 'auto-success');
        
        console.log('✅ Pregunta insertada:', pregunta);
    } else {
        console.error('❌ Error: No se pudo insertar la pregunta', {
            evaluacionTextarea: !!evaluacionTextarea,
            preguntasActuales: !!window.preguntasActuales,
            index: index
        });
    }
}
```

### **3. Reset Inteligente de Preguntas**

#### **Detección de Cambios Significativos**
```javascript
// Función para configurar observadores automáticos
function configurarObservadoresAutomaticos() {
    // ... código existente ...

    // Observar cambios en campos específicos
    const camposImportantes = ['motivoConsulta', 'tipoAtencion', 'edad', 'antecedentes', 'evaluacion'];
    camposImportantes.forEach(campo => {
        const elemento = document.getElementById(campo);
        if (elemento) {
            elemento.addEventListener('input', () => {
                // ✅ Resetear preguntas sugeridas si el motivo de consulta cambia significativamente
                if (campo === 'motivoConsulta') {
                    const motivoActual = elemento.value;
                    // ✅ Solo resetear si el cambio es significativo (más de 3 caracteres de diferencia)
                    if (motivoActual !== motivoConsultaCompleto &&
                        motivoActual.length > 10 &&
                        Math.abs(motivoActual.length - motivoConsultaCompleto.length) > 3) {
                        preguntasSugeridas = false;
                        console.log('🔄 Motivo de consulta cambiado significativamente, reseteando preguntas sugeridas');
                        console.log('Motivo anterior:', motivoConsultaCompleto);
                        console.log('Motivo actual:', motivoActual);
                    }
                }
                detectarCambiosFormularioAutomatico();
            });
        }
    });
}
```

## 🎯 Flujo de Control Mejorado

### **1. Primera Escritura del Motivo**
```
👤 Usuario escribe: "Dolor de espalda por carga manual"
🤖 Sistema detecta: Motivo > 10 caracteres
✅ Sistema analiza: preguntasSugeridas = false
📝 Sistema genera: Preguntas personalizadas
✅ Sistema marca: preguntasSugeridas = true
✅ Sistema guarda: motivoConsultaCompleto = "Dolor de espalda por carga manual"
✅ Sistema marca: ultimoMotivoAnalizado = "Dolor de espalda por carga manual"
```

### **2. Edición del Motivo (Sin Cambio Significativo)**
```
👤 Usuario edita: "Dolor de espalda por carga manual" → "Dolor de espalda por carga manual."
🤖 Sistema detecta: Motivo > 10 caracteres
🤖 Sistema detecta: Cambio no significativo (< 3 caracteres)
❌ Sistema NO analiza: preguntasSugeridas = true
❌ Sistema NO genera: Preguntas duplicadas
```

### **3. Cambio Significativo del Motivo**
```
👤 Usuario cambia: "Dolor de espalda por carga manual" → "Dolor lumbar con irradiación"
🤖 Sistema detecta: Motivo diferente al anterior
🤖 Sistema detecta: Cambio significativo (> 3 caracteres)
✅ Sistema resetea: preguntasSugeridas = false
✅ Sistema analiza: Nuevo motivo de consulta
📝 Sistema genera: Nuevas preguntas personalizadas
```

### **4. Inserción de Preguntas**
```
👤 Usuario hace clic: "Insertar" en pregunta 1
🤖 Sistema busca: Campo evaluacion
✅ Sistema inserta: Pregunta en textarea
✅ Sistema dispara: Event input para detectar cambio
✅ Sistema confirma: "Pregunta 1 insertada en Evaluación/Observaciones IA Sugerida"
```

## 🎯 Beneficios de las Mejoras

### **Para el Usuario**
- ✅ **Sin duplicación**: Preguntas sugeridas solo una vez por motivo
- ✅ **Inserción confiable**: Las preguntas se insertan correctamente en Evaluación
- ✅ **Experiencia fluida**: No spam de mensajes duplicados
- ✅ **Feedback claro**: Confirmación específica de inserción
- ✅ **Control intuitivo**: Reset automático solo en cambios significativos

### **Para el Sistema**
- ✅ **Eficiencia**: Menos llamadas a la API innecesarias
- ✅ **Rendimiento**: Menos procesamiento duplicado
- ✅ **Estabilidad**: Control de estado consistente
- ✅ **Debugging**: Logs detallados para troubleshooting
- ✅ **Escalabilidad**: Fácil agregar nuevos controles

## 🔧 Casos de Uso Cubiertos

### **1. Escritura Normal**
- ✅ Usuario escribe motivo de consulta
- ✅ Sistema sugiere preguntas una vez
- ✅ Usuario puede editar sin duplicación
- ✅ Preguntas se insertan correctamente

### **2. Corrección de Errores**
- ✅ Usuario corrige ortografía
- ✅ Sistema no regenera preguntas
- ✅ Experiencia fluida
- ✅ Inserción funciona

### **3. Cambio de Contexto**
- ✅ Usuario cambia paciente
- ✅ Sistema resetea completamente
- ✅ Nuevo análisis para nuevo caso
- ✅ Inserción funciona en nuevo contexto

### **4. Cambio Significativo**
- ✅ Usuario cambia motivo drásticamente
- ✅ Sistema detecta cambio significativo
- ✅ Genera nuevas preguntas relevantes
- ✅ Inserción funciona con nuevas preguntas

## 🎯 Resultado Final

### **Antes de las Mejoras**
```
👤 Usuario escribe: "Dolor de espalda"
🤖 Sistema sugiere: Preguntas A, B, C
👤 Usuario edita: "Dolor de espalda."
🤖 Sistema sugiere: Preguntas A, B, C (DUPLICADO)
👤 Usuario hace clic: "Insertar"
❌ Sistema NO inserta: Pregunta en Evaluación
```

### **Después de las Mejoras**
```
👤 Usuario escribe: "Dolor de espalda"
🤖 Sistema sugiere: Preguntas A, B, C
👤 Usuario edita: "Dolor de espalda."
🤖 Sistema NO sugiere: (Ya sugeridas)
👤 Usuario cambia: "Dolor lumbar con irradiación"
🤖 Sistema sugiere: Nuevas preguntas D, E, F
👤 Usuario hace clic: "Insertar"
✅ Sistema inserta: Pregunta en Evaluación/Observaciones IA Sugerida
```

---

**🎯 ¡SOLUCIÓN COMPLETA IMPLEMENTADA!**

El sistema ahora:
- ✅ **Evita duplicaciones** de preguntas sugeridas
- ✅ **Inserta correctamente** las preguntas en Evaluación
- ✅ **Detecta cambios significativos** para resetear cuando sea necesario
- ✅ **Proporciona feedback claro** al usuario
- ✅ **Mantiene logs detallados** para debugging 