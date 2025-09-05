#!/usr/bin/env python3
"""
Script para corregir completamente el método get_user_by_email duplicado
"""


def fix_duplicated_methods():
    """Corrige completamente el método get_user_by_email duplicado"""

    print("🔧 Corrigiendo método get_user_by_email duplicado...")

    # Leer el archivo actual
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar el método get_user_by_email incorrecto
    old_method = '''    def get_user_by_email(self, email):
        """Obtener usuario por email desde ambas tablas"""
        try:
            # Buscar en tabla profesionales
            self.cursor.execute(
                """
                SELECT id, nombre, apellido, 'profesional' as tipo_usuario
                FROM profesionales 
                WHERE nombre = %s AND apellido = %s
            """,
                (email.split("@")[0], email.split("@")[0]),
            )
            professional = self.cursor.fetchone()

            if professional:
                return {
                    "id": professional[0],
                    "nombre": professional[1],
                    "apellido": professional[2],
                    "email": email,
                    "tipo_usuario": "profesional",
                }

            # Buscar en tabla pacientes_profesional
            self.cursor.execute(
                """
                SELECT paciente_id as id, email, 
                       SPLIT_PART(nombre_completo, ' ', 1) as nombre,
                       SPLIT_PART(nombre_completo, ' ', 2) as apellido,
                       'paciente' as tipo_usuario
                FROM pacientes_profesional 
                WHERE email = %s
            """,
                (email,),
            )
            patient = self.cursor.fetchone()

            if patient:
                return {
                    "id": patient[0],
                    "nombre": patient[1],
                    "apellido": patient[2],
                    "email": patient[3],
                    "tipo_usuario": "paciente",
                }

            return None

        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario por email: {e}")
            return None'''

    new_method = '''    def get_user_by_email(self, email):
        """Obtener usuario por email desde la tabla usuarios"""
        try:
            # Buscar en tabla usuarios
            self.cursor.execute("""
                SELECT id, email, nombre, apellido, tipo_usuario
                FROM usuarios 
                WHERE email = %s AND activo = TRUE
            """, (email,))
            user = self.cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'email': user[1],
                    'nombre': user[2],
                    'apellido': user[3],
                    'tipo_usuario': user[4]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuario por email: {e}")
            return None'''

    if old_method in content:
        content = content.replace(old_method, new_method)
        print("✅ Método get_user_by_email corregido")
    else:
        print("❌ No se encontró el método duplicado para corregir")

    # Escribir el archivo corregido
    with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Archivo corregido")
    return True


if __name__ == "__main__":
    fix_duplicated_methods()
