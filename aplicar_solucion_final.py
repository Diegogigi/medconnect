#!/usr/bin/env python3
"""
Script final para aplicar la solución de rate limiting al archivo app.py
"""

def aplicar_solucion():
    """Aplica la solución de rate limiting al archivo app.py"""
    print("🔧 APLICANDO SOLUCIÓN DE RATE LIMITING")
    print("=" * 50)
    
    # Leer el archivo app.py
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        print("✅ Archivo app.py leído correctamente")
    except Exception as e:
        print(f"❌ Error leyendo app.py: {e}")
        return False
    
    # Agregar importación de threading si no existe
    if 'import threading' not in content:
        # Buscar después de las importaciones existentes
        if 'import time' in content and 'import random' in content:
            # Insertar después de las importaciones existentes
            content = content.replace('import time\nimport random', 'import time\nimport random\nimport threading')
            print("✅ Importación de threading agregada")
    
    # Agregar sistema de caché después de las importaciones
    cache_system = '''
# Sistema de caché para reducir llamadas a Google Sheets API
_cache = {}
_cache_lock = threading.Lock()
_cache_timeout = 60  # segundos (aumentado para reducir llamadas)

def get_cached_data(key, timeout=None):
    """Obtiene datos del caché si están disponibles y no han expirado"""
    if timeout is None:
        timeout = _cache_timeout
    
    with _cache_lock:
        if key in _cache:
            data, timestamp = _cache[key]
            if time.time() - timestamp < timeout:
                logger.info(f"[CACHE] Datos obtenidos del caché para: {key}")
                return data
            else:
                del _cache[key]
    return None

def set_cached_data(key, data):
    """Almacena datos en el caché"""
    with _cache_lock:
        _cache[key] = (data, time.time())
        logger.info(f"[CACHE] Datos almacenados en caché para: {key}")

def clear_cache():
    """Limpia el caché"""
    with _cache_lock:
        _cache.clear()
        logger.info("[CACHE] Caché limpiado")
'''
    
    # Insertar sistema de caché después de las importaciones
    if '# Sistema de caché' not in content:
        # Buscar donde insertar (después de las importaciones)
        insert_point = content.find('logger.info("  Iniciando importaciones de MedConnect...")')
        if insert_point != -1:
            # Insertar después de esa línea
            insert_point = content.find('\n', insert_point) + 1
            content = content[:insert_point] + cache_system + content[insert_point:]
            print("✅ Sistema de caché agregado")
    
    # Reemplazar la función handle_rate_limiting
    old_function = '''def handle_rate_limiting(func, max_retries=5, base_delay=2):
    """
    Maneja el rate limiting de Google Sheets API con retry exponencial mejorado
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_str = str(e).lower()
            
            # Detectar diferentes tipos de errores de rate limiting
            if any(keyword in error_str for keyword in ['429', 'quota exceeded', 'resource_exhausted', 'rate_limit']):
                if attempt < max_retries - 1:
                    # Delay exponencial con jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
                    logger.warning(f"[ADVERTENCIA] Rate limiting detectado (intento {attempt + 1}/{max_retries}). Esperando {delay:.2f}s...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"[ERROR] Rate limiting persistente despu s de {max_retries} intentos")
                    return None
            elif '500' in error_str or 'internal server error' in error_str:
                logger.error(f"[ERROR] Error interno del servidor de Google Sheets: {e}")
                return None
            else:
                logger.error(f"[ERROR] Error no relacionado con rate limiting: {e}")
                return None
    
    return None'''
    
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
    
    return None'''
    
    # Reemplazar la función
    if old_function in content:
        content = content.replace(old_function, new_function)
        print("✅ Función handle_rate_limiting mejorada")
    else:
        print("⚠️  No se encontró la función handle_rate_limiting original")
    
    # Guardar el archivo modificado
    try:
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Archivo app.py actualizado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error guardando app.py: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 APLICANDO SOLUCIÓN FINAL DE RATE LIMITING")
    print("=" * 60)
    
    try:
        success = aplicar_solucion()
        
        if success:
            print("\n✅ SOLUCIÓN APLICADA EXITOSAMENTE:")
            print("=" * 60)
            print("   • Sistema de caché implementado")
            print("   • Rate limiting mejorado con delays más largos")
            print("   • Fallback a datos en caché (10 minutos)")
            print("   • Detección mejorada de errores")
            print("   • Timeout de caché aumentado a 60 segundos")
            print("   • Manejo de errores 500 con fallback")
            
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
            print("\n❌ Error aplicando la solución")
            
    except Exception as e:
        print(f"\n❌ Error durante la aplicación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 