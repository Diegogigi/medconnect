// Script de prueba para verificar la funcionalidad de resize de la sidebar
console.log('🧪 Iniciando prueba de resize de sidebar...');

// Función para verificar que los elementos existen
function verificarElementosSidebar() {
    const sidebarContainer = document.getElementById('sidebarContainer');
    const resizeHandle = document.getElementById('sidebarResizeHandle');
    const mainContent = document.querySelector('.col-lg-8.col-xl-9');

    console.log('📋 Verificando elementos de sidebar:');
    console.log('- sidebarContainer:', sidebarContainer ? '✅ Encontrado' : '❌ No encontrado');
    console.log('- resizeHandle:', resizeHandle ? '✅ Encontrado' : '❌ No encontrado');
    console.log('- mainContent:', mainContent ? '✅ Encontrado' : '❌ No encontrado');

    if (sidebarContainer) {
        console.log('- Ancho actual de sidebar:', sidebarContainer.offsetWidth + 'px');
        console.log('- Estilos de sidebar:', {
            width: sidebarContainer.style.width,
            display: sidebarContainer.style.display,
            visibility: sidebarContainer.style.visibility,
            opacity: sidebarContainer.style.opacity
        });
    }

    if (resizeHandle) {
        console.log('- Estilos de resize handle:', {
            width: resizeHandle.style.width,
            background: resizeHandle.style.background,
            cursor: resizeHandle.style.cursor
        });
    }

    return sidebarContainer && resizeHandle && mainContent;
}

// Función para probar el resize
function probarResize() {
    console.log('🔧 Probando funcionalidad de resize...');

    const sidebarContainer = document.getElementById('sidebarContainer');
    const resizeHandle = document.getElementById('sidebarResizeHandle');

    if (!sidebarContainer || !resizeHandle) {
        console.log('❌ No se pueden probar los elementos - no encontrados');
        return;
    }

    // Simular un evento de resize
    const anchoOriginal = sidebarContainer.offsetWidth;
    console.log('- Ancho original:', anchoOriginal + 'px');

    // Cambiar el ancho manualmente para probar
    const nuevoAncho = anchoOriginal + 50;
    sidebarContainer.style.width = nuevoAncho + 'px';

    console.log('- Ancho después del cambio:', sidebarContainer.offsetWidth + 'px');
    console.log('- Cambio aplicado:', sidebarContainer.offsetWidth !== anchoOriginal ? '✅' : '❌');

    // Restaurar el ancho original
    setTimeout(() => {
        sidebarContainer.style.width = anchoOriginal + 'px';
        console.log('- Ancho restaurado:', sidebarContainer.offsetWidth + 'px');
    }, 1000);
}

// Función para verificar localStorage
function verificarLocalStorage() {
    console.log('💾 Verificando localStorage:');
    const savedWidth = localStorage.getItem('sidebarWidth');
    console.log('- Ancho guardado:', savedWidth ? savedWidth + 'px' : 'No hay ancho guardado');

    if (savedWidth) {
        const width = parseInt(savedWidth);
        console.log('- Ancho como número:', width + 'px');
        console.log('- Es válido:', width >= 300 && width <= window.innerWidth * 0.6 ? '✅' : '❌');
    }
}

// Función para probar la persistencia
function probarPersistencia() {
    console.log('💾 Probando persistencia de tamaño...');

    const sidebarContainer = document.getElementById('sidebarContainer');
    if (!sidebarContainer) return;

    const anchoActual = sidebarContainer.offsetWidth;
    console.log('- Ancho actual:', anchoActual + 'px');

    // Guardar en localStorage
    localStorage.setItem('sidebarWidth', anchoActual);
    console.log('- Ancho guardado en localStorage');

    // Simular recarga de página
    const anchoGuardado = localStorage.getItem('sidebarWidth');
    console.log('- Ancho recuperado:', anchoGuardado + 'px');

    console.log('- Persistencia:', anchoGuardado == anchoActual ? '✅ Funciona' : '❌ No funciona');
}

// Función principal de prueba
function ejecutarPruebasSidebar() {
    console.log('🚀 Ejecutando pruebas completas de sidebar...');
    console.log('='.repeat(50));

    // Verificar elementos
    const elementosExisten = verificarElementosSidebar();
    console.log('='.repeat(50));

    if (elementosExisten) {
        // Probar resize
        probarResize();
        console.log('='.repeat(50));

        // Verificar localStorage
        verificarLocalStorage();
        console.log('='.repeat(50));

        // Probar persistencia
        probarPersistencia();
        console.log('='.repeat(50));

        console.log('✅ Todas las pruebas completadas');
    } else {
        console.log('❌ No se pueden ejecutar las pruebas - elementos faltantes');
    }
}

// Ejecutar pruebas cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ejecutarPruebasSidebar);
} else {
    ejecutarPruebasSidebar();
}

// Exportar funciones para uso manual
window.probarSidebarResize = {
    verificarElementos: verificarElementosSidebar,
    probarResize: probarResize,
    verificarLocalStorage: verificarLocalStorage,
    probarPersistencia: probarPersistencia,
    ejecutarTodas: ejecutarPruebasSidebar
};

console.log('📝 Funciones de prueba disponibles en window.probarSidebarResize'); 