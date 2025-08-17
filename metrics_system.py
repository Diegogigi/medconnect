#!/usr/bin/env python3
"""
Sistema de Métricas y Observabilidad
Métricas: % respuestas con ≥2 citas, % oraciones con soporte, latencia p95, tasa de preprints filtrados
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Punto de métrica con timestamp"""

    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """Resumen de métrica"""

    nombre: str
    valor_actual: float
    valor_promedio: float
    valor_minimo: float
    valor_maximo: float
    p95: float
    p99: float
    num_muestras: int
    ultima_actualizacion: datetime


class MetricsCollector:
    """Colector de métricas del sistema RAG"""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.metadata: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.start_time = datetime.now()

        logger.info("📊 Sistema de métricas inicializado")

    def record_metric(self, nombre: str, valor: float, metadata: Dict[str, Any] = None):
        """Registra una métrica"""
        timestamp = datetime.now()

        metric_point = MetricPoint(
            timestamp=timestamp, value=valor, metadata=metadata or {}
        )

        self.metrics[nombre].append(metric_point)

        # Actualizar metadata
        if metadata:
            self.metadata[nombre].update(metadata)

        logger.debug(f"📈 Métrica registrada: {nombre} = {valor}")

    def record_latency(self, componente: str, latencia: float):
        """Registra latencia de un componente"""
        self.record_metric(
            f"latencia_{componente}", latencia, {"componente": componente}
        )

    def record_citation_coverage(self, oraciones_con_citas: int, total_oraciones: int):
        """Registra cobertura de citas"""
        if total_oraciones > 0:
            cobertura = oraciones_con_citas / total_oraciones
            self.record_metric(
                "cobertura_citas",
                cobertura,
                {
                    "oraciones_con_citas": oraciones_con_citas,
                    "total_oraciones": total_oraciones,
                },
            )

    def record_response_quality(self, respuestas_con_citas: int, total_respuestas: int):
        """Registra calidad de respuestas"""
        if total_respuestas > 0:
            calidad = respuestas_con_citas / total_respuestas
            self.record_metric(
                "calidad_respuestas",
                calidad,
                {
                    "respuestas_con_citas": respuestas_con_citas,
                    "total_respuestas": total_respuestas,
                },
            )

    def record_preprint_filtering(self, preprints_filtrados: int, total_preprints: int):
        """Registra filtrado de preprints"""
        if total_preprints > 0:
            tasa_filtrado = preprints_filtrados / total_preprints
            self.record_metric(
                "tasa_preprints_filtrados",
                tasa_filtrado,
                {
                    "preprints_filtrados": preprints_filtrados,
                    "total_preprints": total_preprints,
                },
            )

    def record_search_coverage(self, terminos_encontrados: int, total_terminos: int):
        """Registra cobertura de búsqueda"""
        if total_terminos > 0:
            cobertura = terminos_encontrados / total_terminos
            self.record_metric(
                "cobertura_busqueda",
                cobertura,
                {
                    "terminos_encontrados": terminos_encontrados,
                    "total_terminos": total_terminos,
                },
            )

    def record_ranking_precision(
        self, resultados_relevantes: int, total_resultados: int
    ):
        """Registra precisión del ranking"""
        if total_resultados > 0:
            precision = resultados_relevantes / total_resultados
            self.record_metric(
                "precision_ranking",
                precision,
                {
                    "resultados_relevantes": resultados_relevantes,
                    "total_resultados": total_resultados,
                },
            )

    def get_metric_summary(self, nombre: str) -> Optional[MetricSummary]:
        """Obtiene resumen de una métrica"""
        if nombre not in self.metrics or not self.metrics[nombre]:
            return None

        values = [mp.value for mp in self.metrics[nombre]]

        return MetricSummary(
            nombre=nombre,
            valor_actual=values[-1] if values else 0.0,
            valor_promedio=statistics.mean(values) if values else 0.0,
            valor_minimo=min(values) if values else 0.0,
            valor_maximo=max(values) if values else 0.0,
            p95=(
                statistics.quantiles(values, n=20)[18]
                if len(values) >= 20
                else values[-1] if values else 0.0
            ),
            p99=(
                statistics.quantiles(values, n=100)[98]
                if len(values) >= 100
                else values[-1] if values else 0.0
            ),
            num_muestras=len(values),
            ultima_actualizacion=(
                self.metrics[nombre][-1].timestamp
                if self.metrics[nombre]
                else datetime.now()
            ),
        )

    def get_all_summaries(self) -> Dict[str, MetricSummary]:
        """Obtiene resúmenes de todas las métricas"""
        summaries = {}
        for nombre in self.metrics.keys():
            summary = self.get_metric_summary(nombre)
            if summary:
                summaries[nombre] = summary
        return summaries

    def get_latency_p95(self, componente: str = None) -> float:
        """Obtiene latencia p95 de un componente o general"""
        if componente:
            metric_name = f"latencia_{componente}"
        else:
            # Calcular p95 de todas las latencias
            all_latencies = []
            for nombre, metric_points in self.metrics.items():
                if nombre.startswith("latencia_"):
                    all_latencies.extend([mp.value for mp in metric_points])

            if not all_latencies:
                return 0.0

            return (
                statistics.quantiles(all_latencies, n=20)[18]
                if len(all_latencies) >= 20
                else all_latencies[-1]
            )

        summary = self.get_metric_summary(metric_name)
        return summary.p95 if summary else 0.0

    def get_citation_metrics(self) -> Dict[str, float]:
        """Obtiene métricas relacionadas con citas"""
        metrics = {}

        # Cobertura de citas
        cobertura_summary = self.get_metric_summary("cobertura_citas")
        if cobertura_summary:
            metrics["cobertura_citas"] = cobertura_summary.valor_actual
            metrics["cobertura_citas_p95"] = cobertura_summary.p95

        # Calidad de respuestas
        calidad_summary = self.get_metric_summary("calidad_respuestas")
        if calidad_summary:
            metrics["calidad_respuestas"] = calidad_summary.valor_actual
            metrics["calidad_respuestas_p95"] = calidad_summary.p95

        return metrics

    def get_performance_metrics(self) -> Dict[str, float]:
        """Obtiene métricas de rendimiento"""
        metrics = {}

        # Latencia p95 general
        metrics["latencia_p95"] = self.get_latency_p95()

        # Latencias por componente
        for nombre in self.metrics.keys():
            if nombre.startswith("latencia_"):
                componente = nombre.replace("latencia_", "")
                summary = self.get_metric_summary(nombre)
                if summary:
                    metrics[f"latencia_{componente}_p95"] = summary.p95
                    metrics[f"latencia_{componente}_promedio"] = summary.valor_promedio

        return metrics

    def get_quality_metrics(self) -> Dict[str, float]:
        """Obtiene métricas de calidad"""
        metrics = {}

        # Cobertura de búsqueda
        cobertura_summary = self.get_metric_summary("cobertura_busqueda")
        if cobertura_summary:
            metrics["cobertura_busqueda"] = cobertura_summary.valor_actual

        # Precisión de ranking
        precision_summary = self.get_metric_summary("precision_ranking")
        if precision_summary:
            metrics["precision_ranking"] = precision_summary.valor_actual

        # Tasa de preprints filtrados
        preprint_summary = self.get_metric_summary("tasa_preprints_filtrados")
        if preprint_summary:
            metrics["tasa_preprints_filtrados"] = preprint_summary.valor_actual

        return metrics

    def generate_report(self) -> Dict[str, Any]:
        """Genera reporte completo de métricas"""
        uptime = datetime.now() - self.start_time

        report = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": uptime.total_seconds(),
            "num_metrics": len(self.metrics),
            "total_samples": sum(
                len(metric_points) for metric_points in self.metrics.values()
            ),
            "performance": self.get_performance_metrics(),
            "quality": self.get_quality_metrics(),
            "citations": self.get_citation_metrics(),
            "summaries": {
                nombre: {
                    "valor_actual": summary.valor_actual,
                    "valor_promedio": summary.valor_promedio,
                    "p95": summary.p95,
                    "num_muestras": summary.num_muestras,
                }
                for nombre, summary in self.get_all_summaries().items()
            },
        }

        return report

    def export_metrics(self, filename: str = None) -> str:
        """Exporta métricas a JSON"""
        if not filename:
            filename = f"rag_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Preparar datos para exportación
        export_data = {
            "metadata": {
                "start_time": self.start_time.isoformat(),
                "export_time": datetime.now().isoformat(),
                "window_size": self.window_size,
            },
            "metrics": {},
            "summaries": self.get_all_summaries(),
        }

        # Exportar puntos de métricas
        for nombre, metric_points in self.metrics.items():
            export_data["metrics"][nombre] = [
                {
                    "timestamp": mp.timestamp.isoformat(),
                    "value": mp.value,
                    "metadata": mp.metadata,
                }
                for mp in metric_points
            ]

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Métricas exportadas a: {filename}")
        return filename

    def reset_metrics(self):
        """Resetea todas las métricas"""
        self.metrics.clear()
        self.metadata.clear()
        self.start_time = datetime.now()
        logger.info("🔄 Métricas reseteadas")


class ObservabilitySystem:
    """Sistema de observabilidad integrado"""

    def __init__(self, langfuse_secret_key: str = None, wandb_project: str = None):
        self.metrics_collector = MetricsCollector()
        self.rag_tracing = None

        # Importar sistema de trazabilidad si está disponible
        try:
            from rag_tracing_system import RAGTracingSystem

            self.rag_tracing = RAGTracingSystem(langfuse_secret_key, wandb_project)
            logger.info("✅ Sistema de observabilidad completo inicializado")
        except ImportError:
            logger.warning("⚠️ Sistema de trazabilidad no disponible")

    def start_operation(self, operation_name: str, **kwargs) -> str:
        """Inicia una operación con trazabilidad completa"""
        trace_id = None

        if self.rag_tracing:
            consulta = kwargs.get("consulta", operation_name)
            trace_id = self.rag_tracing.start_trace(consulta)

        # Registrar inicio de operación
        self.metrics_collector.record_metric(
            f"operacion_{operation_name}_inicio",
            1.0,
            {"operation": operation_name, "trace_id": trace_id, **kwargs},
        )

        return trace_id

    def end_operation(
        self, trace_id: str, resultados: Dict[str, Any], metricas: Dict[str, float]
    ):
        """Finaliza una operación"""
        if self.rag_tracing:
            self.rag_tracing.end_trace(trace_id, resultados, metricas)

        # Registrar métricas finales
        for nombre, valor in metricas.items():
            self.metrics_collector.record_metric(nombre, valor)

    def record_component_operation(
        self,
        trace_id: str,
        component_name: str,
        entrada: Dict[str, Any],
        salida: Dict[str, Any],
        latencia: float,
        metricas: Dict[str, float],
    ):
        """Registra operación de un componente"""
        if self.rag_tracing:
            component_id = self.rag_tracing.trace_component(
                trace_id, component_name, entrada
            )
            self.rag_tracing.end_component(component_id, salida, metricas)

        # Registrar métricas del componente
        self.metrics_collector.record_latency(component_name, latencia)
        for nombre, valor in metricas.items():
            self.metrics_collector.record_metric(f"{component_name}_{nombre}", valor)

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Obtiene reporte completo de observabilidad"""
        report = {
            "metrics": self.metrics_collector.generate_report(),
            "tracing": {
                "available": self.rag_tracing is not None,
                "num_traces": len(self.rag_tracing.traces) if self.rag_tracing else 0,
            },
        }

        return report


# Instancia global para uso en otros módulos
metrics_collector = MetricsCollector()
observability_system = ObservabilitySystem()
