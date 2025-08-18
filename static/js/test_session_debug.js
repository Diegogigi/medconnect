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

        if (response.ok) {
            console.log('✅ API de Copilot funciona correctamente');
            return true;
        } else {
            console.log('❌ Error en API de Copilot:', data);
            return false;
        }
    } catch (error) {
        console.error('❌ Error probando API de Copilot:', error);
        return false;
    }
}

// Ejecutar pruebas cuando se carga la página
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Iniciando pruebas de sesión...');

    // Esperar un poco para que la página se cargue completamente
    setTimeout(async () => {
        const sessionOk = await testSession();
        if (sessionOk) {
            await testCopilotAPI();
        }
    }, 1000);
});

// Hacer las funciones disponibles globalmente
window.testSession = testSession;
window.testCopilotAPI = testCopilotAPI; 