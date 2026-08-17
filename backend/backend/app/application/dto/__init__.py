"""Data transfer objects used to move data across layer boundaries.

Distinct from both domain entities and API (Pydantic) schemas -- keeping
these separate means a change to the public API shape never forces a
change to the domain model, and vice versa.
"""
