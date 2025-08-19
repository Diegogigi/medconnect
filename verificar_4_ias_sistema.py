#!/usr/bin/env python3
"""
Script para verificar el estado de las 4 IAs principales del sistema
"""

import os
import importlib.util
from datetime import datetime


def verificar_ia(ia_name, archivos, descripcion):
    """Verificar si una IA está disponible y funcionando"""
    print(f"\n🤖 Verificando {ia_name}")
    print("=" * 50)
    print(f"📋 Descripción: {descripcion}")

    archivos_encontrados = []
    archivos_faltantes = []

    for archivo in archivos:
        if os.path.exists(archivo):
            archivos_encontrados.append(archivo)
            print(f"✅ {archivo}")
        else:
            archivos_faltantes.append(archivo)
            print(f"❌ {archivo} - NO ENCONTRADO")

    # Intentar importar el archivo principal
    archivo_principal = archivos[0] if archivos else None
    importacion_exitosa = False

    if archivo_principal and os.path.exists(archivo_principal):
        try:
            # Extraer nombre del módulo sin extensión
            modulo_nombre = archivo_principal.replace(".py", "")

            # Intentar importar
            spec = importlib.util.spec_from_file_location(
                modulo_nombre, archivo_principal
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                importacion_exitosa = True
                print(f"✅ Importación exitosa: {archivo_principal}")
            else:
                print(f"❌ No se pudo importar: {archivo_principal}")
        except Exception as e:
            print(f"❌ Error importando {archivo_principal}: {e}")

    return {
        "nombre": ia_name,
        "archivos_encontrados": archivos_encontrados,
        "archivos_faltantes": archivos_faltantes,
        "importacion_exitosa": importacion_exitosa,
        "total_archivos": len(archivos),
        "archivos_ok": len(archivos_encontrados),
    }


def verificar_integracion_app():
    """Verificar la integración en app.py"""
    print(f"\n🔧 Verificando integración en app.py")
    print("=" * 50)

    if not os.path.exists("app.py"):
        print("❌ app.py no encontrado")
        return False

    try:
        with open("app.py", "r", encoding="utf-8") as f:
            contenido = f.read()

        # Buscar referencias a las IAs
        referencias = {
            "unified_copilot_assistant": "Unified Copilot Assistant",
            "unified_scientific_search": "Unified Scientific Search",
            "unified_nlp_processor": "Unified NLP Processor",
            "unified_orchestration_system": "Unified Orchestration System",
            "copilot_health": "Copilot Health",
            "medical_rag_system": "Medical RAG System",
            "medical_apis_integration": "Medical APIs Integration",
        }

        encontradas = []
        faltantes = []

        for referencia, nombre in referencias.items():
            if referencia in contenido:
                encontradas.append(nombre)
                print(f"✅ {nombre} - Referenciado en app.py")
            else:
                faltantes.append(nombre)
                print(f"❌ {nombre} - NO referenciado en app.py")

        return {
            "encontradas": encontradas,
            "faltantes": faltantes,
            "total": len(referencias),
        }

    except Exception as e:
        print(f"❌ Error leyendo app.py: {e}")
        return False


def verificar_endpoints_api():
    """Verificar endpoints de API relacionados con las IAs"""
    print(f"\n🔌 Verificando endpoints de API")
    print("=" * 50)

    if not os.path.exists("app.py"):
        print("❌ app.py no encontrado")
        return False

    try:
        with open("app.py", "r", encoding="utf-8") as f:
            contenido = f.read()

        # Buscar endpoints relacionados con IAs
        endpoints = [
            "/api/copilot/chat",
            "/api/copilot/orchestrate",
            "/api/copilot/analyze-enhanced",
            "/api/search-scientific-papers",
            "/api/nlp/process",
            "/api/medical/search",
        ]

        encontrados = []
        faltantes = []

        for endpoint in endpoints:
            if endpoint in contenido:
                encontrados.append(endpoint)
                print(f"✅ {endpoint}")
            else:
                faltantes.append(endpoint)
                print(f"❌ {endpoint} - NO ENCONTRADO")

        return {
            "encontrados": encontrados,
            "faltantes": faltantes,
            "total": len(endpoints),
        }

    except Exception as e:
        print(f"❌ Error verificando endpoints: {e}")
        return False


def main():
    """Función principal"""
    print("🤖 Verificación de las 4 IAs Principales del Sistema")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Definir las 4 IAs principales
    ias_principales = {
        "unified_copilot_assistant": {
            "nombre": "Unified Copilot Assistant",
            "descripcion": "Asistencia integral + Chat + Orquestación",
            "archivos": [
                "unified_copilot_assistant.py",
                "unified_copilot_assistant_enhanced.py",
                "copilot_health.py",
            ],
        },
        "unified_scientific_search": {
            "nombre": "Unified Scientific Search",
            "descripcion": "PubMed + Europe PMC + NCBI + RAG",
            "archivos": [
                "unified_scientific_search.py",
                "unified_scientific_search_enhanced.py",
                "medical_rag_system.py",
                "medical_apis_integration.py",
            ],
        },
        "unified_nlp_processor": {
            "nombre": "Unified NLP Processor",
            "descripcion": "NLP + Patrones + Análisis clínico",
            "archivos": [
                "unified_nlp_processor.py",
                "unified_nlp_processor_main.py",
                "medical_nlp_processor.py",
                "clinical_pattern_analyzer.py",
            ],
        },
        "unified_orchestration_system": {
            "nombre": "Unified Orchestration System",
            "descripcion": "Coordinación y gestión de recursos",
            "archivos": [
                "unified_orchestration_system.py",
                "metrics_system.py",
                "rag_tracing_system.py",
            ],
        },
    }

    # Verificar cada IA
    resultados_ias = {}
    for ia_key, ia_info in ias_principales.items():
        resultado = verificar_ia(
            ia_info["nombre"], ia_info["archivos"], ia_info["descripcion"]
        )
        resultados_ias[ia_key] = resultado

    # Verificar integración en app.py
    resultado_integracion = verificar_integracion_app()

    # Verificar endpoints de API
    resultado_endpoints = verificar_endpoints_api()

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 60)

    total_ias = len(ias_principales)
    ias_funcionando = 0
    archivos_totales = 0
    archivos_ok = 0

    for ia_key, resultado in resultados_ias.items():
        if resultado["archivos_ok"] > 0:
            ias_funcionando += 1
        archivos_totales += resultado["total_archivos"]
        archivos_ok += resultado["archivos_ok"]

    print(f"🤖 IAs Principales: {ias_funcionando}/{total_ias} funcionando")
    print(f"📁 Archivos: {archivos_ok}/{archivos_totales} encontrados")

    if resultado_integracion:
        print(
            f"🔧 Integración: {len(resultado_integracion['encontradas'])}/{resultado_integracion['total']} referencias en app.py"
        )

    if resultado_endpoints:
        print(
            f"🔌 Endpoints: {len(resultado_endpoints['encontrados'])}/{resultado_endpoints['total']} disponibles"
        )

    print("\n🔧 PROBLEMAS DETECTADOS:")

    # Verificar problemas específicos
    problemas = []

    for ia_key, resultado in resultados_ias.items():
        if resultado["archivos_ok"] == 0:
            problemas.append(f"❌ {resultado['nombre']}: No se encontraron archivos")
        elif resultado["archivos_ok"] < resultado["total_archivos"]:
            problemas.append(
                f"⚠️ {resultado['nombre']}: Faltan {len(resultado['archivos_faltantes'])} archivos"
            )

    if resultado_integracion and len(resultado_integracion["faltantes"]) > 0:
        problemas.append(
            f"⚠️ Integración: {len(resultado_integracion['faltantes'])} IAs no referenciadas en app.py"
        )

    if resultado_endpoints and len(resultado_endpoints["faltantes"]) > 0:
        problemas.append(
            f"⚠️ Endpoints: {len(resultado_endpoints['faltantes'])} endpoints no encontrados"
        )

    if problemas:
        for problema in problemas:
            print(f"   {problema}")
    else:
        print("   ✅ No se detectaron problemas")

    print("\n💡 RECOMENDACIONES:")

    if ias_funcionando < total_ias:
        print("   1. Verificar que todos los archivos de las IAs estén presentes")
        print("   2. Asegurar que las importaciones funcionen correctamente")

    if resultado_integracion and len(resultado_integracion["faltantes"]) > 0:
        print("   3. Integrar las IAs faltantes en app.py")

    if resultado_endpoints and len(resultado_endpoints["faltantes"]) > 0:
        print("   4. Implementar los endpoints de API faltantes")

    print("   5. Verificar que la API key de OpenRouter esté configurada correctamente")
    print("   6. Probar la funcionalidad de cada IA individualmente")

    print("=" * 60)


if __name__ == "__main__":
    main()
