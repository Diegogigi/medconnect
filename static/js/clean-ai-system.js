/**
 * Sistema de IA Limpio y Simple
 * Reemplaza todos los sistemas problemáticos con una solución única
 */

class CleanAISystem {
    constructor() {
        this.isInitialized = false;
        this.isProcessing = false;
        this.currentQuery = '';

        this.init();
    }

    init() {
        console.log('🧹 Inicializando Sistema de IA Limpio...');

        // Limpiar todos los sistemas anteriores
        this.cleanupAllSystems();

        // Crear interfaz limpia
        this.createCleanInterface();

        // Configurar eventos
        this.setupEventListeners();

        this.isInitialized = true;
        console.log('✅ Sistema de IA Limpio inicializado');
    }

    cleanupAllSystems() {
        // Remover todos los sistemas anteriores
        const elementsToRemove = [
            'unifiedAISection',
            'real-time-analysis',
            'ai-insights',
            'scientific-evidence',
            'ai-recommendations',
            'evidenceContainer',
            'resultsArea',
            'evidenceCardsContainer'
        ];

        elementsToRemove.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.remove();
            }
        });

        // Ocultar indicadores problemáticos
        const indicators = document.querySelectorAll('.auto-mode-indicator, .typing-elegant');
        indicators.forEach(indicator => {
            indicator.style.display = 'none';
        });

        // Limpiar mensajes duplicados del chat
        this.cleanupChatMessages();
    }

    cleanupChatMessages() {
        const chatContainer = document.querySelector('.copilot-chat-elegant');
        if (chatContainer) {
            const messages = chatContainer.querySelectorAll('.message');
            let errorCount = 0;
            let successCount = 0;

            messages.forEach(message => {
                const text = message.textContent || '';
                if (text.includes('❌ **Error:**') || text.includes('✅ **Análisis unificado completado**')) {
                    message.remove();
                    if (text.includes('❌ **Error:**')) errorCount++;
                    if (text.includes('✅ **Análisis unificado completado**')) successCount++;
                }
            });

            console.log(`🧹 Limpiados ${errorCount} errores y ${successCount} mensajes duplicados`);
        }
    }

    createCleanInterface() {
        const sidebarContainer = document.getElementById('sidebarContainer');
        if (!sidebarContainer) return;

        const panelContent = sidebarContainer.querySelector('.panel-content');
        if (!panelContent) return;

        // Crear sección limpia
        const cleanSection = document.createElement('div');
        cleanSection.className = 'clean-ai-section card mb-3';
        cleanSection.id = 'cleanAISection';

        cleanSection.innerHTML = `
            <div class="card-header">
                <h6 class="mb-0">
                    <i class="fas fa-robot me-2"></i>
                    
                </h6>
            </div>
            <div class="card-body">
                <div class="ai-status mb-3">
                    <div class="status-indicator">
                        <div class="status-dot ready" id="aiStatusDot"></div>
                        <span id="aiStatusText">IA lista para consultas</span>
                    </div>
                </div>
                
                <div class="ai-content">
                    <!-- Sección de Análisis -->
                    <div class="analysis-section mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-chart-line me-2"></i>
                            Análisis Clínico
                        </h6>
                        <div id="cleanAnalysisContainer">
                            <div class="placeholder-content">
                                <i class="fas fa-lightbulb text-muted"></i>
                                <p>El análisis aparecerá aquí</p>
                            </div>
                        </div>
                    </div>

                    <!-- Sección de Evidencia Científica -->
                    <div class="evidence-section mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-microscope me-2"></i>
                            Evidencia Científica
                        </h6>
                        <div id="cleanEvidenceContainer">
                            <div class="placeholder-content">
                                <i class="fas fa-microscope text-muted"></i>
                                <p>La evidencia científica se cargará aquí</p>
                            </div>
                        </div>
                    </div>

                    <!-- Sección de Recomendaciones -->
                    <div class="recommendations-section mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-clipboard-list me-2"></i>
                            Recomendaciones
                        </h6>
                        <div id="cleanRecommendationsContainer">
                            <div class="placeholder-content">
                                <i class="fas fa-clipboard-list text-muted"></i>
                                <p>Las recomendaciones aparecerán aquí</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Input limpio -->
                <div class="clean-input mt-3">
                    <div class="input-group">
                        <input type="text" 
                               id="cleanAIInput" 
                               class="form-control" 
                               placeholder="Escribe tu consulta médica aquí..."
                               onkeydown="if(event.key==='Enter'){ cleanAI.processQuery(this.value); this.value='';}">
                        <button class="btn btn-primary" 
                                onclick="cleanAI.processQuery(document.getElementById('cleanAIInput').value)">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Insertar antes del chat existente
        const existingChat = panelContent.querySelector('.copilot-chat-elegant');
        if (existingChat) {
            existingChat.parentNode.insertBefore(cleanSection, existingChat);
        } else {
            panelContent.appendChild(cleanSection);
        }
    }

    setupEventListeners() {
        // Interceptar comandos del chat de manera segura
        this.interceptChatCommands();

        // Escuchar cambios del formulario
        this.setupFormListener();
    }

    interceptChatCommands() {
        // Esperar a que la función esté disponible
        const waitForFunction = () => {
            if (typeof window.agregarMensajeElegant === 'function') {
                const originalAddMessage = window.agregarMensajeElegant;
                window.agregarMensajeElegant = (mensaje, tipo) => {
                    // Solo procesar mensajes de usuario que sean comandos
                    if (tipo === 'user' && this.isMedicalQuery(mensaje)) {
                        this.processQuery(mensaje);
                        return;
                    }
                    originalAddMessage(mensaje, tipo);
                };
                console.log('✅ Chat interceptado de manera segura');
            } else {
                setTimeout(waitForFunction, 100);
            }
        };
        waitForFunction();
    }

    isMedicalQuery(mensaje) {
        const lowerMessage = mensaje.toLowerCase();
        const medicalTerms = [
            'busca', 'buscar', 'papers', 'evidencia', 'estudios',
            'analizar', 'recomendar', 'evaluar', 'dolor', 'tratamiento',
            'diagnóstico', 'síntomas', 'rehabilitación'
        ];

        return medicalTerms.some(term => lowerMessage.includes(term));
    }

    setupFormListener() {
        // Escuchar cambios del formulario de manera simple
        const formFields = [
            'motivoConsulta', 'tipoAtencion', 'pacienteNombre',
            'antecedentes', 'evaluacion', 'diagnostico'
        ];

        formFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('change', () => {
                    console.log(`📝 Campo ${fieldId} actualizado`);
                });
            }
        });
    }

    async processQuery(query) {
        if (!query.trim() || this.isProcessing) return;

        console.log('🔍 Procesando consulta:', query);
        this.isProcessing = true;
        this.currentQuery = query;
        this.updateStatus('processing', 'Procesando consulta...');

        try {
            // Agregar mensaje del usuario al chat
            this.addMessageToChat(query, 'user');

            // Realizar análisis
            await this.performAnalysis(query);

        } catch (error) {
            console.error('❌ Error procesando consulta:', error);
            this.updateStatus('error', 'Error en el procesamiento');
            this.addMessageToChat(`❌ **Error:** ${error.message}`, 'error');
        } finally {
            this.isProcessing = false;
            this.updateStatus('ready', 'IA lista para consultas');
        }
    }

    async performAnalysis(query) {
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
            throw new Error('Error en el análisis');
        }

        const data = await response.json();

        if (data.success) {
            this.displayResults(data);
            this.addMessageToChat('✅ **Análisis completado exitosamente**', 'system');
        } else {
            throw new Error(data.error || 'Error en el análisis');
        }
    }

    displayResults(data) {
        // Mostrar evidencia científica
        if (data.evidence && data.evidence.length > 0) {
            this.displayEvidence(data.evidence);
        } else {
            this.displayEvidence([]);
        }

        // Mostrar análisis clínico
        if (data.clinical_analysis) {
            this.displayAnalysis(data.clinical_analysis);
        }

        // Mostrar recomendaciones
        if (data.clinical_analysis && data.clinical_analysis.recomendaciones) {
            this.displayRecommendations(data.clinical_analysis.recomendaciones);
        }

        // INTEGRACIÓN MedlinePlus: Mostrar educación del paciente
        if (data.patient_education && data.patient_education.show_panel) {
            this.displayPatientEducation(data.patient_education);
        }
    }

    displayEvidence(evidenceData) {
        const container = document.getElementById('cleanEvidenceContainer');
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

            let revistaFormateada = revista;
            if (año !== 'N/A') {
                revistaFormateada += `. ${año}`;
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
        const container = document.getElementById('cleanAnalysisContainer');
        if (!container) return;

        let content = `
            <div class="analysis-item">
                <div class="analysis-header">
                    <i class="fas fa-chart-line text-info"></i>
                    <span class="analysis-title">Análisis Clínico</span>
                </div>
                <div class="analysis-content">
                    <p>Análisis completado para: <strong>${this.currentQuery}</strong></p>
                </div>
            </div>
        `;

        container.innerHTML = content;
    }

    displayRecommendations(recommendations) {
        const container = document.getElementById('cleanRecommendationsContainer');
        if (!container) return;

        if (!recommendations || recommendations.length === 0) {
            container.innerHTML = `
                <div class="placeholder-content">
                    <i class="fas fa-clipboard-list text-muted"></i>
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

    updateStatus(status, message) {
        const statusDot = document.getElementById('aiStatusDot');
        const statusText = document.getElementById('aiStatusText');

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

    displayPatientEducation(educationData) {
        const container = document.getElementById('cleanPatientEducationContainer');
        if (!container) {
            // Crear contenedor si no existe
            const evidenceContainer = document.getElementById('cleanEvidenceContainer');
            if (evidenceContainer) {
                const educationContainer = document.createElement('div');
                educationContainer.id = 'cleanPatientEducationContainer';
                educationContainer.className = 'patient-education-section card mb-3';
                evidenceContainer.parentNode.insertBefore(educationContainer, evidenceContainer.nextSibling);
            } else {
                return;
            }
        }

        const educationHTML = `
            <div class="card-header">
                <h6 class="mb-0">
                    <i class="fas fa-graduation-cap text-success me-2"></i>
                    📚 Educación del Paciente
                </h6>
            </div>
            <div class="card-body">
                <div class="education-content">
                    <div class="education-title">
                        <strong>${educationData.title || 'Información Educativa'}</strong>
                    </div>
                    <div class="education-summary">
                        ${educationData.content || 'Información educativa disponible'}
                    </div>
                    <div class="education-source">
                        <small class="text-muted">
                            <i class="fas fa-external-link-alt me-1"></i>
                            Fuente: ${educationData.source || 'MedlinePlus.gov'}
                        </small>
                    </div>
                    ${educationData.url ? `
                        <div class="education-action mt-2">
                            <a href="${educationData.url}" target="_blank" class="btn btn-outline-success btn-sm">
                                <i class="fas fa-external-link-alt me-1"></i>
                                Leer más en MedlinePlus
                            </a>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        container.innerHTML = educationHTML;

        // Agregar mensaje al chat
        const chatMessage = `📚 **Educación del Paciente:** ${educationData.title}\n\n${educationData.content}\n\n🔗 [Leer más en MedlinePlus](${educationData.url})`;
        this.addMessageToChat(chatMessage, 'system');
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.cleanAI = new CleanAISystem();
});

// Exportar para uso global
window.CleanAISystem = CleanAISystem; 