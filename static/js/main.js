/**
 * MedConnect - JavaScript Principal
 * Funcionalidades generales de la aplicación
 */

// Configuración global
const MedConnect = {
    config: {
        apiBaseUrl: '/api',
        version: '1.0.0',
        debug: true
    },

    // Inicialización
    init: function () {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupAjaxDefaults();
        this.log('MedConnect inicializado correctamente');
    },

    // Logging
    log: function (message, data = null) {
        if (this.config.debug) {
            console.log(`[MedConnect] ${message}`, data || '');
        }
    },

    // Configurar event listeners globales
    setupEventListeners: function () {
        // Confirmar acciones destructivas
        document.addEventListener('click', function (e) {
            if (e.target.matches('[data-confirm]')) {
                const message = e.target.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                }
            }
        });

        // Auto-hide alerts
        document.addEventListener('DOMContentLoaded', function () {
            const alerts = document.querySelectorAll('.alert[data-auto-hide]');
            alerts.forEach(alert => {
                const delay = parseInt(alert.getAttribute('data-auto-hide')) || 5000;
                setTimeout(() => {
                    alert.style.transition = 'opacity 0.5s ease';
                    alert.style.opacity = '0';
                    setTimeout(() => alert.remove(), 500);
                }, delay);
            });
        });

        // Form validation
        document.addEventListener('submit', function (e) {
            const form = e.target;
            if (form.hasAttribute('data-validate')) {
                if (!MedConnect.validateForm(form)) {
                    e.preventDefault();
                }
            }
        });
    },

    // Inicializar componentes
    initializeComponents: function () {
        this.initializeTooltips();
        this.initializeModals();
        this.initializeDataTables();
        this.initializeCharts();
    },

    // Configurar AJAX por defecto
    setupAjaxDefaults: function () {
        // Configurar headers por defecto para AJAX
        if (typeof $ !== 'undefined') {
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (settings.type === 'POST' || settings.type === 'PUT' || settings.type === 'DELETE') {
                        xhr.setRequestHeader('X-CSRFToken', MedConnect.getCSRFToken());
                    }
                }
            });
        }
    },

    // Obtener token CSRF
    getCSRFToken: function () {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    },

    // Validar formulario
    validateForm: function (form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'Este campo es requerido');
                isValid = false;
            } else {
                this.clearFieldError(field);
            }
        });

        // Validar emails
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !this.isValidEmail(field.value)) {
                this.showFieldError(field, 'Ingrese un email válido');
                isValid = false;
            }
        });

        return isValid;
    },

    // Mostrar error en campo
    showFieldError: function (field, message) {
        this.clearFieldError(field);
        field.classList.add('is-invalid');

        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    },

    // Limpiar error de campo
    clearFieldError: function (field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    },

    // Validar email
    isValidEmail: function (email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    // Inicializar tooltips
    initializeTooltips: function () {
        if (typeof bootstrap !== 'undefined') {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    },

    // Inicializar modales
    initializeModals: function () {
        if (typeof bootstrap !== 'undefined') {
            const modalTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="modal"]'));
            modalTriggerList.map(function (modalTriggerEl) {
                return new bootstrap.Modal(modalTriggerEl);
            });
        }
    },

    // Inicializar tablas de datos
    initializeDataTables: function () {
        // Si DataTables está disponible, inicializar tablas
        if (typeof $.fn.DataTable !== 'undefined') {
            $('.data-table').DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/es-ES.json'
                },
                responsive: true,
                pageLength: 25,
                order: [[0, 'desc']]
            });
        }
    },

    // Inicializar gráficos
    initializeCharts: function () {
        // Si Chart.js está disponible, inicializar gráficos
        if (typeof Chart !== 'undefined') {
            this.initializeDashboardCharts();
        }
    },

    // Inicializar gráficos del dashboard
    initializeDashboardCharts: function () {
        // Gráfico de pacientes por mes
        const patientsChart = document.getElementById('patientsChart');
        if (patientsChart) {
            new Chart(patientsChart, {
                type: 'line',
                data: {
                    labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Pacientes',
                        data: [12, 19, 3, 5, 2, 3],
                        borderColor: 'rgb(102, 126, 234)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    }
                }
            });
        }

        // Gráfico de consultas por tipo
        const consultationsChart = document.getElementById('consultationsChart');
        if (consultationsChart) {
            new Chart(consultationsChart, {
                type: 'doughnut',
                data: {
                    labels: ['Kinesiología', 'Traumatología', 'Fisioterapia'],
                    datasets: [{
                        data: [45, 30, 25],
                        backgroundColor: [
                            'rgb(102, 126, 234)',
                            'rgb(118, 75, 162)',
                            'rgb(255, 193, 7)'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        }
                    }
                }
            });
        }
    },

    // Utilidades AJAX
    ajax: {
        get: function (url, callback) {
            this.request('GET', url, null, callback);
        },

        post: function (url, data, callback) {
            this.request('POST', url, data, callback);
        },

        put: function (url, data, callback) {
            this.request('PUT', url, data, callback);
        },

        delete: function (url, callback) {
            this.request('DELETE', url, null, callback);
        },

        request: function (method, url, data, callback) {
            const xhr = new XMLHttpRequest();
            xhr.open(method, url, true);
            xhr.setRequestHeader('Content-Type', 'application/json');

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4) {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            callback(null, response);
                        } catch (e) {
                            callback(e, null);
                        }
                    } else {
                        callback(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`), null);
                    }
                }
            };

            xhr.send(data ? JSON.stringify(data) : null);
        }
    },

    // Utilidades de UI
    ui: {
        showLoading: function (element) {
            if (element) {
                element.innerHTML = '<div class="spinner"></div>';
            }
        },

        hideLoading: function (element, originalContent) {
            if (element && originalContent) {
                element.innerHTML = originalContent;
            }
        },

        showAlert: function (message, type = 'info', container = null) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.setAttribute('data-auto-hide', '5000');
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            const targetContainer = container || document.querySelector('.container') || document.body;
            targetContainer.insertBefore(alertDiv, targetContainer.firstChild);
        },

        confirm: function (message, callback) {
            if (confirm(message)) {
                callback();
            }
        },

        formatDate: function (date) {
            return new Date(date).toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        },

        formatTime: function (time) {
            return new Date(`2000-01-01T${time}`).toLocaleTimeString('es-ES', {
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    },

    // Utilidades de datos
    data: {
        // Obtener pacientes
        getPatients: function (callback) {
            MedConnect.ajax.get('/api/patients', callback);
        },

        // Obtener consultas
        getConsultations: function (callback) {
            MedConnect.ajax.get('/api/consultations', callback);
        },

        // Obtener agenda
        getSchedule: function (callback) {
            MedConnect.ajax.get('/api/schedule', callback);
        },

        // Obtener estadísticas del dashboard
        getDashboardStats: function (callback) {
            MedConnect.ajax.get('/api/dashboard/stats', callback);
        }
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    MedConnect.init();
});

// Exportar para uso global
window.MedConnect = MedConnect;
