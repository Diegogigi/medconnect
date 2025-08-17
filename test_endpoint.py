#!/usr/bin/env python3
"""
Script para probar el endpoint y verificar la integración de MedlinePlus
"""

import requests
import json


def test_endpoint():
    """Prueba el endpoint analyze-enhanced"""

    url = "http://localhost:5000/api/copilot/analyze-enhanced"

    # Datos de prueba
    data = {
        "consulta": "dolor de rodilla",
        "contexto_clinico": {
            "motivoConsulta": "Dolor en rodilla",
            "tipoAtencion": "Fisioterapia",
        },
    }

    headers = {"Content-Type": "application/json"}

    try:
        print("🔍 Probando endpoint:", url)
        print("📝 Datos enviados:", json.dumps(data, indent=2))

        response = requests.post(url, json=data, headers=headers, timeout=30)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")

        # Mostrar respuesta raw
        print(f"📝 Respuesta raw (primeros 500 caracteres):")
        print(response.text[:500])
        print("...")

        if response.status_code == 200:
            try:
                result = response.json()

                print("✅ Respuesta JSON parseada exitosamente!")
                print(f"📋 Success: {result.get('success', 'N/A')}")

                # Verificar evidencia
                evidence = result.get("evidence", [])
                print(f"📚 Evidencia encontrada: {len(evidence)} papers")

                # Verificar análisis clínico
                clinical = result.get("clinical_analysis", {})
                print(f"🏥 Análisis clínico: {'Presente' if clinical else 'Ausente'}")

                # Verificar educación del paciente (MedlinePlus)
                patient_education = result.get("patient_education", {})
                education_available = result.get("education_available", False)

                print(
                    f"📚 Educación del paciente: {'Presente' if patient_education else 'Ausente'}"
                )
                print(f"📋 Education available: {education_available}")

                if patient_education:
                    print("📖 Detalles de educación del paciente:")
                    print(f"   Título: {patient_education.get('title', 'N/A')}")
                    print(
                        f"   Contenido: {patient_education.get('content', 'N/A')[:100]}..."
                    )
                    print(f"   URL: {patient_education.get('url', 'N/A')}")
                    print(
                        f"   Show panel: {patient_education.get('show_panel', False)}"
                    )
                    print(f"   Fuente: {patient_education.get('source', 'N/A')}")
                else:
                    print("❌ No se encontró información de educación del paciente")

                # Verificar estructura completa
                print("\n📋 Estructura de respuesta:")
                for key in result.keys():
                    print(f"   ✅ {key}: {type(result[key]).__name__}")

            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
                print(f"📝 Respuesta completa: {response.text}")

        else:
            print(f"❌ Error en la respuesta: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: El servidor no está corriendo en localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Timeout: La respuesta tardó demasiado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_endpoint()
