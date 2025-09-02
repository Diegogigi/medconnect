#!/usr/bin/env python3
"""
Script para corregir la consulta de login
"""


def fix_login_query():
    """Corrige la consulta de login"""

    print("🔧 Corrigiendo consulta de login...")

    # Leer el archivo actual
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar la consulta problemática de profesionales
    old_query_prof = '''            query_prof = "SELECT id, nombre, apellido, email, especialidad, numero_registro FROM profesionales WHERE email = %s"'''

    # Nueva consulta sin email
    new_query_prof = '''            query_prof = "SELECT id, nombre, apellido, especialidad, numero_registro FROM profesionales WHERE nombre = %s AND apellido = %s"'''

    # Reemplazar la consulta
    if old_query_prof in content:
        new_content = content.replace(old_query_prof, new_query_prof)

        # También actualizar la ejecución de la consulta
        old_execute = """            self.cursor.execute(query_prof, (email,))"""
        new_execute = """            # Buscar por nombre y apellido (ya que no hay email)
            nombre = email.split('@')[0] if '@' in email else email
            self.cursor.execute(query_prof, (nombre, nombre))"""

        new_content = new_content.replace(old_execute, new_execute)

        # Actualizar el procesamiento del resultado
        old_result = """                return {
                    'id': profesional[0],
                    'nombre': profesional[1],
                    'apellido': profesional[2],
                    'email': profesional[3],
                    'tipo_usuario': 'profesional',
                    'especialidad': profesional[4],
                    'numero_registro': profesional[5]
                }"""

        new_result = """                return {
                    'id': profesional[0],
                    'nombre': profesional[1],
                    'apellido': profesional[2],
                    'email': email,  # Usar el email original
                    'tipo_usuario': 'profesional',
                    'especialidad': profesional[3],
                    'numero_registro': profesional[4]
                }"""

        new_content = new_content.replace(old_result, new_result)

        # Escribir el archivo actualizado
        with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ Consulta de login corregida")
        print("   📝 Ajustada consulta de profesionales")
        print("   📝 Actualizado procesamiento de resultados")
        return True

    print("❌ No se pudo encontrar la consulta de login para corregir")
    return False


if __name__ == "__main__":
    fix_login_query()
