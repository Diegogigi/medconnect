#!/usr/bin/env python3
"""
Script para verificar que todas las plantillas HTML existan
"""

import os
import glob


def verificar_plantillas():
    """Verifica que todas las plantillas HTML existan"""

    print("🔍 VERIFICANDO PLANTILLAS HTML")
    print("=" * 50)

    # Directorio de plantillas
    templates_dir = "templates"

    if not os.path.exists(templates_dir):
        print(f"❌ Directorio {templates_dir} no existe")
        return False

    # Plantillas requeridas
    plantillas_requeridas = [
        "index.html",
        "login.html",
        "register.html",
        "professional.html",
        "profile.html",
        "reports.html",
        "patients.html",
        "consultations.html",
        "schedule.html",
    ]

    # Buscar todas las plantillas existentes
    plantillas_existentes = glob.glob(os.path.join(templates_dir, "*.html"))
    plantillas_existentes = [os.path.basename(f) for f in plantillas_existentes]

    print(f"📁 Directorio: {templates_dir}")
    print(f"📄 Plantillas encontradas: {len(plantillas_existentes)}")
    print()

    # Verificar plantillas requeridas
    faltantes = []
    existentes = []

    for plantilla in plantillas_requeridas:
        if plantilla in plantillas_existentes:
            print(f"✅ {plantilla}")
            existentes.append(plantilla)
        else:
            print(f"❌ {plantilla} - FALTANTE")
            faltantes.append(plantilla)

    print()
    print("=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    print(f"✅ Plantillas existentes: {len(existentes)}/{len(plantillas_requeridas)}")
    print(f"❌ Plantillas faltantes: {len(faltantes)}")

    if faltantes:
        print("\n🔧 Plantillas que necesitas crear:")
        for plantilla in faltantes:
            print(f"  - {plantilla}")

    # Mostrar plantillas adicionales
    adicionales = [p for p in plantillas_existentes if p not in plantillas_requeridas]
    if adicionales:
        print(f"\n📋 Plantillas adicionales encontradas:")
        for plantilla in adicionales:
            print(f"  - {plantilla}")

    return len(faltantes) == 0


def verificar_archivos_estaticos():
    """Verifica archivos estáticos importantes"""

    print("\n🔍 VERIFICANDO ARCHIVOS ESTÁTICOS")
    print("=" * 50)

    static_dir = "static"

    if not os.path.exists(static_dir):
        print(f"❌ Directorio {static_dir} no existe")
        return False

    # Archivos estáticos importantes
    archivos_importantes = [
        "css/style.css",
        "js/main.js",
        "images/logo.png",
        "favicon.ico",
    ]

    print(f"📁 Directorio: {static_dir}")
    print()

    faltantes = []
    existentes = []

    for archivo in archivos_importantes:
        ruta_completa = os.path.join(static_dir, archivo)
        if os.path.exists(ruta_completa):
            print(f"✅ {archivo}")
            existentes.append(archivo)
        else:
            print(f"❌ {archivo} - FALTANTE")
            faltantes.append(archivo)

    print()
    print("=" * 50)
    print("📊 RESUMEN ARCHIVOS ESTÁTICOS")
    print("=" * 50)
    print(f"✅ Archivos existentes: {len(existentes)}/{len(archivos_importantes)}")
    print(f"❌ Archivos faltantes: {len(faltantes)}")

    if faltantes:
        print("\n🔧 Archivos que podrías necesitar:")
        for archivo in faltantes:
            print(f"  - {archivo}")

    return len(faltantes) == 0


def main():
    """Función principal"""
    print("🚀 VERIFICADOR DE PLANTILLAS Y ARCHIVOS ESTÁTICOS")
    print("=" * 70)

    plantillas_ok = verificar_plantillas()
    static_ok = verificar_archivos_estaticos()

    print("\n" + "=" * 70)
    print("🎯 RESULTADO FINAL")
    print("=" * 70)

    if plantillas_ok and static_ok:
        print("🎉 ¡Todas las plantillas y archivos estáticos están presentes!")
        print("✅ La aplicación debería funcionar correctamente.")
    elif plantillas_ok:
        print("⚠️ Plantillas OK, pero faltan algunos archivos estáticos.")
        print("🔧 La aplicación funcionará, pero podría faltar estilos o scripts.")
    elif static_ok:
        print("⚠️ Archivos estáticos OK, pero faltan plantillas.")
        print("❌ La aplicación NO funcionará correctamente.")
    else:
        print("❌ Faltan plantillas y archivos estáticos.")
        print("🔧 La aplicación NO funcionará correctamente.")

    print("\n💡 Para crear plantillas faltantes, puedes:")
    print("  1. Copiar plantillas similares existentes")
    print("  2. Crear plantillas básicas con el contenido mínimo")
    print("  3. Usar las plantillas de la versión de Railway")


if __name__ == "__main__":
    main()
