#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el nuevo diseño elegante de la sidebar
"""

import requests
import re
from bs4 import BeautifulSoup

def test_diseno_elegante():
    """Verifica que el nuevo diseño elegante esté implementado correctamente"""
    
    print("🎨 VERIFICACIÓN DEL DISEÑO ELEGANTE")
    print("=" * 50)
    
    try:
        # Hacer request a la página professional
        response = requests.get('http://localhost:5000/professional')
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("1. 🔍 Verificando estructura HTML elegante...")
        
        # Verificar elementos del nuevo diseño
        elementos_elegantes = [
            'copilotChatElegant',
            'chat-header-elegant',
            'chat-title',
            'chat-status',
            'chat-messages-elegant',
            'messages-container',
            'message-elegant',
            'message-bubble',
            'message-icon',
            'message-text',
            'typing-elegant',
            'typing-bubble',
            'typing-avatar',
            'typing-content',
            'typing-animation',
            'results-area',
            'main-action',
            'btn-copilot-primary',
            'btn-content',
            'btn-status'
        ]
        
        elementos_encontrados = 0
        for elemento in elementos_elegantes:
            if soup.find(id=elemento) or soup.find(class_=elemento.replace('Elegant', '-elegant')):
                print(f"   ✅ {elemento}")
                elementos_encontrados += 1
            else:
                print(f"   ❌ {elemento} - NO ENCONTRADO")
        
        print(f"\n   📊 Elementos encontrados: {elementos_encontrados}/{len(elementos_elegantes)}")
        
        print("\n2. 🎨 Verificando estilos CSS elegantes...")
        
        # Verificar estilos CSS
        estilos_elegantes = [
            'copilot-chat-elegant',
            'chat-header-elegant',
            'chat-title',
            'chat-status',
            'status-indicator',
            'chat-messages-elegant',
            'messages-container',
            'message-elegant',
            'message-bubble',
            'message-icon',
            'message-text',
            'message-time',
            'typing-elegant',
            'typing-bubble',
            'typing-avatar',
            'typing-content',
            'typing-animation',
            'results-area',
            'main-action',
            'btn-copilot-primary',
            'btn-content',
            'btn-status',
            'analyzing'
        ]
        
        estilos_encontrados = 0
        for estilo in estilos_elegantes:
            patron = r'\.' + estilo.replace('-', r'\-')
            if re.search(patron, response.text):
                print(f"   ✅ {estilo}")
                estilos_encontrados += 1
            else:
                print(f"   ❌ {estilo} - NO ENCONTRADO")
        
        print(f"\n   📊 Estilos encontrados: {estilos_encontrados}/{len(estilos_elegantes)}")
        
        print("\n3. ⚡ Verificando funciones JavaScript elegantes...")
        
        # Verificar funciones JavaScript
        funciones_elegantes = [
            'agregarMensajeElegant',
            'mostrarTypingElegant',
            'removerTypingElegant',
            'limpiarChatElegant',
            'actualizarEstadoBoton',
            'activarCopilotHealthElegant',
            'realizarAnalisisElegant',
            'mostrarResultadosElegant',
            'insertarPaperElegant',
            'inicializarObservadorFormularioElegant'
        ]
        
        funciones_encontradas = 0
        for funcion in funciones_elegantes:
            if re.search(f'function {funcion}', response.text):
                print(f"   ✅ {funcion}")
                funciones_encontradas += 1
            else:
                print(f"   ❌ {funcion} - NO ENCONTRADA")
        
        print(f"\n   📊 Funciones encontradas: {funciones_encontradas}/{len(funciones_elegantes)}")
        
        print("\n4. 🎯 Verificando características específicas...")
        
        # Verificar características específicas
        caracteristicas = [
            ('Gradiente de fondo', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'),
            ('Border radius', 'border-radius: 16px'),
            ('Box shadow', 'box-shadow: 0 8px 32px'),
            ('Animaciones', '@keyframes slideInUp'),
            ('Animaciones typing', '@keyframes elegantTyping'),
            ('Animación spin', '@keyframes spin'),
            ('Scrollbar personalizado', '::-webkit-scrollbar'),
            ('Botón principal', 'btn-copilot-primary'),
            ('Estado analyzing', 'analyzing')
        ]
        
        caracteristicas_encontradas = 0
        for nombre, patron in caracteristicas:
            if re.search(patron, response.text):
                print(f"   ✅ {nombre}")
                caracteristicas_encontradas += 1
            else:
                print(f"   ❌ {nombre} - NO ENCONTRADO")
        
        print(f"\n   📊 Características encontradas: {caracteristicas_encontradas}/{len(caracteristicas)}")
        
        # Calcular progreso general
        total_elementos = len(elementos_elegantes) + len(estilos_elegantes) + len(funciones_elegantes) + len(caracteristicas)
        elementos_totales = elementos_encontrados + estilos_encontrados + funciones_encontradas + caracteristicas_encontradas
        
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 50)
        print(f"✅ Elementos HTML: {elementos_encontrados}/{len(elementos_elegantes)}")
        print(f"✅ Estilos CSS: {estilos_encontrados}/{len(estilos_elegantes)}")
        print(f"✅ Funciones JS: {funciones_encontradas}/{len(funciones_elegantes)}")
        print(f"✅ Características: {caracteristicas_encontradas}/{len(caracteristicas)}")
        print(f"📈 PROGRESO GENERAL: {elementos_totales}/{total_elementos} ({elementos_totales/total_elementos*100:.1f}%)")
        
        if elementos_totales >= total_elementos * 0.8:
            print("\n🎉 ¡DISEÑO ELEGANTE IMPLEMENTADO EXITOSAMENTE!")
            print("   El nuevo diseño está listo para usar.")
        else:
            print("\n⚠️  DISEÑO ELEGANTE INCOMPLETO")
            print("   Algunos elementos faltan. Verifica la implementación.")
        
        return elementos_totales >= total_elementos * 0.8
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    test_diseno_elegante() 