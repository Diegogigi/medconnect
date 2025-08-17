#!/usr/bin/env python3
"""
Analizador de Patrones Clínicos Mejorado
Identifica palabras clave, patologías y escalas de evaluación específicas
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class PalabraClave:
    """Representa una palabra clave identificada en el motivo de consulta"""
    palabra: str
    categoria: str
    intensidad: float  # 0.0 a 1.0
    patologias_asociadas: List[str]
    escalas_evaluacion: List[str]
    preguntas_sugeridas: List[str]

@dataclass
class PatologiaIdentificada:
    """Representa una patología identificada"""
    nombre: str
    confianza: float  # 0.0 a 1.0
    sintomas_asociados: List[str]
    escalas_recomendadas: List[str]
    terminos_busqueda: List[str]

@dataclass
class EscalaEvaluacion:
    """Representa una escala de evaluación recomendada"""
    nombre: str
    descripcion: str
    aplicacion: str
    puntuacion: str
    preguntas: List[str]

@dataclass
class AnalisisMejorado:
    """Resultado del análisis mejorado del motivo de consulta"""
    palabras_clave: List[PalabraClave]
    patologias_identificadas: List[PatologiaIdentificada]
    escalas_recomendadas: List[EscalaEvaluacion]
    terminos_busqueda_mejorados: List[str]
    preguntas_evaluacion: List[str]
    confianza_global: float

class ClinicalPatternAnalyzer:
    """Analizador mejorado de patrones clínicos"""
    
    def __init__(self):
        self.palabras_clave_db = self._load_palabras_clave()
        self.patologias_db = self._load_patologias()
        self.escalas_db = self._load_escalas_evaluacion()
        self.sintomas_db = self._load_sintomas()
        
    def _load_palabras_clave(self) -> Dict[str, Dict]:
        """Carga la base de datos de palabras clave"""
        return {
            # DOLOR
            'dolor': {
                'categoria': 'sintoma_principal',
                'intensidad': 0.9,
                'patologias_asociadas': ['dolor_agudo', 'dolor_cronico', 'inflamacion'],
                'escalas_evaluacion': ['EVA', 'Escala_Numerica', 'Escala_Verbal'],
                'preguntas_sugeridas': [
                    '¿En qué escala de 0 a 10 calificaría el dolor?',
                    '¿El dolor es constante o intermitente?',
                    '¿Qué factores agravan el dolor?',
                    '¿Qué factores alivian el dolor?'
                ]
            },
            'molestia': {
                'categoria': 'sintoma_secundario',
                'intensidad': 0.6,
                'patologias_asociadas': ['disconfort', 'irritacion'],
                'escalas_evaluacion': ['EVA', 'Escala_Verbal'],
                'preguntas_sugeridas': [
                    '¿Cómo describiría la molestia?',
                    '¿Es tolerable o interfiere con sus actividades?'
                ]
            },
            'ardor': {
                'categoria': 'sintoma_especifico',
                'intensidad': 0.8,
                'patologias_asociadas': ['quemadura', 'irritacion', 'inflamacion'],
                'escalas_evaluacion': ['EVA', 'Escala_Verbal'],
                'preguntas_sugeridas': [
                    '¿En qué escala de 0 a 10 calificaría el ardor?',
                    '¿El ardor es superficial o profundo?'
                ]
            },
            
            # MOVIMIENTO
            'rigidez': {
                'categoria': 'sintoma_movimiento',
                'intensidad': 0.7,
                'patologias_asociadas': ['artritis', 'artrosis', 'contractura'],
                'escalas_evaluacion': ['Escala_Rigidez', 'EVA'],
                'preguntas_sugeridas': [
                    '¿La rigidez es mayor por la mañana?',
                    '¿Cuánto tiempo dura la rigidez?',
                    '¿Mejora con el movimiento?'
                ]
            },
            'limitacion': {
                'categoria': 'sintoma_funcional',
                'intensidad': 0.8,
                'patologias_asociadas': ['disfuncion', 'debilidad', 'atrofia'],
                'escalas_evaluacion': ['Escala_Funcional', 'Escala_Discapacidad'],
                'preguntas_sugeridas': [
                    '¿Qué actividades no puede realizar?',
                    '¿Cómo afecta su vida diaria?',
                    '¿Ha notado pérdida de fuerza?'
                ]
            },
            'debilidad': {
                'categoria': 'sintoma_muscular',
                'intensidad': 0.8,
                'patologias_asociadas': ['atrofia', 'lesion_nerviosa', 'miopatia'],
                'escalas_evaluacion': ['Escala_Fuerza', 'Escala_Funcional'],
                'preguntas_sugeridas': [
                    '¿En qué escala de 0 a 5 calificaría la fuerza?',
                    '¿La debilidad es progresiva?',
                    '¿Afecta ambos lados?'
                ]
            },
            
            # SENSACIONES
            'hormigueo': {
                'categoria': 'sintoma_neurologico',
                'intensidad': 0.6,
                'patologias_asociadas': ['compresion_nerviosa', 'neuropatia'],
                'escalas_evaluacion': ['Escala_Sensibilidad', 'EVA'],
                'preguntas_sugeridas': [
                    '¿El hormigueo es constante o intermitente?',
                    '¿Se agrava con ciertas posiciones?',
                    '¿Acompaña a otros síntomas?'
                ]
            },
            'entumecimiento': {
                'categoria': 'sintoma_neurologico',
                'intensidad': 0.7,
                'patologias_asociadas': ['compresion_nerviosa', 'neuropatia'],
                'escalas_evaluacion': ['Escala_Sensibilidad', 'EVA'],
                'preguntas_sugeridas': [
                    '¿El entumecimiento es completo o parcial?',
                    '¿Afecta la sensibilidad al tacto?',
                    '¿Se agrava con el movimiento?'
                ]
            },
            
            # INFLAMACION
            'inflamacion': {
                'categoria': 'signo_inflamatorio',
                'intensidad': 0.8,
                'patologias_asociadas': ['artritis', 'bursitis', 'tendinitis'],
                'escalas_evaluacion': ['Escala_Inflamacion', 'EVA'],
                'preguntas_sugeridas': [
                    '¿La inflamación es visible?',
                    '¿Está caliente al tacto?',
                    '¿Aumenta con el uso?'
                ]
            },
            'hinchazon': {
                'categoria': 'signo_inflamatorio',
                'intensidad': 0.7,
                'patologias_asociadas': ['edema', 'inflamacion', 'trauma'],
                'escalas_evaluacion': ['Escala_Edema', 'EVA'],
                'preguntas_sugeridas': [
                    '¿La hinchazón es simétrica?',
                    '¿Mejora con la elevación?',
                    '¿Está asociada a trauma?'
                ]
            }
        }
    
    def _load_patologias(self) -> Dict[str, Dict]:
        """Carga la base de datos de patologías"""
        return {
            'dolor_agudo': {
                'sintomas': ['dolor', 'molestia', 'ardor'],
                'escalas': ['EVA', 'Escala_Numerica'],
                'terminos_busqueda': ['acute pain', 'pain management', 'analgesia']
            },
            'dolor_cronico': {
                'sintomas': ['dolor', 'molestia', 'rigidez'],
                'escalas': ['EVA', 'Escala_Dolor_Cronico'],
                'terminos_busqueda': ['chronic pain', 'pain management', 'rehabilitation']
            },
            'artritis': {
                'sintomas': ['dolor', 'rigidez', 'inflamacion'],
                'escalas': ['EVA', 'Escala_Artritis', 'Escala_Rigidez'],
                'terminos_busqueda': ['arthritis', 'joint inflammation', 'rheumatoid arthritis']
            },
            'artrosis': {
                'sintomas': ['dolor', 'rigidez', 'limitacion'],
                'escalas': ['EVA', 'Escala_Artrosis', 'Escala_Funcional'],
                'terminos_busqueda': ['osteoarthritis', 'joint degeneration', 'cartilage damage']
            },
            'tendinitis': {
                'sintomas': ['dolor', 'inflamacion', 'limitacion'],
                'escalas': ['EVA', 'Escala_Tendinitis'],
                'terminos_busqueda': ['tendinitis', 'tendon inflammation', 'overuse injury']
            },
            'bursitis': {
                'sintomas': ['dolor', 'inflamacion', 'hinchazon'],
                'escalas': ['EVA', 'Escala_Bursitis'],
                'terminos_busqueda': ['bursitis', 'bursa inflammation', 'joint swelling']
            },
            'compresion_nerviosa': {
                'sintomas': ['dolor', 'hormigueo', 'entumecimiento'],
                'escalas': ['EVA', 'Escala_Sensibilidad'],
                'terminos_busqueda': ['nerve compression', 'radiculopathy', 'nerve entrapment']
            },
            'atrofia_muscular': {
                'sintomas': ['debilidad', 'limitacion', 'dolor'],
                'escalas': ['Escala_Fuerza', 'Escala_Funcional'],
                'terminos_busqueda': ['muscle atrophy', 'muscle weakness', 'disuse atrophy']
            }
        }
    
    def _load_escalas_evaluacion(self) -> Dict[str, Dict]:
        """Carga la base de datos de escalas de evaluación"""
        return {
            'EVA': {
                'nombre': 'Escala Visual Analógica',
                'descripcion': 'Escala de 0 a 10 para evaluar intensidad del dolor',
                'aplicacion': 'Dolor agudo y crónico',
                'puntuacion': '0-10',
                'preguntas': [
                    '¿En qué escala de 0 a 10 calificaría el dolor?',
                    '0 = Sin dolor, 10 = Dolor máximo imaginable'
                ]
            },
            'Escala_Numerica': {
                'nombre': 'Escala Numérica del Dolor',
                'descripcion': 'Escala numérica de 0 a 10',
                'aplicacion': 'Dolor en general',
                'puntuacion': '0-10',
                'preguntas': [
                    '¿En qué escala de 0 a 10 calificaría el dolor?',
                    '0 = Sin dolor, 10 = Dolor máximo'
                ]
            },
            'Escala_Verbal': {
                'nombre': 'Escala Verbal del Dolor',
                'descripcion': 'Descripción verbal del dolor',
                'aplicacion': 'Dolor y molestias',
                'puntuacion': 'Leve/Moderado/Severo',
                'preguntas': [
                    '¿Cómo describiría el dolor?',
                    'Leve, Moderado o Severo'
                ]
            },
            'Escala_Funcional': {
                'nombre': 'Escala Funcional',
                'descripcion': 'Evaluación de la capacidad funcional',
                'aplicacion': 'Limitaciones de movimiento',
                'puntuacion': '0-100%',
                'preguntas': [
                    '¿Qué porcentaje de su función normal tiene?',
                    '¿Qué actividades no puede realizar?'
                ]
            },
            'Escala_Fuerza': {
                'nombre': 'Escala de Fuerza Muscular',
                'descripcion': 'Evaluación de la fuerza muscular',
                'aplicacion': 'Debilidad muscular',
                'puntuacion': '0-5',
                'preguntas': [
                    '¿En qué escala de 0 a 5 calificaría la fuerza?',
                    '0 = Sin contracción, 5 = Fuerza normal'
                ]
            },
            'Escala_Sensibilidad': {
                'nombre': 'Escala de Sensibilidad',
                'descripcion': 'Evaluación de la sensibilidad',
                'aplicacion': 'Alteraciones sensoriales',
                'puntuacion': 'Normal/Disminuida/Ausente',
                'preguntas': [
                    '¿Cómo está la sensibilidad?',
                    'Normal, Disminuida o Ausente'
                ]
            },
            'Escala_Inflamacion': {
                'nombre': 'Escala de Inflamación',
                'descripcion': 'Evaluación de signos inflamatorios',
                'aplicacion': 'Procesos inflamatorios',
                'puntuacion': 'Leve/Moderada/Severa',
                'preguntas': [
                    '¿Cómo está la inflamación?',
                    '¿Está caliente al tacto?'
                ]
            }
        }
    
    def _load_sintomas(self) -> Dict[str, List[str]]:
        """Carga la base de datos de síntomas por región anatómica"""
        return {
            'rodilla': {
                'sintomas_comunes': ['dolor', 'rigidez', 'inflamacion', 'limitacion'],
                'patologias_comunes': ['artritis', 'artrosis', 'tendinitis', 'bursitis'],
                'escalas_especificas': ['EVA', 'Escala_Funcional_Rodilla', 'Escala_Artritis']
            },
            'hombro': {
                'sintomas_comunes': ['dolor', 'limitacion', 'rigidez', 'debilidad'],
                'patologias_comunes': ['tendinitis', 'bursitis', 'artritis'],
                'escalas_especificas': ['EVA', 'Escala_Funcional_Hombro']
            },
            'columna': {
                'sintomas_comunes': ['dolor', 'rigidez', 'hormigueo', 'entumecimiento'],
                'patologias_comunes': ['compresion_nerviosa', 'artritis', 'hernia'],
                'escalas_especificas': ['EVA', 'Escala_Dolor_Columna', 'Escala_Sensibilidad']
            },
            'cadera': {
                'sintomas_comunes': ['dolor', 'rigidez', 'limitacion', 'debilidad'],
                'patologias_comunes': ['artritis', 'artrosis', 'bursitis'],
                'escalas_especificas': ['EVA', 'Escala_Funcional_Cadera']
            },
            'tobillo': {
                'sintomas_comunes': ['dolor', 'inflamacion', 'limitacion', 'inestabilidad'],
                'patologias_comunes': ['esguince', 'tendinitis', 'artritis'],
                'escalas_especificas': ['EVA', 'Escala_Funcional_Tobillo']
            }
        }
    
    def identificar_palabras_clave(self, motivo_consulta: str) -> List[PalabraClave]:
        """Identifica palabras clave en el motivo de consulta"""
        palabras_clave_encontradas = []
        motivo_lower = motivo_consulta.lower()
        
        # Primero identificar la región anatómica
        region_anatomica = self.identificar_region_anatomica(motivo_consulta)
        
        for palabra, info in self.palabras_clave_db.items():
            if palabra in motivo_lower:
                # Calcular intensidad basada en contexto
                intensidad = self._calcular_intensidad_palabra(palabra, motivo_lower)
                
                # Mejorar las patologías asociadas basadas en la región anatómica
                patologias_asociadas = info['patologias_asociadas'].copy()
                
                # Agregar patologías específicas por región
                if region_anatomica:
                    if region_anatomica == 'rodilla' and palabra == 'dolor':
                        patologias_asociadas.extend(['meniscopatia', 'ligamentopatia', 'condromalacia'])
                    elif region_anatomica == 'hombro' and palabra == 'dolor':
                        patologias_asociadas.extend(['impingement', 'rotator_cuff_tear', 'frozen_shoulder'])
                    elif region_anatomica == 'columna' and palabra == 'dolor':
                        patologias_asociadas.extend(['hernia_discal', 'estenosis', 'espondilosis'])
                    elif region_anatomica == 'tobillo' and palabra == 'dolor':
                        patologias_asociadas.extend(['esguince', 'tendinitis', 'fractura'])
                    elif region_anatomica == 'codo' and palabra == 'dolor':
                        patologias_asociadas.extend(['epicondilitis', 'epitrocleitis', 'bursitis'])
                    elif region_anatomica == 'muñeca' and palabra == 'dolor':
                        patologias_asociadas.extend(['sindrome_tunel_carpiano', 'tendinitis', 'artritis'])
                
                palabra_clave = PalabraClave(
                    palabra=palabra,
                    categoria=info['categoria'],
                    intensidad=intensidad,
                    patologias_asociadas=patologias_asociadas,
                    escalas_evaluacion=info['escalas_evaluacion'],
                    preguntas_sugeridas=info['preguntas_sugeridas']
                )
                palabras_clave_encontradas.append(palabra_clave)
        
        return palabras_clave_encontradas
    
    def _calcular_intensidad_palabra(self, palabra: str, texto: str) -> float:
        """Calcula la intensidad de una palabra clave basada en el contexto"""
        base_intensidad = self.palabras_clave_db[palabra]['intensidad']
        
        # Modificadores de intensidad
        modificadores = {
            'muy': 1.2,
            'mucho': 1.2,
            'intenso': 1.3,
            'severo': 1.3,
            'leve': 0.7,
            'poco': 0.7,
            'ligero': 0.6
        }
        
        # Buscar modificadores cerca de la palabra
        for modificador, factor in modificadores.items():
            if modificador in texto and abs(texto.find(modificador) - texto.find(palabra)) < 10:
                base_intensidad *= factor
                break
        
        return min(base_intensidad, 1.0)
    
    def identificar_patologias(self, palabras_clave: List[PalabraClave]) -> List[PatologiaIdentificada]:
        """Identifica patologías basadas en las palabras clave encontradas"""
        patologias_identificadas = []
        
        for palabra_clave in palabras_clave:
            for patologia_nombre in palabra_clave.patologias_asociadas:
                if patologia_nombre in self.patologias_db:
                    patologia_info = self.patologias_db[patologia_nombre]
                    
                    # Calcular confianza basada en síntomas coincidentes
                    sintomas_coincidentes = sum(1 for sintoma in patologia_info['sintomas'] 
                                              if sintoma in [pc.palabra for pc in palabras_clave])
                    confianza = min(sintomas_coincidentes / len(patologia_info['sintomas']), 1.0)
                    
                    if confianza > 0.3:  # Umbral mínimo de confianza
                        patologia = PatologiaIdentificada(
                            nombre=patologia_nombre,
                            confianza=confianza,
                            sintomas_asociados=patologia_info['sintomas'],
                            escalas_recomendadas=patologia_info['escalas'],
                            terminos_busqueda=patologia_info['terminos_busqueda']
                        )
                        patologias_identificadas.append(patologia)
        
        # Eliminar duplicados y ordenar por confianza
        patologias_unicas = {}
        for patologia in patologias_identificadas:
            if patologia.nombre not in patologias_unicas or patologia.confianza > patologias_unicas[patologia.nombre].confianza:
                patologias_unicas[patologia.nombre] = patologia
        
        return sorted(patologias_unicas.values(), key=lambda x: x.confianza, reverse=True)
    
    def identificar_escalas_evaluacion(self, palabras_clave: List[PalabraClave], 
                                      region_anatomica: str = None) -> List[EscalaEvaluacion]:
        """Identifica escalas de evaluación recomendadas"""
        escalas_recomendadas = []
        escalas_identificadas = set()
        
        # Escalas basadas en palabras clave
        for palabra_clave in palabras_clave:
            for escala_nombre in palabra_clave.escalas_evaluacion:
                if escala_nombre in self.escalas_db and escala_nombre not in escalas_identificadas:
                    escala_info = self.escalas_db[escala_nombre]
                    escala = EscalaEvaluacion(
                        nombre=escala_nombre,
                        descripcion=escala_info['descripcion'],
                        aplicacion=escala_info['aplicacion'],
                        puntuacion=escala_info['puntuacion'],
                        preguntas=escala_info['preguntas']
                    )
                    escalas_recomendadas.append(escala)
                    escalas_identificadas.add(escala_nombre)
        
        # Escalas específicas por región anatómica
        if region_anatomica and region_anatomica in self.sintomas_db:
            for escala_nombre in self.sintomas_db[region_anatomica]['escalas_especificas']:
                if escala_nombre in self.escalas_db and escala_nombre not in escalas_identificadas:
                    escala_info = self.escalas_db[escala_nombre]
                    escala = EscalaEvaluacion(
                        nombre=escala_nombre,
                        descripcion=escala_info['descripcion'],
                        aplicacion=escala_info['aplicacion'],
                        puntuacion=escala_info['puntuacion'],
                        preguntas=escala_info['preguntas']
                    )
                    escalas_recomendadas.append(escala)
                    escalas_identificadas.add(escala_nombre)
        
        return escalas_recomendadas
    
    def generar_terminos_busqueda_mejorados(self, palabras_clave: List[PalabraClave], 
                                           patologias: List[PatologiaIdentificada],
                                           region_anatomica: str = None) -> List[str]:
        """Genera términos de búsqueda mejorados basados en el análisis"""
        terminos = set()
        
        # Términos de palabras clave
        for palabra_clave in palabras_clave:
            terminos.add(palabra_clave.palabra)
            terminos.add(f"{palabra_clave.palabra} management")
            terminos.add(f"{palabra_clave.palabra} treatment")
        
        # Términos de patologías
        for patologia in patologias:
            terminos.update(patologia.terminos_busqueda)
        
        # Términos específicos por región anatómica
        if region_anatomica:
            terminos.add(region_anatomica)
            terminos.add(f"{region_anatomica} pain")
            terminos.add(f"{region_anatomica} rehabilitation")
            terminos.add(f"{region_anatomica} therapy")
            terminos.add(f"{region_anatomica} injury")
            terminos.add(f"{region_anatomica} condition")
            
            # Términos específicos por región
            if region_anatomica == 'rodilla':
                terminos.update(['knee pain', 'knee injury', 'patellar', 'meniscus', 'ACL', 'PCL'])
            elif region_anatomica == 'hombro':
                terminos.update(['shoulder pain', 'rotator cuff', 'impingement', 'frozen shoulder'])
            elif region_anatomica == 'columna':
                terminos.update(['back pain', 'spinal', 'herniated disc', 'sciatica', 'lumbar'])
            elif region_anatomica == 'cadera':
                terminos.update(['hip pain', 'hip replacement', 'bursitis', 'labral tear'])
            elif region_anatomica == 'tobillo':
                terminos.update(['ankle pain', 'sprain', 'tendon', 'ligament'])
            elif region_anatomica == 'codo':
                terminos.update(['elbow pain', 'tennis elbow', 'golfer elbow', 'epicondylitis'])
            elif region_anatomica == 'muñeca':
                terminos.update(['wrist pain', 'carpal tunnel', 'tendonitis'])
            elif region_anatomica == 'brazo':
                terminos.update(['arm pain', 'muscle strain', 'biceps', 'triceps'])
            elif region_anatomica == 'pierna':
                terminos.update(['leg pain', 'muscle strain', 'thigh', 'calf'])
            elif region_anatomica == 'cuello':
                terminos.update(['neck pain', 'cervical', 'whiplash', 'stiff neck'])
            elif region_anatomica == 'cabeza':
                terminos.update(['headache', 'migraine', 'tension headache'])
            elif region_anatomica == 'pecho':
                terminos.update(['chest pain', 'rib', 'sternum', 'costal'])
            elif region_anatomica == 'abdomen':
                terminos.update(['abdominal pain', 'stomach pain', 'digestive'])
            elif region_anatomica == 'cara':
                terminos.update(['facial pain', 'TMJ', 'jaw pain'])
            elif region_anatomica == 'ojo':
                terminos.update(['eye pain', 'ocular', 'vision'])
            elif region_anatomica == 'oído':
                terminos.update(['ear pain', 'otitis', 'hearing'])
            elif region_anatomica == 'nariz':
                terminos.update(['nasal pain', 'sinus', 'rhinitis'])
            elif region_anatomica == 'boca':
                terminos.update(['oral pain', 'dental', 'toothache'])
            elif region_anatomica == 'garganta':
                terminos.update(['throat pain', 'pharyngitis', 'laryngitis'])
        
        # Términos de escalas de evaluación
        for palabra_clave in palabras_clave:
            for escala in palabra_clave.escalas_evaluacion:
                if 'EVA' in escala:
                    terminos.add("pain scale")
                    terminos.add("visual analog scale")
                elif 'funcional' in escala.lower():
                    terminos.add("functional assessment")
                    terminos.add("functional scale")
        
        # Combinar región anatómica con síntomas específicos
        if region_anatomica:
            for palabra_clave in palabras_clave:
                if palabra_clave.palabra == 'dolor':
                    terminos.add(f"{region_anatomica} pain syndrome")
                    terminos.add(f"chronic {region_anatomica} pain")
                    terminos.add(f"acute {region_anatomica} pain")
                elif palabra_clave.palabra == 'inflamacion':
                    terminos.add(f"{region_anatomica} inflammation")
                    terminos.add(f"{region_anatomica} swelling")
                elif palabra_clave.palabra == 'rigidez':
                    terminos.add(f"{region_anatomica} stiffness")
                    terminos.add(f"{region_anatomica} mobility")
                elif palabra_clave.palabra == 'limitacion':
                    terminos.add(f"{region_anatomica} limitation")
                    terminos.add(f"{region_anatomica} function")
        
        return list(terminos)
    
    def generar_preguntas_evaluacion(self, palabras_clave: List[PalabraClave], 
                                   escalas: List[EscalaEvaluacion],
                                   tipo_atencion: str = None,
                                   region_anatomica: str = None) -> List[str]:
        """Genera preguntas de evaluación específicas y sin duplicados"""
        preguntas = []
        preguntas_eva = []  # Para controlar preguntas de EVA
        preguntas_dolor = []  # Para controlar preguntas de dolor
        
        # 1. Preguntas específicas por tipo de atención
        preguntas.extend(self._get_preguntas_por_profesion(tipo_atencion))
        
        # 2. Preguntas de palabras clave (evitando duplicados)
        for palabra_clave in palabras_clave:
            for pregunta in palabra_clave.preguntas_sugeridas:
                # Controlar preguntas de EVA
                if 'escala' in pregunta.lower() and '0' in pregunta and '10' in pregunta:
                    if not preguntas_eva:
                        preguntas_eva.append(pregunta)
                # Controlar preguntas de dolor
                elif 'dolor' in pregunta.lower():
                    if pregunta not in preguntas_dolor:
                        preguntas_dolor.append(pregunta)
                else:
                    preguntas.append(pregunta)
        
        # 3. Agregar preguntas controladas
        preguntas.extend(preguntas_eva)
        preguntas.extend(preguntas_dolor)
        
        # 4. Preguntas específicas por región anatómica
        if region_anatomica:
            preguntas.extend(self._get_preguntas_por_region(region_anatomica))
        
        # 5. Preguntas de escalas de evaluación (evitando duplicados de EVA)
        for escala in escalas:
            for pregunta in escala.preguntas:
                if 'escala' in pregunta.lower() and '0' in pregunta and '10' in pregunta:
                    if not preguntas_eva:
                        preguntas_eva.append(pregunta)
                else:
                    preguntas.append(pregunta)
        
        # 6. Preguntas generales de evaluación
        preguntas.extend(self._get_preguntas_generales(tipo_atencion))
        
        # Eliminar duplicados y limitar a máximo 8 preguntas
        preguntas_unicas = list(dict.fromkeys(preguntas))  # Mantiene orden
        return preguntas_unicas[:8]
    
    def _get_preguntas_por_profesion(self, tipo_atencion: str) -> List[str]:
        """Obtiene preguntas específicas por tipo de atención"""
        preguntas = {
            'fisioterapia': [
                '¿Cómo afecta el problema su movilidad diaria?',
                '¿Ha notado cambios en la fuerza muscular?',
                '¿El dolor se irradia a otras zonas?'
            ],
            'kinesiologia': [
                '¿Cómo afecta el problema su movilidad diaria?',
                '¿Ha notado cambios en la fuerza muscular?',
                '¿El dolor se irradia a otras zonas?'
            ],
            'fonoaudiologia': [
                '¿Cómo afecta el problema su comunicación?',
                '¿Ha notado cambios en la voz o el habla?',
                '¿El problema afecta la deglución?'
            ],
            'psicologia': [
                '¿Cómo afecta el problema su estado emocional?',
                '¿Ha notado cambios en el sueño o apetito?',
                '¿El problema afecta sus relaciones sociales?'
            ],
            'nutricion': [
                '¿Cómo afecta el problema su alimentación?',
                '¿Ha notado cambios en el peso?',
                '¿El problema afecta su digestión?'
            ],
            'terapia_ocupacional': [
                '¿Cómo afecta el problema sus actividades diarias?',
                '¿Ha notado cambios en la coordinación?',
                '¿El problema afecta su independencia?'
            ],
            'enfermeria': [
                '¿Ha notado cambios en los signos vitales?',
                '¿El problema afecta su descanso?',
                '¿Ha tenido fiebre o malestar general?'
            ],
            'urgencia': [
                '¿Cuándo comenzó el problema exactamente?',
                '¿Ha tenido traumatismos recientes?',
                '¿Hay otros síntomas asociados?'
            ]
        }
        
        return preguntas.get(tipo_atencion, [])
    
    def _get_preguntas_por_region(self, region_anatomica: str) -> List[str]:
        """Obtiene preguntas específicas por región anatómica"""
        preguntas = {
            'rodilla': [
                '¿El dolor se agrava al subir o bajar escaleras?',
                '¿Ha notado bloqueos o inestabilidad en la rodilla?',
                '¿El dolor es mayor al flexionar o extender la rodilla?',
                '¿Ha tenido episodios de hinchazón o derrame articular?',
                '¿El dolor se localiza en la parte anterior, posterior o lateral de la rodilla?'
            ],
            'hombro': [
                '¿El dolor se agrava al levantar el brazo por encima de la cabeza?',
                '¿Ha notado debilidad al realizar movimientos con el brazo?',
                '¿El dolor se irradia hacia el brazo o cuello?',
                '¿Tiene dificultad para dormir sobre el lado afectado?',
                '¿El dolor es mayor por la noche?'
            ],
            'columna': [
                '¿El dolor se irradia hacia las piernas o brazos?',
                '¿Ha notado cambios en la sensibilidad o fuerza?',
                '¿El dolor se agrava con la tos o estornudos?',
                '¿Tiene dificultad para mantener posturas por tiempo prolongado?',
                '¿El dolor mejora o empeora con el movimiento?'
            ],
            'tobillo': [
                '¿El dolor se agrava al caminar o estar de pie?',
                '¿Ha notado inestabilidad al caminar?',
                '¿El dolor es mayor en la parte interna o externa del tobillo?',
                '¿Ha tenido episodios de hinchazón?',
                '¿El dolor se agrava al subir o bajar escaleras?'
            ],
            'codo': [
                '¿El dolor se agrava al realizar movimientos de agarre?',
                '¿Ha notado debilidad al levantar objetos?',
                '¿El dolor se localiza en la parte interna o externa del codo?',
                '¿El dolor se agrava con actividades repetitivas?',
                '¿Ha notado rigidez matutina?'
            ],
            'muñeca': [
                '¿El dolor se agrava con movimientos repetitivos?',
                '¿Ha notado hormigueo o entumecimiento en los dedos?',
                '¿El dolor se agrava por la noche?',
                '¿Ha notado debilidad al agarrar objetos?',
                '¿El dolor se localiza en la palma o dorso de la mano?'
            ],
            'cuello': [
                '¿El dolor se irradia hacia los brazos o cabeza?',
                '¿Ha notado mareos o vértigo?',
                '¿El dolor se agrava con movimientos del cuello?',
                '¿Tiene dificultad para girar la cabeza?',
                '¿El dolor se agrava con el estrés?'
            ],
            'cabeza': [
                '¿El dolor es pulsátil o constante?',
                '¿Ha notado cambios en la visión?',
                '¿El dolor se acompaña de náuseas o vómitos?',
                '¿El dolor se agrava con la luz o ruidos?',
                '¿Ha notado cambios en el patrón del dolor?'
            ],
            'pecho': [
                '¿El dolor se agrava con la respiración?',
                '¿Ha notado dificultad para respirar?',
                '¿El dolor se irradia hacia el brazo o mandíbula?',
                '¿El dolor se agrava con el ejercicio?',
                '¿Ha notado palpitaciones o taquicardia?'
            ],
            'abdomen': [
                '¿El dolor se agrava con la ingesta de alimentos?',
                '¿Ha notado cambios en el hábito intestinal?',
                '¿El dolor se acompaña de náuseas o vómitos?',
                '¿El dolor se localiza en una zona específica?',
                '¿Ha notado cambios en el apetito?'
            ]
        }
        
        return preguntas.get(region_anatomica, [])
    
    def _get_preguntas_generales(self, tipo_atencion: str) -> List[str]:
        """Obtiene preguntas generales de evaluación"""
        preguntas = [
            '¿Cuándo comenzó el problema?',
            '¿Qué factores agravan los síntomas?',
            '¿Qué factores alivian los síntomas?',
            '¿Ha recibido tratamiento previo para este problema?',
            '¿Toma algún medicamento actualmente?',
            '¿Tiene alguna condición médica previa?'
        ]
        
        # Agregar preguntas específicas según el tipo de atención
        if tipo_atencion in ['fisioterapia', 'kinesiologia']:
            preguntas.extend([
                '¿El problema afecta su capacidad de trabajo?',
                '¿Ha notado cambios en la postura?'
            ])
        elif tipo_atencion in ['psicologia']:
            preguntas.extend([
                '¿Cómo se siente emocionalmente?',
                '¿Ha notado cambios en su estado de ánimo?'
            ])
        elif tipo_atencion in ['nutricion']:
            preguntas.extend([
                '¿Ha notado cambios en su apetito?',
                '¿Tiene alguna restricción alimentaria?'
            ])
        
        return preguntas
    
    def identificar_region_anatomica(self, motivo_consulta: str) -> Optional[str]:
        """Identifica la región anatómica mencionada en el motivo de consulta"""
        motivo_lower = motivo_consulta.lower()
        
        regiones = {
            'rodilla': ['rodilla', 'knee', 'articulacion rodilla', 'articulación rodilla', 'patela', 'rótula'],
            'hombro': ['hombro', 'shoulder', 'articulacion hombro', 'articulación hombro', 'deltoides'],
            'columna': ['columna', 'espalda', 'lumbar', 'cervical', 'dorsal', 'vertebra', 'vértebra', 'espina'],
            'cadera': ['cadera', 'hip', 'articulacion cadera', 'articulación cadera', 'pelvis', 'pélvis'],
            'tobillo': ['tobillo', 'ankle', 'articulacion tobillo', 'articulación tobillo', 'peroneo'],
            'codo': ['codo', 'elbow', 'articulacion codo', 'articulación codo', 'cubital'],
            'muñeca': ['muñeca', 'wrist', 'articulacion muñeca', 'articulación muñeca', 'carpiano'],
            'brazo': ['brazo', 'arm', 'bíceps', 'tríceps', 'húmero'],
            'pierna': ['pierna', 'leg', 'fémur', 'tibia', 'peroné'],
            'pie': ['pie', 'foot', 'metatarso', 'calcáneo', 'talón'],
            'mano': ['mano', 'hand', 'dedos', 'falanges', 'metacarpiano'],
            'cuello': ['cuello', 'neck', 'cervical', 'nuca', 'trapecio'],
            'cabeza': ['cabeza', 'head', 'cráneo', 'craneo', 'temporal'],
            'pecho': ['pecho', 'chest', 'tórax', 'torax', 'esternón'],
            'abdomen': ['abdomen', 'stomach', 'vientre', 'barriga', 'ombligo'],
            'cara': ['cara', 'face', 'rostro', 'frente', 'mejilla'],
            'ojo': ['ojo', 'eye', 'ocular', 'párpado', 'parpado'],
            'oído': ['oído', 'ear', 'auditivo', 'tímpano', 'timpanico'],
            'nariz': ['nariz', 'nose', 'nasal', 'fosas nasales'],
            'boca': ['boca', 'mouth', 'oral', 'labios', 'lengua'],
            'garganta': ['garganta', 'throat', 'faringe', 'laringe', 'amígdalas']
        }
        
        for region, palabras in regiones.items():
            for palabra in palabras:
                if palabra in motivo_lower:
                    return region
        
        return None
    
    def analizar_motivo_consulta_mejorado(self, motivo_consulta: str, tipo_atencion: str = None) -> AnalisisMejorado:
        """Análisis completo y mejorado del motivo de consulta"""
        try:
            # Paso 1: Identificar región anatómica primero
            region_anatomica = self.identificar_region_anatomica(motivo_consulta)
            
            # Paso 2: Identificar palabras clave con contexto anatómico
            palabras_clave = self.identificar_palabras_clave(motivo_consulta)
            
            # Paso 3: Identificar patologías
            patologias = self.identificar_patologias(palabras_clave)
            
            # Paso 4: Identificar escalas de evaluación
            escalas = self.identificar_escalas_evaluacion(palabras_clave, region_anatomica)
            
            # Paso 5: Generar términos de búsqueda mejorados
            terminos_busqueda = self.generar_terminos_busqueda_mejorados(
                palabras_clave, patologias, region_anatomica
            )
            
            # Paso 6: Generar preguntas de evaluación (mejorada)
            preguntas_evaluacion = self.generar_preguntas_evaluacion(
                palabras_clave, escalas, tipo_atencion, region_anatomica
            )
            
            # Paso 7: Calcular confianza global
            confianza_global = self._calcular_confianza_global(palabras_clave, patologias)
            
            # Paso 8: Agregar información de región anatómica al análisis
            if region_anatomica:
                # Agregar términos específicos de la región
                terminos_busqueda.extend([
                    f"{region_anatomica} assessment",
                    f"{region_anatomica} evaluation",
                    f"{region_anatomica} diagnosis"
                ])
                
                # Agregar preguntas específicas de la región
                preguntas_regionales = self._get_preguntas_por_region(region_anatomica)
                preguntas_evaluacion.extend(preguntas_regionales)
            
            return AnalisisMejorado(
                palabras_clave=palabras_clave,
                patologias_identificadas=patologias,
                escalas_recomendadas=escalas,
                terminos_busqueda_mejorados=terminos_busqueda,
                preguntas_evaluacion=preguntas_evaluacion,
                confianza_global=confianza_global
            )
            
        except Exception as e:
            logger.error(f"Error en análisis mejorado: {e}")
            return AnalisisMejorado(
                palabras_clave=[],
                patologias_identificadas=[],
                escalas_recomendadas=[],
                terminos_busqueda_mejorados=[],
                preguntas_evaluacion=[],
                confianza_global=0.0
            )
    
    def _calcular_confianza_global(self, palabras_clave: List[PalabraClave], 
                                  patologias: List[PatologiaIdentificada]) -> float:
        """Calcula la confianza global del análisis"""
        if not palabras_clave:
            return 0.0
        
        # Promedio de intensidades de palabras clave
        intensidad_promedio = sum(pc.intensidad for pc in palabras_clave) / len(palabras_clave)
        
        # Promedio de confianzas de patologías
        confianza_patologias = sum(p.confianza for p in patologias) / max(len(patologias), 1)
        
        # Confianza global como promedio ponderado
        confianza_global = (intensidad_promedio * 0.6) + (confianza_patologias * 0.4)
        
        return min(confianza_global, 1.0)

# Instancia global del analizador
clinical_analyzer = ClinicalPatternAnalyzer() 