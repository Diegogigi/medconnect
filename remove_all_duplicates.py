#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar todos los endpoints duplicados en app.py
"""

import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def remove_all_duplicates():
    """Eliminar todos los endpoints duplicados"""
    logger.info("🔧 Eliminando todos los endpoints duplicados...")

    try:
        with open("app.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Patrones para todos los endpoints duplicados encontrados
        patterns = [
            {
                "name": "test_complete",
                "pattern": r'@app\.route\("/test-complete"\)\s*def test_complete\(\):[^@]*?return html\s*\n',
            },
            {
                "name": "favicon",
                "pattern": r'@app\.route\("/favicon\.ico"\)\s*def favicon\(\):[^@]*?mimetype="image/[^"]+",?\s*\)\s*\n',
            },
            {
                "name": "serve_static",
                "pattern": r'@app\.route\("/static/<path:filename>"\)\s*def serve_static\([^)]*\):[^@]*?return[^@]*?\n(?=\s*(?:@app\.route|def|class|if __name__|$))',
            },
            {
                "name": "uploaded_file",
                "pattern": r'@app\.route\("/uploads/medical_files/<filename>"\)\s*def uploaded_file\([^)]*\):[^@]*?return[^@]*?\n(?=\s*(?:@app\.route|def|class|if __name__|$))',
            },
            {
                "name": "upload_exam_file",
                "pattern": r'@app\.route\("/api/patient/<patient_id>/exams/upload"[^)]*\)\s*def upload_exam_file\([^)]*\):[^@]*?return[^@]*?\n(?=\s*(?:@app\.route|def|class|if __name__|$))',
            },
        ]

        for endpoint_info in patterns:
            name = endpoint_info["name"]
            pattern = endpoint_info["pattern"]

            # Encontrar todas las coincidencias
            matches = list(re.finditer(pattern, content, re.DOTALL))
            logger.info(f"📊 Encontradas {len(matches)} definiciones de {name}")

            if len(matches) > 1:
                logger.info(f"🗑️ Eliminando definiciones duplicadas de {name}...")

                # Eliminar desde la última hacia la primera
                for i in range(len(matches) - 1, 0, -1):
                    match = matches[i]
                    start, end = match.span()
                    start_line = content[:start].count("\n") + 1
                    end_line = content[:end].count("\n") + 1
                    logger.info(
                        f"❌ Eliminando definición {i+1} de {name} (líneas {start_line}-{end_line})"
                    )
                    content = content[:start] + content[end:]

                logger.info(f"✅ Endpoints duplicados de {name} eliminados")
            else:
                logger.info(f"✅ No se encontraron duplicados de {name}")

        # Guardar el archivo
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(content)

        logger.info("✅ Todos los endpoints duplicados eliminados exitosamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error eliminando duplicados: {e}")
        return False


def main():
    """Función principal"""
    logger.info("🚀 Iniciando eliminación de todos los endpoints duplicados...")

    if remove_all_duplicates():
        logger.info("🎉 Proceso completado exitosamente")
        logger.info("💡 Ahora puedes ejecutar python app.py")
    else:
        logger.error("❌ No se pudieron eliminar los duplicados")


if __name__ == "__main__":
    main()
