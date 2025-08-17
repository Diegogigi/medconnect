#!/usr/bin/env python3
"""
Script para probar el análisis completo de Copilot Health
"""

import requests
import json
import time

def test_analisis_completo():
    """Prueba el análisis completo de Copilot Health"""
    print("🤖 PRUEBA DE ANÁLISIS COMPLETO - COPILOT HEALTH")
    print("=" * 60)
    
    # 1. Verificar que el servidor esté funcionando
    print("🔍 Verificando servidor...")
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Servidor funcionando")
        else:
            print(f"❌ Servidor respondió con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False
    
    # 2. Crear sesión autenticada
    print("\n🔐 Creando sesión autenticada...")
    session = requests.Session()
    
    try:
        # Obtener página de login
        response = session.get("http://localhost:5000/login", timeout=10)
        if response.status_code != 200:
            print(f"❌ Error obteniendo página de login: {response.status_code}")
            return False
        
        # Intentar login
        login_data = {
            'username': 'admin@medconnect.cl',
            'password': 'admin123',
            'remember': 'on'
        }
        
        response = session.post("http://localhost:5000/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Sesión creada (login exitoso o redirigido)")
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante login: {e}")
        return False
    
    # 3. Probar análisis completo
    print("\n🔍 Probando análisis completo...")
    url = "http://localhost:5000/api/copilot/complete-analysis"
    
    test_data = {
        "motivo_consulta": "Dolor lumbar crónico de 3 semanas",
        "tipo_atencion": "kinesiologia",
        "edad_paciente": 45,
        "antecedentes": "Paciente con antecedentes de dolor lumbar recurrente",
        "evaluacion": "Dolor en región lumbar, limitación de movimientos"
    }
    
    try:
        print(f"📤 Enviando datos: {test_data}")
        response = session.post(url, json=test_data, timeout=30)
        
        print(f"📥 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    print("✅ Análisis completo realizado correctamente")
                    print(f"📊 Resumen: {data.get('resumen', 'No disponible')}")
                    return True
                else:
                    print(f"❌ Error en análisis completo: {data.get('message', 'Error desconocido')}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Contenido de respuesta: {response.text[:500]}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {error_data}")
            except:
                print(f"📄 Contenido: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en análisis completo: {e}")
        return False

def test_extraccion_terminos_clave():
    """Prueba la extracción de términos clave"""
    print("\n🔍 Probando extracción de términos clave...")
    
    # Crear sesión autenticada
    session = requests.Session()
    
    try:
        # Obtener página de login
        response = session.get("http://localhost:5000/login", timeout=10)
        if response.status_code != 200:
            print(f"❌ Error obteniendo página de login: {response.status_code}")
            return False
        
        # Intentar login
        login_data = {
            'username': 'admin@medconnect.cl',
            'password': 'admin123',
            'remember': 'on'
        }
        
        response = session.post("http://localhost:5000/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Sesión creada para extracción de términos")
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante login: {e}")
        return False
    
    url = "http://localhost:5000/api/copilot/extract-key-terms"
    
    test_data = {
        "analisis": {
            "motivo_consulta": "Dolor lumbar crónico de 3 semanas",
            "tipo_atencion": "kinesiologia",
            "edad_paciente": 45,
            "antecedentes": "Paciente con antecedentes de dolor lumbar recurrente",
            "evaluacion": "Dolor en región lumbar, limitación de movimientos"
        }
    }
    
    try:
        print(f"📤 Enviando datos de análisis...")
        response = session.post(url, json=test_data, timeout=30)
        
        print(f"📥 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    terminos_clave = data.get('terminos_clave', [])
                    print("✅ Términos clave extraídos correctamente")
                    print(f"📋 Términos clave: {terminos_clave}")
                    return True
                else:
                    print(f"❌ Error extrayendo términos clave: {data.get('message', 'Error desconocido')}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Contenido de respuesta: {response.text[:500]}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {error_data}")
            except:
                print(f"📄 Contenido: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error extrayendo términos clave: {e}")
        return False

def test_busqueda_con_terminos_clave():
    """Prueba la búsqueda con términos clave"""
    print("\n🔍 Probando búsqueda con términos clave...")
    
    # Crear sesión autenticada
    session = requests.Session()
    
    try:
        # Obtener página de login
        response = session.get("http://localhost:5000/login", timeout=10)
        if response.status_code != 200:
            print(f"❌ Error obteniendo página de login: {response.status_code}")
            return False
        
        # Intentar login
        login_data = {
            'username': 'admin@medconnect.cl',
            'password': 'admin123',
            'remember': 'on'
        }
        
        response = session.post("http://localhost:5000/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Sesión creada para búsqueda con términos clave")
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante login: {e}")
        return False
    
    url = "http://localhost:5000/api/copilot/search-with-key-terms"
    
    test_data = {
        "condicion": "Dolor lumbar crónico",
        "especialidad": "kinesiologia",
        "edad": 45,
        "terminos_clave": ["physical therapy", "rehabilitation", "exercise", "pain management"]
    }
    
    try:
        print(f"📤 Enviando búsqueda con términos clave...")
        response = session.post(url, json=test_data, timeout=60)
        
        print(f"📥 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('success'):
                    planes = data.get('planes_tratamiento', [])
                    print("✅ Búsqueda con términos clave completada")
                    print(f"📄 Planes de tratamiento encontrados: {len(planes)}")
                    
                    if planes:
                        # Mostrar el primer plan como ejemplo
                        primer_plan = planes[0]
                        print(f"📋 Ejemplo - Título: {primer_plan.get('titulo', 'Sin título')}")
                        print(f"📋 Ejemplo - DOI: {primer_plan.get('doi', 'Sin DOI')}")
                    
                    return True
                else:
                    print(f"❌ Error en búsqueda con términos clave: {data.get('message', 'Error desconocido')}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"📄 Contenido de respuesta: {response.text[:500]}")
                return False
        else:
            print(f"❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📄 Error: {error_data}")
            except:
                print(f"📄 Contenido: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error en búsqueda con términos clave: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE ANÁLISIS COMPLETO")
    print("=" * 60)
    
    # Prueba 1: Análisis completo
    analisis_ok = test_analisis_completo()
    
    if not analisis_ok:
        print("\n❌ Problema con el análisis completo")
        return
    
    # Prueba 2: Extracción de términos clave
    terminos_ok = test_extraccion_terminos_clave()
    
    if not terminos_ok:
        print("\n❌ Problema con la extracción de términos clave")
        return
    
    # Prueba 3: Búsqueda con términos clave
    busqueda_ok = test_busqueda_con_terminos_clave()
    
    if not busqueda_ok:
        print("\n❌ Problema con la búsqueda con términos clave")
        return
    
    print("\n✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("🎉 El análisis completo de Copilot Health está funcionando correctamente")
    print("\n💡 El sistema ahora puede:")
    print("   • Analizar tipo de consulta, edad y motivo")
    print("   • Identificar términos clave del análisis")
    print("   • Generar términos de búsqueda expandidos")
    print("   • Buscar evidencia científica con términos clave")
    print("   • Proporcionar apoyo completo para el tratamiento")

if __name__ == "__main__":
    main() 