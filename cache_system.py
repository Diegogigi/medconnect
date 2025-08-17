#!/usr/bin/env python3
"""
Sistema de caché para reducir llamadas a Google Sheets API
"""

import time
import random
import threading
import logging

logger = logging.getLogger(__name__)

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

def get_cache_stats():
    """Obtiene estadísticas del caché"""
    with _cache_lock:
        return {
            'total_entries': len(_cache),
            'cache_timeout': _cache_timeout
        }

def handle_rate_limiting(func, max_retries=5, base_delay=2, use_cache=True):
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
    
    return None

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