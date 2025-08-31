#!/usr/bin/env python3
"""
Script para configurar variables de entorno en Railway
"""

def railway_env_setup():
    """Configura las variables de entorno necesarias para Railway"""
    
    print("🚀 Configuración de Variables de Entorno para Railway")
    print("=" * 60)
    
    print("📋 Variables que debes configurar en Railway Dashboard:")
    print()
    
    print("1️⃣ DATABASE_URL (CRÍTICA)")
    print("   Valor: postgresql://postgres:SBbyfurhbJUJsFbelYJCcOvkSpXDCNZd@hopper.proxy.rlwy.net:51396/railway")
    print("   Descripción: Conexión a PostgreSQL de Railway")
    print()
    
    print("2️⃣ SECRET_KEY (CRÍTICA)")
    print("   Valor: medconnect-secret-key-2025-railway-production")
    print("   Descripción: Clave secreta para sesiones Flask")
    print()
    
    print("3️⃣ FLASK_ENV (CRÍTICA)")
    print("   Valor: production")
    print("   Descripción: Entorno de Flask")
    print()
    
    print("4️⃣ OPENROUTER_API_KEY (CRÍTICA)")
    print("   Valor: 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")
    print("   Descripción: API Key para OpenRouter")
    print()
    
    print("5️⃣ PORT (CRÍTICA)")
    print("   Valor: 5000")
    print("   Descripción: Puerto de la aplicación")
    print()
    
    print("6️⃣ TELEGRAM_BOT_TOKEN (OPCIONAL)")
    print("   Valor: (dejar vacío si no tienes bot de Telegram)")
    print("   Descripción: Token del bot de Telegram")
    print()
    
    print("7️⃣ CORS_ORIGINS (OPCIONAL)")
    print("   Valor: *")
    print("   Descripción: Orígenes permitidos para CORS")
    print()
    
    print("=" * 60)
    print("🔧 Pasos para configurar en Railway:")
    print()
    print("1. Ve a Railway Dashboard")
    print("2. Selecciona tu proyecto MedConnect")
    print("3. Ve a la pestaña 'Variables'")
    print("4. Agrega cada variable con su valor correspondiente")
    print("5. Guarda los cambios")
    print("6. Railway redeployará automáticamente")
    print()
    
    print("⚠️ IMPORTANTE:")
    print("- DATABASE_URL es la más crítica")
    print("- Sin ella, tendrás errores 502")
    print("- Railway redeployará automáticamente al cambiar variables")
    print()
    
    print("✅ Después de configurar las variables:")
    print("- La aplicación debería funcionar correctamente")
    print("- PostgreSQL se conectará automáticamente")
    print("- Los errores 502 deberían desaparecer")

if __name__ == "__main__":
    railway_env_setup() 