#!/usr/bin/env python3
"""
Módulo Mejorado para Asignación de Citas por Oración
Implementa RapidFuzz para similitud precisa y asignación automática de citas
"""

import logging
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from rapidfuzz import fuzz, process

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Metadatos de chunk para asignación de citas"""

    text: str
    source: str  # "pmid:1234" o "chunk_id"
    span: Tuple[int, int]  # (start, end)
    meta: Dict[str, Any]  # Metadatos completos del chunk
    apa_citation: str = ""
    relevancia_score: float = 0.0
    entidades_clave: List[str] = field(default_factory=list)


@dataclass
class SentenceCitation:
    """Cita asignada a una oración"""

    sentence: str
    citations: List[str]  # Lista de citas APA
    chunks_soporte: List[str]  # IDs de chunks que soportan
    similitud_scores: List[float]  # Scores de similitud
    confianza_global: float = 0.0
    entidades_compartidas: List[str] = field(default_factory=list)


class CitationAssignerEnhanced:
    """Asignador mejorado de citas por oración usando RapidFuzz"""

    def __init__(self, sim_threshold: float = 0.65, top_k: int = 3):
        self.sim_threshold = sim_threshold
        self.top_k = top_k
        self.fuzz_scorer = fuzz.token_set_ratio
        logger.info(
            f"🎯 CitationAssigner inicializado con threshold={sim_threshold}, top_k={top_k}"
        )

    def attach_citations_to_sentences(
        self, sentences: List[str], chunks: List[ChunkMetadata]
    ) -> List[SentenceCitation]:
        """Asigna citas a oraciones usando RapidFuzz"""
        logger.info(
            f"🔍 Asignando citas a {len(sentences)} oraciones usando {len(chunks)} chunks"
        )

        sentence_citations = []

        for sentence in sentences:
            # Encontrar los mejores chunks para esta oración
            best_chunks = self._find_best_chunks(sentence, chunks)

            # Filtrar por umbral de similitud
            cited_chunks = [
                chunk
                for chunk in best_chunks
                if self.fuzz_scorer(sentence, chunk.text)
                >= int(self.sim_threshold * 100)
            ]

            # Extraer citas APA
            citations = [
                chunk.apa_citation for chunk in cited_chunks if chunk.apa_citation
            ]
            chunks_soporte = [chunk.source for chunk in cited_chunks]
            similitud_scores = [
                self.fuzz_scorer(sentence, chunk.text) / 100.0 for chunk in cited_chunks
            ]

            # Calcular confianza global
            confianza_global = self._calcular_confianza_global(
                sentence, cited_chunks, similitud_scores
            )

            # Extraer entidades compartidas
            entidades_compartidas = self._extraer_entidades_compartidas(
                sentence, cited_chunks
            )

            # Crear objeto de cita
            sentence_citation = SentenceCitation(
                sentence=sentence,
                citations=citations,
                chunks_soporte=chunks_soporte,
                similitud_scores=similitud_scores,
                confianza_global=confianza_global,
                entidades_compartidas=entidades_compartidas,
            )

            sentence_citations.append(sentence_citation)

            logger.debug(f"📝 Oración: {sentence[:50]}... → {len(citations)} citas")

        logger.info(
            f"✅ Asignación completada: {sum(len(sc.citations) for sc in sentence_citations)} citas totales"
        )
        return sentence_citations

    def _find_best_chunks(
        self, sentence: str, chunks: List[ChunkMetadata]
    ) -> List[ChunkMetadata]:
        """Encuentra los mejores chunks para una oración usando RapidFuzz"""
        chunk_texts = [chunk.text for chunk in chunks]

        # Obtener top_k matches con scores
        matches = process.extract(
            sentence, chunk_texts, scorer=self.fuzz_scorer, limit=self.top_k
        )

        # Mapear de vuelta a los chunks originales
        best_chunks = []
        for match_data in matches:
            # process.extract devuelve tuplas (texto, score, index)
            if len(match_data) >= 2:
                match_text, score = match_data[0], match_data[1]
                for chunk in chunks:
                    if chunk.text == match_text:
                        chunk.relevancia_score = score / 100.0
                        best_chunks.append(chunk)
                        break

        return best_chunks

    def _calcular_confianza_global(
        self,
        sentence: str,
        cited_chunks: List[ChunkMetadata],
        similitud_scores: List[float],
    ) -> float:
        """Calcula confianza global basada en múltiples factores"""
        if not cited_chunks:
            return 0.0

        # Factor 1: Similitud promedio
        similitud_promedio = sum(similitud_scores) / len(similitud_scores)

        # Factor 2: Número de chunks de soporte
        factor_soporte = min(len(cited_chunks) / 3.0, 1.0)

        # Factor 3: Calidad de las fuentes
        factor_fuentes = self._calcular_factor_fuentes(cited_chunks)

        # Factor 4: Entidades compartidas
        factor_entidades = self._calcular_factor_entidades(sentence, cited_chunks)

        # Combinar factores
        confianza = (
            similitud_promedio * 0.4
            + factor_soporte * 0.2
            + factor_fuentes * 0.2
            + factor_entidades * 0.2
        )

        return min(1.0, max(0.0, confianza))

    def _calcular_factor_fuentes(self, chunks: List[ChunkMetadata]) -> float:
        """Calcula factor de calidad de fuentes"""
        if not chunks:
            return 0.0

        fuentes_preferidas = ["pubmed", "pmc", "europepmc"]
        factor = 0.0

        for chunk in chunks:
            source_lower = chunk.source.lower()
            if any(pref in source_lower for pref in fuentes_preferidas):
                factor += 1.0

        return factor / len(chunks)

    def _calcular_factor_entidades(
        self, sentence: str, chunks: List[ChunkMetadata]
    ) -> float:
        """Calcula factor basado en entidades compartidas"""
        if not chunks:
            return 0.0

        entidades_sentence = self._extraer_entidades(sentence)

        total_entidades_compartidas = 0
        for chunk in chunks:
            entidades_chunk = chunk.entidades_clave
            entidades_compartidas = set(entidades_sentence) & set(entidades_chunk)
            total_entidades_compartidas += len(entidades_compartidas)

        return min(total_entidades_compartidas / (len(chunks) * 5.0), 1.0)

    def _extraer_entidades(self, text: str) -> List[str]:
        """Extrae entidades clave del texto"""
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
            "paciente",
            "estudio",
            "resultado",
            "efecto",
            "beneficio",
        ]

        encontradas = []
        text_lower = text.lower()
        for entidad in entidades_clave:
            if entidad in text_lower:
                encontradas.append(entidad)

        return encontradas

    def _extraer_entidades_compartidas(
        self, sentence: str, chunks: List[ChunkMetadata]
    ) -> List[str]:
        """Extrae entidades compartidas entre oración y chunks"""
        entidades_sentence = self._extraer_entidades(sentence)
        entidades_compartidas = set(entidades_sentence)

        for chunk in chunks:
            entidades_chunk = chunk.entidades_clave
            entidades_compartidas &= set(entidades_chunk)

        return list(entidades_compartidas)


# Función de conveniencia para uso directo
def attach_citations_to_sentences_enhanced(
    sentences: List[str], chunks: List[Dict[str, Any]], sim_threshold: float = 0.65
) -> List[Dict[str, Any]]:
    """Función de conveniencia para asignar citas a oraciones"""
    # Convertir chunks a ChunkMetadata
    chunk_metadata_list = []
    for chunk in chunks:
        chunk_meta = ChunkMetadata(
            text=chunk["text"],
            source=chunk["source"],
            span=chunk["span"],
            meta=chunk["meta"],
            apa_citation=chunk.get("meta", {}).get("apa", ""),
            relevancia_score=chunk.get("relevancia_score", 0.0),
            entidades_clave=chunk.get("entidades_clave", []),
        )
        chunk_metadata_list.append(chunk_meta)

    # Crear asignador y asignar citas
    assigner = CitationAssignerEnhanced(sim_threshold=sim_threshold)
    sentence_citations = assigner.attach_citations_to_sentences(
        sentences, chunk_metadata_list
    )

    # Convertir a formato de salida
    result = []
    for sc in sentence_citations:
        result.append(
            {
                "sentence": sc.sentence,
                "citations": sc.citations,
                "chunks_soporte": sc.chunks_soporte,
                "confianza": sc.confianza_global,
                "entidades_compartidas": sc.entidades_compartidas,
            }
        )

    return result


# Instancia global para uso en otros módulos
citation_assigner_enhanced = CitationAssignerEnhanced()
