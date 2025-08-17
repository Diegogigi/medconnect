#!/usr/bin/env python3
"""
Script de prueba para verificar que los cambios de ancho de la sidebar se han aplicado correctamente
"""

import os
import re


def verificar_cambios_ancho():
    """Verifica que los cambios de ancho en la sidebar se hayan aplicado correctamente"""

    print("🔍 Verificando cambios de ancho en la sidebar...")

    # Archivo a verificar
    archivo = "templates/professional.html"

    cambios_verificados = {
        "sidebar_container_width": False,
        "sidebar_container_min_width": False,
        "sidebar_container_max_width": False,
        "chat_messages_width": False,
        "messages_container_width": False,
        "message_bubble_width": False,
        "message_text_width": False,
        "copilot_chat_width": False,
        "panel_content_width": False,
    }

    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Verificar cambios en sidebar-container
    if re.search(r"\.sidebar-container\s*{[^}]*width:\s*50%", contenido):
        cambios_verificados["sidebar_container_width"] = True
        print("✅ sidebar-container width: 50% aplicado")

    if re.search(r"\.sidebar-container\s*{[^}]*min-width:\s*400px", contenido):
        cambios_verificados["sidebar_container_min_width"] = True
        print("✅ sidebar-container min-width: 400px aplicado")

    if re.search(r"\.sidebar-container\s*{[^}]*max-width:\s*70%", contenido):
        cambios_verificados["sidebar_container_max_width"] = True
        print("✅ sidebar-container max-width: 70% aplicado")

    # Verificar cambios en chat-messages-elegant
    if re.search(r"\.chat-messages-elegant\s*{[^}]*width:\s*100%", contenido):
        cambios_verificados["chat_messages_width"] = True
        print("✅ chat-messages-elegant width: 100% aplicado")

    # Verificar cambios en messages-container
    if re.search(r"\.messages-container\s*{[^}]*width:\s*100%", contenido):
        cambios_verificados["messages_container_width"] = True
        print("✅ messages-container width: 100% aplicado")

    # Verificar cambios en message-bubble
    if re.search(r"\.message-bubble\s*{[^}]*width:\s*100%", contenido):
        cambios_verificados["message_bubble_width"] = True
        print("✅ message-bubble width: 100% aplicado")

    # Verificar cambios en message-text
    if re.search(r"\.message-text\s*{[^}]*width:\s*100%", contenido):
        cambios_verificados["message_text_width"] = True
        print("✅ message-text width: 100% aplicado")

    # Verificar cambios en copilot-chat-elegant
    if re.search(r"\.copilot-chat-elegant\s*{[^}]*width:\s*100%", contenido):
        cambios_verificados["copilot_chat_width"] = True
        print("✅ copilot-chat-elegant width: 100% aplicado")

    # Verificar cambios en panel-content
    if re.search(r"\.panel-content\s*{[^}]*width:\s*100%", contenido):
        cambios_verificados["panel_content_width"] = True
        print("✅ panel-content width: 100% aplicado")

    # Resumen de verificación
    print("\n📊 Resumen de verificación:")
    total_cambios = len(cambios_verificados)
    cambios_exitosos = sum(cambios_verificados.values())

    for cambio, verificado in cambios_verificados.items():
        estado = "✅" if verificado else "❌"
        print(f"{estado} {cambio}")

    print(f"\n🎯 Progreso: {cambios_exitosos}/{total_cambios} cambios aplicados")

    if cambios_exitosos == total_cambios:
        print("🎉 ¡Todos los cambios de ancho se han aplicado correctamente!")
        print("💡 La sidebar ahora es más ancha y aprovecha mejor el espacio")
        print("💡 Los mensajes tienen más espacio para mostrarse")
    else:
        print("⚠️ Algunos cambios de ancho no se han aplicado completamente")
        print("💡 Revisa los archivos manualmente si es necesario")


def generar_instrucciones_verificacion():
    """Genera instrucciones para verificar los cambios manualmente"""

    instrucciones = """
🔍 INSTRUCCIONES PARA VERIFICAR MANUALMENTE:

1. 📱 Abre la aplicación en el navegador
2. 🔍 Ve a la página del profesional
3. 📋 Abre la sidebar (botón en la esquina superior derecha)
4. 📏 Verifica el ancho de la sidebar:
   - La sidebar debería ser más ancha (50% del ancho de la pantalla)
   - Ancho mínimo: 400px
   - Ancho máximo: 70% de la pantalla

5. 💬 Verifica el área de chat:
   - Los mensajes deberían usar todo el ancho disponible
   - El texto no debería verse comprimido
   - Los mensajes deberían tener más espacio horizontal

6. 📝 Prueba escribir un mensaje largo:
   - Escribe un mensaje con muchas palabras
   - Verifica que el texto se ajuste al ancho disponible
   - No debería verse cortado o comprimido

7. 🔄 Prueba redimensionar la sidebar:
   - Arrastra el borde izquierdo de la sidebar
   - Verifica que se puede hacer más ancha o más estrecha
   - Los mensajes deberían ajustarse al nuevo ancho

✅ Si todo se ve como se describe, los cambios de ancho se han aplicado correctamente.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de cambios de ancho en la sidebar")
    print("=" * 60)

    verificar_cambios_ancho()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
