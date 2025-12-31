"""
Comando Django para reintentar trabajos de documento fallidos.

Uso:
    python manage.py retry_failed_jobs
    python manage.py retry_failed_jobs --limit 10
"""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from documentos.models import DocumentJob
from documentos.services import DocumentService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reintenta trabajos de documento fallidos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Número máximo de trabajos fallidos a reintentar'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Reintenta trabajos fallidos en las últimas N horas'
        )
    
    def handle(self, *args, **options):
        limit = options['limit']
        hours = options['hours']
        
        # Buscar trabajos fallidos recientes
        cutoff_time = timezone.now() - timedelta(hours=hours)
        failed_jobs = DocumentJob.objects.filter(
            status=DocumentJob.Status.FAILED,
            updated_at__gte=cutoff_time
        ).order_by('-created_at')[:limit]
        
        if not failed_jobs.exists():
            self.stdout.write(
                self.style.SUCCESS('No hay trabajos fallidos para reintentar')
            )
            return
        
        self.stdout.write(
            f'Reintentando {failed_jobs.count()} trabajos fallidos...'
        )
        
        retry_count = 0
        for job in failed_jobs:
            try:
                # Resetear el estado a pendiente
                job.status = DocumentJob.Status.PENDING
                job.error_message = None
                job.started_at = None
                job.completed_at = None
                job.save()
                
                # Enviar a Celery nuevamente
                DocumentService.send_to_celery(job)
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Trabajo reintentado: {job.id}')
                )
                retry_count += 1
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error reintentando {job.id}: {str(e)}')
                )
                logger.error(f'Error reintentando trabajo {job.id}: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal reintentados: {retry_count}/{failed_jobs.count()}')
        )
