#!/usr/bin/env python3
"""
Script para integrar todos los sistemas mejorados en app.py
"""

import re
import os
from pathlib import Path


def update_imports_in_app_py():
    """Actualiza las importaciones en app.py"""
    
    app_py_path = Path("app.py")
    if not app_py_path.exists():
        print("❌ app.py no encontrado")
        return False
    
    # Leer el archivo
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazos de importaciones
    replacements = [
        # Reemplazar importaciones de sistemas antiguos
        (r'from medical_apis_integration import MedicalAPIsIntegration', 
         'from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced'),
        
        (r'from medical_rag_system import MedicalRAGSystem', 
         'from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced'),
        
        (r'from medical_nlp_processor import MedicalNLPProcessor', 
         'from unified_nlp_processor_main import UnifiedNLPProcessor'),
        
        (r'from clinical_pattern_analyzer import ClinicalPatternAnalyzer', 
         'from unified_nlp_processor_main import UnifiedNLPProcessor'),
        
        (r'from copilot_health import copilot_health', 
         'from unified_copilot_assistant_enhanced import UnifiedCopilotAssistant'),
        
        (r'from enhanced_copilot_health import EnhancedCopilotHealth', 
         'from unified_copilot_assistant_enhanced import UnifiedCopilotAssistant'),
    ]
    
    # Aplicar reemplazos
    for old_pattern, new_pattern in replacements:
        content = re.sub(old_pattern, new_pattern, content)
    
    # Agregar importaciones de sistemas de observabilidad
    observability_imports = '''
# Importaciones de sistemas mejorados
from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced
from unified_nlp_processor_main import UnifiedNLPProcessor
from unified_copilot_assistant_enhanced import UnifiedCopilotAssistant
from unified_orchestration_system import UnifiedOrchestrationSystem
from rag_tracing_system import RAGTracingSystem
from metrics_system import MetricsCollector, ObservabilitySystem

# Inicializar sistemas de observabilidad
rag_tracing = RAGTracingSystem()
metrics_collector = MetricsCollector()
observability_system = ObservabilitySystem()
'''
    
    # Insertar después de las importaciones de Flask
    flask_import_end = content.find('logger.info("[OK] Flask-CORS importado exitosamente")')
    if flask_import_end != -1:
        insert_pos = content.find('\n', flask_import_end) + 1
        content = content[:insert_pos] + observability_imports + content[insert_pos:]
    
    # Escribir el archivo actualizado
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Importaciones actualizadas en app.py")
    return True


def update_search_functions():
    """Actualiza las funciones de búsqueda científica"""
    
    app_py_path = Path("app.py")
    if not app_py_path.exists():
        return False
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar la función de búsqueda científica
    search_pattern = r'def search_scientific_papers\(\):.*?return jsonify\(.*?\)'
    
    new_search_function = '''
def search_scientific_papers():
    """Búsqueda científica mejorada con sistema unificado"""
    try:
        data = request.get_json()
        if not data or "motivo_consulta" not in data:
            return jsonify({"success": False, "message": "Motivo de consulta requerido"}), 400

        motivo_consulta = data["motivo_consulta"]
        logger.info(f"🔍 Búsqueda científica mejorada para: {motivo_consulta}")

        # Iniciar trazabilidad
        trace_id = rag_tracing.start_trace(motivo_consulta)
        
        try:
            # Análisis NLP mejorado
            nlp_processor = UnifiedNLPProcessor()
            analisis_nlp = nlp_processor.procesar_texto(motivo_consulta)
            
            # Búsqueda científica unificada
            search_system = UnifiedScientificSearchEnhanced()
            resultados = search_system.buscar_evidencia_cientifica(
                motivo_consulta, 
                analisis_nlp=analisis_nlp,
                max_resultados=10
            )
            
            # Procesar resultados
            papers_encontrados = []
            for evidencia in resultados:
                papers_encontrados.append({
                    "titulo": evidencia.titulo,
                    "resumen": evidencia.resumen,
                    "doi": evidencia.doi,
                    "fuente": evidencia.fuente.title(),
                    "año_publicacion": evidencia.año_publicacion,
                    "tipo_evidencia": evidencia.nivel_evidencia,
                    "url": evidencia.url,
                    "relevancia_score": evidencia.relevancia_score,
                    "cita_apa": evidencia.cita_apa
                })
            
            # Registrar métricas
            metrics_collector.record_search_coverage(
                len(resultados), 
                len(analisis_nlp.get("terminos_clave", []))
            )
            
            # Finalizar trazabilidad
            metricas = {
                "num_resultados": len(papers_encontrados),
                "relevancia_promedio": sum(r["relevancia_score"] for r in papers_encontrados) / len(papers_encontrados) if papers_encontrados else 0
            }
            rag_tracing.end_trace(trace_id, {"papers": papers_encontrados}, metricas)
            
            return jsonify({
                "success": True,
                "papers_encontrados": papers_encontrados,
                "total_papers": len(papers_encontrados),
                "fuentes_consultadas": ["PubMed", "Europe PMC", "Sistema Unificado"],
                "mensaje": f"Encontrados {len(papers_encontrados)} artículos científicos relevantes",
                "metricas": metricas
            })
            
        except Exception as e:
            rag_tracing.end_trace(trace_id, {}, {"error": str(e)})
            raise e

    except Exception as e:
        logger.error(f"❌ Error en búsqueda científica mejorada: {e}")
        return jsonify({"success": False, "message": f"Error en búsqueda: {str(e)}"}), 500
'''
    
    # Reemplazar la función existente
    content = re.sub(search_pattern, new_search_function, content, flags=re.DOTALL)
    
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Función de búsqueda científica actualizada")
    return True


def update_copilot_functions():
    """Actualiza las funciones del copilot"""
    
    app_py_path = Path("app.py")
    if not app_py_path.exists():
        return False
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar funciones del copilot
    copilot_pattern = r'def copilot_chat\(\):.*?return jsonify\(.*?\)'
    
    new_copilot_function = '''
def copilot_chat():
    """Chat del copilot mejorado con sistema unificado"""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"success": False, "message": "Mensaje requerido"}), 400

        message = data["message"]
        logger.info(f"🤖 Copilot mejorado: {message}")

        # Iniciar trazabilidad
        trace_id = rag_tracing.start_trace(f"copilot_chat: {message}")
        
        try:
            # Sistema de copilot unificado
            copilot = UnifiedCopilotAssistant()
            respuesta = copilot.procesar_consulta(message)
            
            # Registrar métricas
            metrics_collector.record_metric("copilot_queries", 1.0)
            
            # Finalizar trazabilidad
            metricas = {
                "longitud_respuesta": len(respuesta),
                "tiempo_procesamiento": 0.5  # Simulado
            }
            rag_tracing.end_trace(trace_id, {"respuesta": respuesta}, metricas)
            
            return jsonify({
                "success": True,
                "response": respuesta,
                "source": "Sistema Unificado de Copilot"
            })
            
        except Exception as e:
            rag_tracing.end_trace(trace_id, {}, {"error": str(e)})
            raise e

    except Exception as e:
        logger.error(f"❌ Error en copilot mejorado: {e}")
        return jsonify({"success": False, "message": f"Error en copilot: {str(e)}"}), 500
'''
    
    # Reemplazar la función existente
    content = re.sub(copilot_pattern, new_copilot_function, content, flags=re.DOTALL)
    
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Funciones del copilot actualizadas")
    return True


def add_orchestration_endpoint():
    """Agrega endpoint para el sistema de orquestación"""
    
    app_py_path = Path("app.py")
    if not app_py_path.exists():
        return False
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el final del archivo para agregar el nuevo endpoint
    new_endpoint = '''

@app.route("/api/orchestration/query", methods=["POST"])
@login_required
def orchestration_query():
    """Endpoint para consultas con sistema de orquestación completo"""
    try:
        data = request.get_json()
        if not data or "consulta" not in data:
            return jsonify({"success": False, "message": "Consulta requerida"}), 400

        consulta = data["consulta"]
        logger.info(f"🎯 Orquestación completa para: {consulta}")

        # Iniciar trazabilidad
        trace_id = rag_tracing.start_trace(consulta)
        
        try:
            # Sistema de orquestación completo
            orchestration_system = UnifiedOrchestrationSystem()
            
            # Análisis NLP
            nlp_processor = UnifiedNLPProcessor()
            analisis_nlp = nlp_processor.procesar_texto(consulta)
            
            # Ejecutar pipeline completo
            resultado = orchestration_system.ejecutar_pipeline_completo(consulta, analisis_nlp)
            
            # Procesar resultado
            respuesta_final = {
                "consulta": consulta,
                "terminos_pico": resultado.terminos_busqueda,
                "resultados_encontrados": len(resultado.resultados_recuperados),
                "chunks_procesados": len(resultado.chunks_procesados),
                "oraciones_con_evidencia": len(resultado.resumen_final.oraciones_con_evidencia),
                "mapeos_citas": len(resultado.mapeo_oracion_cita),
                "tiempo_total": resultado.tiempo_total,
                "estadisticas": resultado.estadisticas
            }
            
            # Registrar métricas
            metrics_collector.record_metric("orchestration_queries", 1.0)
            metrics_collector.record_latency("orchestration", resultado.tiempo_total)
            
            # Finalizar trazabilidad
            rag_tracing.end_trace(trace_id, respuesta_final, resultado.estadisticas)
            
            return jsonify({
                "success": True,
                "resultado": respuesta_final,
                "source": "Sistema de Orquestación RAG Clínico"
            })
            
        except Exception as e:
            rag_tracing.end_trace(trace_id, {}, {"error": str(e)})
            raise e

    except Exception as e:
        logger.error(f"❌ Error en orquestación: {e}")
        return jsonify({"success": False, "message": f"Error en orquestación: {str(e)}"}), 500


@app.route("/api/metrics/report", methods=["GET"])
@login_required
def get_metrics_report():
    """Obtiene reporte de métricas del sistema"""
    try:
        report = metrics_collector.generate_report()
        return jsonify({
            "success": True,
            "report": report
        })
    except Exception as e:
        logger.error(f"❌ Error obteniendo métricas: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@app.route("/api/tracing/export", methods=["GET"])
@login_required
def export_traces():
    """Exporta traces para análisis"""
    try:
        filename = rag_tracing.export_traces()
        return jsonify({
            "success": True,
            "filename": filename,
            "message": "Traces exportados exitosamente"
        })
    except Exception as e:
        logger.error(f"❌ Error exportando traces: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
'''
    
    # Agregar al final del archivo
    content += new_endpoint
    
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Endpoints de orquestación y métricas agregados")
    return True


def main():
    """Función principal de integración"""
    print("🚀 Integrando sistemas mejorados en app.py...")
    
    # Crear backup
    app_py_path = Path("app.py")
    if app_py_path.exists():
        backup_path = Path("app_backup_before_integration.py")
        with open(app_py_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_content)
        print(f"✅ Backup creado: {backup_path}")
    
    # Ejecutar integraciones
    steps = [
        ("Actualizando importaciones", update_imports_in_app_py),
        ("Actualizando funciones de búsqueda", update_search_functions),
        ("Actualizando funciones del copilot", update_copilot_functions),
        ("Agregando endpoints de orquestación", add_orchestration_endpoint),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔧 {step_name}...")
        try:
            if step_func():
                print(f"   ✅ {step_name} completado")
            else:
                print(f"   ❌ {step_name} falló")
        except Exception as e:
            print(f"   ❌ Error en {step_name}: {e}")
    
    print("\n🎉 Integración completada!")
    print("📋 Nuevos endpoints disponibles:")
    print("   - POST /api/orchestration/query - Sistema de orquestación completo")
    print("   - GET /api/metrics/report - Reporte de métricas")
    print("   - GET /api/tracing/export - Exportar traces")


if __name__ == "__main__":
    main() 