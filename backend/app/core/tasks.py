import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.follow_up_service import follow_up_service
from app.services.gmail_monitor_service import gmail_monitor_service
from app.services.facebook_monitor_service import facebook_monitor_service
from app.services.instagram_monitor_service import instagram_monitor_service
logger = logging.getLogger(__name__)

async def run_follow_up_service():
    """
    Run the follow-up service to send emails to leads.
    This function should be called periodically (e.g., every hour).
    """
    print("[DEBUG] run_follow_up_service called")
    logger.info("[DEBUG] run_follow_up_service called")
    logger.info(f"[DEBUG] run_follow_up_service called at {datetime.now()}")
    logger.info(f"Starting follow-up service at {datetime.now()}")
    
    try:
        # Create a new database session
        db = SessionLocal()
        try:
            await follow_up_service.send_follow_up_emails(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error running follow-up service: {str(e)}")
        raise

async def run_facebook_monitor_service():
    """
    Run the Facebook monitor service to poll for new messages for all companies.
    This function should be called periodically (e.g., every minute).
    """
    print("[DEBUG] run_facebook_monitor_service called")
    logger.info("[DEBUG] run_facebook_monitor_service called")
    logger.info(f"[DEBUG] run_facebook_monitor_service called at {datetime.now()}")
    logger.info(f"Starting Facebook monitor service at {datetime.now()}")
    try:
        db = SessionLocal()
        try:
            await facebook_monitor_service.poll_facebook_messages_from_companies()
        finally:
            db.close()
    except Exception as e:
        print(f"[DEBUG] Error running Facebook monitor service: {e}")
        logger.error(f"Error running Facebook monitor service: {str(e)}")

async def run_instagram_monitor_service():
    """
    Run the Instagram monitor service to poll for new messages for all companies.
    This function should be called periodically (e.g., every minute).
    """
    print("[DEBUG] run_instagram_monitor_service called")
    logger.info("[DEBUG] run_instagram_monitor_service called")
    logger.info(f"[DEBUG] run_instagram_monitor_service called at {datetime.now()}")
    logger.info(f"Starting Instagram monitor service at {datetime.now()}")
    try:
        db = SessionLocal()
        try:
            await instagram_monitor_service.poll_instagram_messages_from_companies()
        finally:
            db.close()
    except Exception as e:
        print(f"[DEBUG] Error running Instagram monitor service: {e}")
        logger.error(f"Error running Instagram monitor service: {str(e)}")
async def run_gmail_monitor_service():
    """
    Run the Gmail monitor service to poll for new emails for all companies.
    This function should be called periodically (e.g., every minute).
    """
    print("[DEBUG] run_gmail_monitor_service called")
    logger.info("[DEBUG] run_gmail_monitor_service called")
    logger.info(f"[DEBUG] run_gmail_monitor_service called at {datetime.now()}")
    logger.info(f"Starting Gmail monitor service at {datetime.now()}")
    try:
        db = SessionLocal()
        try:
            await gmail_monitor_service.poll_new_emails(db)
        finally:
            db.close()
    except Exception as e:
        print(f"[DEBUG] Error running Gmail monitor service: {e}")
        logger.error(f"Error running Gmail monitor service: {str(e)}")

async def run_outlook_monitor_service():
    """
    Run the Outlook monitor service to poll for new emails for all companies.
    This function should be called periodically (e.g., every minute).
    """
    print("[DEBUG] run_outlook_monitor_service called")
    logger.info("[DEBUG] run_outlook_monitor_service called")
    logger.info(f"[DEBUG] run_outlook_monitor_service called at {datetime.now()}")
    logger.info(f"Starting Outlook monitor service at {datetime.now()}")
    try:
        db = SessionLocal()
        try:
            from app.services.outlook_monitor_service import outlook_monitor_service
            await outlook_monitor_service.poll_new_emails(db)
        finally:
            db.close()
    except Exception as e:
        print(f"[DEBUG] Error running Outlook monitor service: {e}")
        logger.error(f"Error running Outlook monitor service: {str(e)}")

async def run_email_monitor_services():
    """
    Run both Gmail and Outlook monitor services.
    This function should be called periodically (e.g., every minute).
    """
    logger.info(f"Starting email monitor services at {datetime.now()}")
    
    # Run Gmail monitoring
    await run_gmail_monitor_service()
    
    # # Run Outlook monitoring
    await run_outlook_monitor_service()
    
    await run_facebook_monitor_service()

    await run_instagram_monitor_service()

async def run_periodic_tasks():
    print("[DEBUG] run_periodic_tasks entered")
    logger.info("[DEBUG] run_periodic_tasks entered")
    try:
        print("[DEBUG] Before while True in run_periodic_tasks")
        while True:
            print("[DEBUG] run_periodic_tasks loop iteration")
            await run_email_monitor_services()
            # await run_follow_up_service()
            await asyncio.sleep(60)
    except Exception as e:
        print(f"[DEBUG] Exception in run_periodic_tasks: {e}")
        logger.error(f"Exception in run_periodic_tasks: {e}") 