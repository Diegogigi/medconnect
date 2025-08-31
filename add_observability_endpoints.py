#!/usr/bin/env python3
"""
Script para agregar endpoints de observabilidad
"""


def add_observability_endpoints():
    """Agrega endpoints de observabilidad"""

    print("🔧 Agregando endpoints de observabilidad...")

    # Leer el archivo app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar el endpoint /health existente
    health_endpoint = """@app.route("/health")
def health_check():
    try:
        # Verificar AuthManager
        auth_status = "OK" if auth_manager else "ERROR"
        
        # Verificar PostgreSQL
        postgres_status = "OK" if (postgres_db and postgres_db.is_connected()) else "ERROR"
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "auth_manager": auth_status,
            "postgres_connected": postgres_status == "OK",
            "environment": app.config.get("FLASK_ENV", "unknown")
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500"""

    # Nuevo endpoint /ready más completo
    ready_endpoint = '''@app.route("/ready")
def ready_check():
    """Endpoint completo para verificar que la app está lista para recibir tráfico"""
    try:
        checks = {
            "app": "OK",
            "auth_manager": "ERROR",
            "postgres": "ERROR",
            "templates": "ERROR"
        }
        
        # Verificar AuthManager
        if auth_manager:
            checks["auth_manager"] = "OK"
        
        # Verificar PostgreSQL
        if postgres_db and postgres_db.is_connected():
            checks["postgres"] = "OK"
        
        # Verificar templates básicos
        template_files = ["login.html", "index.html"]
        missing_templates = []
        for template in template_files:
            if not os.path.exists(os.path.join("templates", template)):
                missing_templates.append(template)
        
        if not missing_templates:
            checks["templates"] = "OK"
        
        # Determinar estado general
        all_ok = all(status == "OK" for status in checks.values())
        status_code = 200 if all_ok else 503
        
        return jsonify({
            "status": "ready" if all_ok else "not_ready",
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "missing_templates": missing_templates if missing_templates else None
        }), status_code
        
    except Exception as e:
        logger.error(f"Ready check error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/health")
def health_check():
    """Endpoint simple para verificar que la app está viva"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": app.config.get("FLASK_ENV", "unknown")
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500'''

    # Reemplazar el endpoint /health existente
    if health_endpoint in content:
        content = content.replace(health_endpoint, ready_endpoint)

        # Escribir el archivo actualizado
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Endpoints de observabilidad agregados")
        print("🔧 /health - Verificación simple de vida")
        print("🔧 /ready - Verificación completa de disponibilidad")
    else:
        print("❌ No se encontró el endpoint /health existente")


if __name__ == "__main__":
    add_observability_endpoints()
