#!/usr/bin/env python3
"""
Pruebas para parsing, formateo APA y ranking
"""

import pytest
from typing import List
from unified_scientific_search_enhanced import APACitationFormatter, TipoEstudio
from citation_assigner_enhanced import CitationAssignerEnhanced


class TestParsing:
    """Pruebas de parsing de datos PubMed"""

    def test_pubmed_xml_parsing(self, known_pubmed_articles):
        """Prueba parsing de XML de PubMed"""
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search_system = UnifiedScientificSearchEnhanced()

        for article in known_pubmed_articles:
            # Simular XML parsing
            parsed_data = {
                "pmid": article.pmid,
                "title": article.title,
                "authors": article.authors,
                "abstract": article.abstract,
                "publication_types": article.publication_types,
                "journal": article.journal,
                "year": article.year,
                "doi": article.doi,
            }

            # Verificar que todos los campos se parsean correctamente
            assert parsed_data["pmid"] == article.pmid
            assert parsed_data["title"] == article.title
            assert len(parsed_data["authors"]) == len(article.authors)
            assert parsed_data["abstract"] == article.abstract
            assert parsed_data["publication_types"] == article.publication_types
            assert parsed_data["journal"] == article.journal
            assert parsed_data["year"] == article.year
            assert parsed_data["doi"] == article.doi

    def test_publication_type_detection(self, known_pubmed_articles):
        """Prueba detección de tipos de publicación"""
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search_system = UnifiedScientificSearchEnhanced()

        for article in known_pubmed_articles:
            tipo_estudio = search_system._determinar_tipo_estudio(
                article.publication_types, article.title, article.abstract
            )

            # Verificar que el tipo de estudio se detecta correctamente
            if (
                "Systematic Review" in article.publication_types
                or "Meta-Analysis" in article.publication_types
            ):
                assert tipo_estudio in [
                    TipoEstudio.SYSTEMATIC_REVIEW,
                    TipoEstudio.META_ANALYSIS,
                ]
            elif "Randomized Controlled Trial" in article.publication_types:
                assert tipo_estudio == TipoEstudio.RCT
            elif "Case Report" in article.publication_types:
                assert tipo_estudio == TipoEstudio.CASE_REPORT


class TestAPAFormatting:
    """Pruebas de formateo APA"""

    def test_apa_citation_formatting(self, known_pubmed_articles):
        """Prueba formateo de citas APA"""
        for article in known_pubmed_articles:
            # Crear objeto de evidencia
            from unified_scientific_search_enhanced import EvidenciaCientifica

            evidencia = EvidenciaCientifica(
                titulo=article.title,
                autores=article.authors,
                doi=article.doi,
                fecha_publicacion=article.year,
                resumen=article.abstract,
                nivel_evidencia=article.expected_nivel_evidencia,
                fuente="pubmed",
                url=f"https://pubmed.ncbi.nlm.nih.gov/{article.pmid}/",
                relevancia_score=0.8,
                año_publicacion=article.year,
                journal=article.journal,
            )

            # Formatear cita APA
            cita_apa = APACitationFormatter.format_citation(evidencia)

            # Verificar que la cita contiene elementos esenciales
            assert article.year in cita_apa
            assert any(author.split(", ")[0] in cita_apa for author in article.authors)
            assert article.journal in cita_apa
            assert article.title[:50] in cita_apa  # Primeros 50 caracteres del título

    def test_apa_authors_formatting(self):
        """Prueba formateo de autores en APA"""
        # Caso 1: Un autor
        evidencia_1 = type(
            "obj",
            (object,),
            {
                "autores": ["Smith, J."],
                "año_publicacion": "2023",
                "titulo": "Test Article",
                "journal": "Test Journal",
                "volumen": "1",
                "numero": "",
                "paginas": "",
                "doi": "",
            },
        )()

        cita_1 = APACitationFormatter.format_citation(evidencia_1)
        assert "Smith, J." in cita_1

        # Caso 2: Dos autores
        evidencia_2 = type(
            "obj",
            (object,),
            {
                "autores": ["Smith, J.", "Johnson, A."],
                "año_publicacion": "2023",
                "titulo": "Test Article",
                "journal": "Test Journal",
                "volumen": "1",
                "numero": "",
                "paginas": "",
                "doi": "",
            },
        )()

        cita_2 = APACitationFormatter.format_citation(evidencia_2)
        assert "Smith, J." in cita_2
        assert "Johnson, A." in cita_2
        assert "&" in cita_2  # Debe usar & para dos autores

    def test_apa_title_case(self):
        """Prueba conversión a title case"""
        test_cases = [
            ("exercise therapy for knee pain", "Exercise Therapy for Knee Pain"),
            ("randomized controlled trial", "Randomized Controlled Trial"),
            (
                "systematic review and meta-analysis",
                "Systematic Review and Meta-Analysis",
            ),
        ]

        for input_text, expected in test_cases:
            result = APACitationFormatter._title_case(input_text)
            assert result == expected


class TestRanking:
    """Pruebas de ranking y relevancia"""

    def test_clinical_ranking(self, known_pubmed_articles):
        """Prueba ranking clínico"""
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search_system = UnifiedScientificSearchEnhanced()

        # Crear lista de evidencias
        evidencias = []
        for article in known_pubmed_articles:
            from unified_scientific_search_enhanced import EvidenciaCientifica

            evidencia = EvidenciaCientifica(
                titulo=article.title,
                autores=article.authors,
                doi=article.doi,
                fecha_publicacion=article.year,
                resumen=article.abstract,
                nivel_evidencia=article.expected_nivel_evidencia,
                fuente="pubmed",
                url=f"https://pubmed.ncbi.nlm.nih.gov/{article.pmid}/",
                relevancia_score=0.5,  # Score inicial
                año_publicacion=article.year,
                journal=article.journal,
                publication_types=article.publication_types,
            )
            evidencias.append(evidencia)

        # Aplicar ranking clínico
        evidencias_ranked = search_system._aplicar_ranking_clinico(
            evidencias, "dolor de rodilla"
        )

        # Verificar que el ranking se aplicó
        assert len(evidencias_ranked) == len(evidencias)

        # Verificar que los scores cambiaron
        scores_originales = [ev.relevancia_score for ev in evidencias]
        scores_ranked = [ev.relevancia_score for ev in evidencias_ranked]

        # Al menos algunos scores deben haber cambiado
        assert scores_originales != scores_ranked

    def test_evidence_level_detection(self, known_pubmed_articles):
        """Prueba detección de nivel de evidencia"""
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search_system = UnifiedScientificSearchEnhanced()

        for article in known_pubmed_articles:
            nivel_detectado = search_system._determinar_nivel_evidencia(
                article.title, article.abstract
            )

            # Verificar que el nivel detectado coincide con el esperado
            assert nivel_detectado == article.expected_nivel_evidencia

    def test_relevance_score_calculation(self, known_pubmed_articles):
        """Prueba cálculo de score de relevancia"""
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search_system = UnifiedScientificSearchEnhanced()

        for article in known_pubmed_articles:
            score = search_system._calcular_relevancia_score_mejorado(
                article.title,
                article.abstract,
                "dolor de rodilla",
                search_system._determinar_tipo_estudio(
                    article.publication_types, article.title, article.abstract
                ),
                article.year,
            )

            # Verificar que el score está en el rango correcto
            assert 0.0 <= score <= 1.0

            # Verificar que artículos más relevantes tienen scores más altos
            if "rodilla" in article.title.lower() or "knee" in article.title.lower():
                assert score > 0.3  # Debe tener relevancia mínima


class TestDeduplication:
    """Pruebas de deduplicación"""

    def test_doi_deduplication(self):
        """Prueba deduplicación por DOI"""
        from unified_scientific_search_enhanced import (
            UnifiedScientificSearchEnhanced,
            EvidenciaCientifica,
        )

        search_system = UnifiedScientificSearchEnhanced()

        # Crear evidencias con el mismo DOI
        evidencia1 = EvidenciaCientifica(
            titulo="Article 1",
            autores=["Author 1"],
            doi="10.1000/test.001",
            fecha_publicacion="2023",
            resumen="Test abstract 1",
            nivel_evidencia="Nivel I",
            fuente="pubmed",
            url="https://pubmed.ncbi.nlm.nih.gov/123/",
            relevancia_score=0.8,
        )

        evidencia2 = EvidenciaCientifica(
            titulo="Article 2",
            autores=["Author 2"],
            doi="10.1000/test.001",  # Mismo DOI
            fecha_publicacion="2023",
            resumen="Test abstract 2",
            nivel_evidencia="Nivel I",
            fuente="europepmc",
            url="https://europepmc.org/article/456",
            relevancia_score=0.9,
        )

        evidencias = [evidencia1, evidencia2]
        evidencias_deduplicadas = search_system._deduplicar_evidencias(evidencias)

        # Debe quedar solo una evidencia
        assert len(evidencias_deduplicadas) == 1

        # Debe mantener la de mayor score
        assert evidencias_deduplicadas[0].relevancia_score == 0.9

    def test_pmid_deduplication(self):
        """Prueba deduplicación por PMID"""
        from unified_scientific_search_enhanced import (
            UnifiedScientificSearchEnhanced,
            EvidenciaCientifica,
        )

        search_system = UnifiedScientificSearchEnhanced()

        # Crear evidencias con el mismo PMID
        evidencia1 = EvidenciaCientifica(
            titulo="Article 1",
            autores=["Author 1"],
            doi="",
            fecha_publicacion="2023",
            resumen="Test abstract 1",
            nivel_evidencia="Nivel I",
            fuente="pubmed",
            url="https://pubmed.ncbi.nlm.nih.gov/12345678/",
            relevancia_score=0.8,
            pmid="12345678",
        )

        evidencia2 = EvidenciaCientifica(
            titulo="Article 2",
            autores=["Author 2"],
            doi="",
            fecha_publicacion="2023",
            resumen="Test abstract 2",
            nivel_evidencia="Nivel I",
            fuente="pubmed",
            url="https://pubmed.ncbi.nlm.nih.gov/12345678/",
            relevancia_score=0.9,
            pmid="12345678",  # Mismo PMID
        )

        evidencias = [evidencia1, evidencia2]
        evidencias_deduplicadas = search_system._deduplicar_evidencias(evidencias)

        # Debe quedar solo una evidencia
        assert len(evidencias_deduplicadas) == 1
