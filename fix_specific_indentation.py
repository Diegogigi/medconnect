#!/usr/bin/env python3
"""
Script para corregir específicamente las líneas problemáticas
"""

def fix_specific_indentation():
    """Corrige específicamente las líneas problemáticas"""
    
    app_py_path = "app.py"
    
    print("🔧 Corrigiendo líneas problemáticas...")
    
    # Leer el archivo
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y eliminar las líneas problemáticas
    lines = content.split('\n')
    corrected_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Eliminar líneas sueltas que causan error de indentación
        if (line.strip() == 'consulta, evidencia=evidencia_cientifica, contexto_nlp=analisis_nlp' or
            line.strip() == ')'):
            print(f"✅ Eliminando línea problemática: {line.strip()}")
            i += 1
            continue
        
        corrected_lines.append(line)
        i += 1
    
    # Unir las líneas corregidas
    corrected_content = '\n'.join(corrected_lines)
    
    # Escribir el archivo corregido
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(corrected_content)
    
    print("✅ Líneas problemáticas corregidas")
    return True


def verify_fix():
    """Verifica que el error esté corregido"""
    
    print("🔍 Verificando corrección...")
    
    try:
        import ast
        with open("app.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar sintaxis
        ast.parse(content)
        print("✅ Sintaxis correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        return False
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Corrigiendo líneas problemáticas...")
    
    if fix_specific_indentation():
        print("✅ Líneas corregidas")
        
        if verify_fix():
            print("✅ Verificación exitosa")
            print("\n🎉 ¡Error de indentación solucionado!")
            print("🚀 Ahora puedes ejecutar: python app.py")
        else:
            print("❌ Error en verificación")
    else:
        print("❌ No se pudieron corregir las líneas")


if __name__ == "__main__":
    main() 