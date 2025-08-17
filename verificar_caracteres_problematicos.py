#!/usr/bin/env python3
"""
Script para verificar caracteres problemáticos en el archivo HTML
"""

import os
import re

def verificar_caracteres_problematicos():
    """Verifica caracteres problemáticos en el archivo HTML"""
    
    print("🔍 VERIFICACIÓN DE CARACTERES PROBLEMÁTICOS")
    print("=" * 50)
    
    html_file = "templates/professional.html"
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Tamaño del archivo: {len(content)} caracteres")
        
        # Verificar caracteres de control
        control_chars = []
        for i, char in enumerate(content):
            if ord(char) < 32 and char not in '\n\r\t':
                control_chars.append((i, char, ord(char)))
        
        if control_chars:
            print(f"⚠️ Encontrados {len(control_chars)} caracteres de control:")
            for pos, char, code in control_chars[:10]:  # Mostrar solo los primeros 10
                print(f"   - Posición {pos}: '{char}' (código {code})")
        else:
            print("✅ No se encontraron caracteres de control problemáticos")
        
        # Verificar caracteres especiales al inicio
        print("\n🔍 Verificando inicio del archivo...")
        first_chars = content[:500]
        print(f"📋 Primeros 500 caracteres:")
        print(f"'{first_chars}'")
        
        # Verificar si hay caracteres invisibles al inicio
        if content.startswith(' '):
            print("⚠️ El archivo comienza con espacios")
        elif content.startswith('\t'):
            print("⚠️ El archivo comienza con tabulaciones")
        elif content.startswith('\n'):
            print("⚠️ El archivo comienza con saltos de línea")
        elif content.startswith('\ufeff'):
            print("⚠️ El archivo tiene BOM UTF-8")
        else:
            print("✅ El archivo comienza correctamente")
        
        # Verificar que comience con DOCTYPE
        if content.strip().startswith('<!DOCTYPE html>'):
            print("✅ El archivo comienza correctamente con DOCTYPE")
        else:
            print("❌ El archivo NO comienza con DOCTYPE")
            print(f"   Comienza con: '{content[:100]}'")
        
        # Verificar scripts inline problemáticos
        print("\n🔍 Verificando scripts inline...")
        
        # Buscar scripts que puedan tener problemas
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, content, re.DOTALL)
        
        print(f"📊 Scripts inline encontrados: {len(scripts)}")
        
        for i, script_content in enumerate(scripts):
            # Verificar si hay caracteres problemáticos en el script
            problematic_chars = []
            for j, char in enumerate(script_content):
                if ord(char) < 32 and char not in '\n\r\t':
                    problematic_chars.append((j, char, ord(char)))
            
            if problematic_chars:
                print(f"⚠️ Script {i+1} tiene caracteres problemáticos:")
                for pos, char, code in problematic_chars[:5]:
                    print(f"   - Posición {pos}: '{char}' (código {code})")
        
        # Verificar si hay scripts que se abren pero no se cierran
        open_scripts = len(re.findall(r'<script[^>]*>', content))
        close_scripts = len(re.findall(r'</script>', content))
        
        print(f"\n📊 Scripts que abren: {open_scripts}")
        print(f"📊 Scripts que cierran: {close_scripts}")
        
        if open_scripts == close_scripts:
            print("✅ Scripts balanceados correctamente")
        else:
            print(f"❌ Scripts desbalanceados: {open_scripts} abiertos, {close_scripts} cerrados")
        
        # Verificar si hay caracteres especiales en atributos onclick
        print("\n🔍 Verificando atributos onclick...")
        
        onclick_pattern = r'onclick="([^"]*)"'
        onclicks = re.findall(onclick_pattern, content)
        
        print(f"📊 Atributos onclick encontrados: {len(onclicks)}")
        
        for i, onclick_content in enumerate(onclicks):
            # Verificar si hay comillas sin escapar
            if "'" in onclick_content and '"' in onclick_content:
                print(f"⚠️ onclick {i+1} tiene comillas mixtas: {onclick_content[:100]}")
        
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
        clean_file = html_file + '.clean'
        with open(clean_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Versión limpia creada: {clean_file}")
        
        # Verificar que la versión limpia es válida
        with open(clean_file, 'r', encoding='utf-8') as f:
            clean_content = f.read()
        
        if clean_content == content:
            print("✅ Verificación exitosa: la versión limpia es correcta")
        else:
            print("❌ Error en la verificación de la versión limpia")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    verificar_caracteres_problematicos() 