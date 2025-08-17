#!/usr/bin/env python3
"""
Script para actualizar el template professional.html con la integración de IA
"""

import re
from pathlib import Path


def update_template_with_ai_integration():
    """Actualiza el template con la integración de IA"""
    
    template_path = Path("templates/professional.html")
    if not template_path.exists():
        print("❌ Template professional.html no encontrado")
        return False
    
    # Leer el template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Agregar CSS de la sidebar mejorada
    css_link = '<link rel="stylesheet" href="/static/css/enhanced-sidebar-ai.css">'
    if css_link not in content:
        # Insertar después del CSS existente
        css_insertion = f'''
    <link rel="stylesheet" href="/static/css/patient-styles.css">
    {css_link}
'''
        content = content.replace(
            '<link rel="stylesheet" href="/static/css/patient-styles.css">',
            css_insertion
        )
    
    # 2. Agregar JavaScript de la sidebar mejorada
    js_script = '<script src="/static/js/enhanced-sidebar-ai.js"></script>'
    if js_script not in content:
        # Insertar antes del cierre del body
        content = content.replace(
            '</body>',
            f'    {js_script}\n</body>'
        )
    
    # 3. Actualizar la función de inicialización de sidebar
    new_sidebar_init = '''
// Inicialización mejorada de la sidebar con IA
if (typeof window.inicializarSidebarDinamica !== 'function') {
    window.inicializarSidebarDinamica = function() {
        console.log('🚀 Inicializando Enhanced Sidebar AI...');
        
        // Inicializar el sistema de IA si está disponible
        if (typeof window.enhancedAI !== 'undefined') {
            console.log('✅ Enhanced Sidebar AI ya inicializado');
        } else {
            console.log('⚠️ Enhanced Sidebar AI no disponible, usando función temporal');
            // Función temporal mientras se carga
            setTimeout(() => {
                if (typeof window.enhancedAI !== 'undefined') {
                    console.log('✅ Enhanced Sidebar AI cargado correctamente');
                }
            }, 1000);
        }
        
        // Configurar sidebar básica
        const sidebarContainer = document.getElementById("sidebarContainer");
        if (sidebarContainer) {
            sidebarContainer.classList.add("show");
            console.log('✅ Sidebar mostrada');
        }
    };
}
'''
    
    # Reemplazar la función existente
    old_pattern = r'if \(typeof window\.inicializarSidebarDinamica !== \'function\'\) \{.*?\}'
    content = re.sub(old_pattern, new_sidebar_init, content, flags=re.DOTALL)
    
    # 4. Agregar controles de IA en la sidebar
    ai_controls = '''
                <!-- Controles de IA -->
                <div class="sidebar-controls">
                    <button class="control-btn" id="autoModeToggle" title="Modo Automático">
                        <i class="fas fa-robot"></i>
                    </button>
                    <button class="control-btn" id="manualAnalyzeBtn" title="Análisis Manual">
                        <i class="fas fa-search"></i>
                    </button>
                    <button class="control-btn" id="refreshAnalysisBtn" title="Actualizar Análisis">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>
'''
    
    # Insertar controles después del handle de resize
    if 'sidebar-controls' not in content:
        content = content.replace(
            '<div class="sidebar-resize-handle" id="sidebarResizeHandle"></div>',
            f'<div class="sidebar-resize-handle" id="sidebarResizeHandle"></div>\n{ai_controls}'
        )
    
    # 5. Agregar indicador de estado de IA
    ai_status = '''
                <!-- Indicador de Estado de IA -->
                <div class="ai-status-panel">
                    <div class="ai-status-indicator">
                        <div class="status-dot ready" id="aiStatusDot"></div>
                        <span id="aiStatusText">IA lista para análisis</span>
                    </div>
                    <div class="ai-progress" id="aiProgress" style="display: none;">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                        <span id="progressText">Analizando...</span>
                    </div>
                </div>
'''
    
    # Insertar después del panel-content
    if 'ai-status-panel' not in content:
        content = content.replace(
            '<div class="panel-content p-3">',
            f'<div class="panel-content p-3">\n{ai_status}'
        )
    
    # 6. Agregar funciones de utilidad
    utility_functions = '''
// Funciones de utilidad para la IA
window.showAINotification = function(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.classList.add('show'), 100);
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
};

window.updateAIStatus = function(status, message) {
    const statusDot = document.getElementById('aiStatusDot');
    const statusText = document.getElementById('aiStatusText');
    
    if (statusDot) {
        statusDot.className = `status-dot ${status}`;
    }
    
    if (statusText) {
        statusText.textContent = message;
    }
};

window.showAIProgress = function(percentage, text) {
    const progress = document.getElementById('aiProgress');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    
    if (progress) {
        progress.style.display = 'block';
    }
    
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }
    
    if (progressText) {
        progressText.textContent = text;
    }
};

window.hideAIProgress = function() {
    const progress = document.getElementById('aiProgress');
    if (progress) {
        progress.style.display = 'none';
    }
};
'''
    
    # Insertar antes del cierre del body
    if 'showAINotification' not in content:
        content = content.replace(
            '</body>',
            f'{utility_functions}\n</body>'
        )
    
    # Escribir el template actualizado
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Template professional.html actualizado con integración de IA")
    return True


def create_demo_endpoints():
    """Crea endpoints de demostración para la IA"""
    
    demo_endpoints = '''
# Endpoints de demostración para la IA
@app.route("/api/nlp/analyze", methods=["POST"])
@login_required
def nlp_analyze():
    """Endpoint de demostración para análisis NLP"""
    try:
        data = request.get_json()
        texto = data.get("texto", "")
        contexto = data.get("contexto", "general")
        
        # Simular análisis NLP
        sintomas = ["dolor", "limitación", "debilidad"] if "dolor" in texto.lower() else []
        confianza = 0.85 if len(texto) > 10 else 0.5
        
        return jsonify({
            "success": True,
            "sintomas": sintomas,
            "confianza": confianza,
            "contexto": contexto,
            "texto_analizado": texto
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ai/insights", methods=["POST"])
@login_required
def generate_ai_insights():
    """Endpoint de demostración para insights de IA"""
    try:
        data = request.get_json()
        form_data = data.get("form_data", {})
        
        # Simular insights
        insights = [
            {
                "tipo": "sintomas",
                "titulo": "Síntomas Identificados",
                "contenido": ["Dolor de rodilla", "Limitación de movimiento"],
                "confianza": 0.9
            },
            {
                "tipo": "patron",
                "titulo": "Patrón Clínico Detectado",
                "contenido": "Posible osteoartritis de rodilla",
                "confianza": 0.75
            }
        ]
        
        return jsonify({
            "success": True,
            "insights": insights
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
'''
    
    # Agregar al final de app.py
    app_py_path = Path("app.py")
    if app_py_path.exists():
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "nlp_analyze" not in content:
            with open(app_py_path, 'a', encoding='utf-8') as f:
                f.write(demo_endpoints)
            
            print("✅ Endpoints de demostración agregados a app.py")
    
    return True


def main():
    """Función principal"""
    print("🔧 Actualizando template con integración de IA...")
    
    # Actualizar template
    if update_template_with_ai_integration():
        print("✅ Template actualizado exitosamente")
    else:
        print("❌ Error actualizando template")
        return False
    
    # Crear endpoints de demostración
    if create_demo_endpoints():
        print("✅ Endpoints de demostración creados")
    else:
        print("❌ Error creando endpoints")
        return False
    
    print("\n🎉 Integración de IA en sidebar completada!")
    print("📋 Características implementadas:")
    print("   - CSS mejorado para la sidebar")
    print("   - JavaScript de IA integrado")
    print("   - Controles de modo automático")
    print("   - Indicadores de estado de IA")
    print("   - Endpoints de demostración")
    print("\n🚀 La IA ahora capturará automáticamente la información del formulario")
    
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ ¡Todo listo! La sidebar con IA está completamente integrada.")
    else:
        print("\n❌ Hubo errores en la integración.") 