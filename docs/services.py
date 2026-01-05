"""
Business services for the documents application.

Provides high-level operations for document generation, including:
- Job creation
- File storage
- Task submission to Celery
- Status retrieval
"""

import logging

from django.conf import settings
from django.core.files.base import ContentFile

from .models import DocumentJob

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service layer for managing document generation jobs.

    Responsibilities:
    - Create and persist document jobs
    - Store input and output files
    - Submit jobs to Celery
    - Retrieve job status and metadata
    """

    # =========================
    # Job creation
    # =========================
    @staticmethod
    def create_job(
        template_name: str,
        input_data: dict,
        input_file=None,
    ) -> DocumentJob:
        """
        Create a new document generation job.

        Args:
            template_name: Template identifier
                ('contract', 'invoice', 'certificate')
            input_data: Dictionary containing template data
            input_file: Optional input JSON file

        Returns:
            The created DocumentJob instance
        """
        job = DocumentJob.objects.create(
            template_name=template_name,
            input_data=input_data,
            status=DocumentJob.Status.PENDING,
        )

        if input_file:
            file_name = f'{job.id}_input.json'
            job.input_file.save(file_name, input_file)

        logger.info(
            'Document job created: %s (template=%s)',
            job.id,
            template_name,
        )

        return job

    # =========================
    # Celery integration
    # =========================
    @staticmethod
    def send_to_celery(job: DocumentJob) -> None:
        """Send the job to the correct Celery task based on the template file extension.

        This inspects SETTINGS.SUPPORTED_DOCUMENT_TYPES to find the actual
        template filename (e.g. 'contract.html.j2' or 'contract.docx') and
        chooses the appropriate task: docx -> generate_docx_task, json ->
        generate_json_task, else -> generate_pdf_task.
        """
        template_file = None
        try:
            template_file = job.template_name and settings.SUPPORTED_DOCUMENT_TYPES.get(job.template_name)
        except Exception:
            template_file = None

        # Fallback to using the template name as filename
        filename = template_file if template_file else job.template_name
        ext = (filename.split('.')[-1].lower() if filename and '.' in filename else '')

        from docs.tasks import generate_docx_task, generate_json_task, generate_pdf_task

        if ext == 'docx':
            task = generate_docx_task.apply_async((str(job.id),))  # type: ignore
        elif ext == 'json':
            task = generate_json_task.apply_async((str(job.id),))  # type: ignore
        else:
            task = generate_pdf_task.apply_async((str(job.id),))  # type: ignore

        job.celery_task_id = task.id
        job.save(update_fields=['celery_task_id'])

    # =========================
    # Status & retrieval
    # =========================
    @staticmethod
    def get_job_status(job_id: str) -> dict | None:
        """
        Retrieve the current status of a document job.

        Args:
            job_id: UUID of the job

        Returns:
            Dictionary with job status information,
            or None if the job does not exist
        """
        try:
            job = DocumentJob.objects.get(id=job_id)
        except DocumentJob.DoesNotExist:
            logger.warning('Document job not found: %s', job_id)
            return None

        return {
            'id': str(job.id),
            'status': job.status,
            'template_name': job.template_name,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': (
                job.completed_at.isoformat() if job.completed_at else None
            ),
            'error_message': job.error_message,
            'output_url': job.output_file.url if job.output_file else None,
        }

    @staticmethod
    def get_job(job_id: str) -> DocumentJob | None:
        """
        Retrieve a DocumentJob by its ID.

        Args:
            job_id: UUID of the job

        Returns:
            DocumentJob instance or None if not found
        """
        try:
            return DocumentJob.objects.get(id=job_id)
        except DocumentJob.DoesNotExist:
            return None

    # =========================
    # Output handling
    # =========================
    @staticmethod
    def save_output_file(
        job: DocumentJob,
        output_content: bytes,
        file_name: str | None = None,
    ) -> None:
        """
        Persist the generated output file for a job.

        Args:
            job: DocumentJob instance
            output_content: Binary content of the generated file
            file_name: Optional filename (defaults to '<job_id>.pdf')
        """
        final_name = file_name or f'{job.id}.pdf'

        job.output_file.save(
            final_name,
            ContentFile(output_content),
            save=True,
        )

        logger.info(
            'Output file saved: %s (job_id=%s)',
            final_name,
            job.id,
        )

    # =========================
    # Query helpers
    # =========================
    @staticmethod
    def list_jobs(
        status: str | None = None,
        template_name: str | None = None,
        limit: int = 50,
    ) -> list[DocumentJob]:
        """
        List document jobs with optional filters.

        Args:
            status: Optional status filter
            template_name: Optional template filter
            limit: Maximum number of results

        Returns:
            List of DocumentJob instances
        """
        queryset = DocumentJob.objects.all()

        if status:
            queryset = queryset.filter(status=status)

        if template_name:
            queryset = queryset.filter(template_name=template_name)

        return list(queryset[:limit])
