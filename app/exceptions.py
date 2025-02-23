class LinkShortenerError(Exception):
    """Base exception for link shortener."""
    pass

class LinkNotFoundError(LinkShortenerError):
    """Raised when a link is not found."""
    pass

class InvalidUrlError(LinkShortenerError):
    """Raised when the provided URL is invalid."""
    pass