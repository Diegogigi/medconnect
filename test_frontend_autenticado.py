#!/usr/bin/env python3
"""
Script para probar el frontend con autenticación
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_login():
    """Prueba el login para obtener una sesión"""
    print("🔐 PRUEBA DE LOGIN")
    print("=" * 30)
    
    url = "http://localhost:5000/login"
    
    # Datos de login (usar credenciales reales del sistema)
    data = {
        'email': 'giselle.arratia@gmail.com',
        'password': '123456',
        'tipo_usuario': 'profesional'
    }
    
    try:
        print("🔍 Intentando login...")
        response = requests.post(url, data=data, allow_redirects=False)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 302:  # Redirect después del login exitoso
            print("✅ Login exitoso (redirect)")
            return response.cookies
        else:
            print("❌ Login falló")
            print(f"Respuesta: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return None

def test_api_con_sesion(cookies):
    """Prueba las APIs con sesión autenticada"""
    print("\n🔍 PRUEBA DE API CON SESIÓN")
    print("=" * 40)
    
    if not cookies:
        print("❌ No hay cookies de sesión")
        return
    
    # Probar API de búsqueda
    url = "http://localhost:5000/api/copilot/suggest-treatment"
    
    data = {
        'motivo_atencion': 'Dolor lumbar de 3 semanas',
        'tipo_atencion': 'kinesiologia',
        'evaluacion_observaciones': 'Paciente presenta dolor lumbar de 3 semanas de evolución, con irradiación hacia la pierna izquierda.'
    }
    
    try:
        print("🔍 Enviando petición de búsqueda con sesión...")
        response = requests.post(url, json=data, cookies=cookies, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resultado = response.json()
                print("✅ Respuesta JSON válida")
                
                if 'tratamientos_cientificos' in resultado:
                    tratamientos = resultado['tratamientos_cientificos']
                    print(f"✅ Encontrados {len(tratamientos)} tratamientos científicos")
                    
                    if tratamientos:
                        print("\n📄 Primer tratamiento:")
                        primer_tratamiento = tratamientos[0]
                        print(f"   Título: {primer_tratamiento.get('titulo', 'Sin título')}")
                        print(f"   DOI: {primer_tratamiento.get('doi', 'Sin DOI')}")
                        print(f"   Fuente: {primer_tratamiento.get('fuente', 'Sin fuente')}")
                    else:
                        print("⚠️ No hay tratamientos en la respuesta")
                else:
                    print("❌ No hay 'tratamientos_cientificos' en la respuesta")
                    print(f"Estructura: {list(resultado.keys())}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
                print(f"Respuesta: {response.text[:200]}...")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"Respuesta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_pacientes_con_sesion(cookies):
    """Prueba la API de pacientes con sesión"""
    print("\n👥 PRUEBA DE PACIENTES CON SESIÓN")
    print("=" * 40)
    
    if not cookies:
        print("❌ No hay cookies de sesión")
        return
    
    url = "http://localhost:5000/api/professional/patients"
    
    try:
        print("🔍 Obteniendo pacientes con sesión...")
        response = requests.get(url, cookies=cookies, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                pacientes = response.json()
                print(f"✅ Encontrados {len(pacientes)} pacientes")
                
                if pacientes:
                    for i, paciente in enumerate(pacientes[:3], 1):
                        print(f"   {i}. {paciente.get('nombre_completo', 'Sin nombre')}")
                else:
                    print("⚠️ No hay pacientes disponibles")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error obteniendo pacientes: {e}")

def test_preguntas_con_sesion(cookies):
    """Prueba la API de preguntas con sesión"""
    print("\n❓ PRUEBA DE PREGUNTAS CON SESIÓN")
    print("=" * 40)
    
    if not cookies:
        print("❌ No hay cookies de sesión")
        return
    
    url = "http://localhost:5000/api/copilot/generate-evaluation-questions"
    
    data = {
        'motivo_atencion': 'Dolor lumbar de 3 semanas',
        'tipo_atencion': 'kinesiologia'
    }
    
    try:
        print("🔍 Generando preguntas con sesión...")
        response = requests.post(url, json=data, cookies=cookies, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                resultado = response.json()
                print("✅ Respuesta JSON válida")
                
                if 'preguntas' in resultado:
                    preguntas = resultado['preguntas']
                    print(f"✅ Generadas {len(preguntas)} preguntas")
                    
                    for i, pregunta in enumerate(preguntas[:3], 1):
                        print(f"   {i}. {pregunta}")
                else:
                    print("❌ No hay 'preguntas' en la respuesta")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error decodificando JSON: {e}")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error generando preguntas: {e}")

def main():
    """Función principal"""
    print("🔍 PRUEBAS DE FRONTEND CON AUTENTICACIÓN")
    print("=" * 50)
    
    # Probar login
    cookies = test_login()
    
    if cookies:
        # Probar APIs con sesión
        test_api_con_sesion(cookies)
        test_pacientes_con_sesion(cookies)
        test_preguntas_con_sesion(cookies)
    else:
        print("❌ No se pudo obtener sesión autenticada")
    
    print("\n✅ Todas las pruebas completadas")

if __name__ == "__main__":
    main() 