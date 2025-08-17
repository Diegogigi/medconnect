#!/usr/bin/env python3
"""
Módulo de integración con APIs médicas gratuitas para mejorar la IA clínica
"""

import requests
import json
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import quote
import re # Added for _limpiar_termino_busqueda

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TratamientoCientifico:
    """Estructura para tratamientos basados en evidencia científica"""
    titulo: str
    descripcion: str
    doi: str
    fuente: str
    tipo_evidencia: str
    fecha_publicacion: str
    autores: List[str]
    resumen: str
    keywords: List[str]
    año_publicacion: str = "N/A"
    nivel_evidencia: str = "Nivel V"
    evidencia_cientifica: str = "Evidencia científica"
    contraindicaciones: str = "Consultar con profesional de la salud"

@dataclass
class PreguntaCientifica:
    """Estructura para preguntas basadas en evidencia"""
    pregunta: str
    contexto: str
    fuente: str
    relevancia: str
    tipo: str

@dataclass
class PlanIntervencion:
    """Estructura para planes de intervención específicos"""
    titulo: str
    descripcion: str
    tecnicas_especificas: List[str]
    aplicaciones_practicas: List[str]
    masajes_tecnicas: List[str]
    ejercicios_especificos: List[str]
    protocolo_tratamiento: List[str]
    evidencia_cientifica: str
    doi_referencia: str
    nivel_evidencia: str
    contraindicaciones: List[str]
    frecuencia_sesiones: str
    duracion_tratamiento: str

class MedicalAPIsIntegration:
    """Integración con APIs médicas gratuitas"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MedConnect-IA/1.0 (https://medconnect.cl)'
        })
        
        # Configuración de rate limiting
        self.last_request_time = 0
        self.min_interval = 0.5  # 2 requests per second con API Key
        
        # API Key para NCBI
        self.ncbi_api_key = 'fc67562a31bc52ad079357404cf1f6572107'
        
        # Mapeo de términos en español a inglés para mejores búsquedas
        self.terminos_espanol_ingles = {
            'dolor lumbar': 'low back pain',
            'dolor de espalda': 'back pain',
            'problemas de habla': 'speech disorders',
            'trastornos del habla': 'speech disorders',
            'ansiedad': 'anxiety',
            'depresión': 'depression',
            'diabetes': 'diabetes',
            'hipertensión': 'hypertension',
            'artritis': 'arthritis',
            'fisioterapia': 'physical therapy',
            'fonoaudiologia': 'speech therapy',
            'psicologia': 'psychology',
            'medicina': 'medicine',
            'kinesiologia': 'physical therapy',
            'terapia ocupacional': 'occupational therapy',
            'dolor en brazo': 'arm pain',
            'dolor en hombro': 'shoulder pain',
            'dolor en cuello': 'neck pain',
            'dolor en espalda': 'back pain',
            'dolor en rodilla': 'knee pain',
            'dolor en tobillo': 'ankle pain',
            'dolor en muñeca': 'wrist pain',
            'dolor en codo': 'elbow pain',
            'elevar el brazo': 'shoulder pain',
            'brazo': 'arm pain',
            'hombro': 'shoulder pain',
            'cuello': 'neck pain',
            'espalda': 'back pain',
            'rodilla': 'knee pain',
            'tobillo': 'ankle pain',
            'muñeca': 'wrist pain',
            'codo': 'elbow pain',
            'flexión de hombro': 'shoulder pain',
            'elevaciones laterales': 'shoulder pain',
            'secarme': 'shoulder pain',
            # Condiciones específicas importantes
            'sindrome moebius': 'Moebius syndrome',
            'síndrome moebius': 'Moebius syndrome',
            'moebius': 'Moebius syndrome',
            'parálisis facial': 'facial paralysis',
            'paralisis facial': 'facial paralysis',
            'dificultad lactancia': 'breastfeeding difficulty',
            'problemas lactancia': 'breastfeeding problems',
            'lactancia materna': 'breastfeeding',
            'bajo peso': 'underweight',
            'desnutrición': 'malnutrition',
            'desnutricion': 'malnutrition',
            'frenillo lingual': 'tongue tie',
            'anquiloglosia': 'ankyloglossia',
            'deglución': 'swallowing',
            'deglucion': 'swallowing',
            'disfagia': 'dysphagia',
            'trastornos deglución': 'swallowing disorders',
            'problemas deglución': 'swallowing problems'
        }
        
        # Diccionario de condiciones médicas específicas para mejor detección
        self.condiciones_especificas = {
            'sindrome_moebius': {
                'terminos': ['moebius', 'síndrome moebius', 'sindrome moebius', 'parálisis facial congénita'],
                'mesh_terms': ['"Moebius Syndrome"[MeSH Terms]', '"Facial Paralysis"[MeSH Terms]'],
                'especialidades': ['fonoaudiologia', 'pediatria', 'neurologia'],
                'tecnicas_especificas': [
                    'Estimulación orofacial',
                    'Técnicas de succión mejorada',
                    'Posicionamiento para lactancia',
                    'Ejercicios de lengua y labios',
                    'Masaje facial'
                ]
            },
            'anquiloglosia': {
                'terminos': ['frenillo lingual', 'anquiloglosia', 'tongue tie', 'frenillo corto'],
                'mesh_terms': ['"Ankyloglossia"[MeSH Terms]', '"Tongue"[MeSH Terms]'],
                'especialidades': ['fonoaudiologia', 'pediatria'],
                'tecnicas_especificas': [
                    'Ejercicios de lengua',
                    'Técnicas de succión',
                    'Posicionamiento para alimentación',
                    'Estimulación oral'
                ]
            },
            'disfagia': {
                'terminos': ['disfagia', 'dificultad para tragar', 'problemas deglución', 'dificultad deglución'],
                'mesh_terms': ['"Deglutition Disorders"[MeSH Terms]', '"Dysphagia"[MeSH Terms]'],
                'especialidades': ['fonoaudiologia', 'nutricion'],
                'tecnicas_especificas': [
                    'Ejercicios de deglución',
                    'Técnicas de compensación',
                    'Modificación de consistencia',
                    'Posicionamiento para alimentación'
                ]
            },
            'dolor_lumbar': {
                'terminos': ['dolor lumbar', 'lumbalgia', 'dolor de espalda baja', 'low back pain'],
                'mesh_terms': ['"Low Back Pain"[MeSH Terms]', '"Back Pain"[MeSH Terms]'],
                'especialidades': ['fisioterapia', 'kinesiologia'],
                'tecnicas_especificas': [
                    'Terapia manual',
                    'Ejercicios de estabilización',
                    'Masaje terapéutico',
                    'Técnicas de movilización'
                ]
            }
        }
    
    def _detectar_condiciones_especificas(self, texto: str) -> List[str]:
        """Detecta condiciones médicas específicas en el texto"""
        condiciones_detectadas = []
        texto_lower = texto.lower()
        
        for condicion, info in self.condiciones_especificas.items():
            for termino in info['terminos']:
                if termino in texto_lower:
                    condiciones_detectadas.append(condicion)
                    break
        
        return condiciones_detectadas
    
    def _generar_plan_intervencion_especifico(self, condicion: str, especialidad: str, estudios_cientificos: List[TratamientoCientifico]) -> PlanIntervencion:
        """Genera un plan de intervención específico basado en la condición y especialidad"""
        
        # Detectar condiciones específicas
        condiciones_detectadas = self._detectar_condiciones_especificas(condicion)
        
        # Generar técnicas específicas según especialidad y condición
        tecnicas_especificas = self._generar_tecnicas_especificas(condicion, especialidad, condiciones_detectadas)
        aplicaciones_practicas = self._generar_aplicaciones_practicas(condicion, especialidad, condiciones_detectadas)
        masajes_tecnicas = self._generar_masajes_tecnicas(condicion, especialidad, condiciones_detectadas)
        ejercicios_especificos = self._generar_ejercicios_especificos(condicion, especialidad, condiciones_detectadas)
        protocolo_tratamiento = self._generar_protocolo_tratamiento(condicion, especialidad, condiciones_detectadas)
        
        # Obtener evidencia científica de los estudios
        evidencia_cientifica = "Basado en evidencia científica actualizada"
        doi_referencia = "Múltiples fuentes"
        if estudios_cientificos:
            evidencia_cientifica = f"Basado en {len(estudios_cientificos)} estudios científicos"
            if estudios_cientificos[0].doi != "Sin DOI":
                doi_referencia = estudios_cientificos[0].doi
        
        return PlanIntervencion(
            titulo=f"Plan de Intervención - {especialidad.title()}",
            descripcion=f"Plan integral de tratamiento para {condicion} basado en evidencia científica",
            tecnicas_especificas=tecnicas_especificas,
            aplicaciones_practicas=aplicaciones_practicas,
            masajes_tecnicas=masajes_tecnicas,
            ejercicios_especificos=ejercicios_especificos,
            protocolo_tratamiento=protocolo_tratamiento,
            evidencia_cientifica=evidencia_cientifica,
            doi_referencia=doi_referencia,
            nivel_evidencia="Nivel A",
            contraindicaciones=self._generar_contraindicaciones(especialidad),
            frecuencia_sesiones=self._determinar_frecuencia_sesiones(especialidad),
            duracion_tratamiento=self._determinar_duracion_tratamiento(especialidad)
        )
    
    def _generar_tecnicas_especificas(self, condicion: str, especialidad: str, condiciones_detectadas: List[str]) -> List[str]:
        """Genera técnicas específicas según la especialidad y condición"""
        tecnicas = []
        
        if 'fonoaudiologia' in especialidad.lower():
            if 'sindrome_moebius' in condiciones_detectadas:
                tecnicas = [
                    "Estimulación orofacial con masaje facial",
                    "Técnicas de succión mejorada con posicionamiento",
                    "Ejercicios de lengua y labios con resistencia",
                    "Técnicas de alimentación adaptada",
                    "Estimulación sensorial oral"
                ]
            elif 'anquiloglosia' in condiciones_detectadas:
                tecnicas = [
                    "Ejercicios de elevación de lengua",
                    "Técnicas de succión con posicionamiento",
                    "Estimulación de movimientos linguales",
                    "Técnicas de alimentación compensatoria"
                ]
            elif 'disfagia' in condiciones_detectadas:
                tecnicas = [
                    "Ejercicios de deglución con modificaciones posturales",
                    "Técnicas de compensación deglutoria",
                    "Estimulación sensorial faríngea",
                    "Técnicas de protección de vía aérea"
                ]
            else:
                tecnicas = [
                    "Evaluación funcional del habla y deglución",
                    "Técnicas de rehabilitación vocal",
                    "Ejercicios de articulación",
                    "Técnicas de respiración"
                ]
        
        elif 'fisioterapia' in especialidad.lower() or 'kinesiologia' in especialidad.lower():
            if 'dolor_lumbar' in condiciones_detectadas:
                tecnicas = [
                    "Terapia manual con técnicas de movilización",
                    "Ejercicios de estabilización lumbar",
                    "Masaje terapéutico profundo",
                    "Técnicas de McKenzie",
                    "Ejercicios de fortalecimiento progresivo"
                ]
            else:
                tecnicas = [
                    "Evaluación funcional completa",
                    "Terapia manual específica",
                    "Ejercicios terapéuticos",
                    "Técnicas de movilización articular",
                    "Ejercicios de fortalecimiento muscular"
                ]
        
        elif 'psicologia' in especialidad.lower():
            tecnicas = [
                "Terapia cognitivo-conductual",
                "Técnicas de relajación progresiva",
                "Intervención en crisis",
                "Terapia de aceptación y compromiso",
                "Técnicas de mindfulness"
            ]
        
        elif 'nutricion' in especialidad.lower():
            tecnicas = [
                "Evaluación nutricional completa",
                "Planificación de comidas personalizada",
                "Educación nutricional",
                "Seguimiento de progreso",
                "Modificaciones dietéticas específicas"
            ]
        
        return tecnicas
    
    def _generar_aplicaciones_practicas(self, condicion: str, especialidad: str, condiciones_detectadas: List[str]) -> List[str]:
        """Genera aplicaciones prácticas específicas"""
        aplicaciones = []
        
        if 'fonoaudiologia' in especialidad.lower():
            if 'sindrome_moebius' in condiciones_detectadas:
                aplicaciones = [
                    "Posicionamiento del lactante para facilitar la succión",
                    "Uso de técnicas de estimulación oral previa a la alimentación",
                    "Aplicación de masaje facial para mejorar la movilidad",
                    "Técnicas de alimentación con cuchara adaptada",
                    "Estimulación sensorial con diferentes texturas"
                ]
            else:
                aplicaciones = [
                    "Aplicación de técnicas de rehabilitación vocal",
                    "Implementación de ejercicios de articulación",
                    "Aplicación de técnicas de deglución segura",
                    "Uso de ayudas técnicas para comunicación"
                ]
        
        elif 'fisioterapia' in especialidad.lower() or 'kinesiologia' in especialidad.lower():
            aplicaciones = [
                "Aplicación de técnicas de terapia manual",
                "Implementación de programa de ejercicios domiciliarios",
                "Aplicación de técnicas de movilización",
                "Uso de agentes físicos (calor, frío, electroterapia)",
                "Aplicación de técnicas de vendaje funcional"
            ]
        
        return aplicaciones
    
    def _generar_masajes_tecnicas(self, condicion: str, especialidad: str, condiciones_detectadas: List[str]) -> List[str]:
        """Genera técnicas de masaje específicas"""
        masajes = []
        
        if 'fonoaudiologia' in especialidad.lower():
            if 'sindrome_moebius' in condiciones_detectadas:
                masajes = [
                    "Masaje facial con técnicas de estimulación",
                    "Masaje de lengua con movimientos circulares",
                    "Masaje de labios para mejorar la movilidad",
                    "Masaje de mejillas para estimulación sensorial"
                ]
        
        elif 'fisioterapia' in especialidad.lower() or 'kinesiologia' in especialidad.lower():
            masajes = [
                "Masaje terapéutico profundo",
                "Masaje de tejidos blandos",
                "Masaje de puntos gatillo",
                "Masaje de drenaje linfático",
                "Masaje de relajación muscular"
            ]
        
        return masajes
    
    def _generar_ejercicios_especificos(self, condicion: str, especialidad: str, condiciones_detectadas: List[str]) -> List[str]:
        """Genera ejercicios específicos"""
        ejercicios = []
        
        if 'fonoaudiologia' in especialidad.lower():
            if 'sindrome_moebius' in condiciones_detectadas:
                ejercicios = [
                    "Ejercicios de elevación de lengua",
                    "Ejercicios de protrusión lingual",
                    "Ejercicios de movimientos labiales",
                    "Ejercicios de succión con resistencia",
                    "Ejercicios de masticación"
                ]
        
        elif 'fisioterapia' in especialidad.lower() or 'kinesiologia' in especialidad.lower():
            ejercicios = [
                "Ejercicios de fortalecimiento progresivo",
                "Ejercicios de estabilización",
                "Ejercicios de movilidad articular",
                "Ejercicios de equilibrio y coordinación",
                "Ejercicios de resistencia muscular"
            ]
        
        return ejercicios
    
    def _generar_protocolo_tratamiento(self, condicion: str, especialidad: str, condiciones_detectadas: List[str]) -> List[str]:
        """Genera protocolo de tratamiento específico"""
        protocolo = []
        
        if 'fonoaudiologia' in especialidad.lower():
            protocolo = [
                "Evaluación inicial completa",
                "Establecimiento de objetivos específicos",
                "Aplicación de técnicas específicas",
                "Seguimiento y re-evaluación",
                "Educación a familiares/cuidadores"
            ]
        
        elif 'fisioterapia' in especialidad.lower() or 'kinesiologia' in especialidad.lower():
            protocolo = [
                "Evaluación funcional inicial",
                "Diseño de programa individualizado",
                "Aplicación de técnicas manuales",
                "Progresión de ejercicios",
                "Evaluación de resultados"
            ]
        
        return protocolo
    
    def _generar_contraindicaciones(self, especialidad: str) -> List[str]:
        """Genera contraindicaciones según la especialidad"""
        if 'fonoaudiologia' in especialidad.lower():
            return ["Aspiración severa", "Infección activa", "Trauma reciente"]
        elif 'fisioterapia' in especialidad.lower() or 'kinesiologia' in especialidad.lower():
            return ["Fracturas inestables", "Infección activa", "Trombosis venosa"]
        elif 'psicologia' in especialidad.lower():
            return ["Psicosis activa", "Riesgo suicida", "Crisis aguda"]
        else:
            return ["Consultar con profesional de la salud"]
    
    def _determinar_frecuencia_sesiones(self, especialidad: str) -> str:
        """Determina la frecuencia de sesiones según especialidad"""
        if 'fonoaudiologia' in especialidad.lower():
            return "2-3 sesiones por semana"
        elif 'fisioterapia' in especialidad.lower() or 'kinesiologia' in especialidad.lower():
            return "2-4 sesiones por semana"
        elif 'psicologia' in especialidad.lower():
            return "1-2 sesiones por semana"
        else:
            return "Según indicación profesional"
    
    def _determinar_duracion_tratamiento(self, especialidad: str) -> str:
        """Determina la duración del tratamiento según especialidad"""
        if 'fonoaudiologia' in especialidad.lower():
            return "8-12 semanas"
        elif 'fisioterapia' in especialidad.lower() or 'kinesiologia' in especialidad.lower():
            return "6-12 semanas"
        elif 'psicologia' in especialidad.lower():
            return "12-24 semanas"
        else:
            return "Según evolución clínica"

    def _traducir_termino(self, termino):
        """Traduce un término de español a inglés si es posible"""
        termino_lower = termino.lower().strip()
        return self.terminos_espanol_ingles.get(termino_lower, termino)
    
    def _traducir_especialidad(self, especialidad):
        """Traduce especialidad de español a inglés"""
        mapeo_especialidades = {
            'kinesiologia': 'physical therapy',
            'fisioterapia': 'physical therapy',
            'fonoaudiologia': 'speech therapy',
            'psicologia': 'psychology',
            'medicina': 'medicine',
            'terapia_ocupacional': 'occupational therapy',
            'general': 'general medicine'
        }
        return mapeo_especialidades.get(especialidad.lower(), especialidad)
        
    def _rate_limit(self):
        """Implementar rate limiting para APIs"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            time.sleep(self.min_interval - time_since_last)
        self.last_request_time = time.time()
    
    def buscar_tratamiento_pubmed(self, condicion, especialidad, edad_paciente=None):
        """Busca tratamientos en PubMed con búsqueda mejorada y caché inteligente"""
        try:
            # Normalizar y limpiar la condición
            condicion_limpia = self._limpiar_termino_busqueda(condicion)
            
            # Crear clave de caché única
            cache_key = f"pubmed_{hash(condicion_limpia + especialidad + str(edad_paciente))}"
            
            # Verificar caché primero
            cached_result = self._get_cached_search_result(cache_key)
            if cached_result:
                logger.info(f"✅ Usando resultado del caché para: {condicion_limpia}")
                return cached_result
            
            logger.info(f"🔍 Búsqueda PubMed: '{condicion}' -> '{condicion_limpia}' en '{especialidad}'")
            
            tratamientos_encontrados = []
            errores_pubmed = 0
            max_errores = 3
            
            # Generar términos de búsqueda más específicos y relevantes
            terminos_busqueda = self._generar_terminos_busqueda_mejorados(condicion_limpia, especialidad, edad_paciente)
            
            # Limitar a los 3 términos más relevantes para evitar búsquedas excesivas
            terminos_busqueda = terminos_busqueda[:3]
            
            for termino in terminos_busqueda:
                try:
                    # Búsqueda más específica con filtros mejorados
                    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                    params = {
                        'db': 'pubmed',
                        'term': f'"{termino}"[Title/Abstract] AND ("treatment"[Title/Abstract] OR "therapy"[Title/Abstract] OR "intervention"[Title/Abstract]) AND ("2020"[Date - Publication] : "2025"[Date - Publication])',
                        'retmode': 'json',
                        'retmax': 8,  # Aumentado para mejor cobertura
                        'sort': 'relevance',
                        'field': 'title',
                        'api_key': self.ncbi_api_key,
                        'tool': 'MedConnect-IA',
                        'email': 'support@medconnect.cl'
                    }
                    
                    logger.info(f"🔍 Consultando PubMed con término específico: {termino}")
                    response = requests.get(url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                                ids = data['esearchresult']['idlist']
                                
                                if ids:
                                    logger.info(f"✅ Encontrados {len(ids)} artículos para '{termino}'")
                                    detalles = self._obtener_detalles_pubmed(ids)
                                    
                                    for detalle in detalles:
                                        if detalle and self._es_articulo_altamente_relevante(detalle, condicion_limpia, especialidad):
                                            tratamientos_encontrados.append(detalle)
                                else:
                                    logger.info(f"⚠️ No se encontraron artículos para '{termino}'")
                            else:
                                logger.warning(f"⚠️ Respuesta inesperada de PubMed para '{termino}'")
                                errores_pubmed += 1
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"❌ Error decodificando JSON de PubMed: {e}")
                            errores_pubmed += 1
                            continue
                    else:
                        logger.warning(f"⚠️ Error HTTP {response.status_code} para '{termino}'")
                        errores_pubmed += 1
                        
                        if errores_pubmed >= max_errores:
                            logger.warning(f"⚠️ Demasiados errores en PubMed ({errores_pubmed}), cambiando a Europe PMC")
                            return self._busqueda_fallback_europepmc(condicion_limpia, especialidad, edad_paciente)
                        continue
                    
                    # Pausa para evitar rate limiting
                    time.sleep(1.5)  # Aumentado para mayor estabilidad
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"⚠️ Timeout en PubMed para '{termino}'")
                    errores_pubmed += 1
                    if errores_pubmed >= max_errores:
                        logger.warning(f"⚠️ Demasiados timeouts en PubMed, cambiando a Europe PMC")
                        return self._busqueda_fallback_europepmc(condicion_limpia, especialidad, edad_paciente)
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Error buscando término '{termino}': {e}")
                    errores_pubmed += 1
                    if errores_pubmed >= max_errores:
                        logger.warning(f"⚠️ Demasiados errores en PubMed, cambiando a Europe PMC")
                        return self._busqueda_fallback_europepmc(condicion_limpia, especialidad, edad_paciente)
                    continue
            
            # Eliminar duplicados y ordenar por relevancia
            tratamientos_unicos = self._eliminar_duplicados_tratamientos(tratamientos_encontrados)
            
            # Filtrar solo los 10 más relevantes
            tratamientos_filtrados = self._filtrar_papers_mas_relevantes(tratamientos_unicos, condicion_limpia, especialidad, max_papers=10)
            
            # Guardar en caché
            self._set_cached_search_result(cache_key, tratamientos_filtrados)
            
            logger.info(f"✅ Encontrados {len(tratamientos_filtrados)} papers altamente relevantes de {len(tratamientos_unicos)} totales para {condicion_limpia}")
            
            return tratamientos_filtrados
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda PubMed: {e}")
            return self._busqueda_fallback_europepmc(condicion, especialidad, edad_paciente)

    def _es_articulo_altamente_relevante(self, articulo, condicion, especialidad):
        """Determina si un artículo es altamente relevante usando criterios más estrictos"""
        if not articulo or not articulo.titulo:
            return False
        
        titulo_lower = articulo.titulo.lower()
        condicion_lower = condicion.lower()
        especialidad_lower = especialidad.lower()
        
        # Criterios de relevancia más estrictos
        criterios_relevancia = []
        
        # 1. Verificar palabras clave específicas de la condición
        palabras_clave_condicion = self._extraer_palabras_clave_especificas(condicion)
        coincidencias_condicion = sum(1 for palabra in palabras_clave_condicion if palabra in titulo_lower)
        criterios_relevancia.append(coincidencias_condicion >= 2)  # Al menos 2 palabras clave
        
        # 2. Verificar términos de la especialidad
        terminos_especialidad = self._obtener_terminos_especialidad(especialidad)
        coincidencias_especialidad = sum(1 for termino in terminos_especialidad if termino in titulo_lower)
        criterios_relevancia.append(coincidencias_especialidad >= 1)  # Al menos 1 término de especialidad
        
        # 3. Verificar términos de tratamiento
        terminos_tratamiento = ['treatment', 'therapy', 'intervention', 'rehabilitation', 'exercise']
        coincidencias_tratamiento = sum(1 for termino in terminos_tratamiento if termino in titulo_lower)
        criterios_relevancia.append(coincidencias_tratamiento >= 1)  # Al menos 1 término de tratamiento
        
        # 4. Verificar que no sea un artículo de revisión general
        exclusiones = ['review', 'meta-analysis', 'systematic review', 'overview']
        es_exclusion = any(exclusion in titulo_lower for exclusion in exclusiones)
        
        # El artículo es relevante si cumple al menos 2 criterios y no es una exclusión
        return sum(criterios_relevancia) >= 2 and not es_exclusion

    def _extraer_palabras_clave_especificas(self, condicion):
        """Extrae palabras clave específicas y relevantes de la condición"""
        palabras_clave = []
        condicion_lower = condicion.lower()
        
        # Mapeo más específico de términos médicos
        mapeo_especifico = {
            'dolor': ['pain', 'ache', 'discomfort'],
            'rodilla': ['knee', 'patellar', 'meniscal'],
            'hombro': ['shoulder', 'rotator cuff', 'acromial'],
            'cuello': ['neck', 'cervical', 'cervical spine'],
            'espalda': ['back', 'lumbar', 'thoracic', 'spine'],
            'brazo': ['arm', 'upper limb', 'forearm'],
            'pierna': ['leg', 'lower limb', 'thigh'],
            'lumbar': ['lumbar', 'low back', 'lumbosacral'],
            'cervical': ['cervical', 'neck', 'cervical spine'],
            'dorsal': ['thoracic', 'dorsal', 'mid back'],
            'fisioterapia': ['physical therapy', 'physiotherapy'],
            'kinesiologia': ['physical therapy', 'kinesiology'],
            'rehabilitacion': ['rehabilitation', 'rehab'],
            'ejercicio': ['exercise', 'training', 'workout'],
            'lesion': ['injury', 'trauma', 'damage'],
            'tratamiento': ['treatment', 'therapy', 'intervention'],
            'terapia': ['therapy', 'treatment', 'intervention'],
            'correr': ['running', 'jogging', 'sprint'],
            'saltar': ['jumping', 'leap', 'hop'],
            'levantar': ['lifting', 'weight', 'strength'],
            'trabajar': ['work', 'occupational', 'ergonomic']
        }
        
        for termino_esp, terminos_en in mapeo_especifico.items():
            if termino_esp in condicion_lower:
                palabras_clave.extend(terminos_en)
        
        # Si no se encontraron palabras clave específicas, usar términos generales pero más restrictivos
        if not palabras_clave:
            palabras = condicion_lower.split()
            for palabra in palabras:
                if len(palabra) > 4:  # Solo palabras de más de 4 caracteres
                    palabras_clave.append(palabra)
        
        return palabras_clave

    def _get_cached_search_result(self, cache_key):
        """Obtiene resultado del caché de búsqueda"""
        try:
            # Implementar caché simple en memoria con timeout
            current_time = time.time()
            if hasattr(self, '_search_cache'):
                if cache_key in self._search_cache:
                    data, timestamp = self._search_cache[cache_key]
                    if current_time - timestamp < 1800:  # 30 minutos de caché
                        return data
                    else:
                        del self._search_cache[cache_key]
            return None
        except Exception as e:
            logger.warning(f"⚠️ Error accediendo al caché: {e}")
            return None

    def _set_cached_search_result(self, cache_key, data):
        """Guarda resultado en el caché de búsqueda"""
        try:
            if not hasattr(self, '_search_cache'):
                self._search_cache = {}
            
            # Limpiar caché si es muy grande
            if len(self._search_cache) > 100:
                # Eliminar entradas más antiguas
                sorted_cache = sorted(self._search_cache.items(), key=lambda x: x[1][1])
                for key, _ in sorted_cache[:50]:
                    del self._search_cache[key]
            
            self._search_cache[cache_key] = (data, time.time())
            logger.info(f"💾 Resultado guardado en caché: {cache_key}")
        except Exception as e:
            logger.warning(f"⚠️ Error guardando en caché: {e}")

    def _generar_terminos_busqueda_mejorados(self, condicion, especialidad, edad_paciente=None):
        """Genera términos de búsqueda mejorados y más específicos"""
        terminos = []
        
        # 1. Términos específicos de la condición
        palabras_clave = self._extraer_palabras_clave_especificas(condicion)
        terminos.extend(palabras_clave)
        
        # 2. Combinaciones específicas de condición + especialidad
        terminos_especialidad = self._obtener_terminos_especialidad(especialidad)
        for palabra_clave in palabras_clave[:2]:  # Solo las 2 primeras palabras clave
            for termino_esp in terminos_especialidad[:2]:  # Solo los 2 primeros términos de especialidad
                terminos.append(f"{palabra_clave} {termino_esp}")
        
        # 3. Términos específicos por edad si está disponible
        if edad_paciente is not None:
            terminos_edad = self._obtener_terminos_por_edad(edad_paciente, especialidad)
            terminos.extend(terminos_edad[:2])  # Solo los 2 primeros términos de edad
        
        # 4. Términos de tratamiento específicos
        terminos_tratamiento = self._obtener_terminos_tratamiento(condicion)
        terminos.extend(terminos_tratamiento[:2])  # Solo los 2 primeros términos de tratamiento
        
        # Eliminar duplicados y limitar a los más relevantes
        terminos_unicos = list(dict.fromkeys(terminos))  # Mantener orden
        return terminos_unicos[:5]  # Máximo 5 términos más relevantes

    def _busqueda_fallback_europepmc(self, condicion, especialidad, edad_paciente=None):
        """Función de fallback que usa Europe PMC cuando PubMed falla"""
        try:
            logger.info(f"🔄 Cambiando a Europe PMC para '{condicion}' en '{especialidad}'")
            
            # Usar la función existente de Europe PMC
            tratamientos = self.buscar_europepmc(condicion, especialidad, edad_paciente)
            
            if tratamientos:
                logger.info(f"✅ Europe PMC encontró {len(tratamientos)} tratamientos")
                return tratamientos
            else:
                logger.warning(f"⚠️ Europe PMC no encontró tratamientos para '{condicion}'")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error en fallback Europe PMC: {e}")
            return []

    def _generar_terminos_busqueda_simples(self, condicion, especialidad, edad_paciente=None):
        """Genera términos de búsqueda simples y efectivos, considerando la edad del paciente"""
        terminos = []
        
        # Extraer palabras clave básicas
        palabras_clave = self._extraer_palabras_clave_simples(condicion)
        terminos.extend(palabras_clave)
        
        # Agregar términos específicos de la especialidad
        terminos_especialidad = self._obtener_terminos_especialidad(especialidad)
        terminos.extend(terminos_especialidad)
        
        # Agregar términos específicos por edad si está disponible
        if edad_paciente is not None:
            terminos_edad = self._obtener_terminos_por_edad(edad_paciente, especialidad)
            terminos.extend(terminos_edad)
            
            # Combinar términos básicos con términos de edad
            for palabra in palabras_clave[:2]:  # Tomar solo las 2 primeras palabras clave
                for termino_edad in terminos_edad[:2]:  # Tomar solo los 2 primeros términos de edad
                    combinacion = f"{palabra} {termino_edad}"
                    terminos.append(combinacion)
        
        # Combinar términos básicos con especialidad
        for palabra in palabras_clave[:3]:  # Tomar solo las 3 primeras palabras clave
            for termino_esp in terminos_especialidad[:2]:  # Tomar solo los 2 primeros términos de especialidad
                combinacion = f"{palabra} {termino_esp}"
                terminos.append(combinacion)
        
        # Eliminar duplicados y limitar a 8 términos (aumentado para incluir edad)
        terminos_unicos = list(set(terminos))
        return terminos_unicos[:8]

    def _extraer_palabras_clave_simples(self, condicion):
        """Extrae palabras clave simples de la condición"""
        palabras_clave = []
        condicion_lower = condicion.lower()
        
        # Mapeo de términos médicos comunes
        mapeo_terminos = {
            'dolor': ['pain', 'ache'],
            'rodilla': ['knee'],
            'hombro': ['shoulder'],
            'cuello': ['neck'],
            'espalda': ['back', 'spine'],
            'brazo': ['arm'],
            'pierna': ['leg'],
            'lumbar': ['lumbar', 'low back'],
            'cervical': ['cervical', 'neck'],
            'dorsal': ['thoracic', 'back'],
            'fisioterapia': ['physical therapy'],
            'kinesiologia': ['physical therapy'],
            'rehabilitacion': ['rehabilitation'],
            'ejercicio': ['exercise'],
            'lesion': ['injury'],
            'tratamiento': ['treatment'],
            'terapia': ['therapy']
        }
        
        for termino_esp, terminos_en in mapeo_terminos.items():
            if termino_esp in condicion_lower:
                palabras_clave.extend(terminos_en)
        
        # Si no se encontraron palabras clave específicas, usar términos generales
        if not palabras_clave:
            palabras = condicion_lower.split()
            for palabra in palabras:
                if len(palabra) > 3:  # Palabras de más de 3 caracteres
                    palabras_clave.append(palabra)
        
        return palabras_clave

    def _obtener_terminos_especialidad(self, especialidad):
        """Obtiene términos específicos de la especialidad"""
        mapeo_especialidades = {
            'kinesiologia': ['physical therapy', 'rehabilitation', 'exercise'],
            'fisioterapia': ['physical therapy', 'rehabilitation', 'exercise'],
            'fonoaudiologia': ['speech therapy', 'communication', 'swallowing'],
            'nutricion': ['nutrition', 'diet', 'food'],
            'psicologia': ['psychology', 'mental health', 'therapy'],
            'enfermeria': ['nursing', 'care'],
            'medicina': ['medicine', 'treatment'],
            'urgencias': ['emergency', 'urgent care'],
            'terapia_ocupacional': ['occupational therapy', 'activities']
        }
        
        return mapeo_especialidades.get(especialidad.lower(), ['treatment', 'therapy'])

    def _obtener_terminos_por_edad(self, edad: int, especialidad: str) -> List[str]:
        """Obtiene términos específicos según la edad del paciente y especialidad"""
        terminos_edad = []
        
        # Categorías de edad
        if edad < 18:
            # Pediatría
            terminos_edad.extend(['pediatric', 'child', 'adolescent', 'young'])
            if edad < 5:
                terminos_edad.extend(['infant', 'toddler', 'preschool'])
            elif edad < 12:
                terminos_edad.extend(['school-age', 'child'])
            else:
                terminos_edad.extend(['adolescent', 'teenager'])
                
        elif edad < 65:
            # Adulto joven y adulto
            terminos_edad.extend(['adult', 'young adult'])
            if edad < 30:
                terminos_edad.extend(['young adult', 'early adult'])
            elif edad < 50:
                terminos_edad.extend(['middle-aged', 'adult'])
            else:
                terminos_edad.extend(['middle-aged', 'pre-elderly'])
                
        else:
            # Geriatría
            terminos_edad.extend(['elderly', 'geriatric', 'older adult', 'senior'])
            if edad < 75:
                terminos_edad.extend(['young elderly', 'early elderly'])
            else:
                terminos_edad.extend(['old elderly', 'frail elderly'])
        
        # Términos específicos por especialidad y edad
        if especialidad.lower() in ['kinesiologia', 'fisioterapia']:
            if edad < 18:
                terminos_edad.extend(['pediatric rehabilitation', 'child physical therapy'])
            elif edad >= 65:
                terminos_edad.extend(['geriatric rehabilitation', 'elderly physical therapy'])
            else:
                terminos_edad.extend(['adult rehabilitation', 'adult physical therapy'])
                
        elif especialidad.lower() == 'fonoaudiologia':
            if edad < 18:
                terminos_edad.extend(['pediatric speech therapy', 'child communication'])
            elif edad >= 65:
                terminos_edad.extend(['geriatric speech therapy', 'elderly swallowing'])
            else:
                terminos_edad.extend(['adult speech therapy', 'adult communication'])
                
        elif especialidad.lower() == 'psicologia':
            if edad < 18:
                terminos_edad.extend(['pediatric psychology', 'child mental health'])
            elif edad >= 65:
                terminos_edad.extend(['geriatric psychology', 'elderly mental health'])
            else:
                terminos_edad.extend(['adult psychology', 'adult mental health'])
                
        elif especialidad.lower() == 'nutricion':
            if edad < 18:
                terminos_edad.extend(['pediatric nutrition', 'child diet'])
            elif edad >= 65:
                terminos_edad.extend(['geriatric nutrition', 'elderly diet'])
            else:
                terminos_edad.extend(['adult nutrition', 'adult diet'])
        
        # Consideraciones específicas por edad
        if edad < 18:
            terminos_edad.extend(['developmental', 'growth', 'maturation'])
        elif edad >= 65:
            terminos_edad.extend(['aging', 'age-related', 'comorbidity'])
        else:
            terminos_edad.extend(['adult', 'working age'])
        
        return list(set(terminos_edad))  # Eliminar duplicados

    def generar_terminos_busqueda_disponibles(self, condicion: str, especialidad: str, edad_paciente: int = None) -> Dict:
        """
        Genera todos los términos de búsqueda disponibles para que el profesional seleccione
        """
        terminos_disponibles = {
            'terminos_basicos': [],
            'terminos_especialidad': [],
            'terminos_edad': [],
            'terminos_combinados': [],
            'terminos_recomendados': []
        }
        
        try:
            # Detectar condiciones específicas
            condiciones_detectadas = self._detectar_condiciones_especificas(condicion)
            
            # Términos básicos de la condición
            palabras_clave = self._extraer_palabras_clave_simples(condicion)
            terminos_disponibles['terminos_basicos'] = palabras_clave[:5]
            
            # Términos de especialidad
            terminos_especialidad = self._obtener_terminos_especialidad(especialidad)
            terminos_disponibles['terminos_especialidad'] = terminos_especialidad
            
            # Términos por edad
            if edad_paciente is not None:
                terminos_edad = self._obtener_terminos_por_edad(edad_paciente, especialidad)
                terminos_disponibles['terminos_edad'] = terminos_edad
            
            # Términos combinados (básicos + especialidad)
            for palabra in palabras_clave[:3]:
                for termino_esp in terminos_especialidad[:2]:
                    combinacion = f"{palabra} {termino_esp}"
                    terminos_disponibles['terminos_combinados'].append(combinacion)
            
            # Términos combinados con edad
            if edad_paciente is not None:
                for palabra in palabras_clave[:2]:
                    for termino_edad in terminos_edad[:2]:
                        combinacion = f"{palabra} {termino_edad}"
                        terminos_disponibles['terminos_combinados'].append(combinacion)
            
            # Términos recomendados (los más relevantes)
            terminos_recomendados = []
            terminos_recomendados.extend(palabras_clave[:2])  # 2 términos básicos
            terminos_recomendados.extend(terminos_especialidad[:2])  # 2 términos de especialidad
            if edad_paciente is not None:
                terminos_recomendados.extend(terminos_edad[:2])  # 2 términos de edad
            terminos_recomendados.extend(terminos_disponibles['terminos_combinados'][:3])  # 3 combinaciones
            
            terminos_disponibles['terminos_recomendados'] = list(set(terminos_recomendados))[:8]
            
            # Limpiar duplicados en todas las categorías
            for categoria in terminos_disponibles:
                terminos_disponibles[categoria] = list(set(terminos_disponibles[categoria]))
            
            logger.info(f"🔍 Términos disponibles generados: {len(terminos_disponibles['terminos_recomendados'])} recomendados")
            
        except Exception as e:
            logger.error(f"❌ Error generando términos disponibles: {e}")
        
        return terminos_disponibles

    def extraer_terminos_clave_analisis(self, analisis: Dict) -> List[str]:
        """
        Extrae términos clave del análisis completo del caso
        """
        terminos_clave = []
        
        try:
            # Extraer términos del motivo de consulta
            if 'motivo_consulta' in analisis:
                palabras_clave = self._extraer_palabras_clave_simples(analisis['motivo_consulta'])
                terminos_clave.extend(palabras_clave[:3])
            
            # Extraer términos de la especialidad
            if 'tipo_atencion' in analisis:
                terminos_especialidad = self._obtener_terminos_especialidad(analisis['tipo_atencion'])
                terminos_clave.extend(terminos_especialidad[:2])
            
            # Extraer términos de antecedentes
            if 'antecedentes' in analisis and analisis['antecedentes']:
                palabras_antecedentes = self._extraer_palabras_clave_simples(analisis['antecedentes'])
                terminos_clave.extend(palabras_antecedentes[:2])
            
            # Extraer términos de evaluación
            if 'evaluacion' in analisis and analisis['evaluacion']:
                palabras_evaluacion = self._extraer_palabras_clave_simples(analisis['evaluacion'])
                terminos_clave.extend(palabras_evaluacion[:2])
            
            # Términos específicos por edad
            if 'edad_paciente' in analisis and analisis['edad_paciente']:
                terminos_edad = self._obtener_terminos_por_edad(analisis['edad_paciente'], analisis.get('tipo_atencion', ''))
                terminos_clave.extend(terminos_edad[:2])
            
            # Eliminar duplicados y limitar a 10 términos
            terminos_clave = list(set(terminos_clave))[:10]
            
            logger.info(f"🔍 Términos clave extraídos: {terminos_clave}")
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo términos clave: {e}")
        
        return terminos_clave

    def generar_terminos_busqueda_expandidos(self, condicion: str, especialidad: str, edad_paciente: int = None, terminos_clave: List[str] = None) -> Dict:
        """
        Genera términos de búsqueda expandidos basados en términos clave
        """
        terminos_disponibles = {
            'terminos_basicos': [],
            'terminos_especialidad': [],
            'terminos_edad': [],
            'terminos_combinados': [],
            'terminos_recomendados': [],
            'terminos_clave_expandidos': []
        }
        
        try:
            # Usar términos clave si están disponibles
            if terminos_clave:
                terminos_disponibles['terminos_clave_expandidos'] = terminos_clave
            
            # Generar términos básicos
            palabras_clave = self._extraer_palabras_clave_simples(condicion)
            terminos_disponibles['terminos_basicos'] = palabras_clave[:5]
            
            # Términos de especialidad
            terminos_especialidad = self._obtener_terminos_especialidad(especialidad)
            terminos_disponibles['terminos_especialidad'] = terminos_especialidad
            
            # Términos por edad
            if edad_paciente is not None:
                terminos_edad = self._obtener_terminos_por_edad(edad_paciente, especialidad)
                terminos_disponibles['terminos_edad'] = terminos_edad
            
            # Combinar términos clave con términos básicos
            if terminos_clave:
                for termino_clave in terminos_clave[:3]:
                    for palabra in palabras_clave[:2]:
                        combinacion = f"{termino_clave} {palabra}"
                        terminos_disponibles['terminos_combinados'].append(combinacion)
            
            # Términos recomendados incluyendo términos clave
            terminos_recomendados = []
            if terminos_clave:
                terminos_recomendados.extend(terminos_clave[:3])  # 3 términos clave
            terminos_recomendados.extend(palabras_clave[:2])  # 2 términos básicos
            terminos_recomendados.extend(terminos_especialidad[:2])  # 2 términos de especialidad
            if edad_paciente is not None:
                terminos_recomendados.extend(terminos_edad[:2])  # 2 términos de edad
            terminos_recomendados.extend(terminos_disponibles['terminos_combinados'][:3])  # 3 combinaciones
            
            terminos_disponibles['terminos_recomendados'] = list(set(terminos_recomendados))[:10]
            
            # Limpiar duplicados
            for categoria in terminos_disponibles:
                terminos_disponibles[categoria] = list(set(terminos_disponibles[categoria]))
            
            logger.info(f"🔍 Términos expandidos generados: {len(terminos_disponibles['terminos_recomendados'])} recomendados")
            
        except Exception as e:
            logger.error(f"❌ Error generando términos expandidos: {e}")
        
        return terminos_disponibles

    def buscar_con_terminos_clave(self, condicion: str, especialidad: str, terminos_clave: List[str], edad_paciente: int = None) -> Dict:
        """
        Realiza búsqueda usando términos clave específicos
        """
        resultados = {
            'tratamientos_pubmed': [],
            'tratamientos_europepmc': [],
            'preguntas_cientificas': [],
            'medicamentos_fda': {},
            'plan_intervencion': None
        }
        
        try:
            logger.info(f"🔍 Búsqueda con términos clave: {terminos_clave}")
            
            # Construir consulta con términos clave
            consulta_clave = condicion
            if terminos_clave:
                consulta_clave += " " + " ".join(terminos_clave[:5])  # Máximo 5 términos clave
            
            # Búsqueda en PubMed con términos clave
            try:
                resultados['tratamientos_pubmed'] = self.buscar_tratamiento_pubmed(consulta_clave, especialidad, edad_paciente)
                if resultados['tratamientos_pubmed']:
                    logger.info(f"✅ PubMed con términos clave: {len(resultados['tratamientos_pubmed'])} resultados")
                else:
                    logger.warning("⚠️ PubMed no devolvió resultados con términos clave")
            except Exception as e:
                logger.error(f"❌ Error en PubMed con términos clave: {e}")
                resultados['tratamientos_pubmed'] = []
            
            # Búsqueda en Europe PMC con términos clave
            try:
                resultados['tratamientos_europepmc'] = self.buscar_europepmc(consulta_clave, especialidad, edad_paciente)
                if resultados['tratamientos_europepmc']:
                    logger.info(f"✅ Europe PMC con términos clave: {len(resultados['tratamientos_europepmc'])} resultados")
                else:
                    logger.warning("⚠️ Europe PMC no devolvió resultados con términos clave")
            except Exception as e:
                logger.error(f"❌ Error en Europe PMC con términos clave: {e}")
                resultados['tratamientos_europepmc'] = []
            
            # Generar preguntas científicas basadas en términos clave
            try:
                resultados['preguntas_cientificas'] = self.generar_preguntas_cientificas(consulta_clave, especialidad)
                if resultados['preguntas_cientificas']:
                    logger.info(f"✅ Preguntas científicas generadas: {len(resultados['preguntas_cientificas'])}")
            except Exception as e:
                logger.error(f"❌ Error generando preguntas científicas: {e}")
                resultados['preguntas_cientificas'] = []
            
            # Generar plan de intervención si hay resultados
            tratamientos_totales = len(resultados['tratamientos_pubmed']) + len(resultados['tratamientos_europepmc'])
            if tratamientos_totales > 0:
                try:
                    resultados['plan_intervencion'] = self._generar_plan_intervencion_especifico(
                        condicion, especialidad, resultados['tratamientos_pubmed'] + resultados['tratamientos_europepmc']
                    )
                    logger.info("✅ Plan de intervención generado")
                except Exception as e:
                    logger.error(f"❌ Error generando plan de intervención: {e}")
            
            logger.info(f"✅ Búsqueda con términos clave completada: {tratamientos_totales} tratamientos encontrados")
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda con términos clave: {e}")
        
        return resultados

    def buscar_con_terminos_personalizados(self, condicion: str, especialidad: str, terminos_seleccionados: List[str], edad_paciente: int = None) -> Dict:
        """
        Realiza búsqueda usando términos específicos seleccionados por el profesional
        """
        resultados = {
            'tratamientos_pubmed': [],
            'tratamientos_europepmc': [],
            'preguntas_cientificas': [],
            'medicamentos_fda': {},
            'plan_intervencion': None
        }
        
        try:
            logger.info(f"🔍 Búsqueda personalizada con términos: {terminos_seleccionados}")
            
            # Construir consulta con términos seleccionados
            consulta_personalizada = condicion
            if terminos_seleccionados:
                consulta_personalizada += " " + " ".join(terminos_seleccionados)
            
            # Búsqueda en PubMed con términos personalizados
            try:
                resultados['tratamientos_pubmed'] = self.buscar_tratamiento_pubmed(consulta_personalizada, especialidad, edad_paciente)
                if resultados['tratamientos_pubmed']:
                    logger.info(f"✅ PubMed con términos personalizados: {len(resultados['tratamientos_pubmed'])} resultados")
                else:
                    logger.warning("⚠️ PubMed no devolvió resultados con términos personalizados")
            except Exception as e:
                logger.error(f"❌ Error en PubMed con términos personalizados: {e}")
                resultados['tratamientos_pubmed'] = []
            
            # Búsqueda en Europe PMC con términos personalizados
            try:
                resultados['tratamientos_europepmc'] = self.buscar_europepmc(consulta_personalizada, especialidad, edad_paciente)
                if resultados['tratamientos_europepmc']:
                    logger.info(f"✅ Europe PMC con términos personalizados: {len(resultados['tratamientos_europepmc'])} resultados")
                else:
                    logger.warning("⚠️ Europe PMC no devolvió resultados con términos personalizados")
            except Exception as e:
                logger.error(f"❌ Error en Europe PMC con términos personalizados: {e}")
                resultados['tratamientos_europepmc'] = []
            
            # Generar preguntas científicas
            try:
                resultados['preguntas_cientificas'] = self.generar_preguntas_cientificas(condicion, especialidad)
            except Exception as e:
                logger.error(f"❌ Error generando preguntas: {e}")
                resultados['preguntas_cientificas'] = []
            
            # Generar plan de intervención
            todos_tratamientos = resultados['tratamientos_pubmed'] + resultados['tratamientos_europepmc']
            if todos_tratamientos:
                try:
                    resultados['plan_intervencion'] = self._generar_plan_intervencion_especifico(condicion, especialidad, todos_tratamientos)
                    logger.info(f"✅ Plan de intervención generado con {len(resultados['plan_intervencion'].tecnicas_especificas)} técnicas específicas")
                except Exception as e:
                    logger.error(f"❌ Error generando plan de intervención: {e}")
            
            logger.info(f"✅ Búsqueda personalizada completada para {condicion} en {especialidad}")
            logger.info(f"✅ Total resultados: {len(todos_tratamientos)}")
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda personalizada: {e}")
        
        return resultados

    def _busqueda_simple_pubmed(self, condicion, especialidad):
        """Búsqueda simple en PubMed sin términos MeSH complejos"""
        try:
            # Crear términos de búsqueda simples
            terminos_simples = []
            
            # Extraer palabras clave básicas
            palabras_clave = self._extraer_palabras_clave_mesh(condicion)
            for palabra in palabras_clave:
                terminos_simples.append(palabra)
            
            # Agregar términos específicos de la especialidad
            if especialidad.lower() in ['kinesiologia', 'fisioterapia']:
                terminos_simples.extend(['physical therapy', 'rehabilitation', 'exercise'])
            elif especialidad.lower() == 'fonoaudiologia':
                terminos_simples.extend(['speech therapy', 'communication', 'swallowing'])
            elif especialidad.lower() == 'nutricion':
                terminos_simples.extend(['nutrition', 'diet', 'food'])
            elif especialidad.lower() == 'psicologia':
                terminos_simples.extend(['psychology', 'mental health', 'therapy'])
            
            tratamientos_encontrados = []
            
            for termino in terminos_simples[:3]:  # Limitar a 3 términos
                try:
                    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                    params = {
                        'db': 'pubmed',
                        'term': termino,
                        'retmode': 'json',
                        'retmax': 5,
                        'sort': 'relevance',
                        'api_key': self.ncbi_api_key,
                        'tool': 'MedConnect-IA',
                        'email': 'support@medconnect.cl'
                    }
                    
                    logger.info(f"🔍 Búsqueda simple PubMed: {termino}")
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                                ids = data['esearchresult']['idlist']
                                
                                if ids:
                                    logger.info(f"✅ Encontrados {len(ids)} artículos para '{termino}'")
                                    detalles = self._obtener_detalles_pubmed(ids)
                                    
                                    for detalle in detalles:
                                        if detalle and self._es_articulo_relevante(detalle, condicion):
                                            tratamientos_encontrados.append(detalle)
                                            
                        except json.JSONDecodeError:
                            logger.warning(f"⚠️ Error decodificando JSON para '{termino}'")
                            continue
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error en búsqueda simple '{termino}': {e}")
                    continue
            
            return tratamientos_encontrados
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda simple PubMed: {e}")
            return []

    def _generar_terminos_mesh_especificos(self, condicion, especialidad):
        """Genera términos MeSH específicos analizando toda la información clínica"""
        terminos_mesh = []
        condicion_lower = condicion.lower()
        
        # Detectar condiciones específicas para mejorar la búsqueda
        condiciones_detectadas = self._detectar_condiciones_especificas(condicion)
        
        # Agregar términos MeSH específicos de condiciones detectadas
        for condicion_esp in condiciones_detectadas:
            if condicion_esp in self.condiciones_especificas:
                terminos_mesh.extend(self.condiciones_especificas[condicion_esp]['mesh_terms'])
        
        # Mapeo de especialidades a términos MeSH específicos
        mapeo_especialidades = {
            'kinesiologia': self._terminos_mesh_kinesiologia,
            'fisioterapia': self._terminos_mesh_kinesiologia,
            'fonoaudiologia': self._terminos_mesh_fonoaudiologia,
            'nutricion': self._terminos_mesh_nutricion,
            'psicologia': self._terminos_mesh_psicologia,
            'enfermeria': self._terminos_mesh_enfermeria,
            'medicina': self._terminos_mesh_medicina_general,
            'urgencias': self._terminos_mesh_urgencias,
            'terapia_ocupacional': self._terminos_mesh_terapia_ocupacional
        }
        
        # Obtener función específica para la especialidad
        funcion_especialidad = mapeo_especialidades.get(especialidad.lower(), self._terminos_mesh_general)
        
        # Generar términos MeSH específicos para la especialidad
        terminos_especialidad = funcion_especialidad(condicion_lower)
        terminos_mesh.extend(terminos_especialidad)
        
        # Si no hay términos específicos, usar términos generales
        if not terminos_mesh:
            terminos_mesh = self._terminos_mesh_general(condicion_lower)
        
        # Eliminar duplicados y limitar a 5 términos más relevantes
        terminos_mesh = list(set(terminos_mesh))[:5]
        
        logger.info(f"🔍 Términos MeSH generados: {terminos_mesh}")
        return terminos_mesh

    def _terminos_mesh_fonoaudiologia(self, condicion):
        """Términos MeSH específicos para Fonoaudiología con análisis completo"""
        terminos = []
        
        # Análisis específico para lactancia y frenillo lingual
        if any(palabra in condicion for palabra in ['lactancia', 'lactation', 'succion', 'suction', 'pecho', 'breast']):
            terminos.append('("Breast Feeding"[MeSH Terms] OR "Lactation Disorders"[MeSH Terms])')
        
        if any(palabra in condicion for palabra in ['frenillo', 'frenulum', 'lingual', 'tongue']):
            terminos.append('("Tongue"[MeSH Terms] OR "Ankyloglossia"[MeSH Terms])')
        
        if any(palabra in condicion for palabra in ['deglucion', 'swallowing', 'tragar', 'dificultad']):
            terminos.append('("Deglutition Disorders"[MeSH Terms] OR "Dysphagia"[MeSH Terms])')
        
        # Análisis para hiperbilirrubinemia
        if any(palabra in condicion for palabra in ['hiperbilirrubina', 'hyperbilirubinemia', 'bilirrubina', 'bilirubin']):
            terminos.append('("Hyperbilirubinemia"[MeSH Terms] OR "Jaundice"[MeSH Terms])')
        
        # Análisis para hipoalimentación
        if any(palabra in condicion for palabra in ['hipoalimentacion', 'underfeeding', 'desnutricion', 'malnutrition']):
            terminos.append('("Malnutrition"[MeSH Terms] OR "Infant Nutrition Disorders"[MeSH Terms])')
        
        # Análisis para fatiga y desacoplamiento
        if any(palabra in condicion for palabra in ['fatiga', 'fatigue', 'desacopla', 'desacoplamiento']):
            terminos.append('("Fatigue"[MeSH Terms] OR "Feeding and Eating Disorders"[MeSH Terms])')
        
        # Análisis para chasquido lingual
        if any(palabra in condicion for palabra in ['chasquido', 'clicking', 'lingual']):
            terminos.append('("Tongue"[MeSH Terms] OR "Oral Manifestations"[MeSH Terms])')
        
        # Análisis para edad específica (1 año)
        if any(palabra in condicion for palabra in ['1 año', '1 year', 'infant', 'bebe', 'baby']):
            terminos.append('("Infant"[MeSH Terms] OR "Child Development"[MeSH Terms])')
        
        # Problemas de habla (más específicos)
        if any(palabra in condicion for palabra in ['habla', 'speech', 'lenguaje', 'language']):
            terminos.append('("Speech Disorders"[MeSH Terms] OR "Language Development Disorders"[MeSH Terms])')
        
        # Problemas de voz
        if any(palabra in condicion for palabra in ['voz', 'voice']):
            terminos.append('("Voice Disorders"[MeSH Terms] OR "Dysphonia"[MeSH Terms])')
        
        # Problemas de audición
        if any(palabra in condicion for palabra in ['audicion', 'hearing', 'sordera']):
            terminos.append('("Hearing Disorders"[MeSH Terms] OR "Deafness"[MeSH Terms])')
        
        # Términos combinados más específicos para casos complejos
        if len(terminos) >= 2:
            # Combinar lactancia con frenillo
            if any('Breast Feeding' in t for t in terminos) and any('Ankyloglossia' in t for t in terminos):
                terminos.append('("Breast Feeding"[MeSH Terms] AND "Ankyloglossia"[MeSH Terms])')
            
            # Combinar lactancia con problemas de deglución
            if any('Breast Feeding' in t for t in terminos) and any('Deglutition Disorders' in t for t in terminos):
                terminos.append('("Breast Feeding"[MeSH Terms] AND "Deglutition Disorders"[MeSH Terms])')
            
            # Combinar frenillo con problemas de alimentación
            if any('Ankyloglossia' in t for t in terminos) and any('Feeding and Eating Disorders' in t for t in terminos):
                terminos.append('("Ankyloglossia"[MeSH Terms] AND "Feeding and Eating Disorders"[MeSH Terms])')
        
        # Términos generales de fonoaudiología pediátrica
        if not terminos:
            terminos.append('("Speech Therapy"[MeSH Terms] OR "Communication Disorders"[MeSH Terms])')
        
        return terminos

    def _terminos_mesh_kinesiologia(self, condicion):
        """Términos MeSH específicos para Kinesiología/Fisioterapia con análisis completo"""
        terminos = []
        
        # Análisis específico para dolor de rodilla
        if any(palabra in condicion for palabra in ['rodilla', 'knee']):
            if any(palabra in condicion for palabra in ['correr', 'running', 'deporte', 'sport']):
                terminos.append('("Knee Injuries"[MeSH Terms] OR "Athletic Injuries"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['dolor', 'pain']):
                terminos.append('("Knee Pain"[MeSH Terms] OR "Patellofemoral Pain Syndrome"[MeSH Terms])')
            else:
                terminos.append('("Knee"[MeSH Terms] OR "Knee Joint"[MeSH Terms])')
        
        # Análisis específico para dolor de hombro
        elif any(palabra in condicion for palabra in ['hombro', 'shoulder']):
            if any(palabra in condicion for palabra in ['levantar', 'lifting', 'peso', 'weight']):
                terminos.append('("Rotator Cuff Injuries"[MeSH Terms] OR "Shoulder Injuries"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['dolor', 'pain']):
                terminos.append('("Shoulder Pain"[MeSH Terms] OR "Shoulder Joint"[MeSH Terms])')
            else:
                terminos.append('("Shoulder"[MeSH Terms] OR "Shoulder Joint"[MeSH Terms])')
        
        # Análisis específico para dolor de cuello
        elif any(palabra in condicion for palabra in ['cuello', 'neck']):
            if any(palabra in condicion for palabra in ['trabajar', 'work', 'computadora', 'computer']):
                terminos.append('("Neck Pain"[MeSH Terms] OR "Cervical Pain"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['dolor', 'pain']):
                terminos.append('("Neck Pain"[MeSH Terms] OR "Cervical Vertebrae"[MeSH Terms])')
            else:
                terminos.append('("Neck"[MeSH Terms] OR "Cervical Vertebrae"[MeSH Terms])')
        
        # Análisis específico para dolor de espalda
        elif any(palabra in condicion for palabra in ['espalda', 'back', 'lumbar']):
            if any(palabra in condicion for palabra in ['baja', 'low']):
                terminos.append('("Low Back Pain"[MeSH Terms] OR "Lumbar Vertebrae"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['dolor', 'pain']):
                terminos.append('("Back Pain"[MeSH Terms] OR "Spine"[MeSH Terms])')
            else:
                terminos.append('("Back"[MeSH Terms] OR "Spine"[MeSH Terms])')
        
        # Análisis para lesiones deportivas específicas
        elif any(palabra in condicion for palabra in ['deporte', 'sport', 'correr', 'running']):
            if any(palabra in condicion for palabra in ['lesion', 'injury', 'accidente']):
                terminos.append('("Athletic Injuries"[MeSH Terms] OR "Sports Medicine"[MeSH Terms])')
            else:
                terminos.append('("Exercise"[MeSH Terms] OR "Physical Activity"[MeSH Terms])')
        
        # Análisis para rehabilitación específica
        elif any(palabra in condicion for palabra in ['rehabilitacion', 'rehabilitation']):
            if any(palabra in condicion for palabra in ['post', 'despues', 'after']):
                terminos.append('("Rehabilitation"[MeSH Terms] OR "Recovery of Function"[MeSH Terms])')
            else:
                terminos.append('("Physical Therapy Modalities"[MeSH Terms] OR "Exercise Therapy"[MeSH Terms])')
        
        # Términos generales de fisioterapia
        if not terminos:
            terminos.append('("Physical Therapy Modalities"[MeSH Terms] OR "Exercise Therapy"[MeSH Terms])')
        
        return terminos

    def _terminos_mesh_nutricion(self, condicion):
        """Términos MeSH específicos para Nutrición con análisis completo"""
        terminos = []
        
        # Análisis específico para diabetes
        if any(palabra in condicion for palabra in ['diabetes', 'glucosa', 'glucose']):
            if any(palabra in condicion for palabra in ['tipo 2', 'type 2']):
                terminos.append('("Diabetes Mellitus, Type 2"[MeSH Terms] OR "Blood Glucose"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['control', 'management']):
                terminos.append('("Diabetes Mellitus"[MeSH Terms] OR "Blood Glucose"[MeSH Terms])')
            else:
                terminos.append('("Diabetes Mellitus"[MeSH Terms] OR "Blood Glucose"[MeSH Terms])')
        
        # Análisis específico para obesidad
        elif any(palabra in condicion for palabra in ['obesidad', 'obesity', 'peso', 'weight']):
            if any(palabra in condicion for palabra in ['perder', 'loss', 'bajar']):
                terminos.append('("Weight Loss"[MeSH Terms] OR "Obesity"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['control', 'management']):
                terminos.append('("Obesity"[MeSH Terms] OR "Weight Management"[MeSH Terms])')
            else:
                terminos.append('("Obesity"[MeSH Terms] OR "Body Weight"[MeSH Terms])')
        
        # Análisis específico para hipertensión
        elif any(palabra in condicion for palabra in ['hipertension', 'hypertension', 'presion']):
            if any(palabra in condicion for palabra in ['control', 'management']):
                terminos.append('("Hypertension"[MeSH Terms] OR "Blood Pressure"[MeSH Terms])')
            else:
                terminos.append('("Hypertension"[MeSH Terms] OR "Blood Pressure"[MeSH Terms])')
        
        # Análisis específico para desnutrición
        elif any(palabra in condicion for palabra in ['desnutricion', 'malnutrition']):
            if any(palabra in condicion for palabra in ['infantil', 'pediatric', 'nino', 'child']):
                terminos.append('("Child Nutrition Disorders"[MeSH Terms] OR "Malnutrition"[MeSH Terms])')
            else:
                terminos.append('("Malnutrition"[MeSH Terms] OR "Nutrition Disorders"[MeSH Terms])')
        
        # Análisis para problemas de alimentación
        elif any(palabra in condicion for palabra in ['alimentacion', 'feeding', 'comida', 'food']):
            if any(palabra in condicion for palabra in ['dificultad', 'difficulty', 'problema']):
                terminos.append('("Feeding and Eating Disorders"[MeSH Terms] OR "Nutrition Disorders"[MeSH Terms])')
            else:
                terminos.append('("Nutrition Therapy"[MeSH Terms] OR "Diet Therapy"[MeSH Terms])')
        
        # Términos generales de nutrición
        if not terminos:
            terminos.append('("Nutrition Therapy"[MeSH Terms] OR "Diet Therapy"[MeSH Terms])')
        
        return terminos

    def _terminos_mesh_psicologia(self, condicion):
        """Términos MeSH específicos para Psicología con análisis completo"""
        terminos = []
        
        # Análisis específico para ansiedad
        if any(palabra in condicion for palabra in ['ansiedad', 'anxiety', 'estres', 'stress']):
            if any(palabra in condicion for palabra in ['sueño', 'sleep', 'insomnio']):
                terminos.append('("Anxiety Disorders"[MeSH Terms] OR "Sleep Disorders"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['trabajo', 'work', 'laboral']):
                terminos.append('("Stress Disorders"[MeSH Terms] OR "Occupational Stress"[MeSH Terms])')
            else:
                terminos.append('("Anxiety Disorders"[MeSH Terms] OR "Stress Disorders"[MeSH Terms])')
        
        # Análisis específico para depresión
        elif any(palabra in condicion for palabra in ['depresion', 'depression', 'tristeza']):
            if any(palabra in condicion for palabra in ['mayor', 'major', 'severa']):
                terminos.append('("Depressive Disorder, Major"[MeSH Terms] OR "Depression"[MeSH Terms])')
            else:
                terminos.append('("Depression"[MeSH Terms] OR "Depressive Disorder"[MeSH Terms])')
        
        # Análisis específico para trastornos del sueño
        elif any(palabra in condicion for palabra in ['sueño', 'sleep', 'insomnio']):
            if any(palabra in condicion for palabra in ['problema', 'disorder', 'dificultad']):
                terminos.append('("Sleep Disorders"[MeSH Terms] OR "Insomnia"[MeSH Terms])')
            else:
                terminos.append('("Sleep"[MeSH Terms] OR "Sleep Wake Disorders"[MeSH Terms])')
        
        # Análisis específico para trastornos de conducta
        elif any(palabra in condicion for palabra in ['conducta', 'behavior', 'comportamiento']):
            if any(palabra in condicion for palabra in ['nino', 'child', 'infantil']):
                terminos.append('("Child Behavior Disorders"[MeSH Terms] OR "Behavioral Symptoms"[MeSH Terms])')
            else:
                terminos.append('("Behavioral Symptoms"[MeSH Terms] OR "Mental Disorders"[MeSH Terms])')
        
        # Análisis para problemas de adaptación
        elif any(palabra in condicion for palabra in ['adaptacion', 'adaptation', 'ajuste']):
            terminos.append('("Adaptation, Psychological"[MeSH Terms] OR "Adjustment Disorders"[MeSH Terms])')
        
        # Términos generales de psicología
        if not terminos:
            terminos.append('("Psychotherapy"[MeSH Terms] OR "Mental Health"[MeSH Terms])')
        
        return terminos

    def _terminos_mesh_enfermeria(self, condicion):
        """Términos MeSH específicos para Enfermería con análisis completo"""
        terminos = []
        
        # Análisis específico para cuidados de heridas
        if any(palabra in condicion for palabra in ['herida', 'wound', 'curación']):
            if any(palabra in condicion for palabra in ['postoperatoria', 'postoperative', 'quirurgica']):
                terminos.append('("Postoperative Care"[MeSH Terms] OR "Wound Healing"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['cronica', 'chronic', 'ulcera']):
                terminos.append('("Wounds and Injuries"[MeSH Terms] OR "Wound Healing"[MeSH Terms])')
            else:
                terminos.append('("Wounds and Injuries"[MeSH Terms] OR "Wound Healing"[MeSH Terms])')
        
        # Análisis específico para cuidados paliativos
        elif any(palabra in condicion for palabra in ['paliativo', 'palliative', 'terminal']):
            if any(palabra in condicion for palabra in ['dolor', 'pain']):
                terminos.append('("Palliative Care"[MeSH Terms] OR "Pain Management"[MeSH Terms])')
            else:
                terminos.append('("Palliative Care"[MeSH Terms] OR "Terminal Care"[MeSH Terms])')
        
        # Análisis específico para cuidados críticos
        elif any(palabra in condicion for palabra in ['critico', 'critical', 'intensivo']):
            if any(palabra in condicion for palabra in ['respiratorio', 'respiratory']):
                terminos.append('("Critical Care"[MeSH Terms] OR "Respiratory Care"[MeSH Terms])')
            else:
                terminos.append('("Critical Care"[MeSH Terms] OR "Intensive Care"[MeSH Terms])')
        
        # Análisis específico para educación del paciente
        elif any(palabra in condicion for palabra in ['educacion', 'education', 'paciente']):
            if any(palabra in condicion for palabra in ['diabetes', 'diabetic']):
                terminos.append('("Patient Education"[MeSH Terms] OR "Diabetes Mellitus"[MeSH Terms])')
            else:
                terminos.append('("Patient Education"[MeSH Terms] OR "Health Education"[MeSH Terms])')
        
        # Análisis para cuidados pediátricos
        elif any(palabra in condicion for palabra in ['pediatrico', 'pediatric', 'nino', 'child']):
            terminos.append('("Pediatric Nursing"[MeSH Terms] OR "Child Care"[MeSH Terms])')
        
        # Términos generales de enfermería
        if not terminos:
            terminos.append('("Nursing Care"[MeSH Terms] OR "Nursing"[MeSH Terms])')
        
        return terminos

    def _terminos_mesh_medicina_general(self, condicion):
        """Términos MeSH específicos para Medicina General con análisis completo"""
        terminos = []
        
        # Análisis específico para hipertensión
        if any(palabra in condicion for palabra in ['hipertension', 'hypertension', 'presion']):
            if any(palabra in condicion for palabra in ['control', 'management']):
                terminos.append('("Hypertension"[MeSH Terms] OR "Blood Pressure"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['arterial', 'arterial']):
                terminos.append('("Hypertension"[MeSH Terms] OR "Blood Pressure"[MeSH Terms])')
            else:
                terminos.append('("Hypertension"[MeSH Terms] OR "Blood Pressure"[MeSH Terms])')
        
        # Análisis específico para diabetes
        elif any(palabra in condicion for palabra in ['diabetes', 'glucosa', 'glucose']):
            if any(palabra in condicion for palabra in ['control', 'management']):
                terminos.append('("Diabetes Mellitus"[MeSH Terms] OR "Blood Glucose"[MeSH Terms])')
            else:
                terminos.append('("Diabetes Mellitus"[MeSH Terms] OR "Blood Glucose"[MeSH Terms])')
        
        # Análisis específico para infecciones respiratorias
        elif any(palabra in condicion for palabra in ['respiratorio', 'respiratory', 'tos', 'cough']):
            if any(palabra in condicion for palabra in ['infeccion', 'infection']):
                terminos.append('("Respiratory Tract Infections"[MeSH Terms] OR "Cough"[MeSH Terms])')
            else:
                terminos.append('("Respiratory System"[MeSH Terms] OR "Respiratory Tract Diseases"[MeSH Terms])')
        
        # Análisis específico para dolor general
        elif any(palabra in condicion for palabra in ['dolor', 'pain']):
            if any(palabra in condicion for palabra in ['agudo', 'acute']):
                terminos.append('("Acute Pain"[MeSH Terms] OR "Pain Management"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['cronico', 'chronic']):
                terminos.append('("Chronic Pain"[MeSH Terms] OR "Pain Management"[MeSH Terms])')
            else:
                terminos.append('("Pain"[MeSH Terms] OR "Pain Management"[MeSH Terms])')
        
        # Análisis para problemas digestivos
        elif any(palabra in condicion for palabra in ['digestivo', 'digestive', 'estomago', 'stomach']):
            terminos.append('("Digestive System Diseases"[MeSH Terms] OR "Gastrointestinal Diseases"[MeSH Terms])')
        
        # Términos generales de medicina
        if not terminos:
            terminos.append('("Primary Health Care"[MeSH Terms] OR "General Practice"[MeSH Terms])')
        
        return terminos

    def _terminos_mesh_urgencias(self, condicion):
        """Términos MeSH específicos para Urgencias con análisis completo"""
        terminos = []
        
        # Análisis específico para trauma
        if any(palabra in condicion for palabra in ['trauma', 'accidente', 'accident']):
            if any(palabra in condicion for palabra in ['craneal', 'head', 'cabeza']):
                terminos.append('("Head Injuries"[MeSH Terms] OR "Trauma"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['toracico', 'chest', 'pecho']):
                terminos.append('("Thoracic Injuries"[MeSH Terms] OR "Chest Pain"[MeSH Terms])')
            else:
                terminos.append('("Wounds and Injuries"[MeSH Terms] OR "Trauma"[MeSH Terms])')
        
        # Análisis específico para dolor agudo
        elif any(palabra in condicion for palabra in ['dolor agudo', 'acute pain']):
            if any(palabra in condicion for palabra in ['pecho', 'chest', 'toracico']):
                terminos.append('("Chest Pain"[MeSH Terms] OR "Acute Pain"[MeSH Terms])')
            elif any(palabra in condicion for palabra in ['abdominal', 'abdomen']):
                terminos.append('("Abdominal Pain"[MeSH Terms] OR "Acute Pain"[MeSH Terms])')
            else:
                terminos.append('("Acute Pain"[MeSH Terms] OR "Pain Management"[MeSH Terms])')
        
        # Análisis específico para problemas cardíacos
        elif any(palabra in condicion for palabra in ['cardiaco', 'cardiac', 'corazon', 'heart']):
            if any(palabra in condicion for palabra in ['ataque', 'attack', 'infarto']):
                terminos.append('("Heart Attack"[MeSH Terms] OR "Myocardial Infarction"[MeSH Terms])')
            else:
                terminos.append('("Heart Diseases"[MeSH Terms] OR "Cardiac Emergencies"[MeSH Terms])')
        
        # Análisis específico para problemas respiratorios
        elif any(palabra in condicion for palabra in ['respiratorio', 'respiratory', 'dificultad']):
            if any(palabra in condicion for palabra in ['respirar', 'breathing', 'disnea']):
                terminos.append('("Respiratory Distress"[MeSH Terms] OR "Dyspnea"[MeSH Terms])')
            else:
                terminos.append('("Respiratory System"[MeSH Terms] OR "Respiratory Tract Diseases"[MeSH Terms])')
        
        # Análisis para convulsiones
        elif any(palabra in condicion for palabra in ['convulsion', 'seizure', 'epilepsia']):
            terminos.append('("Seizures"[MeSH Terms] OR "Epilepsy"[MeSH Terms])')
        
        # Términos generales de urgencias
        if not terminos:
            terminos.append('("Emergency Medicine"[MeSH Terms] OR "Emergency Treatment"[MeSH Terms])')
        
        return terminos

    def _terminos_mesh_terapia_ocupacional(self, condicion):
        """Términos MeSH específicos para Terapia Ocupacional con análisis completo"""
        terminos = []
        
        # Análisis específico para actividades de la vida diaria
        if any(palabra in condicion for palabra in ['actividades', 'activities', 'vida diaria']):
            if any(palabra in condicion for palabra in ['bano', 'bath', 'vestirse', 'dressing']):
                terminos.append('("Activities of Daily Living"[MeSH Terms] OR "Self Care"[MeSH Terms])')
            else:
                terminos.append('("Activities of Daily Living"[MeSH Terms] OR "Occupational Therapy"[MeSH Terms])')
        
        # Análisis específico para rehabilitación funcional
        elif any(palabra in condicion for palabra in ['funcional', 'functional', 'rehabilitacion']):
            if any(palabra in condicion for palabra in ['post', 'despues', 'after']):
                terminos.append('("Rehabilitation"[MeSH Terms] OR "Recovery of Function"[MeSH Terms])')
            else:
                terminos.append('("Rehabilitation"[MeSH Terms] OR "Functional Status"[MeSH Terms])')
        
        # Análisis específico para problemas de movilidad
        elif any(palabra in condicion for palabra in ['movilidad', 'mobility', 'movimiento']):
            if any(palabra in condicion for palabra in ['limitacion', 'limitation']):
                terminos.append('("Mobility Limitation"[MeSH Terms] OR "Movement Disorders"[MeSH Terms])')
            else:
                terminos.append('("Movement"[MeSH Terms] OR "Motor Skills"[MeSH Terms])')
        
        # Análisis específico para adaptaciones
        elif any(palabra in condicion for palabra in ['adaptacion', 'adaptation', 'equipamiento']):
            if any(palabra in condicion for palabra in ['dispositivo', 'device', 'ayuda']):
                terminos.append('("Self-Help Devices"[MeSH Terms] OR "Assistive Technology"[MeSH Terms])')
            else:
                terminos.append('("Adaptation, Psychological"[MeSH Terms] OR "Occupational Therapy"[MeSH Terms])')
        
        # Análisis para accidentes cerebrovasculares
        elif any(palabra in condicion for palabra in ['acv', 'stroke', 'cerebrovascular']):
            terminos.append('("Stroke"[MeSH Terms] OR "Cerebrovascular Disorders"[MeSH Terms])')
        
        # Términos generales de terapia ocupacional
        if not terminos:
            terminos.append('("Occupational Therapy"[MeSH Terms] OR "Occupational Therapists"[MeSH Terms])')
        
        return terminos

    def _terminos_mesh_general(self, condicion):
        """Términos MeSH generales cuando no hay especialidad específica"""
        terminos = []
        
        # Dolor general
        if any(palabra in condicion for palabra in ['dolor', 'pain']):
            terminos.append('("Pain"[MeSH Terms] OR "Pain Management"[MeSH Terms])')
        
        # Tratamiento general
        elif any(palabra in condicion for palabra in ['tratamiento', 'treatment', 'terapia']):
            terminos.append('("Therapeutics"[MeSH Terms] OR "Treatment Outcome"[MeSH Terms])')
        
        # Diagnóstico
        elif any(palabra in condicion for palabra in ['diagnostico', 'diagnosis']):
            terminos.append('("Diagnosis"[MeSH Terms] OR "Diagnostic Techniques"[MeSH Terms])')
        
        # Términos generales
        terminos.append('("Medicine"[MeSH Terms] OR "Patient Care"[MeSH Terms])')
        
        return terminos

    def _extraer_palabras_clave_mesh(self, condicion):
        """Extrae palabras clave para búsqueda MeSH"""
        palabras_clave = []
        
        # Palabras clave para dolor
        if any(palabra in condicion for palabra in ['dolor', 'pain', 'ache']):
            palabras_clave.append('pain')
        
        # Palabras clave para localizaciones
        if any(palabra in condicion for palabra in ['rodilla', 'knee']):
            palabras_clave.append('knee pain')
        elif any(palabra in condicion for palabra in ['hombro', 'shoulder']):
            palabras_clave.append('shoulder pain')
        elif any(palabra in condicion for palabra in ['cuello', 'neck']):
            palabras_clave.append('neck pain')
        elif any(palabra in condicion for palabra in ['espalda', 'back']):
            palabras_clave.append('back pain')
        
        # Palabras clave para actividades
        if any(palabra in condicion for palabra in ['correr', 'running']):
            palabras_clave.append('running injury')
        elif any(palabra in condicion for palabra in ['deporte', 'sport']):
            palabras_clave.append('sports injury')
        
        # Palabras clave para tratamiento
        if any(palabra in condicion for palabra in ['fisioterapia', 'physical therapy', 'rehabilitacion']):
            palabras_clave.append('physical therapy')
        
        return palabras_clave



    def _extraer_palabras_clave(self, condicion):
        """Extrae palabras clave principales de la condición"""
        # Mapeo de términos médicos comunes
        mapeo_terminos = {
            'dolor': ['pain', 'ache', 'discomfort'],
            'rodilla': ['knee', 'knee joint'],
            'hombro': ['shoulder', 'shoulder joint'],
            'cuello': ['neck', 'cervical'],
            'espalda': ['back', 'spine', 'lumbar'],
            'brazo': ['arm', 'upper limb'],
            'pierna': ['leg', 'lower limb'],
            'correr': ['running', 'jogging'],
            'saltar': ['jumping', 'leap'],
            'levantar': ['lifting', 'raise'],
            'trabajar': ['work', 'occupational'],
            'fisioterapia': ['physical therapy', 'physiotherapy'],
            'kinesiologia': ['physical therapy', 'physiotherapy'],
            'rehabilitacion': ['rehabilitation', 'rehab'],
            'ejercicio': ['exercise', 'training'],
            'lesion': ['injury', 'trauma'],
            'tratamiento': ['treatment', 'therapy'],
            'terapia': ['therapy', 'treatment']
        }
        
        palabras_clave = []
        condicion_lower = condicion.lower()
        
        for termino_esp, terminos_en in mapeo_terminos.items():
            if termino_esp in condicion_lower:
                palabras_clave.extend(terminos_en)
        
        return palabras_clave

    def _obtener_terminos_medicos_especificos(self, condicion):
        """Obtiene términos médicos específicos para la condición"""
        terminos_especificos = []
        condicion_lower = condicion.lower()
        
        # Mapeo de condiciones específicas
        if 'dolor' in condicion_lower and 'rodilla' in condicion_lower:
            terminos_especificos.extend([
                'knee pain',
                'knee pain treatment',
                'knee injury',
                'knee rehabilitation'
            ])
        elif 'dolor' in condicion_lower and 'hombro' in condicion_lower:
            terminos_especificos.extend([
                'shoulder pain',
                'shoulder pain treatment',
                'shoulder injury',
                'shoulder rehabilitation'
            ])
        elif 'dolor' in condicion_lower and 'cuello' in condicion_lower:
            terminos_especificos.extend([
                'neck pain',
                'neck pain treatment',
                'cervical pain',
                'neck rehabilitation'
            ])
        elif 'dolor' in condicion_lower and 'espalda' in condicion_lower:
            terminos_especificos.extend([
                'back pain',
                'back pain treatment',
                'lumbar pain',
                'back rehabilitation'
            ])
        elif 'correr' in condicion_lower:
            terminos_especificos.extend([
                'running injury',
                'running pain',
                'runner injury',
                'running rehabilitation'
            ])
        elif 'trabajar' in condicion_lower:
            terminos_especificos.extend([
                'work injury',
                'occupational injury',
                'work-related pain',
                'occupational rehabilitation'
            ])
        
        return terminos_especificos

    def _obtener_terminos_tratamiento(self, condicion):
        """Obtiene términos relacionados con tratamiento"""
        terminos_tratamiento = [
            'physical therapy',
            'physiotherapy',
            'rehabilitation',
            'treatment',
            'therapy',
            'exercise therapy',
            'manual therapy'
        ]
        
        return terminos_tratamiento

    def _es_articulo_relevante(self, articulo, condicion):
        """Determina si un artículo es relevante para la condición"""
        if not articulo or not articulo.titulo:
            return False
        
        titulo_lower = articulo.titulo.lower()
        condicion_lower = condicion.lower()
        
        # Verificar si el título contiene palabras clave relevantes
        palabras_clave = condicion_lower.split()
        coincidencias = sum(1 for palabra in palabras_clave if palabra in titulo_lower)
        
        # Considerar relevante si hay al menos una coincidencia
        return coincidencias > 0

    def buscar_europepmc(self, condicion, especialidad, edad_paciente=None):
        """Busca en Europe PMC con búsqueda mejorada y caché inteligente"""
        try:
            # Normalizar y limpiar la condición
            condicion_limpia = self._limpiar_termino_busqueda(condicion)
            
            # Crear clave de caché única
            cache_key = f"europepmc_{hash(condicion_limpia + especialidad + str(edad_paciente))}"
            
            # Verificar caché primero
            cached_result = self._get_cached_search_result(cache_key)
            if cached_result:
                logger.info(f"✅ Usando resultado del caché para Europe PMC: {condicion_limpia}")
                return cached_result
            
            # Generar términos simplificados pero más específicos para Europe PMC
            terminos_simples = self._generar_terminos_simples_europepmc_mejorados(condicion_limpia, especialidad, edad_paciente)
            
            logger.info(f"🔍 Búsqueda Europe PMC: '{condicion}' -> '{condicion_limpia}' en '{especialidad}'")
            
            tratamientos_encontrados = []
            
            # Buscar con cada término (limitado a 3 para evitar búsquedas excesivas)
            for termino in terminos_simples[:3]:
                try:
                    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                    params = {
                        'query': f'"{termino}" AND ("treatment" OR "therapy" OR "intervention") AND PUB_YEAR:2020-2025',
                        'format': 'json',
                        'pageSize': 8,  # Aumentado para mejor cobertura
                        'resultType': 'core',
                        'sort': 'RELEVANCE'
                    }
                    
                    logger.info(f"🔍 Consultando Europe PMC con término específico: {termino}")
                    response = requests.get(url, params=params, timeout=10)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    if 'resultList' in data and 'result' in data['resultList']:
                        resultados = data['resultList']['result']
                        
                        for resultado in resultados:
                            if self._es_articulo_altamente_relevante_europepmc(resultado, condicion_limpia, especialidad):
                                tratamiento = self._convertir_resultado_europepmc(resultado)
                                if tratamiento:
                                    tratamientos_encontrados.append(tratamiento)
                    
                    # Pausa para evitar rate limiting
                    time.sleep(0.8)  # Aumentado para mayor estabilidad
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error buscando en Europe PMC término '{termino}': {e}")
                    continue
            
            # Eliminar duplicados y ordenar por relevancia
            tratamientos_unicos = self._eliminar_duplicados_tratamientos(tratamientos_encontrados)
            
            # Filtrar solo los 10 más relevantes
            tratamientos_filtrados = self._filtrar_papers_mas_relevantes(tratamientos_unicos, condicion_limpia, especialidad, max_papers=10)
            
            # Guardar en caché
            self._set_cached_search_result(cache_key, tratamientos_filtrados)
            
            logger.info(f"✅ Encontrados {len(tratamientos_filtrados)} papers altamente relevantes de {len(tratamientos_unicos)} totales en Europe PMC para {condicion_limpia}")
            
            return tratamientos_filtrados
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda Europe PMC: {e}")
            return []

    def _es_articulo_altamente_relevante_europepmc(self, resultado, condicion, especialidad):
        """Determina si un resultado de Europe PMC es altamente relevante"""
        if not resultado or 'title' not in resultado:
            return False
        
        titulo = resultado.get('title', '').lower()
        condicion_lower = condicion.lower()
        especialidad_lower = especialidad.lower()
        
        # Criterios de relevancia más estrictos
        criterios_relevancia = []
        
        # 1. Verificar palabras clave específicas de la condición
        palabras_clave_condicion = self._extraer_palabras_clave_especificas(condicion)
        coincidencias_condicion = sum(1 for palabra in palabras_clave_condicion if palabra in titulo)
        criterios_relevancia.append(coincidencias_condicion >= 2)  # Al menos 2 palabras clave
        
        # 2. Verificar términos de la especialidad
        terminos_especialidad = self._obtener_terminos_especialidad(especialidad)
        coincidencias_especialidad = sum(1 for termino in terminos_especialidad if termino in titulo)
        criterios_relevancia.append(coincidencias_especialidad >= 1)  # Al menos 1 término de especialidad
        
        # 3. Verificar términos de tratamiento
        terminos_tratamiento = ['treatment', 'therapy', 'intervention', 'rehabilitation', 'exercise']
        coincidencias_tratamiento = sum(1 for termino in terminos_tratamiento if termino in titulo)
        criterios_relevancia.append(coincidencias_tratamiento >= 1)  # Al menos 1 término de tratamiento
        
        # 4. Verificar que no sea un artículo de revisión general
        exclusiones = ['review', 'meta-analysis', 'systematic review', 'overview']
        es_exclusion = any(exclusion in titulo for exclusion in exclusiones)
        
        # El artículo es relevante si cumple al menos 2 criterios y no es una exclusión
        return sum(criterios_relevancia) >= 2 and not es_exclusion

    def _generar_terminos_simples_europepmc_mejorados(self, condicion, especialidad, edad_paciente=None):
        """Genera términos simples pero más específicos para Europe PMC"""
        terminos = []
        condicion_lower = condicion.lower()
        
        # 1. Términos específicos basados en la condición
        if 'knee' in condicion_lower or 'rodilla' in condicion_lower:
            terminos.extend(['knee pain treatment', 'knee injury rehabilitation', 'knee physical therapy'])
        elif 'shoulder' in condicion_lower or 'hombro' in condicion_lower:
            terminos.extend(['shoulder pain treatment', 'shoulder injury rehabilitation', 'shoulder physical therapy'])
        elif 'neck' in condicion_lower or 'cuello' in condicion_lower:
            terminos.extend(['neck pain treatment', 'cervical pain therapy', 'neck rehabilitation'])
        elif 'back' in condicion_lower or 'espalda' in condicion_lower:
            terminos.extend(['back pain treatment', 'low back pain therapy', 'back rehabilitation'])
        elif 'lumbar' in condicion_lower:
            terminos.extend(['lumbar pain treatment', 'low back pain therapy', 'lumbar rehabilitation'])
        elif 'cervical' in condicion_lower:
            terminos.extend(['cervical pain treatment', 'neck pain therapy', 'cervical rehabilitation'])
        
        # 2. Términos de tratamiento específicos por especialidad
        if especialidad.lower() in ['kinesiologia', 'fisioterapia']:
            terminos.extend(['physical therapy', 'physiotherapy', 'rehabilitation'])
        elif especialidad.lower() == 'fonoaudiologia':
            terminos.extend(['speech therapy', 'communication therapy', 'swallowing treatment'])
        elif especialidad.lower() == 'nutricion':
            terminos.extend(['nutrition therapy', 'dietary treatment', 'nutritional intervention'])
        elif especialidad.lower() == 'psicologia':
            terminos.extend(['psychological therapy', 'mental health treatment', 'psychotherapy'])
        
        # 3. Términos de actividad específicos
        if 'running' in condicion_lower or 'correr' in condicion_lower:
            terminos.extend(['running injury treatment', 'sports injury rehabilitation'])
        elif 'lifting' in condicion_lower or 'levantar' in condicion_lower:
            terminos.extend(['lifting injury treatment', 'work injury rehabilitation'])
        elif 'work' in condicion_lower or 'trabajar' in condicion_lower:
            terminos.extend(['work injury treatment', 'occupational therapy'])
        
        # 4. Agregar términos específicos por edad si está disponible
        if edad_paciente is not None:
            terminos_edad = self._obtener_terminos_por_edad(edad_paciente, especialidad)
            terminos.extend(terminos_edad[:2])  # Solo los 2 primeros términos de edad
        
        # 5. Si no hay términos específicos, usar generales pero más restrictivos
        if not terminos:
            palabras_clave = self._extraer_palabras_clave_especificas(condicion)
            if palabras_clave:
                terminos.extend([f"{palabra} treatment" for palabra in palabras_clave[:2]])
            else:
                # Términos generales pero específicos
                terminos.extend(['physical therapy', 'rehabilitation', 'treatment'])
        
        # Eliminar duplicados y limitar a los más relevantes
        terminos_unicos = list(dict.fromkeys(terminos))  # Mantener orden
        return terminos_unicos[:5]  # Máximo 5 términos más relevantes

    def _convertir_resultado_europepmc(self, resultado):
        """Convierte un resultado de Europe PMC a Tratamiento"""
        try:
            titulo = resultado.get('title', 'Sin título')
            autores = resultado.get('authorString', '').split(', ') if resultado.get('authorString') else []
            doi = resultado.get('doi', 'Sin DOI')
            fecha = resultado.get('firstPublicationDate', 'Fecha no disponible')
            resumen = resultado.get('abstractText', 'Sin resumen disponible')
            
            # Extraer año de la fecha
            año = 'N/A'
            if fecha and fecha != 'Fecha no disponible':
                try:
                    # Intentar extraer año de diferentes formatos
                    if '-' in fecha:
                        año = fecha.split('-')[0]
                    elif '/' in fecha:
                        año = fecha.split('/')[-1]
                    else:
                        # Buscar 4 dígitos consecutivos
                        import re
                        año_match = re.search(r'\d{4}', fecha)
                        if año_match:
                            año = año_match.group()
                except:
                    año = 'N/A'
            
            # Limpiar DOI
            doi_limpio = doi
            if doi and doi != 'Sin DOI':
                # Remover prefijos comunes
                doi_limpio = doi.replace('https://doi.org/', '').replace('http://doi.org/', '')
                # Asegurar que no tenga espacios
                doi_limpio = doi_limpio.strip()
            
            return TratamientoCientifico(
                titulo=titulo,
                descripcion=resumen[:200] if resumen else "Sin descripción disponible",
                doi=doi_limpio,
                fuente='Europe PMC',
                tipo_evidencia='Artículo científico',
                fecha_publicacion=fecha,
                autores=autores,
                resumen=resumen,
                keywords=[],
                año_publicacion=año  # Agregar año específico
            )
        except Exception as e:
            logger.error(f"❌ Error convirtiendo resultado Europe PMC: {e}")
            return None

    def _limpiar_termino_busqueda(self, termino):
        """Limpia y normaliza el término de búsqueda"""
        if not termino:
            return ""
        
        # Remover caracteres especiales y normalizar
        termino_limpio = re.sub(r'[^\w\s]', ' ', termino)
        termino_limpio = re.sub(r'\s+', ' ', termino_limpio).strip()
        
        # Traducir términos comunes
        traducciones = {
            'dolor': 'pain',
            'rodilla': 'knee',
            'hombro': 'shoulder',
            'cuello': 'neck',
            'espalda': 'back',
            'brazo': 'arm',
            'pierna': 'leg',
            'correr': 'running',
            'saltar': 'jumping',
            'levantar': 'lifting',
            'trabajar': 'work',
            'fisioterapia': 'physical therapy',
            'kinesiologia': 'physical therapy',
            'rehabilitacion': 'rehabilitation',
            'ejercicio': 'exercise',
            'lesion': 'injury',
            'tratamiento': 'treatment',
            'terapia': 'therapy'
        }
        
        for esp, en in traducciones.items():
            termino_limpio = termino_limpio.replace(esp, en)
        
        return termino_limpio
    
    def buscar_medicamento_fda(self, nombre_medicamento: str) -> Dict:
        """
        Busca información de medicamentos en OpenFDA
        """
        try:
            url = "https://api.fda.gov/drug/label.json"
            params = {
                'search': f'generic_name:"{nombre_medicamento}"',
                'limit': 1
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if results:
                drug_info = results[0]
                return {
                    'nombre': drug_info.get('openfda', {}).get('generic_name', [nombre_medicamento])[0],
                    'indicaciones': drug_info.get('indications_and_usage', ['No disponible']),
                    'efectos_adversos': drug_info.get('adverse_reactions', ['No disponible']),
                    'contraindicaciones': drug_info.get('contraindications', ['No disponible']),
                    'fuente': 'OpenFDA'
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error buscando en OpenFDA: {e}")
            return {}
    
    def generar_preguntas_cientificas(self, condicion: str, especialidad: str) -> List[PreguntaCientifica]:
        """
        Genera preguntas basadas en evidencia científica
        """
        preguntas = []
        
        # Buscar en PubMed para contexto
        tratamientos = self.buscar_tratamiento_pubmed(condicion, especialidad)
        
        if tratamientos:
            # Extraer información relevante para preguntas
            for tratamiento in tratamientos[:2]:  # Usar solo los 2 primeros
                resumen = tratamiento.resumen.lower()
                
                # Generar preguntas basadas en el contenido
                if 'dolor' in resumen:
                    preguntas.append(PreguntaCientifica(
                        pregunta="¿Cuál es la intensidad del dolor en una escala del 1 al 10?",
                        contexto="Evaluación de dolor según evidencia científica",
                        fuente="PubMed",
                        relevancia="Alta",
                        tipo="Evaluación"
                    ))
                
                if 'duración' in resumen or 'tiempo' in resumen:
                    preguntas.append(PreguntaCientifica(
                        pregunta="¿Cuánto tiempo ha estado experimentando estos síntomas?",
                        contexto="Evaluación temporal de síntomas",
                        fuente="PubMed",
                        relevancia="Alta",
                        tipo="Historia clínica"
                    ))
                
                if 'actividad' in resumen or 'ejercicio' in resumen:
                    preguntas.append(PreguntaCientifica(
                        pregunta="¿Qué actividades agravan o alivian sus síntomas?",
                        contexto="Evaluación de factores modificadores",
                        fuente="PubMed",
                        relevancia="Media",
                        tipo="Evaluación funcional"
                    ))
        
        # Preguntas específicas por especialidad
        preguntas_especialidad = self._preguntas_por_especialidad(especialidad, condicion)
        preguntas.extend(preguntas_especialidad)
        
        return preguntas
    
    def _preguntas_por_especialidad(self, especialidad: str, condicion: str) -> List[PreguntaCientifica]:
        """
        Genera preguntas específicas por especialidad médica
        """
        preguntas = []
        
        if especialidad == 'fisioterapia' or especialidad == 'kinesiologia':
            preguntas.extend([
                PreguntaCientifica(
                    pregunta="¿Qué movimientos o actividades le causan más dolor?",
                    contexto="Evaluación funcional en fisioterapia",
                    fuente="Evidencia clínica",
                    relevancia="Alta",
                    tipo="Evaluación funcional"
                ),
                PreguntaCientifica(
                    pregunta="¿Ha notado mejoría con algún tipo de ejercicio o movimiento?",
                    contexto="Identificación de factores terapéuticos",
                    fuente="Evidencia clínica",
                    relevancia="Alta",
                    tipo="Evaluación terapéutica"
                )
            ])
        
        elif especialidad == 'psicologia':
            preguntas.extend([
                PreguntaCientifica(
                    pregunta="¿Cómo ha afectado esta condición su estado de ánimo?",
                    contexto="Evaluación psicológica",
                    fuente="Evidencia clínica",
                    relevancia="Alta",
                    tipo="Evaluación psicológica"
                ),
                PreguntaCientifica(
                    pregunta="¿Ha notado cambios en su calidad del sueño?",
                    contexto="Evaluación de síntomas asociados",
                    fuente="Evidencia clínica",
                    relevancia="Media",
                    tipo="Evaluación de síntomas"
                )
            ])
        
        elif especialidad == 'nutricion':
            preguntas.extend([
                PreguntaCientifica(
                    pregunta="¿Ha notado cambios en su apetito o peso recientemente?",
                    contexto="Evaluación nutricional",
                    fuente="Evidencia clínica",
                    relevancia="Alta",
                    tipo="Evaluación nutricional"
                ),
                PreguntaCientifica(
                    pregunta="¿Hay alimentos que le causan malestar o que evita?",
                    contexto="Identificación de intolerancias",
                    fuente="Evidencia clínica",
                    relevancia="Media",
                    tipo="Evaluación dietética"
                )
            ])
        
        return preguntas
    
    def obtener_tratamientos_completos(self, condicion: str, especialidad: str, edad_paciente: int = None, terminos_seleccionados: List[str] = None) -> Dict:
        """
        Obtiene tratamientos completos de múltiples fuentes y genera planes de intervención específicos
        Incluye consideración de la edad del paciente para búsquedas más específicas
        Permite al profesional seleccionar términos de búsqueda específicos
        """
        resultados = {
            'tratamientos_pubmed': [],
            'tratamientos_europepmc': [],
            'preguntas_cientificas': [],
            'medicamentos_fda': {},
            'plan_intervencion': None
        }
        
        try:
            # Detectar condiciones específicas para mejorar la búsqueda
            condiciones_detectadas = self._detectar_condiciones_especificas(condicion)
            logger.info(f"🔍 Condiciones detectadas: {condiciones_detectadas}")
            
            # Mejorar términos de búsqueda con condiciones específicas
            condicion_mejorada = condicion
            if condiciones_detectadas:
                for condicion_esp in condiciones_detectadas:
                    if condicion_esp in self.condiciones_especificas:
                        terminos_adicionales = self.condiciones_especificas[condicion_esp]['terminos']
                        condicion_mejorada += " " + " ".join(terminos_adicionales[:2])
            
            # Usar términos seleccionados por el profesional o generar automáticamente
            if terminos_seleccionados and len(terminos_seleccionados) > 0:
                # Usar términos seleccionados por el profesional
                condicion_mejorada += " " + " ".join(terminos_seleccionados)
                logger.info(f"👨‍⚕️ Términos seleccionados por el profesional: {terminos_seleccionados}")
            else:
                # Agregar términos específicos por edad si está disponible
                if edad_paciente is not None:
                    terminos_edad = self._obtener_terminos_por_edad(edad_paciente, especialidad)
                    if terminos_edad:
                        condicion_mejorada += " " + " ".join(terminos_edad)
                        logger.info(f"👤 Términos por edad ({edad_paciente} años): {terminos_edad}")
            
            # Intentar búsqueda en PubMed primero
            try:
                resultados['tratamientos_pubmed'] = self.buscar_tratamiento_pubmed(condicion_mejorada, especialidad, edad_paciente)
                if resultados['tratamientos_pubmed']:
                    logger.info(f"✅ PubMed funcionando: {len(resultados['tratamientos_pubmed'])} resultados")
                else:
                    logger.warning("⚠️ PubMed no devolvió resultados")
            except Exception as e:
                logger.error(f"❌ Error en PubMed: {e}")
                resultados['tratamientos_pubmed'] = []
            
            # Buscar en Europe PMC (fuente más confiable)
            try:
                resultados['tratamientos_europepmc'] = self.buscar_europepmc(condicion_mejorada, especialidad, edad_paciente)
                if resultados['tratamientos_europepmc']:
                    logger.info(f"✅ Europe PMC funcionando: {len(resultados['tratamientos_europepmc'])} resultados")
                else:
                    logger.warning("⚠️ Europe PMC no devolvió resultados")
            except Exception as e:
                logger.error(f"❌ Error en Europe PMC: {e}")
                resultados['tratamientos_europepmc'] = []
            
            # Si no se encontraron resultados, intentar búsqueda más amplia
            if not resultados['tratamientos_pubmed'] and not resultados['tratamientos_europepmc']:
                logger.info("🔄 Intentando búsqueda más amplia...")
                try:
                    # Búsqueda más simple en Europe PMC
                    resultados['tratamientos_europepmc'] = self._busqueda_amplia_europepmc(condicion, especialidad)
                    if resultados['tratamientos_europepmc']:
                        logger.info(f"✅ Búsqueda amplia exitosa: {len(resultados['tratamientos_europepmc'])} resultados")
                except Exception as e:
                    logger.error(f"❌ Error en búsqueda amplia: {e}")
            
            # Generar preguntas científicas
            resultados['preguntas_cientificas'] = self.generar_preguntas_cientificas(condicion, especialidad)
            
            # Generar plan de intervención específico
            todos_tratamientos = resultados['tratamientos_pubmed'] + resultados['tratamientos_europepmc']
            resultados['plan_intervencion'] = self._generar_plan_intervencion_especifico(
                condicion, especialidad, todos_tratamientos
            )
            
            # Si hay medicamentos mencionados, buscar en FDA
            if 'medicamento' in condicion.lower() or 'farmaco' in condicion.lower():
                # Extraer posibles nombres de medicamentos (simplificado)
                palabras = condicion.split()
                for palabra in palabras:
                    if len(palabra) > 3:  # Posible nombre de medicamento
                        info_fda = self.buscar_medicamento_fda(palabra)
                        if info_fda:
                            resultados['medicamentos_fda'][palabra] = info_fda
            
            total_resultados = len(resultados['tratamientos_pubmed']) + len(resultados['tratamientos_europepmc'])
            logger.info(f"✅ Búsqueda completada para {condicion} en {especialidad}")
            logger.info(f"✅ Total resultados: {total_resultados}")
            logger.info(f"✅ Plan de intervención generado con {len(resultados['plan_intervencion'].tecnicas_especificas)} técnicas específicas")
            
            return resultados
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda completa: {e}")
            return resultados

    def _busqueda_amplia_europepmc(self, condicion, especialidad):
        """Búsqueda más amplia en Europe PMC con términos más simples"""
        try:
            logger.info(f"🔍 Búsqueda amplia Europe PMC: '{condicion}' en '{especialidad}'")
            
            # Términos de búsqueda más simples
            terminos_simples = []
            
            # Extraer palabras clave básicas
            palabras = condicion.lower().split()
            for palabra in palabras:
                if len(palabra) > 3:  # Palabras de más de 3 caracteres
                    terminos_simples.append(palabra)
            
            # Agregar términos de especialidad
            if especialidad.lower() in ['kinesiologia', 'fisioterapia']:
                terminos_simples.extend(['therapy', 'treatment', 'exercise'])
            elif especialidad.lower() == 'fonoaudiologia':
                terminos_simples.extend(['speech', 'communication', 'swallowing'])
            elif especialidad.lower() == 'nutricion':
                terminos_simples.extend(['nutrition', 'diet', 'food'])
            elif especialidad.lower() == 'psicologia':
                terminos_simples.extend(['psychology', 'mental', 'therapy'])
            
            tratamientos_encontrados = []
            
            # Buscar con cada término simple
            for termino in terminos_simples[:3]:  # Limitar a 3 términos
                try:
                    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                    params = {
                        'query': termino,
                        'format': 'json',
                        'pageSize': 5
                    }
                    
                    logger.info(f"🔍 Búsqueda amplia Europe PMC: {termino}")
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            if 'resultList' in data and 'result' in data['resultList']:
                                resultados = data['resultList']['result']
                                
                                for resultado in resultados:
                                    if self._es_articulo_relevante_europepmc(resultado, condicion):
                                        tratamiento = self._convertir_resultado_europepmc(resultado)
                                        if tratamiento:
                                            tratamientos_encontrados.append(tratamiento)
                                
                                logger.info(f"✅ Encontrados {len(resultados)} artículos para '{termino}'")
                            else:
                                logger.warning(f"⚠️ Respuesta inesperada de Europe PMC para '{termino}'")
                                
                        except json.JSONDecodeError as e:
                            logger.warning(f"⚠️ Error decodificando JSON para '{termino}': {e}")
                            continue
                    else:
                        logger.warning(f"⚠️ Error HTTP {response.status_code} para '{termino}'")
                        continue
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error en búsqueda amplia '{termino}': {e}")
                    continue
            
            # Eliminar duplicados
            tratamientos_unicos = self._eliminar_duplicados_tratamientos(tratamientos_encontrados)
            
            logger.info(f"✅ Búsqueda amplia completada: {len(tratamientos_unicos)} tratamientos únicos")
            return tratamientos_unicos
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda amplia Europe PMC: {e}")
            return []

    def _eliminar_duplicados_tratamientos(self, tratamientos):
        """Elimina duplicados de tratamientos usando criterios más estrictos"""
        if not tratamientos:
            return []
        
        tratamientos_unicos = []
        titulos_vistos = set()
        dois_vistos = set()
        
        for tratamiento in tratamientos:
            if not tratamiento or not tratamiento.titulo:
                continue
            
            # Normalizar título para comparación
            titulo_normalizado = self._normalizar_titulo(tratamiento.titulo)
            
            # Verificar si es duplicado basado en DOI
            if tratamiento.doi and tratamiento.doi != "Sin DOI":
                doi_limpio = tratamiento.doi.strip()
                if doi_limpio in dois_vistos:
                    logger.debug(f"⚠️ Duplicado por DOI ignorado: {doi_limpio}")
                    continue
                dois_vistos.add(doi_limpio)
            
            # Verificar si es duplicado basado en título normalizado
            if titulo_normalizado in titulos_vistos:
                logger.debug(f"⚠️ Duplicado por título ignorado: {tratamiento.titulo}")
                continue
            
            titulos_vistos.add(titulo_normalizado)
            tratamientos_unicos.append(tratamiento)
        
        # Ordenar por relevancia (títulos más específicos primero)
        tratamientos_unicos.sort(key=lambda x: self._calcular_score_relevancia(x), reverse=True)
        
        logger.info(f"✅ Eliminados duplicados: {len(tratamientos)} -> {len(tratamientos_unicos)} tratamientos únicos")
        return tratamientos_unicos

    def _normalizar_titulo(self, titulo):
        """Normaliza un título para comparación de duplicados"""
        if not titulo:
            return ""
        
        # Convertir a minúsculas
        titulo_lower = titulo.lower()
        
        # Remover caracteres especiales y espacios extra
        titulo_limpio = re.sub(r'[^\w\s]', ' ', titulo_lower)
        titulo_limpio = re.sub(r'\s+', ' ', titulo_limpio).strip()
        
        # Remover palabras comunes que no aportan significado
        palabras_comunes = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        palabras = titulo_limpio.split()
        palabras_filtradas = [palabra for palabra in palabras if palabra not in palabras_comunes and len(palabra) > 2]
        
        return ' '.join(palabras_filtradas)

    def _obtener_detalles_pubmed(self, ids):
        """Obtiene detalles de artículos de PubMed"""
        try:
            if not ids:
                return []
            
            # Convertir lista de IDs a string
            id_string = ','.join(ids)
            
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            params = {
                'db': 'pubmed',
                'id': id_string,
                'retmode': 'json',
                'api_key': self.ncbi_api_key,
                'tool': 'MedConnect-IA',
                'email': 'support@medconnect.cl'
            }
            
            logger.info(f"🔍 Obteniendo detalles para {len(ids)} artículos de PubMed")
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"⚠️ Error HTTP {response.status_code} obteniendo detalles de PubMed")
                return []
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error decodificando JSON de detalles PubMed: {e}")
                return []
            
            tratamientos = []
            
            if 'result' in data:
                for pmid, info in data['result'].items():
                    if pmid == 'uids':
                        continue
                    
                    try:
                        titulo = info.get('title', 'Sin título')
                        autores = info.get('authors', [])
                        doi = info.get('articleids', [])
                        fecha = info.get('pubdate', 'Fecha no disponible')
                        resumen = info.get('abstract', 'Sin resumen disponible')
                        
                        # Extraer DOI
                        doi_valor = 'Sin DOI'
                        for article_id in doi:
                            if article_id.get('idtype') == 'doi':
                                doi_valor = article_id.get('value', 'Sin DOI')
                                break
                        
                        # Limpiar DOI
                        doi_limpio = doi_valor
                        if doi_valor and doi_valor != 'Sin DOI':
                            # Remover prefijos comunes
                            doi_limpio = doi_valor.replace('https://doi.org/', '').replace('http://doi.org/', '')
                            # Asegurar que no tenga espacios
                            doi_limpio = doi_limpio.strip()
                        
                        # Extraer año de la fecha
                        año = 'N/A'
                        if fecha and fecha != 'Fecha no disponible':
                            try:
                                # Intentar extraer año de diferentes formatos
                                if '-' in fecha:
                                    año = fecha.split('-')[0]
                                elif '/' in fecha:
                                    año = fecha.split('/')[-1]
                                else:
                                    # Buscar 4 dígitos consecutivos
                                    import re
                                    año_match = re.search(r'\d{4}', fecha)
                                    if año_match:
                                        año = año_match.group()
                            except:
                                año = 'N/A'
                        
                        # Extraer autores
                        autores_lista = []
                        if autores:
                            for autor in autores:
                                if 'name' in autor:
                                    autores_lista.append(autor['name'])
                        
                        tratamiento = TratamientoCientifico(
                            titulo=titulo,
                            descripcion=resumen[:200] if resumen else "Sin descripción disponible",
                            doi=doi_limpio,
                            fuente="PubMed",
                            tipo_evidencia=self._determinar_nivel_evidencia(titulo, resumen),
                            fecha_publicacion=fecha,
                            autores=autores_lista,
                            resumen=resumen,
                            keywords=[],
                            nivel_evidencia=self._determinar_nivel_evidencia(titulo, resumen),
                            año_publicacion=año,
                            evidencia_cientifica=f"Estudio de {', '.join(autores_lista[:2])} ({año})" if autores_lista else "Evidencia científica",
                            contraindicaciones="Consultar con profesional de la salud"
                        )
                        
                        tratamientos.append(tratamiento)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error procesando artículo {pmid}: {e}")
                        continue
            
            return tratamientos
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo detalles PubMed: {e}")
            return []

    def _determinar_nivel_evidencia(self, titulo, resumen):
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

    def _calcular_score_relevancia(self, tratamiento):
        """Calcula un score de relevancia para ordenar tratamientos"""
        if not tratamiento or not tratamiento.titulo:
            return 0
        
        score = 0
        titulo_lower = tratamiento.titulo.lower()
        
        # Puntos por términos específicos de tratamiento
        terminos_tratamiento = ['treatment', 'therapy', 'intervention', 'rehabilitation', 'exercise']
        for termino in terminos_tratamiento:
            if termino in titulo_lower:
                score += 10
        
        # Puntos por términos específicos de especialidad
        terminos_especialidad = ['physical therapy', 'physiotherapy', 'speech therapy', 'nutrition', 'psychology']
        for termino in terminos_especialidad:
            if termino in titulo_lower:
                score += 8
        
        # Puntos por términos específicos de condición
        terminos_condicion = ['pain', 'injury', 'disorder', 'syndrome', 'disease']
        for termino in terminos_condicion:
            if termino in titulo_lower:
                score += 5
        
        # Puntos por tener DOI
        if tratamiento.doi and tratamiento.doi != "Sin DOI":
            score += 3
        
        # Puntos por tener año de publicación reciente
        if tratamiento.año_publicacion and tratamiento.año_publicacion != "N/A":
            try:
                año = int(tratamiento.año_publicacion)
                if año >= 2020:
                    score += 5
                elif año >= 2018:
                    score += 3
                elif año >= 2015:
                    score += 1
            except:
                pass
        
        # Penalización por términos de exclusión
        exclusiones = ['review', 'meta-analysis', 'systematic review', 'overview', 'case report']
        for exclusion in exclusiones:
            if exclusion in titulo_lower:
                score -= 5
        
        return score

    def _filtrar_papers_mas_relevantes(self, tratamientos, condicion, especialidad, max_papers=10):
        """Filtra y retorna solo los papers más relevantes basados en criterios estrictos"""
        if not tratamientos:
            return []
        
        # Calcular score de relevancia específico para cada tratamiento
        tratamientos_con_score = []
        for tratamiento in tratamientos:
            score = self._calcular_score_relevancia_especifica(tratamiento, condicion, especialidad)
            tratamientos_con_score.append((tratamiento, score))
        
        # Ordenar por score de relevancia (mayor primero)
        tratamientos_con_score.sort(key=lambda x: x[1], reverse=True)
        
        # Filtrar solo los que tienen score mínimo
        tratamientos_filtrados = []
        for tratamiento, score in tratamientos_con_score:
            if score >= 15:  # Score mínimo para considerar relevante
                tratamientos_filtrados.append(tratamiento)
                if len(tratamientos_filtrados) >= max_papers:
                    break
        
        # Si no hay suficientes con score alto, tomar los mejores disponibles
        if len(tratamientos_filtrados) < max_papers:
            for tratamiento, score in tratamientos_con_score:
                if score >= 8:  # Score mínimo más bajo
                    if tratamiento not in tratamientos_filtrados:
                        tratamientos_filtrados.append(tratamiento)
                        if len(tratamientos_filtrados) >= max_papers:
                            break
        
        # Si aún no hay suficientes, tomar los primeros max_papers
        if len(tratamientos_filtrados) < max_papers:
            tratamientos_filtrados = [t[0] for t in tratamientos_con_score[:max_papers]]
        
        logger.info(f"🎯 Filtrados {len(tratamientos_filtrados)} papers más relevantes de {len(tratamientos)} totales")
        return tratamientos_filtrados

    def _calcular_score_relevancia_especifica(self, tratamiento, condicion, especialidad):
        """Calcula un score de relevancia específico basado en la condición y especialidad"""
        if not tratamiento or not tratamiento.titulo:
            return 0
        
        score = 0
        titulo_lower = tratamiento.titulo.lower()
        condicion_lower = condicion.lower()
        especialidad_lower = especialidad.lower()
        
        # Score por coincidencia exacta de palabras clave de la condición
        palabras_clave_condicion = self._extraer_palabras_clave_especificas(condicion)
        coincidencias_condicion = sum(1 for palabra in palabras_clave_condicion if palabra in titulo_lower)
        score += coincidencias_condicion * 15  # 15 puntos por cada palabra clave
        
        # Score por términos de la especialidad
        terminos_especialidad = self._obtener_terminos_especialidad(especialidad)
        coincidencias_especialidad = sum(1 for termino in terminos_especialidad if termino in titulo_lower)
        score += coincidencias_especialidad * 10  # 10 puntos por cada término de especialidad
        
        # Score por términos de tratamiento
        terminos_tratamiento = ['treatment', 'therapy', 'intervention', 'rehabilitation', 'exercise', 'training']
        coincidencias_tratamiento = sum(1 for termino in terminos_tratamiento if termino in titulo_lower)
        score += coincidencias_tratamiento * 8  # 8 puntos por cada término de tratamiento
        
        # Score por año de publicación reciente
        if tratamiento.año_publicacion and tratamiento.año_publicacion != "N/A":
            try:
                año = int(tratamiento.año_publicacion)
                if año >= 2023:
                    score += 10
                elif año >= 2020:
                    score += 8
                elif año >= 2018:
                    score += 5
                elif año >= 2015:
                    score += 3
            except:
                pass
        
        # Score por tener DOI
        if tratamiento.doi and tratamiento.doi != "Sin DOI":
            score += 5
        
        # Penalización por términos de exclusión
        exclusiones = ['review', 'meta-analysis', 'systematic review', 'overview', 'case report', 'letter', 'editorial']
        for exclusion in exclusiones:
            if exclusion in titulo_lower:
                score -= 10
        
        # Penalización por títulos muy genéricos
        palabras_genericas = ['study', 'analysis', 'evaluation', 'assessment']
        if any(palabra in titulo_lower for palabra in palabras_genericas):
            score -= 5
        
        return max(0, score)  # No permitir scores negativos

    def generar_preguntas_personalizadas_evaluacion(self, motivo_consulta: str, tipo_atencion: str) -> List[str]:
        """
        Genera preguntas personalizadas para evaluación/anamnesis basadas en el motivo de consulta y tipo de atención
        """
        try:
            logger.info(f"🔍 Generando preguntas personalizadas para: {motivo_consulta} en {tipo_atencion}")
            
            # Normalizar inputs
            motivo_lower = motivo_consulta.lower()
            tipo_lower = tipo_atencion.lower()
            
            # Mapeo de tipos de atención a funciones específicas
            mapeo_tipos = {
                'fonoaudiologia': self._preguntas_fonoaudiologia,
                'fonoaudiología': self._preguntas_fonoaudiologia,
                'kinesiologia': self._preguntas_kinesiologia,
                'kinesiología': self._preguntas_kinesiologia,
                'fisioterapia': self._preguntas_kinesiologia,
                'nutricion': self._preguntas_nutricion,
                'nutrición': self._preguntas_nutricion,
                'psicologia': self._preguntas_psicologia,
                'psicología': self._preguntas_psicologia,
                'enfermeria': self._preguntas_enfermeria,
                'enfermería': self._preguntas_enfermeria,
                'medicina': self._preguntas_medicina_general,
                'medicina_general': self._preguntas_medicina_general,
                'urgencias': self._preguntas_urgencias,
                'terapia_ocupacional': self._preguntas_terapia_ocupacional,
                'terapia ocupacional': self._preguntas_terapia_ocupacional
            }
            
            # Obtener función específica para el tipo de atención
            funcion_preguntas = mapeo_tipos.get(tipo_lower, self._preguntas_generales)
            
            # Generar preguntas personalizadas
            preguntas = funcion_preguntas(motivo_lower)
            
            # Limitar a 5-10 preguntas más relevantes
            preguntas_finales = preguntas[:10] if len(preguntas) > 10 else preguntas
            
            logger.info(f"✅ Generadas {len(preguntas_finales)} preguntas personalizadas para {tipo_atencion}")
            
            return preguntas_finales
            
        except Exception as e:
            logger.error(f"❌ Error generando preguntas personalizadas: {e}")
            return self._preguntas_generales(motivo_consulta.lower())

    def _preguntas_fonoaudiologia(self, motivo: str) -> List[str]:
        """Preguntas específicas para Fonoaudiología"""
        preguntas = []
        
        # Análisis para lactancia y frenillo lingual
        if any(palabra in motivo for palabra in ['lactancia', 'lactation', 'succion', 'suction', 'pecho', 'breast']):
            preguntas.extend([
                "¿Cuánto tiempo puede succionar el bebé antes de fatigarse?",
                "¿Se desacopla frecuentemente del pecho durante la alimentación?",
                "¿Escucha chasquidos o sonidos al succionar?",
                "¿Cuántas veces al día intenta alimentarse?",
                "¿Hay dolor en los pezones durante la lactancia?",
                "¿El bebé tiene dificultad para mantener el agarre?",
                "¿Cuánto tiempo permanece en cada pecho?",
                "¿Hay pérdida de peso o ganancia insuficiente?"
            ])
        
        # Análisis para frenillo lingual
        if any(palabra in motivo for palabra in ['frenillo', 'frenulum', 'lingual', 'tongue']):
            preguntas.extend([
                "¿El bebé puede sacar la lengua completamente?",
                "¿Hay limitación en el movimiento de la lengua?",
                "¿La lengua tiene forma de corazón al sacarla?",
                "¿Hay dificultad para lamer o mover la lengua?",
                "¿El frenillo se ve tenso o corto?",
                "¿Hay antecedentes familiares de frenillo lingual?",
                "¿El bebé puede hacer movimientos linguales normales?"
            ])
        
        # Análisis para problemas de deglución
        if any(palabra in motivo for palabra in ['deglucion', 'swallowing', 'tragar', 'dificultad']):
            preguntas.extend([
                "¿Hay tos o atragantamiento al comer?",
                "¿Cuánto tiempo tarda en comer una comida?",
                "¿Hay regurgitación nasal?",
                "¿Cambia la voz después de comer?",
                "¿Hay pérdida de peso por dificultad para comer?",
                "¿Prefiere ciertas texturas de alimentos?",
                "¿Hay dolor al tragar?"
            ])
        
        # Análisis para problemas de habla
        if any(palabra in motivo for palabra in ['habla', 'speech', 'lenguaje', 'language']):
            preguntas.extend([
                "¿Qué edad tenía cuando dijo sus primeras palabras?",
                "¿Cuántas palabras dice actualmente?",
                "¿Puede formar frases completas?",
                "¿Los demás entienden lo que dice?",
                "¿Hay sonidos que no puede pronunciar?",
                "¿Ha habido regresión en el lenguaje?",
                "¿Hay antecedentes familiares de problemas de habla?"
            ])
        
        # Análisis para problemas de audición
        if any(palabra in motivo for palabra in ['audicion', 'hearing', 'sordera', 'oído']):
            preguntas.extend([
                "¿Responde a sonidos del ambiente?",
                "¿Gira la cabeza hacia sonidos?",
                "¿Necesita que le repitan las cosas?",
                "¿Sube el volumen de la TV muy alto?",
                "¿Hay antecedentes familiares de pérdida auditiva?",
                "¿Ha tenido infecciones de oído frecuentes?",
                "¿Hay zumbidos o pitidos en los oídos?"
            ])
        
        # Preguntas generales de fonoaudiología
        if not preguntas:
            preguntas.extend([
                "¿Cuál es la principal preocupación sobre la comunicación?",
                "¿Cuándo comenzó a notar el problema?",
                "¿Ha habido cambios recientes en el comportamiento?",
                "¿Hay otros problemas médicos asociados?",
                "¿Qué tratamientos ha recibido anteriormente?",
                "¿Cómo afecta esto en la vida diaria?",
                "¿Qué espera lograr con la terapia?"
            ])
        
        return preguntas

    def _preguntas_kinesiologia(self, motivo: str) -> List[str]:
        """Preguntas específicas para Kinesiología/Fisioterapia"""
        preguntas = []
        
        # Análisis para dolor de rodilla
        if any(palabra in motivo for palabra in ['rodilla', 'knee']):
            preguntas.extend([
                "¿En qué momento del día es peor el dolor?",
                "¿Qué actividades agravan el dolor?",
                "¿Qué actividades alivian el dolor?",
                "¿Hay hinchazón o calor en la rodilla?",
                "¿Ha tenido lesiones previas en la rodilla?",
                "¿El dolor es constante o intermitente?",
                "¿Hay bloqueos o sensación de inestabilidad?",
                "¿Puede subir y bajar escaleras sin dolor?"
            ])
        
        # Análisis para dolor de hombro
        elif any(palabra in motivo for palabra in ['hombro', 'shoulder']):
            preguntas.extend([
                "¿En qué posición es peor el dolor?",
                "¿Puede levantar el brazo por encima de la cabeza?",
                "¿Hay dolor al dormir sobre ese lado?",
                "¿Qué actividades agravan el dolor?",
                "¿Ha tenido lesiones previas en el hombro?",
                "¿Hay pérdida de fuerza en el brazo?",
                "¿El dolor se irradia hacia el brazo?",
                "¿Puede realizar actividades de la vida diaria?"
            ])
        
        # Análisis para dolor de cuello
        elif any(palabra in motivo for palabra in ['cuello', 'neck']):
            preguntas.extend([
                "¿El dolor se irradia hacia los brazos?",
                "¿Hay hormigueo o adormecimiento en las manos?",
                "¿Qué posiciones agravan el dolor?",
                "¿Trabaja con computadora por largas horas?",
                "¿Ha tenido accidentes o traumatismos recientes?",
                "¿Hay mareos o vértigo asociados?",
                "¿El dolor es peor por la mañana?",
                "¿Puede girar la cabeza completamente?"
            ])
        
        # Análisis para dolor de espalda
        elif any(palabra in motivo for palabra in ['espalda', 'back', 'lumbar']):
            preguntas.extend([
                "¿El dolor se irradia hacia las piernas?",
                "¿Hay hormigueo o adormecimiento en las piernas?",
                "¿Qué posiciones alivian el dolor?",
                "¿Ha tenido lesiones previas en la espalda?",
                "¿El dolor es peor al estar sentado o de pie?",
                "¿Puede levantar objetos pesados?",
                "¿Hay pérdida de fuerza en las piernas?",
                "¿El dolor afecta el sueño?"
            ])
        
        # Análisis para lesiones deportivas
        elif any(palabra in motivo for palabra in ['deporte', 'sport', 'correr', 'running']):
            preguntas.extend([
                "¿Qué deporte practica y con qué frecuencia?",
                "¿Cuándo comenzó el problema?",
                "¿Ha cambiado su rutina de entrenamiento?",
                "¿Qué calzado usa para entrenar?",
                "¿Hay superficies específicas que agravan el problema?",
                "¿Ha tenido lesiones similares anteriormente?",
                "¿Cuál es su objetivo deportivo?",
                "¿Puede continuar entrenando con el problema?"
            ])
        
        # Preguntas generales de kinesiología
        if not preguntas:
            preguntas.extend([
                "¿Cuándo comenzó el problema?",
                "¿Qué actividades agravan los síntomas?",
                "¿Qué actividades alivian los síntomas?",
                "¿Ha tenido lesiones previas en la zona?",
                "¿El problema afecta su trabajo o actividades diarias?",
                "¿Ha recibido tratamiento previo?",
                "¿Cuál es su objetivo de recuperación?",
                "¿Hay otros problemas médicos asociados?"
            ])
        
        return preguntas

    def _preguntas_nutricion(self, motivo: str) -> List[str]:
        """Preguntas específicas para Nutrición"""
        preguntas = []
        
        # Análisis para diabetes
        if any(palabra in motivo for palabra in ['diabetes', 'glucosa', 'glucose']):
            preguntas.extend([
                "¿Cuál es su nivel de glucosa en ayunas?",
                "¿Cuál es su hemoglobina glicosilada (HbA1c)?",
                "¿Cuántas veces al día se mide la glucosa?",
                "¿Qué medicamentos toma para la diabetes?",
                "¿Ha tenido episodios de hipoglucemia?",
                "¿Cuál es su peso actual y altura?",
                "¿Qué tipo de dieta sigue actualmente?",
                "¿Realiza actividad física regularmente?",
                "¿Hay antecedentes familiares de diabetes?",
                "¿Ha tenido complicaciones de la diabetes?"
            ])
        
        # Análisis para obesidad
        elif any(palabra in motivo for palabra in ['obesidad', 'obesity', 'peso', 'weight']):
            preguntas.extend([
                "¿Cuál es su peso actual y altura?",
                "¿Cuál es su peso máximo y mínimo en los últimos años?",
                "¿Qué dietas ha intentado anteriormente?",
                "¿Cuál es su nivel de actividad física?",
                "¿Hay factores emocionales que afecten su alimentación?",
                "¿Qué alimentos consume más frecuentemente?",
                "¿Bebe alcohol o bebidas azucaradas?",
                "¿Hay antecedentes familiares de obesidad?",
                "¿Tiene problemas de sueño?",
                "¿Cuál es su objetivo de peso?"
            ])
        
        # Análisis para hipertensión
        elif any(palabra in motivo for palabra in ['hipertension', 'hypertension', 'presion']):
            preguntas.extend([
                "¿Cuál es su presión arterial actual?",
                "¿Qué medicamentos toma para la presión?",
                "¿Consume mucha sal en su dieta?",
                "¿Bebe alcohol regularmente?",
                "¿Realiza actividad física?",
                "¿Hay antecedentes familiares de hipertensión?",
                "¿Tiene otros factores de riesgo cardiovascular?",
                "¿Ha tenido episodios de presión alta?",
                "¿Qué tipo de dieta sigue actualmente?",
                "¿Cuál es su peso y altura?"
            ])
        
        # Análisis para desnutrición
        elif any(palabra in motivo for palabra in ['desnutricion', 'malnutrition']):
            preguntas.extend([
                "¿Cuál es su peso actual y altura?",
                "¿Ha perdido peso recientemente?",
                "¿Cuántas comidas hace al día?",
                "¿Qué alimentos puede tolerar?",
                "¿Hay problemas de masticación o deglución?",
                "¿Tiene apetito normal?",
                "¿Hay problemas digestivos?",
                "¿Qué medicamentos toma?",
                "¿Hay otros problemas médicos?",
                "¿Cuál es su nivel de actividad física?"
            ])
        
        # Preguntas generales de nutrición
        if not preguntas:
            preguntas.extend([
                "¿Cuál es su peso actual y altura?",
                "¿Qué tipo de dieta sigue actualmente?",
                "¿Cuántas comidas hace al día?",
                "¿Qué alimentos consume más frecuentemente?",
                "¿Hay alimentos que no puede tolerar?",
                "¿Realiza actividad física?",
                "¿Cuál es su objetivo nutricional?",
                "¿Hay otros problemas médicos?",
                "¿Qué medicamentos toma?",
                "¿Hay antecedentes familiares de problemas nutricionales?"
            ])
        
        return preguntas

    def _preguntas_psicologia(self, motivo: str) -> List[str]:
        """Preguntas específicas para Psicología"""
        preguntas = []
        
        # Análisis para ansiedad
        if any(palabra in motivo for palabra in ['ansiedad', 'anxiety', 'estres', 'stress']):
            preguntas.extend([
                "¿Cuándo comenzó a sentir ansiedad?",
                "¿Qué situaciones le provocan más ansiedad?",
                "¿Qué síntomas físicos experimenta?",
                "¿Cómo afecta la ansiedad su vida diaria?",
                "¿Ha tenido ataques de pánico?",
                "¿Hay pensamientos recurrentes que le preocupan?",
                "¿Cómo maneja actualmente la ansiedad?",
                "¿Ha recibido tratamiento psicológico anteriormente?",
                "¿Hay antecedentes familiares de ansiedad?",
                "¿Qué actividades le ayudan a relajarse?"
            ])
        
        # Análisis para depresión
        elif any(palabra in motivo for palabra in ['depresion', 'depression', 'tristeza']):
            preguntas.extend([
                "¿Cuándo comenzó a sentirse deprimido?",
                "¿Qué síntomas experimenta principalmente?",
                "¿Ha perdido interés en actividades que antes disfrutaba?",
                "¿Cómo está su apetito y sueño?",
                "¿Ha tenido pensamientos de muerte o suicidio?",
                "¿Hay factores estresantes recientes?",
                "¿Ha recibido tratamiento previo?",
                "¿Hay antecedentes familiares de depresión?",
                "¿Cómo afecta esto su trabajo y relaciones?",
                "¿Qué espera lograr con la terapia?"
            ])
        
        # Análisis para trastornos del sueño
        elif any(palabra in motivo for palabra in ['sueño', 'sleep', 'insomnio']):
            preguntas.extend([
                "¿Cuántas horas duerme por noche?",
                "¿Cuánto tiempo tarda en quedarse dormido?",
                "¿Se despierta frecuentemente durante la noche?",
                "¿Se siente descansado al despertar?",
                "¿Hay factores que afecten su sueño?",
                "¿Toma medicamentos para dormir?",
                "¿Qué rutina tiene antes de dormir?",
                "¿Hay problemas médicos que afecten el sueño?",
                "¿El problema del sueño afecta su día?",
                "¿Ha tenido problemas de sueño anteriormente?"
            ])
        
        # Análisis para trastornos de conducta (niños)
        elif any(palabra in motivo for palabra in ['conducta', 'behavior', 'nino', 'child']):
            preguntas.extend([
                "¿Cuándo comenzó a notar cambios en la conducta?",
                "¿Qué comportamientos específicos le preocupan?",
                "¿Cómo se comporta en la escuela?",
                "¿Hay problemas de atención o hiperactividad?",
                "¿Cómo interactúa con otros niños?",
                "¿Ha habido cambios recientes en la familia?",
                "¿Ha recibido evaluación psicológica anteriormente?",
                "¿Hay antecedentes familiares de problemas de conducta?",
                "¿Cómo maneja actualmente los problemas de conducta?",
                "¿Qué espera lograr con la terapia?"
            ])
        
        # Preguntas generales de psicología
        if not preguntas:
            preguntas.extend([
                "¿Cuándo comenzó el problema?",
                "¿Qué síntomas experimenta principalmente?",
                "¿Cómo afecta esto su vida diaria?",
                "¿Ha recibido tratamiento psicológico anteriormente?",
                "¿Hay factores estresantes recientes?",
                "¿Hay antecedentes familiares de problemas psicológicos?",
                "¿Qué espera lograr con la terapia?",
                "¿Cómo maneja actualmente el problema?",
                "¿Hay otros problemas médicos?",
                "¿Qué actividades le ayudan a sentirse mejor?"
            ])
        
        return preguntas

    def _preguntas_enfermeria(self, motivo: str) -> List[str]:
        """Preguntas específicas para Enfermería"""
        preguntas = []
        
        # Análisis para cuidados de heridas
        if any(palabra in motivo for palabra in ['herida', 'wound', 'curación']):
            preguntas.extend([
                "¿Cuándo se produjo la herida?",
                "¿Cómo se produjo la herida?",
                "¿Ha recibido tratamiento previo?",
                "¿Hay signos de infección (enrojecimiento, calor, dolor)?",
                "¿Qué medicamentos toma actualmente?",
                "¿Tiene diabetes u otros problemas médicos?",
                "¿Cómo está su higiene personal?",
                "¿Puede realizar el cuidado de la herida?",
                "¿Hay alergias a medicamentos o materiales?",
                "¿Cuál es su nivel de movilidad?"
            ])
        
        # Análisis para cuidados paliativos
        elif any(palabra in motivo for palabra in ['paliativo', 'palliative', 'terminal']):
            preguntas.extend([
                "¿Cuál es el diagnóstico principal?",
                "¿Qué síntomas experimenta principalmente?",
                "¿Cómo está su nivel de dolor?",
                "¿Qué medicamentos toma para el dolor?",
                "¿Cómo está su apetito y sueño?",
                "¿Qué apoyo familiar tiene?",
                "¿Cuál es su nivel de independencia?",
                "¿Qué actividades puede realizar?",
                "¿Hay preferencias sobre el cuidado?",
                "¿Cómo está su estado emocional?"
            ])
        
        # Análisis para educación del paciente
        elif any(palabra in motivo for palabra in ['educacion', 'education', 'paciente']):
            preguntas.extend([
                "¿Qué diagnóstico tiene?",
                "¿Qué medicamentos toma?",
                "¿Entiende su condición médica?",
                "¿Qué preguntas tiene sobre su tratamiento?",
                "¿Qué información necesita específicamente?",
                "¿Cómo prefiere recibir la información?",
                "¿Hay barreras de comunicación?",
                "¿Qué apoyo familiar tiene?",
                "¿Cuál es su nivel de alfabetización?",
                "¿Qué espera aprender?"
            ])
        
        # Preguntas generales de enfermería
        if not preguntas:
            preguntas.extend([
                "¿Cuál es su problema de salud principal?",
                "¿Qué síntomas experimenta?",
                "¿Qué medicamentos toma?",
                "¿Hay alergias conocidas?",
                "¿Cuál es su nivel de independencia?",
                "¿Qué apoyo familiar tiene?",
                "¿Cómo está su higiene personal?",
                "¿Cuál es su nivel de movilidad?",
                "¿Hay otros problemas médicos?",
                "¿Qué espera del cuidado de enfermería?"
            ])
        
        return preguntas

    def _preguntas_medicina_general(self, motivo: str) -> List[str]:
        """Preguntas específicas para Medicina General"""
        preguntas = []
        
        # Análisis para hipertensión
        if any(palabra in motivo for palabra in ['hipertension', 'hypertension', 'presion']):
            preguntas.extend([
                "¿Cuál es su presión arterial actual?",
                "¿Qué medicamentos toma para la presión?",
                "¿Consume mucha sal en su dieta?",
                "¿Bebe alcohol regularmente?",
                "¿Realiza actividad física?",
                "¿Hay antecedentes familiares de hipertensión?",
                "¿Tiene otros factores de riesgo cardiovascular?",
                "¿Ha tenido episodios de presión alta?",
                "¿Cuál es su peso y altura?",
                "¿Fuma o ha fumado?"
            ])
        
        # Análisis para diabetes
        elif any(palabra in motivo for palabra in ['diabetes', 'glucosa', 'glucose']):
            preguntas.extend([
                "¿Cuál es su nivel de glucosa en ayunas?",
                "¿Cuál es su hemoglobina glicosilada?",
                "¿Qué medicamentos toma para la diabetes?",
                "¿Ha tenido episodios de hipoglucemia?",
                "¿Cuál es su peso y altura?",
                "¿Realiza actividad física?",
                "¿Hay antecedentes familiares de diabetes?",
                "¿Ha tenido complicaciones de la diabetes?",
                "¿Cómo está su visión?",
                "¿Tiene problemas en los pies?"
            ])
        
        # Análisis para infecciones respiratorias
        elif any(palabra in motivo for palabra in ['respiratorio', 'respiratory', 'tos', 'cough']):
            preguntas.extend([
                "¿Cuándo comenzaron los síntomas?",
                "¿Qué síntomas experimenta?",
                "¿Hay fiebre?",
                "¿Hay dolor de garganta?",
                "¿Hay secreción nasal?",
                "¿La tos es seca o con flema?",
                "¿Qué medicamentos ha tomado?",
                "¿Ha tenido contacto con personas enfermas?",
                "¿Hay otros problemas médicos?",
                "¿Fuma o ha fumado?"
            ])
        
        # Análisis para dolor general
        elif any(palabra in motivo for palabra in ['dolor', 'pain']):
            preguntas.extend([
                "¿Cuándo comenzó el dolor?",
                "¿Dónde está localizado el dolor?",
                "¿Qué tipo de dolor es (punzante, sordo, etc.)?",
                "¿Qué lo agrava o alivia?",
                "¿El dolor es constante o intermitente?",
                "¿Hay otros síntomas asociados?",
                "¿Ha tenido lesiones recientes?",
                "¿Qué medicamentos toma?",
                "¿Hay antecedentes familiares de problemas similares?",
                "¿Cómo afecta esto su vida diaria?"
            ])
        
        # Preguntas generales de medicina
        if not preguntas:
            preguntas.extend([
                "¿Cuál es su problema de salud principal?",
                "¿Cuándo comenzaron los síntomas?",
                "¿Qué síntomas experimenta?",
                "¿Qué medicamentos toma?",
                "¿Hay alergias conocidas?",
                "¿Hay antecedentes familiares relevantes?",
                "¿Ha tenido problemas similares anteriormente?",
                "¿Cómo afecta esto su vida diaria?",
                "¿Hay otros problemas médicos?",
                "¿Qué espera del tratamiento?"
            ])
        
        return preguntas

    def _preguntas_urgencias(self, motivo: str) -> List[str]:
        """Preguntas específicas para Urgencias"""
        preguntas = []
        
        # Análisis para trauma
        if any(palabra in motivo for palabra in ['trauma', 'accidente', 'accident']):
            preguntas.extend([
                "¿Cuándo ocurrió el accidente?",
                "¿Cómo ocurrió el accidente?",
                "¿Hubo pérdida de conciencia?",
                "¿Hay dolor intenso en alguna zona?",
                "¿Hay sangrado activo?",
                "¿Puede mover todas las extremidades?",
                "¿Hay deformidad visible?",
                "¿Ha vomitado desde el accidente?",
                "¿Toma anticoagulantes?",
                "¿Hay otros problemas médicos?"
            ])
        
        # Análisis para dolor agudo
        elif any(palabra in motivo for palabra in ['dolor agudo', 'acute pain']):
            preguntas.extend([
                "¿Cuándo comenzó el dolor?",
                "¿Dónde está localizado el dolor?",
                "¿Qué tipo de dolor es?",
                "¿Hay otros síntomas asociados?",
                "¿Ha tenido problemas similares anteriormente?",
                "¿Qué medicamentos toma?",
                "¿Hay antecedentes médicos relevantes?",
                "¿El dolor es constante o intermitente?",
                "¿Qué lo agrava o alivia?",
                "¿Cómo afecta esto su capacidad funcional?"
            ])
        
        # Análisis para problemas cardíacos
        elif any(palabra in motivo for palabra in ['cardiaco', 'cardiac', 'corazon', 'heart']):
            preguntas.extend([
                "¿Cuándo comenzaron los síntomas?",
                "¿Qué síntomas experimenta?",
                "¿El dolor se irradia hacia el brazo o mandíbula?",
                "¿Hay falta de aire?",
                "¿Hay sudoración fría?",
                "¿Ha tenido problemas cardíacos anteriormente?",
                "¿Toma medicamentos para el corazón?",
                "¿Hay antecedentes familiares de problemas cardíacos?",
                "¿Fuma o tiene otros factores de riesgo?",
                "¿El dolor es constante o intermitente?"
            ])
        
        # Preguntas generales de urgencias
        if not preguntas:
            preguntas.extend([
                "¿Cuándo comenzaron los síntomas?",
                "¿Qué síntomas experimenta?",
                "¿Hay dolor intenso?",
                "¿Hay sangrado activo?",
                "¿Ha perdido la conciencia?",
                "¿Puede respirar normalmente?",
                "¿Qué medicamentos toma?",
                "¿Hay alergias conocidas?",
                "¿Ha tenido problemas similares anteriormente?",
                "¿Hay otros problemas médicos?"
            ])
        
        return preguntas

    def _preguntas_terapia_ocupacional(self, motivo: str) -> List[str]:
        """Preguntas específicas para Terapia Ocupacional"""
        preguntas = []
        
        # Análisis para actividades de la vida diaria
        if any(palabra in motivo for palabra in ['actividades', 'activities', 'vida diaria']):
            preguntas.extend([
                "¿Qué actividades de la vida diaria le resultan difíciles?",
                "¿Puede vestirse independientemente?",
                "¿Puede bañarse sin ayuda?",
                "¿Puede preparar sus comidas?",
                "¿Puede realizar las tareas domésticas?",
                "¿Puede manejar el dinero y las compras?",
                "¿Puede conducir o usar transporte público?",
                "¿Qué adaptaciones usa actualmente?",
                "¿Cuál es su nivel de independencia?",
                "¿Qué actividades le gustaría recuperar?"
            ])
        
        # Análisis para rehabilitación funcional
        elif any(palabra in motivo for palabra in ['funcional', 'functional', 'rehabilitacion']):
            preguntas.extend([
                "¿Cuál es su diagnóstico principal?",
                "¿Cuándo ocurrió la lesión o problema?",
                "¿Qué actividades le resultan difíciles?",
                "¿Cuál es su nivel de movilidad?",
                "¿Qué adaptaciones usa actualmente?",
                "¿Cuál es su objetivo de rehabilitación?",
                "¿Qué actividades le gustaría recuperar?",
                "¿Cuál es su entorno de vivienda?",
                "¿Qué apoyo familiar tiene?",
                "¿Cuál es su nivel de independencia previo?"
            ])
        
        # Análisis para problemas de movilidad
        elif any(palabra in motivo for palabra in ['movilidad', 'mobility', 'movimiento']):
            preguntas.extend([
                "¿Qué movimientos le resultan difíciles?",
                "¿Puede caminar independientemente?",
                "¿Usa algún dispositivo de asistencia?",
                "¿Cuál es su nivel de equilibrio?",
                "¿Ha tenido caídas recientes?",
                "¿Qué actividades le gustaría realizar?",
                "¿Cuál es su entorno de vivienda?",
                "¿Qué adaptaciones necesita?",
                "¿Cuál es su objetivo de movilidad?",
                "¿Qué apoyo tiene disponible?"
            ])
        
        # Preguntas generales de terapia ocupacional
        if not preguntas:
            preguntas.extend([
                "¿Cuál es su problema principal?",
                "¿Qué actividades le resultan difíciles?",
                "¿Cuál es su nivel de independencia?",
                "¿Qué adaptaciones usa actualmente?",
                "¿Cuál es su entorno de vivienda?",
                "¿Qué apoyo familiar tiene?",
                "¿Cuál es su objetivo de terapia?",
                "¿Qué actividades le gustaría recuperar?",
                "¿Ha recibido terapia ocupacional anteriormente?",
                "¿Cómo afecta esto su calidad de vida?"
            ])
        
        return preguntas

    def _preguntas_generales(self, motivo: str) -> List[str]:
        """Preguntas generales para cualquier tipo de atención"""
        return [
            "¿Cuándo comenzó el problema?",
            "¿Qué síntomas experimenta?",
            "¿Cómo afecta esto su vida diaria?",
            "¿Ha recibido tratamiento anteriormente?",
            "¿Qué medicamentos toma?",
            "¿Hay otros problemas médicos?",
            "¿Cuál es su objetivo de tratamiento?",
            "¿Qué espera lograr con la atención?",
            "¿Hay factores que agraven o alivien el problema?",
            "¿Cuál es su nivel de independencia?"
        ]



# Función de utilidad para convertir a formato compatible con Copilot Health
def convertir_a_formato_copilot(tratamientos_cientificos: List[TratamientoCientifico], plan_intervencion: PlanIntervencion = None) -> List[Dict]:
    """
    Convierte tratamientos científicos al formato esperado por Copilot Health
    Incluye planes de intervención específicos si están disponibles
    """
    planes = []
    
    # Si hay un plan de intervención específico, agregarlo primero
    if plan_intervencion:
        plan_intervencion_dict = {
            'titulo': plan_intervencion.titulo,
            'descripcion': plan_intervencion.descripcion,
            'evidencia_cientifica': plan_intervencion.evidencia_cientifica,
            'doi_referencia': plan_intervencion.doi_referencia,
            'nivel_evidencia': plan_intervencion.nivel_evidencia,
            'contraindicaciones': plan_intervencion.contraindicaciones,
            'tecnicas_especificas': plan_intervencion.tecnicas_especificas,
            'aplicaciones_practicas': plan_intervencion.aplicaciones_practicas,
            'masajes_tecnicas': plan_intervencion.masajes_tecnicas,
            'ejercicios_especificos': plan_intervencion.ejercicios_especificos,
            'protocolo_tratamiento': plan_intervencion.protocolo_tratamiento,
            'frecuencia_sesiones': plan_intervencion.frecuencia_sesiones,
            'duracion_tratamiento': plan_intervencion.duracion_tratamiento,
            'tipo': 'plan_intervencion_especifico'
        }
        planes.append(plan_intervencion_dict)
    
    # Agregar tratamientos científicos tradicionales
    for tratamiento in tratamientos_cientificos:
        # Determinar nivel de evidencia basado en la fuente
        nivel_evidencia = 'A' if 'PubMed' in tratamiento.fuente else 'B'
        
        # Generar contraindicaciones basadas en el tipo de tratamiento
        contraindicaciones = []
        if 'fisioterapia' in tratamiento.titulo.lower() or 'physical therapy' in tratamiento.titulo.lower():
            contraindicaciones = ['Fracturas inestables', 'Infección activa']
        elif 'fonoaudiologia' in tratamiento.titulo.lower() or 'speech therapy' in tratamiento.titulo.lower():
            contraindicaciones = ['Aspiración severa']
        elif 'psicologia' in tratamiento.titulo.lower() or 'psychology' in tratamiento.titulo.lower():
            contraindicaciones = ['Psicosis activa', 'Riesgo suicida']
        
        # Crear lista de estudios basados
        estudios_basados = []
        if tratamiento.titulo and tratamiento.titulo != 'Sin título':
            estudios_basados.append({
                'titulo': tratamiento.titulo,
                'autores': ', '.join(tratamiento.autores) if tratamiento.autores else 'Autores no disponibles',
                'doi': tratamiento.doi,
                'fecha': tratamiento.fecha_publicacion,
                'fuente': tratamiento.fuente,
                'resumen': tratamiento.resumen[:200] + "..." if len(tratamiento.resumen) > 200 else tratamiento.resumen
            })
        
        # Procesar DOI correctamente
        doi_referencia = tratamiento.doi
        if doi_referencia and doi_referencia.strip():
            # Limpiar DOI de caracteres extraños
            doi_referencia = doi_referencia.strip()
            if doi_referencia.startswith('10.'):
                # DOI válido
                pass
            elif 'doi.org/' in doi_referencia:
                # Extraer DOI de URL
                doi_referencia = doi_referencia.split('doi.org/')[-1]
            else:
                # DOI inválido o vacío
                doi_referencia = None
        else:
            doi_referencia = None
        
        plan = {
            'titulo': tratamiento.titulo if tratamiento.titulo != 'Sin título' else 'Tratamiento basado en evidencia científica',
            'descripcion': tratamiento.descripcion,
            'evidencia_cientifica': f"{tratamiento.fuente} - {tratamiento.tipo_evidencia}",
            'doi_referencia': doi_referencia,
            'año_publicacion': tratamiento.año_publicacion,
            'fecha_publicacion': tratamiento.fecha_publicacion,
            'nivel_evidencia': nivel_evidencia,
            'contraindicaciones': contraindicaciones,
            'estudios_basados': estudios_basados,
            'tipo': 'tratamiento_cientifico'
        }
        planes.append(plan)
    
    return planes

def convertir_preguntas_a_formato_copilot(preguntas_cientificas: List[PreguntaCientifica]) -> List[str]:
    """
    Convierte preguntas científicas al formato esperado por Copilot Health
    """
    return [pregunta.pregunta for pregunta in preguntas_cientificas]

def generar_planificacion_tratamiento_completa(
    motivo_atencion: str,
    tipo_atencion: str,
    evaluacion_observaciones: str,
    estudios_cientificos: List[TratamientoCientifico]
) -> Dict:
    """
    Genera una planificación completa de tratamiento basada en múltiples fuentes
    """
    planificacion = {
        'resumen_clinico': '',
        'objetivos_tratamiento': [],
        'intervenciones_especificas': [],
        'cronograma_tratamiento': [],
        'criterios_evaluacion': [],
        'estudios_basados': [],
        'aclaracion_legal': 'Estas sugerencias son generadas por inteligencia artificial con base en evidencia científica actualizada. La decisión final recae en el juicio clínico del profesional tratante. Copilot Health es una herramienta de asistencia y no reemplaza la evaluación médica profesional.'
    }
    
    # Generar resumen clínico
    planificacion['resumen_clinico'] = f"""
    BASADO EN:
    • Motivo de atención: {motivo_atencion}
    • Tipo de atención: {tipo_atencion}
    • Evaluación/Observaciones: {evaluacion_observaciones}
    • Estudios científicos: {len(estudios_cientificos)} estudios de 2020-2025
    """
    
    # Generar objetivos basados en el tipo de atención
    if 'fisioterapia' in tipo_atencion.lower() or 'kinesiologia' in tipo_atencion.lower():
        planificacion['objetivos_tratamiento'] = [
            "Reducir dolor y mejorar función",
            "Aumentar rango de movimiento",
            "Fortalecer musculatura afectada",
            "Mejorar calidad de vida"
        ]
    elif 'fonoaudiologia' in tipo_atencion.lower():
        planificacion['objetivos_tratamiento'] = [
            "Mejorar habilidades comunicativas",
            "Optimizar función deglutoria",
            "Desarrollar estrategias compensatorias",
            "Prevenir complicaciones"
        ]
    elif 'psicologia' in tipo_atencion.lower():
        planificacion['objetivos_tratamiento'] = [
            "Reducir síntomas de ansiedad/depresión",
            "Desarrollar estrategias de afrontamiento",
            "Mejorar funcionamiento social",
            "Prevenir recaídas"
        ]
    else:
        planificacion['objetivos_tratamiento'] = [
            "Aliviar síntomas principales",
            "Mejorar función general",
            "Prevenir complicaciones",
            "Optimizar calidad de vida"
        ]
    
    # Generar intervenciones específicas basadas en estudios
    for estudio in estudios_cientificos[:3]:  # Usar máximo 3 estudios
        planificacion['intervenciones_especificas'].append({
            'titulo': estudio.titulo,
            'descripcion': estudio.descripcion,
            'evidencia': f"{estudio.fuente} - {estudio.tipo_evidencia}",
            'doi': estudio.doi,
            'fecha': estudio.fecha_publicacion
        })
    
    # Generar cronograma de tratamiento
    planificacion['cronograma_tratamiento'] = [
        "Fase 1 (Semanas 1-2): Evaluación inicial y establecimiento de objetivos",
        "Fase 2 (Semanas 3-6): Intervención intensiva basada en evidencia",
        "Fase 3 (Semanas 7-10): Consolidación y generalización",
        "Fase 4 (Semanas 11-12): Evaluación de resultados y plan de seguimiento"
    ]
    
    # Generar criterios de evaluación
    planificacion['criterios_evaluacion'] = [
        "Evaluación continua de síntomas",
        "Medición de progreso funcional",
        "Satisfacción del paciente",
        "Cumplimiento del tratamiento"
    ]
    
    # Agregar información de estudios
    for estudio in estudios_cientificos:
        planificacion['estudios_basados'].append({
            'titulo': estudio.titulo,
            'autores': ', '.join(estudio.autores),
            'doi': estudio.doi,
            'fecha': estudio.fecha_publicacion,
            'fuente': estudio.fuente,
            'resumen': estudio.resumen[:200] + "..." if len(estudio.resumen) > 200 else estudio.resumen
        })
    
    return planificacion

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancia
    apis = MedicalAPIsIntegration()
    
    # Probar búsqueda
    print("🔍 Probando integración con APIs médicas...")
    
    # Buscar tratamientos para dolor lumbar
    resultados = apis.obtener_tratamientos_completos("dolor lumbar", "fisioterapia")
    
    print(f"\n📊 Resultados obtenidos:")
    print(f"   PubMed: {len(resultados['tratamientos_pubmed'])} tratamientos")
    print(f"   Europe PMC: {len(resultados['tratamientos_europepmc'])} tratamientos")
    print(f"   Preguntas científicas: {len(resultados['preguntas_cientificas'])} preguntas")
    
    # Mostrar ejemplo de tratamiento
    if resultados['tratamientos_pubmed']:
        tratamiento = resultados['tratamientos_pubmed'][0]
        print(f"\n📋 Ejemplo de tratamiento encontrado:")
        print(f"   Título: {tratamiento.titulo}")
        print(f"   DOI: {tratamiento.doi}")
        print(f"   Fuente: {tratamiento.fuente}")
    
    # Mostrar ejemplo de pregunta
    if resultados['preguntas_cientificas']:
        pregunta = resultados['preguntas_cientificas'][0]
        print(f"\n❓ Ejemplo de pregunta científica:")
        print(f"   Pregunta: {pregunta.pregunta}")
        print(f"   Contexto: {pregunta.contexto}")
        print(f"   Fuente: {pregunta.fuente}") 