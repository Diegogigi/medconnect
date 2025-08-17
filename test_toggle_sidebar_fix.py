#!/usr/bin/env python3
"""
Script para probar el fix de toggleSidebar
"""

import requests
import json
import time


def test_toggle_sidebar_fix():
    """Prueba que el fix de toggleSidebar funcione correctamente"""

    print("🔧 PROBANDO FIX DE TOGGLESIDEBAR")
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

            # Verificar que el script de fix esté incluido
            if "fix-toggle-sidebar.js" in response.text:
                print("✅ Script de fix de toggleSidebar incluido")
            else:
                print("❌ Script de fix de toggleSidebar NO encontrado")

            # Verificar que el botón de toggle esté presente
            if 'onclick="toggleSidebar()"' in response.text:
                print("✅ Botón toggleSidebar encontrado")
            else:
                print("❌ Botón toggleSidebar NO encontrado")

        else:
            print("❌ Error cargando página del profesional")
            return

        print("\n" + "=" * 50)
        print("✅ PRUEBA DE FIX COMPLETADA")
        print("\n📋 Instrucciones para verificar:")
        print("   1. Abre las herramientas de desarrollador (F12)")
        print("   2. Ve a la pestaña 'Console'")
        print("   3. Haz clic en el botón de toggle de la sidebar")
        print("   4. Verifica que NO aparezcan errores de JavaScript")
        print("   5. Busca estos mensajes en la consola:")
        print("      ✅ '🔧 toggleSidebar ejecutándose...'")
        print("      ✅ '✅ Todos los elementos encontrados'")
        print("      ✅ '✅ Sidebar visible' o '✅ Sidebar oculta'")

    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor Flask esté ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def check_console_messages():
    """Instrucciones para verificar mensajes en la consola"""

    print("\n🔍 VERIFICACIÓN EN LA CONSOLA")
    print("=" * 40)
    print("1. Abre las herramientas de desarrollador (F12)")
    print("2. Ve a la pestaña 'Console'")
    print("3. Busca estos mensajes de inicialización:")
    print("   ✅ '✅ toggleSidebar corregido cargado'")
    print("   ✅ '🚀 Inicializando sidebar de manera segura...'")
    print("   ✅ '🔍 Verificando elementos de sidebar:'")
    print("4. Haz clic en el botón de toggle de la sidebar")
    print("5. Verifica que aparezcan estos mensajes:")
    print("   ✅ '🔧 toggleSidebar ejecutándose...'")
    print("   ✅ '✅ Todos los elementos encontrados'")
    print("6. NO debe haber errores de 'Cannot read properties of null'")


def troubleshoot_common_issues():
    """Solución de problemas comunes"""

    print("\n🔧 SOLUCIÓN DE PROBLEMAS")
    print("=" * 40)
    print("Si aún hay errores:")
    print("1. Verifica que el script se cargue correctamente")
    print("2. Asegúrate de que no haya conflictos con otros scripts")
    print("3. Limpia el caché del navegador (Ctrl + Shift + Delete)")
    print("4. Recarga la página (Ctrl + F5)")
    print("5. Verifica que todos los elementos HTML existan:")
    print("   - sidebarContainer")
    print("   - sidebarToggleIcon")
    print("   - sidebarToggle")
    print("   - .col-lg-8.col-xl-9")


if __name__ == "__main__":
    test_toggle_sidebar_fix()
    check_console_messages()
    troubleshoot_common_issues()
