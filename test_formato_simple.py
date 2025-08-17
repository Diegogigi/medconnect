#!/usr/bin/env python3
"""
Script de prueba para verificar que el formato simple se ha implementado correctamente
"""

import os
import re


def verificar_formato_simple():
    """Verifica que el formato simple se ha implementado correctamente"""

    print("🔍 Verificando implementación de formato simple...")

    # Archivo a verificar
    archivo = "static/js/professional.js"

    cambios_verificados = {
        "funcion_build_contexto_simple": False,
        "unificar_respuesta_modificada": False,
        "agregar_mensaje_sin_markdown": False,
        "formato_simple_implementado": False,
    }

    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Verificar función buildContextoSimple
    if re.search(r"function buildContextoSimple", contenido):
        cambios_verificados["funcion_build_contexto_simple"] = True
        print("✅ Función buildContextoSimple creada")

    # Verificar que unificarRespuesta usa buildContextoSimple
    if re.search(r"buildContextoSimple\(context\)", contenido):
        cambios_verificados["unificar_respuesta_modificada"] = True
        print("✅ unificarRespuesta modificada para usar formato simple")

    # Verificar que agregarMensajeElegant no procesa Markdown
    if re.search(r"Convertir saltos de línea a <br>", contenido):
        cambios_verificados["agregar_mensaje_sin_markdown"] = True
        print("✅ agregarMensajeElegant modificado para formato simple")

    # Verificar formato simple en buildContextoSimple
    if re.search(r"CONTEXTO DEL CASO:", contenido):
        cambios_verificados["formato_simple_implementado"] = True
        print("✅ Formato simple implementado en buildContextoSimple")

    # Resumen de verificación
    print("\n📊 Resumen de verificación:")
    total_cambios = len(cambios_verificados)
    cambios_exitosos = sum(cambios_verificados.values())

    for cambio, verificado in cambios_verificados.items():
        estado = "✅" if verificado else "❌"
        print(f"{estado} {cambio}")

    print(f"\n🎯 Progreso: {cambios_exitosos}/{total_cambios} cambios aplicados")

    if cambios_exitosos == total_cambios:
        print("🎉 ¡El formato simple se ha implementado correctamente!")
        print("💡 Ahora las respuestas usan formato natural y simple")
        print("💡 Sin Markdown complejo")
        print("💡 Información ordenada y fácil de leer")
    else:
        print("⚠️ Algunos cambios no se han aplicado completamente")
        print("💡 Revisa los archivos manualmente si es necesario")


def generar_instrucciones_verificacion():
    """Genera instrucciones para verificar la funcionalidad manualmente"""

    instrucciones = """
🔍 INSTRUCCIONES PARA VERIFICAR MANUALMENTE:

1. 📱 Abre la aplicación en el navegador
2. 🔄 Limpia el cache del navegador (Ctrl + Shift + R)
3. 🔍 Ve a la página del profesional
4. 📋 Abre la sidebar (botón en la esquina superior derecha)

5. ✅ Prueba hacer una consulta:
   - Escribe: "Hola, estoy atendiendo a la paciente Giselle Arratia"
   - Completa algunos campos del formulario:
     * Tipo de atención: Kinesiología
     * Motivo: Dolor de caderas por lesión
     * Edad: 35
     * Sexo: Femenino
   - Pregunta: "que evaluación puedo realizar?"
   - Presiona Enter

6. 🔍 Verifica el formato simple:
   - Debería aparecer una respuesta con formato simple
   - Contexto en formato: "CONTEXTO DEL CASO:" seguido de líneas simples
   - NO debería aparecer Markdown complejo (##, **, tablas, etc.)
   - La información debería estar ordenada y fácil de leer

7. 📝 Verifica la estructura:
   - Contexto del caso al inicio
   - Información del paciente en líneas simples
   - Evaluación en formato de lista numerada simple
   - Sin emojis ni formato complejo

8. 🔄 Prueba diferentes consultas:
   - Consultas simples
   - Consultas complejas
   - Verifica que siempre usa formato simple y natural

✅ Si las respuestas aparecen en formato simple y ordenado sin Markdown complejo, la implementación está funcionando correctamente.
"""

    print(instrucciones)


def mostrar_ejemplo_formato():
    """Muestra un ejemplo del nuevo formato"""

    ejemplo = """
📋 **EJEMPLO DEL NUEVO FORMATO SIMPLE:**

**Antes (Markdown complejo):**
```
## 📋 **Ficha Resumen: Giselle Arratia**
**Contexto:**  
- **Motivo de consulta:** Dolor de caderas por lesión  
- **Tipo de atención:** Kinesiología  
- **Datos faltantes:** Edad, sexo, evaluación inicial, plan preliminar  
```

**Después (Formato simple):**
```
CONTEXTO DEL CASO:
Paciente: Giselle Arratia
Tipo de atención: Kinesiología
Motivo: Dolor de caderas por lesión
Edad: 35 años
Sexo: Femenino

Evaluación Kinésica para Dolor de Caderas por Lesión

1. Anamnesis Detallada
   Historia de la lesión: Mecanismo (traumático/sobreuso), tiempo de evolución, tratamiento previo.
   Características del dolor: Localización (anterior, lateral, posterior).

2. Examen Físico
   Inspección: Postura estática/dinámica (alineación pélvica, marcha).
   Palpación: Puntos clave: Trocanter mayor, región inguinal.

3. Evaluación Muscular
   Fuerza: Glúteo medio/máximo, psoas, aductores, isquiotibiales.
   Flexibilidad: Flexores de cadera, piriforme, tensor de la fascia lata.
```

**Beneficios del formato simple:**
- ✅ Fácil de leer y entender
- ✅ Sin símbolos complejos
- ✅ Información ordenada
- ✅ Formato natural
- ✅ Mejor legibilidad
"""

    print(ejemplo)


if __name__ == "__main__":
    print("🚀 Verificación de formato simple")
    print("=" * 60)

    mostrar_ejemplo_formato()

    print("\n" + "=" * 60)
    verificar_formato_simple()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
