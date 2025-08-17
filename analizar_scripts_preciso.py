#!/usr/bin/env python3
"""
Script preciso para analizar el problema de scripts
"""

def analizar_scripts_preciso():
    """Analiza el problema de scripts de manera más precisa"""
    
    print("🔍 ANÁLISIS PRECISO DE SCRIPTS")
    print("=" * 50)
    
    html_file = "templates/professional.html"
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Tamaño del archivo: {len(content)} caracteres")
        
        # Buscar todos los scripts de manera más precisa
        script_opens = []
        script_closes = []
        
        # Buscar aperturas de script
        import re
        open_pattern = r'<script[^>]*>'
        close_pattern = r'</script>'
        
        opens = re.finditer(open_pattern, content)
        closes = re.finditer(close_pattern, content)
        
        for match in opens:
            script_opens.append((match.start(), match.group()))
        
        for match in closes:
            script_closes.append((match.start(), match.group()))
        
        print(f"📊 Scripts que abren: {len(script_opens)}")
        print(f"📊 Scripts que cierran: {len(script_closes)}")
        
        # Mostrar todos los scripts
        print("\n📋 Scripts que abren:")
        for pos, script in script_opens:
            # Encontrar la línea
            line_num = content[:pos].count('\n') + 1
            print(f"   Posición {pos}, Línea ~{line_num}: {script}")
        
        print("\n📋 Scripts que cierran:")
        for pos, script in script_closes:
            # Encontrar la línea
            line_num = content[:pos].count('\n') + 1
            print(f"   Posición {pos}, Línea ~{line_num}: {script}")
        
        # Verificar si hay scripts que se abren y cierran en la misma línea
        print("\n🔍 Verificando scripts que se abren y cierran en la misma línea...")
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '<script' in line and '</script>' in line:
                print(f"   Línea {i}: Script que se abre y cierra en la misma línea")
                print(f"      Contenido: {line.strip()}")
        
        # Verificar si hay scripts que no se cierran
        print("\n🔍 Verificando scripts que no se cierran...")
        
        # Buscar scripts que se abren pero no se cierran en la misma línea
        for i, line in enumerate(lines, 1):
            if '<script' in line and '</script>' not in line:
                print(f"   Línea {i}: Script que se abre pero no se cierra en la misma línea")
                print(f"      Contenido: {line.strip()}")
        
        # Verificar si hay cierres sin apertura
        print("\n🔍 Verificando cierres sin apertura...")
        
        for i, line in enumerate(lines, 1):
            if '</script>' in line and '<script' not in line:
                print(f"   Línea {i}: Cierre de script sin apertura en la misma línea")
                print(f"      Contenido: {line.strip()}")
        
        # Contar scripts que se abren y cierran en la misma línea
        self_closing = 0
        for line in lines:
            if '<script' in line and '</script>' in line:
                self_closing += 1
        
        print(f"\n📊 Scripts que se abren y cierran en la misma línea: {self_closing}")
        
        # Contar scripts que se abren pero no se cierran en la misma línea
        open_only = 0
        for line in lines:
            if '<script' in line and '</script>' not in line:
                open_only += 1
        
        print(f"📊 Scripts que se abren pero no se cierran en la misma línea: {open_only}")
        
        # Contar cierres sin apertura en la misma línea
        close_only = 0
        for line in lines:
            if '</script>' in line and '<script' not in line:
                close_only += 1
        
        print(f"📊 Cierres sin apertura en la misma línea: {close_only}")
        
        # Verificar balance
        total_opens = len(script_opens)
        total_closes = len(script_closes)
        
        print(f"\n📊 Balance final:")
        print(f"   Total aperturas: {total_opens}")
        print(f"   Total cierres: {total_closes}")
        print(f"   Diferencia: {total_opens - total_closes}")
        
        if total_opens == total_closes:
            print("✅ Scripts perfectamente balanceados")
        elif total_opens > total_closes:
            print(f"❌ Faltan {total_opens - total_closes} cierres de script")
        else:
            print(f"❌ Hay {total_closes - total_opens} cierres de script sin apertura")
        
        return total_opens == total_closes
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    analizar_scripts_preciso() 