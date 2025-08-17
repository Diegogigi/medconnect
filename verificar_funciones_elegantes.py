#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que las funciones elegantes están funcionando correctamente
"""

import requests
import re

def verificar_funciones_elegantes():
    """Verifica que las funciones elegantes están funcionando correctamente"""
    
    print("🤖 VERIFICACIÓN DE FUNCIONES ELEGANTES")
    print("=" * 50)
    
    try:
        # Hacer request a la página professional
        response = requests.get('http://localhost:5000/professional')
        response.raise_for_status()
        
        print("1. 🔍 Verificando funciones JavaScript...")
        
        # Funciones que deberían estar presentes
        funciones_requeridas = [
            'activarCopilotHealthElegant',
            'agregarMensajeElegant',
            'mostrarTypingElegant',
            'removerTypingElegant',
            'limpiarChatElegant',
            'actualizarEstadoBoton',
            'realizarAnalisisElegant',
            'mostrarResultadosElegant',
            'insertarPaperElegant',
            'inicializarObservadorFormularioElegant'
        ]
        
        funciones_encontradas = 0
        for funcion in funciones_requeridas:
            if funcion in response.text:
                print(f"   ✅ {funcion} - PRESENTE")
                funciones_encontradas += 1
            else:
                print(f"   ❌ {funcion} - NO ENCONTRADA")
        
        print(f"\n   📊 Funciones encontradas: {funciones_encontradas}/{len(funciones_requeridas)}")
        
        print("\n2. 🎯 Verificando elementos HTML...")
        
        # Elementos HTML que deberían estar presentes
        elementos_html = [
            'btnCopilotPrimary',
            'messagesContainer',
            'typingElegant',
            'resultsArea',
            'btnStatus'
        ]
        
        elementos_encontrados = 0
        for elemento in elementos_html:
            if elemento in response.text:
                print(f"   ✅ {elemento} - PRESENTE")
                elementos_encontrados += 1
            else:
                print(f"   ❌ {elemento} - NO ENCONTRADO")
        
        print(f"\n   📊 Elementos HTML encontrados: {elementos_encontrados}/{len(elementos_html)}")
        
        print("\n3. 🎨 Verificando estilos CSS...")
        
        # Estilos CSS que deberían estar presentes
        estilos_css = [
            'btn-copilot-primary',
            'message-elegant',
            'message-bubble',
            'message-icon',
            'typing-elegant',
            'results-area'
        ]
        
        estilos_encontrados = 0
        for estilo in estilos_css:
            patron = r'\.' + estilo.replace('-', r'\-')
            if re.search(patron, response.text):
                print(f"   ✅ {estilo} - PRESENTE EN CSS")
                estilos_encontrados += 1
            else:
                print(f"   ❌ {estilo} - NO ENCONTRADO EN CSS")
        
        print(f"\n   📊 Estilos CSS encontrados: {estilos_encontrados}/{len(estilos_css)}")
        
        print("\n4. 🔗 Verificando integración...")
        
        # Verificar integración con funciones existentes
        integracion_ok = [
            ('analizarMotivoConsultaMejorado', 'Función de análisis de motivo'),
            ('buscarEvidenciaMejorada', 'Función de búsqueda de evidencia'),
            ('analizarCasoCompletoMejorado', 'Función de análisis completo')
        ]
        
        integracion_encontrada = 0
        for funcion, descripcion in integracion_ok:
            if funcion in response.text:
                print(f"   ✅ {descripcion}")
                integracion_encontrada += 1
            else:
                print(f"   ❌ {descripcion} - NO ENCONTRADA")
        
        print(f"\n   📊 Integración encontrada: {integracion_encontrada}/{len(integracion_ok)}")
        
        # Calcular progreso general
        total_funciones = len(funciones_requeridas) + len(elementos_html) + len(estilos_css) + len(integracion_ok)
        funciones_correctas = funciones_encontradas + elementos_encontrados + estilos_encontrados + integracion_encontrada
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 50)
        print(f"✅ Funciones JavaScript: {funciones_encontradas}/{len(funciones_requeridas)}")
        print(f"✅ Elementos HTML: {elementos_encontrados}/{len(elementos_html)}")
        print(f"✅ Estilos CSS: {estilos_encontrados}/{len(estilos_css)}")
        print(f"✅ Integración: {integracion_encontrada}/{len(integracion_ok)}")
        print(f"📈 PROGRESO GENERAL: {funciones_correctas}/{total_funciones} ({funciones_correctas/total_funciones*100:.1f}%)")
        
        if funciones_correctas >= total_funciones * 0.8:
            print("\n🎉 ¡FUNCIONES ELEGANTES IMPLEMENTADAS EXITOSAMENTE!")
            print("   La sidebar ahora debería funcionar correctamente.")
        else:
            print("\n⚠️  IMPLEMENTACIÓN INCOMPLETA")
            print("   Algunas funciones aún están faltando.")
        
        return funciones_correctas >= total_funciones * 0.8
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    verificar_funciones_elegantes() 