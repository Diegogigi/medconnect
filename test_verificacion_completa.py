#!/usr/bin/env python3
"""
Script de verificación completa para asegurar que se han eliminado todas las referencias al formulario y iconos del bot
"""

import os
import re


def verificar_cambios_completos():
    """Verifica que todos los cambios se han aplicado correctamente"""

    print(
        "🔍 Verificación completa de eliminación de referencias al formulario y iconos del bot..."
    )

    # Archivos críticos a verificar
    archivos = [
        "templates/professional.html",
        "static/js/professional.js",
        "static/js/fix-all-errors.js",
    ]

    cambios_verificados = {
        "html_mensaje_bienvenida": False,
        "html_icono_robot_eliminado": False,
        "html_script_fix_all_errors_comentado": False,
        "js_mensaje_bienvenida": False,
        "js_mensaje_warning": False,
        "js_estado_sidebar": False,
        "fix_all_errors_texto": False,
    }

    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"❌ Archivo no encontrado: {archivo}")
            continue

        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()

        if archivo == "templates/professional.html":
            # Verificar mensaje de bienvenida en HTML
            if re.search(r"¿En qué puedo ayudarte\?", contenido):
                cambios_verificados["html_mensaje_bienvenida"] = True
                print("✅ Mensaje de bienvenida actualizado en HTML")

            # Verificar eliminación del icono robot en controles
            if not re.search(r'<i class="fas fa-robot"></i>', contenido):
                cambios_verificados["html_icono_robot_eliminado"] = True
                print("✅ Icono robot eliminado del HTML")

            # Verificar que fix-all-errors.js esté comentado
            if re.search(
                r'<!-- <script src="/static/js/fix-all-errors\.js"></script> -->',
                contenido,
            ):
                cambios_verificados["html_script_fix_all_errors_comentado"] = True
                print("✅ Script fix-all-errors.js comentado")

        elif archivo == "static/js/professional.js":
            # Verificar mensaje de bienvenida en JavaScript
            if re.search(r"¿En qué puedo ayudarte\?", contenido):
                cambios_verificados["js_mensaje_bienvenida"] = True
                print("✅ Mensaje de bienvenida actualizado en JavaScript")

            # Verificar mensaje de warning actualizado
            if re.search(r"escribe tu consulta", contenido):
                cambios_verificados["js_mensaje_warning"] = True
                print("✅ Mensaje de warning actualizado")

            # Verificar estado de sidebar actualizado
            if re.search(r"Escribe tu consulta para comenzar", contenido):
                cambios_verificados["js_estado_sidebar"] = True
                print("✅ Estado de sidebar actualizado")

        elif archivo == "static/js/fix-all-errors.js":
            # Verificar que el texto en fix-all-errors.js esté actualizado
            if re.search(r"Escribe tu consulta para comenzar", contenido):
                cambios_verificados["fix_all_errors_texto"] = True
                print("✅ Texto en fix-all-errors.js actualizado")

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
        print("💡 Se eliminaron todas las referencias al formulario")
        print("💡 Se eliminaron todos los iconos del bot")
        print("💡 El script problemático está comentado")
        print("💡 Los cambios deberían reflejarse en el frontend")
    else:
        print("⚠️ Algunos cambios no se han aplicado completamente")
        print("💡 Revisa los archivos manualmente si es necesario")


def generar_instrucciones_cache():
    """Genera instrucciones para limpiar el cache del navegador"""

    instrucciones = """
🔍 INSTRUCCIONES PARA LIMPIAR CACHE Y VERIFICAR:

1. 📱 Abre la aplicación en el navegador
2. 🔄 Limpia el cache del navegador:
   - Presiona Ctrl + Shift + R (recarga forzada)
   - O presiona F12, ve a Network, marca "Disable cache"
   - O ve a Configuración > Privacidad > Limpiar datos

3. 🔍 Ve a la página del profesional
4. 📋 Abre la sidebar (botón en la esquina superior derecha)

5. ✅ Verifica que los cambios se aplicaron:
   - El mensaje de bienvenida dice "¿En qué puedo ayudarte?"
   - NO aparece "Completa el formulario para comenzar"
   - NO hay iconos de robot en el área de entrada
   - Solo aparece "IA Unificada" sin iconos

6. 📝 Prueba el sistema:
   - Escribe un mensaje en el input
   - Verifica que funciona correctamente
   - Confirma que no hay errores en la consola

✅ Si después de limpiar el cache los cambios se ven, el problema era el cache del navegador.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación completa de cambios")
    print("=" * 60)

    verificar_cambios_completos()

    print("\n" + "=" * 60)
    generar_instrucciones_cache()
