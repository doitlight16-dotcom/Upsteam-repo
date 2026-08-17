"""Ports: abstract interfaces implemented by the infrastructure layer.

Concrete implementations (SQLAlchemy repositories, the Telegram HTTP
client, the AI module HTTP client) are injected at the composition root
in main.py -- nothing in application/ imports infrastructure/.
"""
