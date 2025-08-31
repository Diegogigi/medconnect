#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar los endpoints principales de la aplicación
"""

import requests
import json
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5000"


def test_login():
    """Probar login"""
    logger.info("🧪 Probando login...")

    try:
        response = requests.post(
            f"{BASE_URL}/login",
            data={"email": "diego.castro.lagos@gmail.com", "password": "password123"},
            allow_redirects=False,
        )

        if response.status_code == 302:
            logger.info("✅ Login exitoso (redirección)")
            return True
        else:
            logger.error(f"❌ Login fallido: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error en login: {e}")
        return False


def test_get_atenciones(session):
    """Probar endpoint de atenciones"""
    logger.info("🧪 Probando endpoint de atenciones...")

    try:
        response = session.get(f"{BASE_URL}/api/get-atenciones")

        if response.status_code == 200:
            data = response.json()
            logger.info(
                f"✅ Atenciones obtenidas: {len(data.get('atenciones', []))} registros"
            )
            return True
        else:
            logger.error(f"❌ Error obteniendo atenciones: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error en atenciones: {e}")
        return False


def test_get_patients(session):
    """Probar endpoint de pacientes"""
    logger.info("🧪 Probando endpoint de pacientes...")

    try:
        response = session.get(f"{BASE_URL}/api/professional/patients")

        if response.status_code == 200:
            data = response.json()
            logger.info(
                f"✅ Pacientes obtenidos: {len(data.get('pacientes', []))} registros"
            )
            return True
        else:
            logger.error(f"❌ Error obteniendo pacientes: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error en pacientes: {e}")
        return False


def test_get_schedule(session):
    """Probar endpoint de agenda"""
    logger.info("🧪 Probando endpoint de agenda...")

    try:
        fecha = time.strftime("%Y-%m-%d")
        response = session.get(
            f"{BASE_URL}/api/professional/schedule?fecha={fecha}&vista=diaria"
        )

        if response.status_code == 200:
            data = response.json()
            logger.info(
                f"✅ Agenda obtenida: {len(data.get('citas_del_dia', []))} citas"
            )
            return True
        else:
            logger.error(f"❌ Error obteniendo agenda: {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ Error en agenda: {e}")
        return False


def main():
    """Función principal"""
    logger.info("🚀 Iniciando pruebas de endpoints...")

    # Crear sesión
    session = requests.Session()

    # Probar login
    login_ok = test_login()

    if login_ok:
        # Probar endpoints autenticados
        atenciones_ok = test_get_atenciones(session)
        patients_ok = test_get_patients(session)
        schedule_ok = test_get_schedule(session)

        # Resumen
        logger.info("📊 Resumen de pruebas:")
        logger.info(f"   Login: {'✅ OK' if login_ok else '❌ Error'}")
        logger.info(f"   Atenciones: {'✅ OK' if atenciones_ok else '❌ Error'}")
        logger.info(f"   Pacientes: {'✅ OK' if patients_ok else '❌ Error'}")
        logger.info(f"   Agenda: {'✅ OK' if schedule_ok else '❌ Error'}")

        if all([login_ok, atenciones_ok, patients_ok, schedule_ok]):
            logger.info("🎉 Todas las pruebas pasaron exitosamente")
            logger.info("💡 La aplicación está funcionando correctamente")
        else:
            logger.warning("⚠️ Algunas pruebas fallaron")
    else:
        logger.error("❌ No se pudo hacer login, no se pueden probar los endpoints")


if __name__ == "__main__":
    main()
