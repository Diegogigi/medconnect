#!/usr/bin/env python3
"""
Script para analizar el estado de las 4 IAs y la integración de MedlinePlus
"""

import os
import re


def analizar_ias_principales():
    """Analiza las 4 IAs principales del sistema"""

    print("🤖 ANALIZANDO LAS 4 IAs PRINCIPALES DEL SISTEMA")
    print("=" * 60)

    # Definir las 4 IAs principales según la documentación
    ias_principales = {
        "unified_copilot_assistant": {
            "nombre": "Unified Copilot Assistant",
            "descripcion": "Asistencia integral + Chat + Orquestación",
            "archivos": [
                "unified_copilot_assistant_enhanced.py",
                "unified_copilot_assistant.py",
                "copilot_health.py",
            ],
        },
        "unified_scientific_search": {
            "nombre": "Unified Scientific Search",
            "descripcion": "PubMed + Europe PMC + NCBI + RAG",
            "archivos": [
                "unified_scientific_search_enhanced.py",
                "unified_scientific_search.py",
                "medical_rag_system.py",
                "medical_apis_integration.py",
            ],
        },
        "unified_nlp_processor": {
            "nombre": "Unified NLP Processor",
            "descripcion": "NLP + Patrones + Análisis clínico",
            "archivos": [
                "unified_nlp_processor_main.py",
                "unified_nlp_processor.py",
                "medical_nlp_processor.py",
                "clinical_pattern_analyzer.py",
            ],
        },
        "system_coordinator": {
            "nombre": "System Coordinator",
            "descripcion": "Coordinación y gestión de recursos",
            "archivos": [
                "unified_orchestration_system.py",
                "metrics_system.py",
                "rag_tracing_system.py",
            ],
        },
    }

    estado_ias = {}

    for ia_key, ia_info in ias_principales.items():
        print(f"\n🔍 Analizando: {ia_info['nombre']}")
        print(f"   Descripción: {ia_info['descripcion']}")

        archivos_encontrados = []
        archivos_faltantes = []

        for archivo in ia_info["archivos"]:
            if os.path.exists(archivo):
                archivos_encontrados.append(archivo)
                print(f"   ✅ {archivo}")
            else:
                archivos_faltantes.append(archivo)
                print(f"   ❌ {archivo} (NO ENCONTRADO)")

        estado_ias[ia_key] = {
            "encontrados": len(archivos_encontrados),
            "total": len(ia_info["archivos"]),
            "archivos_encontrados": archivos_encontrados,
            "archivos_faltantes": archivos_faltantes,
        }

        if archivos_encontrados:
            print(
                f"   📊 Estado: {len(archivos_encontrados)}/{len(ia_info['archivos'])} archivos presentes"
            )
        else:
            print(f"   ⚠️ ADVERTENCIA: Ningún archivo encontrado para esta IA")

    return estado_ias


def analizar_integracion_medlineplus():
    """Analiza la integración de MedlinePlus"""

    print("\n🏥 ANALIZANDO INTEGRACIÓN DE MEDLINEPLUS")
    print("=" * 60)

    # Archivos relacionados con MedlinePlus
    archivos_medlineplus = ["medlineplus_integration.py", "mesh_integration.py"]

    # Verificar archivos principales
    for archivo in archivos_medlineplus:
        if os.path.exists(archivo):
            print(f"✅ {archivo} - ENCONTRADO")

            # Verificar contenido básico
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            if "class" in contenido and "def" in contenido:
                print(f"   📋 Contiene clases y funciones")
            else:
                print(f"   ⚠️ Archivo vacío o sin funcionalidad")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")

    # Verificar integración en sistemas principales
    sistemas_con_medlineplus = [
        "unified_orchestration_system.py",
        "unified_scientific_search_enhanced.py",
        "app.py",
    ]

    print(f"\n🔗 Verificando integración en sistemas principales:")

    for sistema in sistemas_con_medlineplus:
        if os.path.exists(sistema):
            with open(sistema, "r", encoding="utf-8") as f:
                contenido = f.read()

            if "medlineplus" in contenido.lower():
                print(f"✅ {sistema} - Integración MedlinePlus detectada")
            elif "mesh" in contenido.lower():
                print(f"✅ {sistema} - Integración MeSH detectada")
            else:
                print(f"❌ {sistema} - Sin integración MedlinePlus detectada")
        else:
            print(f"⚠️ {sistema} - Archivo no encontrado")


def verificar_endpoints_api():
    """Verifica los endpoints de API relacionados con las IAs"""

    print("\n🌐 VERIFICANDO ENDPOINTS DE API")
    print("=" * 60)

    if os.path.exists("app.py"):
        with open("app.py", "r", encoding="utf-8") as f:
            contenido = f.read()

        # Buscar endpoints relacionados con IAs
        endpoints_ia = [
            r'@app\.route\("/api/copilot/chat"',
            r'@app\.route\("/api/copilot/analyze"',
            r'@app\.route\("/api/copilot/orchestrate"',
            r'@app\.route\("/api/copilot/analyze-enhanced"',
            r'@app\.route\("/api/scientific/search"',
            r'@app\.route\("/api/nlp/process"',
        ]

        endpoints_encontrados = []

        for endpoint in endpoints_ia:
            if re.search(endpoint, contenido):
                endpoints_encontrados.append(endpoint)
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - NO ENCONTRADO")

        return len(endpoints_encontrados)
    else:
        print("❌ app.py no encontrado")
        return 0


def verificar_frontend_integration():
    """Verifica la integración en el frontend"""

    print("\n🎨 VERIFICANDO INTEGRACIÓN FRONTEND")
    print("=" * 60)

    archivos_frontend = [
        "static/js/professional.js",
        "static/js/unified-ai-integration.js",
        "templates/professional.html",
    ]

    for archivo in archivos_frontend:
        if os.path.exists(archivo):
            print(f"✅ {archivo} - ENCONTRADO")

            # Verificar integración básica
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            if "copilot" in contenido.lower() or "ia" in contenido.lower():
                print(f"   🔗 Contiene referencias a IA/Copilot")
            else:
                print(f"   ⚠️ Sin referencias claras a IA")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")


def generar_resumen_estado():
    """Genera un resumen del estado actual"""

    print("\n📊 RESUMEN DEL ESTADO ACTUAL")
    print("=" * 60)

    # Analizar IAs
    estado_ias = analizar_ias_principales()

    # Contar IAs funcionales
    ias_funcionales = 0
    total_archivos_ias = 0
    archivos_encontrados_ias = 0

    for ia_key, estado in estado_ias.items():
        if estado["encontrados"] > 0:
            ias_funcionales += 1
        total_archivos_ias += estado["total"]
        archivos_encontrados_ias += estado["encontrados"]

    # Analizar MedlinePlus
    analizar_integracion_medlineplus()

    # Verificar endpoints
    endpoints_encontrados = verificar_endpoints_api()

    # Verificar frontend
    verificar_frontend_integration()

    # Resumen final
    print(f"\n🎯 RESUMEN FINAL:")
    print(f"   🤖 IAs Funcionales: {ias_funcionales}/4")
    print(f"   📁 Archivos IA: {archivos_encontrados_ias}/{total_archivos_ias}")
    print(f"   🌐 Endpoints API: {endpoints_encontrados}")
    print(
        f"   🏥 MedlinePlus: {'✅ Integrado' if os.path.exists('medlineplus_integration.py') else '❌ No encontrado'}"
    )

    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")

    if ias_funcionales < 4:
        print(f"   ⚠️ Algunas IAs no están completamente implementadas")
        print(f"   🔧 Revisar archivos faltantes para completar la integración")

    if not os.path.exists("medlineplus_integration.py"):
        print(f"   ⚠️ MedlinePlus no está integrado")
        print(
            f"   🔧 Implementar integración de MedlinePlus para educación del paciente"
        )

    if endpoints_encontrados < 3:
        print(f"   ⚠️ Faltan endpoints de API")
        print(f"   🔧 Verificar que todos los endpoints estén implementados")


if __name__ == "__main__":
    print("🚀 Análisis Completo de IAs y MedlinePlus")
    print("=" * 60)

    generar_resumen_estado()
