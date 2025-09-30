"""Custom exceptions for the SPC application."""


class SPCBaseException(Exception):
    """Base exception for all SPC-related errors."""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class GitLabError(SPCBaseException):
    """Exception for GitLab-related operations."""
    
    def __init__(self, message: str, status_code: int = None, operation: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.operation = operation
        self.details.update({
            'status_code': status_code,
            'operation': operation
        })


class GitLabConnectionError(GitLabError):
    """Exception for GitLab connection issues."""
    pass


class GitLabAuthenticationError(GitLabError):
    """Exception for GitLab authentication issues."""
    pass


class GitLabRepositoryError(GitLabError):
    """Exception for GitLab repository operations."""
    pass


class TemplateError(SPCBaseException):
    """Exception for template processing errors."""
    
    def __init__(self, message: str, template_name: str = None, template_path: str = None):
        super().__init__(message)
        self.template_name = template_name
        self.template_path = template_path
        self.details.update({
            'template_name': template_name,
            'template_path': template_path
        })


class TemplateNotFoundError(TemplateError):
    """Exception when template file is not found."""
    pass


class TemplateRenderError(TemplateError):
    """Exception when template rendering fails."""
    pass


class ValidationError(SPCBaseException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: str = None, value: str = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.details.update({
            'field': field,
            'value': value
        })


class ProjectCreationError(SPCBaseException):
    """Exception for project creation errors."""
    
    def __init__(self, message: str, project_name: str = None, project_type: str = None):
        super().__init__(message)
        self.project_name = project_name
        self.project_type = project_type
        self.details.update({
            'project_name': project_name,
            'project_type': project_type
        })


class ConfigurationError(SPCBaseException):
    """Exception for configuration-related errors."""
    
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message)
        self.config_key = config_key
        self.details.update({
            'config_key': config_key
        })


class S3Error(SPCBaseException):
    """Exception for S3-related operations."""
    
    def __init__(self, message: str, bucket: str = None, key: str = None):
        super().__init__(message)
        self.bucket = bucket
        self.key = key
        self.details.update({
            'bucket': bucket,
            'key': key
        })