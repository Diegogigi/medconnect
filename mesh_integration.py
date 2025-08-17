"""
Módulo de Integración con MeSH (Medical Subject Headings)
Mejora la normalización de términos médicos para búsquedas científicas más precisas
"""

import requests
import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache
import time

# Configurar logging
logger = logging.getLogger(__name__)

# Habilitar modo debug para diagnóstico
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")


@dataclass
class MeshDescriptor:
    """Descriptor MeSH con metadatos completos"""

    ui: str
    label: str
    definition: Optional[str] = None
    synonyms: List[str] = None
    tree_numbers: List[str] = None
    concepts: List[Dict] = None
    qualifiers: List[str] = None


@dataclass
class MeshSearchResult:
    """Resultado de búsqueda MeSH"""

    ui: str
    label: str
    resource: str
    match_type: str = "descriptor"


class MeshIntegration:
    """Integración con Open MeSH API para normalización de términos médicos"""

    def __init__(self):
        self.base_url = "https://id.nlm.nih.gov/mesh"
        self.cache_timeout = 86400  # 24 horas
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MedConnect/1.0 (mesh-integration)"})

        # Diccionario de traducción español → inglés para términos médicos comunes
        self.es_en_mapping = {
            # Dolor y síntomas
            "dolor": "pain",
            "dolor de rodilla": "knee pain",
            "dolor de tobillo": "ankle pain",
            "dolor de hombro": "shoulder pain",
            "dolor de espalda": "back pain",
            "dolor lumbar": "low back pain",
            "dolor cervical": "neck pain",
            "dolor de codo": "elbow pain",
            "dolor de muñeca": "wrist pain",
            "dolor de cadera": "hip pain",
            # Especialidades médicas
            "fisioterapia": "physical therapy",
            "kinesiología": "kinesiology",
            "rehabilitación": "rehabilitation",
            "terapia ocupacional": "occupational therapy",
            "fonoaudiología": "speech therapy",
            "nutrición": "nutrition",
            "medicina física": "physical medicine",
            # Condiciones médicas
            "esguince": "sprain",
            "fractura": "fracture",
            "artritis": "arthritis",
            "osteoartritis": "osteoarthritis",
            "tendinitis": "tendinitis",
            "bursitis": "bursitis",
            "esguince de tobillo": "ankle sprain",
            "esguince de rodilla": "knee sprain",
            "esguince de muñeca": "wrist sprain",
            "esguince de hombro": "shoulder sprain",
            "lesión": "injury",
            "lesión deportiva": "sports injury",
            # Tratamientos
            "ejercicio": "exercise",
            "ejercicios": "exercises",
            "terapia manual": "manual therapy",
            "electroterapia": "electrotherapy",
            "ultrasonido": "ultrasound",
            "masaje": "massage",
            "estiramiento": "stretching",
            "fortalecimiento": "strengthening",
            "movilización": "mobilization",
            # Anatomía
            "rodilla": "knee",
            "tobillo": "ankle",
            "hombro": "shoulder",
            "codo": "elbow",
            "muñeca": "wrist",
            "cadera": "hip",
            "columna": "spine",
            "cuello": "neck",
            "espalda": "back",
            # Evaluación
            "evaluación": "assessment",
            "diagnóstico": "diagnosis",
            "examen": "examination",
            "prueba": "test",
            "escala": "scale",
            "medición": "measurement",
            # Resultados
            "mejora": "improvement",
            "recuperación": "recovery",
            "funcionalidad": "function",
            "movilidad": "mobility",
            "fuerza": "strength",
            "flexibilidad": "flexibility",
            # Combinaciones específicas para MeSH
            "fisioterapia para esguince": "physical therapy sprain",
            "fisioterapia para dolor": "physical therapy pain",
            "fisioterapia para lesión": "physical therapy injury",
            "rehabilitación para esguince": "rehabilitation sprain",
            "tratamiento esguince": "sprain treatment",
            "terapia esguince": "sprain therapy",
        }

        logger.info("✅ MeSH Integration inicializado")

    def translate_spanish_to_english(self, term: str) -> str:
        """Traduce términos médicos del español al inglés"""
        term_lower = term.lower().strip()

        # Búsqueda exacta
        if term_lower in self.es_en_mapping:
            return self.es_en_mapping[term_lower]

        # Búsqueda parcial
        for es_term, en_term in self.es_en_mapping.items():
            if es_term in term_lower:
                return term_lower.replace(es_term, en_term)

        return term  # Si no encuentra traducción, devuelve el término original

    @lru_cache(maxsize=1000)
    def search_mesh_descriptors(
        self, query: str, limit: int = 10, match: str = "contains"
    ) -> List[MeshSearchResult]:
        """Busca descriptores MeSH por término"""
        try:
            # Traducir si es necesario
            translated_query = self.translate_spanish_to_english(query)

            url = f"{self.base_url}/lookup/descriptor"
            params = {"label": translated_query, "match": match, "limit": limit}

            logger.info(
                f"🔍 Buscando descriptores MeSH: '{query}' → '{translated_query}'"
            )

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            results = response.json()
            mesh_results = []

            for item in results:
                ui = item.get("resource", "").split("/")[-1]
                mesh_results.append(
                    MeshSearchResult(
                        ui=ui,
                        label=item.get("label", ""),
                        resource=item.get("resource", ""),
                        match_type="descriptor",
                    )
                )

            logger.info(f"✅ Encontrados {len(mesh_results)} descriptores MeSH")
            return mesh_results

        except Exception as e:
            logger.error(f"❌ Error buscando descriptores MeSH: {e}")
            return []

    @lru_cache(maxsize=500)
    def search_mesh_terms(
        self, query: str, limit: int = 10, match: str = "contains"
    ) -> List[MeshSearchResult]:
        """Busca términos MeSH (incluye sinónimos)"""
        try:
            translated_query = self.translate_spanish_to_english(query)

            url = f"{self.base_url}/lookup/term"
            params = {"label": translated_query, "match": match, "limit": limit}

            logger.info(f"🔍 Buscando términos MeSH: '{query}' → '{translated_query}'")

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            results = response.json()
            mesh_results = []

            for item in results:
                ui = item.get("resource", "").split("/")[-1]
                mesh_results.append(
                    MeshSearchResult(
                        ui=ui,
                        label=item.get("label", ""),
                        resource=item.get("resource", ""),
                        match_type="term",
                    )
                )

            logger.info(f"✅ Encontrados {len(mesh_results)} términos MeSH")
            return mesh_results

        except Exception as e:
            logger.error(f"❌ Error buscando términos MeSH: {e}")
            return []

    def get_mesh_descriptor(self, ui: str) -> Optional[MeshDescriptor]:
        """Obtiene descriptor MeSH completo por UI"""
        try:
            url = f"{self.base_url}/{ui}.json"

            logger.info(f"🔍 Obteniendo descriptor MeSH: {ui}")

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Debug: Imprimir estructura del JSON para entender el formato
            logger.debug(
                f"📋 Estructura JSON MeSH para {ui}: {json.dumps(data, indent=2)[:500]}..."
            )

            # Extraer información del JSON-LD - Corregir para URIs completas
            pref_label = ""
            definition = ""
            synonyms = []
            tree_numbers = []
            qualifiers = []

            # Buscar prefLabel en diferentes ubicaciones posibles (incluyendo URIs completas)
            if "prefLabel" in data:
                if (
                    isinstance(data["prefLabel"], dict)
                    and "@value" in data["prefLabel"]
                ):
                    pref_label = data["prefLabel"]["@value"]
                elif isinstance(data["prefLabel"], str):
                    pref_label = data["prefLabel"]

            # Buscar label (término preferido)
            if "label" in data:
                if isinstance(data["label"], dict) and "@value" in data["label"]:
                    pref_label = data["label"]["@value"]
                elif isinstance(data["label"], str):
                    pref_label = data["label"]

            # Buscar definition en diferentes ubicaciones posibles
            if "definition" in data:
                if (
                    isinstance(data["definition"], dict)
                    and "@value" in data["definition"]
                ):
                    definition = data["definition"]["@value"]
                elif isinstance(data["definition"], str):
                    definition = data["definition"]

            # Extraer tree numbers - Buscar en diferentes estructuras
            if "treeNumber" in data:
                for tree in data["treeNumber"]:
                    if isinstance(tree, str):
                        # Extraer solo el número del tree (última parte de la URI)
                        tree_num = tree.split("/")[-1]
                        tree_numbers.append(tree_num)

            # Extraer calificadores permitidos
            if "allowableQualifier" in data:
                for qualifier in data["allowableQualifier"]:
                    if isinstance(qualifier, str):
                        # Extraer solo el número del qualifier
                        qual_num = qualifier.split("/")[-1]
                        qualifiers.append(qual_num)

            # Extraer sinónimos - Buscar en diferentes estructuras
            if "concepts" in data:
                for concept in data["concepts"]:
                    if "terms" in concept:
                        for term in concept["terms"]:
                            if isinstance(term, dict):
                                if (
                                    term.get("type") == "entry"
                                    or term.get("type") == "synonym"
                                ):
                                    if "label" in term:
                                        if (
                                            isinstance(term["label"], dict)
                                            and "@value" in term["label"]
                                        ):
                                            synonyms.append(term["label"]["@value"])
                                        elif isinstance(term["label"], str):
                                            synonyms.append(term["label"])

            # Extraer sinónimos desde altLabel
            if "altLabel" in data:
                for alt_label in data["altLabel"]:
                    if isinstance(alt_label, dict) and "@value" in alt_label:
                        synonyms.append(alt_label["@value"])
                    elif isinstance(alt_label, str):
                        synonyms.append(alt_label)

            # Si no encontramos prefLabel, intentar buscar en otras ubicaciones
            if not pref_label:
                # Buscar en cualquier campo que contenga "label" o "prefLabel"
                for key, value in data.items():
                    if (
                        "label" in key.lower()
                        and isinstance(value, dict)
                        and "@value" in value
                    ):
                        pref_label = value["@value"]
                        break
                    elif "label" in key.lower() and isinstance(value, str):
                        pref_label = value
                        break

            # Si aún no tenemos label, usar el UI como fallback
            if not pref_label:
                pref_label = f"MeSH Term {ui}"
                logger.warning(
                    f"⚠️ No se pudo extraer prefLabel para {ui}, usando fallback"
                )

            # Para términos (T), necesitamos obtener el descriptor padre
            if ui.startswith("T") and not tree_numbers:
                # Buscar el descriptor padre en broaderDescriptor
                if "broaderDescriptor" in data:
                    for broader in data["broaderDescriptor"]:
                        if isinstance(broader, str):
                            broader_ui = broader.split("/")[-1]
                            # Obtener información del descriptor padre
                            parent_descriptor = self.get_mesh_descriptor(broader_ui)
                            if parent_descriptor:
                                tree_numbers.extend(parent_descriptor.tree_numbers)
                                break

            descriptor = MeshDescriptor(
                ui=ui,
                label=pref_label,
                definition=definition,
                synonyms=synonyms,
                tree_numbers=tree_numbers,
                qualifiers=qualifiers,
            )

            logger.info(f"✅ Descriptor MeSH obtenido: {pref_label} (UI: {ui})")
            logger.debug(
                f"📊 Datos extraídos - Sinónimos: {len(synonyms)}, Tree Numbers: {len(tree_numbers)}"
            )

            return descriptor

        except Exception as e:
            logger.error(f"❌ Error obteniendo descriptor MeSH {ui}: {e}")
            return None

    def normalize_medical_term(self, term: str) -> Optional[MeshDescriptor]:
        """Normaliza un término médico usando MeSH"""
        try:
            # Estrategia de búsqueda mejorada
            search_variations = [
                term,  # Término original
                self.translate_spanish_to_english(term),  # Traducción
            ]

            # Agregar variaciones específicas para términos comunes
            if "dolor" in term.lower():
                if "rodilla" in term.lower():
                    search_variations.extend(
                        ["knee pain", "patellofemoral pain", "anterior knee pain"]
                    )
                elif "tobillo" in term.lower():
                    search_variations.extend(["ankle pain", "ankle sprain"])
                elif "hombro" in term.lower():
                    search_variations.extend(["shoulder pain", "rotator cuff"])
                elif "codo" in term.lower():
                    search_variations.extend(["elbow pain", "tennis elbow"])

            if "fisioterapia" in term.lower():
                search_variations.extend(
                    ["physical therapy", "physiotherapy", "rehabilitation"]
                )

            if "esguince" in term.lower():
                search_variations.extend(["sprain", "ligament injury"])

            # Probar cada variación
            for search_term in search_variations:
                logger.info(f"🔍 Probando variación: '{search_term}'")

                # Primero buscar en descriptores
                descriptors = self.search_mesh_descriptors(search_term, limit=3)

                if descriptors:
                    # Tomar el primer resultado (mejor match)
                    best_match = descriptors[0]
                    descriptor = self.get_mesh_descriptor(best_match.ui)
                    if descriptor and descriptor.label != f"MeSH Term {best_match.ui}":
                        logger.info(
                            f"✅ Encontrado descriptor válido: {descriptor.label}"
                        )
                        return descriptor

                # Si no encuentra descriptores, buscar en términos
                terms = self.search_mesh_terms(search_term, limit=3)

                if terms:
                    best_match = terms[0]
                    descriptor = self.get_mesh_descriptor(best_match.ui)
                    if descriptor and descriptor.label != f"MeSH Term {best_match.ui}":
                        logger.info(f"✅ Encontrado término válido: {descriptor.label}")
                        return descriptor

            logger.warning(f"⚠️ No se encontró normalización MeSH para: {term}")
            return None

        except Exception as e:
            logger.error(f"❌ Error normalizando término médico: {e}")
            return None

    def get_enhanced_search_terms(self, original_query: str) -> List[str]:
        """Genera términos de búsqueda mejorados usando MeSH"""
        try:
            descriptor = self.normalize_medical_term(original_query)

            if not descriptor:
                return [original_query]

            # Crear lista de términos de búsqueda
            search_terms = [descriptor.label]

            # Agregar sinónimos relevantes
            if descriptor.synonyms:
                search_terms.extend(descriptor.synonyms[:3])  # Top 3 sinónimos

            # Agregar términos relacionados basados en tree numbers
            if descriptor.tree_numbers:
                for tree_num in descriptor.tree_numbers[:2]:  # Top 2 categorías
                    if "C" in tree_num:  # Categorías de enfermedades
                        search_terms.append(f"[MeSH Terms] {descriptor.label}")
                    elif "E" in tree_num:  # Categorías de técnicas
                        search_terms.append(f"[MeSH Terms] {descriptor.label}")

            logger.info(f"✅ Términos de búsqueda mejorados: {search_terms}")
            return search_terms

        except Exception as e:
            logger.error(f"❌ Error generando términos de búsqueda: {e}")
            return [original_query]

    def get_clinical_context(self, descriptor: MeshDescriptor) -> Dict[str, str]:
        """Obtiene contexto clínico basado en tree numbers"""
        context = {"specialty": "General", "category": "Other", "subcategory": "Other"}

        if not descriptor.tree_numbers:
            return context

        for tree_num in descriptor.tree_numbers:
            if tree_num.startswith("C"):
                context["category"] = "Diseases"
                if "C05" in tree_num:
                    context["specialty"] = "Musculoskeletal"
                elif "C10" in tree_num:
                    context["specialty"] = "Neurology"
                elif "C14" in tree_num:
                    context["specialty"] = "Cardiovascular"
                elif "C16" in tree_num:
                    context["specialty"] = "Pediatrics"
            elif tree_num.startswith("E"):
                context["category"] = "Techniques"
                if "E02" in tree_num:
                    context["specialty"] = "Therapeutics"
                elif "E04" in tree_num:
                    context["specialty"] = "Surgical Procedures"
            elif tree_num.startswith("F"):
                context["category"] = "Psychiatry and Psychology"
                context["specialty"] = "Mental Health"

        return context


# Instancia global del sistema MeSH
mesh_integration = MeshIntegration()


def diagnosticar_estructura_mesh(ui: str):
    """Función de diagnóstico para analizar la estructura JSON de MeSH"""
    try:
        url = f"https://id.nlm.nih.gov/mesh/{ui}.json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        print(f"\n🔍 DIAGNÓSTICO MeSH para UI: {ui}")
        print("=" * 60)

        # Mostrar estructura completa
        print("📋 ESTRUCTURA JSON COMPLETA:")
        print(json.dumps(data, indent=2))

        # Analizar campos específicos
        print(f"\n🔍 ANÁLISIS DE CAMPOS:")

        # Buscar prefLabel
        if "prefLabel" in data:
            print(f"✅ prefLabel encontrado: {data['prefLabel']}")
            print(f"   Tipo: {type(data['prefLabel'])}")
        else:
            print("❌ prefLabel NO encontrado")

        # Buscar definition
        if "definition" in data:
            print(f"✅ definition encontrado: {data['definition']}")
            print(f"   Tipo: {type(data['definition'])}")
        else:
            print("❌ definition NO encontrado")

        # Buscar concepts
        if "concepts" in data:
            print(f"✅ concepts encontrado: {len(data['concepts'])} conceptos")
            for i, concept in enumerate(data["concepts"][:2]):  # Solo primeros 2
                print(f"   Concepto {i+1}: {concept}")
        else:
            print("❌ concepts NO encontrado")

        # Buscar treeNumbers
        if "treeNumbers" in data:
            print(f"✅ treeNumbers encontrado: {data['treeNumbers']}")
        else:
            print("❌ treeNumbers NO encontrado")

        # Buscar @graph
        if "@graph" in data:
            print(f"✅ @graph encontrado: {len(data['@graph'])} elementos")
        else:
            print("❌ @graph NO encontrado")

        print("=" * 60)

    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")


def test_mesh_integration():
    """Función de prueba para el sistema MeSH"""
    print("🧪 Probando Integración MeSH")
    print("=" * 50)

    # Primero diagnosticar la estructura de un descriptor conocido
    print("\n🔍 DIAGNÓSTICO DE ESTRUCTURA MeSH:")
    diagnosticar_estructura_mesh("D017585")  # Knee Pain

    test_terms = [
        "dolor de rodilla",
        "fisioterapia",
        "esguince de tobillo",
        "rehabilitación",
    ]

    for term in test_terms:
        print(f"\n🔍 Probando: '{term}'")

        # Normalizar término
        descriptor = mesh_integration.normalize_medical_term(term)

        if descriptor:
            print(f"   ✅ Normalizado: {descriptor.label}")
            print(
                f"   📝 Definición: {descriptor.definition[:100] if descriptor.definition else 'No disponible'}..."
            )
            print(f"   🔗 UI: {descriptor.ui}")
            print(f"   🌳 Tree Numbers: {descriptor.tree_numbers[:3]}")
            print(f"   📚 Sinónimos: {descriptor.synonyms[:3]}")

            # Obtener contexto clínico
            context = mesh_integration.get_clinical_context(descriptor)
            print(f"   🏥 Especialidad: {context['specialty']}")

            # Generar términos de búsqueda mejorados
            enhanced_terms = mesh_integration.get_enhanced_search_terms(term)
            print(f"   🔍 Términos mejorados: {enhanced_terms}")
        else:
            print(f"   ❌ No se pudo normalizar")

    print("\n✅ Prueba de integración MeSH completada")


if __name__ == "__main__":
    test_mesh_integration()
