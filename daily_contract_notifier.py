from whatsapp_sender import run_notification_job
from datetime import datetime, timedelta
import time

def main():
    """Daily scheduler - runs job at 09:00 every day"""
    print("Script started. Mode: Daily Schedule (09:00).")
    
    while True:
        now = datetime.now()
        # Set target to 9:00 AM today
        target = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # If 9:00 AM has already passed today, schedule for tomorrow
        if now >= target:
             target += timedelta(days=1)
        
        wait_seconds = (target - now).total_seconds()
        print(f"Current time: {now.strftime('%H:%M:%S')}. Waiting {wait_seconds:.0f}s until next run at {target.strftime('%d.%m %H:%M:%S')}...")
        
        # Sleep until target
        time.sleep(wait_seconds)
        
        # Run the job
        run_notification_job()
        
        # Sleep a bit to ensure we don't double trigger
        time.sleep(60)

if __name__ == "__main__":
    main()
