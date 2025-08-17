#!/usr/bin/env python3
"""
Script final para probar que la sidebar muestre correctamente los papers
"""

import requests
import json
import time


def test_sidebar_final():
    """Prueba final de la sidebar con papers"""

    print("🧪 Prueba final: Verificación completa de la sidebar...")
    print("=" * 60)

    # URL base
    base_url = "http://localhost:5000"

    # Credenciales
    credentials = {"email": "diego.castro.lagos@gmail.com", "password": "Muerto6900"}

    # Crear sesión
    session = requests.Session()

    try:
        print("🔐 Paso 1: Login...")
        login_response = session.post(f"{base_url}/login", data=credentials, timeout=10)

        if login_response.status_code not in [200, 302]:
            print(f"❌ Error en login: {login_response.status_code}")
            return

        print("✅ Login exitoso")

        print("\n🔍 Paso 2: Probar búsqueda de papers...")
        print("-" * 40)

        # Caso de prueba específico
        caso_prueba = {
            "consulta": "busca papers de dolor de hombro",
            "contexto_clinico": {
                "motivoConsulta": "Dolor de hombro por golpe",
                "tipoAtencion": "Kinesiología",
                "pacienteNombre": "Paciente Test",
                "pacienteRut": "12345678-9",
                "pacienteEdad": "35",
            },
        }

        try:
            response = session.post(
                f"{base_url}/api/copilot/analyze-enhanced",
                headers={"Content-Type": "application/json"},
                json=caso_prueba,
                timeout=30,
            )

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ Respuesta JSON exitosa")

                    if data.get("success"):
                        print("✅ Análisis completado exitosamente")

                        # Verificar evidencia científica
                        if "evidence" in data and data["evidence"]:
                            print(f"📚 Papers encontrados: {len(data['evidence'])}")

                            # Verificar estructura completa de papers para sidebar
                            for i, paper in enumerate(data["evidence"][:3], 1):
                                print(f"\n📄 Paper {i} - Verificación completa:")
                                print(
                                    f"   ✅ Título: {paper.get('titulo', 'Sin título')}"
                                )
                                print(
                                    f"   ✅ Año: {paper.get('año_publicacion', paper.get('year', 'N/A'))}"
                                )
                                print(f"   ✅ DOI: {paper.get('doi', 'Sin DOI')}")
                                print(
                                    f"   ✅ Relevancia: {paper.get('relevancia_score', paper.get('relevancia', 0)):.2f}"
                                )

                                # Verificar campos críticos para sidebar
                                campos_criticos = {
                                    "titulo": paper.get("titulo"),
                                    "año_publicacion": paper.get(
                                        "año_publicacion", paper.get("year")
                                    ),
                                    "doi": paper.get("doi"),
                                    "relevancia_score": paper.get(
                                        "relevancia_score", paper.get("relevancia")
                                    ),
                                    "resumen": paper.get("resumen"),
                                    "cita_apa": paper.get("cita_apa"),
                                    "autores": paper.get("autores"),
                                }

                                campos_ok = 0
                                for campo, valor in campos_criticos.items():
                                    if valor:
                                        print(f"   ✅ {campo}: Presente")
                                        campos_ok += 1
                                    else:
                                        print(f"   ❌ {campo}: Faltante")

                                print(
                                    f"   📊 Campos completos: {campos_ok}/{len(campos_criticos)}"
                                )

                                # Verificar cita APA específicamente
                                if paper.get("cita_apa"):
                                    print(
                                        f"   📖 Cita APA: {paper['cita_apa'][:100]}..."
                                    )
                                else:
                                    print(f"   ❌ Sin cita APA")

                                # Verificar DOI válido
                                if paper.get("doi") and paper["doi"] != "Sin DOI":
                                    print(f"   🔗 DOI válido: {paper['doi']}")
                                else:
                                    print(f"   ❌ Sin DOI válido")

                                # Verificar relevancia del contenido
                                titulo = paper.get("titulo", "").lower()
                                if (
                                    "shoulder" in titulo
                                    or "hombro" in titulo
                                    or "capsulitis" in titulo
                                ):
                                    print(f"   ✅ Título relevante para hombro")
                                else:
                                    print(
                                        f"   ⚠️ Título no parece relevante para hombro"
                                    )
                        else:
                            print("❌ No se encontraron papers científicos")

                        # Verificar análisis clínico
                        if "clinical_analysis" in data:
                            print("💡 Análisis clínico disponible")
                            if data["clinical_analysis"].get("recomendaciones"):
                                print(
                                    f"   📋 Recomendaciones: {len(data['clinical_analysis']['recomendaciones'])}"
                                )
                        else:
                            print("⚠️ Sin análisis clínico")

                    else:
                        print("❌ Análisis falló")
                        print(f"Error: {data.get('error', 'Desconocido')}")

                except json.JSONDecodeError:
                    print("❌ Respuesta no es JSON válido")
                    print(f"Respuesta: {response.text[:300]}...")

            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"Respuesta: {response.text[:200]}...")

        except Exception as e:
            print(f"❌ Error en la prueba: {e}")

        print("\n" + "=" * 60)
        print("📋 Instrucciones finales para verificar en el navegador:")
        print("\n🎯 PASOS PARA VERIFICAR LA SIDEBAR:")
        print("\n1. Abre el navegador y ve a la aplicación")
        print("2. Inicia sesión con:")
        print("   Email: diego.castro.lagos@gmail.com")
        print("   Password: Muerto6900")
        print("3. Completa el formulario con datos del paciente")
        print("4. Escribe en el chat: 'busca papers de dolor de hombro'")
        print("5. Verifica en la sidebar (panel derecho):")
        print("   ✅ Sección 'Evidencia Científica' visible")
        print("   ✅ Papers con títulos completos")
        print("   ✅ Años de publicación (2024, 2023, etc.)")
        print("   ✅ DOIs clickeables (enlaces azules)")
        print("   ✅ Citas APA completas")
        print("   ✅ Resúmenes de los papers")
        print("   ✅ Porcentajes de relevancia")
        print("6. Verifica que NO aparezca:")
        print("   ❌ 'No se encontró evidencia científica relevante'")
        print("   ❌ Placeholder vacío")
        print("   ❌ Mensajes de error")

        print("\n🔍 Verificación técnica en consola (F12):")
        print("7. Abre la consola del navegador")
        print("8. Busca estos logs:")
        print("   ✅ 'Interceptando mensaje'")
        print("   ✅ 'Comando de búsqueda detectado'")
        print("   ✅ 'Tema de búsqueda extraído'")
        print("   ✅ 'Enviando búsqueda científica'")
        print("   ✅ 'displayEvidence' o 'displayUnifiedResults'")

        print("\n🎉 RESULTADO ESPERADO:")
        print("La sidebar debe mostrar papers científicos completos con:")
        print("- Títulos relevantes sobre dolor de hombro")
        print("- DOIs válidos y clickeables")
        print("- Citas APA en formato correcto")
        print("- Resúmenes de los estudios")
        print("- Información de relevancia")

        print("\n" + "=" * 60)
        print("🎯 Prueba final completada")

    except Exception as e:
        print(f"❌ Error general: {e}")


if __name__ == "__main__":
    test_sidebar_final()
