#!/usr/bin/env python3
"""
Sistema Unificado de Asistencia IA Mejorado - Versión con Evidencia
Implementa plantillas estructuradas, citación por oración, guardrails anti-alucinación
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


class TipoRespuesta(Enum):
    """Tipos de respuesta estructurada"""
    TLDR = "tldr"
    EVIDENCIA = "evidencia"
    LIMITACIONES = "limitaciones"
    RECOMENDACION = "recomendacion"
    BIBLIOGRAFIA = "bibliografia"


class NivelUrgencia(Enum):
    """Niveles de urgencia clínica"""
    NORMAL = "normal"
    URGENTE = "urgente"
    CRITICO = "critico"
    DERIVACION = "derivacion"


class TipoClaim(Enum):
    """Tipos de claims en la respuesta"""
    EVIDENCIADO = "evidenciado"
    INFERIDO = "inferido"
    CRITICABLE = "criticable"
    SIN_SOPORTE = "sin_soporte"


@dataclass
class ChunkEvidencia:
    """Chunk de evidencia con metadatos"""
    texto: str
    fuente: str
    doi: str
    autores: List[str]
    año: str
    titulo: str
    seccion: str
    inicio_char: int
    fin_char: int
    relevancia_score: float
    entidades_clave: List[str] = field(default_factory=list)
    hash_chunk: str = ""


@dataclass
class ClaimVerificado:
    """Claim verificado con evidencia"""
    claim: str
    tipo: TipoClaim
    chunks_soporte: List[ChunkEvidencia]
    similitud_maxima: float
    entidades_compartidas: List[str]
    confianza: float
    advertencias: List[str] = field(default_factory=list)


@dataclass
class RespuestaEstructurada:
    """Respuesta estructurada con citación por oración"""
    tldr: str
    evidencia_clave: List[Dict[str, Any]]  # {claim: str, citas: List[str], confianza: float}
    limitaciones: List[str]
    recomendacion: str
    bibliografia: List[Dict[str, str]]
    nivel_urgencia: NivelUrgencia
    claims_criticos: List[str]
    tiempo_generacion: float
    fuentes_utilizadas: int
    chunks_procesados: int


@dataclass
class RespuestaCopilot:
    """Respuesta unificada del Copilot (renombrada para evitar duplicación)"""
    respuesta_estructurada: RespuestaEstructurada
    mensaje_usuario: str
    contexto_consulta: Dict[str, Any]
    timestamp: datetime
    session_id: str
    confianza_global: float


class PlantillaRespuesta:
    """Generador de plantillas de respuesta estructurada"""
    
    def __init__(self):
        self.plantilla_base = {
            "tldr": "",
            "evidencia_clave": [],
            "limitaciones": [],
            "recomendacion": "",
            "bibliografia": [],
            "nivel_urgencia": "normal",
            "claims_criticos": [],
            "tiempo_generacion": 0.0,
            "fuentes_utilizadas": 0,
            "chunks_procesados": 0
        }
    
    def generar_esqueleto(self, consulta: str, evidencia: List[ChunkEvidencia]) -> Dict[str, Any]:
        """Genera el esqueleto de la respuesta estructurada"""
        esqueleto = self.plantilla_base.copy()
        
        # Analizar consulta para determinar estructura
        if "tratamiento" in consulta.lower():
            esqueleto["evidencia_clave"].append({
                "tipo": "intervenciones",
                "claims": [],
                "citas": []
            })
        
        if "diagnóstico" in consulta.lower():
            esqueleto["evidencia_clave"].append({
                "tipo": "criterios_diagnosticos",
                "claims": [],
                "citas": []
            })
        
        if "pronóstico" in consulta.lower():
            esqueleto["evidencia_clave"].append({
                "tipo": "factores_pronostico",
                "claims": [],
                "citas": []
            })
        
        # Agregar sección de evidencia general
        esqueleto["evidencia_clave"].append({
            "tipo": "evidencia_general",
            "claims": [],
            "citas": []
        })
        
        return esqueleto


class VerificadorClaims:
    """Verificador de claims con guardrails anti-alucinación"""
    
    def __init__(self, umbral_similitud: float = 0.7):
        self.umbral_similitud = umbral_similitud
        self.claims_criticos = [
            "cura definitiva",
            "100% efectivo",
            "sin efectos secundarios",
            "garantizado",
            "milagroso"
        ]
    
    def verificar_claim(self, claim: str, chunks: List[ChunkEvidencia]) -> ClaimVerificado:
        """Verifica un claim contra la evidencia disponible"""
        # Extraer entidades del claim
        entidades_claim = self._extraer_entidades(claim)
        
        # Buscar chunks con similitud
        chunks_soporte = []
        similitud_maxima = 0.0
        entidades_compartidas = []
        
        for chunk in chunks:
            similitud = self._calcular_similitud(claim, chunk.texto)
            if similitud > self.umbral_similitud:
                chunks_soporte.append(chunk)
                similitud_maxima = max(similitud_maxima, similitud)
                
                # Verificar entidades compartidas
                entidades_chunk = self._extraer_entidades(chunk.texto)
                compartidas = set(entidades_claim) & set(entidades_chunk)
                entidades_compartidas.extend(list(compartidas))
        
        # Determinar tipo de claim
        tipo_claim = self._determinar_tipo_claim(claim, chunks_soporte, similitud_maxima)
        
        # Calcular confianza
        confianza = self._calcular_confianza_claim(claim, chunks_soporte, similitud_maxima)
        
        # Verificar advertencias
        advertencias = self._verificar_advertencias(claim)
        
        return ClaimVerificado(
            claim=claim,
            tipo=tipo_claim,
            chunks_soporte=chunks_soporte,
            similitud_maxima=similitud_maxima,
            entidades_compartidas=list(set(entidades_compartidas)),
            confianza=confianza,
            advertencias=advertencias
        )
    
    def _extraer_entidades(self, texto: str) -> List[str]:
        """Extrae entidades clave del texto"""
        # Implementación simplificada - en producción usar NER
        palabras_clave = [
            'dolor', 'tratamiento', 'ejercicio', 'terapia', 'medicamento',
            'rodilla', 'hombro', 'espalda', 'fisioterapia', 'rehabilitación'
        ]
        
        entidades = []
        texto_lower = texto.lower()
        for palabra in palabras_clave:
            if palabra in texto_lower:
                entidades.append(palabra)
        
        return entidades
    
    def _calcular_similitud(self, claim: str, chunk_texto: str) -> float:
        """Calcula similitud entre claim y chunk"""
        # Implementación simplificada - en producción usar embeddings
        claim_words = set(claim.lower().split())
        chunk_words = set(chunk_texto.lower().split())
        
        if not claim_words or not chunk_words:
            return 0.0
        
        intersection = claim_words & chunk_words
        union = claim_words | chunk_words
        
        return len(intersection) / len(union) if union else 0.0
    
    def _determinar_tipo_claim(self, claim: str, chunks_soporte: List[ChunkEvidencia], similitud: float) -> TipoClaim:
        """Determina el tipo de claim basado en evidencia"""
        if not chunks_soporte:
            return TipoClaim.SIN_SOPORTE
        
        if similitud > 0.8:
            return TipoClaim.EVIDENCIADO
        elif similitud > 0.6:
            return TipoClaim.INFERIDO
        else:
            return TipoClaim.CRITICABLE
    
    def _calcular_confianza_claim(self, claim: str, chunks_soporte: List[ChunkEvidencia], similitud: float) -> float:
        """Calcula confianza del claim"""
        confianza_base = similitud
        
        # Bonus por número de chunks de soporte
        bonus_chunks = min(len(chunks_soporte) * 0.1, 0.3)
        
        # Penalización por claims críticos
        penalizacion_critico = 0.0
        for claim_critico in self.claims_criticos:
            if claim_critico in claim.lower():
                penalizacion_critico = 0.3
                break
        
        confianza = confianza_base + bonus_chunks - penalizacion_critico
        return max(0.0, min(1.0, confianza))
    
    def _verificar_advertencias(self, claim: str) -> List[str]:
        """Verifica advertencias en el claim"""
        advertencias = []
        
        # Claims críticos
        for claim_critico in self.claims_criticos:
            if claim_critico in claim.lower():
                advertencias.append(f"⚠️ Claim crítico detectado: '{claim_critico}'")
        
        # Lenguaje absoluto
        absolutos = ["siempre", "nunca", "todos", "ninguno", "100%", "0%"]
        for absoluto in absolutos:
            if absoluto in claim.lower():
                advertencias.append(f"⚠️ Lenguaje absoluto: '{absoluto}'")
        
        return advertencias


class FormateadorAPA:
    """Formateador de citas APA"""
    
    def __init__(self):
        self.plantilla_apa = "{autores} ({año}). {titulo}. {fuente}."
    
    def formatear_cita(self, chunk: ChunkEvidencia) -> str:
        """Formatea una cita APA"""
        # Procesar autores
        if len(chunk.autores) == 1:
            autores_str = chunk.autores[0]
        elif len(chunk.autores) <= 3:
            autores_str = " & ".join(chunk.autores)
        elif len(chunk.autores) <= 20:
            autores_str = ", ".join(chunk.autores[:-1]) + " & " + chunk.autores[-1]
        else:
            autores_str = ", ".join(chunk.autores[:19]) + " et al."
        
        # Formatear título
        titulo_formateado = self._formatear_titulo(chunk.titulo)
        
        # Determinar fuente
        fuente = self._determinar_fuente(chunk.fuente)
        
        cita = self.plantilla_apa.format(
            autores=autores_str,
            año=chunk.año,
            titulo=titulo_formateado,
            fuente=fuente
        )
        
        return cita
    
    def _formatear_titulo(self, titulo: str) -> str:
        """Formatea el título según reglas APA"""
        # Capitalizar primera letra de palabras principales
        palabras = titulo.split()
        palabras_formateadas = []
        
        for palabra in palabras:
            if len(palabra) > 3:  # Palabras largas se capitalizan
                palabras_formateadas.append(palabra.capitalize())
            else:
                palabras_formateadas.append(palabra.lower())
        
        return " ".join(palabras_formateadas)
    
    def _determinar_fuente(self, fuente: str) -> str:
        """Determina la fuente para la cita"""
        if "pubmed" in fuente.lower():
            return "PubMed"
        elif "europepmc" in fuente.lower():
            return "Europe PMC"
        else:
            return fuente


class DetectorUrgencia:
    """Detector de urgencia clínica y banderas rojas"""
    
    def __init__(self):
        self.banderas_rojas = {
            "traumatologia": [
                "dolor intenso", "deformidad", "imposibilidad de movimiento",
                "pérdida de sensibilidad", "pérdida de fuerza"
            ],
            "cardiologia": [
                "dolor en el pecho", "dificultad para respirar", "palpitaciones",
                "desmayo", "sudoración fría"
            ],
            "neurologia": [
                "dolor de cabeza intenso", "pérdida de consciencia", "convulsiones",
                "pérdida de visión", "dificultad para hablar"
            ],
            "general": [
                "fiebre alta", "sangrado", "dolor abdominal intenso",
                "vómitos persistentes", "diarrea severa"
            ]
        }
    
    def detectar_urgencia(self, consulta: str, sintomas: List[str]) -> NivelUrgencia:
        """Detecta nivel de urgencia basado en consulta y síntomas"""
        texto_completo = consulta.lower() + " " + " ".join(sintomas).lower()
        
        # Contar banderas rojas
        banderas_detectadas = 0
        
        for especialidad, banderas in self.banderas_rojas.items():
            for bandera in banderas:
                if bandera in texto_completo:
                    banderas_detectadas += 1
        
        # Determinar nivel de urgencia
        if banderas_detectadas >= 3:
            return NivelUrgencia.CRITICO
        elif banderas_detectadas >= 2:
            return NivelUrgencia.URGENTE
        elif banderas_detectadas >= 1:
            return NivelUrgencia.DERIVACION
        else:
            return NivelUrgencia.NORMAL


class PromptingController:
    """Controlador de prompting con function-calling"""
    
    def __init__(self):
        self.functions_disponibles = {
            "fetch_more": self._fetch_more_evidence,
            "format_apa": self._format_apa_citation,
            "verify_claim": self._verify_claim_evidence
        }
    
    def generar_prompt_estructurado(self, consulta: str, evidencia: List[ChunkEvidencia], esqueleto: Dict) -> str:
        """Genera prompt estructurado para el LLM"""
        prompt = f"""
Eres un asistente médico especializado. Analiza la siguiente consulta y evidencia científica para generar una respuesta estructurada.

CONSULTA: {consulta}

EVIDENCIA DISPONIBLE ({len(evidencia)} chunks):
{self._formatear_evidencia(evidencia)}

ESQUELETO DE RESPUESTA:
{json.dumps(esqueleto, indent=2, ensure_ascii=False)}

INSTRUCCIONES:
1. Completa cada sección del esqueleto con información basada ÚNICAMENTE en la evidencia proporcionada
2. Cada claim debe tener al menos una cita APA
3. Si detectas vacíos en la evidencia, usa fetch_more(query) para obtener más información
4. Formatea las citas usando format_apa(metadata)
5. Marca claims sin soporte con ⚠️
6. Mantén un tono profesional y basado en evidencia

FUNCTIONS DISPONIBLES:
- fetch_more(query): Obtener más evidencia sobre un tema específico
- format_apa(metadata): Formatear cita APA
- verify_claim(claim, evidence): Verificar un claim contra la evidencia

Genera la respuesta estructurada siguiendo exactamente el formato del esqueleto.
"""
        return prompt
    
    def _formatear_evidencia(self, evidencia: List[ChunkEvidencia]) -> str:
        """Formatea la evidencia para el prompt"""
        formateado = []
        for i, chunk in enumerate(evidencia[:5]):  # Limitar a 5 chunks para el prompt
            formateado.append(f"""
CHUNK {i+1}:
Texto: {chunk.texto[:200]}...
Fuente: {chunk.fuente}
Autores: {', '.join(chunk.autores[:3])}
Año: {chunk.año}
Relevancia: {chunk.relevancia_score:.2f}
""")
        return "\n".join(formateado)
    
    def _fetch_more_evidence(self, query: str) -> List[ChunkEvidencia]:
        """Función para obtener más evidencia"""
        # En producción, esto llamaría al sistema de búsqueda científica
        logger.info(f"🔍 Fetching more evidence for: {query}")
        return []
    
    def _format_apa_citation(self, metadata: Dict) -> str:
        """Función para formatear citas APA"""
        formateador = FormateadorAPA()
        chunk = ChunkEvidencia(
            texto="",
            fuente=metadata.get("fuente", ""),
            doi=metadata.get("doi", ""),
            autores=metadata.get("autores", []),
            año=metadata.get("año", ""),
            titulo=metadata.get("titulo", ""),
            seccion="",
            inicio_char=0,
            fin_char=0,
            relevancia_score=0.0
        )
        return formateador.formatear_cita(chunk)
    
    def _verify_claim_evidence(self, claim: str, evidence: List[str]) -> Dict:
        """Función para verificar claims"""
        verificador = VerificadorClaims()
        chunks = [ChunkEvidencia(texto=e, fuente="", doi="", autores=[], año="", titulo="", seccion="", inicio_char=0, fin_char=0, relevancia_score=0.0) for e in evidence]
        claim_verificado = verificador.verificar_claim(claim, chunks)
        
        return {
            "claim": claim,
            "tipo": claim_verificado.tipo.value,
            "confianza": claim_verificado.confianza,
            "advertencias": claim_verificado.advertencias
        }


class UnifiedCopilotAssistantEnhanced:
    """Sistema unificado de asistencia IA mejorado con evidencia"""
    
    def __init__(self):
        logger.info("🤖 Inicializando Sistema Unificado de Asistencia IA Mejorado")
        
        # Inicializar componentes
        self.plantilla = PlantillaRespuesta()
        self.verificador = VerificadorClaims()
        self.formateador_apa = FormateadorAPA()
        self.detector_urgencia = DetectorUrgencia()
        self.prompting_controller = PromptingController()
        
        # Configuración
        self.api_key = None  # Se configurará desde environment
        self.base_url = "https://openrouter.ai/api/v1"
        
        logger.info("✅ Sistema Unificado de Asistencia IA Mejorado inicializado")
    
    def procesar_consulta_con_evidencia(
        self,
        consulta: str,
        evidencia: List[ChunkEvidencia],
        contexto: Dict[str, Any] = None
    ) -> RespuestaCopilot:
        """Procesa una consulta con evidencia científica estructurada"""
        start_time = time.time()
        
        logger.info(f"🤖 Procesando consulta con evidencia: {consulta[:50]}...")
        
        try:
            # Paso 1: Generar esqueleto de respuesta
            esqueleto = self.plantilla.generar_esqueleto(consulta, evidencia)
            
            # Paso 2: Detectar urgencia
            sintomas = contexto.get("sintomas", []) if contexto else []
            nivel_urgencia = self.detector_urgencia.detectar_urgencia(consulta, sintomas)
            esqueleto["nivel_urgencia"] = nivel_urgencia.value
            
            # Paso 3: Generar prompt estructurado
            prompt = self.prompting_controller.generar_prompt_estructurado(
                consulta, evidencia, esqueleto
            )
            
            # Paso 4: Llamar al LLM con function-calling
            respuesta_llm = self._llm_with_functions(prompt, evidencia)
            
            # Paso 5: Verificar claims y aplicar guardrails
            respuesta_verificada = self._verificar_respuesta(respuesta_llm, evidencia)
            
            # Paso 6: Formatear citas APA
            respuesta_formateada = self._formatear_citas_apa(respuesta_verificada)
            
            # Paso 7: Crear respuesta estructurada
            tiempo_generacion = time.time() - start_time
            respuesta_estructurada = RespuestaEstructurada(
                tldr=respuesta_formateada.get("tldr", ""),
                evidencia_clave=respuesta_formateada.get("evidencia_clave", []),
                limitaciones=respuesta_formateada.get("limitaciones", []),
                recomendacion=respuesta_formateada.get("recomendacion", ""),
                bibliografia=respuesta_formateada.get("bibliografia", []),
                nivel_urgencia=nivel_urgencia,
                claims_criticos=respuesta_formateada.get("claims_criticos", []),
                tiempo_generacion=tiempo_generacion,
                fuentes_utilizadas=len(set(chunk.fuente for chunk in evidencia)),
                chunks_procesados=len(evidencia)
            )
            
            # Paso 8: Crear respuesta final
            respuesta_copilot = RespuestaCopilot(
                respuesta_estructurada=respuesta_estructurada,
                mensaje_usuario=consulta,
                contexto_consulta=contexto or {},
                timestamp=datetime.now(),
                session_id=self._generar_session_id(),
                confianza_global=self._calcular_confianza_global(respuesta_estructurada)
            )
            
            logger.info(f"✅ Respuesta estructurada generada en {tiempo_generacion:.2f}s")
            return respuesta_copilot
            
        except Exception as e:
            logger.error(f"❌ Error en procesamiento: {e}")
            # Retornar respuesta de error
            return self._respuesta_error(consulta, str(e))
    
    def _llm_with_functions(self, prompt: str, evidencia: List[ChunkEvidencia]) -> Dict:
        """Llama al LLM con function-calling"""
        # Simulación de llamada al LLM - en producción usar OpenRouter
        logger.info("🧠 Llamando al LLM con function-calling...")
        
        # Simular respuesta del LLM
        respuesta_simulada = {
            "tldr": "El ejercicio físico es efectivo para el dolor de rodilla según evidencia científica.",
            "evidencia_clave": [
                {
                    "tipo": "intervenciones",
                    "claims": [
                        "El ejercicio físico reduce el dolor de rodilla",
                        "La fisioterapia mejora la función articular"
                    ],
                    "citas": ["Smith et al. (2023)", "Johnson et al. (2022)"]
                }
            ],
            "limitaciones": [
                "Evidencia limitada para casos severos",
                "Necesidad de más estudios a largo plazo"
            ],
            "recomendacion": "Implementar programa de ejercicio supervisado",
            "bibliografia": [
                {"autores": "Smith, J.", "año": "2023", "titulo": "Exercise for knee pain", "fuente": "PubMed"}
            ]
        }
        
        return respuesta_simulada
    
    def _verificar_respuesta(self, respuesta_llm: Dict, evidencia: List[ChunkEvidencia]) -> Dict:
        """Verifica la respuesta del LLM contra la evidencia"""
        respuesta_verificada = respuesta_llm.copy()
        claims_criticos = []
        
        # Verificar claims en evidencia clave
        for seccion in respuesta_verificada.get("evidencia_clave", []):
            claims_verificados = []
            for claim in seccion.get("claims", []):
                claim_verificado = self.verificador.verificar_claim(claim, evidencia)
                
                if claim_verificado.tipo == TipoClaim.CRITICABLE:
                    claims_criticos.append(f"⚠️ {claim}")
                elif claim_verificado.tipo == TipoClaim.SIN_SOPORTE:
                    claims_criticos.append(f"❌ {claim} (sin evidencia)")
                
                claims_verificados.append({
                    "claim": claim,
                    "tipo": claim_verificado.tipo.value,
                    "confianza": claim_verificado.confianza,
                    "advertencias": claim_verificado.advertencias
                })
            
            seccion["claims_verificados"] = claims_verificados
        
        respuesta_verificada["claims_criticos"] = claims_criticos
        return respuesta_verificada
    
    def _formatear_citas_apa(self, respuesta: Dict) -> Dict:
        """Formatea las citas en formato APA"""
        respuesta_formateada = respuesta.copy()
        
        # Formatear bibliografía
        bibliografia_formateada = []
        for cita in respuesta.get("bibliografia", []):
            cita_apa = self.formateador_apa.formatear_cita(
                ChunkEvidencia(
                    texto="",
                    fuente=cita.get("fuente", ""),
                    doi="",
                    autores=cita.get("autores", "").split(", "),
                    año=cita.get("año", ""),
                    titulo=cita.get("titulo", ""),
                    seccion="",
                    inicio_char=0,
                    fin_char=0,
                    relevancia_score=0.0
                )
            )
            bibliografia_formateada.append({
                "cita_apa": cita_apa,
                "metadata": cita
            })
        
        respuesta_formateada["bibliografia"] = bibliografia_formateada
        return respuesta_formateada
    
    def _calcular_confianza_global(self, respuesta: RespuestaEstructurada) -> float:
        """Calcula la confianza global de la respuesta"""
        # Factores de confianza
        factor_evidencia = min(respuesta.fuentes_utilizadas / 5.0, 1.0)
        factor_claims = 1.0 - (len(respuesta.claims_criticos) * 0.1)
        factor_urgencia = 1.0 if respuesta.nivel_urgencia == NivelUrgencia.NORMAL else 0.8
        
        confianza = (factor_evidencia + factor_claims + factor_urgencia) / 3.0
        return max(0.0, min(1.0, confianza))
    
    def _generar_session_id(self) -> str:
        """Genera un ID de sesión único"""
        return hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
    
    def _respuesta_error(self, consulta: str, error: str) -> RespuestaCopilot:
        """Genera respuesta de error"""
        return RespuestaCopilot(
            respuesta_estructurada=RespuestaEstructurada(
                tldr="Error en el procesamiento de la consulta.",
                evidencia_clave=[],
                limitaciones=[f"Error técnico: {error}"],
                recomendacion="Por favor, intente nuevamente o contacte soporte.",
                bibliografia=[],
                nivel_urgencia=NivelUrgencia.NORMAL,
                claims_criticos=[],
                tiempo_generacion=0.0,
                fuentes_utilizadas=0,
                chunks_procesados=0
            ),
            mensaje_usuario=consulta,
            contexto_consulta={},
            timestamp=datetime.now(),
            session_id=self._generar_session_id(),
            confianza_global=0.0
        )


# Instancia global del sistema mejorado
unified_copilot_enhanced = UnifiedCopilotAssistantEnhanced()


def test_copilot_enhanced():
    """Función de prueba para el sistema Copilot mejorado"""
    print("🤖 Probando Sistema Copilot Mejorado")
    print("=" * 50)
    
    # Evidencia de prueba
    evidencia_prueba = [
        ChunkEvidencia(
            texto="El ejercicio físico reduce significativamente el dolor de rodilla en pacientes con osteoartritis.",
            fuente="pubmed",
            doi="10.1000/ejemplo1",
            autores=["Smith", "Johnson", "Williams"],
            año="2023",
            titulo="Exercise therapy for knee osteoarthritis",
            seccion="abstract",
            inicio_char=0,
            fin_char=100,
            relevancia_score=0.9
        ),
        ChunkEvidencia(
            texto="La fisioterapia mejora la función articular y reduce la discapacidad.",
            fuente="europepmc",
            doi="10.1000/ejemplo2",
            autores=["Brown", "Davis"],
            año="2022",
            titulo="Physical therapy outcomes in knee pain",
            seccion="results",
            inicio_char=0,
            fin_char=80,
            relevancia_score=0.8
        )
    ]
    
    # Casos de prueba
    casos_prueba = [
        "¿Qué tratamientos son efectivos para el dolor de rodilla?",
        "¿Cuál es el pronóstico de la osteoartritis de rodilla?",
        "Tengo dolor intenso en el pecho y dificultad para respirar"
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🔍 Caso {i}: {caso}")
        
        start_time = time.time()
        respuesta = unified_copilot_enhanced.procesar_consulta_con_evidencia(
            caso, evidencia_prueba
        )
        tiempo = time.time() - start_time
        
        print(f"   ✅ Tiempo: {tiempo:.2f}s")
        print(f"   📊 Confianza: {respuesta.confianza_global:.2f}")
        print(f"   🚨 Urgencia: {respuesta.respuesta_estructurada.nivel_urgencia.value}")
        print(f"   📚 Fuentes: {respuesta.respuesta_estructurada.fuentes_utilizadas}")
        print(f"   ⚠️ Claims críticos: {len(respuesta.respuesta_estructurada.claims_criticos)}")
        
        # Mostrar TL;DR
        if respuesta.respuesta_estructurada.tldr:
            print(f"   📝 TL;DR: {respuesta.respuesta_estructurada.tldr[:100]}...")
    
    print("\n✅ Pruebas del sistema Copilot mejorado completadas!")


if __name__ == "__main__":
    test_copilot_enhanced() 