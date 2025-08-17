#!/usr/bin/env python3
"""
Script para verificar problemas en el archivo HTML professional.html
"""

import os
import chardet

def verificar_html_professional():
    """Verifica problemas en el archivo HTML professional.html"""
    
    print("🔍 VERIFICACIÓN DE HTML PROFESSIONAL")
    print("=" * 50)
    
    html_file = "templates/professional.html"
    
    if not os.path.exists(html_file):
        print(f"❌ Archivo no encontrado: {html_file}")
        return False
    
    try:
        # Leer el archivo en modo binario para detectar la codificación
        with open(html_file, 'rb') as f:
            raw_data = f.read()
        
        # Detectar la codificación
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        
        print(f"📊 Archivo: {html_file}")
        print(f"📊 Tamaño: {len(raw_data)} bytes")
        print(f"📊 Codificación detectada: {encoding} (confianza: {confidence:.2%})")
        
        # Verificar si hay BOM (Byte Order Mark)
        if raw_data.startswith(b'\xef\xbb\xbf'):
            print("⚠️ Archivo tiene BOM UTF-8")
            has_bom = True
        else:
            print("✅ Archivo no tiene BOM")
            has_bom = False
        
        # Leer el archivo como texto
        try:
            with open(html_file, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"✅ Archivo leído correctamente con codificación {encoding}")
        except UnicodeDecodeError as e:
            print(f"❌ Error decodificando con {encoding}: {e}")
            # Intentar con UTF-8
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
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
        first_chars = content[:200]
        print(f"📋 Primeros 200 caracteres:")
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
        
        # Verificar que comience con DOCTYPE
        if content.strip().startswith('<!DOCTYPE html>'):
            print("✅ El archivo comienza correctamente con DOCTYPE")
        else:
            print("❌ El archivo NO comienza con DOCTYPE")
            print(f"   Comienza con: '{content[:50]}'")
        
        # Verificar scripts inline
        print("\n🔍 Verificando scripts inline...")
        
        script_tags = content.count('<script>')
        script_src_tags = content.count('<script src=')
        script_closing_tags = content.count('</script>')
        
        print(f"📊 Scripts inline: {script_tags}")
        print(f"📊 Scripts con src: {script_src_tags}")
        print(f"📊 Tags de cierre de script: {script_closing_tags}")
        
        if script_tags == script_closing_tags:
            print("✅ Scripts balanceados correctamente")
        else:
            print(f"❌ Scripts desbalanceados: {script_tags} abiertos, {script_closing_tags} cerrados")
        
        # Verificar que el archivo termina correctamente
        print("\n🔍 Verificando final del archivo...")
        last_chars = content[-100:]
        print(f"📋 Últimos 100 caracteres:")
        print(f"'{last_chars}'")
        
        if content.strip().endswith('</html>'):
            print("✅ El archivo termina correctamente con </html>")
        else:
            print("⚠️ El archivo puede no terminar correctamente")
        
        # Crear una versión limpia si es necesario
        print("\n🔍 Creando versión de respaldo...")
        backup_file = html_file + '.backup'
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
        if script_tags != script_closing_tags:
            issues.append("scripts desbalanceados")
        if not content.strip().startswith('<!DOCTYPE html>'):
            issues.append("no comienza con DOCTYPE")
        
        if issues:
            print(f"⚠️ Se encontraron {len(issues)} posibles problemas:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ No se encontraron problemas evidentes")
            print("✅ El archivo HTML debería funcionar correctamente")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Error verificando archivo: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    verificar_html_professional() 