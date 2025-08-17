#!/usr/bin/env python3
"""
Test de múltiples casos para verificar preguntas personalizadas
"""

import requests
import json

def test_caso(motivo_consulta, tipo_atencion, nombre_caso):
    """Prueba un caso específico"""
    url = "http://localhost:5000/api/copilot/test-analyze-motivo"
    
    data = {
        "motivo_consulta": motivo_consulta,
        "tipo_atencion": tipo_atencion
    }
    
    try:
        print(f"\n📋 CASO: {nombre_caso}")
        print("-" * 50)
        print(f"Motivo: {motivo_consulta}")
        print(f"Tipo de atención: {tipo_atencion}")
        
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            response_json = response.json()
            
            if response_json.get('success'):
                analisis = response_json['analisis']
                preguntas = analisis.get('preguntas_sugeridas', [])
                especialidad = analisis.get('especialidad_detectada', '')
                
                print(f"✅ Especialidad detectada: {especialidad}")
                print(f"📊 Número de preguntas: {len(preguntas)}")
                
                print("\n📝 Preguntas generadas:")
                for i, pregunta in enumerate(preguntas, 1):
                    print(f"  {i}. {pregunta}")
                
                # Verificar que no sean preguntas genéricas
                preguntas_genericas = {
                    'fonoaudiologia': [
                        "¿Ha notado cambios en su voz o habla?",
                        "¿Tiene dificultades para tragar?",
                        "¿Hay problemas de comunicación?"
                    ],
                    'kinesiologia': [
                        "¿Qué movimientos le resultan más difíciles?",
                        "¿Ha notado mejoría con algún tipo de ejercicio?",
                        "¿Hay actividades que ya no puede realizar?"
                    ],
                    'psicologia': [
                        "¿Cómo se ha sentido emocionalmente últimamente?",
                        "¿Ha notado cambios en su estado de ánimo?",
                        "¿Cómo está manejando el estrés?"
                    ]
                }
                
                coincidencias = 0
                if especialidad in preguntas_genericas:
                    for pregunta in preguntas:
                        if pregunta in preguntas_genericas[especialidad]:
                            coincidencias += 1
                
                if coincidencias < 3:
                    print(f"✅ EXCELENTE - {len(preguntas)} preguntas personalizadas generadas")
                    return True
                else:
                    print(f"⚠️ ADVERTENCIA - {coincidencias} preguntas genéricas detectadas")
                    return False
            else:
                print(f"❌ Error en respuesta: {response_json.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    
    casos = [
        {
            "nombre": "Fonoaudiología - Problemas de Voz",
            "motivo": "Tengo problemas con mi voz, se me cansa muy rápido y a veces se me quiebra cuando hablo",
            "tipo": "fonoaudiologia"
        },
        {
            "nombre": "Fonoaudiología - Dificultad para Tragar",
            "motivo": "Me cuesta mucho tragar los alimentos, especialmente los sólidos, y a veces me atraganto",
            "tipo": "fonoaudiologia"
        },
        {
            "nombre": "Kinesiología - Lesión Deportiva",
            "motivo": "Me lesioné jugando fútbol, tengo dolor en la rodilla derecha y no puedo doblarla bien",
            "tipo": "kinesiologia"
        },
        {
            "nombre": "Psicología - Ansiedad",
            "motivo": "Me siento muy ansioso últimamente, no puedo dormir bien y me preocupo por todo",
            "tipo": "psicologia"
        },
        {
            "nombre": "Nutrición - Control de Peso",
            "motivo": "Quiero bajar de peso, he subido 15 kilos en el último año y no sé cómo controlarlo",
            "tipo": "nutricion"
        }
    ]
    
    print("🧪 PRUEBAS DE PREGUNTAS PERSONALIZADAS")
    print("=" * 60)
    
    exitosos = 0
    total = len(casos)
    
    for caso in casos:
        resultado = test_caso(caso["motivo"], caso["tipo"], caso["nombre"])
        if resultado:
            exitosos += 1
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Casos exitosos: {exitosos}/{total}")
    
    if exitosos == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema genera preguntas personalizadas correctamente.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar el sistema.")
    
    return exitosos == total

if __name__ == "__main__":
    main() 