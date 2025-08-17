// Script para probar la limpieza del diagnóstico
function limpiarDiagnostico(motivoConsulta) {
    console.log('🔍 Diagnóstico original:', motivoConsulta);

    // Filtrar contenido que contenga preguntas sugeridas
    let contenidoLimpio = motivoConsulta;

    // Si contiene "PREGUNTAS SUGERIDAS", tomar solo el contenido antes
    if (contenidoLimpio.includes('PREGUNTAS SUGERIDAS')) {
        contenidoLimpio = contenidoLimpio.split('PREGUNTAS SUGERIDAS')[0].trim();
        console.log('✅ Removido: PREGUNTAS SUGERIDAS');
    }

    // Si contiene "PREGUNTAS SUGERIDAS POR IA", tomar solo el contenido antes
    if (contenidoLimpio.includes('PREGUNTAS SUGERIDAS POR IA')) {
        contenidoLimpio = contenidoLimpio.split('PREGUNTAS SUGERIDAS POR IA')[0].trim();
        console.log('✅ Removido: PREGUNTAS SUGERIDAS POR IA');
    }

    // Si contiene números seguidos de puntos (1. 2. 3.), tomar solo el contenido antes
    if (contenidoLimpio.match(/\d+\./)) {
        contenidoLimpio = contenidoLimpio.split(/\d+\./)[0].trim();
        console.log('✅ Removido: Números con puntos');
    }

    // Si es muy largo, tomar solo las primeras palabras
    if (contenidoLimpio.length > 100) {
        contenidoLimpio = contenidoLimpio.substring(0, 100).trim();
        console.log('✅ Limitado a 100 caracteres');
    }

    // Si aún no hay diagnóstico limpio, usar un término genérico
    if (!contenidoLimpio || contenidoLimpio.length < 3) {
        contenidoLimpio = 'dolor';
        console.log('✅ Usando término genérico: dolor');
    }

    console.log('🎯 Diagnóstico limpio:', contenidoLimpio);
    return contenidoLimpio;
}

// Casos de prueba
const casosPrueba = [
    {
        nombre: "Caso 1: Con preguntas sugeridas",
        motivo: "PREGUNTAS SUGERIDAS POR IA:\n1. ¿Qué movimientos o actividades le causan más dolor?\nflexión de cadera\n2. ¿Ha notado mejoría con algún tipo de ejercicio o movimiento?\nno\n3. ¿Qué movimientos le resultan más difíciles?\nflexión de cadera y extensión de cadera\n4. ¿Ha notado mejoría con algún tipo de ejercicio?\nno\n5. ¿Hay actividades que ya no puede realizar?\ncorrer, saltar, realizar deporte."
    },
    {
        nombre: "Caso 2: Solo motivo de consulta",
        motivo: "Dolor en la rodilla al caminar"
    },
    {
        nombre: "Caso 3: Motivo largo",
        motivo: "Tengo un dolor muy intenso en la espalda baja que me impide realizar actividades cotidianas como levantarme de la cama, caminar por más de 10 minutos, y realizar cualquier tipo de ejercicio físico. El dolor se irradia hacia la pierna derecha y empeora cuando me siento por mucho tiempo."
    },
    {
        nombre: "Caso 4: Vacío",
        motivo: ""
    }
];

console.log('🚀 PRUEBAS DE LIMPIEZA DE DIAGNÓSTICO');
console.log('='.repeat(50));

casosPrueba.forEach((caso, index) => {
    console.log(`\n📋 ${caso.nombre}`);
    console.log('-'.repeat(30));
    const resultado = limpiarDiagnostico(caso.motivo);
    console.log(`✅ Resultado final: "${resultado}"`);
});

console.log('\n🎯 PRUEBAS COMPLETADAS'); 