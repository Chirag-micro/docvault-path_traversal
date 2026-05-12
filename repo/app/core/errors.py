"""Domain-level exceptions used across the service layer."""


class DocVaultError(Exception):
    """Base class for all DocVault domain errors."""


class TemplateNotFoundError(DocVaultError):
    """Raised when a template cannot be located on disk."""


class InvalidTemplateRequest(DocVaultError):
    """Raised when the requested template name or locale is malformed."""


class TemplateAccessDenied(DocVaultError):
    """Raised when a resolved path falls outside the sandbox."""
