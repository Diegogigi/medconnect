document.addEventListener('DOMContentLoaded', function () {
    initializeReports();
});

// Inicializar la página de reportes
function initializeReports() {
    console.log('📊 Inicializando página de reportes...');

    // Cargar reporte por defecto (últimos 30 días, atenciones)
    setTimeout(() => {
        generarReportePersonalizado(30, 'atenciones');
    }, 1000);
}

// ===== FUNCIONES DE REPORTES =====

// Generar reporte por tipo predefinido
async function generarReporte(tipo) {
    const periodos = {
        'semanal': 7,
        'mensual': 30,
        'anual': 365
    };

    const periodo = periodos[tipo];
    await generarReportePersonalizado(periodo, 'atenciones');
}

// Generar reporte personalizado
async function generarReportePersonalizado(periodo = null, tipo = null) {
    const periodoSeleccionado = periodo || document.getElementById('periodoReporte').value;
    const tipoSeleccionado = tipo || document.getElementById('tipoReporte').value;

    try {
        // Mostrar loading
        mostrarLoadingReporte();

        const response = await fetch(`/api/professional/reports`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                periodo: parseInt(periodoSeleccionado),
                tipo: tipoSeleccionado
            })
        });

        if (response.ok) {
            const data = await response.json();
            mostrarReporte(data, tipoSeleccionado);
        } else {
            throw new Error('Error al generar el reporte');
        }
    } catch (error) {
        console.error('Error generando reporte:', error);
        mostrarErrorReporte('Error al generar reporte: ' + error.message);
    }
}

// Mostrar loading en el reporte
function mostrarLoadingReporte() {
    const contenido = document.getElementById('reporteContenido');
    const tabla = document.getElementById('tablaReporte');

    contenido.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="text-muted">Generando reporte...</p>
        </div>
    `;

    tabla.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-secondary mb-2" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="text-muted">Procesando datos...</p>
        </div>
    `;
}

// Mostrar error en el reporte
function mostrarErrorReporte(mensaje) {
    const contenido = document.getElementById('reporteContenido');
    const tabla = document.getElementById('tablaReporte');

    contenido.innerHTML = `
        <div class="text-center py-5">
            <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
            <p class="text-muted">${mensaje}</p>
            <button class="btn btn-primary" onclick="generarReportePersonalizado()">
                <i class="fas fa-redo me-1"></i>Reintentar
            </button>
        </div>
    `;

    tabla.innerHTML = `
        <div class="text-center py-4">
            <i class="fas fa-exclamation-circle fa-2x text-warning mb-2"></i>
            <p class="text-muted">No se pudieron cargar los datos</p>
        </div>
    `;
}

// Mostrar reporte con datos
function mostrarReporte(data, tipo) {
    mostrarEstadisticas(data.estadisticas, tipo);
    mostrarTablaDatos(data.datos, tipo);
}

// Mostrar estadísticas
function mostrarEstadisticas(estadisticas, tipo) {
    const contenido = document.getElementById('reporteContenido');

    let html = `
        <div class="row g-4">
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="card-body text-center p-4">
                        <div class="mb-3">
                            <i class="fas fa-chart-line fa-3x" style="color: #3498DB;"></i>
                        </div>
                        <h3 class="fw-bold mb-1" style="color: #2C3E50;">${estadisticas.total || 0}</h3>
                        <p class="text-muted mb-0 text-uppercase" style="font-size: 0.85rem; letter-spacing: 1px;">Total ${tipo}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="card-body text-center p-4">
                        <div class="mb-3">
                            <i class="fas fa-arrow-up fa-3x" style="color: #27AE60;"></i>
                        </div>
                        <h3 class="fw-bold mb-1" style="color: #2C3E50;">${estadisticas.promedio || 0}</h3>
                        <p class="text-muted mb-0 text-uppercase" style="font-size: 0.85rem; letter-spacing: 1px;">Promedio</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="card-body text-center p-4">
                        <div class="mb-3">
                            <i class="fas fa-calendar-check fa-3x" style="color: #F39C12;"></i>
                        </div>
                        <h3 class="fw-bold mb-1" style="color: #2C3E50;">${estadisticas.maximo || 0}</h3>
                        <p class="text-muted mb-0 text-uppercase" style="font-size: 0.85rem; letter-spacing: 1px;">Máximo</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card">
                    <div class="card-body text-center p-4">
                        <div class="mb-3">
                            <i class="fas fa-percentage fa-3x" style="color: #E74C3C;"></i>
                        </div>
                        <h3 class="fw-bold mb-1" style="color: #2C3E50;">${estadisticas.crecimiento || 0}%</h3>
                        <p class="text-muted mb-0 text-uppercase" style="font-size: 0.85rem; letter-spacing: 1px;">Crecimiento</p>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Agregar gráfico si hay datos de tendencia
    if (estadisticas.tendencia && estadisticas.tendencia.length > 0) {
        html += `
            <div class="mt-4">
                <h6 class="mb-3">Tendencia</h6>
                <div class="chart-container">
                    <canvas id="tendenciaChart"></canvas>
                </div>
            </div>
        `;
    }

    contenido.innerHTML = html;

    // Crear gráfico si hay datos
    if (estadisticas.tendencia && estadisticas.tendencia.length > 0) {
        crearGraficoTendencia(estadisticas.tendencia, tipo);
    }
}

// Crear gráfico de tendencia
function crearGraficoTendencia(datos, tipo) {
    const ctx = document.getElementById('tendenciaChart');
    if (!ctx) return;

    // Destruir gráfico existente si hay uno
    if (window.tendenciaChart) {
        window.tendenciaChart.destroy();
    }

    // Simular datos de tendencia (en producción vendrían del backend)
    const labels = datos.map((_, index) => `Día ${index + 1}`);
    const values = datos;

    window.tendenciaChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: tipo.charAt(0).toUpperCase() + tipo.slice(1),
                data: values,
                borderColor: '#3498DB',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.4,
                fill: true,
                borderWidth: 3,
                pointBackgroundColor: '#3498DB',
                pointBorderColor: '#2C3E50',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            weight: '600'
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0,0,0,0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            weight: '600'
                        }
                    }
                }
            }
        }
    });
}

// Mostrar tabla de datos
function mostrarTablaDatos(datos, tipo) {
    const tabla = document.getElementById('tablaReporte');

    if (!datos || datos.length === 0) {
        tabla.innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-inbox fa-2x text-muted mb-2"></i>
                <p class="text-muted">No hay datos disponibles para este período</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="table-responsive">
            <table class="table table-hover" style="border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <thead style="background: linear-gradient(135deg, #2C3E50, #34495E); color: white;">
                    <tr>
    `;

    // Crear encabezados según el tipo de reporte
    const headers = obtenerHeadersTabla(tipo);
    headers.forEach(header => {
        html += `<th style="padding: 16px 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.85rem;">${header}</th>`;
    });

    html += `
                    </tr>
                </thead>
                <tbody>
    `;

    // Agregar filas de datos
    datos.forEach((item, index) => {
        const rowClass = index % 2 === 0 ? 'style="background-color: rgba(255,255,255,0.8);"' : 'style="background-color: rgba(248,249,250,0.8);"';
        html += `<tr ${rowClass}>`;
        headers.forEach(header => {
            const key = obtenerClaveHeader(header, tipo);
            html += `<td style="padding: 14px 12px; font-weight: 500; border-bottom: 1px solid rgba(0,0,0,0.05);">${item[key] || '-'}</td>`;
        });
        html += `</tr>`;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    tabla.innerHTML = html;
}

// Obtener headers de tabla según tipo
function obtenerHeadersTabla(tipo) {
    const headers = {
        'atenciones': ['Fecha', 'Paciente', 'Tipo', 'Estado', 'Duración'],
        'pacientes': ['Nombre', 'Edad', 'Género', 'Última Consulta', 'Total Atenciones'],
        'ingresos': ['Fecha', 'Concepto', 'Monto', 'Estado', 'Método Pago'],
        'productividad': ['Fecha', 'Atenciones', 'Horas Trabajadas', 'Eficiencia', 'Calificación']
    };
    return headers[tipo] || ['Datos'];
}

// Obtener clave del header
function obtenerClaveHeader(header, tipo) {
    const mapeo = {
        'atenciones': {
            'Fecha': 'fecha',
            'Paciente': 'paciente',
            'Tipo': 'tipo',
            'Estado': 'estado',
            'Duración': 'duracion'
        },
        'pacientes': {
            'Nombre': 'nombre',
            'Edad': 'edad',
            'Género': 'genero',
            'Última Consulta': 'ultima_consulta',
            'Total Atenciones': 'total_atenciones'
        },
        'ingresos': {
            'Fecha': 'fecha',
            'Concepto': 'concepto',
            'Monto': 'monto',
            'Estado': 'estado',
            'Método Pago': 'metodo_pago'
        },
        'productividad': {
            'Fecha': 'fecha',
            'Atenciones': 'atenciones',
            'Horas Trabajadas': 'horas_trabajadas',
            'Eficiencia': 'eficiencia',
            'Calificación': 'calificacion'
        }
    };
    return mapeo[tipo]?.[header] || header.toLowerCase();
}

// Exportar reporte
async function exportarReporte(formato) {
    const periodo = document.getElementById('periodoReporte').value;
    const tipo = document.getElementById('tipoReporte').value;

    try {
        const response = await fetch(`/api/professional/reports/export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                periodo: parseInt(periodo),
                tipo: tipo,
                formato: formato
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reporte_${tipo}_${new Date().toISOString().split('T')[0]}.${formato}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            mostrarNotificacion(`Reporte exportado como ${formato.toUpperCase()}`, 'success');
        } else {
            throw new Error('Error al exportar el reporte');
        }
    } catch (error) {
        console.error('Error exportando reporte:', error);
        mostrarNotificacion('Error al exportar reporte: ' + error.message, 'error');
    }
}

// Mostrar notificación
function mostrarNotificacion(mensaje, tipo = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${tipo === 'error' ? 'danger' : tipo === 'success' ? 'success' : 'info'} border-0 position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${mensaje}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    document.body.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
} 