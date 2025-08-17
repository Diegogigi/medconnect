#!/usr/bin/env python3
"""
Script para probar login y búsqueda de papers con credenciales reales
"""

import requests
import json
import time


def test_login_y_busqueda():
    """Prueba el login y búsqueda de papers con credenciales reales"""

    print("🧪 Probando login y búsqueda de papers con credenciales reales...")
    print("=" * 60)

    # URL base
    base_url = "http://localhost:5000"

    # Credenciales proporcionadas
    credentials = {"email": "diego.castro.lagos@gmail.com", "password": "Muerto6900"}

    # Crear sesión para mantener cookies
    session = requests.Session()

    try:
        print("🔐 Paso 1: Intentando login...")

        # Intentar login
        login_response = session.post(f"{base_url}/login", data=credentials, timeout=10)

        print(f"Status Code Login: {login_response.status_code}")

        if login_response.status_code == 200:
            print("✅ Login exitoso")

            # Verificar si estamos en la página correcta
            if (
                "professional" in login_response.url
                or "dashboard" in login_response.url
            ):
                print("✅ Redirigido a página profesional")
            else:
                print("⚠️ No redirigido a página profesional")
                print(f"URL actual: {login_response.url}")

        elif login_response.status_code == 302:
            print("✅ Login exitoso (redirección)")
            # Seguir la redirección
            redirect_response = session.get(login_response.headers.get("Location", ""))
            print(f"URL después de redirección: {redirect_response.url}")

        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Respuesta: {login_response.text[:200]}...")
            return

        print("\n🔍 Paso 2: Probando búsqueda de papers...")
        print("-" * 40)

        # Casos de prueba para búsqueda
        casos_prueba = [
            {
                "consulta": "busca papers de dolor de hombro",
                "contexto_clinico": {
                    "motivoConsulta": "Dolor de hombro por golpe",
                    "tipoAtencion": "Kinesiología",
                    "pacienteNombre": "Paciente Test",
                    "pacienteRut": "12345678-9",
                    "pacienteEdad": "35",
                },
            },
            {
                "consulta": "buscar papers sobre dolor de rodilla",
                "contexto_clinico": {
                    "motivoConsulta": "Dolor de rodilla por lesión al jugar futbol",
                    "tipoAtencion": "Kinesiología",
                    "pacienteNombre": "Paciente Test",
                    "pacienteRut": "12345678-9",
                    "pacienteEdad": "28",
                },
            },
        ]

        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n{i}️⃣ Probando búsqueda: '{caso['consulta']}'")
            print("-" * 50)

            try:
                # Probar endpoint de análisis con sesión autenticada
                response = session.post(
                    f"{base_url}/api/copilot/analyze-enhanced",
                    headers={"Content-Type": "application/json"},
                    json=caso,
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
                                        print(
                                            f"   📖 Cita APA: {paper['cita_apa'][:100]}..."
                                        )
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

                    except json.JSONDecodeError:
                        print("❌ Respuesta no es JSON válido")
                        print(f"Respuesta: {response.text[:300]}...")

                elif response.status_code == 401:
                    print("❌ No autorizado - problema de autenticación")
                elif response.status_code == 302:
                    print("❌ Redirigido - posible problema de sesión")
                    print(f"Location: {response.headers.get('Location', 'N/A')}")
                else:
                    print(f"❌ Error HTTP: {response.status_code}")
                    print(f"Respuesta: {response.text[:200]}...")

            except Exception as e:
                print(f"❌ Error en la prueba: {e}")

        print("\n" + "=" * 60)
        print("📋 Instrucciones para verificar en el navegador:")
        print("\n1. Abre el navegador y ve a la aplicación")
        print("2. Inicia sesión con:")
        print("   Email: diego.castro.lagos@gmail.com")
        print("   Password: Muerto6900")
        print("3. Completa el formulario con datos del paciente")
        print("4. Escribe en el chat: 'busca papers de dolor de hombro'")
        print("5. Verifica en la consola (F12) los logs:")
        print("   - 'Interceptando mensaje'")
        print("   - 'Comando de búsqueda detectado'")
        print("   - 'Tema de búsqueda extraído'")
        print("   - 'Enviando búsqueda científica'")
        print("6. Verifica que aparezcan papers con DOIs y citas APA")

        print("\n" + "=" * 60)
        print("🎯 Prueba completada")

    except Exception as e:
        print(f"❌ Error general: {e}")


if __name__ == "__main__":
    test_login_y_busqueda()
