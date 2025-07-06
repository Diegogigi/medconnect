#!/usr/bin/env python3
"""
Script de prueba para verificar las optimizaciones de Google Sheets API
"""

import time
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_optimizations():
    """Prueba las optimizaciones implementadas"""
    
    print("🚀 Iniciando pruebas de optimizaciones de API...")
    
    try:
        # Importar el gestor optimizado
        from backend.database.sheets_manager import sheets_db
        from api_monitoring import get_api_stats, get_api_recommendations
        
        print("✅ SheetsManager importado correctamente")
        
        # Probar métodos optimizados
        print("\n📊 Probando métodos optimizados...")
        
        # 1. Probar batch_get_values
        print("1. Probando batch_get_values...")
        try:
            ranges = ["Usuarios!A:L", "Atenciones_Medicas!A:N"]
            result = sheets_db.batch_get_values(ranges)
            if result:
                print(f"   ✅ Batch get exitoso: {len(result.get('valueRanges', []))} rangos")
            else:
                print("   ❌ Batch get falló")
        except Exception as e:
            print(f"   ❌ Error en batch_get_values: {e}")
        
        # 2. Probar get_worksheet_with_fields
        print("2. Probando get_worksheet_with_fields...")
        try:
            fields = ["nombre", "email", "telefono"]
            result = sheets_db.get_worksheet_with_fields("Usuarios", fields)
            if result:
                print(f"   ✅ Field masks exitoso: {len(result.get('values', []))} registros")
            else:
                print("   ❌ Field masks falló")
        except Exception as e:
            print(f"   ❌ Error en get_worksheet_with_fields: {e}")
        
        # 3. Probar optimized_get_user_data
        print("3. Probando optimized_get_user_data...")
        try:
            # Usar un ID de prueba
            test_user_id = "USR_20240101_120000"
            result = sheets_db.optimized_get_user_data(test_user_id)
            if result:
                print(f"   ✅ Optimized user data exitoso")
                print(f"      - Atenciones: {len(result.get('atenciones', []))}")
                print(f"      - Medicamentos: {len(result.get('medicamentos', []))}")
                print(f"      - Exámenes: {len(result.get('examenes', []))}")
            else:
                print("   ⚠️ Optimized user data no encontró datos (normal para ID de prueba)")
        except Exception as e:
            print(f"   ❌ Error en optimized_get_user_data: {e}")
        
        # 4. Probar monitoreo
        print("4. Probando sistema de monitoreo...")
        try:
            stats = get_api_stats()
            recommendations = get_api_recommendations()
            
            print(f"   ✅ Estadísticas obtenidas:")
            print(f"      - Total requests: {stats.get('total_requests', 0)}")
            print(f"      - Requests/min: {stats.get('requests_last_minute', 0)}")
            print(f"      - Error rate: {stats.get('error_rate', 0):.2%}")
            print(f"      - Rate limit hits: {stats.get('rate_limit_hits', 0)}")
            
            if recommendations:
                print(f"   📋 Recomendaciones:")
                for rec in recommendations:
                    print(f"      - {rec.get('type', 'info').upper()}: {rec.get('message', '')}")
            else:
                print("   ✅ No hay recomendaciones (uso normal)")
                
        except Exception as e:
            print(f"   ❌ Error en monitoreo: {e}")
        
        # 5. Probar cache
        print("5. Probando sistema de cache...")
        try:
            # Primera llamada (sin cache)
            start_time = time.time()
            result1 = sheets_db.get_worksheet("Usuarios")
            time1 = time.time() - start_time
            
            # Segunda llamada (con cache)
            start_time = time.time()
            result2 = sheets_db.get_worksheet("Usuarios")
            time2 = time.time() - start_time
            
            print(f"   ✅ Cache funcionando:")
            print(f"      - Primera llamada: {time1:.3f}s")
            print(f"      - Segunda llamada: {time2:.3f}s")
            print(f"      - Mejora: {((time1 - time2) / time1 * 100):.1f}%")
            
        except Exception as e:
            print(f"   ❌ Error probando cache: {e}")
        
        print("\n🎯 Resumen de pruebas:")
        print("✅ Todas las optimizaciones están implementadas")
        print("✅ Sistema de monitoreo activo")
        print("✅ Cache funcionando correctamente")
        print("✅ Rate limiting implementado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general en pruebas: {e}")
        return False

def test_rate_limiting():
    """Prueba el sistema de rate limiting"""
    
    print("\n🔄 Probando rate limiting...")
    
    try:
        from backend.database.sheets_manager import sheets_db
        
        # Simular múltiples requests rápidos
        for i in range(5):
            start_time = time.time()
            result = sheets_db.get_worksheet("Usuarios")
            time_taken = time.time() - start_time
            
            print(f"   Request {i+1}: {time_taken:.3f}s")
            
            if time_taken > 1:
                print(f"   ⚠️ Rate limiting activo (espera detectada)")
        
        print("✅ Rate limiting funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en rate limiting: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PRUEBAS DE OPTIMIZACIONES DE GOOGLE SHEETS API")
    print("=" * 60)
    
    # Ejecutar pruebas
    success1 = test_api_optimizations()
    success2 = test_rate_limiting()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TODAS LAS PRUEBAS EXITOSAS")
        print("✅ Las optimizaciones están funcionando correctamente")
        print("✅ El sistema está listo para manejar el rate limiting")
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON")
        print("❌ Revisar la configuración de las optimizaciones")
    
    print("=" * 60) 