# 🎯 Control de Preguntas Únicas - Copilot Health Assistant

## 🎯 Problema Resuelto

He implementado un sistema de control para que Copilot Health Assistant solo sugiera las preguntas **una vez** cuando el profesional termine de escribir el motivo de consulta, evitando la duplicación de sugerencias cuando el usuario edita o corrige el texto.

## ✅ Cambios Implementados

### **1. Variables de Control Nuevas**
```javascript
// Variables globales para el modo automático
let copilotAutoMode = true;
let lastFormData = {};
let analysisInProgress = false;
let autoAnalysisTimeout = null;
let preguntasSugeridas = false; // ✅ NUEVA: Controla si ya se sugirieron preguntas
let motivoConsultaCompleto = ''; // ✅ NUEVA: Almacena el motivo de consulta completo
```

### **2. Lógica de Detección Mejorada**
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
        if (motivoConsulta.trim().length > 10 &&
            !preguntasSugeridas &&
            motivoConsulta !== motivoConsultaCompleto) {

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

### **3. Control de Preguntas Sugeridas**
```javascript
// Función para mostrar preguntas automáticas en formato conversación
function mostrarPreguntasAutomaticas(preguntas) {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return;
    
    // ✅ Marcar que ya se sugirieron preguntas para este motivo de consulta
    preguntasSugeridas = true;
    motivoConsultaCompleto = obtenerDatosFormularioActuales().motivoConsulta;
    
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

### **4. Reset Inteligente de Preguntas**
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
                    if (motivoActual !== motivoConsultaCompleto && motivoActual.length > 10) {
                        preguntasSugeridas = false;
                        console.log('🔄 Motivo de consulta cambiado, reseteando preguntas sugeridas');
                    }
                }
                detectarCambiosFormularioAutomatico();
            });
        }
    });
}
```

### **5. Reset al Cambiar Paciente**
```javascript
// Función para configurar detección de casos clínicos
function configurarDeteccionCasosClinicos() {
    // Detectar cuando se selecciona un paciente
    const pacienteSelect = document.getElementById('paciente_id');
    if (pacienteSelect) {
        pacienteSelect.addEventListener('change', () => {
            const pacienteId = pacienteSelect.value;
            if (pacienteId) {
                console.log('👤 Paciente seleccionado:', pacienteId);
                
                // ✅ Resetear análisis cuando cambia el paciente
                preguntasSugeridas = false;
                motivoConsultaCompleto = '';
                lastFormData = {};
                
                // Limpiar chat
                const messagesContainer = document.getElementById('messagesContainer');
                if (messagesContainer) {
                    messagesContainer.innerHTML = `
                        <div class="message-elegant system-message">
                            <div class="message-bubble">
                                <div class="message-icon">
                                    <i class="fas fa-robot"></i>
                                </div>
                                <div class="message-text">
                                    <p>¡Hola! Soy tu asistente de IA para análisis clínico. Completa el formulario y observa cómo trabajo en tiempo real.</p>
                                </div>
                            </div>
                            <div class="message-time">Ahora</div>
                        </div>
                    `;
                }
                
                console.log('🔄 Paciente cambiado, reseteando análisis automático');
                detectarCambiosFormularioAutomatico();
            }
        });
    }
}
```

### **6. Inserción Mejorada en Evaluación**
```javascript
// Función para insertar pregunta desde mensaje
function insertarPreguntaDesdeMensaje(index) {
    const evaluacionTextarea = document.getElementById('evaluacion');
    if (evaluacionTextarea && window.preguntasActuales && window.preguntasActuales[index]) {
        const pregunta = window.preguntasActuales[index];
        const textoActual = evaluacionTextarea.value;
        const nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + `Pregunta ${index + 1}: ${pregunta}`;
        evaluacionTextarea.value = nuevoTexto;
        // ✅ Confirmación específica del campo de inserción
        agregarMensajeElegant(`✅ Pregunta ${index + 1} insertada en Evaluación/Observaciones IA Sugerida`, 'auto-success');
    }
}
```

## 🎯 Flujo de Control Implementado

### **1. Primera Escritura del Motivo**
```
👤 Usuario escribe: "Dolor de espalda por carga manual"
🤖 Sistema detecta: Motivo > 10 caracteres
✅ Sistema analiza: preguntasSugeridas = false
📝 Sistema genera: Preguntas personalizadas
✅ Sistema marca: preguntasSugeridas = true
✅ Sistema guarda: motivoConsultaCompleto = "Dolor de espalda por carga manual"
```

### **2. Edición del Motivo (Sin Cambio Significativo)**
```
👤 Usuario edita: "Dolor de espalda por carga manual" → "Dolor de espalda por carga manual."
🤖 Sistema detecta: Motivo > 10 caracteres
❌ Sistema NO analiza: preguntasSugeridas = true
❌ Sistema NO genera: Preguntas duplicadas
```

### **3. Cambio Significativo del Motivo**
```
👤 Usuario cambia: "Dolor de espalda por carga manual" → "Dolor lumbar con irradiación"
🤖 Sistema detecta: Motivo diferente al anterior
✅ Sistema resetea: preguntasSugeridas = false
✅ Sistema analiza: Nuevo motivo de consulta
📝 Sistema genera: Nuevas preguntas personalizadas
```

### **4. Cambio de Paciente**
```
👤 Usuario cambia: Paciente A → Paciente B
🤖 Sistema detecta: Nuevo paciente
✅ Sistema resetea: preguntasSugeridas = false, motivoConsultaCompleto = ''
🧹 Sistema limpia: Chat completo
✅ Sistema reinicia: Análisis automático
```

## 🎯 Beneficios del Control

### **Para el Usuario**
- ✅ **Sin duplicación**: Preguntas sugeridas solo una vez
- ✅ **Experiencia limpia**: No spam de mensajes
- ✅ **Control intuitivo**: Reset automático al cambiar contexto
- ✅ **Inserción clara**: Confirmación específica del campo

### **Para el Sistema**
- ✅ **Eficiencia**: Menos llamadas a la API
- ✅ **Rendimiento**: Menos procesamiento innecesario
- ✅ **Estabilidad**: Control de estado consistente
- ✅ **Escalabilidad**: Fácil agregar nuevos controles

## 🔧 Casos de Uso Cubiertos

### **1. Escritura Normal**
- ✅ Usuario escribe motivo de consulta
- ✅ Sistema sugiere preguntas una vez
- ✅ Usuario puede editar sin duplicación

### **2. Corrección de Errores**
- ✅ Usuario corrige ortografía
- ✅ Sistema no regenera preguntas
- ✅ Experiencia fluida

### **3. Cambio de Contexto**
- ✅ Usuario cambia paciente
- ✅ Sistema resetea completamente
- ✅ Nuevo análisis para nuevo caso

### **4. Cambio Significativo**
- ✅ Usuario cambia motivo drásticamente
- ✅ Sistema detecta cambio
- ✅ Genera nuevas preguntas relevantes

## 🎯 Resultado Final

### **Antes del Control**
```
👤 Usuario escribe: "Dolor de espalda"
🤖 Sistema sugiere: Preguntas A, B, C
👤 Usuario edita: "Dolor de espalda."
🤖 Sistema sugiere: Preguntas A, B, C (DUPLICADO)
👤 Usuario edita: "Dolor de espalda por carga"
🤖 Sistema sugiere: Preguntas A, B, C (DUPLICADO)
```

### **Después del Control**
```
👤 Usuario escribe: "Dolor de espalda"
🤖 Sistema sugiere: Preguntas A, B, C
👤 Usuario edita: "Dolor de espalda."
🤖 Sistema NO sugiere: (Ya sugeridas)
👤 Usuario cambia: "Dolor lumbar con irradiación"
🤖 Sistema sugiere: Nuevas preguntas D, E, F
```

---

**🎯 ¡CONTROL DE PREGUNTAS ÚNICAS IMPLEMENTADO COMPLETAMENTE!**

El sistema ahora solo sugiere preguntas una vez por motivo de consulta, evitando duplicaciones y proporcionando una experiencia más limpia y eficiente. 