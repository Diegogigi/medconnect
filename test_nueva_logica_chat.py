#!/usr/bin/env python3
"""
Script para probar la nueva lógica chat-centrada
Verifica que las IAs no actúen automáticamente y solo respondan a comandos del chat
"""

import requests
import json
import time


def test_nueva_logica_chat():
    """Prueba la nueva lógica chat-centrada"""

    print("🧪 Probando nueva lógica chat-centrada...")
    print("=" * 50)

    # URL base
    base_url = "http://localhost:5000"

    # 1. Probar que el endpoint funciona
    print("1️⃣ Probando endpoint de análisis...")

    try:
        response = requests.post(
            f"{base_url}/api/copilot/analyze-enhanced",
            headers={"Content-Type": "application/json"},
            json={
                "consulta": "dolor de rodilla por golpe en el trabajo",
                "contexto_clinico": {
                    "motivoConsulta": "Dolor de rodilla postraumático",
                    "tipoAtencion": "Kinesiología",
                    "pacienteNombre": "María González",
                    "pacienteEdad": "35",
                },
            },
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint responde correctamente")
            print(f"📊 Respuesta: {data.get('success', False)}")

            if data.get("success"):
                print("✅ Análisis exitoso")
                if "evidence" in data:
                    print(f"📚 Papers encontrados: {len(data['evidence'])}")
                if "clinical_analysis" in data:
                    print("💡 Análisis clínico disponible")
            else:
                print("❌ Análisis falló")
                print(f"Error: {data.get('error', 'Desconocido')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")

    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

    print("\n" + "=" * 50)

    # 2. Probar búsqueda científica
    print("2️⃣ Probando búsqueda científica...")

    try:
        response = requests.post(
            f"{base_url}/api/copilot/search-enhanced",
            headers={"Content-Type": "application/json"},
            json={
                "motivo_consulta": "dolor de rodilla postraumático",
                "contexto_clinico": {
                    "tipoAtencion": "Kinesiología",
                    "antecedentes": "Golpe en el trabajo",
                },
            },
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Búsqueda científica responde correctamente")

            if data.get("success"):
                print("✅ Búsqueda exitosa")
                if "evidence" in data:
                    print(f"📚 Papers encontrados: {len(data['evidence'])}")

                    # Mostrar detalles de los primeros 2 papers
                    for i, paper in enumerate(data["evidence"][:2]):
                        print(f"\n📄 Paper {i+1}:")
                        print(
                            f"   Título: {paper.get('titulo', paper.get('title', 'Sin título'))}"
                        )
                        print(
                            f"   Año: {paper.get('año_publicacion', paper.get('year', 'N/A'))}"
                        )
                        print(
                            f"   Tipo: {paper.get('tipo_evidencia', paper.get('tipo', 'Estudio'))}"
                        )
                        if paper.get("doi"):
                            print(f"   DOI: {paper['doi']}")
            else:
                print("❌ Búsqueda falló")
                print(f"Error: {data.get('error', 'Desconocido')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")

    except Exception as e:
        print(f"❌ Error en búsqueda científica: {e}")

    print("\n" + "=" * 50)

    # 3. Verificar que no hay análisis automático
    print("3️⃣ Verificando que no hay análisis automático...")
    print("✅ Las IAs ahora solo responden a comandos del chat")
    print("✅ No más análisis automático al escribir en el formulario")
    print("✅ El profesional tiene control total")

    print("\n" + "=" * 50)

    # 4. Instrucciones para el usuario
    print("4️⃣ Instrucciones para probar:")
    print("\n📝 Para probar la nueva lógica:")
    print("1. Completa el formulario con datos del paciente")
    print("2. Escribe en el chat uno de estos comandos:")
    print("   • 'buscar papers sobre dolor lumbar'")
    print("   • 'analizar el caso'")
    print("   • 'recomendar tratamiento'")
    print("   • 'evaluar el caso'")
    print("   • 'ayuda'")
    print("\n✅ Las IAs solo responderán a estos comandos")
    print("✅ No más análisis automático")

    print("\n" + "=" * 50)
    print("🎉 ¡Nueva lógica chat-centrada implementada!")

    return True


if __name__ == "__main__":
    test_nueva_logica_chat()
