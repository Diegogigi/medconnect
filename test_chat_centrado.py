#!/usr/bin/env python3
"""
Script para probar el sistema de chat centrado
"""

import requests
import json


def test_chat_centrado():
    """Prueba el sistema de chat centrado"""

    print("🧪 Probando sistema de chat centrado...")
    print("=" * 50)

    # URL base
    base_url = "http://localhost:5000"

    # Casos de prueba para el chat
    casos_prueba = [
        {
            "consulta": "buscar papers sobre dolor de hombro por golpe en el trabajo",
            "contexto_clinico": {
                "motivoConsulta": "Dolor de hombro por golpe en el trabajo",
                "tipoAtencion": "Kinesiología",
                "pacienteNombre": "María González",
                "pacienteEdad": "35",
            },
        },
        {
            "consulta": "analizar el caso de dolor lumbar postraumático",
            "contexto_clinico": {
                "motivoConsulta": "Dolor lumbar postraumático",
                "tipoAtencion": "Kinesiología",
                "pacienteNombre": "Juan Pérez",
                "pacienteEdad": "45",
            },
        },
        {
            "consulta": "recomendar tratamiento para lesión de rodilla",
            "contexto_clinico": {
                "motivoConsulta": "Lesión de rodilla por accidente laboral",
                "tipoAtencion": "Kinesiología",
                "pacienteNombre": "Carlos López",
                "pacienteEdad": "28",
            },
        },
    ]

    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n{i}️⃣ Probando caso: '{caso['consulta']}'")
        print("-" * 50)

        try:
            # Probar endpoint de análisis
            response = requests.post(
                f"{base_url}/api/copilot/analyze-enhanced",
                headers={"Content-Type": "application/json"},
                json=caso,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                print("✅ Respuesta exitosa del servidor")

                if data.get("success"):
                    print("✅ Análisis completado exitosamente")

                    # Verificar evidencia científica
                    if "evidence" in data and data["evidence"]:
                        print(f"📚 Papers encontrados: {len(data['evidence'])}")

                        # Mostrar detalles de los primeros 2 papers
                        for j, paper in enumerate(data["evidence"][:2], 1):
                            print(f"\n📄 Paper {j}:")
                            print(
                                f"   Título: {paper.get('titulo', paper.get('title', 'Sin título'))}"
                            )
                            print(
                                f"   Año: {paper.get('año_publicacion', paper.get('year', 'N/A'))}"
                            )
                            print(f"   DOI: {paper.get('doi', 'Sin DOI')}")
                            print(
                                f"   Relevancia: {paper.get('relevancia_score', 0):.2f}"
                            )
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

        except Exception as e:
            print(f"❌ Error en la prueba: {e}")

    print("\n" + "=" * 50)

    # Instrucciones para el usuario
    print("📋 Instrucciones para probar en el navegador:")
    print("\n1. Abre la aplicación en el navegador")
    print("2. Completa el formulario con datos del paciente")
    print("3. Escribe en el chat uno de estos comandos:")
    print("   • 'buscar papers sobre dolor de hombro'")
    print("   • 'analizar el caso'")
    print("   • 'recomendar tratamiento'")
    print("   • 'evaluar el caso'")
    print("   • 'ayuda'")
    print("\n4. Verifica que las IAs respondan correctamente")

    print("\n" + "=" * 50)
    print("🎯 Prueba completada")


if __name__ == "__main__":
    test_chat_centrado()
