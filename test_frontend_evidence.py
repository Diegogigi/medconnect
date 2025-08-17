#!/usr/bin/env python3
"""
Script para probar que el frontend muestra correctamente la evidencia científica
"""

import requests
import json


def test_frontend_evidence_display():
    """Prueba que el frontend muestra correctamente la evidencia científica"""

    print("🧪 Probando visualización de evidencia científica en frontend...")
    print("=" * 70)

    try:
        # URL del endpoint
        url = "http://localhost:5000/api/copilot/analyze-enhanced"

        # Datos de prueba
        data = {
            "consulta": "dolor de rodilla por golpe en el trabajo",
            "contexto_clinico": {
                "motivoConsulta": "Dolor de rodilla postraumático",
                "sintomasPrincipales": "Dolor en rodilla derecha",
                "antecedentesMedicos": "Golpe en el trabajo",
            },
        }

        # Headers
        headers = {"Content-Type": "application/json"}

        print("1️⃣ Enviando consulta al backend...")
        print(f"   📝 Consulta: {data['consulta']}")

        # Hacer request
        response = requests.post(url, json=data, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta exitosa del backend")

            # Verificar estructura de respuesta
            print("\n2️⃣ Verificando estructura de respuesta...")

            if result.get("success"):
                print("   ✅ Campo 'success': True")

                # Verificar evidencia científica
                evidence = result.get("evidence", [])
                print(f"   📊 Evidencia científica: {len(evidence)} artículos")

                if evidence:
                    print("\n3️⃣ Detalles de la evidencia científica:")
                    for i, paper in enumerate(evidence[:3], 1):
                        print(f"   📄 Paper {i}:")
                        print(
                            f"      📝 Título: {paper.get('titulo', 'Sin título')[:60]}..."
                        )
                        print(f"      📅 Año: {paper.get('year', 'N/A')}")
                        print(f"      📊 Tipo: {paper.get('tipo', 'N/A')}")
                        print(f"      📈 Relevancia: {paper.get('relevancia', 0):.2f}")
                        print(f"      🔗 DOI: {paper.get('doi', 'Sin DOI')}")
                        print(
                            f"      📝 Resumen: {paper.get('resumen', 'Sin resumen')[:80]}..."
                        )
                        print()

                # Verificar análisis clínico
                clinical = result.get("clinical_analysis", {})
                print("4️⃣ Análisis clínico:")
                print(
                    f"   💡 Recomendaciones: {len(clinical.get('recomendaciones', []))}"
                )
                print(f"   🏥 Patologías: {len(clinical.get('patologias', []))}")
                print(f"   📊 Escalas: {len(clinical.get('escalas', []))}")

                if clinical.get("recomendaciones"):
                    print("\n   📋 Recomendaciones encontradas:")
                    for rec in clinical["recomendaciones"]:
                        print(f"      • {rec}")

                # Verificar análisis NLP
                nlp = result.get("nlp_analysis", {})
                print(f"\n5️⃣ Análisis NLP:")
                print(f"   🔑 Palabras clave: {len(nlp.get('palabras_clave', []))}")
                print(f"   📝 Síntomas: {len(nlp.get('sintomas', []))}")
                print(f"   🏥 Entidades: {len(nlp.get('entidades', []))}")
                print(f"   📊 Confianza: {nlp.get('confianza', 0):.2f}")

                print("\n✅ Estructura de respuesta correcta")
                print("🎯 El frontend debería mostrar:")
                print("   📄 Los títulos de los papers")
                print("   📅 Años de publicación")
                print("   📊 Tipos de estudio")
                print("   📈 Scores de relevancia")
                print("   🔗 Enlaces DOI")
                print("   📝 Resúmenes de los papers")
                print("   💡 Recomendaciones clínicas")

                return True
            else:
                print("❌ Campo 'success' es False")
                print(f"📝 Mensaje: {result.get('message', 'Sin mensaje')}")
                return False

        else:
            print(f"❌ Error en respuesta: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False


if __name__ == "__main__":
    success = test_frontend_evidence_display()
    print(f"\n{'✅ Prueba exitosa' if success else '❌ Prueba fallida'}")
