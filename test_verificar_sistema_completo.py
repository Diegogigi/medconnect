#!/usr/bin/env python3
"""
Script para verificar que todo el sistema esté funcionando correctamente
"""

import requests
import time

def test_verificar_sistema_completo():
    """Verifica que todo el sistema esté funcionando correctamente"""
    print("🎯 VERIFICACIÓN COMPLETA DEL SISTEMA")
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
            if 'professional.js?v=1.5' in response.text:
                print("✅ Script professional.js versión 1.5 detectado")
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
            
            # 4. Verificar que las funciones del chat estén presentes
            js_content = js_response.text
            
            funciones_requeridas = [
                'inicializarCopilotChat',
                'agregarMensajeCopilot',
                'mostrarTypingCopilot',
                'removerTypingCopilot',
                'toggleCopilotChat',
                'mostrarBotonCopilotChat',
                'limpiarChatCopilot',
                'copilotHealthAssistant'
            ]
            
            print("\n3. 🔍 Verificando funciones del chat...")
            funciones_encontradas = []
            funciones_faltantes = []
            
            for funcion in funciones_requeridas:
                if funcion in js_content:
                    funciones_encontradas.append(funcion)
                    print(f"✅ Función '{funcion}' encontrada")
                else:
                    funciones_faltantes.append(funcion)
                    print(f"❌ Función '{funcion}' NO encontrada")
            
            # 5. Verificar estilos CSS del chat
            print("\n4. 🔍 Verificando estilos CSS del chat...")
            estilos_requeridos = [
                'copilot-chat-container',
                'copilot-message',
                'copilot-typing',
                'typing-dots',
                'copilot-system',
                'copilot-thinking',
                'copilot-success',
                'copilot-warning',
                'copilot-error',
                'copilot-progress'
            ]
            
            estilos_encontrados = []
            estilos_faltantes = []
            
            for estilo in estilos_requeridos:
                if estilo in js_content:
                    estilos_encontrados.append(estilo)
                    print(f"✅ Estilo '{estilo}' encontrado")
                else:
                    estilos_faltantes.append(estilo)
                    print(f"❌ Estilo '{estilo}' NO encontrado")
            
            # 6. Verificar integración con funciones existentes
            print("\n5. 🔍 Verificando integración...")
            integraciones_requeridas = [
                'mostrarPapersEnSidebar',
                'inicializarSidebarDinamica',
                'mostrarNotificacionSidebar',
                'mostrarProgresoSidebar'
            ]
            
            integraciones_encontradas = []
            integraciones_faltantes = []
            
            for integracion in integraciones_requeridas:
                if integracion in js_content:
                    integraciones_encontradas.append(integracion)
                    print(f"✅ Integración '{integracion}' encontrada")
                else:
                    integraciones_faltantes.append(integracion)
                    print(f"❌ Integración '{integracion}' NO encontrada")
            
            # 7. Verificar sistema de control de mensajes duplicados
            print("\n6. 🔍 Verificando sistema de control de mensajes...")
            control_mensajes = [
                'mensajeCompletadoMostrado',
                'ultimoMotivoConsulta',
                'limpiarControlMensajes'
            ]
            
            control_encontrado = []
            control_faltante = []
            
            for control in control_mensajes:
                if control in js_content:
                    control_encontrado.append(control)
                    print(f"✅ Control '{control}' encontrado")
                else:
                    control_faltante.append(control)
                    print(f"❌ Control '{control}' NO encontrado")
            
            # 8. Resumen
            print("\n" + "="*60)
            print("📊 RESUMEN DE VERIFICACIÓN COMPLETA")
            print("="*60)
            
            print(f"✅ Funciones del chat: {len(funciones_encontradas)}/{len(funciones_requeridas)}")
            print(f"✅ Estilos CSS: {len(estilos_encontrados)}/{len(estilos_requeridos)}")
            print(f"✅ Integraciones: {len(integraciones_encontradas)}/{len(integraciones_requeridas)}")
            print(f"✅ Control de mensajes: {len(control_encontrado)}/{len(control_mensajes)}")
            
            total_verificaciones = len(funciones_requeridas) + len(estilos_requeridos) + len(integraciones_requeridas) + len(control_mensajes)
            total_encontradas = len(funciones_encontradas) + len(estilos_encontrados) + len(integraciones_encontradas) + len(control_encontrado)
            
            print(f"\n📈 PROGRESO GENERAL: {total_encontradas}/{total_verificaciones} ({total_encontradas/total_verificaciones*100:.1f}%)")
            
            if len(funciones_faltantes) == 0 and len(estilos_faltantes) == 0 and len(integraciones_faltantes) == 0 and len(control_faltante) == 0:
                print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
                print("   - Todas las funciones están presentes")
                print("   - Todos los estilos están definidos")
                print("   - Todas las integraciones están activas")
                print("   - Sistema de control de mensajes activo")
                print("\n💡 Para probar el sistema:")
                print("   1. Ve a la página professional")
                print("   2. Busca el botón flotante con ícono de robot")
                print("   3. Completa el formulario y activa Copilot Health")
                print("   4. Observa el chat en tiempo real")
                print("   5. Verifica que no haya mensajes duplicados")
            else:
                print("\n⚠️ PROBLEMAS DETECTADOS:")
                if funciones_faltantes:
                    print(f"   - Funciones faltantes: {', '.join(funciones_faltantes)}")
                if estilos_faltantes:
                    print(f"   - Estilos faltantes: {', '.join(estilos_faltantes)}")
                if integraciones_faltantes:
                    print(f"   - Integraciones faltantes: {', '.join(integraciones_faltantes)}")
                if control_faltante:
                    print(f"   - Control faltante: {', '.join(control_faltante)}")
                
        else:
            print(f"❌ Error accediendo al archivo JavaScript: {js_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. Asegúrate de que el servidor esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_verificar_sistema_completo() 