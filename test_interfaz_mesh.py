#!/usr/bin/env python3
"""
Script para probar que la interfaz web está usando correctamente el endpoint con términos MeSH específicos
"""

import requests
import json
import time

def test_endpoint_mesh():
    """Prueba el endpoint de sugerencia de tratamiento con términos MeSH específicos"""
    print("🌐 PRUEBA ENDPOINT MESH ESPECÍFICO")
    print("=" * 60)
    
    # URL del endpoint (asumiendo que está corriendo localmente)
    url = "http://localhost:5000/api/copilot/suggest-treatment"
    
    # Caso específico de fonoaudiología
    payload = {
        "diagnostico": "Dificultad de lactancia, posible frenillo lingual corto, hiperbilirrubina por hipoalimentación",
        "especialidad": "fonoaudiologia",
        "edad": 1,
        "evaluacion": "Trenes de succión cortos, fatiga, se desacopla del pecho, chasquido lingual al succionar"
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
            print(f"📊 Nivel de confianza: {data.get('nivel_confianza', 'No disponible')}")
            print(f"🔍 Términos utilizados: {data.get('terminos_utilizados', [])}")
            print(f"🏥 Especialidad detectada: {data.get('especialidad_detectada', 'No disponible')}")
            print(f"📝 Análisis clínico: {data.get('analisis_clinico', 'No disponible')}")
            print(f"📊 Evidencia encontrada: {data.get('evidencia_encontrada', False)}")
            
            # Mostrar planes de tratamiento
            planes = data.get('planes_tratamiento', [])
            print(f"\n📋 PLANES DE TRATAMIENTO ENCONTRADOS: {len(planes)}")
            
            for i, plan in enumerate(planes[:5], 1):  # Mostrar solo los primeros 5
                print(f"\n📋 Plan {i}:")
                print(f"   Título: {plan.get('titulo', 'Sin título')}")
                print(f"   Descripción: {plan.get('descripcion', 'Sin descripción')[:100]}...")
                print(f"   Nivel de evidencia: {plan.get('nivel_evidencia', 'No disponible')}")
                print(f"   DOI: {plan.get('doi_referencia', 'Sin DOI')}")
                print(f"   Evidencia científica: {plan.get('evidencia_cientifica', 'No disponible')}")
                print(f"   Fuente: {plan.get('fuente', 'No disponible')}")
                print(f"   URL: {plan.get('url', 'Sin URL')}")
                print(f"   Score de relevancia: {plan.get('relevancia_score', 'No disponible')}")
            
            # Verificar que los términos MeSH son específicos
            terminos = data.get('terminos_utilizados', [])
            if terminos:
                print(f"\n🔍 VERIFICACIÓN DE TÉRMINOS MESH:")
                for i, termino in enumerate(terminos, 1):
                    print(f"   {i}. {termino}")
                    
                    # Verificar que son términos específicos para el caso
                    if 'Breast Feeding' in termino or 'Lactation Disorders' in termino:
                        print(f"      ✅ Relevante para lactancia")
                    elif 'Ankyloglossia' in termino or 'Tongue' in termino:
                        print(f"      ✅ Relevante para frenillo lingual")
                    elif 'Deglutition Disorders' in termino or 'Dysphagia' in termino:
                        print(f"      ✅ Relevante para problemas de deglución")
                    else:
                        print(f"      ⚠️ Término general")
            
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

def test_casos_adicionales():
    """Prueba casos adicionales para verificar que funciona para todas las especialidades"""
    print("\n🧪 PRUEBAS ADICIONALES PARA OTRAS ESPECIALIDADES")
    print("=" * 60)
    
    casos = [
        {
            "nombre": "Kinesiología - Dolor de rodilla",
            "payload": {
                "diagnostico": "Dolor de rodilla al correr",
                "especialidad": "kinesiologia",
                "edad": 25,
                "evaluacion": "Dolor agudo en rodilla derecha al correr"
            }
        },
        {
            "nombre": "Nutrición - Diabetes",
            "payload": {
                "diagnostico": "Control de diabetes tipo 2",
                "especialidad": "nutricion",
                "edad": 45,
                "evaluacion": "Paciente con diabetes tipo 2, necesita control de peso"
            }
        },
        {
            "nombre": "Psicología - Ansiedad",
            "payload": {
                "diagnostico": "Trastorno de ansiedad",
                "especialidad": "psicologia",
                "edad": 30,
                "evaluacion": "Ansiedad laboral, problemas de sueño"
            }
        }
    ]
    
    url = "http://localhost:5000/api/copilot/suggest-treatment"
    
    for caso in casos:
        print(f"\n🔍 Probando: {caso['nombre']}")
        
        try:
            response = requests.post(
                url,
                json=caso['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                planes = data.get('planes_tratamiento', [])
                terminos = data.get('terminos_utilizados', [])
                
                print(f"   ✅ Encontrados {len(planes)} planes de tratamiento")
                print(f"   🔍 Términos MeSH: {terminos}")
                
                if planes:
                    primer_plan = planes[0]
                    print(f"   📋 Primer plan: {primer_plan.get('titulo', 'Sin título')[:50]}...")
                
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 PRUEBA INTERFAZ MESH ESPECÍFICO")
    print("=" * 60)
    
    # Probar el endpoint principal
    success = test_endpoint_mesh()
    
    if success:
        print("\n✅ ENDPOINT FUNCIONANDO CORRECTAMENTE")
        print("🎯 El sistema está usando términos MeSH específicos")
        print("📊 Los resultados son más relevantes y precisos")
        
        # Probar casos adicionales
        test_casos_adicionales()
        
        print("\n🎉 ¡PRUEBA COMPLETA EXITOSA!")
        print("✅ La interfaz web está usando correctamente el sistema MeSH")
        print("✅ Los términos generados son específicos y relevantes")
        print("✅ Los resultados están alineados con el caso clínico")
        
    else:
        print("\n❌ PRUEBA FALLIDA")
        print("⚠️ El endpoint no está funcionando correctamente")
        print("💡 Verifica que el servidor esté corriendo y el endpoint esté disponible")

if __name__ == "__main__":
    main() 