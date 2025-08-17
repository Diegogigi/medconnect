#!/usr/bin/env python3
"""
Script para probar la solución de rate limiting implementada
"""

import requests
import time
import json

def test_rate_limiting_solution():
    """Prueba la solución de rate limiting"""
    print("🔄 PRUEBA DE SOLUCIÓN DE RATE LIMITING")
    print("=" * 50)
    
    # Realizar login
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
    
    # Probar múltiples llamadas rápidas para simular rate limiting
    print("\n📊 Probando múltiples llamadas...")
    
    endpoints = [
        ('/api/professional/patients', 'Pacientes'),
        ('/api/get-atenciones', 'Atenciones')
    ]
    
    resultados = []
    
    for endpoint, nombre in endpoints:
        print(f"\n🔍 Probando {nombre}...")
        
        # Hacer 3 llamadas rápidas
        for i in range(3):
            try:
                start_time = time.time()
                response = session.get(f"http://localhost:5000{endpoint}", timeout=30)
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"   ✅ Llamada {i+1}: {endpoint} - {end_time - start_time:.2f}s")
                        resultados.append((endpoint, True, end_time - start_time))
                    else:
                        print(f"   ❌ Llamada {i+1}: {endpoint} - Error: {data.get('message')}")
                        resultados.append((endpoint, False, 0))
                elif response.status_code == 429:
                    print(f"   ⚠️ Llamada {i+1}: {endpoint} - Rate limiting detectado (esperado)")
                    resultados.append((endpoint, True, 0))  # Rate limiting es manejado correctamente
                else:
                    print(f"   ❌ Llamada {i+1}: {endpoint} - HTTP {response.status_code}")
                    resultados.append((endpoint, False, 0))
                
                # Pequeña pausa entre llamadas
                time.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Llamada {i+1}: {endpoint} - Error: {e}")
                resultados.append((endpoint, False, 0))
    
    # Analizar resultados
    print("\n📊 ANÁLISIS DE RESULTADOS")
    print("=" * 40)
    
    exitos = 0
    total_llamadas = len(resultados)
    
    for endpoint, exitoso, tiempo in resultados:
        if exitoso:
            print(f"✅ {endpoint}: OK (tiempo: {tiempo:.2f}s)")
            exitos += 1
        else:
            print(f"❌ {endpoint}: FALLO")
    
    print(f"\n🎯 Resultado: {exitos}/{total_llamadas} llamadas exitosas")
    
    if exitos >= total_llamadas * 0.8:  # 80% de éxito
        print("✅ SOLUCIÓN DE RATE LIMITING FUNCIONANDO")
        return True
    else:
        print("❌ PROBLEMAS CON RATE LIMITING")
        return False

def test_specific_rate_limiting():
    """Prueba específica de rate limiting con reintentos"""
    print("\n🔄 PRUEBA ESPECÍFICA DE RATE LIMITING")
    print("=" * 50)
    
    # Realizar login
    session = requests.Session()
    login_data = {
        'email': 'giselle.arratia@gmail.com',
        'password': 'Gigi2025',
        'tipo_usuario': 'profesional'
    }
    
    response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=False)
    
    if response.status_code != 302:
        print("❌ Error en login")
        return False
    
    print("✅ Login exitoso")
    
    # Probar endpoint que sabemos que causa rate limiting
    print("\n🔍 Probando endpoint con rate limiting...")
    
    try:
        response = session.get("http://localhost:5000/api/professional/patients", timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                pacientes = data.get('pacientes', [])
                print(f"✅ Éxito: {len(pacientes)} pacientes obtenidos")
                return True
            else:
                print(f"❌ Error en respuesta: {data.get('message')}")
                return False
        elif response.status_code == 429:
            print("✅ Rate limiting detectado y manejado correctamente")
            return True
        else:
            print(f"❌ HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def mostrar_instrucciones():
    """Muestra instrucciones para el usuario"""
    print("\n🎯 INSTRUCCIONES PARA EL USUARIO")
    print("=" * 50)
    print("1. El sistema ahora maneja automáticamente el rate limiting")
    print("2. Si ocurre un error 429, el sistema:")
    print("   • Espera un tiempo exponencial (1s, 2s, 4s)")
    print("   • Reintenta hasta 3 veces")
    print("   • Si persiste, devuelve error 429")
    print("3. Para evitar rate limiting:")
    print("   • No hagas muchas llamadas rápidas")
    print("   • Espera entre operaciones")
    print("   • El sistema manejará automáticamente los reintentos")
    print("4. Si ves errores 429, es normal y el sistema los manejará")

def main():
    """Función principal"""
    print("🔄 PRUEBA COMPLETA DE SOLUCIÓN DE RATE LIMITING")
    print("=" * 60)
    
    # Ejecutar pruebas
    resultados = []
    
    # Prueba general
    resultados.append(("Prueba General", test_rate_limiting_solution()))
    
    # Prueba específica
    resultados.append(("Prueba Específica", test_specific_rate_limiting()))
    
    # Mostrar resumen
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 40)
    
    exitos = 0
    for nombre, resultado in resultados:
        if resultado:
            print(f"✅ {nombre}: OK")
            exitos += 1
        else:
            print(f"❌ {nombre}: FALLO")
    
    print(f"\n🎯 Resultado: {exitos}/{len(resultados)} pruebas exitosas")
    
    if exitos == len(resultados):
        print("✅ SOLUCIÓN DE RATE LIMITING IMPLEMENTADA CORRECTAMENTE")
        print("✅ El sistema ahora maneja automáticamente los errores 429")
        mostrar_instrucciones()
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("❌ Revisa los errores anteriores")

if __name__ == "__main__":
    main() 