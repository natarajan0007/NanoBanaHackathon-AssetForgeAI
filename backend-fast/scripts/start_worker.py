#!/usr/bin/env python3
"""
Start Celery worker with proper configuration
"""
import os
import sys
import subprocess

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings


def start_worker(queue_name: str = "default", concurrency: int = 2):
    """Start a Celery worker"""
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        'PYTHONPATH': os.path.dirname(os.path.dirname(__file__)),
        'C_FORCE_ROOT': '1',  # Allow running as root (for Docker)
    })
    
    # Build command
    cmd = [
        'celery',
        '-A', 'app.celery_app',
        'worker',
        '--loglevel=info',
        f'--concurrency={concurrency}',
        f'--queues={queue_name}',
        '--pool=prefork',
        '--without-gossip',
        '--without-mingle',
        '--without-heartbeat'
    ]
    
    print(f"Starting Celery worker for queue: {queue_name}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\nShutting down worker...")
    except subprocess.CalledProcessError as e:
        print(f"Worker failed with exit code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Start Celery worker')
    parser.add_argument('--queue', default='default', help='Queue name to process')
    parser.add_argument('--concurrency', type=int, default=2, help='Number of worker processes')
    
    args = parser.parse_args()
    start_worker(args.queue, args.concurrency)
