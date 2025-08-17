
/**
 * Sistema Unificado de IA para Sidebar
 * Versión limpia sin duplicaciones
 */

class UnifiedSidebarAI {
    constructor() {
        this.isInitialized = false;
        this.formData = {};
        this.currentAnalysis = null;
        this.isProcessing = false;
        this.autoMode = true;
        this.debounceTimer = null;
        this.lastFormHash = '';
        
        this.config = {
            debounceDelay: 1000,
            maxRetries: 3,
            timeout: 30000,
            autoAnalyzeThreshold: 10
        };
        
        this.init();
    }

    init() {
        console.log('🚀 Inicializando Sistema Unificado de IA...');
        
        this.initFormWatchers();
        this.initEventListeners();
        this.initAutoMode();
        
        this.isInitialized = true;
        console.log('✅ Sistema Unificado de IA inicializado');
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

        const analyzeBtn = document.getElementById('manualAnalyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.triggerManualAnalysis());
        }
    }

    initAutoMode() {
        this.autoMode = true;
        this.updateAutoModeIndicator();
    }

    handleFormChange() {
        if (!this.autoMode || this.isProcessing) return;

        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.analyzeFormData();
        }, this.config.debounceDelay);
    }

    async analyzeFormData() {
        const formData = this.collectFormData();
        const formHash = this.hashFormData(formData);

        if (formHash === this.lastFormHash) return;
        this.lastFormHash = formHash;

        const totalContent = Object.values(formData).join(' ').trim();
        if (totalContent.length < this.config.autoAnalyzeThreshold) {
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
            console.error('❌ Error en análisis unificado:', error);
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
        this.currentAnalysis = result;
        this.displayUnifiedResults(result);
        this.updateAIStatus('success', 'Análisis completado');
    }

    displayUnifiedResults(result) {
        // Mostrar resultados en el chat
        let message = '📊 **Análisis Unificado Completado**\n\n';
        
        if (result.palabras_clave) {
            message += '🔑 **Palabras Clave Identificadas:**\n';
            result.palabras_clave.forEach(palabra => {
                message += `- ${palabra.termino} (${palabra.confianza}%)\n`;
            });
            message += '\n';
        }
        
        if (result.evidence && result.evidence.length > 0) {
            message += f'🔬 **Evidencia Científica:** {result.evidence.length} artículos encontrados\n\n';
        }
        
        if (result.recommendations && result.recommendations.length > 0) {
            message += '💡 **Recomendaciones Generadas**\n';
            result.recommendations.forEach(rec => {
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

        formData.timestamp = new Date().toISOString();
        formData.userId = this.getCurrentUserId();

        return formData;
    }

    buildConsultaFromFormData(formData) {
        const parts = [];
        
        if (formData.motivoConsulta) parts.push(`Motivo: ${formData.motivoConsulta}`);
        if (formData.sintomasPrincipales) parts.push(`Síntomas: ${formData.sintomasPrincipales}`);
        if (formData.antecedentesMedicos) parts.push(`Antecedentes: ${formData.antecedentesMedicos}`);
        if (formData.diagnosticoPresuntivo) parts.push(`Diagnóstico: ${formData.diagnosticoPresuntivo}`);
        
        return parts.join('. ');
    }

    hashFormData(formData) {
        const content = JSON.stringify(formData);
        return btoa(content).slice(0, 20);
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
        this.updateAutoModeIndicator();
        
        const message = this.autoMode ? 
            '🔄 **Modo automático activado** - La IA analizará automáticamente los cambios en el formulario' :
            '⏸️ **Modo automático desactivado** - Usa el botón "Analizar" para análisis manual';
        
        if (typeof agregarMensajeElegant === 'function') {
            agregarMensajeElegant(message, 'system');
        }
    }

    updateAutoModeIndicator() {
        const indicator = document.querySelector('.auto-mode-status');
        if (indicator) {
            indicator.innerHTML = this.autoMode ? 
                '<i class="fas fa-check-circle text-success"></i>' :
                '<i class="fas fa-pause-circle text-warning"></i>';
        }
    }

    async triggerManualAnalysis() {
        if (this.isProcessing) return;
        
        const formData = this.collectFormData();
        const totalContent = Object.values(formData).join(' ').trim();
        
        if (totalContent.length < this.config.autoAnalyzeThreshold) {
            if (typeof agregarMensajeElegant === 'function') {
                agregarMensajeElegant('⚠️ **Advertencia:** No hay suficiente información en el formulario para realizar un análisis significativo.', 'warning');
            }
            return;
        }
        
        await this.analyzeFormData();
    }

    getCurrentUserId() {
        return document.querySelector('meta[name="user-id"]')?.content || 'unknown';
    }
}

// Inicializar el sistema unificado cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.unifiedAI = new UnifiedSidebarAI();
});

// Exportar para uso global
window.UnifiedSidebarAI = UnifiedSidebarAI;
