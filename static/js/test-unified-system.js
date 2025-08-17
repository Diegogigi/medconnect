
// Script de prueba para verificar el sistema unificado
console.log('🧪 Iniciando prueba del sistema unificado...');

// Verificar que el sistema esté disponible
if (typeof window.unifiedAI !== 'undefined') {
    console.log('✅ UnifiedSidebarAI disponible');
    
    // Verificar métodos principales
    const methods = ['init', 'analyzeFormData', 'updateAIStatus', 'toggleAutoMode'];
    methods.forEach(method => {
        if (typeof window.unifiedAI[method] === 'function') {
            console.log(`✅ Método ${method} disponible`);
        } else {
            console.log(`❌ Método ${method} no disponible`);
        }
    });
    
    // Verificar elementos del DOM
    const elements = ['aiStatusDot', 'aiStatusText', 'aiProgress', 'autoModeToggle'];
    elements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            console.log(`✅ Elemento ${elementId} encontrado`);
        } else {
            console.log(`❌ Elemento ${elementId} no encontrado`);
        }
    });
    
    // Probar análisis manual
    console.log('🧪 Probando análisis manual...');
    if (typeof window.unifiedAI.triggerManualAnalysis === 'function') {
        window.unifiedAI.triggerManualAnalysis();
        console.log('✅ Análisis manual iniciado');
    } else {
        console.log('❌ No se pudo iniciar análisis manual');
    }
    
} else {
    console.log('❌ UnifiedSidebarAI no está disponible');
    console.log('🔍 Verificando si hay otros sistemas...');
    
    if (typeof window.enhancedAI !== 'undefined') {
        console.log('⚠️ EnhancedAI encontrado (sistema anterior)');
    }
    
    if (typeof window.showAINotification !== 'undefined') {
        console.log('⚠️ Funciones de notificación encontradas');
    }
}

console.log('🧪 Prueba completada');
