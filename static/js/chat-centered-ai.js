/**
 * Sistema de Chat Centrado para IAs
 * El chat es el centro de control donde el profesional solicita asistencia
 */

class ChatCenteredAI {
    constructor() {
        this.isInitialized = false;
        this.availableCommands = {
            'buscar': this.handleSearchRequest,
            'analizar': this.handleAnalysisRequest,
            'recomendar': this.handleRecommendationRequest,
            'evaluar': this.handleEvaluationRequest,
            'ayuda': this.handleHelpRequest
        };

        this.init();
    }

    init() {
        console.log('🤖 Inicializando ChatCenteredAI...');

        // Esperar a que el formulario esté disponible
        this.waitForFormObserver();
    }

    waitForFormObserver() {
        const checkInterval = setInterval(() => {
            if (window.formObserverAI) {
                clearInterval(checkInterval);
                this.setupChat();
                this.isInitialized = true;
                console.log('✅ ChatCenteredAI inicializado');
            }
        }, 100);

        // Timeout después de 10 segundos
        setTimeout(() => {
            if (!this.isInitialized) {
                clearInterval(checkInterval);
                console.warn('⚠️ FormObserverAI no disponible, inicializando sin contexto');
                this.setupChat();
                this.isInitialized = true;
            }
        }, 10000);
    }

    setupChat() {
        // Configurar el chat para procesar comandos
        this.setupMessageHandler();
        this.setupCommandSuggestions();
        this.showWelcomeMessage();
    }

    setupMessageHandler() {
        // Esperar a que la función agregarMensajeCopilot esté disponible
        const waitForFunction = () => {
            if (typeof window.agregarMensajeCopilot === 'function') {
                console.log('✅ Función agregarMensajeCopilot encontrada, configurando interceptación...');

                // Guardar la función original
                const originalAddMessage = window.agregarMensajeCopilot;

                // Interceptar la función
                window.agregarMensajeCopilot = (mensaje, tipo) => {
                    console.log('🔍 Interceptando mensaje:', mensaje, 'tipo:', tipo);

                    if (tipo === 'user' && this.isCommand(mensaje)) {
                        console.log('🤖 Comando detectado, procesando...');
                        this.processCommand(mensaje);
                        return;
                    }

                    // Llamar a la función original
                    originalAddMessage(mensaje, tipo);
                };

                console.log('✅ Interceptación configurada correctamente');
            } else {
                console.log('⏳ Esperando función agregarMensajeCopilot...');
                setTimeout(waitForFunction, 100);
            }
        };

        // Iniciar la espera
        waitForFunction();
    }

    isCommand(mensaje) {
        const lowerMessage = mensaje.toLowerCase();

        // Comandos específicos para búsqueda
        if (lowerMessage.includes('busca papers') ||
            lowerMessage.includes('buscar papers') ||
            lowerMessage.includes('papers sobre') ||
            lowerMessage.includes('evidencia científica') ||
            lowerMessage.includes('estudios sobre')) {
            return true;
        }

        // Otros comandos
        return Object.keys(this.availableCommands).some(cmd =>
            lowerMessage.includes(cmd)
        );
    }

    processCommand(mensaje) {
        console.log('🔍 Procesando comando:', mensaje);

        const lowerMessage = mensaje.toLowerCase();

        // Comandos específicos para búsqueda
        if (lowerMessage.includes('busca papers') ||
            lowerMessage.includes('buscar papers') ||
            lowerMessage.includes('papers sobre') ||
            lowerMessage.includes('evidencia científica') ||
            lowerMessage.includes('estudios sobre')) {
            console.log('🔍 Comando de búsqueda detectado');
            this.handleSearchRequest(mensaje);
            return;
        }

        // Determinar qué comando ejecutar
        for (const [command, handler] of Object.entries(this.availableCommands)) {
            if (lowerMessage.includes(command)) {
                handler.call(this, mensaje);
                return;
            }
        }

        // Si no es un comando reconocido, mostrar ayuda
        this.handleHelpRequest(mensaje);
    }

    async handleSearchRequest(mensaje) {
        const context = this.getFormContext();
        console.log('🔍 Contexto del formulario:', context);

        // Extraer tema de búsqueda del mensaje
        const searchTopic = this.extractSearchTopic(mensaje);
        console.log('🔍 Tema de búsqueda extraído:', searchTopic);

        if (!context.hasSufficientContext) {
            this.showMessage('⚠️ Necesito más información del caso clínico para buscar papers. Por favor, completa el motivo de consulta y tipo de atención.', 'warning');
            return;
        }

        this.showMessage(`🔍 Buscando papers científicos sobre: ${searchTopic}...`, 'info');

        try {
            const searchContext = context.getScientificSearchContext();
            // Usar el tema extraído del mensaje en lugar del contexto del formulario
            searchContext.consulta = searchTopic;
            console.log('🔍 Contexto de búsqueda:', searchContext);

            const response = await this.performScientificSearch(searchContext);

            if (response.success && response.evidence && response.evidence.length > 0) {
                this.displaySearchResults(response.evidence);
            } else {
                this.showMessage('❌ No se encontraron papers relevantes para este caso.', 'warning');
            }
        } catch (error) {
            console.error('Error en búsqueda:', error);
            this.showMessage('❌ Error al buscar papers científicos.', 'error');
        }
    }

    extractSearchTopic(mensaje) {
        const lowerMessage = mensaje.toLowerCase();

        // Patrones para extraer el tema de búsqueda
        const patterns = [
            /busca papers de (.+)/i,
            /buscar papers de (.+)/i,
            /papers sobre (.+)/i,
            /evidencia científica de (.+)/i,
            /estudios sobre (.+)/i,
            /busca papers (.+)/i,
            /buscar papers (.+)/i
        ];

        for (const pattern of patterns) {
            const match = mensaje.match(pattern);
            if (match && match[1]) {
                return match[1].trim();
            }
        }

        // Si no se encuentra un patrón específico, usar el mensaje completo
        return mensaje.replace(/busca papers|buscar papers|papers sobre|evidencia científica|estudios sobre/gi, '').trim();
    }

    async handleAnalysisRequest(mensaje) {
        const context = this.getFormContext();

        if (!context.hasSufficientContext) {
            this.showMessage('⚠️ Necesito más información del caso clínico para realizar el análisis. Por favor, completa el motivo de consulta.', 'warning');
            return;
        }

        this.showMessage('🧠 Analizando el caso clínico...', 'info');

        try {
            const analysisContext = context.getContextSummary();
            const response = await this.performClinicalAnalysis(analysisContext);

            if (response.success) {
                this.displayAnalysisResults(response);
            } else {
                this.showMessage('❌ Error al analizar el caso clínico.', 'error');
            }
        } catch (error) {
            console.error('Error en análisis:', error);
            this.showMessage('❌ Error al realizar el análisis clínico.', 'error');
        }
    }

    async handleRecommendationRequest(mensaje) {
        const context = this.getFormContext();

        if (!context.hasSufficientContext) {
            this.showMessage('⚠️ Necesito más información del caso clínico para generar recomendaciones.', 'warning');
            return;
        }

        this.showMessage('💡 Generando recomendaciones clínicas...', 'info');

        try {
            const recommendationContext = context.getContextSummary();
            const response = await this.generateRecommendations(recommendationContext);

            if (response.success) {
                this.displayRecommendations(response.recommendations);
            } else {
                this.showMessage('❌ Error al generar recomendaciones.', 'error');
            }
        } catch (error) {
            console.error('Error en recomendaciones:', error);
            this.showMessage('❌ Error al generar recomendaciones clínicas.', 'error');
        }
    }

    async handleEvaluationRequest(mensaje) {
        const context = this.getFormContext();

        if (!context.hasSufficientContext) {
            this.showMessage('⚠️ Necesito más información del caso clínico para realizar la evaluación.', 'warning');
            return;
        }

        this.showMessage('📊 Evaluando el caso clínico...', 'info');

        try {
            const evaluationContext = context.getContextSummary();
            const response = await this.performEvaluation(evaluationContext);

            if (response.success) {
                this.displayEvaluationResults(response);
            } else {
                this.showMessage('❌ Error al realizar la evaluación.', 'error');
            }
        } catch (error) {
            console.error('Error en evaluación:', error);
            this.showMessage('❌ Error al realizar la evaluación clínica.', 'error');
        }
    }

    handleHelpRequest(mensaje) {
        const helpMessage = `
🤖 **Comandos disponibles:**

🔍 **Buscar papers científicos:**
- "buscar papers sobre [tema]"
- "buscar evidencia científica"
- "necesito papers sobre [condición]"

🧠 **Analizar caso clínico:**
- "analizar el caso"
- "analizar la situación"
- "necesito análisis del caso"

💡 **Generar recomendaciones:**
- "recomendar tratamiento"
- "dar recomendaciones"
- "sugerir intervenciones"

📊 **Evaluar caso:**
- "evaluar el caso"
- "hacer evaluación"
- "valorar la situación"

❓ **Ayuda:**
- "ayuda"
- "comandos disponibles"
- "qué puedo hacer"
        `;

        this.showMessage(helpMessage, 'info');
    }

    getFormContext() {
        // Obtener datos directamente del formulario
        const getFormData = () => {
            const formData = {
                motivoConsulta: document.getElementById('motivoConsulta')?.value || '',
                tipoAtencion: document.getElementById('tipoAtencion')?.value || '',
                pacienteNombre: document.getElementById('pacienteNombre')?.value || '',
                pacienteRut: document.getElementById('pacienteRut')?.value || '',
                pacienteEdad: document.getElementById('pacienteEdad')?.value || '',
                antecedentes: document.getElementById('antecedentes')?.value || '',
                evaluacion: document.getElementById('evaluacion')?.value || '',
                diagnostico: document.getElementById('diagnostico')?.value || '',
                tratamiento: document.getElementById('tratamiento')?.value || '',
                observaciones: document.getElementById('observaciones')?.value || ''
            };
            return formData;
        };

        const formData = getFormData();
        const hasSufficientContext = !!(formData.motivoConsulta && formData.tipoAtencion);

        return {
            hasSufficientContext: hasSufficientContext,
            getContextSummary: () => ({
                paciente: {
                    nombre: formData.pacienteNombre,
                    edad: formData.pacienteEdad
                },
                consulta: {
                    motivo: formData.motivoConsulta,
                    tipo: formData.tipoAtencion
                },
                clinico: {
                    antecedentes: formData.antecedentes,
                    evaluacion: formData.evaluacion,
                    diagnostico: formData.diagnostico
                }
            }),
            getScientificSearchContext: () => ({
                consulta: formData.motivoConsulta,
                tipoAtencion: formData.tipoAtencion,
                antecedentes: formData.antecedentes,
                evaluacion: formData.evaluacion,
                diagnostico: formData.diagnostico
            })
        };
    }

    async performScientificSearch(context) {
        console.log('🔍 Enviando búsqueda científica:', context);

        const response = await fetch('/api/copilot/search-enhanced', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                motivo_consulta: context.consulta,
                contexto_clinico: context
            })
        });

        const data = await response.json();
        console.log('📊 Respuesta de búsqueda científica:', data);
        return data;
    }

    async performClinicalAnalysis(context) {
        console.log('🧠 Enviando análisis clínico:', context);

        const response = await fetch('/api/copilot/analyze-enhanced', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                consulta: context.consulta?.motivo || 'Análisis clínico',
                contexto_clinico: context
            })
        });

        const data = await response.json();
        console.log('📊 Respuesta de análisis clínico:', data);
        return data;
    }

    async generateRecommendations(context) {
        // Usar el sistema de análisis clínico para generar recomendaciones
        return await this.performClinicalAnalysis(context);
    }

    async performEvaluation(context) {
        // Usar el sistema de análisis clínico para evaluación
        return await this.performClinicalAnalysis(context);
    }

    displaySearchResults(evidence) {
        let message = '📚 **Papers científicos encontrados:**\n\n';

        evidence.slice(0, 5).forEach((paper, index) => {
            message += `**${index + 1}. ${paper.titulo || paper.title}**\n`;
            message += `📅 Año: ${paper.year || paper.año_publicacion || 'N/A'}\n`;
            message += `📊 Tipo: ${paper.tipo || paper.tipo_evidencia || 'Estudio'}\n`;
            message += `📈 Relevancia: ${Math.round((paper.relevancia || paper.relevancia_score || 0) * 100)}%\n`;

            // Mostrar DOI si existe y no es "Sin DOI"
            if (paper.doi && paper.doi !== "Sin DOI") {
                message += `🔗 DOI: ${paper.doi}\n`;
            }

            // Mostrar cita APA si existe
            if (paper.cita_apa) {
                message += `📖 **Cita APA:** ${paper.cita_apa}\n`;
            }

            message += `📝 ${(paper.resumen || paper.abstract || '').substring(0, 150)}...\n\n`;
        });

        this.showMessage(message, 'success');
    }

    displayAnalysisResults(response) {
        let message = '🧠 **Análisis clínico completado:**\n\n';

        if (response.nlp_analysis) {
            const nlp = response.nlp_analysis;
            message += `🔑 **Palabras clave:** ${nlp.palabras_clave?.join(', ') || 'No identificadas'}\n`;
            message += `📝 **Síntomas:** ${nlp.sintomas?.join(', ') || 'No identificados'}\n`;
            message += `🏥 **Entidades:** ${nlp.entidades?.join(', ') || 'No identificadas'}\n`;
            message += `📊 **Confianza:** ${Math.round((nlp.confianza || 0) * 100)}%\n\n`;
        }

        if (response.clinical_analysis?.recomendaciones) {
            message += '💡 **Recomendaciones:**\n';
            response.clinical_analysis.recomendaciones.forEach(rec => {
                message += `• ${rec}\n`;
            });
        }

        this.showMessage(message, 'success');
    }

    displayRecommendations(recommendations) {
        let message = '💡 **Recomendaciones clínicas:**\n\n';

        if (Array.isArray(recommendations)) {
            recommendations.forEach(rec => {
                message += `• ${rec}\n`;
            });
        } else if (typeof recommendations === 'string') {
            message += recommendations;
        }

        this.showMessage(message, 'success');
    }

    displayEvaluationResults(response) {
        let message = '📊 **Evaluación clínica completada:**\n\n';

        if (response.clinical_analysis) {
            const clinical = response.clinical_analysis;

            if (clinical.patologias?.length > 0) {
                message += '🏥 **Patologías identificadas:**\n';
                clinical.patologias.forEach(pat => {
                    message += `• ${pat}\n`;
                });
                message += '\n';
            }

            if (clinical.escalas?.length > 0) {
                message += '📊 **Escalas recomendadas:**\n';
                clinical.escalas.forEach(esc => {
                    message += `• ${esc}\n`;
                });
                message += '\n';
            }

            if (clinical.recomendaciones?.length > 0) {
                message += '💡 **Recomendaciones:**\n';
                clinical.recomendaciones.forEach(rec => {
                    message += `• ${rec}\n`;
                });
            }
        }

        this.showMessage(message, 'success');
    }

    showMessage(mensaje, tipo = 'info') {
        if (window.agregarMensajeCopilot) {
            window.agregarMensajeCopilot(mensaje, tipo);
        } else {
            console.log(`[${tipo.toUpperCase()}] ${mensaje}`);
        }
    }

    showWelcomeMessage() {
        const welcomeMessage = `
🤖 **¡Hola! Soy tu asistente IA clínico.**

Estoy observando el formulario y puedo ayudarte con:

🔍 **Búsqueda de papers científicos**
🧠 **Análisis de casos clínicos**  
💡 **Recomendaciones de tratamiento**
📊 **Evaluaciones clínicas**

**Para empezar, escribe:**
- "ayuda" - para ver todos los comandos
- "buscar papers sobre [tema]" - para buscar evidencia científica
- "analizar el caso" - para análisis clínico completo

**Importante:** Completa el formulario con la información del paciente para obtener mejores resultados.
        `;

        this.showMessage(welcomeMessage, 'info');
    }

    setupCommandSuggestions() {
        // Agregar sugerencias de comandos al chat
        const suggestions = [
            'buscar papers',
            'analizar caso',
            'recomendar tratamiento',
            'evaluar paciente',
            'ayuda'
        ];

        // Exponer sugerencias para el UI
        window.chatCommandSuggestions = suggestions;
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.chatCenteredAI = new ChatCenteredAI();
    });
} else {
    window.chatCenteredAI = new ChatCenteredAI();
} 