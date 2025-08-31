#!/usr/bin/env python3
"""
Script para eliminar la instancia global de AuthManager
"""


def fix_auth_global_instance():
    """Elimina la instancia global de AuthManager"""

    print("🔧 Eliminando instancia global de AuthManager...")

    # Leer el archivo auth_manager.py
    with open("auth_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y eliminar la instancia global
    old_global = """
# Crear instancia global
try:
    auth_manager = AuthManager()
    logger.info("✅ AuthManager inicializado correctamente")
except Exception as e:
    logger.error(f"❌ Error inicializando AuthManager: {e}")
    auth_manager = None"""

    new_global = """
# No crear instancia global - se crea en app.py cuando sea necesario"""

    # Reemplazar en el contenido
    if old_global in content:
        content = content.replace(old_global, new_global)

        # Escribir el archivo actualizado
        with open("auth_manager.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Instancia global de AuthManager eliminada")
        print("🔧 Ahora solo se crea una instancia en app.py")
    else:
        print("❌ No se encontró la instancia global")


if __name__ == "__main__":
    fix_auth_global_instance()
