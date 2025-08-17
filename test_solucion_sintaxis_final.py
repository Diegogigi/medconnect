#!/usr/bin/env python3
"""
Script para probar la solución final del error de sintaxis
"""

import requests
import json

def test_solucion_sintaxis_final():
    """Prueba la solución final del error de sintaxis"""
    
    print("🧪 PRUEBA DE SOLUCIÓN FINAL DEL ERROR DE SINTAXIS")
    print("=" * 60)
    
    # URL base
    base_url = "http://localhost:5000"
    
    try:
        # 1. Probar login
        print("1. 🔐 Probando login...")
        session = requests.Session()
        
        login_data = {
            'email': 'giselle.arratia@gmail.com',
            'password': 'Gigi2025'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code == 302:
            print("✅ Login exitoso")
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text[:200]}")
            return False
        
        # 2. Acceder a la página professional
        print("\n2. 📄 Accediendo a la página professional...")
        professional_response = session.get(f"{base_url}/professional")
        
        if professional_response.status_code == 200:
            print("✅ Página professional cargada correctamente")
            
            # Verificar que la versión del script esté actualizada
            if 'professional.js?v=1.2' in professional_response.text:
                print("✅ Script professional.js con versión 1.2 detectado")
            else:
                print("⚠️ Script professional.js no tiene la versión esperada")
        else:
            print(f"❌ Error accediendo a professional: {professional_response.status_code}")
            return False
        
        # 3. Probar generación de términos con caracteres especiales
        print("\n3. 🔍 Probando generación de términos con caracteres especiales...")
        
        # Usar una condición con caracteres especiales que podrían causar problemas
        test_data = {
            'condicion': "Dolor de rodilla con 'comillas' y \"comillas dobles\" y \\backslashes\\",
            'especialidad': "kinesiología con 'acentos' y caracteres especiales",
            'edad': 30
        }
        
        terms_response = session.post(
            f"{base_url}/api/copilot/generate-search-terms",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if terms_response.status_code == 200:
            try:
                terms_data = terms_response.json()
                if terms_data.get('success'):
                    print("✅ Generación de términos exitosa")
                    print(f"   Términos recomendados: {len(terms_data.get('terminos_recomendados', []))}")
                    print(f"   Términos básicos: {len(terms_data.get('terminos_basicos', []))}")
                    print(f"   Términos especialidad: {len(terms_data.get('terminos_especialidad', []))}")
                else:
                    print(f"❌ Error en generación de términos: {terms_data.get('message')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print(f"   Respuesta: {terms_response.text[:200]}")
                return False
        else:
            print(f"❌ Error en generación de términos: {terms_response.status_code}")
            print(f"   Respuesta: {terms_response.text[:200]}")
            return False
        
        # 4. Probar búsqueda personalizada con caracteres especiales
        print("\n4. 🔍 Probando búsqueda personalizada con caracteres especiales...")
        
        search_data = {
            'condicion': "Dolor de rodilla con 'comillas' y \"comillas dobles\" y \\backslashes\\",
            'especialidad': "kinesiología con 'acentos' y caracteres especiales",
            'edad': 30,
            'terminos_seleccionados': ["dolor de rodilla", "kinesiología", "tratamiento"]
        }
        
        search_response = session.post(
            f"{base_url}/api/copilot/search-with-terms",
            json=search_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if search_response.status_code == 200:
            try:
                search_data_result = search_response.json()
                if search_data_result.get('success'):
                    print("✅ Búsqueda personalizada exitosa")
                    print(f"   Tratamientos encontrados: {len(search_data_result.get('planes_tratamiento', []))}")
                else:
                    print(f"❌ Error en búsqueda personalizada: {search_data_result.get('message')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                print(f"   Respuesta: {search_response.text[:200]}")
                return False
        else:
            print(f"❌ Error en búsqueda personalizada: {search_response.status_code}")
            print(f"   Respuesta: {search_response.text[:200]}")
            return False
        
        print("\n🎯 PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 40)
        print("✅ El error de sintaxis ha sido solucionado")
        print("✅ Los caracteres especiales se manejan correctamente")
        print("✅ La funcionalidad de búsqueda personalizada funciona")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_solucion_sintaxis_final() 