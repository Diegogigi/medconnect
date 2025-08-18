// Script para probar la sesión
async function testSession() {
    try {
        console.log('🔍 Probando sesión...');

        const response = await fetch('/api/test-session', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();
        console.log('📊 Datos de sesión:', data);

        if (data.has_user_id) {
            console.log('✅ Sesión válida encontrada');
            return true;
        } else {
            console.log('❌ No hay sesión válida');
            return false;
        }
    } catch (error) {
        console.error('❌ Error probando sesión:', error);
        return false;
    }
}

// Función para probar la API de copilot
async function testCopilotAPI() {
    try {
        console.log('🤖 Probando API de Copilot...');

        const response = await fetch('/api/copilot/chat', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                message: 'Hola, esto es una prueba',
                context: {}
            })
        });

        const data = await response.json();
        console.log('📊 Respuesta de Copilot:', data);
        console.log('📋 Status de respuesta:', response.status);
        console.log('📋 Headers de respuesta:', Object.fromEntries(response.headers.entries()));

        if (response.ok) {
            console.log('✅ API de Copilot funciona correctamente');
            return true;
        } else {
            console.log('❌ Error en API de Copilot:', data);
            console.log('❌ Status HTTP:', response.status);
            console.log('❌ Status Text:', response.statusText);
            return false;
        }
    } catch (error) {
        console.error('❌ Error probando API de Copilot:', error);
        return false;
    }
}

// Función para probar la API de copilot test (sin decorador)
async function testCopilotAPITest() {
    try {
        console.log('🧪 Probando API de Copilot Test (sin decorador)...');

        const response = await fetch('/api/copilot/chat-test', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                message: 'Hola, esto es una prueba',
                context: {}
            })
        });

        const data = await response.json();
        console.log('📊 Respuesta de Copilot Test:', data);
        console.log('📋 Status de respuesta:', response.status);
        console.log('📋 Headers de respuesta:', Object.fromEntries(response.headers.entries()));

        if (response.ok) {
            console.log('✅ API de Copilot Test funciona correctamente');
            return true;
        } else {
            console.log('❌ Error en API de Copilot Test:', data);
            console.log('❌ Status HTTP:', response.status);
            console.log('❌ Status Text:', response.statusText);
            return false;
        }
    } catch (error) {
        console.error('❌ Error probando API de Copilot Test:', error);
        return false;
    }
}

// Ejecutar pruebas cuando se carga la página
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Iniciando pruebas de sesión...');

    // Esperar un poco para que la página se cargue completamente
    setTimeout(async () => {
        try {
            const sessionOk = await testSession();
            if (sessionOk) {
                await testCopilotAPITest(); // Probar primero la versión sin decorador
                await testCopilotAPI(); // Luego probar la versión con decorador
            }
        } catch (error) {
            console.error('❌ Error en pruebas de sesión:', error);
        }
    }, 2000);
});

// También ejecutar cuando la ventana se carga completamente
window.addEventListener('load', async () => {
    console.log('🌐 Ventana cargada completamente, probando sesión...');

    setTimeout(async () => {
        try {
            const sessionOk = await testSession();
            if (sessionOk) {
                await testCopilotAPITest(); // Probar primero la versión sin decorador
                await testCopilotAPI(); // Luego probar la versión con decorador
            }
        } catch (error) {
            console.error('❌ Error en pruebas de sesión (load):', error);
        }
    }, 3000);
});

// Hacer las funciones disponibles globalmente
window.testSession = testSession;
window.testCopilotAPI = testCopilotAPI; 