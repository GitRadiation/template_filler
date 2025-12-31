"""
Vistas de la aplicación documentos.

Define las vistas para:
- Subida de archivos (UploadView)
- Consulta de estado (StatusView)
- Descarga de documentos (DownloadView)
"""

import json
import logging

from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import DocumentJob
from .services import DocumentService

logger = logging.getLogger(__name__)


class UploadView(View):
    """
    Vista para subir archivos y crear trabajos de documento.
    
    GET: Muestra el formulario de subida
    POST: Procesa la subida y crea un trabajo
    """
    
    def get(self, request):
        """Muestra el formulario de subida con Drag&Drop."""
        return render(request, 'documentos/upload.html', {
            'templates': settings.SUPPORTED_DOCUMENT_TYPES.keys(),
        })
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """
        Procesa la subida de archivo y crea un trabajo de documento.
        
        Espera:
            - template_name: Tipo de plantilla
            - file: Archivo JSON (opcional)
            - data: JSON directamente en el body (si no hay archivo)
        
        Retorna:
            JSON con id del trabajo y status
        """
        try:
            template_name = request.POST.get('template_name')
            
            # Validar template_name
            if not template_name or template_name not in settings.SUPPORTED_DOCUMENT_TYPES:
                return JsonResponse({
                    'error': f'Plantilla no soportada: {template_name}',
                    'supported': list(settings.SUPPORTED_DOCUMENT_TYPES.keys())
                }, status=400)
            
            # Obtener datos de entrada
            input_data = {}
            input_file = request.FILES.get('file')
            
            # Si se envía un archivo, leerlo como JSON
            if input_file:
                try:
                    file_content = input_file.read().decode('utf-8')
                    input_data = json.loads(file_content)
                except json.JSONDecodeError as e:
                    return JsonResponse({
                        'error': f'Archivo JSON inválido: {str(e)}'
                    }, status=400)
            else:
                # Intentar obtener datos del POST
                data_json = request.POST.get('data')
                if data_json:
                    try:
                        input_data = json.loads(data_json)
                    except json.JSONDecodeError as e:
                        return JsonResponse({
                            'error': f'JSON inválido: {str(e)}'
                        }, status=400)
            
            # Crear el trabajo
            job = DocumentService.create_job(
                template_name=template_name,
                input_data=input_data,
                input_file=input_file
            )
            
            # Enviar a Celery
            DocumentService.send_to_celery(job)
            
            logger.info(f'Trabajo creado y enviado a Celery: {job.id}')
            
            return JsonResponse({
                'success': True,
                'job_id': str(job.id),
                'status': job.status,
                'message': 'Documento en proceso de generación'
            }, status=201)
        
        except Exception as e:
            logger.error(f'Error en UploadView: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': str(e)
            }, status=500)


class StatusView(View):
    """
    Vista para consultar el estado de un trabajo.
    
    GET: Retorna el estado del trabajo en formato JSON
    """
    
    def get(self, request, job_id):
        """
        Obtiene el estado de un trabajo.
        
        Args:
            job_id: ID del trabajo
        
        Retorna:
            JSON con estado del trabajo
        """
        try:
            status = DocumentService.get_job_status(job_id)
            
            if not status:
                return JsonResponse({
                    'error': 'Trabajo no encontrado'
                }, status=404)
            
            return JsonResponse(status)
        
        except Exception as e:
            logger.error(f'Error en StatusView: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': str(e)
            }, status=500)


class DownloadView(View):
    """
    Vista para descargar el documento generado.
    
    GET: Descarga el archivo PDF/DOCX/JSON generado
    """
    
    def get(self, request, job_id):
        """
        Descarga el documento generado.
        
        Args:
            job_id: ID del trabajo
        
        Retorna:
            FileResponse con el archivo generado
        """
        try:
            job = get_object_or_404(DocumentJob, id=job_id)
            
            # Verificar que el trabajo está completado
            if not job.is_completed():
                return JsonResponse({
                    'error': f'Documento aún no está listo. Estado: {job.status}'
                }, status=400)
            
            # Verificar que hay archivo de salida
            if not job.output_file:
                return JsonResponse({
                    'error': 'Archivo de salida no encontrado'
                }, status=404)
            
            # Descargar el archivo
            response = FileResponse(job.output_file.open('rb'))
            response['Content-Disposition'] = f'attachment; filename="{job.id}.pdf"'
            
            logger.info(f'Documento descargado: {job_id}')
            return response
        
        except DocumentJob.DoesNotExist:
            return JsonResponse({
                'error': 'Trabajo no encontrado'
            }, status=404)
        
        except Exception as e:
            logger.error(f'Error en DownloadView: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': str(e)
            }, status=500)


class ListJobsView(View):
    """
    Vista para listar trabajos (para debugging y monitoreo).
    
    GET: Retorna lista de trabajos recientes
    """
    
    def get(self, request):
        """
        Lista trabajos con filtros opcionales.
        
        Parámetros opcionales:
            - status: Filtrar por estado
            - template: Filtrar por tipo de plantilla
            - limit: Número de resultados (default: 50)
        
        Retorna:
            JSON con lista de trabajos
        """
        try:
            status = request.GET.get('status')
            template_name = request.GET.get('template')
            limit = int(request.GET.get('limit', 50))
            
            jobs = DocumentService.list_jobs(
                status=status,
                template_name=template_name,
                limit=limit
            )
            
            jobs_data = [
                {
                    'id': str(job.id),
                    'template_name': job.template_name,
                    'status': job.status,
                    'created_at': job.created_at.isoformat(),
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                }
                for job in jobs
            ]
            
            return JsonResponse({
                'count': len(jobs_data),
                'jobs': jobs_data
            })
        
        except Exception as e:
            logger.error(f'Error en ListJobsView: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': str(e)
            }, status=500)
