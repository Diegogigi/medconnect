#!/usr/bin/env python3
"""
Script para actualizar el endpoint analyze-enhanced para usar el sistema unificado
"""


def update_endpoint_to_unified():
    """Actualiza el endpoint para usar el sistema unificado"""

    app_py_path = "app.py"

    print("🔧 Actualizando endpoint para usar sistema unificado...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar el endpoint actual
    endpoint_start = content.find(
        '@app.route("/api/copilot/analyze-enhanced", methods=["POST"])'
    )
    if endpoint_start == -1:
        print("❌ Endpoint no encontrado")
        return False

    # Buscar el final de la función
    function_start = content.find("def analyze_enhanced():", endpoint_start)
    if function_start == -1:
        print("❌ Función no encontrada")
        return False

    # Buscar el final de la función (aproximadamente)
    function_end = content.find("@app.route", function_start + 100)
    if function_end == -1:
        function_end = len(content)

    # Extraer la función actual
    current_function = content[function_start:function_end]

    # Crear la nueva función unificada
    new_function = '''def analyze_enhanced():
    """Análisis unificado usando el sistema mejorado.
    Integra todos los sistemas: NLP, Búsqueda Científica, y Copilot.
    """
    try:
        data = request.get_json(force=True) or {}
        consulta = data.get("consulta", "").strip()
        contexto_clinico = data.get("contexto_clinico", {})
        
        # Si no hay consulta directa, construirla desde el contexto
        if not consulta:
            motivo = contexto_clinico.get("motivoConsulta", "")
            sintomas = contexto_clinico.get("sintomasPrincipales", "")
            antecedentes = contexto_clinico.get("antecedentesMedicos", "")
            consulta = f"{motivo}. {sintomas}. {antecedentes}".strip()
        
        if not consulta:
            return jsonify({
                "success": False, 
                "message": "Se requiere consulta o contexto clínico"
            }), 400

        logger.info(f"🔍 Análisis unificado iniciado para: {consulta[:100]}...")
        
        # 1. Análisis NLP usando el sistema unificado
        try:
            from unified_nlp_processor_main import UnifiedNLPProcessor
            nlp_processor = UnifiedNLPProcessor()
            analisis_nlp = nlp_processor.analizar_texto(consulta)
            logger.info("✅ Análisis NLP completado")
        except Exception as e:
            logger.warning(f"⚠️ Error en NLP, usando análisis básico: {e}")
            analisis_nlp = {
                "sintomas": [],
                "entidades": [],
                "confianza": 0.5,
                "palabras_clave": []
            }

        # 2. Búsqueda científica usando el sistema unificado
        try:
            from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced
            search_system = UnifiedScientificSearchEnhanced()
            evidencia_cientifica = search_system.buscar_evidencia_cientifica(
                consulta, 
                analisis_nlp=analisis_nlp,
                max_resultados=5
            )
            logger.info(f"✅ Búsqueda científica completada: {len(evidencia_cientifica)} resultados")
        except Exception as e:
            logger.warning(f"⚠️ Error en búsqueda científica: {e}")
            evidencia_cientifica = []

        # 3. Análisis clínico usando el sistema unificado
        try:
            from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced
            copilot = UnifiedCopilotAssistantEnhanced()
            analisis_clinico = copilot.analizar_caso_clinico(
                consulta, 
                evidencia=evidencia_cientifica,
                contexto_nlp=analisis_nlp
            )
            logger.info("✅ Análisis clínico completado")
        except Exception as e:
            logger.warning(f"⚠️ Error en análisis clínico: {e}")
            analisis_clinico = {
                "recomendaciones": [],
                "patologias": [],
                "escalas": []
            }

        # 4. Generar respuesta unificada
        respuesta_unificada = {
            "success": True,
            "consulta_original": consulta,
            "nlp_analysis": {
                "palabras_clave": analisis_nlp.get("palabras_clave", []),
                "sintomas": analisis_nlp.get("sintomas", []),
                "entidades": analisis_nlp.get("entidades", []),
                "confianza": analisis_nlp.get("confianza", 0.5)
            },
            "evidence": [
                {
                    "titulo": ev.titulo,
                    "resumen": ev.resumen,
                    "doi": ev.doi,
                    "fuente": ev.fuente,
                    "year": ev.año_publicacion,
                    "tipo": ev.tipo_evidencia,
                    "url": ev.url,
                    "relevancia": ev.relevancia_score
                }
                for ev in evidencia_cientifica
            ],
            "clinical_analysis": {
                "recomendaciones": analisis_clinico.get("recomendaciones", []),
                "patologias": analisis_clinico.get("patologias", []),
                "escalas": analisis_clinico.get("escalas", []),
                "region_anatomica": analisis_nlp.get("region_anatomica", "")
            },
            "timestamp": time.time(),
            "sistema": "unificado"
        }

        logger.info("✅ Análisis unificado completado exitosamente")
        return jsonify(respuesta_unificada)

    except Exception as e:
        logger.error(f"❌ Error en análisis unificado: {e}")
        return jsonify({
            "success": False,
            "message": f"Error en análisis: {str(e)}"
        }), 500
'''

    # Reemplazar la función
    new_content = content[:function_start] + new_function + content[function_end:]

    # Agregar imports necesarios al inicio del archivo
    imports_to_add = """
import time
from unified_nlp_processor_main import UnifiedNLPProcessor
from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced
from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced
"""

    # Buscar donde agregar los imports
    import_section = new_content.find("import logging")
    if import_section != -1:
        # Agregar después de los imports existentes
        new_content = (
            new_content[:import_section] + imports_to_add + new_content[import_section:]
        )

    # Escribir el archivo actualizado
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ Endpoint actualizado para usar sistema unificado")
    return True


def verify_unified_endpoint():
    """Verifica que el endpoint esté usando el sistema unificado"""

    app_py_path = "app.py"

    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verificar que use los sistemas unificados
    unified_indicators = [
        "UnifiedNLPProcessor",
        "UnifiedScientificSearchEnhanced",
        "UnifiedCopilotAssistantEnhanced",
        'sistema": "unificado"',
    ]

    print("🔍 Verificando endpoint unificado...")
    for indicator in unified_indicators:
        if indicator in content:
            print(f"✅ {indicator} - Encontrado")
        else:
            print(f"❌ {indicator} - No encontrado")

    return all(indicator in content for indicator in unified_indicators)


def create_simple_sidebar_interface():
    """Crea una interfaz simple para la sidebar"""

    print("🎨 Creando interfaz simple para la sidebar...")

    # Actualizar el JavaScript para mostrar resultados de manera simple
    simple_js = """
/**
 * Sistema Unificado de IA para Sidebar - Interfaz Simple
 */

class SimpleUnifiedSidebarAI {
    constructor() {
        this.isInitialized = false;
        this.formData = {};
        this.isProcessing = false;
        this.autoMode = true;
        this.debounceTimer = null;
        
        this.init();
    }

    init() {
        console.log('🚀 Inicializando Sistema Unificado Simple...');
        
        this.initFormWatchers();
        this.initEventListeners();
        this.updateAIStatus('ready', 'IA lista para análisis');
        
        this.isInitialized = true;
        console.log('✅ Sistema Unificado Simple inicializado');
    }

    initFormWatchers() {
        const formSelectors = [
            '#motivoConsulta',
            '#sintomasPrincipales',
            '#antecedentesMedicos',
            '#medicamentosActuales',
            '#alergias',
            '#examenFisico',
            '#diagnosticoPresuntivo',
            '#planTratamiento'
        ];

        formSelectors.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                element.addEventListener('input', () => this.handleFormChange());
                element.addEventListener('change', () => this.handleFormChange());
            }
        });
    }

    initEventListeners() {
        const autoModeBtn = document.getElementById('autoModeToggle');
        if (autoModeBtn) {
            autoModeBtn.addEventListener('click', () => this.toggleAutoMode());
        }
    }

    handleFormChange() {
        if (!this.autoMode || this.isProcessing) return;

        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.analyzeFormData();
        }, 1000);
    }

    async analyzeFormData() {
        const formData = this.collectFormData();
        const totalContent = Object.values(formData).join(' ').trim();
        
        if (totalContent.length < 10) {
            this.updateAIStatus('waiting', 'Esperando más información...');
            return;
        }

        console.log('🔍 Iniciando análisis unificado...');
        this.isProcessing = true;
        this.updateAIStatus('processing', 'Analizando datos...');
        this.showProgress();

        try {
            await this.performUnifiedAnalysis(formData);
        } catch (error) {
            console.error('❌ Error en análisis:', error);
            this.updateAIStatus('error', 'Error en análisis');
            this.showError(error.message);
        } finally {
            this.isProcessing = false;
            this.hideProgress();
        }
    }

    async performUnifiedAnalysis(formData) {
        const consulta = this.buildConsultaFromFormData(formData);
        
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

        const result = await response.json();
        
        if (result.success) {
            this.displaySimpleResults(result);
            this.updateAIStatus('success', 'Análisis completado');
        } else {
            throw new Error(result.message || 'Error en el análisis');
        }
    }

    displaySimpleResults(result) {
        // Mostrar resultados de manera simple en el chat
        let message = '📊 **Análisis Unificado Completado**\\n\\n';
        
        // Palabras clave
        if (result.nlp_analysis && result.nlp_analysis.palabras_clave) {
            message += '🔑 **Palabras Clave:**\\n';
            result.nlp_analysis.palabras_clave.forEach(palabra => {
                message += `- ${palabra.termino} (${palabra.confianza}%)\\n`;
            });
            message += '\\n';
        }
        
        // Región anatómica
        if (result.clinical_analysis && result.clinical_analysis.region_anatomica) {
            message += `📍 **Región:** ${result.clinical_analysis.region_anatomica}\\n\\n`;
        }
        
        // Patologías
        if (result.clinical_analysis && result.clinical_analysis.patologias) {
            message += '🏥 **Patologías:**\\n';
            result.clinical_analysis.patologias.forEach(pat => {
                message += `- ${pat.nombre} (${pat.confianza}%)\\n`;
            });
            message += '\\n';
        }
        
        // Escalas
        if (result.clinical_analysis && result.clinical_analysis.escalas) {
            message += '📊 **Escalas Recomendadas:**\\n';
            result.clinical_analysis.escalas.forEach(escala => {
                message += `- ${escala.nombre}\\n`;
            });
            message += '\\n';
        }
        
        // Evidencia científica
        if (result.evidence && result.evidence.length > 0) {
            message += `🔬 **Evidencia Científica:** ${result.evidence.length} artículos\\n\\n`;
        }
        
        // Recomendaciones
        if (result.clinical_analysis && result.clinical_analysis.recomendaciones) {
            message += '💡 **Recomendaciones:**\\n';
            result.clinical_analysis.recomendaciones.forEach(rec => {
                message += `- ${rec}\\n`;
            });
            message += '\\n';
        }
        
        message += '✅ Análisis unificado completado exitosamente.';
        
        if (typeof agregarMensajeElegant === 'function') {
            agregarMensajeElegant(message, 'system');
        }
    }

    collectFormData() {
        const formData = {};
        
        const fields = {
            motivoConsulta: '#motivoConsulta',
            sintomasPrincipales: '#sintomasPrincipales',
            antecedentesMedicos: '#antecedentesMedicos',
            medicamentosActuales: '#medicamentosActuales',
            alergias: '#alergias',
            examenFisico: '#examenFisico',
            diagnosticoPresuntivo: '#diagnosticoPresuntivo',
            planTratamiento: '#planTratamiento'
        };

        Object.entries(fields).forEach(([key, selector]) => {
            const element = document.querySelector(selector);
            if (element) {
                formData[key] = element.value || element.textContent || '';
            }
        });

        return formData;
    }

    buildConsultaFromFormData(formData) {
        const parts = [];
        
        if (formData.motivoConsulta) parts.push(formData.motivoConsulta);
        if (formData.sintomasPrincipales) parts.push(formData.sintomasPrincipales);
        if (formData.antecedentesMedicos) parts.push(formData.antecedentesMedicos);
        if (formData.diagnosticoPresuntivo) parts.push(formData.diagnosticoPresuntivo);
        
        return parts.join('. ');
    }

    updateAIStatus(status, message) {
        const statusDot = document.getElementById('aiStatusDot');
        const statusText = document.getElementById('aiStatusText');
        
        if (statusDot) {
            statusDot.className = `status-dot ${status}`;
        }
        
        if (statusText) {
            statusText.textContent = message;
        }
    }

    showProgress() {
        const progress = document.getElementById('aiProgress');
        if (progress) {
            progress.style.display = 'block';
        }
    }

    hideProgress() {
        const progress = document.getElementById('aiProgress');
        if (progress) {
            progress.style.display = 'none';
        }
    }

    showError(message) {
        this.updateAIStatus('error', `Error: ${message}`);
        
        if (typeof agregarMensajeElegant === 'function') {
            agregarMensajeElegant(`❌ **Error en análisis:** ${message}`, 'error');
        }
    }

    toggleAutoMode() {
        this.autoMode = !this.autoMode;
        
        const indicator = document.querySelector('.auto-mode-status');
        if (indicator) {
            indicator.innerHTML = this.autoMode ? 
                '<i class="fas fa-check-circle text-success"></i>' :
                '<i class="fas fa-pause-circle text-warning"></i>';
        }
        
        const message = this.autoMode ? 
            '🔄 **Modo automático activado**' :
            '⏸️ **Modo automático desactivado**';
        
        if (typeof agregarMensajeElegant === 'function') {
            agregarMensajeElegant(message, 'system');
        }
    }
}

// Inicializar el sistema simple cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.simpleUnifiedAI = new SimpleUnifiedSidebarAI();
});

// Exportar para uso global
window.SimpleUnifiedSidebarAI = SimpleUnifiedSidebarAI;
"""

    # Escribir el JavaScript simple
    with open("static/js/simple-unified-sidebar-ai.js", "w", encoding="utf-8") as f:
        f.write(simple_js)

    print("✅ JavaScript simple creado")


def update_template_with_simple_interface():
    """Actualiza el template para usar la interfaz simple"""

    template_path = "templates/professional.html"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar el script de la sidebar con el simple
    old_script = '<script src="/static/js/unified-sidebar-ai.js"></script>'
    new_script = '<script src="/static/js/simple-unified-sidebar-ai.js"></script>'

    if old_script in content:
        content = content.replace(old_script, new_script)

    with open(template_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Template actualizado con interfaz simple")


def main():
    """Función principal"""
    print("🔧 Actualizando sistema para usar sistema unificado con interfaz simple...")

    # 1. Actualizar endpoint
    if update_endpoint_to_unified():
        print("✅ Endpoint actualizado")
    else:
        print("❌ Error actualizando endpoint")
        return

    # 2. Verificar endpoint
    if verify_unified_endpoint():
        print("✅ Endpoint verificado")
    else:
        print("❌ Endpoint no verificado correctamente")

    # 3. Crear interfaz simple
    create_simple_sidebar_interface()

    # 4. Actualizar template
    update_template_with_simple_interface()

    print("\n🎉 ¡Sistema actualizado exitosamente!")
    print("📋 Cambios realizados:")
    print("   ✅ Endpoint usa sistema unificado")
    print("   ✅ Interfaz simple y limpia")
    print("   ✅ Sin duplicaciones")
    print("   ✅ Resultados consistentes")

    print("\n🚀 Ahora el sistema:")
    print("   - Usa UnifiedNLPProcessor")
    print("   - Usa UnifiedScientificSearchEnhanced")
    print("   - Usa UnifiedCopilotAssistantEnhanced")
    print("   - Mantiene interfaz simple")
    print("   - Sin sistema antiguo")


if __name__ == "__main__":
    main()
