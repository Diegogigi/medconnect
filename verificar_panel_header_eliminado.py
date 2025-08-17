#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que el header del panel de Copilot Health ha sido eliminado
"""

import requests
import re

def verificar_panel_header_eliminado():
    """Verifica que el header del panel de Copilot Health ha sido eliminado correctamente"""
    
    print("🗑️  VERIFICACIÓN DE ELIMINACIÓN DEL HEADER DEL PANEL")
    print("=" * 60)
    
    try:
        # Hacer request a la página professional
        response = requests.get('http://localhost:5000/professional')
        response.raise_for_status()
        
        print("1. 🔍 Verificando elementos eliminados...")
        
        # Elementos que deberían estar eliminados
        elementos_eliminados = [
            'panel-header',
            'Copilot Health',
            'fas fa-robot me-2',
            'minimizePanel()',
            'maximizePanel()',
            'fas fa-minus',
            'fas fa-expand',
            'panel-controls'
        ]
        
        elementos_encontrados = 0
        for elemento in elementos_eliminados:
            if elemento in response.text:
                print(f"   ❌ {elemento} - AÚN PRESENTE")
                elementos_encontrados += 1
            else:
                print(f"   ✅ {elemento} - ELIMINADO CORRECTAMENTE")
        
        print(f"\n   📊 Elementos eliminados: {len(elementos_eliminados) - elementos_encontrados}/{len(elementos_eliminados)}")
        
        print("\n2. 🎨 Verificando estilos CSS eliminados...")
        
        # Estilos CSS que deberían estar eliminados
        estilos_eliminados = [
            'panel-header'
        ]
        
        estilos_encontrados = 0
        for estilo in estilos_eliminados:
            patron = r'\.' + estilo.replace('-', r'\-')
            if re.search(patron, response.text):
                print(f"   ❌ {estilo} - AÚN PRESENTE EN CSS")
                estilos_encontrados += 1
            else:
                print(f"   ✅ {estilo} - ELIMINADO DEL CSS")
        
        print(f"\n   📊 Estilos eliminados: {len(estilos_eliminados) - estilos_encontrados}/{len(estilos_eliminados)}")
        
        print("\n3. 🎯 Verificando estructura simplificada...")
        
        # Elementos que deberían estar presentes
        elementos_presentes = [
            'sidebar-container',
            'sidebar-resize-handle',
            'panel-content',
            'copilot-chat-elegant',
            'chat-messages-elegant',
            'btn-copilot-primary'
        ]
        
        elementos_ok = 0
        for elemento in elementos_presentes:
            if elemento in response.text:
                print(f"   ✅ {elemento} - PRESENTE")
                elementos_ok += 1
            else:
                print(f"   ❌ {elemento} - NO ENCONTRADO")
        
        print(f"\n   📊 Elementos presentes: {elementos_ok}/{len(elementos_presentes)}")
        
        print("\n4. 📏 Verificando espaciado ajustado...")
        
        # Verificar que el espaciado se haya ajustado
        espaciado_ajustado = [
            ('border-bottom border-secondary', 'Borde inferior eliminado'),
            ('justify-content-between align-items-center p-3', 'Layout del header eliminado')
        ]
        
        espaciado_ok = 0
        for patron, descripcion in espaciado_ajustado:
            if re.search(patron, response.text):
                print(f"   ❌ {descripcion} - AÚN PRESENTE")
            else:
                print(f"   ✅ {descripcion} - ELIMINADO")
                espaciado_ok += 1
        
        print(f"\n   📊 Espaciado ajustado: {espaciado_ok}/{len(espaciado_ajustado)}")
        
        # Calcular progreso general
        total_eliminaciones = len(elementos_eliminados) + len(estilos_eliminados)
        eliminaciones_exitosas = (len(elementos_eliminados) - elementos_encontrados) + (len(estilos_eliminados) - estilos_encontrados)
        
        total_elementos = len(elementos_presentes) + len(espaciado_ajustado)
        elementos_correctos = elementos_ok + espaciado_ok
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 60)
        print(f"✅ Elementos eliminados: {eliminaciones_exitosas}/{total_eliminaciones}")
        print(f"✅ Elementos presentes: {elementos_correctos}/{total_elementos}")
        print(f"📈 PROGRESO GENERAL: {(eliminaciones_exitosas + elementos_correctos)}/{(total_eliminaciones + total_elementos)} ({(eliminaciones_exitosas + elementos_correctos)/(total_eliminaciones + total_elementos)*100:.1f}%)")
        
        if eliminaciones_exitosas >= total_eliminaciones * 0.8 and elementos_correctos >= total_elementos * 0.8:
            print("\n🎉 ¡HEADER DEL PANEL ELIMINADO EXITOSAMENTE!")
            print("   La sidebar ahora es completamente limpia sin header.")
        else:
            print("\n⚠️  ELIMINACIÓN INCOMPLETA")
            print("   Algunos elementos del header aún están presentes.")
        
        return eliminaciones_exitosas >= total_eliminaciones * 0.8 and elementos_correctos >= total_elementos * 0.8
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    verificar_panel_header_eliminado() 