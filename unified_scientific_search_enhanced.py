#!/usr/bin/env python3
"""
Sistema Unificado de Búsqueda Científica - Versión Mejorada
Implementa mejoras: Abstract + Full-Text, Deduplicación, Ranking Clínico, Filtros, Chunking, Citas APA
"""

import requests
import json
import time
import logging
import os
import re
import hashlib
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from urllib.parse import quote, urlparse
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3
from pathlib import Path
import xml.etree.ElementTree as ET
from enum import Enum
from mesh_integration import mesh_integration
from medlineplus_integration import (
    medlineplus_integration,
    get_patient_education_for_code,
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TipoEstudio(Enum):
    """Tipos de estudio por nivel de evidencia"""

    GUIDELINE = "guideline"
    META_ANALYSIS = "meta-analysis"
    SYSTEMATIC_REVIEW = "systematic review"
    RCT = "randomized controlled trial"
    COHORT = "cohort study"
    CASE_CONTROL = "case-control study"
    CASE_SERIES = "case series"
    CASE_REPORT = "case report"
    PREPRINT = "preprint"
    OTHER = "other"


@dataclass
class ChunkTexto:
    """Chunk de texto con trazabilidad"""

    texto: str
    seccion: str  # 'abstract', 'methods', 'results', 'conclusions'
    inicio_char: int
    fin_char: int
    tokens: int
    relevancia_score: float = 0.0


@dataclass
class EvidenciaCientifica:
    """Estructura mejorada para evidencia científica"""

    titulo: str
    autores: List[str]
    doi: str
    fecha_publicacion: str
    resumen: str
    nivel_evidencia: str
    fuente: str  # 'pubmed', 'europepmc', 'ncbi'
    url: str
    relevancia_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    año_publicacion: str = "N/A"
    tipo_evidencia: str = "Estudio científico"

    # Nuevos campos
    pmid: str = ""
    pmcid: str = ""
    tipo_estudio: TipoEstudio = TipoEstudio.OTHER
    journal: str = ""
    volumen: str = ""
    numero: str = ""
    paginas: str = ""
    is_open_access: bool = False
    has_full_text: bool = False
    publication_types: List[str] = field(default_factory=list)
    chunks: List[ChunkTexto] = field(default_factory=list)
    cita_apa: str = ""

    # Clave de deduplicación
    clave_unica: str = ""

    # Campos MeSH para integración
    mesh_terms: List[str] = field(default_factory=list)
    clinical_context: Dict[str, str] = field(default_factory=dict)
    mesh_ui: str = ""
    mesh_synonyms: List[str] = field(default_factory=list)
    mesh_tree_numbers: List[str] = field(default_factory=list)

    # Campos MedlinePlus para educación del paciente
    patient_education: Dict[str, str] = field(default_factory=dict)
    education_available: bool = False


@dataclass
class FiltrosBusqueda:
    """Filtros de búsqueda configurables"""

    peer_reviewed_only: bool = True
    year_from: int = 2010
    year_to: int = None
    study_designs: List[TipoEstudio] = field(default_factory=list)
    open_access_only: bool = False
    has_full_text: bool = False
    max_results: int = 10


@dataclass
class RespuestaUnificada:
    """Estructura para respuesta unificada mejorada"""

    respuesta: str
    evidencias: List[EvidenciaCientifica]
    terminos_utilizados: List[str]
    nivel_confianza: float
    citaciones: List[str]
    recomendaciones: List[str]
    tiempo_procesamiento: float
    fuentes_consultadas: List[str]
    estadisticas: Dict[str, any] = field(default_factory=dict)


class CacheManager:
    """Gestor de cache persistente con SQLite"""

    def __init__(self, db_path: str = "cache_scientific_search.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Inicializar base de datos SQLite"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key_hash TEXT PRIMARY KEY,
                    data TEXT,
                    timestamp REAL,
                    ttl INTEGER,
                    version TEXT
                )
            """
            )
            conn.commit()

    def get(self, key: str) -> Optional[Dict]:
        """Obtener datos del cache"""
        key_hash = hashlib.md5(key.encode()).hexdigest()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data, timestamp, ttl FROM cache WHERE key_hash = ?", (key_hash,)
            )
            result = cursor.fetchone()

            if result:
                data, timestamp, ttl = result
                if time.time() - timestamp < ttl:
                    return json.loads(data)
                else:
                    # Eliminar expirado
                    conn.execute("DELETE FROM cache WHERE key_hash = ?", (key_hash,))
                    conn.commit()

        return None

    def set(self, key: str, data: Dict, ttl: int = 3600):
        """Guardar datos en cache"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        timestamp = time.time()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key_hash, data, timestamp, ttl, version) VALUES (?, ?, ?, ?, ?)",
                (key_hash, json.dumps(data), timestamp, ttl, "1.0"),
            )
            conn.commit()


class RateLimiter:
    """Gestor de rate limiting con backoff exponencial"""

    def __init__(self, requests_per_second: float = 3.0):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0
        self.consecutive_failures = 0
        self.max_retries = 3

    def wait(self):
        """Esperar según rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def backoff_wait(self):
        """Espera con backoff exponencial"""
        if self.consecutive_failures > 0:
            backoff_time = min(2**self.consecutive_failures, 60)  # Máximo 60 segundos
            logger.warning(f"⏳ Backoff exponencial: esperando {backoff_time}s")
            time.sleep(backoff_time)

    def record_success(self):
        """Registrar éxito"""
        self.consecutive_failures = 0

    def record_failure(self):
        """Registrar fallo"""
        self.consecutive_failures += 1


class APACitationFormatter:
    """Formateador de citas APA 7"""

    @staticmethod
    def format_citation(evidencia: EvidenciaCientifica) -> str:
        """Formatear cita APA 7"""
        try:
            # Procesar autores
            autores = evidencia.autores[:20]  # Máximo 20 autores
            if len(evidencia.autores) > 20:
                autores.append("...")

            # Formatear lista de autores
            if len(autores) == 1:
                autores_str = autores[0]
            elif len(autores) == 2:
                autores_str = f"{autores[0]} & {autores[1]}"
            else:
                autores_str = ", ".join(autores[:-1]) + f", & {autores[-1]}"

            # Año de publicación
            año = (
                evidencia.año_publicacion
                if evidencia.año_publicacion != "N/A"
                else "s.f."
            )

            # Título con title case
            titulo = APACitationFormatter._title_case(evidencia.titulo)

            # Información del journal
            journal_info = evidencia.journal
            if evidencia.volumen:
                journal_info += f", {evidencia.volumen}"
                if evidencia.numero:
                    journal_info += f"({evidencia.numero})"
                if evidencia.paginas:
                    journal_info += f", {evidencia.paginas}"

            # DOI
            doi_str = (
                f" https://doi.org/{evidencia.doi}"
                if evidencia.doi and evidencia.doi != "Sin DOI"
                else ""
            )

            # Construir cita
            cita = f"{autores_str} ({año}). {titulo}. {journal_info}.{doi_str}"

            return cita

        except Exception as e:
            logger.error(f"Error formateando cita APA: {e}")
            return f"{evidencia.autores[0] if evidencia.autores else 'Autor'} ({evidencia.año_publicacion}). {evidencia.titulo}."

    @staticmethod
    def _title_case(text: str) -> str:
        """Convertir a title case según APA 7"""
        # Palabras que no se capitalizan (excepto al inicio)
        minor_words = {
            "a",
            "an",
            "and",
            "as",
            "at",
            "but",
            "by",
            "for",
            "in",
            "of",
            "on",
            "or",
            "the",
            "to",
            "up",
        }

        words = text.split()
        if not words:
            return text

        # Primera palabra siempre capitalizada
        result = [words[0].title()]

        # Resto de palabras
        for word in words[1:]:
            if word.lower() in minor_words:
                result.append(word.lower())
            else:
                result.append(word.title())

        return " ".join(result)


class UnifiedScientificSearchEnhanced:
    """Sistema unificado de búsqueda científica mejorado"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "MedConnect-IA/2.0 (https://medconnect.cl)"}
        )

        # Rate limiter mejorado
        self.rate_limiter = RateLimiter(requests_per_second=3.0)

        # Cache persistente
        self.cache = CacheManager()

        # API Keys (desde variables de entorno)
        self.ncbi_api_key = os.getenv(
            "NCBI_API_KEY", "fc67562a31bc52ad079357404cf1f6572107"
        )
        self.europepmc_api_key = os.getenv("EUROPEPMC_API_KEY", "")

        # Configuración
        self.max_evidencias = 15
        self.min_relevancia_score = 0.2

        # Mapeo de términos
        self.terminos_espanol_ingles = {
            "dolor lumbar": "low back pain",
            "dolor cervical": "neck pain",
            "dolor de hombro": "shoulder pain",
            "dolor de rodilla": "knee pain",
            "artritis": "arthritis",
            "fibromialgia": "fibromyalgia",
            "esclerosis múltiple": "multiple sclerosis",
            "diabetes": "diabetes",
            "hipertensión": "hypertension",
            "ansiedad": "anxiety",
            "depresión": "depression",
            "trastorno de ansiedad": "anxiety disorder",
            "trastorno depresivo": "depressive disorder",
            "rehabilitación": "rehabilitation",
            "fisioterapia": "physical therapy",
            "terapia ocupacional": "occupational therapy",
            "psicoterapia": "psychotherapy",
            "medicación": "medication",
            "tratamiento": "treatment",
            "terapia": "therapy",
        }

        # Tipos de estudio por prioridad
        self.tipo_estudio_prioridad = {
            TipoEstudio.GUIDELINE: 10,
            TipoEstudio.META_ANALYSIS: 9,
            TipoEstudio.SYSTEMATIC_REVIEW: 8,
            TipoEstudio.RCT: 7,
            TipoEstudio.COHORT: 6,
            TipoEstudio.CASE_CONTROL: 5,
            TipoEstudio.CASE_SERIES: 4,
            TipoEstudio.CASE_REPORT: 3,
            TipoEstudio.PREPRINT: 1,
            TipoEstudio.OTHER: 2,
        }

        logger.info("✅ Sistema Unificado de Búsqueda Científica Mejorado inicializado")

    def buscar_evidencia_unificada(
        self,
        termino: str,
        especialidad: str = None,
        max_resultados: int = None,
        filtros: FiltrosBusqueda = None,
    ) -> List[EvidenciaCientifica]:
        """Búsqueda unificada mejorada con normalización MeSH y ranking clínico"""

        if filtros is None:
            filtros = FiltrosBusqueda()

        if max_resultados is None:
            max_resultados = filtros.max_results

        start_time = time.time()
        logger.info(f"🔍 Búsqueda unificada mejorada con MeSH: {termino}")

        # INTEGRACIÓN MeSH: Normalizar término médico
        mesh_descriptor = mesh_integration.normalize_medical_term(termino)

        if mesh_descriptor:
            logger.info(
                f"✅ Término normalizado MeSH: '{termino}' → '{mesh_descriptor.label}'"
            )

            # Generar términos de búsqueda mejorados
            enhanced_terms = mesh_integration.get_enhanced_search_terms(termino)

            # Obtener contexto clínico
            clinical_context = mesh_integration.get_clinical_context(mesh_descriptor)
            logger.info(
                f"🏥 Contexto clínico: {clinical_context['specialty']} - {clinical_context['category']}"
            )

            # Usar términos mejorados para la búsqueda
            search_terms = enhanced_terms[:3]  # Usar top 3 términos
        else:
            logger.warning(f"⚠️ No se pudo normalizar con MeSH: {termino}")
            search_terms = [termino]

        # Estrategia 1: Búsqueda con términos MeSH mejorados
        todas_evidencias = []
        for search_term in search_terms:
            logger.info(f"🔍 Búsqueda con término MeSH: {search_term}")

            evidencias_pubmed = self._buscar_pubmed_mejorado(
                search_term, especialidad, filtros
            )
            evidencias_europepmc = self._buscar_europepmc_mejorado(
                search_term, especialidad, filtros
            )

            todas_evidencias.extend(evidencias_pubmed)
            todas_evidencias.extend(evidencias_europepmc)

        # Combinar y deduplicar
        todas_evidencias = evidencias_pubmed + evidencias_europepmc
        evidencias_deduplicadas = self._deduplicar_evidencias(todas_evidencias)

        # Si no hay resultados, usar estrategias alternativas
        if len(evidencias_deduplicadas) == 0:
            logger.info(
                "🔄 No se encontraron resultados, probando estrategias alternativas..."
            )

            # Estrategia 2: Búsqueda con términos más generales
            termino_general = self._generar_terminos_generales(termino)
            if termino_general != termino:
                logger.info(f"🔍 Probando búsqueda general: {termino_general}")
                evidencias_generales = self._buscar_pubmed_mejorado(
                    termino_general, especialidad, filtros
                )
                evidencias_deduplicadas.extend(evidencias_generales)

            # Estrategia 3: Búsqueda por especialidad médica
            if especialidad:
                termino_especialidad = f"{especialidad} treatment"
                logger.info(
                    f"🔍 Probando búsqueda por especialidad: {termino_especialidad}"
                )
                evidencias_especialidad = self._buscar_pubmed_mejorado(
                    termino_especialidad, None, filtros
                )
                evidencias_deduplicadas.extend(evidencias_especialidad)

            # Estrategia 4: Búsqueda de guías clínicas
            if len(evidencias_deduplicadas) == 0:
                logger.info("🔍 Probando búsqueda de guías clínicas...")
                filtros_guias = FiltrosBusqueda()
                filtros_guias.study_designs = [TipoEstudio.GUIDELINE]
                evidencias_guias = self._buscar_pubmed_mejorado(
                    "clinical guidelines", especialidad, filtros_guias
                )
                evidencias_deduplicadas.extend(evidencias_guias)

        # Aplicar ranking clínico
        evidencias_ranked = self._aplicar_ranking_clinico(
            evidencias_deduplicadas, termino
        )

        # Limitar resultados
        evidencias_finales = evidencias_ranked[:max_resultados]

        # INTEGRACIÓN MeSH: Agregar información MeSH a los resultados
        if mesh_descriptor:
            for evidencia in evidencias_finales:
                # Agregar campos MeSH a la evidencia
                evidencia.mesh_terms = [mesh_descriptor.label]
                evidencia.clinical_context = clinical_context
                evidencia.mesh_ui = mesh_descriptor.ui
                evidencia.mesh_synonyms = mesh_descriptor.synonyms
                evidencia.mesh_tree_numbers = mesh_descriptor.tree_numbers

                logger.debug(
                    f"📊 Evidencia con MeSH: {evidencia.titulo[:50]}... - MeSH: {mesh_descriptor.label}"
                )

        # INTEGRACIÓN MedlinePlus: Agregar educación del paciente
        if mesh_descriptor and clinical_context:
            try:
                patient_education = self._get_patient_education(
                    termino, clinical_context
                )
                for evidencia in evidencias_finales:
                    evidencia.patient_education = patient_education
                    evidencia.education_available = patient_education.get(
                        "show_panel", False
                    )

                logger.info(
                    f"📚 Educación del paciente agregada: {patient_education.get('title', 'N/A')}"
                )
            except Exception as e:
                logger.error(f"❌ Error agregando educación del paciente: {e}")

        # Generar citas APA
        for evidencia in evidencias_finales:
            evidencia.cita_apa = APACitationFormatter.format_citation(evidencia)

        tiempo_procesamiento = time.time() - start_time
        logger.info(
            f"✅ Búsqueda unificada completada: {len(evidencias_finales)} resultados en {tiempo_procesamiento:.2f}s"
        )

        return evidencias_finales

    def _buscar_pubmed_mejorado(
        self, termino: str, especialidad: str = None, filtros: FiltrosBusqueda = None
    ) -> List[EvidenciaCientifica]:
        """Búsqueda mejorada en PubMed con efetch para abstracts"""

        self.rate_limiter.wait()

        # Verificar cache
        cache_key = f"pubmed_{termino}_{especialidad}_{hash(str(filtros))}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return [EvidenciaCientifica(**ev) for ev in cached_data]

        termino_limpio = self._limpiar_termino_busqueda(termino)

        try:
            # Paso 1: Búsqueda inicial
            query_parts = [termino_limpio]
            if especialidad:
                query_parts.append(especialidad)

            # Aplicar filtros de fecha
            if filtros.year_from:
                query_parts.append(
                    f"{filtros.year_from}[dp]:{filtros.year_to or 3000}[dp]"
                )

            # Aplicar filtros de tipo de estudio
            if filtros.study_designs:
                study_filters = []
                for study_type in filtros.study_designs:
                    if study_type == TipoEstudio.RCT:
                        study_filters.append("randomized controlled trial[pt]")
                    elif study_type == TipoEstudio.META_ANALYSIS:
                        study_filters.append("meta-analysis[pt]")
                    elif study_type == TipoEstudio.SYSTEMATIC_REVIEW:
                        study_filters.append("systematic review[pt]")
                    elif study_type == TipoEstudio.GUIDELINE:
                        study_filters.append("guideline[pt]")

                if study_filters:
                    query_parts.append(f"({' OR '.join(study_filters)})")

            query = " AND ".join(query_parts)

            # Búsqueda inicial
            url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params_search = {
                "db": "pubmed",
                "term": query,
                "retmax": 20,  # Más resultados para mejor selección
                "retmode": "json",
                "sort": "relevance",
                "api_key": self.ncbi_api_key,
            }

            response = self.session.get(url_search, params=params_search, timeout=15)
            response.raise_for_status()

            data = response.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])

            if not id_list:
                return []

            # Paso 2: Obtener detalles completos con efetch
            self.rate_limiter.wait()

            url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params_fetch = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "rettype": "abstract",
                "retmode": "xml",
                "api_key": self.ncbi_api_key,
            }

            response_fetch = self.session.get(
                url_fetch, params=params_fetch, timeout=15
            )
            response_fetch.raise_for_status()

            # Parsear XML
            root = ET.fromstring(response_fetch.content)
            evidencias = []

            for article in root.findall(".//PubmedArticle"):
                try:
                    evidencia = self._parse_pubmed_article(article, termino_limpio)
                    if evidencia:
                        evidencias.append(evidencia)
                except Exception as e:
                    logger.warning(f"Error parseando artículo PubMed: {e}")
                    continue

            # Guardar en cache
            cache_data = [self._evidencia_to_dict(ev) for ev in evidencias]
            self.cache.set(cache_key, cache_data, ttl=3600)

            self.rate_limiter.record_success()
            logger.info(f"✅ PubMed mejorado: {len(evidencias)} resultados encontrados")
            return evidencias

        except Exception as e:
            self.rate_limiter.record_failure()
            logger.error(f"❌ Error en búsqueda PubMed mejorada: {e}")
            return []

    def _parse_pubmed_article(
        self, article: ET.Element, termino_busqueda: str
    ) -> Optional[EvidenciaCientifica]:
        """Parsear artículo PubMed desde XML"""
        try:
            # Extraer información básica
            medline_citation = article.find(".//MedlineCitation")
            pubmed_data = article.find(".//PubmedData")

            if not medline_citation:
                return None

            # PMID
            pmid = medline_citation.get("PMID", "")

            # Título
            title_element = medline_citation.find(".//ArticleTitle")
            titulo = (
                " ".join(title_element.itertext())
                if title_element is not None
                else "Sin título"
            )

            # Autores
            autores = []
            author_list = medline_citation.find(".//AuthorList")
            if author_list is not None:
                for author in author_list.findall(".//Author"):
                    last_name = author.find("LastName")
                    fore_name = author.find("ForeName")
                    if last_name is not None and fore_name is not None:
                        autores.append(f"{fore_name.text} {last_name.text}")
                    elif last_name is not None:
                        autores.append(last_name.text)

            # Abstract
            abstract_element = medline_citation.find(".//Abstract/AbstractText")
            resumen = (
                " ".join(abstract_element.itertext())
                if abstract_element is not None
                else "Sin resumen"
            )

            # Fecha de publicación
            pub_date = medline_citation.find(".//PubDate")
            fecha_publicacion = "Fecha no disponible"
            año_publicacion = "N/A"

            if pub_date is not None:
                year_element = pub_date.find("Year")
                if year_element is not None:
                    año_publicacion = year_element.text
                    fecha_publicacion = año_publicacion

            # Journal info
            journal_element = medline_citation.find(".//Journal")
            journal = ""
            volumen = ""
            numero = ""
            paginas = ""

            if journal_element is not None:
                journal_title = journal_element.find(".//Title")
                if journal_title is not None:
                    journal = journal_title.text

                journal_issue = journal_element.find(".//JournalIssue")
                if journal_issue is not None:
                    vol_element = journal_issue.find("Volume")
                    if vol_element is not None:
                        volumen = vol_element.text

                    issue_element = journal_issue.find("Issue")
                    if issue_element is not None:
                        numero = issue_element.text

            # DOI - Buscar en múltiples ubicaciones
            doi = ""

            # 1. Buscar en ELocationID
            elocation_ids = medline_citation.findall(".//ELocationID")
            for elocation_id in elocation_ids:
                if elocation_id.get("EIdType") == "doi":
                    doi = elocation_id.text
                    break

            # 2. Buscar en ArticleIdList (PubmedData)
            if not doi and pubmed_data is not None:
                article_ids = pubmed_data.findall(".//ArticleId")
                for article_id in article_ids:
                    if article_id.get("IdType") == "doi":
                        doi = article_id.text
                        break

            # 3. Buscar en AbstractText (a veces el DOI está en el abstract)
            if not doi:
                abstract_text = medline_citation.find(".//Abstract/AbstractText")
                if abstract_text is not None:
                    abstract_content = " ".join(abstract_text.itertext())
                    import re

                    doi_match = re.search(r"10\.\d{4,}/[-._;()/:\w]+", abstract_content)
                    if doi_match:
                        doi = doi_match.group()

            # Si no se encontró DOI, usar "Sin DOI"
            if not doi:
                doi = "Sin DOI"

            # PMC ID
            pmcid = ""
            article_ids = (
                pubmed_data.findall(".//ArticleId") if pubmed_data is not None else []
            )
            for article_id in article_ids:
                if article_id.get("IdType") == "pmc":
                    pmcid = article_id.text
                    break

            # Publication types
            publication_types = []
            pub_type_list = medline_citation.find(".//PublicationTypeList")
            if pub_type_list is not None:
                for pub_type in pub_type_list.findall(".//PublicationType"):
                    publication_types.append(pub_type.text)

            # Determinar tipo de estudio
            tipo_estudio = self._determinar_tipo_estudio(
                publication_types, titulo, resumen
            )

            # Calcular relevancia
            relevancia_score = self._calcular_relevancia_score_mejorado(
                titulo, resumen, termino_busqueda, tipo_estudio, año_publicacion
            )

            # Crear evidencia
            evidencia = EvidenciaCientifica(
                titulo=titulo,
                autores=autores,
                doi=doi,
                fecha_publicacion=fecha_publicacion,
                resumen=resumen,
                nivel_evidencia=self._determinar_nivel_evidencia(titulo, resumen),
                fuente="pubmed",
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                relevancia_score=relevancia_score,
                año_publicacion=año_publicacion,
                pmid=pmid,
                pmcid=pmcid,
                tipo_estudio=tipo_estudio,
                journal=journal,
                volumen=volumen,
                numero=numero,
                paginas=paginas,
                publication_types=publication_types,
                is_open_access=bool(pmcid),
                has_full_text=bool(pmcid),
            )

            # Generar clave única
            evidencia.clave_unica = self._generar_clave_unica(evidencia)

            return evidencia

        except Exception as e:
            logger.error(f"Error parseando artículo PubMed: {e}")
            return None

    def _buscar_europepmc_mejorado(
        self, termino: str, especialidad: str = None, filtros: FiltrosBusqueda = None
    ) -> List[EvidenciaCientifica]:
        """Búsqueda mejorada en Europe PMC con full-text cuando esté disponible"""

        self.rate_limiter.wait()

        # Verificar cache
        cache_key = f"europepmc_{termino}_{especialidad}_{hash(str(filtros))}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return [EvidenciaCientifica(**ev) for ev in cached_data]

        termino_limpio = self._limpiar_termino_busqueda(termino)

        try:
            # Construir query con filtros
            query_parts = [termino_limpio]

            # Filtros específicos de Europe PMC
            if filtros.open_access_only:
                query_parts.append("OPEN_ACCESS:y")

            if filtros.has_full_text:
                query_parts.append("HAS_PDF:y")

            if filtros.study_designs:
                for study_type in filtros.study_designs:
                    if study_type == TipoEstudio.SYSTEMATIC_REVIEW:
                        query_parts.append("PUB_TYPE:Review")
                    elif study_type == TipoEstudio.META_ANALYSIS:
                        query_parts.append("PUB_TYPE:Meta-analysis")

            query = " AND ".join(query_parts)

            # URL de Europe PMC
            url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
            params = {
                "query": query,
                "resultType": "core",
                "pageSize": 20,
                "format": "json",
                "sort": "RELEVANCE",
            }

            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            papers = data.get("resultList", {}).get("result", [])

            evidencias = []
            for paper in papers:
                try:
                    evidencia = self._parse_europepmc_paper(paper, termino_limpio)
                    if evidencia:
                        evidencias.append(evidencia)
                except Exception as e:
                    logger.warning(f"Error parseando artículo Europe PMC: {e}")
                    continue

            # Guardar en cache
            cache_data = [self._evidencia_to_dict(ev) for ev in evidencias]
            self.cache.set(cache_key, cache_data, ttl=3600)

            self.rate_limiter.record_success()
            logger.info(
                f"✅ Europe PMC mejorado: {len(evidencias)} resultados encontrados"
            )
            return evidencias

        except Exception as e:
            self.rate_limiter.record_failure()
            logger.error(f"❌ Error en búsqueda Europe PMC mejorada: {e}")
            return []

    def _parse_europepmc_paper(
        self, paper: Dict, termino_busqueda: str
    ) -> Optional[EvidenciaCientifica]:
        """Parsear artículo Europe PMC"""
        try:
            # Información básica
            titulo = paper.get("title", "Sin título")

            # Autores
            autores = []
            author_string = paper.get("authorString", "")
            if author_string:
                autores = [
                    author.strip()
                    for author in author_string.split(", ")
                    if author.strip()
                ]

            # DOI
            doi = paper.get("doi", "Sin DOI")

            # Fecha de publicación
            fecha_publicacion = paper.get("firstPublicationDate", "Fecha no disponible")
            año_publicacion = fecha_publicacion[:4] if fecha_publicacion else "N/A"

            # Abstract
            resumen = paper.get("abstractText", "Sin resumen")

            # Journal info
            journal = paper.get("journalInfo", {}).get("journal", {}).get("title", "")
            volumen = paper.get("journalInfo", {}).get("volume", "")
            numero = paper.get("journalInfo", {}).get("issue", "")
            paginas = paper.get("journalInfo", {}).get("pageInfo", "")

            # PMC ID
            pmcid = paper.get("pmcid", "")

            # Open Access
            is_open_access = paper.get("isOpenAccess", False)

            # Publication types
            publication_types = (
                paper.get("documentType", "").split(";")
                if paper.get("documentType")
                else []
            )

            # Determinar tipo de estudio
            tipo_estudio = self._determinar_tipo_estudio(
                publication_types, titulo, resumen
            )

            # Calcular relevancia
            relevancia_score = self._calcular_relevancia_score_mejorado(
                titulo, resumen, termino_busqueda, tipo_estudio, año_publicacion
            )

            # Construir URL correcta
            url = self._construir_url_europepmc(paper)

            # Crear evidencia
            evidencia = EvidenciaCientifica(
                titulo=titulo,
                autores=autores,
                doi=doi,
                fecha_publicacion=fecha_publicacion,
                resumen=resumen,
                nivel_evidencia=self._determinar_nivel_evidencia(titulo, resumen),
                fuente="europepmc",
                url=url,
                relevancia_score=relevancia_score,
                año_publicacion=año_publicacion,
                pmcid=pmcid,
                tipo_estudio=tipo_estudio,
                journal=journal,
                volumen=volumen,
                numero=numero,
                paginas=paginas,
                publication_types=publication_types,
                is_open_access=is_open_access,
                has_full_text=bool(pmcid and is_open_access),
            )

            # Generar clave única
            evidencia.clave_unica = self._generar_clave_unica(evidencia)

            return evidencia

        except Exception as e:
            logger.error(f"Error parseando artículo Europe PMC: {e}")
            return None

    def _construir_url_europepmc(self, paper: Dict) -> str:
        """Construir URL correcta para Europe PMC"""
        source = paper.get("source", "")
        id_type = paper.get("id", "")

        if source == "MED" and id_type:
            return f"https://europepmc.org/abstract/MED/{id_type}"
        elif source == "PMC" and id_type:
            return f"https://europepmc.org/article/PMC/{id_type}"
        else:
            return f"https://europepmc.org/article/{source}/{id_type}"

    def _deduplicar_evidencias(
        self, evidencias: List[EvidenciaCientifica]
    ) -> List[EvidenciaCientifica]:
        """Deduplicar evidencias usando clave única"""
        seen = set()
        deduplicadas = []

        for evidencia in evidencias:
            if evidencia.clave_unica not in seen:
                seen.add(evidencia.clave_unica)
                deduplicadas.append(evidencia)

        logger.info(f"🔄 Deduplicación: {len(evidencias)} → {len(deduplicadas)}")
        return deduplicadas

    def _generar_clave_unica(self, evidencia: EvidenciaCientifica) -> str:
        """Generar clave única para deduplicación"""
        # Normalizar DOI
        doi_normalizado = self._normalizar_doi(evidencia.doi)

        # Usar DOI si está disponible, sino combinación de título y autores
        if doi_normalizado and doi_normalizado != "sin doi":
            return f"doi:{doi_normalizado}"
        else:
            # Hash del título + primer autor
            primer_autor = evidencia.autores[0] if evidencia.autores else "unknown"
            texto = f"{evidencia.titulo.lower()}:{primer_autor.lower()}"
            return hashlib.md5(texto.encode()).hexdigest()

    def _normalizar_doi(self, doi: str) -> str:
        """Normalizar DOI"""
        if not doi or doi == "Sin DOI":
            return ""

        # Limpiar DOI
        doi_limpio = doi.lower().strip()
        doi_limpio = re.sub(r"^doi:", "", doi_limpio)
        doi_limpio = re.sub(r"^https?://doi\.org/", "", doi_limpio)

        return doi_limpio

    def _determinar_tipo_estudio(
        self, publication_types: List[str], titulo: str, resumen: str
    ) -> TipoEstudio:
        """Determinar tipo de estudio basado en publication types y contenido"""

        texto_completo = f"{titulo} {resumen}".lower()
        publication_types_lower = [pt.lower() for pt in publication_types]

        # Verificar publication types específicos
        if any(
            pt in publication_types_lower for pt in ["guideline", "practice guideline"]
        ):
            return TipoEstudio.GUIDELINE
        elif any(
            pt in publication_types_lower
            for pt in ["meta-analysis", "systematic review"]
        ):
            return TipoEstudio.META_ANALYSIS
        elif "systematic review" in publication_types_lower:
            return TipoEstudio.SYSTEMATIC_REVIEW
        elif any(
            pt in publication_types_lower
            for pt in ["randomized controlled trial", "clinical trial"]
        ):
            return TipoEstudio.RCT
        elif any(
            pt in publication_types_lower
            for pt in ["cohort study", "prospective study"]
        ):
            return TipoEstudio.COHORT
        elif any(pt in publication_types_lower for pt in ["case-control study"]):
            return TipoEstudio.CASE_CONTROL
        elif any(pt in publication_types_lower for pt in ["case series"]):
            return TipoEstudio.CASE_SERIES
        elif any(pt in publication_types_lower for pt in ["case report"]):
            return TipoEstudio.CASE_REPORT
        elif any(pt in publication_types_lower for pt in ["preprint"]):
            return TipoEstudio.PREPRINT

        # Verificar en texto si no hay publication types específicos
        if "randomized" in texto_completo and "trial" in texto_completo:
            return TipoEstudio.RCT
        elif "cohort" in texto_completo:
            return TipoEstudio.COHORT
        elif "case-control" in texto_completo:
            return TipoEstudio.CASE_CONTROL
        elif "case series" in texto_completo:
            return TipoEstudio.CASE_SERIES
        elif "case report" in texto_completo:
            return TipoEstudio.CASE_REPORT

        return TipoEstudio.OTHER

    def _aplicar_ranking_clinico(
        self, evidencias: List[EvidenciaCientifica], termino_busqueda: str
    ) -> List[EvidenciaCientifica]:
        """Aplicar ranking clínico basado en tipo de estudio y otros factores"""

        for evidencia in evidencias:
            # Score base del tipo de estudio
            score_tipo = self.tipo_estudio_prioridad.get(evidencia.tipo_estudio, 1)

            # Penalización por antigüedad (más de 10 años)
            año_actual = datetime.now().year
            if evidencia.año_publicacion != "N/A":
                try:
                    año_paper = int(evidencia.año_publicacion)
                    if año_actual - año_paper > 10:
                        score_tipo *= 0.7  # Penalización del 30%
                except ValueError:
                    pass

            # Penalización por preprint
            if evidencia.tipo_estudio == TipoEstudio.PREPRINT:
                score_tipo *= 0.5

            # Bonus por open access
            if evidencia.is_open_access:
                score_tipo *= 1.1

            # Bonus por full text disponible
            if evidencia.has_full_text:
                score_tipo *= 1.2

            # Combinar con relevancia existente
            evidencia.relevancia_score = (evidencia.relevancia_score * 0.6) + (
                score_tipo * 0.4
            )

        # Ordenar por relevancia
        evidencias_ranked = sorted(
            evidencias, key=lambda x: x.relevancia_score, reverse=True
        )

        return evidencias_ranked

    def _calcular_relevancia_score_mejorado(
        self,
        titulo: str,
        resumen: str,
        termino_busqueda: str,
        tipo_estudio: TipoEstudio,
        año_publicacion: str,
    ) -> float:
        """Calcular score de relevancia mejorado"""

        texto_completo = f"{titulo} {resumen}".lower()
        termino_lower = termino_busqueda.lower()

        # Score base por coincidencia de términos
        score = 0.0

        # Coincidencia exacta en título (máximo peso)
        if termino_lower in titulo.lower():
            score += 0.4

        # Coincidencia en resumen
        if termino_lower in resumen.lower():
            score += 0.3

        # Coincidencia de palabras individuales
        palabras_termino = termino_lower.split()
        palabras_texto = texto_completo.split()

        coincidencias = sum(
            1 for palabra in palabras_termino if palabra in palabras_texto
        )
        score += (coincidencias / len(palabras_termino)) * 0.2

        # Bonus por tipo de estudio
        score_tipo = self.tipo_estudio_prioridad.get(tipo_estudio, 1) / 10.0
        score += score_tipo * 0.1

        return min(score, 1.0)

    def _limpiar_termino_busqueda(self, termino: str) -> str:
        """Limpiar y traducir término de búsqueda para consultas clínicas"""
        termino_limpio = termino.strip().lower()

        # Remover palabras innecesarias para búsqueda médica
        palabras_remover = [
            "usuaria",
            "usuario",
            "paciente",
            "llega",
            "consulta",
            "con",
            "por",
            "en",
            "el",
            "la",
            "del",
            "de",
            "un",
            "una",
            "trabajo",
            "laboral",
            "accidente",
            "trauma",
            "traumático",
            "postraumático",
            "post",
            "después",
        ]

        for palabra in palabras_remover:
            termino_limpio = termino_limpio.replace(f" {palabra} ", " ")
            termino_limpio = termino_limpio.replace(f"{palabra} ", "")
            termino_limpio = termino_limpio.replace(f" {palabra}", "")

        # Traducir términos médicos específicos
        traducciones_medicas = {
            "dolor": "pain",
            "rodilla": "knee",
            "hombro": "shoulder",
            "espalda": "back",
            "lumbar": "low back",
            "cervical": "neck",
            "cadera": "hip",
            "tobillo": "ankle",
            "muñeca": "wrist",
            "codo": "elbow",
            "golpe": "trauma",
            "lesión": "injury",
            "fractura": "fracture",
            "esguince": "sprain",
            "luxación": "dislocation",
            "tendinitis": "tendinitis",
            "bursitis": "bursitis",
            "artritis": "arthritis",
            "artrosis": "osteoarthritis",
            "hernia": "hernia",
            "discal": "disc",
            "lumbar": "lumbar",
            "cervical": "cervical",
            "dorsal": "thoracic",
            "rehabilitación": "rehabilitation",
            "fisioterapia": "physical therapy",
            "kinesiología": "physical therapy",
            "terapia": "therapy",
            "tratamiento": "treatment",
            "ejercicio": "exercise",
            "ejercicios": "exercises",
            "movilización": "mobilization",
            "manipulación": "manipulation",
            "masaje": "massage",
            "electroterapia": "electrotherapy",
            "ultrasonido": "ultrasound",
            "termoterapia": "thermotherapy",
            "crioterapia": "cryotherapy",
            "tens": "tens",
            "estimulación": "stimulation",
            "neuromuscular": "neuromuscular",
            "funcional": "functional",
            "movimiento": "movement",
            "rango": "range",
            "amplitud": "motion",
            "fuerza": "strength",
            "resistencia": "resistance",
            "flexibilidad": "flexibility",
            "equilibrio": "balance",
            "coordinación": "coordination",
            "propriocepción": "proprioception",
            "estabilidad": "stability",
            "control": "control",
            "motor": "motor",
            "neurológico": "neurological",
            "músculo": "muscle",
            "músculos": "muscles",
            "muscular": "muscular",
            "ligamento": "ligament",
            "ligamentos": "ligaments",
            "tendón": "tendon",
            "tendones": "tendons",
            "articulación": "joint",
            "articulaciones": "joints",
            "hueso": "bone",
            "huesos": "bones",
            "nervio": "nerve",
            "nervios": "nerves",
            "nervioso": "nervous",
            "sistema": "system",
            "esquelético": "skeletal",
            "musculoesquelético": "musculoskeletal",
            "ortopédico": "orthopedic",
            "traumatológico": "traumatological",
            "deportivo": "sports",
            "deportiva": "sports",
            "laboral": "occupational",
            "ergonomía": "ergonomics",
            "postura": "posture",
            "postural": "postural",
            "biomecánica": "biomechanics",
            "biomecánico": "biomechanical",
            # Términos específicos para casos clínicos
            "en la rodilla": "knee",
            "de rodilla": "knee",
            "en el trabajo": "occupational",
            "por golpe": "trauma",
            "traumático": "trauma",
            "postraumático": "post-traumatic",
        }

        # Aplicar traducciones médicas
        for espanol, ingles in traducciones_medicas.items():
            if espanol in termino_limpio:
                termino_limpio = termino_limpio.replace(espanol, ingles)

        # Traducir términos generales en español
        for espanol, ingles in self.terminos_espanol_ingles.items():
            if espanol in termino_limpio:
                termino_limpio = termino_limpio.replace(espanol, ingles)

        # Limpiar espacios múltiples
        termino_limpio = " ".join(termino_limpio.split())

        # Si el término está muy corto o vacío, usar términos genéricos
        if len(termino_limpio.split()) < 2:
            if "knee" in termino_limpio or "rodilla" in termino:
                termino_limpio = "knee pain treatment"
            elif (
                "back" in termino_limpio or "espalda" in termino or "lumbar" in termino
            ):
                termino_limpio = "low back pain treatment"
            elif "shoulder" in termino_limpio or "hombro" in termino:
                termino_limpio = "shoulder pain treatment"
            else:
                termino_limpio = "musculoskeletal pain treatment"

        logger.info(f"🔍 Término original: {termino}")
        logger.info(f"🔍 Término procesado: {termino_limpio}")

        return termino_limpio

    def _generar_terminos_generales(self, termino: str) -> str:
        """Genera términos de búsqueda más generales cuando no hay resultados"""
        termino_limpio = self._limpiar_termino_busqueda(termino)

        # Mapeo de términos específicos a términos generales
        mapeo_general = {
            "knee": "musculoskeletal",
            "shoulder": "musculoskeletal",
            "back": "musculoskeletal",
            "low back": "musculoskeletal",
            "neck": "musculoskeletal",
            "hip": "musculoskeletal",
            "ankle": "musculoskeletal",
            "wrist": "musculoskeletal",
            "elbow": "musculoskeletal",
            "pain": "pain",
            "injury": "injury",
            "trauma": "trauma",
            "fracture": "fracture",
            "sprain": "sprain",
            "dislocation": "dislocation",
            "tendinitis": "tendinitis",
            "bursitis": "bursitis",
            "arthritis": "arthritis",
            "osteoarthritis": "osteoarthritis",
            "hernia": "hernia",
            "disc": "disc",
            "physical therapy": "physical therapy",
            "rehabilitation": "rehabilitation",
            "therapy": "therapy",
            "treatment": "treatment",
            "exercise": "exercise",
            "mobilization": "mobilization",
            "manipulation": "manipulation",
            "massage": "massage",
            "electrotherapy": "electrotherapy",
            "ultrasound": "ultrasound",
            "thermotherapy": "thermotherapy",
            "cryotherapy": "cryotherapy",
        }

        # Extraer palabras clave del término
        palabras = termino_limpio.split()
        palabras_generales = []

        for palabra in palabras:
            if palabra in mapeo_general:
                palabras_generales.append(mapeo_general[palabra])
            else:
                palabras_generales.append(palabra)

        # Generar términos de búsqueda generales
        termino_general = " ".join(palabras_generales)

        # Si el término es muy específico, usar términos más generales
        if len(palabras_generales) > 3:
            # Tomar solo las 2-3 palabras más importantes
            termino_general = " ".join(palabras_generales[:3])

        # Asegurar que tenga al menos "treatment" o "therapy"
        if "treatment" not in termino_general and "therapy" not in termino_general:
            termino_general += " treatment"

        logger.info(f"🔍 Término general generado: {termino_general}")
        return termino_general

    def _determinar_nivel_evidencia(self, titulo: str, resumen: str) -> str:
        """Determinar nivel de evidencia basado en contenido"""
        texto = f"{titulo} {resumen}".lower()

        if any(
            palabra in texto
            for palabra in ["meta-analysis", "systematic review", "guideline"]
        ):
            return "Nivel I"
        elif any(
            palabra in texto for palabra in ["randomized controlled trial", "rct"]
        ):
            return "Nivel II"
        elif any(palabra in texto for palabra in ["cohort study", "case-control"]):
            return "Nivel III"
        elif any(palabra in texto for palabra in ["case series", "case report"]):
            return "Nivel IV"
        else:
            return "Nivel V"

    def _evidencia_to_dict(self, evidencia: EvidenciaCientifica) -> Dict:
        """Convertir evidencia a diccionario para cache"""
        return {
            "titulo": evidencia.titulo,
            "autores": evidencia.autores,
            "doi": evidencia.doi,
            "fecha_publicacion": evidencia.fecha_publicacion,
            "resumen": evidencia.resumen,
            "nivel_evidencia": evidencia.nivel_evidencia,
            "fuente": evidencia.fuente,
            "url": evidencia.url,
            "relevancia_score": evidencia.relevancia_score,
            "keywords": evidencia.keywords,
            "año_publicacion": evidencia.año_publicacion,
            "tipo_evidencia": evidencia.tipo_evidencia,
            "pmid": evidencia.pmid,
            "pmcid": evidencia.pmcid,
            "tipo_estudio": evidencia.tipo_estudio.value,
            "journal": evidencia.journal,
            "volumen": evidencia.volumen,
            "numero": evidencia.numero,
            "paginas": evidencia.paginas,
            "is_open_access": evidencia.is_open_access,
            "has_full_text": evidencia.has_full_text,
            "publication_types": evidencia.publication_types,
            "clave_unica": evidencia.clave_unica,
        }

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


# Instancia global del sistema mejorado
unified_search_enhanced = UnifiedScientificSearchEnhanced()


def test_enhanced_search():
    """Función de prueba para el sistema mejorado"""
    print("🧪 Probando Sistema Unificado de Búsqueda Científica Mejorado")
    print("=" * 70)

    # Casos de prueba
    casos_prueba = [
        {
            "termino": "low back pain treatment",
            "filtros": FiltrosBusqueda(
                peer_reviewed_only=True,
                year_from=2015,
                study_designs=[TipoEstudio.RCT, TipoEstudio.META_ANALYSIS],
            ),
        },
        {
            "termino": "fibromyalgia therapy",
            "filtros": FiltrosBusqueda(open_access_only=True, year_from=2020),
        },
    ]

    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🔍 Caso de prueba {i}: {caso['termino']}")

        start_time = time.time()
        evidencias = unified_search_enhanced.buscar_evidencia_unificada(
            caso["termino"], filtros=caso["filtros"]
        )
        tiempo = time.time() - start_time

        print(f"   ✅ Tiempo: {tiempo:.2f}s")
        print(f"   📊 Resultados: {len(evidencias)}")

        if evidencias:
            # Mostrar top 3 resultados
            for j, evidencia in enumerate(evidencias[:3], 1):
                print(f"   {j}. {evidencia.titulo[:80]}...")
                print(
                    f"      📚 {evidencia.tipo_estudio.value} | {evidencia.año_publicacion}"
                )
                print(
                    f"      📊 Score: {evidencia.relevancia_score:.2f} | OA: {evidencia.is_open_access}"
                )
                print(f"      📝 Cita: {evidencia.cita_apa[:100]}...")
                print()

        print(f"   🔄 Deduplicadas: {len(set(ev.clave_unica for ev in evidencias))}")

    print("\n✅ Todas las pruebas completadas!")


if __name__ == "__main__":
    test_enhanced_search()
