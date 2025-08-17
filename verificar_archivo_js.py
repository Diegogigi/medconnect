#!/usr/bin/env python3
"""
Script para verificar problemas de codificación en el archivo JavaScript
"""

import os
import chardet

def verificar_codificacion_js():
    """Verifica la codificación del archivo JavaScript"""
    
    print("🔍 VERIFICACIÓN DE CODIFICACIÓN JAVASCRIPT")
    print("=" * 50)
    
    js_file = "static/js/professional.js"
    
    if not os.path.exists(js_file):
        print(f"❌ Archivo no encontrado: {js_file}")
        return False
    
    try:
        # Leer el archivo en modo binario para detectar la codificación
        with open(js_file, 'rb') as f:
            raw_data = f.read()
        
        # Detectar la codificación
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        
        print(f"📊 Archivo: {js_file}")
        print(f"📊 Tamaño: {len(raw_data)} bytes")
        print(f"📊 Codificación detectada: {encoding} (confianza: {confidence:.2%})")
        
        # Verificar si hay BOM (Byte Order Mark)
        if raw_data.startswith(b'\xef\xbb\xbf'):
            print("⚠️ Archivo tiene BOM UTF-8")
            has_bom = True
        else:
            print("✅ Archivo no tiene BOM")
            has_bom = False
        
        # Leer el archivo como texto con la codificación detectada
        try:
            with open(js_file, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"✅ Archivo leído correctamente con codificación {encoding}")
        except UnicodeDecodeError as e:
            print(f"❌ Error decodificando con {encoding}: {e}")
            # Intentar con UTF-8
            try:
                with open(js_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print("✅ Archivo leído correctamente con UTF-8")
                encoding = 'utf-8'
            except UnicodeDecodeError as e2:
                print(f"❌ Error también con UTF-8: {e2}")
                return False
        
        # Verificar caracteres problemáticos
        print("\n🔍 Verificando caracteres problemáticos...")
        
        # Buscar caracteres de control
        control_chars = []
        for i, char in enumerate(content):
            if ord(char) < 32 and char not in '\n\r\t':
                control_chars.append((i, char, ord(char)))
        
        if control_chars:
            print(f"⚠️ Encontrados {len(control_chars)} caracteres de control:")
            for pos, char, code in control_chars[:5]:  # Mostrar solo los primeros 5
                print(f"   - Posición {pos}: '{char}' (código {code})")
        else:
            print("✅ No se encontraron caracteres de control problemáticos")
        
        # Verificar caracteres especiales al inicio
        print("\n🔍 Verificando inicio del archivo...")
        first_chars = content[:100]
        print(f"📋 Primeros 100 caracteres:")
        print(f"'{first_chars}'")
        
        # Verificar si hay espacios o caracteres invisibles al inicio
        if content.startswith(' '):
            print("⚠️ El archivo comienza con espacios")
        elif content.startswith('\t'):
            print("⚠️ El archivo comienza con tabulaciones")
        elif content.startswith('\n'):
            print("⚠️ El archivo comienza con saltos de línea")
        else:
            print("✅ El archivo comienza correctamente")
        
        # Verificar sintaxis básica
        print("\n🔍 Verificando sintaxis básica...")
        
        # Contar llaves y paréntesis
        open_braces = content.count('{')
        close_braces = content.count('}')
        open_parens = content.count('(')
        close_parens = content.count(')')
        
        print(f"📊 Llaves: {open_braces} abiertas, {close_braces} cerradas")
        print(f"📊 Paréntesis: {open_parens} abiertos, {close_parens} cerrados")
        
        if open_braces == close_braces:
            print("✅ Llaves balanceadas")
        else:
            print(f"❌ Llaves desbalanceadas: {open_braces - close_braces}")
        
        if open_parens == close_parens:
            print("✅ Paréntesis balanceados")
        else:
            print(f"❌ Paréntesis desbalanceados: {open_parens - close_parens}")
        
        # Verificar que el archivo termina correctamente
        print("\n🔍 Verificando final del archivo...")
        last_chars = content[-50:]
        print(f"📋 Últimos 50 caracteres:")
        print(f"'{last_chars}'")
        
        if content.strip().endswith('}'):
            print("✅ El archivo termina correctamente")
        else:
            print("⚠️ El archivo puede no terminar correctamente")
        
        # Crear una versión limpia si es necesario
        print("\n🔍 Creando versión de respaldo...")
        backup_file = js_file + '.backup'
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Respaldo creado: {backup_file}")
        
        print("\n🎯 VERIFICACIÓN COMPLETADA")
        print("=" * 30)
        
        # Resumen
        issues = []
        if has_bom:
            issues.append("BOM UTF-8")
        if control_chars:
            issues.append(f"{len(control_chars)} caracteres de control")
        if open_braces != close_braces:
            issues.append("llaves desbalanceadas")
        if open_parens != close_parens:
            issues.append("paréntesis desbalanceados")
        
        if issues:
            print(f"⚠️ Se encontraron {len(issues)} posibles problemas:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ No se encontraron problemas evidentes")
            print("✅ El archivo JavaScript debería funcionar correctamente")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error verificando archivo: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    verificar_codificacion_js() 