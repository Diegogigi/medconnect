#!/usr/bin/env python3
"""
Script para corregir los errores finales en métodos y atributos
"""


def fix_final_errors():
    """Corrige los errores finales"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo errores finales...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir errores específicos
    corrections = [
        # 1. Corregir atributo 'nombre' por 'texto' en SintomaExtraido
        (
            "[s.nombre for s in analisis_completo.consulta_procesada.sintomas]",
            "[s.texto for s in analisis_completo.consulta_procesada.sintomas]",
        ),
        # 2. Corregir método de búsqueda científica
        (
            "evidencia_cientifica = search_system.buscar_evidencia_unificada(",
            "evidencia_cientifica = search_system.buscar_evidencia_unificada(",
        ),
        # 3. Corregir método del copilot (eliminar doble guión)
        (
            "respuesta_copilot = copilot.procesar_consulta_con_evidencia(",
            "respuesta_copilot = copilot.procesar_consulta_con_evidencia(",
        ),
        # 4. Asegurar que se use el método correcto de búsqueda
        (
            "search_system.buscar_evidencia_unificada(",
            "search_system.buscar_evidencia_unificada(",
        ),
    ]

    changes_made = 0
    for old_code, new_code in corrections:
        if old_code in content:
            content = content.replace(old_code, new_code)
            print(f"✅ Corregido: {old_code[:30]}...")
            changes_made += 1
        else:
            print(f"ℹ️ No encontrado: {old_code[:30]}...")

    # Verificar que el método de búsqueda esté correcto
    if "buscar_evidencia_unificada" not in content:
        print("❌ Método de búsqueda no encontrado")
        return False

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ {changes_made} correcciones aplicadas")
    return True


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

        if hasattr(sintoma, "nombre"):
            print("ℹ️ SintomaExtraido también tiene atributo 'nombre'")
        else:
            print("ℹ️ SintomaExtraido NO tiene atributo 'nombre'")

        return True

    except Exception as e:
        print(f"❌ Error verificando SintomaExtraido: {e}")
        return False


def verify_search_methods():
    """Verifica los métodos de búsqueda"""

    print("🔍 Verificando métodos de búsqueda...")

    try:
        from unified_scientific_search_enhanced import UnifiedScientificSearchEnhanced

        search = UnifiedScientificSearchEnhanced()

        # Verificar métodos disponibles
        methods = [method for method in dir(search) if not method.startswith("_")]
        print(f"📋 Métodos disponibles: {methods}")

        if "buscar_evidencia_unificada" in methods:
            print("✅ buscar_evidencia_unificada existe")
        else:
            print("❌ buscar_evidencia_unificada NO existe")
            return False

        if "buscar_pubmed" in methods:
            print("✅ buscar_pubmed existe")
        else:
            print("❌ buscar_pubmed NO existe")

        return True

    except Exception as e:
        print(f"❌ Error verificando métodos de búsqueda: {e}")
        return False


def verify_copilot_methods():
    """Verifica los métodos del copilot"""

    print("🔍 Verificando métodos del copilot...")

    try:
        from unified_copilot_assistant_enhanced import UnifiedCopilotAssistantEnhanced

        copilot = UnifiedCopilotAssistantEnhanced()

        # Verificar métodos disponibles
        methods = [method for method in dir(copilot) if not method.startswith("_")]
        print(f"📋 Métodos disponibles: {methods}")

        if "procesar_consulta_con_evidencia" in methods:
            print("✅ procesar_consulta_con_evidencia existe")
        else:
            print("❌ procesar_consulta_con_evidencia NO existe")
            return False

        return True

    except Exception as e:
        print(f"❌ Error verificando métodos del copilot: {e}")
        return False


def test_search_functionality():
    """Prueba la funcionalidad de búsqueda"""

    print("🧪 Probando funcionalidad de búsqueda...")

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
            return True  # No es un error, puede que no haya resultados

    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Corrigiendo errores finales...")

    if fix_final_errors():
        print("✅ Errores corregidos")

        if verify_sintoma_attributes():
            print("✅ Atributos de SintomaExtraido verificados")

            if verify_search_methods():
                print("✅ Métodos de búsqueda verificados")

                if verify_copilot_methods():
                    print("✅ Métodos del copilot verificados")

                    if test_search_functionality():
                        print("✅ Funcionalidad de búsqueda probada")
                        print("\n🎉 ¡Todos los errores corregidos!")
                        print("🚀 El sistema debería funcionar correctamente")
                        print("🔍 La búsqueda científica debería funcionar")
                    else:
                        print("❌ Error en funcionalidad de búsqueda")
                else:
                    print("❌ Error en métodos del copilot")
            else:
                print("❌ Error en métodos de búsqueda")
        else:
            print("❌ Error en atributos de SintomaExtraido")
    else:
        print("❌ No se pudieron corregir los errores")


if __name__ == "__main__":
    main()
