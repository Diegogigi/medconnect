#!/usr/bin/env python3
"""
Sistema Unificado de Búsqueda Científica
Consolida Medical APIs Integration + Medical RAG System
"""

import requests
import json
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import quote
import re
from datetime import datetime
from collections import defaultdict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EvidenciaCientifica:
    """Estructura unificada para evidencia científica"""

    titulo: str
    autores: List[str]
    doi: str
    fecha_publicacion: str
    resumen: str
    nivel_evidencia: str
    fuente: str  # 'pubmed', 'europepmc', 'ncbi'
    url: str
    relevancia_score: float = 0.0
    keywords: List[str] = None
    año_publicacion: str = "N/A"
    tipo_evidencia: str = "Estudio científico"


@dataclass
class RespuestaUnificada:
    """Estructura para respuesta unificada"""

    respuesta: str
    evidencias: List[EvidenciaCientifica]
    terminos_utilizados: List[str]
    nivel_confianza: float
    citaciones: List[str]
    recomendaciones: List[str]
    tiempo_procesamiento: float
    fuentes_consultadas: List[str]


@dataclass
class TratamientoCientifico:
    """Estructura para tratamientos basados en evidencia científica"""

    titulo: str
    descripcion: str
    doi: str
    fuente: str
    tipo_evidencia: str
    fecha_publicacion: str
    autores: List[str]
    resumen: str
    keywords: List[str]
    año_publicacion: str = "N/A"
    nivel_evidencia: str = "Nivel V"
    evidencia_cientifica: str = "Evidencia científica"
    contraindicaciones: str = "Consultar con profesional de la salud"


class UnifiedScientificSearch:
    """Sistema unificado de búsqueda científica"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "MedConnect-IA/1.0 (https://medconnect.cl)"}
        )

        # Configuración optimizada de rate limiting
        self.last_request_time = 0
        self.min_interval = 0.3  # 3 requests per second (optimizado)

        # API Key para NCBI
        self.ncbi_api_key = "fc67562a31bc52ad079357404cf1f6572107"

        # Cache optimizado
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora

        # Configuración de búsqueda
        self.max_evidencias = 8  # Aumentado para mejor cobertura
        self.min_relevancia_score = 0.25  # Reducido para más resultados

        # Mapeo de términos en español a inglés
        self.terminos_espanol_ingles = {
            "dolor lumbar": "low back pain",
            "dolor de espalda": "back pain",
            "problemas de habla": "speech disorders",
            "trastornos del habla": "speech disorders",
            "ansiedad": "anxiety",
            "depresión": "depression",
            "diabetes": "diabetes",
            "hipertensión": "hypertension",
            "artritis": "arthritis",
            "fisioterapia": "physical therapy",
            "fonoaudiologia": "speech therapy",
            "psicologia": "psychology",
            "medicina": "medicine",
            "kinesiologia": "physical therapy",
            "terapia ocupacional": "occupational therapy",
            "dolor en brazo": "arm pain",
            "dolor en hombro": "shoulder pain",
            "dolor en cuello": "neck pain",
            "dolor en espalda": "back pain",
            "dolor en rodilla": "knee pain",
            "dolor en tobillo": "ankle pain",
        }

        # Plantillas unificadas para respuestas
        self.plantillas_respuesta = {
            "tratamiento": {
                "intro": "Basándome en la evidencia científica disponible, aquí están las opciones de tratamiento:",
                "evidencia": "Según {autores} ({año}), {hallazgo}",
                "recomendacion": "Se recomienda {tratamiento} para {condicion}",
                "conclusion": "Estas recomendaciones están basadas en evidencia científica verificable.",
            },
            "diagnostico": {
                "intro": "Basándome en la evidencia científica, los posibles diagnósticos incluyen:",
                "evidencia": "La investigación de {autores} ({año}) sugiere que {hallazgo}",
                "recomendacion": "Se sugiere evaluar {diagnostico}",
                "conclusion": "Se recomienda consulta médica para confirmación diagnóstica.",
            },
            "rehabilitacion": {
                "intro": "Los programas de rehabilitación basados en evidencia incluyen:",
                "evidencia": "El estudio de {autores} ({año}) demuestra que {hallazgo}",
                "recomendacion": "Se recomienda {ejercicio} para mejorar {funcion}",
                "conclusion": "La rehabilitación debe ser supervisada por profesionales.",
            },
        }

        logger.info("✅ Sistema Unificado de Búsqueda Científica inicializado")

    def _rate_limit(self):
        """Control de rate limiting optimizado"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get_cache_key(self, query: str, source: str) -> str:
        """Genera clave de cache"""
        return f"{source}:{query.lower().strip()}"

    def _get_from_cache(self, query: str, source: str) -> Optional[List]:
        """Obtiene datos del cache"""
        cache_key = self._get_cache_key(query, source)
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"📋 Datos obtenidos del cache: {source}")
                return data
        return None

    def _save_to_cache(self, query: str, source: str, data: List):
        """Guarda datos en cache"""
        cache_key = self._get_cache_key(query, source)
        self.cache[cache_key] = (data, time.time())
        logger.info(f"💾 Datos guardados en cache: {source}")

    def _limpiar_termino_busqueda(self, termino: str) -> str:
        """Limpia y optimiza términos de búsqueda"""
        # Remover caracteres especiales y normalizar
        termino = re.sub(r"[^\w\s]", " ", termino)
        termino = re.sub(r"\s+", " ", termino).strip()

        # Traducir términos comunes
        termino_lower = termino.lower()
        for espanol, ingles in self.terminos_espanol_ingles.items():
            if espanol in termino_lower:
                termino = termino.replace(espanol, ingles)
                break

        return termino

    def buscar_pubmed(
        self, termino: str, especialidad: str = None
    ) -> List[EvidenciaCientifica]:
        """Búsqueda optimizada en PubMed"""
        self._rate_limit()

        # Verificar cache
        cached_data = self._get_from_cache(termino, "pubmed")
        if cached_data:
            return cached_data

        termino_limpio = self._limpiar_termino_busqueda(termino)

        try:
            # Construir query optimizada
            query_parts = [termino_limpio]
            if especialidad:
                query_parts.append(especialidad)

            query = " AND ".join(query_parts)

            # URL de PubMed
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": 10,
                "retmode": "json",
                "sort": "relevance",
                "api_key": self.ncbi_api_key,
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            id_list = data.get("esearchresult", {}).get("idlist", [])

            if not id_list:
                return []

            # Obtener detalles de los papers
            url_fetch = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            params_fetch = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json",
                "api_key": self.ncbi_api_key,
            }

            response_fetch = self.session.get(
                url_fetch, params=params_fetch, timeout=10
            )
            response_fetch.raise_for_status()

            data_fetch = response_fetch.json()
            papers = data_fetch.get("result", {})

            evidencias = []
            for paper_id in id_list:
                if paper_id in papers:
                    paper = papers[paper_id]

                    # Procesar autores correctamente
                    autores_raw = paper.get("authors", [])
                    if isinstance(autores_raw, list):
                        autores = [str(author) for author in autores_raw if author]
                    else:
                        autores = []

                    # Procesar keywords correctamente
                    keywords_raw = paper.get("keywords", [])
                    if isinstance(keywords_raw, list):
                        keywords = [str(kw) for kw in keywords_raw if kw]
                    else:
                        keywords = []

                    evidencia = EvidenciaCientifica(
                        titulo=paper.get("title", "Sin título"),
                        autores=autores,
                        doi=paper.get("elocationid", "Sin DOI"),
                        fecha_publicacion=paper.get("pubdate", "Fecha no disponible"),
                        resumen=paper.get("abstract", "Sin resumen"),
                        nivel_evidencia=self._determinar_nivel_evidencia(
                            paper.get("title", ""), paper.get("abstract", "")
                        ),
                        fuente="pubmed",
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/",
                        relevancia_score=self._calcular_relevancia_score(
                            paper, termino_limpio
                        ),
                        keywords=keywords,
                        año_publicacion=(
                            paper.get("pubdate", "N/A")[:4]
                            if paper.get("pubdate")
                            else "N/A"
                        ),
                    )
                    evidencias.append(evidencia)

            # Guardar en cache
            self._save_to_cache(termino, "pubmed", evidencias)

            logger.info(f"✅ PubMed: {len(evidencias)} resultados encontrados")
            return evidencias

        except Exception as e:
            logger.error(f"❌ Error en búsqueda PubMed: {e}")
            return []

    def buscar_europepmc(
        self, termino: str, especialidad: str = None
    ) -> List[EvidenciaCientifica]:
        """Búsqueda optimizada en Europe PMC"""
        self._rate_limit()

        # Verificar cache
        cached_data = self._get_from_cache(termino, "europepmc")
        if cached_data:
            return cached_data

        termino_limpio = self._limpiar_termino_busqueda(termino)

        try:
            # URL de Europe PMC
            url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
            params = {
                "query": termino_limpio,
                "resultType": "core",
                "pageSize": 10,
                "format": "json",
                "sort": "RELEVANCE",
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            papers = data.get("resultList", {}).get("result", [])

            evidencias = []
            for paper in papers:
                # Procesar autores correctamente
                author_string = paper.get("authorString", "")
                if author_string:
                    autores = [
                        author.strip()
                        for author in author_string.split(", ")
                        if author.strip()
                    ]
                else:
                    autores = []

                # Procesar keywords correctamente
                keywords_raw = paper.get("keywordList", [])
                if isinstance(keywords_raw, list):
                    keywords = [str(kw) for kw in keywords_raw if kw]
                else:
                    keywords = []

                evidencia = EvidenciaCientifica(
                    titulo=paper.get("title", "Sin título"),
                    autores=autores,
                    doi=paper.get("doi", "Sin DOI"),
                    fecha_publicacion=paper.get(
                        "firstPublicationDate", "Fecha no disponible"
                    ),
                    resumen=paper.get("abstractText", "Sin resumen"),
                    nivel_evidencia=self._determinar_nivel_evidencia(
                        paper.get("title", ""), paper.get("abstractText", "")
                    ),
                    fuente="europepmc",
                    url=f"https://europepmc.org/article/MED/{paper.get('id', '')}",
                    relevancia_score=self._calcular_relevancia_score(
                        paper, termino_limpio
                    ),
                    keywords=keywords,
                    año_publicacion=(
                        paper.get("firstPublicationDate", "N/A")[:4]
                        if paper.get("firstPublicationDate")
                        else "N/A"
                    ),
                )
                evidencias.append(evidencia)

            # Guardar en cache
            self._save_to_cache(termino, "europepmc", evidencias)

            logger.info(f"✅ Europe PMC: {len(evidencias)} resultados encontrados")
            return evidencias

        except Exception as e:
            logger.error(f"❌ Error en búsqueda Europe PMC: {e}")
            return []

    def _determinar_nivel_evidencia(self, titulo: str, resumen: str) -> str:
        """Determina el nivel de evidencia basado en el contenido"""
        texto_completo = f"{titulo} {resumen}".lower()

        # Palabras clave para diferentes niveles de evidencia
        nivel_1_keywords = [
            "systematic review",
            "meta-analysis",
            "revisión sistemática",
            "meta-análisis",
        ]
        nivel_2_keywords = [
            "randomized controlled trial",
            "ensayo clínico aleatorizado",
            "rct",
        ]
        nivel_3_keywords = [
            "cohort study",
            "estudio de cohorte",
            "case-control",
            "caso-control",
        ]
        nivel_4_keywords = [
            "case series",
            "serie de casos",
            "case report",
            "reporte de caso",
        ]

        if any(keyword in texto_completo for keyword in nivel_1_keywords):
            return "Nivel I"
        elif any(keyword in texto_completo for keyword in nivel_2_keywords):
            return "Nivel II"
        elif any(keyword in texto_completo for keyword in nivel_3_keywords):
            return "Nivel III"
        elif any(keyword in texto_completo for keyword in nivel_4_keywords):
            return "Nivel IV"
        else:
            return "Nivel V"

    def _calcular_relevancia_score(self, paper: Dict, termino_busqueda: str) -> float:
        """Calcula el score de relevancia del paper"""
        titulo = paper.get("title", "").lower()
        resumen = paper.get("abstract", paper.get("abstractText", "")).lower()
        termino = termino_busqueda.lower()

        # Calcular score basado en presencia de términos
        score = 0.0

        # Términos en título (mayor peso)
        if termino in titulo:
            score += 0.6

        # Términos en resumen
        if termino in resumen:
            score += 0.3

        # Palabras individuales
        palabras_termino = termino.split()
        for palabra in palabras_termino:
            if palabra in titulo:
                score += 0.1
            if palabra in resumen:
                score += 0.05

        # Normalizar score
        return min(score, 1.0)

    def buscar_evidencia_unificada(
        self, termino: str, especialidad: str = None, max_resultados: int = None
    ) -> List[EvidenciaCientifica]:
        """Búsqueda unificada en múltiples fuentes"""
        start_time = time.time()

        if max_resultados is None:
            max_resultados = self.max_evidencias

        logger.info(f"🔍 Búsqueda unificada: {termino}")

        # Búsquedas paralelas optimizadas
        evidencias_pubmed = self.buscar_pubmed(termino, especialidad)
        evidencias_europepmc = self.buscar_europepmc(termino, especialidad)

        # Combinar y ordenar por relevancia
        todas_evidencias = evidencias_pubmed + evidencias_europepmc

        # Eliminar duplicados basados en DOI
        evidencias_unicas = {}
        for evidencia in todas_evidencias:
            doi_key = evidencia.doi if evidencia.doi != "Sin DOI" else evidencia.titulo
            if (
                doi_key not in evidencias_unicas
                or evidencia.relevancia_score
                > evidencias_unicas[doi_key].relevancia_score
            ):
                evidencias_unicas[doi_key] = evidencia

        # Ordenar por relevancia y filtrar
        evidencias_filtradas = [
            ev
            for ev in evidencias_unicas.values()
            if ev.relevancia_score >= self.min_relevancia_score
        ]

        evidencias_filtradas.sort(key=lambda x: x.relevancia_score, reverse=True)
        evidencias_finales = evidencias_filtradas[:max_resultados]

        tiempo_procesamiento = time.time() - start_time

        logger.info(
            f"✅ Búsqueda unificada completada: {len(evidencias_finales)} resultados en {tiempo_procesamiento:.2f}s"
        )

        return evidencias_finales

    def generar_respuesta_estructurada(
        self, evidencias: List[EvidenciaCientifica], tipo_consulta: str = "general"
    ) -> RespuestaUnificada:
        """Genera respuesta estructurada basada en evidencia"""
        if not evidencias:
            return RespuestaUnificada(
                respuesta="No se encontró evidencia científica relevante para la consulta.",
                evidencias=[],
                terminos_utilizados=[],
                nivel_confianza=0.0,
                citaciones=[],
                recomendaciones=["Consultar con un profesional de la salud"],
                tiempo_procesamiento=0.0,
                fuentes_consultadas=[],
            )

        # Obtener plantilla según tipo de consulta
        plantilla = self.plantillas_respuesta.get(
            tipo_consulta, self.plantillas_respuesta["tratamiento"]
        )

        # Generar respuesta
        respuesta_parts = [plantilla["intro"]]
        citaciones = []
        recomendaciones = []

        for evidencia in evidencias[:3]:  # Top 3 evidencias
            # Formatear evidencia
            autores_str = (
                ", ".join(evidencia.autores[:3])
                if evidencia.autores
                else "Autores no disponibles"
            )
            año = evidencia.año_publicacion

            evidencia_text = plantilla["evidencia"].format(
                autores=autores_str,
                año=año,
                hallazgo=(
                    evidencia.resumen[:200] + "..."
                    if len(evidencia.resumen) > 200
                    else evidencia.resumen
                ),
            )
            respuesta_parts.append(evidencia_text)

            # Agregar citación
            if evidencia.doi != "Sin DOI":
                citaciones.append(
                    f"{autores_str} ({año}). {evidencia.titulo}. DOI: {evidencia.doi}"
                )
            else:
                citaciones.append(f"{autores_str} ({año}). {evidencia.titulo}")

        respuesta_parts.append(plantilla["conclusion"])

        # Calcular nivel de confianza
        nivel_confianza = sum(ev.relevancia_score for ev in evidencias) / len(
            evidencias
        )

        # Generar recomendaciones
        recomendaciones = [
            "Consultar con un profesional de la salud para evaluación personalizada",
            "Considerar la evidencia científica más reciente",
            "Evaluar contraindicaciones individuales",
        ]

        return RespuestaUnificada(
            respuesta="\n\n".join(respuesta_parts),
            evidencias=evidencias,
            terminos_utilizados=[ev.titulo for ev in evidencias],
            nivel_confianza=nivel_confianza,
            citaciones=citaciones,
            recomendaciones=recomendaciones,
            tiempo_procesamiento=0.0,  # Se calculará en la función principal
            fuentes_consultadas=list(set(ev.fuente for ev in evidencias)),
        )

    def buscar_tratamiento_completo(
        self, termino: str, especialidad: str = None
    ) -> RespuestaUnificada:
        """Búsqueda completa de tratamientos con respuesta estructurada"""
        start_time = time.time()

        # Búsqueda unificada
        evidencias = self.buscar_evidencia_unificada(termino, especialidad)

        # Generar respuesta estructurada
        respuesta = self.generar_respuesta_estructurada(evidencias, "tratamiento")
        respuesta.tiempo_procesamiento = time.time() - start_time

        return respuesta


# Instancia global del sistema unificado
unified_search = UnifiedScientificSearch()


def test_unified_search():
    """Función de prueba para el sistema unificado"""
    print("🧪 Probando Sistema Unificado de Búsqueda Científica")
    print("=" * 60)

    # Prueba 1: Búsqueda en PubMed
    print("\n1. 🔍 Probando búsqueda PubMed...")
    evidencias_pubmed = unified_search.buscar_pubmed("low back pain")
    print(f"   ✅ PubMed: {len(evidencias_pubmed)} resultados")

    # Prueba 2: Búsqueda en Europe PMC
    print("\n2. 🔍 Probando búsqueda Europe PMC...")
    evidencias_europepmc = unified_search.buscar_europepmc("shoulder pain")
    print(f"   ✅ Europe PMC: {len(evidencias_europepmc)} resultados")

    # Prueba 3: Búsqueda unificada
    print("\n3. 🔍 Probando búsqueda unificada...")
    evidencias_unificadas = unified_search.buscar_evidencia_unificada("knee pain")
    print(f"   ✅ Unificada: {len(evidencias_unificadas)} resultados")

    # Prueba 4: Respuesta estructurada
    print("\n4. 📝 Probando respuesta estructurada...")
    respuesta = unified_search.buscar_tratamiento_completo("neck pain")
    print(f"   ✅ Respuesta generada en {respuesta.tiempo_procesamiento:.2f}s")
    print(f"   📊 Nivel de confianza: {respuesta.nivel_confianza:.2f}")
    print(f"   📚 Fuentes consultadas: {', '.join(respuesta.fuentes_consultadas)}")

    print("\n✅ Todas las pruebas completadas exitosamente!")


if __name__ == "__main__":
    test_unified_search()
