// Funciones globales para el dashboard profesional
// Este archivo debe cargarse antes que professional.js

// Funci n para mostrar modal de agregar paciente
window.showAddPatientModal = function () {
    console.log('  Abriendo modal para agregar paciente');

    const modal = document.getElementById('addPatientModal');
    if (!modal) {
        console.error('  Modal addPatientModal no encontrado');
        return;
    }

    // Limpiar el formulario
    const form = document.getElementById('addPatientForm');
    if (form) {
        form.reset();
    }

    // Cambiar el t tulo del modal
    const modalLabel = document.getElementById('addPatientModalLabel');
    if (modalLabel) {
        modalLabel.textContent = 'Agregar Nuevo Paciente';
    }

    // Mostrar el modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
};

// Funci n para ver historial del paciente
window.viewPatientHistory = function (pacienteId) {
    console.log(`  Viendo historial del paciente: ${pacienteId}`);

    // Verificar si la función verHistorialPaciente está disponible
    if (typeof verHistorialPaciente === 'function') {
        console.log('  Función verHistorialPaciente encontrada, ejecutando...');
        try {
            verHistorialPaciente(pacienteId);
        } catch (error) {
            console.error('  Error ejecutando verHistorialPaciente:', error);
            if (typeof showNotification === 'function') {
                showNotification('Error de conexión al obtener historial', 'error');
            }
        }
    } else {
        console.error('  Función verHistorialPaciente no está disponible');
        console.log('  Funciones disponibles en window:', Object.keys(window).filter(key => key.includes('Historial') || key.includes('Paciente')));

        // Fallback: intentar hacer la petición directamente
        console.log('  Intentando petición directa...');
        fetch(`/api/professional/patients/${pacienteId}`, {
            method: 'GET',
            credentials: 'include'
        })
            .then(response => {
                console.log('  Respuesta directa:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('  Datos recibidos directamente:', data);
                if (data.success) {
                    // Mostrar modal con los datos
                    const modal = document.getElementById('patientHistoryModal');
                    if (modal) {
                        const bootstrapModal = new bootstrap.Modal(modal);
                        bootstrapModal.show();
                    }
                } else {
                    throw new Error(data.message || 'Error al obtener historial');
                }
            })
            .catch(error => {
                console.error('  Error en petición directa:', error);
                if (typeof showNotification === 'function') {
                    showNotification('Error de conexión al obtener historial', 'error');
                }
            });
    }
};

// Funci n para editar paciente
window.editPatient = function (pacienteId) {
    console.log(`  Editando paciente: ${pacienteId}`);

    if (typeof editarPaciente === 'function') {
        editarPaciente(pacienteId);
    } else {
        console.error('  Funci n editarPaciente no est  disponible');
        // Fallback: mostrar modal de agregar paciente
        showAddPatientModal();
    }
};

// Funci n para nueva consulta
window.newConsultation = function (pacienteId) {
    console.log(`  Nueva consulta para paciente: ${pacienteId}`);

    // Buscar el paciente en la lista local
    const paciente = window.pacientesList ? window.pacientesList.find(p => p.paciente_id === pacienteId) : null;
    if (!paciente) {
        console.error('  Paciente no encontrado en la lista local');
        if (typeof showNotification === 'function') {
            showNotification('Paciente no encontrado', 'error');
        }
        return;
    }

    // Llenar el formulario de nueva cita con los datos del paciente
    const appointmentPatientSelect = document.getElementById('appointmentPatient');
    if (appointmentPatientSelect) {
        appointmentPatientSelect.value = pacienteId;
    }

    // Establecer la fecha actual como fecha por defecto
    const appointmentDateInput = document.getElementById('appointmentDate');
    if (appointmentDateInput) {
        const today = new Date().toISOString().split('T')[0];
        appointmentDateInput.value = today;
    }

    // Mostrar el modal de programar cita
    const scheduleModal = document.getElementById('scheduleModal');
    if (scheduleModal) {
        const bootstrapModal = new bootstrap.Modal(scheduleModal);
        bootstrapModal.show();
    } else {
        console.error('  Modal de programar cita no encontrado');
        if (typeof showNotification === 'function') {
            showNotification('Error: Modal de programar cita no encontrado', 'error');
        }
    }
};

// Funci n para guardar paciente
window.savePatient = function () {
    console.log('  Guardando paciente...');

    const form = document.getElementById('addPatientForm');
    if (!form) {
        console.error('  Formulario no encontrado');
        return;
    }

    // Obtener datos del formulario
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

    console.log('  Datos del paciente:', pacienteData);

    // Validar campos requeridos
    if (!pacienteData.nombre_completo) {
        if (typeof showNotification === 'function') {
            showNotification('El nombre completo es requerido', 'error');
        }
        return;
    }

    if (!pacienteData.rut) {
        if (typeof showNotification === 'function') {
            showNotification('El RUT es requerido', 'error');
        }
        return;
    }

    // Verificar si es edici n o nuevo paciente
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
            console.log('  Respuesta del servidor:', data);

            if (data.success) {
                if (typeof showNotification === 'function') {
                    showNotification(
                        isEditing ? 'Paciente actualizado exitosamente' : 'Paciente agregado exitosamente',
                        'success'
                    );
                }

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addPatientModal'));
                if (modal) {
                    modal.hide();
                }

                // Recargar lista de pacientes
                if (typeof cargarListaPacientes === 'function') {
                    cargarListaPacientes();
                }

                // Limpiar formulario
                form.reset();
                form.removeAttribute('data-editing-id');

            } else {
                if (typeof showNotification === 'function') {
                    showNotification(data.message || 'Error al guardar paciente', 'error');
                }
            }
        })
        .catch(error => {
            console.error('  Error:', error);
            if (typeof showNotification === 'function') {
                showNotification('Error de conexi n al guardar paciente', 'error');
            }
        });
};

// Funci n para guardar cita
window.saveAppointment = function () {
    console.log('  Guardando nueva cita...');

    const form = document.getElementById('scheduleForm');
    if (!form) {
        console.error('  Formulario de cita no encontrado');
        if (typeof showNotification === 'function') {
            showNotification('Error: Formulario no encontrado', 'error');
        }
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

    console.log('  Datos de la cita:', appointmentData);

    // Validar campos requeridos
    if (!appointmentData.paciente_id) {
        if (typeof showNotification === 'function') {
            showNotification('Debe seleccionar un paciente', 'error');
        }
        return;
    }

    if (!appointmentData.fecha) {
        if (typeof showNotification === 'function') {
            showNotification('Debe seleccionar una fecha', 'error');
        }
        return;
    }

    if (!appointmentData.hora) {
        if (typeof showNotification === 'function') {
            showNotification('Debe seleccionar una hora', 'error');
        }
        return;
    }

    if (!appointmentData.tipo_atencion) {
        if (typeof showNotification === 'function') {
            showNotification('Debe seleccionar un tipo de atenci n', 'error');
        }
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
            console.log('  Respuesta del servidor:', data);

            if (data.success) {
                if (typeof showNotification === 'function') {
                    showNotification('Cita agendada exitosamente', 'success');
                }

                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleModal'));
                if (modal) {
                    modal.hide();
                }

                // Limpiar formulario
                form.reset();

                // Recargar agenda si est  visible
                const scheduleTab = document.querySelector('button[data-bs-target="#schedule"]');
                if (scheduleTab && scheduleTab.classList.contains('active')) {
                    // Aqu  podr as recargar la agenda
                    console.log('  Recargando agenda...');
                }

            } else {
                if (typeof showNotification === 'function') {
                    showNotification(data.message || 'Error al agendar la cita', 'error');
                }
            }
        })
        .catch(error => {
            console.error('  Error:', error);
            if (typeof showNotification === 'function') {
                showNotification('Error de conexi n al agendar la cita', 'error');
            }
        });
};

// Variable global para almacenar la lista de pacientes
window.pacientesList = [];

// Funci n de notificaci n b sica si no existe
if (typeof window.showNotification === 'undefined') {
    window.showNotification = function (message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
        // Crear un toast b sico si Bootstrap est  disponible
        if (typeof bootstrap !== 'undefined') {
            const toastContainer = document.querySelector('.toast-container');
            if (toastContainer) {
                const toast = document.createElement('div');
                toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
                toast.setAttribute('role', 'alert');
                toast.innerHTML = `
                    <div class="d-flex">
                        <div class="toast-body">${message}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                `;
                toastContainer.appendChild(toast);
                const bsToast = new bootstrap.Toast(toast);
                bsToast.show();
            }
        }
    };
}

console.log('  Funciones globales cargadas correctamente');
// Última actualización: 2025-08-01 13:06:22
