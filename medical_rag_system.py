#!/usr/bin/env python3
"""
Sistema RAG médico para recuperación y generación de respuestas basadas en evidencia
"""

import logging
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import time

from medical_apis_integration import MedicalAPIsIntegration
from medical_nlp_processor import nlp_processor, ConsultaProcesada

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EvidenciaCientifica:
    """Estructura para evidencia científica"""
    titulo: str
    autores: List[str]
    doi: str
    fecha_publicacion: str
    resumen: str
    nivel_evidencia: str
    fuente: str  # 'pubmed' o 'europepmc'
    url: str
    relevancia_score: float = 0.0

@dataclass
class RespuestaRAG:
    """Estructura para respuesta RAG"""
    respuesta: str
    evidencias: List[EvidenciaCientifica]
    terminos_utilizados: List[str]
    nivel_confianza: float
    citaciones: List[str]
    recomendaciones: List[str]

class MedicalRAGSystem:
    """Sistema RAG médico para recuperación y generación de respuestas"""
    
    def __init__(self):
        self.apis = MedicalAPIsIntegration()
        self.nlp_processor = nlp_processor
        
        # Configuración de búsqueda
        self.max_evidencias = 5
        self.min_relevancia_score = 0.3
        
        # Plantillas para respuestas
        self.plantillas_respuesta = {
            'tratamiento': {
                'intro': "Basándome en la evidencia científica disponible, aquí están las opciones de tratamiento:",
                'evidencia': "Según {autores} ({año}), {hallazgo}",
                'recomendacion': "Se recomienda {tratamiento} para {condicion}",
                'conclusion': "Estas recomendaciones están basadas en evidencia científica verificable."
            },
            'diagnostico': {
                'intro': "Basándome en la evidencia científica, los posibles diagnósticos incluyen:",
                'evidencia': "La investigación de {autores} ({año}) sugiere que {hallazgo}",
                'recomendacion': "Se sugiere evaluar {diagnostico}",
                'conclusion': "Se recomienda consulta médica para confirmación diagnóstica."
            },
            'rehabilitacion': {
                'intro': "Los programas de rehabilitación basados en evidencia incluyen:",
                'evidencia': "El estudio de {autores} ({año}) demuestra que {hallazgo}",
                'recomendacion': "Se recomienda {ejercicio} para mejorar {funcion}",
                'conclusion': "La rehabilitación debe ser supervisada por profesionales."
            }
        }

    def recuperar_evidencia(self, consulta_procesada: ConsultaProcesada) -> List[EvidenciaCientifica]:
        """Recupera evidencia científica relevante"""
        logger.info(f"🔍 Recuperando evidencia para: {consulta_procesada.terminos_busqueda}")
        
        evidencias = []
        
        # Buscar en PubMed
        for termino in consulta_procesada.terminos_busqueda[:3]:  # Limitar a 3 términos más relevantes
            try:
                tratamientos_pubmed = self.apis.buscar_tratamiento_pubmed(termino, consulta_procesada.especialidad)
                
                for tratamiento in tratamientos_pubmed:
                    evidencia = EvidenciaCientifica(
                        titulo=tratamiento.titulo,
                        autores=tratamiento.autores or [],
                        doi=tratamiento.doi or "Sin DOI",
                        fecha_publicacion=tratamiento.fecha_publicacion or "Fecha no disponible",
                        resumen=tratamiento.resumen or "",
                        nivel_evidencia=self._determinar_nivel_evidencia(tratamiento.titulo, tratamiento.resumen),
                        fuente="pubmed",
                        url=f"https://doi.org/{tratamiento.doi}" if tratamiento.doi and tratamiento.doi != "Sin DOI" else "",
                        relevancia_score=self._calcular_relevancia(tratamiento, consulta_procesada)
                    )
                    evidencias.append(evidencia)
                
                logger.info(f"✅ Encontradas {len(tratamientos_pubmed)} evidencias en PubMed para '{termino}'")
                
            except Exception as e:
                logger.error(f"❌ Error buscando en PubMed para '{termino}': {e}")
        
        # Buscar en Europe PMC
        for termino in consulta_procesada.terminos_busqueda[:3]:
            try:
                tratamientos_europepmc = self.apis.buscar_europepmc(termino, consulta_procesada.especialidad)
                
                for tratamiento in tratamientos_europepmc:
                    evidencia = EvidenciaCientifica(
                        titulo=tratamiento.titulo,
                        autores=tratamiento.autores or [],
                        doi=tratamiento.doi or "Sin DOI",
                        fecha_publicacion=tratamiento.fecha_publicacion or "Fecha no disponible",
                        resumen=tratamiento.resumen or "",
                        nivel_evidencia=self._determinar_nivel_evidencia(tratamiento.titulo, tratamiento.resumen),
                        fuente="europepmc",
                        url=f"https://doi.org/{tratamiento.doi}" if tratamiento.doi and tratamiento.doi != "Sin DOI" else "",
                        relevancia_score=self._calcular_relevancia(tratamiento, consulta_procesada)
                    )
                    evidencias.append(evidencia)
                
                logger.info(f"✅ Encontradas {len(tratamientos_europepmc)} evidencias en Europe PMC para '{termino}'")
                
            except Exception as e:
                logger.error(f"❌ Error buscando en Europe PMC para '{termino}': {e}")
        
        # Filtrar por relevancia y ordenar
        evidencias_filtradas = [
            ev for ev in evidencias 
            if ev.relevancia_score >= self.min_relevancia_score
        ]
        
        # Ordenar por relevancia y fecha
        evidencias_filtradas.sort(key=lambda x: (x.relevancia_score, x.fecha_publicacion), reverse=True)
        
        # Limitar número de evidencias
        evidencias_finales = evidencias_filtradas[:self.max_evidencias]
        
        logger.info(f"📊 Total evidencias recuperadas: {len(evidencias_finales)}")
        
        return evidencias_finales

    def _determinar_nivel_evidencia(self, titulo: str, resumen: str) -> str:
        """Determina el nivel de evidencia basado en el título y resumen"""
        texto_completo = f"{titulo} {resumen}".lower()
        
        # Palabras clave para diferentes niveles de evidencia
        nivel_indicadores = {
            'Nivel I': ['ensayo aleatorizado', 'randomized trial', 'rct', 'meta-análisis', 'meta-analysis'],
            'Nivel II': ['estudio de cohorte', 'cohort study', 'case-control', 'estudio controlado'],
            'Nivel III': ['estudio observacional', 'observational study', 'case series', 'serie de casos'],
            'Nivel IV': ['revisión sistemática', 'systematic review', 'guideline', 'guía clínica'],
            'Nivel V': ['opinión de expertos', 'expert opinion', 'case report', 'reporte de caso']
        }
        
        for nivel, indicadores in nivel_indicadores.items():
            if any(indicator in texto_completo for indicator in indicadores):
                return nivel
        
        return "Nivel V"  # Por defecto

    def _calcular_relevancia(self, tratamiento, consulta_procesada: ConsultaProcesada) -> float:
        """Calcula el score de relevancia de una evidencia"""
        score = 0.0
        texto_completo = f"{tratamiento.titulo} {tratamiento.resumen}".lower()
        
        # Score por coincidencia de términos de búsqueda
        for termino in consulta_procesada.terminos_busqueda:
            if termino.lower() in texto_completo:
                score += 0.3
        
        # Score por coincidencia de síntomas
        for sintoma in consulta_procesada.sintomas:
            if sintoma.localizacion.lower() in texto_completo:
                score += 0.2
        
        # Score por coincidencia de actividades
        for actividad in consulta_procesada.actividades_afectadas:
            if actividad.lower() in texto_completo:
                score += 0.2
        
        # Score por fecha reciente (últimos 5 años)
        if tratamiento.fecha_publicacion:
            try:
                fecha = datetime.strptime(tratamiento.fecha_publicacion, "%Y-%m-%d")
                if (datetime.now() - fecha).days < 1825:  # 5 años
                    score += 0.1
            except:
                pass
        
        # Score por DOI válido
        if tratamiento.doi and tratamiento.doi != "Sin DOI":
            score += 0.1
        
        return min(score, 1.0)  # Máximo 1.0

    def generar_respuesta(self, consulta_procesada: ConsultaProcesada, 
                         evidencias: List[EvidenciaCientifica]) -> RespuestaRAG:
        """Genera una respuesta basada en evidencia científica"""
        logger.info(f"🤖 Generando respuesta RAG con {len(evidencias)} evidencias")
        
        if not evidencias:
            return self._generar_respuesta_sin_evidencia(consulta_procesada)
        
        # Determinar tipo de respuesta
        tipo_respuesta = consulta_procesada.intencion.value
        if tipo_respuesta not in self.plantillas_respuesta:
            tipo_respuesta = 'tratamiento'
        
        plantilla = self.plantillas_respuesta[tipo_respuesta]
        
        # Generar respuesta estructurada
        respuesta = self._construir_respuesta_estructurada(evidencias, plantilla, consulta_procesada)
        
        # Generar citaciones
        citaciones = self._generar_citaciones(evidencias)
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(evidencias, consulta_procesada)
        
        # Calcular nivel de confianza
        nivel_confianza = self._calcular_nivel_confianza(evidencias)
        
        return RespuestaRAG(
            respuesta=respuesta,
            evidencias=evidencias,
            terminos_utilizados=consulta_procesada.terminos_busqueda,
            nivel_confianza=nivel_confianza,
            citaciones=citaciones,
            recomendaciones=recomendaciones
        )

    def _generar_respuesta_sin_evidencia(self, consulta_procesada: ConsultaProcesada) -> RespuestaRAG:
        """Genera respuesta cuando no hay evidencia disponible"""
        respuesta = f"""
        Basándome en la información proporcionada sobre {', '.join(consulta_procesada.terminos_busqueda)}, 
        no encontré evidencia científica específica en las bases de datos médicas consultadas.
        
        Se recomienda:
        1. Consultar con un profesional de la salud para evaluación completa
        2. Realizar estudios adicionales si es necesario
        3. Considerar opciones de tratamiento conservador mientras se evalúa
        """
        
        return RespuestaRAG(
            respuesta=respuesta,
            evidencias=[],
            terminos_utilizados=consulta_procesada.terminos_busqueda,
            nivel_confianza=0.0,
            citaciones=[],
            recomendaciones=["Consultar profesional de la salud", "Evaluación médica completa"]
        )

    def _construir_respuesta_estructurada(self, evidencias: List[EvidenciaCientifica], 
                                        plantilla: Dict, 
                                        consulta_procesada: ConsultaProcesada) -> str:
        """Construye respuesta estructurada basada en evidencia"""
        respuesta = plantilla['intro'] + "\n\n"
        
        for i, evidencia in enumerate(evidencias, 1):
            autores_str = ", ".join(evidencia.autores[:3]) if evidencia.autores else "Autores no disponibles"
            año = evidencia.fecha_publicacion[:4] if evidencia.fecha_publicacion else "Año no disponible"
            
            # Extraer hallazgo principal del resumen
            hallazgo = self._extraer_hallazgo_principal(evidencia.resumen)
            
            respuesta += f"{i}. {plantilla['evidencia'].format(autores=autores_str, año=año, hallazgo=hallazgo)}\n"
            respuesta += f"   Nivel de evidencia: {evidencia.nivel_evidencia}\n"
            if evidencia.doi and evidencia.doi != "Sin DOI":
                respuesta += f"   DOI: {evidencia.doi}\n"
            respuesta += "\n"
        
        respuesta += plantilla['conclusion']
        
        return respuesta

    def _extraer_hallazgo_principal(self, resumen: str) -> str:
        """Extrae el hallazgo principal del resumen"""
        if not resumen:
            return "Se encontraron resultados relevantes"
        
        # Buscar frases que indiquen hallazgos principales
        frases_clave = [
            "se encontró", "se demostró", "se observó", "se concluyó",
            "resultó en", "mostró que", "indicó que", "sugirió que"
        ]
        
        resumen_lower = resumen.lower()
        for frase in frases_clave:
            if frase in resumen_lower:
                # Extraer la frase completa que contiene el hallazgo
                inicio = resumen_lower.find(frase)
                fin = resumen.find(".", inicio)
                if fin == -1:
                    fin = len(resumen)
                return resumen[inicio:fin].strip()
        
        # Si no encuentra frases clave, usar las primeras 100 caracteres
        return resumen[:100] + "..." if len(resumen) > 100 else resumen

    def _generar_citaciones(self, evidencias: List[EvidenciaCientifica]) -> List[str]:
        """Genera lista de citaciones en formato estándar"""
        citaciones = []
        
        for evidencia in evidencias:
            autores_str = ", ".join(evidencia.autores[:3]) if evidencia.autores else "Autores no disponibles"
            año = evidencia.fecha_publicacion[:4] if evidencia.fecha_publicacion else "Año no disponible"
            
            citacion = f"{autores_str} ({año}). {evidencia.titulo}. "
            if evidencia.doi and evidencia.doi != "Sin DOI":
                citacion += f"DOI: {evidencia.doi}"
            else:
                citacion += f"Fuente: {evidencia.fuente.upper()}"
            
            citaciones.append(citacion)
        
        return citaciones

    def _generar_recomendaciones(self, evidencias: List[EvidenciaCientifica], 
                                consulta_procesada: ConsultaProcesada) -> List[str]:
        """Genera recomendaciones basadas en la evidencia"""
        recomendaciones = []
        
        # Recomendaciones basadas en síntomas
        for sintoma in consulta_procesada.sintomas:
            if sintoma.sintoma == 'dolor':
                recomendaciones.append(f"Evaluar dolor en {sintoma.localizacion}")
                if sintoma.intensidad:
                    recomendaciones.append(f"Considerar intensidad del dolor: {sintoma.intensidad}")
        
        # Recomendaciones basadas en actividades
        for actividad in consulta_procesada.actividades_afectadas:
            recomendaciones.append(f"Evaluar limitaciones en {actividad}")
        
        # Recomendaciones basadas en evidencia
        for evidencia in evidencias[:2]:  # Solo las 2 más relevantes
            if "physical therapy" in evidencia.titulo.lower() or "physiotherapy" in evidencia.titulo.lower():
                recomendaciones.append("Considerar fisioterapia como opción de tratamiento")
            if "exercise" in evidencia.titulo.lower() or "ejercicio" in evidencia.titulo.lower():
                recomendaciones.append("Evaluar programa de ejercicios específicos")
        
        # Recomendación general
        recomendaciones.append("Consultar con profesional de la salud para evaluación completa")
        
        return list(set(recomendaciones))  # Eliminar duplicados

    def _calcular_nivel_confianza(self, evidencias: List[EvidenciaCientifica]) -> float:
        """Calcula el nivel de confianza basado en la evidencia"""
        if not evidencias:
            return 0.0
        
        # Calcular score promedio de relevancia
        relevancia_promedio = sum(ev.relevancia_score for ev in evidencias) / len(evidencias)
        
        # Bonus por número de evidencias
        bonus_cantidad = min(len(evidencias) * 0.1, 0.3)
        
        # Bonus por nivel de evidencia
        nivel_scores = {
            'Nivel I': 0.3,
            'Nivel II': 0.2,
            'Nivel III': 0.1,
            'Nivel IV': 0.2,
            'Nivel V': 0.0
        }
        
        nivel_bonus = sum(nivel_scores.get(ev.nivel_evidencia, 0) for ev in evidencias) / len(evidencias)
        
        confianza = relevancia_promedio + bonus_cantidad + nivel_bonus
        return min(confianza, 1.0)  # Máximo 1.0

    def procesar_consulta_completa(self, texto: str, especialidad: str, 
                                  edad: Optional[int] = None, 
                                  genero: Optional[str] = None) -> RespuestaRAG:
        """Procesa una consulta completa usando el pipeline RAG"""
        logger.info(f"🚀 Iniciando procesamiento RAG completo para: {texto[:100]}...")
        
        # Paso 1: Procesamiento NLP
        consulta_procesada = self.nlp_processor.procesar_consulta(texto, especialidad, edad, genero)
        logger.info(f"✅ Procesamiento NLP completado")
        
        # Paso 2: Recuperación de evidencia
        evidencias = self.recuperar_evidencia(consulta_procesada)
        logger.info(f"✅ Recuperación de evidencia completada: {len(evidencias)} evidencias")
        
        # Paso 3: Generación de respuesta
        respuesta_rag = self.generar_respuesta(consulta_procesada, evidencias)
        logger.info(f"✅ Generación de respuesta completada")
        
        return respuesta_rag

# Instancia global del sistema RAG
rag_system = MedicalRAGSystem() 