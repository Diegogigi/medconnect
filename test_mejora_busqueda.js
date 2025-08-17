// Script para probar la mejora en la búsqueda
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
            if (linea.includes('flexión de hombro')) {
                sintomas.push('dolor en hombro');
                actividades.push('flexión de hombro');
            }
            if (linea.includes('elevaciones laterales')) {
                sintomas.push('dolor en hombro');
                actividades.push('elevaciones laterales');
            }
            if (linea.includes('secarme')) {
                sintomas.push('dolor en hombro');
                actividades.push('secarme');
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

    // Si no se puede extraer información útil, retornar null para usar fallback
    console.log('⚠️ No se pudo extraer diagnóstico específico, usando fallback');
    return null;
}

function obtenerDiagnosticoLimpio(diagnostico, motivoConsulta, especialidad) {
    console.log('🔍 Diagnóstico original:', diagnostico);
    console.log('🔍 Motivo consulta:', motivoConsulta);
    console.log('🔍 Especialidad:', especialidad);

    let diagnosticoLimpio = diagnostico;

    if (!diagnosticoLimpio && motivoConsulta) {
        // Extraer información útil de las preguntas sugeridas
        console.log('🔍 Extrayendo diagnóstico de motivo consulta...');
        let diagnosticoExtraido = extraerDiagnosticoDePreguntas(motivoConsulta);
        diagnosticoLimpio = diagnosticoExtraido;
        console.log('🔍 Diagnóstico extraído:', diagnosticoExtraido);
    }

    // Si aún no hay diagnóstico limpio, usar términos específicos según especialidad
    if (!diagnosticoLimpio || diagnosticoLimpio.length < 3) {
        console.log('⚠️ No hay diagnóstico específico, usando términos según especialidad');
        
        // Mapear especialidad a términos de búsqueda más efectivos
        const especialidadTerminos = {
            'kinesiologia': 'physical therapy pain',
            'fisioterapia': 'physical therapy pain',
            'fonoaudiologia': 'speech therapy disorders',
            'psicologia': 'mental health therapy',
            'medicina': 'medical treatment',
            'terapia_ocupacional': 'occupational therapy',
            'general': 'pain treatment'
        };
        
        diagnosticoLimpio = especialidadTerminos[especialidad] || 'pain treatment';
        console.log('🔍 Usando término específico:', diagnosticoLimpio);
    }

    return diagnosticoLimpio;
}

// Casos de prueba
const casosPrueba = [
    {
        nombre: "Caso 1: Sin diagnóstico específico, especialidad kinesiologia",
        diagnostico: "",
        motivoConsulta: "PREGUNTAS SUGERIDAS POR IA:\n1. ¿Qué movimientos o actividades le causan más dolor?\n\n2. ¿Ha notado mejoría con algún tipo de ejercicio o movimiento?\n\n3. ¿Qué movimientos le resultan más difíciles?\n\n4. ¿Ha notado mejoría con algún tipo de ejercicio?\n\n5. ¿Hay actividades que ya no puede realizar?",
        especialidad: "kinesiologia"
    },
    {
        nombre: "Caso 2: Con diagnóstico específico de hombro",
        diagnostico: "",
        motivoConsulta: "PREGUNTAS SUGERIDAS POR IA:\n1. ¿Qué movimientos o actividades le causan más dolor?\nflexión de hombro y elevaciones laterales\n\n2. ¿Ha notado mejoría con algún tipo de ejercicio o movimiento?\nno\n\n3. ¿Qué movimientos le resultan más difíciles?\n\n4. ¿Ha notado mejoría con algún tipo de ejercicio?\n\n5. ¿Hay actividades que ya no puede realizar?\nlevantar peso, secarme",
        especialidad: "kinesiologia"
    },
    {
        nombre: "Caso 3: Sin información útil, especialidad fonoaudiologia",
        diagnostico: "",
        motivoConsulta: "PREGUNTAS SUGERIDAS POR IA:\n1. ¿Qué movimientos o actividades le causan más dolor?\n\n2. ¿Ha notado mejoría con algún tipo de ejercicio o movimiento?\n\n3. ¿Qué movimientos le resultan más difíciles?\n\n4. ¿Ha notado mejoría con algún tipo de ejercicio?\n\n5. ¿Hay actividades que ya no puede realizar?",
        especialidad: "fonoaudiologia"
    }
];

console.log('🚀 PRUEBA DE MEJORA EN BÚSQUEDA');
console.log('=' .repeat(50));

casosPrueba.forEach((caso, index) => {
    console.log(`\n📋 ${caso.nombre}`);
    console.log('-'.repeat(30));
    const resultado = obtenerDiagnosticoLimpio(caso.diagnostico, caso.motivoConsulta, caso.especialidad);
    console.log(`✅ Resultado final: "${resultado}"`);
});

console.log('\n🎯 PRUEBA COMPLETADA'); 