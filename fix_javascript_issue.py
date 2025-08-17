#!/usr/bin/env python3
"""
Script para corregir el problema específico del JavaScript mostrándose en la interfaz
"""


def fix_javascript_issue():
    """Corrige el problema del JavaScript mostrándose en la interfaz"""

    template_path = "templates/professional.html"

    # Leer el archivo
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("🔍 Analizando el problema del JavaScript...")

    # Verificar si hay JavaScript suelto (fuera de etiquetas script)
    lines = content.split("\n")
    javascript_outside_script = []

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("//") and not line.strip().startswith("// "):
            # Buscar si esta línea está dentro de un bloque script
            script_start = content.find("<script>", 0, content.find(line))
            script_end = content.find("</script>", 0, content.find(line))

            if script_start == -1 or script_end == -1 or script_start > script_end:
                javascript_outside_script.append((i, line))

    if javascript_outside_script:
        print(
            f"❌ Se encontraron {len(javascript_outside_script)} líneas de JavaScript fuera de etiquetas script:"
        )
        for line_num, line in javascript_outside_script:
            print(f"   Línea {line_num}: {line.strip()}")

        # Corregir el problema
        print("🔧 Corrigiendo el problema...")

        # Buscar y reemplazar el JavaScript mal formateado
        # Buscar el patrón específico que está causando el problema
        problematic_patterns = [
            "// Funciones de utilidad para la IA",
            "window.showAINotification",
            "window.updateAIStatus",
            "window.showAIProgress",
            "window.hideAIProgress",
        ]

        # Verificar si el JavaScript está correctamente dentro de etiquetas script
        script_start = content.find("<script>")
        script_end = content.find("</script>")

        if script_start != -1 and script_end != -1:
            script_content = content[script_start:script_end]

            # Verificar si todas las funciones están dentro del script
            all_functions_in_script = all(
                pattern in script_content for pattern in problematic_patterns
            )

            if all_functions_in_script:
                print(
                    "✅ El JavaScript está correctamente dentro de etiquetas <script>"
                )
                print("🔍 El problema puede estar en el navegador o en el CSS")

                # Verificar si hay algún problema con el CSS
                css_link = (
                    '<link rel="stylesheet" href="/static/css/enhanced-sidebar-ai.css">'
                )
                if css_link in content:
                    print("✅ CSS de la sidebar está incluido")
                else:
                    print("❌ CSS de la sidebar no está incluido")
                    # Agregar el CSS
                    content = content.replace(
                        '<link rel="stylesheet" href="/static/css/patient-styles.css">',
                        '<link rel="stylesheet" href="/static/css/patient-styles.css">\n    <link rel="stylesheet" href="/static/css/enhanced-sidebar-ai.css">',
                    )

                # Verificar si el JavaScript está siendo cargado correctamente
                js_script = '<script src="/static/js/enhanced-sidebar-ai.js"></script>'
                if js_script in content:
                    print("✅ JavaScript de la sidebar está incluido")
                else:
                    print("❌ JavaScript de la sidebar no está incluido")

                # Escribir el archivo corregido
                with open(template_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print("✅ Archivo corregido")
                return True
            else:
                print("❌ Algunas funciones no están dentro de etiquetas script")
                return False
        else:
            print("❌ No se encontraron etiquetas script")
            return False
    else:
        print("✅ No se encontró JavaScript fuera de etiquetas script")
        print("🔍 El problema puede estar en el navegador")
        return True


def create_debug_script():
    """Crea un script de debug para verificar el problema"""

    debug_script = """
// Script de debug para verificar el problema del JavaScript
console.log('🔍 Debug: Verificando JavaScript de la sidebar...');

// Verificar si las funciones están disponibles
console.log('showAINotification disponible:', typeof window.showAINotification);
console.log('updateAIStatus disponible:', typeof window.updateAIStatus);
console.log('showAIProgress disponible:', typeof window.showAIProgress);
console.log('hideAIProgress disponible:', typeof window.hideAIProgress);

// Verificar si EnhancedSidebarAI está disponible
console.log('EnhancedSidebarAI disponible:', typeof window.enhancedAI);

// Verificar elementos del DOM
console.log('aiStatusDot:', document.getElementById('aiStatusDot'));
console.log('aiStatusText:', document.getElementById('aiStatusText'));
console.log('aiProgress:', document.getElementById('aiProgress'));

// Probar una función
if (typeof window.showAINotification === 'function') {
    console.log('✅ Función showAINotification funciona');
    window.showAINotification('Prueba de notificación', 'success');
} else {
    console.log('❌ Función showAINotification no está disponible');
}

console.log('🔍 Debug completado');
"""

    with open("static/js/debug-sidebar.js", "w", encoding="utf-8") as f:
        f.write(debug_script)

    print("✅ Script de debug creado: static/js/debug-sidebar.js")


def main():
    """Función principal"""
    print("🔧 Corrigiendo problema del JavaScript en la interfaz...")

    if fix_javascript_issue():
        print("\n✅ Problema corregido o no encontrado")

        # Crear script de debug
        create_debug_script()

        print("\n📋 Instrucciones para debug:")
        print("1. Abre la consola del navegador (F12)")
        print("2. Recarga la página")
        print("3. Busca mensajes de error relacionados con JavaScript")
        print(
            "4. Si ves código JavaScript en la página, puede ser un problema de caché"
        )
        print("5. Intenta Ctrl+F5 para recarga forzada")

        print("\n🔧 Si el problema persiste:")
        print("- Limpia la caché del navegador")
        print("- Verifica que no haya errores en la consola")
        print("- Asegúrate de que el servidor esté ejecutándose")

    else:
        print("\n❌ No se pudo corregir el problema")


if __name__ == "__main__":
    main()
