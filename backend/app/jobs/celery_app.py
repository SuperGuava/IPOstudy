import os
from collections.abc import Callable


class _FallbackCelery:
    def __init__(self) -> None:
        self.tasks: dict[str, Callable] = {}
        self.conf: dict = {"beat_schedule": {}}

    def task(self, name: str | None = None) -> Callable:
        def decorator(fn: Callable) -> Callable:
            self.tasks[name or fn.__name__] = fn
            return fn

        return decorator


def create_celery_app():
    try:
        from celery import Celery  # type: ignore
    except ModuleNotFoundError:
        return _FallbackCelery()

    app = Celery("anti_gravity")
    app.conf.update(
        broker_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        result_backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    )
    return app


celery_app = create_celery_app()
