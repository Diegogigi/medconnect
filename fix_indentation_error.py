#!/usr/bin/env python3
"""
Script para corregir el error de indentación
"""

def fix_indentation_error():
    """Corrige el error de indentación"""
    
    app_py_path = "app.py"
    
    print("🔧 Corrigiendo error de indentación...")
    
    # Leer el archivo
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y corregir las líneas problemáticas
    lines = content.split('\n')
    corrected_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Verificar si hay líneas duplicadas o mal indentadas
        if i < len(lines) - 1:
            next_line = lines[i + 1]
            
            # Si hay líneas duplicadas del copilot, eliminar la segunda
            if ('respuesta_copilot = copilot.procesar_consulta_con_evidencia(' in line and 
                'consulta, evidencia=evidencia_cientifica, contexto_nlp=analisis_nlp' in next_line):
                print("✅ Eliminando línea duplicada del copilot")
                corrected_lines.append(line)
                i += 2  # Saltar la línea duplicada
                continue
        
        corrected_lines.append(line)
        i += 1
    
    # Unir las líneas corregidas
    corrected_content = '\n'.join(corrected_lines)
    
    # Escribir el archivo corregido
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(corrected_content)
    
    print("✅ Error de indentación corregido")
    return True


def verify_syntax():
    """Verifica la sintaxis del archivo"""
    
    print("🔍 Verificando sintaxis...")
    
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
        print(f"❌ Error verificando sintaxis: {e}")
        return False


def test_server_start():
    """Prueba que el servidor pueda iniciarse"""
    
    print("🧪 Probando inicio del servidor...")
    
    try:
        # Importar el módulo
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        module = importlib.util.module_from_spec(spec)
        
        # Verificar que las variables estén disponibles
        if hasattr(module, 'app'):
            print("✅ Aplicación Flask disponible")
        else:
            print("❌ Aplicación Flask no disponible")
            return False
        
        print("✅ Servidor puede iniciarse correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error probando servidor: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Corrigiendo error de indentación...")
    
    if fix_indentation_error():
        print("✅ Error de indentación corregido")
        
        if verify_syntax():
            print("✅ Sintaxis verificada")
            
            if test_server_start():
                print("✅ Servidor puede iniciarse")
                print("\n🎉 ¡Error de indentación solucionado!")
                print("🚀 Ahora puedes ejecutar: python app.py")
            else:
                print("❌ Error en inicio del servidor")
        else:
            print("❌ Error de sintaxis")
    else:
        print("❌ No se pudo corregir el error de indentación")


if __name__ == "__main__":
    main()
