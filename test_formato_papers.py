#!/usr/bin/env python3
"""
Script para probar el formato específico de papers científicos
"""

import requests
import json
import time


def test_formato_papers():
    """Prueba el formato específico de papers científicos"""

    print("🧪 Probando formato específico de papers científicos...")
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

        print("\n🔍 Paso 2: Probar formato de papers...")
        print("-" * 40)

        # Caso de prueba específico
        caso_prueba = {
            "consulta": "busca papers de dolor de rodilla",
            "contexto_clinico": {
                "motivoConsulta": "Dolor de rodilla por trauma en el trabajo",
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

                            # Verificar formato específico de papers
                            for i, paper in enumerate(data["evidence"][:3], 1):
                                print(f"\n📄 Paper {i} - Verificación de formato:")
                                print(
                                    f"   ✅ Título: {paper.get('titulo', 'Sin título')}"
                                )

                                # Verificar autores
                                autores = paper.get("autores", [])
                                if autores:
                                    if len(autores) <= 3:
                                        autores_str = ", ".join(autores)
                                    else:
                                        autores_str = (
                                            f"{', '.join(autores[:3])}, et al."
                                        )
                                    print(f"   ✅ Autores: {autores_str}")
                                else:
                                    print(f"   ❌ Sin autores")

                                # Verificar revista
                                revista = paper.get("journal", "")
                                año = paper.get(
                                    "año_publicacion", paper.get("year", "")
                                )
                                volumen = paper.get("volumen", "")
                                numero = paper.get("numero", "")
                                paginas = paper.get("paginas", "")

                                revista_formateada = revista
                                if año:
                                    revista_formateada += f". {año}"
                                    if volumen:
                                        revista_formateada += f";{volumen}"
                                        if numero:
                                            revista_formateada += f"({numero})"
                                        if paginas:
                                            revista_formateada += f":{paginas}"
                                    revista_formateada += "."

                                print(f"   ✅ Revista: {revista_formateada}")

                                # Verificar DOI
                                doi = paper.get("doi", "")
                                if doi and doi != "Sin DOI":
                                    doi_formateado = f"doi:{doi}"
                                    print(f"   ✅ DOI: {doi_formateado}")
                                else:
                                    print(f"   ❌ Sin DOI válido")

                                # Verificar resumen
                                resumen = paper.get(
                                    "resumen", paper.get("abstract", "")
                                )
                                if resumen:
                                    print(f"   ✅ Resumen: {resumen[:100]}...")
                                else:
                                    print(f"   ⚠️ Sin resumen")

                                # Mostrar formato esperado
                                print(f"\n   📋 Formato esperado:")
                                print(f"   {i}. {paper.get('titulo', 'Sin título')}")
                                if autores:
                                    print(f"   📝 Autores: {autores_str}.")
                                print(f"   📚 Revista: {revista_formateada}")
                                if doi and doi != "Sin DOI":
                                    print(f"   🔗 DOI: doi:{doi}")
                                if resumen:
                                    print(f"   📖 Resumen: {resumen[:100]}...")
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
        print("📋 Instrucciones para verificar el formato en el navegador:")
        print("\n🎯 PASOS PARA VERIFICAR EL FORMATO:")
        print("\n1. Abre el navegador y ve a la aplicación")
        print("2. Inicia sesión con las credenciales")
        print("3. Completa el formulario con datos del paciente")
        print("4. Escribe en el chat: 'busca papers de dolor de rodilla'")
        print("5. Verifica que los papers aparezcan en este formato:")
        print("\n   📄 **Título del Paper**")
        print("   📝 **Autores:** Autor1, Autor2, Autor3, et al.")
        print("   📚 **Revista:** Nombre revista. Año;Volumen(Número):Páginas.")
        print("   🔗 **DOI:** doi:10.xxxx/xxxxx")
        print("   📖 **Resumen:** Primeros 150 caracteres...")

        print("\n6. Verifica en la sidebar que aparezca el mismo formato")
        print("7. Verifica que los DOIs sean clickeables")

        print("\n" + "=" * 60)
        print("🎯 Prueba completada")

    except Exception as e:
        print(f"❌ Error general: {e}")


if __name__ == "__main__":
    test_formato_papers()
