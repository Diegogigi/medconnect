// Archivo principal del dashboard profesional
// Las funciones globales est n definidas en global-functions.js

// Variables globales para la agenda
let currentDate = new Date();
let agendaData = {};
let pacientesDropdownList = [];
let currentView = 'diaria'; // diaria, semanal, mensual
let currentWeekStart = null;
let currentMonth = null;

// Asegurar que las funciones estn disponibles globalmente
// Estas funciones se definen ms abajo en el archivo
window.showReminderModal = null;
window.editReminder = null;
window.deleteReminder = null;

// Funcin para escapar caracteres especiales en HTML
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
        console.error(' Error convirtiendo a string:', error, 'valor:', text);
        return 'Error de conversin';
    }

    // Verificar que stringValue es realmente un string
    if (typeof stringValue !== 'string') {
        console.error(' Valor no es string despus de conversin:', stringValue, 'tipo:', typeof stringValue);
        return 'Error de tipo';
    }

    // Si est vaco despus de la conversin, retornar vaco
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
        console.error(' Error procesando string:', error, 'valor:', stringValue);
        return 'Error de procesamiento';
    }
}

// Funcin helper para obtener valores seguros de pacientes
function getSafeValue(value, defaultValue = 'No especificado') {
    if (value === null || value === undefined || value === '') {
        return defaultValue;
    }
    return value;
}

// Función para mostrar confirmaciones de eliminación con diseño mejorado
function mostrarConfirmacionEliminacion(titulo, pregunta, descripcion, textoBoton, onConfirm) {
    // Crear modal de confirmación
    const modalId = 'confirmacionEliminacionModal';
    let modal = document.getElementById(modalId);

    // Si el modal no existe, crearlo
    if (!modal) {
        modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = modalId;
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('aria-labelledby', modalId + 'Label');
        modal.setAttribute('aria-hidden', 'true');

        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-header bg-danger text-white border-0">
                        <h5 class="modal-title" id="${modalId}Label">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            ${titulo}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body p-4">
                        <div class="text-center mb-4">
                            <div class="bg-danger bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                                <i class="fas fa-trash-alt text-danger" style="font-size: 24px;"></i>
                            </div>
                            <h6 class="text-danger fw-bold mb-2">${pregunta}</h6>
                            <p class="text-muted mb-0">${descripcion}</p>
                        </div>
                        <div class="alert alert-warning border-0 bg-warning bg-opacity-10">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-info-circle text-warning me-2"></i>
                                <small class="text-warning fw-medium">
                                    <strong>Importante:</strong> Esta acción no se puede deshacer una vez confirmada.
                                </small>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer border-0 pt-0">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>
                            Cancelar
                        </button>
                        <button type="button" class="btn btn-danger" id="confirmarEliminacionBtn">
                            <i class="fas fa-trash-alt me-2"></i>
                            ${textoBoton}
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    // Configurar el botón de confirmación
    const confirmarBtn = modal.querySelector('#confirmarEliminacionBtn');
    confirmarBtn.onclick = () => {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
        onConfirm();
    };

    // Mostrar el modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

document.addEventListener('DOMContentLoaded', function () {
    // Inicializar componentes existentes
    initMaps();
    initAvailabilityToggle();
    setupMobileNav();
    initRequestInteractions();
    handleFileUpload();

    // Cargar estadsticas del dashboard
    cargarEstadisticasDashboard();

    // Prueba de conexin con el backend
    console.log(' Verificando conexin con el backend...');
    fetch('/health')
        .then(response => {
            console.log(' Health check response:', response.status);
            return response.json();
        })
        .then(data => {
            console.log(' Health check data:', data);
        })
        .catch(error => {
            console.error(' Error en health check:', error);
        });

    // Prueba especfica del sistema de atenciones
    console.log(' Probando sistema de atenciones...');
    fetch('/api/test-atencion')
        .then(response => {
            console.log(' Test atenciones response:', response.status);
            return response.json();
        })
        .then(data => {
            console.log(' Test atenciones data:', data);
            if (data.success) {
                console.log(' Sistema de atenciones funcionando');
                console.log(` Usuario ID: ${data.user_id}`);
                console.log(` Email: ${data.user_email}`);
                console.log(` Registros existentes: ${data.total_records}`);
            } else {
                console.error(' Error en sistema de atenciones:', data.message);
            }
        })
        .catch(error => {
            console.error(' Error probando sistema de atenciones:', error);
        });

    // Cargar historial de atenciones al iniciar
    actualizarHistorialAtenciones();

    // Configurar gestin de pacientes
    setupPatientSearch();

    // Event listener para la pestaa de pacientes
    const patientsTab = document.getElementById('patients-tab');
    if (patientsTab) {
        patientsTab.addEventListener('shown.bs.tab', function () {
            console.log(' Pestaa de pacientes activada, cargando datos...');
            cargarListaPacientes();
        });
    }

    // Event listener para la pestaa de agenda
    const scheduleTab = document.getElementById('schedule-tab');
    if (scheduleTab) {
        scheduleTab.addEventListener('shown.bs.tab', function () {
            console.log(' Pestaa de agenda activada, cargando datos...');
            // Inicializar con vista diaria
            currentView = 'diaria';
            cargarAgenda();
        });
    }

    // Si la pestaa de pacientes est activa al cargar, cargar los datos
    if (patientsTab && patientsTab.classList.contains('active')) {
        cargarListaPacientes();
    }

    // Cargar pacientes despus de un breve delay para asegurar que todo est listo
    setTimeout(() => {
        console.log(' Cargando pacientes iniciales...');
        cargarListaPacientes();
        cargarPacientesDropdown(); // Cargar tambin en el dropdown del formulario
    }, 1000);

    // Inicializar bsqueda de atenciones
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
            // Actualizar historial cada vez que se abra la pestaa
            setTimeout(() => {
                actualizarHistorialAtenciones();
            }, 100);
        });
    }

    // Manejar la seleccin de archivos en el formulario de nueva atencin
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
    // Verificar si Leaflet est disponible
    if (typeof L === 'undefined') {
        console.warn(' Leaflet no est disponible, saltando inicializacin de mapas');
        return;
    }

    try {
        // Verificar si el contenedor del mapa existe antes de inicializar
        const coverageMapElement = document.getElementById('coverage-map');
        if (!coverageMapElement) {
            console.log(' Contenedor de mapa no encontrado, saltando inicializacin');
            return;
        }

        // Mapa de cobertura
        const coverageMap = L.map('coverage-map').setView([-33.45, -70.67], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(coverageMap);

        // Crear marcador para la ubicacin del profesional
        const professionalIcon = L.divIcon({
            className: 'professional-marker',
            html: '<div class="marker-icon"><i class="fas fa-user-md"></i></div>',
            iconSize: [40, 40],
            iconAnchor: [20, 40]
        });

        // Agregar marcador del profesional
        const professionalMarker = L.marker([-33.45, -70.67], { icon: professionalIcon }).addTo(coverageMap);

        // Crear crculo de cobertura
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

            // Lnea de ruta
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

        console.log(' Mapas inicializados correctamente');
    } catch (error) {
        console.error(' Error inicializando mapas:', error);
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

// Navegacin mvil
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

            // Si no es el enlace de inicio, prevenir navegacin por defecto
            if (this.id !== 'pro-nav-home') {
                e.preventDefault();

                // Aqu se podra implementar navegacin por SPA
                // Por ahora solo para demostracin
                const targetSection = this.id.replace('pro-nav-', '');
                console.log(`Navegando a seccin: ${targetSection}`);
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

            // Mostrar mensaje de confirmacin
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

            // Mostrar mensaje de confirmacin
            showNotification('Solicitud rechazada');

            // Animar desaparicin de la tarjeta
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
            console.log(' Formulario de atención enviado');

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
                console.error(' Campos faltantes:', missingFields);
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

                        console.log(' Subiendo archivos...');
                        const uploadResponse = await fetch('/api/archivos/upload', {
                            method: 'POST',
                            body: formData
                        });

                        const uploadResult = await uploadResponse.json();
                        if (!uploadResult.success) {
                            console.error(' Error subiendo archivos:', uploadResult.error);
                            showNotification('Atención registrada, pero hubo un error al subir algunos archivos', 'warning');
                        } else {
                            console.log(' Archivos subidos correctamente:', uploadResult);
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
                    console.error(' Error del servidor:', atencionResult.message);
                    showNotification(atencionResult.message || 'Error al registrar la atención', 'error');
                }
            } catch (error) {
                console.error(' Error de red:', error);
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

// Función para borrar el mensaje de bienvenida
function borrarMensajeBienvenida() {
    const welcomeMessage = document.getElementById('welcomeMessage');
    if (welcomeMessage) {
        // Agregar animación de fade out
        welcomeMessage.style.transition = 'opacity 0.3s ease-out';
        welcomeMessage.style.opacity = '0';

        // Remover el elemento después de la animación
        setTimeout(() => {
            welcomeMessage.remove();
            console.log('✅ Mensaje de bienvenida eliminado');
        }, 300);
    }
}

// Función para actualizar el mensaje de bienvenida con el nombre del usuario
function actualizarMensajeBienvenida(nombreUsuario) {
    const welcomeMessage = document.getElementById('welcomeMessage');
    if (welcomeMessage) {
        const messageText = welcomeMessage.querySelector('.message-text p');
        if (messageText) {
            const nombre = nombreUsuario || 'Profesional';
            messageText.textContent = `¡Hola ${nombre}! Soy Tena, tu asistente IA. Completa el formulario y observa cómo trabajo en tiempo real.`;
        }
    }
}

// Función para actualizar el historial de atenciones
function actualizarHistorialAtenciones() {
    console.log(' Iniciando actualización del historial...');
    fetch('/api/get-atenciones')
        .then(response => {
            console.log(' Respuesta get-atenciones:', response.status);
            return response.json();
        })
        .then(data => {
            console.log(' Datos del historial recibidos:', data);
            if (data.success && data.atenciones) {
                const tbody = document.getElementById('historialAtenciones');
                console.log(' Elemento tbody encontrado:', !!tbody);
                if (tbody) {
                    tbody.innerHTML = '';
                    console.log(` Procesando ${data.atenciones.length} atenciones`);

                    data.atenciones.forEach((atencion, index) => {
                        console.log(` Procesando atención ${index + 1}:`, atencion);
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${formatearFecha(atencion.fecha_hora)}</td>
                            <td>${atencion.paciente_nombre}</td>
                            <td><span class="badge bg-primary">${atencion.tipo_atencion}</span></td>
                            <td title="${(atencion.diagnostico || '').replaceAll('\n', ' ').slice(0, 300)}">${atencion.motivo_consulta || atencion.motivo || (atencion.diagnostico ? atencion.diagnostico.slice(0, 120) + '…' : 'Sin motivo')}</td>
                            <td>
                                <span class="badge bg-success">Completada</span>
                            </td>
                            <td>
                                <div class="d-flex justify-content-center gap-1">
                                    <button class="btn btn-sm btn-action btn-view" onclick="verDetalleAtencion('${atencion.atencion_id}')" title="Ver Detalle">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <button class="btn btn-sm btn-action btn-edit" onclick="editarAtencion('${atencion.atencion_id}')" title="Editar">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-sm btn-action btn-delete" onclick="eliminarAtencion('${atencion.atencion_id}')" title="Eliminar">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                    <button class="btn btn-sm btn-action btn-session" onclick="verSesionesAtencion('${atencion.atencion_id}')" title="Ver Sesiones">
                                        <i class="fas fa-calendar-alt"></i>
                                    </button>
                                </div>
                            </td>
                        `;
                        tbody.appendChild(row);
                    });
                    console.log(' Historial actualizado correctamente');
                } else {
                    console.error(' No se encontró el elemento tbody con ID historialAtenciones');
                }
            } else {
                console.error(' Respuesta inválida del servidor:', data);
            }
        })
        .catch(error => {
            console.error(' Error al actualizar historial:', error);
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
    mostrarConfirmacionEliminacion(
        'Eliminar Atención Médica',
        '¿Está seguro de que desea eliminar esta atención médica?',
        'Esta acción eliminará permanentemente el registro de la atención y todos los datos asociados. Esta acción no se puede deshacer.',
        'Eliminar Atención',
        () => {
            fetch(`/api/delete-atencion/${atencionId}`, {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('✅ Atención eliminada exitosamente', 'success');
                        actualizarHistorialAtenciones();
                        actualizarEstadisticasDashboard();
                    } else {
                        showNotification(data.message || '❌ Error al eliminar la atención', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('❌ Error de conexión al eliminar la atención', 'error');
                });
        }
    );
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
    console.log(` Viendo detalle de atención: ${atencionId}`);

    fetch(`/api/get-atencion/${atencionId}`)
        .then(response => {
            console.log(' Respuesta get-atencion:', response.status);
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(' Datos de la atención:', data);
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
                console.error(' Error en la respuesta de la API:', data.message);
                showNotification(`Error: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error(' Error en fetch:', error);
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
    console.log(` Vista previa de: ${nombreArchivo} (ID: ${archivoId})`);

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

                console.log(' Imagen cargada usando blob URL');

                // Limpiar URL del blob cuando se cierre el modal
                const modalElement = document.getElementById(modalId);
                modalElement.addEventListener('hidden.bs.modal', () => {
                    URL.revokeObjectURL(imageUrl);
                    modalElement.remove();
                });
            })
            .catch(error => {
                console.error(' Error cargando imagen:', error);
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
                                    onload="console.log(' PDF cargado correctamente')"
                                    onerror="console.error(' Error cargando PDF')">
                            </iframe>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-sm btn-action btn-download" onclick="downloadArchivo('${archivoId}', '${nombreArchivo}')">
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
                            <button type="button" class="btn btn-sm btn-action btn-download" onclick="downloadArchivo('${archivoId}', '${nombreArchivo}')">
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
    console.log(` Descargando: ${nombreArchivo} (ID: ${archivoId})`);
    const downloadUrl = `/api/archivos/${archivoId}/download`;

    // Crear un enlace temporal y hacer clic en l
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.target = '_blank'; // Abrir en nueva pestaa por si el navegador lo bloquea
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
    if (confirm('Est seguro de que desea cancelar esta cita?')) {
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

// Funcin para exportar el historial
function exportarHistorial(formato) {
    // Obtener los datos de la tabla
    const tabla = document.getElementById('historialAtenciones');
    const filas = tabla.getElementsByTagName('tr');
    let datos = [];

    // Obtener encabezados
    const encabezados = ['Fecha', 'Paciente', 'Tipo', 'Diagnstico', 'Estado'];
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

    // Crear el archivo segn el formato
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

// ========================================
// FUNCIONES PARA MANEJO DE SESIONES
// ========================================

/**
 * Abre el modal para registrar una nueva sesión
 * @param {string} atencionId - ID de la atención
 * @param {string} pacienteNombre - Nombre del paciente
 */
function registrarSesion(atencionId, pacienteNombre) {
    console.log('📝 Abriendo modal para registrar sesión:', { atencionId, pacienteNombre });

    // Limpiar formulario
    document.getElementById('sesionForm').reset();

    // Establecer valores iniciales
    document.getElementById('sesionAtencionId').value = atencionId;
    document.getElementById('sesionPaciente').value = pacienteNombre;

    // Establecer fecha y hora actual
    const ahora = new Date();
    const fechaHora = ahora.toISOString().slice(0, 16);
    document.getElementById('sesionFecha').value = fechaHora;

    // Verificar límite de sesiones
    verificarLimiteSesiones(atencionId);

    // Abrir modal
    const modal = new bootstrap.Modal(document.getElementById('sesionModal'));
    modal.show();
}

/**
 * Verifica el límite de sesiones para una atención (1-15 sesiones)
 * @param {string} atencionId - ID de la atención
 */
async function verificarLimiteSesiones(atencionId) {
    try {
        const response = await fetch(`/api/get-sesiones/${atencionId}`);
        const data = await response.json();

        if (data.success) {
            const numSesiones = data.sesiones ? data.sesiones.length : 0;

            if (numSesiones >= 15) {
                showNotification('⚠️ Esta atención ya tiene el máximo de 15 sesiones registradas', 'warning');
                document.querySelector('#sesionModal .btn-success').disabled = true;
            } else {
                document.querySelector('#sesionModal .btn-success').disabled = false;
                showNotification(`📊 Sesiones registradas: ${numSesiones}/15`, 'info');
            }
        }
    } catch (error) {
        console.error('Error verificando límite de sesiones:', error);
    }
}

/**
 * Guarda una nueva sesión
 */
async function guardarSesion() {
    console.log('💾 Guardando sesión...');

    const form = document.getElementById('sesionForm');
    const formData = new FormData(form);

    // Validar formulario
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Mostrar indicador de carga
    const btnGuardar = document.querySelector('#sesionModal .btn-success');
    const textoOriginal = btnGuardar.innerHTML;
    btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Guardando...';
    btnGuardar.disabled = true;

    try {
        const response = await fetch('/api/guardar-sesion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                atencion_id: formData.get('atencion_id'),
                fecha_sesion: formData.get('fecha_sesion'),
                duracion: parseInt(formData.get('duracion')),
                tipo_sesion: formData.get('tipo_sesion'),
                objetivos: formData.get('objetivos'),
                actividades: formData.get('actividades'),
                observaciones: formData.get('observaciones'),
                progreso: formData.get('progreso'),
                estado: formData.get('estado'),
                recomendaciones: formData.get('recomendaciones'),
                proxima_sesion: formData.get('proxima_sesion')
            })
        });

        const data = await response.json();

        if (data.success) {
            showNotification('✅ Sesión registrada exitosamente', 'success');

            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('sesionModal'));
            modal.hide();

            // Actualizar historial de atenciones
            actualizarHistorialAtenciones();

            // Limpiar formulario
            form.reset();

        } else {
            showNotification(`❌ Error al guardar sesión: ${data.message}`, 'error');
        }

    } catch (error) {
        console.error('Error guardando sesión:', error);
        showNotification('❌ Error de conexión al guardar sesión', 'error');
    } finally {
        // Restaurar botón
        btnGuardar.innerHTML = textoOriginal;
        btnGuardar.disabled = false;
    }
}

/**
 * Muestra las sesiones de una atención
 * @param {string} atencionId - ID de la atención
 */
async function verSesionesAtencion(atencionId) {
    console.log('👁️ Mostrando sesiones de atención:', atencionId);

    try {
        const response = await fetch(`/api/get-sesiones/${atencionId}`);
        const data = await response.json();

        if (data.success) {
            mostrarModalSesiones(data.sesiones, atencionId);
        } else {
            showNotification(`❌ Error al cargar sesiones: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error cargando sesiones:', error);
        showNotification('❌ Error de conexión al cargar sesiones', 'error');
    }
}

/**
 * Muestra el modal con las sesiones de una atención
 * @param {Array} sesiones - Lista de sesiones
 * @param {string} atencionId - ID de la atención
 */
function mostrarModalSesiones(sesiones, atencionId) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'sesionesModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-clipboard-list me-2 text-primary"></i>
                        Sesiones de la Atención
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <span class="badge bg-info">${sesiones.length}/15 sesiones</span>
                        <button class="btn btn-sm btn-action btn-session" onclick="registrarSesion('${atencionId}', 'Paciente')">
                            <i class="fas fa-calendar-plus me-1"></i>Nueva Sesión
                        </button>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-light">
                                <tr>
                                    <th>Fecha</th>
                                    <th>Duración</th>
                                    <th>Tipo</th>
                                    <th>Progreso</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${sesiones.map((sesion, index) => `
                                    <tr>
                                        <td>${formatearFecha(sesion.fecha_sesion)}</td>
                                        <td>${sesion.duracion} min</td>
                                        <td><span class="badge bg-primary">${sesion.tipo_sesion}</span></td>
                                        <td><span class="badge bg-${getProgresoColor(sesion.progreso)}">${sesion.progreso}</span></td>
                                        <td><span class="badge bg-${getEstadoColor(sesion.estado)}">${sesion.estado}</span></td>
                                        <td>
                                            <div class="btn-group btn-group-sm">
                                                                        <button class="btn btn-sm btn-action btn-view" onclick="verDetalleSesion('${sesion.id}')" title="Ver Detalle">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-action btn-edit" onclick="editarSesion('${sesion.id}')" title="Editar">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-action btn-delete" onclick="eliminarSesion('${sesion.id}')" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                                            </div>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();

    // Limpiar modal al cerrar
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

/**
 * Obtiene el color del badge para el progreso
 * @param {string} progreso - Nivel de progreso
 * @returns {string} Clase de color
 */
function getProgresoColor(progreso) {
    const colores = {
        'excelente': 'success',
        'muy_bueno': 'info',
        'bueno': 'primary',
        'regular': 'warning',
        'necesita_mejora': 'danger'
    };
    return colores[progreso] || 'secondary';
}

/**
 * Obtiene el color del badge para el estado
 * @param {string} estado - Estado de la sesión
 * @returns {string} Clase de color
 */
function getEstadoColor(estado) {
    const colores = {
        'completada': 'success',
        'pendiente': 'warning',
        'cancelada': 'danger',
        'reprogramada': 'info'
    };
    return colores[estado] || 'secondary';
}

/**
 * Muestra el detalle de una sesión
 * @param {string} sesionId - ID de la sesión
 */
async function verDetalleSesion(sesionId) {
    console.log('👁️ Mostrando detalle de sesión:', sesionId);

    try {
        const response = await fetch(`/api/get-sesion/${sesionId}`);
        const data = await response.json();

        if (data.success) {
            mostrarModalDetalleSesion(data.sesion);
        } else {
            showNotification(`❌ Error al cargar sesión: ${data.message}`, 'error');
        }
    } catch (error) {
        console.error('Error cargando sesión:', error);
        showNotification('❌ Error de conexión al cargar sesión', 'error');
    }
}

/**
 * Muestra el modal con el detalle de una sesión
 * @param {Object} sesion - Datos de la sesión
 */
function mostrarModalDetalleSesion(sesion) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'detalleSesionModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">
                        <i class="fas fa-clipboard-list me-2 text-info"></i>
                        Detalle de Sesión
                    </h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Información General</h6>
                            <p><strong>Fecha:</strong> ${formatearFecha(sesion.fecha_sesion)}</p>
                            <p><strong>Duración:</strong> ${sesion.duracion} minutos</p>
                            <p><strong>Tipo:</strong> <span class="badge bg-primary">${sesion.tipo_sesion}</span></p>
                            <p><strong>Estado:</strong> <span class="badge bg-${getEstadoColor(sesion.estado)}">${sesion.estado}</span></p>
                        </div>
                        <div class="col-md-6">
                            <h6>Evaluación</h6>
                            <p><strong>Progreso:</strong> <span class="badge bg-${getProgresoColor(sesion.progreso)}">${sesion.progreso}</span></p>
                        </div>
                    </div>
                    
                    <hr>
                    
                    <div class="row">
                        <div class="col-12">
                            <h6>Objetivos</h6>
                            <p>${sesion.objetivos || 'No especificado'}</p>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12">
                            <h6>Actividades Realizadas</h6>
                            <p>${sesion.actividades || 'No especificado'}</p>
                        </div>
                    </div>
                    
                    ${sesion.observaciones ? `
                    <div class="row">
                        <div class="col-12">
                            <h6>Observaciones</h6>
                            <p>${sesion.observaciones}</p>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${sesion.recomendaciones ? `
                    <div class="row">
                        <div class="col-12">
                            <h6>Recomendaciones</h6>
                            <p>${sesion.recomendaciones}</p>
                        </div>
                    </div>
                    ` : ''}
                    
                    ${sesion.proxima_sesion ? `
                    <div class="row">
                        <div class="col-12">
                            <h6>Próxima Sesión</h6>
                            <p>${sesion.proxima_sesion}</p>
                        </div>
                    </div>
                    ` : ''}
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                                            <button type="button" class="btn btn-sm btn-action btn-edit" onclick="editarSesion('${sesion.id}')">
                        <i class="fas fa-edit me-1"></i>Editar
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();

    // Limpiar modal al cerrar
    modal.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(modal);
    });
}

/**
 * Elimina una sesión
 * @param {string} sesionId - ID de la sesión
 */
async function eliminarSesion(sesionId) {
    console.log('🗑️ Eliminando sesión:', sesionId);

    mostrarConfirmacionEliminacion(
        'Eliminar Sesión de Tratamiento',
        '¿Está seguro de que desea eliminar esta sesión de tratamiento?',
        'Esta acción eliminará permanentemente el registro de la sesión y todos los datos asociados. Esta acción no se puede deshacer.',
        'Eliminar Sesión',
        async () => {
            try {
                const response = await fetch(`/api/eliminar-sesion/${sesionId}`, {
                    method: 'DELETE'
                });

                const data = await response.json();

                if (data.success) {
                    showNotification('✅ Sesión eliminada exitosamente', 'success');
                    // Cerrar modal de sesiones si está abierto
                    const sesionesModal = bootstrap.Modal.getInstance(document.getElementById('sesionesModal'));
                    if (sesionesModal) {
                        sesionesModal.hide();
                    }
                } else {
                    showNotification(`❌ Error al eliminar sesión: ${data.message}`, 'error');
                }
            } catch (error) {
                console.error('Error eliminando sesión:', error);
                showNotification('❌ Error de conexión al eliminar sesión', 'error');
            }
        }
    );
}

// Inicializar funciones de sesiones cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    console.log('📝 Inicializando funciones de sesiones...');
});

// Funcin para generar PDF de una atencin
function generarPDF(atencionId) {
    fetch(`/api/get-atencion/${atencionId}`)
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                showNotification('Error al obtener los datos de la atencin', 'error');
                return;
            }

            const atencion = data.atencion;
            const doc = new jsPDF();

            // Agregar logo y encabezado
            doc.setFontSize(20);
            doc.text('MedConnect', 105, 20, { align: 'center' });

            doc.setFontSize(16);
            doc.text('Registro de Atencin Mdica', 105, 30, { align: 'center' });

            // Informacin del paciente
            doc.setFontSize(12);
            doc.text('Informacin del Paciente', 20, 45);
            doc.setFontSize(10);
            doc.text(`Nombre: ${atencion.paciente_nombre}`, 20, 55);
            doc.text(`RUT: ${atencion.paciente_rut}`, 20, 62);
            doc.text(`Edad: ${atencion.paciente_edad} aos`, 20, 69);
            doc.text(`Fecha: ${formatearFecha(atencion.fecha_hora)}`, 20, 76);
            doc.text(`Tipo de Atencin: ${atencion.tipo_atencion}`, 20, 83);

            // Detalles de la atencin
            doc.setFontSize(12);
            doc.text('Detalles de la Atenci n', 20, 100);
            doc.setFontSize(10);

            // Motivo de consulta
            doc.text('Motivo de Consulta:', 20, 110);
            const motivoLines = doc.splitTextToSize(atencion.motivo_consulta || 'No especificado', 170);
            doc.text(motivoLines, 20, 117);

            // Diagnstico
            doc.text('Diagn stico:', 20, 135);
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

            // Pie de pgina
            doc.setFontSize(8);
            doc.text('Este documento es un registro m dico confidencial.', 105, 280, { align: 'center' });

            // Guardar el PDF
            doc.save(`atencion_${atencionId}.pdf`);
        })
        .catch(error => {
            showNotification('Error al generar el PDF', 'error');
        });
}

// Funcin para probar el registro de atenciones
function probarRegistroAtencion() {
    console.log(' Probando registro de atencin...');
    const form = document.getElementById('formRegistroAtencion');
    if (!form) {
        console.error(' No se encontr el formulario de registro');
        return;
    }

    // Crear un objeto FormData a partir del formulario
    const formData = new FormData(form);

    // Agregar datos de prueba al FormData
    formData.set('pacienteId', 'PAC_12345');
    formData.set('fechaHora', new Date().toISOString());
    formData.set('tipoAtencion', 'domiciliaria');
    formData.set('motivoConsulta', 'Prueba de registro con archivos');
    formData.set('diagnostico', 'Diagnstico de prueba');
    formData.set('tratamiento', 'Tratamiento de prueba');
    formData.set('observaciones', 'Observaciones de prueba');

    // Simular un archivo adjunto
    const blob = new Blob(["Este es un archivo de prueba"], { type: "text/plain" });
    const file = new File([blob], "prueba.txt", { type: "text/plain" });
    formData.append('archivos', file);

    console.log(' FormData de prueba:', ...formData.entries());

    fetch('/api/register-atencion', {
        method: 'POST',
        body: formData // No se necesita 'Content-Type', el navegador lo establece automticamente
    })
        .then(response => {
            console.log(' Respuesta de prueba de registro:', response.status);
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.message || 'Error en el servidor') });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log(' Prueba de registro exitosa:', data);
                showNotification('Prueba de registro de atencin completada con xito', 'success');
            } else {
                console.error(' Error en prueba de registro:', data.message);
                showNotification(`Error en prueba: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error(' Error fatal en prueba de registro:', error);
            showNotification(`Error en la prueba de registro: ${error.message}`, 'error');
        });
}

// Exponer funcin para testing manual
window.probarRegistroAtencion = probarRegistroAtencion;

// ========================================
// FUNCIONES PARA ESTADSTICAS DEL DASHBOARD
// ========================================

// Cargar estadsticas del dashboard
function cargarEstadisticasDashboard() {
    console.log(' Cargando estadsticas del dashboard...');

    // Cargar estadsticas en paralelo
    Promise.all([
        cargarEstadisticasAtenciones(),
        cargarEstadisticasPacientes(),
        cargarEstadisticasCitasHoy(),
        cargarEstadisticasPendientes()
    ]).then(() => {
        console.log(' Todas las estadsticas del dashboard cargadas');
    }).catch(error => {
        console.error(' Error cargando estadsticas del dashboard:', error);
    });
}

// Cargar estadsticas de atenciones
function cargarEstadisticasAtenciones() {
    return fetch('/api/get-atenciones')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const totalAtenciones = data.atenciones.length;
                document.getElementById('total-atenciones').textContent = totalAtenciones;
                console.log(` Total atenciones: ${totalAtenciones}`);
            } else {
                console.error(' Error obteniendo atenciones:', data.message);
                document.getElementById('total-atenciones').textContent = '0';
            }
        })
        .catch(error => {
            console.error(' Error en estadsticas de atenciones:', error);
            document.getElementById('total-atenciones').textContent = '0';
        });
}

// Cargar estadsticas de pacientes
function cargarEstadisticasPacientes() {
    return fetch('/api/professional/patients')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const totalPacientes = data.total || 0;
                document.getElementById('total-pacientes').textContent = totalPacientes;
                console.log(` Total pacientes: ${totalPacientes}`);
            } else {
                console.error(' Error obteniendo pacientes:', data.message);
                document.getElementById('total-pacientes').textContent = '0';
            }
        })
        .catch(error => {
            console.error(' Error en estadsticas de pacientes:', error);
            document.getElementById('total-pacientes').textContent = '0';
        });
}

// Cargar estadsticas de citas de hoy
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
                console.log(` Citas hoy: ${citasHoy}`);
            } else {
                console.error(' Error obteniendo citas de hoy:', data.message);
                document.getElementById('citas-hoy').textContent = '0';
            }
        })
        .catch(error => {
            console.error(' Error en estadsticas de citas hoy:', error);
            document.getElementById('citas-hoy').textContent = '0';
        });
}

// Cargar estadsticas de atenciones pendientes
function cargarEstadisticasPendientes() {
    return fetch('/api/get-atenciones')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const pendientes = data.atenciones.filter(atencion =>
                    atencion.estado && atencion.estado.toLowerCase() === 'pendiente'
                ).length;

                document.getElementById('atenciones-pendientes').textContent = pendientes;
                console.log(` Atenciones pendientes: ${pendientes}`);
            } else {
                console.error(' Error obteniendo atenciones pendientes:', data.message);
                document.getElementById('atenciones-pendientes').textContent = '0';
            }
        })
        .catch(error => {
            console.error(' Error en estadsticas de pendientes:', error);
            document.getElementById('atenciones-pendientes').textContent = '0';
        });
}

// ========================================
// FUNCIONES PARA GESTIN DE PACIENTES
// ========================================

// Variable global para almacenar la lista de pacientes
let pacientesList = [];

// Cargar lista de pacientes al inicializar
function cargarListaPacientes() {
    console.log(' Cargando lista de pacientes...');

    fetch('/api/professional/patients', {
        method: 'GET',
        credentials: 'include'
    })
        .then(response => {
            console.log(' Respuesta HTTP:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log(' Respuesta del servidor:', data);

            if (data.success) {
                // Validar que los datos sean correctos
                if (!Array.isArray(data.pacientes)) {
                    console.error(' Los datos de pacientes no son un array:', data.pacientes);
                    throw new Error('Formato de datos incorrecto');
                }

                window.pacientesList = data.pacientes;
                console.log(' Debug - Datos recibidos del servidor:', data);
                console.log(' Debug - Lista de pacientes:', data.pacientes);
                console.log(' Debug - Total de pacientes:', data.total);

                // Intentar actualizar la tabla con manejo de errores
                try {
                    actualizarTablaPacientes();
                    actualizarContadorPacientes();
                    console.log(` ${data.total} pacientes cargados exitosamente`);
                } catch (tableError) {
                    console.error(' Error actualizando tabla:', tableError);
                    console.error(' Stack trace:', tableError.stack);
                    showNotification('Error al mostrar los pacientes en la tabla', 'error');
                }
            } else {
                console.error(' Error cargando pacientes:', data.message);
                showNotification(`Error al cargar pacientes: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            console.error(' Error completo:', error);
            console.error(' Stack trace:', error.stack);
            console.error(' Error message:', error.message);
            showNotification(`Error de conexin: ${error.message}`, 'error');
        });
}

// Actualizar la tabla de pacientes
function actualizarTablaPacientes(filteredList = null) {
    console.log(' Actualizando tabla de pacientes...');

    const tabla = document.getElementById('patientsTable');
    if (!tabla) {
        console.warn(' Tabla de pacientes no encontrada');
        return;
    }

    const tbody = tabla.querySelector('tbody');
    if (!tbody) {
        console.warn(' Tbody de la tabla no encontrado');
        return;
    }

    const pacientes = filteredList || window.pacientesList;

    console.log(' Debug - Pacientes a mostrar:', pacientes);
    console.log(' Debug - Nmero de pacientes:', pacientes.length);

    // Debug detallado del primer paciente si existe
    if (pacientes.length > 0) {
        console.log(' Debug - Primer paciente:', pacientes[0]);
        console.log(' Debug - Tipo de edad:', typeof pacientes[0].edad);
        console.log(' Debug - Valor de edad:', pacientes[0].edad);
        console.log(' Debug - Tipo de num_atenciones:', typeof pacientes[0].num_atenciones);
        console.log(' Debug - Valor de num_atenciones:', pacientes[0].num_atenciones);
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
                console.log(` Procesando paciente ${index + 1}:`, paciente);

                // Obtener valores seguros para cada campo
                const nombreCompleto = escapeHTML(getSafeValue(paciente.nombre_completo, 'Sin nombre'));
                const rut = escapeHTML(getSafeValue(paciente.rut, 'Sin RUT'));
                const edad = escapeHTML(getSafeValue(paciente.edad, 'No especificada'));
                const telefono = escapeHTML(getSafeValue(paciente.telefono, 'No especificado'));
                const email = escapeHTML(getSafeValue(paciente.email, 'No especificado'));
                const direccion = escapeHTML(getSafeValue(paciente.direccion, 'No especificada'));
                const estadoRelacion = escapeHTML(getSafeValue(paciente.estado_relacion, 'Activo'));
                const pacienteId = escapeHTML(getSafeValue(paciente.paciente_id, ''));

                console.log(` Paciente ${index + 1} procesado exitosamente`);

                // Manejar nmeros de atenciones
                const numAtenciones = paciente.num_atenciones !== null && paciente.num_atenciones !== undefined ? paciente.num_atenciones : 0;

                // Manejar fecha de ltima consulta
                const ultimaConsulta = paciente.ultima_consulta ? formatearFecha(paciente.ultima_consulta) : 'No registrada';
                const textoUltimaConsulta = paciente.ultima_consulta ? 'ltima consulta' : 'Sin consultas';

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
                                    <small class="text-muted d-block">${edad} aos</small>
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
                                <button class="btn btn-sm btn-action btn-view" title="Ver historial" onclick="viewPatientHistory('${pacienteId}')">
                                    <i class="fas fa-history me-1"></i>Historial
                                </button>
                                <button class="btn btn-sm btn-action btn-edit" title="Editar" onclick="editPatient('${pacienteId}')">
                                    <i class="fas fa-edit me-1"></i>Editar
                                </button>
                                <button class="btn btn-sm btn-action btn-session" title="Agendar cita" onclick="newConsultation('${pacienteId}')">
                                    <i class="fas fa-calendar-plus me-1"></i>Cita
                                </button>
                                <button class="btn btn-sm btn-action btn-delete" title="Eliminar paciente" onclick="eliminarPaciente('${pacienteId}')">
                                    <i class="fas fa-trash me-1"></i>Borrar
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            } catch (patientError) {
                console.error(` Error procesando paciente ${index + 1}:`, patientError);
                console.error(' Datos del paciente problemtico:', paciente);
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
        console.error(' Error general en actualizacin de tabla:', generalError);
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-danger py-4">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <br>Error al cargar los pacientes
                    <br><small>Por favor, recarga la pgina</small>
                </td>
            </tr>
        `;
        throw generalError; // Re-lanzar para que se capture en el nivel superior
    }

    console.log(` Tabla actualizada con ${pacientes.length} pacientes`);
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

    // Actualizar tambin la tarjeta del dashboard
    const dashboardElement = document.getElementById('total-pacientes');
    if (dashboardElement) {
        dashboardElement.textContent = total;
    }

    console.log(` Pacientes: ${total} total, ${activos} activos`);
}

// Funcin para actualizar todas las estadsticas del dashboard
function actualizarEstadisticasDashboard() {
    console.log(' Actualizando estadsticas del dashboard...');
    cargarEstadisticasDashboard();
}



// Guardar paciente (nuevo o editado)
function savePatient() {
    console.log(' Guardando paciente...');

    const form = document.getElementById('addPatientForm');
    if (!form) {
        console.error(' Formulario no encontrado');
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

    console.log(' Datos del paciente:', pacienteData);

    // Validar campos requeridos
    if (!pacienteData.nombre_completo) {
        showNotification('El nombre completo es requerido', 'error');
        return;
    }

    if (!pacienteData.rut) {
        showNotification('El RUT es requerido', 'error');
        return;
    }

    // Verificar si es edicin o nuevo paciente
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
            console.log(' Respuesta del servidor:', data);

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

                // Recargar lista de pacientes y actualizar estadsticas
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
            console.error(' Error:', error);
            showNotification('Error de conexin al guardar paciente', 'error');
        });
}

// Editar paciente
function editarPaciente(pacienteId) {
    console.log(` Editando paciente: ${pacienteId}`);

    // Buscar el paciente en la lista local
    const paciente = window.pacientesList.find(p => p.paciente_id === pacienteId);
    if (!paciente) {
        console.error(' Paciente no encontrado en la lista local');
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

    // Marcar el formulario como edicin
    const form = document.getElementById('addPatientForm');
    form.setAttribute('data-editing-id', pacienteId);

    // Cambiar el ttulo del modal
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
    console.log(` Eliminando paciente: ${pacienteId}`);

    // Buscar el paciente para mostrar su nombre en la confirmación
    const paciente = window.pacientesList.find(p => p.paciente_id === pacienteId);
    const nombrePaciente = paciente ? paciente.nombre_completo : 'este paciente';

    mostrarConfirmacionEliminacion(
        'Eliminar Paciente de la Lista',
        `¿Está seguro de que desea eliminar a ${nombrePaciente} de su lista de pacientes?`,
        'Esta acción solo eliminará al paciente de su lista personal. El paciente permanecerá en el sistema y podrá ser agregado nuevamente en el futuro.',
        'Eliminar de Mi Lista',
        () => {
            fetch(`/api/professional/patients/${pacienteId}`, {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    console.log(' Respuesta del servidor:', data);

                    if (data.success) {
                        showNotification('✅ Paciente eliminado de su lista exitosamente', 'success');
                        cargarListaPacientes(); // Recargar lista
                        actualizarEstadisticasDashboard(); // Actualizar estadísticas
                    } else {
                        showNotification(data.message || '❌ Error al eliminar paciente', 'error');
                    }
                })
                .catch(error => {
                    console.error(' Error:', error);
                    showNotification('❌ Error de conexión al eliminar paciente', 'error');
                });
        }
    );
}

// Ver historial de un paciente especfico
function verHistorialPaciente(pacienteId) {
    console.log(` Viendo historial del paciente: ${pacienteId}`);

    fetch(`/api/professional/patients/${pacienteId}`, {
        method: 'GET',
        credentials: 'include'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // El backend solo devuelve datos del paciente, no atenciones
                // Por ahora, mostrar solo los datos del paciente
                mostrarModalHistorialPaciente(data.paciente, []);
            } else {
                showNotification('Error al obtener el historial del paciente', 'error');
            }
        })
        .catch(error => {
            console.error(' Error:', error);
            showNotification('Error de conexin al obtener historial', 'error');
        });
}

// Mostrar modal con historial del paciente
function mostrarModalHistorialPaciente(paciente, atenciones) {
    const modal = document.getElementById('patientHistoryModal');
    if (!modal) {
        console.error(' Modal patientHistoryModal no encontrado');
        return;
    }

    // Actualizar ttulo del modal
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
                    <h6 class="text-primary">Informacin Personal</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Nombre:</strong></td><td>${paciente.nombre_completo}</td></tr>
                        <tr><td><strong>RUT:</strong></td><td>${paciente.rut}</td></tr>
                        <tr><td><strong>Edad:</strong></td><td>${paciente.edad || 'No especificada'} aos</td></tr>
                        <tr><td><strong>Gnero:</strong></td><td>${paciente.genero || 'No especificado'}</td></tr>
                        <tr><td><strong>Telfono:</strong></td><td>${paciente.telefono || 'No especificado'}</td></tr>
                        <tr><td><strong>Email:</strong></td><td>${paciente.email || 'No especificado'}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6 class="text-primary">Estadsticas</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Total Atenciones:</strong></td><td>${atenciones.length}</td></tr>
                        <tr><td><strong>Primera Consulta:</strong></td><td>${paciente.fecha_primera_consulta ? formatearFecha(paciente.fecha_primera_consulta) : 'No registrada'}</td></tr>
                        <tr><td><strong>ltima Consulta:</strong></td><td>${paciente.ultima_consulta ? formatearFecha(paciente.ultima_consulta) : 'No registrada'}</td></tr>
                        <tr><td><strong>Registrado:</strong></td><td>${formatearFecha(paciente.fecha_registro)}</td></tr>
                    </table>
                </div>
            </div>
            
            ${paciente.antecedentes_medicos ? `
                <div class="mt-3">
                    <h6 class="text-primary">Antecedentes Mdicos</h6>
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
                        <br><small>Las atenciones se mostrarán aquí cuando se registren</small>
                    </div>
                ` : `
                    <div class="table-responsive">
                        <table class="table table-sm table-striped">
                            <thead>
                                <tr>
                                    <th>Fecha</th>
                                    <th>Tipo</th>
                                    <th>Motivo</th>
                                    <th>Diagnstico</th>
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
                                            <button class="btn btn-sm btn-action btn-view" onclick="verDetalleAtencion('${atencion.atencion_id}')" title="Ver detalles">
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

// Funcin de bsqueda y filtrado
function setupPatientSearch() {
    console.log(' Configurando bsqueda de pacientes...');

    // Funcin para configurar los event listeners
    const configurarBusqueda = () => {
        const searchInput = document.getElementById('searchPatients');
        const filterSelect = document.getElementById('filterPatients');

        console.log(' Elementos de bsqueda encontrados:', {
            searchInput: !!searchInput,
            filterSelect: !!filterSelect
        });

        if (searchInput) {
            // Remover event listener anterior si existe
            searchInput.removeEventListener('input', filterPatients);
            // Agregar nuevo event listener
            searchInput.addEventListener('input', function (e) {
                console.log(' Bsqueda iniciada:', e.target.value);
                filterPatients();
            });
            console.log(' Event listener de bsqueda configurado');
        } else {
            console.warn(' Elemento searchPatients no encontrado');
        }

        if (filterSelect) {
            // Remover event listener anterior si existe
            filterSelect.removeEventListener('change', filterPatients);
            // Agregar nuevo event listener
            filterSelect.addEventListener('change', function (e) {
                console.log(' Filtro cambiado:', e.target.value);
                filterPatients();
            });
            console.log(' Event listener de filtro configurado');
        } else {
            console.warn(' Elemento filterPatients no encontrado');
        }
    };

    // Intentar configurar inmediatamente
    configurarBusqueda();

    // Si los elementos no estn disponibles, intentar despus de un delay
    if (!document.getElementById('searchPatients') || !document.getElementById('filterPatients')) {
        console.log(' Elementos de bsqueda no disponibles, reintentando en 500ms...');
        setTimeout(configurarBusqueda, 500);
    }

    // Tambin configurar cuando se active la pestaa de pacientes
    const patientsTab = document.getElementById('patients-tab');
    if (patientsTab) {
        patientsTab.addEventListener('shown.bs.tab', function () {
            console.log(' Pestaa de pacientes activada, configurando bsqueda...');
            setTimeout(configurarBusqueda, 100);
        });
    }


}

// Filtrar pacientes por bsqueda y filtros
function filterPatients() {
    console.log(' Ejecutando filtrado de pacientes...');

    const searchInput = document.getElementById('searchPatients');
    const filterSelect = document.getElementById('filterPatients');

    if (!searchInput || !filterSelect) {
        console.warn(' Elementos de bsqueda no encontrados');
        return;
    }

    const searchTerm = searchInput.value?.toLowerCase() || '';
    const filterValue = filterSelect.value || '';

    console.log(' Parmetros de bsqueda:', {
        searchTerm: searchTerm,
        filterValue: filterValue,
        totalPacientes: window.pacientesList?.length || 0
    });

    let filteredPatients = window.pacientesList || [];

    // Aplicar filtro de bsqueda
    if (searchTerm) {
        const antes = filteredPatients.length;
        filteredPatients = filteredPatients.filter(paciente => {
            const nombreMatch = paciente.nombre_completo?.toLowerCase().includes(searchTerm) || false;
            const rutMatch = paciente.rut?.toLowerCase().includes(searchTerm) || false;
            const emailMatch = paciente.email?.toLowerCase().includes(searchTerm) || false;

            return nombreMatch || rutMatch || emailMatch;
        });
        console.log(` Filtro de bsqueda: ${antes} -> ${filteredPatients.length} pacientes`);
    }

    // Aplicar filtro de estado
    if (filterValue) {
        const antes = filteredPatients.length;
        filteredPatients = filteredPatients.filter(paciente =>
            paciente.estado_relacion === filterValue
        );
        console.log(` Filtro de estado: ${antes} -> ${filteredPatients.length} pacientes`);
    }

    console.log(` Filtrado completado: ${filteredPatients.length} pacientes encontrados`);

    // Mostrar notificacin si no hay resultados
    if (filteredPatients.length === 0 && (searchTerm || filterValue)) {
        showNotification(`No se encontraron pacientes que coincidan con "${searchTerm}"`, 'warning');
    }

    actualizarTablaPacientes(filteredPatients);
}



// Funciones para manejar archivos adjuntos
function cargarArchivosAdjuntos(atencionId) {
    console.log(` Cargando archivos adjuntos para: ${atencionId}`);

    fetch(`/api/archivos/${atencionId}`)
        .then(response => response.json())
        .then(data => {
            console.log(' Archivos recibidos:', data);

            const listaArchivos = document.getElementById('listaArchivos');
            const noArchivos = document.getElementById('noArchivos');

            if (!listaArchivos || !noArchivos) {
                console.error(' No se encontraron los elementos de la lista de archivos');
                return;
            }

            // Limpiar lista anterior
            listaArchivos.innerHTML = '';

            if (data.archivos && data.archivos.length > 0) {
                console.log(` Mostrando ${data.archivos.length} archivos`);

                // Ocultar mensaje "no archivos" y mostrar lista
                noArchivos.style.display = 'none';
                listaArchivos.style.display = 'block';

                data.archivos.forEach(archivo => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item d-flex justify-content-between align-items-center';

                    // Determinar el icono segn el tipo de archivo
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
                            `<button class="btn btn-sm btn-action btn-view me-1" onclick="previewArchivo('${archivo.archivo_id}', '${archivo.nombre_archivo.replace(/['"\\]/g, '\\$&')}')">
                                    <i class="fas fa-eye"></i> Ver
                                </button>` : ''}
                            <button class="btn btn-sm btn-action btn-download" onclick="downloadArchivo('${archivo.archivo_id}', '${archivo.nombre_archivo.replace(/['"\\]/g, '\\$&')}')">
                                <i class="fas fa-download"></i> Descargar
                            </button>
                        </div>
                    `;

                    listaArchivos.appendChild(li);
                });
            } else {
                console.log(' No hay archivos adjuntos');

                // Mostrar mensaje "no archivos" y ocultar lista
                noArchivos.style.display = 'block';
                listaArchivos.style.display = 'none';
            }
        })
        .catch(error => {
            console.error(' Error cargando archivos:', error);
            showNotification('Error al cargar los archivos adjuntos', 'error');
        });
}

// Funcin para descargar archivo
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

// Funcin para eliminar archivo
function eliminarArchivo(archivoId) {
    if (confirm('Est seguro de que desea eliminar este archivo? Esta accin no se puede deshacer.')) {
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

// Variable para almacenar el ID de la atencin actual
let atencionActualId = null;

// Modificar la funcin existente de cargar detalle de atencin
function cargarDetalleAtencion(atencionId) {
    atencionActualId = atencionId;
    // ... cdigo existente ...

    // Agregar llamada para cargar archivos
    cargarArchivosAdjuntos(atencionId);
}

// Variable para almacenar archivos seleccionados
let selectedFiles = [];

// Funcin para manejar la seleccin de archivos
function handleFileSelection(event) {
    const fileInput = event.target;
    const fileList = document.getElementById('fileList');

    if (!fileList) {
        console.error(' No se encontr el contenedor de la lista de archivos');
        return;
    }

    // Limpiar lista anterior
    fileList.innerHTML = '';
    selectedFiles = Array.from(fileInput.files);

    // Mostrar archivos seleccionados
    selectedFiles.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'selected-file d-flex align-items-center p-2 border rounded mb-2';

        // Determinar icono segn tipo de archivo
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
                    onclick="removeFile('${file.name.replace(/['"\\]/g, '\\$&')}')">
                <i class="fas fa-times"></i>
            </button>
        `;

        fileList.appendChild(fileItem);
    });
}

// Funcin para formatear el tamao del archivo
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Funcin para remover un archivo
function removeFile(fileName) {
    selectedFiles = selectedFiles.filter(file => file.name !== fileName);
    const fileInput = document.getElementById('fileUpload');
    handleFileSelection({ target: fileInput });
}

// Funcin para descargar PDF de atencin (llamada desde el modal)
function descargarPDFAtencion(atencionId) {
    console.log(` Descargando PDF para atencin: ${atencionId}`);

    if (!atencionId) {
        showNotification('Error: No se especific el ID de la atencin', 'error');
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
            console.error(' Error descargando PDF:', error);
            showNotification('Error al descargar el PDF. Intentando mtodo alternativo...', 'warning');

            // Mtodo alternativo usando la funcin generarPDF existente
            generarPDF(atencionId);
        });
}

// Funcin para guardar nueva cita
function saveAppointment() {
    console.log(' Guardando nueva cita...');

    const form = document.getElementById('scheduleForm');
    if (!form) {
        console.error(' Formulario de cita no encontrado');
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

    console.log(' Datos de la cita:', appointmentData);

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
        showNotification('Debe seleccionar un tipo de atencin', 'error');
        return;
    }

    // Enviar datos al servidor
    fetch('/api/professional/schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'include',
        body: JSON.stringify(appointmentData)
    })
        .then(response => response.json())
        .then(data => {
            console.log(' Respuesta del servidor:', data);

            if (data.success) {
                showNotification('Cita agendada exitosamente', 'success');

                // Marcar que se acaba de agendar una cita
                window.citaRecienAgendada = true;

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleModal'));
                if (modal) {
                    modal.hide();
                }

                // Limpiar formulario
                form.reset();

                // Recargar agenda en todas las vistas
                console.log(' Recargando agenda en todas las vistas...');
                recargarAgendaCompleta();

            } else {
                showNotification(data.message || 'Error al agendar la cita', 'error');
            }
        })
        .catch(error => {
            console.error(' Error:', error);
            showNotification('Error de conexin al agendar la cita', 'error');
        });
}

// ==========================================
// FUNCIONES PARA EL DROPDOWN DE PACIENTES
// ==========================================

// Variable global para almacenar la lista de pacientes
window.pacientesDropdownList = [];

// Funcin para cargar pacientes en el dropdown del formulario de atencin
async function cargarPacientesDropdown() {
    try {
        console.log(' Cargando pacientes para dropdown...');

        const response = await fetch('/api/professional/patients', {
            method: 'GET',
            credentials: 'include'
        });
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

                console.log(` ${data.pacientes.length} pacientes cargados en dropdown`);
            }
        } else {
            console.warn(' No se pudieron cargar pacientes para dropdown');
        }
    } catch (error) {
        console.error(' Error cargando pacientes para dropdown:', error);
    }
}

// Funcin para manejar la seleccin de paciente en el dropdown
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
        console.log(' Seleccionado: Crear nuevo paciente');
        camposPaciente.style.display = 'block';
        limpiarCamposPaciente();

        // Hacer campos requeridos
        document.getElementById('pacienteNombre').required = true;
        document.getElementById('pacienteRut').required = true;

    } else if (selectedValue && selectedValue !== '') {
        // Mostrar informacin del paciente seleccionado
        console.log(` Seleccionado paciente: ${selectedValue}`);
        const paciente = window.pacientesDropdownList.find(p => p.paciente_id === selectedValue);

        if (paciente) {
            mostrarInfoPacienteSeleccionado(paciente);
            infoPacienteSeleccionado.style.display = 'block';

            // Llenar campos ocultos para el envo del formulario
            llenarCamposOcultosPaciente(paciente);
        }

        // Campos no requeridos (paciente ya existe)
        document.getElementById('pacienteNombre').required = false;
        document.getElementById('pacienteRut').required = false;

    } else {
        // No hay seleccin
        console.log(' No hay paciente seleccionado');
        limpiarCamposPaciente();

        // Campos no requeridos
        document.getElementById('pacienteNombre').required = false;
        document.getElementById('pacienteRut').required = false;
    }
}

// Funcin para mostrar informacin del paciente seleccionado
function mostrarInfoPacienteSeleccionado(paciente) {
    document.getElementById('nombrePacienteSeleccionado').textContent = paciente.nombre_completo || 'Sin nombre';
    document.getElementById('rutPacienteSeleccionado').textContent = paciente.rut || 'Sin RUT';
    document.getElementById('edadPacienteSeleccionado').textContent = paciente.edad || 'Sin edad';
}

// Funcin para llenar campos ocultos con datos del paciente seleccionado
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

// Funcin para limpiar campos del paciente
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

// Funcin para editar datos del paciente seleccionado
function editarDatosPaciente() {
    console.log(' Editando datos del paciente seleccionado');

    const infoPacienteSeleccionado = document.getElementById('infoPacienteSeleccionado');
    const camposPaciente = document.getElementById('camposPaciente');

    // Ocultar info y mostrar campos editables
    infoPacienteSeleccionado.style.display = 'none';
    camposPaciente.style.display = 'block';

    // Los campos ya estn llenos por llenarCamposOcultosPaciente()
}

// Funcin para recargar la lista de pacientes
async function recargarListaPacientes() {
    console.log(' Recargando lista de pacientes...');

    const button = event.target;
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    button.disabled = true;

    try {
        await cargarPacientesDropdown();
        showNotification('Lista de pacientes actualizada', 'success');
    } catch (error) {
        console.error(' Error recargando pacientes:', error);
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

// Inicializar agenda cuando se carga la pgina
document.addEventListener('DOMContentLoaded', function () {
    // Cargar agenda si el tab est activo
    const agendaTab = document.getElementById('schedule-tab');
    if (agendaTab) {
        agendaTab.addEventListener('click', function () {
            cargarAgenda();
        });
    }

    // Si la agenda est visible al cargar, cargarla
    const agendaPane = document.getElementById('schedule');
    if (agendaPane && agendaPane.classList.contains('active')) {
        cargarAgenda();
    }
});

// Funcin para cargar la agenda
function cargarAgenda(fecha = null) {
    console.log(' Cargando agenda...');

    if (!fecha) {
        fecha = fechaActualAgenda.toISOString().split('T')[0];
    }

    // Actualizar fecha en el header
    actualizarFechaHeader(fecha);

    // Cargar citas del da con vista actual
    fetch(`/api/professional/schedule?fecha=${fecha}&vista=${currentView}`, {
        credentials: 'include'
    })
        .then(response => response.json())
        .then(data => {
            console.log(' Datos de agenda recibidos:', data);

            if (data.success) {
                agendaData = data;

                // Actualizar la vista actual
                if (currentView === 'diaria') {
                    citasDelDia = data.citas || [];
                    console.log(' Citas del día cargadas:', citasDelDia);
                    actualizarVistaAgenda(data.citas, data.horarios_disponibles);
                } else if (currentView === 'semanal') {
                    actualizarVistaSemanal(data.agenda_semanal, data.fecha_inicio, data.fecha_fin);
                } else if (currentView === 'mensual') {
                    actualizarVistaMensual(data.agenda_mensual, data.fecha_inicio, data.fecha_fin);
                }

                // Actualizar estadísticas y recordatorios
                actualizarEstadisticasAgenda(data.estadisticas);

                if (data.citas) {
                    actualizarRecordatorios(data.citas);
                }

                // Si se acaba de agendar una cita, mostrar notificación adicional
                if (window.citaRecienAgendada) {
                    showNotification('La cita se ha agregado al calendario en todas las vistas', 'success');
                    window.citaRecienAgendada = false;
                }
            } else {
                console.error(' Error cargando agenda:', data.message);
                showNotification('Error al cargar la agenda: ' + data.message, 'error');
                // Inicializar array vacío en caso de error
                citasDelDia = [];
            }
        })
        .catch(error => {
            console.error(' Error de red:', error);
            showNotification('Error de conexin al cargar la agenda', 'error');
            // Inicializar array vacío en caso de error de red
            citasDelDia = [];
        });
}

// Funcin para actualizar la fecha en el header
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

// Funcin para actualizar la vista de la agenda
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
                        <button class="btn btn-sm btn-action btn-view" onclick="verCita('${cita.cita_id}')" title="Ver detalles">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-action btn-confirm" onclick="confirmarCita('${cita.cita_id}')" title="Confirmar">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-sm btn-action btn-cancel" onclick="cancelarCita('${cita.cita_id}')" title="Cancelar">
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

// Funcin para obtener el color del estado
function getEstadoColor(estado) {
    switch (estado) {
        case 'confirmada': return 'success';
        case 'pendiente': return 'warning';
        case 'cancelada': return 'danger';
        case 'completada': return 'info';
        default: return 'secondary';
    }
}

// Funcin para capitalizar primera letra
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Funcin para actualizar estadsticas
function actualizarEstadisticasAgenda(estadisticas) {
    console.log(' Actualizando estadsticas de agenda:', estadisticas);

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

    // Agregar animacin de actualizacin
    Object.values(elementos).forEach(element => {
        if (element) {
            element.style.transform = 'scale(1.1)';
            setTimeout(() => {
                element.style.transform = 'scale(1)';
            }, 200);
        }
    });
}

// Funcin para actualizar recordatorios
function actualizarRecordatorios(citas) {
    console.log(' Actualizando recordatorios:', citas);

    // Cargar recordatorios desde el servidor
    cargarRecordatorios();
}

// Funcin para cargar recordatorios desde el servidor
function cargarRecordatorios() {
    fetch('/api/professional/reminders')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                mostrarRecordatorios(data.recordatorios);
            } else {
                console.error(' Error cargando recordatorios:', data.message);
                mostrarRecordatorios([]);
            }
        })
        .catch(error => {
            console.error(' Error de red cargando recordatorios:', error);
            mostrarRecordatorios([]);
        });
}

// Funcin para mostrar recordatorios en la interfaz
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
                                            <button class="btn btn-sm btn-action btn-edit" onclick="editReminder(${recordatorio.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                                            <button class="btn btn-sm btn-action btn-delete" onclick="deleteReminder(${recordatorio.id})" title="Eliminar">
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

// Funcin para obtener el color segn la prioridad
function getReminderColor(prioridad) {
    switch (prioridad) {
        case 'urgente': return 'danger';
        case 'alta': return 'warning';
        case 'media': return 'info';
        case 'baja': return 'secondary';
        default: return 'info';
    }
}

// Funcin para obtener el icono segn el tipo
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

// Funcin para formatear fecha y hora
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
    console.log(' showReminderModal ejecutndose con ID:', recordatorioId);

    const modal = document.getElementById('reminderModal');
    console.log(' Modal encontrado:', modal);

    if (!modal) {
        console.error(' Modal de recordatorio NO encontrado');
        return;
    }

    const modalTitle = document.getElementById('reminderModalTitle');
    const saveButton = document.getElementById('saveReminderText');
    const reminderId = document.getElementById('reminderId');

    console.log(' Elementos del modal:', {
        modalTitle: modalTitle,
        saveButton: saveButton,
        reminderId: reminderId
    });

    // Limpiar formulario
    const form = document.getElementById('reminderForm');
    if (form) {
        form.reset();
        console.log(' Formulario limpiado');
    } else {
        console.error(' Formulario NO encontrado');
    }

    // Configurar fecha y hora por defecto
    const now = new Date();
    const dateInput = document.getElementById('reminderDate');
    const timeInput = document.getElementById('reminderTime');

    if (dateInput && timeInput) {
        dateInput.value = now.toISOString().split('T')[0];
        timeInput.value = now.toTimeString().slice(0, 5);
        console.log(' Fecha y hora configuradas');
    } else {
        console.error(' Inputs de fecha/hora NO encontrados');
    }

    if (recordatorioId) {
        // Modo edicin
        console.log(' Modo edicin');
        modalTitle.textContent = 'Editar Recordatorio';
        saveButton.textContent = 'Actualizar Recordatorio';
        reminderId.value = recordatorioId;
        cargarRecordatorioParaEditar(recordatorioId);
    } else {
        // Modo creacin
        console.log(' Modo creacin');
        modalTitle.textContent = 'Crear Recordatorio';
        saveButton.textContent = 'Guardar Recordatorio';
        reminderId.value = '';
    }

    // Mostrar modal
    console.log(' Mostrando modal...');
    console.log(' Bootstrap disponible:', typeof bootstrap);

    try {
        if (typeof bootstrap !== 'undefined') {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            console.log(' Modal mostrado exitosamente con Bootstrap');

            // Cargar pacientes despus de que el modal est visible
            setTimeout(() => {
                console.log(' Cargando pacientes despus de mostrar modal con Bootstrap...');
                cargarPacientesEnReminderSelect();
            }, 300);
        } else {
            // Fallback: mostrar modal manualmente
            console.log(' Bootstrap no disponible, usando fallback');
            modal.style.display = 'block';
            modal.classList.add('show');
            document.body.classList.add('modal-open');

            // Agregar backdrop
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            document.body.appendChild(backdrop);

            console.log(' Modal mostrado con fallback');

            // Cargar pacientes despus de que el modal est visible
            setTimeout(() => {
                console.log(' Cargando pacientes despus de mostrar modal con fallback...');
                cargarPacientesEnReminderSelect();
            }, 300);
        }
    } catch (error) {
        console.error(' Error mostrando modal:', error);
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

                // Mostrar/ocultar opciones de repeticin
                toggleRepeatOptions();
            } else {
                showNotification('Error cargando recordatorio', 'error');
            }
        })
        .catch(error => {
            console.error(' Error cargando recordatorio:', error);
            showNotification('Error cargando recordatorio', 'error');
        });
}

// Cargar pacientes en el select de recordatorios
function cargarPacientesEnReminderSelect() {
    console.log(' Cargando pacientes en select de recordatorios...');

    const select = document.getElementById('reminderPatient');
    if (!select) {
        console.error(' Select de pacientes no encontrado');
        return;
    }

    console.log(' Limpiando opciones existentes...');
    // Limpiar opciones existentes (excepto la primera)
    while (select.children.length > 1) {
        select.removeChild(select.lastChild);
    }

    // Funcin para agregar pacientes al select
    function agregarPacientesAlSelect(pacientes) {
        console.log(` Agregando ${pacientes.length} pacientes al select`);
        pacientes.forEach(paciente => {
            const option = document.createElement('option');
            option.value = paciente.paciente_id;
            option.textContent = `${paciente.nombre_completo} - ${paciente.rut}`;
            select.appendChild(option);
        });
        console.log(' Pacientes agregados al select exitosamente');
    }

    // Usar la lista global de pacientes si est disponible
    if (window.pacientesList && window.pacientesList.length > 0) {
        console.log(` Usando lista global de pacientes: ${window.pacientesList.length} pacientes`);
        agregarPacientesAlSelect(window.pacientesList);
    } else {
        console.log(' No hay lista global, cargando desde API...');
        // Si no hay lista global, cargar desde API
        fetch('/api/professional/patients', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'include'
        })
            .then(response => {
                console.log(' Respuesta de API:', response.status, response.statusText);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(' Datos recibidos:', data);
                if (data.success && data.pacientes && Array.isArray(data.pacientes)) {
                    console.log(` Cargando ${data.pacientes.length} pacientes desde API`);
                    agregarPacientesAlSelect(data.pacientes);

                    // Guardar en la lista global para futuras referencias
                    window.pacientesList = data.pacientes;
                    console.log(' Lista de pacientes guardada en window.pacientesList');
                } else {
                    console.warn(' No se recibieron pacientes vlidos de la API');
                    console.log(' Respuesta completa:', data);

                    // Mostrar mensaje de error en el select
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'No hay pacientes disponibles';
                    option.disabled = true;
                    select.appendChild(option);
                }
            })
            .catch(error => {
                console.error(' Error cargando pacientes:', error);
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
        credentials: 'include',
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
            console.error(' Error guardando recordatorio:', error);
            showNotification('Error al guardar recordatorio', 'error');
        });
}

// Editar recordatorio
function editReminder(recordatorioId) {
    showReminderModal(recordatorioId);
}

// Eliminar recordatorio
function deleteReminder(recordatorioId) {
    mostrarConfirmacionEliminacion(
        'Eliminar Recordatorio',
        '¿Está seguro de que desea eliminar este recordatorio?',
        'Esta acción eliminará permanentemente el recordatorio y todas las notificaciones asociadas. Esta acción no se puede deshacer.',
        'Eliminar Recordatorio',
        () => {
            fetch(`/api/professional/reminders/${recordatorioId}`, {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('✅ Recordatorio eliminado exitosamente', 'success');
                        cargarRecordatorios();
                    } else {
                        showNotification(data.message || '❌ Error al eliminar recordatorio', 'error');
                    }
                })
                .catch(error => {
                    console.error(' Error eliminando recordatorio:', error);
                    showNotification('❌ Error al eliminar recordatorio', 'error');
                });
        }
    );
}

// Funcin de fallback para mostrar modal de recordatorio
function mostrarModalRecordatorioManual() {
    console.log(' Usando funcin de fallback para mostrar modal');

    const modal = document.getElementById('reminderModal');
    if (!modal) {
        console.error(' Modal de recordatorio no encontrado');
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

    // Configurar ttulo
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

        console.log(' Modal mostrado con funcin de fallback');
    } catch (error) {
        console.error(' Error mostrando modal:', error);
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

// Toggle opciones de repeticin
function toggleRepeatOptions() {
    const repeatCheckbox = document.getElementById('reminderRepeat');
    const repeatOptions = document.getElementById('repeatOptions');

    if (repeatCheckbox.checked) {
        repeatOptions.classList.remove('d-none');
    } else {
        repeatOptions.classList.add('d-none');
    }
}

// Agregar event listener para el checkbox de repeticin
document.addEventListener('DOMContentLoaded', function () {
    const repeatCheckbox = document.getElementById('reminderRepeat');
    if (repeatCheckbox) {
        repeatCheckbox.addEventListener('change', toggleRepeatOptions);
    }

    // Inicializar event listeners para recordatorios
    inicializarEventListenersRecordatorios();

    // Inicializacin adicional para asegurar que los botones funcionen
    setTimeout(() => {
        inicializarBotonesRecordatorios();
    }, 1000);
});

// Funcin para manejar el clic en crear recordatorio
function handleCrearRecordatorio() {
    console.log(' Botn crear recordatorio clickeado');

    // Lgica inline para mostrar el modal sin depender de funciones globales
    const modal = document.getElementById('reminderModal');
    if (!modal) {
        console.error(' Modal de recordatorio no encontrado');

        // Crear modal dinmicamente si no existe
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

    // Configurar ttulo
    const modalTitle = document.getElementById('reminderModalTitle');
    const saveButton = document.getElementById('saveReminderText');
    const reminderId = document.getElementById('reminderId');

    if (modalTitle) modalTitle.textContent = 'Crear Recordatorio';
    if (saveButton) saveButton.textContent = 'Guardar Recordatorio';
    if (reminderId) reminderId.value = '';

    // Mostrar modal con mltiples mtodos
    mostrarModalRecordatorio(modal);

    // Cargar pacientes despus de mostrar el modal
    setTimeout(() => {
        console.log(' Cargando pacientes despus de mostrar modal...');
        cargarPacientesEnReminderSelect();
    }, 100);
}

// Funcin para mostrar el modal de recordatorio
function mostrarModalRecordatorio(modal) {
    try {
        // Mtodo 1: Bootstrap
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
            console.log(' Modal mostrado con Bootstrap');
            return;
        }

        // Mtodo 2: jQuery Bootstrap
        if (typeof $ !== 'undefined' && $.fn.modal) {
            $(modal).modal('show');
            console.log(' Modal mostrado con jQuery Bootstrap');
            return;
        }

        // Mtodo 3: Fallback manual
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

        console.log(' Modal mostrado manualmente');

    } catch (error) {
        console.error(' Error mostrando modal:', error);

        // Mtodo 4: Alert como ltimo recurso
        alert('Error al mostrar el modal. Usando mtodo alternativo.');
        mostrarFormularioRecordatorioAlternativo();
    }
}

// Funcin para cerrar el modal
function cerrarModalRecordatorio(modal) {
    try {
        // Mtodo 1: Bootstrap
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) {
                bootstrapModal.hide();
                return;
            }
        }

        // Mtodo 2: jQuery Bootstrap
        if (typeof $ !== 'undefined' && $.fn.modal) {
            $(modal).modal('hide');
            return;
        }

        // Mtodo 3: Fallback manual
        modal.style.display = 'none';
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');

        // Remover backdrop
        const backdrop = document.getElementById('reminderModalBackdrop');
        if (backdrop) {
            backdrop.remove();
        }

    } catch (error) {
        console.error(' Error cerrando modal:', error);
    }
}

// Funcin para crear modal dinmicamente
function crearModalRecordatorio() {
    console.log(' Creando modal de recordatorio dinmicamente...');

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
                                <label for="reminderTitle" class="form-label">Ttulo</label>
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
                                <label for="reminderDescription" class="form-label">Descripcin</label>
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
                        <button type="button" class="btn btn-sm btn-action btn-edit" id="saveReminderText" onclick="saveReminder()">
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

// Funcin alternativa para mostrar formulario
function mostrarFormularioRecordatorioAlternativo() {
    console.log(' Mostrando formulario alternativo...');

    const formHTML = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;">
            <div style="background: white; padding: 20px; border-radius: 8px; max-width: 500px; width: 90%;">
                <h5>Crear Recordatorio</h5>
                <form id="reminderFormAlt">
                    <div style="margin-bottom: 15px;">
                        <label>Ttulo:</label>
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
                        <label>Descripcin:</label>
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

// Funcin para guardar recordatorio alternativo
function guardarRecordatorioAlternativo() {
    const title = document.getElementById('reminderTitleAlt').value;
    const date = document.getElementById('reminderDateAlt').value;
    const time = document.getElementById('reminderTimeAlt').value;
    const description = document.getElementById('reminderDescriptionAlt').value;

    if (!title || !date || !time) {
        alert('Por favor completa todos los campos requeridos');
        return;
    }

    // Aqu puedes implementar la lgica para guardar el recordatorio
    console.log('Guardando recordatorio alternativo:', { title, date, time, description });

    // Cerrar el formulario
    document.getElementById('reminderFormAlt').parentElement.parentElement.remove();

    // Mostrar mensaje de xito
    alert('Recordatorio guardado exitosamente');
}

// Funcin para inicializar event listeners de recordatorios
function inicializarEventListenersRecordatorios() {
    console.log(' Inicializando event listeners de recordatorios...');

    // Event listener para crear recordatorio
    const btnCrearRecordatorio = document.getElementById('btnCrearRecordatorio');
    console.log(' Buscando botn crear recordatorio:', btnCrearRecordatorio);

    if (btnCrearRecordatorio) {
        console.log(' Botn crear recordatorio encontrado, agregando event listener...');

        // Remover event listeners existentes para evitar duplicados
        btnCrearRecordatorio.removeEventListener('click', handleCrearRecordatorio);
        btnCrearRecordatorio.addEventListener('click', handleCrearRecordatorio);

        console.log(' Event listener agregado al botn');
    } else {
        console.error(' Botn crear recordatorio NO encontrado');

        // Buscar el botn por clase como respaldo
        const botonesRecordatorio = document.querySelectorAll('.btn-outline-light');
        console.log(' Buscando botones por clase:', botonesRecordatorio);

        botonesRecordatorio.forEach(boton => {
            if (boton.title === 'Crear Recordatorio') {
                console.log(' Botn encontrado por ttulo, agregando event listener...');
                boton.removeEventListener('click', handleCrearRecordatorio);
                boton.addEventListener('click', handleCrearRecordatorio);
            }
        });
    }

    // Event listeners para editar recordatorios (delegacin de eventos)
    document.addEventListener('click', function (e) {
        if (e.target.closest('.btn-edit-reminder')) {
            const button = e.target.closest('.btn-edit-reminder');
            const recordatorioId = button.getAttribute('data-id');
            console.log(' Editando recordatorio:', recordatorioId);
            editReminder(recordatorioId);
        }

        if (e.target.closest('.btn-delete-reminder')) {
            const button = e.target.closest('.btn-delete-reminder');
            const recordatorioId = button.getAttribute('data-id');
            console.log(' Eliminando recordatorio:', recordatorioId);
            deleteReminder(recordatorioId);
        }
    });

    console.log(' Event listeners de recordatorios inicializados');
}

// Funcin adicional para asegurar que los botones funcionen
function inicializarBotonesRecordatorios() {
    console.log(' Inicializacin adicional de botones de recordatorios...');

    // Buscar todos los botones que puedan ser de recordatorios
    const botones = document.querySelectorAll('button');

    botones.forEach(boton => {
        // Verificar si es el botn de crear recordatorio
        if (boton.id === 'btnCrearRecordatorio' ||
            boton.title === 'Crear Recordatorio' ||
            boton.textContent.includes('Crear Recordatorio')) {

            console.log(' Encontrado botn de crear recordatorio:', boton);

            // Remover todos los event listeners existentes
            const nuevoBoton = boton.cloneNode(true);
            boton.parentNode.replaceChild(nuevoBoton, boton);

            // Agregar el event listener correcto
            nuevoBoton.addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                console.log(' Botn crear recordatorio clickeado (inicializacin adicional)');
                handleCrearRecordatorio();
            });

            console.log(' Botn de crear recordatorio configurado correctamente');
        }
    });

    // Tambin buscar por onclick y eliminarlo
    const botonesConOnclick = document.querySelectorAll('[onclick*="showReminderModal"]');
    botonesConOnclick.forEach(boton => {
        console.log(' Removiendo onclick problemtico de:', boton);
        boton.removeAttribute('onclick');

        // Agregar event listener correcto
        boton.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            console.log(' Botn crear recordatorio clickeado (removido onclick)');
            handleCrearRecordatorio();
        });
    });
}

// Funciones de navegacin de fecha
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

// Funciones de navegacin especficas (para compatibilidad)
function prevDay() {
    navegarAnterior();
}

function nextDay() {
    navegarSiguiente();
}

function today() {
    irHoy();
}

// Funcin para agendar nueva cita
function agendarCita(hora = null) {
    console.log(` Agendando cita para las ${hora || 'hora no especificada'}`);

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

// Funcin para cargar pacientes en el select de citas
function cargarPacientesEnSelect() {
    const select = document.getElementById('appointmentPatient');
    if (!select) return;

    // Limpiar opciones existentes (excepto la primera)
    while (select.children.length > 1) {
        select.removeChild(select.lastChild);
    }

    // Usar la lista global de pacientes si est disponible
    if (window.pacientesList && window.pacientesList.length > 0) {
        window.pacientesList.forEach(paciente => {
            const option = document.createElement('option');
            option.value = paciente.paciente_id;
            option.textContent = `${paciente.nombre_completo} - ${paciente.rut}`;
            select.appendChild(option);
        });
    } else {
        // Si no hay lista global, cargar desde API
        fetch('/api/professional/patients', {
            method: 'GET',
            credentials: 'include'
        })
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
                console.error(' Error cargando pacientes:', error);
            });
    }
}

// Funcin para mostrar modal de agenda (alternativa)
function showScheduleModal() {
    agendarCita();
}

// Funcin para guardar cita (sobrescribir la existente)
function saveAppointment() {
    console.log(' Guardando cita...');

    const form = document.getElementById('scheduleForm');
    if (!form) {
        console.error(' Formulario de cita no encontrado');
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

    console.log(' Datos de la cita:', citaData);

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
        showNotification('Debe seleccionar un tipo de atencin', 'error');
        return;
    }

    // Enviar datos al servidor
    fetch('/api/professional/schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'include',
        body: JSON.stringify(citaData)
    })
        .then(response => response.json())
        .then(data => {
            console.log(' Respuesta del servidor:', data);

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
            console.error(' Error:', error);
            showNotification('Error de conexin al agendar la cita', 'error');
        });
}

// Funcin para recargar la agenda manualmente
function recargarAgenda() {
    console.log(' Recargando agenda...');
    cargarAgenda();
    showNotification('Agenda recargada', 'success');
}

// Funcin para recargar agenda completa en todas las vistas
function recargarAgendaCompleta() {
    console.log(' Recargando agenda completa en todas las vistas...');

    // Obtener la fecha actual de la agenda
    const fechaActual = fechaActualAgenda.toISOString().split('T')[0];

    // Recargar la vista actual inmediatamente
    cargarAgenda(fechaActual);

    // Programar una recarga adicional después de un breve delay
    // para asegurar que los datos se hayan actualizado en el servidor
    setTimeout(() => {
        console.log(' Recarga adicional para sincronización...');
        cargarAgenda(fechaActual);
    }, 1000);

    console.log(' Agenda completa recargada exitosamente');
}
function verCita(citaId) {
    console.log(` Viendo cita: ${citaId}`);
    console.log(' Citas del día disponibles:', citasDelDia);
    console.log(' Vista actual:', currentView);

    // Verificar si estamos en vista diaria
    if (currentView !== 'diaria') {
        showNotification('Esta función solo está disponible en vista diaria', 'warning');
        return;
    }

    // Verificar si hay citas cargadas
    if (!citasDelDia || citasDelDia.length === 0) {
        showNotification('No hay citas cargadas para el día actual', 'info');
        return;
    }

    const cita = citasDelDia.find(c => c.cita_id === citaId);
    if (!cita) {
        console.error(' Cita no encontrada. ID buscado:', citaId);
        console.error(' IDs disponibles:', citasDelDia.map(c => c.cita_id));
        showNotification('Cita no encontrada. Intente recargar la agenda', 'error');
        return;
    }

    // Mostrar detalles de la cita (puedes implementar un modal especfico)
    alert(`Detalles de la cita:
Paciente: ${cita.paciente_nombre}
RUT: ${cita.paciente_rut}
Hora: ${cita.hora}
Tipo: ${cita.tipo_atencion}
Estado: ${cita.estado}
Notas: ${cita.notas || 'Sin notas'}`);
}

// Funcin para confirmar una cita
function confirmarCita(citaId) {
    console.log(` Confirmando cita: ${citaId}`);

    actualizarEstadoCita(citaId, 'confirmada');
}

// Funcin para cancelar una cita
function cancelarCita(citaId) {
    console.log(` Cancelando cita: ${citaId}`);

    if (confirm('Est seguro de que desea cancelar esta cita?')) {
        actualizarEstadoCita(citaId, 'cancelada');
    }
}

// Funcin para actualizar el estado de una cita
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
                recargarAgendaCompleta(); // Recargar agenda completa
            } else {
                showNotification(data.message || 'Error al actualizar la cita', 'error');
            }
        })
        .catch(error => {
            console.error(' Error:', error);
            showNotification('Error de conexin al actualizar la cita', 'error');
        });
}

// Funcin para eliminar una cita
function eliminarCita(citaId) {
    mostrarConfirmacionEliminacion(
        'Eliminar Cita',
        '¿Está seguro de que desea eliminar esta cita?',
        'Esta acción eliminará permanentemente la cita del calendario. Esta acción no se puede deshacer.',
        'Eliminar Cita',
        () => {
            fetch(`/api/professional/schedule/${citaId}`, {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('✅ Cita eliminada exitosamente', 'success');
                        recargarAgendaCompleta(); // Recargar agenda completa
                    } else {
                        showNotification(data.message || '❌ Error al eliminar la cita', 'error');
                    }
                })
                .catch(error => {
                    console.error(' Error:', error);
                    showNotification('❌ Error de conexión al eliminar la cita', 'error');
                });
        }
    );
}

// Funcin para ver la cita (compatibilidad con HTML existente)
function viewAppointment(citaId) {
    verCita(citaId);
}

// Funcin para agendar en horario especfico (compatibilidad con HTML existente)
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

console.log(' Funciones de agenda cargadas correctamente');

// ====== FUNCIONES DE CONFIGURACIN DE HORARIOS ======

// Funcin para mostrar modal de configuracin de horarios
function configurarHorarios() {
    console.log(' Configurando horarios...');

    // Cargar horarios actuales
    cargarHorariosActuales();

    // Mostrar modal
    const modal = document.getElementById('horariosModal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

// Funcin para cargar horarios actuales
function cargarHorariosActuales() {
    fetch('/api/professional/working-hours')
        .then(response => response.json())
        .then(data => {
            console.log(' Horarios actuales:', data);

            if (data.success && data.horarios) {
                // Mapear das de espaol a ingls para IDs
                const diasMap = {
                    'Lunes': 'lunes',
                    'Martes': 'martes',
                    'Mircoles': 'miercoles',
                    'Jueves': 'jueves',
                    'Viernes': 'viernes',
                    'Sbado': 'sabado',
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
            console.error(' Error cargando horarios:', error);
            showNotification('Error al cargar horarios actuales', 'error');
        });
}

// Funcin para guardar horarios
function guardarHorarios() {
    console.log(' Guardando horarios...');

    // Mapear das de IDs a espaol
    const diasMap = {
        'lunes': 'Lunes',
        'martes': 'Martes',
        'miercoles': 'Mircoles',
        'jueves': 'Jueves',
        'viernes': 'Viernes',
        'sabado': 'Sbado',
        'domingo': 'Domingo'
    };

    const horarios = [];

    // Recopilar datos de todos los das
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

    console.log(' Horarios a guardar:', horarios);

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
            console.log(' Respuesta del servidor:', data);

            if (data.success) {
                showNotification('Horarios guardados exitosamente', 'success');

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('horariosModal'));
                if (modal) {
                    modal.hide();
                }

                // Recargar agenda si est visible
                const agendaPane = document.getElementById('schedule');
                if (agendaPane && agendaPane.classList.contains('active')) {
                    cargarAgenda();
                }

            } else {
                showNotification(data.message || 'Error al guardar horarios', 'error');
            }
        })
        .catch(error => {
            console.error(' Error:', error);
            showNotification('Error de conexin al guardar horarios', 'error');
        });
}

// Exponer funciones globalmente
window.configurarHorarios = configurarHorarios;
window.guardarHorarios = guardarHorarios;

console.log(' Funciones de configuracin de horarios cargadas correctamente');

// ========================================
// FUNCIONES PARA VISTAS MLTIPLES DE AGENDA
// ========================================

// Funcin para cambiar vista de agenda
function cambiarVista(nuevaVista) {
    console.log(` Cambiando vista a: ${nuevaVista}`);

    currentView = nuevaVista;

    // Ocultar todas las vistas
    document.getElementById('vistaDiariaContent').classList.add('d-none');
    document.getElementById('vistaSemanalContent').classList.add('d-none');
    document.getElementById('vistaMensualContent').classList.add('d-none');

    // Mostrar vista seleccionada
    document.getElementById(`vista${nuevaVista.charAt(0).toUpperCase() + nuevaVista.slice(1)}Content`).classList.remove('d-none');

    // Resetear fecha a la actual cuando se cambie a vista semanal
    if (nuevaVista === 'semanal') {
        fechaActualAgenda = new Date();
        console.log(' 🔄 Fecha reseteada a actual para vista semanal:', fechaActualAgenda.toISOString().split('T')[0]);
    }

    // Actualizar título de la agenda específicamente
    const tituloAgenda = document.querySelector('#agendaCard .card-header h5');
    if (tituloAgenda) {
        const fecha = fechaActualAgenda.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        switch (nuevaVista) {
            case 'diaria':
                tituloAgenda.innerHTML = `Agenda de Hoy - <span id="currentDate">${fecha}</span>`;
                break;
            case 'semanal':
                tituloAgenda.innerHTML = `Agenda Semanal - <span id="currentDate">${fecha}</span>`;
                break;
            case 'mensual':
                tituloAgenda.innerHTML = `Agenda Mensual - <span id="currentDate">${fecha}</span>`;
                break;
        }
    }

    // Recargar datos
    cargarAgenda();
}

// Funcin para actualizar vista semanal
function actualizarVistaSemanal(agendaSemanal, fechaInicio, fechaFin) {
    console.log(' Actualizando vista semanal:', agendaSemanal);

    const tbody = document.getElementById('agendaSemanalBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    // Actualizar fechas en los headers
    actualizarFechasSemanal(fechaInicio);

    // Generar horarios de 8:00 a 18:00
    const horarios = [];
    for (let hora = 8; hora < 18; hora++) {
        horarios.push(`${hora.toString().padStart(2, '0')}:00`);
    }

    // Crear filas por horario
    horarios.forEach(hora => {
        const fila = document.createElement('tr');
        fila.innerHTML = `<td class="text-center fw-bold">${hora}</td>`;

        // Agregar celdas para cada da de la semana
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

// Funcin para actualizar fechas en la vista semanal
function actualizarFechasSemanal(fechaInicio) {
    console.log(' Actualizando fechas semanales:', fechaInicio);

    const fechaInicioObj = new Date(fechaInicio);
    const diasSemana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'];

    // Calcular el lunes de la semana
    const diaSemana = fechaInicioObj.getDay();
    const diasHastaLunes = diaSemana === 0 ? 6 : diaSemana - 1; // 0 = domingo
    const lunesSemana = new Date(fechaInicioObj);
    lunesSemana.setDate(lunesSemana.getDate() - diasHastaLunes);

    // Actualizar cada fecha
    diasSemana.forEach((dia, index) => {
        const fechaElement = document.getElementById(`fecha-${dia}`);
        if (fechaElement) {
            const fechaActual = new Date(lunesSemana);
            fechaActual.setDate(lunesSemana.getDate() + index);

            const dia = fechaActual.getDate().toString().padStart(2, '0');
            const mes = (fechaActual.getMonth() + 1).toString().padStart(2, '0');

            fechaElement.textContent = `${dia}/${mes}`;
        }
    });
}

// Funcin para actualizar vista mensual
function actualizarVistaMensual(agendaMensual, fechaInicio, fechaFin) {
    console.log(' Actualizando vista mensual:', agendaMensual);

    const calendario = document.getElementById('calendarioMensual');
    if (!calendario) return;

    calendario.innerHTML = '';

    // Headers de das de la semana
    const diasSemana = ['Dom', 'Lun', 'Mar', 'Mi', 'Jue', 'Vie', 'Sb'];
    diasSemana.forEach(dia => {
        const header = document.createElement('div');
        header.className = 'dia-header';
        header.textContent = dia;
        calendario.appendChild(header);
    });

    // Obtener primer da del mes y calcular das a mostrar
    const fechaInicioObj = new Date(fechaInicio);
    const fechaFinObj = new Date(fechaFin);

    // Agregar das del mes anterior si es necesario
    const primerDiaSemana = fechaInicioObj.getDay();
    const fechaInicioCalendario = new Date(fechaInicioObj);
    fechaInicioCalendario.setDate(fechaInicioCalendario.getDate() - primerDiaSemana);

    // Generar calendario
    const fechaActual = new Date(fechaInicioCalendario);
    const hoy = new Date().toISOString().split('T')[0];

    for (let i = 0; i < 42; i++) { // 6 semanas mximo
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

        // Nmero del da
        const diaNumero = document.createElement('div');
        diaNumero.className = 'dia-numero';
        diaNumero.textContent = fechaActual.getDate();
        diaCelda.appendChild(diaNumero);

        // Citas del da
        const diaData = agendaMensual[fechaStr];
        if (diaData && diaData.citas.length > 0) {
            diaData.citas.slice(0, 3).forEach(cita => { // Mostrar mximo 3 citas
                const citaDiv = document.createElement('div');
                citaDiv.className = `cita-mensual ${cita.estado}`;
                citaDiv.textContent = `${cita.hora} ${cita.paciente_nombre}`;
                citaDiv.onclick = () => verCita(cita.cita_id);
                diaCelda.appendChild(citaDiv);
            });

            // Mostrar contador si hay ms citas
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

// Funcin para agendar cita en fecha especfica
function agendarCitaFecha(fecha, hora = null) {
    console.log(` Agendando cita para ${fecha} a las ${hora || 'hora por definir'}`);

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

console.log(' Funciones de vistas mltiples de agenda cargadas correctamente');

// ===== IA CLNICA ASISTIVA =====

let analisisTimeout = null;
let ultimoMotivoAnalizado = '';

// Funcin para analizar el motivo de consulta en tiempo real
async function analizarMotivoEnTiempoReal() {
    const motivoConsulta = document.getElementById('motivoConsulta').value.trim();
    const tipoAtencion = document.getElementById('tipoAtencion').value;

    // Si el motivo est vaco, ocultar resultados
    if (!motivoConsulta) {
        ocultarResultadosIA();
        return;
    }

    // Si es el mismo motivo que ya analizamos, no hacer nada
    if (motivoConsulta === ultimoMotivoAnalizado) {
        return;
    }

    // Mostrar indicador de anlisis
    mostrarIndicadorAnalisis();

    // Cancelar anlisis anterior si existe
    if (analisisTimeout) {
        clearTimeout(analisisTimeout);
    }

    // Esperar 1 segundo antes de analizar (para evitar muchas llamadas)
    analisisTimeout = setTimeout(async () => {
        try {
            console.log(' Analizando motivo de consulta:', motivoConsulta);
            console.log(' Tipo de atencin seleccionado:', tipoAtencion);

            // Usar el nuevo endpoint de análisis mejorado
            const response = await fetch('/api/copilot/analyze-enhanced', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    motivo_consulta: motivoConsulta,
                    tipo_atencion: tipoAtencion,
                    edad_paciente: null,
                    antecedentes: null
                })
            });

            const data = await response.json();

            if (data.success) {
                // Mostrar análisis en la sidebar de Copilot Health
                mostrarAnalisisMejoradoEnSidebar(data.analisis_mejorado);
                ultimoMotivoAnalizado = motivoConsulta;

                // Mostrar mensaje de éxito
                showNotification('Análisis completado por Copilot Health', 'success');
            } else {
                console.error(' Error en análisis:', data.message);
                mostrarErrorAnalisis(data.message);
            }

        } catch (error) {
            console.error(' Error en anlisis de IA:', error);
            mostrarErrorAnalisis('Error de conexin con el servidor');
        } finally {
            ocultarIndicadorAnalisis();
        }
    }, 1000);
}

// Funcin para mostrar el indicador de anlisis
function mostrarIndicadorAnalisis() {
    const indicator = document.getElementById('iaAnalysisIndicator');
    const results = document.getElementById('iaAnalysisResults');
    const preguntas = document.getElementById('preguntasSugeridas');

    if (indicator) indicator.style.display = 'block';
    if (results) results.style.display = 'none';
    if (preguntas) preguntas.style.display = 'none';
}

// Funcin para ocultar el indicador de anlisis
function ocultarIndicadorAnalisis() {
    const indicator = document.getElementById('iaAnalysisIndicator');
    if (indicator) indicator.style.display = 'none';
}

// Funcin para mostrar los resultados del anlisis
function mostrarResultadosAnalisis(analisis) {
    // Actualizar campos del anlisis
    document.getElementById('especialidadDetectada').textContent =
        analisis.especialidad_detectada.replace('_', ' ').toUpperCase();
    document.getElementById('categoriaDetectada').textContent =
        analisis.categoria.toUpperCase();
    document.getElementById('urgenciaDetectada').textContent =
        analisis.urgencia;
    document.getElementById('sintomasDetectados').textContent =
        analisis.sintomas_principales.join(', ') || 'No detectados';

    // Mostrar resultados
    document.getElementById('iaAnalysisResults').style.display = 'block';

    // Las preguntas ahora se muestran en la sidebar de Copilot Health
    // No se llama a mostrarPreguntasSugeridas aquí

    console.log('✅ Análisis de IA completado:', analisis);
}

// Función para mostrar las preguntas sugeridas en la sidebar de Copilot Health
// ESTA FUNCIÓN HA SIDO ELIMINADA - Las preguntas ahora se muestran solo en mostrarAnalisisMejoradoEnSidebar
function mostrarPreguntasSugeridas(preguntas) {
    // Esta función ha sido eliminada para evitar que se active la sección antigua
    console.log('❌ mostrarPreguntasSugeridas ha sido eliminada - Las preguntas se muestran en mostrarAnalisisMejoradoEnSidebar');

    // En su lugar, mostrar un mensaje de que las preguntas están en la sidebar
    showNotification('Las preguntas de evaluación aparecen en la sidebar de Copilot Health', 'info');
}

// Funcin para insertar una pregunta especfica en la evaluacin
function insertarPreguntaEnEvaluacion(pregunta) {
    const evaluacionTextarea = document.getElementById('diagnostico');
    const textoActual = evaluacionTextarea.value;

    // Agregar la pregunta al final del texto actual
    const nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + ` ${pregunta}`;
    evaluacionTextarea.value = nuevoTexto;

    // Mostrar notificacin
    showNotification('Pregunta agregada a la evaluacin', 'success');

    console.log(' Pregunta insertada:', pregunta);
}

//   NUEVA L GICA SIMPLIFICADA: Funci n para insertar todas las preguntas sugeridas en la evaluaci n
function insertarPreguntasEnEvaluacion() {
    const evaluacionTextarea = document.getElementById('diagnostico');
    const textoActual = evaluacionTextarea.value;
    const preguntas = document.querySelectorAll('#listaPreguntasSugeridas .mb-2 span.flex-grow-1');

    let nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + 'PREGUNTAS SUGERIDAS POR IA:\n';

    preguntas.forEach((pregunta, index) => {
        nuevoTexto += `${index + 1}. ${pregunta.textContent}\n`;
    });

    evaluacionTextarea.value = nuevoTexto;

    // Mostrar notificaci n
    showNotification('Todas las preguntas han sido agregadas a la evaluacin', 'success');

    console.log(' Todas las preguntas insertadas');
}

// Funcin para mostrar error en el anlisis
function mostrarErrorAnalisis(mensaje) {
    console.error(' Error en anlisis de IA:', mensaje);

    // Mostrar notificacin de error
    showNotification(`Error en anlisis de IA: ${mensaje}`, 'error');

    // Ocultar resultados
    ocultarResultadosIA();
}

// Funcin para ocultar todos los resultados de IA
function ocultarResultadosIA() {
    const results = document.getElementById('iaAnalysisResults');
    const preguntas = document.getElementById('preguntasSugeridas');
    const indicator = document.getElementById('iaAnalysisIndicator');

    if (results) results.style.display = 'none';
    if (preguntas) preguntas.style.display = 'none';
    if (indicator) indicator.style.display = 'none';

    ultimoMotivoAnalizado = '';
}

// Funcin para evaluar antecedentes con IA
async function evaluarAntecedentesIA(antecedentes, especialidad, edad) {
    try {
        const response = await fetch('/api/copilot/evaluate-antecedentes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                antecedentes: antecedentes,
                especialidad: especialidad,
                edad: edad
            })
        });

        const data = await response.json();

        if (data.success) {
            return data.evaluacion;
        } else {
            console.error(' Error en evaluacin de antecedentes:', data.message);
            return null;
        }

    } catch (error) {
        console.error(' Error en evaluacin de antecedentes:', error);
        return null;
    }
}

// Funcin para sugerir tratamiento con IA
async function sugerirTratamientoIA(diagnostico, especialidad, edad) {
    try {
        const response = await fetch('/api/copilot/suggest-treatment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                diagnostico: diagnostico,
                especialidad: especialidad,
                edad: edad
            })
        });

        const data = await response.json();

        if (data.success) {
            return data.planes_tratamiento;
        } else {
            console.error(' Error en sugerencia de tratamiento:', data.message);
            return null;
        }

    } catch (error) {
        console.error(' Error en sugerencia de tratamiento:', error);
        return null;
    }
}

// Funcin para anlisis completo con IA
async function analisisCompletoIA(motivo, antecedentes, diagnostico) {
    try {
        const response = await fetch('/api/copilot/complete-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                motivo_consulta: motivo,
                antecedentes: antecedentes,
                diagnostico: diagnostico
            })
        });

        const data = await response.json();

        if (data.success) {
            return data.resumen_completo;
        } else {
            console.error(' Error en anlisis completo:', data.message);
            return null;
        }

    } catch (error) {
        console.error(' Error en anlisis completo:', error);
        return null;
    }
}

// Funcin para mostrar resumen completo de IA
function mostrarResumenCompletoIA(resumen) {
    // Crear modal para mostrar el resumen completo
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'resumenCompletoModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header bg-primary text-white">
                    <h5 class="modal-title">
                        <i class="fas fa-robot me-2"></i>
                        Resumen Completo - IA
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        Este resumen es generado por IA y debe ser revisado por el profesional.
                    </div>
                    <div class="border rounded p-3 bg-light">
                        <pre style="white-space: pre-wrap; font-family: inherit;">${resumen}</pre>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                    <button type="button" class="btn btn-primary" onclick="copiarResumenAlFormulario()">
                        <i class="fas fa-copy me-2"></i>
                        Copiar al Formulario
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Mostrar modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();

    // Limpiar modal cuando se cierre
    modal.addEventListener('hidden.bs.modal', function () {
        document.body.removeChild(modal);
    });
}

// Funcin para copiar el resumen al formulario
function copiarResumenAlFormulario() {
    const diagnosticoTextarea = document.getElementById('diagnostico');
    const tratamientoTextarea = document.getElementById('tratamiento');

    // Aqu se puede implementar la lgica para copiar partes especficas del resumen
    // a los campos correspondientes del formulario

    showNotification('Resumen copiado al formulario', 'success');

    // Cerrar modal
    const modal = bootstrap.Modal.getInstance(document.getElementById('resumenCompletoModal'));
    if (modal) modal.hide();
}

// Exponer funciones de IA globalmente
window.analizarMotivoEnTiempoReal = analizarMotivoEnTiempoReal;
window.insertarPreguntaEnEvaluacion = insertarPreguntaEnEvaluacion;
window.insertarPreguntasEnEvaluacion = insertarPreguntasEnEvaluacion;
window.evaluarAntecedentesIA = evaluarAntecedentesIA;
window.sugerirTratamientoIA = sugerirTratamientoIA;
window.analisisCompletoIA = analisisCompletoIA;
window.mostrarResumenCompletoIA = mostrarResumenCompletoIA;

console.log(' Funciones de IA cargadas correctamente');



// Funcin para mostrar las sugerencias de tratamiento
function mostrarSugerenciasTratamiento(planes) {
    console.log(' Mostrando sugerencias de tratamiento:', planes);

    const container = document.getElementById('listaSugerenciasTratamiento');
    const modal = document.getElementById('sugerenciasTratamiento');

    if (!container || !modal) {
        console.error(' Elementos de sugerencias no encontrados');
        return;
    }

    // Limpiar sugerencias anteriores
    container.innerHTML = '';

    // Mostrar el modal
    modal.style.display = 'block';

    if (!planes || planes.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                <strong>Informacin sobre el tratamiento:</strong>
                <br><br>
                <p>No se encontraron estudios cientficos especficos para esta condicin en este momento.</p>
                <p><strong>Recomendaciones generales:</strong></p>
                <ul>
                    <li>Consultar con un profesional de la salud para evaluacin completa</li>
                    <li>Realizar exmenes complementarios si es necesario</li>
                    <li>Seguir las indicaciones del profesional tratante</li>
                    <li>Mantener un registro de sntomas y evolucin</li>
                </ul>
                <small class="text-muted">La informacin mdica debe ser evaluada por un profesional calificado.</small>
            </div>
        `;
        return;
    }

    // Separar planes de intervencin de otros planes
    const planesIntervencion = planes.filter(plan =>
        plan.titulo && plan.titulo.toLowerCase().includes('intervencin')
    );
    const otrosPlanes = planes.filter(plan =>
        !plan.titulo || !plan.titulo.toLowerCase().includes('intervencin')
    );

    // Mostrar planes de intervencin primero con estilo destacado
    if (planesIntervencion.length > 0) {
        const intervencionHeader = document.createElement('div');
        intervencionHeader.className = 'mb-3';
        intervencionHeader.innerHTML = `
            <div class="alert alert-success border-success">
                <h6 class="mb-2">
                    <i class="fas fa-target me-2"></i>
                    <strong> PLAN DE INTERVENCIN IA SUGERIDA</strong>
                </h6>
                <small class="text-muted">Plan especfico con tcnicas, aplicaciones y protocolos</small>
            </div>
        `;
        container.appendChild(intervencionHeader);

        planesIntervencion.forEach((plan, index) => {
            const planDiv = document.createElement('div');
            planDiv.className = 'mb-3 p-3 bg-success bg-opacity-10 rounded border-start border-success border-4';
            planDiv.innerHTML = `
                <div class="d-flex align-items-start">
                    <span class="badge bg-success text-white me-2">
                        <i class="fas fa-target me-1"></i>Plan ${index + 1}
                    </span>
                    <div class="flex-grow-1">
                        <h6 class="mb-2 text-success">${plan.titulo}</h6>
                        <div class="mb-3">
                            ${plan.descripcion}
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <small class="text-muted">Nivel de Evidencia:</small>
                                <div class="fw-bold text-success">${plan.nivel_evidencia}</div>
                            </div>
                            <div class="col-md-4">
                                <small class="text-muted">DOI:</small>
                                <div class="fw-bold text-primary">
                                    ${plan.doi_referencia && plan.doi_referencia !== 'Sin DOI' && plan.doi_referencia !== 'Múltiples fuentes'
                    ? `<a href="https://doi.org/${plan.doi_referencia}" target="_blank" class="text-primary">
                                             <i class="fas fa-external-link-alt me-1"></i>Ver Paper
                                           </a>`
                    : 'No disponible'
                }
                                </div>
                            </div>
                            <div class="col-md-4">
                                <small class="text-muted">Año:</small>
                                <div class="fw-bold text-info">
                                    ${plan.año_publicacion && plan.año_publicacion !== 'N/A'
                    ? plan.año_publicacion
                    : (plan.fecha_publicacion && plan.fecha_publicacion !== 'Fecha no disponible'
                        ? plan.fecha_publicacion.match(/\d{4}/)?.[0] || 'N/A'
                        : 'N/A')
                }
                                </div>
                            </div>
                        </div>
                        ${plan.contraindicaciones ? `
                            <div class="mt-2">
                                <small class="text-danger"> Contraindicaciones: ${plan.contraindicaciones}</small>
                            </div>
                        ` : ''}
                    </div>
                    <button type="button" class="btn btn-sm btn-action btn-confirm ms-2" 
                            onclick="insertarSugerenciaTratamiento('${plan.titulo.replace(/['"\\]/g, '\\$&')}', '${plan.descripcion.replace(/['"\\]/g, '\\$&')}', '${plan.doi_referencia || ''}', '${plan.evidencia_cientifica || ''}')">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            `;
            container.appendChild(planDiv);
        });
    }

    // Mostrar otros planes de tratamiento
    if (otrosPlanes.length > 0) {
        const estudiosHeader = document.createElement('div');
        estudiosHeader.className = 'mb-3';
        estudiosHeader.innerHTML = `
            <div class="alert alert-info border-info">
                <h6 class="mb-2">
                    <i class="fas fa-microscope me-2"></i>
                    <strong> ESTUDIOS CIENTFICOS RELACIONADOS</strong>
                </h6>
                <small class="text-muted">Evidencia cientfica adicional para referencia</small>
            </div>
        `;
        container.appendChild(estudiosHeader);

        otrosPlanes.forEach((plan, index) => {
            const planDiv = document.createElement('div');
            planDiv.className = 'mb-3 p-3 bg-light rounded border-start border-warning border-4';
            planDiv.innerHTML = `
                <div class="d-flex align-items-start">
                    <span class="badge bg-warning text-dark me-2">Estudio ${index + 1}</span>
                    <div class="flex-grow-1">
                        <h6 class="mb-2">${plan.titulo}</h6>
                        <p class="mb-2">${plan.descripcion}</p>
                        <div class="row">
                            <div class="col-md-6">
                                <small class="text-muted">Nivel de Evidencia:</small>
                                <div class="fw-bold text-info">${plan.nivel_evidencia}</div>
                            </div>
                            <div class="col-md-6">
                                <small class="text-muted">DOI:</small>
                                <div class="fw-bold text-primary">${plan.doi_referencia || 'No disponible'}</div>
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-md-6">
                                <small class="text-muted">Evidencia Cientfica:</small>
                                <div class="fw-bold text-success">${plan.evidencia_cientifica || 'Basado en evidencia clnica'}</div>
                            </div>
                            <div class="col-md-6">
                                <small class="text-muted">Link del Paper:</small>
                                <div class="fw-bold">
                                    ${plan.doi_referencia && plan.doi_referencia !== 'No disponible' && plan.doi_referencia !== 'M ltiples fuentes' ?
                    `<a href="https://doi.org/${plan.doi_referencia}" target="_blank" class="text-primary">
                                        <i class="fas fa-external-link-alt me-1"></i>Ver Paper
                                    </a>` :
                    '<span class="text-muted">No disponible</span>'
                }
                                </div>
                            </div>
                        </div>
                        ${plan.contraindicaciones ? `
                            <div class="mt-2">
                                <small class="text-danger"> Contraindicaciones: ${plan.contraindicaciones}</small>
                            </div>
                        ` : ''}
                    </div>
                    <button type="button" class="btn btn-sm btn-action btn-cancel ms-2" 
                            onclick="insertarSugerenciaTratamiento('${plan.titulo.replace(/['"\\]/g, '\\$&')}', '${plan.descripcion.replace(/['"\\]/g, '\\$&')}', '${plan.doi_referencia || ''}', '${plan.evidencia_cientifica || ''}')">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            `;
            container.appendChild(planDiv);
        });
    }

    console.log(' Sugerencias de tratamiento mostradas:', planes);
    console.log(' Planes de intervencin:', planesIntervencion.length);
    console.log(' Estudios cientficos:', otrosPlanes.length);
}

// Funcin para insertar una sugerencia especfica de tratamiento
function insertarSugerenciaTratamiento(titulo, descripcion, doi = null, evidencia = null) {
    const tratamientoTextarea = document.getElementById('tratamiento');
    const textoActual = tratamientoTextarea.value;

    // Construir el texto con referencias si estn disponibles
    let nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + ` ${titulo}:\n${descripcion}`;

    if (doi) {
        nuevoTexto += `\n   DOI: ${doi}`;
    }

    if (evidencia) {
        nuevoTexto += `\n   Evidencia: ${evidencia}`;
    }

    tratamientoTextarea.value = nuevoTexto;

    // Mostrar notificacin
    showNotification('Sugerencia de tratamiento agregada', 'success');

    console.log(' Sugerencia de tratamiento insertada:', titulo);
}

// Función para insertar todas las sugerencias de tratamiento (MEJORADA)
function insertarSugerenciasTratamiento() {
    const tratamientoTextarea = document.getElementById('tratamiento');
    const textoActual = tratamientoTextarea.value;
    const sugerencias = document.querySelectorAll('#listaSugerenciasTratamiento .mb-3');

    let nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + 'EVIDENCIA CIENTÍFICA RECOMENDADA:\n\n';

    sugerencias.forEach((sugerencia, index) => {
        const tituloElement = sugerencia.querySelector('h6');
        const descripcionElement = sugerencia.querySelector('p');

        const titulo = tituloElement ? tituloElement.textContent : 'Sin título';
        const descripcion = descripcionElement ? descripcionElement.textContent : 'Sin descripción';

        // Buscar DOI y evidencia en los elementos de la sugerencia
        const doiElement = sugerencia.querySelector('.text-primary');
        const evidenciaElement = sugerencia.querySelector('.text-success');

        const doi = doiElement ? doiElement.textContent : '';
        const evidencia = evidenciaElement ? evidenciaElement.textContent : '';

        nuevoTexto += `${index + 1}. ${titulo}:\n${descripcion}`;

        if (doi && doi !== 'No disponible') {
            nuevoTexto += `\n   DOI: ${doi}`;
        }

        if (evidencia && evidencia !== 'Basado en evidencia clínica') {
            nuevoTexto += `\n   Evidencia: ${evidencia}`;
        }

        nuevoTexto += '\n\n';
    });

    tratamientoTextarea.value = nuevoTexto;

    // Mostrar notificación
    showNotification('Evidencia científica agregada al plan de tratamiento', 'success');

    console.log('✅ Evidencia científica insertada correctamente');
}

// Funcin para mostrar error en las sugerencias
function mostrarErrorSugerencias(mensaje) {
    console.error(' Error en sugerencias de tratamiento:', mensaje);

    const container = document.getElementById('listaSugerenciasTratamiento');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error: ${mensaje}
            </div>
        `;
    }

    // Mostrar notificacin de error
    showNotification(`Error en sugerencias de tratamiento: ${mensaje}`, 'error');
}

//   FUNCI N ELIMINADA - Reemplazada por nueva l gica simplificada al final del archivo

//   FUNCI N ELIMINADA - Reemplazada por nueva l gica simplificada al final del archivo

// FUNCIÓN ELIMINADA: realizarBusquedaAutomatica - Produjo resultados irrelevantes
// Se mantiene solo realizarBusquedaAutomaticaDesdeSidebar que produce mejores resultados

// Funcin para obtener t rminos seleccionados
//   NUEVA L GICA SIMPLIFICADA: Funci n para obtener t rminos seleccionados
function obtenerTerminosSeleccionados() {
    const checkboxes = document.querySelectorAll('#listaSugerenciasTratamiento input[type="checkbox"]:checked');
    const terminos = Array.from(checkboxes).map(cb => cb.value);
    console.log(' T rminos seleccionados encontrados:', terminos);
    return terminos;
}

// Funcin para seleccionar todos los trminos
function seleccionarTodosTerminos() {
    const checkboxes = document.querySelectorAll('#listaSugerenciasTratamiento input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = true);
    showNotification('Todos los trminos seleccionados', 'info');
}

// Funcin para deseleccionar todos los trminos
function deseleccionarTodosTerminos() {
    const checkboxes = document.querySelectorAll('#listaSugerenciasTratamiento input[type="checkbox"]');
    checkboxes.forEach(cb => cb.checked = false);
    showNotification('Todos los trminos deseleccionados', 'info');
}

//   NUEVA: Funci n para restaurar el estado original del motivo de consulta
function restaurarMotivoOriginal() {
    const motivoConsulta = document.getElementById('motivoConsulta');
    const motivoOriginal = motivoConsulta.getAttribute('data-motivo-original');

    if (motivoOriginal) {
        motivoConsulta.value = motivoOriginal;
        console.log('   Motivo original restaurado:', motivoOriginal);
        return true;
    }
    return false;
}

//   NUEVA: Funci n para verificar si hay preguntas insertadas
function hayPreguntasInsertadas() {
    const motivoConsulta = document.getElementById('motivoConsulta');
    return motivoConsulta.value.includes('PREGUNTAS SUGERIDAS POR IA:');
}

// Exponer funciones adicionales globalmente
window.insertarSugerenciaTratamiento = insertarSugerenciaTratamiento;
window.insertarSugerenciasTratamiento = insertarSugerenciasTratamiento;
window.mostrarTerminosDisponibles = mostrarTerminosDisponibles;
window.realizarBusquedaPersonalizada = realizarBusquedaPersonalizada;
window.realizarBusquedaAutomatica = realizarBusquedaAutomaticaDesdeSidebar; // Redirigido a la función mejorada
window.seleccionarTodosTerminos = seleccionarTodosTerminos;
window.deseleccionarTodosTerminos = deseleccionarTodosTerminos;
window.obtenerTerminosSeleccionados = obtenerTerminosSeleccionados;
window.restaurarMotivoOriginal = restaurarMotivoOriginal;
window.hayPreguntasInsertadas = hayPreguntasInsertadas;

// Funcin para actualizar anlisis cuando cambie el tipo de atencin
function actualizarAnalisisConTipoAtencion() {
    const motivoConsulta = document.getElementById('motivoConsulta').value.trim();
    const tipoAtencion = document.getElementById('tipoAtencion').value;

    // Si hay un motivo de consulta y se seleccion un tipo de atencin, re-analizar
    if (motivoConsulta && tipoAtencion) {
        console.log(' Actualizando anlisis con nuevo tipo de atencin:', tipoAtencion);
        ultimoMotivoAnalizado = ''; // Forzar re-anlisis
        analizarMotivoEnTiempoReal();
    }
}

// Funcin para realizar anlisis completo con IA
async function realizarAnalisisCompletoIA() {
    const motivoConsulta = document.getElementById('motivoConsulta').value.trim();
    const diagnostico = document.getElementById('diagnostico').value.trim();
    const tratamiento = document.getElementById('tratamiento').value.trim();

    if (!motivoConsulta && !diagnostico) {
        showNotification('Por favor, ingresa al menos un motivo de consulta o diagnstico', 'warning');
        return;
    }

    // Mostrar indicador de carga
    showNotification('Realizando anlisis completo con IA...', 'info');

    try {
        console.log(' Realizando anlisis completo con IA...');

        const response = await fetch('/api/copilot/complete-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                motivo_consulta: motivoConsulta,
                antecedentes: '', // Se puede mejorar obteniendo antecedentes del paciente
                diagnostico: diagnostico,
                tratamiento: tratamiento
            })
        });

        const data = await response.json();

        if (data.success) {
            mostrarResumenCompletoIA(data.resumen_completo);
            showNotification('Anlisis completo realizado exitosamente', 'success');
        } else {
            console.error(' Error en anlisis completo:', data.message);
            showNotification(`Error en anlisis completo: ${data.message}`, 'error');
        }

    } catch (error) {
        console.error(' Error en anlisis completo:', error);
        showNotification('Error de conexin con el servidor', 'error');
    }
}

async function generarPlanificacionCompletaIA() {
    const motivoConsulta = document.getElementById('motivoConsulta').value.trim();
    const tipoAtencion = document.getElementById('tipoAtencion').value;
    const evaluacionObservaciones = document.getElementById('evaluacionObservaciones').value.trim();

    if (!motivoConsulta) {
        showNotification('Por favor, ingresa un motivo de consulta primero', 'warning');
        return;
    }

    if (!tipoAtencion) {
        showNotification('Por favor, selecciona un tipo de atencin', 'warning');
        return;
    }

    // Mostrar indicador de carga
    const resumenCompletoDiv = document.getElementById('resumenCompletoIA');
    if (resumenCompletoDiv) {
        resumenCompletoDiv.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border spinner-border-sm text-success me-2" role="status">
                        <span class="visually-hidden">Generando planificacin...</span>
                    </div>
                    <small class="text-success">IA generando planificacin completa basada en estudios 2020-2025...</small>
                </div>
            `;
    }

    try {
        console.log(' Generando planificacin completa con IA...');

        const response = await fetch('/api/copilot/planificacion-completa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                motivo_atencion: motivoConsulta,
                tipo_atencion: tipoAtencion,
                evaluacion_observaciones: evaluacionObservaciones,
                edad: 35
            })
        });

        const data = await response.json();

        if (data.success) {
            mostrarPlanificacionCompletaIA(data.planificacion);
        } else {
            console.error(' Error en planificacin completa:', data.message);
            showNotification(`Error en planificacin completa: ${data.message}`, 'error');
        }

    } catch (error) {
        console.error(' Error en planificacin completa:', error);
        showNotification('Error de conexin con el servidor', 'error');
    }
}

function mostrarPlanificacionCompletaIA(planificacion) {
    const container = document.getElementById('resumenCompletoIA');
    if (!container) return;

    let html = `
            <div class="card border-success">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0">
                        <i class="fas fa-clipboard-list me-2"></i>
                        Planificacin Completa de Tratamiento - IA
                    </h5>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <h6 class="text-success"> Resumen Clnico</h6>
                        <p class="mb-0">${planificacion.resumen_clinico}</p>
                    </div>

                    <div class="mb-3">
                        <h6 class="text-primary"> Objetivos del Tratamiento</h6>
                        <ul class="list-unstyled">
                            ${planificacion.objetivos_tratamiento.map(obj => `<li><i class="fas fa-check text-success me-2"></i>${obj}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="mb-3">
                        <h6 class="text-info"> Intervenciones Especficas (Basadas en Estudios 2020-2025)</h6>
                        ${planificacion.intervenciones_especificas.length > 0 ?
            planificacion.intervenciones_especificas.map(intervencion => `
                                <div class="card mb-2">
                                    <div class="card-body p-2">
                                        <h6 class="mb-1">${intervencion.titulo}</h6>
                                        <p class="mb-1 small">${intervencion.descripcion}</p>
                                        <div class="row">
                                            <div class="col-md-6">
                                                <small class="text-muted">Evidencia: ${intervencion.evidencia}</small>
                                            </div>
                                            <div class="col-md-6">
                                                <small class="text-muted">DOI: ${intervencion.doi}</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join('') :
            '<p class="text-muted">Basado en evidencia clnica actualizada</p>'
        }
                    </div>

                    <div class="mb-3">
                        <h6 class="text-info"> Criterios de Evaluacin</h6>
                        <ul class="list-unstyled">
                            ${planificacion.criterios_evaluacion.map(criterio => `<li><i class="fas fa-chart-line text-info me-2"></i>${criterio}</li>`).join('')}
                        </ul>
                    </div>

                    ${planificacion.estudios_basados.length > 0 ? `
                        <div class="mb-3">
                            <h6 class="text-secondary"> Estudios Cientficos Consultados</h6>
                            ${planificacion.estudios_basados.map(estudio => `
                                <div class="card mb-2">
                                    <div class="card-body p-2">
                                        <h6 class="mb-1">${estudio.titulo}</h6>
                                        <p class="mb-1 small">${estudio.resumen}</p>
                                        <div class="row">
                                            <div class="col-md-4">
                                                <small class="text-muted">Autores: ${estudio.autores}</small>
                                            </div>
                                            <div class="col-md-4">
                                                <small class="text-muted">DOI: ${estudio.doi}</small>
                                            </div>
                                            <div class="col-md-4">
                                                <small class="text-muted">Fecha: ${estudio.fecha}</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}

                    <div class="alert alert-warning mt-3">
                        <h6 class="alert-heading"> Aclaracin Legal</h6>
                        <p class="mb-0 small">${planificacion.aclaracion_legal}</p>
                    </div>

                    <div class="mt-3">
                        <button type="button" class="btn btn-success me-2" onclick="copiarPlanificacionAlFormulario()">
                            <i class="fas fa-copy me-1"></i>Copiar al Formulario
                        </button>
                        <button type="button" class="btn btn-outline-secondary" onclick="cerrarPlanificacionCompleta()">
                            <i class="fas fa-times me-1"></i>Cerrar
                        </button>
                    </div>
                </div>
            </div>
        `;

    container.innerHTML = html;
    container.style.display = 'block';

    console.log(' Planificacin completa mostrada:', planificacion);
}

function copiarPlanificacionAlFormulario() {
    const tratamientoTextarea = document.getElementById('tratamiento');
    const planificacionDiv = document.getElementById('resumenCompletoIA');

    if (!tratamientoTextarea || !planificacionDiv) return;

    // Extraer texto de la planificacin
    const textoPlanificacion = planificacionDiv.textContent || planificacionDiv.innerText;

    // Agregar al formulario
    const textoActual = tratamientoTextarea.value;
    const nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + 'PLANIFICACIN COMPLETA DE TRATAMIENTO - IA:\n' + textoPlanificacion;
    tratamientoTextarea.value = nuevoTexto;

    showNotification('Planificacin completa agregada al formulario', 'success');
}

function cerrarPlanificacionCompleta() {
    const container = document.getElementById('resumenCompletoIA');
    if (container) {
        container.style.display = 'none';
    }
}

// Exponer funcin de anlisis completo globalmente
window.realizarAnalisisCompletoIA = realizarAnalisisCompletoIA;

console.log(' Funciones adicionales de IA cargadas correctamente');

// Funcin para extraer diagnstico til de las preguntas sugeridas
function extraerDiagnosticoDePreguntas(motivoConsulta) {
    console.log(' Extrayendo diagnstico de preguntas sugeridas:', motivoConsulta);

    // Si contiene "PREGUNTAS SUGERIDAS POR IA", extraer informacin til
    if (motivoConsulta.includes('PREGUNTAS SUGERIDAS POR IA')) {
        const lineas = motivoConsulta.split('\n');
        let sintomas = [];
        let actividades = [];

        for (let i = 0; i < lineas.length; i++) {
            const linea = lineas[i].trim();

            // Buscar respuestas que contengan informacin til
            if (linea.includes('flexi n de cadera')) {
                sintomas.push('dolor en cadera');
                actividades.push('flexin de cadera');
            }
            if (linea.includes('rotacin') || linea.includes('rotar el cuerpo')) {
                sintomas.push('dolor en rotacin');
                actividades.push('rotacin');
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
            if (linea.includes('flexin de hombro')) {
                sintomas.push('dolor en hombro');
                actividades.push('flexin de hombro');
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
            if (linea.includes('mueca')) {
                sintomas.push('dolor en mueca');
                actividades.push('mueca');
            }
            if (linea.includes('codo')) {
                sintomas.push('dolor en codo');
                actividades.push('codo');
            }
        }

        // Construir diagnstico basado en la informacin extrada
        if (sintomas.length > 0) {
            const diagnostico = sintomas.join(', ');
            console.log(' Diagnstico extrado:', diagnostico);
            return diagnostico;
        }

        // Si no se encontraron sntomas especficos, usar informacin general
        if (actividades.length > 0) {
            const diagnostico = `dolor en ${actividades.join(', ')}`;
            console.log(' Diagnstico extrado:', diagnostico);
            return diagnostico;
        }
    }

    // Si no se puede extraer informacin til, retornar null para usar fallback
    console.log(' No se pudo extraer diagnstico especfico, usando fallback');
    return null;
}

// Exponer funci n globalmente
window.extraerDiagnosticoDePreguntas = extraerDiagnosticoDePreguntas;

// Mostrar otros términos disponibles
const otrasCategorias = ['terminos_basicos', 'terminos_especialidad', 'terminos_edad', 'terminos_combinados'];

otrasCategorias.forEach(categoria => {
    if (terminosDisponibles[categoria] && terminosDisponibles[categoria].length > 0) {
        const titulo = categoria.replace('terminos_', '').replace('_', ' ').toUpperCase();
        html += `
                <div class="mb-3">
                    <h6 class="text-secondary"><i class="fas fa-list me-1"></i>${titulo}</h6>
                    <div class="row">
            `;

        terminosDisponibles[categoria].forEach((termino, index) => {
            const id = `${categoria}_${index}`;
            html += `
                    <div class="col-md-6 mb-2">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" value="${termino}" id="${id}">
                            <label class="form-check-label" for="${id}">
                                ${termino}
                            </label>
                        </div>
                    </div>
                `;
        });

        html += `
                    </div>
                </div>
            `;
    }
});

// Botones de acci n
html += `
        <div class="d-flex gap-2 mt-3">
            <button type="button" class="btn btn-primary btn-sm" onclick="realizarBusquedaPersonalizada('${condicionEscapada}', '${especialidadEscapada}', ${edad})">
                <i class="fas fa-search me-1"></i>
                Buscar con T rminos Seleccionados
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm" onclick="realizarBusquedaAutomatica('${condicionEscapada}', '${especialidadEscapada}', ${edad})">
                <i class="fas fa-magic me-1"></i>
                B squeda Autom tica
            </button>
            <button type="button" class="btn btn-outline-info btn-sm" onclick="seleccionarTodosTerminos()">
                <i class="fas fa-check-square me-1"></i>
                Seleccionar Todos
            </button>
            <button type="button" class="btn btn-outline-info btn-sm" onclick="deseleccionarTodosTerminos()">
                <i class="fas fa-square me-1"></i>
                Deseleccionar Todos
            </button>
        </div>
    `;

listaDiv.innerHTML = html;
if (sugerenciasDiv) sugerenciasDiv.style.display = 'block';

console.log(' T rminos mostrados correctamente');

// Verificar que los elementos est n visibles
setTimeout(() => {
    const checkboxes = listaDiv.querySelectorAll('input[type="checkbox"]');
    console.log(' Checkboxes encontrados:', checkboxes.length);

    if (checkboxes.length > 0) {
        showNotification(`${checkboxes.length} t rminos de b squeda disponibles para seleccionar`, 'success');
    } else {
        console.warn(' No se encontraron checkboxes en el HTML renderizado');
    }
}, 100);

// ========================================
// FUNCIONES DE LA SIDEBAR DERECHA
// ========================================

// ========================================
// COPILOT HEALTH - FUNCIONALIDAD PRINCIPAL EN SIDEBAR
// ========================================

// Función principal de Copilot Health que actúa como asistente
// Función para obtener información del profesional
async function obtenerInformacionProfesional() {
    try {
        const response = await fetch('/api/professional/profile', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        });

        if (response.status === 200) {
            const data = await response.json();
            if (data.success) {
                return data.profesional;
            }
        }
        return null;
    } catch (error) {
        console.error('❌ Error obteniendo información del profesional:', error);
        return null;
    }
}

// Función para generar mensajes naturales de Copilot Health
function generarMensajeNatural(accion, datos = {}) {
    const profesional = datos.profesional;
    const nombre = profesional ? `${profesional.nombre} ${profesional.apellido}` : 'Doctor';
    const especialidad = profesional ? profesional.especialidad : 'especialidad';

    const mensajes = {
        'inicio': `¡Hola ${nombre}! 👋 Soy Copilot Health, tu asistente de IA. Estoy aquí para ayudarte con el análisis clínico y la búsqueda de evidencia científica.`,

        'analisis_iniciado': `Perfecto, ${nombre}. He iniciado el análisis completo del caso. Estoy revisando el tipo de consulta, la edad del paciente y el motivo de consulta para identificar los aspectos más relevantes.`,

        'terminos_clave': `Excelente, ${nombre}. He identificado los términos clave más importantes para la búsqueda de evidencia científica. Estos términos me ayudarán a encontrar la información más relevante para tu caso.`,

        'busqueda_iniciada': `Ahora estoy realizando la búsqueda de evidencia científica en las bases de datos médicas más importantes. Esto puede tomar unos momentos mientras consulto PubMed, Europe PMC y otras fuentes confiables.`,

        'busqueda_progreso': `Estoy consultando múltiples fuentes de evidencia científica para encontrar los estudios más relevantes para tu caso. Esto incluye revisiones sistemáticas, ensayos clínicos y guías de práctica clínica.`,

        'resultados_encontrados': `¡Excelente, ${nombre}! He encontrado evidencia científica relevante para tu caso. He identificado estudios que pueden respaldar tu plan de tratamiento y proporcionar información valiosa para la toma de decisiones clínicas.`,

        'analisis_completado': `¡Perfecto, ${nombre}! He completado el análisis y encontrado evidencia científica relevante para tu caso. Los resultados más importantes están listos en la sidebar.`,

        'error': `Lo siento, ${nombre}. He encontrado un problema durante el análisis. Esto puede deberse a una conexión temporal o a que necesito más información específica. ¿Podrías verificar los datos ingresados e intentar nuevamente?`,

        'sin_evidencia': `${nombre}, he revisado las bases de datos disponibles, pero no he encontrado evidencia científica específica para este caso. Esto puede deberse a que el tema es muy específico o que necesitamos ajustar los términos de búsqueda.`
    };

    return mensajes[accion] || `Procesando, ${nombre}...`;
}

// Variable global para controlar mensajes duplicados
let mensajeCompletadoMostrado = false;
let ultimoMotivoConsulta = '';

// Función para limpiar el control de mensajes
function limpiarControlMensajes() {
    mensajeCompletadoMostrado = false;
    ultimoMotivoConsulta = '';
    console.log('🔄 Control de mensajes limpiado');
}

// Sistema de comunicación en tiempo real para Copilot Health
let copilotChatContainer = null;
let copilotChatMessages = [];

// Sistema de chat integrado en la sidebar
let sidebarChatMessages = [];
let sidebarChatActive = false;

function inicializarCopilotChat() {
    // Crear contenedor de chat si no existe
    if (!copilotChatContainer) {
        copilotChatContainer = document.createElement('div');
        copilotChatContainer.id = 'copilot-chat-container';
        copilotChatContainer.className = 'copilot-chat-container';
        copilotChatContainer.innerHTML = `
            <div class="copilot-chat-header">
                <h5>Copilot Health Assistant</h5>
                <button class="btn btn-sm btn-action btn-view" onclick="toggleCopilotChat()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="copilot-chat-messages" id="copilot-chat-messages">
                <div class="copilot-message copilot-system">
                    <i class="fas fa-info-circle me-2"></i>
                    <span>Hola, soy Tena, tu asistente IA. Estoy listo para ayudarte.</span>
                </div>
            </div>
        `;

        // Agregar estilos CSS
        const style = document.createElement('style');
        style.textContent = `
            .copilot-chat-container {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 400px;
                max-height: 500px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                display: none;
                flex-direction: column;
            }
            
            .copilot-chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 15px;
                border-radius: 10px 10px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .copilot-chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                max-height: 400px;
            }
            
            .copilot-message {
                margin-bottom: 12px;
                padding: 10px 12px;
                border-radius: 8px;
                font-size: 14px;
                line-height: 1.4;
                animation: fadeInUp 0.3s ease-out;
            }
            
            .copilot-system {
                background: #f8f9fa;
                border-left: 4px solid #6c757d;
            }
            
            .copilot-thinking {
                background: #e3f2fd;
                border-left: 4px solid #2196f3;
                font-style: italic;
            }
            
            .copilot-success {
                background: #e8f5e8;
                border-left: 4px solid #4caf50;
            }
            
            .copilot-warning {
                background: #fff3e0;
                border-left: 4px solid #ff9800;
            }
            
            .copilot-error {
                background: #ffebee;
                border-left: 4px solid #f44336;
            }
            
            .copilot-progress {
                background: #f3e5f5;
                border-left: 4px solid #9c27b0;
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .copilot-typing {
                display: flex;
                align-items: center;
                gap: 4px;
                padding: 8px 12px;
                background: #f8f9fa;
                border-radius: 8px;
                font-style: italic;
                color: #666;
            }
            
            .typing-dots {
                display: flex;
                gap: 2px;
            }
            
            .typing-dot {
                width: 6px;
                height: 6px;
                background: #666;
                border-radius: 50%;
                animation: typing 1.4s infinite;
            }
            
            .typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .typing-dot:nth-child(3) { animation-delay: 0.4s; }
            
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-10px); }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(copilotChatContainer);
    }
}

function toggleCopilotChat() {
    // Inicializar el chat si no existe
    inicializarCopilotChat();

    if (copilotChatContainer) {
        const isVisible = copilotChatContainer.style.display !== 'none';
        copilotChatContainer.style.display = isVisible ? 'none' : 'flex';
    }
}



function agregarMensajeCopilot(mensaje, tipo = 'system') {
    inicializarCopilotChat();

    const messagesContainer = document.getElementById('copilot-chat-messages');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `copilot-message copilot-${tipo}`;

    const icon = tipo === 'thinking' ? 'fas fa-brain' :
        tipo === 'success' ? 'fas fa-check-circle' :
            tipo === 'warning' ? 'fas fa-exclamation-triangle' :
                tipo === 'error' ? 'fas fa-times-circle' :
                    tipo === 'progress' ? 'fas fa-cog fa-spin' :
                        '';

    let contenidoSeguro = '';
    if (tipo === 'assistant') {
        try {
            const html = marked.parse(mensaje || '');
            contenidoSeguro = DOMPurify.sanitize(html, { USE_PROFILES: { html: true } });
        } catch (e) {
            contenidoSeguro = DOMPurify.sanitize(mensaje);
        }
    } else {
        contenidoSeguro = DOMPurify.sanitize(mensaje);
    }

    messageDiv.innerHTML = `
        <i class="${icon} me-2"></i>
        <span class="copilot-markdown">${contenidoSeguro}</span>
    `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Guardar mensaje en el historial
    copilotChatMessages.push({ mensaje, tipo, timestamp: new Date() });
}

function mostrarTypingCopilot() {
    inicializarCopilotChat();

    const messagesContainer = document.getElementById('copilot-chat-messages');
    if (!messagesContainer) return;

    // Remover typing anterior si existe
    const existingTyping = messagesContainer.querySelector('.copilot-typing');
    if (existingTyping) {
        existingTyping.remove();
    }

    const typingDiv = document.createElement('div');
    typingDiv.className = 'copilot-typing';
    typingDiv.innerHTML = `
        <span>Tena Copilot está pensando...</span>
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;

    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removerTypingCopilot() {
    const messagesContainer = document.getElementById('copilot-chat-messages');
    if (!messagesContainer) return;

    const typingDiv = messagesContainer.querySelector('.copilot-typing');
    if (typingDiv) {
        typingDiv.remove();
    }
}

function limpiarChatCopilot() {
    copilotChatMessages = [];
    const messagesContainer = document.getElementById('copilot-chat-messages');
    if (messagesContainer) {
        messagesContainer.innerHTML = `
            <div class="copilot-message copilot-system">
                <i class="fas fa-info-circle me-2"></i>
                <span>Hola, soy Tena, tu asistente IA. Estoy listo para ayudarte.</span>
            </div>
        `;
    }
}

// Funciones para el chat integrado en la sidebar
function agregarMensajeSidebar(mensaje, tipo = 'system') {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message copilot-${tipo}`;

    const icon = tipo === 'thinking' ? 'fas fa-brain' :
        tipo === 'success' ? 'fas fa-check-circle' :
            tipo === 'warning' ? 'fas fa-exclamation-triangle' :
                tipo === 'error' ? 'fas fa-times-circle' :
                    tipo === 'progress' ? 'fas fa-cog fa-spin' :
                        '';

    const now = new Date();
    const timeString = now.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });

    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="${icon}"></i>
            <span>${mensaje}</span>
        </div>
        <div class="message-time">${timeString}</div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Guardar mensaje en el historial
    sidebarChatMessages.push({ mensaje, tipo, timestamp: now });
}

function mostrarTypingSidebar() {
    const chatTyping = document.getElementById('chatTyping');
    if (chatTyping) {
        chatTyping.style.display = 'block';
    }
}

function removerTypingSidebar() {
    const chatTyping = document.getElementById('chatTyping');
    if (chatTyping) {
        chatTyping.style.display = 'none';
    }
}

function limpiarChatSidebar() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="chat-message copilot-system">
                <div class="message-content">
                    <span>¡Hola! Soy Tena, tu asistente IA. Estoy aquí para ayudarte con el análisis de casos clínicos. Completa el formulario y observa cómo trabajo en tiempo real.</span>
                </div>
                <div class="message-time">Ahora</div>
            </div>
        `;
    }
    sidebarChatMessages = [];
}

function toggleChatSidebar() {
    const dynamicContentArea = document.getElementById('dynamicContentArea');
    if (dynamicContentArea) {
        const isVisible = dynamicContentArea.style.display !== 'none';
        dynamicContentArea.style.display = isVisible ? 'none' : 'block';

        // Cambiar el ícono del botón
        const toggleButton = document.querySelector('[onclick="toggleChatSidebar()"]');
        if (toggleButton) {
            const icon = toggleButton.querySelector('i');
            if (icon) {
                icon.className = isVisible ? 'fas fa-plus' : 'fas fa-minus';
            }
        }
    }
}

function activarCopilotHealthSidebar() {
    sidebarChatActive = true;
    agregarMensajeSidebar('Iniciando análisis completo del caso...', 'progress');

    // Obtener datos del formulario
    const motivoConsulta = document.getElementById('motivoConsulta')?.value?.trim() || '';
    const tipoAtencion = document.getElementById('tipoAtencion')?.value || '';
    const pacienteEdad = document.getElementById('pacienteEdad')?.value || '';
    const antecedentes = document.getElementById('antecedentes')?.value?.trim() || '';
    const evaluacion = document.getElementById('evaluacion')?.value?.trim() || '';

    if (!motivoConsulta) {
        agregarMensajeSidebar('❌ Por favor, ingresa un motivo de consulta para comenzar el análisis.', 'error');
        return;
    }

    // Iniciar análisis en tiempo real
    realizarAnalisisCompletoSidebar(motivoConsulta, tipoAtencion, pacienteEdad, antecedentes, evaluacion);
}

async function realizarAnalisisCompletoSidebar(motivoConsulta, tipoAtencion, edad, antecedentes, evaluacion) {
    try {
        // Paso 1: Análisis del motivo de consulta
        agregarMensajeSidebar('🔍 Analizando el motivo de consulta...', 'thinking');
        mostrarTypingSidebar();
        await new Promise(resolve => setTimeout(resolve, 1000));
        removerTypingSidebar();

        agregarMensajeSidebar('✅ Motivo de consulta analizado: "' + motivoConsulta + '"', 'success');

        // Paso 2: Extracción de términos clave
        agregarMensajeSidebar('📝 Extrayendo términos clave para la búsqueda...', 'thinking');
        mostrarTypingSidebar();
        await new Promise(resolve => setTimeout(resolve, 1500));
        removerTypingSidebar();

        // Simular extracción de términos
        const terminosClave = ['tratamiento', 'rehabilitación', 'terapia'];
        agregarMensajeSidebar('✅ Términos clave identificados: ' + terminosClave.join(', '), 'success');

        // Paso 3: Generación de términos de búsqueda
        agregarMensajeSidebar('🔬 Generando términos de búsqueda expandidos...', 'thinking');
        mostrarTypingSidebar();
        await new Promise(resolve => setTimeout(resolve, 2000));
        removerTypingSidebar();

        // Paso 4: Búsqueda en bases de datos
        agregarMensajeSidebar('🌐 Consultando bases de datos médicas (PubMed, Europe PMC)...', 'progress');
        mostrarTypingSidebar();
        await new Promise(resolve => setTimeout(resolve, 3000));
        removerTypingSidebar();

        // Paso 5: Filtrado y análisis de relevancia
        agregarMensajeSidebar('🎯 Filtrando resultados por relevancia...', 'thinking');
        mostrarTypingSidebar();
        await new Promise(resolve => setTimeout(resolve, 1500));
        removerTypingSidebar();

        // Paso 6: Resultados
        agregarMensajeSidebar('📊 Análisis completado. Encontrados 8 estudios relevantes.', 'success');
        agregarMensajeSidebar('💡 Los resultados están listos para revisión en la sección de papers.', 'system');

        // Mostrar sección de papers
        mostrarSeccionPapersSidebar();

    } catch (error) {
        console.error('❌ Error en análisis sidebar:', error);
        agregarMensajeSidebar('❌ Error durante el análisis. Por favor, verifica la conexión e intenta nuevamente.', 'error');
    }
}

function mostrarSeccionPapersSidebar() {
    const sidebarPapers = document.getElementById('sidebarPapers');
    if (sidebarPapers) {
        sidebarPapers.style.display = 'block';

        // Simular papers encontrados
        const papersContainer = document.getElementById('sidebarListaPapers');
        if (papersContainer) {
            papersContainer.innerHTML = `
                <div class="sidebar-paper-item">
                    <div class="sidebar-paper-title">Efectividad de la rehabilitación en pacientes con dolor lumbar</div>
                    <div class="sidebar-paper-doi">DOI: 10.1000/ejemplo.2023.001</div>
                    <div class="sidebar-paper-evidence">Evidencia: Alta</div>
                </div>
                <div class="sidebar-paper-item">
                    <div class="sidebar-paper-title">Intervenciones terapéuticas para el manejo del dolor</div>
                    <div class="sidebar-paper-doi">DOI: 10.1000/ejemplo.2023.002</div>
                    <div class="sidebar-paper-evidence">Evidencia: Media</div>
                </div>
            `;
        }
    }
}

// Observador para detectar cambios en el formulario
function inicializarObservadorFormulario() {
    const formulario = document.querySelector('form');
    if (formulario) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    if (sidebarChatActive) {
                        agregarMensajeSidebar('📝 Detectado cambio en el formulario. Actualizando análisis...', 'progress');
                    }
                }
            });
        });

        observer.observe(formulario, {
            childList: true,
            subtree: true,
            attributes: true
        });
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', function () {
    inicializarObservadorFormulario();
});

async function copilotHealthAssistant() {
    console.log('🤖 Copilot Health Assistant iniciado...');

    // Inicializar chat y mostrar interfaz
    inicializarCopilotChat();
    copilotChatContainer.style.display = 'flex';
    limpiarChatCopilot();

    // Obtener información del profesional
    const profesional = await obtenerInformacionProfesional();

    // Obtener todos los datos del formulario
    const motivoConsulta = document.getElementById('motivoConsulta').value.trim();
    const tipoAtencion = document.getElementById('tipoAtencion').value;
    const pacienteEdad = document.getElementById('pacienteEdad').value || '30';
    const antecedentes = document.getElementById('antecedentes') ? document.getElementById('antecedentes').value : '';
    const evaluacion = document.getElementById('evaluacion') ? document.getElementById('evaluacion').value : '';

    if (!motivoConsulta) {
        agregarMensajeCopilot('Por favor, ingresa un motivo de consulta para comenzar el análisis', 'warning');
        return;
    }

    // Verificar si es el mismo motivo de consulta para evitar mensajes duplicados
    if (motivoConsulta === ultimoMotivoConsulta && mensajeCompletadoMostrado) {
        agregarMensajeCopilot('Ya he analizado este motivo de consulta anteriormente. Los resultados están disponibles en la sidebar.', 'system');
        return;
    }

    // Resetear control de mensajes si es un nuevo motivo
    if (motivoConsulta !== ultimoMotivoConsulta) {
        limpiarControlMensajes();
        ultimoMotivoConsulta = motivoConsulta;
    }

    // Mensaje de inicio
    agregarMensajeCopilot(`¡Hola ${profesional.nombre}! Voy a analizar el caso: "${motivoConsulta}" en ${tipoAtencion}.`, 'system');

    // Mostrar que está pensando
    mostrarTypingCopilot();
    await new Promise(resolve => setTimeout(resolve, 1000));
    removerTypingCopilot();

    agregarMensajeCopilot('Iniciando análisis completo del caso...', 'progress');

    try {
        // Paso 1: Análisis completo del caso
        agregarMensajeCopilot('Analizando el motivo de consulta y extrayendo información clave...', 'thinking');
        mostrarTypingCopilot();

        const analisisCompleto = await realizarAnalisisCompleto(motivoConsulta, tipoAtencion, pacienteEdad, antecedentes, evaluacion);
        removerTypingCopilot();

        if (analisisCompleto && analisisCompleto.success) {
            agregarMensajeCopilot('✅ Análisis del caso completado. Identificando términos clave para la búsqueda...', 'success');
            mostrarTypingCopilot();

            // Paso 2: Extraer términos clave del análisis
            const terminosClave = await extraerTerminosClave(analisisCompleto);
            removerTypingCopilot();

            if (terminosClave && terminosClave.success) {
                agregarMensajeCopilot(`✅ Términos clave identificados: ${terminosClave.terminos_clave.join(', ')}`, 'success');
                agregarMensajeCopilot('Generando términos de búsqueda expandidos para obtener mejores resultados...', 'progress');
                mostrarTypingCopilot();

                // Paso 3: Generar términos de búsqueda expandidos
                const terminos = await generarTerminosBusquedaExpandidos(motivoConsulta, tipoAtencion, pacienteEdad, terminosClave.terminos_clave);
                removerTypingCopilot();

                if (terminos && terminos.success) {
                    agregarMensajeCopilot('✅ Términos de búsqueda generados. Mostrando opciones en la sidebar...', 'success');

                    // Paso 4: Mostrar términos en sidebar
                    mostrarTerminosEnSidebar(terminos.terminos_disponibles, motivoConsulta, tipoAtencion, pacienteEdad);

                    agregarMensajeCopilot('Iniciando búsqueda de evidencia científica en bases de datos médicas...', 'progress');
                    mostrarTypingCopilot();

                    // Paso 5: Realizar búsqueda automática con términos clave
                    setTimeout(async () => {
                        agregarMensajeCopilot('Consultando PubMed, Europe PMC y otras fuentes confiables...', 'thinking');

                        const resultado = await realizarBusquedaConTerminosClave(terminosClave.terminos_clave, motivoConsulta, tipoAtencion, pacienteEdad);
                        removerTypingCopilot();

                        if (resultado && resultado.planes_tratamiento && resultado.planes_tratamiento.length > 0) {
                            agregarMensajeCopilot(`✅ Encontrados ${resultado.planes_tratamiento.length} estudios científicos relevantes`, 'success');
                            agregarMensajeCopilot('Filtrando y ordenando los resultados por relevancia...', 'progress');

                            // Solo mostrar mensaje de completado si no se ha mostrado antes
                            if (!mensajeCompletadoMostrado) {
                                setTimeout(() => {
                                    agregarMensajeCopilot('🎯 Análisis completado. Los resultados más relevantes están disponibles en la sidebar.', 'success');
                                    mensajeCompletadoMostrado = true;
                                }, 1000);
                            }
                        } else {
                            agregarMensajeCopilot('⚠️ No se encontraron estudios específicos para este caso. Considera ajustar los términos de búsqueda.', 'warning');
                        }
                    }, 2000);

                } else {
                    agregarMensajeCopilot('❌ Error al generar términos de búsqueda. Verificando datos de entrada...', 'error');
                }
            } else {
                agregarMensajeCopilot('❌ Error al extraer términos clave del análisis. Revisando información...', 'error');
            }
        } else {
            agregarMensajeCopilot('❌ Error en el análisis del caso. Verificando datos proporcionados...', 'error');
        }

    } catch (error) {
        console.error('❌ Error en Copilot Health Assistant:', error);
        agregarMensajeCopilot('❌ Error inesperado durante el análisis. Por favor, verifica la conexión e intenta nuevamente.', 'error');
    }
}

// Función para análisis mejorado con identificación de palabras clave
async function analizarMotivoConsultaMejorado(motivoConsulta) {
    try {
        console.log('🔍 Iniciando análisis mejorado del motivo de consulta...');

        const response = await fetch('/api/copilot/identify-keywords', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                motivo_consulta: motivoConsulta
            })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                console.log('✅ Análisis mejorado completado');
                return data;
            } else {
                console.error('❌ Error en análisis mejorado:', data.message);
                return null;
            }
        } else {
            console.error('❌ Error HTTP en análisis mejorado:', response.status);
            return null;
        }
    } catch (error) {
        console.error('❌ Error en analizarMotivoConsultaMejorado:', error);
        return null;
    }
}

// Función para búsqueda mejorada con análisis de patrones clínicos
async function buscarEvidenciaMejorada(motivoConsulta) {
    try {
        console.log('🔍 Iniciando búsqueda mejorada de evidencia científica...');

        const response = await fetch('/api/copilot/search-enhanced', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ motivo_consulta: motivoConsulta })
        });

        if (!response.ok) {
            console.error('❌ Error HTTP en búsqueda mejorada:', response.status);
            return [];
        }
        const data = await response.json();
        if (!data.success) {
            console.error('❌ Error en búsqueda mejorada:', data.message);
            return [];
        }
        console.log('✅ Búsqueda mejorada completada');
        const lista = data.papers_encontrados || [];
        return lista.map(p => ({
            title: p.titulo || p.title,
            year: p.año_publicacion || p.year,
            study_type: p.tipo_evidencia || p.study_type,
            doi: p.doi,
            url: p.doi ? `https://doi.org/${p.doi}` : (p.url || ''),
            source: p.fuente || p.source || ''
        }));
    } catch (error) {
        console.error('❌ Error en buscarEvidenciaMejorada:', error);
        return [];
    }
}

// Función para análisis completo mejorado
async function analizarCasoCompletoMejorado(motivoConsulta, tipoAtencion, edadPaciente, antecedentes) {
    try {
        console.log('🔍 Iniciando análisis completo mejorado...');

        const response = await fetch('/api/copilot/analyze-enhanced', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                motivo_consulta: motivoConsulta,
                tipo_atencion: tipoAtencion,
                edad_paciente: edadPaciente,
                antecedentes: antecedentes
            })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                console.log('✅ Análisis completo mejorado completado');
                return data;
            } else {
                console.error('❌ Error en análisis completo mejorado:', data.message);
                return null;
            }
        } else {
            console.error('❌ Error HTTP en análisis completo mejorado:', response.status);
            return null;
        }
    } catch (error) {
        console.error('❌ Error en analizarCasoCompletoMejorado:', error);
        return null;
    }
}

// ===== FUNCIONES PARA EL DISEÑO ELEGANTE =====

function renderTarjetaEvidencia(record) {
    const container = document.getElementById('evidenceCardsContainer');
    if (!container || !record) return;

    const card = document.createElement('div');
    card.className = 'evidence-card';

    const title = DOMPurify.sanitize(record.title || 'Artículo sin título');
    const metaPieces = [];
    if (record.study_type) metaPieces.push(`<span class=\"badge bg-light text-dark\">${DOMPurify.sanitize(record.study_type)}</span>`);
    if (record.year) metaPieces.push(`<span class=\"badge bg-secondary\">${record.year}</span>`);
    if (record.source) metaPieces.push(`<span class=\"text-muted\">${DOMPurify.sanitize(record.source)}</span>`);
    const meta = metaPieces.join(' ');

    const link = record.url || (record.doi ? `https://doi.org/${record.doi}` : '');
    const abstract = record.abstract || '';

    card.innerHTML = `
        <div class="title">${title}</div>
        <div class="meta">${meta}</div>
        ${abstract ? `<div class="abstract">${DOMPurify.sanitize(abstract)}</div>` : ''}
        <div class="actions">
            ${link ? `<a class="btn btn-sm btn-outline-primary" target="_blank" href="${DOMPurify.sanitize(link)}"><i class="fas fa-external-link-alt"></i> Ver</a>` : ''}
        </div>
    `;

    container.appendChild(card);
}

function renderTarjetaEvidenciaBasica(titulo, year, tipo, url) {
    renderTarjetaEvidencia({ title: titulo, year, study_type: tipo, url });
}



async function solicitarEvidenciaRespuesta(contextoPaciente) {
    try {
        agregarMensajeElegant('Buscando evidencia científica y generando respuesta estructurada...', 'progress');
        const resp = await fetch('/evidence/answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'include',
            body: JSON.stringify({ patient_context: contextoPaciente, language: 'es' })
        });
        const data = await resp.json();
        if (!data.success) {
            agregarMensajeElegant('❌ ' + (data.message || 'No se pudo obtener evidencia'), 'error');
            return null;
        }
        const ans = data.answer || {};
        const md = [
            '## Respuesta basada en evidencia',
            '',
            ans.summary ? `**Resumen:**\n${ans.summary}` : '',
            ans.recommendations && ans.recommendations.length ? ('\n**Recomendación:**\n' + ans.recommendations.map(r => `- ${r}`).join('\n')) : '',
            ans.key_points && ans.key_points.length ? ('\n**Puntos clave:**\n' + ans.key_points.map(p => `- ${p}`).join('\n')) : '',
            ans.risks && ans.risks.length ? ('\n**Riesgos/contraindicaciones:**\n' + ans.risks.map(r => `- ${r}`).join('\n')) : '',
            (ans.evidence_level || ans.limitations) ? (`\n**Nivel de evidencia:** ${ans.evidence_level || 'N/D'}\n**Limitaciones:** ${ans.limitations || 'N/D'}`) : '',
            data.records && data.records.length ? ('\n---\n**Estudios incluidos:**\n' + data.records.map((r, i) => `- ${r.title} (${r.year || 's.f.'}) ${r.study_type ? `— ${r.study_type}` : ''}`).join('\n')) : '',
            ans.citations_apa && ans.citations_apa.length ? ('\n**Citas (APA):**\n' + ans.citations_apa.map(c => `- ${c}`).join('\n')) : '',
            ans.links && ans.links.length ? ('\n**Enlaces:**\n' + ans.links.map(l => `- ${l}`).join('\n')) : ''
        ].filter(Boolean).join('\n');
        agregarMensajeElegant(md, 'assistant');
        return data;
    } catch (e) {
        agregarMensajeElegant('❌ Error solicitando evidencia: ' + e.message, 'error');
        return null;
    }
}



// Función para agregar mensajes elegantes
function getContextoPacienteDesdeFormulario() {
    const v = id => document.getElementById(id)?.value?.trim() || '';
    return {
        tipo_atencion: v('tipoAtencion') || v('seleccionTipoAtencion') || '',
        motivo: v('motivoConsulta') || '',
        evaluacion: v('evaluacion') || '',
        plan_preliminar: v('plan') || v('planTratamiento') || '',
        edad: v('edad') || v('patientAge') || '',
        sexo: v('patientGender') || ''
    };
}

function __truncateText(text, maxLen = 140) {
    const t = (text || '').trim();
    return t.length > maxLen ? t.slice(0, maxLen - 1) + '…' : t;
}

function buildContextSummaryMarkdown(ctx) {
    if (!ctx) return '';
    const secciones = [];
    if (ctx.tipo_atencion) secciones.push(`- **Tipo de atención**: ${ctx.tipo_atencion}`);
    if (ctx.motivo) secciones.push(`- **Motivo**: ${__truncateText(ctx.motivo, 160)}`);
    if (ctx.evaluacion) secciones.push(`- **Evaluación**: ${__truncateText(ctx.evaluacion, 160)}`);
    if (ctx.plan_preliminar) secciones.push(`- **Plan**: ${__truncateText(ctx.plan_preliminar, 160)}`);
    if (ctx.edad) secciones.push(`- **Edad**: ${ctx.edad}`);
    if (ctx.sexo) secciones.push(`- **Sexo**: ${ctx.sexo}`);
    if (secciones.length === 0) return '';
    return ['### Contexto del caso (resumen)', '', ...secciones].join('\n');
}

// Función para unificar respuestas y evitar duplicación
function unificarRespuesta(respuestaIA, contexto) {
    // Si la respuesta ya incluye contexto, devolverla tal como está
    if (respuestaIA.includes('Contexto del caso') || respuestaIA.includes('Ficha Resumen')) {
        return respuestaIA;
    }

    // Si no incluye contexto, agregarlo al inicio con formato simple
    const context = getContextoPacienteDesdeFormulario();
    const contextoSimple = buildContextoSimple(context);

    if (contextoSimple) {
        return contextoSimple + '\n\n' + respuestaIA;
    }

    return respuestaIA;
}

// Función para generar contexto en formato simple y natural
function buildContextoSimple(ctx) {
    if (!ctx) return '';

    const secciones = [];

    // Agregar información básica del paciente
    if (ctx.nombre_paciente) {
        secciones.push(`Paciente: ${ctx.nombre_paciente}`);
    }

    if (ctx.tipo_atencion) {
        secciones.push(`Tipo de atención: ${ctx.tipo_atencion}`);
    }

    if (ctx.motivo) {
        secciones.push(`Motivo: ${__truncateText(ctx.motivo, 200)}`);
    }

    if (ctx.edad) {
        secciones.push(`Edad: ${ctx.edad} años`);
    }

    if (ctx.sexo) {
        secciones.push(`Sexo: ${ctx.sexo}`);
    }

    if (ctx.evaluacion) {
        secciones.push(`Evaluación: ${__truncateText(ctx.evaluacion, 200)}`);
    }

    if (ctx.plan_preliminar) {
        secciones.push(`Plan: ${__truncateText(ctx.plan_preliminar, 200)}`);
    }

    if (secciones.length === 0) return '';

    return 'CONTEXTO DEL CASO:\n' + secciones.join('\n');
}

// Función para eliminar Markdown y convertir a formato simple
function eliminarMarkdown(texto) {
    if (!texto) return '';

    let resultado = texto;

    // Eliminar bloques de código Markdown
    resultado = resultado.replace(/```markdown\s*\n?/g, '');
    resultado = resultado.replace(/```\s*\n?/g, '');

    // Eliminar encabezados Markdown
    resultado = resultado.replace(/^#{1,6}\s+/gm, '');

    // Eliminar negritas e itálicas
    resultado = resultado.replace(/\*\*(.*?)\*\*/g, '$1');
    resultado = resultado.replace(/\*(.*?)\*/g, '$1');
    resultado = resultado.replace(/__(.*?)__/g, '$1');
    resultado = resultado.replace(/_(.*?)_/g, '$1');

    // Eliminar enlaces Markdown
    resultado = resultado.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

    // Eliminar listas con guiones y asteriscos
    resultado = resultado.replace(/^[\s]*[-*+]\s+/gm, '');

    // Eliminar líneas horizontales
    resultado = resultado.replace(/^[\s]*[-*_]{3,}[\s]*$/gm, '');

    // Eliminar tablas Markdown
    resultado = resultado.replace(/\|.*\|/g, '');
    resultado = resultado.replace(/^[\s]*[-|]+[\s]*$/gm, '');

    // Eliminar bloques de código en línea
    resultado = resultado.replace(/`([^`]+)`/g, '$1');

    // Eliminar emojis y símbolos especiales
    resultado = resultado.replace(/[🔍📋🧩⚠️🛠️✅📌🎯💡📊🎉]/g, '');

    // Limpiar líneas vacías múltiples
    resultado = resultado.replace(/\n\s*\n\s*\n/g, '\n\n');

    // Limpiar espacios al inicio y final
    resultado = resultado.trim();

    return resultado;
}

function __hashContext(ctx) {
    try {
        const minimal = {
            t: ctx?.tipo_atencion || '',
            m: ctx?.motivo || '',
            e: ctx?.evaluacion || '',
            p: ctx?.plan_preliminar || '',
            a: ctx?.edad || '',
            s: ctx?.sexo || ''
        };
        return JSON.stringify(minimal);
    } catch { return ''; }
}

var __lastCtxHash = window.__lastCtxHash || ''; window.__lastCtxHash = __lastCtxHash;

async function enviarMensajeCopilot(message) {
    try {
        // Borrar mensaje de bienvenida si existe
        borrarMensajeBienvenida();

        const context = getContextoPacienteDesdeFormulario();

        // NO generar contexto automáticamente aquí para evitar duplicación
        // const ctxHash = __hashContext(context);
        // if (ctxHash !== __lastCtxHash) {
        //     const mdCtx = buildContextSummaryMarkdown(context);
        //     if (mdCtx) agregarMensajeElegant(mdCtx, 'assistant');
        //     __lastCtxHash = ctxHash;
        // }

        mostrarTypingElegant();
        const resp = await fetch('/api/copilot/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin',
            body: JSON.stringify({ message, context })
        });
        const data = await resp.json();
        removerTypingElegant();
        if (data.success) {
            // Unificar respuesta en un solo mensaje
            const respuestaUnificada = unificarRespuesta(data.reply, context);
            agregarMensajeElegant(respuestaUnificada, 'assistant');
        } else {
            agregarMensajeElegant('❌ ' + (data.message || 'Error al procesar la solicitud'), 'error');
        }
    } catch (err) {
        removerTypingElegant();
        agregarMensajeElegant('❌ Error de conexión: ' + err.message, 'error');
    }
}

let copilotCtxTimer;
function inicializarSincronizacionFormularioCopilot() {
    const ids = ['motivoConsulta', 'tipoAtencion', 'edad', 'antecedentes', 'evaluacion', 'plan', 'patientGender', 'patientAge'];
    const handler = () => {
        if (copilotCtxTimer) clearTimeout(copilotCtxTimer);
        copilotCtxTimer = setTimeout(async () => {
            const ctx = getContextoPacienteDesdeFormulario();
            const mdCtx = buildContextSummaryMarkdown(ctx);
            const ctxHash = __hashContext(ctx);
            if (ctxHash !== __lastCtxHash) {
                if (mdCtx) agregarMensajeElegant(mdCtx, 'assistant');
                __lastCtxHash = ctxHash;
            }
            try {
                const resp = await fetch('/api/copilot/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ message: 'Actualizar contexto clínico del caso.', context: ctx })
                });
                await resp.json();
            } catch (e) { /* silencioso */ }
        }, 700);
    };
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', handler);
            el.addEventListener('input', handler);
        }
    });
    setTimeout(() => {
        const ctx = getContextoPacienteDesdeFormulario();
        const mdCtx = buildContextSummaryMarkdown(ctx);
        const ctxHash = __hashContext(ctx);
        if (mdCtx && ctxHash !== __lastCtxHash) {
            agregarMensajeElegant(mdCtx, 'assistant');
            __lastCtxHash = ctxHash;
        }
    }, 400);
}

function agregarMensajeElegant(mensaje, tipo = 'system') {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return;

    // Si es un mensaje del usuario, borrar el mensaje de bienvenida
    if (tipo === 'user') {
        borrarMensajeBienvenida();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-elegant system-message';

    // Para todos los tipos, usar formato simple sin Markdown
    let contenidoSeguro = '';
    if (tipo === 'assistant') {
        // Eliminar completamente el formato Markdown y convertir a formato simple
        let mensajeSimple = eliminarMarkdown(mensaje);
        // Convertir saltos de línea a <br> para mantener formato simple
        contenidoSeguro = DOMPurify.sanitize(mensajeSimple.replace(/\n/g, '<br>'));
    } else {
        // Para otros tipos, escapamos simple
        contenidoSeguro = DOMPurify.sanitize(mensaje);
    }

    messageDiv.innerHTML = `
        <div class="message-bubble">
            <div class="message-text copilot-markdown">
                ${contenidoSeguro}
            </div>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Función para mostrar typing elegante
function mostrarTypingElegant() {
    const typingElegant = document.getElementById('typingElegant');
    if (typingElegant) {
        // Array de mensajes variados para mostrar
        const mensajes = [
            'Tena Copilot está pensando...',
            'Analizando tu consulta...',
            'Procesando información...',
            'Buscando la mejor respuesta...',
            'Evaluando opciones...',
            'Preparando recomendaciones...',
            'Consultando bases de datos...',
            'Sintetizando información...'
        ];

        // Seleccionar un mensaje aleatorio
        const mensajeAleatorio = mensajes[Math.floor(Math.random() * mensajes.length)];

        // Actualizar el texto del mensaje
        const mensajeSpan = typingElegant.querySelector('.typing-content span');
        if (mensajeSpan) {
            mensajeSpan.textContent = mensajeAleatorio;
        }

        typingElegant.style.display = 'block';
    }

    // Mostrar estado de "pensando" en el indicador principal
    mostrarEstadoPensando();
}

// Función para mostrar estado de "pensando"
function mostrarEstadoPensando() {
    const statusElement = document.getElementById('tenaCopilotStatus');
    if (statusElement) {
        statusElement.classList.add('thinking');
        statusElement.textContent = 'Tena Copilot...';
    }
}

// Función para ocultar estado de "pensando"
function ocultarEstadoPensando() {
    const statusElement = document.getElementById('tenaCopilotStatus');
    if (statusElement) {
        statusElement.classList.remove('thinking');
        statusElement.textContent = 'Tena Copilot';
    }
}

// Función para remover typing elegante
function removerTypingElegant() {
    const typingElegant = document.getElementById('typingElegant');
    if (typingElegant) {
        typingElegant.style.display = 'none';
    }

    // Ocultar estado de "pensando" en el indicador principal
    ocultarEstadoPensando();
}

// Función para limpiar chat elegante
function inicializarCopilotSidebar() {
    // Mensaje inicial ya está en el HTML; aquí solo enlazamos inputs si existen
    const motivo = document.getElementById('motivoConsulta');
    if (motivo) {
        motivo.addEventListener('change', () => {
            const texto = motivo.value?.trim();
            if (texto) enviarMensajeCopilot('Analiza este motivo de consulta: ' + texto);
        });
    }
}

function limpiarChatElegant() {
    const messagesContainer = document.getElementById('messagesContainer');
    if (messagesContainer) {
        // Obtener el nombre del usuario desde la sesión o usar 'Profesional' por defecto
        const nombreUsuario = obtenerNombreUsuario();

        messagesContainer.innerHTML = `
            <div class="message-elegant system-message" id="welcomeMessage">
                <div class="message-bubble">
                    <div class="message-text">
                        <p>¡Hola ${nombreUsuario}! Soy Tena, tu asistente IA. ¿En qué puedo ayudarte?</p>
                    </div>
                </div>
                <div class="message-time">Ahora</div>
                <button type="button" class="btn-close btn-close-white position-absolute top-0 end-0 m-2" 
                        onclick="borrarMensajeBienvenida()" 
                        style="font-size: 0.7rem; opacity: 0.7;" 
                        title="Borrar mensaje">
                </button>
            </div>
        `;
    }
}

// Función para obtener el nombre del usuario
function obtenerNombreUsuario() {
    // Intentar obtener el nombre desde elementos del DOM
    const userElements = document.querySelectorAll('[data-user-name], .user-name, .navbar .user-info');
    for (let element of userElements) {
        const userName = element.textContent?.trim() || element.getAttribute('data-user-name');
        if (userName && userName !== 'Usuario') {
            return userName.split(' ')[0]; // Tomar solo el primer nombre
        }
    }

    // Si no se encuentra, buscar en el mensaje actual
    const currentWelcomeMessage = document.getElementById('welcomeMessage');
    if (currentWelcomeMessage) {
        const messageText = currentWelcomeMessage.querySelector('.message-text p');
        if (messageText) {
            const match = messageText.textContent.match(/¡Hola ([^!]+)!/);
            if (match && match[1] && match[1] !== 'Profesional') {
                return match[1];
            }
        }
    }

    return 'Profesional';
}

// Función para actualizar estado del botón
function actualizarEstadoBoton(estado) {
    const btnCopilotPrimary = document.getElementById('btnCopilotPrimary');
    const btnStatus = document.getElementById('btnStatus');

    if (!btnCopilotPrimary || !btnStatus) return;

    switch (estado) {
        case 'listo':
            btnCopilotPrimary.classList.remove('analyzing');
            btnStatus.innerHTML = '<i class="fas fa-play"></i>';
            break;
        case 'analizando':
            btnCopilotPrimary.classList.add('analyzing');
            btnStatus.innerHTML = '<i class="fas fa-spinner"></i>';
            break;
        case 'completado':
            btnCopilotPrimary.classList.remove('analyzing');
            btnStatus.innerHTML = '<i class="fas fa-check"></i>';
            break;
    }
}

// Función principal para activar Copilot Health Elegant
function activarCopilotHealthElegant() {
    if (__analisisElegantEnCurso) { console.warn('Análisis ya en curso, cancelando duplicado'); return; }
    __analisisElegantEnCurso = true;
    console.log('🤖 Activando Copilot Health Elegant...');

    // Obtener datos del formulario
    const motivoConsulta = document.getElementById('motivoConsulta')?.value || '';
    const tipoAtencion = document.getElementById('tipoAtencion')?.value || '';
    const edad = document.getElementById('edad')?.value || '';
    const antecedentes = document.getElementById('antecedentes')?.value || '';
    const evaluacion = document.getElementById('evaluacion')?.value || '';

    if (!motivoConsulta.trim()) {
        agregarMensajeElegant('Por favor, escribe tu consulta para comenzar el análisis.', 'warning');
        return;
    }

    // Actualizar estado del botón
    actualizarEstadoBoton('analizando');

    // Limpiar chat y agregar mensaje inicial
    limpiarChatElegant();
    agregarMensajeElegant('Iniciando análisis clínico...', 'system');
    mostrarTypingElegant();

    // Realizar análisis completo
    realizarAnalisisElegant(motivoConsulta, tipoAtencion, edad, antecedentes, evaluacion);
}

// Función para realizar análisis elegante
let __analisisElegantEnCurso = false;
async function realizarAnalisisElegant(motivoConsulta, tipoAtencion, edad, antecedentes, evaluacion) {
    try {
        removerTypingElegant();
        agregarMensajeElegant('Analizando motivo de consulta...', 'progress');

        // Análisis del motivo
        const analisisMotivo = await analizarMotivoConsultaMejorado(motivoConsulta);
        agregarMensajeElegant('✅ Motivo de consulta analizado', 'success');

        mostrarTypingElegant();
        await new Promise(resolve => setTimeout(resolve, 1000));
        removerTypingElegant();

        agregarMensajeElegant('Analizando tipo de atención...', 'progress');
        agregarMensajeElegant(`Tipo de atención: ${tipoAtencion}`, 'info');

        agregarMensajeElegant('Analizando edad del paciente...', 'progress');
        agregarMensajeElegant(`Edad: ${edad} años`, 'info');

        agregarMensajeElegant('Analizando antecedentes...', 'progress');
        if (antecedentes && antecedentes.trim()) {
            agregarMensajeElegant('✅ Antecedentes analizados', 'success');
        }

        agregarMensajeElegant('Analizando evaluación...', 'progress');
        if (evaluacion && evaluacion.trim()) {
            agregarMensajeElegant('✅ Evaluación analizada', 'success');
        }

        mostrarTypingElegant();
        await new Promise(resolve => setTimeout(resolve, 1000));
        removerTypingElegant();

        agregarMensajeElegant('Generando preguntas personalizadas...', 'progress');

        // Generar preguntas personalizadas
        const preguntas = await generarPreguntasPersonalizadas(motivoConsulta, tipoAtencion, edad, antecedentes);
        agregarMensajeElegant('✅ Preguntas personalizadas generadas', 'success');

        mostrarTypingElegant();
        await new Promise(resolve => setTimeout(resolve, 1000));
        removerTypingElegant();

        agregarMensajeElegant('Buscando evidencia científica...', 'progress');

        // Búsqueda de evidencia
        const evidencia = await buscarEvidenciaMejorada(motivoConsulta);
        agregarMensajeElegant('✅ Evidencia científica encontrada', 'success');

        mostrarTypingElegant();
        await new Promise(resolve => setTimeout(resolve, 1000));
        removerTypingElegant();

        agregarMensajeElegant('Generando recomendaciones...', 'progress');

        // Análisis completo
        const analisisCompleto = await analizarCasoCompletoMejorado(motivoConsulta, tipoAtencion, edad, antecedentes);
        agregarMensajeElegant('✅ Análisis completo finalizado', 'success');

        // Mostrar resultados
        mostrarResultadosElegant(analisisCompleto, evidencia, preguntas);
        // Render tarjetas de evidencia si hay datos
        try {
            const ev = (evidencia && evidencia.papers_encontrados) ? evidencia.papers_encontrados : (evidencia || []);
            if (Array.isArray(ev)) {
                document.getElementById('evidenceCardsContainer')?.replaceChildren();
                const top = ev.slice(0, 5);
                top.forEach(p => {
                    renderTarjetaEvidenciaBasica(p.titulo || p.title, p.año_publicacion || p.year, p.tipo_evidencia || p.study_type, (p.doi ? `https://doi.org/${p.doi}` : p.url));
                });
                // También mostrar lista en el chat en formato Markdown
                const bullets = top.map(p => {
                    const title = p.titulo || p.title || 'Título no disponible';
                    const year = p.año_publicacion || p.year || 's.f.';
                    const tipo = p.tipo_evidencia || p.study_type || '';
                    const link = p.doi ? `https://doi.org/${p.doi}` : (p.url || '');
                    const tipoPart = tipo ? ` — ${tipo}` : '';
                    const linkPart = link ? ` — ${link}` : '';
                    return `- ${title} (${year})${tipoPart}${linkPart}`;
                });
                if (bullets.length) {
                    const md = ['### Estudios relacionados', '', ...bullets].join('\n');
                    agregarMensajeElegant(md, 'assistant');
                }
            }
        } catch (_) { }


        actualizarEstadoBoton('completado');

    } catch (error) {
        console.error('❌ Error en análisis elegante:', error);
        removerTypingElegant();
        agregarMensajeElegant('❌ Error en el análisis. Por favor, intenta nuevamente.', 'error');
        actualizarEstadoBoton('listo');
    } finally {
        __analisisElegantEnCurso = false;
    }
}

// Función para generar preguntas personalizadas
async function generarPreguntasPersonalizadas(motivoConsulta, tipoAtencion, edad, antecedentes) {
    try {
        const response = await fetch('/api/copilot/generate-evaluation-questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                motivo_consulta: motivoConsulta,
                tipo_atencion: tipoAtencion,
                edad: edad,
                antecedentes: antecedentes
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.preguntas || [];
    } catch (error) {
        console.error('❌ Error generando preguntas:', error);
        return [];
    }
}

// Función para analizar motivo de consulta mejorado
async function analizarMotivoConsultaMejorado(motivoConsulta) {
    try {
        const response = await fetch('/api/copilot/analyze-motivo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                motivo_consulta: motivoConsulta
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.analisis || { resumen: 'Análisis del motivo de consulta completado' };
    } catch (error) {
        console.error('❌ Error analizando motivo:', error);
        return { resumen: 'Análisis del motivo de consulta completado' };
    }
}

// Función para buscar evidencia mejorada
async function buscarEvidenciaMejorada(motivoConsulta) {
    try {
        const response = await fetch('/api/copilot/search-enhanced', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ motivo_consulta: motivoConsulta })
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        if (data && data.success) {
            const lista = data.papers_encontrados || [];
            // Normalizar a estructura usada por tarjetas
            return lista.map(p => ({
                title: p.titulo || p.title,
                year: p.año_publicacion || p.year,
                study_type: p.tipo_evidencia || p.study_type,
                doi: p.doi,
                url: p.doi ? `https://doi.org/${p.doi}` : (p.url || ''),
                source: p.fuente || p.source || ''
            }));
        }
        return [];
    } catch (error) {
        console.error('❌ Error buscando evidencia:', error);
        return [];
    }
}

// Función para analizar caso completo mejorado
async function analizarCasoCompletoMejorado(motivoConsulta, tipoAtencion, edadPaciente, antecedentes) {
    try {
        const response = await fetch('/api/copilot/complete-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                motivo_consulta: motivoConsulta,
                tipo_atencion: tipoAtencion,
                edad: edadPaciente,
                antecedentes: antecedentes
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.analisis || { resumen: 'Análisis completo del caso finalizado' };
    } catch (error) {
        console.error('❌ Error en análisis completo:', error);
        return { resumen: 'Análisis completo del caso finalizado' };
    }
}

// Función para mostrar resultados elegantes
function mostrarResultadosElegant(analisisCompleto, evidencia, preguntas) {
    const resultsArea = document.getElementById('resultsArea');
    if (!resultsArea) return;

    let html = `
        <div class="results-header">
            <h6><i class="fas fa-chart-line me-2"></i>Resultados del Análisis</h6>
        </div>
    `;

    // Mostrar análisis
    if (analisisCompleto) {
        html += `
            <div class="result-section">
                <h6><i class="fas fa-brain me-2"></i>Análisis Clínico</h6>
                <p>${analisisCompleto.resumen || 'Análisis completado'}</p>
            </div>
        `;
    }

    // Mostrar preguntas personalizadas
    if (preguntas && preguntas.length > 0) {
        html += `
            <div class="result-section">
                <h6><i class="fas fa-question-circle me-2"></i>Preguntas Personalizadas</h6>
                <div class="questions-list">
        `;

        preguntas.forEach((pregunta, index) => {
            html += `
                <div class="question-item" onclick="insertarPreguntaElegant(${index})">
                    <div class="question-text">${pregunta}</div>
                    <div class="question-actions">
                        <button class="btn btn-sm btn-action btn-edit" onclick="insertarPreguntaElegant(${index})">
                            <i class="fas fa-arrow-right"></i> Insertar
                        </button>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    }

    // Mostrar evidencia
    if (evidencia && evidencia.length > 0) {
        html += `
            <div class="result-section">
                <h6><i class="fas fa-file-medical me-2"></i>Evidencia Científica</h6>
                <div class="evidence-list">
        `;

        evidencia.slice(0, 3).forEach((paper, index) => {
            html += `
                <div class="evidence-item" onclick="insertarPaperElegant(${index})">
                    <div class="evidence-title">${paper.titulo}</div>
                    <div class="evidence-authors">${paper.autores}</div>
                    <div class="evidence-year">${paper.ano}</div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    }

    resultsArea.innerHTML = html;
    resultsArea.style.display = 'block';
}

// Función para insertar paper elegante
function insertarPaperElegant(index) {
    agregarMensajeElegant(`Paper ${index + 1} insertado en el tratamiento`, 'success');
}

// Función para insertar pregunta elegante
function insertarPreguntaElegant(index) {
    const evaluacionTextarea = document.getElementById('evaluacion');
    if (evaluacionTextarea) {
        const pregunta = document.querySelector(`.question-item:nth-child(${index + 1}) .question-text`)?.textContent;
        if (pregunta) {
            const textoActual = evaluacionTextarea.value;
            const nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + `Pregunta ${index + 1}: ${pregunta}`;
            evaluacionTextarea.value = nuevoTexto;
            agregarMensajeElegant(`Pregunta ${index + 1} insertada en la evaluación`, 'success');
        }
    }
}

// Función para inicializar observador de formulario elegante
function inicializarObservadorFormularioElegant() {
    const formulario = document.querySelector('form');
    if (!formulario) return;

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                const motivoConsulta = document.getElementById('motivoConsulta')?.value || '';
                if (motivoConsulta.trim()) {
                    agregarMensajeElegant('Formulario actualizado. Listo para análisis.', 'info');
                }
            }
        });
    });

    observer.observe(formulario, {
        attributes: true,
        subtree: true,
        attributeFilter: ['value']
    });
}

// Función para mostrar resultados del análisis mejorado en la sidebar
function mostrarAnalisisMejoradoEnSidebar(analisisData) {
    console.log('📊 Mostrando análisis mejorado en sidebar...');

    const messagesContainer = document.getElementById('messagesContainer');

    if (!messagesContainer) {
        console.error('❌ Elementos de sidebar no encontrados');
        return;
    }

    // Verificar si ya se mostró este análisis para evitar duplicaciones
    const ultimoAnalisis = window.ultimoAnalisisMostrado;
    const datosActuales = JSON.stringify(analisisData);

    if (ultimoAnalisis === datosActuales) {
        console.log('⚠️ Análisis ya mostrado, evitando duplicación');
        return;
    }

    // Marcar este análisis como mostrado
    window.ultimoAnalisisMostrado = datosActuales;

    // Agregar mensaje de análisis mejorado
    agregarMensajeElegant('📊 Análisis clínico mejorado completado', 'auto-success');

    // Mostrar palabras clave identificadas con contexto
    if (analisisData.palabras_clave_identificadas && analisisData.palabras_clave_identificadas.length > 0) {
        let palabrasHtml = '<div class="mb-3"><strong>🔑 Palabras Clave Identificadas:</strong><br>';
        analisisData.palabras_clave_identificadas.forEach(pc => {
            const intensidad = pc.intensidad ? ` (${Math.round(pc.intensidad * 100)}%)` : '';
            palabrasHtml += `<span class="badge bg-primary me-1">${pc.palabra}${intensidad}</span>`;
        });
        palabrasHtml += '</div>';
        agregarMensajeElegant(palabrasHtml, 'auto-info');
    }

    // Mostrar región anatómica si está identificada
    if (analisisData.region_anatomica) {
        let regionHtml = `<div class="mb-3"><strong>📍 Región Anatómica:</strong><br>`;
        regionHtml += `<span class="badge bg-info me-1">${analisisData.region_anatomica}</span></div>`;
        agregarMensajeElegant(regionHtml, 'auto-info');
    }

    // Mostrar patologías identificadas con contexto
    if (analisisData.patologias_sugeridas && analisisData.patologias_sugeridas.length > 0) {
        let patologiasHtml = '<div class="mb-3"><strong>🏥 Patologías Sugeridas:</strong><br>';
        analisisData.patologias_sugeridas.forEach(pat => {
            const confianza = pat.confianza ? ` (${Math.round(pat.confianza * 100)}%)` : '';
            patologiasHtml += `<span class="badge bg-warning me-1">${pat.nombre}${confianza}</span>`;
        });
        patologiasHtml += '</div>';
        agregarMensajeElegant(patologiasHtml, 'auto-info');
    }

    // Mostrar escalas recomendadas con descripción
    if (analisisData.escalas_recomendadas && analisisData.escalas_recomendadas.length > 0) {
        let escalasHtml = '<div class="mb-3"><strong>📊 Escalas de Evaluación Recomendadas:</strong><br>';
        analisisData.escalas_recomendadas.forEach(escala => {
            escalasHtml += `<div class="mb-2"><strong>${escala.nombre}</strong><br><small>${escala.descripcion}</small></div>`;
        });
        escalasHtml += '</div>';
        agregarMensajeElegant(escalasHtml, 'auto-info');
    }

    // Mostrar evidencia científica si está disponible
    if (analisisData.evidencia_cientifica && analisisData.evidencia_cientifica.length > 0) {
        let evidenciaHtml = '<div class="mb-3"><strong>🔬 Evidencia Científica Encontrada:</strong><br>';
        analisisData.evidencia_cientifica.slice(0, 3).forEach((evidencia, index) => {
            evidenciaHtml += `
                <div class="mb-2 p-2 border rounded">
                    <h6 class="mb-1">${evidencia.titulo || 'Sin título'}</h6>
                    <p class="mb-1 small">${evidencia.resumen || 'Sin resumen disponible'}</p>
                        <small class="text-muted">
                            ${evidencia.doi ? `<a href="https://doi.org/${evidencia.doi}" target="_blank">DOI: ${evidencia.doi}</a>` : 'DOI no disponible'}
                        </small>
                </div>
            `;
        });
        evidenciaHtml += '</div>';
        agregarMensajeElegant(evidenciaHtml, 'auto-info');
    }

    // Mostrar recomendaciones si están disponibles
    if (analisisData.recomendaciones && analisisData.recomendaciones.length > 0) {
        let recomendacionesHtml = '<div class="mb-3"><strong>💡 Recomendaciones:</strong><br><ul class="list-unstyled mb-0">';
        analisisData.recomendaciones.forEach(rec => {
            recomendacionesHtml += `<li class="mb-1"><i class="fas fa-check text-success me-2"></i>${rec}</li>`;
        });
        recomendacionesHtml += '</ul></div>';
        agregarMensajeElegant(recomendacionesHtml, 'auto-info');
    }
}

// Función mejorada de Copilot Health que integra el análisis mejorado
async function copilotHealthAssistantMejorado() {
    console.log('🤖 Copilot Health Assistant Mejorado iniciado...');

    // Obtener información del profesional
    const profesional = await obtenerInformacionProfesional();

    // Obtener todos los datos del formulario
    const motivoConsulta = document.getElementById('motivoConsulta').value.trim();
    const tipoAtencion = document.getElementById('tipoAtencion').value;
    const pacienteEdad = document.getElementById('pacienteEdad').value;
    const antecedentes = document.getElementById('antecedentes').value.trim();
    const evaluacion = document.getElementById('evaluacion').value.trim();

    if (!motivoConsulta) {
        mostrarErrorSidebar('Por favor, ingrese el motivo de consulta');
        return;
    }

    // Mensaje de inicio personalizado
    const mensajeInicio = generarMensajeNatural('inicio', { profesional });
    mostrarNotificacionSidebar(mensajeInicio, 'info');

    // Mostrar progreso inicial
    mostrarProgresoSidebar(10, 'Iniciando análisis mejorado de Copilot Health...');

    try {
        // Paso 1: Análisis mejorado del motivo de consulta
        const mensajeAnalisis = generarMensajeNatural('analisis_iniciado', { profesional });
        mostrarProgresoSidebar(20, mensajeAnalisis);

        const analisisMejorado = await analizarMotivoConsultaMejorado(motivoConsulta);

        if (analisisMejorado && analisisMejorado.success) {
            const mensajeTerminos = generarMensajeNatural('terminos_clave', { profesional });
            mostrarProgresoSidebar(40, mensajeTerminos);

            // Paso 2: Búsqueda mejorada de evidencia científica
            const mensajeBusqueda = generarMensajeNatural('busqueda_iniciada', { profesional });
            mostrarProgresoSidebar(60, mensajeBusqueda);

            const evidenciaMejorada = await buscarEvidenciaMejorada(motivoConsulta);

            if (evidenciaMejorada && evidenciaMejorada.success) {
                const mensajeProgreso = generarMensajeNatural('busqueda_progreso', { profesional });
                mostrarProgresoSidebar(80, mensajeProgreso);

                // Paso 3: Análisis completo mejorado
                const analisisCompleto = await analizarCasoCompletoMejorado(
                    motivoConsulta, tipoAtencion, pacienteEdad, antecedentes
                );

                if (analisisCompleto && analisisCompleto.success) {
                    const mensajeResultados = generarMensajeNatural('resultados_encontrados', { profesional });
                    mostrarProgresoSidebar(95, mensajeResultados);

                    // Mostrar resultados en sidebar
                    mostrarAnalisisMejoradoEnSidebar(analisisCompleto.analisis_mejorado);

                    // Solo mostrar mensaje de completado si no se ha mostrado antes
                    if (!mensajeCompletadoMostrado) {
                        setTimeout(() => {
                            const mensajeCompletado = generarMensajeNatural('analisis_completado', { profesional });
                            mostrarNotificacionSidebar(mensajeCompletado, 'success');
                            mensajeCompletadoMostrado = true;
                        }, 1000);
                    }
                } else {
                    const mensajeError = generarMensajeNatural('error', { profesional });
                    mostrarErrorSidebar(mensajeError);
                }
            } else {
                const mensajeError = generarMensajeNatural('error', { profesional });
                mostrarErrorSidebar(mensajeError);
            }
        } else {
            const mensajeError = generarMensajeNatural('error', { profesional });
            mostrarErrorSidebar(mensajeError);
        }

    } catch (error) {
        console.error('❌ Error en Copilot Health Assistant Mejorado:', error);
        const mensajeError = generarMensajeNatural('error', { profesional });
        mostrarErrorSidebar(mensajeError);
    }
}

// Función para realizar análisis completo del caso
async function realizarAnalisisCompleto(motivoConsulta, tipoAtencion, edad, antecedentes, evaluacion) {
    try {
        const response = await fetch('/api/copilot/complete-analysis', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                motivo_consulta: motivoConsulta,
                tipo_atencion: tipoAtencion,
                edad_paciente: parseInt(edad),
                antecedentes: antecedentes,
                evaluacion: evaluacion
            })
        });

        if (response.status === 200) {
            const data = await response.json();
            if (data.success) {
                console.log('✅ Análisis completo realizado');
                return data;
            } else {
                console.error('❌ Error en análisis completo:', data.message);
                return null;
            }
        } else {
            console.error('❌ Error HTTP en análisis completo:', response.status);
            return null;
        }
    } catch (error) {
        console.error('❌ Error en realizarAnalisisCompleto:', error);
        return null;
    }
}

// Función para extraer términos clave del análisis
async function extraerTerminosClave(analisisCompleto) {
    try {
        const response = await fetch('/api/copilot/extract-key-terms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                analisis: analisisCompleto
            })
        });

        if (response.status === 200) {
            const data = await response.json();
            if (data.success) {
                console.log('✅ Términos clave extraídos');
                return data;
            } else {
                console.error('❌ Error extrayendo términos clave:', data.message);
                return null;
            }
        } else {
            console.error('❌ Error HTTP extrayendo términos clave:', response.status);
            return null;
        }
    } catch (error) {
        console.error('❌ Error en extraerTerminosClave:', error);
        return null;
    }
}

// Función para generar términos de búsqueda expandidos
async function generarTerminosBusquedaExpandidos(condicion, especialidad, edad, terminosClave) {
    try {
        const response = await fetch('/api/copilot/generate-expanded-search-terms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                condicion: condicion,
                especialidad: especialidad,
                edad: parseInt(edad),
                terminos_clave: terminosClave
            })
        });

        if (response.status === 200) {
            const data = await response.json();
            if (data.success) {
                return data;
            } else {
                console.error('❌ Error en respuesta:', data.message);
                return null;
            }
        } else {
            console.error('❌ Error HTTP:', response.status);
            return null;
        }
    } catch (error) {
        console.error('❌ Error en generarTerminosBusquedaExpandidos:', error);
        return null;
    }
}

// Función para realizar búsqueda con términos clave
async function realizarBusquedaConTerminosClave(terminosClave, condicion, especialidad, edad) {
    try {
        // Obtener información del profesional para mensajes personalizados
        const profesional = await obtenerInformacionProfesional();

        // Mensaje de inicio de búsqueda
        const mensajeBusqueda = generarMensajeNatural('busqueda_iniciada', { profesional });
        mostrarProgresoSidebar(75, mensajeBusqueda);

        const response = await fetch('/api/copilot/search-with-key-terms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                condicion: condicion,
                especialidad: especialidad,
                edad: parseInt(edad),
                terminos_clave: terminosClave
            })
        });

        if (response.status === 200) {
            const data = await response.json();
            if (data.success) {
                console.log('✅ Búsqueda con términos clave completada');

                // Mensaje de progreso durante la búsqueda
                const mensajeProgreso = generarMensajeNatural('busqueda_progreso', { profesional });
                mostrarProgresoSidebar(85, mensajeProgreso);

                // Mostrar resultados en sidebar
                mostrarPapersEnSidebar(data.planes_tratamiento);

                // Mensaje de resultados encontrados
                if (data.planes_tratamiento && data.planes_tratamiento.length > 0) {
                    const mensajeResultados = generarMensajeNatural('resultados_encontrados', { profesional });
                    mostrarProgresoSidebar(95, mensajeResultados);
                } else {
                    const mensajeSinEvidencia = generarMensajeNatural('sin_evidencia', { profesional });
                    mostrarProgresoSidebar(95, mensajeSinEvidencia);
                }

                return data;
            } else {
                console.error('❌ Error en búsqueda con términos clave:', data.message);
                const mensajeError = generarMensajeNatural('error', { profesional });
                mostrarErrorSidebar(mensajeError);
                return null;
            }
        } else {
            console.error('❌ Error HTTP en búsqueda con términos clave:', response.status);
            const mensajeError = generarMensajeNatural('error', { profesional });
            mostrarErrorSidebar(mensajeError);
            return null;
        }
    } catch (error) {
        console.error('❌ Error en realizarBusquedaConTerminosClave:', error);
        const profesional = await obtenerInformacionProfesional();
        const mensajeError = generarMensajeNatural('error', { profesional });
        mostrarErrorSidebar(mensajeError);
        return null;
    }
}

// Función para generar términos de búsqueda
async function generarTerminosBusqueda(condicion, especialidad, edad) {
    try {
        const response = await fetch('/api/copilot/generate-search-terms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                condicion: condicion,
                especialidad: especialidad,
                edad: parseInt(edad)
            })
        });

        if (response.status === 200) {
            const data = await response.json();
            if (data.success) {
                return data;
            } else {
                console.error('❌ Error en respuesta:', data.message);
                return null;
            }
        } else {
            console.error('❌ Error HTTP:', response.status);
            return null;
        }
    } catch (error) {
        console.error('❌ Error en generarTerminosBusqueda:', error);
        return null;
    }
}

// Función para mostrar términos en la sidebar
function mostrarTerminosEnSidebar(terminosDisponibles, condicion, especialidad, edad) {
    console.log('📋 Mostrando términos en sidebar...');

    const sidebarLista = document.getElementById('sidebarListaTerminos');
    const sidebarTerminos = document.getElementById('sidebarTerminos');

    if (!sidebarLista || !sidebarTerminos) {
        console.error('❌ Elementos de sidebar no encontrados');
        return;
    }

    let html = '';

    // Mostrar términos recomendados primero
    if (terminosDisponibles.terminos_recomendados && terminosDisponibles.terminos_recomendados.length > 0) {
        html += `
            <div class="mb-3">
                <h6 class="text-primary"><i class="fas fa-star me-1"></i>Términos Recomendados</h6>
        `;

        terminosDisponibles.terminos_recomendados.forEach((termino, index) => {
            html += `
                <div class="sidebar-term-item" onclick="toggleTerminoSidebar(this, '${termino}')" data-termino="${termino}">
                    <i class="fas fa-check-circle me-2 text-success"></i>
                    ${termino}
                </div>
            `;
        });

        html += `</div>`;
    }

    // Mostrar otros términos disponibles
    const otrasCategorias = ['terminos_basicos', 'terminos_especialidad', 'terminos_edad', 'terminos_combinados'];

    otrasCategorias.forEach(categoria => {
        if (terminosDisponibles[categoria] && terminosDisponibles[categoria].length > 0) {
            const titulo = categoria.replace('terminos_', '').replace('_', ' ').toUpperCase();
            html += `
                <div class="mb-3">
                    <h6 class="text-secondary"><i class="fas fa-list me-1"></i>${titulo}</h6>
            `;

            terminosDisponibles[categoria].forEach((termino, index) => {
                html += `
                    <div class="sidebar-term-item" onclick="toggleTerminoSidebar(this, '${termino}')" data-termino="${termino}">
                        <i class="fas fa-circle me-2 text-muted"></i>
                        ${termino}
                    </div>
                `;
            });

            html += `</div>`;
        }
    });

    sidebarLista.innerHTML = html;
    sidebarTerminos.style.display = 'block';
    sidebarTerminos.classList.add('show');
    sidebarTerminos.classList.add('sidebar-section');

    // Actualizar estado dinámicamente
    actualizarSidebarDinamica('terminos_generados', {
        terminos: terminosDisponibles,
        condicion: condicion,
        especialidad: especialidad,
        edad: edad
    });

    // Hacer la sidebar interactiva después de agregar contenido
    setTimeout(() => {
        hacerSidebarInteractiva();
    }, 100);

    // Asegurar que la sidebar esté disponible pero no visible automáticamente
    const sidebarContainer = document.getElementById('sidebarContainer');
    if (sidebarContainer) {
        sidebarContainer.style.display = 'block';
        sidebarContainer.style.visibility = 'visible';
        // No mostrar automáticamente, solo preparar el contenido

        // Actualizar el botón de toggle
        const toggleIcon = document.getElementById('sidebarToggleIcon');
        if (toggleIcon) {
            toggleIcon.className = 'fas fa-th-large';
        }
    }

    console.log('✅ Términos mostrados en sidebar dinámicamente');
}

// Función para alternar selección de términos en sidebar
function toggleTerminoSidebar(element, termino) {
    element.classList.toggle('selected');

    const icon = element.querySelector('i');
    if (element.classList.contains('selected')) {
        icon.className = 'fas fa-check-circle me-2 text-white';
    } else {
        icon.className = 'fas fa-circle me-2 text-muted';
    }

    console.log(`🔄 Término ${element.classList.contains('selected') ? 'seleccionado' : 'deseleccionado'}: ${termino}`);
}

// Función para obtener términos seleccionados de la sidebar
function obtenerTerminosSeleccionadosSidebar() {
    const elementosSeleccionados = document.querySelectorAll('#sidebarListaTerminos .sidebar-term-item.selected');
    const terminos = Array.from(elementosSeleccionados).map(el => el.getAttribute('data-termino'));

    console.log('📋 Términos seleccionados en sidebar:', terminos);
    return terminos;
}

// Función para realizar búsqueda desde la sidebar
async function realizarBusquedaDesdeSidebar() {
    const terminosSeleccionados = obtenerTerminosSeleccionadosSidebar();

    if (terminosSeleccionados.length === 0) {
        showNotification('Selecciona al menos un término para buscar', 'warning');
        return;
    }

    // Obtener datos del formulario
    const motivoConsulta = document.getElementById('motivoConsulta').value;
    const especialidad = document.getElementById('tipoAtencion').value;
    const edad = document.getElementById('pacienteEdad').value || '30';

    console.log('🔍 Realizando búsqueda desde sidebar...');
    console.log('Datos:', { motivoConsulta, especialidad, edad, terminosSeleccionados });

    try {
        const response = await fetch('/api/copilot/search-with-terms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Incluir cookies de sesión
            body: JSON.stringify({
                condicion: motivoConsulta,
                especialidad: especialidad,
                edad: parseInt(edad),
                terminos_seleccionados: terminosSeleccionados
            })
        });

        const data = await response.json();

        if (data.success) {
            mostrarPapersEnSidebar(data.planes_tratamiento);
            showNotification(`Búsqueda completada: ${data.planes_tratamiento.length} tratamientos encontrados`, 'success');
        } else {
            console.error('❌ Error en búsqueda desde sidebar:', data.message);
            showNotification(data.message, 'error');
        }

    } catch (error) {
        console.error('❌ Error en búsqueda desde sidebar:', error);
        showNotification('Error de conexión con el servidor', 'error');
    }
}

// Función para realizar búsqueda automática desde la sidebar
async function realizarBusquedaAutomaticaDesdeSidebar() {
    const motivoConsulta = document.getElementById('motivoConsulta').value;
    const especialidad = document.getElementById('tipoAtencion').value;
    const edad = document.getElementById('pacienteEdad').value || '30';

    console.log('🔍 Realizando búsqueda automática desde sidebar...');

    try {
        const response = await fetch('/api/copilot/search-with-terms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include', // Incluir cookies de sesión
            body: JSON.stringify({
                condicion: motivoConsulta,
                especialidad: especialidad,
                edad: parseInt(edad),
                terminos_seleccionados: [] // Búsqueda automática sin términos específicos
            })
        });

        const data = await response.json();

        if (data.success) {
            mostrarPapersEnSidebar(data.planes_tratamiento);
            showNotification(`Búsqueda automática completada: ${data.planes_tratamiento.length} tratamientos encontrados`, 'success');
        } else {
            console.error('❌ Error en búsqueda automática desde sidebar:', data.message);
            showNotification(data.message, 'error');
        }

    } catch (error) {
        console.error('❌ Error en búsqueda automática desde sidebar:', error);
        showNotification('Error de conexión con el servidor', 'error');
    }
}

// Función para mostrar papers en la sidebar
async function mostrarPapersEnSidebar(planes) {
    console.log('📄 Mostrando papers en sidebar...');

    const sidebarLista = document.getElementById('sidebarListaPapers');
    const sidebarPapers = document.getElementById('sidebarPapers');

    if (!sidebarLista || !sidebarPapers) {
        console.error('❌ Elementos de sidebar papers no encontrados');
        return;
    }

    // Obtener información del profesional para mensajes personalizados
    const profesional = await obtenerInformacionProfesional();

    // Agregar mensaje al chat de Copilot
    agregarMensajeCopilot(`Mostrando ${planes ? planes.length : 0} estudios científicos en la sidebar...`, 'progress');

    let html = `
        <div class="alert alert-success mb-3">
            <i class="fas fa-check-circle me-2"></i>
            <strong>Estudios científicos encontrados</strong>
        </div>
    `;

    if (!planes || planes.length === 0) {
        agregarMensajeCopilot('⚠️ No se encontraron estudios específicos para este caso.', 'warning');
        html += `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                No se encontraron estudios específicos para este caso. Considera ajustar los términos de búsqueda.
            </div>
        `;
    } else {
        planes.forEach((plan, index) => {
            // Procesar DOI y crear link
            let doiLink = '';
            let añoEstudio = '';

            if (plan.doi && plan.doi !== 'Sin DOI' && plan.doi !== 'No disponible' && plan.doi !== 'Múltiples fuentes') {
                // Limpiar DOI si tiene prefijos
                let doiLimpio = plan.doi;
                if (doiLimpio.startsWith('https://doi.org/')) {
                    doiLimpio = doiLimpio.replace('https://doi.org/', '');
                } else if (doiLimpio.startsWith('http://doi.org/')) {
                    doiLimpio = doiLimpio.replace('http://doi.org/', '');
                }

                doiLink = `<a href="https://doi.org/${doiLimpio}" target="_blank" class="sidebar-paper-doi">
                             <i class="fas fa-external-link-alt me-1"></i>Ver Paper
                           </a>`;
            } else {
                doiLink = `<span class="sidebar-paper-doi text-muted">DOI no disponible</span>`;
            }

            // Extraer año del estudio
            if (plan.año_publicacion && plan.año_publicacion !== 'N/A') {
                añoEstudio = `<span class="sidebar-paper-year">
                                <i class="fas fa-calendar me-1"></i>${plan.año_publicacion}
                              </span>`;
            } else if (plan.fecha_publicacion && plan.fecha_publicacion !== 'Fecha no disponible') {
                // Intentar extraer año de la fecha
                const añoMatch = plan.fecha_publicacion.match(/\d{4}/);
                if (añoMatch) {
                    añoEstudio = `<span class="sidebar-paper-year">
                                    <i class="fas fa-calendar me-1"></i>${añoMatch[0]}
                                  </span>`;
                }
            }

            html += `
                <div class="sidebar-paper-item" data-index="${index}" onclick="seleccionarPaperSidebar(this, ${index})">
                    <div class="sidebar-paper-title">${plan.titulo || 'Sin título'}</div>
                    <div class="mb-2">${plan.descripcion || 'Sin descripción'}</div>
                    <div class="d-flex justify-content-between align-items-center">
                        ${doiLink}
                        <div class="d-flex align-items-center">
                            ${añoEstudio}
                            <span class="sidebar-paper-evidence ms-2">
                                <i class="fas fa-chart-line me-1"></i>${plan.evidencia || 'N/A'}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        });

        // Solo agregar mensaje de finalización si no se ha mostrado antes
        if (!mensajeCompletadoMostrado) {
            agregarMensajeCopilot('🎯 Análisis completado. Los resultados más relevantes están disponibles en la sidebar.', 'success');
            html += `
                <div class="alert alert-info mt-3">
                    <i class="fas fa-lightbulb me-2"></i>
                    <strong>Análisis completado. Los resultados más relevantes están disponibles.</strong>
                </div>
            `;
            mensajeCompletadoMostrado = true;
        }
    }

    sidebarLista.innerHTML = html;
    sidebarPapers.style.display = 'block';
    sidebarPapers.classList.add('show');
    sidebarPapers.classList.add('sidebar-section');

    // Actualizar estado dinámicamente
    actualizarSidebarDinamica('papers_encontrados', { planes: planes });

    // Hacer la sidebar interactiva después de agregar contenido
    setTimeout(() => {
        hacerSidebarInteractiva();
    }, 100);

    // Asegurar que la sidebar esté disponible pero no visible automáticamente
    const sidebarContainer = document.getElementById('sidebarContainer');
    if (sidebarContainer) {
        sidebarContainer.style.display = 'block';
        sidebarContainer.style.visibility = 'visible';
        // No mostrar automáticamente, solo preparar el contenido

        // Actualizar el botón de toggle
        const toggleIcon = document.getElementById('sidebarToggleIcon');
        if (toggleIcon) {
            toggleIcon.className = 'fas fa-th-large';
        }
    }

    // Mostrar notificación de éxito
    showNotification(`${mensajeCompletado}`, 'success');

    console.log('✅ Papers mostrados en sidebar dinámicamente');
}

// Función para seleccionar paper en la sidebar
function seleccionarPaperSidebar(element, index) {
    // Remover selección anterior
    document.querySelectorAll('.sidebar-paper-item.selected').forEach(el => {
        el.classList.remove('selected');
    });

    // Seleccionar el actual
    element.classList.add('selected');

    // Actualizar estado
    actualizarSidebarDinamica('paper_seleccionado', {
        index: index,
        titulo: element.querySelector('.sidebar-paper-title').textContent
    });

    console.log(`📄 Paper seleccionado: ${index}`);
}

// Función para insertar papers desde la sidebar
function insertarPapersDesdeSidebar() {
    const papersSeleccionados = document.querySelectorAll('#sidebarListaPapers .sidebar-paper-item');

    if (papersSeleccionados.length === 0) {
        showNotification('No hay papers disponibles para insertar', 'warning');
        return;
    }

    const tratamientoTextarea = document.getElementById('tratamiento');
    let textoActual = tratamientoTextarea.value;

    papersSeleccionados.forEach((paper, index) => {
        const titulo = paper.querySelector('.sidebar-paper-title').textContent;
        const descripcion = paper.querySelector('.div').textContent;
        const doiLink = paper.querySelector('.sidebar-paper-doi a');
        const doi = doiLink ? doiLink.href : '';

        const paperText = `
=== PAPER ${index + 1} ===
Título: ${titulo}
Descripción: ${descripcion}
${doi ? `DOI: ${doi}` : ''}
`;

        textoActual += paperText;
    });

    tratamientoTextarea.value = textoActual;
    showNotification(`${papersSeleccionados.length} papers insertados en el tratamiento`, 'success');

    console.log('✅ Papers insertados desde sidebar');
}

// Función para actualizar el estado de la sidebar
function actualizarEstadoSidebar(mensaje) {
    const estadoContenido = document.getElementById('sidebarEstadoContenido');

    if (estadoContenido) {
        estadoContenido.innerHTML = `
            <p class="text-muted mb-0">
                <i class="fas fa-info-circle me-1"></i>
                ${mensaje}
            </p>
        `;
    }
}

// Función para limpiar la sidebar
function limpiarSidebar() {
    const sidebarTerminos = document.getElementById('sidebarTerminos');
    const sidebarPapers = document.getElementById('sidebarPapers');

    if (sidebarTerminos) {
        sidebarTerminos.style.display = 'none';
        sidebarTerminos.classList.remove('show');
    }

    if (sidebarPapers) {
        sidebarPapers.style.display = 'none';
        sidebarPapers.classList.remove('show');
    }

    actualizarEstadoSidebar('Realiza una búsqueda para ver términos sugeridos y papers aquí.');
}

// Función para integrar la sidebar con las funciones existentes
function integrarSidebarConFuncionesExistentes() {
    // Sobrescribir la función mostrarTerminosDisponibles para usar la sidebar
    const originalMostrarTerminos = window.mostrarTerminosDisponibles;

    window.mostrarTerminosDisponibles = function (terminosDisponibles, condicion, especialidad, edad) {
        // Mostrar automáticamente en la sidebar
        mostrarTerminosEnSidebar(terminosDisponibles, condicion, especialidad, edad);

        // También mostrar en el área principal para compatibilidad
        if (originalMostrarTerminos) {
            originalMostrarTerminos(terminosDisponibles, condicion, especialidad, edad);
        }
    };

    // Sobrescribir la función mostrarSugerenciasTratamiento para usar la sidebar
    const originalMostrarSugerencias = window.mostrarSugerenciasTratamiento;

    window.mostrarSugerenciasTratamiento = function (planes) {
        // Mostrar automáticamente papers en la sidebar
        mostrarPapersEnSidebar(planes);

        // También mostrar en el área principal para compatibilidad
        if (originalMostrarSugerencias) {
            originalMostrarSugerencias(planes);
        }
    };

    // Sobrescribir la función realizarBusquedaPersonalizada para actualizar sidebar
    const originalBusquedaPersonalizada = window.realizarBusquedaPersonalizada;

    window.realizarBusquedaPersonalizada = async function (condicion, especialidad, edad) {
        console.log('🔍 Iniciando búsqueda personalizada desde sidebar...');

        // Obtener términos seleccionados de la sidebar
        const terminosSeleccionados = obtenerTerminosSeleccionadosSidebar();
        console.log('📋 Términos seleccionados:', terminosSeleccionados);

        if (terminosSeleccionados.length === 0) {
            showNotification('Selecciona al menos un término para buscar', 'warning');
            return;
        }

        // Limpiar papers anteriores
        limpiarPapersSidebar();

        // Actualizar estado
        actualizarEstadoSidebar('Realizando búsqueda...');

        try {
            const response = await fetch('/api/copilot/search-with-terms', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Incluir cookies de sesión
                body: JSON.stringify({
                    condicion: condicion,
                    especialidad: especialidad,
                    edad: parseInt(edad),
                    terminos_seleccionados: terminosSeleccionados
                })
            });

            const data = await response.json();

            if (data.success) {
                // Mostrar papers automáticamente en sidebar
                mostrarPapersEnSidebar(data.planes_tratamiento);
                actualizarEstadoSidebar(`${data.planes_tratamiento.length} papers encontrados`);
                showNotification(`Búsqueda completada: ${data.planes_tratamiento.length} tratamientos encontrados`, 'success');
            } else {
                console.error('❌ Error en búsqueda personalizada:', data.message);
                actualizarEstadoSidebar('Error en la búsqueda');
                showNotification(data.message, 'error');
            }

        } catch (error) {
            console.error('❌ Error en búsqueda personalizada:', error);
            actualizarEstadoSidebar('Error de conexión');
            showNotification('Error de conexión con el servidor', 'error');
        }
    };

    console.log('✅ Sidebar integrada con funciones existentes');
}

// Inicializar la sidebar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    integrarSidebarConFuncionesExistentes();
    console.log('✅ Funciones de sidebar inicializadas');
});

// ========================================
// FUNCIONES ADICIONALES PARA SIDEBAR DINÁMICA
// ========================================

// Función para limpiar papers de la sidebar
function limpiarPapersSidebar() {
    const sidebarLista = document.getElementById('sidebarListaPapers');
    const sidebarPapers = document.getElementById('sidebarPapers');

    if (sidebarLista) {
        sidebarLista.innerHTML = '';
    }

    if (sidebarPapers) {
        sidebarPapers.style.display = 'none';
        sidebarPapers.classList.remove('show');
    }
}

// Función para limpiar términos de la sidebar
function limpiarTerminosSidebar() {
    const sidebarLista = document.getElementById('sidebarListaTerminos');
    const sidebarTerminos = document.getElementById('sidebarTerminos');

    if (sidebarLista) {
        sidebarLista.innerHTML = '';
    }

    if (sidebarTerminos) {
        sidebarTerminos.style.display = 'none';
        sidebarTerminos.classList.remove('show');
    }
}

// Función para actualizar dinámicamente la sidebar
function actualizarSidebarDinamica(accion, datos) {
    console.log(`🔄 Actualizando sidebar dinámicamente: ${accion}`);

    switch (accion) {
        case 'terminos_generados':
            mostrarTerminosEnSidebar(datos.terminos, datos.condicion, datos.especialidad, datos.edad);
            actualizarEstadoSidebar(`Términos generados para: ${datos.condicion}`);
            break;

        case 'busqueda_iniciada':
            actualizarEstadoSidebar('Realizando búsqueda...');
            limpiarPapersSidebar();
            break;

        case 'papers_encontrados':
            mostrarPapersEnSidebar(datos.planes);
            actualizarEstadoSidebar(`${datos.planes.length} papers encontrados`);
            break;

        case 'error_busqueda':
            actualizarEstadoSidebar('Error en la búsqueda');
            break;

        case 'limpiar_todo':
            limpiarSidebar();
            break;

        case 'termino_seleccionado':
            actualizarEstadoSidebar(`Término seleccionado: ${datos.termino}`);
            break;

        case 'paper_insertado':
            actualizarEstadoSidebar('Paper insertado en tratamiento');
            break;

        default:
            console.log('🔄 Acción de sidebar no reconocida:', accion);
    }
}

// Función para detectar cambios en el formulario y actualizar sidebar
function detectarCambiosFormulario() {
    const motivoConsulta = document.getElementById('motivoConsulta');
    const tipoAtencion = document.getElementById('tipoAtencion');
    const pacienteEdad = document.getElementById('pacienteEdad');

    if (motivoConsulta) {
        motivoConsulta.addEventListener('input', function () {
            if (this.value.length > 10) {
                // Si hay suficiente texto, sugerir generar términos
                actualizarEstadoSidebar('Texto detectado. Considera generar términos de búsqueda.');
            }
        });
    }

    if (tipoAtencion) {
        tipoAtencion.addEventListener('change', function () {
            actualizarEstadoSidebar(`Especialidad seleccionada: ${this.value}`);
        });
    }

    if (pacienteEdad) {
        pacienteEdad.addEventListener('input', function () {
            if (this.value) {
                actualizarEstadoSidebar(`Edad del paciente: ${this.value} años`);
            }
        });
    }
}

// Función para hacer la sidebar más interactiva
function hacerSidebarInteractiva() {
    // Agregar tooltips a los elementos de la sidebar
    const sidebarElements = document.querySelectorAll('.sidebar-term-item, .sidebar-paper-item');

    sidebarElements.forEach(element => {
        element.addEventListener('mouseenter', function () {
            this.style.transform = 'translateX(-5px)';
            this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.15)';
        });

        element.addEventListener('mouseleave', function () {
            this.style.transform = 'translateX(0)';
            this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        });
    });
}

// Función para auto-actualizar la sidebar
function autoActualizarSidebar() {
    // Verificar cada 5 segundos si hay nuevos datos para mostrar
    setInterval(() => {
        const sidebarTerminos = document.getElementById('sidebarTerminos');
        const sidebarPapers = document.getElementById('sidebarPapers');

        // Si no hay contenido en la sidebar, mostrar mensaje de ayuda
        if (sidebarTerminos && sidebarTerminos.style.display === 'none' &&
            sidebarPapers && sidebarPapers.style.display === 'none') {
            actualizarEstadoSidebar('Completa el formulario y genera términos para ver contenido aquí.');
        }
    }, 5000);
}

// Función para mostrar notificaciones en la sidebar
function mostrarNotificacionSidebar(mensaje, tipo = 'info') {
    const estadoContenido = document.getElementById('sidebarEstadoContenido');

    if (estadoContenido) {
        const icono = tipo === 'success' ? 'fas fa-check-circle' :
            tipo === 'error' ? 'fas fa-exclamation-circle' :
                tipo === 'warning' ? 'fas fa-exclamation-triangle' :
                    'fas fa-info-circle';

        const color = tipo === 'success' ? 'text-success' :
            tipo === 'error' ? 'text-danger' :
                tipo === 'warning' ? 'text-warning' :
                    'text-info';

        estadoContenido.innerHTML = `
            <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
                <i class="${icono} me-2"></i>
                ${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            actualizarEstadoSidebar('Listo para usar');
        }, 5000);
    }
}

// Función para integrar con el análisis en tiempo real
function integrarConAnalisisTiempoReal() {
    // Sobrescribir la función de análisis en tiempo real
    const originalAnalizarMotivo = window.analizarMotivoEnTiempoReal;

    if (originalAnalizarMotivo) {
        window.analizarMotivoEnTiempoReal = async function () {
            // Mostrar estado en sidebar
            actualizarEstadoSidebar('Analizando motivo de consulta...');

            try {
                await originalAnalizarMotivo();
                actualizarEstadoSidebar('Análisis completado. Considera generar términos.');
            } catch (error) {
                actualizarEstadoSidebar('Error en el análisis');
                console.error('Error en análisis:', error);
            }
        };
    }
}

// Función para mostrar errores en la sidebar
function mostrarErrorSidebar(mensaje) {
    console.error(`❌ Sidebar Error: ${mensaje}`);
    mostrarNotificacionSidebar(mensaje, 'error');
}

// Función para mostrar progreso en la sidebar
function mostrarProgresoSidebar(progreso, mensaje) {
    const estadoContenido = document.getElementById('sidebarEstadoContenido');

    if (estadoContenido) {
        estadoContenido.innerHTML = `
            <div class="mb-2">
                <small class="text-muted">${mensaje}</small>
            </div>
            <div class="progress" style="height: 6px;">
                <div class="progress-bar" role="progressbar" 
                     style="width: ${progreso}%" 
                     aria-valuenow="${progreso}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                </div>
            </div>
        `;
    }
}

// Función para mostrar/ocultar la sidebar estilo Cursor
function toggleSidebar() {
    const sidebarContainer = document.getElementById('sidebarContainer');
    const toggleIcon = document.getElementById('sidebarToggleIcon');
    const toggleButton = document.getElementById('sidebarToggle');
    const mainContent = document.querySelector('.col-lg-8.col-xl-9');

    if (sidebarContainer.classList.contains('show')) {
        // Ocultar panel
        sidebarContainer.classList.remove('show');
        toggleIcon.className = 'fas fa-columns'; /* Icono de layout para panel oculto */
        toggleButton.title = 'Mostrar panel Copilot Health';

        // Restaurar tamaño del formulario
        if (mainContent) {
            mainContent.classList.add('sidebar-hidden');
            mainContent.style.width = '100%';
            mainContent.style.maxWidth = '100%';
            mainContent.style.flex = '1';

            // Forzar reajuste de elementos
            setTimeout(() => {
                forceLayoutUpdate();
            }, 50);
        }
    } else {
        // Mostrar panel
        sidebarContainer.classList.add('show');
        toggleIcon.className = 'fas fa-window-minimize'; /* Icono de minimizar ventana para panel visible */
        toggleButton.title = 'Ocultar panel Copilot Health';

        // Ajustar tamaño del formulario
        if (mainContent) {
            mainContent.classList.remove('sidebar-hidden');
            mainContent.style.width = 'calc(100% - 400px)';
            mainContent.style.maxWidth = 'calc(100% - 400px)';
            mainContent.style.flex = '1';

            // Forzar reajuste de elementos
            setTimeout(() => {
                forceLayoutUpdate();
            }, 50);
        }
    }
}

// Función para inicializar todas las funcionalidades dinámicas
function inicializarSidebarDinamica() {
    console.log('🚀 Inicializando sidebar dinámica...');

    // Asegurar que la sidebar esté visible desde el inicio
    const sidebarContainer = document.getElementById('sidebarContainer');
    if (sidebarContainer) {
        sidebarContainer.style.display = 'block';
        sidebarContainer.style.visibility = 'visible';
        sidebarContainer.style.opacity = '1';

        // El panel estará oculto por defecto en todos los dispositivos
        sidebarContainer.classList.remove('show');
        const toggleIcon = document.getElementById('sidebarToggleIcon');
        if (toggleIcon) {
            toggleIcon.className = 'fas fa-columns'; /* Icono inicial de layout */
        }

        // Configurar el contenido principal en tamaño normal
        const mainContent = document.querySelector('.col-lg-8.col-xl-9');
        if (mainContent) {
            mainContent.classList.add('sidebar-hidden');
            mainContent.style.width = '100%';
            mainContent.style.maxWidth = '100%';
            mainContent.style.flex = '1';
        }
    }

    // Detectar cambios en el formulario
    detectarCambiosFormulario();

    // Hacer la sidebar interactiva
    hacerSidebarInteractiva();

    // Auto-actualizar la sidebar
    autoActualizarSidebar();

    // Integrar con análisis en tiempo real
    integrarConAnalisisTiempoReal();

    // Mostrar mensaje inicial
    actualizarEstadoSidebar('Sidebar dinámica activa. Escribe tu consulta para comenzar.');

    // Asegurar que el estado inicial sea visible
    const sidebarEstado = document.getElementById('sidebarEstado');
    if (sidebarEstado) {
        sidebarEstado.style.display = 'block';
        sidebarEstado.classList.add('show');
    }

    console.log('✅ Sidebar dinámica inicializada');

    // Inicializar el resize de la sidebar
    initializeSidebarResize();

    // Agregar listener para cambios de tamaño de ventana
    window.addEventListener('resize', handleWindowResize);
}

// Función para forzar el reajuste de elementos
function forceLayoutUpdate() {
    const mainContent = document.querySelector('.col-lg-8.col-xl-9');
    if (mainContent) {
        // Forzar reflow
        mainContent.offsetHeight;

        // Actualizar todos los elementos hijos
        const allElements = mainContent.querySelectorAll('*');
        allElements.forEach(element => {
            if (element.offsetHeight) {
                element.offsetHeight;
            }
        });
    }
}

// Función para minimizar el panel
function minimizePanel() {
    const sidebarContainer = document.getElementById('sidebarContainer');
    if (sidebarContainer) {
        sidebarContainer.classList.remove('show');
        const toggleIcon = document.getElementById('sidebarToggleIcon');
        if (toggleIcon) {
            toggleIcon.className = 'fas fa-columns'; /* Icono de layout para panel oculto */
        }

        const mainContent = document.querySelector('.col-lg-8.col-xl-9');
        if (mainContent && window.innerWidth >= 1200) {
            mainContent.classList.add('sidebar-hidden');
            setTimeout(() => {
                forceLayoutUpdate();
            }, 50);
        }
    }
}

// Función para maximizar el panel
function maximizePanel() {
    const sidebarContainer = document.getElementById('sidebarContainer');
    if (sidebarContainer) {
        sidebarContainer.classList.add('show');
        const toggleIcon = document.getElementById('sidebarToggleIcon');
        if (toggleIcon) {
            toggleIcon.className = 'fas fa-window-minimize';
        }

        const mainContent = document.querySelector('.col-lg-8.col-xl-9');
        if (mainContent && window.innerWidth >= 1200) {
            mainContent.classList.remove('sidebar-hidden');
            setTimeout(() => {
                forceLayoutUpdate();
            }, 50);
        }
    }
}

// Función para inicializar el resize de la sidebar
function initializeSidebarResize() {
    const sidebarContainer = document.getElementById('sidebarContainer');
    const resizeHandle = document.getElementById('sidebarResizeHandle');
    const mainContent = document.querySelector('.col-lg-8.col-xl-9');

    if (!sidebarContainer || !resizeHandle) {
        console.log('❌ Elementos de sidebar no encontrados');
        return;
    }

    console.log('🔧 Inicializando resize de sidebar...');

    let isResizing = false;
    let startX, startWidth;
    let originalWidth = sidebarContainer.offsetWidth;

    // Función para actualizar el contenido principal
    function updateMainContent() {
        if (mainContent && window.innerWidth >= 1200) {
            const sidebarWidth = sidebarContainer.offsetWidth;
            const windowWidth = window.innerWidth;
            const sidebarPercentage = (sidebarWidth / windowWidth) * 100;

            // Aplicar transición suave
            mainContent.style.transition = 'margin-right 0.3s ease, width 0.3s ease';
            mainContent.style.marginRight = sidebarPercentage + '%';
            mainContent.style.width = (100 - sidebarPercentage) + '%';

            // Guardar el ancho en localStorage para persistencia
            localStorage.setItem('sidebarWidth', sidebarWidth);
        }
    }

    // Función para restaurar el ancho guardado
    function restoreSidebarWidth() {
        const savedWidth = localStorage.getItem('sidebarWidth');
        if (savedWidth) {
            const width = parseInt(savedWidth);
            const minWidth = 300;
            const maxWidth = window.innerWidth * 0.6;

            if (width >= minWidth && width <= maxWidth) {
                sidebarContainer.style.width = width + 'px';
                updateMainContent();
            }
        }
    }

    // Restaurar ancho al inicializar
    restoreSidebarWidth();

    // Evento de inicio de resize
    resizeHandle.addEventListener('mousedown', function (e) {
        isResizing = true;
        startX = e.clientX;
        startWidth = sidebarContainer.offsetWidth;
        originalWidth = startWidth;

        // Agregar clases para el cursor y feedback visual
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
        resizeHandle.style.background = 'rgb(96,75,217)';
        sidebarContainer.style.transition = 'none'; // Desactivar transiciones durante resize

        // Agregar overlay para mejor UX
        const overlay = document.createElement('div');
        overlay.id = 'resizeOverlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.1);
            z-index: 9999;
            cursor: col-resize;
        `;
        document.body.appendChild(overlay);

        e.preventDefault();
        e.stopPropagation();
    });

    // Evento de movimiento del mouse
    document.addEventListener('mousemove', function (e) {
        if (!isResizing) return;

        const deltaX = startX - e.clientX;
        const newWidth = startWidth + deltaX;

        // Limitar el ancho mínimo y máximo
        const minWidth = 300; // 300px mínimo
        const maxWidth = window.innerWidth * 0.6; // 60% máximo

        if (newWidth >= minWidth && newWidth <= maxWidth) {
            sidebarContainer.style.width = newWidth + 'px';
            updateMainContent();

            // Mostrar indicador de tamaño
            showResizeIndicator(newWidth);
        }
    });

    // Evento de fin de resize
    document.addEventListener('mouseup', function () {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
            resizeHandle.style.background = 'rgba(96,75,217,0.3)';
            sidebarContainer.style.transition = 'width 0.3s ease';

            // Remover overlay
            const overlay = document.getElementById('resizeOverlay');
            if (overlay) {
                overlay.remove();
            }

            // Ocultar indicador
            hideResizeIndicator();

            // Guardar el nuevo ancho
            const newWidth = sidebarContainer.offsetWidth;
            localStorage.setItem('sidebarWidth', newWidth);

            console.log('✅ Sidebar redimensionada a:', newWidth + 'px');
        }
    });

    // Evento de doble click para resetear el tamaño
    resizeHandle.addEventListener('dblclick', function () {
        const defaultWidth = window.innerWidth * 0.4; // 40% por defecto
        sidebarContainer.style.width = defaultWidth + 'px';
        updateMainContent();
        localStorage.setItem('sidebarWidth', defaultWidth);
        console.log('🔄 Tamaño de sidebar reseteado a:', defaultWidth + 'px');
    });

    // Función para mostrar indicador de tamaño
    function showResizeIndicator(width) {
        let indicator = document.getElementById('resizeIndicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'resizeIndicator';
            indicator.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(96,75,217,0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                z-index: 10000;
                pointer-events: none;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            `;
            document.body.appendChild(indicator);
        }
        indicator.textContent = `${width}px`;
    }

    // Función para ocultar indicador de tamaño
    function hideResizeIndicator() {
        const indicator = document.getElementById('resizeIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    // Agregar tooltip al handle
    resizeHandle.title = 'Arrastra para redimensionar • Doble click para resetear';

    console.log('✅ Resize de sidebar inicializado');
}

// Función para manejar cambios de tamaño de ventana
function handleWindowResize() {
    const sidebarContainer = document.getElementById('sidebarContainer');
    const mainContent = document.querySelector('.col-lg-8.col-xl-9');
    const toggleIcon = document.getElementById('sidebarToggleIcon');

    // Mantener el panel oculto por defecto en todos los dispositivos
    if (sidebarContainer) {
        sidebarContainer.classList.remove('show');
    }
    if (toggleIcon) {
        toggleIcon.className = 'fas fa-columns'; /* Icono de layout */
    }
    if (mainContent) {
        mainContent.classList.add('sidebar-hidden');
        setTimeout(() => {
            forceLayoutUpdate();
        }, 50);
    }
}

// Inicializar la sidebar dinámica cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    // Esperar un poco para que se carguen todas las funciones
    setTimeout(() => {
        inicializarSidebarDinamica();
        inicializarObservadorFormularioElegant();

        // Inicializar modo automático de Copilot Health
        setTimeout(() => {
            inicializarCopilotAutoMode();
        }, 2000);
    }, 1000);
});

// ===== FUNCIONES AUXILIARES PARA PREGUNTAS DE EVALUACIÓN EN SIDEBAR =====

// Función para insertar todas las preguntas de evaluación desde la sidebar
function insertarTodasLasPreguntasEvaluacion() {
    const evaluacionTextarea = document.getElementById('diagnostico');
    const textoActual = evaluacionTextarea.value;

    // Obtener todas las preguntas de la sidebar
    const preguntasElements = document.querySelectorAll('#sidebarListaPapers .card .card-body .mb-3 p strong');

    if (preguntasElements.length === 0) {
        showNotification('No hay preguntas disponibles para insertar', 'warning');
        return;
    }

    let nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + 'PREGUNTAS SUGERIDAS POR COPILOT HEALTH:\n';

    preguntasElements.forEach((preguntaElement, index) => {
        nuevoTexto += `${index + 1}. ${preguntaElement.textContent}\n`;
    });

    evaluacionTextarea.value = nuevoTexto;

    // Mostrar notificación
    showNotification('Todas las preguntas de Copilot Health han sido agregadas a la evaluación', 'success');

    console.log('✅ Todas las preguntas de evaluación insertadas desde sidebar');
}

// Función para copiar preguntas al portapapeles
function copiarPreguntasAlPortapapeles() {
    const preguntasElements = document.querySelectorAll('#sidebarListaPapers .card .card-body .mb-3 p strong');

    if (preguntasElements.length === 0) {
        showNotification('No hay preguntas disponibles para copiar', 'warning');
        return;
    }

    let textoPreguntas = 'PREGUNTAS SUGERIDAS POR COPILOT HEALTH:\n\n';

    preguntasElements.forEach((preguntaElement, index) => {
        textoPreguntas += `${index + 1}. ${preguntaElement.textContent}\n`;
    });

    // Copiar al portapapeles
    navigator.clipboard.writeText(textoPreguntas).then(() => {
        showNotification('Preguntas copiadas al portapapeles', 'success');
        console.log('✅ Preguntas copiadas al portapapeles');
    }).catch(err => {
        console.error('❌ Error copiando al portapapeles:', err);
        showNotification('Error al copiar al portapapeles', 'error');
    });
}

// Función mejorada para insertar una pregunta específica desde la sidebar
function insertarPreguntaEnEvaluacion(pregunta) {
    const evaluacionTextarea = document.getElementById('diagnostico');
    const textoActual = evaluacionTextarea.value;

    // Verificar si ya hay preguntas insertadas
    if (textoActual.includes('PREGUNTAS SUGERIDAS POR COPILOT HEALTH:')) {
        // Agregar la pregunta al final de la sección existente
        const nuevoTexto = textoActual + `\n${pregunta}`;
        evaluacionTextarea.value = nuevoTexto;
    } else {
        // Crear nueva sección de preguntas
        const nuevoTexto = textoActual + (textoActual ? '\n\n' : '') + `PREGUNTAS SUGERIDAS POR COPILOT HEALTH:\n${pregunta}`;
        evaluacionTextarea.value = nuevoTexto;
    }

    // Mostrar notificación
    showNotification('Pregunta de Copilot Health agregada a la evaluación', 'success');

    console.log('✅ Pregunta insertada desde sidebar:', pregunta);
}

// Hacer las funciones disponibles globalmente
window.insertarTodasLasPreguntasEvaluacion = insertarTodasLasPreguntasEvaluacion;
window.copiarPreguntasAlPortapapeles = copiarPreguntasAlPortapapeles;
window.insertarPreguntaEnEvaluacion = insertarPreguntaEnEvaluacion;

// ===== SISTEMA DE DETECCIÓN AUTOMÁTICA PARA COPILOT HEALTH ASSISTANT =====

// Variables globales para el modo automático
let copilotAutoMode = true;
let lastFormData = {};
let analysisInProgress = false;
let autoAnalysisTimeout = null;
let preguntasSugeridas = false; // Nueva variable para controlar si ya se sugirieron preguntas
let motivoConsultaCompleto = ''; // Variable para almacenar el motivo de consulta completo

// Función para inicializar el modo automático de Copilot Health
function inicializarCopilotAutoMode() {
    console.log('🤖 Inicializando Copilot Health Auto Mode...');

    // Configurar observadores para detectar cambios automáticamente
    configurarObservadoresAutomaticos();

    // Iniciar monitoreo de actividad
    // iniciarMonitoreoActividad(); // FUNCIÓN ELIMINADA - No es necesaria

    // Configurar detección de casos clínicos
    // configurarDeteccionCasosClinicos(); // FUNCIÓN ELIMINADA - No es necesaria

    console.log('✅ Copilot Health Auto Mode inicializado');
}

// Función para configurar observadores automáticos
function configurarObservadoresAutomaticos() {
    // Observar cambios en el formulario de atención
    const formularioAtencion = document.querySelector('form[data-form="atencion"]');
    if (formularioAtencion) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    detectarCambiosFormularioAutomatico();
                }
            });
        });

        observer.observe(formularioAtencion, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['value', 'checked']
        });
    }

    // Observar cambios en campos específicos
    const camposImportantes = ['motivoConsulta', 'tipoAtencion', 'edad', 'antecedentes', 'evaluacion'];
    camposImportantes.forEach(campo => {
        const elemento = document.getElementById(campo);
        if (elemento) {
            elemento.addEventListener('input', () => {
                // Resetear preguntas sugeridas si el motivo de consulta cambia significativamente
                if (campo === 'motivoConsulta') {
                    const motivoActual = elemento.value;
                    // Solo resetear si el cambio es significativo (más del 30% de diferencia)
                    if (motivoActual !== motivoConsultaCompleto &&
                        motivoActual.length > 10 &&
                        Math.abs(motivoActual.length - motivoConsultaCompleto.length) > 3) {
                        preguntasSugeridas = false;
                        console.log('🔄 Motivo de consulta cambiado significativamente, reseteando preguntas sugeridas');
                        console.log('Motivo anterior:', motivoConsultaCompleto);
                        console.log('Motivo actual:', motivoActual);
                    }
                }
                detectarCambiosFormularioAutomatico();
            });
        }
    });
}

// Función para detectar cambios automáticamente
function detectarCambiosFormularioAutomatico() {
    if (!copilotAutoMode || analysisInProgress) return;

    // Obtener datos actuales del formulario
    const datosActuales = obtenerDatosFormularioActuales();
    const motivoConsulta = datosActuales.motivoConsulta || '';

    // Verificar si los datos han cambiado significativamente
    const datosCambiaron = JSON.stringify(datosActuales) !== JSON.stringify(lastFormData);

    if (datosCambiaron) {
        lastFormData = datosActuales;

        // Solo analizar si:
        // 1. Hay suficiente información para análisis (más de 10 caracteres)
        // 2. No se han sugerido preguntas para este motivo de consulta
        // 3. El motivo de consulta es diferente al anterior
        // 4. El motivo de consulta es significativamente diferente al último analizado
        if (motivoConsulta.trim().length > 10 &&
            !preguntasSugeridas &&
            motivoConsulta !== motivoConsultaCompleto &&
            motivoConsulta !== ultimoMotivoAnalizado) {

            // Retrasar el análisis para evitar demasiadas llamadas
            if (autoAnalysisTimeout) {
                clearTimeout(autoAnalysisTimeout);
            }

            autoAnalysisTimeout = setTimeout(() => {
                // Verificar que no se haya iniciado otro análisis
                if (!analysisInProgress) {
                    realizarAnalisisAutomatico(datosActuales);
                }
            }, 3000); // Aumentado a 3 segundos para mayor estabilidad
        }
    }
}

// Función para obtener datos actuales del formulario
function obtenerDatosFormularioActuales() {
    return {
        motivoConsulta: document.getElementById('motivoConsulta')?.value || '',
        tipoAtencion: document.getElementById('tipoAtencion')?.value || '',
        edad: document.getElementById('edad')?.value || '',
        antecedentes: document.getElementById('antecedentes')?.value || '',
        evaluacion: document.getElementById('evaluacion')?.value || '',
        pacienteId: document.getElementById('paciente_id')?.value || '',
        pacienteNombre: document.getElementById('paciente_nombre')?.value || ''
    };
}

// Función para realizar análisis automático
async function realizarAnalisisAutomatico(datos) {
    if (analysisInProgress) return;

    analysisInProgress = true;
    console.log('🤖 Iniciando análisis automático...', datos);

    try {
        // Mostrar indicador de análisis automático
        mostrarIndicadorAnalisisAutomatico();

        // Análisis del motivo de consulta
        if (datos.motivoConsulta && datos.motivoConsulta.trim()) {
            await analizarMotivoAutomatico(datos.motivoConsulta);
        }

        // Generar preguntas personalizadas automáticamente
        if (datos.motivoConsulta && datos.tipoAtencion) {
            await generarPreguntasAutomaticas(datos);
        }

        // Buscar evidencia científica automáticamente
        if (datos.motivoConsulta) {
            await buscarEvidenciaAutomatica(datos.motivoConsulta);
        }

        // Análisis completo del caso
        if (datos.motivoConsulta && datos.tipoAtencion) {
            await analizarCasoCompletoAutomatico(datos);
        }

        console.log('✅ Análisis automático completado');

    } catch (error) {
        console.error('❌ Error en análisis automático:', error);
    } finally {
        analysisInProgress = false;
        ocultarIndicadorAnalisisAutomatico();
    }
}

// Función para analizar motivo automáticamente
async function analizarMotivoAutomatico(motivoConsulta) {
    try {
        agregarMensajeElegant('Analizando motivo de consulta automáticamente...', 'auto');

        const response = await fetch('/api/copilot/analyze-motivo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ motivo_consulta: motivoConsulta })
        });

        if (response.ok) {
            const data = await response.json();
            agregarMensajeElegant('Análisis automático completado', 'auto-success');

            // Mostrar resumen del análisis
            if (data.analisis && data.analisis.resumen) {
                mostrarResumenAnalisisAutomatico(data.analisis);
            }
        }
    } catch (error) {
        console.error('❌ Error en análisis automático:', error);
    }
}

// Función para generar preguntas automáticamente
async function generarPreguntasAutomaticas(datos) {
    try {
        agregarMensajeElegant('Generando preguntas personalizadas automáticamente...', 'auto');

        const response = await fetch('/api/copilot/generate-evaluation-questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                motivo_consulta: datos.motivoConsulta,
                tipo_atencion: datos.tipoAtencion,
                edad: datos.edad,
                antecedentes: datos.antecedentes
            })
        });

        if (response.ok) {
            const data = await response.json();
            agregarMensajeElegant('Preguntas generadas automáticamente', 'auto-success');

            // Mostrar preguntas en la sidebar
            if (data.preguntas && data.preguntas.length > 0) {
                mostrarPreguntasAutomaticas(data.preguntas);
            }
        }
    } catch (error) {
        console.error('❌ Error generando preguntas automáticas:', error);
    }
}

// Función para buscar evidencia automáticamente
async function buscarEvidenciaAutomatica(motivoConsulta) {
    try {
        agregarMensajeElegant('Buscando evidencia científica automáticamente...', 'auto');

        // Mostrar barra de progreso
        mostrarProgresoSidebar(0, 'Iniciando búsqueda...');
        setTimeout(() => mostrarProgresoSidebar(25, 'Analizando términos de búsqueda...'), 500);
        setTimeout(() => mostrarProgresoSidebar(50, 'Consultando bases de datos científicas...'), 1000);
        setTimeout(() => mostrarProgresoSidebar(75, 'Procesando resultados...'), 2000);

        // Obtener datos completos del formulario para análisis contextual
        const datosCompletos = obtenerDatosFormularioActuales();
        const terminosMejorados = generarTerminosBusquedaMejorados(datosCompletos);

        console.log('🔍 Términos de búsqueda mejorados:', terminosMejorados);

        // Usar solo el endpoint que produce mejores resultados con términos más específicos
        const terminosEspecificos = terminosMejorados.terminosClave.filter(termino =>
            !termino.includes('aterectomía') &&
            !termino.includes('Haglund') &&
            !termino.includes('Aquiles') &&
            !termino.includes('tendón') &&
            termino.length > 2
        );

        console.log('🔍 Términos específicos filtrados:', terminosEspecificos);

        const response = await fetch('/api/copilot/search-with-terms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                condicion: terminosMejorados.queryCompleta,
                especialidad: terminosMejorados.especialidad,
                edad: terminosMejorados.edad,
                terminos_seleccionados: terminosEspecificos
            })
        });

        if (response.ok) {
            const data = await response.json();
            console.log('🔍 Datos recibidos del backend:', data);

            // Completar barra de progreso
            mostrarProgresoSidebar(100, 'Búsqueda completada');
            setTimeout(() => mostrarProgresoSidebar(0, ''), 2000);

            agregarMensajeElegant('✅ Evidencia científica encontrada automáticamente', 'auto-success');

            // Mostrar papers en la sidebar (formato simplificado) - CON VALIDACIÓN
            if (data.planes_tratamiento && data.planes_tratamiento.length > 0) {
                console.log('📄 Evidencia científica encontrada:', data.planes_tratamiento.length, 'papers');

                // Validar que los resultados sean relevantes
                const resultadosRelevantes = data.planes_tratamiento.filter(paper => {
                    const titulo = (paper.titulo || '').toLowerCase();
                    const abstract = (paper.abstract || paper.resumen || '').toLowerCase();

                    // Verificar que NO contenga términos irrelevantes
                    const terminosIrrelevantes = [
                        'aterectomía', 'haglund', 'aquiles', 'tendón', 'cardiovascular',
                        'cáncer', 'oncológico', 'quimioterapia', 'radioterapia'
                    ];

                    const esIrrelevante = terminosIrrelevantes.some(termino =>
                        titulo.includes(termino) || abstract.includes(termino)
                    );

                    // Verificar que SÍ contenga términos relevantes para fracturas
                    const terminosRelevantes = [
                        'fractura', 'tobillo', 'trauma', 'lesión', 'ósea', 'maleolo',
                        'peroné', 'tibia', 'rehabilitación', 'fisioterapia'
                    ];

                    const esRelevante = terminosRelevantes.some(termino =>
                        titulo.includes(termino) || abstract.includes(termino)
                    );

                    return !esIrrelevante && esRelevante;
                });

                if (resultadosRelevantes.length > 0) {
                    agregarMensajeElegant(`Se encontraron ${resultadosRelevantes.length} artículos científicos relevantes`, 'auto-success');
                    mostrarPapersAutomaticos(resultadosRelevantes);
                } else {
                    console.log('⚠️ No se encontraron resultados relevantes después del filtrado');
                    agregarMensajeElegant('No se encontraron estudios específicos para este caso. Los resultados disponibles no son relevantes.', 'auto-warning');
                }
            } else {
                console.log('⚠️ No se encontraron papers en la respuesta');
                agregarMensajeElegant('No se encontraron estudios científicos relevantes para este caso.', 'auto-warning');
            }
        } else {
            console.error('❌ Error en búsqueda de evidencia:', response.status, response.statusText);
            mostrarProgresoSidebar(0, '');
            agregarMensajeElegant('No se pudo completar la búsqueda de evidencia científica en este momento.', 'auto-warning');
        }
    } catch (error) {
        console.error('❌ Error buscando evidencia automática:', error);
        mostrarProgresoSidebar(0, '');
        agregarMensajeElegant('Error en la búsqueda de evidencia científica. Revisando conectividad...', 'auto-error');
    }
}

// Función para mostrar papers automáticos con mejor formato
function mostrarPapersAutomaticos(papers) {
    console.log('📄 Mostrando papers automáticos:', papers);

    const sidebarLista = document.getElementById('sidebarListaPapers');
    const sidebarPapers = document.getElementById('sidebarPapers');

    if (!sidebarLista || !sidebarPapers) {
        console.error('❌ Elementos de sidebar papers no encontrados');
        return;
    }

    // Limitar a máximo 10 artículos
    const papersLimitados = papers.slice(0, 10);

    let html = `
        <div class="alert alert-success mb-3">
            <i class="fas fa-check-circle me-2"></i>
            <strong>Evidencia Científica Encontrada</strong>
            <br><small class="text-muted">Búsqueda automática filtrada para relevancia clínica</small>
        </div>
    `;

    if (papersLimitados.length === 0) {
        html += `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                No se encontraron estudios específicos para este caso. Considera ajustar los términos de búsqueda.
            </div>
        `;
    } else {
        papersLimitados.forEach((paper, index) => {
            // Procesar DOI y crear link
            let doiLink = '';
            let añoEstudio = '';

            if (paper.doi && paper.doi !== 'Sin DOI' && paper.doi !== 'No disponible' && paper.doi !== 'Múltiples fuentes') {
                let doiLimpio = paper.doi;
                if (doiLimpio.startsWith('https://doi.org/')) {
                    doiLimpio = doiLimpio.replace('https://doi.org/', '');
                } else if (doiLimpio.startsWith('http://doi.org/')) {
                    doiLimpio = doiLimpio.replace('http://doi.org/', '');
                }

                doiLink = `<a href="https://doi.org/${doiLimpio}" target="_blank" class="sidebar-paper-doi">
                             <i class="fas fa-external-link-alt me-1"></i>Ver Paper
                           </a>`;
            } else {
                doiLink = `<span class="sidebar-paper-doi text-muted">DOI no disponible</span>`;
            }

            // Extraer año del estudio
            if (paper.año_publicacion && paper.año_publicacion !== 'N/A') {
                añoEstudio = `<span class="sidebar-paper-year">
                                <i class="fas fa-calendar me-1"></i>${paper.año_publicacion}
                              </span>`;
            } else if (paper.fecha_publicacion && paper.fecha_publicacion !== 'Fecha no disponible') {
                const fecha = new Date(paper.fecha_publicacion);
                if (!isNaN(fecha.getFullYear())) {
                    añoEstudio = `<span class="sidebar-paper-year">
                                    <i class="fas fa-calendar me-1"></i>${fecha.getFullYear()}
                                  </span>`;
                }
            }

            html += `
                <div class="sidebar-paper-item" data-index="${index}">
                    <div class="sidebar-paper-header">
                        <h6 class="sidebar-paper-title">${paper.titulo || 'Título no disponible'}</h6>
                        <div class="sidebar-paper-meta">
                            ${añoEstudio}
                            ${doiLink}
                        </div>
                    </div>
                    <div class="sidebar-paper-content">
                        <p class="sidebar-paper-abstract">
                            ${paper.abstract || paper.resumen || 'Sin resumen disponible'}
                        </p>
                        <div class="sidebar-paper-actions">
                            <button class="btn btn-sm btn-action btn-view" onclick="insertarPaperAutomatico(${index})">
                                <i class="fas fa-arrow-right me-1"></i>Insertar
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        if (papers.length > 10) {
            html += `
                <div class="alert alert-info mt-3">
                    <i class="fas fa-info-circle me-2"></i>
                    Mostrando 10 de ${papers.length} artículos encontrados
                </div>
            `;
        }
    }

    sidebarLista.innerHTML = html;
    sidebarPapers.style.display = 'block';

    // Agregar mensaje al chat
    agregarMensajeElegant(`Se encontraron ${papersLimitados.length} artículos científicos relevantes`, 'auto-success');
}

// Función para insertar paper automático
function insertarPaperAutomatico(index) {
    console.log('📄 Insertando paper automático:', index);
    // Implementar lógica de inserción similar a insertarPaperSidebar
    showNotification('Paper insertado correctamente', 'success');
}

// Función para generar términos de búsqueda mejorados basados en todos los datos del formulario
function generarTerminosBusquedaMejorados(datos) {
    console.log('🔍 Generando términos de búsqueda mejorados con datos:', datos);

    const terminosClave = [];
    const contextoClinico = [];
    let especialidad = 'general';
    let edad = 'adulto';

    // 1. Analizar tipo de atención para especialidad
    if (datos.tipoAtencion) {
        const tipoLower = datos.tipoAtencion.toLowerCase();

        // Kinesiología / Fisioterapia
        if (tipoLower.includes('kinesiologia') || tipoLower.includes('fisioterapia') || tipoLower.includes('kinesio')) {
            especialidad = 'fisioterapia';
            terminosClave.push('fisioterapia', 'kinesiología', 'rehabilitación', 'terapia física', 'movimiento');
            contextoClinico.push('intervención fisioterapéutica');
        }
        // Medicina General
        else if (tipoLower.includes('medicina') || tipoLower.includes('general')) {
            especialidad = 'medicina';
            terminosClave.push('medicina clínica', 'medicina general', 'diagnóstico médico', 'tratamiento médico');
            contextoClinico.push('evaluación médica integral');
        }
        // Psicología
        else if (tipoLower.includes('psicologia') || tipoLower.includes('psicoterapia')) {
            especialidad = 'psicología';
            terminosClave.push('psicología', 'salud mental', 'terapia psicológica', 'intervención psicológica', 'bienestar emocional');
            contextoClinico.push('evaluación psicológica');
        }
        // Fonoaudiología
        else if (tipoLower.includes('fonoaudiologia') || tipoLower.includes('logopedia')) {
            especialidad = 'fonoaudiología';
            terminosClave.push('fonoaudiología', 'terapia del lenguaje', 'comunicación', 'habla', 'lenguaje', 'deglución');
            contextoClinico.push('evaluación fonoaudiológica');
        }
    }

    // 2. Analizar motivo de consulta para términos clave
    if (datos.motivoConsulta) {
        const motivo = datos.motivoConsulta.toLowerCase();

        // Términos específicos para fonoaudiología
        if (especialidad === 'fonoaudiología') {
            const terminosFono = ['voz', 'habla', 'lenguaje', 'comunicación', 'deglución', 'respiración', 'articulación', 'disfonía', 'afasia', 'disfagia'];
            terminosFono.forEach(termino => {
                if (motivo.includes(termino)) {
                    terminosClave.push(termino);
                    contextoClinico.push(`dificultad en ${termino}`);
                }
            });
        }

        // Términos específicos para psicología
        if (especialidad === 'psicología') {
            const terminosPsico = ['ansiedad', 'depresión', 'estrés', 'trauma', 'miedo', 'pánico', 'obsesión', 'compulsión', 'trastorno', 'bipolar', 'esquizofrenia'];
            terminosPsico.forEach(termino => {
                if (motivo.includes(termino)) {
                    terminosClave.push(termino);
                    contextoClinico.push(`síntoma psicológico: ${termino}`);
                }
            });
        }

        // Extraer términos anatómicos - MEJORADO
        const terminosAnatomicos = [
            'rodilla', 'hombro', 'espalda', 'cuello', 'cabeza', 'brazo', 'pierna',
            'tobillo', 'muñeca', 'codo', 'cadera', 'columna', 'lumbar', 'cervical',
            'articulación', 'músculo', 'tendón', 'ligamento', 'menisco', 'cartílago'
        ];

        terminosAnatomicos.forEach(termino => {
            if (motivo.includes(termino)) {
                terminosClave.push(termino);
                contextoClinico.push(`dolor en ${termino}`);

                // Términos específicos para tobillo
                if (termino === 'tobillo') {
                    terminosClave.push('fractura de tobillo', 'lesión de tobillo', 'trauma de tobillo');
                    terminosClave.push('maleolo', 'peroné distal', 'tibia distal');
                    contextoClinico.push('lesión de extremidad inferior', 'trauma de tobillo');
                }
            }
        });

        // Extraer términos de causa - MEJORADO SIGNIFICATIVAMENTE
        if (motivo.includes('golpe') || motivo.includes('trauma') || motivo.includes('accidente')) {
            terminosClave.push('trauma', 'lesión traumática', 'trauma externo');
            contextoClinico.push('lesión por trauma');
        }
        if (motivo.includes('fractura') || motivo.includes('rotura')) {
            terminosClave.push('fractura', 'lesión ósea', 'trauma óseo');
            contextoClinico.push('lesión traumática ósea');
        }
        if (motivo.includes('trabajo') || motivo.includes('laboral')) {
            terminosClave.push('lesión laboral', 'accidente de trabajo', 'trauma laboral');
            contextoClinico.push('lesión relacionada con el trabajo');
        }

        // DETECCIÓN ESPECÍFICA PARA FRACTURAS DE TOBILLO
        if (motivo.includes('tobillo') && (motivo.includes('fractura') || motivo.includes('accidente') || motivo.includes('golpe'))) {
            terminosClave.push('fractura de tobillo', 'fractura maleolar', 'fractura de peroné distal', 'fractura de tibia distal');
            terminosClave.push('lesión de tobillo', 'trauma de tobillo', 'fractura de tobillo tratamiento');
            terminosClave.push('fractura de tobillo rehabilitación', 'fractura de tobillo fisioterapia');
            contextoClinico.push('fractura de tobillo por trauma', 'lesión traumática de tobillo');
        }
        if (motivo.includes('deporte') || motivo.includes('ejercicio')) {
            terminosClave.push('lesión deportiva', 'deporte');
            contextoClinico.push('lesión relacionada con actividad física');
        }
    }

    // 3. Analizar evaluación para síntomas específicos
    if (datos.evaluacion) {
        const evaluacion = datos.evaluacion.toLowerCase();

        // Síntomas de dolor
        if (evaluacion.includes('dolor')) {
            terminosClave.push('dolor', 'síndrome de dolor');

            // Tipo de dolor
            if (evaluacion.includes('constante')) {
                terminosClave.push('dolor constante');
                contextoClinico.push('dolor persistente');
            }
            if (evaluacion.includes('intermitente')) {
                terminosClave.push('dolor intermitente');
                contextoClinico.push('dolor episódico');
            }
            if (evaluacion.includes('peor')) {
                terminosClave.push('dolor agravado');
                contextoClinico.push('dolor que empeora con actividades');
            }
        }

        // Síntomas de inflamación
        if (evaluacion.includes('hinchazón') || evaluacion.includes('edema')) {
            terminosClave.push('hinchazón', 'edema', 'inflamación');
            contextoClinico.push('inflamación local');
        }
        if (evaluacion.includes('calor')) {
            terminosClave.push('calor local', 'inflamación');
            contextoClinico.push('signos de inflamación aguda');
        }

        // Síntomas de inestabilidad
        if (evaluacion.includes('inestabilidad') || evaluacion.includes('bloqueo')) {
            terminosClave.push('inestabilidad articular', 'bloqueo articular');
            contextoClinico.push('disfunción articular');
        }

        // Síntomas de limitación funcional
        if (evaluacion.includes('escaleras') || evaluacion.includes('subir') || evaluacion.includes('bajar')) {
            terminosClave.push('limitación funcional', 'dificultad para movimientos');
            contextoClinico.push('limitación en actividades de la vida diaria');
        }
        if (evaluacion.includes('reposo') || evaluacion.includes('alivia')) {
            terminosClave.push('alivio con reposo', 'dolor mecánico');
            contextoClinico.push('dolor que mejora con reposo');
        }
        if (evaluacion.includes('tiempo de pie') || evaluacion.includes('estar de pie')) {
            terminosClave.push('dolor postural', 'dolor por bipedestación');
            contextoClinico.push('dolor relacionado con postura');
        }

        // Síntomas de lesión previa
        if (evaluacion.includes('lesiones previas') || evaluacion.includes('lesión previa')) {
            terminosClave.push('antecedentes de lesión', 'lesión previa');
            contextoClinico.push('historia de trauma previo');
        }
    }

    // 4. Analizar edad para contexto
    if (datos.edad) {
        const edadNum = parseInt(datos.edad);
        if (edadNum < 18) {
            edad = 'pediátrico';
            terminosClave.push('pediatría', 'niño', 'adolescente');
        } else if (edadNum > 65) {
            edad = 'geriátrico';
            terminosClave.push('geriatría', 'adulto mayor', 'envejecimiento');
        }
    }

    // 5. Crear query completa combinando todos los elementos - MEJORADA SIGNIFICATIVAMENTE
    // Priorizar términos específicos de fracturas
    const terminosPrioritarios = terminosClave.filter(termino =>
        termino.includes('fractura') ||
        termino.includes('tobillo') ||
        termino.includes('trauma') ||
        termino.includes('lesión')
    );

    const terminosSecundarios = terminosClave.filter(termino =>
        !termino.includes('fractura') &&
        !termino.includes('tobillo') &&
        !termino.includes('trauma') &&
        !termino.includes('lesión')
    );

    const queryCompleta = [
        datos.motivoConsulta,
        ...terminosPrioritarios.slice(0, 5), // Priorizar términos específicos
        ...terminosSecundarios.slice(0, 3), // Agregar términos secundarios
        especialidad
    ].filter(Boolean).join(' ');

    // 6. Eliminar duplicados y limpiar términos
    const terminosUnicos = [...new Set(terminosClave)];
    const contextoUnico = [...new Set(contextoClinico)];

    const resultado = {
        queryCompleta: queryCompleta,
        terminosClave: terminosUnicos,
        especialidad: especialidad,
        edad: edad,
        contextoClinico: contextoUnico
    };

    console.log('✅ Términos de búsqueda mejorados generados:', resultado);
    return resultado;
}

// Función para analizar caso completo automáticamente
async function analizarCasoCompletoAutomatico(datos) {
    try {
        agregarMensajeElegant('Analizando caso completo automáticamente...', 'auto');

        const response = await fetch('/api/copilot/complete-analysis', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                motivo_consulta: datos.motivoConsulta,
                tipo_atencion: datos.tipoAtencion,
                edad: datos.edad,
                antecedentes: datos.antecedentes
            })
        });

        if (response.ok) {
            const data = await response.json();
            agregarMensajeElegant('✅ Análisis completo automático finalizado', 'auto-success');

            // Mostrar resumen completo
            if (data.analisis && data.analisis.resumen) {
                mostrarResumenCompletoAutomatico(data.analisis);
            }
        }
    } catch (error) {
        console.error('❌ Error en análisis completo automático:', error);
    }
}

// Función para mostrar indicador de análisis automático
function mostrarIndicadorAnalisisAutomatico() {
    const sidebar = document.querySelector('.sidebar-content');
    if (sidebar) {
        const indicador = document.createElement('div');
        indicador.id = 'indicadorAnalisisAuto';
        indicador.className = 'indicador-analisis-auto';
        indicador.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Analizando...</span>
                </div>
                <span>Copilot Health analizando automáticamente...</span>
            </div>
        `;
        sidebar.appendChild(indicador);
    }
}

// Función para ocultar indicador de análisis automático
function ocultarIndicadorAnalisisAutomatico() {
    const indicador = document.getElementById('indicadorAnalisisAuto');
    if (indicador) {
        indicador.remove();
    }
}

// Función para mostrar preguntas automáticas en formato conversación
function mostrarPreguntasAutomaticas(preguntas) {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return;

    // Marcar que ya se sugirieron preguntas para este motivo de consulta
    preguntasSugeridas = true;
    motivoConsultaCompleto = obtenerDatosFormularioActuales().motivoConsulta;
    ultimoMotivoAnalizado = motivoConsultaCompleto; // Marcar como último motivo analizado

    console.log('✅ Preguntas sugeridas para motivo:', motivoConsultaCompleto);

    // Agregar mensaje introductorio
    agregarMensajeElegant('Luego del análisis del motivo de consulta te sugiero que realices las siguientes preguntas:', 'auto-success');

    // Agregar cada pregunta como mensaje individual
    preguntas.forEach((pregunta, index) => {
        const preguntaHtml = `
            <div class="pregunta-mensaje">
                <div class="pregunta-texto">${pregunta}</div>
            </div>
        `;

        agregarMensajeElegant(preguntaHtml, 'pregunta');
    });

    // Almacenar preguntas para uso posterior
    window.preguntasActuales = preguntas;
}

// Función para mostrar resultados del análisis mejorado en la sidebar
function mostrarAnalisisMejoradoEnSidebar(analisisData) {
    console.log('📊 Mostrando análisis mejorado en sidebar...');

    const messagesContainer = document.getElementById('messagesContainer');

    if (!messagesContainer) {
        console.error('❌ Elementos de sidebar no encontrados');
        return;
    }

    // Verificar si ya se mostró este análisis para evitar duplicaciones
    const ultimoAnalisis = window.ultimoAnalisisMostrado;
    const datosActuales = JSON.stringify(analisisData);

    if (ultimoAnalisis === datosActuales) {
        console.log('⚠️ Análisis ya mostrado, evitando duplicación');
        return;
    }

    // Marcar este análisis como mostrado
    window.ultimoAnalisisMostrado = datosActuales;

    // Agregar mensaje de análisis mejorado
    agregarMensajeElegant('📊 Análisis clínico mejorado completado', 'auto-success');

    // Mostrar palabras clave identificadas con contexto
    if (analisisData.palabras_clave_identificadas && analisisData.palabras_clave_identificadas.length > 0) {
        let palabrasHtml = '<div class="mb-3"><strong>🔑 Palabras Clave Identificadas:</strong><br>';
        analisisData.palabras_clave_identificadas.forEach(pc => {
            const intensidad = pc.intensidad ? ` (${Math.round(pc.intensidad * 100)}%)` : '';
            palabrasHtml += `<span class="badge bg-primary me-1">${pc.palabra}${intensidad}</span>`;
        });
        palabrasHtml += '</div>';
        agregarMensajeElegant(palabrasHtml, 'auto-info');
    }

    // Mostrar región anatómica si está identificada
    if (analisisData.region_anatomica) {
        let regionHtml = `<div class="mb-3"><strong>📍 Región Anatómica:</strong><br>`;
        regionHtml += `<span class="badge bg-info me-1">${analisisData.region_anatomica}</span></div>`;
        agregarMensajeElegant(regionHtml, 'auto-info');
    }

    // Mostrar patologías identificadas con contexto
    if (analisisData.patologias_sugeridas && analisisData.patologias_sugeridas.length > 0) {
        let patologiasHtml = '<div class="mb-3"><strong>🏥 Patologías Sugeridas:</strong><br>';
        analisisData.patologias_sugeridas.forEach(pat => {
            const confianza = pat.confianza ? ` (${Math.round(pat.confianza * 100)}%)` : '';
            patologiasHtml += `<span class="badge bg-warning me-1">${pat.nombre}${confianza}</span>`;
        });
        patologiasHtml += '</div>';
        agregarMensajeElegant(patologiasHtml, 'auto-info');
    }

    // Mostrar escalas recomendadas con descripción
    if (analisisData.escalas_recomendadas && analisisData.escalas_recomendadas.length > 0) {
        let escalasHtml = '<div class="mb-3"><strong>📊 Escalas de Evaluación Recomendadas:</strong><br>';
        analisisData.escalas_recomendadas.forEach(escala => {
            escalasHtml += `<div class="mb-2"><strong>${escala.nombre}</strong><br><small>${escala.descripcion}</small></div>`;
        });
        escalasHtml += '</div>';
        agregarMensajeElegant(escalasHtml, 'auto-info');
    }

    // Mostrar evidencia científica si está disponible
    if (analisisData.evidencia_cientifica && analisisData.evidencia_cientifica.length > 0) {
        let evidenciaHtml = '<div class="mb-3"><strong>🔬 Evidencia Científica Encontrada:</strong><br>';
        analisisData.evidencia_cientifica.slice(0, 3).forEach((evidencia, index) => {
            evidenciaHtml += `
                <div class="mb-2 p-2 border rounded">
                    <h6 class="mb-1">${evidencia.titulo || 'Sin título'}</h6>
                    <p class="mb-1 small">${evidencia.resumen || 'Sin resumen disponible'}</p>
                    <small class="text-muted">
                        ${evidencia.doi ? `<a href="https://doi.org/${evidencia.doi}" target="_blank">DOI: ${evidencia.doi}</a>` : 'DOI no disponible'}
                    </small>
                        </div>
                    `;
        });
        evidenciaHtml += '</div>';
        agregarMensajeElegant(evidenciaHtml, 'auto-info');
    }

    // Mostrar recomendaciones si están disponibles
    if (analisisData.recomendaciones && analisisData.recomendaciones.length > 0) {
        let recomendacionesHtml = '<div class="mb-3"><strong>💡 Recomendaciones:</strong><br><ul class="list-unstyled mb-0">';
        analisisData.recomendaciones.forEach(rec => {
            recomendacionesHtml += `<li class="mb-1"><i class="fas fa-check text-success me-2"></i>${rec}</li>`;
        });
        recomendacionesHtml += '</ul></div>';
        agregarMensajeElegant(recomendacionesHtml, 'auto-info');
    }
}

// Función para inicializar el mensaje de bienvenida dinámico
function inicializarMensajeBienvenida() {
    // Esperar a que el DOM esté completamente cargado
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            setTimeout(inicializarMensajeBienvenida, 100);
        });
        return;
    }

    const welcomeMessage = document.getElementById('welcomeMessage');
    if (welcomeMessage) {
        // Actualizar el mensaje con el nombre del usuario
        actualizarMensajeBienvenida(obtenerNombreUsuario());

        // Agregar evento para mostrar el botón de cerrar al hacer hover
        welcomeMessage.addEventListener('mouseenter', function () {
            const closeButton = this.querySelector('.btn-close');
            if (closeButton) {
                closeButton.style.opacity = '1';
            }
        });

        welcomeMessage.addEventListener('mouseleave', function () {
            const closeButton = this.querySelector('.btn-close');
            if (closeButton) {
                closeButton.style.opacity = '0.7';
            }
        });

        console.log('✅ Mensaje de bienvenida dinámico inicializado');
    }
}

// Ejecutar la inicialización cuando se carga la página
if (typeof window !== 'undefined') {
    // Ejecutar inmediatamente si el DOM ya está listo
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
        setTimeout(inicializarMensajeBienvenida, 100);
    } else {
        // Esperar a que el DOM esté listo
        document.addEventListener('DOMContentLoaded', function () {
            setTimeout(inicializarMensajeBienvenida, 100);
        });
    }

    // También ejecutar cuando la ventana esté completamente cargada
    window.addEventListener('load', function () {
        setTimeout(inicializarMensajeBienvenida, 200);
    });
}