#!/usr/bin/env python3
"""
Sistema de Orquestación RAG Clínico - Pipeline Completo
Meta-flujo: NLP → Terms/PICO → Recuperación dual → Filtrado → Re-ranking → Chunking → LLM → Verificación → APA
"""

import re
import json
import time
import logging
import hashlib
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import requests
from urllib.parse import quote

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar integración MeSH y MedlinePlus
from mesh_integration import mesh_integration
from medlineplus_integration import (
    medlineplus_integration,
    get_patient_education_for_code,
)


class TipoEstudio(Enum):
    """Tipos de estudios clínicos"""

    RCT = "randomized_controlled_trial"
    META_ANALYSIS = "meta_analysis"
    SYSTEMATIC_REVIEW = "systematic_review"
    GUIDELINE = "guideline"
    OBSERVATIONAL = "observational"
    CASE_STUDY = "case_study"
    EXPERT_OPINION = "expert_opinion"


class NivelEvidencia(Enum):
    """Niveles de evidencia clínica"""

    A = "A"  # Meta-análisis, RCTs
    B = "B"  # Estudios observacionales
    C = "C"  # Casos clínicos, opinión experta
    D = "D"  # Evidencia insuficiente


@dataclass
class TerminoBusqueda:
    """Término de búsqueda con metadatos"""

    termino: str
    tipo: str  # "PICO", "MeSH", "keyword"
    peso: float
    fuente: str  # "NLP", "manual", "MeSH"
    confianza: float


@dataclass
class ResultadoBusqueda:
    """Resultado de búsqueda con metadatos"""

    titulo: str
    abstract: str
    autores: List[str]
    año: int
    doi: str
    pmid: str
    fuente: str  # "PubMed", "EuropePMC"
    tipo_estudio: TipoEstudio
    nivel_evidencia: NivelEvidencia
    score_bm25: float
    score_embeddings: float
    score_final: float
    peer_reviewed: bool
    has_full_text: bool
    keywords: List[str]
    mesh_terms: List[str]


@dataclass
class ChunkConAnchors:
    """Chunk de texto con anchors para trazabilidad"""

    texto: str
    inicio_char: int
    fin_char: int
    seccion: str  # "abstract", "methods", "results", "discussion"
    parrafo: int
    oraciones: List[str]
    anchors: List[str]  # IDs únicos para cada oración
    entidades_clave: List[str]
    relevancia_clinica: float


@dataclass
class ResumenConEvidencia:
    """Resumen con evidencia requerida"""

    resumen: str
    oraciones_con_evidencia: List[
        Dict[str, Any]
    ]  # {oracion: str, citas: List[str], confianza: float}
    oraciones_sin_evidencia: List[str]
    claims_no_concluyentes: List[str]
    confianza_global: float
    # Campos para integración MedlinePlus
    patient_education: Dict[str, str] = field(default_factory=dict)
    education_available: bool = False
    education_summary: str = ""


@dataclass
class MapeoOracionCita:
    """Mapeo oración ↔ cita para auditoría"""

    oracion_id: str
    oracion_texto: str
    citas: List[str]
    chunks_soporte: List[str]
    confianza: float
    timestamp: datetime


@dataclass
class ResultadoOrquestacion:
    """Resultado final del pipeline de orquestación"""

    consulta_original: str
    terminos_busqueda: List[TerminoBusqueda]
    resultados_recuperados: List[ResultadoBusqueda]
    chunks_procesados: List[ChunkConAnchors]
    resumen_final: ResumenConEvidencia
    mapeo_oracion_cita: List[MapeoOracionCita]
    tiempo_total: float
    estadisticas: Dict[str, Any]


class GeneradorTerminosPICO:
    """Generador de términos de búsqueda PICO"""

    def __init__(self):
        self.patrones_pico = {
            "P": r"(pacientes?|personas?|sujetos?|individuos?|población)",
            "I": r"(intervención|tratamiento|terapia|medicamento|procedimiento)",
            "C": r"(comparador|control|placebo|estándar|alternativa)",
            "O": r"(resultado|outcome|efecto|beneficio|desenlace)",
        }

    def generar_terminos(
        self, consulta: str, analisis_nlp: Dict
    ) -> List[TerminoBusqueda]:
        """Genera términos de búsqueda basados en PICO"""
        terminos = []

        # Extraer términos del análisis NLP
        sintomas = analisis_nlp.get("sintomas", [])
        organos = analisis_nlp.get("organos", [])
        medicamentos = analisis_nlp.get("medicamentos", [])
        pico_terms = analisis_nlp.get("pico_terms", {})

        # Términos P (Población)
        for sintoma in sintomas:
            terminos.append(
                TerminoBusqueda(
                    termino=sintoma,
                    tipo="PICO_P",
                    peso=0.8,
                    fuente="NLP",
                    confianza=0.9,
                )
            )

        # Términos I (Intervención)
        for medicamento in medicamentos:
            terminos.append(
                TerminoBusqueda(
                    termino=medicamento,
                    tipo="PICO_I",
                    peso=0.9,
                    fuente="NLP",
                    confianza=0.8,
                )
            )

        # Términos O (Outcome)
        outcomes = ["mejora", "reducción", "efectividad", "beneficio"]
        for outcome in outcomes:
            if outcome in consulta.lower():
                terminos.append(
                    TerminoBusqueda(
                        termino=outcome,
                        tipo="PICO_O",
                        peso=0.7,
                        fuente="NLP",
                        confianza=0.7,
                    )
                )

        # INTEGRACIÓN MeSH: Usar términos MeSH reales del análisis NLP
        mesh_terms = analisis_nlp.get("mesh_terms", [])
        mesh_descriptor = analisis_nlp.get("mesh_descriptor", "")
        clinical_context = analisis_nlp.get("clinical_context", {})

        # Agregar términos MeSH principales
        if mesh_descriptor:
            terminos.append(
                TerminoBusqueda(
                    termino=mesh_descriptor,
                    tipo="MeSH_primary",
                    peso=0.9,
                    fuente="MeSH",
                    confianza=0.9,
                )
            )

        # Agregar términos MeSH expandidos
        for term in mesh_terms:
            if term != mesh_descriptor:  # Evitar duplicados
                terminos.append(
                    TerminoBusqueda(
                        termino=term,
                        tipo="MeSH_expanded",
                        peso=0.7,
                        fuente="MeSH",
                        confianza=0.8,
                    )
                )

        # Agregar términos de contexto clínico
        if clinical_context.get("specialty"):
            terminos.append(
                TerminoBusqueda(
                    termino=clinical_context["specialty"],
                    tipo="clinical_context",
                    peso=0.6,
                    fuente="MeSH",
                    confianza=0.7,
                )
            )

        return terminos

    def _expandir_mesh_terms(self, terminos: List[str]) -> List[str]:
        """Expande términos usando MeSH real"""
        # Este método ahora usa la integración MeSH real
        # La expansión se hace en el pipeline principal
        return []


class RecuperadorDual:
    """Recuperación dual: BM25 + Embeddings"""

    def __init__(self):
        self.api_key = None  # Se configurará desde environment

    def recuperar_dual(
        self, terminos: List[TerminoBusqueda]
    ) -> List[ResultadoBusqueda]:
        """Recupera documentos usando BM25 + Embeddings"""
        logger.info(f"🔍 Recuperación dual con {len(terminos)} términos")

        # Construir query combinada
        query_bm25 = self._construir_query_bm25(terminos)
        query_embeddings = self._construir_query_embeddings(terminos)

        # Búsqueda BM25 (simulada)
        resultados_bm25 = self._buscar_bm25(query_bm25)

        # Búsqueda por embeddings (simulada)
        resultados_embeddings = self._buscar_embeddings(query_embeddings)

        # Combinar y rankear resultados
        resultados_combinados = self._combinar_resultados(
            resultados_bm25, resultados_embeddings
        )

        logger.info(f"✅ {len(resultados_combinados)} resultados recuperados")
        return resultados_combinados

    def _construir_query_bm25(self, terminos: List[TerminoBusqueda]) -> str:
        """Construye query para BM25"""
        # Priorizar términos PICO
        pico_terms = [t.termino for t in terminos if t.tipo.startswith("PICO")]
        mesh_terms = [t.termino for t in terminos if t.tipo == "MeSH"]

        query_parts = []
        if pico_terms:
            query_parts.append(" AND ".join(pico_terms))
        if mesh_terms:
            query_parts.append(" OR ".join(mesh_terms))

        return (
            " AND ".join(query_parts)
            if query_parts
            else " ".join([t.termino for t in terminos])
        )

    def _construir_query_embeddings(self, terminos: List[TerminoBusqueda]) -> str:
        """Construye query para embeddings"""
        # Usar todos los términos con pesos
        weighted_terms = []
        for termino in terminos:
            weighted_terms.extend([termino.termino] * int(termino.peso * 10))

        return " ".join(weighted_terms)

    def _buscar_bm25(self, query: str) -> List[ResultadoBusqueda]:
        """Búsqueda BM25 (simulada)"""
        # Simulación de resultados BM25
        return [
            ResultadoBusqueda(
                titulo="Exercise therapy for knee osteoarthritis",
                abstract="Randomized controlled trial showing significant improvement...",
                autores=["Smith", "Johnson"],
                año=2023,
                doi="10.1000/ejemplo1",
                pmid="12345678",
                fuente="PubMed",
                tipo_estudio=TipoEstudio.RCT,
                nivel_evidencia=NivelEvidencia.A,
                score_bm25=0.85,
                score_embeddings=0.0,
                score_final=0.85,
                peer_reviewed=True,
                has_full_text=True,
                keywords=["exercise", "knee", "osteoarthritis"],
                mesh_terms=["Exercise Therapy", "Knee Joint", "Osteoarthritis"],
            ),
            ResultadoBusqueda(
                titulo="Physical therapy outcomes in chronic pain",
                abstract="Systematic review of physical therapy interventions...",
                autores=["Brown", "Davis"],
                año=2022,
                doi="10.1000/ejemplo2",
                pmid="87654321",
                fuente="EuropePMC",
                tipo_estudio=TipoEstudio.SYSTEMATIC_REVIEW,
                nivel_evidencia=NivelEvidencia.A,
                score_bm25=0.78,
                score_embeddings=0.0,
                score_final=0.78,
                peer_reviewed=True,
                has_full_text=True,
                keywords=["physical therapy", "chronic pain"],
                mesh_terms=["Physical Therapy", "Chronic Pain"],
            ),
        ]

    def _buscar_embeddings(self, query: str) -> List[ResultadoBusqueda]:
        """Búsqueda por embeddings (simulada)"""
        # Simulación de resultados embeddings
        return [
            ResultadoBusqueda(
                titulo="Rehabilitation strategies for joint pain",
                abstract="Comprehensive approach to joint rehabilitation...",
                autores=["Wilson", "Taylor"],
                año=2023,
                doi="10.1000/ejemplo3",
                pmid="11223344",
                fuente="PubMed",
                tipo_estudio=TipoEstudio.OBSERVATIONAL,
                nivel_evidencia=NivelEvidencia.B,
                score_bm25=0.0,
                score_embeddings=0.92,
                score_final=0.92,
                peer_reviewed=True,
                has_full_text=False,
                keywords=["rehabilitation", "joint pain"],
                mesh_terms=["Rehabilitation", "Joint Pain"],
            )
        ]

    def _combinar_resultados(
        self, bm25: List[ResultadoBusqueda], embeddings: List[ResultadoBusqueda]
    ) -> List[ResultadoBusqueda]:
        """Combina y rankea resultados"""
        # Combinar resultados únicos
        todos_resultados = {}

        for resultado in bm25 + embeddings:
            key = resultado.doi
            if key not in todos_resultados:
                todos_resultados[key] = resultado
            else:
                # Combinar scores
                todos_resultados[key].score_bm25 = max(
                    todos_resultados[key].score_bm25, resultado.score_bm25
                )
                todos_resultados[key].score_embeddings = max(
                    todos_resultados[key].score_embeddings, resultado.score_embeddings
                )
                todos_resultados[key].score_final = (
                    todos_resultados[key].score_bm25
                    + todos_resultados[key].score_embeddings
                ) / 2

        # Ordenar por score final
        resultados_ordenados = sorted(
            todos_resultados.values(), key=lambda x: x.score_final, reverse=True
        )

        return resultados_ordenados


class FiltradorEstudios:
    """Filtrado por diseño de estudio + año + peer-review"""

    def __init__(self):
        self.filtros_default = {
            "año_minimo": 2015,
            "peer_reviewed_only": True,
            "tipos_estudio_preferidos": [
                TipoEstudio.RCT,
                TipoEstudio.META_ANALYSIS,
                TipoEstudio.SYSTEMATIC_REVIEW,
                TipoEstudio.GUIDELINE,
            ],
            "niveles_evidencia_minimos": [NivelEvidencia.A, NivelEvidencia.B],
        }

    def filtrar_resultados(
        self, resultados: List[ResultadoBusqueda], filtros: Dict = None
    ) -> List[ResultadoBusqueda]:
        """Filtra resultados según criterios clínicos"""
        if filtros is None:
            filtros = self.filtros_default

        logger.info(f"🔍 Filtrando {len(resultados)} resultados")

        resultados_filtrados = []
        for resultado in resultados:
            if self._cumple_filtros(resultado, filtros):
                resultados_filtrados.append(resultado)

        logger.info(f"✅ {len(resultados_filtrados)} resultados después del filtrado")
        return resultados_filtrados

    def _cumple_filtros(self, resultado: ResultadoBusqueda, filtros: Dict) -> bool:
        """Verifica si un resultado cumple los filtros"""
        # Filtro de año
        if resultado.año < filtros.get("año_minimo", 2015):
            return False

        # Filtro de peer-review
        if filtros.get("peer_reviewed_only", True) and not resultado.peer_reviewed:
            return False

        # Filtro de tipo de estudio
        tipos_preferidos = filtros.get("tipos_estudio_preferidos", [])
        if tipos_preferidos and resultado.tipo_estudio not in tipos_preferidos:
            return False

        # Filtro de nivel de evidencia
        niveles_minimos = filtros.get("niveles_evidencia_minimos", [])
        if niveles_minimos and resultado.nivel_evidencia not in niveles_minimos:
            return False

        return True


class ReRankerClinico:
    """Re-ranking clínico (cross-encoder)"""

    def __init__(self):
        self.factores_ranking = {
            "tipo_estudio": {
                TipoEstudio.RCT: 1.0,
                TipoEstudio.META_ANALYSIS: 0.95,
                TipoEstudio.SYSTEMATIC_REVIEW: 0.9,
                TipoEstudio.GUIDELINE: 0.85,
                TipoEstudio.OBSERVATIONAL: 0.7,
                TipoEstudio.CASE_STUDY: 0.5,
                TipoEstudio.EXPERT_OPINION: 0.3,
            },
            "nivel_evidencia": {
                NivelEvidencia.A: 1.0,
                NivelEvidencia.B: 0.8,
                NivelEvidencia.C: 0.6,
                NivelEvidencia.D: 0.3,
            },
            "año": {"factor": 0.1, "año_base": 2023},  # Bonus por año reciente
            "full_text": 0.1,  # Bonus por texto completo disponible
            "score_original": 0.5,  # Peso del score original
        }

    def rerank_clinico(
        self, resultados: List[ResultadoBusqueda], consulta: str
    ) -> List[ResultadoBusqueda]:
        """Aplica re-ranking clínico"""
        logger.info(f"🔄 Re-ranking clínico de {len(resultados)} resultados")

        for resultado in resultados:
            score_clinico = self._calcular_score_clinico(resultado, consulta)
            resultado.score_final = score_clinico

        # Ordenar por score clínico
        resultados_reranked = sorted(
            resultados, key=lambda x: x.score_final, reverse=True
        )

        logger.info(f"✅ Re-ranking completado")
        return resultados_reranked

    def _calcular_score_clinico(
        self, resultado: ResultadoBusqueda, consulta: str
    ) -> float:
        """Calcula score clínico basado en múltiples factores"""
        score = 0.0

        # Factor tipo de estudio
        score += self.factores_ranking["tipo_estudio"].get(resultado.tipo_estudio, 0.5)

        # Factor nivel de evidencia
        score += self.factores_ranking["nivel_evidencia"].get(
            resultado.nivel_evidencia, 0.5
        )

        # Factor año
        años_recientes = max(
            0, resultado.año - self.factores_ranking["año"]["año_base"]
        )
        score += años_recientes * self.factores_ranking["año"]["factor"]

        # Factor texto completo
        if resultado.has_full_text:
            score += self.factores_ranking["full_text"]

        # Factor score original
        score_original = (resultado.score_bm25 + resultado.score_embeddings) / 2
        score += score_original * self.factores_ranking["score_original"]

        # Normalizar a 0-1
        return min(1.0, max(0.0, score / 3.0))


class ChunkerConAnchors:
    """Chunking con anchors para trazabilidad"""

    def __init__(self):
        self.secciones_importantes = [
            "abstract",
            "methods",
            "results",
            "discussion",
            "conclusion",
        ]

    def chunkear_con_anchors(
        self, resultados: List[ResultadoBusqueda]
    ) -> List[ChunkConAnchors]:
        """Crea chunks con anchors para trazabilidad"""
        logger.info(f"📄 Chunking con anchors de {len(resultados)} resultados")

        chunks = []
        for i, resultado in enumerate(resultados):
            # Chunkear abstract
            chunks_abstract = self._chunkear_texto(
                resultado.abstract, f"resultado_{i}_abstract", "abstract"
            )
            chunks.extend(chunks_abstract)

            # Si hay texto completo, chunkear secciones
            if resultado.has_full_text:
                # Simulación de texto completo
                texto_completo = self._simular_texto_completo(resultado)
                chunks_texto = self._chunkear_texto(
                    texto_completo, f"resultado_{i}_fulltext", "full_text"
                )
                chunks.extend(chunks_texto)

        logger.info(f"✅ {len(chunks)} chunks creados con anchors")
        return chunks

    def _chunkear_texto(
        self, texto: str, prefijo: str, seccion: str
    ) -> List[ChunkConAnchors]:
        """Chunkea texto en oraciones con anchors"""
        chunks = []

        # Dividir en oraciones
        oraciones = re.split(r"[.!?]+", texto)
        oraciones = [o.strip() for o in oraciones if o.strip()]

        # Crear chunks de 2-3 oraciones
        chunk_size = 3
        for i in range(0, len(oraciones), chunk_size):
            chunk_oraciones = oraciones[i : i + chunk_size]
            chunk_texto = ". ".join(chunk_oraciones) + "."

            # Generar anchors únicos
            anchors = []
            for j, oracion in enumerate(chunk_oraciones):
                anchor = f"{prefijo}_oracion_{i+j}_{hashlib.md5(oracion.encode()).hexdigest()[:8]}"
                anchors.append(anchor)

            # Extraer entidades clave (simplificado)
            entidades = self._extraer_entidades_clave(chunk_texto)

            chunk = ChunkConAnchors(
                texto=chunk_texto,
                inicio_char=0,  # Simplificado
                fin_char=len(chunk_texto),
                seccion=seccion,
                parrafo=i // chunk_size,
                oraciones=chunk_oraciones,
                anchors=anchors,
                entidades_clave=entidades,
                relevancia_clinica=0.8,  # Valor por defecto
            )

            chunks.append(chunk)

        return chunks

    def _extraer_entidades_clave(self, texto: str) -> List[str]:
        """Extrae entidades clave del texto"""
        # Implementación simplificada
        entidades_clave = [
            "dolor",
            "ejercicio",
            "tratamiento",
            "terapia",
            "rehabilitación",
            "rodilla",
            "articulación",
            "fisioterapia",
            "mejora",
            "efectividad",
        ]

        encontradas = []
        texto_lower = texto.lower()
        for entidad in entidades_clave:
            if entidad in texto_lower:
                encontradas.append(entidad)

        return encontradas

    def _simular_texto_completo(self, resultado: ResultadoBusqueda) -> str:
        """Simula texto completo del artículo"""
        return f"""
{resultado.abstract}

Methods: This study employed a randomized controlled design with 100 participants.

Results: Significant improvements were observed in pain reduction (p<0.001) and functional outcomes.

Discussion: The findings support the effectiveness of the intervention for managing symptoms.

Conclusion: This treatment approach shows promising results for clinical practice.
"""


class LLMSummarizer:
    """LLM Summarizer "con evidencia requerida" """

    def __init__(self):
        self.prompt_template = """
Sistema (oculto al usuario)

Eres un asistente clínico que genera respuestas basadas exclusivamente en evidencia encontrada en bases biomédicas.
Objetivo: producir un informe breve, claro y coherente para profesionales de la salud, en español, con el siguiente orden fijo:

Introducción (2–4 frases), 2) Evaluación/Examen (pruebas, escalas), 3) Diagnóstico (diferencial, criterios, imágenes), 4) Tratamiento/Terapia (conservador y/o quirúrgico; dosis, frecuencia, progresiones), 5) Cierre/Síntesis (take-home), 6) Referencias (formato APA 7).

Reglas de citación:
- Inserta marcadores [n] en el texto en cada afirmación que requiera respaldo (máx. 1–2 por frase).
- En "Referencias" lista solo las obras citadas con coincidencia 1:1 respecto a los marcadores.
- Formato APA 7 corto (Autor, Año. Título. Revista; volumen(nº):páginas. DOI/URL).

Evidencia: usa solo los ítems suministrados por el módulo de búsqueda (con título, autores, año, DOI/URL). No inventes ni extrapoles más allá de lo que dicen los estudios.

Estilo: frases concisas, párrafos de 3–5 líneas, voz activa, sin jerga innecesaria.

Seguridad: si la evidencia es limitada o conflictiva, decláralo y sugiere decisiones compartidas.
Si faltan datos críticos para una recomendación (p. ej., dosis), indícalo como "no concluyente [n]".
Si no hay evidencia suficiente, entregar "Hallazgos insuficientes para conclusiones", más una lista de vacíos.

Longitud: 250–600 palabras (según complejidad).
No uses bullets en Referencias; usa lista numerada.

EVIDENCIA DISPONIBLE:
{chunks_texto}

Salida estrictamente en el siguiente esquema Markdown:

## Introducción
{{contexto breve con 2–4 frases y 1–2 citas [n]}}

## Evaluación / Examen
{{signos, pruebas clínicas, escalas, umbrales, cuándo pedir imágenes; incluir sensibilidad/especificidad si están reportadas [n]}}

## Diagnóstico
{{criterios, diagnóstico diferencial, algoritmos, cuándo derivar; límites de evidencia [n]}}

## Tratamiento / Terapia
{{opciones conservadoras y/o quirúrgicas; parámetros: tipo, dosis, frecuencia, duración; progresiones; efectos adversos; calidad de evidencia [n]}}

## Cierre
{{síntesis práctica en 3–5 puntos o 4–6 líneas [n]}}

## Referencias
1. {{APA de la cita [1]}}
2. {{APA de la cita [2]}}
...
"""

    def resumir_con_evidencia(
        self, chunks: List[ChunkConAnchors], consulta: str
    ) -> ResumenConEvidencia:
        """Genera resumen con evidencia requerida"""
        logger.info(f"🧠 Generando resumen con evidencia de {len(chunks)} chunks")

        # Preparar chunks para el LLM
        chunks_texto = self._preparar_chunks_para_llm(chunks)

        # Generar prompt
        prompt = self.prompt_template.format(chunks_texto=chunks_texto)

        # Llamar al LLM (simulado)
        respuesta_llm = self._llm_summarize(prompt)

        # Procesar respuesta
        resumen_procesado = self._procesar_respuesta_llm(respuesta_llm, chunks)

        logger.info(f"✅ Resumen con evidencia generado")
        return resumen_procesado

    def _preparar_chunks_para_llm(self, chunks: List[ChunkConAnchors]) -> str:
        """Prepara chunks para el LLM"""
        chunks_texto = []
        for i, chunk in enumerate(chunks):
            chunks_texto.append(
                f"""
CHUNK {i+1} [ID: {chunk.anchors[0]}]:
{chunk.texto}
"""
            )
        return "\n".join(chunks_texto)

    def _llm_summarize(self, prompt: str) -> str:
        """Llama al LLM real para resumir la evidencia científica"""
        try:
            # Importar OpenAI para llamar al LLM real
            from openai import OpenAI
            import os

            # Configurar cliente OpenAI
            api_key = (
                os.getenv("OPENROUTER_API_KEY")
                or "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"
            )
            client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

            # Llamar al LLM real
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente médico especializado en análisis de evidencia científica. Tu objetivo es proporcionar análisis claros, estructurados y clínicamente relevantes basados en la evidencia disponible. Usa lenguaje profesional pero accesible, enfócate en hallazgos aplicables y mantén un formato organizado.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Baja temperatura para respuestas más consistentes
                max_tokens=1000,
            )

            # Extraer respuesta del LLM
            respuesta_llm = completion.choices[0].message.content.strip()
            logger.info(f"✅ LLM real llamado exitosamente")

            return respuesta_llm

        except Exception as e:
            logger.error(f"❌ Error llamando al LLM real: {e}")
            logger.warning("⚠️ Usando respuesta simulada como fallback")

            # Respuesta simulada como fallback
            return """
El ejercicio físico reduce significativamente el dolor de rodilla [CHUNK1].

La fisioterapia mejora la función articular [CHUNK2].

La rehabilitación supervisada es más efectiva que el ejercicio no supervisado [CHUNK3].

NO CONCLUSIVO: No hay evidencia suficiente sobre la duración óptima del tratamiento.
"""

    def _procesar_respuesta_llm(
        self, respuesta: str, chunks: List[ChunkConAnchors]
    ) -> ResumenConEvidencia:
        """Procesa la respuesta del LLM con formato estructurado"""
        # Verificar si la respuesta tiene formato estructurado
        if "## Introducción" in respuesta or "## Evaluación" in respuesta:
            return self._procesar_respuesta_estructurada(respuesta, chunks)
        else:
            return self._procesar_respuesta_simple(respuesta, chunks)

    def _procesar_respuesta_estructurada(
        self, respuesta: str, chunks: List[ChunkConAnchors]
    ) -> ResumenConEvidencia:
        """Procesa respuesta con formato estructurado (nuevo formato)"""
        oraciones_con_evidencia = []
        oraciones_sin_evidencia = []
        claims_no_concluyentes = []

        # Extraer marcadores de citas [n] del texto
        import re

        citas_encontradas = re.findall(r"\[(\d+)\]", respuesta)
        citas_unicas = list(set(citas_encontradas))

        # Contar oraciones con evidencia
        oraciones_con_citas = len(re.findall(r"\[(\d+)\]", respuesta))

        # Procesar cada sección
        secciones = respuesta.split("##")

        for seccion in secciones:
            if not seccion.strip():
                continue

            # Contar marcadores de citas en esta sección
            citas_seccion = re.findall(r"\[(\d+)\]", seccion)
            if citas_seccion:
                oraciones_con_evidencia.append(
                    {
                        "oracion": seccion.strip(),
                        "citas": citas_seccion,
                        "confianza": 0.9,
                    }
                )

        return ResumenConEvidencia(
            resumen=respuesta,
            oraciones_con_evidencia=oraciones_con_evidencia,
            oraciones_sin_evidencia=oraciones_sin_evidencia,
            claims_no_concluyentes=claims_no_concluyentes,
            confianza_global=0.85,
        )

    def _procesar_respuesta_simple(
        self, respuesta: str, chunks: List[ChunkConAnchors]
    ) -> ResumenConEvidencia:
        """Procesa respuesta simple (formato anterior)"""
        oraciones = respuesta.strip().split("\n")

        oraciones_con_evidencia = []
        oraciones_sin_evidencia = []
        claims_no_concluyentes = []

        for oracion in oraciones:
            if not oracion.strip():
                continue

            if "NO CONCLUSIVO" in oracion:
                claims_no_concluyentes.append(oracion)
            elif "[" in oracion and "]" in oracion:
                # Extraer citas
                citas = re.findall(r"\[(.*?)\]", oracion)
                oracion_limpia = re.sub(r"\[.*?\]", "", oracion).strip()

                oraciones_con_evidencia.append(
                    {"oracion": oracion_limpia, "citas": citas, "confianza": 0.9}
                )
            else:
                oraciones_sin_evidencia.append(oracion)

        return ResumenConEvidencia(
            resumen=respuesta,
            oraciones_con_evidencia=oraciones_con_evidencia,
            oraciones_sin_evidencia=oraciones_sin_evidencia,
            claims_no_concluyentes=claims_no_concluyentes,
            confianza_global=0.8,
        )


class VerificadorFactual:
    """Verificación factual mejorada con RapidFuzz"""

    def __init__(self):
        self.umbral_similitud = 0.7
        self.umbral_entidades = 0.5
        # Importar el asignador mejorado de citas
        try:
            from citation_assigner_enhanced import citation_assigner_enhanced

            self.citation_assigner = citation_assigner_enhanced
            logger.info("✅ VerificadorFactual mejorado con RapidFuzz")
        except ImportError:
            logger.warning("⚠️ RapidFuzz no disponible, usando verificación básica")
            self.citation_assigner = None

    def verificar_factual(
        self, resumen: ResumenConEvidencia, chunks: List[ChunkConAnchors]
    ) -> List[MapeoOracionCita]:
        """Verifica factualidad del resumen usando RapidFuzz si está disponible"""
        logger.info(
            f"🔍 Verificación factual de {len(resumen.oraciones_con_evidencia)} oraciones"
        )

        if self.citation_assigner:
            return self._verificar_con_rapidfuzz(resumen, chunks)
        else:
            return self._verificar_basico(resumen, chunks)

    def _verificar_con_rapidfuzz(
        self, resumen: ResumenConEvidencia, chunks: List[ChunkConAnchors]
    ) -> List[MapeoOracionCita]:
        """Verificación usando RapidFuzz para mayor precisión"""
        from citation_assigner_enhanced import (
            ChunkMetadata,
            attach_citations_to_sentences_enhanced,
        )

        # Convertir chunks a formato compatible
        chunks_metadata = []
        for chunk in chunks:
            chunk_meta = ChunkMetadata(
                text=chunk.texto,
                source=(
                    chunk.anchors[0]
                    if chunk.anchors
                    else f"chunk_{len(chunks_metadata)}"
                ),
                span=(chunk.inicio_char, chunk.fin_char),
                meta={
                    "seccion": chunk.seccion,
                    "parrafo": chunk.parrafo,
                    "relevancia_clinica": chunk.relevancia_clinica,
                },
                apa_citation=f"CHUNK_{len(chunks_metadata)+1}",
                entidades_clave=chunk.entidades_clave,
            )
            chunks_metadata.append(chunk_meta)

        # Extraer oraciones del resumen
        oraciones = []
        for oracion_data in resumen.oraciones_con_evidencia:
            oraciones.append(oracion_data["oracion"])

        # Usar asignador mejorado
        chunks_dict = []
        for chunk_meta in chunks_metadata:
            chunks_dict.append(
                {
                    "text": chunk_meta.text,
                    "source": chunk_meta.source,
                    "span": chunk_meta.span,
                    "meta": chunk_meta.meta,
                    "relevancia_score": chunk_meta.relevancia_score,
                    "entidades_clave": chunk_meta.entidades_clave,
                }
            )

        # Asignar citas usando RapidFuzz
        resultados = attach_citations_to_sentences_enhanced(
            oraciones, chunks_dict, sim_threshold=0.65
        )

        # Convertir a MapeoOracionCita
        mapeos = []
        for i, resultado in enumerate(resultados):
            oracion = resultado["sentence"]
            mapeo = MapeoOracionCita(
                oracion_id=hashlib.md5(oracion.encode()).hexdigest()[:8],
                oracion_texto=oracion,
                citas=resultado["citations"],
                chunks_soporte=resultado["chunks_soporte"],
                confianza=resultado["confianza"],
                timestamp=datetime.now(),
            )
            mapeos.append(mapeo)

        logger.info(f"✅ Verificación factual con RapidFuzz completada")
        return mapeos

    def _verificar_basico(
        self, resumen: ResumenConEvidencia, chunks: List[ChunkConAnchors]
    ) -> List[MapeoOracionCita]:
        """Verificación básica sin RapidFuzz"""
        mapeos = []

        for oracion_data in resumen.oraciones_con_evidencia:
            oracion = oracion_data["oracion"]
            citas = oracion_data["citas"]

            # Verificar cada cita
            chunks_soporte = []
            confianza_total = 0.0

            for cita in citas:
                chunk_soporte = self._encontrar_chunk_soporte(cita, chunks)
                if chunk_soporte:
                    chunks_soporte.append(chunk_soporte.anchors[0])
                    confianza_total += self._calcular_confianza_oracion(
                        oracion, chunk_soporte
                    )

            # Calcular confianza promedio
            confianza_promedio = (
                confianza_total / len(chunks_soporte) if chunks_soporte else 0.0
            )

            # Crear mapeo
            mapeo = MapeoOracionCita(
                oracion_id=hashlib.md5(oracion.encode()).hexdigest()[:8],
                oracion_texto=oracion,
                citas=citas,
                chunks_soporte=chunks_soporte,
                confianza=confianza_promedio,
                timestamp=datetime.now(),
            )

            mapeos.append(mapeo)

        logger.info(f"✅ Verificación factual básica completada")
        return mapeos

    def _encontrar_chunk_soporte(
        self, cita: str, chunks: List[ChunkConAnchors]
    ) -> Optional[ChunkConAnchors]:
        """Encuentra chunk que soporta una cita"""
        for chunk in chunks:
            if cita in chunk.anchors[0]:
                return chunk
        return None

    def _calcular_confianza_oracion(
        self, oracion: str, chunk: ChunkConAnchors
    ) -> float:
        """Calcula confianza de una oración contra un chunk"""
        # Similitud de texto
        similitud_texto = self._calcular_similitud_texto(oracion, chunk.texto)

        # Similitud de entidades
        similitud_entidades = self._calcular_similitud_entidades(
            self._extraer_entidades(oracion), chunk.entidades_clave
        )

        # Confianza combinada
        confianza = (similitud_texto + similitud_entidades) / 2
        return min(1.0, max(0.0, confianza))

    def _calcular_similitud_texto(self, texto1: str, texto2: str) -> float:
        """Calcula similitud de texto"""
        palabras1 = set(texto1.lower().split())
        palabras2 = set(texto2.lower().split())

        if not palabras1 or not palabras2:
            return 0.0

        intersection = palabras1 & palabras2
        union = palabras1 | palabras2

        return len(intersection) / len(union)

    def _calcular_similitud_entidades(
        self, entidades1: List[str], entidades2: List[str]
    ) -> float:
        """Calcula similitud de entidades"""
        if not entidades1 or not entidades2:
            return 0.0

        intersection = set(entidades1) & set(entidades2)
        union = set(entidades1) | set(entidades2)

        return len(intersection) / len(union)

    def _extraer_entidades(self, texto: str) -> List[str]:
        """Extrae entidades del texto"""
        # Implementación simplificada
        entidades_clave = [
            "dolor",
            "ejercicio",
            "tratamiento",
            "terapia",
            "rehabilitación",
            "rodilla",
            "articulación",
            "fisioterapia",
            "mejora",
            "efectividad",
        ]

        encontradas = []
        texto_lower = texto.lower()
        for entidad in entidades_clave:
            if entidad in texto_lower:
                encontradas.append(entidad)

        return encontradas


class FormateadorAPAFinal:
    """APA + Render final"""

    def __init__(self):
        self.formateador = None  # Se inicializará con el formateador APA existente

    def formatear_final(
        self, mapeos: List[MapeoOracionCita], resultados: List[ResultadoBusqueda]
    ) -> str:
        """Formatea resultado final con citas APA"""
        logger.info(f"📚 Formateando resultado final con {len(mapeos)} mapeos")

        # Crear diccionario de resultados por DOI
        resultados_dict = {r.doi: r for r in resultados}

        # Formatear cada oración con citas APA
        oraciones_formateadas = []

        for mapeo in mapeos:
            citas_apa = []
            for chunk_id in mapeo.chunks_soporte:
                # Encontrar resultado correspondiente
                for resultado in resultados:
                    if resultado.doi in chunk_id:
                        cita_apa = self._formatear_cita_apa(resultado)
                        citas_apa.append(cita_apa)
                        break

            if citas_apa:
                oracion_con_citas = f"{mapeo.oracion_texto} ({', '.join(citas_apa)})"
            else:
                oracion_con_citas = f"{mapeo.oracion_texto} [sin cita]"

            oraciones_formateadas.append(oracion_con_citas)

        # Crear resultado final
        resultado_final = "\n\n".join(oraciones_formateadas)

        logger.info(f"✅ Resultado final formateado")
        return resultado_final

    def _formatear_cita_apa(self, resultado: ResultadoBusqueda) -> str:
        """Formatea cita APA para un resultado"""
        # Formato simplificado APA
        if len(resultado.autores) == 1:
            autores = resultado.autores[0]
        elif len(resultado.autores) <= 3:
            autores = " & ".join(resultado.autores)
        else:
            autores = ", ".join(resultado.autores[:2]) + " et al."

        return f"{autores} ({resultado.año})"


class UnifiedOrchestrationSystem:
    """Sistema de Orquestación RAG Clínico Completo"""

    def __init__(self):
        logger.info("🎯 Inicializando Sistema de Orquestación RAG Clínico")

        # Inicializar componentes
        self.generador_terminos = GeneradorTerminosPICO()
        self.recuperador_dual = RecuperadorDual()
        self.filtrador = FiltradorEstudios()
        self.reranker = ReRankerClinico()
        self.chunker = ChunkerConAnchors()
        self.summarizer = LLMSummarizer()
        self.verificador = VerificadorFactual()
        self.formateador = FormateadorAPAFinal()

        logger.info("✅ Sistema de Orquestación RAG Clínico inicializado")

    def ejecutar_pipeline_completo(
        self, consulta: str, analisis_nlp: Dict[str, Any]
    ) -> ResultadoOrquestacion:
        """Ejecuta el pipeline completo de orquestación"""
        start_time = time.time()

        logger.info(f"🎯 Ejecutando pipeline completo para: {consulta[:50]}...")

        try:
            # INTEGRACIÓN MeSH: Normalizar consulta y generar términos mejorados
            mesh_descriptor = mesh_integration.normalize_medical_term(consulta)

            if mesh_descriptor:
                logger.info(
                    f"✅ Término normalizado MeSH: '{consulta}' → '{mesh_descriptor.label}'"
                )

                # Generar términos de búsqueda mejorados con MeSH
                enhanced_terms = mesh_integration.get_enhanced_search_terms(consulta)

                # Obtener contexto clínico
                clinical_context = mesh_integration.get_clinical_context(
                    mesh_descriptor
                )
                logger.info(
                    f"🏥 Contexto clínico: {clinical_context['specialty']} - {clinical_context['category']}"
                )

                # Agregar términos MeSH al análisis NLP
                analisis_nlp["mesh_terms"] = enhanced_terms
                analisis_nlp["mesh_descriptor"] = mesh_descriptor.label
                analisis_nlp["clinical_context"] = clinical_context
            else:
                logger.warning(f"⚠️ No se pudo normalizar con MeSH: {consulta}")

            # Paso 1: Generar términos PICO mejorados con MeSH
            terminos = self.generador_terminos.generar_terminos(consulta, analisis_nlp)
            logger.info(f"📝 {len(terminos)} términos generados (incluyendo MeSH)")

            # Paso 2: Recuperación dual (BM25 + Embeddings)
            resultados_recuperados = self.recuperador_dual.recuperar_dual(terminos)
            logger.info(f"🔍 {len(resultados_recuperados)} resultados recuperados")

            # Paso 3: Filtrado por diseño de estudio + año + peer-review
            resultados_filtrados = self.filtrador.filtrar_resultados(
                resultados_recuperados
            )
            logger.info(
                f"🔍 {len(resultados_filtrados)} resultados después del filtrado"
            )

            # Paso 4: Re-ranking clínico
            resultados_reranked = self.reranker.rerank_clinico(
                resultados_filtrados, consulta
            )
            logger.info(f"🔄 Re-ranking clínico completado")

            # Paso 5: Chunking con anchors
            chunks = self.chunker.chunkear_con_anchors(resultados_reranked)
            logger.info(f"📄 {len(chunks)} chunks creados con anchors")

            # Paso 6: LLM Summarizer con evidencia requerida
            resumen = self.summarizer.resumir_con_evidencia(chunks, consulta)
            logger.info(f"🧠 Resumen con evidencia generado")

            # Paso 7: Verificación factual
            mapeos = self.verificador.verificar_factual(resumen, chunks)
            logger.info(f"🔍 Verificación factual completada")

            # Paso 8: Formateo APA final
            resultado_final = self.formateador.formatear_final(
                mapeos, resultados_reranked
            )
            logger.info(f"📚 Formateo APA final completado")

            # INTEGRACIÓN MedlinePlus: Obtener educación del paciente
            patient_education = {}
            education_available = False

            if mesh_descriptor and clinical_context:
                try:
                    patient_education = self._get_patient_education(
                        consulta, clinical_context
                    )
                    education_available = patient_education.get("show_panel", False)

                    # Agregar educación del paciente al resumen
                    resumen.patient_education = patient_education
                    resumen.education_available = education_available
                    resumen.education_summary = patient_education.get("content", "")

                    logger.info(
                        f"📚 Educación del paciente agregada: {patient_education.get('title', 'N/A')}"
                    )
                except Exception as e:
                    logger.error(f"❌ Error obteniendo educación del paciente: {e}")

            # Calcular tiempo total
            tiempo_total = time.time() - start_time

            # Crear estadísticas
            estadisticas = {
                "terminos_generados": len(terminos),
                "resultados_recuperados": len(resultados_recuperados),
                "resultados_filtrados": len(resultados_filtrados),
                "chunks_creados": len(chunks),
                "oraciones_con_evidencia": len(resumen.oraciones_con_evidencia),
                "oraciones_sin_evidencia": len(resumen.oraciones_sin_evidencia),
                "claims_no_concluyentes": len(resumen.claims_no_concluyentes),
                "mapeos_verificados": len(mapeos),
            }

            # Crear resultado final
            resultado = ResultadoOrquestacion(
                consulta_original=consulta,
                terminos_busqueda=terminos,
                resultados_recuperados=resultados_reranked,
                chunks_procesados=chunks,
                resumen_final=resumen,
                mapeo_oracion_cita=mapeos,
                tiempo_total=tiempo_total,
                estadisticas=estadisticas,
            )

            logger.info(f"✅ Pipeline completo ejecutado en {tiempo_total:.2f}s")
            return resultado

        except Exception as e:
            logger.error(f"❌ Error en pipeline: {e}")
            # Retornar resultado de error
            return self._resultado_error(consulta, str(e))

    def _resultado_error(self, consulta: str, error: str) -> ResultadoOrquestacion:
        """Genera resultado de error"""
        return ResultadoOrquestacion(
            consulta_original=consulta,
            terminos_busqueda=[],
            resultados_recuperados=[],
            chunks_procesados=[],
            resumen_final=ResumenConEvidencia(
                resumen="Error en el procesamiento del pipeline.",
                oraciones_con_evidencia=[],
                oraciones_sin_evidencia=[],
                claims_no_concluyentes=[f"Error técnico: {error}"],
                confianza_global=0.0,
            ),
            mapeo_oracion_cita=[],
            tiempo_total=0.0,
            estadisticas={"error": error},
        )

    def _get_patient_education(
        self, query: str, clinical_context: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Obtiene información educativa para el paciente usando MedlinePlus

        Args:
            query: Consulta original del usuario
            clinical_context: Contexto clínico determinado por MeSH

        Returns:
            Dict con información educativa formateada
        """
        try:
            # Determinar tipo de código basado en contexto
            specialty = clinical_context.get("specialty", "General")

            # Mapeo de especialidades a tipos de códigos más probables
            code_type_mapping = {
                "Musculoskeletal": "diagnosis",  # ICD-10 para lesiones
                "Therapeutics": "medication",  # RxCUI para medicamentos
                "Cardiology": "diagnosis",  # ICD-10 para condiciones cardíacas
                "Neurology": "diagnosis",  # ICD-10 para condiciones neurológicas
                "Respiratory": "diagnosis",  # ICD-10 para condiciones respiratorias
                "Oncology": "diagnosis",  # ICD-10 para cáncer
                "General": "diagnosis",  # Por defecto
            }

            code_type = code_type_mapping.get(specialty, "diagnosis")

            # Por ahora, retornamos información educativa genérica
            # En una implementación completa, se extraerían códigos específicos
            education_info = {
                "title": f"📚 Información sobre {query}",
                "content": f"Obtén información educativa oficial sobre {query} en MedlinePlus.gov",
                "url": f"https://medlineplus.gov/spanish/search.html?query={quote(query)}",
                "show_panel": True,
                "source": "MedlinePlus.gov",
                "language": "es",
                "code_type": code_type,
                "specialty": specialty,
            }

            logger.info(f"✅ Información educativa preparada para: {query}")
            return education_info

        except Exception as e:
            logger.error(f"❌ Error obteniendo educación del paciente: {e}")
            return {
                "title": "Información educativa",
                "content": "Información educativa disponible en MedlinePlus.gov",
                "url": "https://medlineplus.gov/spanish/",
                "show_panel": False,
                "source": "MedlinePlus.gov",
                "language": "es",
            }


# Instancia global del sistema de orquestación
unified_orchestration = UnifiedOrchestrationSystem()


def test_orchestration_system():
    """Función de prueba para el sistema de orquestación"""
    print("🎯 Probando Sistema de Orquestación RAG Clínico")
    print("=" * 60)

    # Análisis NLP de prueba
    analisis_nlp_prueba = {
        "sintomas": ["dolor de rodilla", "rigidez articular"],
        "organos": ["rodilla", "articulación"],
        "medicamentos": ["paracetamol", "ibuprofeno"],
        "pico_terms": {
            "P": ["pacientes con osteoartritis"],
            "I": ["ejercicio físico", "fisioterapia"],
            "C": ["tratamiento estándar"],
            "O": ["reducción del dolor", "mejora funcional"],
        },
    }

    # Casos de prueba
    casos_prueba = [
        "¿Qué tratamientos son efectivos para el dolor de rodilla?",
        "¿Cuál es la evidencia sobre fisioterapia para osteoartritis?",
        "¿Qué ejercicios recomiendan para rehabilitación de rodilla?",
    ]

    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🔍 Caso {i}: {caso}")

        start_time = time.time()
        resultado = unified_orchestration.ejecutar_pipeline_completo(
            caso, analisis_nlp_prueba
        )
        tiempo = time.time() - start_time

        print(f"   ✅ Tiempo: {tiempo:.2f}s")
        print(f"   📝 Términos: {resultado.estadisticas['terminos_generados']}")
        print(f"   🔍 Recuperados: {resultado.estadisticas['resultados_recuperados']}")
        print(f"   🔍 Filtrados: {resultado.estadisticas['resultados_filtrados']}")
        print(f"   📄 Chunks: {resultado.estadisticas['chunks_creados']}")
        print(
            f"   📝 Con evidencia: {resultado.estadisticas['oraciones_con_evidencia']}"
        )
        print(
            f"   ⚠️ Sin evidencia: {resultado.estadisticas['oraciones_sin_evidencia']}"
        )
        print(
            f"   ❓ No concluyentes: {resultado.estadisticas['claims_no_concluyentes']}"
        )
        print(f"   🔍 Mapeos: {resultado.estadisticas['mapeos_verificados']}")

        # Mostrar resumen
        if resultado.resumen_final.resumen:
            print(f"   📋 Resumen: {resultado.resumen_final.resumen[:100]}...")

    print("\n✅ Pruebas del sistema de orquestación completadas!")


if __name__ == "__main__":
    test_orchestration_system()
