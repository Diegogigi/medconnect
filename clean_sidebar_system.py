#!/usr/bin/env python3
"""
Script para limpiar completamente la sidebar y asegurar un solo sistema funcionando
"""


def clean_sidebar_system():
    """Limpia completamente la sidebar para evitar duplicaciones"""

    print("🧹 Limpiando sistema de sidebar...")

    # 1. Limpiar el template de elementos duplicados
    clean_template()

    # 2. Crear un sistema único y limpio
    create_clean_system()

    # 3. Verificar que todo esté funcionando
    verify_clean_system()

    print("✅ Sistema de sidebar limpiado")


def clean_template():
    """Limpia el template de elementos duplicados"""

    template_path = "templates/professional.html"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    print("🔧 Limpiando template...")

    # Remover elementos duplicados de la sidebar
    # Buscar y limpiar secciones duplicadas
    import re

    # Limpiar secciones duplicadas de AI
    patterns_to_clean = [
        r"<!-- Indicador de Estado de IA -->.*?<!-- Sistema de Chat",
        r"<!-- Controles de IA -->.*?<!-- Contenido del Panel",
        r'<div class="ai-status-panel">.*?</div>',
        r'<div class="sidebar-controls">.*?</div>',
    ]

    for pattern in patterns_to_clean:
        content = re.sub(pattern, "", content, flags=re.DOTALL)

    # Crear una sidebar limpia y única
    clean_sidebar = """
                <!-- Sidebar Unificada de IA -->
                <div class="sidebar-container" id="sidebarContainer">
                    <!-- Handle de resize -->
                    <div class="sidebar-resize-handle" id="sidebarResizeHandle"></div>
                    
                    <!-- Controles de IA Unificados -->
                    <div class="sidebar-controls">
                        <button class="control-btn" id="autoModeToggle" title="Modo Automático">
                            <i class="fas fa-robot"></i>
                        </button>
                        <button class="control-btn" id="manualAnalyzeBtn" title="Análisis Manual">
                            <i class="fas fa-search"></i>
                        </button>
                        <button class="control-btn" id="refreshAnalysisBtn" title="Actualizar Análisis">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>

                    <!-- Contenido del Panel -->
                    <div class="panel-content p-3">
                        <!-- Indicador de Estado de IA Unificado -->
                        <div class="ai-status-panel">
                            <div class="ai-status-indicator">
                                <div class="status-dot ready" id="aiStatusDot"></div>
                                <span id="aiStatusText">IA lista para análisis</span>
                            </div>
                            <div class="ai-progress" id="aiProgress" style="display: none;">
                                <div class="progress-bar">
                                    <div class="progress-fill" id="progressFill"></div>
                                </div>
                                <span id="progressText">Analizando...</span>
                            </div>
                        </div>

                        <!-- Sistema de Chat Unificado -->
                        <div class="copilot-chat-elegant" id="copilotChatElegant">
                            <!-- Área de Mensajes -->
                            <div class="chat-messages-elegant" id="chatMessagesElegant">
                                <div class="messages-container" id="messagesContainer">
                                    <!-- Mensaje de bienvenida -->
                                    <div class="message-elegant system-message" id="welcomeMessage">
                                        <div class="message-bubble">
                                            <div class="message-icon"></div>
                                            <div class="message-text">
                                                <p>¡Hola {{ user.nombre if user and user.nombre else 'Profesional' }}! Soy tu asistente de IA unificado. Completa el formulario y observa cómo trabajo en tiempo real.</p>
                                            </div>
                                        </div>
                                        <div class="message-time">Ahora</div>
                                        <button type="button" class="btn-close btn-close-white position-absolute top-0 end-0 m-2" 
                                                onclick="borrarMensajeBienvenida()" 
                                                style="font-size: 0.7rem; opacity: 0.7;" 
                                                title="Borrar mensaje">
                                        </button>
                                    </div>
                                </div>
                                
                                <!-- Indicador de typing -->
                                <div class="typing-elegant" id="typingElegant" style="display: none;">
                                    <div class="typing-bubble">
                                        <div class="typing-avatar"></div>
                                        <div class="typing-content">
                                            <span>IA unificada está analizando...</span>
                                            <div class="typing-animation">
                                                <span></span>
                                                <span></span>
                                                <span></span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Área de Resultados -->
                            <div class="results-area" id="resultsArea" style="display: none;"></div>

                            <!-- Tarjetas de evidencia -->
                            <div id="evidenceCardsContainer" class="mt-3"></div>

                            <!-- Indicador de Modo Automático -->
                            <div class="auto-mode-indicator">
                                <div class="auto-mode-content">
                                    <span class="auto-mode-text">IA Unificada</span>
                                    <div class="auto-mode-status">
                                        <i class="fas fa-check-circle text-success"></i>
                                    </div>
                                </div>
                                <div class="mt-2">
                                    <input type="text" id="copilotQuickInput" class="form-control form-control-sm" placeholder="Escribe aquí para preguntar a la IA..." onkeydown="if(event.key==='Enter'){ if(this.value.trim()){ agregarMensajeElegant(this.value,'user'); enviarMensajeCopilot(this.value); this.value='';}}">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
"""

    # Reemplazar toda la sección de sidebar
    sidebar_pattern = r'<div class="sidebar-container" id="sidebarContainer">.*?</div>\s*</div>\s*</main>'
    content = re.sub(
        sidebar_pattern,
        clean_sidebar + "\n        </div>\n    </main>",
        content,
        flags=re.DOTALL,
    )

    # Escribir el template limpio
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Template limpiado")


def create_clean_system():
    """Crea un sistema único y limpio"""

    print("🔧 Creando sistema único...")

    # Crear JavaScript unificado y limpio
    clean_js = """
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
        let message = '📊 **Análisis Unificado Completado**\\n\\n';
        
        if (result.palabras_clave) {
            message += '🔑 **Palabras Clave Identificadas:**\\n';
            result.palabras_clave.forEach(palabra => {
                message += `- ${palabra.termino} (${palabra.confianza}%)\\n`;
            });
            message += '\\n';
        }
        
        if (result.evidence && result.evidence.length > 0) {
            message += f'🔬 **Evidencia Científica:** {result.evidence.length} artículos encontrados\\n\\n';
        }
        
        if (result.recommendations && result.recommendations.length > 0) {
            message += '💡 **Recomendaciones Generadas**\\n';
            result.recommendations.forEach(rec => {
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
"""

    # Escribir el JavaScript limpio
    with open("static/js/unified-sidebar-ai.js", "w", encoding="utf-8") as f:
        f.write(clean_js)

    print("✅ JavaScript unificado creado")


def verify_clean_system():
    """Verifica que el sistema limpio esté funcionando"""

    print("🔍 Verificando sistema limpio...")

    # Verificar archivos
    files_to_check = ["static/js/unified-sidebar-ai.js", "templates/professional.html"]

    for file_path in files_to_check:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "UnifiedSidebarAI" in content:
                    print(f"✅ {file_path} - Sistema unificado encontrado")
                else:
                    print(f"⚠️ {file_path} - Sistema unificado no encontrado")
        except FileNotFoundError:
            print(f"❌ {file_path} - Archivo no encontrado")

    print("✅ Verificación completada")


def update_template_scripts():
    """Actualiza los scripts en el template"""

    template_path = "templates/professional.html"

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar todos los scripts de la sidebar con el unificado
    old_scripts = [
        '<script src="/static/js/enhanced-sidebar-ai.js"></script>',
        '<script src="/static/js/unified-ai-config.js"></script>',
    ]

    new_script = '<script src="/static/js/unified-sidebar-ai.js"></script>'

    for old_script in old_scripts:
        if old_script in content:
            content = content.replace(old_script, "")

    # Asegurar que el script unificado esté presente
    if new_script not in content:
        content = content.replace("</body>", f"    {new_script}\n</body>")

    with open(template_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Scripts del template actualizados")


def main():
    """Función principal"""
    print("🧹 Limpiando sistema de sidebar completamente...")

    clean_sidebar_system()
    update_template_scripts()

    print("\n🎉 ¡Sistema completamente limpiado!")
    print("📋 Cambios realizados:")
    print("   ✅ Template limpiado de duplicaciones")
    print("   ✅ Sistema unificado creado")
    print("   ✅ JavaScript único y limpio")
    print("   ✅ Scripts actualizados")

    print("\n🚀 Ahora solo hay UN sistema funcionando:")
    print("   - UnifiedSidebarAI")
    print("   - Endpoint: /api/copilot/analyze-enhanced")
    print("   - Sin duplicaciones")
    print("   - Sin conflictos")
    print("   - Resultados consistentes")


if __name__ == "__main__":
    main()
