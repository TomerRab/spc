"""Template context models for rendering project templates."""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class TemplateContext:
    """Context object containing all variables needed for template rendering.

    This class encapsulates all parameters needed to generate project files from templates,
    providing a clean interface and avoiding parameter explosion in function signatures.

    Attributes:
        project_type: Type of project (library, microservice, standalone-microservice, delivery)
        repo_name: Repository name (sanitized)
        stack: Technology stack (maven, node, python, dotnet, etc.)
        environments: List of deployment environments (a, b, c, d)
        delivery_url: URL of the associated delivery repository (for microservices only)

    Example:
        >>> context = TemplateContext(
        ...     project_type="microservice",
        ...     repo_name="my-service",
        ...     stack="python",
        ...     environments=["a", "b"],
        ...     delivery_url="https://gitlab.com/group/my-service-delivery.git"
        ... )
        >>> files = await template_processor.get_project_files(context)
    """

    project_type: str
    repo_name: str
    stack: Optional[str] = None
    environments: Optional[List[str]] = None
    delivery_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert context to dictionary for template rendering.

        Returns:
            Dictionary containing all non-None attributes suitable for Jinja2 rendering.
        """
        return {
            "project_type": self.project_type,
            "repo_name": self.repo_name,
            "stack": self.stack or "",
            "environments": self.environments or [],
            "delivery_url": self.delivery_url or "",
        }
