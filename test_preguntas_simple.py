#!/usr/bin/env python3
"""
Script simple para probar el sistema de preguntas personalizadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from medical_apis_integration import MedicalAPIsIntegration

def test_preguntas_simple():
    """Prueba simple del sistema de preguntas personalizadas"""
    print("🧪 PRUEBA SIMPLE DE PREGUNTAS PERSONALIZADAS")
    print("=" * 50)
    
    try:
        # Crear instancia de APIs
        apis = MedicalAPIsIntegration()
        print("✅ APIs médicas inicializadas correctamente")
        
        # Probar con caso de fonoaudiología
        motivo = "Dificultad de lactancia, posible frenillo lingual corto"
        tipo = "fonoaudiologia"
        
        print(f"\n🔍 Probando:")
        print(f"   Motivo: {motivo}")
        print(f"   Tipo: {tipo}")
        
        # Generar preguntas
        preguntas = apis.generar_preguntas_personalizadas_evaluacion(motivo, tipo)
        
        print(f"\n✅ Preguntas generadas: {len(preguntas)}")
        
        for i, pregunta in enumerate(preguntas, 1):
            print(f"   {i}. {pregunta}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_preguntas_simple()
    sys.exit(0 if success else 1) 