import time
import threading
from app_va import log


class ScheduleWorker:
    def __init__(self, api_addr: str, api_port: int):
        self.api_addr = api_addr
        self.api_port = api_port
        self.is_running = False
        self.worker_thread = None

    def main_work(self):
        """Main scheduler work loop"""
        self.is_running = True
        log.info("Schedule worker started")
        
        try:
            while self.is_running:
                # Perform periodic tasks
                self._perform_periodic_tasks()
                
                # Sleep for a reasonable interval (e.g., 30 seconds)
                time.sleep(30)
                
        except Exception as e:
            log.error(f"Schedule worker error: {e}")
        finally:
            log.info("Schedule worker stopped")

    def _perform_periodic_tasks(self):
        """Perform periodic maintenance tasks"""
        try:
            # Example tasks:
            # - Health checks
            # - Cleanup old logs
            # - Update statistics
            # - Check system status
            
            # For now, just log that we're alive
            log.debug("Schedule worker performing periodic tasks")
            
        except Exception as e:
            log.error(f"Error in periodic tasks: {e}")

    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
        log.info("Schedule worker stopped")
