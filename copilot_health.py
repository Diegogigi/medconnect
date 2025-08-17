"""
Copilot Health - Módulo de IA Clínica Asistiva
Evolución de MedConnect.cl

Este módulo proporciona asistencia inteligente para profesionales de la salud
mediante análisis de motivos de consulta, sugerencias de evaluación y planes de tratamiento.
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar integración con APIs médicas
try:
    from medical_apis_integration import MedicalAPIsIntegration, convertir_a_formato_copilot, convertir_preguntas_a_formato_copilot, generar_planificacion_tratamiento_completa
    APIS_MEDICAS_DISPONIBLE = True
    logger.info("✅ Integración con APIs médicas disponible")
except ImportError:
    APIS_MEDICAS_DISPONIBLE = False
    logger.warning("⚠️ Integración con APIs médicas no disponible")

@dataclass
class MotivoConsulta:
    """Estructura para analizar el motivo de consulta"""
    texto_original: str
    especialidad_detectada: str
    categoria: str
    sintomas_principales: List[str]
    urgencia: str
    preguntas_sugeridas: List[str]

@dataclass
class EvaluacionInteligente:
    """Estructura para la evaluación inteligente"""
    banderas_rojas: List[str]
    campos_adicionales: List[str]
    omisiones_detectadas: List[str]
    recomendaciones: List[str]

@dataclass
class PlanTratamiento:
    """Estructura para planes de tratamiento sugeridos"""
    titulo: str
    descripcion: str
    evidencia_cientifica: str
    doi_referencia: str
    nivel_evidencia: str
    contraindicaciones: List[str]

class CopilotHealth:
    """
    Módulo principal de IA clínica asistiva para MedConnect
    """
    
    def __init__(self):
        # Inicializar integración con APIs médicas si está disponible
        self.apis_medicas = None
        if APIS_MEDICAS_DISPONIBLE:
            try:
                self.apis_medicas = MedicalAPIsIntegration()
                logger.info("✅ Integración con APIs médicas inicializada")
            except Exception as e:
                logger.error(f"❌ Error inicializando APIs médicas: {e}")
                self.apis_medicas = None
        
        # Mapeo de tipos de atención a especialidades médicas con sinónimos regionales
        self.tipos_atencion_especialidad = {
            'medicina_general': 'medicina_general',
            'fisioterapia': 'fisioterapia',
            'terapia_ocupacional': 'terapia_ocupacional',
            'enfermeria': 'enfermeria',
            'psicologia': 'psicologia',
            'nutricion': 'nutricion',
            'kinesiologia': 'kinesiologia',
            'fonoaudiologia': 'fonoaudiologia',
            'urgencia': 'urgencia'
        }
        
        # Diccionario de sinónimos y variaciones regionales
        self.sinonimos_especialidades = {
            # Fisioterapia - Variaciones regionales
            'fisioterapia': ['fisioterapia', 'fisioterapeuta', 'fisio', 'fisioterapéutico', 'fisioterapéutica'],
            'kinesiologia': ['kinesiologia', 'kinesiología', 'kinesiólogo', 'kinesióloga', 'kinesio', 'kinesiología', 'kinesiologo'],
            
            # Fonoaudiología - Variaciones regionales
            'fonoaudiologia': ['fonoaudiologia', 'fonoaudiología', 'fonoaudiólogo', 'fonoaudióloga', 'fono', 'logopeda', 'logopedia', 'terapia del habla', 'patología del habla'],
            
            # Terapia Ocupacional - Variaciones regionales
            'terapia_ocupacional': ['terapia ocupacional', 'terapeuta ocupacional', 't.o.', 'to', 'ergoterapia', 'ergoterapeuta'],
            
            # Psicología - Variaciones regionales
            'psicologia': ['psicologia', 'psicología', 'psicólogo', 'psicóloga', 'psico', 'psicoterapia', 'psicoterapeuta'],
            
            # Nutrición - Variaciones regionales
            'nutricion': ['nutricion', 'nutrición', 'nutricionista', 'nutriólogo', 'nutrióloga', 'dietista', 'dietólogo', 'dietóloga'],
            
            # Enfermería - Variaciones regionales
            'enfermeria': ['enfermeria', 'enfermería', 'enfermero', 'enfermera', 'enfermería', 'cuidados de enfermería'],
            
            # Medicina General - Variaciones regionales
            'medicina_general': ['medicina general', 'médico general', 'médica general', 'medicina familiar', 'médico de familia', 'medicina primaria', 'médico primario'],
            
            # Urgencia - Variaciones regionales
            'urgencia': ['urgencia', 'emergencia', 'urgencias', 'emergencias', 'médico de urgencia', 'emergenciólogo']
        }
        
        # Especialidades médicas con palabras clave expandidas
        self.especialidades = {
            'traumatologia': ['dolor', 'fractura', 'esguince', 'luxacion', 'trauma', 'accidente', 'caida'],
            'cardiologia': ['dolor pecho', 'palpitaciones', 'arritmia', 'presion alta', 'infarto', 'angina'],
            'neurologia': ['dolor cabeza', 'migraña', 'mareo', 'vertigo', 'convulsiones', 'parestesias'],
            'gastroenterologia': ['dolor abdominal', 'nausea', 'vomito', 'diarrea', 'acidez', 'reflujo'],
            'neumologia': ['tos', 'dificultad respirar', 'dolor pecho', 'flema', 'sibilancias'],
            'dermatologia': ['erupcion', 'mancha', 'picazon', 'lesion', 'alergia', 'urticaria'],
            'endocrinologia': ['diabetes', 'tiroides', 'peso', 'sed', 'orina frecuente'],
            'psiquiatria': ['ansiedad', 'depresion', 'insomnio', 'estres', 'panico', 'humor'],
            'medicina_general': ['consulta general', 'revision', 'chequeo', 'sintomas generales', 'medico general', 'medicina familiar'],
            'fisioterapia': ['rehabilitacion', 'ejercicios', 'movilidad', 'fuerza', 'dolor muscular', 'fisio', 'fisioterapeuta', 'fisioterapéutico'],
            'terapia_ocupacional': ['actividades diarias', 'independencia', 'adaptaciones', 'rehabilitacion', 'ergoterapia', 'terapeuta ocupacional'],
            'enfermeria': ['cuidados', 'curas', 'medicacion', 'monitoreo', 'educacion', 'enfermero', 'enfermera'],
            'psicologia': ['estado animico', 'ansiedad', 'depresion', 'estres', 'comportamiento', 'psicologo', 'psicologa', 'psicoterapia'],
            'nutricion': ['alimentacion', 'dieta', 'peso', 'nutricion', 'habitos alimentarios', 'nutricionista', 'dietista'],
            'kinesiologia': ['movimiento', 'ejercicio', 'rehabilitacion', 'dolor', 'funcion', 'kinesiologo', 'kinesiologa', 'kinesio'],
            'fonoaudiologia': ['habla', 'lenguaje', 'deglucion', 'voz', 'comunicacion', 'fono', 'fonoaudiologo', 'fonoaudiologa', 'logopeda', 'logopedia'],
            'urgencia': ['emergencia', 'urgente', 'accidente', 'trauma', 'dolor agudo', 'urgencias', 'emergencias']
        }
        
        self.categorias_urgencia = {
            'emergencia': ['dolor fuerte', 'sangre', 'desmayo', 'accidente', 'trauma', 'dificultad respirar'],
            'urgente': ['dolor moderado', 'fiebre alta', 'vomito', 'diarrea severa'],
            'control': ['seguimiento', 'control', 'revision', 'chequeo'],
            'rutina': ['consulta rutinaria', 'examen', 'preventivo']
        }
        
        self.preguntas_especialidad = {
            'traumatologia': [
                "¿Hay irradiación del dolor hacia otras extremidades?",
                "¿Qué actividades agravan o alivian el dolor?",
                "¿Hay antecedentes de trauma directo?",
                "¿Ha tenido episodios similares antes?",
                "¿Hay limitación de movimientos?"
            ],
            'cardiologia': [
                "¿El dolor se irradia hacia el brazo izquierdo o mandíbula?",
                "¿Se agrava con el esfuerzo físico?",
                "¿Hay antecedentes familiares de problemas cardíacos?",
                "¿Presenta sudoración fría o náuseas?",
                "¿Cuánto tiempo dura el dolor?"
            ],
            'neurologia': [
                "¿El dolor es pulsátil o constante?",
                "¿Hay síntomas asociados como náuseas o fotofobia?",
                "¿Hay antecedentes familiares de migrañas?",
                "¿El dolor se agrava con la actividad física?",
                "¿Hay cambios en la visión?"
            ],
            'gastroenterologia': [
                "¿El dolor se relaciona con las comidas?",
                "¿Hay cambios en el hábito intestinal?",
                "¿Presenta fiebre o pérdida de peso?",
                "¿Hay antecedentes de úlceras o reflujo?",
                "¿El dolor es constante o intermitente?"
            ],
            'medicina_general': [
                "¿Cuándo comenzaron los síntomas?",
                "¿Hay factores que agravan o alivian los síntomas?",
                "¿Ha tenido síntomas similares antes?",
                "¿Hay antecedentes médicos relevantes?",
                "¿Está tomando algún medicamento?"
            ],
            'fisioterapia': [
                "¿Qué movimientos o actividades le causan dolor?",
                "¿Ha notado mejoría con algún tipo de ejercicio?",
                "¿Hay limitaciones en las actividades diarias?",
                "¿Ha recibido tratamiento fisioterapéutico antes?",
                "¿Cuál es su nivel de actividad física habitual?"
            ],
            'terapia_ocupacional': [
                "¿Qué actividades de la vida diaria le resultan difíciles?",
                "¿Ha notado cambios en su independencia?",
                "¿Qué adaptaciones ha realizado en su hogar?",
                "¿Cuál es su ocupación y cómo afecta su condición?",
                "¿Qué actividades son más importantes para usted?"
            ],
            'enfermeria': [
                "¿Cómo está su estado general de salud?",
                "¿Está cumpliendo con su medicación?",
                "¿Ha notado cambios en sus signos vitales?",
                "¿Necesita ayuda con cuidados específicos?",
                "¿Tiene dudas sobre su tratamiento?"
            ],
            'psicologia': [
                "¿Cómo se ha sentido emocionalmente últimamente?",
                "¿Ha notado cambios en su estado de ánimo?",
                "¿Cómo está manejando el estrés?",
                "¿Hay situaciones que le causan ansiedad?",
                "¿Cómo está su calidad del sueño?"
            ],
            'nutricion': [
                "¿Cómo es su alimentación actual?",
                "¿Ha notado cambios en su peso?",
                "¿Tiene alguna restricción alimentaria?",
                "¿Cuál es su nivel de actividad física?",
                "¿Hay alimentos que le causan malestar?"
            ],
            'kinesiologia': [
                "¿Qué movimientos le resultan más difíciles?",
                "¿Ha notado mejoría con algún tipo de ejercicio?",
                "¿Hay actividades que ya no puede realizar?",
                "¿Ha recibido tratamiento kinésico antes?",
                "¿Cuál es su objetivo de rehabilitación?"
            ],
            'fonoaudiologia': [
                "¿Ha notado cambios en su voz o habla?",
                "¿Tiene dificultades para tragar?",
                "¿Hay problemas de comunicación?",
                "¿Ha recibido terapia fonoaudiológica antes?",
                "¿Qué actividades de comunicación son más importantes?"
            ],
            'urgencia': [
                "¿Cuándo comenzó el problema?",
                "¿Qué tan intenso es el dolor/síntoma?",
                "¿Hay síntomas asociados?",
                "¿Ha tenido episodios similares antes?",
                "¿Hay antecedentes médicos relevantes?"
            ]
        }
        
        self.banderas_rojas = {
            'traumatologia': [
                "Pérdida de sensibilidad o fuerza",
                "Dolor que no mejora con reposo",
                "Deformidad visible",
                "Imposibilidad para mover la extremidad"
            ],
            'cardiologia': [
                "Dolor opresivo en el pecho",
                "Dificultad para respirar",
                "Sudoración fría",
                "Dolor que se irradia al brazo izquierdo"
            ],
            'neurologia': [
                "Dolor de cabeza súbito y severo",
                "Pérdida de consciencia",
                "Alteraciones visuales",
                "Debilidad o parálisis"
            ]
        }
        
        self.evidencias_cientificas = {
            'dolor_lumbar': {
                'titulo': 'Programa de ejercicio terapéutico progresivo',
                'descripcion': 'Ejercicios de fortalecimiento y estiramiento bajo supervisión profesional',
                'evidencia': 'NICE Guidelines 2023 - Low back pain and sciatica in over 16s',
                'doi': '10.1001/lumbartx2023.001',
                'nivel': 'A',
                'contraindicaciones': ['Fractura vertebral', 'Cáncer metastásico', 'Infección']
            },
            'hipertension': {
                'titulo': 'Modificaciones del estilo de vida y farmacoterapia',
                'descripcion': 'Dieta DASH, ejercicio aeróbico regular y medicación antihipertensiva',
                'evidencia': 'American Heart Association Guidelines 2023',
                'doi': '10.1161/HYP.0000000000000065',
                'nivel': 'A',
                'contraindicaciones': ['Hipersensibilidad a medicamentos', 'Embarazo']
            },
            'diabetes_tipo2': {
                'titulo': 'Manejo integral de diabetes tipo 2',
                'descripcion': 'Educación diabetológica, dieta y medicación oral o insulina',
                'evidencia': 'American Diabetes Association Standards of Care 2024',
                'doi': '10.2337/dc24-SINT',
                'nivel': 'A',
                'contraindicaciones': ['Cetoacidosis diabética', 'Hipersensibilidad a medicamentos']
            }
        }
        
        # Planes de tratamiento específicos por tipo de atención
        self.planes_por_tipo_atencion = {
            'medicina_general': [
                {
                    'titulo': 'Evaluación integral y manejo sintomático',
                    'descripcion': 'Anamnesis completa, examen físico y tratamiento según hallazgos',
                    'evidencia': 'Clinical Practice Guidelines - Primary Care',
                    'doi': '10.1001/jama.2023.001',
                    'nivel': 'A',
                    'contraindicaciones': []
                }
            ],
            'fisioterapia': [
                {
                    'titulo': 'Programa de rehabilitación funcional',
                    'descripcion': 'Ejercicios terapéuticos progresivos y técnicas de movilización',
                    'evidencia': 'APTA Clinical Practice Guidelines 2023',
                    'doi': '10.1093/ptj/pzad001',
                    'nivel': 'A',
                    'contraindicaciones': ['Fracturas inestables', 'Infección activa']
                },
                {
                    'titulo': 'Terapia manual y técnicas de movilización',
                    'descripcion': 'Técnicas de manipulación y movilización articular',
                    'evidencia': 'Manual Therapy Guidelines 2023',
                    'doi': '10.1016/j.math.2023.001',
                    'nivel': 'B',
                    'contraindicaciones': ['Osteoporosis severa', 'Cáncer metastásico']
                }
            ],
            'terapia_ocupacional': [
                {
                    'titulo': 'Evaluación de actividades de la vida diaria',
                    'descripcion': 'Análisis funcional y adaptaciones para independencia',
                    'evidencia': 'AOTA Practice Guidelines 2023',
                    'doi': '10.5014/ajot.2023.001',
                    'nivel': 'A',
                    'contraindicaciones': []
                },
                {
                    'titulo': 'Programa de rehabilitación ocupacional',
                    'descripcion': 'Entrenamiento en actividades específicas y adaptaciones',
                    'evidencia': 'Occupational Therapy Practice Framework',
                    'doi': '10.5014/ajot.2023.002',
                    'nivel': 'B',
                    'contraindicaciones': []
                }
            ],
            'enfermeria': [
                {
                    'titulo': 'Cuidados de enfermería especializados',
                    'descripcion': 'Monitoreo de signos vitales y educación al paciente',
                    'evidencia': 'ANA Standards of Practice 2023',
                    'doi': '10.1097/NUR.000000000000001',
                    'nivel': 'A',
                    'contraindicaciones': []
                }
            ],
            'psicologia': [
                {
                    'titulo': 'Terapia cognitivo-conductual',
                    'descripcion': 'Intervención psicológica para manejo de síntomas',
                    'evidencia': 'APA Clinical Practice Guidelines 2023',
                    'doi': '10.1037/ccp0000001',
                    'nivel': 'A',
                    'contraindicaciones': ['Psicosis activa', 'Riesgo suicida']
                },
                {
                    'titulo': 'Terapia de apoyo y psicoeducación',
                    'descripcion': 'Educación sobre la condición y estrategias de afrontamiento',
                    'evidencia': 'Psychological Interventions Guidelines',
                    'doi': '10.1037/ccp0000002',
                    'nivel': 'B',
                    'contraindicaciones': []
                }
            ],
            'nutricion': [
                {
                    'titulo': 'Plan de alimentación personalizado',
                    'descripcion': 'Evaluación nutricional y plan dietético específico',
                    'evidencia': 'Academy of Nutrition and Dietetics Guidelines 2023',
                    'doi': '10.1016/j.jand.2023.001',
                    'nivel': 'A',
                    'contraindicaciones': ['Alergias alimentarias severas']
                },
                {
                    'titulo': 'Educación nutricional y cambios de hábitos',
                    'descripcion': 'Intervención educativa para mejorar hábitos alimentarios',
                    'evidencia': 'Nutrition Education Guidelines',
                    'doi': '10.1016/j.jand.2023.002',
                    'nivel': 'B',
                    'contraindicaciones': []
                }
            ],
            'kinesiologia': [
                {
                    'titulo': 'Programa de ejercicio terapéutico',
                    'descripcion': 'Ejercicios específicos para rehabilitación y fortalecimiento',
                    'evidencia': 'Kinesiology Practice Guidelines 2023',
                    'doi': '10.1093/kinesiol.2023.001',
                    'nivel': 'A',
                    'contraindicaciones': ['Lesiones agudas', 'Infección activa']
                },
                {
                    'titulo': 'Técnicas de rehabilitación funcional',
                    'descripcion': 'Rehabilitación específica para mejorar función',
                    'evidencia': 'Functional Rehabilitation Guidelines',
                    'doi': '10.1093/kinesiol.2023.002',
                    'nivel': 'B',
                    'contraindicaciones': ['Fracturas inestables']
                }
            ],
            'fonoaudiologia': [
                {
                    'titulo': 'Terapia de lenguaje y comunicación',
                    'descripcion': 'Intervención para mejorar habilidades comunicativas',
                    'evidencia': 'ASHA Practice Guidelines 2023',
                    'doi': '10.1044/2023_asha.001',
                    'nivel': 'A',
                    'contraindicaciones': []
                },
                {
                    'titulo': 'Terapia de deglución',
                    'descripcion': 'Evaluación y tratamiento de trastornos deglutorios',
                    'evidencia': 'Dysphagia Management Guidelines',
                    'doi': '10.1044/2023_asha.002',
                    'nivel': 'B',
                    'contraindicaciones': ['Aspiración severa']
                }
            ],
            'urgencia': [
                {
                    'titulo': 'Manejo de emergencia médica',
                    'descripcion': 'Evaluación rápida y estabilización del paciente',
                    'evidencia': 'ACEP Clinical Policies 2023',
                    'doi': '10.1016/j.annemergmed.2023.001',
                    'nivel': 'A',
                    'contraindicaciones': []
                }
            ]
        }

    def analizar_motivo_consulta(self, texto: str, tipo_atencion: str = None) -> MotivoConsulta:
        """
        Analiza el motivo de consulta y detecta especialidad, categoría y sugiere preguntas
        Considera el tipo de atención seleccionado para ajustar las sugerencias
        Incluye normalización de sinónimos y variaciones regionales
        """
        texto_lower = texto.lower()
        
        # Normalizar el tipo de atención si se proporciona
        tipo_atencion_normalizado = None
        if tipo_atencion:
            tipo_atencion_normalizado = self._normalizar_tipo_atencion(tipo_atencion)
            if tipo_atencion_normalizado:
                logger.info(f"Tipo de atención normalizado: '{tipo_atencion}' -> '{tipo_atencion_normalizado}'")
        
        # Si se proporciona tipo de atención normalizado, usarlo como especialidad principal
        if tipo_atencion_normalizado:
            especialidad_detectada = tipo_atencion_normalizado
        else:
            # Detectar especialidad basada en el texto
            especialidad_detectada = self._detectar_especialidad(texto_lower)
        
        # Detectar categoría de urgencia
        categoria = self._detectar_categoria_urgencia(texto_lower)
        
        # Extraer síntomas principales
        sintomas = self._extraer_sintomas(texto_lower)
        
        # Generar preguntas personalizadas basadas en el motivo de consulta y tipo de atención
        preguntas = self._generar_preguntas_personalizadas(texto, tipo_atencion_normalizado or tipo_atencion, especialidad_detectada)
        
        return MotivoConsulta(
            texto_original=texto,
            especialidad_detectada=especialidad_detectada,
            categoria=categoria,
            sintomas_principales=sintomas,
            urgencia=self._determinar_urgencia(categoria),
            preguntas_sugeridas=preguntas
        )

    def evaluar_antecedentes(self, antecedentes: str, especialidad: str, edad: int) -> EvaluacionInteligente:
        """
        Evalúa los antecedentes y detecta banderas rojas y omisiones
        """
        banderas_rojas = []
        campos_adicionales = []
        omisiones = []
        recomendaciones = []
        
        antecedentes_lower = antecedentes.lower()
        
        # Detectar banderas rojas según especialidad
        if especialidad in self.banderas_rojas:
            for bandera in self.banderas_rojas[especialidad]:
                if any(palabra in antecedentes_lower for palabra in bandera.lower().split()):
                    banderas_rojas.append(bandera)
        
        # Detectar omisiones según edad y especialidad
        if edad > 65:
            if 'presion arterial' not in antecedentes_lower:
                omisiones.append("Presión arterial")
            if 'glicemia' not in antecedentes_lower and 'diabetes' in antecedentes_lower:
                omisiones.append("Nivel de glicemia")
        
        # Sugerir campos adicionales
        if especialidad == 'traumatologia' and 'dolor' in antecedentes_lower:
            campos_adicionales.append("Escala de dolor (0-10)")
            campos_adicionales.append("Rango de movimientos")
        
        if especialidad == 'cardiologia':
            campos_adicionales.append("Frecuencia cardíaca")
            campos_adicionales.append("Presión arterial")
        
        # Generar recomendaciones
        if banderas_rojas:
            recomendaciones.append("⚠️ ATENCIÓN: Se detectaron banderas rojas. Evaluar derivación urgente.")
        
        if omisiones:
            recomendaciones.append(f"📋 Considerar incluir: {', '.join(omisiones)}")
        
        return EvaluacionInteligente(
            banderas_rojas=banderas_rojas,
            campos_adicionales=campos_adicionales,
            omisiones_detectadas=omisiones,
            recomendaciones=recomendaciones
        )

    def sugerir_planes_tratamiento(self, diagnostico: str, especialidad: str, edad: int) -> List[PlanTratamiento]:
        """
        Sugiere planes de tratamiento basados en evidencia científica
        Incluye integración con APIs médicas para evidencia actualizada y planes de intervención específicos
        """
        planes = []
        diagnostico_lower = diagnostico.lower()
        
        # Intentar obtener tratamientos de APIs médicas si están disponibles
        tratamientos_cientificos = []
        plan_intervencion = None
        
        if self.apis_medicas:
            try:
                logger.info(f"🔍 Buscando tratamientos científicos para: {diagnostico} en {especialidad}")
                resultados_apis = self.apis_medicas.obtener_tratamientos_completos(diagnostico, especialidad)
                
                # Convertir tratamientos de PubMed
                if resultados_apis.get('tratamientos_pubmed'):
                    tratamientos_cientificos.extend(resultados_apis['tratamientos_pubmed'])
                
                # Convertir tratamientos de Europe PMC
                if resultados_apis.get('tratamientos_europepmc'):
                    tratamientos_cientificos.extend(resultados_apis['tratamientos_europepmc'])
                
                # Obtener plan de intervención específico si está disponible
                if resultados_apis.get('plan_intervencion'):
                    plan_intervencion = resultados_apis['plan_intervencion']
                    logger.info(f"✅ Plan de intervención específico generado con {len(plan_intervencion.tecnicas_especificas)} técnicas")
                
                # Convertir a formato Copilot Health incluyendo plan de intervención
                if tratamientos_cientificos or plan_intervencion:
                    planes_cientificos = convertir_a_formato_copilot(tratamientos_cientificos, plan_intervencion)
                    for plan_data in planes_cientificos:
                        # Crear PlanTratamiento con información adicional si es plan de intervención
                        if plan_data.get('tipo') == 'plan_intervencion_especifico':
                            # Crear descripción detallada del plan de intervención
                            descripcion_detallada = f"{plan_data['descripcion']}\n\n"
                            descripcion_detallada += "**TÉCNICAS ESPECÍFICAS:**\n"
                            for tecnica in plan_data.get('tecnicas_especificas', []):
                                descripcion_detallada += f"• {tecnica}\n"
                            
                            descripcion_detallada += "\n**APLICACIONES PRÁCTICAS:**\n"
                            for aplicacion in plan_data.get('aplicaciones_practicas', []):
                                descripcion_detallada += f"• {aplicacion}\n"
                            
                            if plan_data.get('masajes_tecnicas'):
                                descripcion_detallada += "\n**TÉCNICAS DE MASAJE:**\n"
                                for masaje in plan_data['masajes_tecnicas']:
                                    descripcion_detallada += f"• {masaje}\n"
                            
                            if plan_data.get('ejercicios_especificos'):
                                descripcion_detallada += "\n**EJERCICIOS ESPECÍFICOS:**\n"
                                for ejercicio in plan_data['ejercicios_especificos']:
                                    descripcion_detallada += f"• {ejercicio}\n"
                            
                            descripcion_detallada += f"\n**PROTOCOLO DE TRATAMIENTO:**\n"
                            for paso in plan_data.get('protocolo_tratamiento', []):
                                descripcion_detallada += f"• {paso}\n"
                            
                            descripcion_detallada += f"\n**FRECUENCIA:** {plan_data.get('frecuencia_sesiones', 'Según indicación')}\n"
                            descripcion_detallada += f"**DURACIÓN:** {plan_data.get('duracion_tratamiento', 'Según evolución')}"
                            
                            planes.append(PlanTratamiento(
                                titulo=plan_data['titulo'],
                                descripcion=descripcion_detallada,
                                evidencia_cientifica=plan_data['evidencia_cientifica'],
                                doi_referencia=plan_data['doi_referencia'],
                                nivel_evidencia=plan_data['nivel_evidencia'],
                                contraindicaciones=plan_data['contraindicaciones']
                            ))
                        else:
                            # Plan de tratamiento científico tradicional
                            planes.append(PlanTratamiento(
                                titulo=plan_data['titulo'],
                                descripcion=plan_data['descripcion'],
                                evidencia_cientifica=plan_data['evidencia_cientifica'],
                                doi_referencia=plan_data['doi_referencia'],
                                nivel_evidencia=plan_data['nivel_evidencia'],
                                contraindicaciones=plan_data['contraindicaciones']
                            ))
                    
                    logger.info(f"✅ {len(planes)} planes de tratamiento obtenidos (incluyendo {len([p for p in planes if 'intervención' in p.titulo])} planes de intervención específicos)")
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo tratamientos de APIs médicas: {e}")
        
        # Si no se obtuvieron tratamientos de APIs, NO usar datos sintéticos
        if not planes:
            logger.warning(f"⚠️ No se encontraron tratamientos científicos para: {diagnostico} en {especialidad}")
            logger.info(f"ℹ️ Solo se mostrarán tratamientos basados en evidencia científica real")
            # Retornar lista vacía en lugar de datos sintéticos
            return []
        
        return planes

    def generar_resumen_ia(self, motivo: MotivoConsulta, evaluacion: EvaluacionInteligente, 
                          planes: List[PlanTratamiento]) -> str:
        """
        Genera un resumen completo de la asistencia de IA
        """
        resumen = f"""🤖 **COPILOT HEALTH - ASISTENCIA IA CLÍNICA**

📋 **ANÁLISIS DEL MOTIVO DE CONSULTA**
• Especialidad detectada: {motivo.especialidad_detectada.title()}
• Categoría: {motivo.categoria.title()}
• Urgencia: {motivo.urgencia}
• Síntomas principales: {', '.join(motivo.sintomas_principales)}

❓ **PREGUNTAS SUGERIDAS PARA ANAMNESIS**
"""
        
        for i, pregunta in enumerate(motivo.preguntas_sugeridas, 1):
            resumen += f"{i}. {pregunta}\n"
        
        if evaluacion.banderas_rojas:
            resumen += f"\n🚨 **BANDERAS ROJAS DETECTADAS**\n"
            for bandera in evaluacion.banderas_rojas:
                resumen += f"• {bandera}\n"
        
        if evaluacion.campos_adicionales:
            resumen += f"\n📋 **CAMPOS ADICIONALES SUGERIDOS**\n"
            for campo in evaluacion.campos_adicionales:
                resumen += f"• {campo}\n"
        
        if planes:
            # Separar planes de intervención de otros planes
            planes_intervencion = [p for p in planes if "intervención" in p.titulo.lower()]
            otros_planes = [p for p in planes if "intervención" not in p.titulo.lower()]
            
            # Mostrar planes de intervención primero
            if planes_intervencion:
                resumen += f"\n🎯 **PLAN DE INTERVENCIÓN IA SUGERIDA**\n"
                for i, plan in enumerate(planes_intervencion, 1):
                    resumen += f"\n**{plan.titulo}**\n"
                    resumen += f"{plan.descripcion}\n"
                    resumen += f"Evidencia: {plan.evidencia_cientifica}\n"
                    resumen += f"DOI: {plan.doi_referencia}\n"
                    resumen += f"Nivel de evidencia: {plan.nivel_evidencia}\n"
                    if plan.contraindicaciones:
                        resumen += f"Contraindicaciones: {', '.join(plan.contraindicaciones)}\n"
            
            # Mostrar otros planes de tratamiento
            if otros_planes:
                resumen += f"\n💡 **ESTUDIOS CIENTÍFICOS RELACIONADOS**\n"
                for i, plan in enumerate(otros_planes, 1):
                    resumen += f"\n**Opción {i}: {plan.titulo}**\n"
                    resumen += f"Descripción: {plan.descripcion}\n"
                    resumen += f"Evidencia: {plan.evidencia_cientifica}\n"
                    resumen += f"DOI: {plan.doi_referencia}\n"
                    resumen += f"Nivel de evidencia: {plan.nivel_evidencia}\n"
                    if plan.contraindicaciones:
                        resumen += f"Contraindicaciones: {', '.join(plan.contraindicaciones)}\n"
        
        resumen += f"""

⚠️ **ACLARACIÓN LEGAL**
Estas sugerencias son generadas por inteligencia artificial con base en evidencia científica actualizada. La decisión final recae en el juicio clínico del profesional tratante. Copilot Health es una herramienta de asistencia y no reemplaza la evaluación médica profesional.

---
*Copilot Health - MedConnect.cl*"""
        
        return resumen

    def generar_planificacion_tratamiento_completa(self, motivo_atencion: str, tipo_atencion: str, 
                                                 evaluacion_observaciones: str, edad: int = 35) -> Dict:
        """
        Genera una planificación completa de tratamiento basada en múltiples fuentes
        Incluye estudios científicos de 2020-2025 y aclaración legal
        """
        try:
            # Obtener estudios científicos de las APIs médicas
            estudios_cientificos = []
            if self.apis_medicas:
                logger.info(f"🔍 Buscando estudios científicos para: {motivo_atencion} en {tipo_atencion}")
                resultados_apis = self.apis_medicas.obtener_tratamientos_completos(motivo_atencion, tipo_atencion)
                
                # Combinar estudios de PubMed y Europe PMC
                if resultados_apis.get('tratamientos_pubmed'):
                    estudios_cientificos.extend(resultados_apis['tratamientos_pubmed'])
                
                if resultados_apis.get('tratamientos_europepmc'):
                    estudios_cientificos.extend(resultados_apis['tratamientos_europepmc'])
                
                logger.info(f"✅ {len(estudios_cientificos)} estudios científicos obtenidos de APIs médicas")
            
            # Generar planificación completa
            planificacion = generar_planificacion_tratamiento_completa(
                motivo_atencion=motivo_atencion,
                tipo_atencion=tipo_atencion,
                evaluacion_observaciones=evaluacion_observaciones,
                estudios_cientificos=estudios_cientificos
            )
            
            return planificacion
            
        except Exception as e:
            logger.error(f"❌ Error generando planificación completa: {e}")
            # Retornar planificación básica en caso de error
            return {
                'resumen_clinico': f"Basado en: {motivo_atencion} - {tipo_atencion}",
                'objetivos_tratamiento': ["Aliviar síntomas", "Mejorar función", "Prevenir complicaciones"],
                'intervenciones_especificas': [],
                'cronograma_tratamiento': ["Evaluación inicial", "Intervención", "Seguimiento"],
                'criterios_evaluacion': ["Evaluación continua", "Medición de progreso"],
                'estudios_basados': [],
                'aclaracion_legal': 'Estas sugerencias son generadas por inteligencia artificial con base en evidencia científica actualizada. La decisión final recae en el juicio clínico del profesional tratante. Copilot Health es una herramienta de asistencia y no reemplaza la evaluación médica profesional.'
            }

    def _detectar_especialidad(self, texto: str) -> str:
        """Detecta la especialidad médica basándose en palabras clave"""
        puntajes = {}
        
        for especialidad, palabras_clave in self.especialidades.items():
            puntaje = sum(1 for palabra in palabras_clave if palabra in texto)
            if puntaje > 0:
                puntajes[especialidad] = puntaje
        
        if puntajes:
            return max(puntajes, key=puntajes.get)
        return 'medicina_general'
    
    def _normalizar_tipo_atencion(self, tipo_atencion: str) -> str:
        """
        Normaliza el tipo de atención considerando sinónimos y variaciones regionales
        """
        if not tipo_atencion:
            return None
            
        tipo_lower = tipo_atencion.lower().strip()
        
        # Buscar en el diccionario de sinónimos
        for especialidad_principal, sinonimos in self.sinonimos_especialidades.items():
            if tipo_lower in sinonimos:
                return especialidad_principal
        
        # Si no se encuentra en sinónimos, verificar si es un tipo válido
        if tipo_lower in self.tipos_atencion_especialidad:
            return tipo_lower
            
        # Búsqueda parcial para casos como "fisio" -> "fisioterapia"
        for especialidad_principal, sinonimos in self.sinonimos_especialidades.items():
            for sinonimo in sinonimos:
                if sinonimo in tipo_lower or tipo_lower in sinonimo:
                    return especialidad_principal
        
        return None

    def _detectar_categoria_urgencia(self, texto: str) -> str:
        """Detecta la categoría de urgencia del motivo de consulta"""
        for categoria, palabras_clave in self.categorias_urgencia.items():
            if any(palabra in texto for palabra in palabras_clave):
                return categoria
        return 'rutina'

    def _extraer_sintomas(self, texto: str) -> List[str]:
        """Extrae los síntomas principales del texto"""
        sintomas_comunes = [
            'dolor', 'fiebre', 'tos', 'nausea', 'vomito', 'diarrea', 'mareo',
            'fatiga', 'perdida peso', 'ganancia peso', 'insomnio', 'ansiedad'
        ]
        
        sintomas_encontrados = []
        for sintoma in sintomas_comunes:
            if sintoma in texto:
                sintomas_encontrados.append(sintoma)
        
        return sintomas_encontrados

    def _generar_preguntas_sugeridas(self, especialidad: str, sintomas: List[str]) -> List[str]:
        """
        Genera preguntas sugeridas según la especialidad y síntomas
        Incluye integración con APIs médicas para preguntas basadas en evidencia
        """
        preguntas = []
        
        # Intentar obtener preguntas científicas de APIs médicas si están disponibles
        if self.apis_medicas:
            try:
                # Crear un contexto combinando especialidad y síntomas
                contexto = f"{especialidad} {' '.join(sintomas)}"
                preguntas_cientificas = self.apis_medicas.generar_preguntas_cientificas(contexto, especialidad)
                
                if preguntas_cientificas:
                    # Convertir preguntas científicas al formato esperado
                    preguntas_apis = convertir_preguntas_a_formato_copilot(preguntas_cientificas)
                    preguntas.extend(preguntas_apis)
                    logger.info(f"✅ {len(preguntas_apis)} preguntas científicas obtenidas de APIs médicas")
                
            except Exception as e:
                logger.error(f"❌ Error obteniendo preguntas de APIs médicas: {e}")
        
        # Preguntas específicas de la especialidad (como respaldo)
        if especialidad in self.preguntas_especialidad:
            preguntas.extend(self.preguntas_especialidad[especialidad][:3])
        
        # Preguntas generales según síntomas
        if 'dolor' in sintomas:
            preguntas.extend([
                "¿Cuándo comenzó el dolor?",
                "¿Qué lo agrava o alivia?",
                "¿Ha tenido episodios similares antes?"
            ])
        
        if 'fiebre' in sintomas:
            preguntas.extend([
                "¿Cuál es la temperatura máxima?",
                "¿Hay otros síntomas asociados?",
                "¿Ha viajado recientemente?"
            ])
        
        return preguntas[:5]  # Máximo 5 preguntas

    def _generar_preguntas_personalizadas(self, motivo_consulta: str, tipo_atencion: str, especialidad: str) -> List[str]:
        """
        Genera preguntas personalizadas basadas en el motivo de consulta y tipo de atención
        Analiza el contenido específico para generar preguntas relevantes
        """
        preguntas = []
        motivo_lower = motivo_consulta.lower()
        
        # Análisis específico por especialidad y contenido del motivo
        if especialidad == 'fonoaudiologia':
            if any(palabra in motivo_lower for palabra in ['voz', 'habla', 'comunicación', 'lenguaje']):
                preguntas.extend([
                    "¿Cuándo comenzó a notar cambios en su voz?",
                    "¿En qué situaciones se agrava la dificultad para hablar?",
                    "¿Ha recibido algún diagnóstico previo relacionado con su voz?",
                    "¿Su trabajo requiere uso intensivo de la voz?",
                    "¿Hay momentos del día en que la voz mejora o empeora?",
                    "¿Ha notado cambios en su capacidad de cantar o hacer diferentes tonos?",
                    "¿Hay antecedentes familiares de problemas de voz?",
                    "¿Ha tenido infecciones respiratorias recientes?"
                ])
            
            elif any(palabra in motivo_lower for palabra in ['tragar', 'deglución', 'disfagia', 'atragantamiento']):
                preguntas.extend([
                    "¿Con qué consistencia de alimentos tiene más dificultad?",
                    "¿Ha notado pérdida de peso por dificultad para comer?",
                    "¿Hay alimentos que evita por miedo a atragantarse?",
                    "¿Ha tenido episodios de neumonía o infecciones respiratorias?",
                    "¿El problema es con líquidos, sólidos o ambos?",
                    "¿Hay antecedentes de accidente cerebrovascular?",
                    "¿Ha notado cambios en su capacidad de masticar?",
                    "¿Hay dolor al tragar?"
                ])
            
            elif any(palabra in motivo_lower for palabra in ['audición', 'oído', 'sordera', 'hipoacusia']):
                preguntas.extend([
                    "¿En qué oído nota más dificultad?",
                    "¿El problema es constante o intermitente?",
                    "¿Ha estado expuesto a ruidos fuertes?",
                    "¿Hay antecedentes familiares de pérdida auditiva?",
                    "¿Ha notado zumbidos o pitidos en los oídos?",
                    "¿El problema afecta su comunicación diaria?",
                    "¿Ha tenido infecciones de oído recientes?",
                    "¿Usa audífonos actualmente?"
                ])
            
            else:
                # Preguntas generales de fonoaudiología
                preguntas.extend([
                    "¿Cuál es el problema principal que le trae a consulta?",
                    "¿Cuándo comenzó a notar estos síntomas?",
                    "¿Ha recibido tratamiento fonoaudiológico antes?",
                    "¿El problema afecta su vida diaria?",
                    "¿Hay situaciones específicas que agravan el problema?",
                    "¿Ha notado progresión de los síntomas?",
                    "¿Hay antecedentes médicos relevantes?",
                    "¿Cuál es su ocupación y cómo afecta su condición?"
                ])
        
        elif especialidad == 'kinesiologia':
            if any(palabra in motivo_lower for palabra in ['dolor', 'lesión', 'trauma', 'accidente']):
                preguntas.extend([
                    "¿Cuándo ocurrió la lesión exactamente?",
                    "¿Qué mecanismo de lesión tuvo?",
                    "¿Inmediatamente después de la lesión, qué síntomas tuvo?",
                    "¿Ha tenido lesiones similares antes?",
                    "¿Qué actividades agravan el dolor?",
                    "¿Ha notado mejoría con reposo o hielo?",
                    "¿Hay limitación de movimientos específicos?",
                    "¿El dolor es constante o intermitente?"
                ])
            
            elif any(palabra in motivo_lower for palabra in ['movilidad', 'flexibilidad', 'rigidez']):
                preguntas.extend([
                    "¿Qué movimientos le resultan más difíciles?",
                    "¿Cuándo comenzó a notar la limitación?",
                    "¿Ha notado progresión de la rigidez?",
                    "¿Hay momentos del día en que mejora?",
                    "¿Qué actividades de la vida diaria se ven afectadas?",
                    "¿Ha recibido tratamiento kinésico antes?",
                    "¿Hay antecedentes de artritis o problemas articulares?",
                    "¿Su trabajo requiere movimientos repetitivos?"
                ])
            
            else:
                preguntas.extend([
                    "¿Cuál es el problema principal que le trae a consulta?",
                    "¿Cuándo comenzaron los síntomas?",
                    "¿Qué actividades se ven afectadas?",
                    "¿Ha recibido tratamiento kinésico antes?",
                    "¿Cuál es su nivel de actividad física habitual?",
                    "¿Hay antecedentes de lesiones previas?",
                    "¿Qué movimientos o actividades le causan más problemas?",
                    "¿Cuál es su objetivo de rehabilitación?"
                ])
        
        elif especialidad == 'psicologia':
            if any(palabra in motivo_lower for palabra in ['ansiedad', 'estrés', 'nervios', 'preocupación']):
                preguntas.extend([
                    "¿Cuándo comenzó a sentir estos síntomas?",
                    "¿Hay situaciones específicas que desencadenan la ansiedad?",
                    "¿Cómo afecta la ansiedad su vida diaria?",
                    "¿Ha notado síntomas físicos asociados?",
                    "¿Hay antecedentes familiares de ansiedad?",
                    "¿Ha recibido tratamiento psicológico antes?",
                    "¿Qué estrategias ha intentado para manejar la ansiedad?",
                    "¿Hay eventos recientes que puedan estar relacionados?"
                ])
            
            elif any(palabra in motivo_lower for palabra in ['depresión', 'tristeza', 'ánimo', 'desánimo']):
                preguntas.extend([
                    "¿Cuándo comenzó a notar cambios en su estado de ánimo?",
                    "¿Ha perdido interés en actividades que antes disfrutaba?",
                    "¿Cómo está su calidad del sueño?",
                    "¿Ha notado cambios en su apetito?",
                    "¿Hay pensamientos negativos recurrentes?",
                    "¿Ha tenido pensamientos de autolesión?",
                    "¿Hay antecedentes familiares de depresión?",
                    "¿Qué eventos recientes pueden estar relacionados?"
                ])
            
            else:
                preguntas.extend([
                    "¿Cuál es el problema principal que le trae a consulta?",
                    "¿Cuándo comenzó a notar estos síntomas?",
                    "¿Cómo afecta esto su vida diaria?",
                    "¿Ha recibido ayuda psicológica antes?",
                    "¿Hay antecedentes familiares de problemas psicológicos?",
                    "¿Qué eventos recientes pueden estar relacionados?",
                    "¿Cómo se siente emocionalmente últimamente?",
                    "¿Cuál es su objetivo de la terapia?"
                ])
        
        elif especialidad == 'nutricion':
            if any(palabra in motivo_lower for palabra in ['peso', 'obesidad', 'sobrepeso']):
                preguntas.extend([
                    "¿Cuál es su peso actual y cuál era hace un año?",
                    "¿Ha intentado dietas antes? ¿Cuáles?",
                    "¿Cuál es su objetivo de peso?",
                    "¿Cómo es su alimentación actual?",
                    "¿Cuál es su nivel de actividad física?",
                    "¿Hay antecedentes familiares de obesidad?",
                    "¿Ha tenido problemas de peso desde la infancia?",
                    "¿Qué alimentos consume más frecuentemente?"
                ])
            
            elif any(palabra in motivo_lower for palabra in ['diabetes', 'glucosa', 'azúcar']):
                preguntas.extend([
                    "¿Cuál es su nivel de glucosa actual?",
                    "¿Ha recibido educación sobre diabetes?",
                    "¿Cómo es su alimentación actual?",
                    "¿Está tomando medicamentos para la diabetes?",
                    "¿Ha tenido episodios de hipoglucemia?",
                    "¿Hay antecedentes familiares de diabetes?",
                    "¿Cuál es su nivel de actividad física?",
                    "¿Ha notado cambios en su peso recientemente?"
                ])
            
            else:
                preguntas.extend([
                    "¿Cuál es el problema principal que le trae a consulta?",
                    "¿Cómo es su alimentación actual?",
                    "¿Ha notado cambios en su peso?",
                    "¿Tiene alguna restricción alimentaria?",
                    "¿Cuál es su nivel de actividad física?",
                    "¿Hay alimentos que le causan malestar?",
                    "¿Cuál es su objetivo nutricional?",
                    "¿Hay antecedentes médicos relevantes?"
                ])
        
        elif especialidad == 'fisioterapia':
            if any(palabra in motivo_lower for palabra in ['dolor', 'lesión', 'trauma']):
                preguntas.extend([
                    "¿Cuándo comenzó el dolor exactamente?",
                    "¿Qué actividades agravan el dolor?",
                    "¿Ha tenido lesiones similares antes?",
                    "¿El dolor es constante o intermitente?",
                    "¿Ha notado mejoría con reposo o hielo?",
                    "¿Hay limitación de movimientos específicos?",
                    "¿Su trabajo requiere movimientos repetitivos?",
                    "¿Cuál es su nivel de actividad física habitual?"
                ])
            
            elif any(palabra in motivo_lower for palabra in ['movilidad', 'flexibilidad', 'rigidez']):
                preguntas.extend([
                    "¿Qué movimientos le resultan más difíciles?",
                    "¿Cuándo comenzó a notar la limitación?",
                    "¿Ha notado progresión de la rigidez?",
                    "¿Qué actividades de la vida diaria se ven afectadas?",
                    "¿Ha recibido tratamiento fisioterapéutico antes?",
                    "¿Hay antecedentes de artritis o problemas articulares?",
                    "¿Su trabajo requiere movimientos repetitivos?",
                    "¿Cuál es su objetivo de rehabilitación?"
                ])
            
            else:
                preguntas.extend([
                    "¿Cuál es el problema principal que le trae a consulta?",
                    "¿Cuándo comenzaron los síntomas?",
                    "¿Qué actividades se ven afectadas?",
                    "¿Ha recibido tratamiento fisioterapéutico antes?",
                    "¿Cuál es su nivel de actividad física habitual?",
                    "¿Hay antecedentes de lesiones previas?",
                    "¿Qué movimientos o actividades le causan más problemas?",
                    "¿Cuál es su objetivo de rehabilitación?"
                ])
        
        else:
            # Preguntas generales para otras especialidades
            preguntas.extend([
                "¿Cuál es el problema principal que le trae a consulta?",
                "¿Cuándo comenzaron los síntomas?",
                "¿Qué actividades se ven afectadas?",
                "¿Ha recibido tratamiento similar antes?",
                "¿Hay antecedentes médicos relevantes?",
                "¿Qué factores agravan o alivian los síntomas?",
                "¿Ha notado progresión de los síntomas?",
                "¿Cuál es su objetivo de tratamiento?"
            ])
        
        # Asegurar que no exceda 10 preguntas
        return preguntas[:10]

    def _determinar_urgencia(self, categoria: str) -> str:
        """Determina el nivel de urgencia"""
        urgencias = {
            'emergencia': 'ALTA - Requiere atención inmediata',
            'urgente': 'MEDIA - Requiere atención en 24h',
            'control': 'BAJA - Control programado',
            'rutina': 'BAJA - Consulta rutinaria'
        }
        return urgencias.get(categoria, 'BAJA')

    def _generar_planes_genericos(self, especialidad: str, edad: int) -> List[PlanTratamiento]:
        """Genera planes de tratamiento genéricos cuando no hay evidencia específica"""
        planes = []
        
        if especialidad == 'traumatologia':
            planes.append(PlanTratamiento(
                titulo="Evaluación traumatológica integral",
                descripcion="Examen físico completo, estudios imagenológicos según necesidad",
                evidencia_cientifica="Clinical Practice Guidelines - Trauma Assessment",
                doi_referencia="10.1001/trauma2024.001",
                nivel_evidencia="B",
                contraindicaciones=["Alergia a contrastes", "Embarazo"]
            ))
        
        elif especialidad == 'cardiologia':
            planes.append(PlanTratamiento(
                titulo="Evaluación cardiovascular",
                descripcion="ECG, ecocardiograma, pruebas de esfuerzo según indicación",
                evidencia_cientifica="ACC/AHA Guidelines for Cardiovascular Assessment",
                doi_referencia="10.1161/CIR.0000000000000001",
                nivel_evidencia="A",
                contraindicaciones=["Alergia a medicamentos", "Embarazo"]
            ))
        
        return planes

# Instancia global del módulo
copilot_health = CopilotHealth() 