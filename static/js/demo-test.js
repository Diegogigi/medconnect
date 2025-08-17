
// Test de demostración del sistema unificado
console.log('🧪 Iniciando test de demostración...');

// Verificar que el sistema esté disponible
if (typeof window.simpleUnifiedAI !== 'undefined') {
    console.log('✅ SimpleUnifiedSidebarAI disponible');
    
    // Simular datos de formulario
    const testFormData = {
        motivoConsulta: 'Dolor de rodilla derecha',
        sintomasPrincipales: 'Dolor al caminar, limitación de movimiento',
        antecedentesMedicos: 'Artritis previa',
        medicamentosActuales: 'Antiinflamatorios',
        alergias: 'Ninguna conocida',
        examenFisico: 'Dolor a la palpación en rodilla derecha',
        diagnosticoPresuntivo: 'Gonartrosis',
        planTratamiento: 'Fisioterapia y ejercicios'
    };
    
    // Simular análisis
    console.log('🧪 Simulando análisis...');
    window.simpleUnifiedAI.performUnifiedAnalysis(testFormData);
    
} else {
    console.log('❌ SimpleUnifiedSidebarAI no disponible');
    
    // Verificar si hay otros sistemas
    if (typeof window.unifiedAI !== 'undefined') {
        console.log('⚠️ UnifiedAI encontrado (sistema anterior)');
    }
    
    if (typeof window.enhancedAI !== 'undefined') {
        console.log('⚠️ EnhancedAI encontrado (sistema anterior)');
    }
}

console.log('🧪 Test de demostración completado');
