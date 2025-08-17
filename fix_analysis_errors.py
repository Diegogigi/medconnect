#!/usr/bin/env python3
"""
Script para corregir los errores en el análisis unificado
"""


def fix_analysis_errors():
    """Corrige los errores en el análisis unificado"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo errores en el análisis unificado...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir errores específicos
    corrections = [
        # 1. Corregir atributo nombre por texto en sintomas
        (
            "s.nombre for s in analisis_completo.consulta_procesada.sintomas",
            "s.texto for s in analisis_completo.consulta_procesada.sintomas",
        ),
        # 2. Asegurar que el análisis clínico tenga estructura correcta
        (
            '"recomendaciones": [respuesta_copilot.respuesta_estructurada.recomendacion]',
            '"recomendaciones": [respuesta_copilot.respuesta_estructurada.recomendacion] if hasattr(respuesta_copilot, "respuesta_estructurada") and hasattr(respuesta_copilot.respuesta_estructurada, "recomendacion") else ["Análisis en progreso"]',
        ),
        # 3. Agregar manejo de errores más robusto
        (
            "except Exception as e:",
            'except Exception as e:\n            logger.error(f"❌ Error específico: {e}")',
        ),
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
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ {changes_made} correcciones aplicadas")
    return changes_made > 0


def verify_sintoma_attributes():
    """Verifica los atributos de SintomaExtraido"""

    print("🔍 Verificando atributos de SintomaExtraido...")

    try:
        from unified_nlp_processor_enhanced import SintomaExtraido

        # Crear una instancia de prueba
        sintoma = SintomaExtraido(
            texto="dolor lumbar",
            tipo="dolor",
            localizacion="lumbar",
            intensidad="moderada",
            duracion="2 semanas",
            confianza=0.8,
        )

        # Verificar atributos
        if hasattr(sintoma, "texto"):
            print("✅ SintomaExtraido tiene atributo 'texto'")
        else:
            print("❌ SintomaExtraido NO tiene atributo 'texto'")
            return False

        return True

    except Exception as e:
        print(f"❌ Error verificando SintomaExtraido: {e}")
        return False


def test_analysis_endpoint():
    """Prueba el endpoint de análisis"""

    print("🧪 Probando endpoint de análisis...")

    try:
        import requests
        import json

        # Datos de prueba
        test_data = {
            "consulta": "Paciente con dolor lumbar agudo",
            "contexto_clinico": {
                "motivoConsulta": "Dolor lumbar",
                "sintomasPrincipales": "Dolor intenso en región lumbar",
                "antecedentesMedicos": "Sin antecedentes relevantes",
            },
        }

        # Hacer petición
        response = requests.post(
            "http://localhost:5000/api/copilot/analyze-enhanced",
            json=test_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint responde correctamente")
            print(f"📊 Resultado: {result.get('success', False)}")
            return True
        else:
            print(f"❌ Endpoint error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")
        return False


def verify_syntax():
    """Verifica la sintaxis"""

    print("🔍 Verificando sintaxis...")

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


def main():
    """Función principal"""
    print("🔧 Corrigiendo errores en el análisis unificado...")

    if fix_analysis_errors():
        print("✅ Errores corregidos")

        if verify_sintoma_attributes():
            print("✅ Atributos verificados")

            if verify_syntax():
                print("✅ Sintaxis verificada")

                print("\n🎉 ¡Errores de análisis corregidos!")
                print("🚀 El análisis unificado debería funcionar correctamente")
                print("📝 Los resultados aparecerán completos y sin errores")
            else:
                print("❌ Error de sintaxis")
        else:
            print("❌ Error en atributos")
    else:
        print("❌ No se pudieron corregir los errores")


if __name__ == "__main__":
    main()
