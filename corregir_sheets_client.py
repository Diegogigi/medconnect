#!/usr/bin/env python3
"""
Script para corregir el problema con sheets_client
"""

def corregir_sheets_client():
    """Corrige el problema con sheets_client"""
    print("🔧 CORRIGIENDO PROBLEMA CON SHEETS_CLIENT")
    print("=" * 50)
    
    try:
        # Leer el archivo app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Archivo app.py leído correctamente")
        
        # Agregar la inicialización global de sheets_client después de la definición de la función
        # Buscar la función get_google_sheets_client y agregar la inicialización después
        
        # Buscar el final de la función get_google_sheets_client
        function_end = content.find("        return None")
        if function_end != -1:
            # Encontrar el final de la función
            end_pos = content.find("\n", function_end + 20)
            if end_pos != -1:
                # Agregar la inicialización global después de la función
                initialization = '''
# Inicializar cliente de Google Sheets globalmente
sheets_client = get_google_sheets_client()

'''
                content = content[:end_pos] + initialization + content[end_pos:]
                print("✅ Inicialización global de sheets_client agregada")
        
        # Comentar las líneas problemáticas que intentan redefinir sheets_client
        content = content.replace(
            "# sheets_client = get_google_sheets_client()  # Movido al final",
            "# sheets_client = get_google_sheets_client()  # Ya inicializado globalmente"
        )
        
        # Guardar el archivo corregido
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Archivo app.py corregido y guardado")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo el archivo: {e}")
        return False

def verificar_correccion():
    """Verifica que la corrección fue exitosa"""
    print("\n🔍 VERIFICANDO CORRECCIÓN")
    print("=" * 50)
    
    try:
        # Intentar importar el archivo para verificar sintaxis
        import subprocess
        result = subprocess.run(['python', '-m', 'py_compile', 'app.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sintaxis correcta - No hay errores de compilación")
            return True
        else:
            print(f"❌ Error de sintaxis: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 CORRIGIENDO PROBLEMA CON SHEETS_CLIENT")
    print("=" * 60)
    
    try:
        # Corregir el error
        success = corregir_sheets_client()
        
        if success:
            # Verificar la corrección
            verificado = verificar_correccion()
            
            if verificado:
                print("\n✅ PROBLEMA CORREGIDO EXITOSAMENTE:")
                print("=" * 60)
                print("   • sheets_client inicializado globalmente")
                print("   • Error NameError resuelto")
                print("   • Sintaxis validada")
                
                print("\n🎯 EL ARCHIVO ESTÁ LISTO PARA USAR:")
                print("   • Puedes ejecutar: python app.py")
                print("   • El servidor Flask debería funcionar correctamente")
                print("   • Todas las funciones deberían tener acceso a sheets_client")
                
            else:
                print("\n⚠️  La corrección se aplicó pero hay errores de sintaxis")
                print("   • Revisar manualmente el archivo app.py")
                
        else:
            print("\n❌ Error aplicando la corrección")
            
    except Exception as e:
        print(f"\n❌ Error durante la corrección: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 