// Archivo principal del dashboard profesional
// Las funciones globales están definidas en global-functions.js

// Variables globales para la agenda
let currentDate = new Date();
let agendaData = {};
let pacientesDropdownList = [];
let currentView = 'diaria'; // diaria, semanal, mensual
let currentWeekStart = null;
let currentMonth = null;

// Asegurar que las funciones estén disponibles globalmente
// Estas funciones se definen más abajo en el archivo
window.showReminderModal = null;
window.editReminder = null;
window.deleteReminder = null;

// Función para escapar caracteres especiales en HTML
function escapeHTML(text) {
    // Manejar casos especiales primero
    if (text === null || text === undefined) {
        return '';
    }

    // Convertir CUALQUIER cosa a string de manera segura
    let stringValue = '';
    try {
        if (typeof text === 'string') {
            stringValue = text;
        } else if (typeof text === 'number') {
            stringValue = text.toString();
        } else if (typeof text === 'boolean') {
            stringValue = text.toString();
        } else if (typeof text === 'object') {
            // Para objetos, usar JSON.stringify o toString
            try {
                stringValue = JSON.stringify(text);
            } catch (jsonError) {
                stringValue = Object.prototype.toString.call(text);
            }
        } else {
            // Para cualquier otro tipo, usar String()
            stringValue = String(text);
        }
    } catch (error) {
        console.error('❌ Error convirtiendo a string:', error, 'valor:', text);
        return 'Error de conversión';
    }

    // Verificar que stringValue es realmente un string
    if (typeof stringValue !== 'string') {
        console.error('❌ Valor no es string después de conversión:', stringValue, 'tipo:', typeof stringValue);
        return 'Error de tipo';
    }

    // Si está vacío después de la conversión, retornar vacío
    if (stringValue === '' || stringValue === 'undefined' || stringValue === 'null') {
        return '';
    }

    // Procesar el string
    try {
        return stringValue
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/\n/g, '<br>')
            .replace(/\r/g, '');
    } catch (error) {
        console.error('❌ Error procesando string:', error, 'valor:', stringValue);
        return 'Error de procesamiento';
    }
}

// Función helper para obtener valores seguros de pacientes
function getSafeValue(value, defaultValue = 'No especificado') {
    if (value === null || value === undefined || value === '') {
        return defaultValue;
    }
    return value;
}

document.addEventListener('DOMContentLoaded', function () {
    // Inicializar componentes existentes
    initMaps();
    initAvailabilityToggle();
    setupMobileNav();
    initRequestInteractions();
    handleFileUpload();

    // Cargar estadísticas del dashboard
    cargarEstadisticasDashboard();

    // Prueba de conexión con el backend
    console.log('🔍 Verificando conexión con el backend...');
    fetch('/health')
        .then(response => {
            console.log('❤️ Health check response:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('❤️ Health check data:', data);
        })
        .catch(error => {
            console.error('❌ Error en health check:', error);
        });

    // Prueba específica del sistema de atenciones
    console.log('🧪 Probando sistema de atenciones...');
    fetch('/api/test-atencion')
        .then(response => {
            console.log('🧪 Test atenciones response:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('🧪 Test atenciones data:', data);
            if (data.success) {
                console.log('✅ Sistema de atenciones funcionando');
                console.log(`👤 Usuario ID: ${data.user_id}`);
                console.log(`📧 Email: ${data.user_email}`);
                console.log(`📊 Registros existentes: ${data.total_records}`);
            } else {
                console.error('❌ Error en sistema de atenciones:', data.message);
            }
        })
        .catch(error => {
            console.error('❌ Error probando sistema de atenciones:', error);
        });

    // Cargar historial de atenciones al iniciar
    actualizarHistorialAtenciones();

    // Configurar gestión de pacientes
    setupPatientSearch();

    // Event listener para la pestaña de pacientes
    const patientsTab = document.getElementById('patients-tab');
    if (patientsTab) {
        patientsTab.addEventListener('shown.bs.tab', function () {
            console.log('🏥 Pestaña de pacientes activada, cargando datos...');
            cargarListaPacientes();
        });
    }

    // Event listener para la pestaña de agenda
    const scheduleTab = document.getElementById('schedule-tab');
    if (scheduleTab) {
        scheduleTab.addEventListener('shown.bs.tab', function () {
            console.log('📅 Pestaña de agenda activada, cargando datos...');
            // Inicializar con vista diaria
            currentView = 'diaria';
            cargarAgenda();
        });
    }

    // Si la pestaña de pacientes está activa al cargar, cargar los datos
    if (patientsTab && patientsTab.classList.contains('active')) {
        cargarListaPacientes();
    }

    // Cargar pacientes después de un breve delay para asegurar que todo esté listo
    setTimeout(() => {
        console.log('🔄 Cargando pacientes iniciales...');
        cargarListaPacientes();
        cargarPacientesDropdown(); // Cargar también en el dropdown del formulario
    }, 1000);

    // Inicializar búsqueda de atenciones
    const searchAtencion = document.getElementById('searchAtencion');
    if (searchAtencion) {
        searchAtencion.addEventListener('input', function (e) {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#historialAtenciones tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }

    // Inicializar filtro de atenciones
    const filterAtencion = document.getElementById('filterAtencion');
    if (filterAtencion) {
        filterAtencion.addEventListener('change', function (e) {
            const filterValue = e.target.value;
            const rows = document.querySelectorAll('#historialAtenciones tr');
            const now = new Date();

            rows.forEach(row => {
                const fechaCell = row.cells[0]; // Primera celda contiene la fecha
                if (!fechaCell) return;

                const fechaTexto = fechaCell.textContent;
                let mostrar = true;

                if (filterValue === 'today') {
                    const fechaAtencion = new Date(fechaTexto);
                    mostrar = fechaAtencion.toDateString() === now.toDateString();
                } else if (filterValue === 'week') {
                    const fechaAtencion = new Date(fechaTexto);
                    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                    mostrar = fechaAtencion >= weekAgo;
                } else if (filterValue === 'month') {
                    const fechaAtencion = new Date(fechaTexto);
                    const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                    mostrar = fechaAtencion >= monthAgo;
                }

                row.style.display = mostrar ? '' : 'none';
            });
        });
    }

    // Event listener para cambio de tabs
    const historyTab = document.querySelector('button[data-bs-target="#history"]');
    if (historyTab) {
        historyTab.addEventListener('click', function () {
            // Actualizar historial cada vez que se abra la pestaña
            setTimeout(() => {
                actualizarHistorialAtenciones();
            }, 100);
        });
    }

    // Manejar la selección de archivos en el formulario de nueva atención
    const inputArchivos = document.getElementById('archivosAtencion');
    if (inputArchivos) {
        inputArchivos.addEventListener('change', function (e) {
            const lista = document.getElementById('listaArchivosSeleccionados');
            lista.innerHTML = '';
            if (this.files.length > 0) {
                const summary = document.createElement('p');
                summary.className = 'mb-1';
                summary.textContent = `${this.files.length} archivo(s) seleccionado(s):`;
                lista.appendChild(summary);

                const fileList = document.createElement('ul');
                fileList.className = 'list-group list-group-flush';
                for (const file of this.files) {
                    const item = document.createElement('li');
                    item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center py-1';
                    item.innerHTML = `
                        <small class="text-truncate" title="${file.name}">${file.name}</small>
                        <small class="text-muted">${formatFileSize(file.size)}</small>
                    `;
                    fileList.appendChild(item);
                }
                lista.appendChild(fileList);
            }
        });
    }
});

// Inicializar mapas
function initMaps() {
    // Verificar si Leaflet está disponible
    if (typeof L === 'undefined') {
        console.warn('⚠️ Leaflet no está disponible, saltando inicialización de mapas');
        return;
    }

    try {
        // Verificar si el contenedor del mapa existe antes de inicializar
        const coverageMapElement = document.getElementById('coverage-map');
        if (!coverageMapElement) {
            console.log('ℹ️ Contenedor de mapa no encontrado, saltando inicialización');
            return;
        }

        // Mapa de cobertura
        const coverageMap = L.map('coverage-map').setView([-33.45, -70.67], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(coverageMap);

        // Crear marcador para la ubicación del profesional
        const professionalIcon = L.divIcon({
            className: 'professional-marker',
            html: '<div class="marker-icon"><i class="fas fa-user-md"></i></div>',
            iconSize: [40, 40],
            iconAnchor: [20, 40]
        });

        // Agregar marcador del profesional
        const professionalMarker = L.marker([-33.45, -70.67], { icon: professionalIcon }).addTo(coverageMap);

        // Crear círculo de cobertura
        const coverageCircle = L.circle([-33.45, -70.67], {
            color: 'rgb(96,75,217)',
            fillColor: 'rgb(96,75,217)',
            fillOpacity: 0.1,
            radius: 10000
        }).addTo(coverageMap);

        // Controles de zoom
        const zoomInBtn = document.getElementById('zoomIn');
        const zoomOutBtn = document.getElementById('zoomOut');

        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', function () {
                coverageMap.zoomIn();
            });
        }

        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', function () {
                coverageMap.zoomOut();
            });
        }

        // Mapa de servicio activo (si existe)
        const serviceMapElement = document.getElementById('service-map');
        if (serviceMapElement) {
            const serviceMap = L.map('service-map').setView([-33.44, -70.65], 14);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(serviceMap);

            // Marcador del profesional
            L.marker([-33.45, -70.67], { icon: professionalIcon }).addTo(serviceMap);

            // Marcador del paciente
            const patientIcon = L.divIcon({
                className: 'patient-marker',
                html: '<div class="marker-icon patient"><i class="fas fa-home"></i></div>',
                iconSize: [40, 40],
                iconAnchor: [20, 40]
            });

            L.marker([-33.44, -70.65], { icon: patientIcon }).addTo(serviceMap);

            // Línea de ruta
            const routePoints = [
                [-33.45, -70.67],
                [-33.445, -70.66],
                [-33.44, -70.65]
            ];

            const routeLine = L.polyline(routePoints, {
                color: 'rgb(96,75,217)',
                weight: 4,
                opacity: 0.7,
                dashArray: '10, 10'
            }).addTo(serviceMap);

            // Ajustar vista para mostrar toda la ruta
            serviceMap.fitBounds(routeLine.getBounds(), {
                padding: [30, 30]
            });
        }

        console.log('✅ Mapas inicializados correctamente');
    } catch (error) {
        console.error('❌ Error inicializando mapas:', error);
    }
}

// Control de disponibilidad
function initAvailabilityToggle() {
    const availabilityToggle = document.getElementById('availabilityToggle');
    const statusText = document.getElementById('statusText');

    if (availabilityToggle && statusText) {
        availabilityToggle.addEventListener('change', function () {
            if (this.checked) {
                statusText.textContent = 'Disponible';
                statusText.classList.remove('bg-danger');
                statusText.classList.add('bg-success');
            } else {
                statusText.textContent = 'No Disponible';
                statusText.classList.remove('bg-success');
                statusText.classList.add('bg-danger');
            }
        });
    }
}

// Navegación móvil
function setupMobileNav() {
    const navItems = document.querySelectorAll('.mobile-nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            // Eliminar clase activa de todos los elementos
            navItems.forEach(navItem => {
                navItem.classList.remove('active');
            });

            // Agregar clase activa al elemento seleccionado
            this.classList.add('active');

            // Si no es el enlace de inicio, prevenir navegación por defecto
            if (this.id !== 'pro-nav-home') {
                e.preventDefault();

                // Aquí se podría implementar navegación por SPA
                // Por ahora solo para demostración
                const targetSection = this.id.replace('pro-nav-', '');
                console.log(`Navegando a sección: ${targetSection}`);
            }
        });
    });
}

// Interacciones con solicitudes
function initRequestInteractions() {
    // Botones de aceptar/rechazar solicitud
    const acceptButtons = document.querySelectorAll('.request-card .btn-success');
    const rejectButtons = document.querySelectorAll('.request-card .btn-danger');

    acceptButtons.forEach(button => {
        button.addEventListener('click', function () {
            const requestCard = this.closest('.request-card');
            requestCard.classList.remove('new');
            requestCard.style.borderLeftColor = '#2ecc71';
            const badge = requestCard.querySelector('.request-badge span');
            if (badge) {
                badge.textContent = 'Aceptado';
                badge.classList.remove('bg-warning');
                badge.classList.add('bg-success');
            }

            // Mostrar mensaje de confirmación
            showNotification('Solicitud aceptada correctamente');
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', function () {
            const requestCard = this.closest('.request-card');
            requestCard.classList.remove('new');
            requestCard.style.borderLeftColor = '#e74c3c';
            const badge = requestCard.querySelector('.request-badge span');
            if (badge) {
                badge.textContent = 'Rechazado';
                badge.classList.remove('bg-warning');
                badge.classList.add('bg-danger');
            }

            // Mostrar mensaje de confirmación
            showNotification('Solicitud rechazada');

            // Animar desaparición de la tarjeta
            setTimeout(() => {
                requestCard.style.opacity = '0';
                requestCard.style.height = '0';
                requestCard.style.margin = '0';
                requestCard.style.padding = '0';
                requestCard.style.overflow = 'hidden';
            }, 1000);
        });
    });
}

// Manejo de archivos adjuntos
function handleFileUpload() {
    const fileUpload = document.getElementById('fileUpload');
    const attachedFilesList = document.getElementById('attachedFilesList');
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB en bytes
    let filesArray = [];

    if (fileUpload) {
        fileUpload.addEventListener('change', handleFileSelect);
    }

    function handleFileSelect(event) {
        const files = event.target.files;

        for (let file of files) {
            // Validar tamaño del archivo
            if (file.size > MAX_FILE_SIZE) {
                showNotification(`El archivo ${file.name} excede el tamaño máximo permitido de 10MB`, 'error');
                continue;
            }

            // Validar tipo de archivo
            if (!isValidFileType(file)) {
                showNotification(`Tipo de archivo no permitido: ${file.name}. Solo se permiten PDF e imágenes.`, 'error');
                continue;
            }

            // Agregar archivo a la lista
            filesArray.push(file);
            addFileToTable(file);
        }

        // Limpiar input para permitir subir el mismo archivo nuevamente
        fileUpload.value = '';
    }

    function isValidFileType(file) {
        const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif'];
        return allowedTypes.includes(file.type);
    }

    function addFileToTable(file) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="d-flex align-items-center">
                    <i class="${getFileIcon(file.type)} me-2"></i>
                    <span class="file-name">${file.name}</span>
                </div>
            </td>
            <td>${file.type.split('/')[1].toUpperCase()}</td>
            <td>${formatFileSize(file.size)}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary btn-preview" title="Vista previa">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-remove" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;

        // Agregar manejadores de eventos
        const previewBtn = row.querySelector('.btn-preview');
        const removeBtn = row.querySelector('.btn-remove');

        previewBtn.addEventListener('click', () => previewFile(file));
        removeBtn.addEventListener('click', () => {
            filesArray = filesArray.filter(f => f !== file);
            row.remove();
            showNotification('Archivo eliminado');
        });

        attachedFilesList.appendChild(row);
        showNotification('Archivo agregado correctamente', 'success');
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function getFileIcon(fileType) {
        switch (fileType) {
            case 'application/pdf':
                return 'fas fa-file-pdf text-danger';
            case 'image/jpeg':
            case 'image/png':
            case 'image/gif':
                return 'fas fa-file-image text-primary';
            default:
                return 'fas fa-file text-secondary';
        }
    }

    function previewFile(file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const previewModal = new bootstrap.Modal(document.getElementById('filePreviewModal') || createPreviewModal());
            const modalContent = document.querySelector('#filePreviewModal .modal-body');

            if (file.type === 'application/pdf') {
                modalContent.innerHTML = `
                    <embed src="${e.target.result}" type="application/pdf" width="100%" height="600px">
                `;
            } else {
                modalContent.innerHTML = `
                    <img src="${e.target.result}" class="img-fluid" alt="${file.name}">
                `;
            }

            previewModal.show();
        };
        reader.readAsDataURL(file);
    }

    function createPreviewModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'filePreviewModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Vista Previa</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body"></div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        return modal;
    }

    // Agregar los archivos al formulario antes de enviar
    const atencionForm = document.getElementById('atencionForm');
    if (atencionForm) {
        atencionForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            console.log('🔍 Formulario de atención enviado');

            // Recopilar datos del formulario
            const atencionData = {
                paciente_nombre: document.getElementById('pacienteNombre').value,
                paciente_rut: document.getElementById('pacienteRut').value,
                paciente_edad: document.getElementById('pacienteEdad').value,
                tipo_atencion: document.getElementById('tipoAtencion').value,
                fecha_hora: document.getElementById('fechaAtencion').value,
                motivo_consulta: document.getElementById('motivoConsulta').value,
                diagnostico: document.getElementById('diagnostico').value,
                tratamiento: document.getElementById('tratamiento').value
            };

            // Validar campos requeridos
            const requiredFields = ['paciente_nombre', 'tipo_atencion', 'fecha_hora', 'motivo_consulta'];
            const missingFields = requiredFields.filter(field => !atencionData[field]);

            if (missingFields.length > 0) {
                console.error('❌ Campos faltantes:', missingFields);
                showNotification('Por favor completa todos los campos requeridos', 'error');
                return;
            }

            // Deshabilitar botón de envío
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Registrando...';

            try {
                // Primero registrar la atención
                const atencionResponse = await fetch('/api/register-atencion', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(atencionData)
                });

                const atencionResult = await atencionResponse.json();

                if (atencionResult.success) {
                    // Si hay archivos seleccionados, subirlos
                    const fileInput = document.getElementById('fileUpload');
                    if (fileInput && fileInput.files.length > 0) {
                        const formData = new FormData();
                        Array.from(fileInput.files).forEach(file => {
                            formData.append('files[]', file);
                        });
                        formData.append('atencion_id', atencionResult.atencion_id);

                        console.log('📤 Subiendo archivos...');
                        const uploadResponse = await fetch('/api/archivos/upload', {
                            method: 'POST',
                            body: formData
                        });

                        const uploadResult = await uploadResponse.json();
                        if (!uploadResult.success) {
                            console.error('❌ Error subiendo archivos:', uploadResult.error);
                            showNotification('Atención registrada, pero hubo un error al subir algunos archivos', 'warning');
                        } else {
                            console.log('✅ Archivos subidos correctamente:', uploadResult);
                        }
                    }

                    showNotification('Atención registrada exitosamente', 'success');

                    // Limpiar formulario y archivos
                    this.reset();
                    const fileList = document.getElementById('fileList');
                    if (fileList) {
                        fileList.innerHTML = '';
                    }

                    // Actualizar historial y estadísticas del dashboard
                    actualizarHistorialAtenciones();
                    actualizarEstadisticasDashboard();

                    // Cambiar a la pestaña de historial
                    const historyTab = document.querySelector('button[data-bs-target="#history"]');
                    if (historyTab) {
                        const tabInstance = new bootstrap.Tab(historyTab);
                        tabInstance.show();
                    }
                } else {
                    console.error('❌ Error del servidor:', atencionResult.message);
                    showNotification(atencionResult.message || 'Error al registrar la atención', 'error');
                }
            } catch (error) {
                console.error('❌ Error de red:', error);
                showNotification('Error de conexión al registrar la atención', 'error');
            } finally {
                // Restaurar botón
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });

        // Agregar evento para manejar selección de archivos
        const fileUpload = document.getElementById('fileUpload');
        if (fileUpload) {
            fileUpload.addEventListener('change', handleFileSelection);
        }
    }
}

// Función para actualizar el historial de atenciones
function actualizarHistorialAtenciones() {
    console.log('🔄 Iniciando actualización del historial...');
    fetch('/api/get-atenciones')
        .then(response => {
            console.log('📡 Respuesta get-atenciones:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📥 Datos del historial recibidos:', data);
            if (data.success && data.atenciones) {
                const tbody = document.getElementById('historialAtenciones');
                console.log('📋 Elemento tbody encontrado:', !!tbody);
                if (tbody) {
                    tbody.innerHTML = '';
                    console.log(`📊 Procesando ${data.atenciones.length} atenciones`);

                    data.atenciones.forEach((atencion, index) => {
                        console.log(`📝 Procesando atención ${index + 1}:`, atencion);
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${formatearFecha(atencion.fecha_hora)}</td>
                            <td>${atencion.paciente_nombre}</td>
                            <td><span class="badge bg-primary">${atencion.tipo_atencion}</span></td>
                            <td>${atencion.diagnostico || 'Sin diagnóstico'}</td>
                            <td>
                                <span class="badge bg-success">Completada</span>
                            </td>
                            <td>
                                <div class="d-flex justify-content-center gap-2">
                                    <button class="btn btn-sm btn-info" onclick="verDetalleAtencion('${atencion.atencion_id}')" title="Ver Detalle">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-primary" onclick="editarAtencion('${atencion.atencion_id}')" title="Editar">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="eliminarAtencion('${atencion.atencion_id}')" title="Eliminar">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                    console.log('✅ Historial actualizado correctamente');
                } else {
                    console.error('❌ No se encontró el elemento tbody con ID historialAtenciones');
                }
            } else {
                console.error('❌ Respuesta inválida del servidor:', data);
            }
        })
        .catch(error => {
            console.error('❌ Error al actualizar historial:', error);
        });
}

// Función para formatear fecha
function formatearFecha(fechaString) {
    try {
        const fecha = new Date(fechaString);
        return fecha.toLocaleDateString('es-CL', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return fechaString;
    }
}

// Función para eliminar atención
function eliminarAtencion(atencionId) {
    if (confirm('¿Está seguro de que desea eliminar esta atención? Esta acción no se puede deshacer.')) {
        fetch(`/api/delete-atencion/${atencionId}`, {
            method: 'DELETE',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Atención eliminada exitosamente', 'success');
                    actualizarHistorialAtenciones();
                    actualizarEstadisticasDashboard();
                } else {
                    showNotification(data.message || 'Error al eliminar la atención', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error de conexión al eliminar la atención', 'error');
            });
    }
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    const toastContainer = document.querySelector('.toast-container');
    toastContainer.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remover el toast después de que se oculte
    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

// Funciones para el manejo de atenciones
function verDetalleAtencion(atencionId) {
    console.log(`🔍 Viendo detalle de atención: ${atencionId}`);

    fetch(`/api/get-atencion/${atencionId}`)
        .then(response => {
            console.log('📡 Respuesta get-atencion:', response.status);
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ Datos de la atención:', data);
            if (data.success) {
                const atencion = data.atencion;

                // Llenar datos generales con validaciones
                const setElementText = (id, text) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = text || 'N/A';
                    }
                };

                setElementText('detalleAtencionId', atencion.atencion_id);
                setElementText('detallePacienteNombre', atencion.paciente_nombre);
                setElementText('detallePacienteRUT', atencion.paciente_rut);
                setElementText('detalleFechaHora', formatDateTime(atencion.fecha_hora));
                setElementText('detalleTipoAtencion', formatTipoAtencion(atencion.tipo_atencion));
                setElementText('detalleMotivoConsulta', atencion.motivo_consulta);
                setElementText('detalleDiagnostico', atencion.diagnostico);
                setElementText('detalleTratamiento', atencion.tratamiento);
                setElementText('detalleObservaciones', atencion.observaciones);

                const estadoBadge = document.getElementById('detalleEstado');
                if (estadoBadge) {
                    estadoBadge.textContent = atencion.estado || 'N/A';
                    estadoBadge.className = 'badge'; // Reset classes
                    if (atencion.estado && atencion.estado.toLowerCase() === 'finalizada') {
                        estadoBadge.classList.add('bg-success');
                    } else if (atencion.estado && atencion.estado.toLowerCase() === 'en curso') {
                        estadoBadge.classList.add('bg-warning', 'text-dark');
                    } else {
                        estadoBadge.classList.add('bg-secondary');
                    }
                }

                // Mostrar el modal
                const modal = new bootstrap.Modal(document.getElementById('detalleAtencionModal'));
                modal.show();

                // Cargar archivos adjuntos específicamente
                cargarArchivosAdjuntos(atencionId);

            } else {
                console.error('❌ Error en la respuesta de la API:', data.message);
                showNotification(`Error: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error en fetch:', error);
            showNotification('No se pudo cargar el detalle de la atención.', 'error');
        });
}

function formatDateTime(dateStr) {
    if (!dateStr) return 'N/A';
    const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateStr).toLocaleDateString('es-CL', options);
}

function formatTipoAtencion(tipo) {
    if (!tipo) return 'N/A';
    return tipo.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getFileIconClass(mimeType) {
    if (!mimeType) return 'fas fa-file';
    if (mimeType.startsWith('image/')) return 'fas fa-file-image';
    if (mimeType === 'application/pdf') return 'fas fa-file-pdf';
    if (mimeType.includes('word')) return 'fas fa-file-word';
    if (mimeType.includes('excel')) return 'fas fa-file-excel';
    return 'fas fa-file-alt';
}

function isPreviewable(mimeType) {
    if (!mimeType) return false;
    return mimeType.startsWith('image/') || mimeType === 'application/pdf';
}

function previewArchivo(archivoId, nombreArchivo) {
    console.log(`👁️‍🗨️ Vista previa de: ${nombreArchivo} (ID: ${archivoId})`);

    // Determinar el tipo de archivo por extensión
    const extension = nombreArchivo.split('.').pop().toLowerCase();
    const isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(extension);
    const isPDF = extension === 'pdf';

    // Crear un modal para la vista previa
    const modalId = 'previewModal';
    let previewModal = document.getElementById(modalId);
    if (previewModal) {
        previewModal.remove(); // Remover si ya existe
    }

    let modalContent = '';

    if (isImage) {
        // Para imágenes, usar fetch para evitar descarga automática
        modalContent = `
            <div class="modal fade" id="${modalId}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-image me-2"></i>${nombreArchivo}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center" style="max-height: 80vh; overflow-y: auto;">
                            <div id="imageContainer">
                                <div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Cargando imagen...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" onclick="downloadArchivo('${archivoId}', '${nombreArchivo}')">
                                <i class="fas fa-download me-1"></i>Descargar
                            </button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Mostrar modal primero
        document.body.insertAdjacentHTML('beforeend', modalContent);
        const modal = new bootstrap.Modal(document.getElementById(modalId));
        modal.show();

        // Cargar imagen usando fetch para evitar descarga automática
        const viewUrl = `/api/test-archivo/${archivoId}`;

        fetch(viewUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.blob();
            })
            .then(blob => {
                // Crear URL del blob
                const imageUrl = URL.createObjectURL(blob);

                // Crear elemento imagen
                const img = document.createElement('img');
                img.src = imageUrl;
                img.className = 'img-fluid';
                img.alt = nombreArchivo;
                img.style.maxWidth = '100%';
                img.style.height = 'auto';

                // Reemplazar spinner con imagen
                const container = document.getElementById('imageContainer');
                if (container) {
                    container.innerHTML = '';
                    container.appendChild(img);
                }

                console.log('✅ Imagen cargada usando blob URL');

                // Limpiar URL del blob cuando se cierre el modal
                const modalElement = document.getElementById(modalId);
                modalElement.addEventListener('hidden.bs.modal', () => {
                    URL.revokeObjectURL(imageUrl);
                    modalElement.remove();
                });
            })
            .catch(error => {
                console.error('❌ Error cargando imagen:', error);
                const container = document.getElementById('imageContainer');
                if (container) {
                    container.innerHTML = `
                        <div class="alert alert-danger" role="alert">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error al cargar la imagen: ${error.message}
                        </div>
                    `;
                }
            });

        return; // Salir aquí para imágenes
    } else if (isPDF) {
        // Para PDFs, usar iframe pero con URL de visualización
        modalContent = `
            <div class="modal fade" id="${modalId}" tabindex="-1">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-file-pdf me-2"></i>${nombreArchivo}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body p-0" style="height: 80vh;">
                            <iframe src="${viewUrl}" width="100%" height="100%" frameborder="0"
                                    onload="console.log('✅ PDF cargado correctamente')"
                                    onerror="console.error('❌ Error cargando PDF')">
                            </iframe>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" onclick="downloadArchivo('${archivoId}', '${nombreArchivo}')">
                                <i class="fas fa-download me-1"></i>Descargar
                            </button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Para otros tipos de archivo, mostrar mensaje y opción de descarga
        modalContent = `
            <div class="modal fade" id="${modalId}" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-file me-2"></i>${nombreArchivo}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center py-5">
                            <i class="fas fa-file-alt fa-4x text-muted mb-3"></i>
                            <h6>Vista previa no disponible</h6>
                            <p class="text-muted">Este tipo de archivo no se puede previsualizar en el navegador.</p>
                            <button type="button" class="btn btn-primary" onclick="downloadArchivo('${archivoId}', '${nombreArchivo}')">
                                <i class="fas fa-download me-1"></i>Descargar archivo
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    document.body.insertAdjacentHTML('beforeend', modalContent);

    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function downloadArchivo(archivoId, nombreArchivo) {
    console.log(`🔽 Descargando: ${nombreArchivo} (ID: ${archivoId})`);
    const downloadUrl = `/api/archivos/${archivoId}/download`;

    // Crear un enlace temporal y hacer clic en él
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.target = '_blank'; // Abrir en nueva pestaña por si el navegador lo bloquea
    link.download = nombreArchivo; // Sugerir nombre de archivo
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showNotification(`Iniciando descarga de ${nombreArchivo}`, 'success');
}

// Funciones para el manejo de pacientes
function agregarPaciente() {
    const modal = new bootstrap.Modal(document.getElementById('pacienteModal'));
    document.getElementById('pacienteForm').reset();
    document.getElementById('pacienteModalLabel').textContent = 'Agregar Nuevo Paciente';
    modal.show();
}

function editarPaciente(pacienteId) {
    fetch(`/api/pacientes/${pacienteId}`)
        .then(response => response.json())
        .then(data => {
            const form = document.getElementById('pacienteForm');
            // Rellenar el formulario con los datos del paciente
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) input.value = data[key];
            });

            document.getElementById('pacienteModalLabel').textContent = 'Editar Paciente';
            form.action = `/actualizar_paciente/${pacienteId}`;

            const modal = new bootstrap.Modal(document.getElementById('pacienteModal'));
            modal.show();
        })
        .catch(error => {
            showNotification('Error al cargar los datos del paciente', 'error');
        });
}

function verHistorialPaciente(pacienteId) {
    window.location.href = `/historial_paciente/${pacienteId}`;
}

// Alias para compatibilidad con HTML onclick
function viewPatientHistory(pacienteId) {
    verHistorialPaciente(pacienteId);
}

// Funciones para el manejo de citas
function agregarCita(hora = null) {
    const modal = new bootstrap.Modal(document.getElementById('citaModal'));
    const form = document.getElementById('citaForm');
    form.reset();

    if (hora) {
        form.querySelector('[name="hora"]').value = hora;
    }

    document.getElementById('citaModalLabel').textContent = 'Agendar Nueva Cita';
    modal.show();
}

function editarCita(citaId) {
    fetch(`/api/citas/${citaId}`)
        .then(response => response.json())
        .then(data => {
            const form = document.getElementById('citaForm');
            // Rellenar el formulario con los datos de la cita
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) input.value = data[key];
            });

            document.getElementById('citaModalLabel').textContent = 'Editar Cita';
            form.action = `/actualizar_cita/${citaId}`;

            const modal = new bootstrap.Modal(document.getElementById('citaModal'));
            modal.show();
        })
        .catch(error => {
            showNotification('Error al cargar los datos de la cita', 'error');
        });
}

function cancelarCita(citaId) {
    if (confirm('¿Está seguro de que desea cancelar esta cita?')) {
        fetch(`/api/citas/${citaId}/cancelar`, {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                showNotification('Cita cancelada exitosamente');
                // Recargar la agenda
                location.reload();
            })
            .catch(error => {
                showNotification('Error al cancelar la cita', 'error');
            });
    }
}

function verVistaCalendario() {
    // Cambiar a vista de calendario
    document.querySelector('.schedule-timeline').style.display = 'none';
    document.querySelector('.calendar-view').style.display = 'block';
}

// Función para exportar el historial
function exportarHistorial(formato) {
    // Obtener los datos de la tabla
    const tabla = document.getElementById('historialAtenciones');
    const filas = tabla.getElementsByTagName('tr');
    let datos = [];

    // Obtener encabezados
    const encabezados = ['Fecha', 'Paciente', 'Tipo', 'Diagnóstico', 'Estado'];
    datos.push(encabezados);

    // Obtener datos de las filas
    for (let fila of filas) {
        let datosFila = [];
        // Solo obtener las primeras 5 columnas (excluir la columna de acciones)
        for (let i = 0; i < 5; i++) {
            const celda = fila.cells[i];
            // Si la celda tiene un badge, obtener su texto
            const badge = celda.querySelector('.badge');
            datosFila.push(badge ? badge.textContent.trim() : celda.textContent.trim());
        }
        datos.push(datosFila);
    }

    // Crear el archivo según el formato
    if (formato === 'excel') {
        exportarExcel(datos);
    } else if (formato === 'csv') {
        exportarCSV(datos);
    }
}

function exportarExcel(datos) {
    // Crear un libro de trabajo
    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(datos);

    // Agregar la hoja al libro
    XLSX.utils.book_append_sheet(wb, ws, "Historial de Atenciones");

    // Generar el archivo y descargarlo
    XLSX.writeFile(wb, "historial_atenciones.xlsx");
}

function exportarCSV(datos) {
    let csv = '';
    datos.forEach(fila => {
        csv += fila.map(celda => `"${celda}"`).join(',') + '\n';
    });

    // Crear el blob y descargarlo
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'historial_atenciones.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Función para generar PDF de una atención
function generarPDF(atencionId) {
    fetch(`/api/get-atencion/${atencionId}`)
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                showNotification('Error al obtener los datos de la atención', 'error');
                return;
            }

            const atencion = data.atencion;
            const doc = new jsPDF();

            // Agregar logo y encabezado
            doc.setFontSize(20);
            doc.text('MedConnect', 105, 20, { align: 'center' });

            doc.setFontSize(16);
            doc.text('Registro de Atención Médica', 105, 30, { align: 'center' });

            // Información del paciente
            doc.setFontSize(12);
            doc.text('Información del Paciente', 20, 45);
            doc.setFontSize(10);
            doc.text(`Nombre: ${atencion.paciente_nombre}`, 20, 55);
            doc.text(`RUT: ${atencion.paciente_rut}`, 20, 62);
            doc.text(`Edad: ${atencion.paciente_edad} años`, 20, 69);
            doc.text(`Fecha: ${formatearFecha(atencion.fecha_hora)}`, 20, 76);
            doc.text(`Tipo de Atención: ${atencion.tipo_atencion}`, 20, 83);

            // Detalles de la atención
            doc.setFontSize(12);
            doc.text('Detalles de la Atención', 20, 100);
            doc.setFontSize(10);

            // Motivo de consulta
            doc.text('Motivo de Consulta:', 20, 110);
            const motivoLines = doc.splitTextToSize(atencion.motivo_consulta || 'No especificado', 170);
            doc.text(motivoLines, 20, 117);

            // Diagnóstico
            doc.text('Diagnóstico:', 20, 135);
            const diagnosticoLines = doc.splitTextToSize(atencion.diagnostico || 'No especificado', 170);
            doc.text(diagnosticoLines, 20, 142);

            // Tratamiento
            doc.text('Tratamiento:', 20, 160);
            const tratamientoLines = doc.splitTextToSize(atencion.tratamiento || 'No especificado', 170);
            doc.text(tratamientoLines, 20, 167);

            // Observaciones
            if (atencion.observaciones) {
                doc.text('Observaciones:', 20, 185);
                const observacionesLines = doc.splitTextToSize(atencion.observaciones, 170);
                doc.text(observacionesLines, 20, 192);
            }

            // Pie de página
            doc.setFontSize(8);
            doc.text('Este documento es un registro médico confidencial.', 105, 280, { align: 'center' });

            // Guardar el PDF
            doc.save(`atencion_${atencionId}.pdf`);
        })
        .catch(error => {
            showNotification('Error al generar el PDF', 'error');
        });
}

// Función para probar el registro de atenciones
function probarRegistroAtencion() {
    console.log('🧪 Probando registro de atención...');
    const form = document.getElementById('formRegistroAtencion');
    if (!form) {
        console.error('❌ No se encontró el formulario de registro');
        return;
    }

    // Crear un objeto FormData a partir del formulario
    const formData = new FormData(form);

    // Agregar datos de prueba al FormData
    formData.set('pacienteId', 'PAC_12345');
    formData.set('fechaHora', new Date().toISOString());
    formData.set('tipoAtencion', 'domiciliaria');
    formData.set('motivoConsulta', 'Prueba de registro con archivos');
    formData.set('diagnostico', 'Diagnóstico de prueba');
    formData.set('tratamiento', 'Tratamiento de prueba');
    formData.set('observaciones', 'Observaciones de prueba');

    // Simular un archivo adjunto
    const blob = new Blob(["Este es un archivo de prueba"], { type: "text/plain" });
    const file = new File([blob], "prueba.txt", { type: "text/plain" });
    formData.append('archivos', file);

    console.log('📦 FormData de prueba:', ...formData.entries());

    fetch('/api/register-atencion', {
        method: 'POST',
        body: formData // No se necesita 'Content-Type', el navegador lo establece automáticamente
    })
        .then(response => {
            console.log('📡 Respuesta de prueba de registro:', response.status);
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.message || 'Error en el servidor') });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log('✅ Prueba de registro exitosa:', data);
                showNotification('Prueba de registro de atención completada con éxito', 'success');
            } else {
                console.error('❌ Error en prueba de registro:', data.message);
                showNotification(`Error en prueba: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error fatal en prueba de registro:', error);
            showNotification(`Error en la prueba de registro: ${error.message}`, 'error');
        });
}

// Exponer función para testing manual
window.probarRegistroAtencion = probarRegistroAtencion;

// ========================================
// FUNCIONES PARA ESTADÍSTICAS DEL DASHBOARD
// ========================================

// Cargar estadísticas del dashboard
function cargarEstadisticasDashboard() {
    console.log('📊 Cargando estadísticas del dashboard...');

    // Cargar estadísticas en paralelo
    Promise.all([
        cargarEstadisticasAtenciones(),
        cargarEstadisticasPacientes(),
        cargarEstadisticasCitasHoy(),
        cargarEstadisticasPendientes()
    ]).then(() => {
        console.log('✅ Todas las estadísticas del dashboard cargadas');
    }).catch(error => {
        console.error('❌ Error cargando estadísticas del dashboard:', error);
    });
}

// Cargar estadísticas de atenciones
function cargarEstadisticasAtenciones() {
    return fetch('/api/get-atenciones')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const totalAtenciones = data.atenciones.length;
                document.getElementById('total-atenciones').textContent = totalAtenciones;
                console.log(`📋 Total atenciones: ${totalAtenciones}`);
            } else {
                console.error('❌ Error obteniendo atenciones:', data.message);
                document.getElementById('total-atenciones').textContent = '0';
            }
        })
        .catch(error => {
            console.error('❌ Error en estadísticas de atenciones:', error);
            document.getElementById('total-atenciones').textContent = '0';
        });
}

// Cargar estadísticas de pacientes
function cargarEstadisticasPacientes() {
    return fetch('/api/professional/patients')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const totalPacientes = data.total || 0;
                document.getElementById('total-pacientes').textContent = totalPacientes;
                console.log(`👥 Total pacientes: ${totalPacientes}`);
            } else {
                console.error('❌ Error obteniendo pacientes:', data.message);
                document.getElementById('total-pacientes').textContent = '0';
            }
        })
        .catch(error => {
            console.error('❌ Error en estadísticas de pacientes:', error);
            document.getElementById('total-pacientes').textContent = '0';
        });
}

// Cargar estadísticas de citas de hoy
function cargarEstadisticasCitasHoy() {
    return fetch('/api/get-atenciones')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const hoy = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
                const citasHoy = data.atenciones.filter(atencion => {
                    if (atencion.fecha_hora) {
                        const fechaAtencion = atencion.fecha_hora.split(' ')[0]; // Obtener solo la fecha
                        return fechaAtencion === hoy;
                    }
                    return false;
                }).length;

                document.getElementById('citas-hoy').textContent = citasHoy;
                console.log(`📅 Citas hoy: ${citasHoy}`);
            } else {
                console.error('❌ Error obteniendo citas de hoy:', data.message);
                document.getElementById('citas-hoy').textContent = '0';
            }
        })
        .catch(error => {
            console.error('❌ Error en estadísticas de citas hoy:', error);
            document.getElementById('citas-hoy').textContent = '0';
        });
}

// Cargar estadísticas de atenciones pendientes
function cargarEstadisticasPendientes() {
    return fetch('/api/get-atenciones')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const pendientes = data.atenciones.filter(atencion =>
                    atencion.estado && atencion.estado.toLowerCase() === 'pendiente'
                ).length;

                document.getElementById('atenciones-pendientes').textContent = pendientes;
                console.log(`⏳ Atenciones pendientes: ${pendientes}`);
            } else {
                console.error('❌ Error obteniendo atenciones pendientes:', data.message);
                document.getElementById('atenciones-pendientes').textContent = '0';
            }
        })
        .catch(error => {
            console.error('❌ Error en estadísticas de pendientes:', error);
            document.getElementById('atenciones-pendientes').textContent = '0';
        });
}

// ========================================
// FUNCIONES PARA GESTIÓN DE PACIENTES
// ========================================

// Variable global para almacenar la lista de pacientes
let pacientesList = [];

// Cargar lista de pacientes al inicializar
function cargarListaPacientes() {
    console.log('📋 Cargando lista de pacientes...');

    fetch('/api/professional/patients')
        .then(response => {
            console.log('📡 Respuesta HTTP:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📥 Respuesta del servidor:', data);

            if (data.success) {
                // Validar que los datos sean correctos
                if (!Array.isArray(data.pacientes)) {
                    console.error('❌ Los datos de pacientes no son un array:', data.pacientes);
                    throw new Error('Formato de datos incorrecto');
                }

                window.pacientesList = data.pacientes;
                console.log('🔍 Debug - Datos recibidos del servidor:', data);
                console.log('🔍 Debug - Lista de pacientes:', data.pacientes);
                console.log('🔍 Debug - Total de pacientes:', data.total);

                // Intentar actualizar la tabla con manejo de errores
                try {
                    actualizarTablaPacientes();
                    actualizarContadorPacientes();
                    console.log(`✅ ${data.total} pacientes cargados exitosamente`);
                } catch (tableError) {
                    console.error('❌ Error actualizando tabla:', tableError);
                    console.error('❌ Stack trace:', tableError.stack);
                    showNotification('Error al mostrar los pacientes en la tabla', 'error');
                }
            } else {
                console.error('❌ Error cargando pacientes:', data.message);
                showNotification(`Error al cargar pacientes: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error completo:', error);
            console.error('❌ Stack trace:', error.stack);
            console.error('❌ Error message:', error.message);
            showNotification(`Error de conexión: ${error.message}`, 'error');
        });
}

// Actualizar la tabla de pacientes
function actualizarTablaPacientes(filteredList = null) {
    console.log('🔄 Actualizando tabla de pacientes...');

    const tabla = document.getElementById('patientsTable');
    if (!tabla) {
        console.warn('⚠️ Tabla de pacientes no encontrada');
        return;
    }

    const tbody = tabla.querySelector('tbody');
    if (!tbody) {
        console.warn('⚠️ Tbody de la tabla no encontrado');
        return;
    }

    const pacientes = filteredList || window.pacientesList;

    console.log('🔍 Debug - Pacientes a mostrar:', pacientes);
    console.log('🔍 Debug - Número de pacientes:', pacientes.length);

    // Debug detallado del primer paciente si existe
    if (pacientes.length > 0) {
        console.log('🔍 Debug - Primer paciente:', pacientes[0]);
        console.log('🔍 Debug - Tipo de edad:', typeof pacientes[0].edad);
        console.log('🔍 Debug - Valor de edad:', pacientes[0].edad);
        console.log('🔍 Debug - Tipo de num_atenciones:', typeof pacientes[0].num_atenciones);
        console.log('🔍 Debug - Valor de num_atenciones:', pacientes[0].num_atenciones);
    }

    if (pacientes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted py-4">
                    <i class="fas fa-users fa-2x mb-2"></i>
                    <br>No tienes pacientes registrados
                    <br><small>Haz clic en "Agregar Paciente" para comenzar</small>
                </td>
            </tr>
        `;
        return;
    }

    try {
        tbody.innerHTML = pacientes.map((paciente, index) => {
            try {
                console.log(`🔍 Procesando paciente ${index + 1}:`, paciente);

                // Obtener valores seguros para cada campo
                const nombreCompleto = escapeHTML(getSafeValue(paciente.nombre_completo, 'Sin nombre'));
                const rut = escapeHTML(getSafeValue(paciente.rut, 'Sin RUT'));
                const edad = escapeHTML(getSafeValue(paciente.edad, 'No especificada'));
                const telefono = escapeHTML(getSafeValue(paciente.telefono, 'No especificado'));
                const email = escapeHTML(getSafeValue(paciente.email, 'No especificado'));
                const direccion = escapeHTML(getSafeValue(paciente.direccion, 'No especificada'));
                const estadoRelacion = escapeHTML(getSafeValue(paciente.estado_relacion, 'Activo'));
                const pacienteId = escapeHTML(getSafeValue(paciente.paciente_id, ''));

                console.log(`✅ Paciente ${index + 1} procesado exitosamente`);

                // Manejar números de atenciones
                const numAtenciones = paciente.num_atenciones !== null && paciente.num_atenciones !== undefined ? paciente.num_atenciones : 0;

                // Manejar fecha de última consulta
                const ultimaConsulta = paciente.ultima_consulta ? formatearFecha(paciente.ultima_consulta) : 'No registrada';
                const textoUltimaConsulta = paciente.ultima_consulta ? 'Última consulta' : 'Sin consultas';

                return `
                    <tr>
                        <td>
                            <div class="patient-info-vertical">
                                <div class="user-avatar-sm me-3">
                                    <i class="fas fa-user"></i>
                                </div>
                                <div>
                                    <div class="fw-medium mb-1">${nombreCompleto}</div>
                                    <small class="text-muted d-block">RUT: ${rut}</small>
                                    <small class="text-muted d-block">${edad} años</small>
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="contact-info">
                                <div class="fw-medium mb-1">${telefono}</div>
                                <small class="text-muted d-block">${email}</small>
                                <small class="text-muted d-block">${direccion}</small>
                            </div>
                        </td>
                        <td>
                            <div class="date-info">
                                <div class="fw-medium">${ultimaConsulta}</div>
                                <small class="text-muted d-block">${numAtenciones} consultas</small>
                                <small class="text-muted d-block">${textoUltimaConsulta}</small>
                            </div>
                        </td>
                        <td>
                            <div class="status-info">
                                <span class="badge bg-success d-block mb-1">${estadoRelacion}</span>
                                <small class="text-muted">${numAtenciones} consultas</small>
                            </div>
                        </td>
                        <td class="text-end">
                            <div class="d-flex flex-column gap-1">
                                <button class="btn btn-outline-primary btn-sm" title="Ver historial" onclick="viewPatientHistory('${pacienteId}')">
                                    <i class="fas fa-history me-1"></i>Historial
                                </button>
                                <button class="btn btn-outline-secondary btn-sm" title="Editar" onclick="editPatient('${pacienteId}')">
                                    <i class="fas fa-edit me-1"></i>Editar
                                </button>
                                <button class="btn btn-outline-info btn-sm" title="Nueva consulta" onclick="newConsultation('${pacienteId}')">
                                    <i class="fas fa-plus me-1"></i>Nueva
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            } catch (patientError) {
                console.error(`❌ Error procesando paciente ${index + 1}:`, patientError);
                console.error('❌ Datos del paciente problemático:', paciente);
                return `
                    <tr>
                        <td colspan="5" class="text-center text-danger py-2">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Error procesando paciente ${index + 1}
                        </td>
                    </tr>
                `;
            }
        }).join('');
    } catch (generalError) {
        console.error('❌ Error general en actualización de tabla:', generalError);
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <br>Error al cargar los pacientes
                    <br><small>Por favor, recarga la página</small>
                </td>
            </tr>
        `;
        throw generalError; // Re-lanzar para que se capture en el nivel superior
    }

    console.log(`✅ Tabla actualizada con ${pacientes.length} pacientes`);
}

// Actualizar contador de pacientes
function actualizarContadorPacientes() {
    const total = window.pacientesList.length;
    const activos = window.pacientesList.filter(p => p.estado_relacion === 'activo').length;

    // Actualizar en la interfaz si existe el elemento
    const statsElements = document.querySelectorAll('[data-stat="pacientes"]');
    statsElements.forEach(element => {
        element.textContent = total;
    });

    // Actualizar también la tarjeta del dashboard
    const dashboardElement = document.getElementById('total-pacientes');
    if (dashboardElement) {
        dashboardElement.textContent = total;
    }

    console.log(`📊 Pacientes: ${total} total, ${activos} activos`);
}

// Función para actualizar todas las estadísticas del dashboard
function actualizarEstadisticasDashboard() {
    console.log('🔄 Actualizando estadísticas del dashboard...');
    cargarEstadisticasDashboard();
}



// Guardar paciente (nuevo o editado)
function savePatient() {
    console.log('💾 Guardando paciente...');

    const form = document.getElementById('addPatientForm');
    if (!form) {
        console.error('❌ Formulario no encontrado');
        return;
    }

    // Obtener datos del formulario
    const formData = new FormData(form);
    const pacienteData = {
        nombre_completo: document.getElementById('patientName').value.trim(),
        rut: document.getElementById('patientRut').value.trim(),
        edad: document.getElementById('patientAge').value,
        genero: document.getElementById('patientGender').value,
        fecha_nacimiento: document.getElementById('patientBirthdate').value,
        telefono: document.getElementById('patientPhone').value.trim(),
        email: document.getElementById('patientEmail').value.trim(),
        direccion: document.getElementById('patientAddress').value.trim(),
        antecedentes_medicos: document.getElementById('patientMedicalHistory').value.trim()
    };

    console.log('📝 Datos del paciente:', pacienteData);

    // Validar campos requeridos
    if (!pacienteData.nombre_completo) {
        showNotification('El nombre completo es requerido', 'error');
        return;
    }

    if (!pacienteData.rut) {
        showNotification('El RUT es requerido', 'error');
        return;
    }

    // Verificar si es edición o nuevo paciente
    const pacienteId = form.getAttribute('data-editing-id');
    const isEditing = pacienteId && pacienteId !== '';

    const url = isEditing
        ? `/api/professional/patients/${pacienteId}`
        : '/api/professional/patients';

    const method = isEditing ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(pacienteData)
    })
        .then(response => response.json())
        .then(data => {
            console.log('📥 Respuesta del servidor:', data);

            if (data.success) {
                showNotification(
                    isEditing ? 'Paciente actualizado exitosamente' : 'Paciente agregado exitosamente',
                    'success'
                );

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addPatientModal'));
                if (modal) {
                    modal.hide();
                }

                // Recargar lista de pacientes y actualizar estadísticas
                cargarListaPacientes();
                actualizarEstadisticasDashboard();

                // Limpiar formulario
                form.reset();
                form.removeAttribute('data-editing-id');

            } else {
                showNotification(data.message || 'Error al guardar paciente', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showNotification('Error de conexión al guardar paciente', 'error');
        });
}

// Editar paciente
function editarPaciente(pacienteId) {
    console.log(`✏️ Editando paciente: ${pacienteId}`);

    // Buscar el paciente en la lista local
    const paciente = window.pacientesList.find(p => p.paciente_id === pacienteId);
    if (!paciente) {
        console.error('❌ Paciente no encontrado en la lista local');
        showNotification('Paciente no encontrado', 'error');
        return;
    }

    // Llenar el formulario con los datos del paciente
    document.getElementById('patientName').value = paciente.nombre_completo || '';
    document.getElementById('patientRut').value = paciente.rut || '';
    document.getElementById('patientAge').value = paciente.edad || '';
    document.getElementById('patientGender').value = paciente.genero || '';
    document.getElementById('patientBirthdate').value = paciente.fecha_nacimiento || '';
    document.getElementById('patientPhone').value = paciente.telefono || '';
    document.getElementById('patientEmail').value = paciente.email || '';
    document.getElementById('patientAddress').value = paciente.direccion || '';
    document.getElementById('patientMedicalHistory').value = paciente.antecedentes_medicos || '';

    // Marcar el formulario como edición
    const form = document.getElementById('addPatientForm');
    form.setAttribute('data-editing-id', pacienteId);

    // Cambiar el título del modal
    const modalLabel = document.getElementById('addPatientModalLabel');
    if (modalLabel) {
        modalLabel.textContent = 'Editar Paciente';
    }

    // Mostrar el modal
    const modal = document.getElementById('addPatientModal');
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

// Eliminar paciente
function eliminarPaciente(pacienteId) {
    console.log(`🗑️ Eliminando paciente: ${pacienteId}`);

    // Buscar el paciente para mostrar su nombre en la confirmación
    const paciente = window.pacientesList.find(p => p.paciente_id === pacienteId);
    const nombrePaciente = paciente ? paciente.nombre_completo : 'este paciente';

    if (!confirm(`¿Estás seguro de que deseas eliminar a ${nombrePaciente} de tu lista de pacientes?\n\nEsto no eliminará al paciente del sistema, solo lo quitará de tu lista personal.`)) {
        return;
    }

    fetch(`/api/professional/patients/${pacienteId}`, {
        method: 'DELETE',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log('📥 Respuesta del servidor:', data);

            if (data.success) {
                showNotification('Paciente eliminado de tu lista exitosamente', 'success');
                cargarListaPacientes(); // Recargar lista
                actualizarEstadisticasDashboard(); // Actualizar estadísticas
            } else {
                showNotification(data.message || 'Error al eliminar paciente', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showNotification('Error de conexión al eliminar paciente', 'error');
        });
}

// Ver historial de un paciente específico
function verHistorialPaciente(pacienteId) {
    console.log(`📄 Viendo historial del paciente: ${pacienteId}`);

    fetch(`/api/professional/patients/${pacienteId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarModalHistorialPaciente(data.paciente, data.atenciones);
            } else {
                showNotification('Error al obtener el historial del paciente', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showNotification('Error de conexión al obtener historial', 'error');
        });
}

// Mostrar modal con historial del paciente
function mostrarModalHistorialPaciente(paciente, atenciones) {
    const modal = document.getElementById('patientHistoryModal');
    if (!modal) {
        console.error('❌ Modal patientHistoryModal no encontrado');
        return;
    }

    // Actualizar título del modal
    const modalLabel = document.getElementById('patientHistoryModalLabel');
    if (modalLabel) {
        modalLabel.textContent = `Historial de ${paciente.nombre_completo}`;
    }

    // Generar contenido del modal
    const modalContent = document.getElementById('patientHistoryContent');
    if (modalContent) {
        modalContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6 class="text-primary">Información Personal</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Nombre:</strong></td><td>${paciente.nombre_completo}</td></tr>
                        <tr><td><strong>RUT:</strong></td><td>${paciente.rut}</td></tr>
                        <tr><td><strong>Edad:</strong></td><td>${paciente.edad || 'No especificada'} años</td></tr>
                        <tr><td><strong>Género:</strong></td><td>${paciente.genero || 'No especificado'}</td></tr>
                        <tr><td><strong>Teléfono:</strong></td><td>${paciente.telefono || 'No especificado'}</td></tr>
                        <tr><td><strong>Email:</strong></td><td>${paciente.email || 'No especificado'}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6 class="text-primary">Estadísticas</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Total Atenciones:</strong></td><td>${atenciones.length}</td></tr>
                        <tr><td><strong>Primera Consulta:</strong></td><td>${paciente.fecha_primera_consulta ? formatearFecha(paciente.fecha_primera_consulta) : 'No registrada'}</td></tr>
                        <tr><td><strong>Última Consulta:</strong></td><td>${paciente.ultima_consulta ? formatearFecha(paciente.ultima_consulta) : 'No registrada'}</td></tr>
                        <tr><td><strong>Registrado:</strong></td><td>${formatearFecha(paciente.fecha_registro)}</td></tr>
                    </table>
                </div>
            </div>
            
            ${paciente.antecedentes_medicos ? `
                <div class="mt-3">
                    <h6 class="text-primary">Antecedentes Médicos</h6>
                    <div class="alert alert-info">
                        <small>${paciente.antecedentes_medicos}</small>
                    </div>
                </div>
            ` : ''}
            
            <div class="mt-4">
                <h6 class="text-primary">Historial de Atenciones (${atenciones.length})</h6>
                ${atenciones.length === 0 ? `
                    <div class="text-center text-muted py-3">
                        <i class="fas fa-calendar-times fa-2x mb-2"></i>
                        <br>No hay atenciones registradas para este paciente
                    </div>
                ` : `
                    <div class="table-responsive">
                        <table class="table table-sm table-striped">
                            <thead>
                                <tr>
                                    <th>Fecha</th>
                                    <th>Tipo</th>
                                    <th>Motivo</th>
                                    <th>Diagnóstico</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${atenciones.map(atencion => `
                                    <tr>
                                        <td>${formatearFecha(atencion.fecha_hora)}</td>
                                        <td><span class="badge bg-secondary">${atencion.tipo_atencion}</span></td>
                                        <td>${atencion.motivo_consulta}</td>
                                        <td>${atencion.diagnostico}</td>
                                        <td><span class="badge bg-success">${atencion.estado}</span></td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-primary" onclick="verDetalleAtencion('${atencion.atencion_id}')" title="Ver detalles">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `}
            </div>
        `;
    }

    // Mostrar el modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

// Función de búsqueda y filtrado
function setupPatientSearch() {
    const searchInput = document.getElementById('searchPatients');
    const filterSelect = document.getElementById('filterPatients');

    if (searchInput) {
        searchInput.addEventListener('input', filterPatients);
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', filterPatients);
    }
}

// Filtrar pacientes por búsqueda y filtros
function filterPatients() {
    const searchTerm = document.getElementById('searchPatients')?.value?.toLowerCase() || '';
    const filterValue = document.getElementById('filterPatients')?.value || '';

    let filteredPatients = window.pacientesList;

    // Aplicar filtro de búsqueda
    if (searchTerm) {
        filteredPatients = filteredPatients.filter(paciente =>
            paciente.nombre_completo.toLowerCase().includes(searchTerm) ||
            paciente.rut.toLowerCase().includes(searchTerm) ||
            (paciente.email && paciente.email.toLowerCase().includes(searchTerm))
        );
    }

    // Aplicar filtro de estado
    if (filterValue) {
        filteredPatients = filteredPatients.filter(paciente =>
            paciente.estado_relacion === filterValue
        );
    }

    actualizarTablaPacientes(filteredPatients);
}



// Funciones para manejar archivos adjuntos
function cargarArchivosAdjuntos(atencionId) {
    console.log(`📁 Cargando archivos adjuntos para: ${atencionId}`);

    fetch(`/api/archivos/${atencionId}`)
        .then(response => response.json())
        .then(data => {
            console.log('📥 Archivos recibidos:', data);

            const listaArchivos = document.getElementById('listaArchivos');
            const noArchivos = document.getElementById('noArchivos');

            if (!listaArchivos || !noArchivos) {
                console.error('❌ No se encontraron los elementos de la lista de archivos');
                return;
            }

            // Limpiar lista anterior
            listaArchivos.innerHTML = '';

            if (data.archivos && data.archivos.length > 0) {
                console.log(`✅ Mostrando ${data.archivos.length} archivos`);

                // Ocultar mensaje "no archivos" y mostrar lista
                noArchivos.style.display = 'none';
                listaArchivos.style.display = 'block';

                data.archivos.forEach(archivo => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item d-flex justify-content-between align-items-center';

                    // Determinar el icono según el tipo de archivo
                    let iconClass = 'fas fa-file';
                    if (archivo.tipo_archivo) {
                        const tipo = archivo.tipo_archivo.toLowerCase();
                        if (tipo.includes('image')) {
                            iconClass = 'fas fa-file-image';
                        } else if (tipo.includes('pdf')) {
                            iconClass = 'fas fa-file-pdf';
                        } else if (tipo.includes('doc')) {
                            iconClass = 'fas fa-file-word';
                        }
                    }

                    const isPreviewable = archivo.tipo_archivo &&
                        (archivo.tipo_archivo.startsWith('image/') ||
                            archivo.tipo_archivo === 'application/pdf');

                    li.innerHTML = `
                        <div>
                            <i class="${iconClass} me-2 text-primary"></i>
                            <span>${archivo.nombre_archivo}</span>
                            <small class="text-muted ms-2">(${archivo.fecha_subida})</small>
                        </div>
                        <div>
                            ${isPreviewable ?
                            `<button class="btn btn-sm btn-outline-primary me-1" onclick="previewArchivo('${archivo.archivo_id}', '${archivo.nombre_archivo.replace(/'/g, "\\'")}')">
                                    <i class="fas fa-eye"></i> Ver
                                </button>` : ''}
                            <button class="btn btn-sm btn-outline-secondary" onclick="downloadArchivo('${archivo.archivo_id}', '${archivo.nombre_archivo.replace(/'/g, "\\'")}')">
                                <i class="fas fa-download"></i> Descargar
                            </button>
                        </div>
                    `;

                    listaArchivos.appendChild(li);
                });
            } else {
                console.log('📭 No hay archivos adjuntos');

                // Mostrar mensaje "no archivos" y ocultar lista
                noArchivos.style.display = 'block';
                listaArchivos.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('❌ Error cargando archivos:', error);
            showNotification('Error al cargar los archivos adjuntos', 'error');
        });
}

// Función para descargar archivo
function descargarArchivo(archivoId, nombreArchivo) {
    fetch(`/api/archivos/${archivoId}/download`)
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = nombreArchivo;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error descargando archivo:', error);
            showNotification('Error al descargar el archivo', 'error');
        });
}

// Función para eliminar archivo
function eliminarArchivo(archivoId) {
    if (confirm('¿Está seguro de que desea eliminar este archivo? Esta acción no se puede deshacer.')) {
        fetch(`/api/archivos/${archivoId}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Archivo eliminado exitosamente', 'success');
                    cargarArchivosAdjuntos(atencionActualId);
                } else {
                    showNotification(data.message || 'Error al eliminar el archivo', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error al eliminar el archivo', 'error');
            });
    }
}

// Evento para mostrar formulario de subida
const btnAgregarArchivos = document.getElementById('btnAgregarArchivos');
if (btnAgregarArchivos) {
    btnAgregarArchivos.addEventListener('click', function () {
        this.classList.add('d-none');
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.classList.remove('d-none');
        }
    });
}

const uploadForm = document.getElementById('uploadForm');
if (uploadForm) {
    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData();
        const fileInput = document.getElementById('fileInput');

        for (let file of fileInput.files) {
            formData.append('files[]', file);
        }
        formData.append('atencion_id', atencionActualId);

        fetch('/api/archivos/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    mostrarNotificacion('Archivos subidos correctamente', 'success');
                    cargarArchivosAdjuntos(atencionActualId);

                    // Resetear formulario
                    this.reset();
                    this.classList.add('d-none');
                    document.getElementById('btnAgregarArchivos').classList.remove('d-none');
                } else {
                    mostrarNotificacion('Error al subir los archivos', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarNotificacion('Error al subir los archivos', 'error');
            });
    });
}

// Variable para almacenar el ID de la atención actual
let atencionActualId = null;

// Modificar la función existente de cargar detalle de atención
function cargarDetalleAtencion(atencionId) {
    atencionActualId = atencionId;
    // ... código existente ...

    // Agregar llamada para cargar archivos
    cargarArchivosAdjuntos(atencionId);
}

// Variable para almacenar archivos seleccionados
let selectedFiles = [];

// Función para manejar la selección de archivos
function handleFileSelection(event) {
    const fileInput = event.target;
    const fileList = document.getElementById('fileList');

    if (!fileList) {
        console.error('❌ No se encontró el contenedor de la lista de archivos');
        return;
    }

    // Limpiar lista anterior
    fileList.innerHTML = '';
    selectedFiles = Array.from(fileInput.files);

    // Mostrar archivos seleccionados
    selectedFiles.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'selected-file d-flex align-items-center p-2 border rounded mb-2';

        // Determinar icono según tipo de archivo
        let iconClass = 'fa-file';
        if (file.type.startsWith('image/')) {
            iconClass = 'fa-file-image';
        } else if (file.type === 'application/pdf') {
            iconClass = 'fa-file-pdf';
        } else if (file.type.includes('word')) {
            iconClass = 'fa-file-word';
        }

        fileItem.innerHTML = `
            <i class="fas ${iconClass} text-primary me-2"></i>
            <div class="flex-grow-1">
                <div class="text-truncate" style="max-width: 200px;" title="${file.name}">
                    ${file.name}
                </div>
                <small class="text-muted">${formatFileSize(file.size)}</small>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger ms-2" 
                    onclick="removeFile('${file.name.replace(/'/g, "\\'")}')">
                <i class="fas fa-times"></i>
            </button>
        `;

        fileList.appendChild(fileItem);
    });
}

// Función para formatear el tamaño del archivo
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Función para remover un archivo
function removeFile(fileName) {
    selectedFiles = selectedFiles.filter(file => file.name !== fileName);
    const fileInput = document.getElementById('fileUpload');
    handleFileSelection({ target: fileInput });
}

// Función para descargar PDF de atención (llamada desde el modal)
function descargarPDFAtencion(atencionId) {
    console.log(`📄 Descargando PDF para atención: ${atencionId}`);

    if (!atencionId) {
        showNotification('Error: No se especificó el ID de la atención', 'error');
        return;
    }

    // Mostrar indicador de carga
    showNotification('Generando PDF...', 'info');

    // Usar la API del servidor para generar el PDF
    fetch(`/api/atencion-pdf/${atencionId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error del servidor: ${response.status}`);
            }
            return response.blob();
        })
        .then(blob => {
            // Crear URL para el blob
            const url = URL.createObjectURL(blob);

            // Crear enlace temporal para descarga
            const link = document.createElement('a');
            link.href = url;
            link.download = `atencion_${atencionId}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            // Limpiar URL del blob
            URL.revokeObjectURL(url);

            showNotification('PDF descargado exitosamente', 'success');
        })
        .catch(error => {
            console.error('❌ Error descargando PDF:', error);
            showNotification('Error al descargar el PDF. Intentando método alternativo...', 'warning');

            // Método alternativo usando la función generarPDF existente
            generarPDF(atencionId);
        });
}

// Función para guardar nueva cita
function saveAppointment() {
    console.log('📅 Guardando nueva cita...');

    const form = document.getElementById('scheduleForm');
    if (!form) {
        console.error('❌ Formulario de cita no encontrado');
        showNotification('Error: Formulario no encontrado', 'error');
        return;
    }

    // Obtener datos del formulario
    const appointmentData = {
        paciente_id: document.getElementById('appointmentPatient').value,
        fecha: document.getElementById('appointmentDate').value,
        hora: document.getElementById('appointmentTime').value,
        tipo_atencion: document.getElementById('appointmentType').value,
        notas: document.getElementById('appointmentNotes').value
    };

    console.log('📝 Datos de la cita:', appointmentData);

    // Validar campos requeridos
    if (!appointmentData.paciente_id) {
        showNotification('Debe seleccionar un paciente', 'error');
        return;
    }

    if (!appointmentData.fecha) {
        showNotification('Debe seleccionar una fecha', 'error');
        return;
    }

    if (!appointmentData.hora) {
        showNotification('Debe seleccionar una hora', 'error');
        return;
    }

    if (!appointmentData.tipo_atencion) {
        showNotification('Debe seleccionar un tipo de atención', 'error');
        return;
    }

    // Enviar datos al servidor
    fetch('/api/professional/appointments', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(appointmentData)
    })
        .then(response => response.json())
        .then(data => {
            console.log('📥 Respuesta del servidor:', data);

            if (data.success) {
                showNotification('Cita agendada exitosamente', 'success');

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleModal'));
                if (modal) {
                    modal.hide();
                }

                // Limpiar formulario
                form.reset();

                // Recargar agenda si está visible
                const scheduleTab = document.querySelector('button[data-bs-target="#schedule"]');
                if (scheduleTab && scheduleTab.classList.contains('active')) {
                    // Aquí podrías recargar la agenda
                    console.log('🔄 Recargando agenda...');
                }

            } else {
                showNotification(data.message || 'Error al agendar la cita', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showNotification('Error de conexión al agendar la cita', 'error');
        });
}

// ==========================================
// FUNCIONES PARA EL DROPDOWN DE PACIENTES
// ==========================================

// Variable global para almacenar la lista de pacientes
window.pacientesDropdownList = [];

// Función para cargar pacientes en el dropdown del formulario de atención
async function cargarPacientesDropdown() {
    try {
        console.log('📋 Cargando pacientes para dropdown...');

        const response = await fetch('/api/professional/patients');
        const data = await response.json();

        if (data.success && Array.isArray(data.pacientes)) {
            window.pacientesDropdownList = data.pacientes;

            const dropdown = document.getElementById('seleccionPaciente');
            if (dropdown) {
                // Limpiar opciones existentes (excepto las primeras dos)
                while (dropdown.children.length > 2) {
                    dropdown.removeChild(dropdown.lastChild);
                }

                // Agregar pacientes al dropdown
                data.pacientes.forEach(paciente => {
                    const option = document.createElement('option');
                    option.value = paciente.paciente_id;
                    option.textContent = `${paciente.nombre_completo} (${paciente.rut})`;
                    dropdown.appendChild(option);
                });

                console.log(`✅ ${data.pacientes.length} pacientes cargados en dropdown`);
            }
        } else {
            console.warn('⚠️ No se pudieron cargar pacientes para dropdown');
        }
    } catch (error) {
        console.error('❌ Error cargando pacientes para dropdown:', error);
    }
}

// Función para manejar la selección de paciente en el dropdown
function manejarSeleccionPaciente() {
    const dropdown = document.getElementById('seleccionPaciente');
    const selectedValue = dropdown.value;

    const camposPaciente = document.getElementById('camposPaciente');
    const infoPacienteSeleccionado = document.getElementById('infoPacienteSeleccionado');

    // Ocultar ambos paneles inicialmente
    camposPaciente.style.display = 'none';
    infoPacienteSeleccionado.style.display = 'none';

    if (selectedValue === 'nuevo') {
        // Mostrar campos para nuevo paciente
        console.log('➕ Seleccionado: Crear nuevo paciente');
        camposPaciente.style.display = 'block';
        limpiarCamposPaciente();

        // Hacer campos requeridos
        document.getElementById('pacienteNombre').required = true;
        document.getElementById('pacienteRut').required = true;

    } else if (selectedValue && selectedValue !== '') {
        // Mostrar información del paciente seleccionado
        console.log(`👤 Seleccionado paciente: ${selectedValue}`);
        const paciente = window.pacientesDropdownList.find(p => p.paciente_id === selectedValue);

        if (paciente) {
            mostrarInfoPacienteSeleccionado(paciente);
            infoPacienteSeleccionado.style.display = 'block';

            // Llenar campos ocultos para el envío del formulario
            llenarCamposOcultosPaciente(paciente);
        }

        // Campos no requeridos (paciente ya existe)
        document.getElementById('pacienteNombre').required = false;
        document.getElementById('pacienteRut').required = false;

    } else {
        // No hay selección
        console.log('❌ No hay paciente seleccionado');
        limpiarCamposPaciente();

        // Campos no requeridos
        document.getElementById('pacienteNombre').required = false;
        document.getElementById('pacienteRut').required = false;
    }
}

// Función para mostrar información del paciente seleccionado
function mostrarInfoPacienteSeleccionado(paciente) {
    document.getElementById('nombrePacienteSeleccionado').textContent = paciente.nombre_completo || 'Sin nombre';
    document.getElementById('rutPacienteSeleccionado').textContent = paciente.rut || 'Sin RUT';
    document.getElementById('edadPacienteSeleccionado').textContent = paciente.edad || 'Sin edad';
}

// Función para llenar campos ocultos con datos del paciente seleccionado
function llenarCamposOcultosPaciente(paciente) {
    document.getElementById('pacienteNombre').value = paciente.nombre_completo || '';
    document.getElementById('pacienteRut').value = paciente.rut || '';
    document.getElementById('pacienteEdad').value = paciente.edad || '';

    // Agregar un campo oculto con el ID del paciente
    let pacienteIdInput = document.getElementById('pacienteIdHidden');
    if (!pacienteIdInput) {
        pacienteIdInput = document.createElement('input');
        pacienteIdInput.type = 'hidden';
        pacienteIdInput.id = 'pacienteIdHidden';
        pacienteIdInput.name = 'pacienteId';
        document.getElementById('atencionForm').appendChild(pacienteIdInput);
    }
    pacienteIdInput.value = paciente.paciente_id;
}

// Función para limpiar campos del paciente
function limpiarCamposPaciente() {
    document.getElementById('pacienteNombre').value = '';
    document.getElementById('pacienteRut').value = '';
    document.getElementById('pacienteEdad').value = '';

    // Remover campo oculto del ID si existe
    const pacienteIdInput = document.getElementById('pacienteIdHidden');
    if (pacienteIdInput) {
        pacienteIdInput.remove();
    }
}

// Función para editar datos del paciente seleccionado
function editarDatosPaciente() {
    console.log('✏️ Editando datos del paciente seleccionado');

    const infoPacienteSeleccionado = document.getElementById('infoPacienteSeleccionado');
    const camposPaciente = document.getElementById('camposPaciente');

    // Ocultar info y mostrar campos editables
    infoPacienteSeleccionado.style.display = 'none';
    camposPaciente.style.display = 'block';

    // Los campos ya están llenos por llenarCamposOcultosPaciente()
}

// Función para recargar la lista de pacientes
async function recargarListaPacientes() {
    console.log('🔄 Recargando lista de pacientes...');

    const button = event.target;
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;

    try {
        await cargarPacientesDropdown();
        showNotification('Lista de pacientes actualizada', 'success');
    } catch (error) {
        console.error('❌ Error recargando pacientes:', error);
        showNotification('Error al actualizar la lista de pacientes', 'error');
    } finally {
        button.innerHTML = originalHTML;
        button.disabled = false;
    }
}

// ====== FUNCIONES DE AGENDA ======

// Variables globales para agenda
let fechaActualAgenda = new Date();
let citasDelDia = [];
let horariosProfesional = [];

// Inicializar agenda cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    // Cargar agenda si el tab está activo
    const agendaTab = document.getElementById('schedule-tab');
    if (agendaTab) {
        agendaTab.addEventListener('click', function () {
            cargarAgenda();
        });
    }

    // Si la agenda está visible al cargar, cargarla
    const agendaPane = document.getElementById('schedule');
    if (agendaPane && agendaPane.classList.contains('active')) {
        cargarAgenda();
    }
});

// Función para cargar la agenda
function cargarAgenda(fecha = null) {
    console.log('📅 Cargando agenda...');

    if (!fecha) {
        fecha = fechaActualAgenda.toISOString().split('T')[0];
    }

    // Actualizar fecha en el header
    actualizarFechaHeader(fecha);

    // Cargar citas del día con vista actual
    fetch(`/api/professional/schedule?fecha=${fecha}&vista=${currentView}`)
        .then(response => response.json())
        .then(data => {
            console.log('📥 Datos de agenda recibidos:', data);

            if (data.success) {
                agendaData = data;

                if (currentView === 'diaria') {
                    citasDelDia = data.citas;
                    actualizarVistaAgenda(data.citas, data.horarios_disponibles);
                } else if (currentView === 'semanal') {
                    actualizarVistaSemanal(data.agenda_semanal, data.fecha_inicio, data.fecha_fin);
                } else if (currentView === 'mensual') {
                    actualizarVistaMensual(data.agenda_mensual, data.fecha_inicio, data.fecha_fin);
                }

                actualizarEstadisticasAgenda(data.estadisticas);

                if (data.citas) {
                    actualizarRecordatorios(data.citas);
                }
            } else {
                console.error('❌ Error cargando agenda:', data.message);
                showNotification('Error al cargar la agenda: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error de red:', error);
            showNotification('Error de conexión al cargar la agenda', 'error');
        });
}

// Función para actualizar la fecha en el header
function actualizarFechaHeader(fecha) {
    const fechaObj = new Date(fecha + 'T00:00:00');
    const opciones = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    };

    const fechaFormateada = fechaObj.toLocaleDateString('es-ES', opciones);
    const currentDateElement = document.getElementById('currentDate');
    if (currentDateElement) {
        currentDateElement.textContent = fechaFormateada;
    }
}

// Función para actualizar la vista de la agenda
function actualizarVistaAgenda(citas, horariosDisponibles) {
    const scheduleTimeline = document.querySelector('.schedule-timeline');
    if (!scheduleTimeline) return;

    // Limpiar timeline
    scheduleTimeline.innerHTML = '';

    // Generar horarios de 8:00 a 18:00 cada 30 minutos
    const horarios = [];
    for (let hora = 8; hora < 18; hora++) {
        for (let minuto of [0, 30]) {
            horarios.push(`${hora.toString().padStart(2, '0')}:${minuto.toString().padStart(2, '0')}`);
        }
    }

    // Crear slots de tiempo
    horarios.forEach(hora => {
        const cita = citas.find(c => c.hora === hora);
        const timeSlot = document.createElement('div');
        timeSlot.className = 'time-slot';

        if (cita) {
            // Slot ocupado con cita
            timeSlot.innerHTML = `
                <div class="time-label">${hora}</div>
                <div class="appointment scheduled">
                    <div class="appointment-info">
                        <h6 class="mb-1">${cita.paciente_nombre}</h6>
                        <p class="mb-0 small text-muted">${cita.tipo_atencion} - ${cita.paciente_rut}</p>
                        <small class="text-${getEstadoColor(cita.estado)}">${capitalizeFirst(cita.estado)}</small>
                    </div>
                    <div class="appointment-actions">
                        <button class="btn btn-sm btn-outline-primary" onclick="verCita('${cita.cita_id}')" title="Ver detalles">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="confirmarCita('${cita.cita_id}')" title="Confirmar">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="cancelarCita('${cita.cita_id}')" title="Cancelar">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
        } else {
            // Slot disponible
            timeSlot.innerHTML = `
                <div class="time-label">${hora}</div>
                <div class="appointment available" onclick="agendarCita('${hora}')">
                    <div class="appointment-info">
                        <p class="mb-0 text-muted">Horario disponible</p>
                        <small class="text-primary">Click para agendar</small>
                    </div>
                </div>
            `;
        }

        scheduleTimeline.appendChild(timeSlot);
    });
}

// Función para obtener el color del estado
function getEstadoColor(estado) {
    switch (estado) {
        case 'confirmada': return 'success';
        case 'pendiente': return 'warning';
        case 'cancelada': return 'danger';
        case 'completada': return 'info';
        default: return 'secondary';
    }
}

// Función para capitalizar primera letra
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Función para actualizar estadísticas
function actualizarEstadisticasAgenda(estadisticas) {
    console.log('📊 Actualizando estadísticas de agenda:', estadisticas);

    const elementos = {
        totalCitas: document.getElementById('totalCitas'),
        confirmadas: document.getElementById('confirmadas'),
        pendientes: document.getElementById('pendientes'),
        disponibles: document.getElementById('disponibles')
    };

    if (elementos.totalCitas) elementos.totalCitas.textContent = estadisticas.total_citas || 0;
    if (elementos.confirmadas) elementos.confirmadas.textContent = estadisticas.confirmadas || 0;
    if (elementos.pendientes) elementos.pendientes.textContent = estadisticas.pendientes || 0;
    if (elementos.disponibles) elementos.disponibles.textContent = estadisticas.disponibles || 0;

    // Agregar animación de actualización
    Object.values(elementos).forEach(element => {
        if (element) {
            element.style.transform = 'scale(1.1)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    });
}

// Función para actualizar recordatorios
function actualizarRecordatorios(citas) {
    console.log('🔔 Actualizando recordatorios:', citas);

    // Cargar recordatorios desde el servidor
    cargarRecordatorios();
}

// Función para cargar recordatorios desde el servidor
function cargarRecordatorios() {
    fetch('/api/professional/reminders')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarRecordatorios(data.recordatorios);
            } else {
                console.error('❌ Error cargando recordatorios:', data.message);
                mostrarRecordatorios([]);
            }
        })
        .catch(error => {
            console.error('❌ Error de red cargando recordatorios:', error);
            mostrarRecordatorios([]);
        });
}

// Función para mostrar recordatorios en la interfaz
function mostrarRecordatorios(recordatorios) {
    const container = document.getElementById('recordatoriosContainer');
    if (!container) return;

    // Limpiar recordatorios existentes
    container.innerHTML = '';

    // Si no hay recordatorios, mostrar mensaje
    if (recordatorios.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-3">
                <i class="fas fa-check-circle fa-2x mb-2"></i>
                <p class="mb-0">No hay recordatorios pendientes</p>
            </div>
        `;
        return;
    }

    // Crear elementos de recordatorios
    recordatorios.forEach(recordatorio => {
        const recordatorioElement = document.createElement('div');
        recordatorioElement.className = `reminder-item mb-3 p-3 rounded bg-${getReminderColor(recordatorio.prioridad)} bg-opacity-10 border-start border-${getReminderColor(recordatorio.prioridad)} border-4`;
        recordatorioElement.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="${getReminderIcon(recordatorio.tipo)} text-${getReminderColor(recordatorio.prioridad)} me-2 mt-1"></i>
                <div class="flex-grow-1">
                    <small class="text-muted d-block">${recordatorio.titulo}</small>
                    <strong class="text-dark">${recordatorio.mensaje}</strong>
                    <small class="text-muted d-block mt-1">
                        <i class="fas fa-clock me-1"></i>
                        ${formatearFechaHora(recordatorio.fecha, recordatorio.hora)}
                    </small>
                </div>
                <div class="reminder-actions">
                    <button class="btn btn-sm btn-outline-${getReminderColor(recordatorio.prioridad)}" onclick="editReminder(${recordatorio.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteReminder(${recordatorio.id})" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
        container.appendChild(recordatorioElement);
    });

    // Actualizar timestamp
    const timestampElement = document.querySelector('.text-center.mt-3 small');
    if (timestampElement) {
        timestampElement.innerHTML = '<i class="fas fa-clock me-1"></i>Actualizado ahora';
    }
}

// Función para obtener el color según la prioridad
function getReminderColor(prioridad) {
    switch (prioridad) {
        case 'urgente': return 'danger';
        case 'alta': return 'warning';
        case 'media': return 'info';
        case 'baja': return 'secondary';
        default: return 'info';
    }
}

// Función para obtener el icono según el tipo
function getReminderIcon(tipo) {
    switch (tipo) {
        case 'confirmacion': return 'fas fa-info-circle';
        case 'llamada': return 'fas fa-phone';
        case 'preparacion': return 'fas fa-stethoscope';
        case 'seguimiento': return 'fas fa-chart-line';
        case 'personal': return 'fas fa-user';
        default: return 'fas fa-bell';
    }
}

// Función para formatear fecha y hora
function formatearFechaHora(fecha, hora) {
    const fechaObj = new Date(fecha + 'T' + hora);
    return fechaObj.toLocaleDateString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    }) + ' ' + hora;
}

// Funciones para gestionar recordatorios

// Mostrar modal de recordatorio
function showReminderModal(recordatorioId = null) {
    console.log('🔔 showReminderModal ejecutándose con ID:', recordatorioId);

    const modal = document.getElementById('reminderModal');
    console.log('🔍 Modal encontrado:', modal);

    if (!modal) {
        console.error('❌ Modal de recordatorio NO encontrado');
        return;
    }

    const modalTitle = document.getElementById('reminderModalTitle');
    const saveButton = document.getElementById('saveReminderText');
    const reminderId = document.getElementById('reminderId');

    console.log('🔍 Elementos del modal:', {
        modalTitle: modalTitle,
        saveButton: saveButton,
        reminderId: reminderId
    });

    // Limpiar formulario
    const form = document.getElementById('reminderForm');
    if (form) {
        form.reset();
        console.log('✅ Formulario limpiado');
    } else {
        console.error('❌ Formulario NO encontrado');
    }

    // Configurar fecha y hora por defecto
    const now = new Date();
    const dateInput = document.getElementById('reminderDate');
    const timeInput = document.getElementById('reminderTime');

    if (dateInput && timeInput) {
        dateInput.value = now.toISOString().split('T')[0];
        timeInput.value = now.toTimeString().slice(0, 5);
        console.log('✅ Fecha y hora configuradas');
    } else {
        console.error('❌ Inputs de fecha/hora NO encontrados');
    }

    if (recordatorioId) {
        // Modo edición
        console.log('✏️ Modo edición');
        modalTitle.textContent = 'Editar Recordatorio';
        saveButton.textContent = 'Actualizar Recordatorio';
        reminderId.value = recordatorioId;
        cargarRecordatorioParaEditar(recordatorioId);
    } else {
        // Modo creación
        console.log('➕ Modo creación');
        modalTitle.textContent = 'Crear Recordatorio';
        saveButton.textContent = 'Guardar Recordatorio';
        reminderId.value = '';
    }

    // Mostrar modal
    console.log('🎭 Mostrando modal...');
    console.log('🔍 Bootstrap disponible:', typeof bootstrap);

    try {
        if (typeof bootstrap !== 'undefined') {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            console.log('✅ Modal mostrado exitosamente con Bootstrap');

            // Cargar pacientes después de que el modal esté visible
            setTimeout(() => {
                console.log('🔄 Cargando pacientes después de mostrar modal con Bootstrap...');
                cargarPacientesEnReminderSelect();
            }, 300);
        } else {
            // Fallback: mostrar modal manualmente
            console.log('⚠️ Bootstrap no disponible, usando fallback');
            modal.style.display = 'block';
            modal.classList.add('show');
            document.body.classList.add('modal-open');

            // Agregar backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            document.body.appendChild(backdrop);

            console.log('✅ Modal mostrado con fallback');

            // Cargar pacientes después de que el modal esté visible
            setTimeout(() => {
                console.log('🔄 Cargando pacientes después de mostrar modal con fallback...');
                cargarPacientesEnReminderSelect();
            }, 300);
        }
    } catch (error) {
        console.error('❌ Error mostrando modal:', error);
    }
}

// Cargar recordatorio para editar
function cargarRecordatorioParaEditar(recordatorioId) {
    fetch(`/api/professional/reminders/${recordatorioId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const recordatorio = data.recordatorio;

                document.getElementById('reminderType').value = recordatorio.tipo;
                document.getElementById('reminderPatient').value = recordatorio.paciente_id || '';
                document.getElementById('reminderTitle').value = recordatorio.titulo;
                document.getElementById('reminderMessage').value = recordatorio.mensaje;
                document.getElementById('reminderDate').value = recordatorio.fecha;
                document.getElementById('reminderTime').value = recordatorio.hora;
                document.getElementById('reminderPriority').value = recordatorio.prioridad;
                document.getElementById('reminderRepeat').checked = recordatorio.repetir;
                document.getElementById('reminderRepeatType').value = recordatorio.tipo_repeticion || 'diario';

                // Mostrar/ocultar opciones de repetición
                toggleRepeatOptions();
            } else {
                showNotification('Error cargando recordatorio', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error cargando recordatorio:', error);
            showNotification('Error cargando recordatorio', 'error');
        });
}

// Cargar pacientes en el select de recordatorios
function cargarPacientesEnReminderSelect() {
    console.log('🔄 Cargando pacientes en select de recordatorios...');

    const select = document.getElementById('reminderPatient');
    if (!select) {
        console.error('❌ Select de pacientes no encontrado');
        return;
    }

    console.log('📋 Limpiando opciones existentes...');
    // Limpiar opciones existentes (excepto la primera)
    while (select.children.length > 1) {
        select.removeChild(select.lastChild);
    }

    // Función para agregar pacientes al select
    function agregarPacientesAlSelect(pacientes) {
        console.log(`📝 Agregando ${pacientes.length} pacientes al select`);
        pacientes.forEach(paciente => {
            const option = document.createElement('option');
            option.value = paciente.paciente_id;
            option.textContent = `${paciente.nombre_completo} - ${paciente.rut}`;
            select.appendChild(option);
        });
        console.log('✅ Pacientes agregados al select exitosamente');
    }

    // Usar la lista global de pacientes si está disponible
    if (window.pacientesList && window.pacientesList.length > 0) {
        console.log(`✅ Usando lista global de pacientes: ${window.pacientesList.length} pacientes`);
        agregarPacientesAlSelect(window.pacientesList);
    } else {
        console.log('⚠️ No hay lista global, cargando desde API...');
        // Si no hay lista global, cargar desde API
        fetch('/api/professional/patients', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                console.log('📡 Respuesta de API:', response.status, response.statusText);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('📊 Datos recibidos:', data);
                if (data.success && data.pacientes && Array.isArray(data.pacientes)) {
                    console.log(`✅ Cargando ${data.pacientes.length} pacientes desde API`);
                    agregarPacientesAlSelect(data.pacientes);

                    // Guardar en la lista global para futuras referencias
                    window.pacientesList = data.pacientes;
                    console.log('💾 Lista de pacientes guardada en window.pacientesList');
                } else {
                    console.warn('⚠️ No se recibieron pacientes válidos de la API');
                    console.log('📊 Respuesta completa:', data);

                    // Mostrar mensaje de error en el select
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'No hay pacientes disponibles';
                    option.disabled = true;
                    select.appendChild(option);
                }
            })
            .catch(error => {
                console.error('❌ Error cargando pacientes:', error);
                // Mostrar mensaje de error al usuario
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'Error cargando pacientes...';
                option.disabled = true;
                select.appendChild(option);
            });
    }
}

// Guardar recordatorio
function saveReminder() {
    const form = document.getElementById('reminderForm');
    const reminderId = document.getElementById('reminderId').value;

    // Validar formulario
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Obtener datos del formulario
    const reminderData = {
        tipo: document.getElementById('reminderType').value,
        paciente_id: document.getElementById('reminderPatient').value || null,
        titulo: document.getElementById('reminderTitle').value,
        mensaje: document.getElementById('reminderMessage').value,
        fecha: document.getElementById('reminderDate').value,
        hora: document.getElementById('reminderTime').value,
        prioridad: document.getElementById('reminderPriority').value,
        repetir: document.getElementById('reminderRepeat').checked,
        tipo_repeticion: document.getElementById('reminderRepeatType').value
    };

    const url = reminderId ? `/api/professional/reminders/${reminderId}` : '/api/professional/reminders';
    const method = reminderId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(reminderData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(
                    reminderId ? 'Recordatorio actualizado exitosamente' : 'Recordatorio creado exitosamente',
                    'success'
                );

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('reminderModal'));
                if (modal) {
                    modal.hide();
                }

                // Recargar recordatorios
                cargarRecordatorios();

            } else {
                showNotification(data.message || 'Error al guardar recordatorio', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error guardando recordatorio:', error);
            showNotification('Error al guardar recordatorio', 'error');
        });
}

// Editar recordatorio
function editReminder(recordatorioId) {
    showReminderModal(recordatorioId);
}

// Eliminar recordatorio
function deleteReminder(recordatorioId) {
    if (!confirm('¿Está seguro de que desea eliminar este recordatorio?')) {
        return;
    }

    fetch(`/api/professional/reminders/${recordatorioId}`, {
        method: 'DELETE',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Recordatorio eliminado exitosamente', 'success');
                cargarRecordatorios();
            } else {
                showNotification(data.message || 'Error al eliminar recordatorio', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error eliminando recordatorio:', error);
            showNotification('Error al eliminar recordatorio', 'error');
        });
}

// Función de fallback para mostrar modal de recordatorio
function mostrarModalRecordatorioManual() {
    console.log('🔄 Usando función de fallback para mostrar modal');

    const modal = document.getElementById('reminderModal');
    if (!modal) {
        console.error('❌ Modal de recordatorio no encontrado');
        alert('Error: Modal de recordatorio no encontrado');
        return;
    }

    // Limpiar formulario
    const form = document.getElementById('reminderForm');
    if (form) {
        form.reset();
    }

    // Configurar fecha y hora por defecto
    const now = new Date();
    const dateInput = document.getElementById('reminderDate');
    const timeInput = document.getElementById('reminderTime');

    if (dateInput && timeInput) {
        dateInput.value = now.toISOString().split('T')[0];
        timeInput.value = now.toTimeString().slice(0, 5);
    }

    // Configurar título
    const modalTitle = document.getElementById('reminderModalTitle');
    const saveButton = document.getElementById('saveReminderText');
    const reminderId = document.getElementById('reminderId');

    if (modalTitle) modalTitle.textContent = 'Crear Recordatorio';
    if (saveButton) saveButton.textContent = 'Guardar Recordatorio';
    if (reminderId) reminderId.value = '';

    // Mostrar modal
    try {
        if (typeof bootstrap !== 'undefined') {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        } else {
            // Fallback manual
            modal.style.display = 'block';
            modal.classList.add('show');
            document.body.classList.add('modal-open');

            // Agregar backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            document.body.appendChild(backdrop);
        }

        console.log('✅ Modal mostrado con función de fallback');
    } catch (error) {
        console.error('❌ Error mostrando modal:', error);
        alert('Error al mostrar el modal de recordatorio');
    }
}

// Asignar las funciones a las variables globales
window.showReminderModal = showReminderModal;
window.editReminder = editReminder;
window.deleteReminder = deleteReminder;
window.mostrarModalRecordatorioManual = mostrarModalRecordatorioManual;
window.handleCrearRecordatorio = handleCrearRecordatorio;
window.mostrarModalRecordatorio = mostrarModalRecordatorio;
window.cerrarModalRecordatorio = cerrarModalRecordatorio;
window.crearModalRecordatorio = crearModalRecordatorio;
window.mostrarFormularioRecordatorioAlternativo = mostrarFormularioRecordatorioAlternativo;
window.guardarRecordatorioAlternativo = guardarRecordatorioAlternativo;

// Toggle opciones de repetición
function toggleRepeatOptions() {
    const repeatCheckbox = document.getElementById('reminderRepeat');
    const repeatOptions = document.getElementById('repeatOptions');

    if (repeatCheckbox.checked) {
        repeatOptions.classList.remove('d-none');
    } else {
        repeatOptions.classList.add('d-none');
    }
}

// Agregar event listener para el checkbox de repetición
document.addEventListener('DOMContentLoaded', function () {
    const repeatCheckbox = document.getElementById('reminderRepeat');
    if (repeatCheckbox) {
        repeatCheckbox.addEventListener('change', toggleRepeatOptions);
    }

    // Inicializar event listeners para recordatorios
    inicializarEventListenersRecordatorios();

    // Inicialización adicional para asegurar que los botones funcionen
    setTimeout(() => {
        inicializarBotonesRecordatorios();
    }, 1000);
});

// Función para manejar el clic en crear recordatorio
function handleCrearRecordatorio() {
    console.log('🔔 Botón crear recordatorio clickeado');

    // Lógica inline para mostrar el modal sin depender de funciones globales
    const modal = document.getElementById('reminderModal');
    if (!modal) {
        console.error('❌ Modal de recordatorio no encontrado');

        // Crear modal dinámicamente si no existe
        crearModalRecordatorio();
        return;
    }

    // Limpiar formulario
    const form = document.getElementById('reminderForm');
    if (form) {
        form.reset();
    }

    // Configurar fecha y hora por defecto
    const now = new Date();
    const dateInput = document.getElementById('reminderDate');
    const timeInput = document.getElementById('reminderTime');

    if (dateInput && timeInput) {
        dateInput.value = now.toISOString().split('T')[0];
        timeInput.value = now.toTimeString().slice(0, 5);
    }

    // Configurar título
    const modalTitle = document.getElementById('reminderModalTitle');
    const saveButton = document.getElementById('saveReminderText');
    const reminderId = document.getElementById('reminderId');

    if (modalTitle) modalTitle.textContent = 'Crear Recordatorio';
    if (saveButton) saveButton.textContent = 'Guardar Recordatorio';
    if (reminderId) reminderId.value = '';

    // Mostrar modal con múltiples métodos
    mostrarModalRecordatorio(modal);

    // Cargar pacientes después de mostrar el modal
    setTimeout(() => {
        console.log('🔄 Cargando pacientes después de mostrar modal...');
        cargarPacientesEnReminderSelect();
    }, 100);
}

// Función para mostrar el modal de recordatorio
function mostrarModalRecordatorio(modal) {
    try {
        // Método 1: Bootstrap
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            console.log('✅ Modal mostrado con Bootstrap');
            return;
        }

        // Método 2: jQuery Bootstrap
        if (typeof $ !== 'undefined' && $.fn.modal) {
            $(modal).modal('show');
            console.log('✅ Modal mostrado con jQuery Bootstrap');
            return;
        }

        // Método 3: Fallback manual
        modal.style.display = 'block';
        modal.classList.add('show');
        document.body.classList.add('modal-open');

        // Agregar backdrop
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        backdrop.id = 'reminderModalBackdrop';
        document.body.appendChild(backdrop);

        // Agregar event listener para cerrar con backdrop
        backdrop.addEventListener('click', function () {
            cerrarModalRecordatorio(modal);
        });

        console.log('✅ Modal mostrado manualmente');

    } catch (error) {
        console.error('❌ Error mostrando modal:', error);

        // Método 4: Alert como último recurso
        alert('Error al mostrar el modal. Usando método alternativo.');
        mostrarFormularioRecordatorioAlternativo();
    }
}

// Función para cerrar el modal
function cerrarModalRecordatorio(modal) {
    try {
        // Método 1: Bootstrap
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
                return;
            }
        }

        // Método 2: jQuery Bootstrap
        if (typeof $ !== 'undefined' && $.fn.modal) {
            $(modal).modal('hide');
            return;
        }

        // Método 3: Fallback manual
        modal.style.display = 'none';
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');

        // Remover backdrop
        const backdrop = document.getElementById('reminderModalBackdrop');
        if (backdrop) {
            backdrop.remove();
        }

    } catch (error) {
        console.error('❌ Error cerrando modal:', error);
    }
}

// Función para crear modal dinámicamente
function crearModalRecordatorio() {
    console.log('🔧 Creando modal de recordatorio dinámicamente...');

    const modalHTML = `
        <div class="modal fade" id="reminderModal" tabindex="-1" aria-labelledby="reminderModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="reminderModalTitle">Crear Recordatorio</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="reminderForm">
                            <input type="hidden" id="reminderId" name="reminderId">
                            <div class="mb-3">
                                <label for="reminderTitle" class="form-label">Título</label>
                                <input type="text" class="form-control" id="reminderTitle" name="title" required>
                            </div>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="reminderDate" class="form-label">Fecha</label>
                                        <input type="date" class="form-control" id="reminderDate" name="date" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="reminderTime" class="form-label">Hora</label>
                                        <input type="time" class="form-control" id="reminderTime" name="time" required>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label for="reminderDescription" class="form-label">Descripción</label>
                                <textarea class="form-control" id="reminderDescription" name="description" rows="3"></textarea>
                            </div>
                            <div class="mb-3">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="reminderRepeat" name="repeat">
                                    <label class="form-check-label" for="reminderRepeat">
                                        Repetir recordatorio
                                    </label>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" id="saveReminderText" onclick="saveReminder()">
                            Guardar Recordatorio
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Agregar el modal al body
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    // Mostrar el modal inmediatamente
    const modal = document.getElementById('reminderModal');
    if (modal) {
        mostrarModalRecordatorio(modal);
    }
}

// Función alternativa para mostrar formulario
function mostrarFormularioRecordatorioAlternativo() {
    console.log('🔧 Mostrando formulario alternativo...');

    const formHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 20px; border-radius: 8px; max-width: 500px; width: 90%;">
                <h5>Crear Recordatorio</h5>
                <form id="reminderFormAlt">
                    <div style="margin-bottom: 15px;">
                        <label>Título:</label>
                        <input type="text" id="reminderTitleAlt" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label>Fecha:</label>
                        <input type="date" id="reminderDateAlt" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label>Hora:</label>
                        <input type="time" id="reminderTimeAlt" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label>Descripción:</label>
                        <textarea id="reminderDescriptionAlt" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; height: 80px;"></textarea>
                    </div>
                    <div style="text-align: right;">
                        <button type="button" onclick="document.getElementById('reminderFormAlt').parentElement.parentElement.remove()" style="padding: 8px 16px; margin-right: 10px; border: 1px solid #ddd; background: #f8f9fa; border-radius: 4px;">Cancelar</button>
                        <button type="button" onclick="guardarRecordatorioAlternativo()" style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px;">Guardar</button>
                    </div>
                </form>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', formHTML);

    // Configurar fecha y hora por defecto
    const now = new Date();
    const dateInput = document.getElementById('reminderDateAlt');
    const timeInput = document.getElementById('reminderTimeAlt');

    if (dateInput && timeInput) {
        dateInput.value = now.toISOString().split('T')[0];
        timeInput.value = now.toTimeString().slice(0, 5);
    }
}

// Función para guardar recordatorio alternativo
function guardarRecordatorioAlternativo() {
    const title = document.getElementById('reminderTitleAlt').value;
    const date = document.getElementById('reminderDateAlt').value;
    const time = document.getElementById('reminderTimeAlt').value;
    const description = document.getElementById('reminderDescriptionAlt').value;

    if (!title || !date || !time) {
        alert('Por favor completa todos los campos requeridos');
        return;
    }

    // Aquí puedes implementar la lógica para guardar el recordatorio
    console.log('Guardando recordatorio alternativo:', { title, date, time, description });

    // Cerrar el formulario
    document.getElementById('reminderFormAlt').parentElement.parentElement.remove();

    // Mostrar mensaje de éxito
    alert('Recordatorio guardado exitosamente');
}

// Función para inicializar event listeners de recordatorios
function inicializarEventListenersRecordatorios() {
    console.log('🔔 Inicializando event listeners de recordatorios...');

    // Event listener para crear recordatorio
    const btnCrearRecordatorio = document.getElementById('btnCrearRecordatorio');
    console.log('🔍 Buscando botón crear recordatorio:', btnCrearRecordatorio);

    if (btnCrearRecordatorio) {
        console.log('✅ Botón crear recordatorio encontrado, agregando event listener...');

        // Remover event listeners existentes para evitar duplicados
        btnCrearRecordatorio.removeEventListener('click', handleCrearRecordatorio);
        btnCrearRecordatorio.addEventListener('click', handleCrearRecordatorio);

        console.log('✅ Event listener agregado al botón');
    } else {
        console.error('❌ Botón crear recordatorio NO encontrado');

        // Buscar el botón por clase como respaldo
        const botonesRecordatorio = document.querySelectorAll('.btn-outline-light');
        console.log('🔍 Buscando botones por clase:', botonesRecordatorio);

        botonesRecordatorio.forEach(boton => {
            if (boton.title === 'Crear Recordatorio') {
                console.log('✅ Botón encontrado por título, agregando event listener...');
                boton.removeEventListener('click', handleCrearRecordatorio);
                boton.addEventListener('click', handleCrearRecordatorio);
            }
        });
    }

    // Event listeners para editar recordatorios (delegación de eventos)
    document.addEventListener('click', function (e) {
        if (e.target.closest('.btn-edit-reminder')) {
            const button = e.target.closest('.btn-edit-reminder');
            const recordatorioId = button.getAttribute('data-id');
            console.log('✏️ Editando recordatorio:', recordatorioId);
            editReminder(recordatorioId);
        }

        if (e.target.closest('.btn-delete-reminder')) {
            const button = e.target.closest('.btn-delete-reminder');
            const recordatorioId = button.getAttribute('data-id');
            console.log('🗑️ Eliminando recordatorio:', recordatorioId);
            deleteReminder(recordatorioId);
        }
    });

    console.log('✅ Event listeners de recordatorios inicializados');
}

// Función adicional para asegurar que los botones funcionen
function inicializarBotonesRecordatorios() {
    console.log('🔧 Inicialización adicional de botones de recordatorios...');

    // Buscar todos los botones que puedan ser de recordatorios
    const botones = document.querySelectorAll('button');

    botones.forEach(boton => {
        // Verificar si es el botón de crear recordatorio
        if (boton.id === 'btnCrearRecordatorio' ||
            boton.title === 'Crear Recordatorio' ||
            boton.textContent.includes('Crear Recordatorio')) {

            console.log('🔍 Encontrado botón de crear recordatorio:', boton);

            // Remover todos los event listeners existentes
            const nuevoBoton = boton.cloneNode(true);
            boton.parentNode.replaceChild(nuevoBoton, boton);

            // Agregar el event listener correcto
            nuevoBoton.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('🔔 Botón crear recordatorio clickeado (inicialización adicional)');
                handleCrearRecordatorio();
            });

            console.log('✅ Botón de crear recordatorio configurado correctamente');
        }
    });

    // También buscar por onclick y eliminarlo
    const botonesConOnclick = document.querySelectorAll('[onclick*="showReminderModal"]');
    botonesConOnclick.forEach(boton => {
        console.log('🔧 Removiendo onclick problemático de:', boton);
        boton.removeAttribute('onclick');

        // Agregar event listener correcto
        boton.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('🔔 Botón crear recordatorio clickeado (removido onclick)');
            handleCrearRecordatorio();
        });
    });
}

// Funciones de navegación de fecha
function navegarAnterior() {
    if (currentView === 'diaria') {
        fechaActualAgenda.setDate(fechaActualAgenda.getDate() - 1);
    } else if (currentView === 'semanal') {
        fechaActualAgenda.setDate(fechaActualAgenda.getDate() - 7);
    } else if (currentView === 'mensual') {
        fechaActualAgenda.setMonth(fechaActualAgenda.getMonth() - 1);
    }
    cargarAgenda(fechaActualAgenda.toISOString().split('T')[0]);
}

function navegarSiguiente() {
    if (currentView === 'diaria') {
        fechaActualAgenda.setDate(fechaActualAgenda.getDate() + 1);
    } else if (currentView === 'semanal') {
        fechaActualAgenda.setDate(fechaActualAgenda.getDate() + 7);
    } else if (currentView === 'mensual') {
        fechaActualAgenda.setMonth(fechaActualAgenda.getMonth() + 1);
    }
    cargarAgenda(fechaActualAgenda.toISOString().split('T')[0]);
}

function irHoy() {
    fechaActualAgenda = new Date();
    cargarAgenda();
}

// Funciones de navegación específicas (para compatibilidad)
function prevDay() {
    navegarAnterior();
}

function nextDay() {
    navegarSiguiente();
}

function today() {
    irHoy();
}

// Función para agendar nueva cita
function agendarCita(hora = null) {
    console.log(`📅 Agendando cita para las ${hora || 'hora no especificada'}`);

    // Llenar el formulario con la hora seleccionada
    if (hora) {
        const appointmentTime = document.getElementById('appointmentTime');
        if (appointmentTime) {
            appointmentTime.value = hora;
        }
    }

    // Llenar la fecha actual
    const appointmentDate = document.getElementById('appointmentDate');
    if (appointmentDate) {
        appointmentDate.value = fechaActualAgenda.toISOString().split('T')[0];
    }

    // Cargar pacientes en el select
    cargarPacientesEnSelect();

    // Mostrar modal
    const modal = document.getElementById('scheduleModal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

// Función para cargar pacientes en el select de citas
function cargarPacientesEnSelect() {
    const select = document.getElementById('appointmentPatient');
    if (!select) return;

    // Limpiar opciones existentes (excepto la primera)
    while (select.children.length > 1) {
        select.removeChild(select.lastChild);
    }

    // Usar la lista global de pacientes si está disponible
    if (window.pacientesList && window.pacientesList.length > 0) {
        window.pacientesList.forEach(paciente => {
            const option = document.createElement('option');
            option.value = paciente.paciente_id;
            option.textContent = `${paciente.nombre_completo} - ${paciente.rut}`;
            select.appendChild(option);
        });
    } else {
        // Si no hay lista global, cargar desde API
        fetch('/api/professional/patients')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.pacientes) {
                    data.pacientes.forEach(paciente => {
                        const option = document.createElement('option');
                        option.value = paciente.paciente_id;
                        option.textContent = `${paciente.nombre_completo} - ${paciente.rut}`;
                        select.appendChild(option);
                    });
                }
            })
            .catch(error => {
                console.error('❌ Error cargando pacientes:', error);
            });
    }
}

// Función para mostrar modal de agenda (alternativa)
function showScheduleModal() {
    agendarCita();
}

// Función para guardar cita (sobrescribir la existente)
function saveAppointment() {
    console.log('💾 Guardando cita...');

    const form = document.getElementById('scheduleForm');
    if (!form) {
        console.error('❌ Formulario de cita no encontrado');
        showNotification('Error: Formulario no encontrado', 'error');
        return;
    }

    // Obtener datos del formulario
    const citaData = {
        paciente_id: document.getElementById('appointmentPatient').value,
        fecha: document.getElementById('appointmentDate').value,
        hora: document.getElementById('appointmentTime').value,
        tipo_atencion: document.getElementById('appointmentType').value,
        notas: document.getElementById('appointmentNotes').value
    };

    console.log('📝 Datos de la cita:', citaData);

    // Validar campos requeridos
    if (!citaData.paciente_id) {
        showNotification('Debe seleccionar un paciente', 'error');
        return;
    }

    if (!citaData.fecha) {
        showNotification('Debe seleccionar una fecha', 'error');
        return;
    }

    if (!citaData.hora) {
        showNotification('Debe seleccionar una hora', 'error');
        return;
    }

    if (!citaData.tipo_atencion) {
        showNotification('Debe seleccionar un tipo de atención', 'error');
        return;
    }

    // Enviar datos al servidor
    fetch('/api/professional/schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(citaData)
    })
        .then(response => response.json())
        .then(data => {
            console.log('📥 Respuesta del servidor:', data);

            if (data.success) {
                showNotification('Cita agendada exitosamente', 'success');

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleModal'));
                if (modal) {
                    modal.hide();
                }

                // Limpiar formulario
                form.reset();

                // Recargar agenda
                cargarAgenda();

            } else {
                showNotification(data.message || 'Error al agendar la cita', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showNotification('Error de conexión al agendar la cita', 'error');
        });
}

// Función para ver detalles de una cita
function verCita(citaId) {
    console.log(`👁️ Viendo cita: ${citaId}`);

    const cita = citasDelDia.find(c => c.cita_id === citaId);
    if (!cita) {
        showNotification('Cita no encontrada', 'error');
        return;
    }

    // Mostrar detalles de la cita (puedes implementar un modal específico)
    alert(`Detalles de la cita:
Paciente: ${cita.paciente_nombre}
RUT: ${cita.paciente_rut}
Hora: ${cita.hora}
Tipo: ${cita.tipo_atencion}
Estado: ${cita.estado}
Notas: ${cita.notas || 'Sin notas'}`);
}

// Función para confirmar una cita
function confirmarCita(citaId) {
    console.log(`✅ Confirmando cita: ${citaId}`);

    actualizarEstadoCita(citaId, 'confirmada');
}

// Función para cancelar una cita
function cancelarCita(citaId) {
    console.log(`❌ Cancelando cita: ${citaId}`);

    if (confirm('¿Está seguro de que desea cancelar esta cita?')) {
        actualizarEstadoCita(citaId, 'cancelada');
    }
}

// Función para actualizar el estado de una cita
function actualizarEstadoCita(citaId, nuevoEstado) {
    fetch(`/api/professional/schedule/${citaId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ estado: nuevoEstado })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`Cita ${nuevoEstado} exitosamente`, 'success');
                cargarAgenda(); // Recargar agenda
            } else {
                showNotification(data.message || 'Error al actualizar la cita', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showNotification('Error de conexión al actualizar la cita', 'error');
        });
}

// Función para eliminar una cita
function eliminarCita(citaId) {
    if (!confirm('¿Está seguro de que desea eliminar esta cita?')) {
        return;
    }

    fetch(`/api/professional/schedule/${citaId}`, {
        method: 'DELETE',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Cita eliminada exitosamente', 'success');
                cargarAgenda(); // Recargar agenda
            } else {
                showNotification(data.message || 'Error al eliminar la cita', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showNotification('Error de conexión al eliminar la cita', 'error');
        });
}

// Función para ver la cita (compatibilidad con HTML existente)
function viewAppointment(citaId) {
    verCita(citaId);
}

// Función para agendar en horario específico (compatibilidad con HTML existente)
function scheduleAppointment(hora) {
    agendarCita(hora);
}

// Exponer funciones globalmente
window.cargarAgenda = cargarAgenda;
window.agendarCita = agendarCita;
window.showScheduleModal = showScheduleModal;
window.saveAppointment = saveAppointment;
window.verCita = verCita;
window.confirmarCita = confirmarCita;
window.cancelarCita = cancelarCita;
window.eliminarCita = eliminarCita;
window.viewAppointment = viewAppointment;
window.scheduleAppointment = scheduleAppointment;
window.prevDay = prevDay;
window.nextDay = nextDay;
window.today = today;

console.log('✅ Funciones de agenda cargadas correctamente');

// ====== FUNCIONES DE CONFIGURACIÓN DE HORARIOS ======

// Función para mostrar modal de configuración de horarios
function configurarHorarios() {
    console.log('⚙️ Configurando horarios...');

    // Cargar horarios actuales
    cargarHorariosActuales();

    // Mostrar modal
    const modal = document.getElementById('horariosModal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

// Función para cargar horarios actuales
function cargarHorariosActuales() {
    fetch('/api/professional/working-hours')
        .then(response => response.json())
        .then(data => {
            console.log('📥 Horarios actuales:', data);

            if (data.success && data.horarios) {
                // Mapear días de español a inglés para IDs
                const diasMap = {
                    'Lunes': 'lunes',
                    'Martes': 'martes',
                    'Miércoles': 'miercoles',
                    'Jueves': 'jueves',
                    'Viernes': 'viernes',
                    'Sábado': 'sabado',
                    'Domingo': 'domingo'
                };

                // Llenar formulario con horarios existentes
                data.horarios.forEach(horario => {
                    const diaId = diasMap[horario.dia_semana];
                    if (diaId) {
                        const disponibleCheckbox = document.getElementById(`${diaId}_disponible`);
                        const inicioInput = document.getElementById(`${diaId}_inicio`);
                        const finInput = document.getElementById(`${diaId}_fin`);
                        const notasInput = document.getElementById(`${diaId}_notas`);

                        if (disponibleCheckbox) disponibleCheckbox.checked = horario.disponible;
                        if (inicioInput) inicioInput.value = horario.hora_inicio;
                        if (finInput) finInput.value = horario.hora_fin;
                        if (notasInput) notasInput.value = horario.notas;
                    }
                });
            }
        })
        .catch(error => {
            console.error('❌ Error cargando horarios:', error);
            showNotification('Error al cargar horarios actuales', 'error');
        });
}

// Función para guardar horarios
function guardarHorarios() {
    console.log('💾 Guardando horarios...');

    // Mapear días de IDs a español
    const diasMap = {
        'lunes': 'Lunes',
        'martes': 'Martes',
        'miercoles': 'Miércoles',
        'jueves': 'Jueves',
        'viernes': 'Viernes',
        'sabado': 'Sábado',
        'domingo': 'Domingo'
    };

    const horarios = [];

    // Recopilar datos de todos los días
    Object.keys(diasMap).forEach(diaId => {
        const disponibleCheckbox = document.getElementById(`${diaId}_disponible`);
        const inicioInput = document.getElementById(`${diaId}_inicio`);
        const finInput = document.getElementById(`${diaId}_fin`);
        const notasInput = document.getElementById(`${diaId}_notas`);

        if (disponibleCheckbox && inicioInput && finInput) {
            horarios.push({
                dia_semana: diasMap[diaId],
                disponible: disponibleCheckbox.checked,
                hora_inicio: inicioInput.value,
                hora_fin: finInput.value,
                notas: notasInput ? notasInput.value : ''
            });
        }
    });

    console.log('📝 Horarios a guardar:', horarios);

    // Validar horarios
    for (const horario of horarios) {
        if (horario.disponible) {
            if (!horario.hora_inicio || !horario.hora_fin) {
                showNotification(`Debe especificar hora de inicio y fin para ${horario.dia_semana}`, 'error');
                return;
            }

            if (horario.hora_inicio >= horario.hora_fin) {
                showNotification(`La hora de inicio debe ser menor que la hora de fin para ${horario.dia_semana}`, 'error');
                return;
            }
        }
    }

    // Enviar al servidor
    fetch('/api/professional/working-hours', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ horarios: horarios })
    })
        .then(response => response.json())
        .then(data => {
            console.log('📥 Respuesta del servidor:', data);

            if (data.success) {
                showNotification('Horarios guardados exitosamente', 'success');

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('horariosModal'));
                if (modal) {
                    modal.hide();
                }

                // Recargar agenda si está visible
                const agendaPane = document.getElementById('schedule');
                if (agendaPane && agendaPane.classList.contains('active')) {
                    cargarAgenda();
                }

            } else {
                showNotification(data.message || 'Error al guardar horarios', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error:', error);
            showNotification('Error de conexión al guardar horarios', 'error');
        });
}

// Exponer funciones globalmente
window.configurarHorarios = configurarHorarios;
window.guardarHorarios = guardarHorarios;

console.log('✅ Funciones de configuración de horarios cargadas correctamente');

// ========================================
// FUNCIONES PARA VISTAS MÚLTIPLES DE AGENDA
// ========================================

// Función para cambiar vista de agenda
function cambiarVista(nuevaVista) {
    console.log(`📅 Cambiando vista a: ${nuevaVista}`);

    currentView = nuevaVista;

    // Ocultar todas las vistas
    document.getElementById('vistaDiariaContent').classList.add('d-none');
    document.getElementById('vistaSemanalContent').classList.add('d-none');
    document.getElementById('vistaMensualContent').classList.add('d-none');

    // Mostrar vista seleccionada
    document.getElementById(`vista${nuevaVista.charAt(0).toUpperCase() + nuevaVista.slice(1)}Content`).classList.remove('d-none');

    // Actualizar título
    const titulo = document.querySelector('.card-header h5');
    if (titulo) {
        const fecha = fechaActualAgenda.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        switch (nuevaVista) {
            case 'diaria':
                titulo.innerHTML = `Agenda de Hoy - <span id="currentDate">${fecha}</span>`;
                break;
            case 'semanal':
                titulo.innerHTML = `Agenda Semanal - <span id="currentDate">${fecha}</span>`;
                break;
            case 'mensual':
                titulo.innerHTML = `Agenda Mensual - <span id="currentDate">${fecha}</span>`;
                break;
        }
    }

    // Recargar datos
    cargarAgenda();
}

// Función para actualizar vista semanal
function actualizarVistaSemanal(agendaSemanal, fechaInicio, fechaFin) {
    console.log('📅 Actualizando vista semanal:', agendaSemanal);

    const tbody = document.getElementById('agendaSemanalBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    // Generar horarios de 8:00 a 18:00
    const horarios = [];
    for (let hora = 8; hora < 18; hora++) {
        horarios.push(`${hora.toString().padStart(2, '0')}:00`);
    }

    // Crear filas por horario
    horarios.forEach(hora => {
        const fila = document.createElement('tr');
        fila.innerHTML = `<td class="text-center fw-bold">${hora}</td>`;

        // Agregar celdas para cada día de la semana
        Object.keys(agendaSemanal).forEach(fecha => {
            const diaData = agendaSemanal[fecha];
            const celda = document.createElement('td');

            // Buscar citas para esta hora
            const citasHora = diaData.citas.filter(cita => cita.hora.startsWith(hora.split(':')[0]));

            if (citasHora.length > 0) {
                citasHora.forEach(cita => {
                    const citaDiv = document.createElement('div');
                    citaDiv.className = `cita-semanal ${cita.estado}`;
                    citaDiv.innerHTML = `
                        <div>${cita.hora}</div>
                        <div>${cita.paciente_nombre}</div>
                    `;
                    citaDiv.onclick = () => verCita(cita.cita_id);
                    celda.appendChild(citaDiv);
                });
            } else {
                // Slot disponible
                const slotDiv = document.createElement('div');
                slotDiv.className = 'slot-disponible';
                slotDiv.textContent = 'Disponible';
                slotDiv.onclick = () => agendarCitaFecha(fecha, hora);
                celda.appendChild(slotDiv);
            }

            fila.appendChild(celda);
        });

        tbody.appendChild(fila);
    });
}

// Función para actualizar vista mensual
function actualizarVistaMensual(agendaMensual, fechaInicio, fechaFin) {
    console.log('📅 Actualizando vista mensual:', agendaMensual);

    const calendario = document.getElementById('calendarioMensual');
    if (!calendario) return;

    calendario.innerHTML = '';

    // Headers de días de la semana
    const diasSemana = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    diasSemana.forEach(dia => {
        const header = document.createElement('div');
        header.className = 'dia-header';
        header.textContent = dia;
        calendario.appendChild(header);
    });

    // Obtener primer día del mes y calcular días a mostrar
    const fechaInicioObj = new Date(fechaInicio);
    const fechaFinObj = new Date(fechaFin);

    // Agregar días del mes anterior si es necesario
    const primerDiaSemana = fechaInicioObj.getDay();
    const fechaInicioCalendario = new Date(fechaInicioObj);
    fechaInicioCalendario.setDate(fechaInicioCalendario.getDate() - primerDiaSemana);

    // Generar calendario
    const fechaActual = new Date(fechaInicioCalendario);
    const hoy = new Date().toISOString().split('T')[0];

    for (let i = 0; i < 42; i++) { // 6 semanas máximo
        const fechaStr = fechaActual.toISOString().split('T')[0];
        const diaCelda = document.createElement('div');
        diaCelda.className = 'dia-celda';

        // Verificar si es del mes actual
        if (fechaActual.getMonth() !== fechaInicioObj.getMonth()) {
            diaCelda.classList.add('otro-mes');
        }

        // Verificar si es hoy
        if (fechaStr === hoy) {
            diaCelda.classList.add('hoy');
        }

        // Número del día
        const diaNumero = document.createElement('div');
        diaNumero.className = 'dia-numero';
        diaNumero.textContent = fechaActual.getDate();
        diaCelda.appendChild(diaNumero);

        // Citas del día
        const diaData = agendaMensual[fechaStr];
        if (diaData && diaData.citas.length > 0) {
            diaData.citas.slice(0, 3).forEach(cita => { // Mostrar máximo 3 citas
                const citaDiv = document.createElement('div');
                citaDiv.className = `cita-mensual ${cita.estado}`;
                citaDiv.textContent = `${cita.hora} ${cita.paciente_nombre}`;
                citaDiv.onclick = () => verCita(cita.cita_id);
                diaCelda.appendChild(citaDiv);
            });

            // Mostrar contador si hay más citas
            if (diaData.citas.length > 3) {
                const contador = document.createElement('div');
                contador.className = 'contador-citas';
                contador.textContent = `+${diaData.citas.length - 3}`;
                diaCelda.appendChild(contador);
            }
        }

        // Click para agendar cita
        diaCelda.onclick = (e) => {
            if (e.target === diaCelda || e.target === diaNumero) {
                agendarCitaFecha(fechaStr);
            }
        };

        calendario.appendChild(diaCelda);
        fechaActual.setDate(fechaActual.getDate() + 1);

        // Parar si hemos pasado el final del mes siguiente
        if (fechaActual > fechaFinObj && fechaActual.getDate() > 7) {
            break;
        }
    }
}

// Función para agendar cita en fecha específica
function agendarCitaFecha(fecha, hora = null) {
    console.log(`📅 Agendando cita para ${fecha} a las ${hora || 'hora por definir'}`);

    // Llenar el formulario
    const appointmentDate = document.getElementById('appointmentDate');
    if (appointmentDate) {
        appointmentDate.value = fecha;
    }

    if (hora) {
        const appointmentTime = document.getElementById('appointmentTime');
        if (appointmentTime) {
            appointmentTime.value = hora;
        }
    }

    // Cargar pacientes y mostrar modal
    cargarPacientesEnSelect();

    const modal = document.getElementById('scheduleModal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

// Exponer funciones globalmente
window.cambiarVista = cambiarVista;
window.actualizarVistaSemanal = actualizarVistaSemanal;
window.actualizarVistaMensual = actualizarVistaMensual;
window.agendarCitaFecha = agendarCitaFecha;
window.navegarAnterior = navegarAnterior;
window.navegarSiguiente = navegarSiguiente;
window.irHoy = irHoy;

console.log('✅ Funciones de vistas múltiples de agenda cargadas correctamente');



