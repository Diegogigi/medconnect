/**
 * Sistema de Observación de Formulario para IAs
 * Las IAs observan el formulario pero no actúan hasta que se solicite por chat
 */

class FormObserverAI {
    constructor() {
        this.formData = {
            motivoConsulta: '',
            tipoAtencion: '',
            pacienteNombre: '',
            pacienteRut: '',
            pacienteEdad: '',
            antecedentes: '',
            evaluacion: '',
            diagnostico: '',
            tratamiento: '',
            observaciones: ''
        };

        this.isObserving = false;
        this.contextHash = '';
        this.lastUpdate = null;

        this.init();
    }

    init() {
        console.log('🔍 Inicializando FormObserverAI...');
        this.startObserving();
        this.setupChatIntegration();
    }

    startObserving() {
        if (this.isObserving) return;

        console.log('👁️ Iniciando observación del formulario...');
        this.isObserving = true;

        // Observar cambios en campos del formulario
        const formFields = [
            'motivoConsulta',
            'tipoAtencion',
            'pacienteNombre',
            'pacienteRut',
            'pacienteEdad',
            'antecedentes',
            'evaluacion',
            'diagnostico',
            'tratamiento',
            'observaciones'
        ];

        formFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.addEventListener('input', () => this.updateFormData());
                element.addEventListener('change', () => this.updateFormData());
            }
        });

        // Observar cambios en selects
        const selects = document.querySelectorAll('select');
        selects.forEach(select => {
            select.addEventListener('change', () => this.updateFormData());
        });

        // Observar cambios en textareas
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', () => this.updateFormData());
        });

        console.log('✅ Observación del formulario iniciada');
    }

    updateFormData() {
        const newData = {
            motivoConsulta: this.getValue('motivoConsulta'),
            tipoAtencion: this.getValue('tipoAtencion'),
            pacienteNombre: this.getValue('pacienteNombre'),
            pacienteRut: this.getValue('pacienteRut'),
            pacienteEdad: this.getValue('pacienteEdad'),
            antecedentes: this.getValue('antecedentes'),
            evaluacion: this.getValue('evaluacion'),
            diagnostico: this.getValue('diagnostico'),
            tratamiento: this.getValue('tratamiento'),
            observaciones: this.getValue('observaciones')
        };

        // Calcular hash del contexto para detectar cambios
        const newHash = JSON.stringify(newData);

        if (newHash !== this.contextHash) {
            this.formData = newData;
            this.contextHash = newHash;
            this.lastUpdate = new Date();

            console.log('📝 Formulario actualizado:', this.formData);

            // Notificar a las IAs sobre el cambio de contexto
            this.notifyAIs();
        }
    }

    getValue(fieldId) {
        const element = document.getElementById(fieldId);
        if (!element) return '';

        if (element.tagName === 'SELECT') {
            return element.options[element.selectedIndex]?.text || '';
        }

        return element.value || '';
    }

    notifyAIs() {
        // Notificar a las IAs sobre el cambio de contexto
        if (window.enhancedAI) {
            window.enhancedAI.updateContext(this.formData);
        }

        if (window.copilotAI) {
            window.copilotAI.updateContext(this.formData);
        }

        // Emitir evento para que otras IAs se enteren
        window.dispatchEvent(new CustomEvent('formContextUpdated', {
            detail: this.formData
        }));
    }

    setupChatIntegration() {
        // Integrar con el sistema de chat
        if (typeof window.setupChatWithFormContext === 'function') {
            window.setupChatWithFormContext(this);
        }

        // Exponer métodos para el chat
        window.formObserver = {
            getContext: () => this.formData,
            getLastUpdate: () => this.lastUpdate,
            isObserving: () => this.isObserving
        };
    }

    // Método para obtener contexto resumido para las IAs
    getContextSummary() {
        const context = {
            paciente: {
                nombre: this.formData.pacienteNombre,
                rut: this.formData.pacienteRut,
                edad: this.formData.pacienteEdad
            },
            consulta: {
                motivo: this.formData.motivoConsulta,
                tipo: this.formData.tipoAtencion
            },
            clinico: {
                antecedentes: this.formData.antecedentes,
                evaluacion: this.formData.evaluacion,
                diagnostico: this.formData.diagnostico,
                tratamiento: this.formData.tratamiento,
                observaciones: this.formData.observaciones
            },
            timestamp: this.lastUpdate
        };

        return context;
    }

    // Método para verificar si hay información suficiente
    hasSufficientContext() {
        return !!(this.formData.motivoConsulta && this.formData.tipoAtencion);
    }

    // Método para obtener contexto para búsqueda científica
    getScientificSearchContext() {
        return {
            consulta: this.formData.motivoConsulta,
            tipoAtencion: this.formData.tipoAtencion,
            antecedentes: this.formData.antecedentes,
            evaluacion: this.formData.evaluacion,
            diagnostico: this.formData.diagnostico
        };
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.formObserverAI = new FormObserverAI();
    });
} else {
    window.formObserverAI = new FormObserverAI();
} 