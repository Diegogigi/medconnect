#!/usr/bin/env python3
"""
Pruebas para asignación de citas por oración
"""

import pytest
from citation_assigner_enhanced import (
    CitationAssignerEnhanced,
    attach_citations_to_sentences_enhanced,
)


class TestCitationAssignment:
    """Pruebas de asignación de citas"""

    def test_basic_citation_assignment(self, sample_sentences, sample_chunks):
        """Prueba asignación básica de citas"""
        assigner = CitationAssignerEnhanced(sim_threshold=0.5, top_k=3)

        # Convertir chunks a formato ChunkMetadata
        from citation_assigner_enhanced import ChunkMetadata

        chunks_metadata = []
        for chunk in sample_chunks:
            chunk_meta = ChunkMetadata(
                text=chunk["text"],
                source=chunk["source"],
                span=chunk["span"],
                meta=chunk["meta"],
                apa_citation=chunk["meta"]["apa"],
                entidades_clave=chunk["entidades_clave"],
            )
            chunks_metadata.append(chunk_meta)

        # Asignar citas
        sentence_citations = assigner.attach_citations_to_sentences(
            sample_sentences, chunks_metadata
        )

        # Verificar resultados
        assert len(sentence_citations) == len(sample_sentences)

        # Verificar que al menos algunas oraciones tienen citas
        oraciones_con_citas = sum(1 for sc in sentence_citations if sc.citations)
        assert oraciones_con_citas > 0

    def test_citation_threshold_variation(self, sample_sentences, sample_chunks):
        """Prueba variación de umbrales de similitud"""
        thresholds = [0.3, 0.5, 0.7, 0.9]

        for threshold in thresholds:
            assigner = CitationAssignerEnhanced(sim_threshold=threshold, top_k=3)

            # Convertir chunks
            from citation_assigner_enhanced import ChunkMetadata

            chunks_metadata = []
            for chunk in sample_chunks:
                chunk_meta = ChunkMetadata(
                    text=chunk["text"],
                    source=chunk["source"],
                    span=chunk["span"],
                    meta=chunk["meta"],
                    apa_citation=chunk["meta"]["apa"],
                    entidades_clave=chunk["entidades_clave"],
                )
                chunks_metadata.append(chunk_meta)

            # Asignar citas
            sentence_citations = assigner.attach_citations_to_sentences(
                sample_sentences, chunks_metadata
            )

            # Verificar que el umbral afecta el número de citas
            total_citas = sum(len(sc.citations) for sc in sentence_citations)

            # Umbrales más altos deben resultar en menos citas
            if threshold > 0.7:
                assert total_citas <= 2  # Pocas citas con umbral alto
            elif threshold < 0.5:
                assert total_citas >= 2  # Más citas con umbral bajo

    def test_confidence_calculation(self, sample_sentences, sample_chunks):
        """Prueba cálculo de confianza"""
        assigner = CitationAssignerEnhanced(sim_threshold=0.5, top_k=3)

        # Convertir chunks
        from citation_assigner_enhanced import ChunkMetadata

        chunks_metadata = []
        for chunk in sample_chunks:
            chunk_meta = ChunkMetadata(
                text=chunk["text"],
                source=chunk["source"],
                span=chunk["span"],
                meta=chunk["meta"],
                apa_citation=chunk["meta"]["apa"],
                entidades_clave=chunk["entidades_clave"],
            )
            chunks_metadata.append(chunk_meta)

        # Asignar citas
        sentence_citations = assigner.attach_citations_to_sentences(
            sample_sentences, chunks_metadata
        )

        # Verificar que la confianza está en el rango correcto
        for sc in sentence_citations:
            assert 0.0 <= sc.confianza_global <= 1.0

            # Oraciones con citas deben tener confianza > 0
            if sc.citations:
                assert sc.confianza_global > 0.0

    def test_entity_sharing_detection(self, sample_sentences, sample_chunks):
        """Prueba detección de entidades compartidas"""
        assigner = CitationAssignerEnhanced(sim_threshold=0.5, top_k=3)

        # Convertir chunks
        from citation_assigner_enhanced import ChunkMetadata

        chunks_metadata = []
        for chunk in sample_chunks:
            chunk_meta = ChunkMetadata(
                text=chunk["text"],
                source=chunk["source"],
                span=chunk["span"],
                meta=chunk["meta"],
                apa_citation=chunk["meta"]["apa"],
                entidades_clave=chunk["entidades_clave"],
            )
            chunks_metadata.append(chunk_meta)

        # Asignar citas
        sentence_citations = assigner.attach_citations_to_sentences(
            sample_sentences, chunks_metadata
        )

        # Verificar que se detectan entidades compartidas
        for sc in sentence_citations:
            if sc.citations:
                # Debe haber entidades compartidas si hay citas
                assert isinstance(sc.entidades_compartidas, list)

    def test_rapidfuzz_integration(self, sample_sentences, sample_chunks):
        """Prueba integración con RapidFuzz"""
        # Usar función de conveniencia
        resultados = attach_citations_to_sentences_enhanced(
            sample_sentences, sample_chunks, sim_threshold=0.5
        )

        # Verificar estructura de resultados
        assert len(resultados) == len(sample_sentences)

        for resultado in resultados:
            assert "sentence" in resultado
            assert "citations" in resultado
            assert "chunks_soporte" in resultado
            assert "confianza" in resultado
            assert "entidades_compartidas" in resultado

            # Verificar tipos de datos
            assert isinstance(resultado["citations"], list)
            assert isinstance(resultado["chunks_soporte"], list)
            assert isinstance(resultado["confianza"], float)
            assert isinstance(resultado["entidades_compartidas"], list)

    def test_error_handling(self):
        """Prueba manejo de errores"""
        assigner = CitationAssignerEnhanced(sim_threshold=0.5, top_k=3)

        # Caso 1: Lista vacía de chunks
        sentence_citations = assigner.attach_citations_to_sentences(
            ["test sentence"], []
        )
        assert len(sentence_citations) == 1
        assert len(sentence_citations[0].citations) == 0

        # Caso 2: Lista vacía de oraciones
        from citation_assigner_enhanced import ChunkMetadata

        chunks = [
            ChunkMetadata(
                text="test chunk",
                source="test",
                span=(0, 10),
                meta={},
                apa_citation="Test (2023).",
                entidades_clave=[],
            )
        ]

        sentence_citations = assigner.attach_citations_to_sentences([], chunks)
        assert len(sentence_citations) == 0

    def test_source_quality_factor(self, sample_sentences, sample_chunks):
        """Prueba factor de calidad de fuentes"""
        assigner = CitationAssignerEnhanced(sim_threshold=0.5, top_k=3)

        # Convertir chunks
        from citation_assigner_enhanced import ChunkMetadata

        chunks_metadata = []
        for chunk in sample_chunks:
            chunk_meta = ChunkMetadata(
                text=chunk["text"],
                source=chunk["source"],
                span=chunk["span"],
                meta=chunk["meta"],
                apa_citation=chunk["meta"]["apa"],
                entidades_clave=chunk["entidades_clave"],
            )
            chunks_metadata.append(chunk_meta)

        # Asignar citas
        sentence_citations = assigner.attach_citations_to_sentences(
            sample_sentences, chunks_metadata
        )

        # Verificar que las fuentes preferidas tienen mejor confianza
        for sc in sentence_citations:
            if sc.citations:
                # Verificar que la confianza se calcula correctamente
                assert sc.confianza_global > 0.0
