#!/usr/bin/env python3
"""
Script para corregir la consulta de la tabla profesionales
"""


def fix_professional_table():
    """Corrige la consulta de la tabla profesionales"""

    print("🔧 Corrigiendo consulta de tabla profesionales...")

    # Leer el archivo actual
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar la consulta problemática
    old_query = '''            query = """
                INSERT INTO profesionales 
                (email, nombre, apellido, numero_registro, especialidad, anos_experiencia,
                 calificacion, direccion_consulta, horario_atencion, idiomas, profesion,
                 institucion, estado, disponible, unnamed_21, unnamed_22)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """'''

    # Nueva consulta basada en la estructura real de la tabla
    new_query = '''            query = """
                INSERT INTO profesionales 
                (nombre, apellido, numero_registro, especialidad, anos_experiencia,
                 calificacion, direccion_consulta, horario_atencion, idiomas, profesion,
                 institucion, estado, disponible, unnamed_21, unnamed_22)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """'''

    # Reemplazar la consulta
    if old_query in content:
        new_content = content.replace(old_query, new_query)

        # También actualizar los valores
        old_values = """            values = (
                user_data['email'],
                user_data['nombre'],
                user_data['apellido'],
                user_data.get('numero_registro'),
                user_data.get('especialidad'),
                user_data.get('anos_experiencia'),
                user_data.get('calificacion'),
                user_data.get('direccion_consulta'),
                user_data.get('horario_atencion'),
                user_data.get('idiomas'),
                user_data.get('profesion'),
                user_data.get('institucion'),
                'activo',
                True,
                datetime.now(),
                datetime.now()
            )"""

        new_values = """            values = (
                user_data['nombre'],
                user_data['apellido'],
                user_data.get('numero_registro'),
                user_data.get('especialidad'),
                user_data.get('anos_experiencia'),
                user_data.get('calificacion'),
                user_data.get('direccion_consulta'),
                user_data.get('horario_atencion'),
                user_data.get('idiomas'),
                user_data.get('profesion'),
                user_data.get('institucion'),
                'activo',
                True,
                datetime.now()
            )"""

        new_content = new_content.replace(old_values, new_values)

        # Escribir el archivo actualizado
        with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
            f.write(new_content)

        print("✅ Consulta de tabla profesionales corregida")
        print("   📝 Removida columna 'email' de la consulta")
        print("   📝 Ajustados los valores correspondientes")
        return True

    print("❌ No se pudo encontrar la consulta para corregir")
    return False


if __name__ == "__main__":
    fix_professional_table()
