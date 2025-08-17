// Script para probar la extracción con el caso del brazo
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
            if (linea.includes('rotación') || linea.includes('rotar el cuerpo')) {
                sintomas.push('dolor en rotación');
                actividades.push('rotación');
            }
            if (linea.includes('doblar las piernas')) {
                sintomas.push('dolor al doblar piernas');
                actividades.push('doblar piernas');
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
            if (linea.includes('elevar el brazo') || linea.includes('brazo')) {
                sintomas.push('dolor en brazo');
                actividades.push('elevar brazo');
            }
            if (linea.includes('hombro')) {
                sintomas.push('dolor en hombro');
                actividades.push('hombro');
            }
            if (linea.includes('cuello')) {
                sintomas.push('dolor en cuello');
                actividades.push('cuello');
            }
            if (linea.includes('espalda')) {
                sintomas.push('dolor en espalda');
                actividades.push('espalda');
            }
            if (linea.includes('rodilla')) {
                sintomas.push('dolor en rodilla');
                actividades.push('rodilla');
            }
            if (linea.includes('tobillo')) {
                sintomas.push('dolor en tobillo');
                actividades.push('tobillo');
            }
            if (linea.includes('muñeca')) {
                sintomas.push('dolor en muñeca');
                actividades.push('muñeca');
            }
            if (linea.includes('codo')) {
                sintomas.push('dolor en codo');
                actividades.push('codo');
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

// Caso de prueba específico del brazo
const casoBrazo = {
    nombre: "Caso: Elevar el brazo genera dolor",
    motivo: "PREGUNTAS SUGERIDAS POR IA:\n1. ¿Qué movimientos o actividades le causan más dolor?\nelevar el brazo genera dolor\n2. ¿Ha notado mejoría con algún tipo de ejercicio o movimiento?\nno, con ninguno\n3. ¿Qué movimientos le resultan más difíciles?\n\n4. ¿Ha notado mejoría con algún tipo de ejercicio?\n5. ¿Hay actividades que ya no puede realizar?"
};

console.log('🚀 PRUEBA DE EXTRACCIÓN - CASO BRAZO');
console.log('='.repeat(50));

console.log(`\n📋 ${casoBrazo.nombre}`);
console.log('-'.repeat(30));
const resultado = extraerDiagnosticoDePreguntas(casoBrazo.motivo);
console.log(`✅ Resultado final: "${resultado}"`);

console.log('\n🎯 PRUEBA COMPLETADA'); 