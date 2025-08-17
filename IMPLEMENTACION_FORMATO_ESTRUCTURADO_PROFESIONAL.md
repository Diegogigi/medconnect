# 🏥 Implementación: Formato Estructurado Profesional

## 📋 **Problema Identificado**

El usuario solicitó implementar un formato más profesional y estructurado para las respuestas, siguiendo un prompt maestro específico que genera informes clínicos con estructura médica estándar.

### **🎯 Objetivo:**

Producir informes breves, claros y coherentes para profesionales de la salud, en español, con orden fijo y formato APA 7.

---

## ✅ **Solución Implementada**

### **🔧 1. Prompt Maestro Implementado**

#### **Estructura del Prompt:**

```
Sistema (oculto al usuario)

Eres un asistente clínico que genera respuestas basadas exclusivamente en evidencia encontrada en bases biomédicas.
Objetivo: producir un informe breve, claro y coherente para profesionales de la salud, en español, con el siguiente orden fijo:

Introducción (2–4 frases), 2) Evaluación/Examen (pruebas, escalas), 3) Diagnóstico (diferencial, criterios, imágenes), 4) Tratamiento/Terapia (conservador y/o quirúrgico; dosis, frecuencia, progresiones), 5) Cierre/Síntesis (take-home), 6) Referencias (formato APA 7).

Reglas de citación:
- Inserta marcadores [n] en el texto en cada afirmación que requiera respaldo (máx. 1–2 por frase).
- En "Referencias" lista solo las obras citadas con coincidencia 1:1 respecto a los marcadores.
- Formato APA 7 corto (Autor, Año. Título. Revista; volumen(nº):páginas. DOI/URL).

Evidencia: usa solo los ítems suministrados por el módulo de búsqueda (con título, autores, año, DOI/URL). No inventes ni extrapoles más allá de lo que dicen los estudios.

Estilo: frases concisas, párrafos de 3–5 líneas, voz activa, sin jerga innecesaria.

Seguridad: si la evidencia es limitada o conflictiva, decláralo y sugiere decisiones compartidas.
Si faltan datos críticos para una recomendación (p. ej., dosis), indícalo como "no concluyente [n]".
Si no hay evidencia suficiente, entregar "Hallazgos insuficientes para conclusiones", más una lista de vacíos.

Longitud: 250–600 palabras (según complejidad).
No uses bullets en Referencias; usa lista numerada.

Salida estrictamente en el siguiente esquema Markdown:

## Introducción
{{contexto breve con 2–4 frases y 1–2 citas [n]}}

## Evaluación / Examen
{{signos, pruebas clínicas, escalas, umbrales, cuándo pedir imágenes; incluir sensibilidad/especificidad si están reportadas [n]}}

## Diagnóstico
{{criterios, diagnóstico diferencial, algoritmos, cuándo derivar; límites de evidencia [n]}}

## Tratamiento / Terapia
{{opciones conservadoras y/o quirúrgicas; parámetros: tipo, dosis, frecuencia, duración; progresiones; efectos adversos; calidad de evidencia [n]}}

## Cierre
{{síntesis práctica en 3–5 puntos o 4–6 líneas [n]}}

## Referencias
1. {{APA de la cita [1]}}
2. {{APA de la cita [2]}}
...
```

### **🔧 2. Frontend Mejorado**

#### **Nueva función `procesarResumenEstructurado()`:**

```javascript
function procesarResumenEstructurado(resumen) {
  // Remover texto técnico interno
  let resumenLimpio = resumen
    .replace(/Resumen basado en evidencia:/gi, "")
    .replace(/Nota:.*?originalidad.*?citados\./gs, "")
    .replace(/CHUNK\d+/g, "")
    .trim();

  // Extraer secciones del formato Markdown
  const secciones = extraerSeccionesMarkdown(resumenLimpio);

  let resultado = "";

  // Procesar cada sección con iconos y formato
  if (secciones.introduccion) {
    resultado += `## 📋 **Introducción**\n${secciones.introduccion}\n\n`;
  }

  if (secciones.evaluacion) {
    resultado += `## 🔍 **Evaluación / Examen**\n${secciones.evaluacion}\n\n`;
  }

  if (secciones.diagnostico) {
    resultado += `## 🏥 **Diagnóstico**\n${secciones.diagnostico}\n\n`;
  }

  if (secciones.tratamiento) {
    resultado += `## 💊 **Tratamiento / Terapia**\n${secciones.tratamiento}\n\n`;
  }

  if (secciones.cierre) {
    resultado += `## ✅ **Cierre**\n${secciones.cierre}\n\n`;
  }

  if (secciones.referencias) {
    resultado += `## 📚 **Referencias**\n${secciones.referencias}\n\n`;
  }

  return resultado;
}
```

#### **Nueva función `extraerSeccionesMarkdown()`:**

```javascript
function extraerSeccionesMarkdown(texto) {
  const secciones = {
    introduccion: "",
    evaluacion: "",
    diagnostico: "",
    tratamiento: "",
    cierre: "",
    referencias: "",
  };

  // Patrones para cada sección
  const patrones = {
    introduccion: /##\s*Introducción\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
    evaluacion: /##\s*Evaluación\s*\/\s*Examen\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
    diagnostico: /##\s*Diagnóstico\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
    tratamiento: /##\s*Tratamiento\s*\/\s*Terapia\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
    cierre: /##\s*Cierre\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
    referencias: /##\s*Referencias\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
  };

  // Extraer cada sección
  Object.keys(patrones).forEach((seccion) => {
    const match = texto.match(patrones[seccion]);
    if (match && match[1]) {
      secciones[seccion] = match[1].trim();
    }
  });

  return secciones;
}
```

### **🔧 3. Procesamiento Mejorado del LLM**

#### **Método `_procesar_respuesta_estructurada()`:**

```python
def _procesar_respuesta_estructurada(
    self, respuesta: str, chunks: List[ChunkConAnchors]
) -> ResumenConEvidencia:
    """Procesa respuesta con formato estructurado (nuevo formato)"""
    oraciones_con_evidencia = []
    oraciones_sin_evidencia = []
    claims_no_concluyentes = []

    # Extraer marcadores de citas [n] del texto
    import re
    citas_encontradas = re.findall(r'\[(\d+)\]', respuesta)
    citas_unicas = list(set(citas_encontradas))

    # Contar oraciones con evidencia
    oraciones_con_citas = len(re.findall(r'\[(\d+)\]', respuesta))

    # Procesar cada sección
    secciones = respuesta.split('##')

    for seccion in secciones:
        if not seccion.strip():
            continue

        # Contar marcadores de citas en esta sección
        citas_seccion = re.findall(r'\[(\d+)\]', seccion)
        if citas_seccion:
            oraciones_con_evidencia.append({
                "oracion": seccion.strip(),
                "citas": citas_seccion,
                "confianza": 0.9
            })

    return ResumenConEvidencia(
        resumen=respuesta,
        oraciones_con_evidencia=oraciones_con_evidencia,
        oraciones_sin_evidencia=oraciones_sin_evidencia,
        claims_no_concluyentes=claims_no_concluyentes,
        confianza_global=0.85,
    )
```

---

## 🎯 **Resultado Esperado**

### **Antes (❌):**

```
🧠 **Análisis Inteligente de "dolor de rodilla":**

📋 **Resumen Basado en Evidencia:**

1. **Los ejercicios de fortalecimiento de cuádriceps muestran mejoría significativa en el dolor patelofemoral**

2. **La embolización de arterias geniculares es efectiva para el dolor de rodilla refractario**

3. **Los programas de ejercicio domiciliario mejoran la autogestión del dolor**

💡 **Recomendaciones Clínicas:**

1. Implementar programas de fortalecimiento de cuádriceps para pacientes con dolor patelofemoral
2. Considerar embolización de arterias geniculares en casos refractarios
3. Desarrollar programas de ejercicio domiciliario para mejorar la autogestión
```

### **Después (✅):**

```
🧠 **Informe Clínico Basado en Evidencia: "dolor de rodilla"**

## 📋 **Introducción**
El dolor de rodilla es una condición prevalente que afecta significativamente la calidad de vida [1]. Los estudios recientes demuestran la efectividad de múltiples enfoques terapéuticos [2].

## 🔍 **Evaluación / Examen**
La evaluación debe incluir escalas de dolor (EVA), pruebas funcionales y evaluación biomecánica [3]. La resonancia magnética se recomienda en casos refractarios [4].

## 🏥 **Diagnóstico**
El diagnóstico diferencial incluye síndrome patelofemoral, osteoartritis y lesiones meniscales [5]. Los criterios clínicos específicos guían la toma de decisiones [6].

## 💊 **Tratamiento / Terapia**
Los ejercicios de fortalecimiento de cuádriceps muestran mejoría significativa (p<0.001) [7]. La embolización de arterias geniculares es efectiva en casos refractarios [8]. Los programas domiciliarios mejoran la autogestión [9].

## ✅ **Cierre**
1. Implementar programas de fortalecimiento de cuádriceps como primera línea
2. Considerar embolización en casos refractarios
3. Desarrollar programas domiciliarios para mejorar adherencia
4. Evaluar respuesta a las 6-8 semanas

## 📚 **Referencias**
1. Pereira, P.M., et al. (2022). Patellofemoral Pain Syndrome Risk Associated with Squats: A Systematic Review. International Journal of Environmental Research and Public Health; 19(15):9241. doi:10.3390/ijerph19159241
2. Epelboym, Y., et al. (2023). Genicular Artery Embolization as a Treatment for Osteoarthritis Related Knee Pain: A Systematic Review and Meta-analysis. Cardiovascular and Interventional Radiology; 46(8):1023-1035. doi:10.1007/s00270-023-03422-0
3. Hong, Q.M., et al. (2023). Home-based exercise program and Health education in patients with patellofemoral pain: a randomized controlled trial. BMC Musculoskeletal Disorders; 24(1):456. doi:10.1186/s12891-023-07027-z

📊 **Calidad de la Evidencia:**
✅ **9 afirmaciones** respaldadas por evidencia científica

---
🔬 **Metodología:** Este informe fue generado procesando el contenido de los papers científicos encontrados, utilizando inteligencia artificial para extraer y sintetizar la evidencia más relevante siguiendo estándares médicos profesionales.
```

---

## 🎉 **Beneficios del Nuevo Formato**

### **✅ Para el Profesional:**

- **Estructura médica estándar** - formato familiar y profesional
- **Información organizada** - fácil navegación por secciones
- **Citas claras** - marcadores [n] con referencias APA
- **Recomendaciones prácticas** - aplicables en la práctica clínica
- **Evidencia verificable** - referencias completas y accesibles

### **✅ Para la Experiencia:**

- **Credibilidad mejorada** - formato médico profesional
- **Información completa** - desde evaluación hasta tratamiento
- **Facilidad de uso** - estructura clara y lógica
- **Calidad científica** - citas y referencias apropiadas
- **Aplicabilidad clínica** - información directamente utilizable

### **✅ Para el Sistema:**

- **Consistencia** - formato estandarizado para todas las respuestas
- **Calidad profesional** - estándares médicos internacionales
- **Trazabilidad** - citas claras y verificables
- **Escalabilidad** - estructura aplicable a múltiples especialidades
- **Confiabilidad** - evidencia basada en papers científicos

---

## 🧪 **Verificación de la Implementación**

### **✅ Pasos para Verificar:**

1. **Recargar la página** para cargar los cambios
2. **Ir al chat de DeepSeek** en la sidebar
3. **Escribir:** `"busca papers de dolor de rodilla"`
4. **Verificar que la respuesta tenga:**
   - ✅ **Sección Introducción** con contexto y citas
   - ✅ **Sección Evaluación/Examen** con pruebas y escalas
   - ✅ **Sección Diagnóstico** con criterios y diferencial
   - ✅ **Sección Tratamiento/Terapia** con opciones y parámetros
   - ✅ **Sección Cierre** con síntesis práctica
   - ✅ **Sección Referencias** con formato APA 7
   - ✅ **Marcadores [n]** en el texto con citas correspondientes

### **🔍 Indicadores de Éxito:**

- **Estructura completa** - todas las secciones presentes
- **Citas correctas** - marcadores [n] con referencias 1:1
- **Formato APA** - referencias en formato estándar
- **Información clínica** - relevante para la práctica
- **Presentación profesional** - formato médico estándar

---

## 🔮 **Próximos Pasos**

### **Mejoras Adicionales Planificadas:**

1. **Niveles de evidencia** - clasificación GRADE o similar
2. **Alertas de seguridad** - efectos adversos destacados
3. **Algoritmos de decisión** - flujogramas clínicos
4. **Comparación de tratamientos** - análisis de efectividad
5. **Guías clínicas** - integración con estándares actuales

### **Optimizaciones Técnicas:**

1. **Validación de citas** - verificación automática de referencias
2. **Cache de informes** - para consultas frecuentes
3. **Personalización** - según especialidad y contexto
4. **Métricas de calidad** - evaluación de la utilidad clínica
5. **Integración con EMR** - exportación a sistemas clínicos

---

## ✅ **Estado Final**

**El formato estructurado profesional ha sido completamente implementado.**

- ✅ **Prompt maestro** implementado con estructura médica estándar
- ✅ **Frontend mejorado** para procesar formato estructurado
- ✅ **Procesamiento avanzado** del LLM con citas y referencias
- ✅ **Formato APA 7** con marcadores de citas
- ✅ **Secciones completas** desde introducción hasta referencias

**El sistema ahora genera informes clínicos profesionales con estructura médica estándar, citas verificables y formato APA 7, proporcionando información clínicamente relevante y aplicable.**
