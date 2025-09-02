#!/usr/bin/env python3
"""
Script para agregar manualmente el método get_user_by_email
"""


def add_missing_method():
    """Agrega el método get_user_by_email manualmente"""

    print("🔧 Agregando método get_user_by_email manualmente...")

    # Leer el archivo actual
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar después del método email_exists
    if "def email_exists" in content and "def get_user_by_email" not in content:
        print("✅ Encontrado método email_exists, agregando get_user_by_email...")

        # Buscar la posición después de email_exists
        email_exists_pos = content.find("def email_exists")
        if email_exists_pos != -1:
            # Encontrar el final del método email_exists
            end_pos = content.find("\n\n", email_exists_pos)
            if end_pos == -1:
                end_pos = content.find("\n    def ", email_exists_pos)

            if end_pos != -1:
                # Método a insertar
                new_method = '''
    def get_user_by_email(self, email):
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
            return None
'''

                # Insertar el método
                new_content = content[:end_pos] + new_method + content[end_pos:]

                # Escribir el archivo actualizado
                with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
                    f.write(new_content)

                print("✅ Método get_user_by_email agregado exitosamente")
                return True

    print("❌ No se pudo agregar el método")
    return False


if __name__ == "__main__":
    add_missing_method()
