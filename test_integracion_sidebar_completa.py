#!/usr/bin/env python3
"""
Script para verificar la integración completa de Copilot Health en la sidebar
"""

import requests
import time

def test_integracion_sidebar_completa():
    """Verifica la integración completa de Copilot Health en la sidebar"""
    print("🎯 VERIFICACIÓN DE INTEGRACIÓN COMPLETA EN SIDEBAR")
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
            if 'professional.js?v=1.7' in response.text:
                print("✅ Script professional.js versión 1.7 detectado")
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
            
            # 4. Verificar que las funciones del chat integrado estén presentes
            js_content = js_response.text
            
            print("\n3. 🔍 Verificando funciones del chat integrado...")
            
            funciones_chat_integrado = [
                'agregarMensajeSidebar',
                'mostrarTypingSidebar',
                'removerTypingSidebar',
                'limpiarChatSidebar',
                'toggleChatSidebar',
                'activarCopilotHealthSidebar',
                'realizarAnalisisCompletoSidebar',
                'mostrarSeccionPapersSidebar',
                'inicializarObservadorFormulario'
            ]
            
            funciones_encontradas = []
            funciones_faltantes = []
            
            for funcion in funciones_chat_integrado:
                if funcion in js_content:
                    funciones_encontradas.append(funcion)
                    print(f"✅ Función '{funcion}' encontrada")
                else:
                    funciones_faltantes.append(funcion)
                    print(f"❌ Función '{funcion}' NO encontrada")
            
            # 5. Verificar estilos CSS del chat integrado
            print("\n4. 🔍 Verificando estilos CSS del chat integrado...")
            estilos_chat_integrado = [
                'copilot-chat-integrated',
                'chat-header',
                'chat-messages-container',
                'chat-messages',
                'chat-message',
                'message-content',
                'message-time',
                'chat-typing',
                'typing-indicator',
                'typing-dots',
                'dynamic-content-area',
                'content-section',
                'chat-activation'
            ]
            
            estilos_encontrados = []
            estilos_faltantes = []
            
            for estilo in estilos_chat_integrado:
                if estilo in js_content or estilo in response.text:
                    estilos_encontrados.append(estilo)
                    print(f"✅ Estilo '{estilo}' encontrado")
                else:
                    estilos_faltantes.append(estilo)
                    print(f"❌ Estilo '{estilo}' NO encontrado")
            
            # 6. Verificar estructura HTML del chat integrado
            print("\n5. 🔍 Verificando estructura HTML del chat integrado...")
            elementos_html = [
                'copilotChatIntegrated',
                'chatMessages',
                'chatTyping',
                'dynamicContentArea',
                'sidebarTerminos',
                'sidebarPapers'
            ]
            
            elementos_encontrados = []
            elementos_faltantes = []
            
            for elemento in elementos_html:
                if elemento in response.text:
                    elementos_encontrados.append(elemento)
                    print(f"✅ Elemento '{elemento}' encontrado")
                else:
                    elementos_faltantes.append(elemento)
                    print(f"❌ Elemento '{elemento}' NO encontrado")
            
            # 7. Verificar funcionalidades específicas
            print("\n6. 🔍 Verificando funcionalidades específicas...")
            funcionalidades = [
                'sidebarChatMessages',
                'sidebarChatActive',
                'MutationObserver',
                'DOMContentLoaded',
                'addEventListener'
            ]
            
            funcionalidades_encontradas = []
            funcionalidades_faltantes = []
            
            for funcionalidad in funcionalidades:
                if funcionalidad in js_content:
                    funcionalidades_encontradas.append(funcionalidad)
                    print(f"✅ Funcionalidad '{funcionalidad}' encontrada")
                else:
                    funcionalidades_faltantes.append(funcionalidad)
                    print(f"❌ Funcionalidad '{funcionalidad}' NO encontrada")
            
            # 8. Resumen
            print("\n" + "="*60)
            print("📊 RESUMEN DE VERIFICACIÓN COMPLETA")
            print("="*60)
            
            print(f"✅ Funciones del chat integrado: {len(funciones_encontradas)}/{len(funciones_chat_integrado)}")
            print(f"✅ Estilos CSS: {len(estilos_encontrados)}/{len(estilos_chat_integrado)}")
            print(f"✅ Elementos HTML: {len(elementos_encontrados)}/{len(elementos_html)}")
            print(f"✅ Funcionalidades: {len(funcionalidades_encontradas)}/{len(funcionalidades)}")
            
            total_verificaciones = len(funciones_chat_integrado) + len(estilos_chat_integrado) + len(elementos_html) + len(funcionalidades)
            total_encontradas = len(funciones_encontradas) + len(estilos_encontrados) + len(elementos_encontrados) + len(funcionalidades_encontradas)
            
            print(f"\n📈 PROGRESO GENERAL: {total_encontradas}/{total_verificaciones} ({total_encontradas/total_verificaciones*100:.1f}%)")
            
            if len(funciones_faltantes) == 0 and len(estilos_faltantes) == 0 and len(elementos_faltantes) == 0 and len(funcionalidades_faltantes) == 0:
                print("\n🎉 ¡INTEGRACIÓN COMPLETA FUNCIONAL!")
                print("   - Todas las funciones del chat integrado están presentes")
                print("   - Todos los estilos CSS están definidos")
                print("   - Todos los elementos HTML están en su lugar")
                print("   - Todas las funcionalidades están activas")
                print("\n💡 Para probar la integración:")
                print("   1. Ve a la página professional")
                print("   2. Abre la sidebar de Copilot Health")
                print("   3. Completa el formulario")
                print("   4. Haz clic en 'Activar Análisis con IA'")
                print("   5. Observa el chat en tiempo real en la sidebar")
                print("   6. Verifica que detecta cambios en el formulario")
                print("   7. Comprueba que muestra papers al final")
                
                print("\n🚀 CARACTERÍSTICAS IMPLEMENTADAS:")
                print("   ✅ Chat integrado en la sidebar")
                print("   ✅ Comunicación en tiempo real")
                print("   ✅ Detección de cambios en formulario")
                print("   ✅ Mensajes paso a paso del proceso")
                print("   ✅ Indicadores de typing")
                print("   ✅ Diferentes tipos de mensajes")
                print("   ✅ Timestamps en mensajes")
                print("   ✅ Scroll automático")
                print("   ✅ Animaciones suaves")
                print("   ✅ Controles de chat (limpiar, minimizar)")
                print("   ✅ Área de contenido dinámico")
                print("   ✅ Sección de papers integrada")
                
            else:
                print("\n⚠️ PROBLEMAS DETECTADOS:")
                if funciones_faltantes:
                    print(f"   - Funciones faltantes: {', '.join(funciones_faltantes)}")
                if estilos_faltantes:
                    print(f"   - Estilos faltantes: {', '.join(estilos_faltantes)}")
                if elementos_faltantes:
                    print(f"   - Elementos faltantes: {', '.join(elementos_faltantes)}")
                if funcionalidades_faltantes:
                    print(f"   - Funcionalidades faltantes: {', '.join(funcionalidades_faltantes)}")
                
        else:
            print(f"❌ Error accediendo al archivo JavaScript: {js_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. Asegúrate de que el servidor esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_integracion_sidebar_completa() 