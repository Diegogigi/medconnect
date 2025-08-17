#!/usr/bin/env python3
"""
Módulo para manejo de sesiones en MedConnect
Permite registrar, consultar y gestionar sesiones asociadas a atenciones (1-15 sesiones)
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configurar logging
logger = logging.getLogger(__name__)

class SesionesManager:
    """Gestor de sesiones para atenciones médicas"""
    
    def __init__(self, sheets_client=None, spreadsheet_id=None):
        self.sheets_client = sheets_client
        self.spreadsheet_id = spreadsheet_id
        self.max_sesiones = 15  # Límite máximo de sesiones por atención
        
    def verificar_limite_sesiones(self, atencion_id: str) -> Dict:
        """Verifica si una atención puede tener más sesiones"""
        try:
            sesiones = self.get_sesiones_atencion(atencion_id)
            num_sesiones = len(sesiones)
            
            return {
                'puede_agregar': num_sesiones < self.max_sesiones,
                'sesiones_actuales': num_sesiones,
                'limite': self.max_sesiones,
                'sesiones_disponibles': self.max_sesiones - num_sesiones
            }
        except Exception as e:
            logger.error(f"Error verificando límite de sesiones: {e}")
            return {
                'puede_agregar': False,
                'sesiones_actuales': 0,
                'limite': self.max_sesiones,
                'sesiones_disponibles': 0,
                'error': str(e)
            }
    
    def get_sesiones_atencion(self, atencion_id: str) -> List[Dict]:
        """Obtiene todas las sesiones de una atención"""
        try:
            if not self.sheets_client:
                logger.error("Cliente de Google Sheets no disponible")
                return []
            
            # Obtener datos de la hoja de sesiones
            range_name = 'Sesiones!A:N'
            result = self.sheets_client.values().get(
                spreadsheetId=self.spreadsheet_id, 
                range=range_name
            ).execute()
            values = result.get('values', [])
            
            sesiones = []
            for row in values[1:]:  # Saltar encabezados
                if len(row) >= 14 and row[1] == atencion_id:  # Columna B es atencion_id
                    sesion = {
                        'id': row[0],
                        'atencion_id': row[1],
                        'fecha_sesion': row[2],
                        'duracion': int(row[3]) if row[3].isdigit() else 0,
                        'tipo_sesion': row[4],
                        'objetivos': row[5],
                        'actividades': row[6],
                        'observaciones': row[7] if len(row) > 7 else '',
                        'progreso': row[8] if len(row) > 8 else '',
                        'estado': row[9] if len(row) > 9 else '',
                        'recomendaciones': row[10] if len(row) > 10 else '',
                        'proxima_sesion': row[11] if len(row) > 11 else '',
                        'fecha_creacion': row[12] if len(row) > 12 else '',
                        'profesional_id': row[13] if len(row) > 13 else ''
                    }
                    sesiones.append(sesion)
            
            # Ordenar por fecha de sesión (más reciente primero)
            sesiones.sort(key=lambda x: x.get('fecha_sesion', ''), reverse=True)
            
            return sesiones
            
        except Exception as e:
            logger.error(f"Error obteniendo sesiones de atención {atencion_id}: {e}")
            return []
    
    def get_sesion_by_id(self, sesion_id: str) -> Optional[Dict]:
        """Obtiene una sesión específica por ID"""
        try:
            if not self.sheets_client:
                logger.error("Cliente de Google Sheets no disponible")
                return None
            
            # Obtener datos de la hoja de sesiones
            range_name = 'Sesiones!A:N'
            result = self.sheets_client.values().get(
                spreadsheetId=self.spreadsheet_id, 
                range=range_name
            ).execute()
            values = result.get('values', [])
            
            for row in values[1:]:  # Saltar encabezados
                if len(row) >= 1 and row[0] == sesion_id:
                    return {
                        'id': row[0],
                        'atencion_id': row[1],
                        'fecha_sesion': row[2],
                        'duracion': int(row[3]) if row[3].isdigit() else 0,
                        'tipo_sesion': row[4],
                        'objetivos': row[5],
                        'actividades': row[6],
                        'observaciones': row[7] if len(row) > 7 else '',
                        'progreso': row[8] if len(row) > 8 else '',
                        'estado': row[9] if len(row) > 9 else '',
                        'recomendaciones': row[10] if len(row) > 10 else '',
                        'proxima_sesion': row[11] if len(row) > 11 else '',
                        'fecha_creacion': row[12] if len(row) > 12 else '',
                        'profesional_id': row[13] if len(row) > 13 else ''
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo sesión {sesion_id}: {e}")
            return None
    
    def guardar_sesion(self, sesion_data: Dict) -> Dict:
        """Guarda una nueva sesión"""
        try:
            # Verificar límite de sesiones
            limite_info = self.verificar_limite_sesiones(sesion_data['atencion_id'])
            if not limite_info['puede_agregar']:
                return {
                    'success': False,
                    'message': f'Límite máximo de {self.max_sesiones} sesiones alcanzado'
                }
            
            # Crear nueva sesión
            nueva_sesion = {
                'id': str(uuid.uuid4()),
                'atencion_id': sesion_data['atencion_id'],
                'fecha_sesion': sesion_data['fecha_sesion'],
                'duracion': sesion_data['duracion'],
                'tipo_sesion': sesion_data['tipo_sesion'],
                'objetivos': sesion_data['objetivos'],
                'actividades': sesion_data['actividades'],
                'observaciones': sesion_data.get('observaciones', ''),
                'progreso': sesion_data['progreso'],
                'estado': sesion_data['estado'],
                'recomendaciones': sesion_data.get('recomendaciones', ''),
                'proxima_sesion': sesion_data.get('proxima_sesion', ''),
                'fecha_creacion': datetime.now().isoformat(),
                'profesional_id': sesion_data.get('profesional_id', '')
            }
            
            # Guardar en Google Sheets
            if self.guardar_sesion_sheets(nueva_sesion):
                logger.info(f"Sesión guardada exitosamente: {nueva_sesion['id']}")
                return {
                    'success': True,
                    'message': 'Sesión registrada exitosamente',
                    'sesion_id': nueva_sesion['id']
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al guardar en Google Sheets'
                }
                
        except Exception as e:
            logger.error(f"Error guardando sesión: {e}")
            return {
                'success': False,
                'message': f'Error interno: {str(e)}'
            }
    
    def eliminar_sesion(self, sesion_id: str) -> Dict:
        """Elimina una sesión"""
        try:
            # Verificar que la sesión existe
            sesion = self.get_sesion_by_id(sesion_id)
            if not sesion:
                return {
                    'success': False,
                    'message': 'Sesión no encontrada'
                }
            
            # Eliminar de Google Sheets
            if self.eliminar_sesion_sheets(sesion_id):
                logger.info(f"Sesión eliminada exitosamente: {sesion_id}")
                return {
                    'success': True,
                    'message': 'Sesión eliminada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al eliminar de Google Sheets'
                }
                
        except Exception as e:
            logger.error(f"Error eliminando sesión: {e}")
            return {
                'success': False,
                'message': f'Error interno: {str(e)}'
            }
    
    def actualizar_sesion(self, sesion_id: str, sesion_data: Dict) -> Dict:
        """Actualiza una sesión existente"""
        try:
            # Verificar que la sesión existe
            sesion_actual = self.get_sesion_by_id(sesion_id)
            if not sesion_actual:
                return {
                    'success': False,
                    'message': 'Sesión no encontrada'
                }
            
            # Actualizar datos
            sesion_actual.update({
                'fecha_sesion': sesion_data.get('fecha_sesion', sesion_actual['fecha_sesion']),
                'duracion': sesion_data.get('duracion', sesion_actual['duracion']),
                'tipo_sesion': sesion_data.get('tipo_sesion', sesion_actual['tipo_sesion']),
                'objetivos': sesion_data.get('objetivos', sesion_actual['objetivos']),
                'actividades': sesion_data.get('actividades', sesion_actual['actividades']),
                'observaciones': sesion_data.get('observaciones', sesion_actual.get('observaciones', '')),
                'progreso': sesion_data.get('progreso', sesion_actual['progreso']),
                'estado': sesion_data.get('estado', sesion_actual['estado']),
                'recomendaciones': sesion_data.get('recomendaciones', sesion_actual.get('recomendaciones', '')),
                'proxima_sesion': sesion_data.get('proxima_sesion', sesion_actual.get('proxima_sesion', '')),
                'fecha_actualizacion': datetime.now().isoformat()
            })
            
            # Actualizar en Google Sheets
            if self.actualizar_sesion_sheets(sesion_actual):
                logger.info(f"Sesión actualizada exitosamente: {sesion_id}")
                return {
                    'success': True,
                    'message': 'Sesión actualizada exitosamente'
                }
            else:
                return {
                    'success': False,
                    'message': 'Error al actualizar en Google Sheets'
                }
                
        except Exception as e:
            logger.error(f"Error actualizando sesión: {e}")
            return {
                'success': False,
                'message': f'Error interno: {str(e)}'
            }
    
    def guardar_sesion_sheets(self, sesion: Dict) -> bool:
        """Guarda sesión en Google Sheets"""
        try:
            if not self.sheets_client:
                logger.error("Cliente de Google Sheets no disponible")
                return False
            
            # Preparar datos para insertar
            row_data = [
                sesion['id'],
                sesion['atencion_id'],
                sesion['fecha_sesion'],
                str(sesion['duracion']),
                sesion['tipo_sesion'],
                sesion['objetivos'],
                sesion['actividades'],
                sesion['observaciones'],
                sesion['progreso'],
                sesion['estado'],
                sesion['recomendaciones'],
                sesion['proxima_sesion'],
                sesion['fecha_creacion'],
                sesion['profesional_id']
            ]
            
            # Insertar en la hoja de sesiones
            range_name = 'Sesiones!A:N'
            body = {
                'values': [row_data]
            }
            
            result = self.sheets_client.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"Sesión guardada en Sheets: {sesion['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando sesión en Sheets: {e}")
            return False
    
    def eliminar_sesion_sheets(self, sesion_id: str) -> bool:
        """Elimina sesión de Google Sheets"""
        try:
            if not self.sheets_client:
                logger.error("Cliente de Google Sheets no disponible")
                return False
            
            # Buscar la fila de la sesión
            range_name = 'Sesiones!A:A'
            result = self.sheets_client.values().get(
                spreadsheetId=self.spreadsheet_id, 
                range=range_name
            ).execute()
            values = result.get('values', [])
            
            # Encontrar la fila que contiene el sesion_id
            row_number = None
            for i, row in enumerate(values):
                if row and row[0] == sesion_id:
                    row_number = i + 1  # +1 porque las filas en Sheets empiezan en 1
                    break
            
            if row_number:
                # Eliminar la fila
                request_body = {
                    'requests': [
                        {
                            'deleteDimension': {
                                'range': {
                                    'sheetId': self.get_sheet_id('Sesiones'),
                                    'dimension': 'ROWS',
                                    'startIndex': row_number - 1,
                                    'endIndex': row_number
                                }
                            }
                        }
                    ]
                }
                
                self.sheets_client.batchUpdate(
                    spreadsheetId=self.spreadsheet_id, 
                    body=request_body
                ).execute()
                
                logger.info(f"Sesión eliminada de Sheets: {sesion_id}")
                return True
            else:
                logger.warning(f"Sesión no encontrada en Sheets: {sesion_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error eliminando sesión de Sheets: {e}")
            return False
    
    def actualizar_sesion_sheets(self, sesion: Dict) -> bool:
        """Actualiza sesión en Google Sheets"""
        try:
            if not self.sheets_client:
                logger.error("Cliente de Google Sheets no disponible")
                return False
            
            # Buscar la fila de la sesión
            range_name = 'Sesiones!A:A'
            result = self.sheets_client.values().get(
                spreadsheetId=self.spreadsheet_id, 
                range=range_name
            ).execute()
            values = result.get('values', [])
            
            # Encontrar la fila que contiene el sesion_id
            row_number = None
            for i, row in enumerate(values):
                if row and row[0] == sesion['id']:
                    row_number = i + 1  # +1 porque las filas en Sheets empiezan en 1
                    break
            
            if row_number:
                # Preparar datos para actualizar
                row_data = [
                    sesion['id'],
                    sesion['atencion_id'],
                    sesion['fecha_sesion'],
                    str(sesion['duracion']),
                    sesion['tipo_sesion'],
                    sesion['objetivos'],
                    sesion['actividades'],
                    sesion['observaciones'],
                    sesion['progreso'],
                    sesion['estado'],
                    sesion['recomendaciones'],
                    sesion['proxima_sesion'],
                    sesion.get('fecha_creacion', ''),
                    sesion.get('profesional_id', ''),
                    sesion.get('fecha_actualizacion', '')
                ]
                
                # Actualizar la fila
                range_name = f'Sesiones!A{row_number}:O{row_number}'
                body = {
                    'values': [row_data]
                }
                
                self.sheets_client.values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                
                logger.info(f"Sesión actualizada en Sheets: {sesion['id']}")
                return True
            else:
                logger.warning(f"Sesión no encontrada en Sheets: {sesion['id']}")
                return False
            
        except Exception as e:
            logger.error(f"Error actualizando sesión en Sheets: {e}")
            return False
    
    def get_sheet_id(self, sheet_name: str) -> Optional[int]:
        """Obtiene el ID de una hoja por nombre"""
        try:
            if not self.sheets_client:
                return None
            
            spreadsheet = self.sheets_client.get(spreadsheetId=self.spreadsheet_id).execute()
            for sheet in spreadsheet['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    return sheet['properties']['sheetId']
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo ID de hoja {sheet_name}: {e}")
            return None

# Instancia global del gestor de sesiones
sesiones_manager = None

def init_sesiones_manager(sheets_client, spreadsheet_id):
    """Inicializa el gestor de sesiones global"""
    global sesiones_manager
    sesiones_manager = SesionesManager(sheets_client, spreadsheet_id)
    logger.info("Gestor de sesiones inicializado")
    return sesiones_manager

def get_sesiones_manager():
    """Obtiene la instancia global del gestor de sesiones"""
    return sesiones_manager 