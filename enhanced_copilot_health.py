#!/usr/bin/env python3
"""
Copilot Health Mejorado con Análisis de Patrones Clínicos
Integra identificación de palabras clave, patologías y escalas de evaluación
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from clinical_pattern_analyzer import ClinicalPatternAnalyzer, AnalisisMejorado
from medical_apis_integration import MedicalAPIsIntegration

logger = logging.getLogger(__name__)

@dataclass
class ResultadoAnalisisMejorado:
    """Resultado del análisis mejorado de Copilot Health"""
    analisis_clinico: AnalisisMejorado
    evidencia_cientifica: List[Dict]
    recomendaciones: List[str]
    escalas_aplicadas: List[str]
    confianza_global: float

class EnhancedCopilotHealth:
    """Copilot Health mejorado con análisis de patrones clínicos"""
    
    def __init__(self):
        self.clinical_analyzer = ClinicalPatternAnalyzer()
        self.medical_apis = MedicalAPIsIntegration()
        logger.info("✅ Copilot Health Mejorado inicializado")
    
    def analizar_caso_completo_mejorado(self, motivo_consulta: str, 
                                       tipo_atencion: str = None,
                                       edad_paciente: int = None,
                                       antecedentes: str = None) -> ResultadoAnalisisMejorado:
        """
        Análisis completo mejorado del caso clínico
        """
        try:
            logger.info(f"🔍 Iniciando análisis mejorado para: {motivo_consulta}")
            logger.info(f"🏥 Tipo de atención: {tipo_atencion}")
            
            # Paso 1: Análisis clínico mejorado (con tipo de atención)
            analisis_clinico = self.clinical_analyzer.analizar_motivo_consulta_mejorado(
                motivo_consulta, tipo_atencion
            )
            
            logger.info(f"✅ Análisis clínico completado. Palabras clave: {len(analisis_clinico.palabras_clave)}")
            logger.info(f"📝 Preguntas generadas: {len(analisis_clinico.preguntas_evaluacion)}")
            
            # Paso 2: Búsqueda de evidencia científica mejorada
            evidencia_cientifica = self._buscar_evidencia_mejorada(analisis_clinico)
            
            # Paso 3: Generar recomendaciones
            recomendaciones = self._generar_recomendaciones_mejoradas(analisis_clinico, evidencia_cientifica)
            
            # Paso 4: Identificar escalas aplicadas
            escalas_aplicadas = self._identificar_escalas_aplicadas(analisis_clinico)
            
            # Paso 5: Calcular confianza global
            confianza_global = self._calcular_confianza_final(analisis_clinico, evidencia_cientifica)
            
            return ResultadoAnalisisMejorado(
                analisis_clinico=analisis_clinico,
                evidencia_cientifica=evidencia_cientifica,
                recomendaciones=recomendaciones,
                escalas_aplicadas=escalas_aplicadas,
                confianza_global=confianza_global
            )
            
        except Exception as e:
            logger.error(f"❌ Error en análisis completo mejorado: {e}")
            return ResultadoAnalisisMejorado(
                analisis_clinico=AnalisisMejorado(
                    palabras_clave=[], patologias_identificadas=[], 
                    escalas_recomendadas=[], terminos_busqueda_mejorados=[],
                    preguntas_evaluacion=[], confianza_global=0.0
                ),
                evidencia_cientifica=[],
                recomendaciones=[],
                escalas_aplicadas=[],
                confianza_global=0.0
            )
    
    def _buscar_evidencia_mejorada(self, analisis_clinico: AnalisisMejorado) -> List[Dict]:
        """
        Búsqueda de evidencia científica mejorada basada en el análisis clínico
        """
        evidencia_encontrada = []
        
        try:
            # Búsqueda por términos mejorados
            for termino in analisis_clinico.terminos_busqueda_mejorados:
                logger.info(f"🔍 Buscando evidencia para término: {termino}")
                
                # Buscar en PubMed y Europe PMC
                resultados = self.medical_apis.buscar_tratamiento_pubmed(termino, "general")
                
                if resultados:
                    for resultado in resultados[:3]:  # Top 3 resultados por término
                        evidencia_encontrada.append({
                            'termino_busqueda': termino,
                            'titulo': resultado.titulo,
                            'doi': resultado.doi,
                            'resumen': resultado.resumen,
                            'año_publicacion': resultado.año_publicacion,
                            'fuente': 'PubMed/Europe PMC',
                            'relevancia': self._calcular_relevancia(resultado, analisis_clinico)
                        })
            
            # Búsqueda específica por patologías identificadas
            for patologia in analisis_clinico.patologias_identificadas:
                if patologia.confianza > 0.5:  # Solo patologías con alta confianza
                    logger.info(f"🔍 Buscando evidencia para patología: {patologia.nombre}")
                    
                    for termino in patologia.terminos_busqueda:
                        resultados = self.medical_apis.buscar_tratamiento_pubmed(termino, "general")
                        
                        if resultados:
                            for resultado in resultados[:2]:  # Top 2 por patología
                                evidencia_encontrada.append({
                                    'termino_busqueda': termino,
                                    'patologia_asociada': patologia.nombre,
                                    'titulo': resultado.titulo,
                                    'doi': resultado.doi,
                                    'resumen': resultado.resumen,
                                    'año_publicacion': resultado.año_publicacion,
                                    'fuente': 'PubMed/Europe PMC',
                                    'relevancia': self._calcular_relevancia(resultado, analisis_clinico)
                                })
            
            # Ordenar por relevancia
            evidencia_encontrada.sort(key=lambda x: x['relevancia'], reverse=True)
            
            logger.info(f"✅ Evidencia encontrada: {len(evidencia_encontrada)} artículos")
            return evidencia_encontrada[:10]  # Top 10 resultados
            
        except Exception as e:
            logger.error(f"❌ Error en búsqueda de evidencia mejorada: {e}")
            return []
    
    def _calcular_relevancia(self, resultado, analisis_clinico: AnalisisMejorado) -> float:
        """
        Calcula la relevancia de un resultado basado en el análisis clínico
        """
        relevancia = 0.5  # Base
        
        # Aumentar relevancia si contiene palabras clave
        titulo_resumen = f"{resultado.titulo} {resultado.resumen}".lower()
        
        for palabra_clave in analisis_clinico.palabras_clave:
            if palabra_clave.palabra in titulo_resumen:
                relevancia += 0.2 * palabra_clave.intensidad
        
        # Aumentar relevancia si es reciente
        if resultado.año_publicacion and resultado.año_publicacion.isdigit():
            año = int(resultado.año_publicacion)
            if año >= 2020:
                relevancia += 0.1
            elif año >= 2015:
                relevancia += 0.05
        
        # Aumentar relevancia si tiene DOI
        if resultado.doi and resultado.doi != "N/A":
            relevancia += 0.1
        
        return min(relevancia, 1.0)
    
    def _generar_recomendaciones_mejoradas(self, analisis_clinico: AnalisisMejorado, 
                                          evidencia_cientifica: List[Dict]) -> List[str]:
        """
        Genera recomendaciones mejoradas basadas en el análisis clínico
        """
        recomendaciones = []
        
        # Recomendaciones basadas en palabras clave
        for palabra_clave in analisis_clinico.palabras_clave:
            if palabra_clave.palabra == 'dolor':
                recomendaciones.append("Evaluar intensidad del dolor usando Escala Visual Analógica (EVA)")
                recomendaciones.append("Considerar factores agravantes y aliviadores del dolor")
            
            elif palabra_clave.palabra == 'rigidez':
                recomendaciones.append("Evaluar rigidez matutina y su duración")
                recomendaciones.append("Considerar ejercicios de movilidad articular")
            
            elif palabra_clave.palabra == 'limitacion':
                recomendaciones.append("Evaluar capacidad funcional y actividades de la vida diaria")
                recomendaciones.append("Considerar rehabilitación funcional")
            
            elif palabra_clave.palabra == 'debilidad':
                recomendaciones.append("Evaluar fuerza muscular usando escala de 0-5")
                recomendaciones.append("Considerar ejercicios de fortalecimiento progresivo")
        
        # Recomendaciones basadas en patologías
        for patologia in analisis_clinico.patologias_identificadas:
            if patologia.nombre == 'artritis':
                recomendaciones.append("Considerar evaluación reumatológica")
                recomendaciones.append("Evaluar signos inflamatorios y rigidez matutina")
            
            elif patologia.nombre == 'tendinitis':
                recomendaciones.append("Evaluar movimientos específicos que agravan el dolor")
                recomendaciones.append("Considerar reposo relativo y ejercicios excéntricos")
            
            elif patologia.nombre == 'compresion_nerviosa':
                recomendaciones.append("Evaluar síntomas neurológicos (hormigueo, entumecimiento)")
                recomendaciones.append("Considerar estudios de conducción nerviosa")
        
        # Recomendaciones basadas en escalas de evaluación
        escalas_identificadas = [escala.nombre for escala in analisis_clinico.escalas_recomendadas]
        if 'EVA' in escalas_identificadas:
            recomendaciones.append("Aplicar Escala Visual Analógica (EVA) para cuantificar el dolor")
        
        if 'Escala_Funcional' in escalas_identificadas:
            recomendaciones.append("Evaluar capacidad funcional usando escalas validadas")
        
        # Recomendaciones basadas en evidencia científica
        if evidencia_cientifica:
            recomendaciones.append(f"Se encontraron {len(evidencia_cientifica)} artículos científicos relevantes")
            recomendaciones.append("Revisar evidencia científica para guiar el tratamiento")
        
        return list(set(recomendaciones))  # Eliminar duplicados
    
    def _identificar_escalas_aplicadas(self, analisis_clinico: AnalisisMejorado) -> List[str]:
        """
        Identifica las escalas de evaluación que deben aplicarse
        """
        escalas_aplicadas = []
        
        for escala in analisis_clinico.escalas_recomendadas:
            escalas_aplicadas.append(f"{escala.nombre}: {escala.descripcion}")
        
        return escalas_aplicadas
    
    def _calcular_confianza_final(self, analisis_clinico: AnalisisMejorado, 
                                 evidencia_cientifica: List[Dict]) -> float:
        """
        Calcula la confianza final del análisis
        """
        # Confianza del análisis clínico
        confianza_analisis = analisis_clinico.confianza_global
        
        # Confianza basada en evidencia encontrada
        confianza_evidencia = min(len(evidencia_cientifica) / 10.0, 1.0)
        
        # Confianza final como promedio ponderado
        confianza_final = (confianza_analisis * 0.7) + (confianza_evidencia * 0.3)
        
        return min(confianza_final, 1.0)
    
    def generar_resumen_mejorado(self, resultado: ResultadoAnalisisMejorado) -> Dict:
        """
        Genera un resumen mejorado del análisis
        """
        return {
            'palabras_clave_identificadas': [
                {
                    'palabra': pc.palabra,
                    'categoria': pc.categoria,
                    'intensidad': pc.intensidad,
                    'escalas': pc.escalas_evaluacion
                }
                for pc in resultado.analisis_clinico.palabras_clave
            ],
            'patologias_sugeridas': [
                {
                    'nombre': p.nombre,
                    'confianza': p.confianza,
                    'sintomas': p.sintomas_asociados
                }
                for p in resultado.analisis_clinico.patologias_identificadas
            ],
            'escalas_recomendadas': [
                {
                    'nombre': e.nombre,
                    'descripcion': e.descripcion,
                    'aplicacion': e.aplicacion,
                    'preguntas': e.preguntas
                }
                for e in resultado.analisis_clinico.escalas_recomendadas
            ],
            'preguntas_evaluacion': resultado.analisis_clinico.preguntas_evaluacion,
            'evidencia_cientifica': resultado.evidencia_cientifica,
            'recomendaciones': resultado.recomendaciones,
            'confianza_global': resultado.confianza_global
        }

# Instancia global
enhanced_copilot = EnhancedCopilotHealth()

# Función de prueba
def test_enhanced_copilot_health():
    """Prueba el Copilot Health mejorado"""
    copilot = EnhancedCopilotHealth()
    
    # Datos de prueba
    patient_data = {
        'age': 45,
        'gender': 'female',
        'medical_history': ['hipertensión', 'diabetes'],
        'lifestyle': {'sedentario': True, 'tabaco': False}
    }
    
    symptoms = ['dolor lumbar', 'rigidez matutina', 'limitación movimiento']
    consultation_type = 'fisioterapia'
    age = 45
    motive = 'Dolor lumbar crónico de 3 meses'
    questions = '¿Qué ejercicios puedo hacer? ¿Cuánto tiempo durará el tratamiento?'
    
    print("🚀 PRUEBA DE COPILOT HEALTH MEJORADO")
    print("=" * 60)
    
    # Análisis comprehensivo
    result = copilot.analyze_comprehensive_case(
        patient_data, symptoms, consultation_type, age, motive, questions
    )
    
    if result['success']:
        print("✅ Análisis comprehensivo completado")
        
        # Mostrar insights clínicos
        clinical = result['clinical_analysis']
        print(f"\n🎯 INSIGHTS CLÍNICOS:")
        print(f"   Condición principal: {clinical['symptom_analysis']['primary_condition']}")
        print(f"   Confianza: {clinical['symptom_analysis']['confidence']:.1%}")
        print(f"   Score clínico: {clinical['clinical_score']:.1%}")
        
        # Mostrar evidencia
        evidence = result['evidence_search']
        print(f"\n📚 EVIDENCIA CIENTÍFICA:")
        print(f"   Estudios encontrados: {len(evidence.get('planes_tratamiento', []))}")
        
        # Mostrar recomendaciones
        recommendations = result['recommendations']
        print(f"\n💡 RECOMENDACIONES:")
        print(f"   Acciones inmediatas: {len(recommendations['immediate_actions'])}")
        print(f"   Plan de tratamiento: {len(recommendations['treatment_plan'])}")
        print(f"   Monitoreo: {len(recommendations['monitoring'])}")
        
        # Mostrar alertas
        risk_assessment = result['risk_assessment']
        print(f"\n⚠️ ALERTAS:")
        print(f"   Total alertas: {risk_assessment['total_alerts']}")
        
        # Mostrar términos clave
        print(f"\n🔍 TÉRMINOS CLAVE:")
        print(f"   Términos extraídos: {len(result['key_terms'])}")
        print(f"   Principales: {result['key_terms'][:5]}")
        
        # Mostrar resumen
        print(f"\n📋 RESUMEN:")
        print(f"   {result['summary']}")
        
    else:
        print(f"❌ Error en análisis: {result.get('error', 'Error desconocido')}")

if __name__ == "__main__":
    test_enhanced_copilot_health() 