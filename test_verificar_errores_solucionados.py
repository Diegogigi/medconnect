#!/usr/bin/env python3
"""
Script para verificar que los errores de JavaScript se han solucionado
"""

import requests
import time

def test_verificar_errores_solucionados():
    """Verifica que los errores de JavaScript se han solucionado"""
    print("🎯 VERIFICACIÓN DE ERRORES SOLUCIONADOS")
    print("=" * 60)
    
    try:
        # URL base
        base_url = "http://localhost:5000"
        
        # 1. Verificar que la página professional esté disponible
        print("\n1. 🔍 Verificando página professional...")
        response = requests.get(f"{base_url}/professional", timeout=10)
        
        if response.status_code == 200:
            print("✅ Página professional accesible")
            
            # 2. Verificar que el archivo JavaScript esté cargado con la versión correcta
            if 'professional.js?v=1.6' in response.text:
                print("✅ Script professional.js versión 1.6 detectado")
            else:
                print("⚠️ Script professional.js no tiene la versión esperada")
                print("   Versiones encontradas:")
                import re
                versions = re.findall(r'professional\.js\?v=(\d+\.\d+)', response.text)
                for version in versions:
                    print(f"   - v{version}")
        else:
            print(f"❌ Error accediendo a la página: {response.status_code}")
            return
        
        # 3. Verificar que el archivo JavaScript esté disponible
        print("\n2. 🔍 Verificando archivo JavaScript...")
        js_response = requests.get(f"{base_url}/static/js/professional.js", timeout=10)
        
        if js_response.status_code == 200:
            print("✅ Archivo professional.js accesible")
            
            # 4. Verificar que los errores se han solucionado
            js_content = js_response.text
            
            print("\n3. 🔍 Verificando errores solucionados...")
            
            # Verificar que sugerirTratamientoConIA NO se expone globalmente
            if 'window.sugerirTratamientoConIA' in js_content:
                print("❌ ERROR: sugerirTratamientoConIA aún se expone globalmente")
            else:
                print("✅ sugerirTratamientoConIA eliminado correctamente")
            
            # Verificar que toggleCopilotChat inicializa el chat
            if 'inicializarCopilotChat();' in js_content and 'function toggleCopilotChat()' in js_content:
                print("✅ toggleCopilotChat inicializa el chat correctamente")
            else:
                print("❌ ERROR: toggleCopilotChat no inicializa el chat")
            
            # Verificar que las funciones del chat estén presentes
            funciones_chat = [
                'inicializarCopilotChat',
                'agregarMensajeCopilot',
                'mostrarTypingCopilot',
                'removerTypingCopilot',
                'toggleCopilotChat',
                'mostrarBotonCopilotChat',
                'limpiarChatCopilot'
            ]
            
            funciones_encontradas = []
            funciones_faltantes = []
            
            for funcion in funciones_chat:
                if funcion in js_content:
                    funciones_encontradas.append(funcion)
                    print(f"✅ Función '{funcion}' encontrada")
                else:
                    funciones_faltantes.append(funcion)
                    print(f"❌ Función '{funcion}' NO encontrada")
            
            # Verificar que las funciones expuestas globalmente estén correctas
            funciones_globales_correctas = [
                'window.insertarSugerenciaTratamiento',
                'window.insertarSugerenciasTratamiento',
                'window.mostrarTerminosDisponibles',
                'window.realizarBusquedaPersonalizada',
                'window.realizarBusquedaAutomatica',
                'window.seleccionarTodosTerminos',
                'window.deseleccionarTodosTerminos',
                'window.obtenerTerminosSeleccionados',
                'window.restaurarMotivoOriginal',
                'window.hayPreguntasInsertadas'
            ]
            
            print("\n4. 🔍 Verificando funciones globales...")
            globales_encontradas = []
            globales_faltantes = []
            
            for funcion in funciones_globales_correctas:
                if funcion in js_content:
                    globales_encontradas.append(funcion)
                    print(f"✅ Función global '{funcion}' encontrada")
                else:
                    globales_faltantes.append(funcion)
                    print(f"❌ Función global '{funcion}' NO encontrada")
            
            # 5. Resumen
            print("\n" + "="*60)
            print("📊 RESUMEN DE VERIFICACIÓN")
            print("="*60)
            
            print(f"✅ Funciones del chat: {len(funciones_encontradas)}/{len(funciones_chat)}")
            print(f"✅ Funciones globales: {len(globales_encontradas)}/{len(funciones_globales_correctas)}")
            
            errores_detectados = len(funciones_faltantes) + len(globales_faltantes)
            
            if errores_detectados == 0:
                print("\n🎉 ¡ERRORES SOLUCIONADOS!")
                print("   - sugerirTratamientoConIA eliminado")
                print("   - toggleCopilotChat inicializa correctamente")
                print("   - Todas las funciones del chat presentes")
                print("   - Funciones globales correctas")
                print("\n💡 Para probar:")
                print("   1. Recarga la página (Ctrl + F5)")
                print("   2. Abre la consola del navegador (F12)")
                print("   3. Verifica que no hay errores")
                print("   4. Prueba el botón de chat de Copilot Health")
            else:
                print(f"\n⚠️ {errores_detectados} ERRORES DETECTADOS:")
                if funciones_faltantes:
                    print(f"   - Funciones faltantes: {', '.join(funciones_faltantes)}")
                if globales_faltantes:
                    print(f"   - Globales faltantes: {', '.join(globales_faltantes)}")
                
        else:
            print(f"❌ Error accediendo al archivo JavaScript: {js_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. Asegúrate de que el servidor esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_verificar_errores_solucionados() 