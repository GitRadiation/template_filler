"""
Django admin configuration for the documents application.

Defines how document-related models are displayed and managed
in the Django administration panel.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import DocumentJob


@admin.register(DocumentJob)
class DocumentJobAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for DocumentJob.
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
            'Basic Information',
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
            'Files',
            {
                'fields': [
                    'input_file',
                    'output_file',
                    'output_file_preview',
                ]
            },
        ),
        (
            'Input Data',
            {
                'fields': [
                    'input_data',
                    'input_data_display',
                ],
                'classes': ['collapse'],
            },
        ),
        (
            'Status & Errors',
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
    def short_id(self, obj) -> str:
        """Display the first 8 characters of the UUID."""
        return str(obj.id)[:8]

    short_id.short_description = 'ID'  # type: ignore

    def status_badge(self, obj) -> str:
        """Display job status using a colored badge."""
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

    status_badge.short_description = 'Status'  # type: ignore

    def output_file_link(self, obj) -> str:
        """Display a download link for the generated output file."""
        if not obj.output_file:
            return '-'

        return format_html(
            '<a href="{}" target="_blank">Download</a>',
            obj.output_file.url,
        )

    output_file_link.short_description = 'Output File'  # type: ignore

    def output_file_preview(self, obj) -> str:
        """Display a preview/download link for the output file."""
        if not obj.output_file:
            return 'Not available'

        return format_html(
            '<a href="{}" target="_blank">View / Download</a>',
            obj.output_file.url,
        )

    output_file_preview.short_description = 'Preview'  # type: ignore

    def input_data_display(self, obj) -> str:
        """Pretty-print input JSON data."""
        import json

        if not obj.input_data:
            return 'No data'

        return format_html(
            '<pre>{}</pre>',
            json.dumps(obj.input_data, indent=2, ensure_ascii=False),
        )

    input_data_display.short_description = 'Input Data'  # type: ignore

    # =========================
    # Permissions
    # =========================
    def has_delete_permission(self, request, obj=None) -> bool:
        """Allow deletion only for superusers."""
        return request.user.is_superuser

    # =========================
    # Admin actions
    # =========================
    actions = [
        'retry_failed_jobs',
        'mark_as_pending',
    ]

    def retry_failed_jobs(self, request, queryset) -> None:
        """
        Retry selected jobs that are in FAILED status.
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
            f'{retried_count} job(s) retried successfully.',
        )

    retry_failed_jobs.short_description = 'Retry failed jobs'  # type: ignore

    def mark_as_pending(self, request, queryset) -> None:
        """
        Mark selected jobs as PENDING.
        """
        updated_count = queryset.update(status=DocumentJob.Status.PENDING)

        self.message_user(
            request,
            f'{updated_count} job(s) marked as pending.',
        )

    mark_as_pending.short_description = 'Mark as pending'  # type: ignore
