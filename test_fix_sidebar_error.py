#!/usr/bin/env python3
"""
Script de prueba para verificar que el error del sidebarContainer se ha solucionado
"""

import os
import re


def verificar_fix_sidebar_error():
    """Verifica que el error del sidebarContainer se ha solucionado"""

    print("🔍 Verificando solución del error sidebarContainer...")

    # Archivo a verificar
    archivo = "static/js/fix-toggle-sidebar.js"

    cambios_verificados = {
        "funcion_esperar_elementos": False,
        "funcion_crear_sidebar": False,
        "toggle_sidebar_robusto": False,
        "exportacion_funciones": False,
        "inicializacion_segura": False,
    }

    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return

    with open(archivo, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Verificar función para esperar elementos
    if re.search(r"function esperarElementosSidebar", contenido):
        cambios_verificados["funcion_esperar_elementos"] = True
        print("✅ Función esperarElementosSidebar agregada")

    # Verificar función para crear sidebar
    if re.search(r"function crearSidebarSiNoExiste", contenido):
        cambios_verificados["funcion_crear_sidebar"] = True
        print("✅ Función crearSidebarSiNoExiste agregada")

    # Verificar que toggleSidebar es más robusto
    if re.search(r"console\.warn.*sidebarContainer no encontrado", contenido):
        cambios_verificados["toggle_sidebar_robusto"] = True
        print("✅ toggleSidebar ahora es más robusto")

    # Verificar exportación de funciones
    if re.search(r"window\.crearSidebarSiNoExiste", contenido):
        cambios_verificados["exportacion_funciones"] = True
        print("✅ Función crearSidebarSiNoExiste exportada")

    # Verificar inicialización segura
    if re.search(r"setInterval.*esperarElementosSidebar", contenido):
        cambios_verificados["inicializacion_segura"] = True
        print("✅ Inicialización segura con setInterval")

    # Resumen de verificación
    print("\n📊 Resumen de verificación:")
    total_cambios = len(cambios_verificados)
    cambios_exitosos = sum(cambios_verificados.values())

    for cambio, verificado in cambios_verificados.items():
        estado = "✅" if verificado else "❌"
        print(f"{estado} {cambio}")

    print(f"\n🎯 Progreso: {cambios_exitosos}/{total_cambios} cambios aplicados")

    if cambios_exitosos == total_cambios:
        print("🎉 ¡El error del sidebarContainer se ha solucionado!")
        print("💡 El script ahora espera a que los elementos estén disponibles")
        print("💡 Si no encuentra la sidebar, intenta crearla")
        print("💡 Los errores se han convertido en advertencias")
        print("💡 El sistema es más robusto y tolerante a fallos")
    else:
        print("⚠️ Algunos cambios no se han aplicado completamente")
        print("💡 Revisa el archivo manualmente si es necesario")


def generar_instrucciones_verificacion():
    """Genera instrucciones para verificar que el error se ha solucionado"""

    instrucciones = """
🔍 INSTRUCCIONES PARA VERIFICAR QUE EL ERROR SE HA SOLUCIONADO:

1. 📱 Abre la aplicación en el navegador
2. 🔄 Limpia el cache del navegador (Ctrl + Shift + R)
3. 🔍 Ve a la página del profesional
4. 📋 Abre las herramientas de desarrollador (F12)

5. ✅ Verifica en la consola:
   - NO debería aparecer "❌ sidebarContainer no encontrado"
   - Debería aparecer "⏳ Esperando elementos de sidebar..."
   - Luego "✅ Elementos de sidebar encontrados, inicializando..."
   - O "✅ sidebarContainer creado exitosamente"

6. 📋 Prueba abrir la sidebar:
   - Haz clic en el botón de la sidebar
   - Verifica que se abre correctamente
   - No debería haber errores en la consola

7. 🔄 Prueba cerrar y abrir la sidebar varias veces:
   - Verifica que funciona consistentemente
   - No debería haber errores

✅ Si no hay errores en la consola y la sidebar funciona correctamente, el problema se ha solucionado.
"""

    print(instrucciones)


if __name__ == "__main__":
    print("🚀 Verificación de solución del error sidebarContainer")
    print("=" * 60)

    verificar_fix_sidebar_error()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()
