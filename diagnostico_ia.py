#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el estado de la IA en el formulario
"""

import requests
import json
import sys

def test_api_endpoint():
    """Prueba el endpoint de la API de IA"""
    print("🔍 DIAGNÓSTICO DE LA IA")
    print("=" * 50)
    
    # URL base (ajustar según tu configuración)
    base_url = "http://localhost:5000"
    
    # Caso de prueba
    test_data = {
        "motivo_consulta": "Dolor lumbar agudo tras levantar objetos pesados en el trabajo. Presenta rigidez matinal y dificultad para inclinarse.",
        "tipo_atencion": "kinesiologia"
    }
    
    print(f"📡 Probando endpoint: {base_url}/api/copilot/test-analyze-motivo")
    print(f"📝 Datos de prueba: {json.dumps(test_data, indent=2)}")
    
    try:
        # Hacer la petición
        response = requests.post(
            f"{base_url}/api/copilot/test-analyze-motivo",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                analisis = data.get('analisis', {})
                print(f"\n🎯 Análisis de IA:")
                print(f"   Especialidad: {analisis.get('especialidad_detectada')}")
                print(f"   Categoría: {analisis.get('categoria')}")
                print(f"   Urgencia: {analisis.get('urgencia')}")
                print(f"   Síntomas: {analisis.get('sintomas_principales')}")
                print(f"   Preguntas: {len(analisis.get('preguntas_sugeridas', []))} preguntas")
                
                for i, pregunta in enumerate(analisis.get('preguntas_sugeridas', []), 1):
                    print(f"     {i}. {pregunta}")
            else:
                print(f"❌ Error en la respuesta: {data.get('message')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor Flask esté ejecutándose")
    except requests.exceptions.Timeout:
        print("❌ Error de timeout: La petición tardó demasiado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_copilot_health_module():
    """Prueba el módulo Copilot Health directamente"""
    print("\n🧪 PRUEBA DIRECTA DEL MÓDULO COPILOT HEALTH")
    print("=" * 50)
    
    try:
        from copilot_health import CopilotHealth
        
        # Crear instancia
        copilot = CopilotHealth()
        print("✅ Módulo Copilot Health cargado correctamente")
        
        # Probar normalización
        test_cases = [
            ("fisio", "fisioterapia"),
            ("kinesio", "kinesiologia"),
            ("fono", "fonoaudiologia"),
            ("logopeda", "fonoaudiologia"),
            ("psicologo", "psicologia"),
            ("nutricionista", "nutricion")
        ]
        
        print("\n🔍 Probando normalización regional:")
        for input_val, expected in test_cases:
            result = copilot._normalizar_tipo_atencion(input_val)
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{input_val}' -> '{result}' (esperado: '{expected}')")
        
        # Probar análisis completo
        print("\n🔍 Probando análisis completo:")
        motivo = "Dolor lumbar agudo tras levantar objetos pesados en el trabajo"
        tipo_atencion = "kinesiologia"
        
        resultado = copilot.analizar_motivo_consulta(motivo, tipo_atencion)
        
        print(f"   Motivo: {motivo}")
        print(f"   Tipo atención: {tipo_atencion}")
        print(f"   Especialidad detectada: {resultado.especialidad_detectada}")
        print(f"   Categoría: {resultado.categoria}")
        print(f"   Urgencia: {resultado.urgencia}")
        print(f"   Síntomas: {resultado.sintomas_principales}")
        print(f"   Preguntas sugeridas: {len(resultado.preguntas_sugeridas)}")
        
        for i, pregunta in enumerate(resultado.preguntas_sugeridas, 1):
            print(f"     {i}. {pregunta}")
            
    except ImportError as e:
        print(f"❌ Error importando módulo: {e}")
    except Exception as e:
        print(f"❌ Error en prueba del módulo: {e}")

def test_flask_app():
    """Prueba si la aplicación Flask está funcionando"""
    print("\n🌐 PRUEBA DE LA APLICACIÓN FLASK")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"✅ Servidor Flask funcionando (Status: {response.status_code})")
        
        # Probar endpoint de health
        if response.status_code == 200:
            print("✅ Endpoint /health responde correctamente")
        else:
            print(f"⚠️ Endpoint /health responde con status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor Flask")
        print("💡 Ejecuta 'python app.py' para iniciar el servidor")
    except Exception as e:
        print(f"❌ Error probando Flask: {e}")

def main():
    """Función principal"""
    print("🚀 INICIANDO DIAGNÓSTICO COMPLETO DE LA IA")
    print("=" * 60)
    
    # Probar Flask
    test_flask_app()
    
    # Probar módulo
    test_copilot_health_module()
    
    # Probar API
    test_api_endpoint()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    print("✅ Si todas las pruebas pasan, la IA debería funcionar correctamente")
    print("❌ Si hay errores, revisa los mensajes anteriores")
    print("\n💡 Para probar la interfaz web:")
    print("   1. Ve a http://localhost:5000/test-ia-formulario")
    print("   2. Selecciona un tipo de atención")
    print("   3. Escribe un motivo de consulta")
    print("   4. Observa si aparecen las sugerencias de IA")

if __name__ == "__main__":
    main() 