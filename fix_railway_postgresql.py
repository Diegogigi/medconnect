#!/usr/bin/env python3
"""
Script para arreglar la conexión a PostgreSQL en Railway
"""


def fix_railway_postgresql():
    """Arregla la conexión a PostgreSQL para Railway"""

    print("🔧 Arreglando conexión PostgreSQL para Railway...")

    # Leer el archivo postgresql_db_manager.py
    with open("postgresql_db_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar la función connect
    old_connect = '''    def connect(self):
        """Conectar a PostgreSQL"""
        try:
            database_url = os.environ.get("DATABASE_URL")

            if database_url:
                self.conn = psycopg2.connect(database_url)
            else:
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
            self.connected = False'''

    new_connect = '''    def connect(self):
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

    # Reemplazar en el contenido
    if old_connect in content:
        content = content.replace(old_connect, new_connect)

        # Escribir el archivo actualizado
        with open("postgresql_db_manager.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Conexión PostgreSQL arreglada para Railway")
        print("🔧 Ahora usará DATABASE_URL cuando esté disponible")
    else:
        print("❌ No se encontró la función connect original")


if __name__ == "__main__":
    fix_railway_postgresql()
