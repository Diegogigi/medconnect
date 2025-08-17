#!/usr/bin/env python3
"""
Script de prueba final para el análisis unificado
"""

import requests
import json
import time


def test_analysis():
    """Prueba el análisis unificado"""

    print("🧪 Probando análisis unificado...")

    # Datos de prueba
    test_data = {
        "consulta": "Paciente con dolor en la rodilla derecha después de un golpe en el trabajo",
        "contexto_clinico": {
            "motivoConsulta": "Dolor en rodilla derecha",
            "sintomasPrincipales": "Dolor, inflamación, dificultad para caminar",
            "antecedentesMedicos": "Sin antecedentes relevantes",
            "medicamentosActuales": "Ninguno",
            "alergias": "Ninguna conocida",
            "examenFisico": "Rodilla derecha inflamada y dolorosa",
            "diagnosticoPresuntivo": "Trauma en rodilla",
            "planTratamiento": "Evaluación por traumatología",
        },
    }

    try:
        print("📡 Enviando petición al endpoint...")

        # Enviar petición
        response = requests.post(
            "http://localhost:5000/api/copilot/analyze-enhanced",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis exitoso")

            # Mostrar resultados de manera estructurada
            print("\n📋 RESULTADOS DEL ANÁLISIS:")
            print("=" * 50)

            if result.get("success"):
                print("✅ Análisis completado exitosamente")

                # NLP Analysis
                nlp = result.get("nlp_analysis", {})
                print(f"\n🧠 ANÁLISIS NLP:")
                print(f"   Palabras clave: {nlp.get('palabras_clave', [])}")
                print(f"   Síntomas: {nlp.get('sintomas', [])}")
                print(f"   Entidades: {nlp.get('entidades', [])}")
                print(f"   Confianza: {nlp.get('confianza', 0)}")

                # Evidence
                evidence = result.get("evidence", [])
                print(f"\n🔬 EVIDENCIA CIENTÍFICA ({len(evidence)} artículos):")
                for i, ev in enumerate(evidence[:3], 1):
                    print(f"   {i}. {ev.get('titulo', 'Sin título')}")
                    print(f"      DOI: {ev.get('doi', 'Sin DOI')}")
                    print(f"      Año: {ev.get('year', 'N/A')}")

                # Clinical Analysis
                clinical = result.get("clinical_analysis", {})
                print(f"\n💡 ANÁLISIS CLÍNICO:")
                print(f"   Recomendaciones: {clinical.get('recomendaciones', [])}")
                print(f"   Patologías: {clinical.get('patologias', [])}")
                print(f"   Escalas: {clinical.get('escalas', [])}")

                return True
            else:
                print(
                    f"❌ Error en análisis: {result.get('message', 'Error desconocido')}"
                )
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Timeout - El análisis tardó demasiado")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - Verifica que el servidor esté ejecutándose")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_simple_analysis():
    """Prueba un análisis simple"""

    print("\n🧪 Probando análisis simple...")

    simple_data = {
        "consulta": "Dolor de cabeza intenso",
        "contexto_clinico": {
            "motivoConsulta": "Dolor de cabeza",
            "sintomasPrincipales": "Dolor intenso, náuseas",
        },
    }

    try:
        response = requests.post(
            "http://localhost:5000/api/copilot/analyze-enhanced",
            json=simple_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis simple exitoso")
            return True
        else:
            print(f"❌ Error en análisis simple: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error en análisis simple: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 Iniciando pruebas del análisis unificado...")

    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Servidor ejecutándose")
    except:
        print("❌ Servidor no disponible")
        print("💡 Ejecuta: python app.py")
        return

    # Ejecutar pruebas
    test1 = test_analysis()
    test2 = test_simple_analysis()

    print("\n📊 RESUMEN DE PRUEBAS:")
    print("=" * 30)
    print(f"   Análisis completo: {'✅ PASÓ' if test1 else '❌ FALLÓ'}")
    print(f"   Análisis simple: {'✅ PASÓ' if test2 else '❌ FALLÓ'}")

    if test1 and test2:
        print("\n🎉 ¡Todas las pruebas pasaron!")
        print("✅ El análisis unificado está funcionando correctamente")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
        print("🔧 Revisa los logs del servidor para más detalles")


if __name__ == "__main__":
    main()
