#!/usr/bin/env python3
"""
Script final para verificar que el frontend funciona correctamente
"""

import requests
import json

def verificar_frontend_completo():
    """Verifica que el frontend esté funcionando correctamente"""
    print("🎯 VERIFICACIÓN FINAL DEL FRONTEND")
    print("=" * 50)
    
    # Realizar login con credenciales reales
    session = requests.Session()
    login_data = {
        'email': 'giselle.arratia@gmail.com',
        'password': 'Gigi2025',
        'tipo_usuario': 'profesional'
    }
    
    print("🔐 Iniciando sesión...")
    response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Error en login")
        return False
    
    print("✅ Login exitoso")
    
    # Verificar página professional
    print("\n🏗️ Verificando página professional...")
    professional_response = session.get("http://localhost:5000/professional")
    
    if professional_response.status_code == 200:
        html_content = professional_response.text
        
        # Verificar elementos críticos (solo HTML, no funciones JS)
        elementos_criticos = [
            'sugerenciasTratamiento',
            'listaSugerenciasTratamiento', 
            'sugerirTratamientoConIA'
        ]
        
        elementos_encontrados = []
        for elemento in elementos_criticos:
            if elemento in html_content:
                elementos_encontrados.append(elemento)
                print(f"✅ {elemento} presente")
            else:
                print(f"❌ {elemento} NO presente")
        
        print(f"\n📊 Elementos encontrados: {len(elementos_encontrados)}/{len(elementos_criticos)}")
        
        if len(elementos_encontrados) == len(elementos_criticos):
            print("✅ Todos los elementos HTML están presentes")
        else:
            print("❌ Faltan elementos HTML")
            return False
    else:
        print(f"❌ Error accediendo a página professional: {professional_response.status_code}")
        return False
    
    # Probar endpoint de términos
    print("\n🔍 Probando endpoint de términos...")
    try:
        terminos_response = session.post(
            "http://localhost:5000/api/copilot/generate-search-terms",
            json={
                'condicion': 'Dolor lumbar de 3 semanas',
                'especialidad': 'kinesiologia',
                'edad': 70
            },
            timeout=15
        )
        
        if terminos_response.status_code == 200:
            data = terminos_response.json()
            if data.get('success'):
                terminos = data.get('terminos_disponibles', {})
                recomendados = terminos.get('terminos_recomendados', [])
                print(f"✅ Endpoint funcionando: {len(recomendados)} términos recomendados")
                
                # Mostrar algunos términos
                print("📋 Términos disponibles:")
                for i, termino in enumerate(recomendados[:5], 1):
                    print(f"   {i}. {termino}")
                
                return True
            else:
                print(f"❌ Error en endpoint: {data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {terminos_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")
        return False

def mostrar_instrucciones_finales():
    """Muestra las instrucciones finales para el usuario"""
    print("\n🎉 ¡VERIFICACIÓN COMPLETADA!")
    print("=" * 40)
    print("✅ El backend está funcionando correctamente")
    print("✅ Los términos se generan exitosamente")
    print("✅ Los elementos HTML están presentes")
    
    print("\n💡 INSTRUCCIONES PARA PROBAR EN EL NAVEGADOR:")
    print("1. Abre http://localhost:5000 en tu navegador")
    print("2. Inicia sesión con:")
    print("   • Email: giselle.arratia@gmail.com")
    print("   • Password: Gigi2025")
    print("   • Tipo: profesional")
    print("3. Ve a la sección 'Registrar Atención'")
    print("4. Llena un diagnóstico (ej: 'Dolor lumbar de 3 semanas')")
    print("5. Haz clic en 'Sugerir Tratamiento con IA'")
    print("6. Deberías ver los términos de búsqueda categorizados:")
    print("   • ⭐ Términos Recomendados")
    print("   • 🏥 Términos de Especialidad")
    print("   • 👤 Términos por Edad")
    print("7. Selecciona los términos que consideres más relevantes")
    print("8. Haz clic en 'Realizar Búsqueda Personalizada'")
    print("9. Se mostrarán los tratamientos basados en tus selecciones")
    
    print("\n🔧 SI NO FUNCIONA:")
    print("• Abre la consola del navegador (F12)")
    print("• Revisa si hay errores en la consola")
    print("• Verifica que el servidor esté corriendo")
    print("• Asegúrate de estar autenticado correctamente")

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 50)
    
    resultado = verificar_frontend_completo()
    
    if resultado:
        mostrar_instrucciones_finales()
    else:
        print("\n❌ VERIFICACIÓN FALLÓ")
        print("❌ Revisa los errores anteriores")

if __name__ == "__main__":
    main() 