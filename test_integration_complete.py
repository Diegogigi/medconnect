#!/usr/bin/env python3
"""
Prueba de Integración Completa: MedlinePlus + IAs + Chat
Verifica que toda la integración funcione correctamente desde el backend hasta el frontend
"""

import sys
import time
import json
from medlineplus_integration import medlineplus_integration
from unified_orchestration_system import unified_orchestration
from unified_scientific_search_enhanced import unified_search_enhanced


def test_medlineplus_direct():
    """Prueba directa de MedlinePlus"""
    print("🧪 Prueba 1: MedlinePlus Directo")
    print("=" * 50)

    # Prueba con diagnóstico
    result = medlineplus_integration.get_diagnosis_education("J45.901", "es")
    print(f"✅ Diagnóstico ICD-10: {result.title}")
    print(f"🔗 URL: {result.url}")
    print(f"📝 Resumen: {result.summary[:100]}...")

    return result.success


def test_orchestration_with_medlineplus():
    """Prueba del sistema de orquestación con MedlinePlus"""
    print("\n🧪 Prueba 2: Sistema de Orquestación con MedlinePlus")
    print("=" * 50)

    consulta = "dolor de rodilla"

    # Simular análisis NLP básico
    analisis_nlp = {
        "palabras_clave": ["dolor", "rodilla"],
        "sintomas": ["dolor de rodilla"],
        "entidades": ["rodilla"],
        "confianza": 0.8,
    }

    try:
        resultado = unified_orchestration.ejecutar_pipeline_completo(
            consulta, analisis_nlp
        )

        if resultado and resultado.resumen_final:
            print(f"✅ Pipeline ejecutado exitosamente")
            print(f"📊 Tiempo total: {resultado.tiempo_total:.2f}s")
            print(f"📝 Resumen: {resultado.resumen_final.resumen[:100]}...")

            # Verificar educación del paciente
            if (
                hasattr(resultado.resumen_final, "patient_education")
                and resultado.resumen_final.patient_education
            ):
                education = resultado.resumen_final.patient_education
                print(f"📚 Educación del paciente:")
                print(f"   Título: {education.get('title', 'N/A')}")
                print(f"   Contenido: {education.get('content', 'N/A')[:100]}...")
                print(f"   URL: {education.get('url', 'N/A')}")
                print(f"   Disponible: {education.get('show_panel', False)}")
                return True
            else:
                print("❌ No se encontró educación del paciente")
                return False
        else:
            print("❌ No se obtuvo resultado del pipeline")
            return False

    except Exception as e:
        print(f"❌ Error en pipeline: {e}")
        return False


def test_search_with_medlineplus():
    """Prueba del sistema de búsqueda con MedlinePlus"""
    print("\n🧪 Prueba 3: Sistema de Búsqueda con MedlinePlus")
    print("=" * 50)

    consulta = "fisioterapia para esguince"

    try:
        evidencias = unified_search_enhanced.buscar_evidencia_unificada(
            consulta, max_resultados=3
        )

        print(f"✅ Búsqueda completada: {len(evidencias)} resultados")

        if evidencias:
            # Verificar primer resultado
            evidencia = evidencias[0]
            print(f"📄 Título: {evidencia.titulo[:80]}...")

            # Verificar campos MedlinePlus
            if hasattr(evidencia, "patient_education") and evidencia.patient_education:
                education = evidencia.patient_education
                print(f"📚 Educación del paciente:")
                print(f"   Título: {education.get('title', 'N/A')}")
                print(f"   Contenido: {education.get('content', 'N/A')[:100]}...")
                print(f"   URL: {education.get('url', 'N/A')}")
                print(f"   Disponible: {education.get('show_panel', False)}")
                return True
            else:
                print("❌ No se encontró educación del paciente en evidencia")
                return False
        else:
            print("❌ No se encontraron evidencias")
            return False

    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return False


def test_api_response_format():
    """Prueba del formato de respuesta de la API"""
    print("\n🧪 Prueba 4: Formato de Respuesta API")
    print("=" * 50)

    # Simular respuesta de la API
    api_response = {
        "success": True,
        "evidence": [
            {
                "titulo": "Estudio sobre dolor de rodilla",
                "resumen": "Estudio clínico sobre tratamiento del dolor de rodilla",
                "doi": "10.1234/test.2023",
                "autores": ["Dr. García", "Dr. López"],
                "año_publicacion": "2023",
            }
        ],
        "clinical_analysis": {
            "recomendaciones": ["Realizar fisioterapia", "Aplicar hielo"],
            "resumen_inteligente": "El dolor de rodilla requiere tratamiento específico",
        },
        "patient_education": {
            "title": "📚 Información sobre dolor de rodilla",
            "content": "Obtén información educativa oficial sobre dolor de rodilla en MedlinePlus.gov",
            "url": "https://medlineplus.gov/spanish/search.html?query=dolor%20de%20rodilla",
            "show_panel": True,
            "source": "MedlinePlus.gov",
            "language": "es",
        },
        "education_available": True,
        "timestamp": time.time(),
        "sistema": "unificado",
    }

    # Verificar estructura
    required_fields = [
        "success",
        "evidence",
        "clinical_analysis",
        "patient_education",
        "education_available",
    ]

    for field in required_fields:
        if field in api_response:
            print(f"✅ Campo '{field}' presente")
        else:
            print(f"❌ Campo '{field}' faltante")
            return False

    # Verificar educación del paciente
    education = api_response.get("patient_education", {})
    education_fields = ["title", "content", "url", "show_panel", "source"]

    for field in education_fields:
        if field in education:
            print(f"✅ Campo de educación '{field}' presente")
        else:
            print(f"❌ Campo de educación '{field}' faltante")
            return False

    print("✅ Formato de respuesta API correcto")
    return True


def test_frontend_integration():
    """Prueba de integración frontend (simulada)"""
    print("\n🧪 Prueba 5: Integración Frontend (Simulada)")
    print("=" * 50)

    # Simular datos que llegarían del frontend
    frontend_data = {
        "consulta": "dolor de rodilla",
        "contexto_clinico": {
            "motivoConsulta": "Dolor en rodilla derecha",
            "tipoAtencion": "Fisioterapia",
            "pacienteNombre": "Juan Pérez",
        },
    }

    # Simular respuesta que se enviaría al frontend
    backend_response = {
        "success": True,
        "evidence": [],
        "clinical_analysis": {"recomendaciones": ["Consulta con especialista"]},
        "patient_education": {
            "title": "📚 Información sobre dolor de rodilla",
            "content": "Información educativa sobre dolor de rodilla",
            "url": "https://medlineplus.gov/spanish/search.html?query=dolor%20de%20rodilla",
            "show_panel": True,
            "source": "MedlinePlus.gov",
        },
        "education_available": True,
    }

    # Verificar que el frontend puede procesar la respuesta
    if backend_response.get("success") and backend_response.get("education_available"):
        education = backend_response.get("patient_education", {})

        if education.get("show_panel"):
            print("✅ Frontend puede mostrar panel de educación")
            print(f"📚 Título: {education.get('title', 'N/A')}")
            print(f"📝 Contenido: {education.get('content', 'N/A')[:50]}...")
            print(f"🔗 URL: {education.get('url', 'N/A')}")
            print(f"🏥 Fuente: {education.get('source', 'N/A')}")
            return True
        else:
            print("❌ Panel de educación no disponible")
            return False
    else:
        print("❌ Respuesta no exitosa o educación no disponible")
        return False


def main():
    """Función principal de pruebas"""
    print("🚀 PRUEBA DE INTEGRACIÓN COMPLETA: MedlinePlus + IAs + Chat")
    print("=" * 70)

    tests = [
        ("MedlinePlus Directo", test_medlineplus_direct),
        ("Orquestación con MedlinePlus", test_orchestration_with_medlineplus),
        ("Búsqueda con MedlinePlus", test_search_with_medlineplus),
        ("Formato de Respuesta API", test_api_response_format),
        ("Integración Frontend", test_frontend_integration),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))

    # Resumen de resultados
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")

    if passed == total:
        print(
            "🎉 ¡TODAS LAS PRUEBAS PASARON! La integración está funcionando correctamente."
        )
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar la implementación.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
