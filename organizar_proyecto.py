#!/usr/bin/env python3
"""
Script para organizar y limpiar el proyecto MedConnect
Elimina archivos duplicados y organiza la estructura
"""

import os
import shutil
from datetime import datetime


def crear_backup_seguro():
    """Crea un backup de seguridad antes de limpiar"""

    backup_dir = f"backup_antes_limpieza_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"📦 Creando backup de seguridad en: {backup_dir}")

    try:
        os.makedirs(backup_dir, exist_ok=True)

        # Archivos importantes a respaldar
        archivos_importantes = [
            "app.py",
            "app_offline.py",
            "app_auditado.py",
            "config.py",
            "auth_manager.py",
            "requirements.txt",
            "templates/",
            "static/",
            "backend/",
        ]

        for archivo in archivos_importantes:
            if os.path.exists(archivo):
                if os.path.isdir(archivo):
                    shutil.copytree(archivo, os.path.join(backup_dir, archivo))
                else:
                    shutil.copy2(archivo, backup_dir)
                print(f"  ✅ {archivo}")

        print(f"✅ Backup creado exitosamente en: {backup_dir}")
        return backup_dir

    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return None


def eliminar_archivos_duplicados():
    """Elimina archivos duplicados y scripts temporales"""

    print("\n🧹 Eliminando archivos duplicados y temporales...")

    # Patrones de archivos a eliminar
    patrones_eliminar = [
        # Scripts de ejecución duplicados
        "run_local.py",
        "run_offline.py",
        # Scripts de configuración duplicados
        "setup_desarrollo_local.py",
        "config_desarrollo_offline.py",
        "config_local.py",
        # Scripts de diagnóstico
        "diagnostico_local.py",
        "diagnostico_produccion.py",
        "diagnostico_ia.py",
        # Scripts de prueba
        "probar_agenda.py",
        "run_tests.py",
        # Scripts de limpieza
        "clean_*.py",
        "fix_*.py",
        "final_*.py",
        # Backups antiguos
        "app_backup*.py",
        "temp_*.py",
        "*_backup_*.py",
        # Scripts de análisis
        "analizar_*.py",
        "check_*.py",
        "debug_*.py",
        # Scripts de integración
        "integrate_*.py",
        "create_*.py",
        "apply_*.py",
        # Archivos temporales
        "*.tmp",
        "*.temp",
        "*.log",
        "*.bak",
    ]

    eliminados = 0

    for patron in patrones_eliminar:
        if "*" in patron:
            # Buscar archivos con patrón
            import glob

            archivos = glob.glob(patron)
            for archivo in archivos:
                try:
                    if os.path.exists(archivo):
                        os.remove(archivo)
                        print(f"  🗑️ {archivo}")
                        eliminados += 1
                except Exception as e:
                    print(f"  ⚠️ No se pudo eliminar {archivo}: {e}")
        else:
            # Archivo específico
            try:
                if os.path.exists(patron):
                    os.remove(patron)
                    print(f"  🗑️ {patron}")
                    eliminados += 1
            except Exception as e:
                print(f"  ⚠️ No se pudo eliminar {patron}: {e}")

    print(f"✅ {eliminados} archivos eliminados")


def crear_estructura_organizada():
    """Crea una estructura de directorios organizada"""

    print("\n📁 Creando estructura organizada...")

    directorios = ["scripts/", "docs/", "backups/", "tests/"]

    for directorio in directorios:
        try:
            os.makedirs(directorio, exist_ok=True)
            print(f"  ✅ {directorio}")
        except Exception as e:
            print(f"  ⚠️ No se pudo crear {directorio}: {e}")


def mover_archivos_organizados():
    """Mueve archivos a directorios organizados"""

    print("\n📦 Moviendo archivos a directorios organizados...")

    # Mover documentación
    docs_files = ["*.md", "*.txt"]

    for patron in docs_files:
        import glob

        archivos = glob.glob(patron)
        for archivo in archivos:
            try:
                if os.path.exists(archivo) and not archivo.startswith("README"):
                    shutil.move(archivo, "docs/")
                    print(f"  📄 {archivo} → docs/")
            except Exception as e:
                print(f"  ⚠️ No se pudo mover {archivo}: {e}")

    # Mover scripts de utilidad
    scripts_files = ["verificar_*.py", "verificacion_*.py", "organizar_*.py"]

    for patron in scripts_files:
        import glob

        archivos = glob.glob(patron)
        for archivo in archivos:
            try:
                if os.path.exists(archivo):
                    shutil.move(archivo, "scripts/")
                    print(f"  🔧 {archivo} → scripts/")
            except Exception as e:
                print(f"  ⚠️ No se pudo mover {archivo}: {e}")


def crear_readme_organizado():
    """Crea un README organizado con instrucciones claras"""

    print("\n📝 Creando README organizado...")

    readme_content = """# 🏥 MedConnect - Sistema de Gestión Médica

## 🚀 Inicio Rápido

### Ejecutar la Aplicación

```bash
# Modo recomendado (offline con datos simulados)
python run_medconnect.py offline

# Modo auditado (completamente verificado)
python run_medconnect.py auditado

# Modo local (con base de datos Railway)
python run_medconnect.py local

# Verificar funcionalidades
python run_medconnect.py verify
```

### Credenciales de Prueba

- **Email:** diego.castro.lagos@gmail.com
- **Password:** password123

- **Email:** rodrigoandressilvabreve@gmail.com  
- **Password:** password123

## 📋 Funcionalidades

- ✅ Dashboard profesional completo
- ✅ Gestión de pacientes
- ✅ Historial de atenciones médicas
- ✅ Sistema de citas/agenda
- ✅ Informes y estadísticas
- ✅ Sesiones de tratamiento
- ✅ Recordatorios
- ✅ Chat con asistente IA
- ✅ APIs completas

## 📊 Datos Simulados

- 👥 3 pacientes
- 🏥 3 atenciones médicas
- 📅 3 citas programadas
- 📋 1 sesión de tratamiento
- 🔔 2 recordatorios

## 🛠️ Desarrollo

### Estructura del Proyecto

```
medconnect/
├── app_auditado.py          # Aplicación auditada (RECOMENDADA)
├── app_offline.py           # Aplicación offline
├── app.py                   # Aplicación principal
├── run_medconnect.py        # Script maestro de ejecución
├── templates/               # Plantillas HTML
├── static/                  # Archivos estáticos
├── backend/                 # Backend y base de datos
├── scripts/                 # Scripts de utilidad
├── docs/                    # Documentación
└── backups/                 # Backups de seguridad
```

### Scripts de Utilidad

```bash
# Verificar plantillas
python scripts/verificar_plantillas.py

# Verificación completa
python scripts/verificacion_completa.py

# Organizar proyecto
python scripts/organizar_proyecto.py
```

## 🌐 URLs Importantes

- **Aplicación:** http://localhost:8000
- **Login:** http://localhost:8000/login
- **Health Check:** http://localhost:8000/api/health

## 📝 Notas

- Usa `offline` o `auditado` para desarrollo local
- Los datos son simulados pero realistas
- Todas las funcionalidades están disponibles
- No requiere conexión a base de datos externa

## 🆘 Soporte

Si encuentras problemas:

1. Ejecuta: `python run_medconnect.py verify`
2. Revisa los logs en la consola
3. Verifica que todas las dependencias estén instaladas
"""

    try:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("  ✅ README.md creado")
    except Exception as e:
        print(f"  ⚠️ No se pudo crear README.md: {e}")


def main():
    """Función principal"""

    print("🏥 MEDCONNECT - ORGANIZADOR DE PROYECTO")
    print("=" * 50)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Confirmar antes de proceder
    respuesta = input("\n¿Deseas proceder con la organización? (s/N): ").lower()
    if respuesta not in ["s", "si", "sí", "y", "yes"]:
        print("❌ Operación cancelada")
        return

    # 1. Crear backup
    backup_dir = crear_backup_seguro()
    if not backup_dir:
        print("❌ No se pudo crear backup. Abortando...")
        return

    # 2. Eliminar duplicados
    eliminar_archivos_duplicados()

    # 3. Crear estructura
    crear_estructura_organizada()

    # 4. Mover archivos
    mover_archivos_organizados()

    # 5. Crear README
    crear_readme_organizado()

    print("\n" + "=" * 50)
    print("🎉 ORGANIZACIÓN COMPLETADA")
    print("=" * 50)
    print(f"📦 Backup creado en: {backup_dir}")
    print("✅ Archivos duplicados eliminados")
    print("✅ Estructura organizada creada")
    print("✅ README actualizado")
    print("\n🚀 Ahora puedes usar: python run_medconnect.py offline")


if __name__ == "__main__":
    main()
