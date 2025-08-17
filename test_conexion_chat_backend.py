#!/usr/bin/env python3
"""
Script para probar la conexión entre el chat y el backend
"""

import requests
import json


def test_conexion_chat_backend():
    """Prueba la conexión entre el chat y el backend"""

    print("🧪 Probando conexión chat-backend...")
    print("=" * 50)

    # URL base
    base_url = "http://localhost:5000"

    # Caso de prueba con datos completos
    caso_prueba = {
        "consulta": "buscar papers sobre dolor de hombro por golpe en el trabajo",
        "contexto_clinico": {
            "motivoConsulta": "Dolor de hombro por golpe en el trabajo",
            "tipoAtencion": "Kinesiología",
            "pacienteNombre": "María González",
            "pacienteEdad": "35",
            "antecedentes": "Golpe en el trabajo hace 2 días",
            "evaluacion": "Dolor en hombro derecho, limitación de movimientos",
            "diagnostico": "Lesión de hombro postraumática",
        },
    }

    print("1️⃣ Probando endpoint de análisis con datos completos...")
    print(f"Consulta: {caso_prueba['consulta']}")
    print(f"Contexto: {caso_prueba['contexto_clinico']['motivoConsulta']}")

    try:
        # Probar endpoint de análisis
        response = requests.post(
            f"{base_url}/api/copilot/analyze-enhanced",
            headers={"Content-Type": "application/json"},
            json=caso_prueba,
            timeout=30,
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa del servidor")

            if data.get("success"):
                print("✅ Análisis completado exitosamente")

                # Verificar evidencia científica
                if "evidence" in data and data["evidence"]:
                    print(f"📚 Papers encontrados: {len(data['evidence'])}")

                    # Mostrar detalles de los primeros 2 papers
                    for i, paper in enumerate(data["evidence"][:2], 1):
                        print(f"\n📄 Paper {i}:")
                        print(
                            f"   Título: {paper.get('titulo', paper.get('title', 'Sin título'))}"
                        )
                        print(
                            f"   Año: {paper.get('año_publicacion', paper.get('year', 'N/A'))}"
                        )
                        print(f"   DOI: {paper.get('doi', 'Sin DOI')}")
                        print(f"   Relevancia: {paper.get('relevancia_score', 0):.2f}")
                else:
                    print("❌ No se encontraron papers científicos")

                # Verificar análisis clínico
                if "clinical_analysis" in data:
                    print("💡 Análisis clínico disponible")
                    if "recomendaciones" in data["clinical_analysis"]:
                        print(
                            f"   Recomendaciones: {len(data['clinical_analysis']['recomendaciones'])}"
                        )
            else:
                print("❌ Análisis falló")
                print(f"Error: {data.get('error', 'Desconocido')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")

    print("\n" + "=" * 50)

    # Probar endpoint de búsqueda específica
    print("2️⃣ Probando endpoint de búsqueda científica...")

    try:
        search_data = {
            "motivo_consulta": "dolor de hombro por golpe en el trabajo",
            "contexto_clinico": {
                "tipoAtencion": "Kinesiología",
                "antecedentes": "Golpe en el trabajo",
            },
        }

        response = requests.post(
            f"{base_url}/api/copilot/search-enhanced",
            headers={"Content-Type": "application/json"},
            json=search_data,
            timeout=30,
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Búsqueda científica exitosa")

            if data.get("success") and data.get("evidence"):
                print(f"📚 Papers encontrados: {len(data['evidence'])}")

                for i, paper in enumerate(data["evidence"][:2], 1):
                    print(f"\n📄 Paper {i}:")
                    print(
                        f"   Título: {paper.get('titulo', paper.get('title', 'Sin título'))}"
                    )
                    print(
                        f"   Año: {paper.get('año_publicacion', paper.get('year', 'N/A'))}"
                    )
                    print(f"   DOI: {paper.get('doi', 'Sin DOI')}")
            else:
                print("❌ No se encontraron papers")
        else:
            print(f"❌ Error HTTP: {response.status_code}")

    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")

    print("\n" + "=" * 50)
    print("📋 Instrucciones para probar en el navegador:")
    print("\n1. Abre la aplicación en el navegador")
    print("2. Completa el formulario con estos datos:")
    print("   - Motivo de consulta: 'Dolor de hombro por golpe en el trabajo'")
    print("   - Tipo de atención: 'Kinesiología'")
    print("   - Datos del paciente")
    print("3. Escribe en el chat: 'buscar papers sobre dolor de hombro'")
    print("4. Verifica en la consola del navegador (F12) los logs")
    print("5. Verifica que se muestren papers científicos específicos")

    print("\n" + "=" * 50)
    print("🎯 Prueba completada")


if __name__ == "__main__":
    test_conexion_chat_backend()
