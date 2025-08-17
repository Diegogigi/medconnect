/**
 * Sistema de IA Integrada en Sidebar con Captura Automática
 * Integra todos los sistemas mejorados: NLP, Búsqueda Científica, Copilot y Orquestación
 */

class EnhancedSidebarAI {
    constructor() {
        this.isInitialized = false;
        this.currentAnalysis = null;
        this.isProcessing = false;
        this.autoMode = false; // Desactivado por defecto
        this.debounceTimer = null;
        this.lastFormHash = '';

        // Configuración
        this.config = {
            debounceDelay: 1000, // 1 segundo
            maxRetries: 3,
            timeout: 30000,
            autoAnalyzeThreshold: 10 // caracteres mínimos para análisis automático
        };

        this.init();
    }

    init() {
        console.log('🚀 Inicializando Enhanced Sidebar AI...');

        // Inicializar componentes
        this.initFormWatchers();
        this.initSidebarUI();
        this.initEventListeners();
        this.initAutoMode();

        this.isInitialized = true;
        console.log('✅ Enhanced Sidebar AI inicializado');
    }

    initFormWatchers() {
        // DESACTIVADO: No más análisis automático
        // Las IAs ahora solo responden a comandos del chat
        console.log('🔇 Análisis automático desactivado - Solo responde a comandos del chat');

        // Solo observar para contexto, no para análisis automático
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

    initSidebarUI() {
        // Crear interfaz mejorada en la sidebar
        const sidebarContainer = document.getElementById('sidebarContainer');
        if (!sidebarContainer) return;

        // Agregar secciones de IA
        this.createAISections(sidebarContainer);

        // Inicializar indicadores de estado
        this.updateAIStatus('ready', 'IA lista para análisis');
    }

    createAISections(container) {
        const panelContent = container.querySelector('.panel-content');
        if (!panelContent) return;

        // Sección de análisis en tiempo real
        const realTimeSection = this.createSection('Análisis en Tiempo Real', 'real-time-analysis');
        realTimeSection.innerHTML = `
            <div class="ai-analysis-container">
                <div class="ai-status-indicator">
                    <div class="status-dot" id="aiStatusDot"></div>
                    <span id="aiStatusText">Esperando datos del formulario...</span>
                </div>
                <div class="ai-progress" id="aiProgress" style="display: none;">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <span id="progressText">Analizando...</span>
                </div>
            </div>
        `;

        // Sección de insights de IA
        const insightsSection = this.createSection('Insights de IA', 'ai-insights');
        insightsSection.innerHTML = `
            <div class="ai-insights-container" id="aiInsightsContainer">
                <div class="insight-placeholder">
                    <i class="fas fa-lightbulb text-muted"></i>
                    <p>Los insights aparecerán aquí automáticamente</p>
                </div>
            </div>
        `;

        // Sección de evidencia científica
        const evidenceSection = this.createSection('Evidencia Científica', 'scientific-evidence');
        evidenceSection.innerHTML = `
            <div class="evidence-container" id="evidenceContainer">
                <div class="evidence-placeholder">
                    <i class="fas fa-microscope text-muted"></i>
                    <p>La evidencia científica se cargará automáticamente</p>
                </div>
            </div>
        `;

        // Sección de recomendaciones
        const recommendationsSection = this.createSection('Recomendaciones IA', 'ai-recommendations');
        recommendationsSection.innerHTML = `
            <div class="recommendations-container" id="recommendationsContainer">
                <div class="recommendation-placeholder">
                    <i class="fas fa-robot text-muted"></i>
                    <p>Las recomendaciones aparecerán aquí</p>
                </div>
            </div>
        `;

        // Insertar secciones en el panel
        const existingContent = panelContent.querySelector('.copilot-chat-elegant');
        if (existingContent) {
            existingContent.parentNode.insertBefore(realTimeSection, existingContent);
            existingContent.parentNode.insertBefore(insightsSection, existingContent);
            existingContent.parentNode.insertBefore(evidenceSection, existingContent);
            existingContent.parentNode.insertBefore(recommendationsSection, existingContent);
        }
    }

    createSection(title, id) {
        const section = document.createElement('div');
        section.className = 'sidebar-section card mb-3';
        section.id = id;
        section.innerHTML = `
            <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">
                    <i class="fas fa-brain me-2"></i>
                    ${title}
                </h6>
                <button class="btn btn-sm btn-outline-secondary" onclick="enhancedAI.toggleSection('${id}')">
                    <i class="fas fa-chevron-down"></i>
                </button>
            </div>
            <div class="card-body">
                <!-- Contenido dinámico -->
            </div>
        `;
        return section;
    }

    initEventListeners() {
        // Botón de modo automático
        const autoModeBtn = document.getElementById('autoModeToggle');
        if (autoModeBtn) {
            autoModeBtn.addEventListener('click', () => this.toggleAutoMode());
        }

        // Botón de análisis manual
        const analyzeBtn = document.getElementById('manualAnalyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.triggerManualAnalysis());
        }
    }

    initAutoMode() {
        // DESACTIVADO: Modo automático desactivado
        // Solo responde a comandos del chat
        this.autoMode = false;
        this.updateAutoModeIndicator();
        console.log('🔇 Modo automático desactivado - Solo comandos del chat');
    }

    handleFormChange() {
        // DESACTIVADO: No más análisis automático
        // Solo se ejecuta por comandos del chat
        console.log('🔇 Análisis automático desactivado');
    }

    updateContextOnly() {
        // Solo actualizar contexto, no analizar
        console.log('📝 Contexto actualizado (sin análisis automático)');

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
        const formHash = this.hashFormData(formData);

        // Evitar análisis duplicados
        if (formHash === this.lastFormHash) return;
        this.lastFormHash = formHash;

        // Verificar si hay suficiente contenido
        const totalContent = Object.values(formData).join(' ').trim();
        if (totalContent.length < this.config.autoAnalyzeThreshold) {
            this.updateAIStatus('waiting', 'Esperando más información...');
            return;
        }

        console.log('🔍 Iniciando análisis automático de formulario...');
        this.isProcessing = true;
        this.updateAIStatus('processing', 'Analizando datos...');
        this.showProgress();

        try {
            // Análisis completo con todos los sistemas
            await this.performCompleteAnalysis(formData);
        } catch (error) {
            console.error('❌ Error en análisis automático:', error);
            this.updateAIStatus('error', 'Error en análisis');
            this.showError(error.message);
        } finally {
            this.isProcessing = false;
            this.hideProgress();
        }
    }

    collectFormData() {
        const formData = {};

        // Campos principales del formulario (actualizados)
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

        // Agregar información contextual
        formData.timestamp = new Date().toISOString();
        formData.userId = this.getCurrentUserId();

        return formData;
    }

    hashFormData(formData) {
        const content = JSON.stringify(formData);
        return btoa(content).slice(0, 20); // Hash simple
    }

    async performCompleteAnalysis(formData) {
        const consulta = this.buildConsultaFromFormData(formData);

        console.log('🔍 Iniciando análisis unificado con datos reales...');
        this.isProcessing = true;
        this.updateAIStatus('processing', 'Analizando datos con PubMed y Europe PMC...');
        this.showProgress();

        try {
            // Usar el endpoint unificado que devuelve datos REALES
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

            const results = await this.processUnifiedResponse(response);
            this.currentAnalysis = results;
            this.displayUnifiedResults(results);
            this.updateAIStatus('success', 'Análisis completado con datos reales');

        } catch (error) {
            console.error('❌ Error en análisis unificado:', error);
            this.updateAIStatus('error', 'Error en análisis');
            this.showError(error.message);
        } finally {
            this.isProcessing = false;
            this.hideProgress();
        }
    }

    async processUnifiedResponse(response) {
        try {
            const data = await response.json();

            if (data.success) {
                return {
                    nlp: data.nlp_analysis || {},
                    evidence: data.evidence || [], // Datos REALES de PubMed/Europe PMC
                    insights: data.insights || [],
                    recommendations: data.recommendations || [],
                    clinical_analysis: data.clinical_analysis || {}
                };
            } else {
                throw new Error(data.error || 'Error en el análisis');
            }
        } catch (error) {
            console.error('Error procesando respuesta:', error);
            throw error;
        }
    }

    displayUnifiedResults(results) {
        // Mostrar insights basados en datos reales
        if (results.insights && results.insights.length > 0) {
            this.displayInsights(results.insights);
        } else {
            this.displayInsights([]);
        }

        // Mostrar evidencia científica REAL
        if (results.evidence && results.evidence.length > 0) {
            this.displayEvidence(results.evidence);
        } else {
            this.displayEvidence([]);
        }

        // Mostrar recomendaciones basadas en evidencia real
        if (results.recommendations && results.recommendations.length > 0) {
            this.displayRecommendations(results.recommendations);
        } else {
            this.displayRecommendations([]);
        }

        // Actualizar chat con datos reales
        this.updateChatWithUnifiedResults(results);
    }

    updateChatWithUnifiedResults(results) {
        let message = '📊 **Análisis Unificado Completado**\n\n';

        // Mostrar palabras clave del análisis NLP
        if (results.nlp && results.nlp.palabras_clave) {
            message += '🔑 **Palabras Clave Identificadas:**\n';
            results.nlp.palabras_clave.forEach(palabra => {
                message += `- ${palabra.termino} (${palabra.confianza}%)\n`;
            });
            message += '\n';
        }

        // Mostrar evidencia científica REAL (no simulada)
        if (results.evidence && results.evidence.length > 0) {
            message += `🔬 **Evidencia Científica Real:** ${results.evidence.length} artículos encontrados\n\n`;

            // Mostrar detalles de los papers REALES
            results.evidence.slice(0, 5).forEach((paper, index) => {
                // Formatear autores REALES
                const autores = paper.autores || [];
                let autoresFormateados = '';
                if (autores.length > 0) {
                    if (autores.length <= 3) {
                        autoresFormateados = autores.join(', ');
                    } else {
                        autoresFormateados = `${autores.slice(0, 3).join(', ')}, et al.`;
                    }
                }

                // Formatear revista REAL
                const revista = paper.journal || paper.revista || 'Revista no especificada';
                const año = paper.año_publicacion || paper.year || 'N/A';
                const volumen = paper.volumen || '';
                const numero = paper.numero || '';
                const paginas = paper.paginas || '';

                let revistaFormateada = revista;
                if (año !== 'N/A') {
                    revistaFormateada += `. ${año}`;
                    if (volumen) {
                        revistaFormateada += `;${volumen}`;
                        if (numero) {
                            revistaFormateada += `(${numero})`;
                        }
                        if (paginas) {
                            revistaFormateada += `:${paginas}`;
                        }
                    }
                    revistaFormateada += '.';
                }

                // Formatear DOI REAL
                const doi = paper.doi || '';
                const doiFormateado = doi && doi !== "Sin DOI" ? `doi:${doi}` : '';

                message += `**${index + 1}. ${paper.titulo || paper.title || 'Sin título'}**\n`;
                if (autoresFormateados) {
                    message += `📝 **Autores:** ${autoresFormateados}.\n`;
                }
                message += `📚 **Revista:** ${revistaFormateada}\n`;
                if (doiFormateado) {
                    message += `🔗 **DOI:** ${doiFormateado}\n`;
                }
                if (paper.resumen || paper.abstract) {
                    message += `📖 **Resumen:** ${(paper.resumen || paper.abstract).substring(0, 150)}...\n`;
                }
                if (paper.relevancia_score || paper.relevancia) {
                    const relevancia = Math.round((paper.relevancia_score || paper.relevancia || 0) * 100);
                    message += `📊 **Relevancia:** ${relevancia}%\n`;
                }
                message += '\n';
            });
        } else {
            message += '🔬 **Evidencia Científica:** No se encontraron artículos relevantes\n\n';
        }

        // Mostrar recomendaciones clínicas REALES
        if (results.clinical_analysis && results.clinical_analysis.recomendaciones && results.clinical_analysis.recomendaciones.length > 0) {
            message += '💡 **Recomendaciones Clínicas**\n';
            results.clinical_analysis.recomendaciones.forEach(rec => {
                message += `- ${rec}\n`;
            });
            message += '\n';
        } else if (results.recommendations && results.recommendations.length > 0) {
            message += '💡 **Recomendaciones Generadas**\n';
            results.recommendations.forEach(rec => {
                message += `- ${rec}\n`;
            });
            message += '\n';
        }

        message += '✅ Análisis unificado completado exitosamente con datos reales de PubMed y Europe PMC.';

        if (typeof agregarMensajeElegant === 'function') {
            agregarMensajeElegant(message, 'system');
        }
    }

    displayInsights(insights) {
        const container = document.getElementById('aiInsightsContainer');
        if (!container) return;

        if (insights.length === 0) {
            container.innerHTML = `
                <div class="insight-placeholder">
                    <i class="fas fa-lightbulb text-muted"></i>
                    <p>No se encontraron insights relevantes</p>
                </div>
            `;
            return;
        }

        const insightsHTML = insights.map(insight => `
            <div class="insight-item">
                <div class="insight-header">
                    <i class="fas fa-lightbulb text-warning"></i>
                    <span class="insight-title">${insight.titulo}</span>
                    <span class="insight-confidence">${Math.round(insight.confianza * 100)}%</span>
                </div>
                <div class="insight-content">
                    ${this.formatInsightContent(insight.contenido)}
                </div>
            </div>
        `).join('');

        container.innerHTML = insightsHTML;
    }

    displayEvidence(evidenceData) {
        const container = document.getElementById('evidenceContainer');
        if (!container) return;

        // Usar únicamente datos REALES de la búsqueda científica
        const papers = Array.isArray(evidenceData) ? evidenceData : (evidenceData.papers_encontrados || []);

        if (!papers || papers.length === 0) {
            container.innerHTML = `
                <div class="evidence-placeholder">
                    <i class="fas fa-microscope text-muted"></i>
                    <p>No se encontró evidencia científica relevante</p>
                    <small class="text-muted">Los datos mostrados provienen únicamente de PubMed y Europe PMC</small>
                </div>
            `;
            return;
        }

        const evidenceHTML = papers.map((paper, index) => {
            // Formatear autores REALES
            const autores = paper.autores || [];
            let autoresFormateados = '';
            if (autores.length > 0) {
                if (autores.length <= 3) {
                    autoresFormateados = autores.join(', ');
                } else {
                    autoresFormateados = `${autores.slice(0, 3).join(', ')}, et al.`;
                }
            }

            // Formatear revista REAL
            const revista = paper.journal || paper.revista || 'Revista no especificada';
            const año = paper.año_publicacion || paper.year || 'N/A';
            const volumen = paper.volumen || '';
            const numero = paper.numero || '';
            const paginas = paper.paginas || '';

            let revistaFormateada = revista;
            if (año !== 'N/A') {
                revistaFormateada += `. ${año}`;
                if (volumen) {
                    revistaFormateada += `;${volumen}`;
                    if (numero) {
                        revistaFormateada += `(${numero})`;
                    }
                    if (paginas) {
                        revistaFormateada += `:${paginas}`;
                    }
                }
                revistaFormateada += '.';
            }

            // Formatear DOI REAL
            const doi = paper.doi || '';
            const doiFormateado = doi && doi !== "Sin DOI" ? `doi:${doi}` : '';

            // Calcular relevancia REAL
            const relevancia = Math.round((paper.relevancia_score || paper.relevancia || 0) * 100);

            return `
                <div class="evidence-item">
                    <div class="evidence-header">
                        <i class="fas fa-microscope text-primary"></i>
                        <span class="evidence-number">${index + 1}.</span>
                        <span class="evidence-title"><strong>${paper.titulo || paper.title || 'Sin título'}</strong></span>
                        <span class="evidence-relevancia">${relevancia}%</span>
                    </div>
                    <div class="evidence-content">
                        ${autoresFormateados ? `<div class="evidence-authors">📝 <strong>Autores:</strong> ${autoresFormateados}.</div>` : ''}
                        <div class="evidence-journal">📚 <strong>Revista:</strong> ${revistaFormateada}</div>
                        ${doiFormateado ? `<div class="evidence-doi">🔗 <strong>DOI:</strong> <a href="https://doi.org/${doi}" target="_blank">${doiFormateado}</a></div>` : ''}
                        ${paper.resumen || paper.abstract ? `<div class="evidence-abstract">📖 <strong>Resumen:</strong> ${(paper.resumen || paper.abstract).substring(0, 200)}...</div>` : ''}
                        <div class="evidence-source">🔬 <strong>Fuente:</strong> ${paper.fuente || 'PubMed/Europe PMC'}</div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = evidenceHTML;
    }

    displayRecommendations(recommendationsData) {
        const container = document.getElementById('recommendationsContainer');
        if (!container) return;

        if (!recommendationsData.response) {
            container.innerHTML = `
                <div class="recommendation-placeholder">
                    <i class="fas fa-robot text-muted"></i>
                    <p>No se pudieron generar recomendaciones</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="recommendation-item">
                <div class="recommendation-header">
                    <i class="fas fa-robot text-success"></i>
                    <span class="recommendation-title">Recomendaciones IA</span>
                </div>
                <div class="recommendation-content">
                    ${this.formatRecommendationContent(recommendationsData.response)}
                </div>
            </div>
        `;
    }

    formatInsightContent(content) {
        if (Array.isArray(content)) {
            return content.map(item => `<div class="insight-bullet">• ${item}</div>`).join('');
        }
        return `<p>${content}</p>`;
    }

    formatRecommendationContent(content) {
        // Formatear recomendaciones del copilot
        return `<p>${content}</p>`;
    }

    buildConsultaFromFormData(formData) {
        const parts = [];

        if (formData.motivoConsulta) parts.push(`Motivo: ${formData.motivoConsulta}`);
        if (formData.sintomasPrincipales) parts.push(`Síntomas: ${formData.sintomasPrincipales}`);
        if (formData.antecedentesMedicos) parts.push(`Antecedentes: ${formData.antecedentesMedicos}`);
        if (formData.diagnosticoPresuntivo) parts.push(`Diagnóstico: ${formData.diagnosticoPresuntivo}`);

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

    updateProgress(percentage, text) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }

        if (progressText) {
            progressText.textContent = text;
        }
    }

    showError(message) {
        this.updateAIStatus('error', `Error: ${message}`);

        // Mostrar error en chat
        this.addMessageToChat(`❌ **Error en análisis:** ${message}`, 'error');
    }

    toggleAutoMode() {
        this.autoMode = !this.autoMode;
        this.updateAutoModeIndicator();

        const message = this.autoMode ?
            '🔄 **Modo automático activado** - La IA analizará automáticamente los cambios en el formulario' :
            '⏸️ **Modo automático desactivado** - Usa el botón "Analizar" para análisis manual';

        this.addMessageToChat(message, 'system');
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
            this.addMessageToChat('⚠️ **Advertencia:** No hay suficiente información en el formulario para realizar un análisis significativo.', 'warning');
            return;
        }

        await this.analyzeFormData();
    }

    toggleSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (!section) return;

        const cardBody = section.querySelector('.card-body');
        const button = section.querySelector('.btn i');

        if (cardBody.style.display === 'none') {
            cardBody.style.display = 'block';
            button.className = 'fas fa-chevron-down';
        } else {
            cardBody.style.display = 'none';
            button.className = 'fas fa-chevron-right';
        }
    }

    addMessageToChat(message, type = 'system') {
        // Implementar agregar mensaje al chat existente
        if (typeof agregarMensajeElegant === 'function') {
            agregarMensajeElegant(message, type);
        }
    }

    getCurrentUserId() {
        // Obtener ID del usuario actual desde la sesión
        return document.querySelector('meta[name="user-id"]')?.content || 'unknown';
    }
}

// Inicializar el sistema cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedAI = new EnhancedSidebarAI();
});

// Exportar para uso global
window.EnhancedSidebarAI = EnhancedSidebarAI; 