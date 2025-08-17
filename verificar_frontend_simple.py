#!/usr/bin/env python3
"""
Script simple para verificar elementos HTML del frontend
"""

import requests

def verificar_elementos_html():
    """Verifica que los elementos HTML necesarios estén presentes"""
    print("🔍 VERIFICACIÓN SIMPLE DE ELEMENTOS HTML")
    print("=" * 50)
    
    try:
        # Obtener la página professional
        response = requests.get("http://localhost:5000/professional", timeout=10)
        
        if response.status_code == 200:
            html_content = response.text
            print("✅ Página professional accesible")
            
            # Verificar elementos críticos
            elementos_criticos = [
                'id="sugerenciasTratamiento"',
                'id="listaSugerenciasTratamiento"',
                'sugerirTratamientoConIA()',
                'mostrarTerminosDisponibles',
                'realizarBusquedaPersonalizada'
            ]
            
            elementos_encontrados = []
            for elemento in elementos_criticos:
                if elemento in html_content:
                    elementos_encontrados.append(elemento)
                    print(f"✅ {elemento}")
                else:
                    print(f"❌ {elemento}")
            
            print(f"\n📊 Resultado: {len(elementos_encontrados)}/{len(elementos_criticos)} elementos encontrados")
            
            if len(elementos_encontrados) == len(elementos_criticos):
                print("✅ TODOS LOS ELEMENTOS HTML ESTÁN PRESENTES")
                print("\n💡 El frontend está configurado correctamente")
                print("💡 El problema puede ser de autenticación o JavaScript")
                return True
            else:
                print("❌ FALTAN ELEMENTOS HTML")
                print("❌ Revisa la implementación del frontend")
                return False
                
        elif response.status_code == 302:
            print("⚠️ Redirección detectada - Probablemente a login")
            print("💡 Esto es normal, la página requiere autenticación")
            return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def verificar_javascript():
    """Verifica que el archivo JavaScript esté disponible"""
    print("\n🖥️ VERIFICACIÓN DE JAVASCRIPT")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5000/static/js/professional.js", timeout=10)
        
        if response.status_code == 200:
            js_content = response.text
            print("✅ Archivo professional.js accesible")
            
            # Verificar funciones críticas
            funciones_criticas = [
                'mostrarTerminosDisponibles',
                'realizarBusquedaPersonalizada',
                'realizarBusquedaAutomatica',
                'obtenerTerminosSeleccionados',
                'seleccionarTodosTerminos',
                'deseleccionarTodosTerminos'
            ]
            
            funciones_encontradas = []
            for funcion in funciones_criticas:
                if funcion in js_content:
                    funciones_encontradas.append(funcion)
                    print(f"✅ {funcion}")
                else:
                    print(f"❌ {funcion}")
            
            print(f"\n📊 Resultado: {len(funciones_encontradas)}/{len(funciones_criticas)} funciones encontradas")
            
            if len(funciones_encontradas) == len(funciones_criticas):
                print("✅ TODAS LAS FUNCIONES JAVASCRIPT ESTÁN PRESENTES")
                return True
            else:
                print("❌ FALTAN FUNCIONES JAVASCRIPT")
                return False
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN SIMPLE DEL FRONTEND")
    print("=" * 50)
    
    # Verificar elementos HTML
    html_ok = verificar_elementos_html()
    
    # Verificar JavaScript
    js_ok = verificar_javascript()
    
    print("\n📊 RESUMEN")
    print("=" * 20)
    
    if html_ok and js_ok:
        print("✅ FRONTEND CONFIGURADO CORRECTAMENTE")
        print("\n💡 El problema puede ser:")
        print("   1. Autenticación requerida")
        print("   2. JavaScript no se ejecuta correctamente")
        print("   3. Endpoints del backend no funcionan")
        print("\n🔧 Para probar manualmente:")
        print("   1. Ve a http://localhost:5000")
        print("   2. Inicia sesión como profesional")
        print("   3. Ve a la sección de atención")
        print("   4. Llena un diagnóstico")
        print("   5. Haz clic en 'Sugerir Tratamiento con IA'")
    else:
        print("❌ PROBLEMAS EN EL FRONTEND")
        print("❌ Revisa la implementación")

if __name__ == "__main__":
    main() 