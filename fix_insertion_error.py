#!/usr/bin/env python3
"""
Script para corregir el error de inserción de la función delete_exam
"""


def fix_insertion_error():
    """Corrige el error de inserción de la función delete_exam"""

    print("🔧 Corrigiendo error de inserción...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Corregir el bloque problemático
    problematic_block = '''    except Exception as e:
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
        return jsonify({"error":"Error interno del servidor"}), 500
        logger.error(f"delete_consultation: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500'''

    corrected_block = '''    except Exception as e:
        logger.error(f"delete_consultation: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500

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

    content = content.replace(problematic_block, corrected_block)

    # Escribir el archivo corregido
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Error de inserción corregido")


if __name__ == "__main__":
    fix_insertion_error()
