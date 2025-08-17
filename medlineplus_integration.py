import requests
import logging
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import time
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MedlinePlusResult:
    """Resultado de consulta a MedlinePlus Connect"""

    title: str
    url: str
    summary: str
    language: str
    code_system: str
    code: str
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class MedlinePlusIntegration:
    """Integración con MedlinePlus Connect para educación del paciente"""

    def __init__(self):
        self.base_url = "https://connect.medlineplus.gov/service"
        self.cache = {}
        self.cache_duration = timedelta(hours=12)  # Cache por 12 horas
        self.rate_limit_delay = 0.6  # 100 requests/min = 0.6s entre requests
        self.last_request_time = 0

        # Sistemas de códigos soportados
        self.code_systems = {
            "icd10": "2.16.840.1.113883.6.90",
            "snomed": "2.16.840.1.113883.6.96",
            "loinc": "2.16.840.1.113883.6.1",
            "cpt": "2.16.840.1.113883.6.12",
            "rxcui": "2.16.840.1.113883.6.88",
            "ndc": "2.16.840.1.113883.6.69",
        }

        logger.info("✅ MedlinePlus Integration inicializado")

    def _rate_limit(self):
        """Control de rate limiting (100 requests/min)"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get_cache_key(self, system_oid: str, code: str, lang: str) -> str:
        """Genera clave única para cache"""
        return f"{system_oid}:{code}:{lang}"

    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Verifica si el cache es válido"""
        if "timestamp" not in cache_entry:
            return False

        cache_time = datetime.fromisoformat(cache_entry["timestamp"])
        return datetime.now() - cache_time < self.cache_duration

    def get_patient_education(
        self, system_oid: str, code: str, lang: str = "es"
    ) -> MedlinePlusResult:
        """
        Obtiene información educativa para el paciente

        Args:
            system_oid: OID del sistema de códigos
            code: Código específico
            lang: Idioma (es/en)

        Returns:
            MedlinePlusResult con información educativa
        """
        cache_key = self._get_cache_key(system_oid, code, lang)

        # Verificar cache
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            logger.info(f"📋 Cache hit para {code}")
            return MedlinePlusResult(**self.cache[cache_key])

        # Rate limiting
        self._rate_limit()

        try:
            params = {
                "mainSearchCriteria.v.cs": system_oid,
                "mainSearchCriteria.v.c": code,
                "informationRecipient.languageCode.c": lang,
                "knowledgeResponseType": "application/json",
            }

            logger.info(f"🔍 Consultando MedlinePlus: {code} ({lang})")

            response = requests.get(
                self.base_url,
                params=params,
                timeout=20,
                headers={"User-Agent": "MedConnect/1.0"},
            )

            response.raise_for_status()
            data = response.json()

            # Procesar respuesta
            if "feed" in data and "entry" in data["feed"] and data["feed"]["entry"]:
                entry = data["feed"]["entry"][0]

                # Extraer título y URL correctamente
                title = entry.get("title", {})
                if isinstance(title, dict) and "_value" in title:
                    title = title["_value"]
                elif isinstance(title, str):
                    title = title
                else:
                    title = str(title)

                url = entry.get("id", {})
                if isinstance(url, dict) and "_value" in url:
                    url = url["_value"]
                elif isinstance(url, str):
                    url = url
                else:
                    url = str(url)

                summary = entry.get("summary", {})
                if isinstance(summary, dict) and "_value" in summary:
                    summary = summary["_value"]
                elif isinstance(summary, str):
                    summary = summary
                else:
                    summary = str(summary)

                result = MedlinePlusResult(
                    title=title,
                    url=url,
                    summary=summary,
                    language=lang,
                    code_system=system_oid,
                    code=code,
                    timestamp=datetime.now(),
                    success=True,
                )

                # Guardar en cache
                self.cache[cache_key] = {
                    "title": result.title,
                    "url": result.url,
                    "summary": result.summary,
                    "language": result.language,
                    "code_system": result.code_system,
                    "code": result.code,
                    "timestamp": result.timestamp.isoformat(),
                    "success": result.success,
                }

                logger.info(f"✅ Información educativa obtenida: {result.title}")
                return result

            else:
                # Intentar con inglés si no hay contenido en español
                if lang == "es":
                    logger.info(f"🔄 No hay contenido en español, probando inglés")
                    return self.get_patient_education(system_oid, code, "en")

                result = MedlinePlusResult(
                    title="",
                    url="",
                    summary="",
                    language=lang,
                    code_system=system_oid,
                    code=code,
                    timestamp=datetime.now(),
                    success=False,
                    error_message="No se encontró información educativa",
                )

                return result

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error en consulta MedlinePlus: {e}")
            return MedlinePlusResult(
                title="",
                url="",
                summary="",
                language=lang,
                code_system=system_oid,
                code=code,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e),
            )

    def get_diagnosis_education(
        self, icd10_code: str, lang: str = "es"
    ) -> MedlinePlusResult:
        """Obtiene educación para diagnóstico ICD-10"""
        return self.get_patient_education(self.code_systems["icd10"], icd10_code, lang)

    def get_medication_education(
        self, rxcui: str, lang: str = "es"
    ) -> MedlinePlusResult:
        """Obtiene educación para medicamento RxCUI"""
        return self.get_patient_education(self.code_systems["rxcui"], rxcui, lang)

    def get_lab_test_education(
        self, loinc_code: str, lang: str = "es"
    ) -> MedlinePlusResult:
        """Obtiene educación para prueba de laboratorio LOINC"""
        return self.get_patient_education(self.code_systems["loinc"], loinc_code, lang)

    def get_procedure_education(
        self, cpt_code: str, lang: str = "es"
    ) -> MedlinePlusResult:
        """Obtiene educación para procedimiento CPT"""
        return self.get_patient_education(self.code_systems["cpt"], cpt_code, lang)

    def format_education_panel(self, result: MedlinePlusResult) -> Dict[str, str]:
        """Formatea resultado para panel educativo"""
        if not result.success:
            return {
                "title": "Información no disponible",
                "content": "No se encontró información educativa para este código.",
                "url": "",
                "show_panel": False,
            }

        return {
            "title": f"📚 {result.title}",
            "content": (
                result.summary[:200] + "..."
                if len(result.summary) > 200
                else result.summary
            ),
            "url": result.url,
            "show_panel": True,
            "source": "MedlinePlus.gov",
            "language": result.language,
        }


# Instancia global
medlineplus_integration = MedlinePlusIntegration()


# Función de conveniencia para integración con IAs
def get_patient_education_for_code(
    code_type: str, code: str, lang: str = "es"
) -> Dict[str, str]:
    """
    Función de conveniencia para obtener educación del paciente

    Args:
        code_type: 'diagnosis', 'medication', 'lab_test', 'procedure'
        code: Código específico
        lang: Idioma

    Returns:
        Dict con información formateada para UI
    """
    try:
        if code_type == "diagnosis":
            result = medlineplus_integration.get_diagnosis_education(code, lang)
        elif code_type == "medication":
            result = medlineplus_integration.get_medication_education(code, lang)
        elif code_type == "lab_test":
            result = medlineplus_integration.get_lab_test_education(code, lang)
        elif code_type == "procedure":
            result = medlineplus_integration.get_procedure_education(code, lang)
        else:
            return {
                "title": "Tipo de código no soportado",
                "content": "Solo se soportan: diagnosis, medication, lab_test, procedure",
                "url": "",
                "show_panel": False,
            }

        return medlineplus_integration.format_education_panel(result)

    except Exception as e:
        logger.error(f"❌ Error obteniendo educación del paciente: {e}")
        return {
            "title": "Error en el servicio",
            "content": "No se pudo obtener información educativa en este momento.",
            "url": "",
            "show_panel": False,
        }


if __name__ == "__main__":
    # Pruebas de la integración
    print("🧪 Probando MedlinePlus Integration")
    print("=" * 50)

    # Prueba con diagnóstico ICD-10
    print("\n🔍 Prueba 1: Diagnóstico ICD-10")
    result = medlineplus_integration.get_diagnosis_education("J45.901", "es")
    print(f"Título: {result.title}")
    print(f"URL: {result.url}")
    print(f"Resumen: {result.summary[:100]}...")

    # Prueba con medicamento RxCUI
    print("\n🔍 Prueba 2: Medicamento RxCUI")
    result = medlineplus_integration.get_medication_education("197361", "es")  # Aspirin
    print(f"Título: {result.title}")
    print(f"URL: {result.url}")
    print(f"Resumen: {result.summary[:100]}...")

    # Prueba con prueba de laboratorio LOINC
    print("\n🔍 Prueba 3: Prueba de laboratorio LOINC")
    result = medlineplus_integration.get_lab_test_education("3187-2", "es")  # Factor IX
    print(f"Título: {result.title}")
    print(f"URL: {result.url}")
    print(f"Resumen: {result.summary[:100]}...")

    print("\n✅ Pruebas completadas")
