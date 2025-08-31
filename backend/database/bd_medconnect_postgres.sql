-- Sheet: Medicamentos
DROP TABLE IF EXISTS "medicamentos";
CREATE TABLE "medicamentos" (
  
);


-- Sheet: Examenes
DROP TABLE IF EXISTS "examenes";
CREATE TABLE "examenes" (
  
);


-- Sheet: Interacciones_Bot
DROP TABLE IF EXISTS "interacciones_bot";
CREATE TABLE "interacciones_bot" (
  "id" NUMERIC,
  "user_id" NUMERIC,
  "username" TEXT,
  "message" TEXT,
  "timestamp" TIMESTAMP,
  "action_type" TEXT,
  "status" TEXT,
  "unnamed_8" TEXT,
  "unnamed_10" TIMESTAMP,
  "unnamed_11" TEXT,
  "unnamed_12" TEXT
);

INSERT INTO "interacciones_bot" ("id", "user_id", "username", "message", "timestamp", "action_type", "status", "unnamed_8", "unnamed_10", "unnamed_11", "unnamed_12") VALUES
(21.0, 1071410995.0, 'Sin username', '/codigo MED170899', TIMESTAMP '2025-06-29 05:27:31', 'message', 'processed', NULL, NULL, NULL, NULL),
(22.0, 1071410995.0, 'Sin username', 'Hola', TIMESTAMP '2025-06-29 05:28:06', 'message', 'processed', NULL, NULL, NULL, NULL),
(23.0, 1071410995.0, 'Sin username', '/registrar', TIMESTAMP '2025-06-29 05:28:19', 'message', 'processed', NULL, NULL, NULL, NULL),
(24.0, 1071410995.0, 'Sin username', 'Hola', TIMESTAMP '2025-06-29 05:28:26', 'message', 'processed', NULL, NULL, NULL, NULL),
(25.0, 1071410995.0, 'Sin username', 'Medicamentos', TIMESTAMP '2025-06-29 05:28:34', 'message', 'processed', NULL, NULL, NULL, NULL),
(NULL, NULL, NULL, NULL, TIMESTAMP '1970-01-01 00:00:00', '1071410995', 'Sin username', '/start', TIMESTAMP '2025-07-05 20:14:15', 'message', 'processed');

-- Sheet: Agenda
DROP TABLE IF EXISTS "agenda";
CREATE TABLE "agenda" (
  
);


-- Sheet: Horarios_Disponibles
DROP TABLE IF EXISTS "horarios_disponibles";
CREATE TABLE "horarios_disponibles" (
  "id" BIGINT,
  "profesional_id" BOOLEAN,
  "dia_semana" TEXT,
  "hora_inicio" TIMESTAMP,
  "hora_fin" TIMESTAMP,
  "intervalo_minutos" BIGINT,
  "estado" TEXT
);

INSERT INTO "horarios_disponibles" ("id", "profesional_id", "dia_semana", "hora_inicio", "hora_fin", "intervalo_minutos", "estado") VALUES
(1, TRUE, 'Lunes', TIMESTAMP '2025-08-31 09:00:00', TIMESTAMP '2025-08-31 18:00:00', 30, 'Activo'),
(2, TRUE, 'Martes', TIMESTAMP '2025-08-31 09:00:00', TIMESTAMP '2025-08-31 18:00:00', 30, 'Activo'),
(3, TRUE, 'Miércoles', TIMESTAMP '2025-08-31 09:00:00', TIMESTAMP '2025-08-31 18:00:00', 30, 'Activo'),
(4, TRUE, 'Jueves', TIMESTAMP '2025-08-31 09:00:00', TIMESTAMP '2025-08-31 18:00:00', 30, 'Activo'),
(5, TRUE, 'Viernes', TIMESTAMP '2025-08-31 09:00:00', TIMESTAMP '2025-08-31 18:00:00', 30, 'Activo');

-- Sheet: Especialidades
DROP TABLE IF EXISTS "especialidades";
CREATE TABLE "especialidades" (
  
);


-- Sheet: Familiares_Autorizados
DROP TABLE IF EXISTS "familiares_autorizados";
CREATE TABLE "familiares_autorizados" (
  
);


-- Sheet: Recordatorios
DROP TABLE IF EXISTS "recordatorios";
CREATE TABLE "recordatorios" (
  
);


-- Sheet: Logs_Acceso
DROP TABLE IF EXISTS "logs_acceso";
CREATE TABLE "logs_acceso" (
  
);


-- Sheet: Usuarios
DROP TABLE IF EXISTS "usuarios";
CREATE TABLE "usuarios" (
  "id" BIGINT,
  "email" TEXT,
  "password_hash" TEXT,
  "nombre" TEXT,
  "apellido" TEXT,
  "telefono" BIGINT,
  "fecha_nacimiento" DATE,
  "genero" TEXT,
  "direccion" TEXT,
  "ciudad" TEXT,
  "fecha_registro" TIMESTAMP,
  "ultimo_acceso" TIMESTAMP,
  "estado" TEXT,
  "tipo_usuario" TEXT,
  "verificado" BOOLEAN
);

INSERT INTO "usuarios" ("id", "email", "password_hash", "nombre", "apellido", "telefono", "fecha_nacimiento", "genero", "direccion", "ciudad", "fecha_registro", "ultimo_acceso", "estado", "tipo_usuario", "verificado") VALUES
(1, 'diego.castro.lagos@gmail.com', '$2b$12$7Q7mZBwzWngSfqgCVgQ0WetbCjsiWPwoPBFgIRinQq7vwtWVmyDeS', 'Diego', 'Castro', 56979712175, NULL, NULL, '4260000', 'Talcahuano', TIMESTAMP '2025-08-04 03:05:37', TIMESTAMP '2025-08-30 21:11:16', 'activo', 'profesional', FALSE),
(2, 'rodrigoandressilvabreve@gmail.com', '$2b$12$SlxNEtGm3/QtcfV2.B3Ga.rsi7WSf6UqQmtyXJD80w.zwy29BepsW', 'Rodrigo Andres', 'Silva Breve', 987042150, DATE '1987-11-10', 'Masculino', 'Las amapolas 157 Villa Radiata', 'Arauco', TIMESTAMP '2025-08-04 04:49:25', TIMESTAMP '2025-08-04 04:57:59', 'activo', 'profesional', FALSE);

-- Sheet: Profesionales
DROP TABLE IF EXISTS "profesionales";
CREATE TABLE "profesionales" (
  "id" BIGINT,
  "email" TEXT,
  "nombre" TEXT,
  "apellido" TEXT,
  "telefono" BIGINT,
  "numero_registro" TEXT,
  "especialidad" TEXT,
  "anos_experiencia" NUMERIC,
  "calificacion" TEXT,
  "direccion_consulta" TEXT,
  "horario_atencion" TEXT,
  "idiomas" TEXT,
  "profesion" TEXT,
  "institucion" TEXT,
  "fecha_registro" NUMERIC,
  "estado" TEXT,
  "disponible" BOOLEAN,
  "unnamed_21" TIMESTAMP,
  "unnamed_22" TIMESTAMP,
  "unnamed_23" TEXT
);

INSERT INTO "profesionales" ("id", "email", "nombre", "apellido", "telefono", "numero_registro", "especialidad", "anos_experiencia", "calificacion", "direccion_consulta", "horario_atencion", "idiomas", "profesion", "institucion", "fecha_registro", "estado", "disponible", "unnamed_21", "unnamed_22", "unnamed_23") VALUES
(1, 'diego.castro.lagos@gmail.com', 'Diego', 'Castro', 56979712175, 'FP101015', NULL, NULL, 'Kinesiología', NULL, NULL, 'Español, ingles', 'Licenciada en Kinesiólogia', 'Universidad Las Ámericas', 0.0, 'activo', TRUE, TIMESTAMP '2025-08-04 03:05:38', TIMESTAMP '2025-08-04 03:05:38', NULL),
(2, 'rodrigoandressilvabreve@gmail.com', 'Rodrigo Andres', 'Silva Breve', 987042150, '624365', 'Traumatología', 5.0, 'Kinesiología', 'Las Amapolas 157 Villa Radiata Arauco', '10:00 - 20:00', 'Español', 'Kinesiólogo', 'Universidad de las Américas', 0.0, 'activo', TRUE, TIMESTAMP '2025-08-04 04:49:25', TIMESTAMP '2025-08-04 04:49:25', 'Rehabilitación musculoesqueletica y respiratoria adulto y niño.');

-- Sheet: Certificaciones
DROP TABLE IF EXISTS "certificaciones";
CREATE TABLE "certificaciones" (
  
);


-- Sheet: Pacientes_Profesional
DROP TABLE IF EXISTS "pacientes_profesional";
CREATE TABLE "pacientes_profesional" (
  "paciente_id" TEXT,
  "profesional_id" BOOLEAN,
  "nombre_completo" TEXT,
  "rut" TEXT,
  "edad" BIGINT,
  "fecha_nacimiento" DATE,
  "genero" TEXT,
  "telefono" NUMERIC,
  "email" TEXT,
  "direccion" TEXT,
  "antecedentes_medicos" TEXT,
  "fecha_primera_consulta" TIMESTAMP,
  "ultima_consulta" TIMESTAMP,
  "num_atenciones" BIGINT,
  "estado_relacion" TEXT,
  "fecha_registro" TIMESTAMP,
  "notas" TEXT
);

INSERT INTO "pacientes_profesional" ("paciente_id", "profesional_id", "nombre_completo", "rut", "edad", "fecha_nacimiento", "genero", "telefono", "email", "direccion", "antecedentes_medicos", "fecha_primera_consulta", "ultima_consulta", "num_atenciones", "estado_relacion", "fecha_registro", "notas") VALUES
('PAC_20250804_031213', TRUE, 'Giselle Arratia', '18145296-k', 34, DATE '1992-06-25', 'Femenino', 56978784574.0, 'giselle.arratia@gmail.com', 'Pasaje El Boldo 8654, Pudahuel, Santiago', 'HTA, EPOC', NULL, TIMESTAMP '2025-08-03 23:13:00', 1, 'activo', TIMESTAMP '2025-08-04 03:12:13', NULL),
('PAC_20250804_003952', TRUE, 'Roberto Reyes', '17675599-8', 34, DATE '1992-02-04', 'Masculino', 56971714520.0, 'r.reyes@gmail.com', 'Los Reyes 1452, depto 123, Las Condes', 'Diabetes, HTA, Lesión meniscal', NULL, TIMESTAMP '2025-08-04 01:17:00', 3, 'activo', TIMESTAMP '2025-08-04 00:39:52', NULL),
('PAC_20250808_235925', TRUE, 'Francisco Reyes', '17675598-6', 35, NULL, NULL, NULL, NULL, NULL, NULL, TIMESTAMP '2025-08-08 23:40:00', TIMESTAMP '2025-08-08 23:40:00', 1, 'activo', TIMESTAMP '2025-08-08 23:59:25', 'Paciente creado automáticamente desde atención ATN_20250808_235924');

-- Sheet: Atenciones_Medicas
DROP TABLE IF EXISTS "atenciones_medicas";
CREATE TABLE "atenciones_medicas" (
  "atencion_id" TEXT,
  "profesional_id" BOOLEAN,
  "profesional_nombre" TEXT,
  "paciente_id" TEXT,
  "paciente_nombre" TEXT,
  "paciente_rut" TEXT,
  "paciente_edad" BIGINT,
  "fecha_hora" TIMESTAMP,
  "tipo_atencion" TEXT,
  "motivo_consulta" TEXT,
  "diagnostico" TEXT,
  "tratamiento" TEXT,
  "fecha_registro" TIMESTAMP,
  "estado" TEXT,
  "requiere_seguimiento" BOOLEAN,
  "tiene_archivos" TEXT
);

INSERT INTO "atenciones_medicas" ("atencion_id", "profesional_id", "profesional_nombre", "paciente_id", "paciente_nombre", "paciente_rut", "paciente_edad", "fecha_hora", "tipo_atencion", "motivo_consulta", "diagnostico", "tratamiento", "fecha_registro", "estado", "requiere_seguimiento", "tiene_archivos") VALUES
('ATN_20250804_031425', TRUE, 'Profesional', 'PAC_20250804_031213', 'Giselle Arratia', '18145296-k', 34, TIMESTAMP '2025-08-03 23:13:00', 'kinesiologia', 'Dolor Lumbar por fuerza mal realizada al levantar caja en el trabajo', 'Eva 8/!0
Kendall 3', 'Terapia Fortalecimeinto del core
Fisioterapia
Crioterapia', TIMESTAMP '2025-08-04 03:14:25', 'completada', FALSE, 'No'),
('ATN_20250804_012642', TRUE, 'Profesional', 'PAC_20250804_003952', 'Roberto Reyes', '17675599-8', 34, TIMESTAMP '2025-08-04 01:17:00', 'kinesiologia', 'Dolor en la rodilla por golpe en trabajo', 'Eva  7/10, Kendall 4, sensación de inestabilidad, en cuanto a los agravantes: se genera mucho dolor al subir escaleras. ', 'Crioterapia, Fortalecimiento muscular.', TIMESTAMP '2025-08-04 01:26:42', 'completada', FALSE, 'Sí'),
('ATN_20250808_235924', TRUE, 'Profesional', 'PAC_20250808_235925', 'Francisco Reyes', '17675598-6', 35, TIMESTAMP '2025-08-08 23:40:00', 'kinesiologia', 'Usuaria acude a la consulta por dolor en la espalda en la zona lumbar por golpe en el trabajo', '
- **Antecedentes del golpe**: 
  - Mecanismo lesional (ej.: caída, impacto directo, giro brusco).
impacto al chocar con una caja
  - Momento exacto del evento (agudo vs. subagudo).
agudo
- **Características del dolor**:
Irradiado
  - Localización precisa (L1-L5/S1, unilateral/bilateral).
localización en L5/S1
  - Irradiación (miembros inferiores, glúteos).
Miembro inferior izquierdo y glúteos
  - Intensidad (EVA u otra escala).
Eva 6/10
  - Factores agravantes/atenuantes (movimiento, postura).
Agravantes saltar, correr y atenuantes posición fetal.

Evaluación Física
Inspección:
- Postura antálgica (ej.: inclinación pélvica).
inclinación pelvica
- Signos inflamatorios (edema, eritema).
edema

Palpación:
- Puntos dolorosos en estructuras específicas:
  - Músculos (cuadrado lumbar, paravertebrales).
Cuadrado lumbar
  - Articulaciones facetarias.
Molestias al movilizar las articulaciones facetarias
  - Ligamentos (supraspinoso, iliolumbar).
Dolor a la plapación

Movilidad:
- Rango de movimiento (ROM) lumbar:
Limitado en la fleaxión por el dolor
  - Flexión/extensión.
Flexión diminuido
  - Rotación y lateralización.
limitadas por dolor
  - Síntomas asociados (click, bloqueo).
Bloqueo

Pruebas Específicas:
- **Neurológicas**:
  - Reflejos (rotuliano, aquiliano).
  - Fuerza muscular (cuádriceps, tibial anterior).
  - Sensibilidad (dermatomas L3-S1).
- **Músculo-esqueléticas**:
  - Signo de Lasègue (ciática).
  - Prueba de Patrick (sacroilíaca).

#### **Funcional**:
- Evaluación de gestos laborales/posturas repetitivas relacionadas con el trabajo.

---', '### **Objetivos Terapéuticos**
- **Corto plazo (1-2 semanas):**
  - Reducir dolor (<4 EVA) e inflamación.
  - Mejorar movilidad lumbar y cadera.
  - Educación postural básica.

- **Mediano plazo (3-4 semanas):**
  - Fortalecimiento progresivo de core y musculatura estabilizadora.
  - Reeducación de patrones funcionales y ergonómicos.

- **Largo plazo (5-6 semanas):**
  - Reintegro laboral seguro.
  - Prevención de recidivas.

---

### **Intervención por Fases**

#### **Fase Aguda (Semanas 1-2)**
- **Terapia manual:**
  - Movilizaciones suaves lumbopélvicas (grados I-II Kaltenborn).
  - Liberación miofascial multinivel (cuadrado lumbar, glúteos, isquiotibiales).

- **Electroterapia:**
  - TENS para control analgésico (80 Hz, amplitud submáxima).
  - Crioterapia post-sesión (15-20 min).

- **Educación:**
  - Técnicas de protección lumbar (técnicas de levantamiento, evitar rotaciones).
  - Recomendaciones ergonómicas laborales (ajuste de silla, pausas activas).

---

#### **Fase Subaguda (Semanas 3-4)**
- **Ejercicios terapéuticos:**
  - Estiramientos: piriforme, psoas, isquiotibiales (3 series x 30 seg).
  - Activación de transverso abdominal y multífidos (ejercicios en decúbito).
  - Movilizaciones activas asistidas (gato-camello, rotaciones en cuadrupedia).

- **Neurodinamia:**
  - Movilización del nervio ciático (slump test modificado).

---

#### **Fase Funcional (Semanas 5-6)**
- **Pilates terapéutico:**
  - Ejercicios en colchoneta con foco en control lumbopélvico (puente, plancha lateral).
- **Entrenamiento de fuerza:**
  - Sentadillas asistidas con TRX, peso muerto con kettlebell ligero.
- **Simulación laboral:**
  - Entrenamiento de gestos funcionales específicos (flexoextensiones controladas, levantamientos con técnica).
', TIMESTAMP '2025-08-08 23:59:24', 'completada', FALSE, 'No');

-- Sheet: Archivos_Adjuntos
DROP TABLE IF EXISTS "archivos_adjuntos";
CREATE TABLE "archivos_adjuntos" (
  "archivo_id" TEXT,
  "atencion_id" TEXT,
  "nombre_archivo" TEXT,
  "tipo_archivo" TEXT,
  "ruta_archivo" TEXT,
  "fecha_subida" TIMESTAMP,
  "estado" TEXT
);

INSERT INTO "archivos_adjuntos" ("archivo_id", "atencion_id", "nombre_archivo", "tipo_archivo", "ruta_archivo", "fecha_subida", "estado") VALUES
('FILE_73C77BF2CBAD', 'ATN_20250804_012642', 'rxtorax.png', 'image/png', 'uploads\ATN_20250804_012642\rxtorax.png', TIMESTAMP '2025-08-04 01:26:45', 'activo');

-- Sheet: Horarios_Profesional
DROP TABLE IF EXISTS "horarios_profesional";
CREATE TABLE "horarios_profesional" (
  "profesional_id" BOOLEAN,
  "dia_semana" TEXT,
  "hora_inicio" TIMESTAMP,
  "hora_fin" TIMESTAMP,
  "disponible" BOOLEAN
);

INSERT INTO "horarios_profesional" ("profesional_id", "dia_semana", "hora_inicio", "hora_fin", "disponible") VALUES
(TRUE, 'Lunes', TIMESTAMP '2025-08-31 08:00:00', TIMESTAMP '2025-08-31 16:03:00', TRUE),
(TRUE, 'Martes', TIMESTAMP '2025-08-31 08:00:00', TIMESTAMP '2025-08-31 16:30:00', TRUE),
(TRUE, 'Mircoles', TIMESTAMP '2025-08-31 08:00:00', TIMESTAMP '2025-08-31 16:30:00', TRUE),
(TRUE, 'Jueves', TIMESTAMP '2025-08-31 08:00:00', TIMESTAMP '2025-08-31 16:30:00', FALSE),
(TRUE, 'Viernes', TIMESTAMP '2025-08-31 08:00:00', TIMESTAMP '2025-08-31 16:30:00', TRUE),
(TRUE, 'Sbado', TIMESTAMP '2025-08-31 08:00:00', TIMESTAMP '2025-08-31 14:00:00', FALSE),
(TRUE, 'Domingo', TIMESTAMP '2025-08-31 08:00:00', TIMESTAMP '2025-08-31 14:00:00', FALSE),
(TRUE, 'Sbado', TIMESTAMP '2025-08-31 08:00:00', TIMESTAMP '2025-08-31 14:00:00', FALSE),
(TRUE, 'Domingo', TIMESTAMP '2025-08-31 08:00:00', TIMESTAMP '2025-08-31 14:00:00', FALSE);

-- Sheet: Recordatorios_Profesional
DROP TABLE IF EXISTS "recordatorios_profesional";
CREATE TABLE "recordatorios_profesional" (
  "recordatorio_id" TEXT,
  "profesional_id" BOOLEAN,
  "tipo" TEXT,
  "paciente_id" TEXT,
  "titulo" TEXT,
  "mensaje" TEXT,
  "fecha" DATE,
  "hora" TIMESTAMP,
  "prioridad" TEXT,
  "repetir" BOOLEAN,
  "tipo_repeticion" TEXT,
  "estado" TEXT,
  "fecha_creacion" TIMESTAMP
);

INSERT INTO "recordatorios_profesional" ("recordatorio_id", "profesional_id", "tipo", "paciente_id", "titulo", "mensaje", "fecha", "hora", "prioridad", "repetir", "tipo_repeticion", "estado", "fecha_creacion") VALUES
('8f684378-928b-4dc2-8590-c0244466a059', TRUE, 'confirmacion', 'PAC_20250804_003952', 'Llamar a Paciente para confirmar cita.', 'No sabía si iba a tener permiso en el trabajo', DATE '2025-08-04', TIMESTAMP '2025-08-31 09:30:00', 'alta', FALSE, 'diario', 'activo', TIMESTAMP '2025-08-04 01:00:29'),
('09213281-06e0-4cc6-af7e-01d8ffaeacd6', TRUE, 'confirmacion', 'PAC_20250804_031213', 'Llamar a Paciente para confirmar cita.', 'Recordar esto', DATE '2025-08-12', TIMESTAMP '2025-08-31 14:40:00', 'media', FALSE, 'diario', 'activo', TIMESTAMP '2025-08-12 01:36:39');

-- Sheet: Citas
DROP TABLE IF EXISTS "citas";
CREATE TABLE "citas" (
  
);


-- Sheet: Profesionales_Medicos
DROP TABLE IF EXISTS "profesionales_medicos";
CREATE TABLE "profesionales_medicos" (
  
);


-- Sheet: Sesiones
DROP TABLE IF EXISTS "sesiones";
CREATE TABLE "sesiones" (
  "id" TEXT,
  "atencion_id" TEXT,
  "fecha_sesion" TIMESTAMP,
  "duracion" BIGINT,
  "tipo_sesion" TEXT,
  "objetivos" TEXT,
  "actividades" TEXT,
  "observaciones" TEXT,
  "progreso" TEXT,
  "estado" TEXT,
  "recomendaciones" TEXT,
  "proxima_sesion" TEXT,
  "fecha_creacion" TIMESTAMP,
  "profesional_id" BOOLEAN
);

INSERT INTO "sesiones" ("id", "atencion_id", "fecha_sesion", "duracion", "tipo_sesion", "objetivos", "actividades", "observaciones", "progreso", "estado", "recomendaciones", "proxima_sesion", "fecha_creacion", "profesional_id") VALUES
('2f8f9c42-eca2-4501-b8ce-a398fbd8b9ab', 'ATN_20250804_031425', TIMESTAMP '2025-08-04 05:42:00', 60, 'tratamiento', 'Modulación del dolor', 'Crioterapia, con hielo localizado por 10 minutos
Movilidad pasiva, en los rangos permitidos por el dolor
bicicleta 15 min carga liviana', 'Usuario presenta dolor aún en el movimiento pasivo 7/10', 'regular', 'completada', 'Se recomienda seguir con tratamiento en el hogar, se educa al usuario', 'La otra semana el mismo día', TIMESTAMP '2025-08-04 01:48:46', TRUE);

-- Sheet: Pacientes
DROP TABLE IF EXISTS "pacientes";
CREATE TABLE "pacientes" (
  
);


-- Sheet: Consultas
DROP TABLE IF EXISTS "consultas";
CREATE TABLE "consultas" (
  
);


-- Sheet: Familiares
DROP TABLE IF EXISTS "familiares";
CREATE TABLE "familiares" (
  
);


-- Sheet: Citas_Agenda
DROP TABLE IF EXISTS "citas_agenda";
CREATE TABLE "citas_agenda" (
  "cita_id" TEXT,
  "fecha" BOOLEAN,
  "hora" TEXT,
  "paciente_id" TEXT,
  "paciente_nombre" TEXT,
  "paciente_rut" DATE,
  "tipo_atencion" TIMESTAMP,
  "estado" TEXT,
  "motivo" TEXT,
  "profesional_id" TEXT,
  "fecha_creacion" TIMESTAMP,
  "fecha_modificacion" BOOLEAN
);

INSERT INTO "citas_agenda" ("cita_id", "fecha", "hora", "paciente_id", "paciente_nombre", "paciente_rut", "tipo_atencion", "estado", "motivo", "profesional_id", "fecha_creacion", "fecha_modificacion") VALUES
('CITA_20250811_224852', TRUE, 'PAC_20250808_235925', 'Francisco Reyes', '17675598-6', DATE '2025-08-12', TIMESTAMP '2025-08-31 08:05:00', 'kinesiologia', 'pendiente', 'te amo', TIMESTAMP '2025-08-11 22:48:52', FALSE),
('CITA_20250811_233035', TRUE, 'PAC_20250808_235925', 'Francisco Reyes', '17675598-6', DATE '2025-08-19', TIMESTAMP '2025-08-31 10:00:00', 'kinesiologia', 'pendiente', 'Te amo gigi', TIMESTAMP '2025-08-11 23:30:35', FALSE),
('CITA_20250811_235556', TRUE, 'PAC_20250804_031213', 'Giselle Arratia', '18145296-k', DATE '2025-08-12', TIMESTAMP '2025-08-31 10:00:00', 'kinesiologia', 'pendiente', 'te amo', TIMESTAMP '2025-08-11 23:55:56', FALSE),
('CITA_20250812_003342', TRUE, 'PAC_20250804_003952', 'Roberto Reyes', '17675599-8', DATE '2025-08-19', TIMESTAMP '2025-08-31 10:00:00', 'kinesiologia', 'pendiente', 'Prueba de cita', TIMESTAMP '2025-08-12 00:33:42', FALSE),
('CITA_20250812_003706', TRUE, 'PAC_20250804_031213', 'Giselle Arratia', '18145296-k', DATE '2025-08-19', TIMESTAMP '2025-08-31 10:30:00', 'kinesiologia', 'pendiente', 'prueba', TIMESTAMP '2025-08-12 00:37:06', FALSE),
('CITA_20250812_003821', TRUE, 'PAC_20250808_235925', 'Francisco Reyes', '17675598-6', DATE '2025-08-13', TIMESTAMP '2025-08-31 09:00:00', 'kinesiologia', 'pendiente', 'prueba', TIMESTAMP '2025-08-12 00:38:21', FALSE),
('CITA_20250813_190130', TRUE, 'PAC_20250804_031213', 'Giselle Arratia', '18145296-k', DATE '2025-07-25', TIMESTAMP '2025-08-31 17:00:00', 'kinesiologia', 'pendiente', 'Atención kinesica', TIMESTAMP '2025-08-13 19:01:30', FALSE);

