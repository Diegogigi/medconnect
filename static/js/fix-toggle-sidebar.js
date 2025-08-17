/**
 * Función toggleSidebar corregida
 * Maneja elementos null y evita errores
 */

function toggleSidebar() {
    console.log('🔧 toggleSidebar ejecutándose...');

    // Obtener elementos con verificación de null
    const sidebarContainer = document.getElementById('sidebarContainer');
    const toggleIcon = document.getElementById('sidebarToggleIcon');
    const toggleButton = document.getElementById('sidebarToggle');
    const mainContent = document.querySelector('.col-lg-8.col-xl-9');

    // Verificar que sidebarContainer existe
    if (!sidebarContainer) {
        console.warn('⚠️ sidebarContainer no encontrado, intentando crear...');
        // Intentar crear la sidebar si no existe
        if (typeof crearSidebarSiNoExiste === 'function') {
            crearSidebarSiNoExiste();
            // Esperar un poco y reintentar
            setTimeout(() => {
                const newSidebarContainer = document.getElementById('sidebarContainer');
                if (newSidebarContainer) {
                    console.log('✅ sidebarContainer creado exitosamente');
                    toggleSidebar(); // Reintentar
                } else {
                    console.error('❌ No se pudo crear sidebarContainer');
                }
            }, 100);
        } else {
            console.error('❌ sidebarContainer no encontrado y no se puede crear');
        }
        return;
    }

    // Verificar que toggleIcon existe
    if (!toggleIcon) {
        console.warn('⚠️ toggleIcon no encontrado, continuando sin él...');
    }

    // Verificar que toggleButton existe
    if (!toggleButton) {
        console.warn('⚠️ toggleButton no encontrado, continuando sin él...');
    }

    console.log('✅ Todos los elementos encontrados');

    // Verificar si la sidebar está visible
    const isVisible = sidebarContainer.classList.contains('show');

    if (isVisible) {
        // Ocultar panel
        console.log('🔄 Ocultando sidebar...');
        sidebarContainer.classList.remove('show');

        if (toggleIcon) {
            toggleIcon.className = 'fas fa-columns';
        }

        if (toggleButton) {
            toggleButton.title = 'Mostrar panel Copilot Health';
        }

        // Restaurar tamaño del formulario
        if (mainContent) {
            mainContent.classList.add('sidebar-hidden');
            mainContent.style.width = '100%';
            mainContent.style.maxWidth = '100%';
            mainContent.style.flex = '1';

            // Forzar reajuste de elementos
            setTimeout(() => {
                if (typeof forceLayoutUpdate === 'function') {
                    forceLayoutUpdate();
                }
            }, 50);
        }

        console.log('✅ Sidebar oculta');
    } else {
        // Mostrar panel
        console.log('🔄 Mostrando sidebar...');
        sidebarContainer.classList.add('show');

        if (toggleIcon) {
            toggleIcon.className = 'fas fa-window-minimize';
        }

        if (toggleButton) {
            toggleButton.title = 'Ocultar panel Copilot Health';
        }

        // Ajustar tamaño del formulario
        if (mainContent) {
            mainContent.classList.remove('sidebar-hidden');
            mainContent.style.width = 'calc(100% - 400px)';
            mainContent.style.maxWidth = 'calc(100% - 400px)';
            mainContent.style.flex = '1';

            // Forzar reajuste de elementos
            setTimeout(() => {
                if (typeof forceLayoutUpdate === 'function') {
                    forceLayoutUpdate();
                }
            }, 50);
        }

        console.log('✅ Sidebar visible');
    }
}

// Función para crear la sidebar si no existe
function crearSidebarSiNoExiste() {
    console.log('🔧 Creando sidebar si no existe...');

    // Verificar si ya existe
    if (document.getElementById('sidebarContainer')) {
        console.log('✅ sidebarContainer ya existe');
        return;
    }

    // Crear la sidebar básica
    const sidebarHtml = `
        <div class="sidebar-container" id="sidebarContainer">
            <div class="sidebar-resize-handle" id="sidebarResizeHandle"></div>
            <div class="panel-content p-3">
                <div class="copilot-chat-elegant" id="copilotChatElegant">
                    <div class="chat-messages-elegant" id="chatMessagesElegant">
                        <div class="messages-container" id="messagesContainer">
                            <div class="message-elegant system-message" id="welcomeMessage">
                                <div class="message-bubble">
                                    <div class="message-text">
                                                                                        <p>¡Hola! Soy Tena, tu asistente IA. ¿En qué puedo ayudarte?</p>
                                    </div>
                                </div>
                                <div class="message-time">Ahora</div>
                            </div>
                        </div>
                    </div>
                    <div class="auto-mode-indicator">
                        <div class="auto-mode-content">
                                                                <span class="auto-mode-text" id="tenaCopilotStatus">Tena Copilot</span>
                        </div>
                        <div class="mt-1">
                            <input type="text" id="copilotQuickInput" placeholder="Escribe tu mensaje aquí..." onkeydown="if(event.key==='Enter'){ if(this.value.trim()){ agregarMensajeElegant(this.value,'user'); enviarMensajeCopilot(this.value); this.value='';}}">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Insertar al final del body
    document.body.insertAdjacentHTML('beforeend', sidebarHtml);
    console.log('✅ sidebarContainer creado');
}

// Función auxiliar para verificar si los elementos existen
function verificarElementosSidebar() {
    const elementos = {
        sidebarContainer: document.getElementById('sidebarContainer'),
        toggleIcon: document.getElementById('sidebarToggleIcon'),
        toggleButton: document.getElementById('sidebarToggle'),
        mainContent: document.querySelector('.col-lg-8.col-xl-9')
    };

    console.log('🔍 Verificando elementos de sidebar:');

    Object.entries(elementos).forEach(([nombre, elemento]) => {
        if (elemento) {
            console.log(`✅ ${nombre}: encontrado`);
        } else {
            console.log(`❌ ${nombre}: NO encontrado`);
        }
    });

    return elementos;
}

// Función para inicializar la sidebar de manera segura
function inicializarSidebarSegura() {
    console.log('🚀 Inicializando sidebar de manera segura...');

    // Verificar elementos
    const elementos = verificarElementosSidebar();

    const sidebarContainer = elementos.sidebarContainer;

    if (sidebarContainer) {
        // Asegurar que la sidebar esté configurada correctamente
        sidebarContainer.style.display = 'block';
        sidebarContainer.style.visibility = 'visible';
        sidebarContainer.style.opacity = '1';

        // El panel estará oculto por defecto
        sidebarContainer.classList.remove('show');

        if (elementos.toggleIcon) {
            elementos.toggleIcon.className = 'fas fa-columns';
        }

        // Configurar el contenido principal
        if (elementos.mainContent) {
            elementos.mainContent.classList.add('sidebar-hidden');
            elementos.mainContent.style.width = '100%';
            elementos.mainContent.style.maxWidth = '100%';
            elementos.mainContent.style.flex = '1';
        }

        console.log('✅ Sidebar inicializada correctamente');
    } else {
        console.error('❌ No se pudo inicializar la sidebar - sidebarContainer no encontrado');
    }
}

// Función para manejar errores de layout
function forceLayoutUpdate() {
    console.log('🔄 Forzando actualización de layout...');

    // Trigger reflow
    document.body.offsetHeight;

    // Disparar evento de resize para forzar reajuste
    window.dispatchEvent(new Event('resize'));

    console.log('✅ Layout actualizado');
}

// Exportar funciones para uso global
window.toggleSidebar = toggleSidebar;
window.verificarElementosSidebar = verificarElementosSidebar;
window.inicializarSidebarSegura = inicializarSidebarSegura;
window.forceLayoutUpdate = forceLayoutUpdate;
window.crearSidebarSiNoExiste = crearSidebarSiNoExiste;

// Función para esperar a que los elementos estén disponibles
function esperarElementosSidebar() {
    const sidebarContainer = document.getElementById('sidebarContainer');
    const toggleButton = document.getElementById('sidebarToggle');

    if (sidebarContainer && toggleButton) {
        console.log('✅ Elementos de sidebar encontrados, inicializando...');
        inicializarSidebarSegura();
        return true;
    } else {
        console.log('⏳ Esperando elementos de sidebar...');
        return false;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('📋 DOM cargado, verificando elementos de sidebar...');

    // Intentar inicializar inmediatamente
    if (!esperarElementosSidebar()) {
        // Si no están disponibles, esperar un poco más
        setTimeout(() => {
            if (!esperarElementosSidebar()) {
                // Si aún no están disponibles, intentar cada 100ms por 5 segundos
                let intentos = 0;
                const maxIntentos = 50;
                const intervalo = setInterval(() => {
                    intentos++;
                    if (esperarElementosSidebar() || intentos >= maxIntentos) {
                        clearInterval(intervalo);
                        if (intentos >= maxIntentos) {
                            console.warn('⚠️ No se pudieron encontrar los elementos de sidebar después de 5 segundos');
                        }
                    }
                }, 100);
            }
        }, 500);
    }
});

// También inicializar inmediatamente si el DOM ya está listo
if (document.readyState === 'loading') {
    console.log('📋 DOM aún cargando...');
} else {
    console.log('📋 DOM ya cargado, verificando elementos inmediatamente...');
    if (!esperarElementosSidebar()) {
        // Si no están disponibles, esperar un poco más
        setTimeout(esperarElementosSidebar, 100);
    }
}

console.log('✅ toggleSidebar corregido cargado'); 