
/**
 * Sistema Unificado de IA para Sidebar - Interfaz Simple
 */

class SimpleUnifiedSidebarAI {
    constructor() {
        this.isInitialized = false;
        this.formData = {};
        this.isProcessing = false;
        this.autoMode = false; // DESACTIVADO: Solo comandos del chat
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
        // DESACTIVADO: No más análisis automático
        // Solo responde a comandos del chat
        console.log('🔇 Sistema Simple: Análisis automático desactivado');

        const formSelectors = [
            '#motivoConsulta',
            '#tipoAtencion',
            '#pacienteNombre',
            '#pacienteRut',
            '#pacienteEdad',
            '#antecedentes',
            '#evaluacion',
            '#diagnostico',
            '#tratamiento',
            '#observaciones'
        ];

        formSelectors.forEach(selector => {
            const element = document.querySelector(selector);
            if (element) {
                // Solo observar, no actuar automáticamente
                element.addEventListener('input', () => this.updateContextOnly());
                element.addEventListener('change', () => this.updateContextOnly());
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
        // DESACTIVADO: No más análisis automático
        console.log('🔇 Sistema Simple: Análisis automático desactivado');
    }

    updateContextOnly() {
        // Solo actualizar contexto, no analizar
        console.log('📝 Sistema Simple: Contexto actualizado (sin análisis automático)');

        // Notificar al sistema unificado sobre el cambio de contexto
        if (window.unifiedAISystem) {
            const formData = this.collectFormData();
            window.unifiedAISystem.currentContext = formData;
        }

        // Emitir evento para que otras IAs se enteren
        window.dispatchEvent(new CustomEvent('formContextUpdated', {
            detail: this.collectFormData()
        }));
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
        let message = '📊 **Análisis Unificado Completado**\n\n';

        // Palabras clave
        if (result.nlp_analysis && result.nlp_analysis.palabras_clave) {
            message += '🔑 **Palabras Clave:**\n';
            result.nlp_analysis.palabras_clave.forEach(palabra => {
                message += `- ${palabra.termino} (${palabra.confianza}%)\n`;
            });
            message += '\n';
        }

        // Región anatómica
        if (result.clinical_analysis && result.clinical_analysis.region_anatomica) {
            message += `📍 **Región:** ${result.clinical_analysis.region_anatomica}\n\n`;
        }

        // Patologías
        if (result.clinical_analysis && result.clinical_analysis.patologias) {
            message += '🏥 **Patologías:**\n';
            result.clinical_analysis.patologias.forEach(pat => {
                message += `- ${pat.nombre} (${pat.confianza}%)\n`;
            });
            message += '\n';
        }

        // Escalas
        if (result.clinical_analysis && result.clinical_analysis.escalas) {
            message += '📊 **Escalas Recomendadas:**\n';
            result.clinical_analysis.escalas.forEach(escala => {
                message += `- ${escala.nombre}\n`;
            });
            message += '\n';
        }

        // Evidencia científica
        if (result.evidence && result.evidence.length > 0) {
            message += `🔬 **Evidencia Científica:** ${result.evidence.length} artículos\n\n`;
        }

        // Recomendaciones
        if (result.clinical_analysis && result.clinical_analysis.recomendaciones) {
            message += '💡 **Recomendaciones:**\n';
            result.clinical_analysis.recomendaciones.forEach(rec => {
                message += `- ${rec}\n`;
            });
            message += '\n';
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
            tipoAtencion: '#tipoAtencion',
            pacienteNombre: '#pacienteNombre',
            pacienteRut: '#pacienteRut',
            pacienteEdad: '#pacienteEdad',
            antecedentes: '#antecedentes',
            evaluacion: '#evaluacion',
            diagnostico: '#diagnostico',
            tratamiento: '#tratamiento',
            observaciones: '#observaciones'
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
