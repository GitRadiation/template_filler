"""
Views for the documents application.

Defines views for:
- File upload (UploadView)
- Status checking (StatusView)
- Document download (DownloadView)
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
    View for uploading files and creating document jobs.
    
    GET: Shows the upload form
    POST: Processes the upload and creates a job
    """
    
    def get(self, request):
        """Shows the upload form with Drag&Drop."""
        return render(request, 'docs/upload.html', {
            'templates': settings.SUPPORTED_DOCUMENT_TYPES.keys(),
        })
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """
        Processes file upload and creates a document job.
        
        Expects:
            - template_name: Template type
            - file: JSON file (optional)
            - data: JSON directly in the body (if no file)
        
        Returns:
            JSON with job id and status
        """
        try:
            template_name = request.POST.get('template_name')
            
            # Validate template_name
            if not template_name or template_name not in settings.SUPPORTED_DOCUMENT_TYPES:
                return JsonResponse({
                    'error': f'Plantilla no soportada: {template_name}',
                    'supported': list(settings.SUPPORTED_DOCUMENT_TYPES.keys())
                }, status=400)
            
            # Get input data
            input_data = {}
            input_file = request.FILES.get('file')
            
            # If a file is sent, read it as JSON
            if input_file:
                try:
                    file_content = input_file.read().decode('utf-8')
                    input_data = json.loads(file_content)
                except json.JSONDecodeError as e:
                    return JsonResponse({
                        'error': f'Archivo JSON inválido: {str(e)}'
                    }, status=400)
            else:
                # Try to get data from POST
                data_json = request.POST.get('data')
                if data_json:
                    try:
                        input_data = json.loads(data_json)
                    except json.JSONDecodeError as e:
                        return JsonResponse({
                            'error': f'JSON inválido: {str(e)}'
                        }, status=400)
            
            # Create the job
            job = DocumentService.create_job(
                template_name=template_name,
                input_data=input_data,
                input_file=input_file
            )
            
            # Send to Celery
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
    View to check the status of a document job.
    
    GET: Returns the job status as JSON
    """
    
    def get(self, request, job_id):
        """
        Gets the status of a job.
        
        Args:
            job_id: ID of the job
        
        Returns:
            JSON with job status
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
    View to download the generated document.
    
    GET: Returns the generated file for download
    """
    
    def get(self, request, job_id):
        """
        Downloads the generated document.
        
        Args:
            job_id: ID of the job
        
        Returns:
            FileResponse with the generated file
        """
        try:
            job = get_object_or_404(DocumentJob, id=job_id)
            
            # Check if job is completed
            if not job.is_completed():
                return JsonResponse({
                    'error': f'Documento aún no está listo. Estado: {job.status}'
                }, status=400)
            
            # Verify that there is an output file
            if not job.output_file:
                return JsonResponse({
                    'error': 'Archivo de salida no encontrado'
                }, status=404)
            
            # Download the file
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
    View to list jobs (for debugging and monitoring).
    
    GET: Returns list of recent jobs
    """
    
    def get(self, request):
        """
        Lists jobs with optional filters.
        
        Optional parameters:
            - status: Filter by status
            - template: Filter by template type
            - limit: Number of results (default: 50)

        Returns:
            JSON with list of jobs
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


class DeleteJobView(View):
    """
    View to delete jobs.
    
    DELETE: Deletes a job from the database
    """
    
    @method_decorator(csrf_exempt)
    def delete(self, request, job_id):
        """
        Deletes a specified job.
        
        Parameters:
            - job_id: UUID of the job to delete
        
        Returns:
            JSON with confirmation
        """
        try:
            job = get_object_or_404(DocumentJob, id=job_id)
            job.delete()
            
            logger.info(f'Trabajo eliminado: {job_id}')
            
            return JsonResponse({
                'success': True,
                'message': 'Trabajo eliminado exitosamente'
            })
        
        except DocumentJob.DoesNotExist:
            return JsonResponse({
                'error': 'Trabajo no encontrado'
            }, status=404)
        
        except Exception as e:
            logger.error(f'Error en DeleteJobView: {str(e)}', exc_info=True)
            return JsonResponse({
                'error': str(e)
            }, status=500)
