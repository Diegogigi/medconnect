#!/usr/bin/env python3
"""
Script para simular exactamente lo que hace el navegador y encontrar el error
"""

import requests
import re

def simular_navegador_error():
    """Simula exactamente lo que hace el navegador"""
    
    print("🌐 SIMULACIÓN DEL NAVEGADOR")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 1. Simular login
        print("1. 🔐 Simulando login...")
        session = requests.Session()
        
        login_data = {
            'email': 'giselle.arratia@gmail.com',
            'password': 'Gigi2025'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code == 302:
            print("✅ Login exitoso")
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            return False
        
        # 2. Obtener la página professional
        print("\n2. 📄 Obteniendo página professional...")
        professional_response = session.get(f"{base_url}/professional")
        
        if professional_response.status_code == 200:
            print("✅ Página professional obtenida")
            html_content = professional_response.text
        else:
            print(f"❌ Error obteniendo página: {professional_response.status_code}")
            return False
        
        # 3. Extraer el contenido del script professional.js
        print("\n3. 📜 Extrayendo contenido del script professional.js...")
        
        # Buscar la referencia al script
        script_pattern = r'<script src="[^"]*professional\.js[^"]*"></script>'
        script_matches = re.findall(script_pattern, html_content)
        
        if script_matches:
            print(f"✅ Encontradas {len(script_matches)} referencias al script")
            for match in script_matches:
                print(f"   - {match}")
        else:
            print("❌ No se encontraron referencias al script")
            return False
        
        # 4. Obtener el archivo JavaScript directamente
        print("\n4. 📜 Obteniendo archivo JavaScript...")
        js_response = session.get(f"{base_url}/static/js/professional.js")
        
        if js_response.status_code == 200:
            js_content = js_response.text
            print(f"✅ Archivo JavaScript obtenido: {len(js_content)} caracteres")
        else:
            print(f"❌ Error obteniendo JavaScript: {js_response.status_code}")
            return False
        
        # 5. Simular la ejecución del JavaScript
        print("\n5. 🔍 Analizando JavaScript para errores...")
        
        # Buscar líneas problemáticas
        lines = js_content.split('\n')
        
        # Buscar líneas con template literals que contengan caracteres especiales
        problematic_lines = []
        for i, line in enumerate(lines, 1):
            if '`' in line and ('"' in line or "'" in line):
                problematic_lines.append((i, line.strip()))
        
        print(f"📊 Líneas con template literals y comillas: {len(problematic_lines)}")
        
        for line_num, line in problematic_lines[:10]:
            print(f"   - Línea {line_num}: {line[:100]}...")
        
        # 6. Buscar específicamente las líneas con onclick que pueden causar problemas
        print("\n6. 🔍 Buscando líneas con onclick problemáticas...")
        
        onclick_lines = []
        for i, line in enumerate(lines, 1):
            if 'onclick=' in line and '`' in line:
                onclick_lines.append((i, line.strip()))
        
        print(f"📊 Líneas con onclick y template literals: {len(onclick_lines)}")
        
        for line_num, line in onclick_lines[:5]:
            print(f"   - Línea {line_num}: {line[:100]}...")
        
        # 7. Buscar líneas específicas de mostrarTerminosDisponibles
        print("\n7. 🔍 Buscando función mostrarTerminosDisponibles...")
        
        mostrar_terminos_lines = []
        for i, line in enumerate(lines, 1):
            if 'mostrarTerminosDisponibles' in line and '`' in line:
                mostrar_terminos_lines.append((i, line.strip()))
        
        print(f"📊 Líneas de mostrarTerminosDisponibles con template literals: {len(mostrar_terminos_lines)}")
        
        for line_num, line in mostrar_terminos_lines[:5]:
            print(f"   - Línea {line_num}: {line[:100]}...")
        
        # 8. Buscar líneas específicas de realizarBusquedaPersonalizada
        print("\n8. 🔍 Buscando función realizarBusquedaPersonalizada...")
        
        realizar_busqueda_lines = []
        for i, line in enumerate(lines, 1):
            if 'realizarBusquedaPersonalizada' in line and '`' in line:
                realizar_busqueda_lines.append((i, line.strip()))
        
        print(f"📊 Líneas de realizarBusquedaPersonalizada con template literals: {len(realizar_busqueda_lines)}")
        
        for line_num, line in realizar_busqueda_lines[:5]:
            print(f"   - Línea {line_num}: {line[:100]}...")
        
        # 9. Verificar si hay caracteres especiales en las líneas problemáticas
        print("\n9. 🔍 Verificando caracteres especiales...")
        
        special_chars = []
        for i, line in enumerate(lines, 1):
            if any(char in line for char in ['"', "'", '`', '\\']):
                # Contar caracteres especiales
                char_count = sum(1 for char in line if char in ['"', "'", '`', '\\'])
                if char_count > 5:  # Si hay muchos caracteres especiales
                    special_chars.append((i, line.strip(), char_count))
        
        print(f"📊 Líneas con muchos caracteres especiales: {len(special_chars)}")
        
        for line_num, line, count in special_chars[:5]:
            print(f"   - Línea {line_num} ({count} caracteres especiales): {line[:100]}...")
        
        # 10. Crear un archivo de prueba con las líneas problemáticas
        print("\n10. 📝 Creando archivo de prueba...")
        
        test_file = "test_js_problematic_lines.js"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("// Archivo de prueba con líneas problemáticas\n")
            f.write("// Líneas con template literals y comillas:\n")
            for line_num, line in problematic_lines[:10]:
                f.write(f"// Línea {line_num}: {line}\n")
            f.write("\n// Líneas con onclick problemáticas:\n")
            for line_num, line in onclick_lines[:5]:
                f.write(f"// Línea {line_num}: {line}\n")
        
        print(f"✅ Archivo de prueba creado: {test_file}")
        
        print("\n🎯 ANÁLISIS COMPLETADO")
        print("=" * 30)
        print("✅ Se encontraron posibles líneas problemáticas")
        print("✅ Se creó un archivo de prueba para análisis")
        print("⚠️ El problema puede estar en template literals con comillas mixtas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la simulación: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    simular_navegador_error() 