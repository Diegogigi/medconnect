#!/usr/bin/env python3
"""
Script para verificar que no hay errores de sintaxis en el archivo JavaScript
"""

import re
import os

def verificar_sintaxis_js():
    """Verifica que no hay errores de sintaxis en el archivo JavaScript"""
    
    print("🔍 VERIFICACIÓN DE SINTAXIS JAVASCRIPT")
    print("=" * 50)
    
    js_file = "static/js/professional.js"
    
    if not os.path.exists(js_file):
        print(f"❌ Archivo no encontrado: {js_file}")
        return False
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Archivo leído: {js_file}")
        print(f"📊 Tamaño: {len(content)} caracteres")
        
        # Verificar caracteres problemáticos en las plantillas de string
        print("\n🔍 Verificando plantillas de string...")
        
        # Buscar patrones problemáticos
        problematic_patterns = [
            r"onclick=\"[^\"]*'\$\{([^}]+)\}'[^\"]*\"",
            r"onclick=\"[^\"]*'\$\{([^}]+)\}'[^\"]*\"",
        ]
        
        for pattern in problematic_patterns:
            matches = re.findall(pattern, content)
            if matches:
                print(f"⚠️ Patrón problemático encontrado: {pattern}")
                for match in matches[:3]:  # Mostrar solo los primeros 3
                    print(f"   - Variable: {match}")
        
        # Verificar que las funciones están correctamente definidas
        print("\n🔍 Verificando funciones...")
        
        required_functions = [
            'realizarBusquedaPersonalizada',
            'realizarBusquedaAutomatica',
            'obtenerTerminosSeleccionados',
            'seleccionarTodosTerminos',
            'deseleccionarTodosTerminos',
            'mostrarTerminosDisponibles'
        ]
        
        for func in required_functions:
            if f"function {func}" in content or f"async function {func}" in content:
                print(f"✅ Función encontrada: {func}")
            else:
                print(f"❌ Función NO encontrada: {func}")
        
        # Verificar exposición global
        print("\n🔍 Verificando exposición global...")
        
        global_exposures = [
            'window.realizarBusquedaPersonalizada',
            'window.realizarBusquedaAutomatica',
            'window.obtenerTerminosSeleccionados',
            'window.seleccionarTodosTerminos',
            'window.deseleccionarTodosTerminos',
            'window.mostrarTerminosDisponibles'
        ]
        
        for exposure in global_exposures:
            if exposure in content:
                print(f"✅ Exposición global encontrada: {exposure}")
            else:
                print(f"❌ Exposición global NO encontrada: {exposure}")
        
        # Verificar que no hay comillas simples sin escapar en onclick
        print("\n🔍 Verificando escape de comillas...")
        
        # Buscar onclick con comillas simples sin escapar
        onclick_pattern = r'onclick="[^"]*\'[^\']*\'[^"]*"'
        onclick_matches = re.findall(onclick_pattern, content)
        
        if onclick_matches:
            print(f"⚠️ Encontrados {len(onclick_matches)} onclick con comillas simples")
            for match in onclick_matches[:2]:  # Mostrar solo los primeros 2
                print(f"   - {match[:100]}...")
        else:
            print("✅ No se encontraron onclick problemáticos")
        
        # Verificar que el archivo termina correctamente
        print("\n🔍 Verificando estructura del archivo...")
        
        if content.strip().endswith('}'):
            print("✅ Archivo termina correctamente")
        else:
            print("⚠️ Archivo puede no terminar correctamente")
        
        # Verificar balance de llaves y paréntesis
        open_braces = content.count('{')
        close_braces = content.count('}')
        open_parens = content.count('(')
        close_parens = content.count(')')
        
        print(f"📊 Balance de llaves: {open_braces} abiertas, {close_braces} cerradas")
        print(f"📊 Balance de paréntesis: {open_parens} abiertos, {close_parens} cerrados")
        
        if open_braces == close_braces:
            print("✅ Llaves balanceadas correctamente")
        else:
            print(f"❌ Llaves desbalanceadas: {open_braces - close_braces}")
        
        if open_parens == close_parens:
            print("✅ Paréntesis balanceados correctamente")
        else:
            print(f"❌ Paréntesis desbalanceados: {open_parens - close_parens}")
        
        print("\n🎯 VERIFICACIÓN COMPLETADA")
        print("=" * 30)
        
        # Resumen
        issues_found = 0
        if open_braces != close_braces:
            issues_found += 1
        if open_parens != close_parens:
            issues_found += 1
        if onclick_matches:
            issues_found += 1
        
        if issues_found == 0:
            print("✅ No se encontraron errores de sintaxis evidentes")
            print("✅ El archivo JavaScript debería funcionar correctamente")
            return True
        else:
            print(f"⚠️ Se encontraron {issues_found} posibles problemas")
            print("⚠️ Se recomienda revisar el archivo manualmente")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando archivo: {e}")
        return False

if __name__ == "__main__":
    verificar_sintaxis_js() 