/**
 * Script para restaurar el chat en la sidebar
 * Asegura que el chat esté presente y funcional
 */

console.log('💬 Restaurando chat en la sidebar...');

// Función para crear el chat en la sidebar
function crearChatEnSidebar() {
    console.log('🔧 Creando chat en la sidebar...');

    const sidebarContainer = document.getElementById('sidebarContainer');
    if (!sidebarContainer) {
        console.error('❌ sidebarContainer no encontrado');
        return;
    }

    const panelContent = sidebarContainer.querySelector('.panel-content');
    if (!panelContent) {
        console.error('❌ panel-content no encontrado');
        return;
    }

    // Verificar si ya existe el chat
    const existingChat = panelContent.querySelector('.copilot-chat-elegant');
    if (existingChat) {
        console.log('✅ Chat ya existe en la sidebar');
        return;
    }

    // Crear el chat
    const chatHtml = `
        <div class="copilot-chat-elegant">
            <div class="chat-header">
                <h6 class="chat-title">
                    <i class="fas fa-comments me-2"></i>
                    Chat IA
                </h6>
            </div>
            <div class="chat-messages" id="chatMessages">
                <div class="message system">
                    <div class="message-content">
                        <div class="message-text">
                            <p>¡Hola! Soy tu asistente de IA. ¿En qué puedo ayudarte?</p>
                        </div>
                        <div class="message-time">Ahora</div>
                    </div>
                </div>
            </div>
            <div class="chat-input">
                <div class="input-group">
                    <input type="text" 
                           id="chatInput" 
                           class="form-control" 
                           placeholder="Escribe tu mensaje aquí..."
                           onkeydown="if(event.key==='Enter'){ enviarMensajeChat(this.value); this.value='';}">
                    <button class="btn btn-primary" 
                            onclick="enviarMensajeChat(document.getElementById('chatInput').value)">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    `;

    // Insertar el chat en la sidebar
    panelContent.insertAdjacentHTML('beforeend', chatHtml);

    console.log('✅ Chat creado en la sidebar');
}

// Función para enviar mensaje desde el chat
function enviarMensajeChat(mensaje) {
    if (!mensaje.trim()) return;

    console.log('💬 Enviando mensaje desde chat:', mensaje);

    // Agregar mensaje del usuario
    agregarMensajeChat(mensaje, 'user');

    // Procesar el mensaje
    procesarMensajeChat(mensaje);
}

// Función para agregar mensaje al chat
function agregarMensajeChat(mensaje, tipo = 'user') {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageHtml = `
        <div class="message ${tipo}">
            <div class="message-content">
                <div class="message-text">
                    <p>${mensaje}</p>
                </div>
                <div class="message-time">Ahora</div>
            </div>
        </div>
    `;

    chatMessages.insertAdjacentHTML('beforeend', messageHtml);

    // Scroll al final
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Función para procesar mensaje del chat
async function procesarMensajeChat(mensaje) {
    console.log('🔍 Procesando mensaje:', mensaje);

    try {
        // Verificar si es un comando de búsqueda
        if (mensaje.toLowerCase().includes('busca') ||
            mensaje.toLowerCase().includes('papers') ||
            mensaje.toLowerCase().includes('evidencia') ||
            mensaje.toLowerCase().includes('estudios')) {

            console.log('🔍 Comando de búsqueda detectado, procesando con DeepSeek...');

            // Extraer tema de búsqueda
            const searchTopic = extraerTemaBusqueda(mensaje);
            console.log('🔍 Tema de búsqueda extraído:', searchTopic);

            // Mostrar mensaje de procesamiento
            agregarMensajeChat(`🔍 Buscando papers científicos sobre: "${searchTopic}"...`, 'info');

            // Realizar búsqueda científica con DeepSeek
            await realizarBusquedaCientifica(searchTopic);

        } else {
            // Procesar con DeepSeek para respuestas generales
            await procesarConDeepSeek(mensaje);
        }

    } catch (error) {
        console.error('❌ Error procesando mensaje:', error);
        agregarMensajeChat('Lo siento, hubo un error procesando tu mensaje. Inténtalo de nuevo.', 'error');
    }
}

// Función para extraer tema de búsqueda
function extraerTemaBusqueda(mensaje) {
    const patterns = [
        /busca papers de (.+)/i,
        /buscar papers de (.+)/i,
        /papers sobre (.+)/i,
        /evidencia científica de (.+)/i,
        /estudios sobre (.+)/i,
        /busca papers (.+)/i,
        /buscar papers (.+)/i,
        /busca (.+)/i,
        /buscar (.+)/i
    ];

    for (const pattern of patterns) {
        const match = mensaje.match(pattern);
        if (match && match[1]) {
            return match[1].trim();
        }
    }

    // Si no hay patrón específico, usar todo el mensaje
    return mensaje.replace(/busca papers|buscar papers|papers sobre|evidencia científica|estudios sobre|busca|buscar/gi, '').trim();
}

// Función para realizar búsqueda científica
async function realizarBusquedaCientifica(tema) {
    try {
        // Obtener contexto del formulario
        const contexto = obtenerContextoFormulario();

        // Realizar búsqueda científica
        const response = await fetch('/api/copilot/analyze-enhanced', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                consulta: tema,
                contexto_clinico: contexto
            })
        });

        if (!response.ok) {
            throw new Error('Error en búsqueda científica');
        }

        const data = await response.json();

        if (data.success && data.evidence && data.evidence.length > 0) {
            // Mostrar resultados de búsqueda
            mostrarResultadosBusqueda(data.evidence, tema);

            // Mostrar resumen inteligente si está disponible
            if (data.clinical_analysis && data.clinical_analysis.resumen_inteligente) {
                mostrarResumenInteligente(data.clinical_analysis, tema);
            }
        } else {
            agregarMensajeChat(`❌ No se encontraron papers científicos sobre "${tema}". Intenta con términos más específicos.`, 'warning');
        }

    } catch (error) {
        console.error('❌ Error en búsqueda científica:', error);
        agregarMensajeChat('❌ Error al buscar papers científicos. Inténtalo de nuevo.', 'error');
    }
}

// Función para mostrar resultados de búsqueda
function mostrarResultadosBusqueda(evidence, tema) {
    let mensaje = `📚 **Papers encontrados sobre "${tema}":**\n\n`;

    // Mostrar información MeSH si está disponible
    if (evidence.length > 0 && evidence[0].mesh_terms && evidence[0].mesh_terms.length > 0) {
        mensaje += `🔬 **Término MeSH normalizado:** ${evidence[0].mesh_terms[0]}\n`;
        if (evidence[0].clinical_context && evidence[0].clinical_context.specialty) {
            mensaje += `🏥 **Especialidad:** ${evidence[0].clinical_context.specialty}\n`;
        }
        mensaje += '\n';
    }

    evidence.slice(0, 5).forEach((paper, index) => {
        // Formatear autores
        const autores = paper.autores || [];
        let autoresFormateados = '';
        if (autores.length > 0) {
            if (autores.length <= 3) {
                autoresFormateados = autores.join(', ');
            } else {
                autoresFormateados = `${autores.slice(0, 3).join(', ')}, et al.`;
            }
        }

        // Formatear revista
        const revista = paper.journal || paper.revista || 'Revista no especificada';
        const año = paper.año_publicacion || paper.year || 'N/A';
        const doi = paper.doi || '';
        const relevancia = Math.round((paper.relevancia_score || paper.relevancia || 0) * 100);

        mensaje += `**${index + 1}. ${paper.titulo || paper.title || 'Sin título'}**\n`;
        if (autoresFormateados) {
            mensaje += `📝 **Autores:** ${autoresFormateados}.\n`;
        }
        mensaje += `📚 **Revista:** ${revista}. ${año !== 'N/A' ? año : ''}\n`;
        if (doi && doi !== "Sin DOI") {
            mensaje += `🔗 **DOI:** ${doi}\n`;
        }
        mensaje += `📊 **Relevancia:** ${relevancia}%\n`;
        if (paper.resumen || paper.abstract) {
            mensaje += `📖 **Resumen:** ${(paper.resumen || paper.abstract).substring(0, 150)}...\n`;
        }
        mensaje += '\n';
    });

    mensaje += `✅ Se encontraron ${evidence.length} papers científicos relevantes sobre "${tema}".`;

    agregarMensajeChat(mensaje, 'system');
}

// Función para mostrar resumen inteligente
function mostrarResumenInteligente(clinicalAnalysis, tema) {
    let mensaje = `🧠 **Informe Clínico Basado en Evidencia: "${tema}"**\n\n`;

    // Mostrar resumen inteligente con formato estructurado
    if (clinicalAnalysis.resumen_inteligente) {
        // Procesar el resumen estructurado
        const resumenEstructurado = procesarResumenEstructurado(clinicalAnalysis.resumen_inteligente);
        mensaje += resumenEstructurado;
    }

    // Mostrar estadísticas de calidad
    mensaje += `\n📊 **Calidad de la Evidencia:**\n`;
    if (clinicalAnalysis.oraciones_con_evidencia > 0) {
        mensaje += `✅ **${clinicalAnalysis.oraciones_con_evidencia} afirmaciones** respaldadas por evidencia científica\n`;
    }

    if (clinicalAnalysis.claims_no_concluyentes > 0) {
        mensaje += `⚠️ **${clinicalAnalysis.claims_no_concluyentes} afirmaciones** requieren más evidencia\n`;
    }

    // Agregar información sobre la metodología
    mensaje += `\n---\n`;
    mensaje += `🔬 **Metodología:** Este informe fue generado procesando el contenido de los papers científicos encontrados, utilizando inteligencia artificial para extraer y sintetizar la evidencia más relevante siguiendo estándares médicos profesionales.`;

    agregarMensajeChat(mensaje, 'ai');
}

// Función para procesar el resumen estructurado
function procesarResumenEstructurado(resumen) {
    if (!resumen) return '';

    // Remover texto técnico interno
    let resumenLimpio = resumen
        .replace(/Resumen basado en evidencia:/gi, '')
        .replace(/Nota:.*?originalidad.*?citados\./gs, '')
        .replace(/CHUNK\d+/g, '')
        .trim();

    // Extraer secciones del formato Markdown
    const secciones = extraerSeccionesMarkdown(resumenLimpio);

    let resultado = '';

    // Procesar cada sección
    if (secciones.introduccion) {
        resultado += `## 📋 **Introducción**\n${secciones.introduccion}\n\n`;
    }

    if (secciones.evaluacion) {
        resultado += `## 🔍 **Evaluación / Examen**\n${secciones.evaluacion}\n\n`;
    }

    if (secciones.diagnostico) {
        resultado += `## 🏥 **Diagnóstico**\n${secciones.diagnostico}\n\n`;
    }

    if (secciones.tratamiento) {
        resultado += `## 💊 **Tratamiento / Terapia**\n${secciones.tratamiento}\n\n`;
    }

    if (secciones.cierre) {
        resultado += `## ✅ **Cierre**\n${secciones.cierre}\n\n`;
    }

    if (secciones.referencias) {
        resultado += `## 📚 **Referencias**\n${secciones.referencias}\n\n`;
    }

    return resultado;
}

// Función para extraer secciones del formato Markdown
function extraerSeccionesMarkdown(texto) {
    const secciones = {
        introduccion: '',
        evaluacion: '',
        diagnostico: '',
        tratamiento: '',
        cierre: '',
        referencias: ''
    };

    // Patrones para cada sección
    const patrones = {
        introduccion: /##\s*Introducción\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
        evaluacion: /##\s*Evaluación\s*\/\s*Examen\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
        diagnostico: /##\s*Diagnóstico\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
        tratamiento: /##\s*Tratamiento\s*\/\s*Terapia\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
        cierre: /##\s*Cierre\s*\n([\s\S]*?)(?=\n##\s*|$)/i,
        referencias: /##\s*Referencias\s*\n([\s\S]*?)(?=\n##\s*|$)/i
    };

    // Extraer cada sección
    Object.keys(patrones).forEach(seccion => {
        const match = texto.match(patrones[seccion]);
        if (match && match[1]) {
            secciones[seccion] = match[1].trim();
        }
    });

    return secciones;
}

// Función para limpiar y formatear el resumen (mantener para compatibilidad)
function limpiarYFormatearResumen(resumen) {
    if (!resumen) return '';

    // Remover texto técnico interno
    let resumenLimpio = resumen
        .replace(/Resumen basado en evidencia:/gi, '')
        .replace(/Nota:.*?originalidad.*?citados\./gs, '')
        .replace(/CHUNK\d+/g, '')
        .replace(/\[.*?\]/g, '')
        .trim();

    // Dividir en puntos numerados si existen
    const puntos = resumenLimpio.split(/\d+\.\s*\*\*/);

    if (puntos.length > 1) {
        // Formatear como lista numerada
        return puntos
            .filter(punto => punto.trim())
            .map((punto, index) => {
                const contenido = punto.replace(/\*\*/g, '').trim();
                return `${index + 1}. **${contenido}**`;
            })
            .join('\n\n');
    } else {
        // Formatear como párrafo único
        return resumenLimpio.replace(/\*\*/g, '**');
    }
}

// Función para limpiar recomendaciones
function limpiarRecomendaciones(recomendaciones) {
    if (!recomendaciones || !Array.isArray(recomendaciones)) return [];

    return recomendaciones
        .filter(rec => rec && rec.trim())
        .map(rec => {
            // Remover numeración duplicada
            let limpia = rec.replace(/^\d+\.\s*\d+\.\s*/, '');
            // Remover asteriscos extra
            limpia = limpia.replace(/\*\*/g, '');
            // Capitalizar primera letra
            return limpia.charAt(0).toUpperCase() + limpia.slice(1);
        })
        .filter(rec => rec.length > 10) // Filtrar recomendaciones muy cortas
        .slice(0, 5); // Limitar a 5 recomendaciones
}

// Función para procesar con DeepSeek
async function procesarConDeepSeek(mensaje) {
    try {
        const contexto = obtenerContextoFormulario();

        const response = await fetch('/api/copilot/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: mensaje,
                context: contexto
            })
        });

        if (!response.ok) {
            throw new Error('Error en chat de DeepSeek');
        }

        const data = await response.json();

        if (data.success && data.reply) {
            agregarMensajeChat(data.reply, 'ai');
        } else {
            agregarMensajeChat('Gracias por tu mensaje. ¿En qué puedo ayudarte específicamente?', 'system');
        }

    } catch (error) {
        console.error('❌ Error procesando con DeepSeek:', error);
        agregarMensajeChat('Gracias por tu mensaje. ¿En qué puedo ayudarte específicamente?', 'system');
    }
}

// Función para obtener contexto del formulario
function obtenerContextoFormulario() {
    const contexto = {};

    // Campos principales
    const campos = {
        motivoConsulta: '#motivoConsulta',
        tipoAtencion: '#tipoAtencion',
        pacienteNombre: '#pacienteNombre',
        pacienteRut: '#pacienteRut',
        pacienteEdad: '#pacienteEdad',
        antecedentes: '#antecedentes',
        evaluacion: '#evaluacion',
        diagnostico: '#diagnostico',
        tratamiento: '#tratamiento',
        observaciones: '#observaciones'
    };

    Object.entries(campos).forEach(([key, selector]) => {
        const element = document.querySelector(selector);
        if (element) {
            contexto[key] = element.value || element.textContent || '';
        }
    });

    return contexto;
}

// Función para integrar con el sistema de IA existente
function integrarConSistemaIA() {
    console.log('🔗 Integrando chat con sistema IA...');

    // Interceptar mensajes del sistema IA para mostrarlos en el chat
    if (typeof window.agregarMensajeElegant === 'function') {
        const originalAddMessage = window.agregarMensajeElegant;
        window.agregarMensajeElegant = function (mensaje, tipo) {
            // Llamar a la función original
            originalAddMessage(mensaje, tipo);

            // También agregar al chat de la sidebar
            agregarMensajeChat(mensaje, tipo);
        };

        console.log('✅ Chat integrado con sistema IA');
    }
}

// Función para verificar y restaurar el chat
function verificarYRestaurarChat() {
    console.log('🔍 Verificando chat en la sidebar...');

    const sidebarContainer = document.getElementById('sidebarContainer');
    if (!sidebarContainer) {
        console.error('❌ sidebarContainer no encontrado');
        return;
    }

    const chat = sidebarContainer.querySelector('.copilot-chat-elegant');
    if (!chat) {
        console.log('🔧 Chat no encontrado, creando...');
        crearChatEnSidebar();
    } else {
        console.log('✅ Chat encontrado en la sidebar');
    }

    // Integrar con sistema IA
    integrarConSistemaIA();
}

// Función para inicializar el chat
function inicializarChat() {
    console.log('🚀 Inicializando chat en la sidebar...');

    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(verificarYRestaurarChat, 100);
        });
    } else {
        setTimeout(verificarYRestaurarChat, 100);
    }
}

// Exportar funciones para uso global
window.crearChatEnSidebar = crearChatEnSidebar;
window.enviarMensajeChat = enviarMensajeChat;
window.agregarMensajeChat = agregarMensajeChat;
window.verificarYRestaurarChat = verificarYRestaurarChat;

// Inicializar cuando se carga el script
inicializarChat();

// También inicializar después de un delay para asegurar que otros scripts se carguen
setTimeout(() => {
    verificarYRestaurarChat();
}, 500);

console.log('✅ Script de restauración de chat cargado'); 