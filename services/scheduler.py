from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from database import SessionLocal
from models.letter import Letter
from services.email import send_time_capsule_email
from datetime import datetime
import asyncio

scheduler = AsyncIOScheduler()

async def check_for_due_letters():
    print(f"[{datetime.now()}] 🕰️ Scheduler waking up... Checking for due letters.")
    db = SessionLocal()
    try:
        # Find letters that are due (delivery_date <= now) AND not sent yet
        due_letters = db.query(Letter).filter(
            Letter.delivery_date <= datetime.utcnow(),
            Letter.is_sent == False
        ).all()

        if due_letters:
            print(f"Found {len(due_letters)} letters to deliver!")
            for letter in due_letters:
                try:
                    await send_time_capsule_email(
                        email_to=letter.email,
                        content=letter.content_text or "(No text content)",
                        media_url=letter.media_url,
                        media_type=letter.media_type
                    )
                    # Mark as sent
                    letter.is_sent = True
                    db.commit()
                    print(f"✅ Delivered letter to {letter.email}")
                except Exception as e:
                    print(f"❌ Failed to deliver to {letter.email}: {e}")
        else:
            print("No letters due at this time.")

    except Exception as e:
        print(f"Scheduler Error: {e}")
    finally:
        db.close()

def start_scheduler():
    # Run every 60 seconds for demo/testing purposes
    # In production, maybe every hour
    scheduler.add_job(check_for_due_letters, 'interval', seconds=60)
    scheduler.start()
