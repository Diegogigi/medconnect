#!/usr/bin/env python3
"""
Script para reiniciar el servidor y verificar la búsqueda científica
"""

import os
import sys
import time
import subprocess
import requests
import json


def reiniciar_servidor():
    """Reinicia el servidor Flask"""
    print("🔄 Reiniciando servidor...")

    # Detener procesos existentes
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
        time.sleep(2)
    except:
        pass

    # Iniciar servidor
    try:
        process = subprocess.Popen(
            ["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        print("⏳ Esperando que el servidor inicie...")
        time.sleep(10)

        return process
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return None


def probar_busqueda_cientifica():
    """Prueba la búsqueda científica via API"""
    print("🧪 Probando búsqueda científica via API...")

    try:
        # URL del endpoint
        url = "http://localhost:5000/api/copilot/search-enhanced"

        # Datos de prueba
        data = {"motivo_consulta": "dolor lumbar postraumático por golpe en el trabajo"}

        # Headers
        headers = {"Content-Type": "application/json"}

        # Hacer request
        response = requests.post(url, json=data, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✅ Búsqueda científica exitosa!")
            print(f"📊 Papers encontrados: {result.get('total_papers', 0)}")

            if result.get("papers_encontrados"):
                print("\n📚 Resultados:")
                for i, paper in enumerate(result["papers_encontrados"][:3], 1):
                    print(f"   {i}. {paper.get('titulo', 'Sin título')[:80]}...")
                    print(f"      📊 Score: {paper.get('relevancia_score', 0):.2f}")
                    print(f"      📅 Año: {paper.get('año_publicacion', 'N/A')}")
                    print()

            return True
        else:
            print(f"❌ Error en búsqueda: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error probando búsqueda: {e}")
        return False


def probar_analisis_unificado():
    """Prueba el análisis unificado via API"""
    print("🧪 Probando análisis unificado via API...")

    try:
        # URL del endpoint
        url = "http://localhost:5000/api/copilot/analyze-enhanced"

        # Datos de prueba
        data = {
            "consulta": "dolor lumbar postraumático por golpe en el trabajo",
            "contexto_clinico": {
                "motivoConsulta": "Dolor lumbar postraumático",
                "sintomasPrincipales": "Dolor en zona lumbar",
                "antecedentesMedicos": "Golpe en el trabajo",
            },
        }

        # Headers
        headers = {"Content-Type": "application/json"}

        # Hacer request
        response = requests.post(url, json=data, headers=headers, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis unificado exitoso!")
            print(f"📊 Evidencias: {len(result.get('evidence', []))}")
            print(
                f"📋 Recomendaciones: {len(result.get('clinical_analysis', {}).get('recomendaciones', []))}"
            )

            return True
        else:
            print(f"❌ Error en análisis: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error probando análisis: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de búsqueda científica...")
    print("=" * 60)

    # Reiniciar servidor
    process = reiniciar_servidor()
    if not process:
        return False

    try:
        # Probar búsqueda científica
        success_busqueda = probar_busqueda_cientifica()

        print("\n" + "=" * 60)

        # Probar análisis unificado
        success_analisis = probar_analisis_unificado()

        print("\n" + "=" * 60)

        if success_busqueda and success_analisis:
            print("✅ Todas las pruebas exitosas!")
            print("🎉 La búsqueda científica está funcionando correctamente")
        else:
            print("⚠️ Algunas pruebas fallaron")
            if not success_busqueda:
                print("   - Búsqueda científica no funciona")
            if not success_analisis:
                print("   - Análisis unificado no funciona")

        return success_busqueda and success_analisis

    finally:
        # Detener servidor
        if process:
            process.terminate()
            print("\n🛑 Servidor detenido")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
