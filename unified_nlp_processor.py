#!/usr/bin/env python3
"""
Sistema Unificado de Procesamiento NLP Médico
Consolida Medical NLP Processor + Clinical Pattern Analyzer
"""

import re
import logging
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntencionClinica(Enum):
    """Tipos de intención clínica"""

    TRATAMIENTO = "tratamiento"
    DIAGNOSTICO = "diagnostico"
    PRONOSTICO = "pronostico"
    PREVENCION = "prevencion"
    REHABILITACION = "rehabilitacion"
    EVALUACION = "evaluacion"
    GENERAL = "general"


@dataclass
class SintomaExtraido:
    """Estructura para síntomas extraídos"""

    sintoma: str
    localizacion: str
    intensidad: Optional[str] = None
    frecuencia: Optional[str] = None
    duracion: Optional[str] = None
    agravantes: List[str] = None
    mejorantes: List[str] = None
    confianza: float = 0.0
    patologias_asociadas: List[str] = None
    escalas_recomendadas: List[str] = None


@dataclass
class PalabraClave:
    """Representa una palabra clave identificada"""

    palabra: str
    categoria: str
    intensidad: float  # 0.0 a 1.0
    patologias_asociadas: List[str]
    escalas_evaluacion: List[str]
    preguntas_sugeridas: List[str]


@dataclass
class PatologiaIdentificada:
    """Representa una patología identificada"""

    nombre: str
    confianza: float  # 0.0 a 1.0
    sintomas_asociados: List[str]
    escalas_recomendadas: List[str]
    terminos_busqueda: List[str]


@dataclass
class EscalaEvaluacion:
    """Representa una escala de evaluación recomendada"""

    nombre: str
    descripcion: str
    aplicacion: str
    puntuacion: str
    preguntas: List[str]


@dataclass
class ConsultaProcesada:
    """Estructura unificada para consulta procesada"""

    intencion: IntencionClinica
    sintomas: List[SintomaExtraido]
    actividades_afectadas: List[str]
    terminos_busqueda: List[str]
    especialidad: str
    edad: Optional[int] = None
    genero: Optional[str] = None
    palabras_clave: List[PalabraClave] = None
    patologias_identificadas: List[PatologiaIdentificada] = None
    escalas_recomendadas: List[EscalaEvaluacion] = None
    preguntas_evaluacion: List[str] = None
    confianza_global: float = 0.0


@dataclass
class AnalisisCompleto:
    """Resultado del análisis completo unificado"""

    consulta_procesada: ConsultaProcesada
    palabras_clave: List[PalabraClave]
    patologias_identificadas: List[PatologiaIdentificada]
    escalas_recomendadas: List[EscalaEvaluacion]
    terminos_busqueda_mejorados: List[str]
    preguntas_evaluacion: List[str]
    confianza_global: float
    tiempo_procesamiento: float


class UnifiedNLPProcessor:
    """Sistema unificado de procesamiento NLP médico"""

    def __init__(self):
        logger.info("🧠 Inicializando Sistema Unificado de Procesamiento NLP")

        # Patrones de reconocimiento para síntomas
        self.patrones_sintomas = {
            "dolor": [
                r"dolor\s+(?:en|del|de)\s+(\w+)",
                r"duele\s+(?:el|la|los|las)\s+(\w+)",
                r"me\s+duele\s+(?:el|la|los|las)\s+(\w+)",
                r"dolor\s+(\w+)",
                r"(\w+)\s+duele",
            ],
            "limitacion": [
                r"no\s+puedo\s+(\w+)",
                r"no\s+puede\s+(\w+)",
                r"dificultad\s+(?:para|en)\s+(\w+)",
                r"problema\s+(?:para|en)\s+(\w+)",
                r"limitacion\s+(?:para|en)\s+(\w+)",
            ],
            "actividad": [
                r"(\w+)\s+(?:causa|causan)\s+dolor",
                r"dolor\s+(?:al|cuando)\s+(\w+)",
                r"(\w+)\s+mejora\s+el\s+dolor",
                r"(\w+)\s+empeora\s+el\s+dolor",
            ],
        }

        # Mapeo de localizaciones anatómicas
        self.localizaciones = {
            "hombro": "shoulder",
            "brazo": "arm",
            "codo": "elbow",
            "muñeca": "wrist",
            "mano": "hand",
            "cuello": "neck",
            "espalda": "back",
            "columna": "spine",
            "cadera": "hip",
            "rodilla": "knee",
            "tobillo": "ankle",
            "pie": "foot",
            "pierna": "leg",
            "cabeza": "head",
            "pecho": "chest",
            "abdomen": "abdomen",
            "lumbar": "lumbar",
            "cervical": "cervical",
            "dorsal": "dorsal",
        }

        # Mapeo de actividades físicas
        self.actividades = {
            "correr": "running",
            "caminar": "walking",
            "saltar": "jumping",
            "levantar": "lifting",
            "agacharse": "bending",
            "girar": "turning",
            "estirar": "stretching",
            "sentarse": "sitting",
            "pararse": "standing",
            "subir": "climbing",
            "bajar": "descending",
        }

        # Cargar bases de datos
        self.palabras_clave_db = self._load_palabras_clave()
        self.patologias_db = self._load_patologias()
        self.escalas_db = self._load_escalas_evaluacion()
        self.sintomas_db = self._load_sintomas()

        # Patrones de intensidad
        self.patrones_intensidad = {
            "leve": ["leve", "ligero", "suave", "poco"],
            "moderado": ["moderado", "medio", "regular"],
            "severo": ["severo", "fuerte", "intenso", "agudo", "grave"],
        }

        # Patrones de frecuencia
        self.patrones_frecuencia = {
            "constante": ["constante", "continuo", "siempre"],
            "intermitente": ["intermitente", "ocasional", "a veces"],
            "diario": ["diario", "cada día", "todos los días"],
        }

        logger.info("✅ Sistema Unificado de Procesamiento NLP inicializado")

    def _load_palabras_clave(self) -> Dict[str, Dict]:
        """Carga la base de datos de palabras clave"""
        return {
            # DOLOR
            "dolor": {
                "categoria": "sintoma_principal",
                "intensidad": 0.9,
                "patologias_asociadas": ["dolor_agudo", "dolor_cronico", "inflamacion"],
                "escalas_evaluacion": ["EVA", "Escala_Numerica", "Escala_Verbal"],
                "preguntas_sugeridas": [
                    "¿En qué escala de 0 a 10 calificaría el dolor?",
                    "¿El dolor es constante o intermitente?",
                    "¿Qué factores agravan el dolor?",
                    "¿Qué factores alivian el dolor?",
                ],
            },
            "molestia": {
                "categoria": "sintoma_secundario",
                "intensidad": 0.6,
                "patologias_asociadas": ["disconfort", "irritacion"],
                "escalas_evaluacion": ["EVA", "Escala_Verbal"],
                "preguntas_sugeridas": [
                    "¿Cómo describiría la molestia?",
                    "¿Es tolerable o interfiere con sus actividades?",
                ],
            },
            "ardor": {
                "categoria": "sintoma_especifico",
                "intensidad": 0.8,
                "patologias_asociadas": ["quemadura", "irritacion", "inflamacion"],
                "escalas_evaluacion": ["EVA", "Escala_Verbal"],
                "preguntas_sugeridas": [
                    "¿En qué escala de 0 a 10 calificaría el ardor?",
                    "¿El ardor es superficial o profundo?",
                ],
            },
            # MOVIMIENTO
            "rigidez": {
                "categoria": "sintoma_movimiento",
                "intensidad": 0.7,
                "patologias_asociadas": ["artritis", "artrosis", "contractura"],
                "escalas_evaluacion": ["Escala_Rigidez", "ROM"],
                "preguntas_sugeridas": [
                    "¿En qué momento del día es peor la rigidez?",
                    "¿Cuánto tiempo dura la rigidez?",
                    "¿La rigidez mejora con el movimiento?",
                ],
            },
            "debilidad": {
                "categoria": "sintoma_muscular",
                "intensidad": 0.8,
                "patologias_asociadas": ["atrofia", "lesion_nerviosa", "mialgia"],
                "escalas_evaluacion": ["Escala_Fuerza", "MMT"],
                "preguntas_sugeridas": [
                    "¿En qué actividades nota la debilidad?",
                    "¿La debilidad es progresiva?",
                    "¿Hay pérdida de masa muscular?",
                ],
            },
            # FUNCIONALIDAD
            "limitacion": {
                "categoria": "sintoma_funcional",
                "intensidad": 0.8,
                "patologias_asociadas": ["discapacidad", "lesion", "dolor_cronico"],
                "escalas_evaluacion": ["DASH", "QuickDASH", "SF-36"],
                "preguntas_sugeridas": [
                    "¿Qué actividades específicas no puede realizar?",
                    "¿Cómo afecta esto su vida diaria?",
                    "¿Ha tenido que modificar sus actividades?",
                ],
            },
            "inestabilidad": {
                "categoria": "sintoma_equilibrio",
                "intensidad": 0.9,
                "patologias_asociadas": [
                    "lesion_ligamentosa",
                    "propriocepcion",
                    "neurologico",
                ],
                "escalas_evaluacion": ["Berg_Balance", "TUG"],
                "preguntas_sugeridas": [
                    "¿En qué situaciones nota la inestabilidad?",
                    "¿Ha tenido caídas?",
                    "¿La inestabilidad es constante o intermitente?",
                ],
            },
        }

    def _load_patologias(self) -> Dict[str, Dict]:
        """Carga la base de datos de patologías"""
        return {
            "dolor_lumbar": {
                "confianza": 0.9,
                "sintomas_asociados": [
                    "dolor espalda baja",
                    "rigidez lumbar",
                    "limitacion movimiento",
                ],
                "escalas_recomendadas": ["Oswestry", "Roland-Morris", "EVA"],
                "terminos_busqueda": ["low back pain", "lumbar pain", "back pain"],
            },
            "dolor_cervical": {
                "confianza": 0.9,
                "sintomas_asociados": [
                    "dolor cuello",
                    "rigidez cervical",
                    "dolor cabeza",
                ],
                "escalas_recomendadas": ["NDI", "EVA", "ROM"],
                "terminos_busqueda": ["neck pain", "cervical pain", "cervicalgia"],
            },
            "dolor_hombro": {
                "confianza": 0.9,
                "sintomas_asociados": [
                    "dolor hombro",
                    "limitacion movimiento",
                    "dolor nocturno",
                ],
                "escalas_recomendadas": ["DASH", "QuickDASH", "EVA"],
                "terminos_busqueda": [
                    "shoulder pain",
                    "rotator cuff",
                    "frozen shoulder",
                ],
            },
            "dolor_rodilla": {
                "confianza": 0.9,
                "sintomas_asociados": ["dolor rodilla", "inestabilidad", "crujidos"],
                "escalas_recomendadas": ["KOOS", "Lysholm", "EVA"],
                "terminos_busqueda": ["knee pain", "osteoarthritis knee", "meniscus"],
            },
            "artritis": {
                "confianza": 0.8,
                "sintomas_asociados": ["rigidez", "dolor articular", "inflamacion"],
                "escalas_recomendadas": ["DAS28", "HAQ", "EVA"],
                "terminos_busqueda": [
                    "arthritis",
                    "rheumatoid arthritis",
                    "osteoarthritis",
                ],
            },
            "fibromialgia": {
                "confianza": 0.8,
                "sintomas_asociados": ["dolor generalizado", "fatiga", "rigidez"],
                "escalas_recomendadas": ["FIQ", "EVA", "SF-36"],
                "terminos_busqueda": ["fibromyalgia", "chronic pain", "fatigue"],
            },
        }

    def _load_escalas_evaluacion(self) -> Dict[str, Dict]:
        """Carga la base de datos de escalas de evaluación"""
        return {
            "EVA": {
                "descripcion": "Escala Visual Analógica del Dolor",
                "aplicacion": "Evaluación de intensidad del dolor",
                "puntuacion": "0-10",
                "preguntas": [
                    "¿En qué escala de 0 a 10 calificaría su dolor?",
                    "0 = Sin dolor, 10 = Dolor máximo imaginable",
                ],
            },
            "DASH": {
                "descripcion": "Disabilities of the Arm, Shoulder and Hand",
                "aplicacion": "Evaluación funcional de extremidad superior",
                "puntuacion": "0-100",
                "preguntas": [
                    "¿Qué tan difícil es realizar actividades con su brazo/hombro?",
                    "30 preguntas sobre actividades diarias",
                ],
            },
            "Oswestry": {
                "descripcion": "Oswestry Disability Index",
                "aplicacion": "Evaluación funcional de dolor lumbar",
                "puntuacion": "0-100%",
                "preguntas": [
                    "¿Cómo afecta el dolor lumbar sus actividades?",
                    "10 secciones sobre diferentes actividades",
                ],
            },
            "NDI": {
                "descripcion": "Neck Disability Index",
                "aplicacion": "Evaluación funcional de dolor cervical",
                "puntuacion": "0-50",
                "preguntas": [
                    "¿Cómo afecta el dolor cervical sus actividades?",
                    "10 preguntas sobre actividades diarias",
                ],
            },
            "KOOS": {
                "descripcion": "Knee Injury and Osteoarthritis Outcome Score",
                "aplicacion": "Evaluación funcional de rodilla",
                "puntuacion": "0-100",
                "preguntas": [
                    "¿Cómo afecta el problema de rodilla sus actividades?",
                    "42 preguntas en 5 subescalas",
                ],
            },
        }

    def _load_sintomas(self) -> Dict[str, Dict]:
        """Carga la base de datos de síntomas"""
        return {
            "dolor": {
                "categoria": "sintoma_principal",
                "intensidad_base": 0.9,
                "patologias": ["dolor_agudo", "dolor_cronico", "inflamacion"],
                "escalas": ["EVA", "Escala_Numerica"],
            },
            "rigidez": {
                "categoria": "sintoma_movimiento",
                "intensidad_base": 0.7,
                "patologias": ["artritis", "artrosis", "contractura"],
                "escalas": ["Escala_Rigidez", "ROM"],
            },
            "debilidad": {
                "categoria": "sintoma_muscular",
                "intensidad_base": 0.8,
                "patologias": ["atrofia", "lesion_nerviosa"],
                "escalas": ["Escala_Fuerza", "MMT"],
            },
        }

    def procesar_consulta_completa(
        self, texto: str, edad: Optional[int] = None, genero: Optional[str] = None
    ) -> AnalisisCompleto:
        """Procesa una consulta completa con análisis unificado"""
        import time

        start_time = time.time()

        logger.info(f"🧠 Procesando consulta: {texto[:100]}...")

        # Procesamiento NLP básico
        consulta_procesada = self._procesar_consulta_nlp(texto, edad, genero)

        # Análisis de patrones clínicos
        palabras_clave = self._identificar_palabras_clave(texto)
        patologias_identificadas = self._identificar_patologias(
            texto, consulta_procesada
        )
        escalas_recomendadas = self._recomendar_escalas(
            patologias_identificadas, palabras_clave
        )

        # Mejorar términos de búsqueda
        terminos_mejorados = self._mejorar_terminos_busqueda(
            consulta_procesada, patologias_identificadas
        )

        # Generar preguntas de evaluación
        preguntas_evaluacion = self._generar_preguntas_evaluacion(
            palabras_clave, patologias_identificadas
        )

        # Calcular confianza global
        confianza_global = self._calcular_confianza_global(
            consulta_procesada, patologias_identificadas, palabras_clave
        )

        # Actualizar consulta procesada con información adicional
        consulta_procesada.palabras_clave = palabras_clave
        consulta_procesada.patologias_identificadas = patologias_identificadas
        consulta_procesada.escalas_recomendadas = escalas_recomendadas
        consulta_procesada.preguntas_evaluacion = preguntas_evaluacion
        consulta_procesada.confianza_global = confianza_global

        tiempo_procesamiento = time.time() - start_time

        logger.info(f"✅ Análisis completo realizado en {tiempo_procesamiento:.2f}s")

        return AnalisisCompleto(
            consulta_procesada=consulta_procesada,
            palabras_clave=palabras_clave,
            patologias_identificadas=patologias_identificadas,
            escalas_recomendadas=escalas_recomendadas,
            terminos_busqueda_mejorados=terminos_mejorados,
            preguntas_evaluacion=preguntas_evaluacion,
            confianza_global=confianza_global,
            tiempo_procesamiento=tiempo_procesamiento,
        )

    def _procesar_consulta_nlp(
        self, texto: str, edad: Optional[int] = None, genero: Optional[str] = None
    ) -> ConsultaProcesada:
        """Procesa la consulta usando NLP básico"""
        texto_lower = texto.lower()

        # Identificar intención
        intencion = self._identificar_intencion(texto_lower)

        # Extraer síntomas
        sintomas = self._extraer_sintomas(texto_lower)

        # Identificar actividades afectadas
        actividades = self._identificar_actividades(texto_lower)

        # Generar términos de búsqueda
        terminos = self._generar_terminos_busqueda(texto_lower, sintomas)

        # Determinar especialidad
        especialidad = self._determinar_especialidad(texto_lower, sintomas)

        return ConsultaProcesada(
            intencion=intencion,
            sintomas=sintomas,
            actividades_afectadas=actividades,
            terminos_busqueda=terminos,
            especialidad=especialidad,
            edad=edad,
            genero=genero,
        )

    def _identificar_intencion(self, texto: str) -> IntencionClinica:
        """Identifica la intención clínica del texto"""
        palabras_tratamiento = ["tratamiento", "terapia", "cura", "mejorar", "aliviar"]
        palabras_diagnostico = [
            "diagnóstico",
            "diagnostico",
            "qué tengo",
            "que tengo",
            "qué es",
        ]
        palabras_pronostico = [
            "pronóstico",
            "pronostico",
            "evolución",
            "evolucion",
            "futuro",
        ]
        palabras_prevencion = ["prevención", "prevencion", "evitar", "prevenir"]
        palabras_rehabilitacion = [
            "rehabilitación",
            "rehabilitacion",
            "recuperación",
            "recuperacion",
        ]
        palabras_evaluacion = [
            "evaluación",
            "evaluacion",
            "examen",
            "revisión",
            "revision",
        ]

        if any(palabra in texto for palabra in palabras_tratamiento):
            return IntencionClinica.TRATAMIENTO
        elif any(palabra in texto for palabra in palabras_diagnostico):
            return IntencionClinica.DIAGNOSTICO
        elif any(palabra in texto for palabra in palabras_pronostico):
            return IntencionClinica.PRONOSTICO
        elif any(palabra in texto for palabra in palabras_prevencion):
            return IntencionClinica.PREVENCION
        elif any(palabra in texto for palabra in palabras_rehabilitacion):
            return IntencionClinica.REHABILITACION
        elif any(palabra in texto for palabra in palabras_evaluacion):
            return IntencionClinica.EVALUACION
        else:
            return IntencionClinica.GENERAL

    def _extraer_sintomas(self, texto: str) -> List[SintomaExtraido]:
        """Extrae síntomas del texto"""
        sintomas = []

        # Buscar patrones de dolor
        for patron in self.patrones_sintomas["dolor"]:
            matches = re.finditer(patron, texto, re.IGNORECASE)
            for match in matches:
                localizacion = match.group(1) if match.group(1) else "general"
                sintoma = SintomaExtraido(
                    sintoma="dolor",
                    localizacion=localizacion,
                    intensidad=self._detectar_intensidad(texto),
                    frecuencia=self._detectar_frecuencia(texto),
                    duracion=self._detectar_duracion(texto),
                    agravantes=self._detectar_agravantes(texto),
                    mejorantes=self._detectar_mejorantes(texto),
                    confianza=0.8,
                )
                sintomas.append(sintoma)

        # Buscar otros síntomas
        otros_sintomas = [
            "rigidez",
            "debilidad",
            "inflamacion",
            "hinchazon",
            "entumecimiento",
        ]
        for sintoma in otros_sintomas:
            if sintoma in texto:
                sintoma_obj = SintomaExtraido(
                    sintoma=sintoma, localizacion="general", confianza=0.6
                )
                sintomas.append(sintoma_obj)

        return sintomas

    def _identificar_actividades(self, texto: str) -> List[str]:
        """Identifica actividades afectadas"""
        actividades = []

        for actividad_es, actividad_en in self.actividades.items():
            if actividad_es in texto:
                actividades.append(actividad_en)

        return actividades

    def _generar_terminos_busqueda(
        self, texto: str, sintomas: List[SintomaExtraido]
    ) -> List[str]:
        """Genera términos de búsqueda"""
        terminos = []

        # Agregar síntomas principales
        for sintoma in sintomas:
            if sintoma.localizacion != "general":
                termino = f"{sintoma.sintoma} {sintoma.localizacion}"
                terminos.append(termino)
            else:
                terminos.append(sintoma.sintoma)

        # Agregar términos del texto
        palabras_clave = [
            "dolor",
            "tratamiento",
            "terapia",
            "ejercicio",
            "rehabilitacion",
        ]
        for palabra in palabras_clave:
            if palabra in texto:
                terminos.append(palabra)

        return list(set(terminos))  # Eliminar duplicados

    def _determinar_especialidad(
        self, texto: str, sintomas: List[SintomaExtraido]
    ) -> str:
        """Determina la especialidad médica"""
        if any(
            "hombro" in s.localizacion or "brazo" in s.localizacion for s in sintomas
        ):
            return "traumatologia"
        elif any(
            "rodilla" in s.localizacion or "pierna" in s.localizacion for s in sintomas
        ):
            return "traumatologia"
        elif any(
            "espalda" in s.localizacion or "columna" in s.localizacion for s in sintomas
        ):
            return "fisiatria"
        elif any("cabeza" in s.localizacion for s in sintomas):
            return "neurologia"
        else:
            return "medicina_general"

    def _identificar_palabras_clave(self, texto: str) -> List[PalabraClave]:
        """Identifica palabras clave en el texto"""
        palabras_clave = []
        texto_lower = texto.lower()

        for palabra, info in self.palabras_clave_db.items():
            if palabra in texto_lower:
                palabra_clave = PalabraClave(
                    palabra=palabra,
                    categoria=info["categoria"],
                    intensidad=info["intensidad"],
                    patologias_asociadas=info["patologias_asociadas"],
                    escalas_evaluacion=info["escalas_evaluacion"],
                    preguntas_sugeridas=info["preguntas_sugeridas"],
                )
                palabras_clave.append(palabra_clave)

        return palabras_clave

    def _identificar_patologias(
        self, texto: str, consulta_procesada: ConsultaProcesada
    ) -> List[PatologiaIdentificada]:
        """Identifica patologías basadas en el texto y síntomas"""
        patologias = []
        texto_lower = texto.lower()

        for patologia, info in self.patologias_db.items():
            # Verificar si los síntomas asociados están presentes
            sintomas_presentes = 0
            for sintoma in info["sintomas_asociados"]:
                if sintoma in texto_lower:
                    sintomas_presentes += 1

            # Calcular confianza basada en síntomas presentes
            if sintomas_presentes > 0:
                confianza = min(0.9, sintomas_presentes * 0.3)

                patologia_obj = PatologiaIdentificada(
                    nombre=patologia,
                    confianza=confianza,
                    sintomas_asociados=info["sintomas_asociados"],
                    escalas_recomendadas=info["escalas_recomendadas"],
                    terminos_busqueda=info["terminos_busqueda"],
                )
                patologias.append(patologia_obj)

        return patologias

    def _recomendar_escalas(
        self,
        patologias: List[PatologiaIdentificada],
        palabras_clave: List[PalabraClave],
    ) -> List[EscalaEvaluacion]:
        """Recomienda escalas de evaluación"""
        escalas_recomendadas = []
        escalas_ya_recomendadas = set()

        # Escalas de patologías
        for patologia in patologias:
            for escala_nombre in patologia.escalas_recomendadas:
                if (
                    escala_nombre in self.escalas_db
                    and escala_nombre not in escalas_ya_recomendadas
                ):
                    info_escala = self.escalas_db[escala_nombre]
                    escala = EscalaEvaluacion(
                        nombre=escala_nombre,
                        descripcion=info_escala["descripcion"],
                        aplicacion=info_escala["aplicacion"],
                        puntuacion=info_escala["puntuacion"],
                        preguntas=info_escala["preguntas"],
                    )
                    escalas_recomendadas.append(escala)
                    escalas_ya_recomendadas.add(escala_nombre)

        # Escalas de palabras clave
        for palabra in palabras_clave:
            for escala_nombre in palabra.escalas_evaluacion:
                if (
                    escala_nombre in self.escalas_db
                    and escala_nombre not in escalas_ya_recomendadas
                ):
                    info_escala = self.escalas_db[escala_nombre]
                    escala = EscalaEvaluacion(
                        nombre=escala_nombre,
                        descripcion=info_escala["descripcion"],
                        aplicacion=info_escala["aplicacion"],
                        puntuacion=info_escala["puntuacion"],
                        preguntas=info_escala["preguntas"],
                    )
                    escalas_recomendadas.append(escala)
                    escalas_ya_recomendadas.add(escala_nombre)

        return escalas_recomendadas

    def _mejorar_terminos_busqueda(
        self,
        consulta_procesada: ConsultaProcesada,
        patologias: List[PatologiaIdentificada],
    ) -> List[str]:
        """Mejora los términos de búsqueda con información de patologías"""
        terminos_mejorados = consulta_procesada.terminos_busqueda.copy()

        # Agregar términos de patologías identificadas
        for patologia in patologias:
            terminos_mejorados.extend(patologia.terminos_busqueda)

        # Agregar términos en inglés para búsquedas internacionales
        for termino in consulta_procesada.terminos_busqueda:
            if termino in self.localizaciones:
                terminos_mejorados.append(self.localizaciones[termino])

        return list(set(terminos_mejorados))  # Eliminar duplicados

    def _generar_preguntas_evaluacion(
        self,
        palabras_clave: List[PalabraClave],
        patologias: List[PatologiaIdentificada],
    ) -> List[str]:
        """Genera preguntas de evaluación específicas"""
        preguntas = []

        # Preguntas de palabras clave
        for palabra in palabras_clave:
            preguntas.extend(palabra.preguntas_sugeridas)

        # Preguntas generales de evaluación
        preguntas_generales = [
            "¿Cuándo comenzó el problema?",
            "¿Ha tenido este problema antes?",
            "¿Qué tratamientos ha probado?",
            "¿Hay antecedentes familiares similares?",
            "¿Toma algún medicamento actualmente?",
        ]

        preguntas.extend(preguntas_generales)

        return list(set(preguntas))  # Eliminar duplicados

    def _calcular_confianza_global(
        self,
        consulta_procesada: ConsultaProcesada,
        patologias: List[PatologiaIdentificada],
        palabras_clave: List[PalabraClave],
    ) -> float:
        """Calcula la confianza global del análisis"""
        confianza = 0.0
        factores = 0

        # Factor 1: Síntomas identificados
        if consulta_procesada.sintomas:
            confianza += 0.3
            factores += 1

        # Factor 2: Patologías identificadas
        if patologias:
            confianza_patologias = sum(p.confianza for p in patologias) / len(
                patologias
            )
            confianza += confianza_patologias * 0.4
            factores += 1

        # Factor 3: Palabras clave identificadas
        if palabras_clave:
            confianza += 0.2
            factores += 1

        # Factor 4: Intención clara
        if consulta_procesada.intencion != IntencionClinica.GENERAL:
            confianza += 0.1
            factores += 1

        return confianza / max(factores, 1)

    def _detectar_intensidad(self, texto: str) -> Optional[str]:
        """Detecta la intensidad del síntoma"""
        for nivel, palabras in self.patrones_intensidad.items():
            if any(palabra in texto for palabra in palabras):
                return nivel
        return None

    def _detectar_frecuencia(self, texto: str) -> Optional[str]:
        """Detecta la frecuencia del síntoma"""
        for frecuencia, palabras in self.patrones_frecuencia.items():
            if any(palabra in texto for palabra in palabras):
                return frecuencia
        return None

    def _detectar_duracion(self, texto: str) -> Optional[str]:
        """Detecta la duración del síntoma"""
        patrones_duracion = [
            r"(\d+)\s+(?:días|dias|semanas|meses|años)",
            r"(?:desde|hace)\s+(\d+)\s+(?:días|dias|semanas|meses|años)",
        ]

        for patron in patrones_duracion:
            match = re.search(patron, texto)
            if match:
                return match.group(0)
        return None

    def _detectar_agravantes(self, texto: str) -> List[str]:
        """Detecta factores agravantes"""
        agravantes = []
        patrones_agravantes = [
            r"(?:empeora|agravan|aumenta)\s+(?:con|al|cuando)\s+(\w+)",
            r"(\w+)\s+(?:empeora|agrava|aumenta)",
        ]

        for patron in patrones_agravantes:
            matches = re.finditer(patron, texto, re.IGNORECASE)
            for match in matches:
                agravantes.append(match.group(1))

        return agravantes

    def _detectar_mejorantes(self, texto: str) -> List[str]:
        """Detecta factores mejorantes"""
        mejorantes = []
        patrones_mejorantes = [
            r"(?:mejora|alivia|disminuye)\s+(?:con|al|cuando)\s+(\w+)",
            r"(\w+)\s+(?:mejora|alivia|disminuye)",
        ]

        for patron in patrones_mejorantes:
            matches = re.finditer(patron, texto, re.IGNORECASE)
            for match in matches:
                mejorantes.append(match.group(1))

        return mejorantes


# Instancia global del sistema unificado
unified_nlp = UnifiedNLPProcessor()


def test_unified_nlp():
    """Función de prueba para el sistema unificado NLP"""
    print("🧪 Probando Sistema Unificado de Procesamiento NLP")
    print("=" * 60)

    # Casos de prueba
    casos_prueba = [
        "Tengo dolor en la espalda baja desde hace 2 semanas, me duele al caminar y no puedo levantar peso",
        "Siento rigidez en el hombro derecho, especialmente por las mañanas, y me cuesta levantar el brazo",
        "Tengo debilidad en la rodilla izquierda después de una caída, me siento inestable al subir escaleras",
    ]

    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🧪 Caso de prueba {i}:")
        print(f"   Texto: {caso}")

        analisis = unified_nlp.procesar_consulta_completa(caso)

        print(f"   ✅ Intención: {analisis.consulta_procesada.intencion.value}")
        print(f"   📊 Confianza: {analisis.confianza_global:.2f}")
        print(f"   🔍 Síntomas: {len(analisis.consulta_procesada.sintomas)}")
        print(f"   🏥 Patologías: {len(analisis.patologias_identificadas)}")
        print(f"   📋 Escalas: {len(analisis.escalas_recomendadas)}")
        print(f"   ⏱️ Tiempo: {analisis.tiempo_procesamiento:.2f}s")

    print("\n✅ Todas las pruebas completadas!")


if __name__ == "__main__":
    test_unified_nlp()
