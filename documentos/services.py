"""
Servicios de negocio para la aplicación documentos.

Implementa la lógica de almacenamiento de archivos, envío de tareas y
actualización de estados.
"""

import logging

from django.core.files.base import ContentFile

from .models import DocumentJob

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Servicio para gestionar la generación de documentos.
    
    Maneja:
    - Almacenamiento de archivos de entrada
    - Creación de trabajos de documento
    - Envío de tareas a Celery
    - Actualización de estados
    """
    
    @staticmethod
    def create_job(template_name: str, input_data: dict, input_file=None) -> DocumentJob:
        """
        Crea un nuevo trabajo de generación de documento.
        
        Args:
            template_name: Tipo de plantilla ('contract', 'invoice', 'certificate')
            input_data: Diccionario con los datos para la plantilla
            input_file: Archivo de entrada (opcional)
        
        Returns:
            DocumentJob: El trabajo creado
        """
        job = DocumentJob.objects.create(
            template_name=template_name,
            input_data=input_data,
            status=DocumentJob.Status.PENDING
        )
        
        # Guardar archivo de entrada si se proporciona
        if input_file:
            file_name = f'{job.id}_input.json'
            job.input_file.save(file_name, input_file)
        
        logger.info(f'Trabajo de documento creado: {job.id} ({template_name})')
        return job
    
    @staticmethod
    def send_to_celery(job: DocumentJob):
        """
        Envía un trabajo a Celery para procesamiento asincrónico.
        
        Args:
            job: El trabajo a enviar
        """
        from typing import Any

        from documentos.tasks import generate_pdf_task
        
        # Enviar tarea a Celery
        job_id_str = str(job.id)
        task: Any = generate_pdf_task.apply_async((job_id_str,))  # type: ignore[misc]
        
        # Guardar el ID de la tarea Celery
        job.celery_task_id = task.id
        job.save(update_fields=['celery_task_id'])
        
        logger.info(f'Tarea enviada a Celery: {task.id} para trabajo {job.id}')
    
    @staticmethod
    def get_job_status(job_id: str) -> dict | None:
        """
        Obtiene el estado de un trabajo.
        
        Args:
            job_id: ID del trabajo
        
        Returns:
            dict: Información del estado del trabajo, o None si no existe
        """
        try:
            job = DocumentJob.objects.get(id=job_id)
            return {
                'id': str(job.id),
                'status': job.status,
                'template_name': job.template_name,
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'error_message': job.error_message,
                'output_url': job.output_file.url if job.output_file else None,
            }
        except DocumentJob.DoesNotExist:
            logger.warning(f'Trabajo no encontrado: {job_id}')
            return None
    
    @staticmethod
    def save_output_file(job: DocumentJob, output_content: bytes, file_name: str | None = None):
        """
        Guarda el archivo de salida generado.
        
        Args:
            job: El trabajo
            output_content: Contenido del archivo generado
            file_name: Nombre del archivo (default: {id}.pdf)
        """
        if not file_name:
            file_name = f'{job.id}.pdf'
        
        job.output_file.save(
            file_name,
            ContentFile(output_content),
            save=True
        )
        
        logger.info(f'Archivo de salida guardado: {file_name}')
    
    @staticmethod
    def get_job(job_id: str) -> DocumentJob | None:
        """
        Obtiene un trabajo por ID.
        
        Args:
            job_id: ID del trabajo
        
        Returns:
            DocumentJob o None
        """
        try:
            return DocumentJob.objects.get(id=job_id)
        except DocumentJob.DoesNotExist:
            return None
    
    @staticmethod
    def list_jobs(status: str | None = None, template_name: str | None = None, limit: int = 50) -> list:
        """
        Lista trabajos con filtros opcionales.
        
        Args:
            status: Filtrar por estado
            template_name: Filtrar por tipo de plantilla
            limit: Número máximo de resultados
        
        Returns:
            Lista de trabajos
        """
        queryset = DocumentJob.objects.all()
        
        if status:
            queryset = queryset.filter(status=status)
        
        if template_name:
            queryset = queryset.filter(template_name=template_name)
        
        return list(queryset[:limit])
