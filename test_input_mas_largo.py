#!/usr/bin/env python3
"""
Script de prueba para verificar que el input de mensajes se ha hecho más largo
"""

import os
import re


def verificar_input_mas_largo():
    """Verifica que el input de mensajes se ha hecho más largo"""

    print("🔍 Verificando que el input de mensajes se ha hecho más largo...")

    # Archivo a verificar
    archivo = "templates/professional.html"

    cambios_verificados = {
        "input_height_aumentado": False,
        "input_width_100": False,
        "input_min_width": False,
        "input_padding_aumentado": False,
        "input_font_size_aumentado": False,
        "contenedor_width_100": False,
        "placeholder_font_size": False,
    }

    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Verificar altura del input aumentada
    if re.search(r"height:\s*40px", contenido):
        cambios_verificados["input_height_aumentado"] = True
        print("✅ Altura del input aumentada a 40px")

    # Verificar ancho del input al 100%
    if re.search(r"width:\s*100%", contenido):
        cambios_verificados["input_width_100"] = True
        print("✅ Ancho del input establecido al 100%")

    # Verificar ancho mínimo del input
    if re.search(r"min-width:\s*280px", contenido):
        cambios_verificados["input_min_width"] = True
        print("✅ Ancho mínimo del input establecido en 280px")

    # Verificar padding aumentado
    if re.search(r"padding:\s*8px 12px", contenido):
        cambios_verificados["input_padding_aumentado"] = True
        print("✅ Padding del input aumentado")

    # Verificar tamaño de fuente aumentado
    if re.search(r"font-size:\s*0\.9rem", contenido):
        cambios_verificados["input_font_size_aumentado"] = True
        print("✅ Tamaño de fuente del input aumentado")

    # Verificar contenedor con ancho 100%
    if re.search(r'style="width:\s*100%"', contenido):
        cambios_verificados["contenedor_width_100"] = True
        print("✅ Contenedor del input con ancho 100%")

    # Verificar tamaño de fuente del placeholder
    if re.search(r"font-size:\s*0\.85rem", contenido):
        cambios_verificados["placeholder_font_size"] = True
        print("✅ Tamaño de fuente del placeholder ajustado")

    # Resumen de verificación
    print("\n📊 Resumen de verificación:")
    total_cambios = len(cambios_verificados)
    cambios_exitosos = sum(cambios_verificados.values())

    for cambio, verificado in cambios_verificados.items():
        estado = "✅" if verificado else "❌"
        print(f"{estado} {cambio}")

    print(f"\n🎯 Progreso: {cambios_exitosos}/{total_cambios} cambios aplicados")

    if cambios_exitosos == total_cambios:
        print("🎉 ¡El input de mensajes se ha hecho más largo!")
        print("💡 Ahora tiene mejor visibilidad del texto")
        print("💡 Usa todo el ancho disponible")
        print("💡 Es más cómodo para escribir mensajes largos")
    else:
        print("⚠️ Algunos cambios no se han aplicado completamente")
        print("💡 Revisa el archivo manualmente si es necesario")


def generar_instrucciones_verificacion():
    """Genera instrucciones para verificar los cambios manualmente"""

    instrucciones = """
🔍 INSTRUCCIONES PARA VERIFICAR MANUALMENTE:

1. 📱 Abre la aplicación en el navegador
2. 🔄 Limpia el cache del navegador (Ctrl + Shift + R)
3. 🔍 Ve a la página del profesional
4. 📋 Abre la sidebar (botón en la esquina superior derecha)

5. ✅ Verifica que el input es más largo:
   - El área de entrada de mensajes es más alta
   - Ocupa todo el ancho disponible
   - El texto se ve más claro y legible
   - Es más cómodo escribir mensajes largos

6. 📝 Prueba escribir un mensaje largo:
   - Escribe un mensaje con muchas palabras
   - Verifica que se ve bien dentro del input
   - Confirma que no se corta o se ve comprimido

7. 🎨 Verifica el diseño:
   - El input tiene un tamaño apropiado
   - El placeholder es legible
   - El focus funciona correctamente
   - El diseño es consistente

✅ Si el input se ve más largo y cómodo para escribir, los cambios se han aplicado correctamente.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de input más largo")
    print("=" * 60)

    verificar_input_mas_largo()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
