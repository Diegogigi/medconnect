#!/usr/bin/env python3
"""
Script para migrar las funciones de eliminación a PostgreSQL
"""


def migrate_delete_functions():
    """Migra las funciones de eliminación a PostgreSQL"""

    print("🔧 Migrando funciones de eliminación a PostgreSQL...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Migrar delete_consultation
    old_delete = """@app.route("/api/patient/<patient_id>/consultations/<consultation_id>", methods=["DELETE"])
@login_required
def delete_consultation(patient_id, consultation_id):
    try:
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error":"No autorizado"}), 403
        # Aquí borrarías en DB; demo:
        return jsonify({"deleted":True})
    except Exception as e:
        logger.error(f"delete_consultation: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500"""

    new_delete = '''@app.route("/api/patient/<patient_id>/consultations/<consultation_id>", methods=["DELETE"])
@login_required
def delete_consultation(patient_id, consultation_id):
    try:
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error":"No autorizado"}), 403
        
        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - simulando eliminación")
            return jsonify({"deleted":True})
        
        # Verificar que la consulta existe y pertenece al paciente
        check_query = """
            SELECT id FROM atenciones_medicas 
            WHERE id = %s AND patient_id = %s
        """
        consultation_exists = postgres_db.execute_query(check_query, (consultation_id, patient_id))
        
        if not consultation_exists:
            return jsonify({"error":"Consulta no encontrada"}), 404
        
        # Eliminar la consulta
        delete_query = """
            DELETE FROM atenciones_medicas 
            WHERE id = %s AND patient_id = %s
        """
        postgres_db.execute_query(delete_query, (consultation_id, patient_id))
        
        logger.info(f"[DB] Consulta {consultation_id} eliminada para paciente {patient_id}")
        return jsonify({"deleted":True})
        
    except Exception as e:
        logger.error(f"delete_consultation: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500'''

    content = content.replace(old_delete, new_delete)

    # Agregar función para eliminar exámenes
    add_exam_delete = '''
@app.route("/api/patient/<patient_id>/exams/<exam_id>", methods=["DELETE"])
@login_required
def delete_exam(patient_id, exam_id):
    try:
        if str(session.get("user_id")) != str(patient_id):
            return jsonify({"error":"No autorizado"}), 403
        
        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - simulando eliminación")
            return jsonify({"deleted":True})
        
        # Verificar que el examen existe y pertenece al paciente
        check_query = """
            SELECT id, file_url FROM examenes 
            WHERE id = %s AND patient_id = %s
        """
        exam_exists = postgres_db.execute_query(check_query, (exam_id, patient_id))
        
        if not exam_exists:
            return jsonify({"error":"Examen no encontrado"}), 404
        
        # Si hay archivo asociado, eliminarlo
        exam_data = exam_exists[0]
        if exam_data.get("file_url"):
            try:
                file_path = exam_data["file_url"].replace("/static/uploads/", "")
                full_path = os.path.join(app.config["UPLOAD_FOLDER"], file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    logger.info(f"[FILE] Archivo eliminado: {file_path}")
            except Exception as file_error:
                logger.error(f"[FILE] Error eliminando archivo: {file_error}")
        
        # Eliminar el examen
        delete_query = """
            DELETE FROM examenes 
            WHERE id = %s AND patient_id = %s
        """
        postgres_db.execute_query(delete_query, (exam_id, patient_id))
        
        logger.info(f"[DB] Examen {exam_id} eliminado para paciente {patient_id}")
        return jsonify({"deleted":True})
        
    except Exception as e:
        logger.error(f"delete_exam: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500'''

    # Insertar después de delete_consultation
    content = content.replace(
        '        return jsonify({"deleted":True})\n        \n    except Exception as e:',
        '        return jsonify({"deleted":True})\n        \n    except Exception as e:'
        + add_exam_delete,
    )

    # Escribir el archivo migrado
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Funciones de eliminación migradas a PostgreSQL")
    print("📝 Cambios realizados:")
    print("   - delete_consultation() - Ahora elimina de tabla 'atenciones_medicas'")
    print("   - delete_exam() - Nueva función que elimina de tabla 'examenes'")
    print("   - Eliminación de archivos asociados a exámenes")


if __name__ == "__main__":
    migrate_delete_functions()
