from typing import Dict, Optional


class StackConfigManager:
    """Manages stack-specific configurations and mappings."""
    
    STACK_CONFIGS = {
        "maven": "settings.xml",
        "spring": "settings.xml",  # Spring uses Maven
        "node": ".npmrc",
        "react": ".npmrc",  # React uses npm
        "python": "pip.ini",
        "dotnet": "nuget.config",
        "csharp": "nuget.config",  # C# uses NuGet
    }

    STACK_FALLBACKS = {
        # Spring -> Maven fallbacks
        "spring": "maven",
        # React -> Node fallbacks
        "react": "node",
        # C# -> .NET fallbacks
        "csharp": "dotnet",
    }

    def get_config_file(self, stack: str) -> Optional[str]:
        """Get the configuration file name for a stack."""
        return self.STACK_CONFIGS.get(stack)

    def get_fallback_template(self, template_path: str) -> Optional[str]:
        """Get fallback template path for common stack mappings.

        Examples:
            library/spring.gitlab-ci.yml -> library/maven.gitlab-ci.yml
            microservice/react.gitlab-ci.yml -> microservice/node.gitlab-ci.yml
        """
        # Extract stack from path (handles both /stack. and /stack/ patterns)
        for stack, fallback_stack in self.STACK_FALLBACKS.items():
            # Handle pattern: /stack.extension (e.g., /spring.gitlab-ci.yml)
            if f"/{stack}." in template_path:
                fallback_path = template_path.replace(f"/{stack}.", f"/{fallback_stack}.")
                return fallback_path
            # Handle pattern: /stack/ (e.g., /spring/)
            if f"/{stack}/" in template_path:
                fallback_path = template_path.replace(f"/{stack}/", f"/{fallback_stack}/")
                return fallback_path
        return None

    def requires_docker(self, project_type: str, stack: str) -> bool:
        """Check if project type and stack combination requires Docker files."""
        return stack and project_type != "library"

    def requires_helm(self, project_type: str) -> bool:
        """Check if project type requires Helm charts."""
        return project_type in ["monorepo", "delivery"]