import time
from functools import wraps

def exponential_backoff(retries=5, backoff_factor=1):
    """
    Decorator for implementing exponential backoff on a function.
    Args:
        retries (int): Number of retries before giving up.
        backoff_factor (float): Base wait time in seconds, multiplied exponentially.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    wait_time = backoff_factor * (2 ** (attempt - 1))
                    print(f"Attempt {attempt} failed: {e}. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
            raise Exception(f"All {retries} retries failed for {func.__name__}")
        return wrapper
    return decorator
