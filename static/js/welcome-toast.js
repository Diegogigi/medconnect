/**
 * Welcome Toast - Mensaje de bienvenida para usuarios que acaban de iniciar sesión
 * MedConnect - Sistema de gestión médica
 */

// Variable global para prevenir múltiples inicializaciones
if (typeof window.medConnectWelcomeToastInitialized === 'undefined') {
    window.medConnectWelcomeToastInitialized = false;
}

// Script para mejorar la funcionalidad del mensaje de bienvenida
document.addEventListener('DOMContentLoaded', function () {
    const welcomeToast = document.getElementById('welcomeToast');

    if (welcomeToast) {
        console.log('🎉 Mensaje de bienvenida encontrado, inicializando...');

        // Mostrar el toast con animación suave
        setTimeout(() => {
            welcomeToast.style.display = 'block';
            // Pequeña pausa para que el DOM se actualice
            setTimeout(() => {
                welcomeToast.classList.add('show');
                console.log('✅ Mensaje de bienvenida mostrado');
            }, 10);
        }, 600);

        // Ocultar automáticamente después de 6 segundos
        setTimeout(() => {
            welcomeToast.classList.remove('show');
            console.log('👋 Mensaje de bienvenida ocultado');

            setTimeout(() => {
                welcomeToast.style.display = 'none';
            }, 400);
        }, 6000);

        // Remover la funcionalidad de clic para cerrar (desaparece solo)
        welcomeToast.style.cursor = 'default';
        welcomeToast.title = '';
    } else {
        console.log('❌ Mensaje de bienvenida NO encontrado en el DOM');
    }
});

// Función para mostrar mensaje de bienvenida personalizado
function showWelcomeMessage(userData) {
    const welcomeToast = document.getElementById('welcomeToast');

    if (welcomeToast && userData) {
        const title = welcomeToast.querySelector('h5');
        const message = welcomeToast.querySelector('p');

        // Personalizar según el tipo de usuario
        if (userData.tipo_usuario === 'profesional') {
            title.textContent = `¡Bienvenido/a, ${userData.nombre}!`;
            message.textContent = userData.especialidad ?
                `Tu asistente de IA está listo para ayudarte con ${userData.especialidad}` :
                'Tu asistente de IA está listo para potenciar tu práctica médica';
        } else {
            title.textContent = `¡Bienvenido/a, ${userData.nombre}!`;
            message.textContent = 'Tu asistente de IA está listo para cuidar de tu salud';
        }

        // Mostrar el toast
        welcomeToast.style.display = 'block';
        welcomeToast.classList.add('show');
    }
}

// Función para forzar la aparición del mensaje (para pruebas)
function forceShowWelcomeMessage() {
    console.log('🧪 Forzando aparición del mensaje de bienvenida...');

    // Crear el mensaje si no existe
    let welcomeToast = document.getElementById('welcomeToast');

    if (!welcomeToast) {
        console.log('📝 Creando mensaje de bienvenida...');
        welcomeToast = document.createElement('div');
        welcomeToast.id = 'welcomeToast';
        welcomeToast.className = 'welcome-toast';
        welcomeToast.innerHTML = `
            <div class="toast-body">
                <div>
                    <h5 class="mb-1">¡Bienvenido/a, Usuario!</h5>
                    <p class="mb-0">Tu asistente de IA está listo para potenciar tu práctica médica</p>
                </div>
            </div>
        `;
        document.body.appendChild(welcomeToast);
    }

    // Mostrar el mensaje
    welcomeToast.style.display = 'block';
    setTimeout(() => {
        welcomeToast.classList.add('show');
        console.log('✅ Mensaje de bienvenida forzado mostrado');
    }, 10);

    // Ocultar después de 6 segundos
    setTimeout(() => {
        welcomeToast.classList.remove('show');
        setTimeout(() => {
            welcomeToast.style.display = 'none';
        }, 400);
    }, 6000);
}

// Exponer la función de prueba globalmente
window.forceShowWelcomeMessage = forceShowWelcomeMessage; 