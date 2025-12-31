"""
Configuración del admin de Django para la aplicación documentos.

Define los modelos que aparecen en el panel de administración.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import DocumentJob


@admin.register(DocumentJob)
class DocumentJobAdmin(admin.ModelAdmin):
    """
    Panel de administración para DocumentJob.
    """
    
    list_display = [
        'id_short',
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
        ('Información básica', {
            'fields': ['id', 'template_name', 'status', 'celery_task_id']
        }),
        ('Archivos', {
            'fields': ['input_file', 'output_file', 'output_file_preview']
        }),
        ('Datos', {
            'fields': ['input_data', 'input_data_display'],
            'classes': ['collapse']
        }),
        ('Estado y errores', {
            'fields': [
                'error_message',
                'created_at',
                'updated_at',
                'started_at',
                'completed_at'
            ]
        }),
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def id_short(self, obj) -> str:
        """Muestra los primeros 8 caracteres del UUID."""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'  # type: ignore
    
    def status_badge(self, obj) -> str:
        """Muestra el estado con un badge de color."""
        colors = {
            'pending': '#FFA500',     # Naranja
            'running': '#1E90FF',     # Azul
            'completed': '#28A745',   # Verde
            'failed': '#DC3545',      # Rojo
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'  # type: ignore
    
    def output_file_link(self, obj) -> str:
        """Muestra un enlace al archivo de salida si existe."""
        if obj.output_file:
            return format_html(
                '<a href="{}" target="_blank">Descargar</a>',
                obj.output_file.url
            )
        return '-'
    output_file_link.short_description = 'Archivo'  # type: ignore
    
    def output_file_preview(self, obj) -> str:
        """Muestra un enlace al archivo de salida."""
        if obj.output_file:
            return format_html(
                '<a href="{}" target="_blank">Ver/Descargar</a>',
                obj.output_file.url
            )
        return 'No disponible'
    output_file_preview.short_description = 'Vista previa'  # type: ignore
    
    def input_data_display(self, obj) -> str:
        """Muestra los datos de entrada formateados."""
        import json
        if obj.input_data:
            return format_html(
                '<pre>{}</pre>',
                json.dumps(obj.input_data, indent=2, ensure_ascii=False)
            )
        return 'Sin datos'
    input_data_display.short_description = 'Datos de entrada'  # type: ignore
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar trabajos."""
        return request.user.is_superuser
    
    actions = ['retry_failed_jobs', 'mark_as_pending']
    
    def retry_failed_jobs(self, request, queryset) -> None:
        """Acción para reintentar trabajos fallidos."""
        failed_jobs = queryset.filter(status=DocumentJob.Status.FAILED)
        count = 0
        
        for job in failed_jobs:
            job.status = DocumentJob.Status.PENDING
            job.error_message = None
            job.save()
            
            from .services import DocumentService
            DocumentService.send_to_celery(job)
            count += 1
        
        self.message_user(request, f'{count} trabajo(s) reintentado(s)')
    retry_failed_jobs.short_description = 'Reintentar trabajos fallidos'  # type: ignore
    
    def mark_as_pending(self, request, queryset) -> None:
        """Acción para marcar trabajos como pendientes."""
        count = queryset.update(status=DocumentJob.Status.PENDING)
        self.message_user(request, f'{count} trabajo(s) marcado(s) como pendiente')
    mark_as_pending.short_description = 'Marcar como pendiente'  # type: ignore
