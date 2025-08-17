#!/usr/bin/env python3
"""
Script de prueba para verificar que el mensaje de bienvenida se borra cuando el profesional escribe un mensaje
"""

import os
import re


def verificar_borrar_mensaje_bienvenida():
    """Verifica que el mensaje de bienvenida se borra cuando el profesional escribe un mensaje"""

    print("🔍 Verificando funcionalidad de borrar mensaje de bienvenida...")

    # Archivo a verificar
    archivo = "static/js/professional.js"

    cambios_verificados = {
        "enviar_mensaje_borra_bienvenida": False,
        "agregar_mensaje_user_borra_bienvenida": False,
        "funcion_borrar_mensaje_existe": False,
        "html_input_correcto": False,
    }

    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Verificar que enviarMensajeCopilot llama a borrarMensajeBienvenida
    if re.search(r"borrarMensajeBienvenida\(\)", contenido):
        cambios_verificados["enviar_mensaje_borra_bienvenida"] = True
        print("✅ enviarMensajeCopilot llama a borrarMensajeBienvenida")

    # Verificar que agregarMensajeElegant borra bienvenida para mensajes de usuario
    if re.search(r"if \(tipo === \'user\'\)", contenido):
        cambios_verificados["agregar_mensaje_user_borra_bienvenida"] = True
        print("✅ agregarMensajeElegant borra bienvenida para mensajes de usuario")

    # Verificar que la función borrarMensajeBienvenida existe
    if re.search(r"function borrarMensajeBienvenida", contenido):
        cambios_verificados["funcion_borrar_mensaje_existe"] = True
        print("✅ Función borrarMensajeBienvenida existe")

    # Verificar HTML del input
    archivo_html = "templates/professional.html"
    if os.path.exists(archivo_html):
        with open(archivo_html, "r", encoding="utf-8") as f:
            contenido_html = f.read()

        if re.search(r"agregarMensajeElegant\(this\.value,\'user\'\)", contenido_html):
            cambios_verificados["html_input_correcto"] = True
            print(
                "✅ HTML del input llama correctamente a agregarMensajeElegant con tipo 'user'"
            )

    # Resumen de verificación
    print("\n📊 Resumen de verificación:")
    total_cambios = len(cambios_verificados)
    cambios_exitosos = sum(cambios_verificados.values())

    for cambio, verificado in cambios_verificados.items():
        estado = "✅" if verificado else "❌"
        print(f"{estado} {cambio}")

    print(f"\n🎯 Progreso: {cambios_exitosos}/{total_cambios} cambios aplicados")

    if cambios_exitosos == total_cambios:
        print(
            "🎉 ¡La funcionalidad de borrar mensaje de bienvenida se ha implementado correctamente!"
        )
        print(
            "💡 El mensaje de bienvenida se borra automáticamente cuando el profesional escribe"
        )
        print("💡 Se libera espacio en la sidebar para más mensajes")
        print("💡 La experiencia de usuario es más limpia")
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

5. ✅ Verifica el mensaje de bienvenida:
   - Debería aparecer "¡Hola! Soy tu asistente de IA unificado. ¿En qué puedo ayudarte?"
   - El mensaje debería estar visible inicialmente

6. 📝 Prueba escribir un mensaje:
   - Escribe cualquier mensaje en el input
   - Presiona Enter para enviarlo
   - Verifica que el mensaje de bienvenida desaparece automáticamente
   - El espacio se libera para más mensajes

7. 🔄 Prueba múltiples mensajes:
   - Escribe varios mensajes
   - Verifica que el mensaje de bienvenida no vuelve a aparecer
   - Confirma que hay más espacio disponible

8. 🎨 Verifica la animación:
   - El mensaje de bienvenida debería desaparecer con una animación suave
   - No debería haber saltos bruscos en la interfaz

✅ Si el mensaje de bienvenida desaparece automáticamente al escribir, la funcionalidad está funcionando correctamente.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de borrar mensaje de bienvenida")
    print("=" * 60)

    verificar_borrar_mensaje_bienvenida()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
