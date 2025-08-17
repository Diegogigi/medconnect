// ==========================================================================
// MEDCONNECT - PROFILE EDIT FUNCTIONALITY
// JavaScript para la edici n de perfil de usuario
// ==========================================================================

// Variables globales
let isEditingPersonal = false;
let isEditingMedical = false;
let originalPersonalData = {};
let originalMedicalData = {};

// Inicializaci n cuando el DOM est  listo
document.addEventListener('DOMContentLoaded', function () {
    initializeProfileEdit();
    attachEventListeners();
});

// Funci n de inicializaci n
function initializeProfileEdit() {
    // Capturar datos originales para poder cancelar cambios
    captureOriginalData();

    // Configurar tooltips si est n disponibles
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Capturar datos originales
function captureOriginalData() {
    // Informaci n personal
    const infoValues = document.querySelectorAll('.info-value');
    if (infoValues.length >= 6) {
        const fullName = infoValues[0]?.textContent?.trim() || '';
        const [nombre, ...apellidoParts] = fullName.split(' ');

        originalPersonalData = {
            nombre: nombre || '',
            apellido: apellidoParts.join(' ') || '',
            fecha_nacimiento: infoValues[2]?.textContent?.trim() || '',
            genero: infoValues[3]?.textContent?.trim() || '',
            telefono: infoValues[4]?.textContent?.replace(/[^\d]/g, '') || '',
            email: infoValues[5]?.textContent?.replace(/[^\w@.-]/g, '') || '',
            direccion: '',
            ciudad: ''
        };

        // Direcci n ( ltimo elemento)
        const direccionElement = document.querySelector('.info-item:last-child .info-value');
        if (direccionElement) {
            const direccionText = direccionElement.textContent?.trim() || '';
            const parts = direccionText.split(',');
            originalPersonalData.direccion = parts[0]?.trim() || '';
            originalPersonalData.ciudad = parts[1]?.trim() || '';
        }
    }
}

// Adjuntar event listeners
function attachEventListeners() {
    // Configuraciones de notificaciones
    const notificationSwitches = document.querySelectorAll('.form-check-input[type="checkbox"]');
    notificationSwitches.forEach(switchEl => {
        switchEl.addEventListener('change', handleNotificationChange);
    });
}

// Alternar edici n de informaci n personal
function togglePersonalEdit() {
    if (isEditingPersonal) {
        cancelPersonalEdit();
    } else {
        startPersonalEdit();
    }
}

// Iniciar edici n de informaci n personal
function startPersonalEdit() {
    isEditingPersonal = true;

    const personalSection = document.querySelector('.profile-section .profile-section-body');
    if (!personalSection) return;

    // Crear formulario de edici n
    const editForm = createPersonalEditForm();

    // Reemplazar contenido con formulario
    personalSection.innerHTML = editForm;

    // Actualizar bot n
    updateEditButton('personal', true);

    // Adjuntar eventos del formulario
    attachPersonalFormEvents();

    showNotification('Modo de edici n activado', 'info');
}

// Crear formulario de edici n personal
function createPersonalEditForm() {
    return `
        <form id="personalEditForm" class="needs-validation" novalidate>
            <div class="info-grid">
                <div class="info-item">
                    <label for="nombre" class="info-label">Nombre</label>
                    <input type="text" class="form-control" id="nombre" name="nombre" 
                           value="${originalPersonalData.nombre}" required>
                    <div class="invalid-feedback">El nombre es requerido</div>
                </div>
                <div class="info-item">
                    <label for="apellido" class="info-label">Apellido</label>
                    <input type="text" class="form-control" id="apellido" name="apellido" 
                           value="${originalPersonalData.apellido}" required>
                    <div class="invalid-feedback">El apellido es requerido</div>
                </div>
                <div class="info-item">
                    <label for="fecha_nacimiento" class="info-label">Fecha de nacimiento</label>
                    <input type="date" class="form-control" id="fecha_nacimiento" name="fecha_nacimiento" 
                           value="${originalPersonalData.fecha_nacimiento}">
                </div>
                <div class="info-item">
                    <label for="genero" class="info-label">G nero</label>
                    <select class="form-control" id="genero" name="genero">
                        <option value="">Seleccionar...</option>
                        <option value="Masculino" ${originalPersonalData.genero === 'Masculino' ? 'selected' : ''}>Masculino</option>
                        <option value="Femenino" ${originalPersonalData.genero === 'Femenino' ? 'selected' : ''}>Femenino</option>
                        <option value="Otro" ${originalPersonalData.genero === 'Otro' ? 'selected' : ''}>Otro</option>
                    </select>
                </div>
                <div class="info-item">
                    <label for="telefono" class="info-label">Tel fono</label>
                    <input type="tel" class="form-control" id="telefono" name="telefono" 
                           value="${originalPersonalData.telefono}" 
                           placeholder="Ej: 56979712175">
                </div>
                <div class="info-item">
                    <label for="email" class="info-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" 
                           value="${originalPersonalData.email}" required>
                    <div class="invalid-feedback">Email v lido es requerido</div>
                </div>
            </div>
            <div class="info-item mt-3">
                <label for="direccion" class="info-label">Direcci n</label>
                <input type="text" class="form-control mb-2" id="direccion" name="direccion" 
                       value="${originalPersonalData.direccion}" 
                       placeholder="Ej: Av. Libertad 1234">
                <label for="ciudad" class="info-label">Ciudad</label>
                <input type="text" class="form-control" id="ciudad" name="ciudad" 
                       value="${originalPersonalData.ciudad}" 
                       placeholder="Ej: Santiago">
            </div>
            <div class="d-flex gap-2 mt-4">
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save me-2"></i>Guardar Cambios
                </button>
                <button type="button" class="btn btn-secondary" onclick="cancelPersonalEdit()">
                    <i class="fas fa-times me-2"></i>Cancelar
                </button>
            </div>
        </form>
    `;
}

// Adjuntar eventos del formulario personal
function attachPersonalFormEvents() {
    const form = document.getElementById('personalEditForm');
    if (form) {
        form.addEventListener('submit', handlePersonalFormSubmit);
    }
}

// Manejar env o del formulario personal
async function handlePersonalFormSubmit(event) {
    event.preventDefault();

    const form = event.target;

    // Validar formulario
    if (!form.checkValidity()) {
        event.stopPropagation();
        form.classList.add('was-validated');
        return;
    }

    // Recopilar datos del formulario
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
        data[key] = value.trim();
    }

    // Mostrar loading
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Guardando...';
    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/profile/personal', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showNotification('  Informaci n personal actualizada exitosamente', 'success');

            // Actualizar datos originales
            originalPersonalData = { ...data };

            // Salir del modo edici n
            cancelPersonalEdit();

            // Recargar la p gina para mostrar los cambios
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            throw new Error(result.error || 'Error actualizando informaci n');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification(`  ${error.message}`, 'error');

        // Restaurar bot n
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Cancelar edici n personal
function cancelPersonalEdit() {
    isEditingPersonal = false;

    // Restaurar contenido original
    restorePersonalContent();

    // Actualizar bot n
    updateEditButton('personal', false);

    showNotification('Edici n cancelada', 'info');
}

// Restaurar contenido personal original
function restorePersonalContent() {
    const personalSection = document.querySelector('.profile-section .profile-section-body');
    if (!personalSection) return;

    const fullName = `${originalPersonalData.nombre} ${originalPersonalData.apellido}`.trim();

    personalSection.innerHTML = `
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Nombre completo</div>
                <p class="info-value">${fullName || 'No especificado'}</p>
            </div>
            <div class="info-item">
                <div class="info-label">ID de Usuario</div>
                <p class="info-value">1</p>
            </div>
            <div class="info-item">
                <div class="info-label">Fecha de nacimiento</div>
                <p class="info-value">${originalPersonalData.fecha_nacimiento || 'No especificada'}</p>
            </div>
            <div class="info-item">
                <div class="info-label">G nero</div>
                <p class="info-value">${originalPersonalData.genero || 'No especificado'}</p>
            </div>
            <div class="info-item">
                <div class="info-label">Tel fono</div>
                <p class="info-value">
                    <i class="fas fa-phone me-2 text-success"></i>
                    ${originalPersonalData.telefono || 'No especificado'}
                </p>
            </div>
            <div class="info-item">
                <div class="info-label">Email</div>
                <p class="info-value">
                    <i class="fas fa-envelope me-2 text-info"></i>
                    ${originalPersonalData.email || 'No especificado'}
                </p>
            </div>
        </div>
        <div class="info-item mt-3">
            <div class="info-label">Direcci n completa</div>
            <p class="info-value">
                <i class="fas fa-map-marker-alt me-2 text-primary"></i>
                ${originalPersonalData.direccion ? `${originalPersonalData.direccion}${originalPersonalData.ciudad ? ', ' + originalPersonalData.ciudad : ''}` : 'No especificada'}
            </p>
        </div>
    `;
}

// Actualizar bot n de edici n
function updateEditButton(type, isEditing) {
    let button;

    if (type === 'personal') {
        button = document.querySelector('[onclick="editPersonalInfo()"]');
    } else if (type === 'medical') {
        button = document.getElementById('editMedicalBtn');
    }

    if (button) {
        if (isEditing) {
            button.innerHTML = '<i class="fas fa-times me-1"></i>Cancelar';
            button.classList.remove('btn-outline-primary');
            button.classList.add('btn-outline-danger');
        } else {
            button.innerHTML = '<i class="fas fa-edit me-1"></i>Editar';
            button.classList.remove('btn-outline-danger');
            button.classList.add('btn-outline-primary');
        }
    }
}

// Manejar cambios en notificaciones
async function handleNotificationChange(event) {
    const checkbox = event.target;
    const setting = checkbox.closest('.notification-setting');
    const settingName = setting.querySelector('.fw-bold').textContent;

    try {
        const response = await fetch('/api/profile/notifications', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                setting: settingName,
                enabled: checkbox.checked
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showNotification(`  ${settingName} ${checkbox.checked ? 'activado' : 'desactivado'}`, 'success');
        } else {
            // Revertir cambio si hay error
            checkbox.checked = !checkbox.checked;
            throw new Error(result.error || 'Error actualizando configuraci n');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification(`  ${error.message}`, 'error');
    }
}

// Sistema de notificaciones
function showNotification(message, type = 'info') {
    // Remover notificaciones existentes
    const existingNotifications = document.querySelectorAll('.profile-notification');
    existingNotifications.forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = `profile-notification alert alert-${getBootstrapAlertClass(type)} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;

    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="flex-grow-1">${message}</div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    document.body.appendChild(notification);

    // Auto-remover despu s de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Convertir tipo de notificaci n a clase de Bootstrap
function getBootstrapAlertClass(type) {
    const mapping = {
        'success': 'success',
        'error': 'danger',
        'info': 'info',
        'warning': 'warning'
    };
    return mapping[type] || 'info';
}

// Funciones globales para compatibilidad con onclick
function editProfile() {
    togglePersonalEdit();
}

function shareProfile() {
    if (navigator.share) {
        navigator.share({
            title: 'Mi Perfil MedConnect',
            text: 'Revisa mi perfil m dico en MedConnect',
            url: window.location.href
        });
    } else {
        // Fallback: copiar URL al portapapeles
        navigator.clipboard.writeText(window.location.href).then(() => {
            showNotification('  Enlace del perfil copiado al portapapeles', 'success');
        });
    }
}

function editPersonalInfo() {
    togglePersonalEdit();
}

// ==========================================================================
// TELEGRAM LINKING FUNCTIONALITY
// ==========================================================================

// Generar c digo de vinculaci n de Telegram
async function generateTelegramCode() {
    try {
        const response = await fetch('/api/user/generate-telegram-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            // Mostrar c digo generado
            document.getElementById('linkingCode').textContent = data.code;
            document.getElementById('codeSection').style.display = 'block';

            showNotification(`C digo generado: ${data.code}. Expira en 15 minutos.`, 'success');

            // Auto-copiar al portapapeles
            await copyToClipboard(data.code);

        } else {
            showNotification('Error generando c digo: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexi n al generar c digo', 'error');
    }
}

// Copiar c digo al portapapeles
async function copyCode() {
    const code = document.getElementById('linkingCode').textContent;
    await copyToClipboard(code);
}

// Funci n auxiliar para copiar al portapapeles
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('C digo copiado al portapapeles', 'success');
    } catch (err) {
        // Fallback para navegadores que no soportan clipboard API
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('C digo copiado al portapapeles', 'success');
    }
}

// Desvincular cuenta de Telegram
async function unlinkTelegram() {
    if (!confirm(' Est s seguro de que quieres desvincular tu cuenta de Telegram?')) {
        return;
    }

    try {
        const response = await fetch('/api/user/unlink-telegram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            showNotification('Cuenta de Telegram desvinculada exitosamente', 'success');
            // Recargar la p gina para mostrar el estado actualizado
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showNotification('Error desvinculando cuenta: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error de conexi n al desvincular cuenta', 'error');
    }
} 