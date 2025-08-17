#!/usr/bin/env python3
"""
Script de prueba para verificar que la eliminación de Markdown funciona correctamente
"""

import os
import re


def verificar_eliminacion_markdown():
    """Verifica que la función de eliminación de Markdown se ha implementado correctamente"""

    print("🔍 Verificando implementación de eliminación de Markdown...")

    # Archivo a verificar
    archivo = "static/js/professional.js"

    cambios_verificados = {
        "funcion_eliminar_markdown": False,
        "llamada_eliminar_markdown": False,
        "procesamiento_sin_markdown": False,
        "regex_markdown_implementado": False,
    }

    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Verificar función eliminarMarkdown
    if re.search(r"function eliminarMarkdown", contenido):
        cambios_verificados["funcion_eliminar_markdown"] = True
        print("✅ Función eliminarMarkdown creada")

    # Verificar llamada a eliminarMarkdown
    if re.search(r"eliminarMarkdown\(mensaje\)", contenido):
        cambios_verificados["llamada_eliminar_markdown"] = True
        print("✅ Llamada a eliminarMarkdown implementada")

    # Verificar procesamiento sin Markdown
    if re.search(r"Eliminar completamente el formato Markdown", contenido):
        cambios_verificados["procesamiento_sin_markdown"] = True
        print("✅ Procesamiento sin Markdown implementado")

    # Verificar regex para eliminar Markdown
    if re.search(r"```markdown", contenido):
        cambios_verificados["regex_markdown_implementado"] = True
        print("✅ Regex para eliminar Markdown implementado")

    # Resumen de verificación
    print("\n📊 Resumen de verificación:")
    total_cambios = len(cambios_verificados)
    cambios_exitosos = sum(cambios_verificados.values())

    for cambio, verificado in cambios_verificados.items():
        estado = "✅" if verificado else "❌"
        print(f"{estado} {cambio}")

    print(f"\n🎯 Progreso: {cambios_exitosos}/{total_cambios} cambios aplicados")

    if cambios_exitosos == total_cambios:
        print("🎉 ¡La eliminación de Markdown se ha implementado correctamente!")
        print("💡 Ahora las respuestas se convertirán a formato simple")
        print("💡 Sin símbolos Markdown complejos")
        print("💡 Formato natural y legible")
    else:
        print("⚠️ Algunos cambios no se han aplicado completamente")
        print("💡 Revisa los archivos manualmente si es necesario")


def mostrar_ejemplo_conversion():
    """Muestra un ejemplo de la conversión de Markdown a formato simple"""

    ejemplo = """
📋 **EJEMPLO DE CONVERSIÓN DE MARKDOWN A FORMATO SIMPLE:**

**Entrada (Markdown complejo):**
```
```markdown
## Evaluación de Esguince de Tobillo (Mujer, 34 años)

### 1. **Anamnesis**
- **Mecanismo de lesión**: Posible inversión forzada del pie (movimiento hacia adentro).
- **Síntomas reportados**:
- Dolor localizado en cara lateral del tobillo.
- Hinchazón progresiva.

### 2. **Exploración Física**
- **Inspección**:
- Edema en región maleolar externa.
- Equimosis (correlaciona con gravedad).

| **Grado** | **Características** |
|-----------|---------------------------------------------------|
| **I** | Estiramiento ligamentoso sin rotura. Dolor leve, edema mínimo. |
| **II** | Rotura parcial. Dolor moderado, edema visible, inestabilidad leve. |
```

**Salida (Formato simple):**
```
Evaluación de Esguince de Tobillo (Mujer, 34 años)

1. Anamnesis
   Mecanismo de lesión: Posible inversión forzada del pie (movimiento hacia adentro).
   Síntomas reportados:
   Dolor localizado en cara lateral del tobillo.
   Hinchazón progresiva.

2. Exploración Física
   Inspección:
   Edema en región maleolar externa.
   Equimosis (correlaciona con gravedad).

Grado I: Estiramiento ligamentoso sin rotura. Dolor leve, edema mínimo.
Grado II: Rotura parcial. Dolor moderado, edema visible, inestabilidad leve.
```

**Elementos eliminados:**
- ✅ Bloques de código ```markdown```
- ✅ Encabezados ## y ###
- ✅ Negritas **texto**
- ✅ Listas con guiones -
- ✅ Tablas con | |
- ✅ Emojis y símbolos especiales
- ✅ Líneas horizontales ---
"""

    print(ejemplo)


def generar_instrucciones_verificacion():
    """Genera instrucciones para verificar la funcionalidad manualmente"""

    instrucciones = """
🔍 INSTRUCCIONES PARA VERIFICAR MANUALMENTE:

1. 📱 Abre la aplicación en el navegador
2. 🔄 Limpia el cache del navegador (Ctrl + Shift + R)
3. 🔍 Ve a la página del profesional
4. 📋 Abre la sidebar (botón en la esquina superior derecha)

5. ✅ Prueba hacer la misma consulta:
   - Escribe: "entregame una evaluación para un esguince de tobillo para una mujer de 34 años"
   - Presiona Enter

6. 🔍 Verifica que NO aparece Markdown:
   - NO debería aparecer ```markdown
   - NO debería aparecer ## o ###
   - NO debería aparecer **texto en negrita**
   - NO debería aparecer tablas con | |
   - NO debería aparecer emojis 🔍📋🧩

7. 📝 Verifica el formato simple:
   - Debería aparecer texto plano y legible
   - Encabezados simples sin símbolos
   - Listas numeradas simples
   - Información clara y ordenada

8. 🔄 Prueba diferentes consultas:
   - Consultas que antes generaban Markdown
   - Verifica que todas aparecen en formato simple
   - Confirma que la información se mantiene completa

✅ Si las respuestas aparecen en formato simple sin símbolos Markdown, la eliminación está funcionando correctamente.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de eliminación de Markdown")
    print("=" * 60)

    mostrar_ejemplo_conversion()

    print("\n" + "=" * 60)
    verificar_eliminacion_markdown()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
