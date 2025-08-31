#!/usr/bin/env python3
"""
Script para mejorar la detección de DATABASE_URL en Railway
"""


def fix_railway_database_detection():
    """Mejora la detección de DATABASE_URL en Railway"""

    print("🔧 Mejorando detección de DATABASE_URL en Railway...")

    # Leer el archivo postgresql_db_manager.py
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la función connect
    old_connect = '''    def connect(self):
        """Conectar a PostgreSQL"""
        try:
            # Priorizar DATABASE_URL (Railway)
            database_url = os.environ.get("DATABASE_URL")
            
            if database_url:
                logger.info("🔗 Conectando usando DATABASE_URL de Railway...")
                self.conn = psycopg2.connect(database_url)
            else:
                # Fallback para desarrollo local
                logger.info("🔗 Conectando usando variables individuales...")
                self.conn = psycopg2.connect(
                    host=os.environ.get("PGHOST", "localhost"),
                    database=os.environ.get("PGDATABASE", "medconnect"),
                    user=os.environ.get("PGUSER", "postgres"),
                    password=os.environ.get("PGPASSWORD", ""),
                    port=os.environ.get("PGPORT", "5432"),
                )

            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            self.connected = True
            logger.info("✅ PostgreSQL DB Manager conectado exitosamente")

        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            self.connected = False
            # En Railway, si no hay DATABASE_URL, no intentar localhost
            if not database_url:
                logger.warning("⚠️ No se encontró DATABASE_URL - modo fallback activado")'''

    new_connect = '''    def connect(self):
        """Conectar a PostgreSQL"""
        try:
            # Debug: Mostrar todas las variables de entorno relacionadas con DB
            logger.info("🔍 Verificando variables de entorno de base de datos...")
            database_url = os.environ.get("DATABASE_URL")
            pghost = os.environ.get("PGHOST")
            pgdatabase = os.environ.get("PGDATABASE")
            pguser = os.environ.get("PGUSER")
            pgpassword = os.environ.get("PGPASSWORD")
            pgport = os.environ.get("PGPORT")
            
            logger.info(f"📋 Variables encontradas:")
            logger.info(f"   DATABASE_URL: {'✅ Configurada' if database_url else '❌ No configurada'}")
            logger.info(f"   PGHOST: {pghost or 'No configurado'}")
            logger.info(f"   PGDATABASE: {pgdatabase or 'No configurado'}")
            logger.info(f"   PGUSER: {pguser or 'No configurado'}")
            logger.info(f"   PGPASSWORD: {'✅ Configurada' if pgpassword else '❌ No configurada'}")
            logger.info(f"   PGPORT: {pgport or 'No configurado'}")
            
            if database_url:
                logger.info("🔗 Conectando usando DATABASE_URL de Railway...")
                logger.info(f"   URL: {database_url[:50]}..." if len(database_url) > 50 else f"   URL: {database_url}")
                self.conn = psycopg2.connect(database_url)
            else:
                # Fallback para desarrollo local
                logger.info("🔗 Conectando usando variables individuales...")
                self.conn = psycopg2.connect(
                    host=pghost or "localhost",
                    database=pgdatabase or "medconnect",
                    user=pguser or "postgres",
                    password=pgpassword or "",
                    port=pgport or "5432",
                )

            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            self.connected = True
            logger.info("✅ PostgreSQL DB Manager conectado exitosamente")

        except Exception as e:
            logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            self.connected = False
            # En Railway, si no hay DATABASE_URL, no intentar localhost
            if not database_url:
                logger.warning("⚠️ No se encontró DATABASE_URL - modo fallback activado")
                logger.warning("🔧 Verifica que DATABASE_URL esté configurada en Railway")'''

    # Reemplazar en el contenido
    if old_connect in content:
        content = content.replace(old_connect, new_connect)

        # Escribir el archivo actualizado
        with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Detección de DATABASE_URL mejorada")
        print("🔍 Ahora mostrará información detallada de las variables")
    else:
        print("❌ No se encontró la función connect original")


if __name__ == "__main__":
    fix_railway_database_detection()
