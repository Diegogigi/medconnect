@app.route("/api/health", methods=["GET"])
def api_health():
    """Endpoint de health check para Railway"""
    try:
        # Verificar estado de la base de datos
        db_status = "disconnected"
        db_mode = "unknown"
        
        if postgres_db and postgres_db.is_connected():
            db_status = "connected"
            db_mode = "postgresql"
        elif auth_manager and hasattr(auth_manager, 'use_fallback') and auth_manager.use_fallback:
            db_status = "fallback"
            db_mode = "simulated"
        else:
            db_status = "disconnected"
            db_mode = "unknown"
        
        # Información del sistema
        health_data = {
            "status": "healthy" if db_status in ["connected", "fallback"] else "unhealthy",
            "database": db_mode,
            "mode": "production",
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - start_time if 'start_time' in globals() else 0,
            "version": "1.0.0",
            "environment": os.environ.get("FLASK_ENV", "production"),
            "railway": True
        }
        
        status_code = 200 if health_data["status"] == "healthy" else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"❌ Error en health check: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """Endpoint de health check simple para Railway"""
    try:
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500
