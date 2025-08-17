// Script para probar la extracción de diagnóstico de preguntas sugeridas
function extraerDiagnosticoDePreguntas(motivoConsulta) {
    console.log('🔍 Extrayendo diagnóstico de preguntas sugeridas:', motivoConsulta);
    
    // Si contiene "PREGUNTAS SUGERIDAS POR IA", extraer información útil
    if (motivoConsulta.includes('PREGUNTAS SUGERIDAS POR IA')) {
        const lineas = motivoConsulta.split('\n');
        let sintomas = [];
        let actividades = [];
        
        for (let i = 0; i < lineas.length; i++) {
            const linea = lineas[i].trim();
            
            // Buscar respuestas que contengan información útil
            if (linea.includes('flexión de cadera')) {
                sintomas.push('dolor en cadera');
                actividades.push('flexión de cadera');
            }
            if (linea.includes('rotación')) {
                sintomas.push('dolor en rotación');
                actividades.push('rotación');
            }
            if (linea.includes('correr')) {
                sintomas.push('dolor al correr');
                actividades.push('correr');
            }
            if (linea.includes('saltar')) {
                sintomas.push('dolor al saltar');
                actividades.push('saltar');
            }
            if (linea.includes('levantar peso')) {
                sintomas.push('dolor al levantar peso');
                actividades.push('levantar peso');
            }
            if (linea.includes('deporte')) {
                sintomas.push('dolor en deportes');
                actividades.push('deportes');
            }
        }
        
        // Construir diagnóstico basado en la información extraída
        if (sintomas.length > 0) {
            const diagnostico = sintomas.join(', ');
            console.log('✅ Diagnóstico extraído:', diagnostico);
            return diagnostico;
        }
        
        // Si no se encontraron síntomas específicos, usar información general
        if (actividades.length > 0) {
            const diagnostico = `dolor en ${actividades.join(', ')}`;
            console.log('✅ Diagnóstico extraído:', diagnostico);
            return diagnostico;
        }
    }
    
    // Si no se puede extraer información útil, usar término genérico
    console.log('⚠️ No se pudo extraer diagnóstico específico, usando término genérico');
    return 'dolor';
}

// Casos de prueba
const casosPrueba = [
    {
        nombre: "Caso 1: Flexión de cadera",
        motivo: "PREGUNTAS SUGERIDAS POR IA:\n1. ¿Qué movimientos o actividades le causan más dolor?\nflexión de cadera\n2. ¿Ha notado mejoría con algún tipo de ejercicio o movimiento?\nno\n3. ¿Qué movimientos le resultan más difíciles?\nflexión de cadera y rotación\n4. ¿Ha notado mejoría con algún tipo de ejercicio?\nno\n5. ¿Hay actividades que ya no puede realizar?\ncorrer, saltar, levantar peso"
    },
    {
        nombre: "Caso 2: Solo dolor",
        motivo: "Dolor en la rodilla"
    },
    {
        nombre: "Caso 3: Sin preguntas sugeridas",
        motivo: "Tengo dolor en la espalda"
    },
    {
        nombre: "Caso 4: Vacío",
        motivo: ""
    }
];

console.log('🚀 PRUEBAS DE EXTRACCIÓN DE DIAGNÓSTICO');
console.log('=' .repeat(50));

casosPrueba.forEach((caso, index) => {
    console.log(`\n📋 ${caso.nombre}`);
    console.log('-'.repeat(30));
    const resultado = extraerDiagnosticoDePreguntas(caso.motivo);
    console.log(`✅ Resultado final: "${resultado}"`);
});

console.log('\n🎯 PRUEBAS COMPLETADAS'); 