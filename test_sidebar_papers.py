#!/usr/bin/env python3
"""
Script para probar que los papers se muestren correctamente en la sidebar
"""

import requests
import json
import time


def test_sidebar_papers():
    """Prueba que los papers se muestren en la sidebar"""

    print("🧪 Probando visualización de papers en la sidebar...")
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

                            # Verificar estructura de papers para sidebar
                            for i, paper in enumerate(data["evidence"][:3], 1):
                                print(f"\n📄 Paper {i} para sidebar:")
                                print(
                                    f"   ✅ Título: {paper.get('titulo', paper.get('title', 'Sin título'))}"
                                )
                                print(
                                    f"   ✅ Año: {paper.get('año_publicacion', paper.get('year', 'N/A'))}"
                                )
                                print(f"   ✅ DOI: {paper.get('doi', 'Sin DOI')}")
                                print(
                                    f"   ✅ Relevancia: {paper.get('relevancia_score', 0):.2f}"
                                )

                                # Verificar campos necesarios para sidebar
                                campos_requeridos = [
                                    "titulo",
                                    "año_publicacion",
                                    "doi",
                                    "relevancia_score",
                                ]
                                campos_faltantes = []

                                for campo in campos_requeridos:
                                    if not paper.get(campo):
                                        campos_faltantes.append(campo)

                                if campos_faltantes:
                                    print(f"   ⚠️ Campos faltantes: {campos_faltantes}")
                                else:
                                    print(
                                        f"   ✅ Todos los campos requeridos presentes"
                                    )

                                # Verificar cita APA
                                if paper.get("cita_apa"):
                                    print(
                                        f"   ✅ Cita APA: {paper['cita_apa'][:80]}..."
                                    )
                                else:
                                    print(f"   ❌ Sin cita APA")

                                # Verificar resumen
                                if paper.get("resumen") or paper.get("abstract"):
                                    print(f"   ✅ Resumen disponible")
                                else:
                                    print(f"   ⚠️ Sin resumen")
                        else:
                            print("❌ No se encontraron papers científicos")

                        # Verificar análisis clínico
                        if "clinical_analysis" in data:
                            print("💡 Análisis clínico disponible")
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
        print("📋 Instrucciones para verificar en el navegador:")
        print("\n1. Abre el navegador y ve a la aplicación")
        print("2. Inicia sesión con las credenciales")
        print("3. Completa el formulario con datos del paciente")
        print("4. Escribe en el chat: 'busca papers de dolor de hombro'")
        print("5. Verifica en la sidebar (panel derecho):")
        print("   - Sección 'Evidencia Científica'")
        print("   - Papers con títulos completos")
        print("   - Años de publicación")
        print("   - DOIs clickeables")
        print("   - Citas APA completas")
        print("   - Resúmenes de los papers")
        print("6. Verifica que NO aparezca:")
        print("   - 'No se encontró evidencia científica relevante'")
        print("   - Placeholder vacío")

        print("\n🔍 Verificación técnica:")
        print("7. Abre la consola del navegador (F12)")
        print("8. Busca estos logs:")
        print("   - 'Interceptando mensaje'")
        print("   - 'Comando de búsqueda detectado'")
        print("   - 'Tema de búsqueda extraído'")
        print("   - 'Enviando búsqueda científica'")
        print("   - 'displayEvidence' o 'displayUnifiedResults'")

        print("\n" + "=" * 60)
        print("🎯 Prueba completada")

    except Exception as e:
        print(f"❌ Error general: {e}")


if __name__ == "__main__":
    test_sidebar_papers()
