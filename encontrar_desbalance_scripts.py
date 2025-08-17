#!/usr/bin/env python3
"""
Script para encontrar el desbalance de scripts en professional.html
"""

def encontrar_desbalance_scripts():
    """Encuentra el desbalance de scripts"""
    
    print("🔍 ENCONTRANDO DESBALANCE DE SCRIPTS")
    print("=" * 50)
    
    html_file = "templates/professional.html"
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📊 Total de líneas: {len(lines)}")
        
        # Buscar todas las líneas con script
        script_lines = []
        for i, line in enumerate(lines, 1):
            if '<script' in line:
                script_lines.append((i, line.strip(), 'open'))
            elif '</script>' in line:
                script_lines.append((i, line.strip(), 'close'))
        
        print(f"📊 Total de líneas con script: {len(script_lines)}")
        
        # Mostrar todas las líneas con script
        print("\n📋 Todas las líneas con script:")
        for line_num, line_content, script_type in script_lines:
            print(f"   Línea {line_num} ({script_type}): {line_content}")
        
        # Contar aperturas y cierres
        opens = [line for line in script_lines if line[2] == 'open']
        closes = [line for line in script_lines if line[2] == 'close']
        
        print(f"\n📊 Resumen:")
        print(f"   Scripts que abren: {len(opens)}")
        print(f"   Scripts que cierran: {len(closes)}")
        print(f"   Diferencia: {len(opens) - len(closes)}")
        
        if len(opens) > len(closes):
            print("❌ Faltan cierres de script")
            print("   Scripts que abren sin cerrar:")
            for line_num, line_content, _ in opens[len(closes):]:
                print(f"   - Línea {line_num}: {line_content}")
        elif len(closes) > len(opens):
            print("❌ Hay cierres de script sin apertura")
            print("   Scripts que cierran sin abrir:")
            for line_num, line_content, _ in closes[len(opens):]:
                print(f"   - Línea {line_num}: {line_content}")
        else:
            print("✅ Scripts balanceados correctamente")
        
        # Verificar si hay scripts que se cierran en la misma línea que se abren
        self_closing = []
        for line_num, line_content, script_type in script_lines:
            if script_type == 'open' and '</script>' in line_content:
                self_closing.append((line_num, line_content))
        
        if self_closing:
            print(f"\n📋 Scripts que se abren y cierran en la misma línea ({len(self_closing)}):")
            for line_num, line_content in self_closing:
                print(f"   - Línea {line_num}: {line_content}")
        
        return len(opens) == len(closes)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    encontrar_desbalance_scripts() 