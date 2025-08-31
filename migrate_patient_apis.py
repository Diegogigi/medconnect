#!/usr/bin/env python3
"""
Script para migrar las APIs de paciente a PostgreSQL
"""


def migrate_patient_apis():
    """Migra las APIs de paciente a PostgreSQL"""

    print("🔧 Migrando APIs de paciente a PostgreSQL...")

    # Leer el archivo
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Migrar get_patient_consultations
    old_consultations = """@app.route("/api/patient/<patient_id>/consultations", methods=["GET"])
@login_required
def get_patient_consultations(patient_id):
    try:
        # Si tienes DB: devolver registros; aquí demo seguro
        return jsonify({"consultations":[]})
    except Exception as e:
        logger.error(f"get_patient_consultations: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500"""

    new_consultations = '''@app.route("/api/patient/<patient_id>/consultations", methods=["GET"])
@login_required
def get_patient_consultations(patient_id):
    try:
        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - retornando array vacío")
            return jsonify({"consultations":[]})
        
        # Consultar consultas del paciente desde PostgreSQL
        query = """
            SELECT id, patient_id, doctor, specialty, date, diagnosis, treatment, notes, status
            FROM atenciones_medicas 
            WHERE patient_id = %s
            ORDER BY date DESC
        """
        result = postgres_db.execute_query(query, (patient_id,))
        
        consultations = []
        if result:
            for row in result:
                consultation = {
                    "id": row.get("id"),
                    "patient_id": row.get("patient_id"),
                    "doctor": row.get("doctor"),
                    "specialty": row.get("specialty"),
                    "date": row.get("date"),
                    "diagnosis": row.get("diagnosis"),
                    "treatment": row.get("treatment"),
                    "notes": row.get("notes"),
                    "status": row.get("status", "completada")
                }
                consultations.append(consultation)
        
        logger.info(f"[DB] Consultas encontradas para paciente {patient_id}: {len(consultations)}")
        return jsonify({"consultations": consultations})
        
    except Exception as e:
        logger.error(f"get_patient_consultations: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500'''

    content = content.replace(old_consultations, new_consultations)

    # 2. Migrar get_patient_exams
    old_exams = """@app.route("/api/patient/<patient_id>/exams", methods=["GET"])
@login_required
def get_patient_exams(patient_id):
    try:
        return jsonify({"exams":[]})
    except Exception as e:
        logger.error(f"get_patient_exams: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500"""

    new_exams = '''@app.route("/api/patient/<patient_id>/exams", methods=["GET"])
@login_required
def get_patient_exams(patient_id):
    try:
        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - retornando array vacío")
            return jsonify({"exams":[]})
        
        # Consultar exámenes del paciente desde PostgreSQL
        query = """
            SELECT id, patient_id, exam_type, date, results, lab, doctor, file_url, status
            FROM examenes 
            WHERE patient_id = %s
            ORDER BY date DESC
        """
        result = postgres_db.execute_query(query, (patient_id,))
        
        exams = []
        if result:
            for row in result:
                exam = {
                    "id": row.get("id"),
                    "patient_id": row.get("patient_id"),
                    "exam_type": row.get("exam_type"),
                    "date": row.get("date"),
                    "results": row.get("results"),
                    "lab": row.get("lab"),
                    "doctor": row.get("doctor"),
                    "file_url": row.get("file_url"),
                    "status": row.get("status", "completado")
                }
                exams.append(exam)
        
        logger.info(f"[DB] Exámenes encontrados para paciente {patient_id}: {len(exams)}")
        return jsonify({"exams": exams})
        
    except Exception as e:
        logger.error(f"get_patient_exams: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500'''

    content = content.replace(old_exams, new_exams)

    # 3. Migrar get_patient_family
    old_family = """@app.route("/api/patient/<patient_id>/family", methods=["GET"])
@login_required
def get_patient_family(patient_id):
    try:
        return jsonify({"family":[]})
    except Exception as e:
        logger.error(f"get_patient_family: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500"""

    new_family = '''@app.route("/api/patient/<patient_id>/family", methods=["GET"])
@login_required
def get_patient_family(patient_id):
    try:
        if not postgres_db or not postgres_db.is_connected():
            logger.warning("PostgreSQL no disponible - retornando array vacío")
            return jsonify({"family":[]})
        
        # Consultar familiares del paciente desde PostgreSQL
        query = """
            SELECT id, patient_id, nombre, relacion, telefono, email, direccion
            FROM familiares_autorizados 
            WHERE patient_id = %s
            ORDER BY nombre
        """
        result = postgres_db.execute_query(query, (patient_id,))
        
        family = []
        if result:
            for row in result:
                family_member = {
                    "id": row.get("id"),
                    "patient_id": row.get("patient_id"),
                    "nombre": row.get("nombre"),
                    "relacion": row.get("relacion"),
                    "telefono": row.get("telefono"),
                    "email": row.get("email"),
                    "direccion": row.get("direccion")
                }
                family.append(family_member)
        
        logger.info(f"[DB] Familiares encontrados para paciente {patient_id}: {len(family)}")
        return jsonify({"family": family})
        
    except Exception as e:
        logger.error(f"get_patient_family: {e}")
        return jsonify({"error":"Error interno del servidor"}), 500'''

    content = content.replace(old_family, new_family)

    # Escribir el archivo migrado
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ APIs de paciente migradas a PostgreSQL")
    print("📝 Cambios realizados:")
    print(
        "   - get_patient_consultations() - Ahora consulta tabla 'atenciones_medicas'"
    )
    print("   - get_patient_exams() - Ahora consulta tabla 'examenes'")
    print("   - get_patient_family() - Ahora consulta tabla 'familiares_autorizados'")


if __name__ == "__main__":
    migrate_patient_apis()
