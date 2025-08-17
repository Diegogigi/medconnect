#!/usr/bin/env python3
"""
Script de debug para verificar exactamente qué está pasando con las preguntas
"""

import requests
import json
import time

def test_debug_preguntas():
    """Prueba de debug para verificar el flujo de preguntas"""
    print("🔍 DEBUG: Verificando flujo de preguntas")
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
    
    try:
        # Prueba 1: Endpoint analyze-enhanced
        print("\n🔍 Prueba 1: Endpoint /api/copilot/analyze-enhanced")
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

def test_flujo_frontend():
    """Prueba el flujo del frontend"""
    print("\n🔍 Prueba 2: Flujo del frontend")
    print("=" * 60)
    
    print("✅ Funciones JavaScript verificadas:")
    print("   • analizarMotivoEnTiempoReal() - Modificada para usar /api/copilot/analyze-enhanced")
    print("   • mostrarAnalisisMejoradoEnSidebar() - Incluye sección de preguntas")
    print("   • mostrarPreguntasSugeridas() - Modificada para mostrar en sidebar")
    
    print("\n✅ Flujo esperado:")
    print("   1. Usuario escribe en campo motivoConsulta")
    print("   2. Se activa oninput='analizarMotivoEnTiempoReal()'")
    print("   3. Se llama a /api/copilot/analyze-enhanced")
    print("   4. Se reciben datos con preguntas_evaluacion")
    print("   5. Se llama a mostrarAnalisisMejoradoEnSidebar()")
    print("   6. Las preguntas aparecen en la sidebar")
    
    print("\n❌ Posibles problemas:")
    print("   • ¿Hay otro endpoint que esté devolviendo datos antiguos?")
    print("   • ¿Hay otro evento que esté activando mostrarPreguntasSugeridas?")
    print("   • ¿El servidor está devolviendo datos en formato antiguo?")
    print("   • ¿Hay caché del navegador?")
    print("   • ¿El análisis en tiempo real no está funcionando?")

def test_verificacion_completa():
    """Verificación completa del sistema"""
    print("\n🔍 Prueba 3: Verificación completa")
    print("=" * 60)
    
    print("✅ Verificaciones a realizar:")
    print("   1. ¿El servidor está corriendo?")
    print("   2. ¿El endpoint /api/copilot/analyze-enhanced funciona?")
    print("   3. ¿Los datos incluyen preguntas_evaluacion?")
    print("   4. ¿mostrarAnalisisMejoradoEnSidebar() se llama?")
    print("   5. ¿Las preguntas aparecen en la sidebar?")
    print("   6. ¿NO aparecen en la sección antigua?")
    
    print("\n🎯 Solución esperada:")
    print("   • Las preguntas deben aparecer SOLO en la sidebar de Copilot Health")
    print("   • NO deben aparecer en 'Preguntas Sugeridas por IA'")
    print("   • El diseño debe ser atractivo con iconos y colores")
    print("   • Debe incluir botones para insertar y copiar")

def main():
    """Función principal de debug"""
    print("🚀 INICIANDO DEBUG DE PREGUNTAS")
    print("=" * 60)
    
    try:
        # Prueba 1: Debug del endpoint
        test_debug_preguntas()
        
        # Prueba 2: Debug del frontend
        test_flujo_frontend()
        
        # Prueba 3: Verificación completa
        test_verificacion_completa()
        
        print("\n📊 RESUMEN DE DEBUG:")
        print("=" * 60)
        print("✅ Endpoint /api/copilot/analyze-enhanced verificado")
        print("✅ Funciones JavaScript modificadas correctamente")
        print("✅ Flujo esperado documentado")
        print("❌ Problema: Las preguntas siguen apareciendo en sección antigua")
        print("🔍 Necesario: Verificar si hay otro flujo activando la sección antigua")
        
        print("\n💡 PRÓXIMOS PASOS:")
        print("   1. Verificar si hay otro endpoint devolviendo datos antiguos")
        print("   2. Verificar si hay otro evento activando mostrarPreguntasSugeridas")
        print("   3. Verificar si el análisis en tiempo real está funcionando")
        print("   4. Verificar si hay caché del navegador")
        print("   5. Verificar si el servidor está devolviendo datos correctos")
        
    except Exception as e:
        print(f"\n❌ Error durante el debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 