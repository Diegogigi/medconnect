/**
 * Sistema de Limpieza Forzada
 * Elimina completamente todos los sistemas anteriores y crea uno nuevo
 */

class ForceCleanSystem {
    constructor() {
        this.isInitialized = false;
        this.init();
    }

    init() {
        console.log('🧹 Inicializando Limpieza Forzada...');

        // Forzar limpieza inmediata
        this.forceCleanup();

        // Crear sistema único
        this.createUniqueSystem();

        this.isInitialized = true;
        console.log('✅ Limpieza Forzada completada');
    }

    forceCleanup() {
        console.log('🧹 Forzando limpieza de todos los sistemas...');

        // 1. Remover TODOS los elementos de IA
        const selectorsToRemove = [
            '#unifiedAISection',
            '#real-time-analysis',
            '#ai-insights',
            '#scientific-evidence',
            '#ai-recommendations',
            '#evidenceContainer',
            '#resultsArea',
            '#evidenceCardsContainer',
            '.auto-mode-indicator',
            '.typing-elegant',
            '.unified-ai-section',
            '.clean-ai-section'
        ];

        selectorsToRemove.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                console.log(`🗑️ Eliminando: ${selector}`);
                element.remove();
            });
        });

        // 2. Remover elementos por texto
        this.removeElementsByText([
            'IA lista para análisis',
            'Esperando datos del formulario',
            'Los insights aparecerán aquí automáticamente',
            'La evidencia científica se cargará automáticamente',
            'Las recomendaciones aparecerán aquí',
            'Tena Copilot',
            'Escribe aquí para preguntar a la IA'
        ]);

        // 3. Limpiar chat completamente
        this.cleanupChatCompletely();

        // 4. Deshabilitar scripts problemáticos
        this.disableProblematicScripts();
    }

    removeElementsByText(texts) {
        texts.forEach(text => {
            const elements = document.querySelectorAll('*');
            elements.forEach(element => {
                if (element.textContent && element.textContent.includes(text)) {
                    // Verificar si es un elemento de IA
                    if (this.isAIElement(element)) {
                        console.log(`🗑️ Eliminando elemento con texto: ${text}`);
                        element.remove();
                    }
                }
            });
        });
    }

    isAIElement(element) {
        // Verificar si el elemento es parte de un sistema de IA
        const aiClasses = [
            'ai', 'unified', 'clean', 'sidebar', 'panel', 'card',
            'analysis', 'evidence', 'recommendations', 'insights'
        ];

        const className = element.className || '';
        const id = element.id || '';

        return aiClasses.some(aiClass =>
            className.toLowerCase().includes(aiClass) ||
            id.toLowerCase().includes(aiClass)
        );
    }

    cleanupChatCompletely() {
        const chatContainer = document.querySelector('.copilot-chat-elegant');
        if (chatContainer) {
            const messages = chatContainer.querySelectorAll('.message');
            let removedCount = 0;

            messages.forEach(message => {
                const text = message.textContent || '';
                if (this.isDuplicateMessage(text)) {
                    message.remove();
                    removedCount++;
                }
            });

            console.log(`🧹 Limpiados ${removedCount} mensajes duplicados del chat`);
        }
    }

    isDuplicateMessage(text) {
        const duplicatePatterns = [
            '❌ **Error:**',
            '✅ **Análisis unificado completado**',
            '🔄 **Sistema Original activado**',
            '🔄 **Sistema Unificado activado**',
            'IA lista para análisis',
            'Tena Copilot'
        ];

        return duplicatePatterns.some(pattern => text.includes(pattern));
    }

    disableProblematicScripts() {
        // Deshabilitar funciones problemáticas
        if (window.enhancedSidebarAI) {
            window.enhancedSidebarAI = null;
        }
        if (window.unifiedAI) {
            window.unifiedAI = null;
        }
        if (window.formObserverAI) {
            window.formObserverAI = null;
        }
        if (window.chatCenteredAI) {
            window.chatCenteredAI = null;
        }

        console.log('🔒 Scripts problemáticos deshabilitados');
    }

    createUniqueSystem() {
        const sidebarContainer = document.getElementById('sidebarContainer');
        if (!sidebarContainer) return;

        const panelContent = sidebarContainer.querySelector('.panel-content');
        if (!panelContent) return;

        // Crear sistema único
        const uniqueSection = document.createElement('div');
        uniqueSection.className = 'unique-ai-system card mb-3';
        uniqueSection.id = 'uniqueAISystem';

        uniqueSection.innerHTML = `
            <div class="card-header">
                <h6 class="mb-0">
                    <i class="fas fa-robot me-2"></i>
                    
                </h6>
            </div>
            <div class="card-body">
                <div class="ai-status mb-3">
                    <div class="status-indicator">
                        <div class="status-dot ready" id="uniqueStatusDot"></div>
                        <span id="uniqueStatusText">Sistema único listo</span>
                    </div>
                </div>
                
                <div class="ai-content">
                    <!-- Sección de Análisis -->
                    <div class="analysis-section mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-chart-line me-2"></i>
                            Análisis Clínico
                        </h6>
                        <div id="uniqueAnalysisContainer">
                            <div class="placeholder-content">
                                <i class="fas fa-lightbulb text-muted"></i>
                                <p>Análisis clínico disponible</p>
                            </div>
                        </div>
                    </div>

                    <!-- Sección de Evidencia Científica -->
                    <div class="evidence-section mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-microscope me-2"></i>
                            Evidencia Científica
                        </h6>
                        <div id="uniqueEvidenceContainer">
                            <div class="placeholder-content">
                                <i class="fas fa-microscope text-muted"></i>
                                <p>Evidencia científica disponible</p>
                            </div>
                        </div>
                    </div>

                    <!-- Sección de Recomendaciones -->
                    <div class="recommendations-section mb-3">
                        <h6 class="section-title">
                            <i class="fas fa-clipboard-list me-2"></i>
                            Recomendaciones
                        </h6>
                        <div id="uniqueRecommendationsContainer">
                            <div class="placeholder-content">
                                <i class="fas fa-clipboard-list text-muted"></i>
                                <p>Recomendaciones disponibles</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Input único -->
                <div class="unique-input mt-3">
                    <div class="input-group">
                        <input type="text" 
                               id="uniqueAIInput" 
                               class="form-control" 
                               placeholder="Escribe tu consulta médica aquí..."
                               onkeydown="if(event.key==='Enter'){ uniqueAI.processQuery(this.value); this.value='';}">
                        <button class="btn btn-primary" 
                                onclick="uniqueAI.processQuery(document.getElementById('uniqueAIInput').value)">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Insertar al inicio del panel
        panelContent.insertBefore(uniqueSection, panelContent.firstChild);

        console.log('✅ Sistema único creado');
    }
}

// Inicializar inmediatamente
window.uniqueAI = new ForceCleanSystem();

// También inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    if (!window.uniqueAI) {
        window.uniqueAI = new ForceCleanSystem();
    }
});

// Exportar para uso global
window.ForceCleanSystem = ForceCleanSystem; 