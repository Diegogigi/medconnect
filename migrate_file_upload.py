#!/usr/bin/env python3
"""
Script para migrar la función de subida de archivos a PostgreSQL
"""


def migrate_file_upload():
    """Migra la función de subida de archivos a PostgreSQL"""

    print("🔧 Migrando función de subida de archivos a PostgreSQL...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Migrar upload_exam_file
    old_upload = """@app.route("/api/exams/<exam_id>/upload", methods=["POST"])
@login_required
def upload_exam_file(exam_id):
    try:
        if "file" not in request.files:
            return jsonify({"error":"No se envió archivo"}), 400
        f = request.files["file"]
        if not f.filename or not allowed_file(f.filename):
            return jsonify({"error":"Tipo de archivo no permitido"}), 400
        safe_name = f"{uuid.uuid4().hex}_{f.filename}"
        dest = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
        f.save(dest)
        file_url = f"/static/uploads/{safe_name}"
        logger.info(f"[UPLOAD] exam:{exam_id} file:{safe_name}")
        # Aquí podrías asociarlo en DB si está disponible
        return jsonify({"success":True, "file_url":file_url})
    except Exception as e:
        logger.error(f"upload_exam_file error: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500"""

    new_upload = '''@app.route("/api/exams/<exam_id>/upload", methods=["POST"])
@login_required
def upload_exam_file(exam_id):
    try:
        if "file" not in request.files:
            return jsonify({"error":"No se envió archivo"}), 400
        f = request.files["file"]
        if not f.filename or not allowed_file(f.filename):
            return jsonify({"error":"Tipo de archivo no permitido"}), 400
        
        # Generar nombre seguro para el archivo
        safe_name = f"{uuid.uuid4().hex}_{f.filename}"
        dest = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
        f.save(dest)
        file_url = f"/static/uploads/{safe_name}"
        
        # Asociar archivo al examen en PostgreSQL si está disponible
        if postgres_db and postgres_db.is_connected():
            try:
                # Verificar que el examen existe y pertenece al usuario
                user_id = session.get("user_id")
                check_query = """
                    SELECT id FROM examenes 
                    WHERE id = %s AND patient_id = %s
                """
                exam_exists = postgres_db.execute_query(check_query, (exam_id, user_id))
                
                if not exam_exists:
                    # Si el examen no existe, eliminamos el archivo subido
                    os.remove(dest)
                    return jsonify({"error":"Examen no encontrado o no autorizado"}), 404
                
                # Actualizar el examen con la URL del archivo
                update_query = """
                    UPDATE examenes 
                    SET file_url = %s, updated_at = NOW()
                    WHERE id = %s
                """
                postgres_db.execute_query(update_query, (file_url, exam_id))
                
                logger.info(f"[DB] Archivo asociado al examen {exam_id}: {safe_name}")
                
            except Exception as db_error:
                logger.error(f"[DB] Error asociando archivo: {db_error}")
                # No fallamos la subida si hay error en DB, solo log
        else:
            logger.warning("PostgreSQL no disponible - archivo subido sin asociar a DB")
        
        logger.info(f"[UPLOAD] exam:{exam_id} file:{safe_name}")
        return jsonify({"success":True, "file_url":file_url})
        
    except Exception as e:
        logger.error(f"upload_exam_file error: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500'''

    content = content.replace(old_upload, new_upload)

    # Escribir el archivo migrado
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Función de subida de archivos migrada a PostgreSQL")
    print("📝 Cambios realizados:")
    print(
        "   - upload_exam_file() - Ahora asocia archivos a registros en tabla 'examenes'"
    )
    print("   - Verifica que el examen pertenece al usuario")
    print("   - Actualiza el campo file_url en la base de datos")


if __name__ == "__main__":
    migrate_file_upload()
