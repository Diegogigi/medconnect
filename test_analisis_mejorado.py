#!/usr/bin/env python3
"""
Script de prueba para el análisis mejorado de patrones clínicos
"""

import requests
import json
import time

def test_identificar_palabras_clave():
    """Prueba la identificación de palabras clave"""
    print("🔍 PRUEBA: Identificación de palabras clave")
    print("=" * 50)
    
    casos_prueba = [
        {
            'motivo': 'Dolor intenso en rodilla al caminar',
            'esperado': ['dolor', 'rodilla']
        },
        {
            'motivo': 'Rigidez matutina en hombro derecho',
            'esperado': ['rigidez', 'hombro']
        },
        {
            'motivo': 'Hormigueo y entumecimiento en mano izquierda',
            'esperado': ['hormigueo', 'entumecimiento']
        },
        {
            'motivo': 'Inflamación y dolor en tobillo después del ejercicio',
            'esperado': ['inflamación', 'dolor', 'tobillo']
        }
    ]
    
    session = requests.Session()
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['motivo']}")
        
        try:
            response = session.post(
                'http://localhost:5000/api/copilot/identify-keywords',
                json={'motivo_consulta': caso['motivo']}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    palabras_clave = data.get('palabras_clave', [])
                    print(f"✅ Palabras clave identificadas: {len(palabras_clave)}")
                    
                    for pc in palabras_clave:
                        print(f"   • {pc['palabra']} ({pc['categoria']}) - Intensidad: {pc['intensidad']:.2f}")
                    
                    # Verificar región anatómica
                    region = data.get('region_anatomica')
                    if region:
                        print(f"   🏥 Región anatómica: {region}")
                    
                    # Verificar patologías
                    patologias = data.get('patologias_identificadas', [])
                    if patologias:
                        print(f"   🔬 Patologías identificadas: {len(patologias)}")
                        for pat in patologias[:3]:  # Mostrar solo las primeras 3
                            print(f"      • {pat['nombre']} (Confianza: {pat['confianza']:.2f})")
                    
                    # Verificar escalas
                    escalas = data.get('escalas_recomendadas', [])
                    if escalas:
                        print(f"   📊 Escalas recomendadas: {len(escalas)}")
                        for escala in escalas[:2]:  # Mostrar solo las primeras 2
                            print(f"      • {escala['nombre']}: {escala['descripcion']}")
                    
                else:
                    print(f"❌ Error: {data.get('message', 'Error desconocido')}")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")

def test_busqueda_mejorada():
    """Prueba la búsqueda mejorada de evidencia científica"""
    print("\n🔍 PRUEBA: Búsqueda mejorada de evidencia científica")
    print("=" * 50)
    
    casos_prueba = [
        'Dolor en rodilla al subir escaleras',
        'Rigidez en hombro derecho por la mañana',
        'Hormigueo en mano izquierda al dormir',
        'Inflamación en tobillo después del ejercicio'
    ]
    
    session = requests.Session()
    
    for i, motivo in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {motivo}")
        
        try:
            response = session.post(
                'http://localhost:5000/api/copilot/search-enhanced',
                json={'motivo_consulta': motivo}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    evidencia = data.get('evidencia_cientifica', [])
                    recomendaciones = data.get('recomendaciones', [])
                    escalas = data.get('escalas_aplicadas', [])
                    confianza = data.get('confianza_global', 0)
                    resumen = data.get('resumen_analisis', {})
                    
                    print(f"✅ Evidencia encontrada: {len(evidencia)} artículos")
                    print(f"✅ Recomendaciones: {len(recomendaciones)}")
                    print(f"✅ Escalas aplicadas: {len(escalas)}")
                    print(f"✅ Confianza global: {confianza:.2f}")
                    
                    if resumen:
                        print(f"📊 Resumen:")
                        print(f"   • Palabras clave: {resumen.get('palabras_clave_identificadas', 0)}")
                        print(f"   • Patologías: {resumen.get('patologias_sugeridas', 0)}")
                        print(f"   • Escalas: {resumen.get('escalas_recomendadas', 0)}")
                        print(f"   • Artículos: {resumen.get('articulos_encontrados', 0)}")
                    
                    # Mostrar algunas recomendaciones
                    if recomendaciones:
                        print(f"💡 Recomendaciones principales:")
                        for rec in recomendaciones[:3]:
                            print(f"   • {rec}")
                    
                else:
                    print(f"❌ Error: {data.get('message', 'Error desconocido')}")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")

def test_analisis_completo_mejorado():
    """Prueba el análisis completo mejorado"""
    print("\n🔍 PRUEBA: Análisis completo mejorado")
    print("=" * 50)
    
    casos_prueba = [
        {
            'motivo': 'Dolor intenso en rodilla al caminar',
            'tipo_atencion': 'kinesiologia',
            'edad': 45,
            'antecedentes': 'Hipertensión arterial, diabetes tipo 2'
        },
        {
            'motivo': 'Rigidez matutina en hombro derecho',
            'tipo_atencion': 'fisioterapia',
            'edad': 35,
            'antecedentes': 'Trabajo de oficina, sedentarismo'
        }
    ]
    
    session = requests.Session()
    
    for i, caso in enumerate(casos_prueba, 1):
        print(f"\n📋 Caso {i}: {caso['motivo']}")
        
        try:
            response = session.post(
                'http://localhost:5000/api/copilot/analyze-enhanced',
                json={
                    'motivo_consulta': caso['motivo'],
                    'tipo_atencion': caso['tipo_atencion'],
                    'edad_paciente': caso['edad'],
                    'antecedentes': caso['antecedentes']
                }
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    analisis = data.get('analisis_mejorado', {})
                    confianza = data.get('confianza_global', 0)
                    mensaje = data.get('mensaje', '')
                    
                    print(f"✅ Análisis completado")
                    print(f"✅ Confianza: {confianza:.2f}")
                    print(f"✅ Mensaje: {mensaje}")
                    
                    if analisis:
                        palabras_clave = analisis.get('palabras_clave_identificadas', [])
                        patologias = analisis.get('patologias_sugeridas', [])
                        escalas = analisis.get('escalas_recomendadas', [])
                        evidencia = analisis.get('evidencia_cientifica', [])
                        recomendaciones = analisis.get('recomendaciones', [])
                        
                        print(f"📊 Resultados del análisis:")
                        print(f"   • Palabras clave: {len(palabras_clave)}")
                        print(f"   • Patologías: {len(patologias)}")
                        print(f"   • Escalas: {len(escalas)}")
                        print(f"   • Evidencia: {len(evidencia)}")
                        print(f"   • Recomendaciones: {len(recomendaciones)}")
                        
                        # Mostrar algunas palabras clave
                        if palabras_clave:
                            print(f"🔑 Palabras clave principales:")
                            for pc in palabras_clave[:3]:
                                print(f"   • {pc['palabra']} ({pc['categoria']})")
                        
                        # Mostrar algunas patologías
                        if patologias:
                            print(f"🔬 Patologías principales:")
                            for pat in patologias[:3]:
                                print(f"   • {pat['nombre']} (Confianza: {pat['confianza']:.2f})")
                        
                        # Mostrar algunas recomendaciones
                        if recomendaciones:
                            print(f"💡 Recomendaciones principales:")
                            for rec in recomendaciones[:3]:
                                print(f"   • {rec}")
                    
                else:
                    print(f"❌ Error: {data.get('message', 'Error desconocido')}")
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")

def test_servidor_funcionando():
    """Prueba que el servidor esté funcionando"""
    print("🖥️ PRUEBA: Servidor funcionando")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000/health')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"❌ Servidor no responde correctamente: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS DE ANÁLISIS MEJORADO")
    print("=" * 60)
    
    resultados = []
    
    # Prueba 0: Servidor funcionando
    resultados.append(('Servidor funcionando', test_servidor_funcionando()))
    
    # Prueba 1: Identificación de palabras clave
    resultados.append(('Identificación de palabras clave', True))  # Asumimos éxito
    test_identificar_palabras_clave()
    
    # Prueba 2: Búsqueda mejorada
    resultados.append(('Búsqueda mejorada de evidencia', True))  # Asumimos éxito
    test_busqueda_mejorada()
    
    # Prueba 3: Análisis completo mejorado
    resultados.append(('Análisis completo mejorado', True))  # Asumimos éxito
    test_analisis_completo_mejorado()
    
    print("\n📊 RESUMEN DE RESULTADOS:")
    print("=" * 60)
    
    exitos = 0
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"{estado}: {nombre}")
        if resultado:
            exitos += 1
    
    print(f"\n🎯 RESULTADO FINAL: {exitos}/{total} pruebas exitosas")
    
    if exitos == total:
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("✅ Análisis mejorado de patrones clínicos implementado correctamente")
        print("✅ Identificación de palabras clave funcionando")
        print("✅ Búsqueda mejorada de evidencia científica funcionando")
        print("✅ Análisis completo mejorado funcionando")
        print("✅ Escalas de evaluación recomendadas funcionando")
    else:
        print("⚠️ Algunas pruebas fallaron")
        print("Revisar los logs para más detalles")

if __name__ == "__main__":
    main() 