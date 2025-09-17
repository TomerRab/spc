from typing import Dict, Optional


class StackConfigManager:
    """Manages stack-specific configurations and mappings."""
    
    STACK_CONFIGS = {
        "maven": "settings.xml",
        "spring": "settings.xml",  # Spring uses Maven
        "node": ".npmrc",
        "react": ".npmrc",  # React uses npm
        "typescript": ".npmrc",  # TypeScript uses npm
        "javascript": ".npmrc",  # JavaScript uses npm
        "vue": ".npmrc",  # Vue uses npm
        "python": "pip.ini",
        "dotnet": "nuget.config",
        "csharp": "nuget.config",  # C# uses NuGet
    }

    STACK_FALLBACKS = {
        # Spring -> Maven fallbacks
        "spring": "maven",
        # React/TypeScript/JavaScript/Vue -> Node fallbacks
        "react": "node",
        "typescript": "node", 
        "javascript": "node",
        "vue": "node",
        # C# -> .NET fallbacks
        "csharp": "dotnet",
    }

    def get_config_file(self, stack: str) -> Optional[str]:
        """Get the configuration file name for a stack."""
        return self.STACK_CONFIGS.get(stack)

    def get_fallback_template(self, template_path: str) -> Optional[str]:
        """Get fallback template path for common stack mappings."""
        for stack, fallback_stack in self.STACK_FALLBACKS.items():
            if f"/{stack}." in template_path:
                return template_path.replace(f"/{stack}.", f"/{fallback_stack}.")
        return None

    def requires_docker(self, project_type: str, stack: str) -> bool:
        """Check if project type and stack combination requires Docker files."""
        return stack and project_type != "library"

    def requires_helm(self, project_type: str) -> bool:
        """Check if project type requires Helm charts."""
        return project_type in ["monorepo", "delivery"]