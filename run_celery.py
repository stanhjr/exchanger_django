"""Celery start """

from celery_tasks.tasks import app

if __name__ == "__main__":
    argv = [
        'worker',
        '-B',
        '--loglevel=DEBUG',
        '--without-heartbeat',
        '--without-mingle',
        '--without-gossip',
        '--queues=celery_tasks,update_rates'
    ]
    app.worker_main(argv)
