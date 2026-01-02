"""
Django management command to retry failed document jobs.

Usage:
    python manage.py retry_failed_jobs
    python manage.py retry_failed_jobs --limit 10
    python manage.py retry_failed_jobs --hours 24
"""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from docs.models import DocumentJob
from docs.services import DocumentService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Retry failed document jobs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Maximum number of failed jobs to retry",
        )
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Retry jobs failed within the last N hours",
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        hours = options["hours"]

        failed_jobs = self._get_recent_failed_jobs(limit, hours)

        if not failed_jobs.exists():
            self.stdout.write(
                self.style.SUCCESS("No failed jobs to retry")
            )
            return

        self.stdout.write(
            f"Retrying {failed_jobs.count()} failed jobs..."
        )

        retried_jobs = self._retry_jobs(failed_jobs)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nTotal retried: {retried_jobs}/{failed_jobs.count()}"
            )
        )

    def _get_recent_failed_jobs(self, limit: int, hours: int):
        cutoff_time = timezone.now() - timedelta(hours=hours)

        return (
            DocumentJob.objects.filter(
                status=DocumentJob.Status.FAILED,
                updated_at__gte=cutoff_time,
            )
            .order_by("-created_at")[:limit]
        )

    def _retry_jobs(self, jobs):
        retried_count = 0

        for job in jobs:
            try:
                self._reset_job(job)
                DocumentService.send_to_celery(job)

                self.stdout.write(
                    self.style.SUCCESS(f"✓ Job retried: {job.id}")
                )
                retried_count += 1

            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Error retrying job {job.id}: {exc}"
                    )
                )
                logger.exception(
                    "Error retrying document job %s", job.id
                )

        return retried_count

    @staticmethod
    def _reset_job(job: DocumentJob):
        job.status = DocumentJob.Status.PENDING
        job.error_message = None
        job.started_at = None
        job.completed_at = None
        job.save()
