import time
from functools import wraps

def retry(times=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error en {func.__name__}: {e} (intento {attempt+1}/{times})")
                    time.sleep(delay)
            raise Exception(f"Falló después de {times} intentos: {func.__name__}")
        return wrapper
    return decorator