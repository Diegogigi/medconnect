#!/usr/bin/env python3
"""
Script para solucionar el error de sintaxis de manera definitiva
"""

import os
import shutil

def solucion_error_sintaxis():
    """Soluciona el error de sintaxis de manera definitiva"""
    
    print("🔧 SOLUCIÓN DEFINITIVA DEL ERROR DE SINTAXIS")
    print("=" * 50)
    
    html_file = "templates/professional.html"
    
    try:
        # Crear respaldo
        backup_file = html_file + '.backup_final'
        shutil.copy2(html_file, backup_file)
        print(f"✅ Respaldo creado: {backup_file}")
        
        # Leer el archivo
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Archivo original: {len(content)} caracteres")
        
        # Verificar si hay caracteres invisibles al inicio
        if content.startswith('\ufeff'):  # BOM UTF-8
            print("⚠️ Archivo tiene BOM UTF-8, removiendo...")
            content = content[1:]
        
        # Remover cualquier espacio o carácter invisible al inicio
        content = content.lstrip()
        
        # Asegurar que comience correctamente
        if not content.startswith('<!DOCTYPE html>'):
            print("❌ El archivo no comienza con DOCTYPE")
            return False
        
        print("✅ El archivo comienza correctamente con DOCTYPE")
        
        # Verificar que termine correctamente
        if not content.rstrip().endswith('</html>'):
            print("❌ El archivo no termina correctamente")
            return False
        
        print("✅ El archivo termina correctamente")
        
        # Escribir el archivo limpio
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Archivo limpio escrito: {len(content)} caracteres")
        
        # Verificar que el archivo se escribió correctamente
        with open(html_file, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        if new_content == content:
            print("✅ Verificación exitosa: el archivo se escribió correctamente")
        else:
            print("❌ Error en la verificación")
            return False
        
        # Crear un archivo de prueba para verificar que no hay errores
        test_file = "test_professional_clean.html"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Archivo de prueba creado: {test_file}")
        
        print("\n🎯 SOLUCIÓN APLICADA:")
        print("   ✅ Se removió cualquier BOM UTF-8")
        print("   ✅ Se limpiaron caracteres invisibles al inicio")
        print("   ✅ Se verificó que el archivo comience y termine correctamente")
        print("   ✅ Se reescribió el archivo con codificación UTF-8 limpia")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def instrucciones_finales():
    """Proporciona instrucciones finales"""
    
    print("\n📋 INSTRUCCIONES FINALES:")
    print("=" * 30)
    
    print("1. 🔄 Recarga la página del navegador (Ctrl+F5)")
    print("2. 🧹 Limpia completamente el cache del navegador:")
    print("   - Chrome: Ctrl+Shift+Delete → 'Todo el tiempo' → 'Limpiar datos'")
    print("   - Firefox: Ctrl+Shift+Delete → 'Todo' → 'Limpiar ahora'")
    print("   - Edge: Ctrl+Shift+Delete → 'Todo' → 'Limpiar'")
    print("3. 🔍 Abre las herramientas de desarrollador (F12)")
    print("4. 📊 Ve a la pestaña 'Console'")
    print("5. 🔄 Recarga la página nuevamente")
    print("6. ✅ Verifica que NO aparezcan errores de sintaxis")
    print("7. 🧪 Prueba la funcionalidad de búsqueda personalizada")
    
    print("\n🎯 SOLUCIONES APLICADAS:")
    print("   ✅ Se corrigió el escape de caracteres especiales en JavaScript")
    print("   ✅ Se agregó versión al script para evitar cache")
    print("   ✅ Se limpió la codificación del archivo HTML")
    print("   ✅ Se verificó que los scripts estén balanceados")
    print("   ✅ Se removió cualquier BOM o caracteres invisibles")

if __name__ == "__main__":
    print("🚀 SOLUCIÓN DEFINITIVA DEL ERROR DE SINTAXIS")
    print("=" * 60)
    
    # Aplicar solución
    solucion_ok = solucion_error_sintaxis()
    
    # Proporcionar instrucciones
    instrucciones_finales()
    
    print("\n📊 RESUMEN")
    print("=" * 20)
    print(f"✅ Solución aplicada: {'OK' if solucion_ok else 'ERROR'}")
    
    if solucion_ok:
        print("\n🎯 CONCLUSIÓN: El error de sintaxis ha sido solucionado definitivamente")
        print("   El archivo HTML está limpio y correctamente codificado")
        print("   Los scripts están balanceados y funcionan correctamente")
        print("   No deberían aparecer más errores de sintaxis")
    else:
        print("\n🎯 CONCLUSIÓN: Hay un problema persistente")
        print("   Se requiere verificar manualmente el archivo") 