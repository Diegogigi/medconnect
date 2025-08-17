#!/usr/bin/env python3
"""
Script para verificar que el chat en la sidebar esté funcionando
"""

import requests
import json
import time


def test_chat_sidebar():
    """Prueba que el chat en la sidebar esté funcionando"""

    print("💬 VERIFICANDO CHAT EN LA SIDEBAR")
    print("=" * 50)

    # URL base
    base_url = "http://localhost:5000"

    try:
        # 1. Verificar que el servidor esté funcionando
        print("1. Verificando servidor...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Servidor funcionando")
        else:
            print("❌ Servidor no responde")
            return

        # 2. Verificar que la página del profesional cargue
        print("2. Verificando página del profesional...")
        response = requests.get(f"{base_url}/professional")
        if response.status_code == 200:
            print("✅ Página del profesional cargada")

            # Verificar que el script de chat esté incluido
            if "restore-chat-sidebar.js" in response.text:
                print("✅ Script de restauración de chat incluido")
            else:
                print("❌ Script de restauración de chat NO encontrado")

            # Verificar que el CSS del chat esté incluido
            if "chat-sidebar.css" in response.text:
                print("✅ CSS del chat incluido")
            else:
                print("❌ CSS del chat NO encontrado")

        else:
            print("❌ Error cargando página del profesional")
            return

        print("\n" + "=" * 50)
        print("✅ VERIFICACIÓN DE ARCHIVOS COMPLETADA")
        print("\n📋 Instrucciones para verificar el chat:")
        print("   1. Abre las herramientas de desarrollador (F12)")
        print("   2. Ve a la pestaña 'Console'")
        print("   3. Recarga la página (Ctrl + F5)")
        print("   4. Verifica que aparezcan estos mensajes:")
        print("      ✅ '💬 Restaurando chat en la sidebar...'")
        print("      ✅ '🔧 Creando chat en la sidebar...'")
        print("      ✅ '✅ Chat creado en la sidebar'")
        print("      ✅ '🔗 Integrando chat con sistema IA...'")
        print("   5. Verifica que el chat aparezca en la sidebar")

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor Flask esté ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def check_chat_functionality():
    """Verificar funcionalidad del chat"""

    print("\n🔍 VERIFICACIÓN DE FUNCIONALIDAD DEL CHAT")
    print("=" * 50)
    print("1. Verificar que el chat esté visible:")
    print("   - Debe aparecer en la sidebar")
    print("   - Debe tener un header con 'Chat IA'")
    print("   - Debe tener un área de mensajes")
    print("   - Debe tener un input para escribir")

    print("\n2. Verificar mensaje de bienvenida:")
    print("   - Debe mostrar '¡Hola! Soy tu asistente de IA'")
    print("   - Debe tener timestamp 'Ahora'")

    print("\n3. Verificar funcionalidad de envío:")
    print("   - Escribe un mensaje en el input")
    print("   - Presiona Enter o haz clic en el botón")
    print("   - Verifica que el mensaje aparezca en el chat")

    print("\n4. Verificar integración con IA:")
    print("   - Escribe 'busca papers de dolor de hombro'")
    print("   - Verifica que se procese la consulta")
    print("   - Verifica que aparezca respuesta del sistema")


def provide_troubleshooting_steps():
    """Proporcionar pasos de solución de problemas"""

    print("\n🔧 PASOS DE SOLUCIÓN DE PROBLEMAS")
    print("=" * 50)
    print("Si el chat no aparece:")
    print("1. Verifica que el script se cargue:")
    print("   - Busca 'restore-chat-sidebar.js' en la consola")
    print("   - Verifica que no haya errores de JavaScript")

    print("\n2. Ejecuta manualmente en la consola:")
    print("   verificarYRestaurarChat()")
    print("   crearChatEnSidebar()")

    print("\n3. Verifica que sidebarContainer exista:")
    print("   document.getElementById('sidebarContainer')")

    print("\n4. Si el chat aparece pero no funciona:")
    print("   - Verifica que las funciones estén definidas")
    print("   - Ejecuta: enviarMensajeChat('test')")
    print("   - Verifica que agregarMensajeChat esté disponible")


def check_console_output():
    """Instrucciones para verificar la salida de la consola"""

    print("\n📊 VERIFICACIÓN EN LA CONSOLA")
    print("=" * 40)
    print("1. Abre las herramientas de desarrollador (F12)")
    print("2. Ve a la pestaña 'Console'")
    print("3. Busca estos mensajes de inicialización:")
    print("   ✅ '💬 Restaurando chat en la sidebar...'")
    print("   ✅ '🔧 Creando chat en la sidebar...'")
    print("   ✅ '✅ Chat creado en la sidebar'")
    print("   ✅ '🔗 Integrando chat con sistema IA...'")
    print("4. Verifica que NO haya errores de:")
    print("   ❌ 'sidebarContainer no encontrado'")
    print("   ❌ 'panel-content no encontrado'")
    print("   ❌ 'chatMessages no encontrado'")
    print("5. Ejecuta: verificarYRestaurarChat()")
    print("6. El chat debe estar visible en la sidebar")


if __name__ == "__main__":
    test_chat_sidebar()
    check_chat_functionality()
    provide_troubleshooting_steps()
    check_console_output()
