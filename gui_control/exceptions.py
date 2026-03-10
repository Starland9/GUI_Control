class AutomationError(Exception):
    """Base class for errors raised by the automation library."""


class NoObjectFound(AutomationError):
    """Raised when no matching object is detected on screen."""


class ClickFailure(AutomationError):
    """Raised when multiple click attempts all fail."""
