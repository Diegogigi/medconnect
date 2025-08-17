#!/usr/bin/env python3
"""
Test de Preguntas Personalizadas - Sistema Final
Verifica que el sistema genere preguntas personalizadas basadas en motivo de consulta y tipo de atención
"""

import sys
import os
import json
import requests
from datetime import datetime

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_preguntas_personalizadas():
    """Prueba el sistema de preguntas personalizadas"""
    
    # Casos de prueba con diferentes especialidades y motivos
    casos_prueba = [
        {
            "nombre": "Fonoaudiología - Problemas de Voz",
            "motivo_consulta": "Tengo problemas con mi voz, se me cansa muy rápido y a veces se me quiebra cuando hablo",
            "tipo_atencion": "fonoaudiologia",
            "especialidad_esperada": "fonoaudiologia",
            "palabras_clave_esperadas": ["voz", "habla", "comunicación"]
        },
        {
            "nombre": "Fonoaudiología - Dificultad para Tragar",
            "motivo_consulta": "Me cuesta mucho tragar los alimentos, especialmente los sólidos, y a veces me atraganto",
            "tipo_atencion": "fonoaudiologia",
            "especialidad_esperada": "fonoaudiologia",
            "palabras_clave_esperadas": ["tragar", "deglución", "disfagia"]
        },
        {
            "nombre": "Kinesiología - Lesión Deportiva",
            "motivo_consulta": "Me lesioné jugando fútbol, tengo dolor en la rodilla derecha y no puedo doblarla bien",
            "tipo_atencion": "kinesiologia",
            "especialidad_esperada": "kinesiologia",
            "palabras_clave_esperadas": ["dolor", "lesión", "trauma"]
        },
        {
            "nombre": "Psicología - Ansiedad",
            "motivo_consulta": "Me siento muy ansioso últimamente, no puedo dormir bien y me preocupo por todo",
            "tipo_atencion": "psicologia",
            "especialidad_esperada": "psicologia",
            "palabras_clave_esperadas": ["ansiedad", "estrés", "nervios"]
        },
        {
            "nombre": "Nutrición - Control de Peso",
            "motivo_consulta": "Quiero bajar de peso, he subido 15 kilos en el último año y no sé cómo controlarlo",
            "tipo_atencion": "nutricion",
            "especialidad_esperada": "nutricion",
            "palabras_clave_esperadas": ["peso", "obesidad", "sobrepeso"]
        }
    ]
    
    print("🧪 INICIANDO PRUEBAS DE PREGUNTAS PERSONALIZADAS")
    print("=" * 60)
    
    resultados = []
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 CASO {i}: {caso['nombre']}")
        print("-" * 40)
        print(f"Motivo: {caso['motivo_consulta']}")
        print(f"Tipo de atención: {caso['tipo_atencion']}")
        
        try:
            # Llamar al endpoint
            response = requests.post(
                "http://localhost:5000/api/copilot/analyze-motivo",
                json={
                    "motivo_consulta": caso['motivo_consulta'],
                    "tipo_atencion": caso['tipo_atencion']
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    analisis = data['analisis']
                    preguntas = analisis.get('preguntas_sugeridas', [])
                    especialidad = analisis.get('especialidad_detectada', '')
                    
                    print(f"✅ Especialidad detectada: {especialidad}")
                    print(f"📊 Número de preguntas generadas: {len(preguntas)}")
                    
                    # Verificar que las preguntas sean personalizadas
                    preguntas_personalizadas = 0
                    for pregunta in preguntas:
                        if any(palabra in pregunta.lower() for palabra in caso['palabras_clave_esperadas']):
                            preguntas_personalizadas += 1
                    
                    print(f"🎯 Preguntas personalizadas: {preguntas_personalizadas}/{len(preguntas)}")
                    
                    # Mostrar las preguntas
                    print("\n📝 Preguntas generadas:")
                    for j, pregunta in enumerate(preguntas, 1):
                        print(f"  {j}. {pregunta}")
                    
                    # Evaluar el resultado
                    if len(preguntas) >= 5 and preguntas_personalizadas >= 3:
                        resultado = "✅ EXCELENTE"
                    elif len(preguntas) >= 3 and preguntas_personalizadas >= 2:
                        resultado = "✅ BUENO"
                    else:
                        resultado = "❌ INSUFICIENTE"
                    
                    resultados.append({
                        "caso": caso['nombre'],
                        "preguntas_generadas": len(preguntas),
                        "preguntas_personalizadas": preguntas_personalizadas,
                        "resultado": resultado
                    })
                    
                else:
                    print(f"❌ Error en la respuesta: {data.get('message', 'Error desconocido')}")
                    resultados.append({
                        "caso": caso['nombre'],
                        "error": data.get('message', 'Error desconocido'),
                        "resultado": "❌ ERROR"
                    })
            
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                print(f"Respuesta: {response.text}")
                resultados.append({
                    "caso": caso['nombre'],
                    "error": f"HTTP {response.status_code}",
                    "resultado": "❌ ERROR"
                })
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            resultados.append({
                "caso": caso['nombre'],
                "error": str(e),
                "resultado": "❌ ERROR"
            })
        
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            resultados.append({
                "caso": caso['nombre'],
                "error": str(e),
                "resultado": "❌ ERROR"
            })
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    exitosos = 0
    total = len(resultados)
    
    for resultado in resultados:
        print(f"{resultado['resultado']} - {resultado['caso']}")
        if 'preguntas_generadas' in resultado:
            print(f"   Preguntas generadas: {resultado['preguntas_generadas']}")
            print(f"   Preguntas personalizadas: {resultado['preguntas_personalizadas']}")
        elif 'error' in resultado:
            print(f"   Error: {resultado['error']}")
        
        if resultado['resultado'].startswith("✅"):
            exitosos += 1
    
    print(f"\n🎯 RESULTADO FINAL: {exitosos}/{total} casos exitosos")
    
    if exitosos == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema genera preguntas personalizadas correctamente.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar el sistema.")
        return False

def test_endpoint_directo():
    """Prueba directa del endpoint con casos específicos"""
    
    print("\n🔍 PRUEBA DIRECTA DEL ENDPOINT")
    print("=" * 40)
    
    # Caso específico de fonoaudiología
    caso_fono = {
        "motivo_consulta": "Tengo problemas con mi voz, se me cansa muy rápido y a veces se me quiebra cuando hablo",
        "tipo_atencion": "fonoaudiologia"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/copilot/analyze-motivo",
            json=caso_fono,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                preguntas = data['analisis'].get('preguntas_sugeridas', [])
                print(f"✅ Preguntas generadas para fonoaudiología: {len(preguntas)}")
                
                for i, pregunta in enumerate(preguntas, 1):
                    print(f"  {i}. {pregunta}")
                
                # Verificar que no sean las 3 preguntas genéricas
                preguntas_genericas = [
                    "¿Ha notado cambios en su voz o habla?",
                    "¿Tiene dificultades para tragar?",
                    "¿Hay problemas de comunicación?"
                ]
                
                coincidencias = 0
                for pregunta in preguntas:
                    if pregunta in preguntas_genericas:
                        coincidencias += 1
                
                if coincidencias < 3:
                    print("✅ Las preguntas NO son genéricas - Sistema funcionando correctamente")
                    return True
                else:
                    print("❌ Las preguntas siguen siendo genéricas - Sistema necesita ajustes")
                    return False
            else:
                print(f"❌ Error en respuesta: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema de preguntas personalizadas...")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor Flask está corriendo")
        else:
            print("❌ Servidor Flask no responde correctamente")
            sys.exit(1)
    except:
        print("❌ No se puede conectar al servidor Flask")
        print("💡 Asegúrate de que el servidor esté corriendo en http://localhost:5000")
        sys.exit(1)
    
    # Ejecutar pruebas
    resultado_principal = test_preguntas_personalizadas()
    resultado_directo = test_endpoint_directo()
    
    if resultado_principal and resultado_directo:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        print("✅ El sistema genera preguntas personalizadas basadas en motivo de consulta y tipo de atención")
    else:
        print("\n⚠️ Algunas pruebas fallaron")
        print("🔧 Revisar la implementación del sistema de preguntas personalizadas") 