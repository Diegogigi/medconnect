#!/usr/bin/env python3
"""
Script de verificación completa de MedConnect
Prueba todas las funcionalidades de la aplicación
"""

import requests
import json
import time
from datetime import datetime


class MedConnectTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_test(self, test_name, success, message="", details=None):
        """Registra el resultado de una prueba"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    📝 {message}")
        if details:
            print(f"    🔍 {details}")

        self.test_results.append(
            {
                "test": test_name,
                "success": success,
                "message": message,
                "details": details,
            }
        )
        print()

    def test_health_check(self):
        """Prueba el health check"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if (
                    data.get("success")
                    and data.get("data", {}).get("status") == "healthy"
                ):
                    self.log_test(
                        "Health Check", True, "Aplicación funcionando correctamente"
                    )
                    return True
                else:
                    self.log_test(
                        "Health Check", False, "Respuesta inválida", str(data)
                    )
                    return False
            else:
                self.log_test(
                    "Health Check", False, f"Status code: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Error de conexión: {e}")
            return False

    def test_login(self):
        """Prueba el sistema de login"""
        try:
            # Probar login con credenciales válidas
            login_data = {
                "email": "diego.castro.lagos@gmail.com",
                "password": "password123",
            }

            response = self.session.post(
                f"{self.base_url}/login", data=login_data, timeout=5
            )

            if response.status_code == 200:
                # Verificar que se redirigió al dashboard
                if "professional" in response.url or "professional" in response.text:
                    self.log_test(
                        "Login Válido", True, "Login exitoso con credenciales correctas"
                    )
                    return True
                else:
                    self.log_test("Login Válido", False, "No se redirigió al dashboard")
                    return False
            else:
                self.log_test(
                    "Login Válido", False, f"Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("Login Válido", False, f"Error: {e}")
            return False

    def test_login_invalid(self):
        """Prueba login con credenciales inválidas"""
        try:
            login_data = {"email": "usuario@inexistente.com", "password": "password123"}

            response = self.session.post(
                f"{self.base_url}/login", data=login_data, timeout=5
            )

            if response.status_code == 200:
                # Debería mostrar error y no redirigir
                if (
                    "error" in response.text.lower()
                    or "incorrecta" in response.text.lower()
                ):
                    self.log_test(
                        "Login Inválido",
                        True,
                        "Manejo correcto de credenciales inválidas",
                    )
                    return True
                else:
                    self.log_test(
                        "Login Inválido",
                        False,
                        "No se mostró error para credenciales inválidas",
                    )
                    return False
            else:
                self.log_test(
                    "Login Inválido", False, f"Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("Login Inválido", False, f"Error: {e}")
            return False

    def test_protected_routes(self):
        """Prueba rutas protegidas sin autenticación"""
        protected_routes = [
            "/professional",
            "/profile",
            "/reports",
            "/patients",
            "/consultations",
            "/schedule",
        ]

        success_count = 0
        for route in protected_routes:
            try:
                response = self.session.get(f"{self.base_url}{route}", timeout=5)
                if response.status_code == 200:
                    # Debería redirigir al login
                    if "login" in response.url or "login" in response.text:
                        self.log_test(
                            f"Ruta Protegida {route}",
                            True,
                            "Redirige correctamente al login",
                        )
                        success_count += 1
                    else:
                        self.log_test(
                            f"Ruta Protegida {route}", False, "No redirige al login"
                        )
                else:
                    self.log_test(
                        f"Ruta Protegida {route}",
                        False,
                        f"Status code: {response.status_code}",
                    )
            except Exception as e:
                self.log_test(f"Ruta Protegida {route}", False, f"Error: {e}")

        return success_count == len(protected_routes)

    def test_api_endpoints(self):
        """Prueba todos los endpoints de API"""
        # Primero hacer login
        login_data = {
            "email": "diego.castro.lagos@gmail.com",
            "password": "password123",
        }
        self.session.post(f"{self.base_url}/login", data=login_data)

        api_endpoints = [
            ("/api/patients", "Pacientes"),
            ("/api/consultations", "Consultas"),
            ("/api/get-atenciones", "Atenciones"),
            ("/api/professional/patients", "Pacientes Profesional"),
            ("/api/professional/schedule", "Agenda Profesional"),
            ("/api/schedule", "Agenda"),
            ("/api/agenda", "Agenda Alternativa"),
            ("/api/citas", "Citas"),
            ("/api/reports", "Informes"),
            ("/api/sessions", "Sesiones"),
            ("/api/reminders", "Recordatorios"),
            ("/api/test-atencion", "Test Atención"),
            ("/api/user/profile", "Perfil Usuario"),
            ("/api/dashboard/stats", "Estadísticas Dashboard"),
        ]

        success_count = 0
        for endpoint, name in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and "data" in data:
                        self.log_test(
                            f"API {name}",
                            True,
                            f"Retorna {data.get('total', 0)} elementos",
                        )
                        success_count += 1
                    else:
                        self.log_test(f"API {name}", False, "Respuesta inválida")
                else:
                    self.log_test(
                        f"API {name}", False, f"Status code: {response.status_code}"
                    )
            except Exception as e:
                self.log_test(f"API {name}", False, f"Error: {e}")

        return success_count == len(api_endpoints)

    def test_copilot_chat(self):
        """Prueba el chat con Copilot"""
        try:
            # Primero hacer login
            login_data = {
                "email": "diego.castro.lagos@gmail.com",
                "password": "password123",
            }
            self.session.post(f"{self.base_url}/login", data=login_data)

            chat_data = {"message": "Hola, ¿cómo estás?"}

            response = self.session.post(
                f"{self.base_url}/api/copilot/chat",
                json=chat_data,
                headers={"Content-Type": "application/json"},
                timeout=5,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "response" in data.get("data", {}):
                    self.log_test(
                        "Chat Copilot", True, "Respuesta generada correctamente"
                    )
                    return True
                else:
                    self.log_test("Chat Copilot", False, "Respuesta inválida")
                    return False
            else:
                self.log_test(
                    "Chat Copilot", False, f"Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("Chat Copilot", False, f"Error: {e}")
            return False

    def test_data_consistency(self):
        """Prueba la consistencia de los datos"""
        try:
            # Primero hacer login
            login_data = {
                "email": "diego.castro.lagos@gmail.com",
                "password": "password123",
            }
            self.session.post(f"{self.base_url}/login", data=login_data)

            # Obtener datos de diferentes endpoints
            patients_response = self.session.get(f"{self.base_url}/api/patients")
            consultations_response = self.session.get(
                f"{self.base_url}/api/consultations"
            )
            schedule_response = self.session.get(f"{self.base_url}/api/schedule")

            if all(
                r.status_code == 200
                for r in [patients_response, consultations_response, schedule_response]
            ):
                patients_data = patients_response.json()
                consultations_data = consultations_response.json()
                schedule_data = schedule_response.json()

                # Verificar que los datos son consistentes
                patients_count = patients_data.get("total", 0)
                consultations_count = consultations_data.get("total", 0)
                schedule_count = schedule_data.get("total", 0)

                if (
                    patients_count > 0
                    and consultations_count > 0
                    and schedule_count > 0
                ):
                    self.log_test(
                        "Consistencia de Datos",
                        True,
                        f"Pacientes: {patients_count}, Consultas: {consultations_count}, Citas: {schedule_count}",
                    )
                    return True
                else:
                    self.log_test(
                        "Consistencia de Datos", False, "Datos vacíos o inconsistentes"
                    )
                    return False
            else:
                self.log_test("Consistencia de Datos", False, "Error obteniendo datos")
                return False

        except Exception as e:
            self.log_test("Consistencia de Datos", False, f"Error: {e}")
            return False

    def test_logout(self):
        """Prueba el logout"""
        try:
            response = self.session.get(f"{self.base_url}/logout", timeout=5)
            if response.status_code == 200:
                # Verificar que se redirigió al login
                if "login" in response.url or "login" in response.text:
                    self.log_test("Logout", True, "Logout exitoso, redirige al login")
                    return True
                else:
                    self.log_test(
                        "Logout", False, "No redirige al login después del logout"
                    )
                    return False
            else:
                self.log_test("Logout", False, f"Status code: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Logout", False, f"Error: {e}")
            return False

    def run_all_tests(self):
        """Ejecuta todas las pruebas"""
        print("🧪 INICIANDO VERIFICACIÓN COMPLETA DE MEDCONNECT")
        print("=" * 70)
        print(f"🌐 URL Base: {self.base_url}")
        print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()

        # Lista de pruebas a ejecutar
        tests = [
            ("Health Check", self.test_health_check),
            ("Login Válido", self.test_login),
            ("Login Inválido", self.test_login_invalid),
            ("Rutas Protegidas", self.test_protected_routes),
            ("Endpoints API", self.test_api_endpoints),
            ("Chat Copilot", self.test_copilot_chat),
            ("Consistencia de Datos", self.test_data_consistency),
            ("Logout", self.test_logout),
        ]

        passed_tests = 0
        total_tests = len(tests)

        for test_name, test_func in tests:
            print(f"🔍 Ejecutando: {test_name}")
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Error inesperado: {e}")
            print("-" * 50)

        # Resumen final
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE VERIFICACIÓN")
        print("=" * 70)
        print(f"✅ Pruebas Exitosas: {passed_tests}/{total_tests}")
        print(f"❌ Pruebas Fallidas: {total_tests - passed_tests}/{total_tests}")
        print(f"📈 Porcentaje de Éxito: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print(
                "\n🎉 ¡TODAS LAS PRUEBAS PASARON! La aplicación está funcionando correctamente."
            )
        elif passed_tests >= total_tests * 0.8:
            print("\n⚠️ La mayoría de las pruebas pasaron. Revisar las fallidas.")
        else:
            print("\n❌ Muchas pruebas fallaron. Revisar la aplicación.")

        print("\n📋 Detalles de las pruebas:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']}: {result['message']}")

        return passed_tests == total_tests


def main():
    """Función principal"""
    print("🚀 Verificador de MedConnect")
    print("Asegúrate de que la aplicación esté ejecutándose en http://localhost:8000")
    print()

    # Esperar un momento para que el usuario lea
    time.sleep(2)

    tester = MedConnectTester()
    success = tester.run_all_tests()

    if success:
        print("\n🎯 La aplicación está lista para usar!")
    else:
        print("\n🔧 Revisa los errores antes de continuar.")


if __name__ == "__main__":
    main()
