"""
Celery configuration for background task processing.
"""
from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "doc_parser",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    "cleanup-old-files": {
        "task": "app.tasks.tasks.cleanup_old_files",
        "schedule": 3600.0,  # Run every hour
    },
    "process-pending-documents": {
        "task": "app.tasks.tasks.process_pending_documents",
        "schedule": 60.0,  # Run every minute
    },
}

if __name__ == "__main__":
    celery_app.start()
