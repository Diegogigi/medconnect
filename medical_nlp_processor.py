#!/usr/bin/env python3
"""
Sistema de procesamiento NLP médico para clasificación y extracción inteligente
"""

import re
import logging
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

@dataclass
class ConsultaProcesada:
    """Estructura para consulta procesada"""
    intencion: IntencionClinica
    sintomas: List[SintomaExtraido]
    actividades_afectadas: List[str]
    terminos_busqueda: List[str]
    especialidad: str
    edad: Optional[int] = None
    genero: Optional[str] = None

class MedicalNLPProcessor:
    """Procesador NLP médico para clasificación y extracción inteligente"""
    
    def __init__(self):
        # Patrones de reconocimiento para síntomas
        self.patrones_sintomas = {
            'dolor': [
                r'dolor\s+(?:en|del|de)\s+(\w+)',
                r'duele\s+(?:el|la|los|las)\s+(\w+)',
                r'me\s+duele\s+(?:el|la|los|las)\s+(\w+)',
                r'dolor\s+(\w+)',
                r'(\w+)\s+duele'
            ],
            'limitacion': [
                r'no\s+puedo\s+(\w+)',
                r'no\s+puede\s+(\w+)',
                r'dificultad\s+(?:para|en)\s+(\w+)',
                r'problema\s+(?:para|en)\s+(\w+)',
                r'limitacion\s+(?:para|en)\s+(\w+)'
            ],
            'actividad': [
                r'(\w+)\s+(?:causa|causan)\s+dolor',
                r'dolor\s+(?:al|cuando)\s+(\w+)',
                r'(\w+)\s+mejora\s+el\s+dolor',
                r'(\w+)\s+empeora\s+el\s+dolor'
            ]
        }
        
        # Mapeo de localizaciones anatómicas
        self.localizaciones = {
            'hombro': 'shoulder',
            'brazo': 'arm',
            'codo': 'elbow',
            'muñeca': 'wrist',
            'mano': 'hand',
            'cuello': 'neck',
            'espalda': 'back',
            'columna': 'spine',
            'cadera': 'hip',
            'rodilla': 'knee',
            'tobillo': 'ankle',
            'pie': 'foot',
            'pierna': 'leg',
            'cabeza': 'head',
            'pecho': 'chest',
            'abdomen': 'abdomen'
        }
        
        # Mapeo de actividades físicas
        self.actividades = {
            'correr': 'running',
            'caminar': 'walking',
            'saltar': 'jumping',
            'levantar': 'lifting',
            'doblar': 'bending',
            'rotar': 'rotating',
            'flexionar': 'flexing',
            'extender': 'extending',
            'elevar': 'raising',
            'secarme': 'drying',
            'vestirme': 'dressing',
            'peinarme': 'combing',
            'cocinar': 'cooking',
            'limpiar': 'cleaning',
            'trabajar': 'working',
            'deportes': 'sports',
            'ejercicio': 'exercise',
            'flexión de hombro': 'shoulder flexion',
            'elevaciones laterales': 'lateral raises',
            'flexión de cadera': 'hip flexion',
            'rotación de tronco': 'trunk rotation'
        }
        
        # Palabras clave para clasificación de intención
        self.palabras_clave_intencion = {
            IntencionClinica.TRATAMIENTO: [
                'tratamiento', 'terapia', 'cura', 'mejorar', 'aliviar', 'reducir',
                'ejercicio', 'rehabilitación', 'fisioterapia', 'kinesiología'
            ],
            IntencionClinica.DIAGNOSTICO: [
                'diagnóstico', 'qué tengo', 'qué es', 'causa', 'origen',
                'por qué', 'razón', 'motivo'
            ],
            IntencionClinica.PRONOSTICO: [
                'pronóstico', 'evolución', 'mejorará', 'tiempo', 'cuánto',
                'recuperación', 'progreso'
            ],
            IntencionClinica.PREVENCION: [
                'prevenir', 'evitar', 'precaución', 'cuidado', 'protección'
            ],
            IntencionClinica.REHABILITACION: [
                'rehabilitación', 'recuperación', 'ejercicios', 'terapia física'
            ]
        }

    def clasificar_intencion(self, texto: str) -> IntencionClinica:
        """Clasifica la intención clínica del texto"""
        texto_lower = texto.lower()
        
        # Contar palabras clave por tipo de intención
        scores = {}
        for intencion, palabras in self.palabras_clave_intencion.items():
            score = sum(1 for palabra in palabras if palabra in texto_lower)
            scores[intencion] = score
        
        # Si no hay coincidencias específicas, usar el contexto
        if max(scores.values()) == 0:
            if any(palabra in texto_lower for palabra in ['dolor', 'molestia', 'problema']):
                return IntencionClinica.TRATAMIENTO
            return IntencionClinica.GENERAL
        
        # Retornar la intención con mayor score
        return max(scores.items(), key=lambda x: x[1])[0]

    def extraer_sintomas(self, texto: str) -> List[SintomaExtraido]:
        """Extrae síntomas del texto usando patrones de reconocimiento"""
        sintomas = []
        texto_lower = texto.lower()
        
        # Extraer síntomas de dolor
        for patron in self.patrones_sintomas['dolor']:
            matches = re.finditer(patron, texto_lower)
            for match in matches:
                localizacion = match.group(1)
                sintoma = SintomaExtraido(
                    sintoma='dolor',
                    localizacion=localizacion,
                    intensidad=self._extraer_intensidad(texto_lower),
                    frecuencia=self._extraer_frecuencia(texto_lower),
                    duracion=self._extraer_duracion(texto_lower),
                    agravantes=self._extraer_agravantes(texto_lower),
                    mejorantes=self._extraer_mejorantes(texto_lower)
                )
                sintomas.append(sintoma)
        
        # Extraer limitaciones funcionales
        for patron in self.patrones_sintomas['limitacion']:
            matches = re.finditer(patron, texto_lower)
            for match in matches:
                actividad = match.group(1)
                sintoma = SintomaExtraido(
                    sintoma='limitacion',
                    localizacion='funcional',
                    agravantes=[actividad]
                )
                sintomas.append(sintoma)
        
        # Extraer actividades que causan dolor
        for patron in self.patrones_sintomas['actividad']:
            matches = re.finditer(patron, texto_lower)
            for match in matches:
                actividad = match.group(1)
                sintoma = SintomaExtraido(
                    sintoma='dolor_por_actividad',
                    localizacion='funcional',
                    agravantes=[actividad]
                )
                sintomas.append(sintoma)
        
        return sintomas

    def _extraer_intensidad(self, texto: str) -> Optional[str]:
        """Extrae información sobre la intensidad del dolor"""
        intensidades = {
            'leve': ['leve', 'suave', 'poco'],
            'moderado': ['moderado', 'medio', 'regular'],
            'severo': ['severo', 'fuerte', 'intenso', 'mucho']
        }
        
        for nivel, palabras in intensidades.items():
            if any(palabra in texto for palabra in palabras):
                return nivel
        return None

    def _extraer_frecuencia(self, texto: str) -> Optional[str]:
        """Extrae información sobre la frecuencia del dolor"""
        frecuencias = {
            'constante': ['constante', 'siempre', 'continuo'],
            'intermitente': ['intermitente', 'a veces', 'ocasional'],
            'diario': ['diario', 'todos los días'],
            'semanal': ['semanal', 'cada semana']
        }
        
        for frecuencia, palabras in frecuencias.items():
            if any(palabra in texto for palabra in palabras):
                return frecuencia
        return None

    def _extraer_duracion(self, texto: str) -> Optional[str]:
        """Extrae información sobre la duración del problema"""
        duraciones = {
            'agudo': ['agudo', 'reciente', 'nuevo', 'hace poco'],
            'subagudo': ['subagudo', 'hace semanas'],
            'cronico': ['crónico', 'hace meses', 'hace años', 'desde hace tiempo']
        }
        
        for duracion, palabras in duraciones.items():
            if any(palabra in texto for palabra in palabras):
                return duracion
        return None

    def _extraer_agravantes(self, texto: str) -> List[str]:
        """Extrae factores que agravan el dolor"""
        agravantes = []
        palabras_agravantes = [
            'movimiento', 'actividad', 'ejercicio', 'trabajo', 'esfuerzo',
            'levantar', 'cargar', 'doblar', 'rotar', 'flexionar'
        ]
        
        for palabra in palabras_agravantes:
            if palabra in texto:
                agravantes.append(palabra)
        
        return agravantes

    def _extraer_mejorantes(self, texto: str) -> List[str]:
        """Extrae factores que mejoran el dolor"""
        mejorantes = []
        palabras_mejorantes = [
            'reposo', 'descanso', 'hielo', 'calor', 'medicamento',
            'analgésico', 'antiinflamatorio', 'masaje', 'estiramiento'
        ]
        
        for palabra in palabras_mejorantes:
            if palabra in texto:
                mejorantes.append(palabra)
        
        return mejorantes

    def extraer_actividades_afectadas(self, texto: str) -> List[str]:
        """Extrae actividades que están afectadas"""
        actividades = []
        texto_lower = texto.lower()
        
        for actividad_esp, actividad_en in self.actividades.items():
            if actividad_esp in texto_lower:
                actividades.append(actividad_en)
        
        return actividades

    def generar_terminos_busqueda(self, sintomas: List[SintomaExtraido], 
                                 actividades: List[str], 
                                 especialidad: str) -> List[str]:
        """Genera términos de búsqueda efectivos para APIs médicas"""
        terminos = []
        
        # Agregar términos basados en síntomas
        for sintoma in sintomas:
            if sintoma.localizacion in self.localizaciones:
                termino_en = self.localizaciones[sintoma.localizacion]
                if sintoma.sintoma == 'dolor':
                    terminos.append(f"{termino_en} pain")
                    terminos.append(f"{termino_en} pain treatment")
                elif sintoma.sintoma == 'limitacion':
                    terminos.append(f"{termino_en} dysfunction")
                    terminos.append(f"{termino_en} rehabilitation")
        
        # Agregar términos basados en actividades
        for actividad in actividades:
            terminos.append(f"{actividad} injury")
            terminos.append(f"{actividad} rehabilitation")
            terminos.append(f"{actividad} physical therapy")
        
        # Agregar términos basados en especialidad
        especialidad_terminos = {
            'kinesiologia': ['physical therapy', 'physiotherapy'],
            'fisioterapia': ['physical therapy', 'physiotherapy'],
            'fonoaudiologia': ['speech therapy', 'communication disorders'],
            'psicologia': ['mental health', 'psychology'],
            'medicina': ['medical treatment', 'clinical management'],
            'terapia_ocupacional': ['occupational therapy', 'functional rehabilitation']
        }
        
        if especialidad in especialidad_terminos:
            terminos.extend(especialidad_terminos[especialidad])
        
        # Si no hay términos específicos, usar fallback
        if not terminos:
            terminos = ['pain treatment', 'physical therapy']
        
        return list(set(terminos))  # Eliminar duplicados

    def procesar_consulta(self, texto: str, especialidad: str, 
                         edad: Optional[int] = None, 
                         genero: Optional[str] = None) -> ConsultaProcesada:
        """Procesa una consulta completa y retorna información estructurada"""
        logger.info(f"🔍 Procesando consulta: {texto[:100]}...")
        
        # Clasificar intención
        intencion = self.clasificar_intencion(texto)
        logger.info(f"🎯 Intención clasificada: {intencion.value}")
        
        # Extraer síntomas
        sintomas = self.extraer_sintomas(texto)
        logger.info(f"📋 Síntomas extraídos: {len(sintomas)}")
        
        # Extraer actividades afectadas
        actividades = self.extraer_actividades_afectadas(texto)
        logger.info(f"🏃 Actividades afectadas: {actividades}")
        
        # Generar términos de búsqueda
        terminos = self.generar_terminos_busqueda(sintomas, actividades, especialidad)
        logger.info(f"🔍 Términos de búsqueda generados: {terminos}")
        
        return ConsultaProcesada(
            intencion=intencion,
            sintomas=sintomas,
            actividades_afectadas=actividades,
            terminos_busqueda=terminos,
            especialidad=especialidad,
            edad=edad,
            genero=genero
        )

# Instancia global del procesador
nlp_processor = MedicalNLPProcessor() 