#!/usr/bin/env python3
"""
Script para corregir el error en unified_nlp_processor_main.py
"""

def fix_nlp_processor_error():
    """Corrige el error en unified_nlp_processor_main.py"""
    
    nlp_file = "unified_nlp_processor_main.py"
    
    print("🔧 Corrigiendo error en unified_nlp_processor_main.py...")
    
    # Leer el archivo
    with open(nlp_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y corregir el error
    old_line = "unified_nlp_enhanced = UnifiedNLPProcessorEnhanced()"
    new_line = "unified_nlp_enhanced = UnifiedNLPProcessor()"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ Error corregido: UnifiedNLPProcessorEnhanced -> UnifiedNLPProcessor")
    else:
        print("⚠️ No se encontró la línea problemática")
    
    # También verificar si hay otros usos de UnifiedNLPProcessorEnhanced
    if "UnifiedNLPProcessorEnhanced" in content:
        print("⚠️ Aún hay referencias a UnifiedNLPProcessorEnhanced")
        # Reemplazar todas las ocurrencias
        content = content.replace("UnifiedNLPProcessorEnhanced", "UnifiedNLPProcessor")
        print("✅ Todas las referencias corregidas")
    
    # Escribir el archivo corregido
    with open(nlp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Archivo corregido")
    return True


def verify_fix():
    """Verifica que el error esté corregido"""
    
    nlp_file = "unified_nlp_processor_main.py"
    
    try:
        # Intentar importar el módulo
        import importlib.util
        spec = importlib.util.spec_from_file_location("unified_nlp_processor_main", nlp_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print("✅ Módulo importado correctamente")
        return True
        
    except NameError as e:
        print(f"❌ Error de nombre: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importando módulo: {e}")
        return False


def test_import():
    """Prueba la importación del módulo"""
    
    print("🧪 Probando importación...")
    
    try:
        from unified_nlp_processor_main import UnifiedNLPProcessor
        print("✅ UnifiedNLPProcessor importado correctamente")
        
        # Crear una instancia
        nlp = UnifiedNLPProcessor()
        print("✅ Instancia creada correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importación: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Corrigiendo error en unified_nlp_processor_main.py...")
    
    if fix_nlp_processor_error():
        print("✅ Error corregido")
        
        if verify_fix():
            print("✅ Verificación exitosa")
            
            if test_import():
                print("✅ Importación exitosa")
                print("\n🎉 ¡Error solucionado!")
                print("🚀 Ahora puedes ejecutar: python app.py")
            else:
                print("❌ Error en importación")
        else:
            print("❌ Verificación falló")
    else:
        print("❌ No se pudo corregir el error")


if __name__ == "__main__":
    main() 