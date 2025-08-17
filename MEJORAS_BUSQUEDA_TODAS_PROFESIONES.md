# MEJORAS DE BÚSQUEDA CONTEXTUAL PARA TODAS LAS PROFESIONES

## Resumen de Implementación

Se han aplicado mejoras significativas al sistema de búsqueda contextual del Copilot Health Assistant para que funcione de manera óptima con **todas las profesiones** soportadas por la plataforma MedConnect.

## Profesiones Soportadas

### 1. **Kinesiología / Fisioterapia**
- **Términos clave**: fisioterapia, kinesiología, rehabilitación, terapia física, movimiento
- **Contexto clínico**: intervención fisioterapéutica
- **Términos anatómicos específicos**: rodilla, hombro, espalda, cuello, cabeza, brazo, pierna, tobillo, muñeca, codo, cadera, columna, lumbar, cervical, articulación, músculo, tendón, ligamento, menisco, cartílago

### 2. **Medicina General**
- **Términos clave**: medicina clínica, medicina general, diagnóstico médico, tratamiento médico
- **Contexto clínico**: evaluación médica integral
- **Análisis completo**: síntomas, diagnósticos, tratamientos farmacológicos y no farmacológicos

### 3. **Psicología**
- **Términos clave**: psicología, salud mental, terapia psicológica, intervención psicológica, bienestar emocional
- **Contexto clínico**: evaluación psicológica
- **Términos específicos**: ansiedad, depresión, estrés, trauma, miedo, pánico, obsesión, compulsión, trastorno, bipolar, esquizofrenia

### 4. **Fonoaudiología**
- **Términos clave**: fonoaudiología, terapia del lenguaje, comunicación, habla, lenguaje, deglución
- **Contexto clínico**: evaluación fonoaudiológica
- **Términos específicos**: voz, habla, lenguaje, comunicación, deglución, respiración, articulación, disfonía, afasia, disfagia

## Mejoras Implementadas

### 1. **Análisis Contextual por Profesión**
- Cada profesión tiene términos específicos que se extraen automáticamente
- El sistema identifica la especialidad basándose en el `tipoAtencion`
- Se generan términos de búsqueda más precisos y relevantes

### 2. **Extracción de Términos Anatómicos**
- Sistema mejorado para detectar regiones anatómicas específicas
- Identificación de estructuras musculoesqueléticas
- Contextualización del dolor y síntomas por región

### 3. **Análisis de Síntomas Específicos**
- **Dolor**: constante, intermitente, agravado
- **Inflamación**: hinchazón, edema, calor local
- **Inestabilidad**: bloqueo articular, disfunción
- **Limitación funcional**: dificultad para movimientos, escaleras, postura

### 4. **Contexto por Edad**
- **Pediátrico** (< 18 años): términos específicos para niños y adolescentes
- **Adulto** (18-65 años): términos generales
- **Geriátrico** (> 65 años): términos específicos para adultos mayores

### 5. **Análisis de Causas**
- **Trauma**: golpe, lesión traumática
- **Laboral**: lesión laboral, accidente de trabajo
- **Deportivo**: lesión deportiva, actividad física

## Funcionamiento del Sistema

### Proceso de Búsqueda Mejorada

1. **Análisis del Tipo de Atención**
   ```javascript
   if (tipoLower.includes('kinesiologia') || tipoLower.includes('fisioterapia')) {
       especialidad = 'fisioterapia';
       terminosClave.push('fisioterapia', 'kinesiología', 'rehabilitación');
   }
   ```

2. **Extracción de Términos Específicos por Profesión**
   ```javascript
   // Para Fonoaudiología
   if (especialidad === 'fonoaudiología') {
       const terminosFono = ['voz', 'habla', 'lenguaje', 'comunicación', 'deglución'];
       // Análisis específico...
   }
   ```

3. **Análisis del Motivo de Consulta**
   - Identificación de términos anatómicos
   - Detección de causas específicas
   - Contextualización por especialidad

4. **Análisis de la Evaluación**
   - Síntomas específicos por profesión
   - Patrones de dolor y disfunción
   - Limitaciones funcionales

5. **Generación de Query Completa**
   ```javascript
   const queryCompleta = [
       datos.motivoConsulta,
       ...terminosClave.slice(0, 5),
       especialidad
   ].filter(Boolean).join(' ');
   ```

## Beneficios para Cada Profesión

### **Kinesiología**
- Identificación precisa de regiones anatómicas
- Análisis de patrones de movimiento
- Contextualización de lesiones deportivas y laborales

### **Medicina General**
- Evaluación integral de síntomas
- Análisis de múltiples sistemas
- Contextualización de diagnósticos diferenciales

### **Psicología**
- Identificación de síntomas psicológicos específicos
- Análisis de trastornos mentales
- Contextualización de intervenciones terapéuticas

### **Fonoaudiología**
- Identificación de trastornos de comunicación
- Análisis de problemas de deglución
- Contextualización de terapias del lenguaje

## Ejemplos de Búsqueda Mejorada

### Caso Kinesiología
- **Entrada**: "Dolor de rodilla por golpe en el trabajo"
- **Términos generados**: rodilla, trauma, lesión laboral, fisioterapia, rehabilitación
- **Query final**: "Dolor de rodilla por golpe en el trabajo rodilla trauma lesión laboral fisioterapia"

### Caso Psicología
- **Entrada**: "Ansiedad y estrés por problemas laborales"
- **Términos generados**: ansiedad, estrés, psicología, salud mental, terapia psicológica
- **Query final**: "Ansiedad y estrés por problemas laborales ansiedad estrés psicología"

### Caso Fonoaudiología
- **Entrada**: "Dificultad para hablar después de un accidente"
- **Términos generados**: habla, comunicación, fonoaudiología, terapia del lenguaje
- **Query final**: "Dificultad para hablar después de un accidente habla comunicación fonoaudiología"

## Implementación Técnica

### Archivos Modificados
- `static/js/professional.js`: Función `generarTerminosBusquedaMejorados()`
- `templates/professional.html`: Cache-busting para v=3.7

### Funciones Clave
- `generarTerminosBusquedaMejorados(datos)`: Análisis contextual completo
- `buscarEvidenciaAutomatica(motivoConsulta)`: Búsqueda con términos mejorados
- `mostrarPapersAutomaticos(papers)`: Visualización de resultados

## Resultados Esperados

1. **Búsquedas más precisas** para cada especialidad
2. **Resultados más relevantes** basados en el contexto profesional
3. **Mejor identificación** de términos específicos por profesión
4. **Contextualización adecuada** de síntomas y diagnósticos
5. **Papers científicos más pertinentes** para cada caso clínico

## Verificación

Para verificar que las mejoras funcionan correctamente:

1. **Probar con diferentes profesiones**:
   - Seleccionar cada tipo de atención
   - Ingresar motivos de consulta específicos
   - Verificar que los términos generados sean apropiados

2. **Verificar la búsqueda de papers**:
   - Los resultados deben ser más específicos
   - Los papers deben estar relacionados con la especialidad
   - Los términos de búsqueda deben ser más precisos

3. **Comprobar la contextualización**:
   - Los términos deben reflejar la profesión seleccionada
   - El análisis debe ser apropiado para cada especialidad
   - Los resultados deben ser relevantes al contexto clínico

## Conclusión

Las mejoras implementadas aseguran que el sistema de búsqueda contextual funcione de manera óptima para **todas las profesiones** soportadas por MedConnect, proporcionando resultados más precisos y relevantes para cada especialidad médica. 