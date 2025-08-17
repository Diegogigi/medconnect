#!/usr/bin/env python3
"""
Script para corregir el color del texto en la sidebar
"""


def fix_sidebar_text_color():
    """Corrige el color del texto en la sidebar"""

    print("🔧 Corrigiendo color del texto en la sidebar...")

    # Corregir CSS
    css_path = "static/css/enhanced-sidebar-ai.css"

    try:
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Asegurar que el texto sea negro
        if "color: white" in content:
            content = content.replace("color: white", "color: black")
            print("✅ Color blanco cambiado a negro en CSS")

        # Agregar reglas específicas para texto negro
        black_text_rules = """
/* Asegurar texto negro en toda la sidebar */
.sidebar-ai-container,
.sidebar-ai-container *,
.ai-analysis-section,
.ai-analysis-section *,
.ai-results,
.ai-results * {
    color: black !important;
}

/* Texto negro específico para resultados */
.ai-results h3,
.ai-results h4,
.ai-results p,
.ai-results li,
.ai-results span {
    color: black !important;
}

/* Texto negro para análisis */
.analysis-item,
.analysis-item * {
    color: black !important;
}
"""

        if "color: black !important" not in content:
            content += black_text_rules
            print("✅ Reglas de texto negro agregadas")

        with open(css_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ CSS corregido")

    except Exception as e:
        print(f"❌ Error corrigiendo CSS: {e}")
        return False

    # Corregir JavaScript si es necesario
    js_path = "static/js/simple-unified-sidebar-ai.js"

    try:
        with open(js_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Asegurar que el texto se renderice en negro
        if "style.color" in content:
            content = content.replace('style.color = "white"', 'style.color = "black"')
            print("✅ Color blanco cambiado a negro en JavaScript")

        with open(js_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ JavaScript corregido")

    except Exception as e:
        print(f"❌ Error corrigiendo JavaScript: {e}")
        return False

    return True


def verify_text_color():
    """Verifica que el texto sea negro"""

    print("🔍 Verificando color del texto...")

    try:
        # Verificar CSS
        with open("static/css/enhanced-sidebar-ai.css", "r", encoding="utf-8") as f:
            css_content = f.read()

        if "color: black !important" in css_content:
            print("✅ CSS tiene reglas de texto negro")
        else:
            print("❌ CSS no tiene reglas de texto negro")
            return False

        # Verificar JavaScript
        with open("static/js/simple-unified-sidebar-ai.js", "r", encoding="utf-8") as f:
            js_content = f.read()

        if "color: black" in js_content or 'color: "black"' in js_content:
            print("✅ JavaScript tiene texto negro")
        else:
            print("ℹ️ JavaScript no especifica color (usará CSS)")

        return True

    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Corrigiendo color del texto en la sidebar...")

    if fix_sidebar_text_color():
        print("✅ Color del texto corregido")

        if verify_text_color():
            print("✅ Verificación exitosa")
            print("\n🎉 ¡Color del texto corregido!")
            print("📝 El texto ahora aparecerá en negro")
        else:
            print("❌ Error en verificación")
    else:
        print("❌ No se pudo corregir el color del texto")


if __name__ == "__main__":
    main()
