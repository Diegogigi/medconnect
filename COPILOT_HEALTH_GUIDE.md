# 🤖 Copilot Health - Guía de Uso

## 📋 Descripción General

**Copilot Health** es el módulo de IA clínica asistiva integrado en MedConnect que proporciona asistencia inteligente a profesionales de la salud durante el proceso clínico. Funciona como un copiloto que guía en cada paso del proceso clínico.

## 🎯 Funcionalidades Principales

### 1. Análisis del Motivo de Consulta
- **Detección automática** de especialidad médica
- **Categorización** del tipo de consulta (emergencia, urgente, control, rutina)
- **Extracción de síntomas** principales
- **Generación de preguntas** sugeridas para anamnesis

### 2. Evaluación Inteligente de Antecedentes
- **Detección de banderas rojas** según especialidad
- **Identificación de omisiones** típicas
- **Sugerencias de campos adicionales** relevantes
- **Recomendaciones personalizadas** según edad y comorbilidades

### 3. Sugerencias de Planes de Tratamiento
- **Planes basados en evidencia científica**
- **Referencias bibliográficas** con DOI
- **Niveles de evidencia** (A, B, C)
- **Contraindicaciones** específicas

## 🚀 Cómo Usar Copilot Health

### Acceso desde el Panel de Profesionales

1. Inicia sesión en tu cuenta de profesional
2. Ve al **Panel de Profesionales**
3. Haz clic en la pestaña **"Copilot Health"** (icono de robot 🤖)
4. Se abrirá la interfaz de Copilot Health en una nueva ventana

### Interfaz de Usuario

La interfaz está organizada en **4 secciones principales**:

#### 📊 Análisis del Motivo de Consulta
```
1. Escribe el motivo de consulta del paciente
2. Haz clic en "Analizar con IA"
3. Revisa los resultados:
   - Especialidad detectada
   - Categoría de urgencia
   - Síntomas principales
   - Preguntas sugeridas para anamnesis
```

#### 🔍 Evaluación de Antecedentes
```
1. Ingresa los antecedentes del paciente
2. Selecciona la especialidad
3. Especifica la edad del paciente
4. Haz clic en "Evaluar con IA"
5. Revisa:
   - Banderas rojas detectadas
   - Campos adicionales sugeridos
   - Omisiones identificadas
   - Recomendaciones específicas
```

#### 💊 Sugerencias de Tratamiento
```
1. Ingresa el diagnóstico del paciente
2. Selecciona especialidad y edad
3. Haz clic en "Sugerir Tratamiento"
4. Revisa los planes sugeridos con:
   - Evidencia científica
   - Referencias DOI
   - Nivel de evidencia
   - Contraindicaciones
```

#### 🧠 Análisis Completo
```
1. Completa todos los campos (motivo, antecedentes, diagnóstico)
2. Haz clic en "Análisis Completo"
3. Recibe un resumen integral con todas las sugerencias
```

## 📡 API Endpoints

### Análisis del Motivo de Consulta
```http
POST /api/copilot/analyze-motivo
Content-Type: application/json

{
  "motivo_consulta": "Dolor lumbar de 3 semanas tras cargar peso"
}
```

**Respuesta:**
```json
{
  "success": true,
  "analisis": {
    "especialidad_detectada": "traumatologia",
    "categoria": "rutina",
    "urgencia": "BAJA - Consulta rutinaria",
    "sintomas_principales": ["dolor"],
    "preguntas_sugeridas": [
      "¿Hay irradiación del dolor hacia otras extremidades?",
      "¿Qué actividades agravan o alivian el dolor?",
      "¿Hay antecedentes de trauma directo?"
    ]
  }
}
```

### Evaluación de Antecedentes
```http
POST /api/copilot/evaluate-antecedentes
Content-Type: application/json

{
  "antecedentes": "Paciente de 70 años con diabetes tipo 2",
  "especialidad": "medicina_general",
  "edad": 70
}
```

**Respuesta:**
```json
{
  "success": true,
  "evaluacion": {
    "banderas_rojas": [],
    "campos_adicionales": [],
    "omisiones_detectadas": ["Presión arterial", "Nivel de glicemia"],
    "recomendaciones": ["📋 Considerar incluir: Presión arterial, Nivel de glicemia"]
  }
}
```

### Sugerencias de Tratamiento
```http
POST /api/copilot/suggest-treatment
Content-Type: application/json

{
  "diagnostico": "Dolor lumbar inespecífico",
  "especialidad": "traumatologia",
  "edad": 45
}
```

**Respuesta:**
```json
{
  "success": true,
  "planes_tratamiento": [
    {
      "titulo": "Programa de ejercicio terapéutico progresivo",
      "descripcion": "Ejercicios de fortalecimiento y estiramiento bajo supervisión profesional",
      "evidencia_cientifica": "NICE Guidelines 2023 - Low back pain and sciatica in over 16s",
      "doi_referencia": "10.1001/lumbartx2023.001",
      "nivel_evidencia": "A",
      "contraindicaciones": ["Fractura vertebral", "Cáncer metastásico", "Infección"]
    }
  ]
}
```

### Análisis Completo
```http
POST /api/copilot/complete-analysis
Content-Type: application/json

{
  "motivo_consulta": "Dolor lumbar de 3 semanas tras cargar peso",
  "antecedentes": "Paciente de 45 años, trabajador de construcción",
  "diagnostico": "Dolor lumbar inespecífico"
}
```

## 🧪 Casos de Prueba

### Caso 1: Dolor Lumbar
```
Motivo: "Dolor lumbar de 3 semanas tras cargar peso"
Resultado esperado:
- Especialidad: Traumatología
- Banderas rojas: Pérdida de sensibilidad, dolor que no mejora
- Plan sugerido: Ejercicio terapéutico progresivo
```

### Caso 2: Síntomas Cardíacos
```
Motivo: "Dolor opresivo en el pecho que se irradia al brazo izquierdo"
Resultado esperado:
- Especialidad: Cardiología
- Banderas rojas: Dolor opresivo, irradiación, sudoración fría
- Plan sugerido: Evaluación cardiovascular
```

### Caso 3: Adulto Mayor con Comorbilidades
```
Antecedentes: "Paciente de 70 años con diabetes tipo 2, hipertensión arterial"
Resultado esperado:
- Omisiones detectadas: Presión arterial, nivel de glicemia
- Recomendaciones: Incluir campos adicionales
```

## ⚠️ Aclaración Legal

**IMPORTANTE:** Copilot Health es una herramienta de asistencia que:

- ✅ **Proporciona sugerencias** basadas en evidencia científica
- ✅ **Ayuda a estructurar** la anamnesis
- ✅ **Detecta omisiones** comunes
- ✅ **Sugiere planes** de tratamiento

- ❌ **NO reemplaza** el juicio clínico del profesional
- ❌ **NO diagnostica** enfermedades
- ❌ **NO prescribe** tratamientos
- ❌ **NO garantiza** resultados

**La decisión final siempre recae en el juicio clínico del profesional tratante.**

## 🔧 Configuración Técnica

### Requisitos
- Python 3.8+
- Flask
- Módulo `copilot_health.py` en el directorio raíz

### Instalación
```bash
# El módulo se importa automáticamente en app.py
# No requiere instalación adicional
```

### Verificación
```bash
# Ejecutar pruebas
python test_copilot_health.py
```

## 📊 Especialidades Soportadas

- **Traumatología**: Dolor, fracturas, esguinces, trauma
- **Cardiología**: Dolor torácico, palpitaciones, arritmias
- **Neurología**: Cefaleas, mareos, convulsiones
- **Gastroenterología**: Dolor abdominal, náuseas, vómitos
- **Neumología**: Tos, dificultad respiratoria
- **Dermatología**: Erupciones, lesiones, alergias
- **Endocrinología**: Diabetes, tiroides, peso
- **Psiquiatría**: Ansiedad, depresión, insomnio

## 🎯 Beneficios para Profesionales

### Eficiencia
- **Ahorro de tiempo** en anamnesis estructurada
- **Detección automática** de banderas rojas
- **Sugerencias contextuales** según especialidad

### Calidad
- **Evidencia científica** actualizada
- **Referencias bibliográficas** con DOI
- **Niveles de evidencia** claros

### Seguridad
- **Detección de omisiones** comunes
- **Alertas de banderas rojas**
- **Contraindicaciones** específicas

## 🔮 Roadmap Futuro

### Versión 2.0
- [ ] Integración con historiales clínicos
- [ ] Análisis de imágenes médicas
- [ ] Predicción de complicaciones
- [ ] Integración con guías clínicas actualizadas

### Versión 3.0
- [ ] Machine Learning avanzado
- [ ] Análisis de voz y dictado
- [ ] Integración con dispositivos IoT
- [ ] Telemedicina integrada

---

**Copilot Health - MedConnect.cl**  
*Tu copiloto en cada paso del proceso clínico* 🤖 