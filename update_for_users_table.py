#!/usr/bin/env python3
"""
Script para actualizar el código para usar la nueva tabla de usuarios
"""


def update_for_users_table():
    """Actualiza el código para usar la nueva tabla de usuarios"""

    print("🔧 Actualizando código para usar la nueva tabla de usuarios...")

    # Leer el archivo actual
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Actualizar método get_user_by_email
    print("1️⃣ Actualizando método get_user_by_email...")

    old_get_user = '''    def get_user_by_email(self, email):
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

    new_get_user = '''    def get_user_by_email(self, email):
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

    if old_get_user in content:
        content = content.replace(old_get_user, new_get_user)
        print("   ✅ Método get_user_by_email actualizado")

    # 2. Actualizar método register_user
    print("2️⃣ Actualizando método register_user...")

    old_register_user = '''    def register_user(self, user_data):
        """Registrar un nuevo usuario en la tabla correspondiente"""
        try:
            tipo_usuario = user_data.get('tipo_usuario', 'paciente')
            
            if tipo_usuario == 'paciente':
                return self._register_patient(user_data)
            elif tipo_usuario == 'profesional':
                return self._register_professional(user_data)
            else:
                return False, "Tipo de usuario no válido"
                
        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            return False, "Error interno del servidor"'''

    new_register_user = '''    def register_user(self, user_data):
        """Registrar un nuevo usuario en la tabla usuarios"""
        try:
            # Verificar si el email ya existe
            if self.email_exists(user_data['email']):
                return False, "Email ya registrado"
            
            # Hashear contraseña
            import bcrypt
            password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insertar en tabla usuarios
            query = """
                INSERT INTO usuarios (email, password_hash, nombre, apellido, tipo_usuario)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """
            
            values = (
                user_data['email'],
                password_hash,
                user_data['nombre'],
                user_data['apellido'],
                user_data['tipo_usuario']
            )
            
            self.cursor.execute(query, values)
            user_id = self.cursor.fetchone()[0]
            
            # Si es profesional, insertar en tabla profesionales
            if user_data['tipo_usuario'] == 'profesional':
                self._register_professional_profile(user_id, user_data)
            # Si es paciente, insertar en tabla pacientes_profesional
            elif user_data['tipo_usuario'] == 'paciente':
                self._register_patient_profile(user_id, user_data)
            
            self.conn.commit()
            
            logger.info(f"✅ Usuario registrado: {user_data['email']}")
            return True, "Usuario registrado exitosamente"
                
        except Exception as e:
            logger.error(f"❌ Error registrando usuario: {e}")
            self.conn.rollback()
            return False, "Error interno del servidor"'''

    if old_register_user in content:
        content = content.replace(old_register_user, new_register_user)
        print("   ✅ Método register_user actualizado")

    # 3. Agregar método _register_professional_profile
    print("3️⃣ Agregando método _register_professional_profile...")

    new_method = '''
    def _register_professional_profile(self, user_id, user_data):
        """Registrar perfil profesional"""
        try:
            query = """
                INSERT INTO profesionales 
                (usuario_id, especialidad, numero_colegio, experiencia_anos, 
                 horario_trabajo, telefono_consultorio, direccion_consultorio)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                user_id,
                user_data.get("especialidad"),
                user_data.get("numero_registro"),
                user_data.get("anos_experiencia"),
                user_data.get("horario_atencion"),
                user_data.get("telefono"),
                user_data.get("direccion_consulta")
            )
            
            self.cursor.execute(query, values)
            logger.info(f"✅ Perfil profesional registrado para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error registrando perfil profesional: {e}")
            raise
    
    def _register_patient_profile(self, user_id, user_data):
        """Registrar perfil de paciente"""
        try:
            # Generar ID único para paciente
            paciente_id = f"PAC_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            query = """
                INSERT INTO pacientes_profesional 
                (paciente_id, nombre_completo, rut, edad, fecha_nacimiento, genero, 
                 telefono, email, direccion, antecedentes_medicos, estado_relacion, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Calcular edad
            edad = None
            if user_data.get('fecha_nacimiento'):
                try:
                    fecha_nac = datetime.strptime(user_data['fecha_nacimiento'], '%Y-%m-%d')
                    edad = (datetime.now() - fecha_nac).days // 365
                except:
                    pass
            
            values = (
                paciente_id,
                f"{user_data['nombre']} {user_data['apellido']}",
                user_data.get('rut'),
                edad,
                user_data.get('fecha_nacimiento'),
                user_data.get('genero'),
                user_data.get('telefono'),
                user_data['email'],
                user_data.get('direccion'),
                user_data.get('antecedentes_medicos'),
                'activo',
                datetime.now()
            )
            
            self.cursor.execute(query, values)
            logger.info(f"✅ Perfil de paciente registrado para usuario {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error registrando perfil de paciente: {e}")
            raise'''

    # Buscar donde insertar el nuevo método
    if "def _register_professional_profile" not in content:
        # Insertar después del método register_user
        register_user_pos = content.find("def register_user")
        if register_user_pos != -1:
            # Encontrar el final del método register_user
            end_pos = content.find("\n\n", register_user_pos)
            if end_pos == -1:
                end_pos = content.find("\n    def ", register_user_pos)

            if end_pos != -1:
                content = content[:end_pos] + new_method + content[end_pos:]
                print("   ✅ Método _register_professional_profile agregado")

    # Escribir el archivo actualizado
    with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("\n✅ Código actualizado para usar la nueva tabla de usuarios")
    print("📝 NOTA: Necesitas ejecutar el script SQL para crear la tabla usuarios")

    return True


if __name__ == "__main__":
    update_for_users_table()
