// Archivo de prueba con líneas problemáticas
// Líneas con template literals y comillas:
// Línea 475: showNotification(`El archivo ${file.name} excede el tamaño máximo permitido de 10MB`, 'error');
// Línea 481: showNotification(`Tipo de archivo no permitido: ${file.name}. Solo se permiten PDF e imágenes.`, 'error');
// Línea 897: showNotification(`Error: ${data.message}`, 'error');
// Línea 1110: showNotification(`Iniciando descarga de ${nombreArchivo}`, 'success');
// Línea 1128: const input = form.querySelector(`[name="${key}"]`);
// Línea 1173: const input = form.querySelector(`[name="${key}"]`);
// Línea 1258: csv += fila.map(celda => `"${celda}"`).join(',') + '\n';
// Línea 1386: showNotification(`Error en prueba: ${data.message}`, 'error');
// Línea 1391: showNotification(`Error en la prueba de registro: ${error.message}`, 'error');
// Línea 1556: showNotification(`Error al cargar pacientes: ${data.message}`, 'error');

// Líneas con onclick problemáticas:
// Línea 2226: `<button class="btn btn-sm btn-outline-primary me-1" onclick="previewArchivo('${archivo.archivo_id}', '${archivo.nombre_archivo.replace(/'/g, "\\'")}')">
