#!/usr/bin/env python3
"""
Script para verificar que el problema del feedback visual se ha solucionado
"""

import os
import re


def verificar_solucion_feedback():
    """Verifica que el problema del feedback visual se ha solucionado"""

    print("🔍 Verificando solución del feedback visual de Tena...")

    # Verificar que fix-toggle-sidebar.js tiene el ID correcto
    if os.path.exists("static/js/fix-toggle-sidebar.js"):
        with open("static/js/fix-toggle-sidebar.js", "r", encoding="utf-8") as f:
            contenido_js = f.read()

        # Verificar que el HTML dinámico incluye el ID
        if re.search(r'id="tenaCopilotStatus"', contenido_js):
            print(
                "✅ fix-toggle-sidebar.js: ID tenaCopilotStatus incluido en HTML dinámico"
            )
        else:
            print("❌ fix-toggle-sidebar.js: ID tenaCopilotStatus NO incluido")

        # Verificar que el texto es correcto
        if re.search(
            r'<span class="auto-mode-text" id="tenaCopilotStatus">Tena Copilot</span>',
            contenido_js,
        ):
            print("✅ fix-toggle-sidebar.js: Elemento completo correcto")
        else:
            print("❌ fix-toggle-sidebar.js: Elemento incompleto o incorrecto")

    # Verificar que professional.js tiene las funciones correctas
    if os.path.exists("static/js/professional.js"):
        with open("static/js/professional.js", "r", encoding="utf-8") as f:
            contenido_js = f.read()

        # Verificar función mostrarEstadoPensando
        if re.search(r"function mostrarEstadoPensando", contenido_js):
            print("✅ professional.js: Función mostrarEstadoPensando presente")
        else:
            print("❌ professional.js: Función mostrarEstadoPensando NO presente")

        # Verificar función ocultarEstadoPensando
        if re.search(r"function ocultarEstadoPensando", contenido_js):
            print("✅ professional.js: Función ocultarEstadoPensando presente")
        else:
            print("❌ professional.js: Función ocultarEstadoPensando NO presente")

    # Verificar que professional.html tiene el CSS correcto
    if os.path.exists("templates/professional.html"):
        with open("templates/professional.html", "r", encoding="utf-8") as f:
            contenido_html = f.read()

        # Verificar CSS para thinking
        if re.search(r"\.auto-mode-text\.thinking", contenido_html):
            print("✅ professional.html: CSS .auto-mode-text.thinking presente")
        else:
            print("❌ professional.html: CSS .auto-mode-text.thinking NO presente")

        # Verificar animación
        if re.search(r"@keyframes thinking-dots", contenido_html):
            print("✅ professional.html: Animación thinking-dots presente")
        else:
            print("❌ professional.html: Animación thinking-dots NO presente")


def generar_instrucciones_verificacion():
    """Genera instrucciones para verificar que funciona"""

    instrucciones = """
🎯 INSTRUCCIONES PARA VERIFICAR QUE EL FEEDBACK FUNCIONA:

1. **Limpia completamente el cache del navegador:**
   - Ctrl + Shift + Delete
   - Selecciona "Todo" y "Desde el inicio"
   - Haz clic en "Limpiar datos"

2. **Recarga la página:**
   - Ctrl + Shift + R (recarga forzada)
   - O Ctrl + F5

3. **Abre la consola del navegador:**
   - F12 → Console

4. **Verifica que el elemento existe:**
   ```javascript
   const elemento = document.getElementById('tenaCopilotStatus');
   console.log('Elemento:', elemento);
   ```
   Debería mostrar un elemento, no null

5. **Prueba el feedback manualmente:**
   ```javascript
   mostrarEstadoPensando();
   ```
   Debería cambiar a "Tena Copilot..." en azul

6. **Prueba restaurar el estado:**
   ```javascript
   ocultarEstadoPensando();
   ```
   Debería volver a "Tena Copilot" en gris

7. **Haz una consulta real:**
   - Escribe cualquier pregunta en el input
   - Presiona Enter
   - Observa si cambia automáticamente a "Tena Copilot..." en azul

8. **Verifica que vuelve al estado normal:**
   - Cuando aparezca la respuesta
   - Debería volver a "Tena Copilot" en gris

✅ Si todos estos pasos funcionan, el feedback visual está completamente implementado.
"""

    print(instrucciones)


def generar_script_debug():
    """Genera un script de debug para verificar el estado"""

    script_debug = """
🔧 SCRIPT DE DEBUG PARA VERIFICAR ESTADO:

// Ejecuta esto en la consola del navegador (F12)

console.log('=== DEBUG FEEDBACK VISUAL ===');

// 1. Verificar elemento
const elemento = document.getElementById('tenaCopilotStatus');
console.log('1. Elemento encontrado:', elemento);

if (elemento) {
    console.log('   - Texto actual:', elemento.textContent);
    console.log('   - Clases actuales:', elemento.className);
    
    // 2. Verificar CSS
    const styles = window.getComputedStyle(elemento);
    console.log('2. Color actual:', styles.color);
    
    // 3. Probar agregar clase thinking
    elemento.classList.add('thinking');
    console.log('3. Clases después de thinking:', elemento.className);
    
    // 4. Verificar color después de thinking
    const stylesAfter = window.getComputedStyle(elemento);
    console.log('4. Color después de thinking:', stylesAfter.color);
    
    // 5. Cambiar texto
    elemento.textContent = 'Tena Copilot...';
    console.log('5. Texto después del cambio:', elemento.textContent);
    
    // 6. Verificar funciones
    console.log('6. Función mostrarEstadoPensando:', typeof mostrarEstadoPensando);
    console.log('6. Función ocultarEstadoPensando:', typeof ocultarEstadoPensando);
    
    // 7. Restaurar después de 3 segundos
    setTimeout(() => {
        elemento.classList.remove('thinking');
        elemento.textContent = 'Tena Copilot';
        console.log('7. Estado restaurado');
    }, 3000);
    
} else {
    console.error('❌ Elemento tenaCopilotStatus no encontrado');
    console.log('Posibles causas:');
    console.log('- Cache del navegador no limpiado');
    console.log('- Script fix-toggle-sidebar.js recreando sidebar sin ID');
    console.log('- Elemento no cargado aún');
}

console.log('=== FIN DEBUG ===');
"""

    print(script_debug)


if __name__ == "__main__":
    print("🚀 Verificación de solución del feedback visual")
    print("=" * 60)

    verificar_solucion_feedback()

    print("\n" + "=" * 60)
    generar_instrucciones_verificacion()

    print("\n" + "=" * 60)
    generar_script_debug()
