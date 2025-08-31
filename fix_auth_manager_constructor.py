#!/usr/bin/env python3
"""
Script para arreglar el constructor de AuthManager
"""


def fix_auth_manager_constructor():
    """Arregla el constructor de AuthManager para aceptar db_instance"""

    print("🔧 Arreglando constructor de AuthManager...")

    # Leer el archivo auth_manager.py
    with open("auth_manager.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Buscar y reemplazar el constructor
    old_constructor = '''    def __init__(self):
        """Inicializar el gestor de autenticación con PostgreSQL"""
        self.postgres_db = None
        self.use_fallback = False

        try:
            # Importar PostgreSQL Manager
            from postgresql_db_manager import PostgreSQLDBManager
            self.postgres_db = PostgreSQLDBManager()
            
            if self.postgres_db.is_connected():
                logger.info("✅ AuthManager inicializado con PostgreSQL")
            else:
                logger.warning("⚠️ PostgreSQL no disponible - usando sistema de fallback")
                self.use_fallback = True
                
        except Exception as e:
            logger.error(f"❌ Error inicializando AuthManager: {e}")
            logger.warning("⚠️ Usando sistema de fallback")
            self.use_fallback = True'''

    new_constructor = '''    def __init__(self, db_instance=None):
        """Inicializar el gestor de autenticación con PostgreSQL"""
        self.postgres_db = None
        self.use_fallback = False

        if db_instance:
            # Usar instancia existente
            self.postgres_db = db_instance
            if self.postgres_db.is_connected():
                logger.info("✅ AuthManager inicializado con PostgreSQL (instancia compartida)")
            else:
                logger.warning("⚠️ PostgreSQL no disponible - usando sistema de fallback")
                self.use_fallback = True
        else:
            # Crear nueva instancia si no se proporciona una
            try:
                from postgresql_db_manager import PostgreSQLDBManager
                self.postgres_db = PostgreSQLDBManager()
                
                if self.postgres_db.is_connected():
                    logger.info("✅ AuthManager inicializado con PostgreSQL")
                else:
                    logger.warning("⚠️ PostgreSQL no disponible - usando sistema de fallback")
                    self.use_fallback = True
                    
            except Exception as e:
                logger.error(f"❌ Error inicializando AuthManager: {e}")
                logger.warning("⚠️ Usando sistema de fallback")
                self.use_fallback = True'''

    # Reemplazar en el contenido
    if old_constructor in content:
        content = content.replace(old_constructor, new_constructor)

        # Escribir el archivo actualizado
        with open("auth_manager.py", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Constructor de AuthManager arreglado")
        print("🔧 Ahora acepta db_instance para compartir conexiones")
    else:
        print("❌ No se encontró el constructor original")


if __name__ == "__main__":
    fix_auth_manager_constructor()
