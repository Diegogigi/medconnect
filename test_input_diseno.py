#!/usr/bin/env python3
"""
Script de prueba para verificar que los cambios del diseño del input de mensajes se han aplicado correctamente
"""

import os
import re


def verificar_cambios_input():
    """Verifica que los cambios del diseño del input se hayan aplicado correctamente"""

    print("🔍 Verificando cambios del diseño del input de mensajes...")

    # Archivo a verificar
    archivo = "templates/professional.html"

    cambios_verificados = {
        "auto_mode_indicator_padding": False,
        "auto_mode_indicator_margin": False,
        "auto_mode_indicator_border_radius": False,
        "auto_mode_text_size": False,
        "copilot_quick_input_styles": False,
        "copilot_quick_input_focus": False,
        "copilot_quick_input_placeholder": False,
        "input_container_margin": False,
        "input_placeholder_text": False,
    }

    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Verificar cambios en auto-mode-indicator
    if re.search(r"\.auto-mode-indicator\s*{[^}]*padding:\s*8px 12px", contenido):
        cambios_verificados["auto_mode_indicator_padding"] = True
        print("✅ auto-mode-indicator padding reducido")

    if re.search(r"\.auto-mode-indicator\s*{[^}]*margin:\s*12px 0", contenido):
        cambios_verificados["auto_mode_indicator_margin"] = True
        print("✅ auto-mode-indicator margin reducido")

    if re.search(r"\.auto-mode-indicator\s*{[^}]*border-radius:\s*6px", contenido):
        cambios_verificados["auto_mode_indicator_border_radius"] = True
        print("✅ auto-mode-indicator border-radius reducido")

    # Verificar cambios en auto-mode-text
    if re.search(r"\.auto-mode-text\s*{[^}]*font-size:\s*0\.8rem", contenido):
        cambios_verificados["auto_mode_text_size"] = True
        print("✅ auto-mode-text font-size reducido")

    # Verificar estilos del input
    if re.search(r"#copilotQuickInput\s*{[^}]*height:\s*32px", contenido):
        cambios_verificados["copilot_quick_input_styles"] = True
        print("✅ copilotQuickInput height reducido")

    if re.search(
        r"#copilotQuickInput:focus\s*{[^}]*border-color:\s*#667eea", contenido
    ):
        cambios_verificados["copilot_quick_input_focus"] = True
        print("✅ copilotQuickInput focus styles aplicados")

    if re.search(
        r"#copilotQuickInput::placeholder\s*{[^}]*font-size:\s*0\.8rem", contenido
    ):
        cambios_verificados["copilot_quick_input_placeholder"] = True
        print("✅ copilotQuickInput placeholder font-size reducido")

    # Verificar HTML del input
    if re.search(r'<div class="mt-1">', contenido):
        cambios_verificados["input_container_margin"] = True
        print("✅ Input container margin reducido")

    if re.search(r'placeholder="Escribe tu mensaje aquí\.\.\."', contenido):
        cambios_verificados["input_placeholder_text"] = True
        print("✅ Input placeholder text actualizado")

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
            "🎉 ¡Todos los cambios del diseño del input se han aplicado correctamente!"
        )
        print("💡 El área de entrada de mensajes ahora es más pequeña y sencilla")
        print("💡 El diseño es más compacto y minimalista")
    else:
        print("⚠️ Algunos cambios del diseño no se han aplicado completamente")
        print("💡 Revisa los archivos manualmente si es necesario")


def generar_instrucciones_verificacion():
    """Genera instrucciones para verificar los cambios manualmente"""

    instrucciones = """
🔍 INSTRUCCIONES PARA VERIFICAR MANUALMENTE:

1. 📱 Abre la aplicación en el navegador
2. 🔍 Ve a la página del profesional
3. 📋 Abre la sidebar (botón en la esquina superior derecha)
4. 💬 Busca el área de entrada de mensajes en la parte inferior de la sidebar

5. ✅ Verifica que el diseño es más pequeño y sencillo:
   - El rectángulo del input es más pequeño (altura reducida)
   - El padding del contenedor es menor
   - El texto "IA Unificada" es más pequeño
   - El espaciado general es más compacto

6. 🎨 Verifica los detalles del diseño:
   - El input tiene bordes más sutiles
   - El placeholder dice "Escribe tu mensaje aquí..."
   - El input se enfoca con un borde azul suave
   - No hay sombras excesivas

7. 📝 Prueba el input:
   - Escribe un mensaje
   - Presiona Enter para enviar
   - Verifica que funciona correctamente
   - El input se limpia después de enviar

✅ Si todo se ve más compacto y sencillo, los cambios se han aplicado correctamente.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de cambios del diseño del input de mensajes")
    print("=" * 60)

    verificar_cambios_input()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
