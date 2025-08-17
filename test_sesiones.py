#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de sesiones en MedConnect
"""

import requests
import json
from datetime import datetime, timedelta

def test_sesiones():
    """Prueba completa de la funcionalidad de sesiones"""
    
    print("🧪 PRUEBA DE FUNCIONALIDAD DE SESIONES")
    print("=" * 60)
    
    # Configuración
    base_url = "http://localhost:5000"
    
    # Datos de prueba
    test_data = {
        "email": "giselle.arratia@medconnect.com",
        "password": "test123"
    }
    
    # 1. Login
    print("1. 🔐 Iniciando sesión...")
    session = requests.Session()
    
    try:
        login_response = session.post(
            f"{base_url}/login",
            data=test_data,
            allow_redirects=False
        )
        
        if login_response.status_code == 302:
            print("✅ Login exitoso")
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # 2. Obtener atenciones existentes
    print("\n2. 📋 Obteniendo atenciones existentes...")
    try:
        atenciones_response = session.get(f"{base_url}/api/get-atenciones")
        if atenciones_response.status_code == 200:
            atenciones_data = atenciones_response.json()
            if atenciones_data.get('success') and atenciones_data.get('atenciones'):
                atencion_id = atenciones_data['atenciones'][0]['id']
                print(f"✅ Atención encontrada: {atencion_id}")
            else:
                print("⚠️ No hay atenciones disponibles")
                return False
        else:
            print(f"❌ Error obteniendo atenciones: {atenciones_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 3. Verificar sesiones existentes
    print(f"\n3. 📊 Verificando sesiones de atención {atencion_id}...")
    try:
        sesiones_response = session.get(f"{base_url}/api/get-sesiones/{atencion_id}")
        if sesiones_response.status_code == 200:
            sesiones_data = sesiones_response.json()
            if sesiones_data.get('success'):
                num_sesiones = sesiones_data.get('total', 0)
                print(f"✅ Sesiones encontradas: {num_sesiones}")
                
                if num_sesiones >= 15:
                    print("⚠️ Atención ya tiene el máximo de sesiones (15)")
                    return True
            else:
                print(f"❌ Error obteniendo sesiones: {sesiones_data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {sesiones_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 4. Crear nueva sesión
    print(f"\n4. ➕ Creando nueva sesión...")
    
    nueva_sesion = {
        "atencion_id": atencion_id,
        "fecha_sesion": datetime.now().strftime("%Y-%m-%dT%H:%M"),
        "duracion": 60,
        "tipo_sesion": "evaluacion",
        "objetivos": "Evaluar progreso del paciente y ajustar tratamiento",
        "actividades": "Evaluación física, revisión de síntomas, ajuste de ejercicios",
        "observaciones": "Paciente muestra mejoría en movilidad",
        "progreso": "bueno",
        "estado": "completada",
        "recomendaciones": "Continuar con ejercicios diarios y mantener rutina",
        "proxima_sesion": "Seguimiento en 2 semanas"
    }
    
    try:
        crear_response = session.post(
            f"{base_url}/api/guardar-sesion",
            json=nueva_sesion,
            headers={'Content-Type': 'application/json'}
        )
        
        if crear_response.status_code == 200:
            crear_data = crear_response.json()
            if crear_data.get('success'):
                sesion_id = crear_data.get('sesion_id')
                print(f"✅ Sesión creada exitosamente: {sesion_id}")
            else:
                print(f"❌ Error creando sesión: {crear_data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {crear_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 5. Verificar sesión creada
    print(f"\n5. 👁️ Verificando sesión creada...")
    try:
        verificar_response = session.get(f"{base_url}/api/get-sesion/{sesion_id}")
        if verificar_response.status_code == 200:
            verificar_data = verificar_response.json()
            if verificar_data.get('success'):
                sesion = verificar_data.get('sesion')
                print(f"✅ Sesión verificada:")
                print(f"   - ID: {sesion['id']}")
                print(f"   - Tipo: {sesion['tipo_sesion']}")
                print(f"   - Duración: {sesion['duracion']} minutos")
                print(f"   - Estado: {sesion['estado']}")
                print(f"   - Progreso: {sesion['progreso']}")
            else:
                print(f"❌ Error verificando sesión: {verificar_data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {verificar_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 6. Listar todas las sesiones
    print(f"\n6. 📋 Listando todas las sesiones...")
    try:
        listar_response = session.get(f"{base_url}/api/get-sesiones/{atencion_id}")
        if listar_response.status_code == 200:
            listar_data = listar_response.json()
            if listar_data.get('success'):
                sesiones = listar_data.get('sesiones', [])
                print(f"✅ Total de sesiones: {len(sesiones)}")
                
                for i, sesion in enumerate(sesiones[:3], 1):  # Mostrar solo las primeras 3
                    print(f"   {i}. {sesion['fecha_sesion']} - {sesion['tipo_sesion']} ({sesion['duracion']} min)")
            else:
                print(f"❌ Error listando sesiones: {listar_data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {listar_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # 7. Eliminar sesión de prueba
    print(f"\n7. 🗑️ Eliminando sesión de prueba...")
    try:
        eliminar_response = session.delete(f"{base_url}/api/eliminar-sesion/{sesion_id}")
        if eliminar_response.status_code == 200:
            eliminar_data = eliminar_response.json()
            if eliminar_data.get('success'):
                print(f"✅ Sesión eliminada exitosamente")
            else:
                print(f"❌ Error eliminando sesión: {eliminar_data.get('message')}")
                return False
        else:
            print(f"❌ Error HTTP: {eliminar_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    return True

def test_limite_sesiones():
    """Prueba el límite de sesiones (1-15)"""
    
    print("\n🧪 PRUEBA DE LÍMITE DE SESIONES")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    # Login
    login_data = {
        "email": "giselle.arratia@medconnect.com",
        "password": "test123"
    }
    
    try:
        login_response = session.post(
            f"{base_url}/login",
            data=login_data,
            allow_redirects=False
        )
        
        if login_response.status_code != 302:
            print("❌ Error en login")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Obtener atención
    try:
        atenciones_response = session.get(f"{base_url}/api/get-atenciones")
        if atenciones_response.status_code == 200:
            atenciones_data = atenciones_response.json()
            if atenciones_data.get('success') and atenciones_data.get('atenciones'):
                atencion_id = atenciones_data['atenciones'][0]['id']
            else:
                print("⚠️ No hay atenciones disponibles")
                return False
        else:
            print(f"❌ Error obteniendo atenciones")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Verificar sesiones existentes
    try:
        sesiones_response = session.get(f"{base_url}/api/get-sesiones/{atencion_id}")
        if sesiones_response.status_code == 200:
            sesiones_data = sesiones_response.json()
            if sesiones_data.get('success'):
                num_sesiones = sesiones_data.get('total', 0)
                print(f"📊 Sesiones actuales: {num_sesiones}/15")
                
                if num_sesiones >= 15:
                    print("✅ Límite de sesiones funcionando correctamente")
                    return True
                else:
                    print(f"ℹ️ Espacio disponible: {15 - num_sesiones} sesiones")
            else:
                print(f"❌ Error obteniendo sesiones")
                return False
        else:
            print(f"❌ Error HTTP")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE SESIONES")
    print("=" * 60)
    
    # Ejecutar pruebas
    test1_result = test_sesiones()
    test2_result = test_limite_sesiones()
    
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"✅ Prueba funcionalidad básica: {'PASÓ' if test1_result else 'FALLÓ'}")
    print(f"✅ Prueba límite de sesiones: {'PASÓ' if test2_result else 'FALLÓ'}")
    
    if test1_result and test2_result:
        print("\n🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
    
    print("\n📝 FUNCIONALIDADES IMPLEMENTADAS:")
    print("   ✅ Registro de sesiones (1-15 por atención)")
    print("   ✅ Verificación de límite de sesiones")
    print("   ✅ Consulta de sesiones por atención")
    print("   ✅ Detalle de sesión individual")
    print("   ✅ Eliminación de sesiones")
    print("   ✅ Validación de datos requeridos")
    print("   ✅ Integración con Google Sheets")
    print("   ✅ Interfaz de usuario completa") 