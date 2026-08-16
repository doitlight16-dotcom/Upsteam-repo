"""Infrastructure layer: concrete implementations of application ports.

Database repositories, the Telegram client, the AI module client, and the
Redis cache client all live here. This is the only layer allowed to import
third-party I/O libraries (SQLAlchemy, httpx, redis).
"""
