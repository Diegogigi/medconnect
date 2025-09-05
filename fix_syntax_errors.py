#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis en postgresql_db_manager.py
"""

import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_syntax_errors():
    """Corrige errores de sintaxis"""

    print("🔧 Corrigiendo errores de sintaxis...")

    # Leer el archivo actual
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Eliminar código duplicado y mal estructurado
    print("1️⃣ Eliminando código duplicado...")

    # Buscar y eliminar el código duplicado del método register_user
    old_duplicated_code = '''        """Registrar un nuevo usuario en la tabla correspondiente"""
        try:
            tipo_usuario = user_data.get("tipo_usuario", "paciente")
    def _register_professional_profile(self, user_id, user_data):'''

    if old_duplicated_code in content:
        content = content.replace(
            old_duplicated_code,
            """    def _register_professional_profile(self, user_id, user_data):""",
        )
        print("   ✅ Código duplicado eliminado")

    # 2. Eliminar el código duplicado del final
    old_end_duplicated = '''            if tipo_usuario == "paciente":
                return self._register_patient(user_data)
            elif tipo_usuario == "profesional":
                return self._register_professional(user_data)
            else:
                return False, "Tipo de usuario no válido"

        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return False, "Error interno del servidor"'''

    if old_end_duplicated in content:
        content = content.replace(old_end_duplicated, "")
        print("   ✅ Código duplicado del final eliminado")

    # 3. Verificar que el método register_user esté completo
    if "def register_user(self, user_data):" in content:
        print("2️⃣ Verificando método register_user...")

        # Buscar el método register_user completo
        start_pos = content.find("def register_user(self, user_data):")
        if start_pos != -1:
            # Buscar el siguiente método
            next_method_pos = content.find("\n    def ", start_pos)
            if next_method_pos != -1:
                register_method = content[start_pos:next_method_pos]

                # Verificar que tenga try/except
                if (
                    "try:" in register_method
                    and "except Exception as e:" in register_method
                ):
                    print(
                        "   ✅ Método register_user está completo y bien estructurado"
                    )
                else:
                    print("   ❌ Método register_user tiene problemas de estructura")
            else:
                print("   ⚠️ No se pudo verificar la estructura completa")

    # 4. Verificar que no haya bloques try sin except
    print("3️⃣ Verificando bloques try/except...")

    try_count = content.count("try:")
    except_count = content.count("except")

    print(f"   📊 Bloques try: {try_count}")
    print(f"   📊 Bloques except: {except_count}")

    if try_count == except_count:
        print("   ✅ Todos los bloques try tienen su except correspondiente")
    else:
        print("   ❌ Hay bloques try sin except correspondiente")

    # Escribir el archivo corregido
    with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("\n✅ Errores de sintaxis corregidos")
    return True


if __name__ == "__main__":
    fix_syntax_errors()
