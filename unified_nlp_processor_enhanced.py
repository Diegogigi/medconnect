#!/usr/bin/env python3
"""
Sistema Unificado de Procesamiento NLP Médico - Versión Mejorada
Implementa NER clínica, NegEx, UMLS/MeSH linking, temporalidad, PICO
"""

import re
import logging
import json
import time
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib

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


class Lateralidad(Enum):
    """Lateralidad anatómica"""

    IZQUIERDA = "izquierda"
    DERECHA = "derecha"
    BILATERAL = "bilateral"
    CENTRAL = "central"
    NO_ESPECIFICADA = "no_especificada"


class Negacion(Enum):
    """Tipos de negación"""

    NEGADO = "negado"
    INCIERTO = "incierto"
    POSITIVO = "positivo"


class TipoEntidad(Enum):
    """Tipos de entidades clínicas"""

    SINTOMA = "sintoma"
    ORGANO = "organo"
    MEDICAMENTO = "medicamento"
    PROCEDIMIENTO = "procedimiento"
    ENFERMEDAD = "enfermedad"
    ANATOMIA = "anatomia"


@dataclass
class EntidadClinica:
    """Entidad clínica identificada por NER"""

    texto: str
    tipo: TipoEntidad
    cui: str = ""  # UMLS Concept Unique Identifier
    mesh_id: str = ""  # MeSH ID
    mesh_term: str = ""  # MeSH term
    confianza: float = 0.0
    negacion: Negacion = Negacion.POSITIVO
    lateralidad: Lateralidad = Lateralidad.NO_ESPECIFICADA
    inicio_char: int = 0
    fin_char: int = 0


@dataclass
class Temporalidad:
    """Información temporal del síntoma"""

    duracion_valor: Optional[int] = None
    duracion_unidad: str = ""  # días, semanas, meses, años
    inicio_relativo: str = ""  # "hace", "desde", "después de"
    fecha_inicio: Optional[datetime] = None
    es_cronico: bool = False
    es_agudo: bool = False


@dataclass
class Intensidad:
    """Información de intensidad del síntoma"""

    valor_numerico: Optional[float] = None
    escala: str = ""  # EVA, verbal, etc.
    descripcion: str = ""  # leve, moderado, severo
    confianza: float = 0.0


@dataclass
class SintomaExtraido:
    """Estructura mejorada para síntomas extraídos"""

    sintoma: str
    entidad_clinica: EntidadClinica
    localizacion: str
    temporalidad: Temporalidad = field(default_factory=Temporalidad)
    intensidad: Intensidad = field(default_factory=Intensidad)
    agravantes: List[str] = field(default_factory=list)
    mejorantes: List[str] = field(default_factory=list)
    confianza: float = 0.0
    patologias_asociadas: List[str] = field(default_factory=list)
    escalas_recomendadas: List[str] = field(default_factory=list)


@dataclass
class PICO:
    """Estructura PICO para términos de búsqueda"""

    population: List[str] = field(default_factory=list)
    intervention: List[str] = field(default_factory=list)
    comparator: List[str] = field(default_factory=list)
    outcome: List[str] = field(default_factory=list)
    terminos_mesh: List[str] = field(default_factory=list)
    terminos_expandidos: List[str] = field(default_factory=list)


@dataclass
class PalabraClave:
    """Representa una palabra clave identificada"""

    palabra: str
    categoria: str
    intensidad: float
    patologias_asociadas: List[str]
    escalas_evaluacion: List[str]
    preguntas_sugeridas: List[str]
    cui: str = ""
    mesh_id: str = ""


@dataclass
class PatologiaIdentificada:
    """Representa una patología identificada"""

    nombre: str
    confianza: float
    sintomas_asociados: List[str]
    escalas_recomendadas: List[str]
    terminos_busqueda: List[str]
    cui: str = ""
    mesh_id: str = ""


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
    """Estructura unificada para consulta procesada mejorada"""

    intencion: IntencionClinica
    sintomas: List[SintomaExtraido]
    entidades_clinicas: List[EntidadClinica]
    actividades_afectadas: List[str]
    terminos_busqueda: List[str]
    especialidad: str
    edad: Optional[int] = None
    genero: Optional[str] = None
    palabras_clave: List[PalabraClave] = field(default_factory=list)
    patologias_identificadas: List[PatologiaIdentificada] = field(default_factory=list)
    escalas_recomendadas: List[EscalaEvaluacion] = field(default_factory=list)
    preguntas_evaluacion: List[str] = field(default_factory=list)
    pico: PICO = field(default_factory=PICO)
    confianza_global: float = 0.0
    señales_clinicas: Dict[str, float] = field(default_factory=dict)


@dataclass
class AnalisisCompleto:
    """Análisis completo mejorado"""

    consulta_procesada: ConsultaProcesada
    palabras_clave: List[PalabraClave]
    patologias_identificadas: List[PatologiaIdentificada]
    escalas_recomendadas: List[EscalaEvaluacion]
    terminos_busqueda_mejorados: List[str]
    preguntas_evaluacion: List[str]
    confianza_global: float
    pico: PICO
    tiempo_procesamiento: float


class NegExProcessor:
    """Procesador de negaciones basado en NegEx/ConText"""

    def __init__(self):
        # Patrones de negación en español
        self.negacion_terminos = {
            "negacion_directa": [
                "no",
                "nunca",
                "jamás",
                "tampoco",
                "ningún",
                "ninguna",
                "sin",
                "ausencia",
                "ausente",
                "negativo",
                "negativa",
            ],
            "negacion_verbo": [
                "niega",
                "desmiente",
                "excluye",
                "rechaza",
                "duda",
                "no presenta",
                "no tiene",
                "no refiere",
                "no manifiesta",
            ],
            "incertidumbre": [
                "quizás",
                "tal vez",
                "posiblemente",
                "probablemente",
                "puede ser",
                "dudoso",
                "incierto",
                "no está claro",
            ],
        }

        # Patrones de contexto para negación
        self.contexto_negacion = [
            r"no\s+(\w+)",
            r"(\w+)\s+no\s+(\w+)",
            r"niega\s+(\w+)",
            r"ausencia\s+de\s+(\w+)",
            r"sin\s+(\w+)",
            r"(\w+)\s+negativo",
            r"(\w+)\s+ausente",
        ]

    def detectar_negacion(self, texto: str, entidad: str, posicion: int) -> Negacion:
        """Detecta negación para una entidad específica"""
        texto_lower = texto.lower()
        entidad_lower = entidad.lower()

        # Buscar patrones de negación directa
        for patron in self.contexto_negacion:
            matches = re.finditer(patron, texto_lower)
            for match in matches:
                if entidad_lower in match.group(0):
                    return Negacion.NEGADO

        # Buscar términos de incertidumbre
        for termino in self.negacion_terminos["incertidumbre"]:
            if termino in texto_lower:
                # Verificar si está cerca de la entidad
                if self._cerca_de_entidad(
                    texto_lower, entidad_lower, termino, posicion
                ):
                    return Negacion.INCIERTO

        return Negacion.POSITIVO

    def _cerca_de_entidad(
        self, texto: str, entidad: str, termino: str, posicion: int
    ) -> bool:
        """Verifica si un término está cerca de la entidad"""
        # Buscar el término en un rango de 50 caracteres alrededor de la entidad
        inicio = max(0, posicion - 50)
        fin = min(len(texto), posicion + 50)
        contexto = texto[inicio:fin]

        return termino in contexto


class TemporalidadProcessor:
    """Procesador de información temporal"""

    def __init__(self):
        # Patrones de duración
        self.patrones_duracion = [
            r"hace\s+(\d+)\s+(días?|semanas?|meses?|años?)",
            r"desde\s+hace\s+(\d+)\s+(días?|semanas?|meses?|años?)",
            r"(\d+)\s+(días?|semanas?|meses?|años?)\s+de\s+evolución",
            r"desde\s+(ayer|hoy|la\s+semana\s+pasada|el\s+mes\s+pasado)",
            r"(\d+)\s+(días?|semanas?|meses?|años?)\s+atrás",
        ]

        # Patrones de cronicidad
        self.patrones_cronico = [
            r"crónico",
            r"crónica",
            r"persistente",
            r"continuo",
            r"desde\s+hace\s+más\s+de\s+(\d+)\s+meses?",
            r"más\s+de\s+(\d+)\s+meses?",
        ]

        # Patrones de agudeza
        self.patrones_agudo = [
            r"agudo",
            r"aguda",
            r"reciente",
            r"súbito",
            r"repentino",
            r"desde\s+hace\s+menos\s+de\s+(\d+)\s+días?",
            r"hace\s+pocos?\s+(días?|horas?)",
        ]

    def extraer_temporalidad(self, texto: str) -> Temporalidad:
        """Extrae información temporal del texto"""
        temporalidad = Temporalidad()
        texto_lower = texto.lower()

        # Buscar duración específica
        for patron in self.patrones_duracion:
            match = re.search(patron, texto_lower)
            if match:
                if len(match.groups()) >= 2:
                    temporalidad.duracion_valor = int(match.group(1))
                    temporalidad.duracion_unidad = match.group(2)
                break

        # Detectar cronicidad
        for patron in self.patrones_cronico:
            if re.search(patron, texto_lower):
                temporalidad.es_cronico = True
                break

        # Detectar agudeza
        for patron in self.patrones_agudo:
            if re.search(patron, texto_lower):
                temporalidad.es_agudo = True
                break

        return temporalidad


class IntensidadProcessor:
    """Procesador de intensidad de síntomas"""

    def __init__(self):
        # Patrones de escala EVA
        self.patrones_eva = [
            r"EVA\s*(\d+(?:\.\d+)?)",
            r"escala\s+(\d+(?:\.\d+)?)",
            r"dolor\s+(\d+(?:\.\d+)?)/10",
            r"(\d+(?:\.\d+)?)/10",
        ]

        # Descriptores de intensidad
        self.intensidad_descriptores = {
            "leve": ["leve", "ligero", "suave", "poco", "escaso"],
            "moderado": ["moderado", "medio", "regular", "moderadamente"],
            "severo": ["severo", "fuerte", "intenso", "agudo", "grave", "muy"],
        }

    def extraer_intensidad(self, texto: str) -> Intensidad:
        """Extrae información de intensidad del texto"""
        intensidad = Intensidad()
        texto_lower = texto.lower()

        # Buscar escala EVA
        for patron in self.patrones_eva:
            match = re.search(patron, texto_lower)
            if match:
                intensidad.valor_numerico = float(match.group(1))
                intensidad.escala = "EVA"
                intensidad.confianza = 0.9
                break

        # Buscar descriptores
        for nivel, descriptores in self.intensidad_descriptores.items():
            for descriptor in descriptores:
                if descriptor in texto_lower:
                    intensidad.descripcion = nivel
                    if not intensidad.valor_numerico:
                        intensidad.confianza = 0.7
                    break

        return intensidad


class LateralidadProcessor:
    """Procesador de lateralidad anatómica"""

    def __init__(self):
        self.terminos_lateralidad = {
            Lateralidad.IZQUIERDA: ["izquierdo", "izquierda", "izq", "izquierda"],
            Lateralidad.DERECHA: ["derecho", "derecha", "der", "derecha"],
            Lateralidad.BILATERAL: [
                "bilateral",
                "ambos",
                "ambas",
                "los dos",
                "las dos",
            ],
            Lateralidad.CENTRAL: ["central", "medio", "centro"],
        }

    def detectar_lateralidad(self, texto: str, entidad: str) -> Lateralidad:
        """Detecta la lateralidad de una entidad"""
        texto_lower = texto.lower()
        entidad_lower = entidad.lower()

        # Buscar términos de lateralidad cerca de la entidad
        for lateralidad, terminos in self.terminos_lateralidad.items():
            for termino in terminos:
                if termino in texto_lower:
                    # Verificar si está cerca de la entidad
                    if self._cerca_de_entidad(texto_lower, entidad_lower, termino):
                        return lateralidad

        return Lateralidad.NO_ESPECIFICADA

    def _cerca_de_entidad(self, texto: str, entidad: str, termino: str) -> bool:
        """Verifica si un término está cerca de la entidad"""
        # Buscar el término en un rango de 30 caracteres alrededor de la entidad
        pos_entidad = texto.find(entidad)
        if pos_entidad == -1:
            return False

        inicio = max(0, pos_entidad - 30)
        fin = min(len(texto), pos_entidad + 30)
        contexto = texto[inicio:fin]

        return termino in contexto


class PICOGenerator:
    """Generador de términos PICO"""

    def __init__(self):
        # Mapeo de términos a categorías PICO
        self.terminos_pico = {
            "population": [
                "adulto",
                "adultos",
                "anciano",
                "ancianos",
                "pediátrico",
                "pediátricos",
                "mujer",
                "mujeres",
                "hombre",
                "hombres",
                "niño",
                "niños",
                "adolescente",
            ],
            "intervention": [
                "ejercicio",
                "terapia",
                "tratamiento",
                "medicación",
                "medicamento",
                "fisioterapia",
                "rehabilitación",
                "cirugía",
                "intervención",
            ],
            "comparator": [
                "placebo",
                "control",
                "estándar",
                "convencional",
                "tradicional",
            ],
            "outcome": [
                "dolor",
                "función",
                "movilidad",
                "calidad de vida",
                "recuperación",
                "mejora",
                "reducción",
                "alivio",
            ],
        }

    def generar_pico(self, texto: str, entidades: List[EntidadClinica]) -> PICO:
        """Genera estructura PICO basada en el texto y entidades"""
        pico = PICO()
        texto_lower = texto.lower()

        # Clasificar entidades por categoría PICO
        for entidad in entidades:
            if entidad.negacion == Negacion.NEGADO:
                continue  # Excluir entidades negadas

            # Determinar categoría basada en tipo de entidad
            if entidad.tipo == TipoEntidad.ENFERMEDAD:
                pico.population.append(entidad.texto)
            elif entidad.tipo == TipoEntidad.PROCEDIMIENTO:
                pico.intervention.append(entidad.texto)
            elif entidad.tipo == TipoEntidad.SINTOMA:
                pico.outcome.append(entidad.texto)

        # Agregar términos basados en texto
        for categoria, terminos in self.terminos_pico.items():
            for termino in terminos:
                if termino in texto_lower:
                    if categoria == "population":
                        pico.population.append(termino)
                    elif categoria == "intervention":
                        pico.intervention.append(termino)
                    elif categoria == "comparator":
                        pico.comparator.append(termino)
                    elif categoria == "outcome":
                        pico.outcome.append(termino)

        # Generar términos MeSH expandidos
        pico.terminos_mesh = self._generar_terminos_mesh(pico)
        pico.terminos_expandidos = self._expandir_terminos(pico)

        return pico

    def _generar_terminos_mesh(self, pico: PICO) -> List[str]:
        """Genera términos MeSH para búsqueda"""
        terminos_mesh = []

        # Agregar términos de población
        for termino in pico.population:
            terminos_mesh.append(f'"{termino}"[MeSH]')

        # Agregar términos de intervención
        for termino in pico.intervention:
            terminos_mesh.append(f'"{termino}"[MeSH]')

        # Agregar términos de resultado
        for termino in pico.outcome:
            terminos_mesh.append(f'"{termino}"[MeSH]')

        return terminos_mesh

    def _expandir_terminos(self, pico: PICO) -> List[str]:
        """Expande términos con sinónimos y variaciones"""
        terminos_expandidos = []

        # Expansión de términos de dolor
        if any("dolor" in termino.lower() for termino in pico.outcome):
            terminos_expandidos.extend(["pain", "ache", "discomfort"])

        # Expansión de términos de ejercicio
        if any("ejercicio" in termino.lower() for termino in pico.intervention):
            terminos_expandidos.extend(
                ["exercise", "physical therapy", "rehabilitation"]
            )

        # Expansión de términos de terapia
        if any("terapia" in termino.lower() for termino in pico.intervention):
            terminos_expandidos.extend(["therapy", "treatment", "intervention"])

        return terminos_expandidos


# Instancia global del sistema mejorado
unified_nlp_enhanced = None  # Se inicializará en el archivo principal


def test_nlp_enhanced():
    """Función de prueba para el sistema NLP mejorado"""
    print("🧪 Probando Sistema NLP Mejorado")
    print("=" * 50)

    # Procesadores individuales
    negex = NegExProcessor()
    temporalidad = TemporalidadProcessor()
    intensidad = IntensidadProcessor()
    lateralidad = LateralidadProcessor()
    pico = PICOGenerator()

    # Casos de prueba
    casos_prueba = [
        "Tengo dolor en la rodilla derecha desde hace 2 semanas, EVA 7/10",
        "No presenta fiebre ni dolor de cabeza",
        "Dolor lumbar crónico en adulto mayor",
        "Duda si tiene dolor en el hombro izquierdo",
    ]

    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🔍 Caso {i}: {caso}")

        # Probar negación
        negacion = negex.detectar_negacion(caso, "dolor", caso.find("dolor"))
        print(f"   🚫 Negación: {negacion.value}")

        # Probar temporalidad
        temp = temporalidad.extraer_temporalidad(caso)
        print(
            f"   ⏰ Temporalidad: {temp.duracion_valor} {temp.duracion_unidad}, Crónico: {temp.es_cronico}"
        )

        # Probar intensidad
        intens = intensidad.extraer_intensidad(caso)
        print(
            f"   📊 Intensidad: {intens.valor_numerico} {intens.escala}, {intens.descripcion}"
        )

        # Probar lateralidad
        lat = lateralidad.detectar_lateralidad(caso, "rodilla")
        print(f"   ↔️ Lateralidad: {lat.value}")

    print("\n✅ Pruebas de procesadores individuales completadas!")


if __name__ == "__main__":
    test_nlp_enhanced()
