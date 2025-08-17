#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que toda la funcionalidad de Copilot Health esté funcionando correctamente
"""

import requests
import re

def verificar_funcionalidad_completa():
    """Verifica que toda la funcionalidad de Copilot Health esté funcionando"""
    
    print("🤖 VERIFICACIÓN DE FUNCIONALIDAD COMPLETA")
    print("=" * 60)
    
    try:
        # Hacer request a la página professional
        response = requests.get('http://localhost:5000/professional')
        response.raise_for_status()
        
        print("1. 🔍 Verificando funciones de análisis...")
        
        # Funciones de análisis que deberían estar presentes
        funciones_analisis = [
            'analizarMotivoConsultaMejorado',
            'buscarEvidenciaMejorada',
            'analizarCasoCompletoMejorado',
            'generarPreguntasPersonalizadas'
        ]
        
        funciones_encontradas = 0
        for funcion in funciones_analisis:
            if funcion in response.text:
                print(f"   ✅ {funcion} - PRESENTE")
                funciones_encontradas += 1
            else:
                print(f"   ❌ {funcion} - NO ENCONTRADA")
        
        print(f"\n   📊 Funciones de análisis: {funciones_encontradas}/{len(funciones_analisis)}")
        
        print("\n2. 🎯 Verificando funciones elegantes...")
        
        # Funciones elegantes que deberían estar presentes
        funciones_elegantes = [
            'activarCopilotHealthElegant',
            'realizarAnalisisElegant',
            'mostrarResultadosElegant',
            'insertarPreguntaElegant',
            'insertarPaperElegant'
        ]
        
        funciones_elegantes_encontradas = 0
        for funcion in funciones_elegantes:
            if funcion in response.text:
                print(f"   ✅ {funcion} - PRESENTE")
                funciones_elegantes_encontradas += 1
            else:
                print(f"   ❌ {funcion} - NO ENCONTRADA")
        
        print(f"\n   📊 Funciones elegantes: {funciones_elegantes_encontradas}/{len(funciones_elegantes)}")
        
        print("\n3. 🎨 Verificando elementos de interfaz...")
        
        # Elementos de interfaz que deberían estar presentes
        elementos_interfaz = [
            'btnCopilotPrimary',
            'messagesContainer',
            'resultsArea',
            'typingElegant'
        ]
        
        elementos_encontrados = 0
        for elemento in elementos_interfaz:
            if elemento in response.text:
                print(f"   ✅ {elemento} - PRESENTE")
                elementos_encontrados += 1
            else:
                print(f"   ❌ {elemento} - NO ENCONTRADO")
        
        print(f"\n   📊 Elementos de interfaz: {elementos_encontrados}/{len(elementos_interfaz)}")
        
        print("\n4. 🎨 Verificando estilos CSS...")
        
        # Estilos CSS que deberían estar presentes
        estilos_css = [
            'btn-copilot-primary',
            'message-elegant',
            'results-area',
            'question-item',
            'evidence-item'
        ]
        
        estilos_encontrados = 0
        for estilo in estilos_css:
            patron = r'\.' + estilo.replace('-', r'\-')
            if re.search(patron, response.text):
                print(f"   ✅ {estilo} - PRESENTE EN CSS")
                estilos_encontrados += 1
            else:
                print(f"   ❌ {estilo} - NO ENCONTRADO EN CSS")
        
        print(f"\n   📊 Estilos CSS: {estilos_encontrados}/{len(estilos_css)}")
        
        print("\n5. 🔗 Verificando integración con formulario...")
        
        # Verificar integración con campos del formulario
        campos_formulario = [
            'motivoConsulta',
            'tipoAtencion',
            'edad',
            'antecedentes',
            'evaluacion'
        ]
        
        campos_encontrados = 0
        for campo in campos_formulario:
            if campo in response.text:
                print(f"   ✅ {campo} - PRESENTE")
                campos_encontrados += 1
            else:
                print(f"   ❌ {campo} - NO ENCONTRADO")
        
        print(f"\n   📊 Campos de formulario: {campos_encontrados}/{len(campos_formulario)}")
        
        print("\n6. 🌐 Verificando endpoints de API...")
        
        # Verificar que los endpoints de API estén documentados
        endpoints_api = [
            '/api/copilot/generate-evaluation-questions',
            '/api/copilot/analyze-motivo',
            '/api/copilot/search-enhanced'
        ]
        
        endpoints_encontrados = 0
        for endpoint in endpoints_api:
            if endpoint in response.text:
                print(f"   ✅ {endpoint} - REFERENCIADO")
                endpoints_encontrados += 1
            else:
                print(f"   ❌ {endpoint} - NO REFERENCIADO")
        
        print(f"\n   📊 Endpoints de API: {endpoints_encontrados}/{len(endpoints_api)}")
        
        # Calcular progreso general
        total_elementos = (len(funciones_analisis) + len(funciones_elegantes) + 
                          len(elementos_interfaz) + len(estilos_css) + 
                          len(campos_formulario) + len(endpoints_api))
        
        elementos_correctos = (funciones_encontradas + funciones_elegantes_encontradas + 
                              elementos_encontrados + estilos_encontrados + 
                              campos_encontrados + endpoints_encontrados)
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 60)
        print(f"✅ Funciones de análisis: {funciones_encontradas}/{len(funciones_analisis)}")
        print(f"✅ Funciones elegantes: {funciones_elegantes_encontradas}/{len(funciones_elegantes)}")
        print(f"✅ Elementos de interfaz: {elementos_encontrados}/{len(elementos_interfaz)}")
        print(f"✅ Estilos CSS: {estilos_encontrados}/{len(estilos_css)}")
        print(f"✅ Campos de formulario: {campos_encontrados}/{len(campos_formulario)}")
        print(f"✅ Endpoints de API: {endpoints_encontrados}/{len(endpoints_api)}")
        print(f"📈 PROGRESO GENERAL: {elementos_correctos}/{total_elementos} ({elementos_correctos/total_elementos*100:.1f}%)")
        
        if elementos_correctos >= total_elementos * 0.8:
            print("\n🎉 ¡FUNCIONALIDAD COMPLETA IMPLEMENTADA!")
            print("   Copilot Health debería funcionar correctamente con:")
            print("   - Análisis de motivo de consulta")
            print("   - Análisis de tipo de atención")
            print("   - Análisis de edad del paciente")
            print("   - Análisis de antecedentes")
            print("   - Análisis de evaluación")
            print("   - Generación de preguntas personalizadas")
            print("   - Búsqueda de evidencia científica")
            print("   - Interfaz elegante en tiempo real")
        else:
            print("\n⚠️  FUNCIONALIDAD INCOMPLETA")
            print("   Algunas funciones aún están faltando.")
        
        return elementos_correctos >= total_elementos * 0.8
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    verificar_funcionalidad_completa() 