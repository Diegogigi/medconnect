// Funcionalidad de cambio de contraseñas
function showPasswordChangeModal() {
    const modal = document.getElementById('passwordChangeModal');
    if (modal) {
        modal.style.display = 'block';
    } else {
        // Crear modal dinámicamente si no existe
        createPasswordChangeModal();
    }
}

function createPasswordChangeModal() {
    const modalHtml = `
        <div id="passwordChangeModal" class="modal" style="display: block;">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>🔒 Cambiar Contraseña</h3>
                    <span class="close" onclick="closePasswordChangeModal()">&times;</span>
                </div>
                <div class="modal-body">
                    <form id="passwordChangeForm">
                        <div class="form-group">
                            <label for="currentPassword">Contraseña Actual:</label>
                            <input type="password" id="currentPassword" name="current_password" required 
                                   placeholder="Ingrese su contraseña actual">
                        </div>
                        <div class="form-group">
                            <label for="newPassword">Nueva Contraseña:</label>
                            <input type="password" id="newPassword" name="new_password" required 
                                   placeholder="Al menos 6 caracteres" minlength="6">
                        </div>
                        <div class="form-group">
                            <label for="confirmPassword">Confirmar Nueva Contraseña:</label>
                            <input type="password" id="confirmPassword" name="confirm_password" required 
                                   placeholder="Repita la nueva contraseña">
                        </div>
                        <div class="form-actions">
                            <button type="button" onclick="closePasswordChangeModal()" class="btn-secondary">
                                Cancelar
                            </button>
                            <button type="submit" class="btn-primary">
                                🔒 Cambiar Contraseña
                            </button>
                        </div>
                    </form>
                    <div id="passwordChangeMessage"></div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Agregar event listener al formulario
    document.getElementById('passwordChangeForm').addEventListener('submit', handlePasswordChange);
}

function closePasswordChangeModal() {
    const modal = document.getElementById('passwordChangeModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function handlePasswordChange(e) {
    e.preventDefault();

    const messageDiv = document.getElementById('passwordChangeMessage');
    const formData = new FormData(e.target);

    const data = {
        current_password: formData.get('current_password'),
        new_password: formData.get('new_password'),
        confirm_password: formData.get('confirm_password')
    };

    // Validaciones cliente
    if (data.new_password !== data.confirm_password) {
        messageDiv.innerHTML = '<div class="alert alert-error">Las contraseñas no coinciden</div>';
        return;
    }

    if (data.new_password.length < 6) {
        messageDiv.innerHTML = '<div class="alert alert-error">La contraseña debe tener al menos 6 caracteres</div>';
        return;
    }

    try {
        messageDiv.innerHTML = '<div class="alert alert-info">🔄 Cambiando contraseña...</div>';

        const response = await fetch('/api/profile/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            messageDiv.innerHTML = `<div class="alert alert-success">✅ ${result.message}</div>`;

            // Limpiar formulario
            document.getElementById('passwordChangeForm').reset();

            // Cerrar modal después de 2 segundos
            setTimeout(() => {
                closePasswordChangeModal();
            }, 2000);

        } else {
            messageDiv.innerHTML = `<div class="alert alert-error">❌ ${result.error}</div>`;
        }

    } catch (error) {
        messageDiv.innerHTML = '<div class="alert alert-error">❌ Error de conexión</div>';
        console.error('Error:', error);
    }
}

// CSS para el modal - Se inyecta automáticamente
const passwordModalCSS = `
#passwordChangeModal {
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
}

#passwordChangeModal .modal-content {
    background-color: #fefefe;
    margin: 5% auto;
    padding: 0;
    border: none;
    border-radius: 10px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

#passwordChangeModal .modal-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px 10px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

#passwordChangeModal .modal-body {
    padding: 20px;
}

#passwordChangeModal .form-group {
    margin-bottom: 15px;
}

#passwordChangeModal .form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
    color: #333;
}

#passwordChangeModal .form-group input {
    width: 100%;
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-size: 14px;
    transition: border-color 0.3s;
    box-sizing: border-box;
}

#passwordChangeModal .form-group input:focus {
    border-color: #667eea;
    outline: none;
}

#passwordChangeModal .form-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 20px;
}

#passwordChangeModal .btn-primary,
#passwordChangeModal .btn-secondary {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 600;
    transition: background-color 0.3s;
}

#passwordChangeModal .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

#passwordChangeModal .btn-secondary {
    background-color: #6c757d;
    color: white;
}

#passwordChangeModal .btn-primary:hover {
    opacity: 0.9;
}

#passwordChangeModal .btn-secondary:hover {
    background-color: #5a6268;
}

#passwordChangeModal .close {
    font-size: 24px;
    font-weight: bold;
    cursor: pointer;
    color: white;
}

#passwordChangeModal .close:hover {
    opacity: 0.7;
}

#passwordChangeModal .alert {
    padding: 10px;
    border-radius: 5px;
    margin-top: 15px;
}

#passwordChangeModal .alert-success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

#passwordChangeModal .alert-error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

#passwordChangeModal .alert-info {
    background-color: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
}
`;

// Inyectar CSS automáticamente cuando se carga el script
if (!document.getElementById('passwordModalStyles')) {
    const style = document.createElement('style');
    style.id = 'passwordModalStyles';
    style.textContent = passwordModalCSS;
    document.head.appendChild(style);
} 