#!/usr/bin/env python3
"""
Fixtures para pruebas del sistema de orquestación
"""

import pytest
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestPubMedData:
    """Datos de prueba con IDs PubMed conocidos"""

    pmid: str
    title: str
    authors: List[str]
    abstract: str
    publication_types: List[str]
    journal: str
    year: str
    doi: str
    expected_apa: str
    expected_nivel_evidencia: str


@pytest.fixture
def known_pubmed_articles() -> List[TestPubMedData]:
    """Artículos PubMed conocidos para pruebas"""
    return [
        TestPubMedData(
            pmid="12345678",
            title="Exercise therapy for knee osteoarthritis: a systematic review and meta-analysis",
            authors=["Smith, J.", "Johnson, A.", "Williams, B."],
            abstract="Background: Knee osteoarthritis (OA) is a common degenerative joint disease affecting millions of people worldwide. Exercise therapy has been proposed as a non-pharmacological treatment option. Methods: We conducted a systematic review and meta-analysis of randomized controlled trials comparing exercise therapy with control interventions in patients with knee OA. Results: Twenty-five studies with 2,847 participants were included. Exercise therapy showed significant improvements in pain reduction (SMD -0.45, 95% CI -0.62 to -0.28) and physical function (SMD -0.38, 95% CI -0.55 to -0.21) compared to control groups. Conclusions: Exercise therapy is an effective treatment for knee OA, providing significant pain relief and functional improvement.",
            publication_types=["Systematic Review", "Meta-Analysis"],
            journal="Journal of Physical Therapy",
            year="2023",
            doi="10.1000/jpt.2023.001",
            expected_apa="Smith, J., Johnson, A., & Williams, B. (2023). Exercise therapy for knee osteoarthritis: a systematic review and meta-analysis. Journal of Physical Therapy.",
            expected_nivel_evidencia="Nivel I",
        ),
        TestPubMedData(
            pmid="87654321",
            title="Randomized controlled trial of physical therapy vs standard care for chronic low back pain",
            authors=["Brown, M.", "Davis, R.", "Wilson, K."],
            abstract="Objective: To compare the effectiveness of physical therapy versus standard care for chronic low back pain. Design: Randomized controlled trial. Participants: 150 patients with chronic low back pain. Interventions: 12 weeks of physical therapy or standard care. Main outcome measures: Pain intensity, disability, and quality of life. Results: Physical therapy group showed greater improvement in pain (p<0.001) and disability (p<0.001) compared to standard care. Conclusion: Physical therapy is more effective than standard care for chronic low back pain.",
            publication_types=["Randomized Controlled Trial"],
            journal="Physical Therapy Journal",
            year="2022",
            doi="10.1000/ptj.2022.002",
            expected_apa="Brown, M., Davis, R., & Wilson, K. (2022). Randomized controlled trial of physical therapy vs standard care for chronic low back pain. Physical Therapy Journal.",
            expected_nivel_evidencia="Nivel II",
        ),
        TestPubMedData(
            pmid="11223344",
            title="Case report: Successful treatment of shoulder impingement with manual therapy",
            authors=["Garcia, L.", "Martinez, P."],
            abstract="We present a case of a 45-year-old patient with shoulder impingement syndrome who was successfully treated with manual therapy techniques. The patient reported significant pain reduction and improved range of motion after 8 weeks of treatment. This case demonstrates the potential effectiveness of manual therapy for shoulder impingement.",
            publication_types=["Case Report"],
            journal="Manual Therapy Today",
            year="2021",
            doi="10.1000/mtt.2021.003",
            expected_apa="Garcia, L., & Martinez, P. (2021). Case report: Successful treatment of shoulder impingement with manual therapy. Manual Therapy Today.",
            expected_nivel_evidencia="Nivel IV",
        ),
    ]


@pytest.fixture
def sample_consulta() -> str:
    """Consulta de prueba"""
    return "¿Qué tratamientos son efectivos para el dolor de rodilla en pacientes con osteoartritis?"


@pytest.fixture
def sample_analisis_nlp() -> Dict[str, Any]:
    """Análisis NLP de prueba"""
    return {
        "sintomas": ["dolor", "rodilla", "osteoartritis"],
        "especialidad": "ortopedia",
        "intencion": "tratamiento",
        "entidades_clave": ["dolor", "rodilla", "osteoartritis", "tratamiento"],
        "confianza": 0.85,
    }


@pytest.fixture
def sample_chunks() -> List[Dict[str, Any]]:
    """Chunks de prueba para asignación de citas"""
    return [
        {
            "text": "El ejercicio físico reduce significativamente el dolor de rodilla en pacientes con osteoartritis.",
            "source": "pmid:12345678",
            "span": (0, 100),
            "meta": {
                "authors": ["Smith, J.", "Johnson, A.", "Williams, B."],
                "year": "2023",
                "title": "Exercise therapy for knee osteoarthritis",
                "journal": "Journal of Physical Therapy",
                "doi": "10.1000/jpt.2023.001",
                "apa": "Smith, J., Johnson, A., & Williams, B. (2023). Exercise therapy for knee osteoarthritis. Journal of Physical Therapy.",
            },
            "relevancia_score": 0.9,
            "entidades_clave": ["ejercicio", "dolor", "rodilla", "osteoartritis"],
        },
        {
            "text": "La fisioterapia mejora la función articular y reduce la discapacidad en pacientes con problemas de rodilla.",
            "source": "pmid:87654321",
            "span": (0, 120),
            "meta": {
                "authors": ["Brown, M.", "Davis, R.", "Wilson, K."],
                "year": "2022",
                "title": "Physical therapy for knee problems",
                "journal": "Physical Therapy Journal",
                "doi": "10.1000/ptj.2022.002",
                "apa": "Brown, M., Davis, R., & Wilson, K. (2022). Physical therapy for knee problems. Physical Therapy Journal.",
            },
            "relevancia_score": 0.8,
            "entidades_clave": ["fisioterapia", "función", "articular", "rodilla"],
        },
    ]


@pytest.fixture
def sample_sentences() -> List[str]:
    """Oraciones de prueba para asignación de citas"""
    return [
        "El ejercicio físico reduce el dolor de rodilla.",
        "La fisioterapia mejora la función articular.",
        "Los tratamientos conservadores son efectivos.",
        "No hay evidencia suficiente sobre tratamientos alternativos.",
    ]


@pytest.fixture
def mock_api_responses() -> Dict[str, Any]:
    """Respuestas simuladas de APIs"""
    return {
        "pubmed_search": {
            "esearchresult": {"idlist": ["12345678", "87654321", "11223344"]}
        },
        "pubmed_fetch": {
            "PubmedArticle": [
                {
                    "MedlineCitation": {
                        "PMID": "12345678",
                        "Article": {
                            "ArticleTitle": "Exercise therapy for knee osteoarthritis",
                            "Abstract": {
                                "AbstractText": "Background: Knee osteoarthritis..."
                            },
                        },
                        "AuthorList": {
                            "Author": [
                                {"LastName": "Smith", "ForeName": "J"},
                                {"LastName": "Johnson", "ForeName": "A"},
                            ]
                        },
                    }
                }
            ]
        },
        "europepmc_search": {
            "resultList": {
                "result": [
                    {
                        "id": "PMC123456",
                        "title": "Physical therapy interventions",
                        "abstractText": "Physical therapy shows promising results...",
                        "authorString": "Brown, M., Davis, R.",
                        "doi": "10.1000/ptj.2022.002",
                    }
                ]
            }
        },
    }


@pytest.fixture
def expected_metrics() -> Dict[str, float]:
    """Métricas esperadas para validación"""
    return {
        "respuestas_con_citas": 0.75,  # 75% de respuestas con ≥2 citas
        "oraciones_con_soporte": 0.80,  # 80% de oraciones con soporte
        "latencia_p95": 5.0,  # 5 segundos p95
        "tasa_preprints_filtrados": 0.90,  # 90% de preprints filtrados
        "precision_ranking": 0.85,  # 85% de precisión en ranking
        "cobertura_busqueda": 0.70,  # 70% de cobertura de búsqueda
    }


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Configuración de prueba"""
    return {
        "sim_threshold": 0.65,
        "top_k": 3,
        "max_results": 10,
        "timeout": 30,
        "retry_attempts": 3,
        "cache_ttl": 3600,
    }
