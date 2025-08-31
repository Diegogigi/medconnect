#!/usr/bin/env python3
"""
Script para probar Gunicorn localmente con el mismo comando que Railway
"""
import os
import subprocess
import time
import requests
import threading


def test_gunicorn_local():
    """Prueba Gunicorn localmente con la misma configuración de Railway"""

    print("🧪 Probando Gunicorn localmente...")
    print("🔧 Usando el mismo comando que Railway")

    # Configurar variables de entorno para el test
    os.environ["PORT"] = "8000"
    os.environ["FLASK_ENV"] = "production"
    os.environ["SECRET_KEY"] = "test-secret-key"

    # Comando exacto que usa Railway
    comando = [
        "gunicorn",
        "-k",
        "gthread",
        "-w",
        "2",
        "-b",
        "0.0.0.0:8000",
        "app:app",
        "--timeout",
        "120",
        "--log-level",
        "info",
        "--access-logfile",
        "-",
    ]

    print(f"📋 Comando: {' '.join(comando)}")

    try:
        # Iniciar Gunicorn en background
        print("🚀 Iniciando Gunicorn...")
        process = subprocess.Popen(
            comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Esperar un poco para que inicie
        time.sleep(3)

        # Probar la conexión
        print("🧪 Probando conexión en localhost:8000...")

        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            print(f"✅ Respuesta /health: {response.status_code}")
            print(f"📄 Contenido: {response.text[:100]}...")

        except requests.exceptions.ConnectionError:
            print("❌ No se pudo conectar a localhost:8000")
            print("🔍 Verificando si el proceso está corriendo...")

        except Exception as e:
            print(f"❌ Error en la petición: {e}")

        # Mostrar logs de Gunicorn
        print("\n📋 Logs de Gunicorn (primeros 10 líneas):")
        try:
            stdout, stderr = process.communicate(timeout=2)
            if stdout:
                lines = stdout.split("\n")[:10]
                for line in lines:
                    if line.strip():
                        print(f"  {line}")
            if stderr:
                print("⚠️ Errores:")
                error_lines = stderr.split("\n")[:5]
                for line in error_lines:
                    if line.strip():
                        print(f"  ERROR: {line}")
        except subprocess.TimeoutExpired:
            print("  (Proceso aún corriendo...)")
            process.terminate()

    except FileNotFoundError:
        print("❌ Gunicorn no encontrado")
        print("🔧 Instala con: pip install gunicorn")

    except Exception as e:
        print(f"❌ Error iniciando Gunicorn: {e}")


if __name__ == "__main__":
    test_gunicorn_local()
