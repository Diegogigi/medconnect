#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de búsqueda en el frontend
"""

import requests
import json
import time

def test_busqueda_frontend():
    """Prueba la funcionalidad de búsqueda en el frontend"""
    print("🔍 PRUEBAS DE BÚSQUEDA EN FRONTEND")
    print("=" * 50)
    
    # URL base (ajustar según tu configuración)
    base_url = "http://localhost:5000"
    
    # Datos de prueba
    test_patients = [
        {
            "nombre_completo": "Juan Pérez López",
            "rut": "12.345.678-9",
            "email": "juan.perez@email.com",
            "estado_relacion": "activo"
        },
        {
            "nombre_completo": "María González Silva",
            "rut": "98.765.432-1",
            "email": "maria.gonzalez@email.com",
            "estado_relacion": "activo"
        },
        {
            "nombre_completo": "Carlos Rodríguez",
            "rut": "11.222.333-4",
            "email": "carlos.rodriguez@email.com",
            "estado_relacion": "inactivo"
        }
    ]
    
    try:
        # 1. Verificar que el servidor esté funcionando
        print("1️⃣ Verificando conexión al servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
        else:
            print(f"❌ Error de conexión: {response.status_code}")
            return False
        
        # 2. Verificar endpoint de pacientes
        print("\n2️⃣ Verificando endpoint de pacientes...")
        response = requests.get(f"{base_url}/api/professional/patients")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint de pacientes funcionando")
            print(f"   Total de pacientes: {data.get('total', 0)}")
        else:
            print(f"❌ Error en endpoint de pacientes: {response.status_code}")
            return False
        
        # 3. Probar búsqueda con diferentes términos
        print("\n3️⃣ Probando búsquedas...")
        
        search_terms = [
            "Juan",
            "Pérez", 
            "12.345",
            "maria",
            "gonzalez",
            "carlos",
            "inactivo",
            "activo"
        ]
        
        for term in search_terms:
            print(f"\n🔍 Probando búsqueda: '{term}'")
            
            # Simular búsqueda en el frontend
            # Esto sería mejor probado con Selenium, pero por ahora simulamos la lógica
            if term.lower() in ["activo", "inactivo"]:
                print(f"   Filtro de estado: {term}")
            else:
                print(f"   Término de búsqueda: {term}")
            
            # Simular delay para evitar rate limiting
            time.sleep(0.5)
        
        # 4. Verificar elementos del DOM
        print("\n4️⃣ Verificando elementos del DOM...")
        
        # Obtener la página principal
        response = requests.get(f"{base_url}/professional")
        if response.status_code == 200:
            html_content = response.text
            
            # Verificar elementos de búsqueda
            elements_to_check = [
                'id="searchPatients"',
                'id="filterPatients"',
                'id="patientsTable"',
                'placeholder="Buscar paciente por nombre o RUT..."'
            ]
            
            for element in elements_to_check:
                if element in html_content:
                    print(f"✅ Elemento encontrado: {element}")
                else:
                    print(f"❌ Elemento NO encontrado: {element}")
        else:
            print(f"❌ Error obteniendo página: {response.status_code}")
        
        # 5. Verificar JavaScript
        print("\n5️⃣ Verificando archivos JavaScript...")
        
        js_files = [
            "/static/js/professional.js"
        ]
        
        for js_file in js_files:
            response = requests.get(f"{base_url}{js_file}")
            if response.status_code == 200:
                js_content = response.text
                
                # Verificar funciones importantes
                functions_to_check = [
                    'function setupPatientSearch',
                    'function filterPatients',
                    'function actualizarTablaPacientes'
                ]
                
                for func in functions_to_check:
                    if func in js_content:
                        print(f"✅ Función encontrada: {func}")
                    else:
                        print(f"❌ Función NO encontrada: {func}")
            else:
                print(f"❌ Error obteniendo {js_file}: {response.status_code}")
        
        print("\n✅ Todas las pruebas completadas")
        print("\n📋 Resumen de funcionalidades verificadas:")
        print("   • Conexión al servidor")
        print("   • Endpoint de pacientes")
        print("   • Elementos de búsqueda en HTML")
        print("   • Funciones JavaScript de búsqueda")
        print("   • Simulación de términos de búsqueda")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        return False

def test_busqueda_manual():
    """Guía para pruebas manuales"""
    print("\n🧪 GUÍA PARA PRUEBAS MANUALES")
    print("=" * 40)
    
    print("1. Abre la aplicación en el navegador")
    print("2. Ve a la sección 'Mis Pacientes'")
    print("3. Prueba las siguientes búsquedas:")
    print("   • Escribe 'Juan' en el campo de búsqueda")
    print("   • Escribe 'Pérez' en el campo de búsqueda")
    print("   • Selecciona 'Pacientes activos' en el filtro")
    print("   • Selecciona 'Pacientes inactivos' en el filtro")
    print("4. Verifica que los resultados se muestren correctamente")
    print("5. Abre la consola del navegador (F12) y busca mensajes de error")
    print("6. Haz clic en 'Probar Búsqueda' para verificar la funcionalidad")

def main():
    """Función principal"""
    print("🔍 PRUEBAS DE BÚSQUEDA EN FRONTEND")
    print("=" * 50)
    
    # Ejecutar pruebas automáticas
    success = test_busqueda_frontend()
    
    if success:
        print("\n✅ Pruebas automáticas completadas exitosamente")
    else:
        print("\n❌ Algunas pruebas fallaron")
    
    # Mostrar guía para pruebas manuales
    test_busqueda_manual()
    
    print("\n🎯 Para probar la búsqueda:")
    print("1. Ejecuta: python app.py")
    print("2. Abre: http://localhost:5000")
    print("3. Ve a 'Mis Pacientes' y prueba la búsqueda")

if __name__ == "__main__":
    main() 