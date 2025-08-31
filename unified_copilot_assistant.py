#!/usr/bin/env python3
"""
Sistema Unificado de Asistencia IA
Consolida Copilot Health + Enhanced Copilot Health + Chat + Orchestrator
"""

import re
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar sistemas unificados
try:
    from unified_scientific_search import (
        unified_search,
        EvidenciaCientifica,
        RespuestaUnificada,
    )
    from unified_nlp_processor import unified_nlp, AnalisisCompleto, ConsultaProcesada

    UNIFIED_SYSTEMS_AVAILABLE = True
    logger.info("✅ Sistemas unificados disponibles")
except ImportError:
    UNIFIED_SYSTEMS_AVAILABLE = False
    logger.warning("⚠️ Sistemas unificados no disponibles")


class ModoAsistencia(Enum):
    """Modos de asistencia disponibles"""

    CHAT = "chat"
    ANALISIS = "analisis"
    ORQUESTACION = "orquestacion"
    COMPLETO = "completo"


@dataclass
class ContextoClinico:
    """Contexto clínico completo"""

    motivo_consulta: str
    tipo_atencion: str
    edad_paciente: Optional[int] = None
    genero: Optional[str] = None
    evaluacion: str = ""
    plan: str = ""
    antecedentes: str = ""
    sintomas: List[str] = None
    especialidad: str = "general"


@dataclass
class RespuestaChat:
    """Respuesta del chat conversacional"""

    mensaje: str
    confianza: float
    fuentes_citadas: List[str]
    recomendaciones: List[str]
    tiempo_respuesta: float


@dataclass
class AnalisisClinico:
    """Análisis clínico completo"""

    sintomas_identificados: List[str]
    patologias_sugeridas: List[str]
    escalas_recomendadas: List[str]
    banderas_rojas: List[str]
    preguntas_clinicas: List[str]
    confianza: float


@dataclass
class PlanTratamiento:
    """Plan de tratamiento sugerido"""

    titulo: str
    descripcion: str
    evidencia_cientifica: List[EvidenciaCientifica]
    escalas_aplicar: List[str]
    contraindicaciones: List[str]
    seguimiento: List[str]
    confianza: float


@dataclass
class RespuestaUnificada:
    """Respuesta unificada completa"""

    modo: ModoAsistencia
    contexto: ContextoClinico
    analisis_nlp: Optional[AnalisisCompleto] = None
    analisis_clinico: Optional[AnalisisClinico] = None
    respuesta_chat: Optional[RespuestaChat] = None
    plan_tratamiento: Optional[PlanTratamiento] = None
    evidencia_cientifica: List[EvidenciaCientifica] = None
    confianza_global: float = 0.0
    tiempo_procesamiento: float = 0.0
    errores: List[str] = None


class UnifiedCopilotAssistant:
    """Sistema unificado de asistencia IA médica"""

    def __init__(self):
        logger.info("🤖 Inicializando Sistema Unificado de Asistencia IA")

        # Verificar disponibilidad de sistemas unificados
        if not UNIFIED_SYSTEMS_AVAILABLE:
            logger.error("❌ Sistemas unificados no disponibles")
            raise ImportError("Sistemas unificados requeridos no disponibles")

        # Configuración de OpenRouter para chat
        self.openrouter_api_key = None
        self.openrouter_client = None
        self._setup_openrouter()

        # Mapeo de tipos de atención
        self.tipos_atencion_especialidad = {
            "medicina_general": "medicina_general",
            "fisioterapia": "fisioterapia",
            "terapia_ocupacional": "terapia_ocupacional",
            "enfermeria": "enfermeria",
            "psicologia": "psicologia",
            "nutricion": "nutricion",
            "kinesiologia": "kinesiologia",
            "fonoaudiologia": "fonoaudiologia",
            "urgencia": "urgencia",
        }

        # Sinónimos de especialidades
        self.sinonimos_especialidades = {
            "fisioterapia": [
                "fisioterapia",
                "fisioterapeuta",
                "fisio",
                "fisioterapéutico",
            ],
            "kinesiologia": ["kinesiologia", "kinesiología", "kinesiólogo", "kinesio"],
            "fonoaudiologia": [
                "fonoaudiologia",
                "fonoaudiología",
                "fonoaudiólogo",
                "fono",
            ],
            "terapia_ocupacional": [
                "terapia ocupacional",
                "terapeuta ocupacional",
                "t.o.",
            ],
            "psicologia": ["psicologia", "psicología", "psicólogo", "psico"],
        }

        # Banderas rojas por especialidad
        self.banderas_rojas = {
            "general": [
                "dolor intenso",
                "pérdida de consciencia",
                "dificultad para respirar",
                "sangrado abundante",
                "fiebre alta",
                "trauma reciente",
            ],
            "fisioterapia": [
                "dolor nocturno",
                "pérdida de fuerza",
                "alteración de sensibilidad",
                "dolor que irradia",
                "trauma reciente",
                "pérdida de control esfínteres",
            ],
            "psicologia": [
                "ideas suicidas",
                "alucinaciones",
                "delirios",
                "agresividad",
                "aislamiento extremo",
                "cambios drásticos de personalidad",
            ],
        }

        logger.info("✅ Sistema Unificado de Asistencia IA inicializado")

    def _setup_openrouter(self):
        """Configurar OpenRouter para chat"""
        try:
            import os
            from openai import OpenAI

            self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

            self.openrouter_client = OpenAI(
                api_key=self.openrouter_api_key, base_url="https://openrouter.ai/api/v1"
            )

            logger.info("✅ OpenRouter configurado para chat")

        except Exception as e:
            logger.warning(f"⚠️ OpenRouter no disponible: {e}")
            self.openrouter_client = None

    def procesar_consulta_unificada(
        self, contexto: ContextoClinico, modo: ModoAsistencia = ModoAsistencia.COMPLETO
    ) -> RespuestaUnificada:
        """Procesa una consulta usando el sistema unificado"""
        start_time = time.time()
        errores = []

        logger.info(f"🤖 Procesando consulta en modo: {modo.value}")

        try:
            # Inicializar respuesta
            respuesta = RespuestaUnificada(
                modo=modo, contexto=contexto, evidencia_cientifica=[], errores=[]
            )

            # Paso 1: Análisis NLP (siempre)
            try:
                analisis_nlp = unified_nlp.procesar_consulta_completa(
                    contexto.motivo_consulta, contexto.edad_paciente, contexto.genero
                )
                respuesta.analisis_nlp = analisis_nlp
                logger.info("✅ Análisis NLP completado")
            except Exception as e:
                error_msg = f"Error en análisis NLP: {e}"
                errores.append(error_msg)
                logger.error(f"❌ {error_msg}")

            # Paso 2: Análisis clínico
            try:
                analisis_clinico = self._realizar_analisis_clinico(
                    contexto, respuesta.analisis_nlp
                )
                respuesta.analisis_clinico = analisis_clinico
                logger.info("✅ Análisis clínico completado")
            except Exception as e:
                error_msg = f"Error en análisis clínico: {e}"
                errores.append(error_msg)
                logger.error(f"❌ {error_msg}")

            # Paso 3: Búsqueda de evidencia científica
            if modo in [ModoAsistencia.ORQUESTACION, ModoAsistencia.COMPLETO]:
                try:
                    evidencia = self._buscar_evidencia_cientifica(
                        contexto, respuesta.analisis_nlp
                    )
                    respuesta.evidencia_cientifica = evidencia
                    logger.info(
                        f"✅ Evidencia científica encontrada: {len(evidencia)} resultados"
                    )
                except Exception as e:
                    error_msg = f"Error en búsqueda de evidencia: {e}"
                    errores.append(error_msg)
                    logger.error(f"❌ {error_msg}")

            # Paso 4: Chat conversacional
            if modo in [ModoAsistencia.CHAT, ModoAsistencia.COMPLETO]:
                try:
                    respuesta_chat = self._procesar_chat(
                        contexto, respuesta.analisis_nlp, respuesta.evidencia_cientifica
                    )
                    respuesta.respuesta_chat = respuesta_chat
                    logger.info("✅ Chat procesado")
                except Exception as e:
                    error_msg = f"Error en chat: {e}"
                    errores.append(error_msg)
                    logger.error(f"❌ {error_msg}")

            # Paso 5: Plan de tratamiento
            if modo in [
                ModoAsistencia.ANALISIS,
                ModoAsistencia.ORQUESTACION,
                ModoAsistencia.COMPLETO,
            ]:
                try:
                    plan_tratamiento = self._generar_plan_tratamiento(
                        contexto, respuesta.analisis_nlp, respuesta.evidencia_cientifica
                    )
                    respuesta.plan_tratamiento = plan_tratamiento
                    logger.info("✅ Plan de tratamiento generado")
                except Exception as e:
                    error_msg = f"Error en plan de tratamiento: {e}"
                    errores.append(error_msg)
                    logger.error(f"❌ {error_msg}")

            # Calcular confianza global y tiempo
            respuesta.confianza_global = self._calcular_confianza_global(respuesta)
            respuesta.tiempo_procesamiento = time.time() - start_time
            respuesta.errores = errores

            logger.info(
                f"✅ Procesamiento completado en {respuesta.tiempo_procesamiento:.2f}s"
            )

            return respuesta

        except Exception as e:
            logger.error(f"❌ Error en procesamiento unificado: {e}")
            return RespuestaUnificada(
                modo=modo,
                contexto=contexto,
                confianza_global=0.0,
                tiempo_procesamiento=time.time() - start_time,
                errores=[f"Error general: {e}"],
            )

    def _realizar_analisis_clinico(
        self, contexto: ContextoClinico, analisis_nlp: Optional[AnalisisCompleto]
    ) -> AnalisisClinico:
        """Realiza análisis clínico basado en contexto y NLP"""

        # Extraer síntomas del análisis NLP
        sintomas_identificados = []
        if analisis_nlp and analisis_nlp.consulta_procesada.sintomas:
            for sintoma in analisis_nlp.consulta_procesada.sintomas:
                sintomas_identificados.append(
                    f"{sintoma.sintoma} en {sintoma.localizacion}"
                )

        # Identificar patologías
        patologias_sugeridas = []
        if analisis_nlp and analisis_nlp.patologias_identificadas:
            for patologia in analisis_nlp.patologias_identificadas:
                patologias_sugeridas.append(patologia.nombre)

        # Escalas recomendadas
        escalas_recomendadas = []
        if analisis_nlp and analisis_nlp.escalas_recomendadas:
            for escala in analisis_nlp.escalas_recomendadas:
                escalas_recomendadas.append(escala.nombre)

        # Detectar banderas rojas
        banderas_rojas = self._detectar_banderas_rojas(contexto, sintomas_identificados)

        # Generar preguntas clínicas
        preguntas_clinicas = self._generar_preguntas_clinicas(contexto, analisis_nlp)

        # Calcular confianza
        confianza = 0.7  # Base
        if analisis_nlp:
            confianza = max(confianza, analisis_nlp.confianza_global)

        return AnalisisClinico(
            sintomas_identificados=sintomas_identificados,
            patologias_sugeridas=patologias_sugeridas,
            escalas_recomendadas=escalas_recomendadas,
            banderas_rojas=banderas_rojas,
            preguntas_clinicas=preguntas_clinicas,
            confianza=confianza,
        )

    def _buscar_evidencia_cientifica(
        self, contexto: ContextoClinico, analisis_nlp: Optional[AnalisisCompleto]
    ) -> List[EvidenciaCientifica]:
        """Busca evidencia científica relevante"""

        terminos_busqueda = []

        # Usar términos del análisis NLP si disponible
        if analisis_nlp and analisis_nlp.terminos_busqueda_mejorados:
            terminos_busqueda = analisis_nlp.terminos_busqueda_mejorados[:3]
        else:
            # Usar motivo de consulta como fallback
            terminos_busqueda = [contexto.motivo_consulta]

        evidencia_combinada = []

        for termino in terminos_busqueda:
            try:
                evidencia = unified_search.buscar_evidencia_unificada(
                    termino, contexto.especialidad, max_resultados=3
                )
                evidencia_combinada.extend(evidencia)
            except Exception as e:
                logger.warning(f"⚠️ Error buscando evidencia para '{termino}': {e}")

        # Eliminar duplicados y limitar resultados
        evidencia_unicos = {}
        for ev in evidencia_combinada:
            key = ev.doi if ev.doi != "Sin DOI" else ev.titulo
            if key not in evidencia_unicos:
                evidencia_unicos[key] = ev

        return list(evidencia_unicos.values())[:5]

    def _procesar_chat(
        self,
        contexto: ContextoClinico,
        analisis_nlp: Optional[AnalisisCompleto],
        evidencia: List[EvidenciaCientifica],
    ) -> RespuestaChat:
        """Procesa chat conversacional con IA"""

        if not self.openrouter_client:
            return RespuestaChat(
                mensaje="Chat no disponible en este momento.",
                confianza=0.0,
                fuentes_citadas=[],
                recomendaciones=[],
                tiempo_respuesta=0.0,
            )

        start_time = time.time()

        try:
            # Construir contexto para el chat
            context_data = {
                "motivo_consulta": contexto.motivo_consulta,
                "tipo_atencion": contexto.tipo_atencion,
                "edad_paciente": contexto.edad_paciente,
                "evaluacion": contexto.evaluacion,
                "plan": contexto.plan,
                "antecedentes": contexto.antecedentes,
            }

            # Agregar información del análisis NLP
            if analisis_nlp:
                context_data["sintomas_identificados"] = [
                    f"{s.sintoma} en {s.localizacion}"
                    for s in analisis_nlp.consulta_procesada.sintomas
                ]
                context_data["patologias_sugeridas"] = [
                    p.nombre for p in analisis_nlp.patologias_identificadas
                ]

            # Agregar evidencia científica
            if evidencia:
                context_data["evidencia_cientifica"] = [
                    {"titulo": e.titulo, "doi": e.doi, "fuente": e.fuente}
                    for e in evidencia[:3]
                ]

            # Crear mensaje del sistema
            system_prompt = (
                "Eres Copilot Health, un asistente de IA que ayuda a profesionales de salud "
                "con análisis clínico y recomendaciones claras y seguras. "
                "Responde SIEMPRE en español y exclusivamente en Markdown bien estructurado: "
                "usa encabezados (##, ###) para secciones, listas con viñetas y numeradas, "
                "separadores (---) cuando aplique, negritas para subtítulos, y tablas cuando aporte claridad. "
                "Evita texto corrido largo; prefiere secciones compactas y bullets. "
                "No incluyas explicaciones fuera del contenido clínico ni bloques de código."
            )

            # Crear mensaje del usuario
            user_message = f"Contexto clínico: {json.dumps(context_data, ensure_ascii=False, indent=2)}"

            # Llamar a OpenRouter
            completion = self.openrouter_client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )

            # Extraer respuesta
            reply = completion.choices[0].message.content.strip()

            # Extraer fuentes citadas
            fuentes_citadas = []
            if evidencia:
                for e in evidencia[:3]:
                    if e.doi != "Sin DOI":
                        fuentes_citadas.append(f"{e.titulo} (DOI: {e.doi})")
                    else:
                        fuentes_citadas.append(e.titulo)

            # Generar recomendaciones básicas
            recomendaciones = []
            if analisis_nlp and analisis_nlp.escalas_recomendadas:
                recomendaciones.append(
                    f"Considerar aplicar escalas: {', '.join([e.nombre for e in analisis_nlp.escalas_recomendadas[:2]])}"
                )

            tiempo_respuesta = time.time() - start_time

            return RespuestaChat(
                mensaje=reply,
                confianza=0.8,
                fuentes_citadas=fuentes_citadas,
                recomendaciones=recomendaciones,
                tiempo_respuesta=tiempo_respuesta,
            )

        except Exception as e:
            logger.error(f"❌ Error en chat: {e}")
            return RespuestaChat(
                mensaje="No pude generar una respuesta en este momento.",
                confianza=0.0,
                fuentes_citadas=[],
                recomendaciones=[],
                tiempo_respuesta=time.time() - start_time,
            )

    def _generar_plan_tratamiento(
        self,
        contexto: ContextoClinico,
        analisis_nlp: Optional[AnalisisCompleto],
        evidencia: List[EvidenciaCientifica],
    ) -> PlanTratamiento:
        """Genera plan de tratamiento basado en análisis y evidencia"""

        # Determinar título del plan
        titulo = "Plan de Tratamiento Personalizado"
        if analisis_nlp and analisis_nlp.patologias_identificadas:
            patologia_principal = analisis_nlp.patologias_identificadas[0].nombre
            titulo = f"Plan de Tratamiento para {patologia_principal.replace('_', ' ').title()}"

        # Generar descripción
        descripcion = (
            f"Plan de tratamiento basado en el análisis de {contexto.motivo_consulta}"
        )
        if contexto.tipo_atencion:
            descripcion += f" para atención en {contexto.tipo_atencion}"

        # Escalas a aplicar
        escalas_aplicar = []
        if analisis_nlp and analisis_nlp.escalas_recomendadas:
            escalas_aplicar = [e.nombre for e in analisis_nlp.escalas_recomendadas[:3]]

        # Contraindicaciones
        contraindicaciones = [
            "Evaluar contraindicaciones individuales",
            "Considerar antecedentes médicos",
            "Verificar alergias y medicamentos",
        ]

        # Seguimiento
        seguimiento = [
            "Evaluación inicial con escalas recomendadas",
            "Seguimiento semanal del progreso",
            "Reevaluación mensual del plan",
        ]

        # Calcular confianza
        confianza = 0.7
        if analisis_nlp:
            confianza = max(confianza, analisis_nlp.confianza_global)
        if evidencia:
            confianza = min(0.9, confianza + 0.1)

        return PlanTratamiento(
            titulo=titulo,
            descripcion=descripcion,
            evidencia_cientifica=evidencia[:3],
            escalas_aplicar=escalas_aplicar,
            contraindicaciones=contraindicaciones,
            seguimiento=seguimiento,
            confianza=confianza,
        )

    def _detectar_banderas_rojas(
        self, contexto: ContextoClinico, sintomas: List[str]
    ) -> List[str]:
        """Detecta banderas rojas en el contexto clínico"""

        banderas_encontradas = []
        texto_completo = (
            f"{contexto.motivo_consulta} {contexto.evaluacion} {contexto.plan}".lower()
        )

        # Banderas rojas generales
        for bandera in self.banderas_rojas.get("general", []):
            if bandera.lower() in texto_completo:
                banderas_encontradas.append(bandera)

        # Banderas rojas específicas por especialidad
        especialidad = self._determinar_especialidad(contexto.tipo_atencion)
        if especialidad in self.banderas_rojas:
            for bandera in self.banderas_rojas[especialidad]:
                if bandera.lower() in texto_completo:
                    banderas_encontradas.append(bandera)

        return list(set(banderas_encontradas))

    def _generar_preguntas_clinicas(
        self, contexto: ContextoClinico, analisis_nlp: Optional[AnalisisCompleto]
    ) -> List[str]:
        """Genera preguntas clínicas específicas"""

        preguntas = []

        # Preguntas del análisis NLP
        if analisis_nlp and analisis_nlp.preguntas_evaluacion:
            preguntas.extend(analisis_nlp.preguntas_evaluacion[:5])

        # Preguntas específicas por tipo de atención
        if contexto.tipo_atencion == "fisioterapia":
            preguntas.extend(
                [
                    "¿Cuándo comenzó el problema?",
                    "¿Qué actividades agravan los síntomas?",
                    "¿Ha tenido este problema antes?",
                    "¿Qué tratamientos ha probado?",
                ]
            )
        elif contexto.tipo_atencion == "psicologia":
            preguntas.extend(
                [
                    "¿Cómo afecta esto su vida diaria?",
                    "¿Ha notado cambios en su estado de ánimo?",
                    "¿Tiene antecedentes familiares similares?",
                    "¿Está tomando algún medicamento?",
                ]
            )
        else:
            preguntas.extend(
                [
                    "¿Cuándo comenzó el problema?",
                    "¿Qué factores lo agravan o mejoran?",
                    "¿Ha tenido síntomas similares antes?",
                    "¿Qué tratamientos ha probado?",
                ]
            )

        return list(set(preguntas))[:8]  # Limitar a 8 preguntas

    def _determinar_especialidad(self, tipo_atencion: str) -> str:
        """Determina la especialidad basada en el tipo de atención"""

        tipo_lower = tipo_atencion.lower()

        for especialidad, sinonimos in self.sinonimos_especialidades.items():
            if tipo_lower in sinonimos:
                return especialidad

        return "general"

    def _calcular_confianza_global(self, respuesta: RespuestaUnificada) -> float:
        """Calcula la confianza global de la respuesta"""

        confianzas = []

        # Confianza del análisis NLP
        if respuesta.analisis_nlp:
            confianzas.append(respuesta.analisis_nlp.confianza_global)

        # Confianza del análisis clínico
        if respuesta.analisis_clinico:
            confianzas.append(respuesta.analisis_clinico.confianza)

        # Confianza del chat
        if respuesta.respuesta_chat:
            confianzas.append(respuesta.respuesta_chat.confianza)

        # Confianza del plan de tratamiento
        if respuesta.plan_tratamiento:
            confianzas.append(respuesta.plan_tratamiento.confianza)

        # Factor de evidencia científica
        if respuesta.evidencia_cientifica:
            confianzas.append(0.8)  # Bonus por evidencia disponible

        # Factor de errores
        if respuesta.errores:
            confianza_errores = max(0.0, 1.0 - len(respuesta.errores) * 0.1)
            confianzas.append(confianza_errores)

        return sum(confianzas) / max(len(confianzas), 1) if confianzas else 0.0

    def chat_simple(self, mensaje: str, contexto: Dict = None) -> str:
        """Chat simple para respuestas rápidas"""

        if not self.openrouter_client:
            return "Chat no disponible en este momento."

        try:
            system_prompt = (
                "Eres Copilot Health, un asistente médico. "
                "Responde de forma clara y concisa en español."
            )

            user_content = mensaje
            if contexto:
                user_content = f"Contexto: {json.dumps(contexto, ensure_ascii=False)}\n\nPregunta: {mensaje}"

            completion = self.openrouter_client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"❌ Error en chat simple: {e}")
            return "No pude generar una respuesta en este momento."


# Instancia global del sistema unificado
unified_copilot = UnifiedCopilotAssistant()


def test_unified_copilot():
    """Función de prueba para el sistema unificado de asistencia IA"""
    print("🤖 Probando Sistema Unificado de Asistencia IA")
    print("=" * 60)

    # Casos de prueba
    casos_prueba = [
        ContextoClinico(
            motivo_consulta="Tengo dolor lumbar crónico desde hace 6 meses",
            tipo_atencion="fisioterapia",
            edad_paciente=45,
            evaluacion="Dolor en zona lumbar que empeora al sentarse",
        ),
        ContextoClinico(
            motivo_consulta="Siento ansiedad y dificultad para dormir",
            tipo_atencion="psicologia",
            edad_paciente=32,
            antecedentes="Antecedentes de estrés laboral",
        ),
    ]

    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🧪 Caso de prueba {i}:")
        print(f"   Motivo: {caso.motivo_consulta}")
        print(f"   Tipo: {caso.tipo_atencion}")

        # Probar modo completo
        respuesta = unified_copilot.procesar_consulta_unificada(
            caso, ModoAsistencia.COMPLETO
        )

        print(f"   ✅ Confianza: {respuesta.confianza_global:.2f}")
        print(f"   ⏱️ Tiempo: {respuesta.tiempo_procesamiento:.2f}s")
        print(
            f"   🔍 Síntomas: {len(respuesta.analisis_clinico.sintomas_identificados) if respuesta.analisis_clinico else 0}"
        )
        print(
            f"   🏥 Patologías: {len(respuesta.analisis_clinico.patologias_sugeridas) if respuesta.analisis_clinico else 0}"
        )
        print(
            f"   📋 Escalas: {len(respuesta.analisis_clinico.escalas_recomendadas) if respuesta.analisis_clinico else 0}"
        )
        print(
            f"   🚨 Banderas rojas: {len(respuesta.analisis_clinico.banderas_rojas) if respuesta.analisis_clinico else 0}"
        )
        print(f"   📚 Evidencia: {len(respuesta.evidencia_cientifica)}")
        print(f"   ❌ Errores: {len(respuesta.errores)}")

    print("\n✅ Todas las pruebas completadas!")


if __name__ == "__main__":
    test_unified_copilot()
