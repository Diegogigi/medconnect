#!/usr/bin/env python3
"""
Script para probar el login específico de Diego Castro
"""

import requests
import json


def test_diego_login():
    """Prueba el login específico de Diego Castro"""

    print("🔐 Probando login específico de Diego Castro...")
    print("=" * 60)

    # URL de login
    login_url = "https://www.medconnect.cl/login"

    # Credenciales de Diego Castro
    email = "diego.castro.lagos@gmail.com"
    password = "password123"

    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")

    try:
        # Crear sesión
        session = requests.Session()

        # 1. Obtener página de login
        print(f"\n📄 Obteniendo página de login...")
        response = session.get(login_url)

        if response.status_code != 200:
            print(f"❌ Error obteniendo página de login: {response.status_code}")
            return False

        print(f"✅ Página de login cargada correctamente")

        # 2. Intentar login
        print(f"🔐 Intentando login...")
        login_data = {"email": email, "password": password}

        login_response = session.post(login_url, data=login_data, allow_redirects=False)

        print(f"📊 Status del login: {login_response.status_code}")

        if login_response.status_code == 302:
            redirect_url = login_response.headers.get("Location", "")
            print(f"✅ Login exitoso - Redirigiendo a: {redirect_url}")

            # Verificar redirección
            if "/professional" in redirect_url:
                print(f"✅ Redirección correcta para profesional")
                return True
            else:
                print(f"⚠️ Redirección inesperada: {redirect_url}")
                return False

        elif login_response.status_code == 200:
            # Verificar si hay mensaje de error en el HTML
            if "Credenciales inválidas" in login_response.text:
                print(f"❌ Login fallido - Credenciales inválidas")
            elif "Error" in login_response.text:
                print(f"❌ Login fallido - Error en el sistema")
            else:
                print(f"⚠️ Login no procesado correctamente")
                print(f"📄 Respuesta: {login_response.text[:200]}...")
            return False
        else:
            print(f"❌ Error inesperado: {login_response.status_code}")
            print(f"📄 Respuesta: {login_response.text[:200]}...")
            return False

    except Exception as e:
        print(f"❌ Error probando login: {e}")
        return False


def test_giselle_login():
    """Prueba el login de Giselle Arratia"""

    print(f"\n🔐 Probando login de Giselle Arratia...")
    print("=" * 50)

    # URL de login
    login_url = "https://www.medconnect.cl/login"

    # Credenciales de Giselle Arratia
    email = "giselle.arratia@gmail.com"
    password = "password123"  # Probando con la misma contraseña

    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")

    try:
        # Crear sesión
        session = requests.Session()

        # 1. Obtener página de login
        print(f"\n📄 Obteniendo página de login...")
        response = session.get(login_url)

        if response.status_code != 200:
            print(f"❌ Error obteniendo página de login: {response.status_code}")
            return False

        print(f"✅ Página de login cargada correctamente")

        # 2. Intentar login
        print(f"🔐 Intentando login...")
        login_data = {"email": email, "password": password}

        login_response = session.post(login_url, data=login_data, allow_redirects=False)

        print(f"📊 Status del login: {login_response.status_code}")

        if login_response.status_code == 302:
            redirect_url = login_response.headers.get("Location", "")
            print(f"✅ Login exitoso - Redirigiendo a: {redirect_url}")
            return True
        elif login_response.status_code == 200:
            if "Credenciales inválidas" in login_response.text:
                print(f"❌ Login fallido - Credenciales inválidas")
            else:
                print(f"⚠️ Login no procesado correctamente")
            return False
        else:
            print(f"❌ Error inesperado: {login_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error probando login: {e}")
        return False


if __name__ == "__main__":
    print("🚀 PRUEBA LOGIN ESPECÍFICO")
    print("=" * 60)

    diego_success = test_diego_login()
    giselle_success = test_giselle_login()

    print(f"\n📋 RESUMEN:")
    print(f"  - Diego Castro: {'✅ Exitoso' if diego_success else '❌ Fallido'}")
    print(f"  - Giselle Arratia: {'✅ Exitoso' if giselle_success else '❌ Fallido'}")

    if diego_success and giselle_success:
        print(f"\n🎉 ¡Ambos logins funcionan!")
    elif diego_success:
        print(f"\n⚠️ Solo Diego Castro puede hacer login")
        print(f"🔧 Giselle Arratia necesita contraseña corregida")
    elif giselle_success:
        print(f"\n⚠️ Solo Giselle Arratia puede hacer login")
        print(f"🔧 Diego Castro necesita contraseña corregida")
    else:
        print(f"\n❌ Ningún login funciona")
        print(f"🔧 Revisa la configuración de la aplicación")
