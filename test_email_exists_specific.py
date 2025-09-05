#!/usr/bin/env python3
"""
Script específico para probar el método email_exists
"""

import os
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.getcwd())


def test_email_exists_specific():
    """Prueba específica del método email_exists"""

    print("🧪 Probando método email_exists específicamente...")

    try:
        # Importar el módulo
        from postgresql_db_manager import PostgreSQLDBManager

        # Crear instancia
        print("📝 Creando instancia de PostgreSQLDBManager...")
        db_manager = PostgreSQLDBManager()

        if not db_manager.is_connected():
            print("❌ No se pudo conectar a la base de datos")
            return False

        print("✅ Conectado a la base de datos")

        # Probar con email existente
        existing_email = "paciente@test.com"
        print(f"\n🔍 Probando con email existente: {existing_email}")

        try:
            result = db_manager.email_exists(existing_email)
            print(f"   📊 Resultado: {result}")
            print(f"   📊 Tipo: {type(result)}")
            print(f"   ✅ Debería ser True")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Probar con email nuevo
        new_email = "nuevo_profesional@test.com"
        print(f"\n🔍 Probando con email nuevo: {new_email}")

        try:
            result = db_manager.email_exists(new_email)
            print(f"   📊 Resultado: {result}")
            print(f"   📊 Tipo: {type(result)}")
            print(f"   ✅ Debería ser False")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Probar el método register_user completo
        print(f"\n🧪 Probando registro completo...")

        test_user_data = {
            "email": "test_profesional_debug@test.com",
            "password": "test123",
            "nombre": "Test",
            "apellido": "Debug",
            "tipo_usuario": "profesional",
            "especialidad": "Medicina General",
            "numero_registro": "DEBUG123",
            "anos_experiencia": "5",
            "horario_atencion": "Lunes a Viernes 9-17",
            "telefono": "+56912345678",
            "direccion_consulta": "Calle Debug 123",
        }

        try:
            success, message = db_manager.register_user(test_user_data)
            print(f"   📊 Success: {success}")
            print(f"   📊 Message: {message}")
            print(f"   📊 Success Type: {type(success)}")
            print(f"   📊 Message Type: {type(message)}")
        except Exception as e:
            print(f"   ❌ Error en registro: {e}")

        # Cerrar conexión
        db_manager.close()

        print("\n✅ Pruebas completadas")
        return True

    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


if __name__ == "__main__":
    test_email_exists_specific()
