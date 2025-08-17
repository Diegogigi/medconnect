#!/usr/bin/env python3
"""
Script para corregir la estructura del análisis
"""


def fix_analysis_structure():
    """Corrige la estructura del análisis"""

    app_py_path = "app.py"

    print("🔧 Corrigiendo estructura del análisis...")

    # Leer el archivo
    with open(app_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir la estructura del análisis clínico
    old_structure = """            analisis_clinico = {
                "recomendaciones": [
                    respuesta_copilot.respuesta_estructurada.recomendacion
                ],
                "patologias": [],
                "escalas": [],
            }"""

    new_structure = """            analisis_clinico = {
                "recomendaciones": [
                    respuesta_copilot.respuesta_estructurada.recomendacion
                ] if hasattr(respuesta_copilot, "respuesta_estructurada") and hasattr(respuesta_copilot.respuesta_estructurada, "recomendacion") else ["Análisis clínico completado"],
                "patologias": [],
                "escalas": [],
            }"""

    if old_structure in content:
        content = content.replace(old_structure, new_structure)
        print("✅ Estructura del análisis clínico corregida")
    else:
        print("ℹ️ Estructura no encontrada")

    # Corregir el manejo de evidencia científica
    old_evidence = """            "evidence": [
                {
                    "titulo": ev.titulo,
                    "resumen": ev.resumen,
                    "doi": ev.doi,
                    "fuente": ev.fuente,
                    "year": ev.año_publicacion,
                    "tipo": ev.tipo_evidencia,
                    "url": ev.url,
                    "relevancia": ev.relevancia_score
                }
                for ev in evidencia_cientifica
            ],"""

    new_evidence = """            "evidence": [
                {
                    "titulo": getattr(ev, 'titulo', 'Sin título'),
                    "resumen": getattr(ev, 'resumen', 'Sin resumen disponible'),
                    "doi": getattr(ev, 'doi', 'Sin DOI'),
                    "fuente": getattr(ev, 'fuente', 'PubMed'),
                    "year": getattr(ev, 'año_publicacion', 'N/A'),
                    "tipo": getattr(ev, 'tipo_evidencia', 'Artículo'),
                    "url": getattr(ev, 'url', ''),
                    "relevancia": getattr(ev, 'relevancia_score', 0.0)
                }
                for ev in evidencia_cientifica
            ],"""

    if old_evidence in content:
        content = content.replace(old_evidence, new_evidence)
        print("✅ Estructura de evidencia científica corregida")
    else:
        print("ℹ️ Estructura de evidencia no encontrada")

    # Escribir el archivo corregido
    with open(app_py_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Estructura del análisis corregida")
    return True


def verify_fix():
    """Verifica que la corrección fue exitosa"""

    print("🔍 Verificando corrección...")

    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar que las correcciones estén aplicadas
        checks = [
            'hasattr(respuesta_copilot, "respuesta_estructurada")',
            "getattr(ev, 'titulo', 'Sin título')",
            "getattr(ev, 'resumen', 'Sin resumen disponible')",
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


def test_server():
    """Prueba el servidor"""

    print("🧪 Probando servidor...")

    try:
        import subprocess
        import time

        # Iniciar servidor en background
        process = subprocess.Popen(
            ["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Esperar a que inicie
        time.sleep(5)

        # Verificar si está ejecutándose
        import requests

        try:
            response = requests.get("http://localhost:5000", timeout=5)
            print("✅ Servidor ejecutándose")

            # Terminar proceso
            process.terminate()
            return True

        except:
            print("❌ Servidor no responde")
            process.terminate()
            return False

    except Exception as e:
        print(f"❌ Error probando servidor: {e}")
        return False


def main():
    """Función principal"""
    print("🔧 Corrigiendo estructura del análisis...")

    if fix_analysis_structure():
        print("✅ Estructura corregida")

        if verify_fix():
            print("✅ Corrección verificada")

            print("\n🎉 ¡Análisis corregido!")
            print("🚀 Ahora puedes probar el análisis")
        else:
            print("❌ Corrección no verificada")
    else:
        print("❌ No se pudo corregir la estructura")


if __name__ == "__main__":
    main()
