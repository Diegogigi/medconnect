#!/usr/bin/env python3
"""
Clase Principal del Sistema Unificado de Procesamiento NLP Médico Mejorado
Integra NER, NegEx, UMLS/MeSH, temporalidad, PICO y confianza
"""

import re
import logging
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Importar estructuras del archivo anterior
from unified_nlp_processor_enhanced import (
    IntencionClinica,
    EntidadClinica,
    Temporalidad,
    Intensidad,
    SintomaExtraido,
    PICO,
    ConsultaProcesada,
    AnalisisCompleto,
    NegExProcessor,
    TemporalidadProcessor,
    IntensidadProcessor,
    LateralidadProcessor,
    PICOGenerator,
    TipoEntidad,
    Negacion,
    Lateralidad,
)

logger = logging.getLogger(__name__)


class ClinicalNER:
    """NER clínico basado en reglas y patrones (simulación de spaCy/medSpaCy)"""

    def __init__(self):
        # Patrones de síntomas
        self.patrones_sintomas = {
            "dolor": [
                r"dolor\s+(?:en|del|de)\s+(\w+)",
                r"me\s+duele\s+(?:el|la|los|las)\s+(\w+)",
                r"duele\s+(?:el|la|los|las)\s+(\w+)",
                r"dolor\s+(\w+)",
                r"(\w+)\s+duele",
            ],
            "limitacion": [
                r"no\s+puedo\s+(\w+)",
                r"dificultad\s+(?:para|en)\s+(\w+)",
                r"problema\s+(?:para|en)\s+(\w+)",
                r"limitacion\s+(?:para|en)\s+(\w+)",
            ],
            "debilidad": [
                r"debilidad\s+(?:en|del|de)\s+(\w+)",
                r"no\s+tengo\s+fuerza\s+(?:en|del|de)\s+(\w+)",
                r"(\w+)\s+debil",
            ],
            "rigidez": [
                r"rigidez\s+(?:en|del|de)\s+(\w+)",
                r"(\w+)\s+rígido",
                r"no\s+puedo\s+mover\s+(?:el|la)\s+(\w+)",
            ],
        }

        # Patrones de órganos/anatomía
        self.patrones_organos = {
            "rodilla": ["rodilla", "rodillas", "articulación de la rodilla"],
            "hombro": ["hombro", "hombros", "articulación del hombro"],
            "espalda": ["espalda", "lumbar", "columna", "dorso"],
            "cuello": ["cuello", "cervical", "nuca"],
            "cabeza": ["cabeza", "cráneo", "cerebro"],
            "pecho": ["pecho", "tórax", "esternón"],
            "abdomen": ["abdomen", "vientre", "estómago"],
            "brazo": ["brazo", "brazos", "miembro superior"],
            "pierna": ["pierna", "piernas", "miembro inferior"],
        }

        # Patrones de medicamentos
        self.patrones_medicamentos = [
            r"(?:tomando|tomé|toma)\s+(\w+)",
            r"medicamento\s+(\w+)",
            r"pastilla\s+(?:de\s+)?(\w+)",
            r"(\w+)\s+(?:mg|ml|g)",
        ]

    def extraer_entidades(self, texto: str) -> List[EntidadClinica]:
        """Extrae entidades clínicas del texto"""
        entidades = []
        texto_lower = texto.lower()

        # Extraer síntomas
        for tipo_sintoma, patrones in self.patrones_sintomas.items():
            for patron in patrones:
                matches = re.finditer(patron, texto_lower)
                for match in matches:
                    sintoma_texto = match.group(0)
                    entidad = EntidadClinica(
                        texto=sintoma_texto,
                        tipo=TipoEntidad.SINTOMA,
                        inicio_char=match.start(),
                        fin_char=match.end(),
                        confianza=0.8,
                    )
                    entidades.append(entidad)

        # Extraer órganos
        for organo, terminos in self.patrones_organos.items():
            for termino in terminos:
                if termino in texto_lower:
                    pos = texto_lower.find(termino)
                    entidad = EntidadClinica(
                        texto=termino,
                        tipo=TipoEntidad.ORGANO,
                        inicio_char=pos,
                        fin_char=pos + len(termino),
                        confianza=0.9,
                    )
                    entidades.append(entidad)

        # Extraer medicamentos
        for patron in self.patrones_medicamentos:
            matches = re.finditer(patron, texto_lower)
            for match in matches:
                medicamento = match.group(1)
                entidad = EntidadClinica(
                    texto=medicamento,
                    tipo=TipoEntidad.MEDICAMENTO,
                    inicio_char=match.start(),
                    fin_char=match.end(),
                    confianza=0.7,
                )
                entidades.append(entidad)

        return entidades


class UMLSLinker:
    """Simulador de linking UMLS/MeSH (en producción usar QuickUMLS/scispaCy)"""

    def __init__(self):
        # Mapeo simulado de términos a CUIs y MeSH IDs
        self.mapeo_umls = {
            "dolor": {"cui": "C0013363", "mesh_id": "D010365", "mesh_term": "Pain"},
            "rodilla": {
                "cui": "C0022674",
                "mesh_id": "M01.060.703.520",
                "mesh_term": "Knee",
            },
            "hombro": {
                "cui": "C0036277",
                "mesh_id": "M01.060.703.520",
                "mesh_term": "Shoulder",
            },
            "espalda": {
                "cui": "C0004604",
                "mesh_id": "M01.060.703.520",
                "mesh_term": "Back",
            },
            "lumbar": {
                "cui": "C0024031",
                "mesh_id": "M01.060.703.520",
                "mesh_term": "Lumbar Vertebrae",
            },
            "fisioterapia": {
                "cui": "C0031804",
                "mesh_id": "E02.779",
                "mesh_term": "Physical Therapy",
            },
            "ejercicio": {
                "cui": "C0015250",
                "mesh_id": "G11.427.410.698.277",
                "mesh_term": "Exercise",
            },
        }

    def link_entidad(self, texto: str) -> Tuple[str, str, str]:
        """Liga una entidad a UMLS CUI y MeSH"""
        texto_lower = texto.lower()

        # Buscar coincidencias exactas o parciales
        for termino, info in self.mapeo_umls.items():
            if termino in texto_lower:
                return info["cui"], info["mesh_id"], info["mesh_term"]

        # Si no encuentra, devolver valores vacíos
        return "", "", ""


class ConfianzaCalculator:
    """Calculador de confianza y señales clínicas"""

    def __init__(self):
        self.factores_confianza = {
            "sintomas_consistentes": 0.3,
            "negaciones": 0.2,
            "claridad_intencion": 0.2,
            "detection_pico": 0.15,
            "temporalidad_clara": 0.1,
            "intensidad_especifica": 0.05,
        }

    def calcular_confianza(
        self, consulta: ConsultaProcesada
    ) -> Tuple[float, Dict[str, float]]:
        """Calcula confianza global y señales individuales"""
        señales = {}

        # Factor 1: Síntomas consistentes
        sintomas_positivos = [
            s
            for s in consulta.sintomas
            if s.entidad_clinica.negacion != Negacion.NEGADO
        ]
        señales["sintomas_consistentes"] = min(len(sintomas_positivos) / 3.0, 1.0)

        # Factor 2: Negaciones
        negaciones = sum(
            1
            for s in consulta.sintomas
            if s.entidad_clinica.negacion == Negacion.NEGADO
        )
        señales["negaciones"] = max(0, 1.0 - (negaciones * 0.2))

        # Factor 3: Claridad de intención
        intenciones_claras = ["tratamiento", "diagnostico", "evaluacion"]
        señales["claridad_intencion"] = (
            1.0 if consulta.intencion.value in intenciones_claras else 0.5
        )

        # Factor 4: Detección PICO
        elementos_pico = sum(
            [
                len(consulta.pico.population),
                len(consulta.pico.intervention),
                len(consulta.pico.outcome),
            ]
        )
        señales["detection_pico"] = min(elementos_pico / 4.0, 1.0)

        # Factor 5: Temporalidad clara
        temporalidades_claras = sum(
            1 for s in consulta.sintomas if s.temporalidad.duracion_valor is not None
        )
        señales["temporalidad_clara"] = (
            min(temporalidades_claras / len(consulta.sintomas), 1.0)
            if consulta.sintomas
            else 0.0
        )

        # Factor 6: Intensidad específica
        intensidades_especificas = sum(
            1 for s in consulta.sintomas if s.intensidad.valor_numerico is not None
        )
        señales["intensidad_especifica"] = (
            min(intensidades_especificas / len(consulta.sintomas), 1.0)
            if consulta.sintomas
            else 0.0
        )

        # Calcular confianza global
        confianza_global = sum(
            señales[factor] * peso for factor, peso in self.factores_confianza.items()
        )

        return confianza_global, señales


class UnifiedNLPProcessor:
    """Sistema unificado de procesamiento NLP médico mejorado"""

    def __init__(self):
        logger.info("🧠 Inicializando Sistema Unificado de Procesamiento NLP Mejorado")

        # Inicializar procesadores
        self.ner = ClinicalNER()
        self.negex = NegExProcessor()
        self.temporalidad = TemporalidadProcessor()
        self.intensidad = IntensidadProcessor()
        self.lateralidad = LateralidadProcessor()
        self.pico = PICOGenerator()
        self.umls = UMLSLinker()
        self.confianza = ConfianzaCalculator()

        # Base de datos de síntomas y patologías
        self.sintomas_db = self._load_sintomas_db()
        self.patologias_db = self._load_patologias_db()
        self.escalas_db = self._load_escalas_db()

        logger.info("✅ Sistema Unificado de Procesamiento NLP Mejorado inicializado")

    def procesar_consulta_completa(
        self, texto: str, edad: Optional[int] = None, genero: Optional[str] = None
    ) -> AnalisisCompleto:
        """Procesa una consulta completa con análisis mejorado"""
        start_time = time.time()

        logger.info(f"🧠 Procesando consulta: {texto[:50]}...")

        try:
            # Paso 1: Extraer entidades clínicas
            entidades = self.ner.extraer_entidades(texto)

            # Paso 2: Procesar cada entidad
            sintomas = []
            for entidad in entidades:
                if entidad.tipo == TipoEntidad.SINTOMA:
                    sintoma = self._procesar_sintoma(texto, entidad)
                    if sintoma:
                        sintomas.append(sintoma)

            # Paso 3: Identificar intención clínica
            intencion = self._identificar_intencion(texto)

            # Paso 4: Determinar especialidad
            especialidad = self._determinar_especialidad(texto, sintomas)

            # Paso 5: Generar palabras clave
            palabras_clave = self._generar_palabras_clave(texto, entidades)

            # Paso 6: Identificar patologías
            patologias = self._identificar_patologias(texto, sintomas)

            # Paso 7: Recomendar escalas
            escalas = self._recomendar_escalas(patologias, palabras_clave)

            # Paso 8: Generar términos de búsqueda
            terminos_busqueda = self._generar_terminos_busqueda(texto, sintomas)

            # Paso 9: Generar PICO
            pico = self.pico.generar_pico(texto, entidades)

            # Paso 10: Generar preguntas de evaluación
            preguntas = self._generar_preguntas_evaluacion(palabras_clave, patologias)

            # Crear consulta procesada
            consulta = ConsultaProcesada(
                intencion=intencion,
                sintomas=sintomas,
                entidades_clinicas=entidades,
                actividades_afectadas=self._extraer_actividades_afectadas(texto),
                terminos_busqueda=terminos_busqueda,
                especialidad=especialidad,
                edad=edad,
                genero=genero,
                palabras_clave=palabras_clave,
                patologias_identificadas=patologias,
                escalas_recomendadas=escalas,
                preguntas_evaluacion=preguntas,
                pico=pico,
            )

            # Calcular confianza
            confianza_global, señales = self.confianza.calcular_confianza(consulta)
            consulta.confianza_global = confianza_global
            consulta.señales_clinicas = señales

            # Crear análisis completo
            tiempo_procesamiento = time.time() - start_time
            analisis = AnalisisCompleto(
                consulta_procesada=consulta,
                palabras_clave=palabras_clave,
                patologias_identificadas=patologias,
                escalas_recomendadas=escalas,
                terminos_busqueda_mejorados=terminos_busqueda,
                preguntas_evaluacion=preguntas,
                confianza_global=confianza_global,
                pico=pico,
                tiempo_procesamiento=tiempo_procesamiento,
            )

            logger.info(
                f"✅ Análisis completo realizado en {tiempo_procesamiento:.2f}s"
            )
            return analisis

        except Exception as e:
            logger.error(f"❌ Error en procesamiento NLP: {e}")
            # Retornar análisis vacío en caso de error
            return AnalisisCompleto(
                consulta_procesada=ConsultaProcesada(
                    intencion=IntencionClinica.GENERAL,
                    sintomas=[],
                    entidades_clinicas=[],
                    actividades_afectadas=[],
                    terminos_busqueda=[],
                    especialidad="general",
                ),
                palabras_clave=[],
                patologias_identificadas=[],
                escalas_recomendadas=[],
                terminos_busqueda_mejorados=[],
                preguntas_evaluacion=[],
                confianza_global=0.0,
                pico=PICO(),
                tiempo_procesamiento=time.time() - start_time,
            )

    def _procesar_sintoma(
        self, texto: str, entidad: EntidadClinica
    ) -> Optional[SintomaExtraido]:
        """Procesa un síntoma individual con toda la información clínica"""
        try:
            # Detectar negación
            negacion = self.negex.detectar_negacion(
                texto, entidad.texto, entidad.inicio_char
            )
            entidad.negacion = negacion

            # Detectar lateralidad
            lateralidad = self.lateralidad.detectar_lateralidad(texto, entidad.texto)

            # Extraer temporalidad
            temporalidad = self.temporalidad.extraer_temporalidad(texto)

            # Extraer intensidad
            intensidad = self.intensidad.extraer_intensidad(texto)

            # Link UMLS/MeSH
            cui, mesh_id, mesh_term = self.umls.link_entidad(entidad.texto)
            entidad.cui = cui
            entidad.mesh_id = mesh_id
            entidad.mesh_term = mesh_term

            # Determinar localización
            localizacion = self._determinar_localizacion(texto, entidad)

            # Extraer agravantes y mejorantes
            agravantes = self._extraer_agravantes(texto)
            mejorantes = self._extraer_mejorantes(texto)

            # Calcular confianza
            confianza = self._calcular_confianza_sintoma(
                entidad, temporalidad, intensidad
            )

            # Crear síntoma
            sintoma = SintomaExtraido(
                sintoma=entidad.texto,
                entidad_clinica=entidad,
                localizacion=localizacion,
                temporalidad=temporalidad,
                intensidad=intensidad,
                agravantes=agravantes,
                mejorantes=mejorantes,
                confianza=confianza,
            )

            return sintoma

        except Exception as e:
            logger.error(f"Error procesando síntoma {entidad.texto}: {e}")
            return None

    def _identificar_intencion(self, texto: str) -> IntencionClinica:
        """Identifica la intención clínica del texto"""
        texto_lower = texto.lower()

        palabras_tratamiento = ["tratamiento", "terapia", "cura", "mejorar", "aliviar"]
        palabras_diagnostico = [
            "diagnóstico",
            "diagnostico",
            "qué tengo",
            "que tengo",
            "qué es",
        ]
        palabras_pronostico = [
            "pronóstico",
            "pronostico",
            "evolución",
            "evolucion",
            "futuro",
        ]
        palabras_prevencion = ["prevención", "prevencion", "evitar", "prevenir"]
        palabras_rehabilitacion = [
            "rehabilitación",
            "rehabilitacion",
            "recuperación",
            "recuperacion",
        ]
        palabras_evaluacion = [
            "evaluación",
            "evaluacion",
            "examen",
            "revisión",
            "revision",
        ]

        if any(palabra in texto_lower for palabra in palabras_tratamiento):
            return IntencionClinica.TRATAMIENTO
        elif any(palabra in texto_lower for palabra in palabras_diagnostico):
            return IntencionClinica.DIAGNOSTICO
        elif any(palabra in texto_lower for palabra in palabras_pronostico):
            return IntencionClinica.PRONOSTICO
        elif any(palabra in texto_lower for palabra in palabras_prevencion):
            return IntencionClinica.PREVENCION
        elif any(palabra in texto_lower for palabra in palabras_rehabilitacion):
            return IntencionClinica.REHABILITACION
        elif any(palabra in texto_lower for palabra in palabras_evaluacion):
            return IntencionClinica.EVALUACION
        else:
            return IntencionClinica.GENERAL

    def _determinar_especialidad(
        self, texto: str, sintomas: List[SintomaExtraido]
    ) -> str:
        """Determina la especialidad médica"""
        texto_lower = texto.lower()

        # Verificar localizaciones específicas
        if any(
            "hombro" in s.localizacion or "brazo" in s.localizacion for s in sintomas
        ):
            return "traumatologia"
        elif any(
            "rodilla" in s.localizacion or "pierna" in s.localizacion for s in sintomas
        ):
            return "traumatologia"
        elif any(
            "espalda" in s.localizacion or "columna" in s.localizacion for s in sintomas
        ):
            return "fisiatria"
        elif any("cabeza" in s.localizacion for s in sintomas):
            return "neurologia"
        elif any("pecho" in s.localizacion for s in sintomas):
            return "cardiologia"
        elif any("abdomen" in s.localizacion for s in sintomas):
            return "gastroenterologia"
        else:
            return "medicina_general"

    def _determinar_localizacion(self, texto: str, entidad: EntidadClinica) -> str:
        """Determina la localización del síntoma"""
        texto_lower = texto.lower()

        # Buscar órganos cerca de la entidad
        organos = [
            "rodilla",
            "hombro",
            "espalda",
            "cuello",
            "cabeza",
            "pecho",
            "abdomen",
        ]

        for organo in organos:
            if organo in texto_lower:
                return organo

        return "general"

    def _extraer_agravantes(self, texto: str) -> List[str]:
        """Extrae factores agravantes"""
        agravantes = []
        patrones = [
            r"(?:empeora|agravan|aumenta)\s+(?:con|al|cuando)\s+(\w+)",
            r"(\w+)\s+(?:empeora|agrava|aumenta)",
        ]

        for patron in patrones:
            matches = re.finditer(patron, texto.lower())
            for match in matches:
                agravantes.append(match.group(1))

        return agravantes

    def _extraer_mejorantes(self, texto: str) -> List[str]:
        """Extrae factores mejorantes"""
        mejorantes = []
        patrones = [
            r"(?:mejora|alivia|disminuye)\s+(?:con|al|cuando)\s+(\w+)",
            r"(\w+)\s+(?:mejora|alivia|disminuye)",
        ]

        for patron in patrones:
            matches = re.finditer(patron, texto.lower())
            for match in matches:
                mejorantes.append(match.group(1))

        return mejorantes

    def _extraer_actividades_afectadas(self, texto: str) -> List[str]:
        """Extrae actividades afectadas"""
        actividades = []
        patrones = [
            r"no\s+puedo\s+(\w+)",
            r"dificultad\s+(?:para|en)\s+(\w+)",
            r"problema\s+(?:para|en)\s+(\w+)",
        ]

        for patron in patrones:
            matches = re.finditer(patron, texto.lower())
            for match in matches:
                actividades.append(match.group(1))

        return actividades

    def _calcular_confianza_sintoma(
        self,
        entidad: EntidadClinica,
        temporalidad: Temporalidad,
        intensidad: Intensidad,
    ) -> float:
        """Calcula la confianza de un síntoma"""
        confianza = entidad.confianza

        # Bonus por temporalidad clara
        if temporalidad.duracion_valor is not None:
            confianza += 0.1

        # Bonus por intensidad específica
        if intensidad.valor_numerico is not None:
            confianza += 0.1

        # Penalización por negación
        if entidad.negacion == Negacion.NEGADO:
            confianza *= 0.5

        return min(confianza, 1.0)

    def _generar_palabras_clave(
        self, texto: str, entidades: List[EntidadClinica]
    ) -> List:
        """Genera palabras clave basadas en entidades"""
        # Implementación simplificada
        return []

    def _identificar_patologias(
        self, texto: str, sintomas: List[SintomaExtraido]
    ) -> List:
        """Identifica patologías basadas en síntomas"""
        # Implementación simplificada
        return []

    def _recomendar_escalas(self, patologias: List, palabras_clave: List) -> List:
        """Recomienda escalas de evaluación"""
        # Implementación simplificada
        return []

    def _generar_terminos_busqueda(
        self, texto: str, sintomas: List[SintomaExtraido]
    ) -> List[str]:
        """Genera términos de búsqueda"""
        terminos = []

        for sintoma in sintomas:
            if sintoma.entidad_clinica.negacion != Negacion.NEGADO:
                terminos.append(sintoma.sintoma)
                if sintoma.entidad_clinica.mesh_term:
                    terminos.append(sintoma.entidad_clinica.mesh_term)

        return list(set(terminos))

    def _generar_preguntas_evaluacion(
        self, palabras_clave: List, patologias: List
    ) -> List[str]:
        """Genera preguntas de evaluación"""
        preguntas = [
            "¿Cuándo comenzó el problema?",
            "¿Qué factores agravan los síntomas?",
            "¿Qué factores mejoran los síntomas?",
            "¿Ha tenido este problema antes?",
            "¿Qué tratamientos ha probado?",
        ]

        return preguntas

    def _load_sintomas_db(self) -> Dict:
        """Carga base de datos de síntomas"""
        return {}

    def _load_patologias_db(self) -> Dict:
        """Carga base de datos de patologías"""
        return {}

    def _load_escalas_db(self) -> Dict:
        """Carga base de datos de escalas"""
        return {}


# Instancia global del sistema mejorado
unified_nlp_enhanced = UnifiedNLPProcessor()


def test_nlp_enhanced_main():
    """Función de prueba para el sistema NLP mejorado principal"""
    print("🧪 Probando Sistema NLP Mejorado Principal")
    print("=" * 60)

    # Casos de prueba
    casos_prueba = [
        "Tengo dolor en la rodilla derecha desde hace 2 semanas, EVA 7/10",
        "No presenta fiebre ni dolor de cabeza",
        "Dolor lumbar crónico en adulto mayor",
        "Duda si tiene dolor en el hombro izquierdo",
    ]

    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n🔍 Caso {i}: {caso}")

        start_time = time.time()
        analisis = unified_nlp_enhanced.procesar_consulta_completa(caso)
        tiempo = time.time() - start_time

        print(f"   ✅ Tiempo: {tiempo:.2f}s")
        print(f"   📊 Confianza: {analisis.confianza_global:.2f}")
        print(f"   🔍 Síntomas: {len(analisis.consulta_procesada.sintomas)}")
        print(f"   🏥 Patologías: {len(analisis.patologias_identificadas)}")
        print(f"   📋 Escalas: {len(analisis.escalas_recomendadas)}")
        print(
            f"   🎯 PICO: {len(analisis.pico.population)} población, {len(analisis.pico.intervention)} intervención"
        )

        # Mostrar señales clínicas
        if analisis.consulta_procesada.señales_clinicas:
            print(f"   📈 Señales clínicas:")
            for señal, valor in analisis.consulta_procesada.señales_clinicas.items():
                print(f"      {señal}: {valor:.2f}")

    print("\n✅ Todas las pruebas completadas!")


if __name__ == "__main__":
    test_nlp_enhanced_main()
