#!/usr/bin/env python3
"""
Script para probar la búsqueda de papers desde el chat
"""

import requests
import json


def test_busqueda_papers_chat():
    """Prueba la búsqueda de papers desde el chat"""

    print("🧪 Probando búsqueda de papers desde el chat...")
    print("=" * 50)

    # URL base
    base_url = "http://localhost:5000"

    # Casos de prueba específicos para búsqueda de papers
    casos_prueba = [
        {
            "consulta": "busca papers de dolor de hombro",
            "contexto_clinico": {
                "motivoConsulta": "Dolor de hombro por golpe",
                "tipoAtencion": "Kinesiología",
            },
        },
        {
            "consulta": "buscar papers sobre dolor de rodilla",
            "contexto_clinico": {
                "motivoConsulta": "Dolor de rodilla por lesión al jugar futbol",
                "tipoAtencion": "Kinesiología",
            },
        },
        {
            "consulta": "evidencia científica de rehabilitación lumbar",
            "contexto_clinico": {
                "motivoConsulta": "Dolor lumbar postraumático",
                "tipoAtencion": "Kinesiología",
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

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("✅ Respuesta exitosa del servidor")

                if data.get("success"):
                    print("✅ Análisis completado exitosamente")

                    # Verificar evidencia científica
                    if "evidence" in data and data["evidence"]:
                        print(f"📚 Papers encontrados: {len(data['evidence'])}")

                        # Mostrar detalles de los primeros 3 papers
                        for j, paper in enumerate(data["evidence"][:3], 1):
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

                            # Verificar cita APA
                            if paper.get("cita_apa"):
                                print(f"   📖 Cita APA: {paper['cita_apa'][:100]}...")
                            else:
                                print(f"   ❌ Sin cita APA")

                            # Verificar DOI
                            if paper.get("doi") and paper["doi"] != "Sin DOI":
                                print(f"   ✅ DOI válido: {paper['doi']}")
                            else:
                                print(f"   ❌ Sin DOI válido")
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
                print(f"Respuesta: {response.text[:200]}...")

        except Exception as e:
            print(f"❌ Error en la prueba: {e}")

    print("\n" + "=" * 50)

    # Instrucciones para el usuario
    print("📋 Instrucciones para probar en el navegador:")
    print("\n1. Abre la aplicación en el navegador")
    print("2. Completa el formulario con datos del paciente")
    print("3. Escribe en el chat uno de estos comandos:")
    print("   • 'busca papers de dolor de hombro'")
    print("   • 'buscar papers sobre dolor de rodilla'")
    print("   • 'evidencia científica de rehabilitación lumbar'")
    print("4. Verifica en la consola del navegador (F12) los logs:")
    print("   - 'Interceptando mensaje'")
    print("   - 'Comando de búsqueda detectado'")
    print("   - 'Tema de búsqueda extraído'")
    print("   - 'Enviando búsqueda científica'")
    print("5. Verifica que se muestren papers con DOIs y citas APA")

    print("\n" + "=" * 50)
    print("🎯 Prueba completada")


if __name__ == "__main__":
    test_busqueda_papers_chat()
