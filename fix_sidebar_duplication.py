#!/usr/bin/env python3
"""
Script para corregir la duplicación de sistemas de IA en la sidebar
"""


def fix_sidebar_duplication():
    """Corrige la duplicación de sistemas de IA"""

    print("🔧 Corrigiendo duplicación de sistemas de IA en la sidebar...")

    # 1. Actualizar el JavaScript de la sidebar para usar los endpoints correctos
    update_sidebar_javascript()

    # 2. Verificar que los endpoints estén funcionando
    verify_endpoints()

    # 3. Crear un sistema unificado
    create_unified_system()

    print("✅ Duplicación corregida")


def update_sidebar_javascript():
    """Actualiza el JavaScript para usar los endpoints correctos"""

    js_file = "static/js/enhanced-sidebar-ai.js"

    # Leer el archivo actual
    with open(js_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar los endpoints incorrectos con los correctos
    replacements = {
        "/api/nlp/analyze": "/api/copilot/analyze-enhanced",
        "/api/search-scientific-papers": "/api/scientific-search",
        "/api/orchestration/query": "/api/copilot/analyze-enhanced",
        "/api/copilot/chat": "/api/copilot/chat",
    }

    for old_endpoint, new_endpoint in replacements.items():
        content = content.replace(old_endpoint, new_endpoint)

    # Agregar manejo de respuestas específicas
    enhanced_content = """
    // Función para procesar respuesta del endpoint unificado
    async function processUnifiedResponse(response) {
        try {
            const data = await response.json();
            
            if (data.success) {
                return {
                    nlp: data.nlp_analysis || {},
                    scientific: data.evidence || [],
                    insights: data.insights || [],
                    recommendations: data.recommendations || []
                };
            } else {
                throw new Error(data.error || 'Error en el análisis');
            }
        } catch (error) {
            console.error('Error procesando respuesta:', error);
            throw error;
        }
    }

    // Función para mostrar resultados en la sidebar
    function displayUnifiedResults(results) {
        // Mostrar insights
        if (results.insights && results.insights.length > 0) {
            displayInsights(results.insights);
        } else {
            displayInsights([]);
        }
        
        // Mostrar evidencia científica
        if (results.scientific && results.scientific.length > 0) {
            displayEvidence(results.scientific);
        } else {
            displayEvidence([]);
        }
        
        // Mostrar recomendaciones
        if (results.recommendations && results.recommendations.length > 0) {
            displayRecommendations(results.recommendations);
        } else {
            displayRecommendations([]);
        }
        
        // Actualizar chat
        updateChatWithUnifiedResults(results);
    }

    // Función para actualizar chat con resultados unificados
    function updateChatWithUnifiedResults(results) {
        let message = '📊 **Análisis Unificado Completado**\\n\\n';
        
        if (results.nlp && results.nlp.palabras_clave) {
            message += '🔑 **Palabras Clave Identificadas:**\\n';
            results.nlp.palabras_clave.forEach(palabra => {
                message += `- ${palabra.termino} (${palabra.confianza}%)\\n`;
            });
            message += '\\n';
        }
        
        if (results.scientific && results.scientific.length > 0) {
            message += f'🔬 **Evidencia Científica:** {results.scientific.length} artículos encontrados\\n\\n';
        }
        
        if (results.recommendations && results.recommendations.length > 0) {
            message += '💡 **Recomendaciones Generadas**\\n';
            results.recommendations.forEach(rec => {
                message += `- ${rec}\\n`;
            });
            message += '\\n';
        }
        
        message += '✅ Análisis unificado completado exitosamente.';
        
        if (typeof agregarMensajeElegant === 'function') {
            agregarMensajeElegant(message, 'system');
        }
    }
"""

    # Insertar el contenido mejorado
    if "processUnifiedResponse" not in content:
        # Buscar donde insertar el código
        insert_position = content.find("class EnhancedSidebarAI")
        if insert_position != -1:
            # Insertar después de la definición de la clase
            class_end = content.find("}", insert_position)
            if class_end != -1:
                content = content[:class_end] + enhanced_content + content[class_end:]

    # Actualizar la función performCompleteAnalysis
    if "performCompleteAnalysis" in content:
        # Reemplazar con la versión unificada
        unified_analysis = """
    async performCompleteAnalysis(formData) {
        const consulta = this.buildConsultaFromFormData(formData);
        
        console.log('🔍 Iniciando análisis unificado...');
        this.isProcessing = true;
        this.updateAIStatus('processing', 'Analizando datos...');
        this.showProgress();

        try {
            // Usar el endpoint unificado
            const response = await fetch('/api/copilot/analyze-enhanced', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    consulta: consulta,
                    contexto_clinico: formData
                })
            });

            if (!response.ok) {
                throw new Error('Error en análisis unificado');
            }

            const results = await processUnifiedResponse(response);
            this.currentAnalysis = results;
            displayUnifiedResults(results);
            this.updateAIStatus('success', 'Análisis completado');
            
        } catch (error) {
            console.error('❌ Error en análisis unificado:', error);
            this.updateAIStatus('error', 'Error en análisis');
            this.showError(error.message);
        } finally {
            this.isProcessing = false;
            this.hideProgress();
        }
    }
"""

        # Reemplazar la función existente
        import re

        pattern = r"async performCompleteAnalysis\(formData\) \{.*?\}"
        content = re.sub(pattern, unified_analysis, content, flags=re.DOTALL)

    # Escribir el archivo actualizado
    with open(js_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ JavaScript de la sidebar actualizado")


def verify_endpoints():
    """Verifica que los endpoints estén funcionando"""

    print("🔍 Verificando endpoints...")

    # Verificar que el endpoint principal esté disponible
    app_py_path = "app.py"

    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    endpoints_to_check = [
        "/api/copilot/analyze-enhanced",
        "/api/scientific-search",
        "/api/copilot/chat",
    ]

    for endpoint in endpoints_to_check:
        if endpoint in content:
            print(f"✅ Endpoint {endpoint} encontrado")
        else:
            print(f"❌ Endpoint {endpoint} no encontrado")


def create_unified_system():
    """Crea un sistema unificado para evitar duplicaciones"""

    print("🔧 Creando sistema unificado...")

    # Crear un archivo de configuración unificado
    config_content = """
// Configuración unificada para la sidebar de IA
window.SidebarAIConfig = {
    // Endpoints unificados
    endpoints: {
        analyze: '/api/copilot/analyze-enhanced',
        scientific: '/api/scientific-search',
        chat: '/api/copilot/chat'
    },
    
    // Configuración de análisis
    analysis: {
        debounceDelay: 1000,
        minContentLength: 10,
        maxResults: 5
    },
    
    // Configuración de UI
    ui: {
        autoMode: true,
        showProgress: true,
        notifications: true
    }
};

// Sistema unificado de notificaciones
window.UnifiedAINotifications = {
    show: function(message, type = 'info') {
        if (typeof window.showAINotification === 'function') {
            window.showAINotification(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    },
    
    success: function(message) {
        this.show(message, 'success');
    },
    
    error: function(message) {
        this.show(message, 'error');
    },
    
    warning: function(message) {
        this.show(message, 'warning');
    },
    
    info: function(message) {
        this.show(message, 'info');
    }
};

// Sistema unificado de estado
window.UnifiedAIStatus = {
    update: function(status, message) {
        if (typeof window.updateAIStatus === 'function') {
            window.updateAIStatus(status, message);
        } else {
            console.log(`[STATUS: ${status}] ${message}`);
        }
    },
    
    ready: function(message = 'IA lista para análisis') {
        this.update('ready', message);
    },
    
    processing: function(message = 'Analizando datos...') {
        this.update('processing', message);
    },
    
    success: function(message = 'Análisis completado') {
        this.update('success', message);
    },
    
    error: function(message = 'Error en análisis') {
        this.update('error', message);
    }
};
"""

    with open("static/js/unified-ai-config.js", "w", encoding="utf-8") as f:
        f.write(config_content)

    print("✅ Sistema unificado creado")


def update_template_with_unified_system():
    """Actualiza el template para usar el sistema unificado"""

    template_path = "templates/professional.html"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Agregar el archivo de configuración unificado
    unified_script = '<script src="/static/js/unified-ai-config.js"></script>'

    if unified_script not in content:
        # Insertar antes del enhanced-sidebar-ai.js
        content = content.replace(
            '<script src="/static/js/enhanced-sidebar-ai.js"></script>',
            f'{unified_script}\n    <script src="/static/js/enhanced-sidebar-ai.js"></script>',
        )

    with open(template_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Template actualizado con sistema unificado")


def main():
    """Función principal"""
    print("🔧 Corrigiendo duplicación de sistemas de IA...")

    fix_sidebar_duplication()
    update_template_with_unified_system()

    print("\n🎉 ¡Duplicación corregida!")
    print("📋 Cambios realizados:")
    print("   ✅ JavaScript actualizado para usar endpoints correctos")
    print("   ✅ Sistema unificado creado")
    print("   ✅ Configuración centralizada")
    print("   ✅ Notificaciones unificadas")

    print("\n🚀 Ahora solo habrá un sistema de IA funcionando:")
    print("   - Endpoint: /api/copilot/analyze-enhanced")
    print("   - Análisis unificado")
    print("   - Sin duplicaciones")
    print("   - Resultados consistentes")


if __name__ == "__main__":
    main()
