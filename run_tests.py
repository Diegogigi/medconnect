#!/usr/bin/env python3
"""
Script para ejecutar todas las pruebas y generar reportes de calidad
"""

import subprocess
import sys
import os
import time
from datetime import datetime
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Ejecuta un comando y reporta el resultado"""
    print(f"\n🔧 {description}...")
    print(f"   Comando: {command}")

    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()

    if result.returncode == 0:
        print(f"   ✅ {description} completado en {end_time - start_time:.2f}s")
        if result.stdout:
            print(f"   📄 Salida: {result.stdout.strip()}")
        return True
    else:
        print(f"   ❌ {description} falló en {end_time - start_time:.2f}s")
        if result.stderr:
            print(f"   📄 Error: {result.stderr.strip()}")
        return False


def run_tests():
    """Ejecuta todas las pruebas"""
    print("🧪 Ejecutando pruebas del sistema RAG...")

    # Crear directorio de reportes
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Ejecutar pytest con cobertura
    pytest_command = f"pytest tests/ -v --cov=. --cov-report=html:reports/coverage_{timestamp} --cov-report=term-missing --cov-report=xml:reports/coverage_{timestamp}.xml"
    pytest_success = run_command(pytest_command, "Pruebas pytest con cobertura")

    # 2. Ejecutar mypy para verificación de tipos
    mypy_command = "mypy . --ignore-missing-imports --html-report reports/mypy_report"
    mypy_success = run_command(mypy_command, "Verificación de tipos con mypy")

    # 3. Ejecutar ruff para linting
    ruff_command = (
        "ruff check . --output-format=json --output-file reports/ruff_report.json"
    )
    ruff_success = run_command(ruff_command, "Linting con ruff")

    # 4. Ejecutar black para formateo
    black_command = "black . --check --diff"
    black_success = run_command(black_command, "Verificación de formateo con black")

    # 5. Ejecutar pruebas específicas de componentes
    component_tests = [
        ("tests/test_parsing_apa_ranking.py", "Pruebas de parsing, APA y ranking"),
        ("tests/test_citation_assignment.py", "Pruebas de asignación de citas"),
    ]

    component_results = []
    for test_file, description in component_tests:
        if Path(test_file).exists():
            test_command = f"pytest {test_file} -v"
            success = run_command(test_command, description)
            component_results.append((description, success))
        else:
            print(f"   ⚠️ Archivo de prueba no encontrado: {test_file}")
            component_results.append((description, False))

    # 6. Generar reporte de métricas
    metrics_command = "python -c \"from metrics_system import metrics_collector; print('Métricas del sistema:', metrics_collector.generate_report())\""
    metrics_success = run_command(metrics_command, "Generación de métricas")

    # 7. Generar reporte final
    generate_final_report(
        pytest_success,
        mypy_success,
        ruff_success,
        black_success,
        component_results,
        timestamp,
    )

    return all(
        [pytest_success, mypy_success, ruff_success, black_success]
        + [r[1] for r in component_results]
    )


def generate_final_report(
    pytest_success,
    mypy_success,
    ruff_success,
    black_success,
    component_results,
    timestamp,
):
    """Genera reporte final de calidad"""
    report_file = f"reports/quality_report_{timestamp}.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# 📊 Reporte de Calidad del Sistema RAG\n\n")
        f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## 🧪 Resultados de Pruebas\n\n")
        f.write("| Componente | Estado |\n")
        f.write("|------------|--------|\n")
        f.write(
            f"| Pytest con cobertura | {'✅ PASÓ' if pytest_success else '❌ FALLÓ'} |\n"
        )
        f.write(
            f"| Verificación de tipos (mypy) | {'✅ PASÓ' if mypy_success else '❌ FALLÓ'} |\n"
        )
        f.write(f"| Linting (ruff) | {'✅ PASÓ' if ruff_success else '❌ FALLÓ'} |\n")
        f.write(
            f"| Formateo (black) | {'✅ PASÓ' if black_success else '❌ FALLÓ'} |\n"
        )

        for description, success in component_results:
            status = "✅ PASÓ" if success else "❌ FALLÓ"
            f.write(f"| {description} | {status} |\n")

        f.write("\n## 📈 Métricas de Calidad\n\n")

        # Calcular métricas
        total_tests = 1 + 1 + 1 + 1 + len(component_results)
        passed_tests = sum(
            [pytest_success, mypy_success, ruff_success, black_success]
            + [r[1] for r in component_results]
        )

        coverage_percentage = (passed_tests / total_tests) * 100

        f.write(
            f"- **Cobertura de pruebas:** {coverage_percentage:.1f}% ({passed_tests}/{total_tests})\n"
        )
        f.write(
            f"- **Estado general:** {'✅ EXITOSO' if coverage_percentage >= 80 else '⚠️ REQUIERE ATENCIÓN'}\n"
        )

        f.write("\n## 📁 Archivos Generados\n\n")
        f.write("- `reports/coverage_{timestamp}/` - Reporte de cobertura HTML\n")
        f.write("- `reports/coverage_{timestamp}.xml` - Reporte de cobertura XML\n")
        f.write("- `reports/mypy_report/` - Reporte de verificación de tipos\n")
        f.write("- `reports/ruff_report.json` - Reporte de linting\n")
        f.write(f"- `reports/quality_report_{timestamp}.md` - Este reporte\n")

        f.write("\n## 🎯 Próximos Pasos\n\n")
        if coverage_percentage >= 80:
            f.write("✅ El sistema cumple con los estándares de calidad.\n")
            f.write("🚀 Listo para producción.\n")
        else:
            f.write("⚠️ Se requieren mejoras en la calidad del código.\n")
            f.write("🔧 Revisar y corregir los errores reportados.\n")

    print(f"\n📊 Reporte final generado: {report_file}")


def run_quick_tests():
    """Ejecuta pruebas rápidas para desarrollo"""
    print("⚡ Ejecutando pruebas rápidas...")

    # Solo ejecutar pytest sin cobertura
    pytest_command = "pytest tests/ -v --tb=short"
    success = run_command(pytest_command, "Pruebas pytest rápidas")

    if success:
        print("✅ Pruebas rápidas completadas exitosamente")
    else:
        print("❌ Pruebas rápidas fallaron")

    return success


def run_linting_only():
    """Ejecuta solo linting y formateo"""
    print("🔍 Ejecutando solo linting y formateo...")

    commands = [
        ("mypy . --ignore-missing-imports", "Verificación de tipos"),
        ("ruff check .", "Linting con ruff"),
        ("black . --check", "Verificación de formateo"),
    ]

    results = []
    for command, description in commands:
        success = run_command(command, description)
        results.append(success)

    all_passed = all(results)
    print(
        f"\n📊 Resultado: {'✅ TODOS PASARON' if all_passed else '❌ ALGUNOS FALLARON'}"
    )

    return all_passed


def main():
    """Función principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "quick":
            success = run_quick_tests()
        elif command == "lint":
            success = run_linting_only()
        elif command == "full":
            success = run_tests()
        else:
            print("Uso: python run_tests.py [quick|lint|full]")
            print("  quick: Pruebas rápidas para desarrollo")
            print("  lint: Solo linting y formateo")
            print("  full: Pruebas completas con reportes")
            sys.exit(1)
    else:
        # Por defecto, ejecutar pruebas completas
        success = run_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
