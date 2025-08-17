#!/usr/bin/env python3
"""
Script de prueba para verificar que las burbujas de conversación han sido eliminadas de la sidebar
"""

import os
import re


def verificar_cambios_sidebar():
    """Verifica que los cambios en la sidebar se hayan aplicado correctamente"""

    print("🔍 Verificando eliminación de burbujas de conversación en la sidebar...")

    # Archivos a verificar
    archivos = ["templates/professional.html", "static/js/professional.js"]

    cambios_verificados = {
        "css_message_bubble": False,
        "css_message_icon": False,
        "css_messages_container": False,
        "css_message_text": False,
        "css_message_time": False,
        "html_welcome_message": False,
        "js_agregar_mensaje": False,
        "js_limpiar_chat": False,
    }

    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"❌ Archivo no encontrado: {archivo}")
            continue

        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()

        if archivo == "templates/professional.html":
            # Verificar cambios en CSS
            if re.search(r"\.message-bubble\s*{[^}]*display:\s*block", contenido):
                cambios_verificados["css_message_bubble"] = True
                print("✅ CSS message-bubble modificado correctamente")

            if re.search(r"\.message-icon\s*{[^}]*display:\s*none", contenido):
                cambios_verificados["css_message_icon"] = True
                print("✅ CSS message-icon ocultado correctamente")

            if re.search(r"\.messages-container\s*{[^}]*gap:\s*16px", contenido):
                cambios_verificados["css_messages_container"] = True
                print("✅ CSS messages-container con espaciado aumentado")

            if re.search(r"\.message-text p\s*{[^}]*font-size:\s*0\.95rem", contenido):
                cambios_verificados["css_message_text"] = True
                print("✅ CSS message-text con tamaño aumentado")

            if re.search(r"\.message-time\s*{[^}]*font-size:\s*0\.75rem", contenido):
                cambios_verificados["css_message_time"] = True
                print("✅ CSS message-time con tamaño aumentado")

            # Verificar HTML del mensaje de bienvenida
            if re.search(
                r'<div class="message-bubble">\s*<div class="message-text">', contenido
            ):
                cambios_verificados["html_welcome_message"] = True
                print("✅ HTML del mensaje de bienvenida sin icono")

        elif archivo == "static/js/professional.js":
            # Verificar función agregarMensajeElegant
            if re.search(
                r'<div class="message-bubble">\s*<div class="message-text copilot-markdown">',
                contenido,
            ):
                cambios_verificados["js_agregar_mensaje"] = True
                print("✅ Función agregarMensajeElegant sin icono")

            # Verificar función limpiarChatElegant
            if re.search(
                r'<div class="message-bubble">\s*<div class="message-text">\s*<p>¡Hola',
                contenido,
            ):
                cambios_verificados["js_limpiar_chat"] = True
                print("✅ Función limpiarChatElegant sin icono")

    # Resumen de verificación
    print("\n📊 Resumen de verificación:")
    total_cambios = len(cambios_verificados)
    cambios_exitosos = sum(cambios_verificados.values())

    for cambio, verificado in cambios_verificados.items():
        estado = "✅" if verificado else "❌"
        print(f"{estado} {cambio}")

    print(f"\n🎯 Progreso: {cambios_exitosos}/{total_cambios} cambios aplicados")

    if cambios_exitosos == total_cambios:
        print("🎉 ¡Todos los cambios se han aplicado correctamente!")
        print("💡 Las burbujas de conversación han sido eliminadas de la sidebar")
        print("💡 Los mensajes ahora son menos compactos y más legibles")
    else:
        print("⚠️ Algunos cambios no se han aplicado completamente")
        print("💡 Revisa los archivos manualmente si es necesario")


def generar_instrucciones_verificacion():
    """Genera instrucciones para verificar los cambios manualmente"""

    instrucciones = """
🔍 INSTRUCCIONES PARA VERIFICAR MANUALMENTE:

1. 📱 Abre la aplicación en el navegador
2. 🔍 Ve a la página del profesional
3. 📋 Abre la sidebar (botón en la esquina superior derecha)
4. 💬 Busca el área de chat en la sidebar
5. ✅ Verifica que:
   - Los mensajes NO tienen burbujas redondeadas
   - Los mensajes NO tienen iconos circulares
   - Los mensajes están separados por líneas divisorias
   - El texto es más grande y legible
   - El espaciado entre mensajes es mayor

6. 🎨 Verifica el diseño:
   - Los mensajes tienen un fondo ligeramente gris
   - El texto es negro sobre fondo claro
   - Los timestamps son visibles en gris
   - No hay sombras ni bordes redondeados

7. 📝 Prueba agregar un nuevo mensaje:
   - Escribe en el campo de entrada
   - Presiona Enter
   - Verifica que el nuevo mensaje aparece sin burbujas

✅ Si todo se ve como se describe, los cambios se han aplicado correctamente.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de eliminación de burbujas de conversación")
    print("=" * 60)

    verificar_cambios_sidebar()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
