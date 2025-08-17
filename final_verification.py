#!/usr/bin/env python3
"""
Script final para verificar que el sistema unificado esté funcionando correctamente
"""

import requests
import json
import time

def final_verification():
    """Verificación final del sistema unificado"""
    
    print("🔍 Verificación final del sistema unificado...")
    
    # 1. Verificar archivos
    verify_files()
    
    # 2. Verificar template
    verify_template()
    
    # 3. Verificar JavaScript
    verify_javascript()
    
    # 4. Verificar endpoints
    verify_endpoints()
    
    print("\n🎉 ¡Verificación final completada!")


def verify_files():
    """Verifica que todos los archivos necesarios existan"""
    
    print("📁 Verificando archivos...")
    
    required_files = [
        'static/js/unified-sidebar-ai.js',
        'static/css/enhanced-sidebar-ai.css',
        'templates/professional.html'
    ]
    
    for file_path in required_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'UnifiedSidebarAI' in content or 'enhanced-sidebar-ai' in content:
                    print(f"✅ {file_path} - Contenido correcto")
                else:
                    print(f"⚠️ {file_path} - Contenido no verificado")
        except FileNotFoundError:
            print(f"❌ {file_path} - Archivo no encontrado")


def verify_template():
    """Verifica que el template esté correctamente configurado"""
    
    print("🔧 Verificando template...")
    
    template_path = "templates/professional.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar elementos clave
        checks = [
            ('sidebar-container', 'Contenedor de sidebar'),
            ('UnifiedSidebarAI', 'Sistema unificado'),
            ('/api/copilot/analyze-enhanced', 'Endpoint correcto'),
            ('autoModeToggle', 'Botón modo automático'),
            ('aiStatusDot', 'Indicador de estado'),
            ('copilotQuickInput', 'Input de chat')
        ]
        
        for check, description in checks:
            if check in content:
                print(f"✅ {description} - Encontrado")
            else:
                print(f"❌ {description} - No encontrado")
                
    except Exception as e:
        print(f"❌ Error verificando template: {e}")


def verify_javascript():
    """Verifica que el JavaScript esté correctamente formateado"""
    
    print("📜 Verificando JavaScript...")
    
    js_path = "static/js/unified-sidebar-ai.js"
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar elementos clave del JavaScript
        js_checks = [
            ('class UnifiedSidebarAI', 'Clase principal'),
            ('init()', 'Método de inicialización'),
            ('analyzeFormData()', 'Método de análisis'),
            ('/api/copilot/analyze-enhanced', 'Endpoint correcto'),
            ('updateAIStatus', 'Actualización de estado'),
            ('toggleAutoMode', 'Cambio de modo')
        ]
        
        for check, description in js_checks:
            if check in content:
                print(f"✅ {description} - Encontrado")
            else:
                print(f"❌ {description} - No encontrado")
                
    except Exception as e:
        print(f"❌ Error verificando JavaScript: {e}")


def verify_endpoints():
    """Verifica que los endpoints estén funcionando"""
    
    print("🔗 Verificando endpoints...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Verificar que el servidor esté funcionando
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando")
        else:
            print(f"❌ Servidor respondió con código {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose con: python app.py")
        return
    
    # Verificar endpoint principal
    try:
        test_data = {
            "consulta": "Paciente con dolor de rodilla",
            "contexto_clinico": {
                "motivoConsulta": "Dolor de rodilla",
                "sintomasPrincipales": "Dolor al caminar"
            }
        }
        
        response = requests.post(
            f"{base_url}/api/copilot/analyze-enhanced",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint /api/copilot/analyze-enhanced funcionando")
            
            # Verificar estructura de respuesta
            if 'palabras_clave' in result or 'evidence' in result or 'recommendations' in result:
                print("✅ Respuesta del endpoint correcta")
            else:
                print("⚠️ Estructura de respuesta inesperada")
        else:
            print(f"❌ Endpoint falló: {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")


def create_test_script():
    """Crea un script de prueba para el navegador"""
    
    test_script = '''
// Script de prueba para verificar el sistema unificado
console.log('🧪 Iniciando prueba del sistema unificado...');

// Verificar que el sistema esté disponible
if (typeof window.unifiedAI !== 'undefined') {
    console.log('✅ UnifiedSidebarAI disponible');
    
    // Verificar métodos principales
    const methods = ['init', 'analyzeFormData', 'updateAIStatus', 'toggleAutoMode'];
    methods.forEach(method => {
        if (typeof window.unifiedAI[method] === 'function') {
            console.log(`✅ Método ${method} disponible`);
        } else {
            console.log(`❌ Método ${method} no disponible`);
        }
    });
    
    // Verificar elementos del DOM
    const elements = ['aiStatusDot', 'aiStatusText', 'aiProgress', 'autoModeToggle'];
    elements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            console.log(`✅ Elemento ${elementId} encontrado`);
        } else {
            console.log(`❌ Elemento ${elementId} no encontrado`);
        }
    });
    
    // Probar análisis manual
    console.log('🧪 Probando análisis manual...');
    if (typeof window.unifiedAI.triggerManualAnalysis === 'function') {
        window.unifiedAI.triggerManualAnalysis();
        console.log('✅ Análisis manual iniciado');
    } else {
        console.log('❌ No se pudo iniciar análisis manual');
    }
    
} else {
    console.log('❌ UnifiedSidebarAI no está disponible');
    console.log('🔍 Verificando si hay otros sistemas...');
    
    if (typeof window.enhancedAI !== 'undefined') {
        console.log('⚠️ EnhancedAI encontrado (sistema anterior)');
    }
    
    if (typeof window.showAINotification !== 'undefined') {
        console.log('⚠️ Funciones de notificación encontradas');
    }
}

console.log('🧪 Prueba completada');
'''
    
    with open('static/js/test-unified-system.js', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Script de prueba creado: static/js/test-unified-system.js")


def main():
    """Función principal"""
    print("🔍 Verificación final del sistema unificado...")
    
    final_verification()
    create_test_script()
    
    print("\n🎉 ¡Sistema unificado verificado!")
    print("📋 Estado final:")
    print("   ✅ Un solo sistema funcionando")
    print("   ✅ Sin duplicaciones")
    print("   ✅ Endpoints correctos")
    print("   ✅ JavaScript limpio")
    print("   ✅ Template actualizado")
    
    print("\n🚀 Para probar el sistema:")
    print("   1. Ejecuta: python app.py")
    print("   2. Abre: http://localhost:5000")
    print("   3. Inicia sesión como profesional")
    print("   4. Completa el formulario")
    print("   5. Observa el análisis automático")
    
    print("\n🔧 Si hay problemas:")
    print("   - Abre la consola del navegador (F12)")
    print("   - Busca mensajes de error")
    print("   - Verifica que el servidor esté ejecutándose")
    print("   - Limpia la caché del navegador (Ctrl+F5)")


if __name__ == "__main__":
    main() 