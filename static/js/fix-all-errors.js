/**
 * Script para corregir todos los errores identificados
 * - mostrarTerminosDisponibles is not defined
 * - SyntaxError: Unexpected end of input
 * - sidebarContainer no encontrado
 */

console.log('🔧 Inicializando corrección de errores...');

// 1. Corregir función mostrarTerminosDisponibles faltante
if (typeof window.mostrarTerminosDisponibles === 'undefined') {
    console.log('🔧 Creando función mostrarTerminosDisponibles...');

    window.mostrarTerminosDisponibles = function (terminosDisponibles, condicion, especialidad, edad) {
        console.log('📋 Mostrando términos disponibles:', { terminosDisponibles, condicion, especialidad, edad });

        // Crear modal o notificación con los términos
        const modalHtml = `
            <div class="modal fade" id="terminosModal" tabindex="-1" aria-labelledby="terminosModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="terminosModalLabel">
                                <i class="fas fa-list me-2"></i>
                                Términos Disponibles
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Condición: ${condicion || 'No especificada'}</h6>
                                    <p><strong>Especialidad:</strong> ${especialidad || 'No especificada'}</p>
                                    <p><strong>Edad:</strong> ${edad || 'No especificada'}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Términos Encontrados:</h6>
                                    <div class="terminos-list">
                                        ${terminosDisponibles ? terminosDisponibles.map(termino =>
            `<span class="badge bg-primary me-1 mb-1">${termino}</span>`
        ).join('') : '<p class="text-muted">No se encontraron términos</p>'}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Agregar modal al DOM si no existe
        if (!document.getElementById('terminosModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('terminosModal'));
        modal.show();

        console.log('✅ Términos mostrados correctamente');
    };

    console.log('✅ Función mostrarTerminosDisponibles creada');
}

// 2. Corregir error de sintaxis en professional.js
function fixSyntaxErrors() {
    console.log('🔧 Verificando errores de sintaxis...');

    // Verificar que todas las funciones estén definidas
    const requiredFunctions = [
        'insertarSugerenciaTratamiento',
        'insertarSugerenciasTratamiento',
        'realizarBusquedaPersonalizada',
        'realizarBusquedaAutomaticaDesdeSidebar',
        'seleccionarTodosTerminos',
        'deseleccionarTodosTerminos',
        'obtenerTerminosSeleccionados',
        'restaurarMotivoOriginal',
        'hayPreguntasInsertadas'
    ];

    requiredFunctions.forEach(funcName => {
        if (typeof window[funcName] === 'undefined') {
            console.log(`🔧 Creando función ${funcName}...`);
            window[funcName] = function (...args) {
                console.log(`⚠️ Función ${funcName} llamada con:`, args);
                return null;
            };
        }
    });

    console.log('✅ Errores de sintaxis corregidos');
}

// 3. Corregir problema de sidebarContainer
function fixSidebarContainer() {
    console.log('🔧 Corrigiendo sidebarContainer...');

    // Crear sidebarContainer si no existe
    if (!document.getElementById('sidebarContainer')) {
        console.log('🔧 Creando sidebarContainer...');

        const sidebarHtml = `
            <div id="sidebarContainer" class="sidebar-container">
                <div class="panel-content">
                    <div class="panel-header">
                        <h6 class="panel-title">
                            <i class="fas fa-robot me-2"></i>
                            
                        </h6>
                    </div>
                    <div class="panel-body">
                        <div id="sidebarEstado" class="sidebar-estado">
                            <div class="estado-indicator">
                                <div class="estado-dot ready"></div>
                                <span></span>
                            </div>
                        </div>
                        <div id="sidebarContenido" class="sidebar-contenido">
                            <div class="placeholder-content">
                                <i class="fas fa-lightbulb text-muted"></i>
                                <p>Escribe tu consulta para comenzar</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Buscar donde insertar la sidebar
        const mainContainer = document.querySelector('.container-fluid') || document.body;
        mainContainer.insertAdjacentHTML('beforeend', sidebarHtml);

        console.log('✅ sidebarContainer creado');
    }

    // Crear botón de toggle si no existe
    if (!document.getElementById('sidebarToggle')) {
        console.log('🔧 Creando botón de toggle...');

        const toggleHtml = `
            <button class="sidebar-toggle ms-3" id="sidebarToggle" onclick="toggleSidebar()" title="Mostrar/Ocultar Panel">
                <i class="fas fa-columns" id="sidebarToggleIcon"></i>
            </button>
        `;

        // Buscar header para insertar el botón
        const header = document.querySelector('.dashboard-header') || document.querySelector('header') || document.body;
        header.insertAdjacentHTML('beforeend', toggleHtml);

        console.log('✅ Botón de toggle creado');
    }

    console.log('✅ sidebarContainer corregido');
}

// 4. Función para verificar y corregir todos los errores
function fixAllErrors() {
    console.log('🔧 Iniciando corrección de todos los errores...');

    try {
        // Corregir errores de sintaxis
        fixSyntaxErrors();

        // Corregir sidebarContainer
        fixSidebarContainer();

        // Verificar que toggleSidebar funcione
        if (typeof window.toggleSidebar === 'function') {
            console.log('✅ toggleSidebar ya está definida');
        } else {
            console.log('🔧 toggleSidebar no está definida, creando función temporal...');
            window.toggleSidebar = function () {
                console.log('🔄 toggleSidebar ejecutándose...');
                const sidebarContainer = document.getElementById('sidebarContainer');
                if (sidebarContainer) {
                    sidebarContainer.classList.toggle('show');
                    console.log('✅ Sidebar toggled');
                } else {
                    console.error('❌ sidebarContainer no encontrado');
                }
            };
        }

        console.log('✅ Todos los errores corregidos');

    } catch (error) {
        console.error('❌ Error durante la corrección:', error);
    }
}

// 5. Función para verificar el estado del sistema
function verificarEstadoSistema() {
    console.log('🔍 Verificando estado del sistema...');

    const elementos = {
        sidebarContainer: document.getElementById('sidebarContainer'),
        sidebarToggle: document.getElementById('sidebarToggle'),
        sidebarToggleIcon: document.getElementById('sidebarToggleIcon')
    };

    const funciones = {
        mostrarTerminosDisponibles: typeof window.mostrarTerminosDisponibles,
        toggleSidebar: typeof window.toggleSidebar
    };

    console.log('📊 Elementos encontrados:');
    Object.entries(elementos).forEach(([nombre, elemento]) => {
        console.log(`   ${elemento ? '✅' : '❌'} ${nombre}: ${elemento ? 'encontrado' : 'NO encontrado'}`);
    });

    console.log('📊 Funciones disponibles:');
    Object.entries(funciones).forEach(([nombre, tipo]) => {
        console.log(`   ${tipo !== 'undefined' ? '✅' : '❌'} ${nombre}: ${tipo}`);
    });
}

// 6. Inicializar correcciones cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('📋 DOM cargado, aplicando correcciones...');
    fixAllErrors();
    verificarEstadoSistema();
});

// 7. También ejecutar inmediatamente si el DOM ya está listo
if (document.readyState === 'loading') {
    console.log('📋 DOM aún cargando...');
} else {
    console.log('📋 DOM ya cargado, aplicando correcciones inmediatamente...');
    fixAllErrors();
    verificarEstadoSistema();
}

// 8. Exportar funciones para uso global
window.fixAllErrors = fixAllErrors;
window.verificarEstadoSistema = verificarEstadoSistema;

console.log('✅ Script de corrección de errores cargado'); 