/**
 * Sistema Unificado de IAs
 * Coordina todas las IAs para trabajar en conjunto según las solicitudes del chat
 */

class UnifiedAISystem {
    constructor() {
        this.ais = {
            nlp: null,
            search: null,
            clinical: null,
            copilot: null
        };

        this.currentContext = null;
        this.isInitialized = false;

        this.init();
    }

    async init() {
        console.log('🤖 Inicializando Sistema Unificado de IAs...');

        try {
            await this.initializeAIs();
            this.setupContextListener();
            this.setupChatIntegration();
            this.isInitialized = true;

            console.log('✅ Sistema Unificado de IAs inicializado');
        } catch (error) {
            console.error('❌ Error inicializando Sistema Unificado de IAs:', error);
        }
    }

    async initializeAIs() {
        // Inicializar NLP Processor
        this.ais.nlp = {
            process: async (text) => {
                try {
                    const response = await fetch('/api/nlp/process', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text })
                    });
                    return await response.json();
                } catch (error) {
                    console.error('Error en NLP:', error);
                    return { success: false, error: error.message };
                }
            }
        };

        // Inicializar Scientific Search
        this.ais.search = {
            search: async (query, context) => {
                try {
                    const response = await fetch('/api/copilot/search-enhanced', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            motivo_consulta: query,
                            contexto_clinico: context
                        })
                    });
                    return await response.json();
                } catch (error) {
                    console.error('Error en búsqueda científica:', error);
                    return { success: false, error: error.message };
                }
            }
        };

        // Inicializar Clinical Analysis
        this.ais.clinical = {
            analyze: async (context) => {
                try {
                    const response = await fetch('/api/copilot/analyze-enhanced', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            consulta: context.consulta || 'Análisis clínico',
                            contexto_clinico: context
                        })
                    });
                    return await response.json();
                } catch (error) {
                    console.error('Error en análisis clínico:', error);
                    return { success: false, error: error.message };
                }
            }
        };

        // Inicializar Copilot Assistant
        this.ais.copilot = {
            assist: async (query, context, evidence) => {
                try {
                    const response = await fetch('/api/copilot/assist', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            query,
                            context,
                            evidence
                        })
                    });
                    return await response.json();
                } catch (error) {
                    console.error('Error en asistente copilot:', error);
                    return { success: false, error: error.message };
                }
            }
        };
    }

    setupContextListener() {
        // Escuchar cambios en el contexto del formulario
        window.addEventListener('formContextUpdated', (event) => {
            this.currentContext = event.detail;
            console.log('📝 Contexto actualizado en Sistema Unificado:', this.currentContext);
        });
    }

    setupChatIntegration() {
        // Integrar con el sistema de chat centrado
        if (window.chatCenteredAI) {
            window.chatCenteredAI.setUnifiedSystem(this);
        }
    }

    // Método principal para procesar solicitudes del chat
    async processChatRequest(request, type) {
        console.log(`🤖 Procesando solicitud de chat: ${type}`, request);

        if (!this.currentContext) {
            return {
                success: false,
                message: 'No hay contexto clínico disponible. Por favor, completa el formulario.'
            };
        }

        try {
            switch (type) {
                case 'search':
                    return await this.handleSearchRequest(request);
                case 'analyze':
                    return await this.handleAnalysisRequest(request);
                case 'recommend':
                    return await this.handleRecommendationRequest(request);
                case 'evaluate':
                    return await this.handleEvaluationRequest(request);
                default:
                    return {
                        success: false,
                        message: 'Tipo de solicitud no reconocido.'
                    };
            }
        } catch (error) {
            console.error('Error procesando solicitud:', error);
            return {
                success: false,
                message: 'Error interno del sistema.'
            };
        }
    }

    async handleSearchRequest(request) {
        console.log('🔍 Procesando solicitud de búsqueda...');

        // 1. Procesar consulta con NLP
        const nlpResult = await this.ais.nlp.process(request.query || request);

        // 2. Realizar búsqueda científica
        const searchContext = {
            consulta: request.query || request,
            tipoAtencion: this.currentContext.tipoAtencion,
            antecedentes: this.currentContext.antecedentes,
            evaluacion: this.currentContext.evaluacion
        };

        const searchResult = await this.ais.search.search(request.query || request, searchContext);

        // 3. Procesar resultados con Copilot
        if (searchResult.success && searchResult.evidence) {
            const copilotResult = await this.ais.copilot.assist(
                'Analizar y explicar estos papers científicos',
                this.currentContext,
                searchResult.evidence
            );

            return {
                success: true,
                type: 'search',
                evidence: searchResult.evidence,
                analysis: copilotResult,
                nlp: nlpResult
            };
        }

        return searchResult;
    }

    async handleAnalysisRequest(request) {
        console.log('🧠 Procesando solicitud de análisis...');

        // 1. Procesar consulta con NLP
        const nlpResult = await this.ais.nlp.process(request.query || request);

        // 2. Realizar análisis clínico completo
        const analysisContext = {
            consulta: {
                motivo: this.currentContext.motivoConsulta,
                tipo: this.currentContext.tipoAtencion
            },
            paciente: {
                nombre: this.currentContext.pacienteNombre,
                rut: this.currentContext.pacienteRut,
                edad: this.currentContext.pacienteEdad
            },
            clinico: {
                antecedentes: this.currentContext.antecedentes,
                evaluacion: this.currentContext.evaluacion,
                diagnostico: this.currentContext.diagnostico,
                tratamiento: this.currentContext.tratamiento,
                observaciones: this.currentContext.observaciones
            }
        };

        const clinicalResult = await this.ais.clinical.analyze(analysisContext);

        // 3. Buscar evidencia científica relacionada
        const searchResult = await this.ais.search.search(
            this.currentContext.motivoConsulta,
            analysisContext
        );

        // 4. Integrar todo con Copilot
        const copilotResult = await this.ais.copilot.assist(
            'Proporcionar análisis clínico completo con evidencia científica',
            analysisContext,
            searchResult.evidence || []
        );

        return {
            success: true,
            type: 'analysis',
            clinical: clinicalResult,
            evidence: searchResult.evidence || [],
            copilot: copilotResult,
            nlp: nlpResult
        };
    }

    async handleRecommendationRequest(request) {
        console.log('💡 Procesando solicitud de recomendaciones...');

        // 1. Realizar análisis clínico
        const analysisResult = await this.handleAnalysisRequest(request);

        // 2. Generar recomendaciones específicas
        const recommendationContext = {
            ...analysisResult,
            request: request.query || request
        };

        const copilotResult = await this.ais.copilot.assist(
            'Generar recomendaciones clínicas específicas y detalladas',
            this.currentContext,
            analysisResult.evidence || []
        );

        return {
            success: true,
            type: 'recommendations',
            analysis: analysisResult,
            recommendations: copilotResult
        };
    }

    async handleEvaluationRequest(request) {
        console.log('📊 Procesando solicitud de evaluación...');

        // 1. Realizar análisis clínico
        const analysisResult = await this.handleAnalysisRequest(request);

        // 2. Generar evaluación estructurada
        const evaluationContext = {
            ...analysisResult,
            request: request.query || request
        };

        const copilotResult = await this.ais.copilot.assist(
            'Realizar evaluación clínica estructurada con escalas y criterios',
            this.currentContext,
            analysisResult.evidence || []
        );

        return {
            success: true,
            type: 'evaluation',
            analysis: analysisResult,
            evaluation: copilotResult
        };
    }

    // Método para obtener contexto actual
    getCurrentContext() {
        return this.currentContext;
    }

    // Método para verificar si hay contexto suficiente
    hasSufficientContext() {
        return !!(this.currentContext?.motivoConsulta && this.currentContext?.tipoAtencion);
    }

    // Método para obtener resumen del contexto
    getContextSummary() {
        if (!this.currentContext) return null;

        return {
            paciente: {
                nombre: this.currentContext.pacienteNombre,
                edad: this.currentContext.pacienteEdad
            },
            consulta: {
                motivo: this.currentContext.motivoConsulta,
                tipo: this.currentContext.tipoAtencion
            },
            clinico: {
                antecedentes: this.currentContext.antecedentes,
                evaluacion: this.currentContext.evaluacion,
                diagnostico: this.currentContext.diagnostico
            }
        };
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.unifiedAISystem = new UnifiedAISystem();
    });
} else {
    window.unifiedAISystem = new UnifiedAISystem();
} 