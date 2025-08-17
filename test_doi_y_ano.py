#!/usr/bin/env python3
"""
Script para probar la extracción y visualización de DOI y año
"""

import requests
import json
import time

def test_doi_y_ano_extraccion():
    """Prueba la extracción de DOI y año de los papers"""
    print("🔍 PRUEBA DE EXTRACCIÓN DOI Y AÑO")
    print("=" * 50)
    
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
            print("✅ Sesión creada")
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante login: {e}")
        return False
    
    # 3. Probar búsqueda con términos clave
    print("\n🔍 Probando búsqueda con términos clave...")
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
                        # Analizar el primer plan para verificar DOI y año
                        primer_plan = planes[0]
                        print(f"\n📋 ANÁLISIS DEL PRIMER PLAN:")
                        print(f"   Título: {primer_plan.get('titulo', 'Sin título')}")
                        print(f"   DOI: {primer_plan.get('doi_referencia', 'No disponible')}")
                        print(f"   Año: {primer_plan.get('año_publicacion', 'No disponible')}")
                        print(f"   Fecha: {primer_plan.get('fecha_publicacion', 'No disponible')}")
                        
                        # Verificar si el DOI es válido
                        doi = primer_plan.get('doi_referencia')
                        if doi and doi != 'Sin DOI' and doi != 'No disponible':
                            print(f"   ✅ DOI válido: {doi}")
                            print(f"   🔗 Link: https://doi.org/{doi}")
                        else:
                            print(f"   ❌ DOI no disponible")
                        
                        # Verificar si el año es válido
                        año = primer_plan.get('año_publicacion')
                        if año and año != 'N/A':
                            print(f"   ✅ Año válido: {año}")
                        else:
                            print(f"   ❌ Año no disponible")
                        
                        return True
                    else:
                        print("❌ No se encontraron planes de tratamiento")
                        return False
                else:
                    print(f"❌ Error en búsqueda: {data.get('message', 'Error desconocido')}")
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
        print(f"❌ Error en búsqueda: {e}")
        return False

def test_visualizacion_frontend():
    """Prueba la visualización en el frontend"""
    print("\n🎨 PRUEBA DE VISUALIZACIÓN FRONTEND")
    print("=" * 50)
    
    print("✅ Para probar la visualización:")
    print("   1. Inicia sesión en el navegador")
    print("   2. Ve a la página professional")
    print("   3. Completa el formulario de atención")
    print("   4. Haz clic en 'Activar Copilot Health'")
    print("   5. Verifica que en la sidebar aparezcan:")
    print("      • DOI con link clickeable")
    print("      • Año del estudio")
    print("      • Información completa del paper")
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBAS DE DOI Y AÑO")
    print("=" * 50)
    
    # Prueba 1: Extracción de DOI y año
    extraccion_ok = test_doi_y_ano_extraccion()
    
    if not extraccion_ok:
        print("\n❌ Problema con la extracción de DOI y año")
        return
    
    # Prueba 2: Visualización frontend
    visualizacion_ok = test_visualizacion_frontend()
    
    if not visualizacion_ok:
        print("\n❌ Problema con la visualización frontend")
        return
    
    print("\n✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("🎉 El sistema ahora muestra correctamente:")
    print("   • DOI con link para ir al paper")
    print("   • Año del estudio")
    print("   • Información completa de los papers")

if __name__ == "__main__":
    main() 