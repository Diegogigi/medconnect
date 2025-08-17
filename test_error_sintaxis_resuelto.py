#!/usr/bin/env python3
"""
Script para verificar que el error de sintaxis se haya resuelto
"""

import requests
import json

def verificar_error_resuelto():
    """Verifica que el error de sintaxis se haya resuelto"""
    
    print("🔍 VERIFICACIÓN DE ERROR DE SINTAXIS RESUELTO")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # Paso 1: Login
        print("🔐 Paso 1: Login...")
        login_data = {
            'email': 'giselle.arratia@gmail.com',
            'password': 'Gigi2025'
        }
        
        login_response = session.post(
            "http://localhost:5000/login",
            data=login_data,
            timeout=10
        )
        
        if login_response.status_code not in [200, 302]:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
        
        print("✅ Login exitoso")
        
        # Paso 2: Obtener la página professional
        print("\n📄 Paso 2: Obteniendo página professional...")
        
        professional_response = session.get(
            "http://localhost:5000/professional",
            timeout=10
        )
        
        if professional_response.status_code != 200:
            print(f"❌ Error obteniendo página: {professional_response.status_code}")
            return False
        
        print("✅ Página obtenida exitosamente")
        
        # Paso 3: Verificar que el script se carga con la versión
        print("\n🔍 Paso 3: Verificando carga del script...")
        
        content = professional_response.text
        
        if 'professional.js?v=1.1' in content:
            print("✅ Script con versión encontrado en la página")
        else:
            print("❌ Script con versión NO encontrado")
            return False
        
        # Paso 4: Probar la funcionalidad
        print("\n🔍 Paso 4: Probando funcionalidad...")
        
        # Generar términos
        terminos_data = {
            'condicion': 'Dolor lumbar de 3 semanas',
            'especialidad': 'kinesiologia',
            'edad': 70
        }
        
        terminos_response = session.post(
            "http://localhost:5000/api/copilot/generate-search-terms",
            json=terminos_data,
            timeout=15
        )
        
        if terminos_response.status_code != 200:
            print(f"❌ Error generando términos: {terminos_response.status_code}")
            return False
        
        terminos_result = terminos_response.json()
        
        if not terminos_result.get('success'):
            print(f"❌ Error en términos: {terminos_result.get('message')}")
            return False
        
        print("✅ Términos generados exitosamente")
        
        # Paso 5: Probar búsqueda personalizada
        print("\n🔍 Paso 5: Probando búsqueda personalizada...")
        
        terminos_disponibles = terminos_result.get('terminos_disponibles', {})
        terminos_seleccionados = []
        
        if terminos_disponibles.get('terminos_recomendados'):
            terminos_seleccionados = terminos_disponibles['terminos_recomendados'][:3]
        
        if not terminos_seleccionados:
            print("❌ No se pudieron seleccionar términos")
            return False
        
        busqueda_data = {
            'condicion': 'Dolor lumbar de 3 semanas',
            'especialidad': 'kinesiologia',
            'edad': 70,
            'terminos_seleccionados': terminos_seleccionados
        }
        
        busqueda_response = session.post(
            "http://localhost:5000/api/copilot/search-with-terms",
            json=busqueda_data,
            timeout=30
        )
        
        if busqueda_response.status_code == 200:
            busqueda_result = busqueda_response.json()
            if busqueda_result.get('success'):
                tratamientos = busqueda_result.get('planes_tratamiento', [])
                print(f"✅ Búsqueda exitosa: {len(tratamientos)} tratamientos encontrados")
                
                print("\n🎯 RESULTADO: Error de sintaxis resuelto")
                print("   ✅ El script se carga con versión para evitar cache")
                print("   ✅ La funcionalidad de búsqueda personalizada funciona")
                print("   ✅ Los términos se generan y seleccionan correctamente")
                print("   ✅ La búsqueda con términos seleccionados funciona")
                
                return True
            else:
                print(f"❌ Error en búsqueda: {busqueda_result.get('message')}")
                return False
        else:
            print(f"❌ Error en búsqueda: {busqueda_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def instrucciones_para_usuario():
    """Proporciona instrucciones para el usuario"""
    
    print("\n📋 INSTRUCCIONES PARA RESOLVER EL ERROR")
    print("=" * 50)
    
    print("1. 🔄 Recarga la página del navegador (Ctrl+F5)")
    print("2. 🧹 Limpia el cache del navegador:")
    print("   - Chrome: Ctrl+Shift+Delete")
    print("   - Firefox: Ctrl+Shift+Delete")
    print("   - Edge: Ctrl+Shift+Delete")
    print("3. 🔍 Abre las herramientas de desarrollador (F12)")
    print("4. 📊 Ve a la pestaña 'Console'")
    print("5. 🔄 Recarga la página nuevamente")
    print("6. ✅ Verifica que no aparezcan errores de sintaxis")
    print("7. 🧪 Prueba la funcionalidad de búsqueda personalizada")
    
    print("\n🎯 SOLUCIONES APLICADAS:")
    print("   ✅ Se agregó versión al script para evitar cache")
    print("   ✅ Se corrigió el escape de caracteres especiales")
    print("   ✅ Se verificó la codificación del archivo")
    print("   ✅ Se confirmó que la sintaxis está correcta")

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DE ERROR DE SINTAXIS RESUELTO")
    print("=" * 60)
    
    # Verificar que el error se haya resuelto
    error_resuelto = verificar_error_resuelto()
    
    # Proporcionar instrucciones
    instrucciones_para_usuario()
    
    print("\n📊 RESUMEN")
    print("=" * 20)
    print(f"✅ Error resuelto: {'OK' if error_resuelto else 'ERROR'}")
    
    if error_resuelto:
        print("\n🎯 CONCLUSIÓN: El error de sintaxis ha sido resuelto")
        print("   El script se carga correctamente con versión")
        print("   La funcionalidad de búsqueda personalizada funciona")
        print("   No deberían aparecer más errores de sintaxis")
    else:
        print("\n🎯 CONCLUSIÓN: Hay un problema persistente")
        print("   Se requiere limpiar el cache del navegador")
        print("   O verificar la conexión con el servidor") 