#!/usr/bin/env python3
"""
Script para verificar el HTML directamente
"""

import requests

def verificar_html_directo():
    """Verifica el HTML directamente sin autenticación"""
    print("🔍 VERIFICACIÓN DIRECTA DEL HTML")
    print("=" * 50)
    
    try:
        # Obtener la página professional
        response = requests.get("http://localhost:5000/professional", timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Content-Type: {response.headers.get('Content-Type', 'No especificado')}")
        
        if response.status_code == 200:
            html_content = response.text
            print("✅ Página professional accesible")
            
            # Buscar elementos específicos
            elementos_buscar = [
                'sugerenciasTratamiento',
                'listaSugerenciasTratamiento',
                'sugerirTratamientoConIA',
                'mostrarTerminosDisponibles',
                'realizarBusquedaPersonalizada'
            ]
            
            for elemento in elementos_buscar:
                if elemento in html_content:
                    print(f"✅ '{elemento}' encontrado")
                else:
                    print(f"❌ '{elemento}' NO encontrado")
            
            # Buscar el contexto alrededor de los elementos
            print("\n🔍 CONTEXTO DE LOS ELEMENTOS:")
            
            # Buscar sugerenciasTratamiento
            if 'sugerenciasTratamiento' in html_content:
                start = html_content.find('sugerenciasTratamiento')
                context = html_content[max(0, start-50):start+100]
                print(f"Contexto sugerenciasTratamiento: {context}")
            
            # Buscar sugerirTratamientoConIA
            if 'sugerirTratamientoConIA' in html_content:
                start = html_content.find('sugerirTratamientoConIA')
                context = html_content[max(0, start-50):start+100]
                print(f"Contexto sugerirTratamientoConIA: {context}")
            
            # Verificar si es página de login
            if 'login' in html_content.lower() or 'iniciar sesión' in html_content.lower():
                print("\n⚠️ PÁGINA DE LOGIN DETECTADA")
                print("💡 La página está redirigiendo a login")
                print("💡 Esto es normal, se requiere autenticación")
                return False
            else:
                print("\n✅ NO ES PÁGINA DE LOGIN")
                return True
                
        elif response.status_code == 302:
            print("⚠️ Redirección detectada")
            print("💡 Probablemente a página de login")
            return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def verificar_estructura_html():
    """Verifica la estructura básica del HTML"""
    print("\n🏗️ VERIFICACIÓN DE ESTRUCTURA HTML")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:5000/professional", timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Verificar elementos básicos de estructura
            elementos_estructura = [
                '<html',
                '<head',
                '<body',
                '<title',
                'professional',
                'dashboard'
            ]
            
            for elemento in elementos_estructura:
                if elemento in html_content:
                    print(f"✅ {elemento}")
                else:
                    print(f"❌ {elemento}")
            
            # Verificar si hay contenido de la aplicación
            if 'MedConnect' in html_content:
                print("✅ Contenido de MedConnect detectado")
            else:
                print("❌ Contenido de MedConnect NO detectado")
            
            # Verificar si hay formularios
            if '<form' in html_content:
                print("✅ Formularios detectados")
            else:
                print("❌ Formularios NO detectados")
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN COMPLETA DEL HTML")
    print("=" * 50)
    
    # Verificar HTML directo
    html_ok = verificar_html_directo()
    
    # Verificar estructura
    verificar_estructura_html()
    
    print("\n📊 RESUMEN")
    print("=" * 20)
    
    if html_ok:
        print("✅ HTML ACCESIBLE Y ELEMENTOS PRESENTES")
        print("💡 El problema puede ser:")
        print("   1. JavaScript no se ejecuta")
        print("   2. Endpoints del backend no funcionan")
        print("   3. Autenticación requerida")
    else:
        print("❌ PROBLEMAS CON EL HTML")
        print("❌ La página puede estar redirigiendo a login")

if __name__ == "__main__":
    main() 