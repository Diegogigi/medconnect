#!/usr/bin/env python3
"""
Script para probar la integración de sistemas mejorados
"""

import sys
import traceback
from pathlib import Path


def test_imports():
    """Prueba que todas las importaciones funcionen"""
    print("🧪 Probando importaciones...")
    
    try:
        # Importar sistemas mejorados
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced
        print("   ✅ UnifiedScientificSearchEnhanced importado")
        
        from unified_nlp_processor_main import UnifiedNLPProcessor
        print("   ✅ UnifiedNLPProcessor importado")
        
        from unified_copilot_assistant_enhanced import UnifiedCopilotAssistant
        print("   ✅ UnifiedCopilotAssistant importado")
        
        from unified_orchestration_system import UnifiedOrchestrationSystem
        print("   ✅ UnifiedOrchestrationSystem importado")
        
        from rag_tracing_system import RAGTracingSystem
        print("   ✅ RAGTracingSystem importado")
        
        from metrics_system import MetricsCollector, ObservabilitySystem
        print("   ✅ MetricsCollector y ObservabilitySystem importados")
        
        from citation_assigner_enhanced import CitationAssignerEnhanced
        print("   ✅ CitationAssignerEnhanced importado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en importaciones: {e}")
        traceback.print_exc()
        return False


def test_system_initialization():
    """Prueba la inicialización de los sistemas"""
    print("\n🔧 Probando inicialización de sistemas...")
    
    try:
        # Inicializar sistemas
        search_system = UnifiedScientificSearchEnhanced()
        print("   ✅ UnifiedScientificSearchEnhanced inicializado")
        
        nlp_processor = UnifiedNLPProcessor()
        print("   ✅ UnifiedNLPProcessor inicializado")
        
        copilot = UnifiedCopilotAssistant()
        print("   ✅ UnifiedCopilotAssistant inicializado")
        
        orchestration = UnifiedOrchestrationSystem()
        print("   ✅ UnifiedOrchestrationSystem inicializado")
        
        rag_tracing = RAGTracingSystem()
        print("   ✅ RAGTracingSystem inicializado")
        
        metrics = MetricsCollector()
        print("   ✅ MetricsCollector inicializado")
        
        observability = ObservabilitySystem()
        print("   ✅ ObservabilitySystem inicializado")
        
        citation_assigner = CitationAssignerEnhanced()
        print("   ✅ CitationAssignerEnhanced inicializado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en inicialización: {e}")
        traceback.print_exc()
        return False


def test_basic_functionality():
    """Prueba funcionalidad básica de los sistemas"""
    print("\n⚡ Probando funcionalidad básica...")
    
    try:
        # Probar NLP
        from unified_nlp_processor_main import UnifiedNLPProcessor
        nlp = UnifiedNLPProcessor()
        analisis = nlp.procesar_texto("dolor de rodilla en paciente de 45 años")
        print(f"   ✅ NLP procesado: {len(analisis)} elementos")
        
        # Probar búsqueda científica
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced
        search = UnifiedScientificSearchEnhanced()
        resultados = search.buscar_evidencia_cientifica("dolor de rodilla", max_resultados=3)
        print(f"   ✅ Búsqueda científica: {len(resultados)} resultados")
        
        # Probar asignación de citas
        from citation_assigner_enhanced import CitationAssignerEnhanced
        assigner = CitationAssignerEnhanced()
        oraciones = ["El ejercicio reduce el dolor de rodilla."]
        chunks = [{
            "text": "El ejercicio reduce el dolor de rodilla.",
            "source": "pmid:123",
            "span": (0, 50),
            "meta": {"apa": "Smith (2023). Exercise Study."},
            "entidades_clave": ["ejercicio", "dolor", "rodilla"]
        }]
        citas = assigner.attach_citations_to_sentences(oraciones, chunks)
        print(f"   ✅ Asignación de citas: {len(citas)} oraciones procesadas")
        
        # Probar métricas
        from metrics_system import MetricsCollector
        metrics = MetricsCollector()
        metrics.record_metric("test_metric", 1.0)
        report = metrics.generate_report()
        print(f"   ✅ Métricas: {len(report)} elementos en reporte")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en funcionalidad básica: {e}")
        traceback.print_exc()
        return False


def test_orchestration_pipeline():
    """Prueba el pipeline de orquestación completo"""
    print("\n🎯 Probando pipeline de orquestación...")
    
    try:
        from unified_orchestration_system import UnifiedOrchestrationSystem
        from unified_nlp_processor_main import UnifiedNLPProcessor
        
        # Inicializar sistemas
        orchestration = UnifiedOrchestrationSystem()
        nlp = UnifiedNLPProcessor()
        
        # Procesar consulta
        consulta = "¿Qué tratamientos son efectivos para el dolor de rodilla?"
        analisis_nlp = nlp.procesar_texto(consulta)
        
        # Ejecutar pipeline
        resultado = orchestration.ejecutar_pipeline_completo(consulta, analisis_nlp)
        
        print(f"   ✅ Pipeline ejecutado en {resultado.tiempo_total:.2f}s")
        print(f"   ✅ {len(resultado.terminos_busqueda)} términos generados")
        print(f"   ✅ {len(resultado.resultados_recuperados)} resultados encontrados")
        print(f"   ✅ {len(resultado.chunks_procesados)} chunks procesados")
        print(f"   ✅ {len(resultado.resumen_final.oraciones_con_evidencia)} oraciones con evidencia")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en pipeline de orquestación: {e}")
        traceback.print_exc()
        return False


def test_tracing_and_metrics():
    """Prueba trazabilidad y métricas"""
    print("\n📊 Probando trazabilidad y métricas...")
    
    try:
        from rag_tracing_system import RAGTracingSystem
        from metrics_system import MetricsCollector
        
        # Inicializar sistemas
        tracing = RAGTracingSystem()
        metrics = MetricsCollector()
        
        # Simular operación RAG
        trace_id = tracing.start_trace("consulta de prueba")
        
        # Registrar métricas
        metrics.record_latency("search", 0.5)
        metrics.record_citation_coverage(3, 4)
        metrics.record_response_quality(2, 3)
        
        # Finalizar trace
        tracing.end_trace(trace_id, {"resultado": "test"}, {"latencia": 0.5})
        
        # Generar reportes
        metrics_report = metrics.generate_report()
        trace_summary = tracing.get_trace_summary(trace_id)
        
        print(f"   ✅ Trazabilidad: {len(tracing.traces)} traces creados")
        print(f"   ✅ Métricas: {len(metrics_report)} elementos en reporte")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en trazabilidad y métricas: {e}")
        traceback.print_exc()
        return False


def main():
    """Función principal de pruebas"""
    print("🚀 Probando integración de sistemas mejorados...")
    print("=" * 60)
    
    tests = [
        ("Importaciones", test_imports),
        ("Inicialización", test_system_initialization),
        ("Funcionalidad Básica", test_basic_functionality),
        ("Pipeline de Orquestación", test_orchestration_pipeline),
        ("Trazabilidad y Métricas", test_tracing_and_metrics),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"   ✅ {test_name}: PASÓ")
                passed_tests += 1
            else:
                print(f"   ❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"   ❌ {test_name}: ERROR - {e}")
    
    print(f"\n📊 Resultados de las pruebas:")
    print(f"   ✅ Pruebas pasadas: {passed_tests}/{total_tests}")
    print(f"   📈 Porcentaje de éxito: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ¡Todas las pruebas pasaron! La integración está funcionando correctamente.")
        print("🚀 El sistema está listo para producción.")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} prueba(s) fallaron. Revisar errores.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 