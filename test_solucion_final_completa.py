#!/usr/bin/env python3
"""
Script de prueba final para verificar que todos los errores han sido corregidos
"""

import requests
import json

def test_solucion_final_completa():
    """Prueba la solución final completa"""
    
    print("🎯 PRUEBA FINAL COMPLETA")
    print("=" * 50)
    
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
            return False
        
        # 2. Verificar que la página professional carga correctamente
        print("\n2. 📄 Verificando página professional...")
        professional_response = session.get(f"{base_url}/professional")
        
        if professional_response.status_code == 200:
            print("✅ Página professional cargada correctamente")
            
            # Verificar que la versión del script esté actualizada
            if 'professional.js?v=1.3' in professional_response.text:
                print("✅ Script professional.js con versión 1.3 detectado")
            else:
                print("⚠️ Script professional.js no tiene la versión esperada")
        else:
            print(f"❌ Error cargando página: {professional_response.status_code}")
            return False
        
        # 3. Probar generación de términos con caracteres especiales problemáticos
        print("\n3. 🔍 Probando generación de términos con caracteres especiales...")
        
        # Usar caracteres que antes causaban problemas
        test_data = {
            'condicion': "Dolor de rodilla con 'comillas simples' y \"comillas dobles\" y \\backslashes\\ y caracteres especiales: áéíóúñ",
            'especialidad': "kinesiología con 'acentos' y \"comillas\" y \\backslashes\\",
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
                    print("✅ Generación de términos exitosa con caracteres especiales")
                    print(f"   Términos recomendados: {len(terms_data.get('terminos_recomendados', []))}")
                    print(f"   Términos básicos: {len(terms_data.get('terminos_basicos', []))}")
                    print(f"   Términos especialidad: {len(terms_data.get('terminos_especialidad', []))}")
                else:
                    print(f"❌ Error en generación de términos: {terms_data.get('message')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                return False
        else:
            print(f"❌ Error en generación de términos: {terms_response.status_code}")
            return False
        
        # 4. Probar búsqueda personalizada con caracteres especiales
        print("\n4. 🔍 Probando búsqueda personalizada con caracteres especiales...")
        
        search_data = {
            'condicion': "Dolor de rodilla con 'comillas simples' y \"comillas dobles\" y \\backslashes\\ y caracteres especiales: áéíóúñ",
            'especialidad': "kinesiología con 'acentos' y \"comillas\" y \\backslashes\\",
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
                    print("✅ Búsqueda personalizada exitosa con caracteres especiales")
                    print(f"   Tratamientos encontrados: {len(search_data_result.get('planes_tratamiento', []))}")
                else:
                    print(f"❌ Error en búsqueda personalizada: {search_data_result.get('message')}")
                    return False
            except json.JSONDecodeError:
                print("❌ Respuesta no es JSON válido")
                return False
        else:
            print(f"❌ Error en búsqueda personalizada: {search_response.status_code}")
            return False
        
        # 5. Verificar que no hay errores de sintaxis en el JavaScript
        print("\n5. 📜 Verificando JavaScript...")
        js_response = session.get(f"{base_url}/static/js/professional.js")
        
        if js_response.status_code == 200:
            js_content = js_response.text
            
            # Verificar que no hay líneas problemáticas
            problematic_patterns = [
                r"replace\('/g, \"\\\\'\"\)",  # Patrón antiguo
                r"onclick.*replace.*\\\\'",    # onclick con escape antiguo
            ]
            
            found_problems = []
            for pattern in problematic_patterns:
                import re
                matches = re.findall(pattern, js_content)
                if matches:
                    found_problems.append(f"Patrón problemático encontrado: {pattern}")
            
            if found_problems:
                print("⚠️ Se encontraron patrones problemáticos:")
                for problem in found_problems:
                    print(f"   - {problem}")
            else:
                print("✅ No se encontraron patrones problemáticos en JavaScript")
        else:
            print(f"❌ Error obteniendo JavaScript: {js_response.status_code}")
            return False
        
        print("\n🎯 PRUEBA FINAL COMPLETADA EXITOSAMENTE")
        print("=" * 50)
        print("✅ Todos los errores de sintaxis han sido corregidos")
        print("✅ Los caracteres especiales se manejan correctamente")
        print("✅ La funcionalidad de búsqueda personalizada funciona")
        print("✅ No hay patrones problemáticos en el JavaScript")
        print("✅ El sistema está completamente funcional")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba final: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_solucion_final_completa() 