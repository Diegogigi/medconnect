#!/usr/bin/env python3
"""
Script de prueba para verificar que el mensaje de bienvenida se ha cambiado para usar "Tena"
en lugar de "asistente de IA unificado"
"""

import os
import re


def verificar_mensaje_bienvenida_tena():
    """Verifica que el mensaje de bienvenida usa 'Tena' en lugar de 'asistente de IA unificado'"""

    print("🔍 Verificando cambio de mensaje de bienvenida a 'Tena'...")

    archivos_verificar = [
        "templates/professional.html",
        "static/js/fix-toggle-sidebar.js",
        "static/js/professional.js",
    ]

    cambios_verificados = {
        "html_mensaje_principal": False,
        "js_fix_toggle_sidebar": False,
        "js_limpiar_chat_elegant": False,
        "js_actualizar_mensaje_bienvenida": False,
        "js_limpiar_chat_copilot": False,
        "js_limpiar_chat_sidebar": False,
    }

    # Verificar templates/professional.html
    if os.path.exists("templates/professional.html"):
        with open("templates/professional.html", "r", encoding="utf-8") as f:
            contenido = f.read()

        if re.search(
            r"¡Hola.*Soy Tena, tu asistente IA\. ¿En qué puedo ayudarte\?", contenido
        ):
            cambios_verificados["html_mensaje_principal"] = True
            print("✅ HTML: mensaje principal cambiado a 'Soy Tena, tu asistente IA'")

    # Verificar static/js/fix-toggle-sidebar.js
    if os.path.exists("static/js/fix-toggle-sidebar.js"):
        with open("static/js/fix-toggle-sidebar.js", "r", encoding="utf-8") as f:
            contenido = f.read()

        if re.search(
            r"¡Hola! Soy Tena, tu asistente IA\. ¿En qué puedo ayudarte\?", contenido
        ):
            cambios_verificados["js_fix_toggle_sidebar"] = True
            print(
                "✅ fix-toggle-sidebar.js: mensaje cambiado a 'Soy Tena, tu asistente IA'"
            )

    # Verificar static/js/professional.js
    if os.path.exists("static/js/professional.js"):
        with open("static/js/professional.js", "r", encoding="utf-8") as f:
            contenido = f.read()

        # Verificar limpiarChatElegant
        if re.search(
            r"¡Hola \$\{nombreUsuario\}! Soy Tena, tu asistente IA\. ¿En qué puedo ayudarte\?",
            contenido,
        ):
            cambios_verificados["js_limpiar_chat_elegant"] = True
            print(
                "✅ professional.js: limpiarChatElegant cambiado a 'Soy Tena, tu asistente IA'"
            )

        # Verificar actualizarMensajeBienvenida
        if re.search(r"¡Hola \$\{nombre\}! Soy Tena, tu asistente IA\.", contenido):
            cambios_verificados["js_actualizar_mensaje_bienvenida"] = True
            print(
                "✅ professional.js: actualizarMensajeBienvenida cambiado a 'Soy Tena, tu asistente IA'"
            )

        # Verificar limpiarChatCopilot
        if re.search(
            r"Hola, soy Tena, tu asistente IA\. Estoy listo para ayudarte\.", contenido
        ):
            cambios_verificados["js_limpiar_chat_copilot"] = True
            print(
                "✅ professional.js: limpiarChatCopilot cambiado a 'Soy Tena, tu asistente IA'"
            )

        # Verificar limpiarChatSidebar
        if re.search(
            r"¡Hola! Soy Tena, tu asistente IA\. Estoy aquí para ayudarte", contenido
        ):
            cambios_verificados["js_limpiar_chat_sidebar"] = True
            print(
                "✅ professional.js: limpiarChatSidebar cambiado a 'Soy Tena, tu asistente IA'"
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
            "🎉 ¡El cambio de mensaje de bienvenida a 'Tena' se ha implementado correctamente!"
        )
        print("💡 Todos los mensajes de bienvenida ahora usan 'Tena, tu asistente IA'")
        print("💡 El nombre del usuario se incluye correctamente en el saludo")
        print("💡 La experiencia es más personalizada y amigable")
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
   - Debería aparecer: "¡Hola [Nombre]! Soy Tena, tu asistente IA. ¿En qué puedo ayudarte?"
   - El nombre del usuario debería aparecer en lugar de "Profesional"
   - El mensaje debería usar "Tena" en lugar de "asistente de IA unificado"

6. 📝 Prueba diferentes escenarios:
   - Si el usuario está logueado, debería mostrar su nombre real
   - Si no hay usuario, debería mostrar "Profesional"
   - El mensaje debería ser consistente en todos los lugares

7. 🔄 Prueba limpiar el chat:
   - Usa la función de limpiar chat
   - Verifica que el mensaje de bienvenida vuelve con el formato correcto
   - Confirma que usa "Tena" en todos los casos

8. 🎨 Verifica la consistencia:
   - Todos los mensajes de bienvenida usan "Tena, tu asistente IA"
   - El nombre del usuario se incluye correctamente
   - No hay referencias a "asistente de IA unificado" o "asistente de IA para análisis clínico"

✅ Si el mensaje de bienvenida usa "Tena, tu asistente IA" y incluye el nombre del usuario, la funcionalidad está funcionando correctamente.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de cambio de mensaje de bienvenida a 'Tena'")
    print("=" * 60)

    verificar_mensaje_bienvenida_tena()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
