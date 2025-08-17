#!/usr/bin/env python3
"""
Script de prueba para verificar que se han eliminado las referencias al formulario y el icono del bot
"""

import os
import re


def verificar_eliminaciones():
    """Verifica que se han eliminado las referencias al formulario y el icono del bot"""

    print("🔍 Verificando eliminación de referencias al formulario y icono del bot...")

    # Archivos a verificar
    archivos = ["templates/professional.html", "static/js/professional.js"]

    cambios_verificados = {
        "html_mensaje_bienvenida": False,
        "html_icono_check": False,
        "js_mensaje_bienvenida": False,
        "js_mensaje_warning": False,
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

            # Verificar eliminación del icono check-circle
            if not re.search(
                r'<i class="fas fa-check-circle text-success"></i>', contenido
            ):
                cambios_verificados["html_icono_check"] = True
                print("✅ Icono check-circle eliminado del HTML")

        elif archivo == "static/js/professional.js":
            # Verificar mensaje de bienvenida en JavaScript
            if re.search(r"¿En qué puedo ayudarte\?", contenido):
                cambios_verificados["js_mensaje_bienvenida"] = True
                print("✅ Mensaje de bienvenida actualizado en JavaScript")

            # Verificar mensaje de warning actualizado
            if re.search(r"escribe tu consulta", contenido):
                cambios_verificados["js_mensaje_warning"] = True
                print("✅ Mensaje de warning actualizado")

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
        print("💡 Se eliminaron las referencias al formulario")
        print("💡 Se eliminó el icono del bot")
        print("💡 Los mensajes ahora son más directos y simples")
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

4. ✅ Verifica que se eliminaron las referencias al formulario:
   - El mensaje de bienvenida dice "¿En qué puedo ayudarte?" en lugar de "Completa el formulario..."
   - No hay referencias a "completa el formulario" en ningún mensaje

5. ✅ Verifica que se eliminó el icono del bot:
   - En el área de entrada de mensajes no hay icono de check-circle verde
   - Solo aparece el texto "IA Unificada" sin iconos

6. 📝 Prueba el sistema:
   - Escribe un mensaje en el input
   - Verifica que los mensajes de error no mencionen "completa el formulario"
   - Confirma que todo funciona correctamente

✅ Si no ves referencias al formulario ni iconos del bot, los cambios se han aplicado correctamente.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de eliminación de referencias al formulario")
    print("=" * 60)

    verificar_eliminaciones()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
