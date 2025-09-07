#!/usr/bin/env python3
"""
Monitor Celery workers and tasks
"""
import os
import sys
import time
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.services.celery_service import CeleryService


def monitor_workers():
    """Monitor Celery workers"""
    print("=== Celery Worker Monitor ===")
    print(f"Started at: {datetime.now()}")
    print()
    
    try:
        while True:
            # Get worker stats
            stats = CeleryService.get_worker_stats()
            active_tasks = CeleryService.get_active_tasks()
            
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Worker Status:")
            
            if not stats:
                print("  No workers found or workers not responding")
            else:
                for worker_name, worker_stats in stats.items():
                    print(f"  Worker: {worker_name}")
                    print(f"    Status: Online")
                    print(f"    Pool: {worker_stats.get('pool', {}).get('implementation', 'unknown')}")
                    print(f"    Processes: {worker_stats.get('pool', {}).get('processes', 'unknown')}")
                    
                    # Active tasks for this worker
                    worker_tasks = active_tasks.get(worker_name, [])
                    print(f"    Active tasks: {len(worker_tasks)}")
                    
                    for task in worker_tasks[:3]:  # Show first 3 tasks
                        print(f"      - {task.get('name', 'unknown')} ({task.get('id', 'no-id')[:8]}...)")
            
            print("\n" + "="*50)
            time.sleep(10)  # Update every 10 seconds
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


def show_task_status(task_id: str):
    """Show status of a specific task"""
    status = CeleryService.get_task_status(task_id)
    
    print(f"Task ID: {task_id}")
    print(f"Status: {status['status']}")
    print(f"Result: {json.dumps(status['result'], indent=2) if status['result'] else 'None'}")
    
    if status['traceback']:
        print(f"Error: {status['traceback']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Celery workers and tasks')
    parser.add_argument('--task-id', help='Show status of specific task')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    
    args = parser.parse_args()
    
    if args.task_id:
        show_task_status(args.task_id)
    elif args.monitor:
        monitor_workers()
    else:
        # Show current status once
        stats = CeleryService.get_worker_stats()
        active_tasks = CeleryService.get_active_tasks()
        
        print("Current Celery Status:")
        print(f"Workers: {len(stats)}")
        print(f"Total active tasks: {sum(len(tasks) for tasks in active_tasks.values())}")
        
        if stats:
            print("\nWorkers:")
            for worker_name in stats.keys():
                worker_tasks = active_tasks.get(worker_name, [])
                print(f"  {worker_name}: {len(worker_tasks)} active tasks")
