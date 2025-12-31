"""
Modelos de la aplicación documentos.

Define el modelo DocumentJob para registrar tareas de generación de documentos.
"""

import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class DocumentJob(models.Model):
    """
    Modelo que representa un trabajo de generación de documento.
    
    Almacena información sobre cada tarea asincrónica que genera un documento,
    incluyendo su estado, archivos de entrada/salida y timestamps.
    """
    
    class Status(models.TextChoices):
        """Estados posibles de un trabajo de documento."""
        PENDING = 'pending', _('Pendiente')
        RUNNING = 'running', _('En proceso')
        COMPLETED = 'completed', _('Completado')
        FAILED = 'failed', _('Falló')
    
    # Identificadores
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID único')
    )
    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('ID de tarea Celery'),
        help_text=_('Identificador de la tarea en Celery para tracking')
    )
    
    # Información del documento
    template_name = models.CharField(
        max_length=100,
        choices=[
            ('contract', _('Contrato')),
            ('invoice', _('Factura')),
            ('certificate', _('Certificado')),
        ],
        verbose_name=_('Tipo de plantilla'),
        help_text=_('Plantilla Jinja2 a utilizar')
    )
    
    # Archivos
    input_file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_('Archivo de entrada'),
        help_text=_('JSON con datos para la plantilla')
    )
    output_file = models.FileField(
        upload_to='generated/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_('Archivo de salida'),
        help_text=_('PDF generado')
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_('Estado'),
        db_index=True
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Mensaje de error'),
        help_text=_('Detalles del error si el trabajo falló')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Creado el'),
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Actualizado el')
    )
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Iniciado el')
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Completado el')
    )
    
    # Datos adicionales
    input_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Datos de entrada'),
        help_text=_('JSON con los datos para renderizar la plantilla')
    )
    
    class Meta:
        verbose_name = _('Trabajo de documento')
        verbose_name_plural = _('Trabajos de documentos')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['template_name', 'status']),
        ]
    
    def __str__(self):
        return f'{self.template_name} - {self.status} ({self.id})'
    
    def is_completed(self):
        """Verifica si el trabajo está completado."""
        return self.status == self.Status.COMPLETED
    
    def is_failed(self):
        """Verifica si el trabajo falló."""
        return self.status == self.Status.FAILED
    
    def is_pending(self):
        """Verifica si el trabajo está pendiente."""
        return self.status == self.Status.PENDING
    
    def mark_running(self):
        """Marca el trabajo como en proceso."""
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])
    
    def mark_completed(self):
        """Marca el trabajo como completado."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])
    
    def mark_failed(self, error_message=None):
        """Marca el trabajo como fallido."""
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'completed_at', 'updated_at'])
