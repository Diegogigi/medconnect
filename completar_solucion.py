#!/usr/bin/env python3
"""
Script para completar las mejoras faltantes en la solución de rate limiting
"""

def completar_solucion():
    """Completa las mejoras faltantes en app.py"""
    print("🔧 COMPLETANDO SOLUCIÓN DE RATE LIMITING")
    print("=" * 50)
    
    try:
        # Leer el archivo app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Archivo app.py leído correctamente")
        
        # Corregir el timeout de caché
        if "_cache_timeout = 30" in content:
            content = content.replace("_cache_timeout = 30", "_cache_timeout = 60")
            print("✅ Timeout de caché corregido a 60 segundos")
        
        # Buscar y reemplazar la función handle_rate_limiting
        # Buscar la función actual
        start_marker = "def handle_rate_limiting("
        end_marker = "return None"
        
        start_pos = content.find(start_marker)
        if start_pos != -1:
            # Encontrar el final de la función
            end_pos = content.find(end_marker, start_pos)
            if end_pos != -1:
                end_pos = content.find("\n", end_pos) + 1
                
                # Nueva función mejorada
                new_function = '''def handle_rate_limiting(func, max_retries=5, base_delay=3, use_cache=True):
    """
    Maneja el rate limiting de Google Sheets API con retry exponencial mejorado y caché
    """
    # Generar clave de caché basada en la función
    cache_key = f"{func.__name__}_{hash(str(func))}"
    
    # Intentar obtener del caché primero
    if use_cache:
        cached_result = get_cached_data(cache_key)
        if cached_result is not None:
            return cached_result
    
    for attempt in range(max_retries):
        try:
            result = func()
            
            # Almacenar en caché si fue exitoso
            if use_cache and result is not None:
                set_cached_data(cache_key, result)
            
            return result
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Detectar diferentes tipos de errores de rate limiting
            if any(keyword in error_str for keyword in ['429', 'quota exceeded', 'resource_exhausted', 'rate_limit']):
                if attempt < max_retries - 1:
                    # Delay exponencial con jitter mejorado
                    delay = base_delay * (2 ** attempt) + random.uniform(2, 5)
                    logger.warning(f"[ADVERTENCIA] Rate limiting detectado (intento {attempt + 1}/{max_retries}). Esperando {delay:.2f}s...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"[ERROR] Rate limiting persistente después de {max_retries} intentos")
                    # Intentar devolver datos del caché como fallback
                    if use_cache:
                        cached_result = get_cached_data(cache_key, timeout=600)  # 10 minutos para fallback
                        if cached_result is not None:
                            logger.info(f"[CACHE] Usando datos del caché como fallback para: {cache_key}")
                            return cached_result
                    return None
            elif '500' in error_str or 'internal server error' in error_str:
                logger.error(f"[ERROR] Error interno del servidor de Google Sheets: {e}")
                # Intentar devolver datos del caché como fallback
                if use_cache:
                    cached_result = get_cached_data(cache_key, timeout=600)
                    if cached_result is not None:
                        logger.info(f"[CACHE] Usando datos del caché como fallback para error 500: {cache_key}")
                        return cached_result
                return None
            else:
                logger.error(f"[ERROR] Error no relacionado con rate limiting: {e}")
                return None
    
    return None
'''
                
                # Reemplazar la función
                content = content[:start_pos] + new_function + content[end_pos:]
                print("✅ Función handle_rate_limiting completamente reemplazada")
        
        # Guardar el archivo modificado
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Archivo app.py actualizado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error completando la solución: {e}")
        return False

def verificar_completado():
    """Verifica que todas las mejoras se completaron"""
    print("\n🔍 VERIFICANDO COMPLETADO DE LA SOLUCIÓN")
    print("=" * 50)
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        verificaciones = [
            ("_cache_timeout = 60", "Timeout de caché correcto"),
            ("base_delay=3", "Base delay mejorado"),
            ("random.uniform(2, 5)", "Jitter mejorado"),
            ("timeout=600", "Timeout de fallback (10 minutos)"),
            ("[CACHE] Usando datos del caché como fallback", "Fallback a caché"),
            ("cache_key = f\"{func.__name__}_{hash(str(func))}\"", "Generación de clave de caché"),
            ("cached_result = get_cached_data(cache_key)", "Uso de caché"),
            ("set_cached_data(cache_key, result)", "Almacenamiento en caché")
        ]
        
        exitos = 0
        for busqueda, descripcion in verificaciones:
            encontrado = busqueda in content
            if encontrado:
                exitos += 1
            status = "✅" if encontrado else "❌"
            print(f"{status} {descripcion}")
        
        print(f"\n📊 Resultado: {exitos}/{len(verificaciones)} mejoras completadas")
        
        if exitos >= len(verificaciones) * 0.9:  # 90% o más
            print("🎉 ¡SOLUCIÓN COMPLETADA EXITOSAMENTE!")
            return True
        else:
            print("⚠️  Algunas mejoras aún faltan")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 COMPLETANDO SOLUCIÓN DE RATE LIMITING")
    print("=" * 60)
    
    try:
        # Completar la solución
        success = completar_solucion()
        
        if success:
            # Verificar que se completó correctamente
            verificado = verificar_completado()
            
            if verificado:
                print("\n✅ SOLUCIÓN COMPLETADA Y VERIFICADA:")
                print("=" * 60)
                print("   • Sistema de caché completamente implementado")
                print("   • Rate limiting mejorado con delays más largos")
                print("   • Fallback a datos en caché (10 minutos)")
                print("   • Detección mejorada de errores")
                print("   • Timeout de caché configurado a 60 segundos")
                print("   • Manejo de errores 500 con fallback")
                print("   • Jitter mejorado (2-5 segundos)")
                
                print("\n🎯 BENEFICIOS ESPERADOS:")
                print("   • Reducción significativa de errores 429")
                print("   • Respuestas más rápidas desde caché")
                print("   • Mejor experiencia de usuario")
                print("   • Menor carga en Google Sheets API")
                print("   • Sistema más resiliente a fallos")
                
                print("\n📋 PRÓXIMOS PASOS:")
                print("   1. Reiniciar el servidor Flask")
                print("   2. Probar el endpoint /api/get-atenciones")
                print("   3. Verificar que los errores 429 se reducen")
                print("   4. Monitorear el rendimiento del sistema")
                
            else:
                print("\n⚠️  La solución se completó pero necesita verificación manual")
                
        else:
            print("\n❌ Error completando la solución")
            
    except Exception as e:
        print(f"\n❌ Error durante la completación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 