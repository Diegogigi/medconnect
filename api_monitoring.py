#!/usr/bin/env python3
"""
Sistema de monitoreo para Google Sheets API
Monitorea el uso de la API y proporciona alertas
"""

import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class APIMonitor:
    def __init__(self):
        self.request_count = 0
        self.request_history = []
        self.error_count = 0
        self.rate_limit_hits = 0
        self.start_time = time.time()
        self.alerts = []
        
        # Configurar límites
        self.max_requests_per_minute = 50
        self.max_requests_per_hour = 1000
        self.alert_threshold = 0.8  # 80% del límite
        
    def log_request(self, endpoint: str, success: bool = True, error_type: str = None):
        """Registra una solicitud a la API"""
        timestamp = time.time()
        
        # Registrar solicitud
        self.request_count += 1
        self.request_history.append({
            'timestamp': timestamp,
            'endpoint': endpoint,
            'success': success,
            'error_type': error_type
        })
        
        # Limpiar historial antiguo (mantener solo últimas 1000 solicitudes)
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
        
        # Contar errores
        if not success:
            self.error_count += 1
            if error_type == '429':
                self.rate_limit_hits += 1
        
        # Verificar límites
        self._check_limits()
        
        # Logging
        if not success:
            logger.warning(f"⚠️ API Request failed: {endpoint} - {error_type}")
        else:
            logger.debug(f"📊 API Request: {endpoint}")
    
    def _check_limits(self):
        """Verifica si se están acercando a los límites"""
        current_time = time.time()
        
        # Solicitudes en el último minuto
        one_minute_ago = current_time - 60
        recent_requests = [r for r in self.request_history if r['timestamp'] > one_minute_ago]
        
        if len(recent_requests) > self.max_requests_per_minute * self.alert_threshold:
            self._add_alert(f"⚠️ Alto uso de API: {len(recent_requests)} requests/min")
        
        # Solicitudes en la última hora
        one_hour_ago = current_time - 3600
        hourly_requests = [r for r in self.request_history if r['timestamp'] > one_hour_ago]
        
        if len(hourly_requests) > self.max_requests_per_hour * self.alert_threshold:
            self._add_alert(f"⚠️ Alto uso de API: {len(hourly_requests)} requests/hour")
    
    def _add_alert(self, message: str):
        """Agrega una alerta"""
        alert = {
            'timestamp': datetime.now(),
            'message': message,
            'severity': 'warning'
        }
        self.alerts.append(alert)
        
        # Mantener solo las últimas 100 alertas
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        logger.warning(message)
    
    def get_usage_stats(self):
        """Obtiene estadísticas de uso de la API"""
        current_time = time.time()
        
        # Solicitudes en diferentes períodos
        one_minute_ago = current_time - 60
        five_minutes_ago = current_time - 300
        one_hour_ago = current_time - 3600
        
        recent_requests = [r for r in self.request_history if r['timestamp'] > one_minute_ago]
        five_min_requests = [r for r in self.request_history if r['timestamp'] > five_minutes_ago]
        hourly_requests = [r for r in self.request_history if r['timestamp'] > one_hour_ago]
        
        # Calcular tasas de error
        recent_errors = [r for r in recent_requests if not r['success']]
        error_rate = len(recent_errors) / len(recent_requests) if recent_requests else 0
        
        return {
            'total_requests': self.request_count,
            'requests_last_minute': len(recent_requests),
            'requests_last_5_minutes': len(five_min_requests),
            'requests_last_hour': len(hourly_requests),
            'error_rate': error_rate,
            'rate_limit_hits': self.rate_limit_hits,
            'uptime_minutes': (current_time - self.start_time) / 60,
            'alerts': self.alerts[-10:],  # Últimas 10 alertas
            'limits': {
                'max_per_minute': self.max_requests_per_minute,
                'max_per_hour': self.max_requests_per_hour,
                'current_usage_percent': (len(recent_requests) / self.max_requests_per_minute) * 100
            }
        }
    
    def get_recommendations(self):
        """Obtiene recomendaciones basadas en el uso actual"""
        stats = self.get_usage_stats()
        recommendations = []
        
        # Verificar uso alto
        if stats['requests_last_minute'] > self.max_requests_per_minute * 0.8:
            recommendations.append({
                'type': 'warning',
                'message': 'Uso alto de API detectado. Considera implementar más cache.',
                'action': 'increase_cache_duration'
            })
        
        # Verificar errores frecuentes
        if stats['error_rate'] > 0.1:  # Más del 10% de errores
            recommendations.append({
                'type': 'error',
                'message': 'Tasa de error alta. Revisa la conectividad con Google Sheets.',
                'action': 'check_connectivity'
            })
        
        # Verificar rate limiting
        if stats['rate_limit_hits'] > 0:
            recommendations.append({
                'type': 'critical',
                'message': f'Rate limiting detectado {stats["rate_limit_hits"]} veces. Reduce la frecuencia de requests.',
                'action': 'reduce_request_frequency'
            })
        
        return recommendations

# Instancia global del monitor
api_monitor = APIMonitor()

def log_api_request(endpoint: str, success: bool = True, error_type: str = None):
    """Función helper para registrar requests de API"""
    api_monitor.log_request(endpoint, success, error_type)

def get_api_stats():
    """Función helper para obtener estadísticas"""
    return api_monitor.get_usage_stats()

def get_api_recommendations():
    """Función helper para obtener recomendaciones"""
    return api_monitor.get_recommendations()

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Simular algunos requests para probar
    log_api_request("sheets.values.get", True)
    log_api_request("sheets.values.update", True)
    log_api_request("sheets.values.batchGet", False, "429")
    
    # Mostrar estadísticas
    stats = get_api_stats()
    print("📊 Estadísticas de API:")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Requests/min: {stats['requests_last_minute']}")
    print(f"  Error rate: {stats['error_rate']:.2%}")
    print(f"  Rate limit hits: {stats['rate_limit_hits']}")
    
    # Mostrar recomendaciones
    recommendations = get_api_recommendations()
    print("\n💡 Recomendaciones:")
    for rec in recommendations:
        print(f"  {rec['type'].upper()}: {rec['message']}") 