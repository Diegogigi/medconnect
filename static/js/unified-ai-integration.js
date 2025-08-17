/**
 * Sistema de Integración Unificada de IA
 * Combina el sistema original y el sistema unificado en una sola experiencia
 */

class UnifiedAIIntegration {
    constructor() {
        this.isInitialized = false;
        this.currentSystem = 'unified'; // 'original' o 'unified'
        this.isProcessing = false;

        this.init();
    }

    init() {
        console.log('🚀 Inicializando Sistema de Integración Unificada...');

        // Inicializar componentes
        this.initUnifiedInterface();
        this.initSystemToggle();
        this.initEventListeners();

        this.isInitialized = true;
        console.log('✅ Sistema de Integración Unificada inicializado');
    }

    initUnifiedInterface() {
        // Crear interfaz unificada que reemplace ambos sistemas
        const sidebarContainer = document.getElementById('sidebarContainer');
        if (!sidebarContainer) return;

        // Limpiar sistemas anteriores
        this.cleanupOldSystems();

        // Crear nueva interfaz unificada
        this.createUnifiedInterface(sidebarContainer);
    }

    cleanupOldSystems() {
        // Remover elementos del sistema original
        const oldElements = [
            'real-time-analysis',
            'ai-insights',
            'scientific-evidence',
            'ai-recommendations'
        ];

        oldElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.remove();
            }
        });

        // Ocultar indicadores del sistema original
        const autoModeIndicator = document.querySelector('.auto-mode-indicator');
        if (autoModeIndicator) {
            autoModeIndicator.style.display = 'none';
        }
    }

    createUnifiedInterface(container) {
        const panelContent = container.querySelector('.panel-content');
        if (!panelContent) return;

        // Crear sección unificada de IA
        const unifiedSection = this.createUnifiedSection();

        // Insertar antes del chat existente
        const existingChat = panelContent.querySelector('.copilot-chat-elegant');
        if (existingChat) {
            existingChat.parentNode.insertBefore(unifiedSection, existingChat);
        } else {
            panelContent.appendChild(unifiedSection);
        }
    }

    createUnifiedSection() {
        const section = document.createElement('div');
        section.className = 'unified-ai-section card mb-3';
        section.id = 'unifiedAISection';

        section.innerHTML = `
            <div class="card-header d-flex justify-content-between align-items-center">
                <h6 class="mb-0">
                    <i class="fas fa-brain me-2"></i>
                    Sistema de IA Integrado
                </h6>
                <div class="system-toggle">
                    <button class="btn btn-sm btn-outline-primary" id="toggleSystemBtn">
                        <i class="fas fa-sync-alt"></i>
                        <span id="systemLabel">Modo Unificado</span>
                    </button>
                </div>
            </div>
            <div class="card-body">
                <div class="unified-status">
                    <div class="status-indicator">
                        <div class="status-dot" id="unifiedStatusDot"></div>
                        <span id="unifiedStatusText">IA lista para análisis</span>
                    </div>
                </div>
                
                <div class="unified-content">
                    <!-- Sección de Análisis -->
                    <div class="analysis-section mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-chart-line me-2"></i>
                            Análisis Clínico
                        </h6>
                        <div id="analysisContainer">
                            <div class="placeholder-content">
                                <i class="fas fa-lightbulb text-muted"></i>
                                <p>El análisis aparecerá aquí automáticamente</p>
                            </div>
                        </div>
                    </div>

                    <!-- Sección de Evidencia Científica -->
                    <div class="evidence-section mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-microscope me-2"></i>
                            Evidencia Científica
                        </h6>
                        <div id="unifiedEvidenceContainer">
                            <div class="placeholder-content">
                                <i class="fas fa-microscope text-muted"></i>
                                <p>La evidencia científica se cargará automáticamente</p>
                            </div>
                        </div>
                    </div>

                    <!-- Sección de Recomendaciones -->
                    <div class="recommendations-section mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-robot me-2"></i>
                            Recomendaciones IA
                        </h6>
                        <div id="unifiedRecommendationsContainer">
                            <div class="placeholder-content">
                                <i class="fas fa-robot text-muted"></i>
                                <p>Las recomendaciones aparecerán aquí</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Input unificado -->
                <div class="unified-input mt-3">
                    <div class="input-group">
                        <input type="text" 
                               id="unifiedAIInput" 
                               class="form-control" 
                               placeholder="Escribe aquí para preguntar a la IA..."
                               onkeydown="if(event.key==='Enter'){ unifiedAI.processUnifiedQuery(this.value); this.value='';}">
                        <button class="btn btn-primary" 
                                onclick="unifiedAI.processUnifiedQuery(document.getElementById('unifiedAIInput').value)">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        return section;
    }

    initSystemToggle() {
        const toggleBtn = document.getElementById('toggleSystemBtn');
        const systemLabel = document.getElementById('systemLabel');

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleSystem();
            });
        }
    }

    toggleSystem() {
        this.currentSystem = this.currentSystem === 'unified' ? 'original' : 'unified';
        this.updateSystemLabel();
        this.updateSystemInterface();

        const message = this.currentSystem === 'unified' ?
            '🔄 **Sistema Unificado activado** - Análisis integrado con evidencia científica' :
            '📊 **Sistema Original activado** - Análisis clínico tradicional';

        this.addMessageToChat(message, 'system');
    }

    updateSystemLabel() {
        const systemLabel = document.getElementById('systemLabel');
        if (systemLabel) {
            systemLabel.textContent = this.currentSystem === 'unified' ? 'Modo Unificado' : 'Modo Original';
        }
    }

    updateSystemInterface() {
        const statusText = document.getElementById('unifiedStatusText');
        if (statusText) {
            statusText.textContent = this.currentSystem === 'unified' ?
                'Tena Copilot lista para análisis' :
                'IA original lista para análisis';
        }
    }

    initEventListeners() {
        // Escuchar eventos de cambio de formulario
        window.addEventListener('formContextUpdated', (event) => {
            this.handleFormContextUpdate(event.detail);
        });

        // Escuchar comandos del chat
        this.interceptChatCommands();
    }

    interceptChatCommands() {
        // Interceptar la función original de agregar mensajes
        if (typeof window.agregarMensajeElegant === 'function') {
            const originalAddMessage = window.agregarMensajeElegant;
            window.agregarMensajeElegant = (mensaje, tipo) => {
                // Procesar comandos antes de agregar el mensaje
                if (tipo === 'user' && this.isAICommand(mensaje)) {
                    this.processUnifiedQuery(mensaje);
                    return;
                }
                originalAddMessage(mensaje, tipo);
            };
        }
    }

    isAICommand(mensaje) {
        const lowerMessage = mensaje.toLowerCase();
        const commands = [
            'busca papers',
            'buscar papers',
            'papers sobre',
            'evidencia científica',
            'estudios sobre',
            'analizar',
            'recomendar',
            'evaluar'
        ];

        return commands.some(cmd => lowerMessage.includes(cmd));
    }

    async processUnifiedQuery(query) {
        if (!query.trim()) return;

        console.log('🔍 Procesando consulta unificada:', query);
        this.isProcessing = true;
        this.updateStatus('processing', 'Procesando consulta...');

        try {
            // Agregar mensaje del usuario al chat
            this.addMessageToChat(query, 'user');

            if (this.currentSystem === 'unified') {
                await this.processUnifiedSystem(query);
            } else {
                await this.processOriginalSystem(query);
            }

        } catch (error) {
            console.error('❌ Error procesando consulta:', error);
            this.updateStatus('error', 'Error en el procesamiento');
            this.addMessageToChat(`❌ **Error:** ${error.message}`, 'error');
        } finally {
            this.isProcessing = false;
            this.updateStatus('ready', 'IA lista para análisis');
        }
    }

    async processUnifiedSystem(query) {
        // Usar el sistema unificado (endpoint analyze-enhanced)
        const formData = this.collectFormData();

        const response = await fetch('/api/copilot/analyze-enhanced', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                consulta: query,
                contexto_clinico: formData
            })
        });

        if (!response.ok) {
            throw new Error('Error en análisis unificado');
        }

        const data = await response.json();

        if (data.success) {
            this.displayUnifiedResults(data);
            this.addMessageToChat('✅ **Análisis unificado completado**', 'system');
        } else {
            throw new Error(data.error || 'Error en el análisis');
        }
    }

    async processOriginalSystem(query) {
        // Usar el sistema original (endpoint copilot/chat)
        const response = await fetch('/api/copilot/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: query,
                contexto: 'formulario_clinico'
            })
        });

        if (!response.ok) {
            throw new Error('Error en análisis original');
        }

        const data = await response.json();

        if (data.success) {
            this.displayOriginalResults(data);
            this.addMessageToChat('✅ **Análisis original completado**', 'system');
        } else {
            throw new Error(data.error || 'Error en el análisis');
        }
    }

    displayUnifiedResults(data) {
        // Mostrar evidencia científica
        if (data.evidence && data.evidence.length > 0) {
            this.displayEvidence(data.evidence);
        }

        // Mostrar análisis clínico
        if (data.clinical_analysis) {
            this.displayAnalysis(data.clinical_analysis);
        }

        // Mostrar recomendaciones
        if (data.clinical_analysis && data.clinical_analysis.recomendaciones) {
            this.displayRecommendations(data.clinical_analysis.recomendaciones);
        }
    }

    displayOriginalResults(data) {
        // Mostrar resultados del sistema original
        this.displayAnalysis({
            respuesta: data.response,
            tipo: 'original'
        });
    }

    displayEvidence(evidenceData) {
        const container = document.getElementById('unifiedEvidenceContainer');
        if (!container) return;

        if (!evidenceData || evidenceData.length === 0) {
            container.innerHTML = `
                <div class="placeholder-content">
                    <i class="fas fa-microscope text-muted"></i>
                    <p>No se encontró evidencia científica relevante</p>
                </div>
            `;
            return;
        }

        const evidenceHTML = evidenceData.map((paper, index) => {
            // Formatear autores
            const autores = paper.autores || [];
            let autoresFormateados = '';
            if (autores.length > 0) {
                if (autores.length <= 3) {
                    autoresFormateados = autores.join(', ');
                } else {
                    autoresFormateados = `${autores.slice(0, 3).join(', ')}, et al.`;
                }
            }

            // Formatear revista
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

            // Formatear DOI
            const doi = paper.doi || '';
            const doiFormateado = doi && doi !== "Sin DOI" ? `doi:${doi}` : '';

            return `
                <div class="evidence-item">
                    <div class="evidence-header">
                        <i class="fas fa-microscope text-primary"></i>
                        <span class="evidence-number">${index + 1}.</span>
                        <span class="evidence-title"><strong>${paper.titulo || paper.title || 'Sin título'}</strong></span>
                    </div>
                    <div class="evidence-content">
                        ${autoresFormateados ? `<div class="evidence-authors">📝 <strong>Autores:</strong> ${autoresFormateados}.</div>` : ''}
                        <div class="evidence-journal">📚 <strong>Revista:</strong> ${revistaFormateada}</div>
                        ${doiFormateado ? `<div class="evidence-doi">🔗 <strong>DOI:</strong> <a href="https://doi.org/${doi}" target="_blank">${doiFormateado}</a></div>` : ''}
                        ${paper.resumen || paper.abstract ? `<div class="evidence-abstract">📖 <strong>Resumen:</strong> ${(paper.resumen || paper.abstract).substring(0, 200)}...</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = evidenceHTML;
    }

    displayAnalysis(analysisData) {
        const container = document.getElementById('analysisContainer');
        if (!container) return;

        let content = '';

        if (analysisData.tipo === 'original') {
            content = `
                <div class="analysis-item">
                    <div class="analysis-header">
                        <i class="fas fa-chart-line text-info"></i>
                        <span class="analysis-title">Análisis Clínico</span>
                    </div>
                    <div class="analysis-content">
                        <p>${analysisData.respuesta}</p>
                    </div>
                </div>
            `;
        } else {
            content = `
                <div class="analysis-item">
                    <div class="analysis-header">
                        <i class="fas fa-chart-line text-info"></i>
                        <span class="analysis-title">Análisis Clínico Unificado</span>
                    </div>
                    <div class="analysis-content">
                        <p>Análisis completado con evidencia científica integrada.</p>
                    </div>
                </div>
            `;
        }

        container.innerHTML = content;
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('unifiedRecommendationsContainer');
        if (!container) return;

        if (!recommendations || recommendations.length === 0) {
            container.innerHTML = `
                <div class="placeholder-content">
                    <i class="fas fa-robot text-muted"></i>
                    <p>No se pudieron generar recomendaciones</p>
                </div>
            `;
            return;
        }

        const recommendationsHTML = recommendations.map(rec => `
            <div class="recommendation-item">
                <div class="recommendation-content">
                    <i class="fas fa-check-circle text-success me-2"></i>
                    <span>${rec}</span>
                </div>
            </div>
        `).join('');

        container.innerHTML = recommendationsHTML;
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

    handleFormContextUpdate(context) {
        // Actualizar contexto cuando cambia el formulario
        console.log('📝 Contexto actualizado:', context);
    }

    updateStatus(status, message) {
        const statusDot = document.getElementById('unifiedStatusDot');
        const statusText = document.getElementById('unifiedStatusText');

        if (statusDot) {
            statusDot.className = `status-dot ${status}`;
        }

        if (statusText) {
            statusText.textContent = message;
        }
    }

    addMessageToChat(message, type = 'system') {
        if (typeof agregarMensajeElegant === 'function') {
            agregarMensajeElegant(message, type);
        }
    }
}

// Inicializar el sistema cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.unifiedAI = new UnifiedAIIntegration();
});

// Exportar para uso global
window.UnifiedAIIntegration = UnifiedAIIntegration; 