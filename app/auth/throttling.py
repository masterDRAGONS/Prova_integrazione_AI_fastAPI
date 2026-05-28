import time
from collections import defaultdict

from fastapi import HTTPException, status
from ..config import settings

# In-memory storage for user requests
user_requests = defaultdict(list)


def apply_rate_limit(user_id: str) -> bool:
    current_time = time.time()

    # Determine rate limits based on user type
    if user_id == "global_unauthenticated_user":
        rate_limit = settings.global_rate_limit
        time_window = settings.global_time_window_seconds
    else:
        rate_limit = settings.auth_rate_limit
        time_window = settings.auth_time_window_seconds

    # Filter out requests older than the time window
    user_requests[user_id] = [
        t for t in user_requests[user_id] if t > current_time - time_window
    ]

    if len(user_requests[user_id]) >= rate_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )

    # Log current usage
    current_usage = len(user_requests[user_id])
    print(f"User {user_id}: {current_usage + 1}/{rate_limit} requests used.")

    user_requests[user_id].append(current_time)
    return True