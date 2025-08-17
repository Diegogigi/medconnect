#!/usr/bin/env python3
"""
Script para analizar el problema de formato duplicado en las respuestas de Tena
y proponer una solución unificada
"""

import os
import re


def analizar_problema_formato_duplicado():
    """Analiza el problema de formato duplicado en las respuestas"""

    print("🔍 Analizando problema de formato duplicado en respuestas de Tena...")

    # Archivo a analizar
    archivo = "static/js/professional.js"

    problemas_identificados = {
        "buildContextSummaryMarkdown": False,
        "enviarMensajeCopilot": False,
        "inicializarSincronizacionFormularioCopilot": False,
        "agregarMensajeElegant": False,
    }

    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Analizar buildContextSummaryMarkdown
    if re.search(r"buildContextSummaryMarkdown.*agregarMensajeElegant", contenido):
        problemas_identificados["buildContextSummaryMarkdown"] = True
        print("⚠️ buildContextSummaryMarkdown genera mensajes adicionales")

    # Analizar enviarMensajeCopilot
    if re.search(
        r"agregarMensajeElegant.*assistant.*agregarMensajeElegant.*assistant", contenido
    ):
        problemas_identificados["enviarMensajeCopilot"] = True
        print("⚠️ enviarMensajeCopilot puede generar múltiples mensajes")

    # Analizar inicializarSincronizacionFormularioCopilot
    if re.search(
        r"inicializarSincronizacionFormularioCopilot.*agregarMensajeElegant", contenido
    ):
        problemas_identificados["inicializarSincronizacionFormularioCopilot"] = True
        print(
            "⚠️ inicializarSincronizacionFormularioCopilot genera mensajes automáticos"
        )

    # Analizar agregarMensajeElegant
    if re.search(r"tipo === \'assistant\'.*marked\.parse", contenido):
        problemas_identificados["agregarMensajeElegant"] = True
        print("✅ agregarMensajeElegant procesa Markdown correctamente")

    # Resumen del análisis
    print("\n📊 Análisis del problema:")
    total_problemas = len(problemas_identificados)
    problemas_encontrados = sum(problemas_identificados.values())

    for problema, encontrado in problemas_identificados.items():
        estado = "⚠️" if encontrado else "✅"
        print(f"{estado} {problema}")

    print(f"\n🎯 Problemas identificados: {problemas_encontrados}/{total_problemas}")

    if problemas_encontrados > 0:
        print("🔧 Se requiere implementar solución unificada")
    else:
        print("✅ No se detectaron problemas de formato")


def generar_solucion_unificada():
    """Genera la solución para unificar el formato de las respuestas"""

    solucion = """
🔧 **SOLUCIÓN PARA UNIFICAR FORMATO DE RESPUESTAS**

## 🎯 **Problema Identificado:**
- Múltiples funciones generan respuestas en diferentes formatos
- buildContextSummaryMarkdown genera contexto en formato Markdown
- enviarMensajeCopilot genera respuesta principal
- Pueden aparecer simultáneamente causando duplicación

## 🛠️ **Solución Propuesta:**

### **1. Modificar enviarMensajeCopilot:**
```javascript
async function enviarMensajeCopilot(message) {
    try {
        // Borrar mensaje de bienvenida si existe
        borrarMensajeBienvenida();
        
        // NO generar contexto automáticamente aquí
        // const context = getContextoPacienteDesdeFormulario();
        // const ctxHash = __hashContext(context);
        // if (ctxHash !== __lastCtxHash) {
        //     const mdCtx = buildContextSummaryMarkdown(context);
        //     if (mdCtx) agregarMensajeElegant(mdCtx, 'assistant');
        //     __lastCtxHash = ctxHash;
        // }
        
        mostrarTypingElegant();
        const resp = await fetch('/api/copilot/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
            body: JSON.stringify({ message, context })
        });
        const data = await resp.json();
        removerTypingElegant();
        if (data.success) {
            // Unificar respuesta en un solo mensaje
            const respuestaUnificada = unificarRespuesta(data.reply, context);
            agregarMensajeElegant(respuestaUnificada, 'assistant');
        } else {
            agregarMensajeElegant('❌ ' + (data.message || 'Error al procesar la solicitud'), 'error');
        }
    } catch (err) {
        removerTypingElegant();
        agregarMensajeElegant('❌ Error de conexión: ' + err.message, 'error');
    }
}
```

### **2. Crear función unificarRespuesta:**
```javascript
function unificarRespuesta(respuestaIA, contexto) {
    // Si la respuesta ya incluye contexto, devolverla tal como está
    if (respuestaIA.includes('Contexto del caso') || respuestaIA.includes('Ficha Resumen')) {
        return respuestaIA;
    }
    
    // Si no incluye contexto, agregarlo al inicio
    const context = getContextoPacienteDesdeFormulario();
    const mdCtx = buildContextSummaryMarkdown(context);
    
    if (mdCtx) {
        return mdCtx + '\n\n' + respuestaIA;
    }
    
    return respuestaIA;
}
```

### **3. Desactivar sincronización automática:**
```javascript
// Comentar o remover la función inicializarSincronizacionFormularioCopilot
// para evitar mensajes automáticos no deseados
```

## ✅ **Beneficios de la Solución:**
- ✅ Una sola respuesta unificada por consulta
- ✅ Formato consistente en Markdown
- ✅ Contexto incluido solo cuando sea necesario
- ✅ Eliminación de duplicación de mensajes
- ✅ Mejor experiencia de usuario

## 📋 **Implementación:**
1. Modificar enviarMensajeCopilot para no generar contexto automático
2. Crear función unificarRespuesta
3. Desactivar sincronización automática del formulario
4. Probar con diferentes tipos de consultas
"""

    print(solucion)


def generar_instrucciones_implementacion():
    """Genera instrucciones para implementar la solución"""

    instrucciones = """
🔧 **INSTRUCCIONES PARA IMPLEMENTAR LA SOLUCIÓN:**

1. 📝 **Modificar enviarMensajeCopilot:**
   - Comentar las líneas que generan contexto automático
   - Agregar llamada a unificarRespuesta
   - Mantener solo una llamada a agregarMensajeElegant

2. 🆕 **Crear función unificarRespuesta:**
   - Verificar si la respuesta ya incluye contexto
   - Agregar contexto solo si es necesario
   - Mantener formato Markdown consistente

3. 🚫 **Desactivar sincronización automática:**
   - Comentar inicializarSincronizacionFormularioCopilot
   - Evitar mensajes automáticos no deseados

4. 🧪 **Probar la implementación:**
   - Hacer consultas simples y complejas
   - Verificar que solo aparece una respuesta
   - Confirmar formato consistente

5. ✅ **Verificar resultados:**
   - Una sola respuesta por consulta
   - Formato Markdown unificado
   - Sin duplicación de información
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Análisis de problema de formato duplicado en Tena")
    print("=" * 60)

    analizar_problema_formato_duplicado()

    print("\n" + "=" * 60)
    generar_solucion_unificada()

    print("\n" + "=" * 60)
    generar_instrucciones_implementacion()
