#!/usr/bin/env python3
"""
Test simple del endpoint analyze-motivo
"""

import requests
import json

def test_endpoint():
    url = "http://localhost:5000/api/copilot/test-analyze-motivo"
    
    data = {
        "motivo_consulta": "Tengo problemas con mi voz, se me cansa muy rápido",
        "tipo_atencion": "fonoaudiologia"
    }
    
    try:
        print("🔍 Probando endpoint de prueba...")
        print(f"URL: {url}")
        print(f"Datos: {json.dumps(data, indent=2)}")
        
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Intentar leer la respuesta como texto primero
        response_text = response.text
        print(f"Response Text: {response_text[:500]}...")
        
        if response_text.strip():
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                
                if response_json.get('success'):
                    preguntas = response_json['analisis'].get('preguntas_sugeridas', [])
                    print(f"\n✅ Preguntas generadas: {len(preguntas)}")
                    for i, pregunta in enumerate(preguntas, 1):
                        print(f"  {i}. {pregunta}")
                    
                    # Verificar si las preguntas son personalizadas
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
                    else:
                        print("❌ Las preguntas siguen siendo genéricas - Sistema necesita ajustes")
                        
                else:
                    print(f"❌ Error en respuesta: {response_json.get('message')}")
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
        else:
            print("❌ Respuesta vacía")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_endpoint() 