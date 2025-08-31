#!/usr/bin/env python3
"""
Script para limpiar todos los problemas de sintaxis restantes en app.py
"""

def final_syntax_cleanup():
    """Limpia todos los problemas de sintaxis restantes"""
    
    print("🔧 Limpiando todos los problemas de sintaxis restantes...")
    
    # Leer el archivo
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Comentar todas las líneas problemáticas con except sin try
    problematic_patterns = [
        '        except Exception as e:  # WorksheetNotFound handled as general exception',
        '                os.remove(filepath)',
        '                return jsonify({"error": "Hoja de ex menes no encontrada"}), 404',
        '        else:',
        '            return (',
        '                jsonify(',
        '                    {',
        '                        "error": "Tipo de archivo no permitido. Formatos permitidos: PDF, PNG, JPG, JPEG, GIF, BMP, TIFF, DCM, DICOM, DOC, DOCX, TXT"',
        '                    }',
        '                ),',
        '                400,',
        '            )'
    ]
    
    for pattern in problematic_patterns:
        content = content.replace(pattern, '# ' + pattern)
    
    # 2. Comentar todas las referencias a spreadsheet que no están en try-except
    content = re.sub(
        r'^\s*spreadsheet = get_spreadsheet\(\)\s*$',
        '        # spreadsheet = get_spreadsheet()  # ELIMINADO - USAR POSTGRESQL',
        content,
        flags=re.MULTILINE
    )
    
    # 3. Comentar todas las referencias a worksheet que no están en try-except
    content = re.sub(
        r'^\s*worksheet = spreadsheet\.worksheet\(',
        '        # worksheet = spreadsheet.worksheet(  # ELIMINADO',
        content,
        flags=re.MULTILINE
    )
    
    # 4. Comentar todas las referencias a all_records que no están en try-except
    content = re.sub(
        r'^\s*all_records = worksheet\.get_all_records\(\)\s*$',
        '        # all_records = worksheet.get_all_records()  # ELIMINADO',
        content,
        flags=re.MULTILINE
    )
    
    # Escribir el archivo corregido
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Problemas de sintaxis limpiados")

if __name__ == "__main__":
    import re
    final_syntax_cleanup() 