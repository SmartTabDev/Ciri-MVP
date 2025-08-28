from datetime import datetime, timezone, timedelta
from typing import Optional

def utcnow() -> datetime:
    """
    Get the current UTC datetime with timezone information.
    
    Returns:
        datetime: Current UTC datetime (timezone-aware)
    """
    return datetime.now(timezone.utc)

def make_aware(dt: datetime) -> datetime:
    """
    Make a naive datetime timezone-aware by attaching UTC timezone.
    
    Args:
        dt: A naive datetime object
        
    Returns:
        datetime: Timezone-aware datetime with UTC timezone
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def make_naive(dt: datetime) -> datetime:
    """
    Make a timezone-aware datetime naive by converting to UTC and removing timezone.
    
    Args:
        dt: A timezone-aware datetime object
        
    Returns:
        datetime: Naive datetime in UTC
    """
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def is_expired(expires_at: datetime) -> bool:
    """
    Check if a datetime has expired compared to current time.
    Handles both naive and aware datetimes.
    
    Args:
        expires_at: The expiration datetime to check
        
    Returns:
        bool: True if expired, False otherwise
    """
    now = utcnow()
    
    # Make both datetimes the same type (both aware or both naive)
    if expires_at.tzinfo is None:
        # If expires_at is naive, make now naive too
        now = make_naive(now)
    else:
        # If expires_at is aware, ensure it's in UTC
        expires_at = expires_at.astimezone(timezone.utc)
    return expires_at < now

def add_expiration(hours: int = 0, minutes: int = 0, seconds: int = 0) -> datetime:
    """
    Get a datetime in the future by adding the specified time to the current UTC time.
    
    Args:
        hours: Hours to add
        minutes: Minutes to add
        seconds: Seconds to add
        
    Returns:
        datetime: Future datetime with timezone information
    """
    return utcnow() + timedelta(hours=hours, minutes=minutes, seconds=seconds)
