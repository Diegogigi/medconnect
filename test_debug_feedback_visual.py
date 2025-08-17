#!/usr/bin/env python3
"""
Script para debuggear el problema del feedback visual de Tena
"""

import os
import re

def verificar_problema_feedback():
    """Verifica dónde está el problema con el feedback visual"""
    
    print("🔍 Debuggeando problema del feedback visual de Tena...")
    
    # Verificar si el elemento existe en el HTML
    if os.path.exists('templates/professional.html'):
        with open('templates/professional.html', 'r', encoding='utf-8') as f:
            contenido_html = f.read()
            
        # Buscar el elemento específico
        if re.search(r'id="tenaCopilotStatus"', contenido_html):
            print("✅ Elemento tenaCopilotStatus encontrado en HTML")
            
            # Extraer el contexto del elemento
            match = re.search(r'<span class="auto-mode-text" id="tenaCopilotStatus">([^<]+)</span>', contenido_html)
            if match:
                texto_actual = match.group(1)
                print(f"📝 Texto actual del elemento: '{texto_actual}'")
        else:
            print("❌ Elemento tenaCopilotStatus NO encontrado en HTML")
    
    # Verificar CSS
    if os.path.exists('templates/professional.html'):
        with open('templates/professional.html', 'r', encoding='utf-8') as f:
            contenido_html = f.read()
            
        # Verificar CSS para thinking
        if re.search(r'\.auto-mode-text\.thinking', contenido_html):
            print("✅ CSS .auto-mode-text.thinking encontrado")
            
            # Extraer el CSS completo
            css_match = re.search(r'\.auto-mode-text\.thinking\s*{[^}]+}', contenido_html)
            if css_match:
                css_content = css_match.group(0)
                print(f"📋 CSS encontrado: {css_content}")
        else:
            print("❌ CSS .auto-mode-text.thinking NO encontrado")
            
        # Verificar animación
        if re.search(r'@keyframes thinking-dots', contenido_html):
            print("✅ Animación thinking-dots encontrada")
        else:
            print("❌ Animación thinking-dots NO encontrada")
    
    # Verificar JavaScript
    if os.path.exists('static/js/professional.js'):
        with open('static/js/professional.js', 'r', encoding='utf-8') as f:
            contenido_js = f.read()
            
        # Verificar función mostrarEstadoPensando
        if re.search(r'function mostrarEstadoPensando', contenido_js):
            print("✅ Función mostrarEstadoPensando encontrada")
            
            # Extraer la función completa
            func_match = re.search(r'function mostrarEstadoPensando\(\)\s*{[^}]+}', contenido_js)
            if func_match:
                func_content = func_match.group(0)
                print(f"📋 Función encontrada: {func_content}")
        else:
            print("❌ Función mostrarEstadoPensando NO encontrada")
            
        # Verificar si se llama desde mostrarTypingElegant
        if re.search(r'mostrarEstadoPensando\(\)', contenido_js):
            print("✅ Llamada a mostrarEstadoPensando encontrada")
        else:
            print("❌ Llamada a mostrarEstadoPensando NO encontrada")

def generar_script_prueba():
    """Genera un script de prueba para verificar el feedback visual"""
    
    script_prueba = """
🔧 SCRIPT DE PRUEBA PARA VERIFICAR FEEDBACK VISUAL:

1. Abre la consola del navegador (F12)
2. Ejecuta estos comandos uno por uno:

// Verificar si el elemento existe
const elemento = document.getElementById('tenaCopilotStatus');
console.log('Elemento encontrado:', elemento);

if (elemento) {
    console.log('Texto actual:', elemento.textContent);
    console.log('Clases actuales:', elemento.className);
    
    // Probar agregar la clase thinking
    elemento.classList.add('thinking');
    console.log('Clases después de agregar thinking:', elemento.className);
    
    // Verificar si el CSS se aplicó
    const styles = window.getComputedStyle(elemento);
    console.log('Color actual:', styles.color);
    
    // Cambiar el texto
    elemento.textContent = 'Tena Copilot...';
    console.log('Texto después del cambio:', elemento.textContent);
    
    // Remover la clase después de 3 segundos
    setTimeout(() => {
        elemento.classList.remove('thinking');
        elemento.textContent = 'Tena Copilot';
        console.log('Estado restaurado');
    }, 3000);
} else {
    console.error('❌ Elemento tenaCopilotStatus no encontrado');
}

3. Verifica en la consola:
   - Si el elemento existe
   - Si el color cambia a azul (#667eea)
   - Si el texto cambia a "Tena Copilot..."
   - Si la animación funciona
"""
    
    print(script_prueba)

def verificar_posibles_conflictos():
    """Verifica posibles conflictos con otros scripts"""
    
    print("\n🔍 Verificando posibles conflictos...")
    
    # Verificar si hay otros scripts que puedan estar interfiriendo
    archivos_js = [
        'static/js/fix-toggle-sidebar.js',
        'static/js/fix-all-errors.js',
        'static/js/force-clean-system.js'
    ]
    
    for archivo in archivos_js:
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            # Buscar referencias a auto-mode-text o tenaCopilotStatus
            if re.search(r'auto-mode-text|tenaCopilotStatus', contenido):
                print(f"⚠️ Posible conflicto en {archivo}")
                print(f"   - Contiene referencias a elementos del sidebar")
            else:
                print(f"✅ {archivo} - Sin conflictos detectados")
        else:
            print(f"ℹ️ {archivo} - No existe")

def generar_solucion_manual():
    """Genera instrucciones para solucionar manualmente"""
    
    solucion = """
🛠️ SOLUCIÓN MANUAL SI EL FEEDBACK NO FUNCIONA:

1. **Verificar que el elemento existe:**
   - Abre la consola del navegador (F12)
   - Ejecuta: `document.getElementById('tenaCopilotStatus')`
   - Debería devolver un elemento, no null

2. **Verificar que el CSS se carga:**
   - En la consola, ejecuta:
   ```javascript
   const elemento = document.getElementById('tenaCopilotStatus');
   elemento.classList.add('thinking');
   const styles = window.getComputedStyle(elemento);
   console.log('Color:', styles.color);
   ```
   - El color debería ser rgb(102, 126, 234) o similar

3. **Verificar que las funciones se ejecutan:**
   - En la consola, ejecuta:
   ```javascript
   mostrarEstadoPensando();
   ```
   - Debería cambiar el texto y el color

4. **Si no funciona, forzar manualmente:**
   ```javascript
   const elemento = document.getElementById('tenaCopilotStatus');
   elemento.style.color = '#667eea';
   elemento.textContent = 'Tena Copilot...';
   ```

5. **Limpiar cache del navegador:**
   - Ctrl + Shift + R (recarga forzada)
   - O Ctrl + F5

6. **Verificar que no hay errores en la consola:**
   - Buscar errores JavaScript que puedan estar interfiriendo
"""
    
    print(solucion)

if __name__ == "__main__":
    print("🚀 Debuggeando feedback visual de Tena")
    print("=" * 60)
    
    verificar_problema_feedback()
    
    print("\n" + "=" * 60)
    verificar_posibles_conflictos()
    
    print("\n" + "=" * 60)
    generar_script_prueba()
    
    print("\n" + "=" * 60)
    generar_solucion_manual() 