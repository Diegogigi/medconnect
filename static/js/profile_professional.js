document.addEventListener('DOMContentLoaded', function () {
    initializeTooltips();
    setupImageUpload();
    setupReportesNavigation();
});

// Configurar navegaci n a la secci n de reportes
function setupReportesNavigation() {
    // Verificar si hay un hash en la URL que apunte a reportes
    if (window.location.hash === '#reportes') {
        // Hacer scroll suave a la secci n de reportes
        setTimeout(() => {
            const reportesSection = document.getElementById('reportes');
            if (reportesSection) {
                reportesSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }, 500); // Peque o delay para asegurar que el DOM est  listo
    }
}

// Inicializar tooltips de Bootstrap
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Configurar carga de imagen de perfil
function setupImageUpload() {
    const avatarContainer = document.querySelector('.professional-avatar');
    if (avatarContainer) {
        avatarContainer.addEventListener('click', function () {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = function (event) {
                const file = event.target.files[0];
                if (file) {
                    uploadProfileImage(file);
                }
            };
            input.click();
        });
    }
}

// Funci n para subir imagen de perfil
async function uploadProfileImage(file) {
    const formData = new FormData();
    formData.append('profile_image', file);

    try {
        const response = await fetch('/api/upload-profile-image', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            updateProfileImage(data.image_url);
            showNotification('Imagen de perfil actualizada correctamente', 'success');
        } else {
            throw new Error('Error al subir la imagen');
        }
    } catch (error) {
        showNotification('Error al subir la imagen: ' + error.message, 'error');
    }
}

// Funci n para editar el perfil
function editarPerfil() {
    // Crear modal de edici n
    const modal = new bootstrap.Modal(document.getElementById('editProfileModal') || createEditProfileModal());

    // Cargar datos actuales en el formulario
    const form = document.getElementById('editProfileForm');
    if (form) {
        // Obtener datos del perfil actual
        const especialidad = document.querySelector('[data-field="especialidad"]')?.textContent || '';
        const numeroRegistro = document.querySelector('[data-field="numero_registro"]')?.textContent || '';
        const email = document.querySelector('[data-field="email"]')?.textContent || '';
        const telefono = document.querySelector('[data-field="telefono"]')?.textContent || '';
        const direccionConsulta = document.querySelector('[data-field="direccion_consulta"]')?.textContent || '';
        const horarioAtencion = document.querySelector('[data-field="horario_atencion"]')?.textContent || '';
        const anosExperiencia = document.querySelector('[data-field="anos_experiencia"]')?.textContent || '0';
        const idiomas = Array.from(document.querySelectorAll('.idioma-badge')).map(badge => badge.textContent).join(', ');
        const areasEspecializacion = Array.from(document.querySelectorAll('.area-especializacion')).map(area => area.textContent).join('\n');

        // Establecer valores en el formulario
        form.especialidad.value = especialidad.trim();
        form.numero_registro.value = numeroRegistro.trim();
        form.email.value = email.trim();
        form.telefono.value = telefono.trim();
        form.direccion_consulta.value = direccionConsulta.trim();
        form.horario_atencion.value = horarioAtencion.trim();
        form.anos_experiencia.value = anosExperiencia.trim();
        form.idiomas.value = idiomas.trim();
        form.areas_especializacion.value = areasEspecializacion.trim();
    }

    modal.show();
}

// Funci n para agregar certificaci n
function agregarCertificacion() {
    const modal = new bootstrap.Modal(document.getElementById('certificationModal') || createCertificationModal());
    modal.show();
}

// Crear modal de edici n de perfil
function createEditProfileModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'editProfileModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Editar Perfil Profesional</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="editProfileForm">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">Especialidad</label>
                                <input type="text" class="form-control" name="especialidad" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">N mero de Registro</label>
                                <input type="text" class="form-control" name="numero_registro" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Email Profesional</label>
                                <input type="email" class="form-control" name="email" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Tel fono</label>
                                <input type="tel" class="form-control" name="telefono">
                            </div>
                            <div class="col-12">
                                <label class="form-label">Direcci n de Consulta</label>
                                <input type="text" class="form-control" name="direccion_consulta">
                            </div>
                            <div class="col-12">
                                <label class="form-label">Horario de Atenci n</label>
                                <input type="text" class="form-control" name="horario_atencion">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">A os de Experiencia</label>
                                <input type="number" class="form-control" name="anos_experiencia">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Idiomas</label>
                                <input type="text" class="form-control" name="idiomas" placeholder="Separados por coma">
                            </div>
                            <div class="col-12">
                                <label class="form-label"> reas de Especializaci n</label>
                                <textarea class="form-control" name="areas_especializacion" rows="3"></textarea>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="guardarPerfil()">Guardar Cambios</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

// Crear modal de certificaci n
function createCertificationModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'certificationModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Agregar Certificaci n</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="certificationForm">
                        <div class="mb-3">
                            <label class="form-label">T tulo</label>
                            <input type="text" class="form-control" name="titulo" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Instituci n</label>
                            <input type="text" class="form-control" name="institucion" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">A o</label>
                            <input type="number" class="form-control" name="ano" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Archivo (PDF)</label>
                            <input type="file" class="form-control" name="certificado" accept=".pdf">
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="guardarCertificacion()">Guardar</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

// Funci n para guardar cambios del perfil
async function guardarPerfil() {
    const form = document.getElementById('editProfileForm');
    if (!form) return;

    // Validar campos requeridos
    const requiredFields = ['especialidad', 'numero_registro', 'email'];
    for (const field of requiredFields) {
        if (!form[field].value.trim()) {
            showNotification(`El campo ${field} es requerido`, 'error');
            return;
        }
    }

    const formData = new FormData(form);

    try {
        const response = await fetch('/api/update-professional-profile', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(data.message || 'Perfil actualizado correctamente', 'success');
            // Cerrar el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
            if (modal) modal.hide();
            // Recargar la p gina despu s de un breve retraso
            setTimeout(() => location.reload(), 1000);
        } else {
            throw new Error(data.error || 'Error al actualizar el perfil');
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Funci n para guardar certificaci n
async function guardarCertificacion() {
    const form = document.getElementById('certificationForm');
    const formData = new FormData(form);

    try {
        const response = await fetch('/api/add-certification', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(data.message || 'Certificaci n agregada correctamente', 'success');

            // Cerrar el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('certificationModal'));
            if (modal) modal.hide();

            // Recargar la p gina despu s de un breve retraso
            setTimeout(() => location.reload(), 1000);
        } else {
            throw new Error(data.error || 'Error al agregar la certificaci n');
        }
    } catch (error) {
        showNotification('Error al agregar la certificaci n: ' + error.message, 'error');
    }
}

// Funci n para actualizar la imagen de perfil en la UI
function updateProfileImage(imageUrl) {
    const avatar = document.querySelector('.professional-avatar');
    if (avatar) {
        avatar.innerHTML = `<img src="${imageUrl}" alt="Foto de perfil" class="rounded-circle">`;
    }
}

// Funci n para mostrar notificaciones
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0 position-fixed top-0 end-0 m-3`;
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
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

// Funci n para editar una secci n espec fica
function editarSeccion(seccion) {
    const modalId = `edit${seccion.charAt(0).toUpperCase() + seccion.slice(1)}Modal`;
    const modal = new bootstrap.Modal(document.getElementById(modalId) || createSectionModal(seccion));

    // Cargar datos actuales
    const form = document.getElementById(`edit${seccion}Form`);
    if (form) {
        const fields = form.querySelectorAll('[name]');
        fields.forEach(field => {
            const dataField = document.querySelector(`[data-field="${field.name}"]`);
            if (dataField) {
                field.value = dataField.textContent.trim();
            }
        });
    }

    modal.show();
}

// Funci n para agregar  rea de especializaci n
function agregarArea() {
    const modal = new bootstrap.Modal(document.getElementById('areaModal') || createAreaModal());
    modal.show();
}

// Crear modal para editar secci n
function createSectionModal(seccion) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = `edit${seccion.charAt(0).toUpperCase() + seccion.slice(1)}Modal`;

    let fields = '';
    if (seccion === 'profesional') {
        fields = `
            <div class="mb-3">
                <label class="form-label">N mero de Registro</label>
                <input type="text" class="form-control" name="numero_registro" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Especialidad</label>
                <input type="text" class="form-control" name="especialidad" required>
            </div>
            <div class="mb-3">
                <label class="form-label">A os de Experiencia</label>
                <input type="number" class="form-control" name="anos_experiencia" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Idiomas</label>
                <input type="text" class="form-control" name="idiomas" placeholder="Separados por coma">
            </div>
        `;
    } else if (seccion === 'contacto') {
        fields = `
            <div class="mb-3">
                <label class="form-label">Email Profesional</label>
                <input type="email" class="form-control" name="email" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Tel fono</label>
                <input type="tel" class="form-control" name="telefono" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Direcci n de Consulta</label>
                <input type="text" class="form-control" name="direccion_consulta" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Horario de Atenci n</label>
                <input type="text" class="form-control" name="horario_atencion" required>
            </div>
        `;
    }

    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Editar ${seccion.charAt(0).toUpperCase() + seccion.slice(1)}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="edit${seccion}Form">
                        ${fields}
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="guardarSeccion('${seccion}')">Guardar</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

// Crear modal para  rea de especializaci n
function createAreaModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'areaModal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Agregar  rea de Especializaci n</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="areaForm">
                        <div class="mb-3">
                            <label class="form-label">Nombre del  rea</label>
                            <input type="text" class="form-control" name="nombre" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Descripci n</label>
                            <textarea class="form-control" name="descripcion" rows="3"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" onclick="guardarArea()">Guardar</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

// Funci n para guardar una secci n
async function guardarSeccion(seccion) {
    const form = document.getElementById(`edit${seccion}Form`);
    if (!form) return;

    const formData = new FormData(form);

    try {
        const response = await fetch('/api/update-professional-profile', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(data.message || 'Datos actualizados correctamente', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById(`edit${seccion.charAt(0).toUpperCase() + seccion.slice(1)}Modal`));
            if (modal) modal.hide();
            setTimeout(() => location.reload(), 1000);
        } else {
            throw new Error(data.error || 'Error al actualizar los datos');
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Funci n para guardar  rea de especializaci n
async function guardarArea() {
    const form = document.getElementById('areaForm');
    if (!form) return;

    const formData = new FormData(form);

    try {
        const response = await fetch('/api/add-specialization-area', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showNotification(data.message || ' rea agregada correctamente', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('areaModal'));
            if (modal) modal.hide();
            setTimeout(() => location.reload(), 1000);
        } else {
            throw new Error(data.error || 'Error al agregar el  rea');
        }
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

