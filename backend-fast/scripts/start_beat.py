#!/usr/bin/env python3
"""
Start Celery beat scheduler for periodic tasks
"""
import os
import sys
import subprocess

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def start_beat():
    """Start Celery beat scheduler"""
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        'PYTHONPATH': os.path.dirname(os.path.dirname(__file__)),
        'C_FORCE_ROOT': '1',
    })
    
    # Build command
    cmd = [
        'celery',
        '-A', 'app.celery_app',
        'beat',
        '--loglevel=info',
        '--schedule=/tmp/celerybeat-schedule',
        '--pidfile=/tmp/celerybeat.pid'
    ]
    
    print("Starting Celery beat scheduler...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\nShutting down beat scheduler...")
    except subprocess.CalledProcessError as e:
        print(f"Beat scheduler failed with exit code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    start_beat()
