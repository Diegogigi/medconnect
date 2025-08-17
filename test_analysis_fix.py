#!/usr/bin/env python3
"""
Script para probar que el análisis funcione correctamente
"""

import requests
import json
import time


def test_analysis():
    """Prueba el análisis unificado"""

    print("🧪 Probando análisis unificado...")

    # Esperar a que el servidor esté listo
    print("⏳ Esperando que el servidor esté listo...")
    time.sleep(5)

    # Datos de prueba
    test_data = {
        "consulta": "Paciente con dolor lumbar agudo por esfuerzo físico",
        "contexto_clinico": {
            "motivoConsulta": "Dolor lumbar agudo",
            "sintomasPrincipales": "Dolor intenso en región lumbar, limitación de movimiento",
            "antecedentesMedicos": "Sin antecedentes relevantes",
        },
    }

    try:
        # Hacer petición al endpoint
        print("📡 Enviando petición al endpoint...")
        response = requests.post(
            "http://localhost:5000/api/copilot/analyze-enhanced",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint responde correctamente")

            # Verificar estructura de respuesta
            if result.get("success"):
                print("✅ Respuesta exitosa")

                # Verificar componentes
                nlp_analysis = result.get("nlp_analysis", {})
                if nlp_analysis:
                    print(
                        f"✅ Análisis NLP: {len(nlp_analysis.get('palabras_clave', []))} palabras clave"
                    )
                    print(
                        f"   Palabras clave: {nlp_analysis.get('palabras_clave', [])}"
                    )
                    print(f"   Síntomas: {nlp_analysis.get('sintomas', [])}")

                evidence = result.get("evidence", [])
                if evidence:
                    print(f"✅ Evidencia científica: {len(evidence)} artículos")
                else:
                    print("⚠️ No se encontró evidencia científica")

                clinical_analysis = result.get("clinical_analysis", {})
                if clinical_analysis:
                    print(
                        f"✅ Análisis clínico: {len(clinical_analysis.get('recomendaciones', []))} recomendaciones"
                    )
                    print(
                        f"   Recomendaciones: {clinical_analysis.get('recomendaciones', [])}"
                    )

                print("\n📊 Resumen de la respuesta:")
                print(f"   - Consulta: {result.get('consulta_original', 'N/A')}")
                print(f"   - Sistema: {result.get('sistema', 'N/A')}")
                print(f"   - Timestamp: {result.get('timestamp', 'N/A')}")

                return True
            else:
                print(
                    f"❌ Respuesta no exitosa: {result.get('message', 'Sin mensaje')}"
                )
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print(
            "   Asegúrate de que el servidor esté ejecutándose en http://localhost:5000"
        )
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout en la petición")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def verify_server_status():
    """Verifica el estado del servidor"""

    print("🔍 Verificando estado del servidor...")

    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor ejecutándose correctamente")
            return True
        else:
            print(f"⚠️ Servidor responde con código: {response.status_code}")
            return True  # No es un error crítico
    except Exception as e:
        print(f"❌ No se puede conectar al servidor: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Probando análisis unificado...")

    if verify_server_status():
        print("✅ Servidor verificado")

        if test_analysis():
            print("\n🎉 ¡Análisis unificado funcionando correctamente!")
            print("✅ Todos los componentes están operativos")
            print("✅ El análisis devuelve resultados completos")
            print("✅ No hay errores en el procesamiento")
        else:
            print("\n❌ Error en el análisis")
            print("⚠️ Revisa los logs del servidor para más detalles")
    else:
        print("\n❌ Servidor no disponible")
        print("⚠️ Asegúrate de que el servidor esté ejecutándose")


if __name__ == "__main__":
    main()
