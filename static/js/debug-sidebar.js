
// Script de debug para verificar el problema del JavaScript
console.log('🔍 Debug: Verificando JavaScript de la sidebar...');

// Verificar si las funciones están disponibles
console.log('showAINotification disponible:', typeof window.showAINotification);
console.log('updateAIStatus disponible:', typeof window.updateAIStatus);
console.log('showAIProgress disponible:', typeof window.showAIProgress);
console.log('hideAIProgress disponible:', typeof window.hideAIProgress);

// Verificar si EnhancedSidebarAI está disponible
console.log('EnhancedSidebarAI disponible:', typeof window.enhancedAI);

// Verificar elementos del DOM
console.log('aiStatusDot:', document.getElementById('aiStatusDot'));
console.log('aiStatusText:', document.getElementById('aiStatusText'));
console.log('aiProgress:', document.getElementById('aiProgress'));

// Probar una función
if (typeof window.showAINotification === 'function') {
    console.log('✅ Función showAINotification funciona');
    window.showAINotification('Prueba de notificación', 'success');
} else {
    console.log('❌ Función showAINotification no está disponible');
}

console.log('🔍 Debug completado');
