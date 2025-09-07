from celery import Celery
from app.core.config import settings
from kombu import Queue, Exchange

# Define exchanges
dead_letter_exchange = Exchange('dead_letter_exchange', type='direct')

celery_app = Celery(
    "ai_creat",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.asset_processing", "app.tasks.generation_tasks", "app.tasks.maintenance"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Define queues with DLQ settings
    task_queues=(
        Queue(
            'asset_processing',
            routing_key='asset_processing',
            queue_arguments={
                'x-dead-letter-exchange': 'dead_letter_exchange',
                'x-dead-letter-routing-key': 'dead_letter'
            }
        ),
        Queue(
            'generation',
            routing_key='generation',
            queue_arguments={
                'x-dead-letter-exchange': 'dead_letter_exchange',
                'x-dead-letter-routing-key': 'dead_letter'
            }
        ),
        Queue('maintenance', routing_key='maintenance'),
        Queue('dead_letter', exchange=dead_letter_exchange, routing_key='dead_letter')
    ),
    
    # Task routing
    task_routes={
        'app.tasks.asset_processing.process_uploaded_assets': {'queue': 'asset_processing'},
        'app.tasks.generation_tasks.process_generation_job': {'queue': 'generation'},
        'app.tasks.generation_tasks.process_prompt_edit_job': {'queue': 'generation'},
        'app.tasks.maintenance.*': {'queue': 'maintenance'},
    },
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_acks_on_failure_or_timeout=False,  # Required for DLQ
    task_reject_on_worker_lost=True,       # Required for DLQ
    worker_max_tasks_per_child=1000,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task annotations for specific configurations
celery_app.conf.task_annotations = {
    'app.tasks.asset_processing.process_uploaded_assets': {
        'rate_limit': '10/m',  # 10 tasks per minute
        'time_limit': 300,     # 5 minutes
        'soft_time_limit': 240, # 4 minutes
    },
    'app.tasks.generation_tasks.process_generation_job': {
        'rate_limit': '5/m',   # 5 tasks per minute
        'time_limit': 600,     # 10 minutes
        'soft_time_limit': 540, # 9 minutes
    },
}
