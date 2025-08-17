#!/usr/bin/env python3
"""
Script de prueba para verificar que el nombre se ha cambiado de "IA Unificada" a "Tena Copilot"
y que los mensajes de estado se han actualizado
"""

import os
import re


def verificar_cambio_nombre_tena_copilot():
    """Verifica que el nombre se ha cambiado de 'IA Unificada' a 'Tena Copilot'"""

    print("🔍 Verificando cambio de nombre a 'Tena Copilot'...")

    archivos_verificar = [
        "templates/professional.html",
        "static/js/fix-toggle-sidebar.js",
        "static/js/force-clean-system.js",
        "static/js/unified-ai-integration.js",
        "static/js/professional.js",
    ]

    cambios_verificados = {
        "html_auto_mode_text": False,
        "html_typing_message": False,
        "js_fix_toggle_sidebar": False,
        "js_force_clean_system": False,
        "js_unified_ai_integration": False,
        "js_professional_typing": False,
        "js_mensajes_variados": False,
    }

    # Verificar templates/professional.html
    if os.path.exists("templates/professional.html"):
        with open("templates/professional.html", "r", encoding="utf-8") as f:
            contenido = f.read()

        if re.search(r'<span class="auto-mode-text">Tena Copilot</span>', contenido):
            cambios_verificados["html_auto_mode_text"] = True
            print("✅ HTML: auto-mode-text cambiado a 'Tena Copilot'")

        if re.search(r"<span>Tena Copilot está pensando\.\.\.</span>", contenido):
            cambios_verificados["html_typing_message"] = True
            print(
                "✅ HTML: mensaje de typing cambiado a 'Tena Copilot está pensando...'"
            )

    # Verificar static/js/fix-toggle-sidebar.js
    if os.path.exists("static/js/fix-toggle-sidebar.js"):
        with open("static/js/fix-toggle-sidebar.js", "r", encoding="utf-8") as f:
            contenido = f.read()

        if re.search(r"Tena Copilot", contenido):
            cambios_verificados["js_fix_toggle_sidebar"] = True
            print("✅ fix-toggle-sidebar.js: nombre cambiado a 'Tena Copilot'")

    # Verificar static/js/force-clean-system.js
    if os.path.exists("static/js/force-clean-system.js"):
        with open("static/js/force-clean-system.js", "r", encoding="utf-8") as f:
            contenido = f.read()

        if re.search(r"Tena Copilot", contenido):
            cambios_verificados["js_force_clean_system"] = True
            print("✅ force-clean-system.js: nombre cambiado a 'Tena Copilot'")

    # Verificar static/js/unified-ai-integration.js
    if os.path.exists("static/js/unified-ai-integration.js"):
        with open("static/js/unified-ai-integration.js", "r", encoding="utf-8") as f:
            contenido = f.read()

        if re.search(r"Tena Copilot lista para análisis", contenido):
            cambios_verificados["js_unified_ai_integration"] = True
            print(
                "✅ unified-ai-integration.js: mensaje cambiado a 'Tena Copilot lista para análisis'"
            )

    # Verificar static/js/professional.js
    if os.path.exists("static/js/professional.js"):
        with open("static/js/professional.js", "r", encoding="utf-8") as f:
            contenido = f.read()

        if re.search(r"Tena Copilot está pensando\.\.\.", contenido):
            cambios_verificados["js_professional_typing"] = True
            print(
                "✅ professional.js: mensaje de typing cambiado a 'Tena Copilot está pensando...'"
            )

        # Verificar mensajes variados
        mensajes_variados = [
            "Analizando tu consulta...",
            "Procesando información...",
            "Buscando la mejor respuesta...",
            "Evaluando opciones...",
            "Preparando recomendaciones...",
            "Consultando bases de datos...",
            "Sintetizando información...",
        ]

        mensajes_encontrados = 0
        for mensaje in mensajes_variados:
            if mensaje in contenido:
                mensajes_encontrados += 1

        if mensajes_encontrados >= 5:  # Al menos 5 de los 7 mensajes
            cambios_verificados["js_mensajes_variados"] = True
            print(
                f"✅ professional.js: {mensajes_encontrados}/7 mensajes variados implementados"
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
            "🎉 ¡El cambio de nombre a 'Tena Copilot' se ha implementado correctamente!"
        )
        print("💡 Todos los mensajes de estado han sido actualizados")
        print("💡 Los mensajes de typing ahora son variados y amigables")
        print("💡 La experiencia de usuario es más personalizada")
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

5. ✅ Verifica el nombre "Tena Copilot":
   - En el área del input debería aparecer "Tena Copilot" en lugar de "IA Unificada"
   - El nombre debería estar visible en la parte superior del área de chat

6. 📝 Prueba escribir un mensaje:
   - Escribe cualquier mensaje en el input
   - Presiona Enter para enviarlo
   - Verifica que aparece un mensaje de estado variado como:
     * "Tena Copilot está pensando..."
     * "Analizando tu consulta..."
     * "Procesando información..."
     * "Buscando la mejor respuesta..."
     * "Evaluando opciones..."
     * "Preparando recomendaciones..."
     * "Consultando bases de datos..."
     * "Sintetizando información..."

7. 🔄 Prueba múltiples mensajes:
   - Escribe varios mensajes
   - Verifica que los mensajes de estado cambian entre diferentes opciones
   - Confirma que todos los mensajes son amigables y profesionales

8. 🎨 Verifica la consistencia:
   - Todos los lugares donde aparecía "IA Unificada" ahora muestran "Tena Copilot"
   - Los mensajes de estado son variados y no repetitivos
   - La experiencia es más personalizada y amigable

✅ Si el nombre "Tena Copilot" aparece correctamente y los mensajes de estado son variados, la funcionalidad está funcionando correctamente.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de cambio de nombre a 'Tena Copilot'")
    print("=" * 60)

    verificar_cambio_nombre_tena_copilot()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
