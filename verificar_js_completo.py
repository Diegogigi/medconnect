#!/usr/bin/env python3
"""
Script para verificar completamente el archivo JavaScript en busca de errores de sintaxis
"""

import re
import os

def verificar_js_completo():
    """Verifica completamente el archivo JavaScript"""
    
    print("🔍 VERIFICACIÓN COMPLETA DEL ARCHIVO JAVASCRIPT")
    print("=" * 60)
    
    js_file = "static/js/professional.js"
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Tamaño del archivo: {len(content)} caracteres")
        print(f"📊 Líneas totales: {content.count(chr(10)) + 1}")
        
        # Verificar caracteres de control problemáticos
        control_chars = []
        for i, char in enumerate(content):
            if ord(char) < 32 and char not in '\n\r\t':
                control_chars.append((i, char, ord(char)))
        
        if control_chars:
            print(f"⚠️ Encontrados {len(control_chars)} caracteres de control:")
            for pos, char, code in control_chars[:10]:
                print(f"   - Posición {pos}: '{char}' (código {code})")
        else:
            print("✅ No se encontraron caracteres de control problemáticos")
        
        # Verificar inicio del archivo
        print("\n🔍 Verificando inicio del archivo...")
        first_chars = content[:200]
        print(f"📋 Primeros 200 caracteres:")
        print(f"'{first_chars}'")
        
        # Verificar que comience correctamente
        if content.strip().startswith('//'):
            print("✅ El archivo comienza correctamente con comentario")
        else:
            print("⚠️ El archivo no comienza con comentario")
        
        # Verificar paréntesis balanceados
        print("\n🔍 Verificando paréntesis balanceados...")
        open_parens = content.count('(')
        close_parens = content.count(')')
        open_braces = content.count('{')
        close_braces = content.count('}')
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        
        print(f"📊 Paréntesis: {open_parens} abiertos, {close_parens} cerrados")
        print(f"📊 Llaves: {open_braces} abiertas, {close_braces} cerradas")
        print(f"📊 Corchetes: {open_brackets} abiertos, {close_brackets} cerrados")
        
        if open_parens == close_parens and open_braces == close_braces and open_brackets == close_brackets:
            print("✅ Todos los delimitadores están balanceados")
        else:
            print("❌ Hay delimitadores desbalanceados")
        
        # Verificar strings problemáticos
        print("\n🔍 Verificando strings problemáticos...")
        
        # Buscar strings con comillas sin escapar
        single_quotes = re.findall(r"'[^']*'", content)
        double_quotes = re.findall(r'"[^"]*"', content)
        
        print(f"📊 Strings con comillas simples: {len(single_quotes)}")
        print(f"📊 Strings con comillas dobles: {len(double_quotes)}")
        
        # Verificar strings problemáticos
        problematic_strings = []
        for i, string in enumerate(single_quotes + double_quotes):
            if "'" in string and '"' in string:
                problematic_strings.append((i, string))
        
        if problematic_strings:
            print(f"⚠️ Encontrados {len(problematic_strings)} strings con comillas mixtas:")
            for i, string in problematic_strings[:5]:
                print(f"   - String {i}: {string}")
        else:
            print("✅ No se encontraron strings con comillas mixtas")
        
        # Verificar template literals problemáticos
        print("\n🔍 Verificando template literals...")
        template_literals = re.findall(r'`[^`]*`', content)
        print(f"📊 Template literals encontrados: {len(template_literals)}")
        
        # Verificar template literals con caracteres especiales
        problematic_templates = []
        for i, template in enumerate(template_literals):
            if "'" in template or '"' in template:
                problematic_templates.append((i, template))
        
        if problematic_templates:
            print(f"⚠️ Encontrados {len(problematic_templates)} template literals problemáticos:")
            for i, template in problematic_templates[:5]:
                print(f"   - Template {i}: {template[:100]}...")
        else:
            print("✅ No se encontraron template literals problemáticos")
        
        # Verificar funciones que se exponen globalmente
        print("\n🔍 Verificando funciones globales...")
        global_functions = re.findall(r'window\.(\w+)\s*=', content)
        print(f"📊 Funciones expuestas globalmente: {len(global_functions)}")
        for func in global_functions[:10]:
            print(f"   - {func}")
        
        # Verificar funciones que pueden estar causando problemas
        print("\n🔍 Verificando funciones específicas...")
        functions_to_check = [
            'mostrarTerminosDisponibles',
            'realizarBusquedaPersonalizada',
            'realizarBusquedaAutomatica',
            'obtenerTerminosSeleccionados',
            'seleccionarTodosTerminos',
            'deseleccionarTodosTerminos'
        ]
        
        for func in functions_to_check:
            if func in content:
                print(f"✅ Función {func} encontrada")
            else:
                print(f"❌ Función {func} NO encontrada")
        
        # Verificar líneas específicas donde puede estar el problema
        print("\n🔍 Verificando líneas específicas...")
        lines = content.split('\n')
        
        # Buscar líneas con onclick que puedan tener problemas
        onclick_lines = []
        for i, line in enumerate(lines, 1):
            if 'onclick=' in line:
                onclick_lines.append((i, line.strip()))
        
        print(f"📊 Líneas con onclick encontradas: {len(onclick_lines)}")
        
        for line_num, line in onclick_lines[:5]:
            print(f"   - Línea {line_num}: {line[:100]}...")
        
        # Verificar si hay líneas que terminen abruptamente
        print("\n🔍 Verificando líneas que terminan abruptamente...")
        incomplete_lines = []
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().endswith(';') and not line.strip().endswith('{') and not line.strip().endswith('}') and not line.strip().endswith(')') and not line.strip().endswith(']'):
                # Verificar si es una línea de función o declaración
                if not re.match(r'^(function|const|let|var|if|for|while|switch|try|catch|finally|class|export|import)', line.strip()):
                    incomplete_lines.append((i, line.strip()))
        
        if incomplete_lines:
            print(f"⚠️ Encontradas {len(incomplete_lines)} líneas que pueden estar incompletas:")
            for line_num, line in incomplete_lines[:5]:
                print(f"   - Línea {line_num}: {line}")
        else:
            print("✅ No se encontraron líneas incompletas")
        
        # Crear una versión limpia del archivo
        print("\n🔧 Creando versión limpia...")
        
        # Remover BOM si existe
        if content.startswith('\ufeff'):
            content = content[1:]
            print("✅ BOM removido")
        
        # Limpiar espacios al inicio
        content = content.lstrip()
        print("✅ Espacios al inicio removidos")
        
        # Escribir versión limpia
        clean_file = js_file + '.clean'
        with open(clean_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Versión limpia creada: {clean_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    verificar_js_completo() 