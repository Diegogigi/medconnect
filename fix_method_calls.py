#!/usr/bin/env python3
"""
Script para corregir las llamadas a métodos incorrectos
"""

def fix_method_calls():
    """Corrige las llamadas a métodos incorrectos"""
    
    app_py_path = "app.py"
    
    print("🔧 Corrigiendo llamadas a métodos...")
    
    # Leer el archivo
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corregir llamadas a métodos
    corrections = [
        # 1. Corregir buscar_pubmed por buscar_evidencia_unificada
        ('evidencia_cientifica = search_system.buscar_pubmed(', 
         'evidencia_cientifica = search_system.buscar_evidencia_unificada('),
        
        # 2. Corregir generar_recomendaciones_clinicas por procesar_consulta_con_evidencia
        ('analisis_clinico = copilot.generar_recomendaciones_clinicas(', 
         'respuesta_copilot = copilot.procesar_consulta_con_evidencia(consulta, evidencia_cientifica, {"sintomas": analisis_nlp.get("sintomas", [])})\n            analisis_clinico = {\n                "recomendaciones": [respuesta_copilot.respuesta_estructurada.recomendacion],\n                "patologias": [],\n                "escalas": []\n            }'),
        
        # 3. Corregir atributo nombre por texto en sintomas
        ('[s.nombre for s in analisis_completo.consulta_procesada.sintomas]', 
         '[s.texto for s in analisis_completo.consulta_procesada.sintomas]'),
    ]
    
    changes_made = 0
    for old_code, new_code in corrections:
        if old_code in content:
            content = content.replace(old_code, new_code)
            print(f"✅ Corregido: {old_code[:40]}...")
            changes_made += 1
        else:
            print(f"ℹ️ No encontrado: {old_code[:40]}...")
    
    # Escribir el archivo corregido
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {changes_made} correcciones aplicadas")
    return changes_made > 0


def verify_methods_exist():
    """Verifica que los métodos existan"""
    
    print("🔍 Verificando métodos...")
    
    try:
        # Verificar Scientific Search
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced
        search = UnifiedScientificSearchEnhanced()
        
        if hasattr(search, 'buscar_evidencia_unificada'):
            print("✅ buscar_evidencia_unificada existe")
        else:
            print("❌ buscar_evidencia_unificada NO existe")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando Scientific Search: {e}")
        return False
    
    try:
        # Verificar Copilot
        from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced
        copilot = UnifiedCopilotAssistantEnhanced()
        
        if hasattr(copilot, 'procesar_consulta_con_evidencia'):
            print("✅ procesar_consulta_con_evidencia existe")
        else:
            print("❌ procesar_consulta_con_evidencia NO existe")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando Copilot: {e}")
        return False
    
    return True


def test_search():
    """Prueba la búsqueda"""
    
    print("🧪 Probando búsqueda...")
    
    try:
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced
        search = UnifiedScientificSearchEnhanced()
        
        # Probar búsqueda
        resultado = search.buscar_evidencia_unificada("dolor lumbar", max_resultados=3)
        
        if resultado:
            print(f"✅ Búsqueda exitosa: {len(resultado)} resultados")
            return True
        else:
            print("⚠️ Búsqueda no devolvió resultados")
            return True
            
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Corrigiendo llamadas a métodos...")
    
    if fix_method_calls():
        print("✅ Llamadas a métodos corregidas")
        
        if verify_methods_exist():
            print("✅ Métodos verificados")
            
            if test_search():
                print("✅ Búsqueda probada")
                print("\n🎉 ¡Métodos corregidos!")
                print("🚀 El sistema debería funcionar correctamente")
                print("🔍 La búsqueda científica debería funcionar")
            else:
                print("❌ Error en búsqueda")
        else:
            print("❌ Error en verificación de métodos")
    else:
        print("❌ No se pudieron corregir las llamadas")


if __name__ == "__main__":
    main() 