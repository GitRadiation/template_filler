"""
Tareas de Celery para la aplicación documentos.

Define las tareas asincrónicas para generar documentos en diferentes formatos
(PDF, DOCX, JSON).
"""

import json
import logging
import traceback
from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from weasyprint import HTML

from .services import DocumentService as _DocumentService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_pdf_task(self, job_id: str):
    """
    Genera un PDF a partir de una plantilla Jinja2 y datos JSON.
    
    Args:
        job_id: ID del trabajo DocumentJob
    
    Returns:
        dict: Información del resultado
    """
    job = _DocumentService.get_job(job_id)
    
    if not job:
        logger.error(f'Trabajo no encontrado: {job_id}')
        return {'status': 'error', 'message': 'Job not found'}
    
    try:
        # Marcar como en proceso
        job.mark_running()
        logger.info(f'Iniciando generación de PDF para trabajo: {job_id}')
        
        # Obtener los datos de entrada
        input_data = job.input_data or {}
        
        # Renderizar HTML desde la plantilla
        html_content = _render_template(job.template_name, input_data)
        
        # Convertir HTML a PDF
        pdf_bytes = _html_to_pdf(html_content)
        
        # Guardar el archivo PDF
        _DocumentService.save_output_file(
            job,
            pdf_bytes,
            file_name=f'{job.id}.pdf'
        )
        
        # Marcar como completado
        job.mark_completed()
        logger.info(f'PDF generado exitosamente: {job_id}')
        
        return {
            'status': 'success',
            'job_id': job_id,
            'message': 'PDF generated successfully'
        }
    
    except Exception as exc:
        logger.error(f'Error generando PDF para {job_id}: {str(exc)}')
        logger.error(traceback.format_exc())
        
        # Marcar como fallido
        job.mark_failed(error_message=str(exc))
        
        # Reintentar si no hemos alcanzado el máximo
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_docx_task(self, job_id: str):
    """
    Genera un DOCX a partir de una plantilla.
    
    Args:
        job_id: ID del trabajo DocumentJob
    
    Returns:
        dict: Información del resultado
    """
    job = _DocumentService.get_job(job_id)
    
    if not job:
        logger.error(f'Trabajo no encontrado: {job_id}')
        return {'status': 'error', 'message': 'Job not found'}
    
    try:
        job.mark_running()
        logger.info(f'Iniciando generación de DOCX para trabajo: {job_id}')
        
        input_data = job.input_data or {}
        
        # Renderizar desde la plantilla
        from docxtpl import DocxTemplate
        
        template_path = settings.TEMPLATES_DOC_DIR / f'{job.template_name}.docx'
        
        if not template_path.exists():
            raise FileNotFoundError(f'Plantilla DOCX no encontrada: {template_path}')
        
        doc = DocxTemplate(str(template_path))
        doc.render(input_data)
        
        # Guardar a bytes
        docx_bytes = BytesIO()
        doc.save(docx_bytes)
        docx_bytes.seek(0)
        
        _DocumentService.save_output_file(
            job,
            docx_bytes.getvalue(),
            file_name=f'{job.id}.docx'
        )
        
        job.mark_completed()
        logger.info(f'DOCX generado exitosamente: {job_id}')
        
        return {
            'status': 'success',
            'job_id': job_id,
            'message': 'DOCX generated successfully'
        }
    
    except Exception as exc:
        logger.error(f'Error generando DOCX para {job_id}: {str(exc)}')
        logger.error(traceback.format_exc())
        job.mark_failed(error_message=str(exc))
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_json_task(self, job_id: str):
    """
    Genera un JSON renderizado (con datos procesados).
    
    Args:
        job_id: ID del trabajo DocumentJob
    
    Returns:
        dict: Información del resultado
    """
    job = _DocumentService.get_job(job_id)
    
    if not job:
        logger.error(f'Trabajo no encontrado: {job_id}')
        return {'status': 'error', 'message': 'Job not found'}
    
    try:
        job.mark_running()
        logger.info(f'Iniciando generación de JSON para trabajo: {job_id}')
        
        input_data = job.input_data or {}
        
        # Procesar los datos (ejemplo: agregar timestamps, cálculos, etc.)
        output_data = {
            'template': job.template_name,
            'generated_at': timezone.now().isoformat(),
            'input_data': input_data,
            'summary': _process_data(input_data),
        }
        
        # Convertir a JSON
        json_bytes = json.dumps(output_data, indent=2, ensure_ascii=False).encode('utf-8')
        
        _DocumentService.save_output_file(
            job,
            json_bytes,
            file_name=f'{job.id}.json'
        )
        
        job.mark_completed()
        logger.info(f'JSON generado exitosamente: {job_id}')
        
        return {
            'status': 'success',
            'job_id': job_id,
            'message': 'JSON generated successfully'
        }
    
    except Exception as exc:
        logger.error(f'Error generando JSON para {job_id}: {str(exc)}')
        logger.error(traceback.format_exc())
        job.mark_failed(error_message=str(exc))
        raise self.retry(exc=exc, countdown=60)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def _render_template(template_name: str, context: dict) -> str:
    """
    Renderiza una plantilla Jinja2 con los datos proporcionados.
    
    Args:
        template_name: Nombre de la plantilla (sin extensión)
        context: Diccionario con los datos
    
    Returns:
        str: HTML renderizado
    
    Raises:
        TemplateNotFound: Si la plantilla no existe
    """
    from datetime import datetime
    
    env = Environment(
        loader=FileSystemLoader(str(settings.TEMPLATES_DOC_DIR)),
        autoescape=True,
        enable_async=False
    )
    
    # Agregar funciones útiles al contexto
    context_with_utils = {
        **context,
        'now': datetime.now(),
        'today': datetime.today(),
    }
    
    template_file = f'{template_name}.html.j2'
    
    try:
        template = env.get_template(template_file)
        logger.info(f'Plantilla cargada: {template_file}')
        return template.render(**context_with_utils)
    except TemplateNotFound:
        logger.error(f'Plantilla no encontrada: {template_file}')
        raise


def _html_to_pdf(html_content: str) -> bytes:
    """
    Convierte HTML a PDF usando WeasyPrint.
    
    Args:
        html_content: Contenido HTML
    
    Returns:
        bytes: Contenido del PDF
    """
    try:
        # Crear documento HTML desde string
        html = HTML(string=html_content, base_url='/')
        
        # Convertir a PDF
        pdf_bytes = html.write_pdf()
        
        if pdf_bytes is None:
            raise ValueError('WeasyPrint returned None when generating PDF')
        
        logger.info('HTML convertido a PDF exitosamente')
        return pdf_bytes
    
    except Exception as e:
        logger.error(f'Error convirtiendo HTML a PDF: {str(e)}')
        raise


def _process_data(data: dict) -> dict:
    """
    Procesa los datos de entrada para crear un resumen.
    
    Args:
        data: Diccionario con los datos
    
    Returns:
        dict: Resumen de los datos procesados
    """
    summary = {
        'fields_count': len(data),
        'keys': list(data.keys()),
        'has_numbers': any(isinstance(v, (int, float)) for v in data.values()),
        'has_strings': any(isinstance(v, str) for v in data.values()),
    }
    return summary
