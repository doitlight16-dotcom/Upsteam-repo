"""Application layer: use cases and ports (interfaces).

This layer orchestrates domain objects to fulfill a use case. It defines
the *interfaces* that infrastructure must implement (repositories, the
Telegram bot provider, the AI module client) but never imports a concrete
implementation directly -- that is the Dependency Inversion Principle in
practice, not just in theory.
"""
