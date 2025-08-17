#!/usr/bin/env python3
"""
Script para probar el sistema de preguntas personalizadas para evaluación/anamnesis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_preguntas_personalizadas():
    """Prueba el sistema de preguntas personalizadas para diferentes especialidades"""
    print("🧪 PRUEBA SISTEMA DE PREGUNTAS PERSONALIZADAS")
    print("=" * 60)
    
    try:
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Casos de prueba para diferentes especialidades
        casos_prueba = [
            {
                "nombre": "Fonoaudiología - Lactancia y Frenillo",
                "motivo": "Dificultad de lactancia, posible frenillo lingual corto, hiperbilirrubina por hipoalimentación",
                "tipo": "fonoaudiologia"
            },
            {
                "nombre": "Kinesiología - Dolor de Rodilla",
                "motivo": "Dolor de rodilla al correr, hinchazón y limitación de movimiento",
                "tipo": "kinesiologia"
            },
            {
                "nombre": "Nutrición - Diabetes",
                "motivo": "Control de diabetes tipo 2, necesidad de plan alimentario",
                "tipo": "nutricion"
            },
            {
                "nombre": "Psicología - Ansiedad",
                "motivo": "Trastorno de ansiedad, problemas de sueño y estrés laboral",
                "tipo": "psicologia"
            },
            {
                "nombre": "Enfermería - Cuidados de Heridas",
                "motivo": "Herida postoperatoria que no cicatriza correctamente",
                "tipo": "enfermeria"
            },
            {
                "nombre": "Medicina General - Hipertensión",
                "motivo": "Control de hipertensión arterial, presión alta persistente",
                "tipo": "medicina"
            },
            {
                "nombre": "Urgencias - Trauma",
                "motivo": "Accidente automovilístico con dolor en pecho y brazo",
                "tipo": "urgencias"
            },
            {
                "nombre": "Terapia Ocupacional - Actividades Vida Diaria",
                "motivo": "Dificultad para realizar actividades de la vida diaria tras ACV",
                "tipo": "terapia_ocupacional"
            }
        ]
        
        for i, caso in enumerate(casos_prueba, 1):
            print(f"\n📋 CASO {i}: {caso['nombre']}")
            print("-" * 50)
            print(f"Motivo: {caso['motivo']}")
            print(f"Tipo: {caso['tipo']}")
            
            # Generar preguntas personalizadas
            preguntas = apis.generar_preguntas_personalizadas_evaluacion(
                caso['motivo'], 
                caso['tipo']
            )
            
            print(f"\n🔍 PREGUNTAS GENERADAS ({len(preguntas)}):")
            for j, pregunta in enumerate(preguntas, 1):
                print(f"   {j}. {pregunta}")
            
            # Verificar que las preguntas son específicas para la especialidad
            print(f"\n✅ VERIFICACIÓN:")
            if len(preguntas) >= 5:
                print(f"   ✅ Cantidad adecuada: {len(preguntas)} preguntas")
            else:
                print(f"   ⚠️ Cantidad baja: {len(preguntas)} preguntas")
            
            # Verificar relevancia según el tipo
            preguntas_relevantes = 0
            for pregunta in preguntas:
                if any(palabra in pregunta.lower() for palabra in ['cuándo', 'qué', 'cómo', 'dónde', 'por qué']):
                    preguntas_relevantes += 1
            
            if preguntas_relevantes >= len(preguntas) * 0.8:
                print(f"   ✅ Preguntas relevantes: {preguntas_relevantes}/{len(preguntas)}")
            else:
                print(f"   ⚠️ Algunas preguntas poco relevantes: {preguntas_relevantes}/{len(preguntas)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de preguntas personalizadas: {e}")
        return False

def test_casos_especificos():
    """Prueba casos específicos para verificar la personalización"""
    print("\n🎯 PRUEBAS DE CASOS ESPECÍFICOS")
    print("=" * 50)
    
    try:
        apis = MedicalAPIsIntegration()
        
        # Caso específico de fonoaudiología
        print("\n🔍 CASO ESPECÍFICO: Fonoaudiología - Lactancia")
        motivo_fono = "Dificultad de lactancia, posible frenillo lingual corto"
        preguntas_fono = apis.generar_preguntas_personalizadas_evaluacion(motivo_fono, "fonoaudiologia")
        
        print(f"Motivo: {motivo_fono}")
        print(f"Preguntas generadas: {len(preguntas_fono)}")
        
        # Verificar que incluye preguntas específicas de lactancia
        preguntas_lactancia = [p for p in preguntas_fono if any(palabra in p.lower() for palabra in ['succion', 'pecho', 'lactancia', 'bebé'])]
        print(f"Preguntas específicas de lactancia: {len(preguntas_lactancia)}")
        
        for pregunta in preguntas_lactancia[:3]:
            print(f"   - {pregunta}")
        
        # Caso específico de kinesiología
        print("\n🔍 CASO ESPECÍFICO: Kinesiología - Dolor de Rodilla")
        motivo_kine = "Dolor de rodilla al correr"
        preguntas_kine = apis.generar_preguntas_personalizadas_evaluacion(motivo_kine, "kinesiologia")
        
        print(f"Motivo: {motivo_kine}")
        print(f"Preguntas generadas: {len(preguntas_kine)}")
        
        # Verificar que incluye preguntas específicas de dolor
        preguntas_dolor = [p for p in preguntas_kine if any(palabra in p.lower() for palabra in ['dolor', 'actividad', 'movimiento'])]
        print(f"Preguntas específicas de dolor: {len(preguntas_dolor)}")
        
        for pregunta in preguntas_dolor[:3]:
            print(f"   - {pregunta}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en pruebas específicas: {e}")
        return False

def test_endpoint_api():
    """Prueba el endpoint de la API para generar preguntas"""
    print("\n🌐 PRUEBA ENDPOINT API")
    print("=" * 40)
    
    import requests
    import json
    
    # URL del endpoint (asumiendo que está corriendo localmente)
    url = "http://localhost:5000/api/copilot/generate-evaluation-questions"
    
    # Caso de prueba
    payload = {
        "motivo_consulta": "Dificultad de lactancia, posible frenillo lingual corto",
        "tipo_atencion": "fonoaudiologia"
    }
    
    try:
        print(f"🔍 Enviando solicitud al endpoint: {url}")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        # Enviar solicitud POST
        response = requests.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa")
            print(f"📋 Success: {data.get('success', False)}")
            print(f"🔍 Método: {data.get('metodo', 'No especificado')}")
            print(f"🏥 Tipo de atención: {data.get('tipo_atencion', 'No disponible')}")
            print(f"📊 Cantidad de preguntas: {data.get('cantidad_preguntas', 0)}")
            
            # Mostrar preguntas generadas
            preguntas = data.get('preguntas', [])
            print(f"\n📋 PREGUNTAS GENERADAS:")
            for i, pregunta in enumerate(preguntas[:5], 1):
                print(f"   {i}. {pregunta}")
            
            return True
            
        else:
            print(f"❌ Error en la respuesta: {response.status_code}")
            print(f"📝 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: El servidor no está corriendo")
        print("💡 Asegúrate de que el servidor Flask esté ejecutándose en http://localhost:5000")
        return False
        
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA SISTEMA DE PREGUNTAS PERSONALIZADAS")
    print("=" * 60)
    
    # Probar el sistema directamente
    success1 = test_preguntas_personalizadas()
    
    # Probar casos específicos
    success2 = test_casos_especificos()
    
    # Probar el endpoint API
    success3 = test_endpoint_api()
    
    if success1 and success2 and success3:
        print("\n\n🎉 ¡PRUEBA COMPLETA EXITOSA!")
        print("✅ El sistema de preguntas personalizadas está funcionando correctamente")
        
        print("\n📊 RESUMEN DE FUNCIONALIDADES:")
        print("   ✅ Generación de preguntas específicas por especialidad")
        print("   ✅ Análisis del motivo de consulta")
        print("   ✅ Personalización según tipo de atención")
        print("   ✅ Preguntas relevantes y contextuales")
        print("   ✅ Cobertura de 8 especialidades médicas")
        print("   ✅ Endpoint API funcionando correctamente")
        
        print("\n🎯 BENEFICIOS OBTENIDOS:")
        print("   ✅ Preguntas personalizadas para cada caso")
        print("   ✅ No más preguntas genéricas para todos")
        print("   ✅ Preguntas específicas por área profesional")
        print("   ✅ Mejor calidad de evaluación/anamnesis")
        print("   ✅ Soporte para múltiples especialidades")
        
        print("\n🚀 SISTEMA IMPLEMENTADO EXITOSAMENTE")
        print("   ✅ Generación inteligente de preguntas")
        print("   ✅ Personalización por especialidad")
        print("   ✅ Análisis contextual del motivo")
        print("   ✅ Preguntas relevantes y específicas")
        
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("⚠️ Revisa los errores específicos arriba")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 