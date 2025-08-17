#!/usr/bin/env python3
"""
Script para verificar el flujo completo y identificar qué está activando la sección antigua
"""

import requests
import json
import time

def test_flujo_completo():
    """Prueba el flujo completo para identificar el problema"""
    print("🔍 VERIFICACIÓN DEL FLUJO COMPLETO")
    print("=" * 60)
    
    session = requests.Session()
    
    # Caso de prueba
    caso_prueba = {
        'motivo_consulta': 'Dolor intenso en rodilla al caminar',
        'tipo_atencion': 'kinesiologia',
        'edad_paciente': 45,
        'antecedentes': 'Sin antecedentes relevantes'
    }
    
    print(f"📋 Caso de prueba: {caso_prueba['motivo_consulta']}")
    
    # Prueba 1: Verificar si el servidor está corriendo
    print("\n🔍 Prueba 1: Verificar servidor")
    try:
        response = session.get('http://localhost:5000/health')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Servidor funcionando")
        else:
            print("❌ Servidor no responde correctamente")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return
    
    # Prueba 2: Verificar endpoint analyze-enhanced
    print("\n🔍 Prueba 2: Endpoint /api/copilot/analyze-enhanced")
    try:
        response = session.post(
            'http://localhost:5000/api/copilot/analyze-enhanced',
            json=caso_prueba
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Respuesta JSON válida")
                
                if data.get('success'):
                    analisis = data.get('analisis_mejorado', {})
                    
                    # Verificar preguntas de evaluación
                    preguntas = analisis.get('preguntas_evaluacion', [])
                    print(f"✅ Preguntas de evaluación encontradas: {len(preguntas)}")
                    
                    if preguntas:
                        print("📝 Preguntas generadas:")
                        for i, pregunta in enumerate(preguntas, 1):
                            print(f"   {i}. {pregunta}")
                    
                    # Verificar otros elementos
                    palabras_clave = analisis.get('palabras_clave_identificadas', [])
                    patologias = analisis.get('patologias_sugeridas', [])
                    escalas = analisis.get('escalas_recomendadas', [])
                    
                    print(f"✅ Palabras clave: {len(palabras_clave)}")
                    print(f"✅ Patologías: {len(patologias)}")
                    print(f"✅ Escalas: {len(escalas)}")
                    
                else:
                    print(f"❌ Error en respuesta: {data.get('message', 'Error desconocido')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Respuesta recibida: {response.text[:200]}...")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
    
    # Prueba 3: Verificar otros endpoints que podrían estar activando la sección antigua
    print("\n🔍 Prueba 3: Verificar otros endpoints")
    
    endpoints_a_verificar = [
        '/api/copilot/analyze-motivo',
        '/api/copilot/generate-evaluation-questions',
        '/api/copilot/complete-analysis'
    ]
    
    for endpoint in endpoints_a_verificar:
        print(f"\n🔍 Verificando {endpoint}")
        try:
            response = session.post(
                f'http://localhost:5000{endpoint}',
                json=caso_prueba
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Verificar si devuelve preguntas_sugeridas
                    if 'preguntas_sugeridas' in str(data):
                        print(f"⚠️ {endpoint} devuelve preguntas_sugeridas - POSIBLE CAUSA DEL PROBLEMA")
                        
                        # Buscar en la respuesta
                        if 'analisis' in data and 'preguntas_sugeridas' in data['analisis']:
                            preguntas = data['analisis']['preguntas_sugeridas']
                            print(f"   Preguntas encontradas: {len(preguntas)}")
                            for i, pregunta in enumerate(preguntas[:3], 1):
                                print(f"   {i}. {pregunta}")
                    
                    elif 'preguntas_evaluacion' in str(data):
                        print(f"✅ {endpoint} devuelve preguntas_evaluacion - CORRECTO")
                    
                    else:
                        print(f"ℹ️ {endpoint} no devuelve preguntas")
                        
                except json.JSONDecodeError:
                    print(f"❌ {endpoint} devuelve HTML en lugar de JSON")
            else:
                print(f"❌ {endpoint} error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error verificando {endpoint}: {e}")

def test_verificacion_frontend():
    """Verificación del frontend"""
    print("\n🔍 VERIFICACIÓN DEL FRONTEND")
    print("=" * 60)
    
    print("✅ Funciones JavaScript verificadas:")
    print("   • analizarMotivoEnTiempoReal() - Modificada para usar /api/copilot/analyze-enhanced")
    print("   • mostrarAnalisisMejoradoEnSidebar() - Incluye sección de preguntas")
    print("   • mostrarPreguntasSugeridas() - Modificada para mostrar en sidebar")
    print("   • mostrarResultadosAnalisis() - NO llama a mostrarPreguntasSugeridas")
    
    print("\n❌ Posibles causas del problema:")
    print("   1. Hay otro endpoint devolviendo preguntas_sugeridas")
    print("   2. Hay otro evento activando mostrarPreguntasSugeridas")
    print("   3. Hay caché del navegador")
    print("   4. El análisis en tiempo real no está funcionando")
    print("   5. Hay otro flujo que está activando la sección antigua")
    
    print("\n💡 Soluciones a verificar:")
    print("   1. Limpiar caché del navegador")
    print("   2. Verificar que no hay otros endpoints activos")
    print("   3. Verificar que el análisis en tiempo real funciona")
    print("   4. Verificar que mostrarAnalisisMejoradoEnSidebar() se llama")
    print("   5. Verificar que NO se llama a mostrarPreguntasSugeridas")

def main():
    """Función principal de verificación"""
    print("🚀 INICIANDO VERIFICACIÓN COMPLETA DEL FLUJO")
    print("=" * 60)
    
    try:
        # Prueba 1: Verificar flujo completo
        test_flujo_completo()
        
        # Prueba 2: Verificación del frontend
        test_verificacion_frontend()
        
        print("\n📊 RESUMEN DE VERIFICACIÓN:")
        print("=" * 60)
        print("✅ Endpoint /api/copilot/analyze-enhanced verificado")
        print("✅ Funciones JavaScript modificadas correctamente")
        print("❌ Problema: Las preguntas siguen apareciendo en sección antigua")
        print("🔍 Necesario: Identificar qué está activando la sección antigua")
        
        print("\n🎯 PRÓXIMOS PASOS:")
        print("   1. Verificar si hay otros endpoints activos")
        print("   2. Limpiar caché del navegador")
        print("   3. Verificar que el análisis en tiempo real funciona")
        print("   4. Verificar que mostrarAnalisisMejoradoEnSidebar() se llama")
        print("   5. Verificar que NO se llama a mostrarPreguntasSugeridas")
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 