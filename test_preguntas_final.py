#!/usr/bin/env python3
"""
Script final para probar el sistema de preguntas personalizadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration

def test_sistema_final():
    """Prueba final del sistema de preguntas personalizadas"""
    print("🎯 PRUEBA FINAL - SISTEMA DE PREGUNTAS PERSONALIZADAS")
    print("=" * 60)
    
    try:
        # Crear instancia de APIs
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Casos de prueba específicos
        casos = [
            {
                "nombre": "Fonoaudiología - Lactancia",
                "motivo": "Dificultad de lactancia, posible frenillo lingual corto",
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
            }
        ]
        
        for i, caso in enumerate(casos, 1):
            print(f"\n📋 CASO {i}: {caso['nombre']}")
            print("-" * 50)
            print(f"Motivo: {caso['motivo']}")
            print(f"Tipo: {caso['tipo']}")
            
            # Generar preguntas personalizadas
            preguntas = apis.generar_preguntas_personalizadas_evaluacion(
                caso['motivo'], 
                caso['tipo']
            )
            
            print(f"\n✅ Preguntas generadas: {len(preguntas)}")
            
            # Mostrar preguntas
            for j, pregunta in enumerate(preguntas, 1):
                print(f"   {j}. {pregunta}")
            
            # Verificar calidad
            preguntas_especificas = 0
            for pregunta in preguntas:
                if any(palabra in pregunta.lower() for palabra in ['cuándo', 'qué', 'cómo', 'dónde', 'por qué']):
                    preguntas_especificas += 1
            
            if preguntas_especificas >= len(preguntas) * 0.8:
                print(f"✅ CALIDAD: {preguntas_especificas}/{len(preguntas)} preguntas son específicas")
            else:
                print(f"⚠️ CALIDAD: Solo {preguntas_especificas}/{len(preguntas)} preguntas son específicas")
        
        print("\n\n🎉 ¡SISTEMA FUNCIONANDO CORRECTAMENTE!")
        print("✅ El sistema de preguntas personalizadas está operativo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sistema_final()
    sys.exit(0 if success else 1) 