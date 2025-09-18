class GitLabError(Exception):
    """Base exception for GitLab-related operations."""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class TemplateError(Exception):
    """Exception for template processing errors."""
    def __init__(self, message: str, template_name: str = None):
        self.message = message
        self.template_name = template_name
        super().__init__(self.message)

class ValidationError(Exception):
    """Exception for validation errors."""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class ProjectCreationError(Exception):
    """Exception for project creation errors."""
    def __init__(self, message: str, project_name: str = None):
        self.message = message
        self.project_name = project_name
        super().__init__(self.message)