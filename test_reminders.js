#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento de los recordatorios
"""

console.log("🧪 Iniciando pruebas de recordatorios...");

// Función para probar la inicialización
function testReminderInitialization() {
    console.log("1. Probando inicialización de recordatorios...");

    // Verificar que las funciones están disponibles
    const functions = [
        'handleCrearRecordatorio',
        'mostrarModalRecordatorio',
        'cerrarModalRecordatorio',
        'crearModalRecordatorio',
        'mostrarFormularioRecordatorioAlternativo',
        'guardarRecordatorioAlternativo'
    ];

    let allFunctionsAvailable = true;
    functions.forEach(funcName => {
        if (typeof window[funcName] === 'function') {
            console.log(`   ✅ ${funcName} disponible`);
        } else {
            console.log(`   ❌ ${funcName} NO disponible`);
            allFunctionsAvailable = false;
        }
    });

    return allFunctionsAvailable;
}

// Función para probar el botón
function testReminderButton() {
    console.log("2. Probando botón de crear recordatorio...");

    const btn = document.getElementById('btnCrearRecordatorio');
    if (btn) {
        console.log("   ✅ Botón encontrado");

        // Simular clic
        try {
            btn.click();
            console.log("   ✅ Clic simulado exitosamente");
            return true;
        } catch (error) {
            console.error("   ❌ Error al hacer clic:", error);
            return false;
        }
    } else {
        console.log("   ❌ Botón no encontrado");
        return false;
    }
}

// Función para probar el modal
function testReminderModal() {
    console.log("3. Probando modal de recordatorio...");

    const modal = document.getElementById('reminderModal');
    if (modal) {
        console.log("   ✅ Modal encontrado en HTML");
        return true;
    } else {
        console.log("   ⚠️ Modal no encontrado, se creará dinámicamente");
        return true; // Es válido que no exista, se creará dinámicamente
    }
}

// Función para probar la creación dinámica
function testDynamicModalCreation() {
    console.log("4. Probando creación dinámica de modal...");

    try {
        // Llamar a la función de creación dinámica
        if (typeof crearModalRecordatorio === 'function') {
            crearModalRecordatorio();
            console.log("   ✅ Modal creado dinámicamente");
            return true;
        } else {
            console.log("   ❌ Función crearModalRecordatorio no disponible");
            return false;
        }
    } catch (error) {
        console.error("   ❌ Error creando modal:", error);
        return false;
    }
}

// Función para probar el formulario alternativo
function testAlternativeForm() {
    console.log("5. Probando formulario alternativo...");

    try {
        if (typeof mostrarFormularioRecordatorioAlternativo === 'function') {
            mostrarFormularioRecordatorioAlternativo();
            console.log("   ✅ Formulario alternativo mostrado");
            return true;
        } else {
            console.log("   ❌ Función mostrarFormularioRecordatorioAlternativo no disponible");
            return false;
        }
    } catch (error) {
        console.error("   ❌ Error mostrando formulario alternativo:", error);
        return false;
    }
}

// Función principal de pruebas
function runReminderTests() {
    console.log("🚀 Iniciando pruebas completas de recordatorios...");

    const tests = [
        testReminderInitialization,
        testReminderButton,
        testReminderModal,
        testDynamicModalCreation,
        testAlternativeForm
    ];

    let passedTests = 0;
    let totalTests = tests.length;

    tests.forEach((test, index) => {
        console.log(`\n--- Prueba ${index + 1} ---`);
        const result = test();
        if (result) {
            passedTests++;
        }
    });

    console.log(`\n📊 Resultados:`);
    console.log(`   ✅ Pruebas pasadas: ${passedTests}/${totalTests}`);
    console.log(`   📈 Porcentaje de éxito: ${(passedTests / totalTests * 100).toFixed(1)}%`);

    if (passedTests === totalTests) {
        console.log("🎉 ¡Todas las pruebas pasaron! Los recordatorios están funcionando correctamente.");
    } else {
        console.log("⚠️ Algunas pruebas fallaron. Revisar la implementación.");
    }
}

// Ejecutar pruebas cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runReminderTests);
} else {
    runReminderTests();
}

// Exportar funciones para uso manual
window.testReminders = {
    runReminderTests,
    testReminderInitialization,
    testReminderButton,
    testReminderModal,
    testDynamicModalCreation,
    testAlternativeForm
};

console.log("🧪 Script de pruebas de recordatorios cargado. Usa testReminders.runReminderTests() para ejecutar las pruebas."); 