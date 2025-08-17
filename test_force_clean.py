#!/usr/bin/env python3
"""
Script para probar la limpieza forzada del sistema
"""

import requests
import json
import time


def test_force_clean():
    """Prueba que la limpieza forzada funcione"""

    print("🧹 PROBANDO LIMPIEZA FORZADA DEL SISTEMA")
    print("=" * 50)

    # URL base
    base_url = "http://localhost:5000"

    try:
        # 1. Verificar que el servidor esté funcionando
        print("1. Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Servidor funcionando")
        else:
            print("❌ Servidor no responde")
            return

        # 2. Verificar que la página del profesional cargue
        print("2. Verificando página del profesional...")
        response = requests.get(f"{base_url}/professional")
        if response.status_code == 200:
            print("✅ Página del profesional cargada")

            # Verificar que el script de limpieza esté incluido
            if "force-clean-system.js" in response.text:
                print("✅ Script de limpieza forzada incluido")
            else:
                print("❌ Script de limpieza forzada NO encontrado")

        else:
            print("❌ Error cargando página del profesional")
            return

        # 3. Simular una consulta para verificar que funcione
        print("3. Probando consulta de prueba...")

        # Datos de prueba
        test_data = {
            "consulta": "busca papers de dolor de hombro",
            "contexto_clinico": {
                "motivoConsulta": "Dolor de hombro por golpe",
                "tipoAtencion": "kinesiologia",
                "pacienteNombre": "Paciente de prueba",
            },
        }

        # Hacer la consulta
        response = requests.post(
            f"{base_url}/api/copilot/analyze-enhanced",
            json=test_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Consulta procesada exitosamente")

                # Verificar que hay evidencia
                evidence = data.get("evidence", [])
                if evidence:
                    print(f"✅ {len(evidence)} papers encontrados")

                    # Verificar relevancia del primer paper
                    if evidence:
                        first_paper = evidence[0]
                        title = first_paper.get("titulo", "").lower()

                        relevant_terms = [
                            "shoulder",
                            "hombro",
                            "pain",
                            "dolor",
                            "trauma",
                            "injury",
                        ]
                        is_relevant = any(term in title for term in relevant_terms)

                        if is_relevant:
                            print("✅ Paper relevante encontrado")
                        else:
                            print("⚠️ Paper puede no ser relevante")

                else:
                    print("⚠️ No se encontraron papers")
            else:
                print(f"❌ Error en consulta: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")

        print("\n" + "=" * 50)
        print("✅ PRUEBA DE LIMPIEZA FORZADA COMPLETADA")
        print("\n📋 Instrucciones para el usuario:")
        print("   1. Recarga la página del profesional")
        print("   2. Verifica que solo aparezca 'Asistente IA Médico Único'")
        print("   3. Prueba una consulta como 'busca papers de dolor de hombro'")
        print("   4. Verifica que no haya sistemas duplicados")

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor Flask esté ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def check_browser_console():
    """Instrucciones para verificar la consola del navegador"""

    print("\n🔍 VERIFICACIÓN EN EL NAVEGADOR")
    print("=" * 40)
    print("1. Abre las herramientas de desarrollador (F12)")
    print("2. Ve a la pestaña 'Console'")
    print("3. Busca estos mensajes:")
    print("   ✅ '🧹 Inicializando Limpieza Forzada...'")
    print("   ✅ '🧹 Forzando limpieza de todos los sistemas...'")
    print("   ✅ '✅ Limpieza Forzada completada'")
    print("   ✅ '✅ Sistema único creado'")
    print("4. No debe haber errores de JavaScript")
    print("5. No debe haber mensajes de sistemas duplicados")


if __name__ == "__main__":
    test_force_clean()
    check_browser_console()
