# this package exposes router modules used by API.py
# modules are left unimported here to avoid circular imports during startup
# but the API imports them explicitly when setting up the application.

# we still define __all__ for clarity
__all__ = [
    "auth",
    "profile",
    "projects",
    "campaigns",
    "documents",
]
