"""
Django admin configuration for the documents application.

Defines how document-related models are displayed and managed
in the Django administration panel.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import DocumentJob


@admin.register(DocumentJob)
class DocumentJobAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración para DocumentJob.
    """

    # =========================
    # List view configuration
    # =========================
    list_display = [
        'short_id',
        'template_name',
        'status_badge',
        'created_at',
        'completed_at',
        'output_file_link',
    ]

    list_filter = [
        'status',
        'template_name',
        'created_at',
    ]

    search_fields = [
        'id',
        'template_name',
        'error_message',
    ]

    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    # =========================
    # Detail view configuration
    # =========================
    readonly_fields = [
        'id',
        'celery_task_id',
        'created_at',
        'updated_at',
        'started_at',
        'completed_at',
        'input_data_display',
        'output_file_preview',
    ]

    fieldsets = (
        (
            _('Información Básica'),
            {
                'fields': [
                    'id',
                    'template_name',
                    'status',
                    'celery_task_id',
                ]
            },
        ),
        (
            _('Archivos'),
            {
                'fields': [
                    'input_file',
                    'output_file',
                    'output_file_preview',
                ]
            },
        ),
        (
            _('Datos de Entrada'),
            {
                'fields': [
                    'input_data',
                    'input_data_display',
                ],
                'classes': ['collapse'],
            },
        ),
        (
            _('Estado y Errores'),
            {
                'fields': [
                    'error_message',
                    'created_at',
                    'updated_at',
                    'started_at',
                    'completed_at',
                ]
            },
        ),
    )

    # =========================
    # Custom display methods
    # =========================
    @admin.display(description=_('ID'))
    def short_id(self, obj) -> str:
        """Muestra los primeros 8 caracteres del UUID."""
        return str(obj.id)[:8]

    @admin.display(description=_('Estado'))
    def status_badge(self, obj) -> str:
        """Muestra el estado del trabajo con una insignia de color."""
        colors = {
            DocumentJob.Status.PENDING: '#FFA500',    # Orange
            DocumentJob.Status.RUNNING: '#1E90FF',    # Blue
            DocumentJob.Status.COMPLETED: '#28A745',  # Green
            DocumentJob.Status.FAILED: '#DC3545',     # Red
        }

        color = colors.get(obj.status, '#6C757D')

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 5px 10px; border-radius: 4px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description=_('Archivo de Salida'))
    def output_file_link(self, obj) -> str:
        """Muestra un enlace de descarga para el archivo de salida."""
        if not obj.output_file:
            return '-'

        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            obj.output_file.url,
            _('Descargar'),
        )

    @admin.display(description=_('Vista Previa'))
    def output_file_preview(self, obj) -> str:
        """Muestra un enlace de vista previa/descarga."""
        if not obj.output_file:
            return _('No disponible')

        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            obj.output_file.url,
            _('Ver / Descargar'),
        )

    @admin.display(description=_('Datos de Entrada'))
    def input_data_display(self, obj) -> str:
        """Muestra los datos JSON de entrada formateados."""
        import json

        if not obj.input_data:
            return _('Sin datos')

        return format_html(
            '<pre>{}</pre>',
            json.dumps(obj.input_data, indent=2, ensure_ascii=False),
        )

    # =========================
    # Permissions
    # =========================
    def has_delete_permission(self, request, obj=None) -> bool:
        """Permite eliminación solo para superusuarios."""
        return request.user.is_superuser

    # =========================
    # Admin actions
    # =========================
    actions = [
        'retry_failed_jobs',
        'mark_as_pending',
    ]

    @admin.action(description=_('Reintentar trabajos fallidos'))
    def retry_failed_jobs(self, request, queryset) -> None:
        """
        Reintenta trabajos seleccionados que están en estado FAILED.
        """
        from .services import DocumentService

        failed_jobs = queryset.filter(status=DocumentJob.Status.FAILED)
        retried_count = 0

        for job in failed_jobs:
            job.status = DocumentJob.Status.PENDING
            job.error_message = None
            job.save(update_fields=['status', 'error_message'])

            DocumentService.send_to_celery(job)
            retried_count += 1

        self.message_user(
            request,
            _('{} trabajo(s) reintentado(s) exitosamente.').format(retried_count),
        )

    @admin.action(description=_('Marcar como pendiente'))
    def mark_as_pending(self, request, queryset) -> None:
        """
        Marca trabajos seleccionados como PENDING.
        """
        updated_count = queryset.update(status=DocumentJob.Status.PENDING)

        self.message_user(
            request,
            _('{} trabajo(s) marcado(s) como pendiente.').format(updated_count),
        )