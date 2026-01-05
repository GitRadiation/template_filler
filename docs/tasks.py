"""
Celery tasks for the documents application.

Defines asynchronous tasks for generating documents in multiple formats:
- PDF
- DOCX
- JSON
"""

import json
import logging
import traceback
from io import BytesIO
from typing import Any, NoReturn

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from docxtpl import DocxTemplate
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from weasyprint import HTML

from .services import DocumentService

logger = logging.getLogger(__name__)


# ============================================================================
# Base helpers
# ============================================================================

def _get_job_or_fail(job_id: str):
    job = DocumentService.get_job(job_id)
    if not job:
        logger.error('Document job not found: %s', job_id)
        return None
    return job


def _handle_task_failure(self, job, exc: Exception) -> NoReturn:
    logger.error('Task failed for job %s: %s', job.id, exc)
    logger.error(traceback.format_exc())

    job.mark_failed(error_message=str(exc))

    raise self.retry(exc=exc, countdown=60)


# ============================================================================
# PDF task
# ============================================================================

@shared_task(bind=True, max_retries=3)
def generate_pdf_task(self, job_id: str) -> dict[str, Any]:
    """
    Generate a PDF document using a Jinja2 HTML template.

    Args:
        job_id: UUID of the DocumentJob

    Returns:
        Result metadata dictionary
    """
    job = _get_job_or_fail(job_id)
    if not job:
        return {'status': 'error', 'message': 'Job not found'}

    try:
        job.mark_running()
        logger.info('Starting PDF generation (job_id=%s)', job_id)

        html_content = _render_template(
            job.template_name,
            job.input_data or {},
        )

        pdf_bytes = _html_to_pdf(html_content)

        DocumentService.save_output_file(
            job,
            pdf_bytes,
            file_name=f'{job.id}.pdf',
        )

        job.mark_completed()
        logger.info('PDF generated successfully (job_id=%s)', job_id)

        return {'status': 'success', 'job_id': job_id}

    except Exception as exc:
        _handle_task_failure(self, job, exc)


# ============================================================================
# DOCX task
# ============================================================================

@shared_task(bind=True, max_retries=3)
def generate_docx_task(self, job_id: str) -> dict[str, Any]:
    job = _get_job_or_fail(job_id)
    if not job:
        return {'status': 'error', 'message': 'Job not found'}

    try:
        job.mark_running()
        logger.info('Starting DOCX generation (job_id=%s)', job_id)

        template_path = settings.TEMPLATES_DOC_DIR / f'{job.template_name}.docx'
        if not template_path.exists():
            raise FileNotFoundError(f'DOCX template not found: {template_path}')

        doc = DocxTemplate(str(template_path))
        doc.render(job.input_data or {}, autoescape=True)

        # Guardamos directamente en memoria
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        docx_bytes = buffer.read()
        buffer.close() 
        DocumentService.save_output_file(
            job,
            docx_bytes,
            file_name=f'{job.id}.docx'
        )

        job.mark_completed()
        logger.info('DOCX generated successfully (job_id=%s)', job_id)

        return {'status': 'success', 'job_id': job_id}

    except Exception as exc:
        _handle_task_failure(self, job, exc)

# ============================================================================
# JSON task
# ============================================================================

@shared_task(bind=True, max_retries=3)
def generate_json_task(self, job_id: str) -> dict[str, Any]:
    """
    Generate a processed JSON output file.

    Args:
        job_id: UUID of the DocumentJob

    Returns:
        Result metadata dictionary
    """
    job = _get_job_or_fail(job_id)
    if not job:
        return {'status': 'error', 'message': 'Job not found'}

    try:
        job.mark_running()
        logger.info('Starting JSON generation (job_id=%s)', job_id)

        input_data = job.input_data or {}

        output_data = {
            'template': job.template_name,
            'generated_at': timezone.now().isoformat(),
            'input_data': input_data,
            'summary': _process_data(input_data),
        }

        json_bytes = json.dumps(
            output_data,
            indent=2,
            ensure_ascii=False,
        ).encode('utf-8')

        DocumentService.save_output_file(
            job,
            json_bytes,
            file_name=f'{job.id}.json',
        )

        job.mark_completed()
        logger.info('JSON generated successfully (job_id=%s)', job_id)

        return {'status': 'success', 'job_id': job_id}

    except Exception as exc:
        _handle_task_failure(self, job, exc)


# ============================================================================
# Template & conversion helpers
# ============================================================================

def _render_template(template_name: str, context: dict) -> str:
    """
    Render a template.

    Args:
        template_name: Template base name (without extension)
        context: Context data for rendering

    Returns:
        Rendered HTML string
    """
    from datetime import datetime

    env = Environment(
        loader=FileSystemLoader(str(settings.TEMPLATES_DOC_DIR)),
        autoescape=True,
    )

    context_with_utils = {
        **context,
        'now': datetime.now(),
        'today': datetime.today(),
    }

    template_file = f'{template_name}'

    try:
        template = env.get_template(template_file)
        logger.info('Template loaded: %s', template_file)
        return template.render(**context_with_utils)
    except TemplateNotFound:
        logger.error('Template not found: %s', template_file)
        raise


def _html_to_pdf(html_content: str) -> bytes:
    """
    Convert HTML content to PDF using WeasyPrint.

    Args:
        html_content: Rendered HTML

    Returns:
        PDF binary content
    """
    html = HTML(string=html_content, base_url='/')
    pdf_bytes = html.write_pdf()

    if not pdf_bytes:
        raise ValueError('Failed to generate PDF')

    logger.info('HTML successfully converted to PDF')
    return pdf_bytes


def _process_data(data: dict) -> dict:
    """
    Generate a summary from input data.

    Args:
        data: Input data dictionary

    Returns:
        Summary dictionary
    """
    return {
        'fields_count': len(data),
        'keys': list(data.keys()),
        'has_numbers': any(isinstance(v, (int, float)) for v in data.values()),
        'has_strings': any(isinstance(v, str) for v in data.values()),
    }
