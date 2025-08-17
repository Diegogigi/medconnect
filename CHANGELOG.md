# Changelog - MedConnect

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2024-12-28

### 🤖 Copilot Health - IA Clínica Asistiva
- **Nuevo**: Módulo completo de IA clínica asistiva integrado
- **Nuevo**: Análisis automático del motivo de consulta con detección de especialidad
- **Nuevo**: Evaluación inteligente de antecedentes con detección de banderas rojas
- **Nuevo**: Sugerencias de planes de tratamiento basados en evidencia científica
- **Nuevo**: Interfaz web dedicada para profesionales en `/copilot-health`
- **Nuevo**: 4 endpoints de API para integración con sistemas externos
- **Nuevo**: Soporte para 8 especialidades médicas principales
- **Nuevo**: Referencias bibliográficas con DOI y niveles de evidencia
- **Nuevo**: Aclaración legal automática en todas las sugerencias
- **Nuevo**: Sistema de pruebas automatizadas para validación

### 🎯 Funcionalidades de Copilot Health
- **Análisis del Motivo**: Detección automática de especialidad, categoría y urgencia
- **Evaluación Inteligente**: Detección de banderas rojas y omisiones comunes
- **Planes de Tratamiento**: Sugerencias con evidencia científica y contraindicaciones
- **Análisis Completo**: Resumen integral con todas las funcionalidades

### 🔧 Integración Técnica
- **Módulo Principal**: `copilot_health.py` con clase CopilotHealth
- **API Endpoints**: 4 endpoints REST para integración
- **Interfaz Web**: Plantilla `copilot_health.html` con diseño moderno
- **Navegación**: Enlace en panel de profesionales
- **Pruebas**: Script `test_copilot_health.py` para validación
- **Normalización Regional**: Función `_normalizar_tipo_atencion()` con diccionario de sinónimos
- **Pruebas Regionales**: Script `test_normalizacion_regional.py` para validar variaciones
- **Documentación Regional**: `NORMALIZACION_REGIONAL_IA.md` con casos de uso y ejemplos

### 📊 Especialidades Soportadas
- Traumatología, Cardiología, Neurología, Gastroenterología
- Neumología, Dermatología, Endocrinología, Psiquiatría

### 🌍 Normalización Regional - Nuevas Capacidades
- **Nuevo**: Reconocimiento de sinónimos y variaciones regionales de carreras de salud
- **Nuevo**: Sistema de normalización inteligente para diferentes contextos geográficos
- **Nuevo**: Soporte para terminología local y familiar en cada región
- **Nuevo**: Adaptación automática a diferentes culturas y contextos médicos

#### Variaciones Regionales Soportadas
- **Fisioterapia/Kinesiología**: fisio, fisioterapeuta, kinesio, kinesiólogo, kinesiología
- **Fonoaudiología/Logopedia**: fono, logopeda, logopedia, terapia del habla, patología del habla
- **Terapia Ocupacional/Ergoterapia**: t.o., to, ergoterapia, ergoterapeuta
- **Psicología/Psicoterapia**: psico, psicólogo, psicóloga, psicoterapia, psicoterapeuta
- **Nutrición/Dietética**: nutricionista, dietista, nutriólogo, dietólogo
- **Medicina General/Familiar**: médico general, medicina familiar, médico de familia, medicina primaria
- **Urgencia/Emergencia**: emergencia, urgencias, emergencias, médico de urgencia

#### Beneficios de la Normalización Regional
- **Inclusión Global**: Soporte para diferentes contextos culturales y geográficos
- **Experiencia Familiar**: Reconocimiento de terminología local y cotidiana
- **Precisión Mejorada**: Detección más robusta de especialidades médicas
- **Adaptabilidad**: Sistema que se adapta a diferentes regiones automáticamente

### 🔄 Integración en Formulario de Atenciones
- **Análisis en Tiempo Real**: Al escribir el motivo de consulta, la IA analiza automáticamente
- **Preguntas Sugeridas Integradas**: Aparecen automáticamente en el campo de evaluación
- **Sugerencias de Tratamiento**: Botón para generar opciones de tratamiento con evidencia
- **Análisis Completo**: Sección especial para análisis integral de toda la información
- **Indicadores Visuales**: Badges y cards que muestran el estado de la IA
- **Funciones JavaScript**: Integración completa con el flujo de trabajo existente

### 🎨 Mejoras de UX
- **Indicadores de IA**: Badges azules, verdes y amarillos para identificar funcionalidades de IA
- **Spinners de Carga**: Indicadores visuales durante el análisis
- **Cards Informativos**: Secciones organizadas para mostrar resultados de IA
- **Botones de Acción**: Funciones para insertar sugerencias en los campos correspondientes
- **Notificaciones**: Feedback inmediato sobre el estado de las operaciones de IA

## [2.2.0] - 2024-12-28

### 🚀 Bot de Telegram - Mejoras Avanzadas
- **Nuevo**: 3 categorías adicionales (recordatorio, cita_futura, seguimiento)
- **Expandido**: Categoría medicamento con 19 palabras clave (+137%)
- **Expandido**: Categoría examen con 20 palabras clave (+150%)
- **Nuevo**: Reconocimiento de medicamentos nuevos vs seguimiento de efectos
- **Nuevo**: Diferenciación entre exámenes realizados y futuros
- **Nuevo**: Sistema de recordatorios inteligentes para medicamentos y citas
- **Nuevo**: Gestión de citas futuras con planificación proactiva
- **Nuevo**: Seguimiento personalizado de tratamientos y evolución
- **Mejorado**: Detección de efectos secundarios y adherencia al tratamiento
- **Mejorado**: Reconocimiento de preparación especial para exámenes

### 💊 Medicamentos Avanzados
- **Frases reconocidas**: "Me recetaron un nuevo medicamento", "¿Cómo va mi tratamiento?", "He notado efectos secundarios"
- **Capacidades**: Seguimiento de efectividad, detección de reacciones, monitoreo de adherencia
- **Diferenciación**: Medicamentos nuevos vs seguimiento de medicamentos existentes

### 🩺 Exámenes Completos
- **Realizados**: "Ya me hice los exámenes", "Tengo resultados", "Salieron los análisis"
- **Futuros**: "Tengo que hacerme", "Debo hacerme", "Tengo programada una ecografía"
- **Capacidades**: Registro de resultados, programación de recordatorios, preparación especial

### 🔔 Sistema de Recordatorios
- **Frases**: "Recordarme tomar las pastillas", "Necesito una alerta", "Programar aviso"
- **Tipos**: Medicamentos, citas médicas, exámenes programados, renovación de recetas

### 📅 Citas Futuras
- **Frases**: "Quiero agendar una cita", "Programar cita con cardiólogo", "Reservar hora"
- **Funcionalidades**: Planificación proactiva, organización de consultas futuras

### 📊 Seguimiento Personalizado
- **Frases**: "¿Cómo voy con mi diabetes?", "Evolución de mi presión", "¿Estoy mejorando?"
- **Capacidades**: Monitoreo continuo, evaluación de progreso, tracking de parámetros vitales

### 📈 Estadísticas Expandidas
- **Categorías**: 11 tipos de intenciones (antes: 8)
- **Palabras clave**: 60+ términos reconocidos (antes: 30+)
- **Cobertura**: +200% en reconocimiento de intenciones
- **Precisión**: 71.4% en 35 frases de prueba avanzadas

### 📚 Documentación Nueva
- **BOT_MEJORAS_AVANZADAS.md**: Documentación completa de 200+ líneas
- **demo_mejoras_avanzadas.py**: Script de demostración con 35 casos de prueba
- **bot_mejoras_avanzadas.py**: Archivo de especificaciones técnicas

## [1.0.0] - 2024-12-19

### ✨ Agregado
- **Sistema completo de gestión médica familiar**
- **Bot de Telegram inteligente** con interfaz de botones
- **Aplicación web Flask** con autenticación
- **Sistema de gestión familiar** con permisos granulares
- **Notificaciones automáticas** a familiares autorizados
- **Recordatorios de medicamentos** y citas médicas
- **Subida de archivos médicos** (exámenes, recetas)
- **Base de datos en Google Sheets** sin costos adicionales
- **Sistema de conectividad robusta** con reintentos automáticos
- **Supervisor de procesos** para el bot
- **Logs estructurados** con timestamps
- **Manejo de errores** comprehensivo

### 🤖 Bot de Telegram
- Comandos principales: `/start`, `/help`, `/mi_info`, `/familiares`, `/notificaciones`
- Palabras clave: `menu`, `familiares`, `documentos`, `notificaciones`
- **Autorización de familiares** paso a paso
- **Gestión multi-usuario** fluida
- **Cambio entre usuarios** gestionados
- **Sistema de permisos**: Solo Ver, Ver y Editar, Control Total
- **Notificaciones en tiempo real** de actividad familiar
- **Recordatorios programables** con diferentes frecuencias

### 🌐 Aplicación Web
- **Dashboard principal** responsivo
- **Autenticación segura** con bcrypt
- **Gestión de perfiles** de usuario
- **Interfaz optimizada** para móviles
- **Páginas especializadas** para pacientes y profesionales

### 👨‍👩‍👧‍👦 Sistema Familiar
- **Autorización granular** de familiares
- **Verificación de permisos** en cada operación
- **Logs de auditoría** de acciones familiares
- **Notificaciones automáticas** cuando usuario principal usa el bot
- **Avisos de nuevas consultas** médicas
- **Alertas de citas** médicas próximas
- **Coordinación entre cuidadores**

### 📊 Base de Datos (Google Sheets)
- **Estructura optimizada** para información médica
- **Hojas especializadas**: Usuarios, Atenciones, Medicamentos, Exámenes, Familiares, Recordatorios
- **Métodos CRUD completos** en `sheets_manager.py`
- **Manejo de errores** de conectividad con Google API
- **Backup automático** en la nube

### 🔧 Mejoras de Conectividad
- **Manejo robusto de errores** de red
- **Timeouts configurables** (10s conexión, 30s lectura)
- **Reintentos automáticos** con backoff exponencial
- **Detección de conectividad** a internet
- **Pausas adaptativas** en caso de errores
- **Contador de errores consecutivos**
- **Supervisor de procesos** con reinicio automático

### 🚀 Despliegue
- **Configuración para Railway** con `Procfile` y `railway.json`
- **Variables de entorno** seguras
- **Archivos de configuración** completos
- **Documentación de despliegue** detallada
- **Guías paso a paso** para GitHub y Railway

### 📝 Documentación
- **README.md completo** con guías de instalación
- **DEPLOY_GUIDE.md** con pasos detallados
- **FUNCIONALIDAD_FAMILIA.md** con casos de uso
- **SOLUCION_CONECTIVIDAD.md** con mejoras técnicas
- **Archivos de ejemplo** para configuración

### 🛡️ Seguridad
- **Exclusión de archivos sensibles** con `.gitignore`
- **Variables de entorno** para credenciales
- **Validación de permisos** en operaciones familiares
- **Logs de auditoría** completos
- **Autenticación robusta** con Flask

### 🔧 Archivos de Configuración
- `.gitignore` - Exclusión de archivos sensibles
- `requirements.txt` - Dependencias actualizadas
- `Procfile` - Comandos para Railway
- `railway.json` - Configuración avanzada de despliegue
- `env.example` - Ejemplo de variables de entorno
- `LICENSE` - Licencia MIT
- `CHANGELOG.md` - Este archivo

### 📋 Estructura del Proyecto
```
medconnect/
├── app.py                          # Aplicación Flask principal
├── bot.py                          # Bot de Telegram con gestión familiar
├── run_bot.py                      # Supervisor del bot
├── config.py                       # Configuración del proyecto
├── auth_manager.py                 # Gestión de autenticación
├── backend/
│   ├── database/
│   │   └── sheets_manager.py      # Gestión completa de Google Sheets
│   ├── api/
│   │   └── flask_api.py           # API REST
│   └── bot/
│       ├── bot_handlers.py        # Manejadores del bot
│       └── telegram_bot.py        # Bot alternativo
├── static/                         # Recursos estáticos
├── templates/                      # Plantillas HTML
└── docs/                          # Documentación
```

### 🎯 Casos de Uso Implementados
1. **Familia con madre de tercera edad**:
   - Hijos autorizan diferentes niveles de permisos
   - Reciben notificaciones automáticas de actividad
   - Programan recordatorios de medicamentos
   - Acceden a información médica completa

2. **Cuidador principal**:
   - Gestiona información médica de múltiples familiares
   - Coordina cuidado entre varios familiares
   - Recibe alertas de citas y medicamentos

3. **Usuario independiente**:
   - Registra su propia información médica
   - Programa recordatorios personales
   - Comparte información selectivamente

### 🧪 Testing
- `test_bot_functionality.py` - Pruebas del bot
- `test_integration.py` - Pruebas de integración
- `test_multi_files_bot.py` - Pruebas multi-archivo
- Pruebas de conectividad exitosas (3/3)

### 🔄 Próximas Versiones
- [ ] App móvil nativa
- [ ] Integración con wearables
- [ ] IA para análisis de síntomas
- [ ] Telemedicina integrada
- [ ] API pública para desarrolladores

---

## Formato de Versiones

- **[MAJOR.MINOR.PATCH]** - Cambios incompatibles, nuevas funcionalidades, correcciones
- **Agregado** - Nuevas funcionalidades
- **Cambiado** - Cambios en funcionalidades existentes
- **Deprecado** - Funcionalidades que serán removidas
- **Removido** - Funcionalidades removidas
- **Corregido** - Corrección de errores
- **Seguridad** - Mejoras de seguridad

## [2024-12-28] - Bot con Lenguaje Natural Avanzado

### 🤖 Mejoras del Bot de Telegram
- **Reconocimiento de intenciones inteligente**: Detecta automáticamente qué quiere hacer el usuario
- **8 categorías de intenciones**: consultas, medicamentos, exámenes, historial, saludos, despedidas, ayuda, emergencias
- **Sinónimos incluidos**: Reconoce múltiples formas de expresar la misma intención
- **Respuestas conversacionales**: Lenguaje natural, amigable y empático
- **Variaciones aleatorias**: El bot no repite siempre la misma respuesta
- **Manejo de contexto**: Recuerda el hilo de conversación del usuario
- **Detección de emergencias**: Respuesta prioritaria con números de emergencia
- **Personalización**: Usa el nombre del usuario cuando está disponible

### 🎯 Ejemplos de Frases que Entiende
- **Consultas**: "Quiero registrar una consulta", "Fui al médico ayer"
- **Medicamentos**: "Necesito anotar un medicamento", "Estoy tomando pastillas"
- **Exámenes**: "Me hice unos exámenes", "Tengo resultados de laboratorio"
- **Historial**: "Muéstrame mi historial", "Quiero ver mis datos"
- **Emergencias**: "Tengo dolor fuerte", "Es urgente"

### 🛠️ Implementación Técnica
- **Sistema de puntuación**: Analiza keywords para detectar intención
- **Contexto en memoria**: Almacena estado de conversación por usuario
- **Respuestas dinámicas**: 4 variaciones para saludos y mensajes de error
- **Priorización**: Emergencias tienen máxima prioridad

### 📚 Documentación
- **BOT_LENGUAJE_NATURAL.md**: Guía completa de funcionalidades
- **Ejemplos de conversación**: Casos de uso detallados
- **Roadmap futuro**: Próximas mejoras planificadas

---

## [2024-12-28] - Sistema de Códigos Telegram + Landing Page Modernizada

### ✨ Nuevas Funcionalidades
- **Sistema de códigos para vinculación Telegram**: Reemplaza el sistema de email por códigos únicos (formato: MED123456)
- **Landing page completamente renovada**: Diseño moderno con hero section espectacular
- **Endpoints de diagnóstico del bot**: `/test-bot` y `/bot-stats` para monitoreo

### 🔧 Mejoras
- **Webhook del bot configurado**: Ahora responde mensajes correctamente
- **UI/UX mejorada**: Header translúcido, gradientes consistentes, efectos 3D
- **Responsive design**: Adaptativo para todos los dispositivos
- **Cache busting**: Parámetro aleatorio para CSS
- **Logging mejorado**: Mejor rastreo de eventos del webhook

### 🎨 Cambios Visuales
- **Logo prominente**: Utilización del logo.png en header y footer
- **Imagen principal**: Imagen2.png como hero background con overlay
- **6 tarjetas de servicios**: Con iconos circulares y efectos hover
- **Fuente Inter**: De Google Fonts para mejor legibilidad
- **Layout de dos columnas**: Texto + imagen con efectos visuales

### 🔗 Flujo de Vinculación Actualizado
1. Usuario va a perfil web → clic "Generar Código"
2. Sistema genera código MED123456 (expira en 15 minutos)
3. Usuario abre @Medconn_bot en Telegram
4. Usuario envía `/codigo MED123456`
5. Bot vincula automáticamente y saluda por nombre

### 🛠️ Archivos Modificados
- `app.py`: Sistema de códigos, webhook mejorado, endpoints de diagnóstico
- `templates/index.html`: Landing page completamente renovada
- `templates/profile.html`: Sección Telegram actualizada para códigos
- `static/js/profile.js`: Funciones de generación y manejo de códigos
- `auth_manager.py`: Método de vinculación por user_id
- `test_bot_functionality.py`: Script de diagnóstico del bot

### 🎯 Estado del Bot
- ✅ Bot de Telegram funcionando y respondiendo mensajes
- ✅ Webhook configurado: `https://www.medconnect.cl/webhook`
- ✅ Bot activo: @Medconn_bot (ID: 7618933472)
- ✅ 4/4 tests exitosos en script de diagnóstico

### 📱 Comandos del Bot Actualizados
- `/start` - Mensaje de bienvenida con instrucciones de códigos
- `/codigo MED123456` - Vinculación por código (nuevo)
- `/help` - Ayuda actualizada
- Todos los tips ahora dirigen a la plataforma web 