
// Configuración unificada para la sidebar de IA
window.SidebarAIConfig = {
    // Endpoints unificados
    endpoints: {
        analyze: '/api/copilot/analyze-enhanced',
        scientific: '/api/scientific-search',
        chat: '/api/copilot/chat'
    },
    
    // Configuración de análisis
    analysis: {
        debounceDelay: 1000,
        minContentLength: 10,
        maxResults: 5
    },
    
    // Configuración de UI
    ui: {
        autoMode: true,
        showProgress: true,
        notifications: true
    }
};

// Sistema unificado de notificaciones
window.UnifiedAINotifications = {
    show: function(message, type = 'info') {
        if (typeof window.showAINotification === 'function') {
            window.showAINotification(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    },
    
    success: function(message) {
        this.show(message, 'success');
    },
    
    error: function(message) {
        this.show(message, 'error');
    },
    
    warning: function(message) {
        this.show(message, 'warning');
    },
    
    info: function(message) {
        this.show(message, 'info');
    }
};

// Sistema unificado de estado
window.UnifiedAIStatus = {
    update: function(status, message) {
        if (typeof window.updateAIStatus === 'function') {
            window.updateAIStatus(status, message);
        } else {
            console.log(`[STATUS: ${status}] ${message}`);
        }
    },
    
    ready: function(message = 'IA lista para análisis') {
        this.update('ready', message);
    },
    
    processing: function(message = 'Analizando datos...') {
        this.update('processing', message);
    },
    
    success: function(message = 'Análisis completado') {
        this.update('success', message);
    },
    
    error: function(message = 'Error en análisis') {
        this.update('error', message);
    }
};
