#!/usr/bin/env python3
"""
Sistema de Trazabilidad RAG con Langfuse
Guarda consultas, documentos, chunks, similitudes y latencias
"""

import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import hashlib

try:
    from langfuse import Langfuse

    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logging.warning("Langfuse no disponible. La trazabilidad estará limitada.")

try:
    import wandb

    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False
    logging.warning("Weights & Biases no disponible. Las métricas no se enviarán.")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RAGTrace:
    """Estructura para trazar operaciones RAG"""

    trace_id: str
    consulta: str
    timestamp: datetime
    latencia_total: float
    componentes: Dict[str, Any]
    resultados: Dict[str, Any]
    metricas: Dict[str, float]
    errores: List[str] = None


@dataclass
class ComponentTrace:
    """Trazabilidad de componentes individuales"""

    nombre: str
    inicio: datetime
    fin: datetime
    latencia: float
    entrada: Dict[str, Any]
    salida: Dict[str, Any]
    metricas: Dict[str, float]
    errores: List[str] = None


class RAGTracingSystem:
    """Sistema de trazabilidad RAG con Langfuse y W&B"""

    def __init__(self, langfuse_secret_key: str = None, wandb_project: str = None):
        self.traces: List[RAGTrace] = []
        self.component_traces: List[ComponentTrace] = []

        # Inicializar Langfuse
        if LANGFUSE_AVAILABLE and langfuse_secret_key:
            self.langfuse = Langfuse(
                secret_key=langfuse_secret_key, host="https://cloud.langfuse.com"
            )
            logger.info("✅ Langfuse inicializado para trazabilidad")
        else:
            self.langfuse = None
            logger.warning("⚠️ Langfuse no disponible - trazabilidad limitada")

        # Inicializar W&B
        if WANDB_AVAILABLE and wandb_project:
            wandb.init(project=wandb_project)
            self.wandb = wandb
            logger.info("✅ Weights & Biases inicializado para métricas")
        else:
            self.wandb = None
            logger.warning("⚠️ Weights & Biases no disponible - métricas no enviadas")

    def start_trace(self, consulta: str) -> str:
        """Inicia un nuevo trace RAG"""
        trace_id = hashlib.md5(f"{consulta}_{time.time()}".encode()).hexdigest()[:12]

        trace = RAGTrace(
            trace_id=trace_id,
            consulta=consulta,
            timestamp=datetime.now(),
            latencia_total=0.0,
            componentes={},
            resultados={},
            metricas={},
            errores=[],
        )

        self.traces.append(trace)

        # Crear trace en Langfuse
        if self.langfuse:
            try:
                self.langfuse.trace(
                    id=trace_id,
                    name="RAG Pipeline",
                    input={"consulta": consulta},
                    metadata={"tipo": "rag_pipeline"},
                )
            except Exception as e:
                logger.error(f"Error creando trace en Langfuse: {e}")

        logger.info(f"🔍 Trace iniciado: {trace_id}")
        return trace_id

    def end_trace(
        self, trace_id: str, resultados: Dict[str, Any], metricas: Dict[str, float]
    ):
        """Finaliza un trace RAG"""
        trace = self._find_trace(trace_id)
        if not trace:
            logger.error(f"Trace no encontrado: {trace_id}")
            return

        # Calcular latencia total
        trace.latencia_total = (datetime.now() - trace.timestamp).total_seconds()
        trace.resultados = resultados
        trace.metricas = metricas

        # Actualizar trace en Langfuse
        if self.langfuse:
            try:
                self.langfuse.trace(
                    id=trace_id,
                    output=resultados,
                    metadata={
                        "latencia_total": trace.latencia_total,
                        "metricas": metricas,
                        "num_componentes": len(trace.componentes),
                    },
                )
            except Exception as e:
                logger.error(f"Error actualizando trace en Langfuse: {e}")

        # Enviar métricas a W&B
        if self.wandb:
            try:
                self.wandb.log(
                    {
                        "latencia_total": trace.latencia_total,
                        "num_componentes": len(trace.componentes),
                        **metricas,
                    }
                )
            except Exception as e:
                logger.error(f"Error enviando métricas a W&B: {e}")

        logger.info(
            f"✅ Trace finalizado: {trace_id} - Latencia: {trace.latencia_total:.2f}s"
        )

    def trace_component(
        self, trace_id: str, nombre: str, entrada: Dict[str, Any]
    ) -> str:
        """Inicia trazabilidad de un componente"""
        component_id = f"{trace_id}_{nombre}_{int(time.time())}"

        component_trace = ComponentTrace(
            nombre=nombre,
            inicio=datetime.now(),
            fin=None,
            latencia=0.0,
            entrada=entrada,
            salida={},
            metricas={},
            errores=[],
        )

        self.component_traces.append(component_trace)

        # Crear span en Langfuse
        if self.langfuse:
            try:
                self.langfuse.span(
                    id=component_id, trace_id=trace_id, name=nombre, input=entrada
                )
            except Exception as e:
                logger.error(f"Error creando span en Langfuse: {e}")

        logger.debug(f"🔧 Componente iniciado: {nombre} en trace {trace_id}")
        return component_id

    def end_component(
        self, component_id: str, salida: Dict[str, Any], metricas: Dict[str, float]
    ):
        """Finaliza trazabilidad de un componente"""
        component_trace = self._find_component_trace(component_id)
        if not component_trace:
            logger.error(f"Componente no encontrado: {component_id}")
            return

        component_trace.fin = datetime.now()
        component_trace.latencia = (
            component_trace.fin - component_trace.inicio
        ).total_seconds()
        component_trace.salida = salida
        component_trace.metricas = metricas

        # Actualizar span en Langfuse
        if self.langfuse:
            try:
                self.langfuse.span(
                    id=component_id,
                    output=salida,
                    metadata={"latencia": component_trace.latencia, **metricas},
                )
            except Exception as e:
                logger.error(f"Error actualizando span en Langfuse: {e}")

        logger.debug(
            f"✅ Componente finalizado: {component_trace.nombre} - Latencia: {component_trace.latencia:.2f}s"
        )

    def trace_search(
        self,
        trace_id: str,
        terminos: List[str],
        resultados: List[Dict],
        latencia: float,
    ):
        """Traza operación de búsqueda"""
        component_id = self.trace_component(
            trace_id, "search", {"terminos": terminos, "num_terminos": len(terminos)}
        )

        metricas = {
            "num_resultados": len(resultados),
            "latencia_busqueda": latencia,
            "cobertura_terminos": len(set(terminos)) / len(terminos) if terminos else 0,
        }

        self.end_component(
            component_id,
            {"resultados": resultados, "num_resultados": len(resultados)},
            metricas,
        )

    def trace_filtering(
        self,
        trace_id: str,
        resultados_antes: int,
        resultados_despues: int,
        latencia: float,
    ):
        """Traza operación de filtrado"""
        component_id = self.trace_component(
            trace_id, "filtering", {"resultados_antes": resultados_antes}
        )

        metricas = {
            "resultados_filtrados": resultados_despues,
            "tasa_filtrado": (
                1 - (resultados_despues / resultados_antes)
                if resultados_antes > 0
                else 0
            ),
            "latencia_filtrado": latencia,
        }

        self.end_component(
            component_id, {"resultados_despues": resultados_despues}, metricas
        )

    def trace_ranking(self, trace_id: str, resultados: List[Dict], latencia: float):
        """Traza operación de ranking"""
        component_id = self.trace_component(
            trace_id, "ranking", {"num_resultados": len(resultados)}
        )

        # Calcular métricas de ranking
        scores = [r.get("relevancia_score", 0) for r in resultados]
        metricas = {
            "score_promedio": sum(scores) / len(scores) if scores else 0,
            "score_maximo": max(scores) if scores else 0,
            "score_minimo": min(scores) if scores else 0,
            "latencia_ranking": latencia,
        }

        self.end_component(component_id, {"resultados_ranked": resultados}, metricas)

    def trace_chunking(
        self, trace_id: str, resultados: List[Dict], chunks: List[Dict], latencia: float
    ):
        """Traza operación de chunking"""
        component_id = self.trace_component(
            trace_id, "chunking", {"num_resultados": len(resultados)}
        )

        metricas = {
            "num_chunks": len(chunks),
            "chunks_por_resultado": len(chunks) / len(resultados) if resultados else 0,
            "latencia_chunking": latencia,
        }

        self.end_component(
            component_id, {"chunks": chunks, "num_chunks": len(chunks)}, metricas
        )

    def trace_citation_assignment(
        self,
        trace_id: str,
        oraciones: List[str],
        citas_asignadas: List[Dict],
        latencia: float,
    ):
        """Traza asignación de citas"""
        component_id = self.trace_component(
            trace_id, "citation_assignment", {"num_oraciones": len(oraciones)}
        )

        # Calcular métricas de citas
        oraciones_con_citas = sum(1 for c in citas_asignadas if c.get("citations"))
        total_citas = sum(len(c.get("citations", [])) for c in citas_asignadas)

        metricas = {
            "oraciones_con_citas": oraciones_con_citas,
            "total_citas": total_citas,
            "citas_por_oracion": total_citas / len(oraciones) if oraciones else 0,
            "cobertura_citas": oraciones_con_citas / len(oraciones) if oraciones else 0,
            "latencia_citas": latencia,
        }

        self.end_component(component_id, {"citas_asignadas": citas_asignadas}, metricas)

    def calculate_metrics(self, trace_id: str) -> Dict[str, float]:
        """Calcula métricas agregadas para un trace"""
        trace = self._find_trace(trace_id)
        if not trace:
            return {}

        # Obtener componentes del trace
        components = [
            ct for ct in self.component_traces if ct.nombre in trace.componentes
        ]

        metricas = {
            "latencia_total": trace.latencia_total,
            "num_componentes": len(components),
            "latencia_promedio_componente": (
                sum(c.latencia for c in components) / len(components)
                if components
                else 0
            ),
            "errores_totales": len(trace.errores) if trace.errores else 0,
        }

        # Métricas específicas por componente
        for component in components:
            if component.nombre == "search":
                metricas.update(
                    {
                        "cobertura_busqueda": component.metricas.get(
                            "cobertura_terminos", 0
                        ),
                        "resultados_busqueda": component.metricas.get(
                            "num_resultados", 0
                        ),
                    }
                )
            elif component.nombre == "filtering":
                metricas.update(
                    {"tasa_filtrado": component.metricas.get("tasa_filtrado", 0)}
                )
            elif component.nombre == "citation_assignment":
                metricas.update(
                    {
                        "respuestas_con_citas": component.metricas.get(
                            "cobertura_citas", 0
                        ),
                        "oraciones_con_soporte": (
                            component.metricas.get("oraciones_con_citas", 0)
                            / len(trace.consulta.split())
                            if trace.consulta
                            else 0
                        ),
                    }
                )

        return metricas

    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """Obtiene resumen completo de un trace"""
        trace = self._find_trace(trace_id)
        if not trace:
            return {}

        components = [
            ct for ct in self.component_traces if ct.nombre in trace.componentes
        ]

        return {
            "trace_id": trace_id,
            "consulta": trace.consulta,
            "timestamp": trace.timestamp.isoformat(),
            "latencia_total": trace.latencia_total,
            "num_componentes": len(components),
            "metricas": trace.metricas,
            "errores": trace.errores,
            "componentes": [
                {
                    "nombre": c.nombre,
                    "latencia": c.latencia,
                    "metricas": c.metricas,
                    "errores": c.errores,
                }
                for c in components
            ],
        }

    def export_traces(self, filename: str = None) -> str:
        """Exporta todos los traces a JSON"""
        if not filename:
            filename = f"rag_traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        traces_data = []
        for trace in self.traces:
            trace_data = asdict(trace)
            trace_data["timestamp"] = trace.timestamp.isoformat()
            traces_data.append(trace_data)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(traces_data, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Traces exportados a: {filename}")
        return filename

    def _find_trace(self, trace_id: str) -> Optional[RAGTrace]:
        """Encuentra un trace por ID"""
        for trace in self.traces:
            if trace.trace_id == trace_id:
                return trace
        return None

    def _find_component_trace(self, component_id: str) -> Optional[ComponentTrace]:
        """Encuentra un componente trace por ID"""
        for component in self.component_traces:
            if component.nombre in component_id:
                return component
        return None


# Instancia global para uso en otros módulos
rag_tracing = RAGTracingSystem()
