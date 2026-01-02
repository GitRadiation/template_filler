"""
Models for the documents application.

Defines the DocumentJob model used to track asynchronous
document generation tasks.
"""

import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class DocumentJob(models.Model):
    """
    Represents a document generation job.

    Stores metadata for each asynchronous task responsible for
    generating a document, including its status, input/output
    files, timestamps, and error information.
    """

    class Status(models.TextChoices):
        """Possible states of a document job."""
        PENDING = 'pending', _('Pending')
        RUNNING = 'running', _('Running')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')

    # =========================
    # Identifiers
    # =========================
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('Unique ID'),
    )

    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Celery task ID'),
        help_text=_('Celery task identifier for tracking purposes'),
    )

    # =========================
    # Document configuration
    # =========================
    TEMPLATE_CHOICES = (
        ('contract', _('Contract')),
        ('invoice', _('Invoice')),
        ('certificate', _('Certificate')),
    )

    template_name = models.CharField(
        max_length=100,
        choices=TEMPLATE_CHOICES,
        verbose_name=_('Template type'),
        help_text=_('Jinja2 template used to generate the document'),
    )

    # =========================
    # Files
    # =========================
    input_file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_('Input file'),
        help_text=_('JSON file containing template data'),
    )

    output_file = models.FileField(
        upload_to='generated/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name=_('Output file'),
        help_text=_('Generated PDF document'),
    )

    # =========================
    # Status & errors
    # =========================
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name=_('Status'),
    )

    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Error message'),
        help_text=_('Error details if the job fails'),
    )

    # =========================
    # Timestamps
    # =========================
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_('Created at'),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at'),
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Started at'),
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Completed at'),
    )

    # =========================
    # Additional data
    # =========================
    input_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Input data'),
        help_text=_('JSON payload used to render the template'),
    )

    # =========================
    # Model configuration
    # =========================
    class Meta:
        verbose_name = _('Document Job')
        verbose_name_plural = _('Document Jobs')
        ordering = ['-created_at']
        db_table = 'documentos_documentjob'  # Keep DB compatibility
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['template_name', 'status']),
        ]

    # =========================
    # String representation
    # =========================
    def __str__(self) -> str:
        return f'{self.template_name} - {self.status} ({self.id})'

    # =========================
    # State helpers
    # =========================
    def is_pending(self) -> bool:
        """Return True if the job is pending."""
        return self.status == self.Status.PENDING

    def is_running(self) -> bool:
        """Return True if the job is currently running."""
        return self.status == self.Status.RUNNING

    def is_completed(self) -> bool:
        """Return True if the job has completed successfully."""
        return self.status == self.Status.COMPLETED

    def is_failed(self) -> bool:
        """Return True if the job has failed."""
        return self.status == self.Status.FAILED

    # =========================
    # State transitions
    # =========================
    def mark_running(self) -> None:
        """Mark the job as running."""
        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at', 'updated_at'])

    def mark_completed(self) -> None:
        """Mark the job as completed."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_failed(self, error_message: str | None = None) -> None:
        """Mark the job as failed and store the error message."""
        self.status = self.Status.FAILED
        self.completed_at = timezone.now()

        if error_message:
            self.error_message = error_message

        self.save(
            update_fields=[
                'status',
                'error_message',
                'completed_at',
                'updated_at',
            ]
        )
