document.addEventListener('DOMContentLoaded', function () {
    // Inicializar componentes existentes
    initMaps();
    initAvailabilityToggle();
    setupMobileNav();
    initRequestInteractions();
    handleFileUpload();

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

    // Si la pestaña de pacientes está activa al cargar, cargar los datos
    if (patientsTab && patientsTab.classList.contains('active')) {
        cargarListaPacientes();
    }

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
            color: '#3a86ff',
            fillColor: '#3a86ff',
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
                color: '#3a86ff',
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

                    // Actualizar historial y cambiar a la pestaña
                    actualizarHistorialAtenciones();
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
// FUNCIONES PARA GESTIÓN DE PACIENTES
// ========================================

// Variable global para almacenar la lista de pacientes
let pacientesList = [];

// Cargar lista de pacientes al inicializar
function cargarListaPacientes() {
    console.log('📋 Cargando lista de pacientes...');

    fetch('/api/professional/patients')
        .then(response => response.json())
        .then(data => {
            console.log('📥 Respuesta del servidor:', data);

            if (data.success) {
                pacientesList = data.pacientes;
                actualizarTablaPacientes();
                actualizarContadorPacientes();
                console.log(`✅ ${data.total} pacientes cargados`);
            } else {
                console.error('❌ Error cargando pacientes:', data.message);
                showNotification('Error al cargar la lista de pacientes', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error de red:', error);
            showNotification('Error de conexión al cargar pacientes', 'error');
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

    const pacientes = filteredList || pacientesList;

    if (pacientes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-muted py-4">
                    <i class="fas fa-users fa-2x mb-2"></i>
                    <br>No tienes pacientes registrados
                    <br><small>Haz clic en "Agregar Paciente" para comenzar</small>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = pacientes.map(paciente => `
        <tr>
            <td>
                <div class="patient-info-vertical">
                    <div>
                        <strong>${paciente.nombre_completo}</strong>
                        <br><small class="text-muted">RUT: ${paciente.rut}</small>
                    </div>
                </div>
            </td>
            <td>
                <span class="badge bg-light text-dark">${paciente.edad || 'No especificada'} años</span>
                <br><small class="text-muted">${paciente.genero || 'No especificado'}</small>
            </td>
            <td>
                <div>
                    ${paciente.telefono ? `<i class="fas fa-phone text-muted"></i> ${paciente.telefono}` : ''}
                    ${paciente.telefono && paciente.email ? '<br>' : ''}
                    ${paciente.email ? `<i class="fas fa-envelope text-muted"></i> ${paciente.email}` : ''}
                </div>
                <small class="text-muted">
                    ${paciente.num_atenciones || 0} atenciones
                    ${paciente.ultima_consulta ? `<br>Última: ${formatearFecha(paciente.ultima_consulta)}` : ''}
                </small>
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-outline-primary btn-sm" title="Ver historial" onclick="verHistorialPaciente('${paciente.paciente_id}')">
                        <i class="fas fa-history"></i>
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" title="Editar" onclick="editarPaciente('${paciente.paciente_id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" title="Eliminar" onclick="eliminarPaciente('${paciente.paciente_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');

    console.log(`✅ Tabla actualizada con ${pacientes.length} pacientes`);
}

// Actualizar contador de pacientes
function actualizarContadorPacientes() {
    const total = pacientesList.length;
    const activos = pacientesList.filter(p => p.estado_relacion === 'activo').length;

    // Actualizar en la interfaz si existe el elemento
    const statsElements = document.querySelectorAll('[data-stat="pacientes"]');
    statsElements.forEach(element => {
        element.textContent = total;
    });

    console.log(`📊 Pacientes: ${total} total, ${activos} activos`);
}

// Mostrar modal para agregar paciente
function showAddPatientModal() {
    console.log('➕ Abriendo modal para agregar paciente');

    const modal = document.getElementById('addPatientModal');
    if (!modal) {
        console.error('❌ Modal addPatientModal no encontrado');
        return;
    }

    // Limpiar el formulario
    const form = document.getElementById('addPatientForm');
    if (form) {
        form.reset();
    }

    // Cambiar el título del modal
    const modalLabel = document.getElementById('addPatientModalLabel');
    if (modalLabel) {
        modalLabel.textContent = 'Agregar Nuevo Paciente';
    }

    // Mostrar el modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
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

                // Recargar lista de pacientes
                cargarListaPacientes();

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
    const paciente = pacientesList.find(p => p.paciente_id === pacienteId);
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
    const paciente = pacientesList.find(p => p.paciente_id === pacienteId);
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

    let filteredPatients = pacientesList;

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

// Alias para compatibilidad con el HTML existente
function editPatient(pacienteId) {
    editarPaciente(pacienteId);
}

function viewPatientHistory(pacienteId) {
    verHistorialPaciente(pacienteId);
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
                            `<button class="btn btn-sm btn-outline-primary me-1" onclick="previewArchivo('${archivo.archivo_id}', '${archivo.nombre_archivo}')">
                                    <i class="fas fa-eye"></i> Ver
                                </button>` : ''}
                            <button class="btn btn-sm btn-outline-secondary" onclick="downloadArchivo('${archivo.archivo_id}', '${archivo.nombre_archivo}')">
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
                    onclick="removeFile('${file.name}')">
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

