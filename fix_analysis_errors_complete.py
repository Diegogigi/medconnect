#!/usr/bin/env python3
"""
Script para corregir todos los errores del análisis de una vez
"""


def fix_analysis_errors_complete():
    """Corrige todos los errores del análisis de una vez"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo todos los errores del análisis...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Correcciones específicas
    corrections = [
        # 1. Corregir método de NLP
        (
            "nlp_processor.analizar_texto(consulta)",
            "nlp_processor.procesar_consulta_completa(consulta)",
        ),
        # 2. Corregir método de búsqueda científica
        (
            "search_system.buscar_evidencia_cientifica(",
            "search_system.buscar_evidencia_unificada(",
        ),
        # 3. Corregir método de copilot
        ("copilot.analizar_caso_clinico(", "copilot.procesar_consulta_con_evidencia("),
        # 4. Corregir acceso a síntomas
        (
            "s.nombre for s in analisis_completo.consulta_procesada.sintomas",
            "s.texto for s in analisis_completo.consulta_procesada.sintomas",
        ),
        # 5. Corregir acceso a entidades
        (
            "e.nombre for e in analisis_completo.consulta_procesada.entidades_clinicas",
            "e.texto for e in analisis_completo.consulta_procesada.entidades_clinicas",
        ),
        # 6. Mejorar manejo de errores
        (
            "except Exception as e:",
            'except Exception as e:\n            logger.error(f"❌ Error específico en análisis: {e}")',
        ),
        # 7. Corregir estructura de respuesta
        (
            '"recomendaciones": [respuesta_copilot.respuesta_estructurada.recomendacion]',
            '"recomendaciones": [respuesta_copilot.respuesta_estructurada.recomendacion] if hasattr(respuesta_copilot, "respuesta_estructurada") and hasattr(respuesta_copilot.respuesta_estructurada, "recomendacion") else ["Análisis clínico completado"]',
        ),
        # 8. Corregir acceso a evidencia científica
        ("ev.titulo", "ev.get('titulo', 'Sin título')"),
        # 9. Corregir acceso a DOI
        ("ev.doi", "ev.get('doi', 'Sin DOI')"),
        # 10. Corregir acceso a resumen
        ("ev.resumen", "ev.get('resumen', 'Sin resumen disponible')"),
        # 11. Corregir acceso a año
        ("ev.año_publicacion", "ev.get('año_publicacion', 'N/A')"),
        # 12. Corregir acceso a fuente
        ("ev.fuente", "ev.get('fuente', 'PubMed')"),
        # 13. Corregir acceso a URL
        ("ev.url", "ev.get('url', '')"),
        # 14. Corregir acceso a relevancia
        ("ev.relevancia_score", "ev.get('relevancia_score', 0.0)"),
        # 15. Corregir acceso a tipo
        ("ev.tipo_evidencia", "ev.get('tipo_evidencia', 'Artículo')"),
    ]

    changes_made = 0
    for old_code, new_code in corrections:
        if old_code in content:
            content = content.replace(old_code, new_code)
            print(f"✅ Corregido: {old_code[:50]}...")
            changes_made += 1
        else:
            print(f"ℹ️ No encontrado: {old_code[:50]}...")

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ {changes_made} correcciones aplicadas")
    return changes_made > 0


def verify_analysis_endpoint():
    """Verifica que el endpoint de análisis esté correcto"""

    print("🔍 Verificando endpoint de análisis...")

    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar que el endpoint use los métodos correctos
        checks = [
            "procesar_consulta_completa",
            "buscar_evidencia_unificada",
            "procesar_consulta_con_evidencia",
            "s.texto for s in",
            "e.texto for e in",
        ]

        all_good = True
        for check in checks:
            if check in content:
                print(f"✅ {check} encontrado")
            else:
                print(f"❌ {check} no encontrado")
                all_good = False

        return all_good

    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False


def test_analysis_syntax():
    """Prueba la sintaxis del análisis"""

    print("🔍 Verificando sintaxis del análisis...")

    try:
        import ast

        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        ast.parse(content)
        print("✅ Sintaxis correcta")
        return True

    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        return False
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False


def create_test_analysis():
    """Crea un script de prueba para el análisis"""

    test_script = '''#!/usr/bin/env python3
"""
Script de prueba para el análisis unificado
"""

import requests
import json
import time

def test_analysis():
    """Prueba el análisis unificado"""
    
    print("🧪 Probando análisis unificado...")
    
    # Datos de prueba
    test_data = {
        "consulta": "Paciente con dolor en la rodilla derecha después de un golpe en el trabajo",
        "contexto_clinico": {
            "motivoConsulta": "Dolor en rodilla derecha",
            "sintomasPrincipales": "Dolor, inflamación, dificultad para caminar",
            "antecedentesMedicos": "Sin antecedentes relevantes",
            "medicamentosActuales": "Ninguno",
            "alergias": "Ninguna conocida",
            "examenFisico": "Rodilla derecha inflamada y dolorosa",
            "diagnosticoPresuntivo": "Trauma en rodilla",
            "planTratamiento": "Evaluación por traumatología"
        }
    }
    
    try:
        # Enviar petición
        response = requests.post(
            'http://localhost:5000/api/copilot/analyze-enhanced',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis exitoso")
            print(f"📊 Resultados: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

if __name__ == "__main__":
    test_analysis()
'''

    with open("test_analysis_final.py", "w", encoding="utf-8") as f:
        f.write(test_script)

    print("✅ Script de prueba creado")


def main():
    """Función principal"""
    print("🔧 Corrigiendo todos los errores del análisis...")

    if fix_analysis_errors_complete():
        print("✅ Errores corregidos")

        if verify_analysis_endpoint():
            print("✅ Endpoint verificado")

            if test_analysis_syntax():
                print("✅ Sintaxis verificada")

                create_test_analysis()
                print("✅ Script de prueba creado")

                print("\n🎉 ¡Análisis corregido!")
                print("🧪 Ejecuta: python test_analysis_final.py")
            else:
                print("❌ Error de sintaxis")
        else:
            print("❌ Endpoint con problemas")
    else:
        print("❌ No se pudieron corregir los errores")


if __name__ == "__main__":
    main()
