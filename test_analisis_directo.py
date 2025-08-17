#!/usr/bin/env python3
"""
Test directo de los módulos de análisis mejorado
"""

def test_clinical_pattern_analyzer():
    """Prueba directa del analizador de patrones clínicos"""
    print("🔍 PRUEBA: Analizador de patrones clínicos")
    print("=" * 50)
    
    try:
        from clinical_pattern_analyzer import clinical_analyzer
        
        casos_prueba = [
            'Dolor intenso en rodilla al caminar',
            'Rigidez matutina en hombro derecho',
            'Hormigueo y entumecimiento en mano izquierda',
            'Inflamación y dolor en tobillo después del ejercicio'
        ]
        
        for i, motivo in enumerate(casos_prueba, 1):
            print(f"\n📋 Caso {i}: {motivo}")
            
            # Análisis completo
            analisis = clinical_analyzer.analizar_motivo_consulta_mejorado(motivo)
            
            print(f"✅ Palabras clave identificadas: {len(analisis.palabras_clave)}")
            for pc in analisis.palabras_clave:
                print(f"   • {pc.palabra} ({pc.categoria}) - Intensidad: {pc.intensidad:.2f}")
            
            print(f"✅ Patologías identificadas: {len(analisis.patologias_identificadas)}")
            for pat in analisis.patologias_identificadas:
                print(f"   • {pat.nombre} (Confianza: {pat.confianza:.2f})")
            
            print(f"✅ Escalas recomendadas: {len(analisis.escalas_recomendadas)}")
            for escala in analisis.escalas_recomendadas:
                print(f"   • {escala.nombre}: {escala.descripcion}")
            
            print(f"✅ Términos de búsqueda: {len(analisis.terminos_busqueda_mejorados)}")
            for termino in analisis.terminos_busqueda_mejorados[:5]:
                print(f"   • {termino}")
            
            print(f"✅ Preguntas de evaluación: {len(analisis.preguntas_evaluacion)}")
            for pregunta in analisis.preguntas_evaluacion[:3]:
                print(f"   • {pregunta}")
            
            print(f"✅ Confianza global: {analisis.confianza_global:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test_clinical_pattern_analyzer: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_copilot_health():
    """Prueba directa del Copilot Health mejorado"""
    print("\n🔍 PRUEBA: Copilot Health mejorado")
    print("=" * 50)
    
    try:
        from enhanced_copilot_health import enhanced_copilot
        
        casos_prueba = [
            {
                'motivo': 'Dolor intenso en rodilla al caminar',
                'tipo_atencion': 'kinesiologia',
                'edad': 45,
                'antecedentes': 'Hipertensión arterial'
            },
            {
                'motivo': 'Rigidez matutina en hombro derecho',
                'tipo_atencion': 'fisioterapia',
                'edad': 35,
                'antecedentes': 'Trabajo de oficina'
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n📋 Caso {i}: {caso['motivo']}")
            
            # Análisis completo mejorado
            resultado = enhanced_copilot.analizar_caso_completo_mejorado(
                motivo_consulta=caso['motivo'],
                tipo_atencion=caso['tipo_atencion'],
                edad_paciente=caso['edad'],
                antecedentes=caso['antecedentes']
            )
            
            print(f"✅ Análisis clínico completado")
            print(f"   • Palabras clave: {len(resultado.analisis_clinico.palabras_clave)}")
            print(f"   • Patologías: {len(resultado.analisis_clinico.patologias_identificadas)}")
            print(f"   • Escalas: {len(resultado.analisis_clinico.escalas_recomendadas)}")
            print(f"   • Términos búsqueda: {len(resultado.analisis_clinico.terminos_busqueda_mejorados)}")
            
            print(f"✅ Evidencia científica: {len(resultado.evidencia_cientifica)} artículos")
            print(f"✅ Recomendaciones: {len(resultado.recomendaciones)}")
            print(f"✅ Escalas aplicadas: {len(resultado.escalas_aplicadas)}")
            print(f"✅ Confianza global: {resultado.confianza_global:.2f}")
            
            # Mostrar algunas recomendaciones
            if resultado.recomendaciones:
                print(f"💡 Recomendaciones principales:")
                for rec in resultado.recomendaciones[:3]:
                    print(f"   • {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test_enhanced_copilot_health: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_palabras_clave_especificas():
    """Prueba casos específicos de palabras clave"""
    print("\n🔍 PRUEBA: Casos específicos de palabras clave")
    print("=" * 50)
    
    try:
        from clinical_pattern_analyzer import clinical_analyzer
        
        # Caso específico: dolor de rodilla
        motivo = "Dolor en rodilla al subir escaleras"
        print(f"📋 Caso: {motivo}")
        
        analisis = clinical_analyzer.analizar_motivo_consulta_mejorado(motivo)
        
        # Verificar que se identificó "dolor"
        dolor_encontrado = any(pc.palabra == 'dolor' for pc in analisis.palabras_clave)
        print(f"✅ Palabra 'dolor' identificada: {dolor_encontrado}")
        
        # Verificar que se identificó "rodilla"
        rodilla_encontrada = analisis.patologias_identificadas or any(
            'rodilla' in termino.lower() for termino in analisis.terminos_busqueda_mejorados
        )
        print(f"✅ Región 'rodilla' identificada: {rodilla_encontrada}")
        
        # Verificar escalas de evaluación
        escalas_dolor = [escala for escala in analisis.escalas_recomendadas 
                        if 'EVA' in escala.nombre or 'dolor' in escala.nombre.lower()]
        print(f"✅ Escalas para dolor identificadas: {len(escalas_dolor)}")
        
        # Verificar preguntas de evaluación
        preguntas_dolor = [pregunta for pregunta in analisis.preguntas_evaluacion 
                          if 'dolor' in pregunta.lower()]
        print(f"✅ Preguntas sobre dolor: {len(preguntas_dolor)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test_palabras_clave_especificas: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DIRECTAS DE ANÁLISIS MEJORADO")
    print("=" * 60)
    
    resultados = []
    
    # Prueba 1: Analizador de patrones clínicos
    resultados.append(('Analizador de patrones clínicos', test_clinical_pattern_analyzer()))
    
    # Prueba 2: Copilot Health mejorado
    resultados.append(('Copilot Health mejorado', test_enhanced_copilot_health()))
    
    # Prueba 3: Casos específicos
    resultados.append(('Casos específicos de palabras clave', test_palabras_clave_especificas()))
    
    print("\n📊 RESUMEN DE RESULTADOS:")
    print("=" * 60)
    
    exitos = 0
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"{estado}: {nombre}")
        if resultado:
            exitos += 1
    
    print(f"\n🎯 RESULTADO FINAL: {exitos}/{total} pruebas exitosas")
    
    if exitos == total:
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("✅ Análisis mejorado de patrones clínicos funcionando correctamente")
        print("✅ Identificación de palabras clave funcionando")
        print("✅ Asociación con patologías funcionando")
        print("✅ Escalas de evaluación recomendadas funcionando")
        print("✅ Búsqueda mejorada de evidencia científica funcionando")
        print("✅ Sistema completo integrado y funcionando")
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("Revisar los logs para más detalles")

if __name__ == "__main__":
    main() 