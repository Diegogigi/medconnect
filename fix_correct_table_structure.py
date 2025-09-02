#!/usr/bin/env python3
"""
Script para corregir las consultas basándose en la estructura real de las tablas
"""


def fix_correct_table_structure():
    """Corrige las consultas basándose en la estructura real"""

    print("🔧 Corrigiendo consultas basándose en la estructura real...")

    # Leer el archivo actual
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Corregir método get_user_by_email
    print("1️⃣ Corrigiendo método get_user_by_email...")

    old_get_user = '''    def get_user_by_email(self, email):
        """Obtener usuario por email desde ambas tablas"""
        try:
            # Buscar en tabla profesionales
            self.cursor.execute("""
                SELECT id, nombre, apellido, 'profesional' as tipo_usuario
                FROM profesionales 
                WHERE nombre = %s AND apellido = %s
            """, (email.split('@')[0], email.split('@')[0]))
            professional = self.cursor.fetchone()
            
            if professional:
                return {
                    'id': professional[0],
                    'nombre': professional[1],
                    'apellido': professional[2],
                    'email': email,
                    'tipo_usuario': 'profesional'
                }
            
            # Buscar en tabla pacientes_profesional
            self.cursor.execute("""
                SELECT paciente_id as id, email, 
                       SPLIT_PART(nombre_completo, ' ', 1) as nombre,
                       SPLIT_PART(nombre_completo, ' ', 2) as apellido,
                       'paciente' as tipo_usuario
                FROM pacientes_profesional 
                WHERE email = %s
            """, (email,))
            patient = self.cursor.fetchone()
            
            if patient:
                return {
                    'id': patient[0],
                    'nombre': patient[1],
                    'apellido': patient[2],
                    'email': patient[3],
                    'tipo_usuario': 'paciente'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario por email: {e}")
            return None'''

    new_get_user = '''    def get_user_by_email(self, email):
        """Obtener usuario por email desde ambas tablas"""
        try:
            # Buscar en tabla pacientes_profesional (tiene email)
            self.cursor.execute("""
                SELECT paciente_id as id, email, 
                       SPLIT_PART(nombre_completo, ' ', 1) as nombre,
                       SPLIT_PART(nombre_completo, ' ', 2) as apellido,
                       'paciente' as tipo_usuario
                FROM pacientes_profesional 
                WHERE email = %s
            """, (email,))
            patient = self.cursor.fetchone()
            
            if patient:
                return {
                    'id': patient[0],
                    'nombre': patient[1],
                    'apellido': patient[2],
                    'email': patient[3],
                    'tipo_usuario': 'paciente'
                }
            
            # Para profesionales, necesitamos crear una tabla de usuarios primero
            # Por ahora, retornar None
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario por email: {e}")
            return None'''

    if old_get_user in content:
        content = content.replace(old_get_user, new_get_user)
        print("   ✅ Método get_user_by_email corregido")

    # 2. Corregir método _register_professional
    print("2️⃣ Corrigiendo método _register_professional...")

    old_register_prof = '''            query = """
                INSERT INTO profesionales 
                (nombre, apellido, numero_registro, especialidad, anos_experiencia,
                 calificacion, direccion_consulta, horario_atencion, idiomas, profesion,
                 institucion, estado, disponible, unnamed_21, unnamed_22)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """'''

    new_register_prof = '''            query = """
                INSERT INTO profesionales 
                (especialidad, numero_colegio, experiencia_anos, horario_trabajo,
                 telefono_consultorio, direccion_consultorio)
                VALUES (%s, %s, %s, %s, %s, %s)
            """'''

    if old_register_prof in content:
        content = content.replace(old_register_prof, new_register_prof)
        print("   ✅ Consulta INSERT de profesionales corregida")

    # 3. Corregir valores en _register_professional
    old_values_prof = """            values = (
                user_data["nombre"],
                user_data["apellido"],
                user_data.get("numero_registro"),
                user_data.get("especialidad"),
                user_data.get("anos_experiencia"),
                user_data.get("calificacion"),
                user_data.get("direccion_consulta"),
                user_data.get("horario_atencion"),
                user_data.get("idiomas"),
                user_data.get("profesion"),
                user_data.get("institucion"),
                "activo",
                True,
                datetime.now(),
                datetime.now()
            )"""

    new_values_prof = """            values = (
                user_data.get("especialidad"),
                user_data.get("numero_registro"),
                user_data.get("anos_experiencia"),
                user_data.get("horario_atencion"),
                user_data.get("telefono"),
                user_data.get("direccion_consulta")
            )"""

    if old_values_prof in content:
        content = content.replace(old_values_prof, new_values_prof)
        print("   ✅ Valores de profesionales corregidos")

    # 4. Corregir método login_user
    print("3️⃣ Corrigiendo método login_user...")

    old_login_prof = '''            query_prof = "SELECT id, nombre, apellido, especialidad, numero_registro FROM profesionales WHERE nombre = %s AND apellido = %s"'''

    new_login_prof = '''            query_prof = "SELECT id, especialidad, numero_colegio FROM profesionales WHERE id = %s"'''

    if old_login_prof in content:
        content = content.replace(old_login_prof, new_login_prof)
        print("   ✅ Consulta de login de profesionales corregida")

    # Escribir el archivo actualizado
    with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("\n✅ Todas las correcciones aplicadas")
    print(
        "📝 NOTA: Para profesionales, necesitarás crear una tabla de usuarios separada"
    )
    print("📝 Por ahora, solo pacientes pueden registrarse e iniciar sesión")

    return True


if __name__ == "__main__":
    fix_correct_table_structure()
