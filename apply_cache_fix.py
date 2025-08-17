#!/usr/bin/env python3
"""
Script para aplicar las mejoras de caché al archivo app.py
"""

import re

def apply_cache_improvements():
    """Aplica las mejoras de caché al archivo app.py"""
    print("🔧 APLICANDO MEJORAS DE CACHÉ A APP.PY")
    print("=" * 50)
    
    # Leer el archivo app.py
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        print("✅ Archivo app.py leído correctamente")
    except Exception as e:
        print(f"❌ Error leyendo app.py: {e}")
        return False
    
    # Agregar importaciones de threading si no existen
    if 'import threading' not in content:
        # Buscar la línea después de las importaciones existentes
        import_pattern = r'(import time\nimport random)'
        replacement = r'\1\nimport threading'
        content = re.sub(import_pattern, replacement, content)
        print("✅ Importación de threading agregada")
    
    # Agregar sistema de caché después de las importaciones
    cache_system = '''
# Sistema de caché para reducir llamadas a Google Sheets API
_cache = {}
_cache_lock = threading.Lock()
_cache_timeout = 30  # segundos

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

def handle_google_sheets_request(func, cache_key=None, timeout=30):
    """
    Maneja una solicitud a Google Sheets con caché y rate limiting
    """
    if cache_key is None:
        cache_key = f"{func.__name__}_{int(time.time())}"
    
    # Intentar obtener del caché primero
    cached_result = get_cached_data(cache_key, timeout)
    if cached_result is not None:
        return cached_result
    
    # Si no está en caché, hacer la solicitud con rate limiting
    result = handle_rate_limiting(func, use_cache=False)
    
    # Almacenar en caché si fue exitoso
    if result is not None:
        set_cached_data(cache_key, result)
    
    return result
'''
    
    # Buscar donde insertar el sistema de caché (después de las importaciones)
    if '# Sistema de caché' not in content:
        # Insertar después de las importaciones
        insert_pattern = r'(logger\.info\("  Iniciando importaciones de MedConnect\.\.\."\))'
        replacement = r'\1' + cache_system
        content = re.sub(insert_pattern, replacement, content)
        print("✅ Sistema de caché agregado")
    
    # Mejorar la función handle_rate_limiting existente
    old_rate_limiting = r'def handle_rate_limiting\(func, max_retries=5, base_delay=2\):\s*""".*?"""\s*for attempt in range\(max_retries\):\s*try:\s*return func\(\)\s*except Exception as e:\s*error_str = str\(e\)\.lower\(\)\s*# Detectar diferentes tipos de errores de rate limiting\s*if any\(keyword in error_str for keyword in \['429', 'quota exceeded', 'resource_exhausted', 'rate_limit'\]\):\s*if attempt < max_retries - 1:\s*# Delay exponencial con jitter\s*delay = base_delay \* \(2 \*\* attempt\) \+ random\.uniform\(0, 2\)\s*logger\.warning\(f"\[ADVERTENCIA\] Rate limiting detectado \(intento \{attempt \+ 1\}/\{max_retries\}\)\. Esperando \{delay:\.2f\}s\.\.\."\)\s*time\.sleep\(delay\)\s*continue\s*else:\s*logger\.error\(f"\[ERROR\] Rate limiting persistente despu s de \{max_retries\} intentos"\)\s*return None\s*elif '500' in error_str or 'internal server error' in error_str:\s*logger\.error\(f"\[ERROR\] Error interno del servidor de Google Sheets: \{e\}"\)\s*return None\s*else:\s*logger\.error\(f"\[ERROR\] Error no relacionado con rate limiting: \{e\}"\)\s*return None\s*return None'
    
    new_rate_limiting = '''def handle_rate_limiting(func, max_retries=5, base_delay=2, use_cache=True):
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
                    delay = base_delay * (2 ** attempt) + random.uniform(1, 3)
                    logger.warning(f"[ADVERTENCIA] Rate limiting detectado (intento {attempt + 1}/{max_retries}). Esperando {delay:.2f}s...")
                    time.sleep(delay)
                    continue
                else:
                    logger.error(f"[ERROR] Rate limiting persistente después de {max_retries} intentos")
                    # Intentar devolver datos del caché como fallback
                    if use_cache:
                        cached_result = get_cached_data(cache_key, timeout=300)  # 5 minutos para fallback
                        if cached_result is not None:
                            logger.info(f"[CACHE] Usando datos del caché como fallback para: {cache_key}")
                            return cached_result
                    return None
            elif '500' in error_str or 'internal server error' in error_str:
                logger.error(f"[ERROR] Error interno del servidor de Google Sheets: {e}")
                # Intentar devolver datos del caché como fallback
                if use_cache:
                    cached_result = get_cached_data(cache_key, timeout=300)
                    if cached_result is not None:
                        logger.info(f"[CACHE] Usando datos del caché como fallback para error 500: {cache_key}")
                        return cached_result
                return None
            else:
                logger.error(f"[ERROR] Error no relacionado con rate limiting: {e}")
                return None
    
    return None'''
    
    # Reemplazar la función handle_rate_limiting
    if 'def handle_rate_limiting(func, max_retries=5, base_delay=2):' in content:
        # Buscar y reemplazar la función completa
        pattern = r'def handle_rate_limiting\(func, max_retries=5, base_delay=2\):.*?return None'
        content = re.sub(pattern, new_rate_limiting, content, flags=re.DOTALL)
        print("✅ Función handle_rate_limiting mejorada")
    
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
    print("🚀 APLICANDO MEJORAS DE CACHÉ A APP.PY")
    print("=" * 60)
    
    try:
        success = apply_cache_improvements()
        
        if success:
            print("\n✅ MEJORAS APLICADAS EXITOSAMENTE:")
            print("   • Sistema de caché implementado")
            print("   • Rate limiting mejorado")
            print("   • Fallback a datos en caché")
            print("   • Detección mejorada de errores")
            print("   • Manejo de errores 500 con fallback")
            
            print("\n🎯 BENEFICIOS ESPERADOS:")
            print("   • Reducción significativa de errores 429")
            print("   • Respuestas más rápidas desde caché")
            print("   • Mejor experiencia de usuario")
            print("   • Menor carga en Google Sheets API")
            
            print("\n📋 PRÓXIMOS PASOS:")
            print("   1. Reiniciar el servidor Flask")
            print("   2. Probar el endpoint /api/get-atenciones")
            print("   3. Verificar que los errores 429 se reducen")
            
        else:
            print("\n❌ Error aplicando las mejoras")
            
    except Exception as e:
        print(f"\n❌ Error durante la aplicación de mejoras: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 