import logging
from typing import Dict, List, Optional, TYPE_CHECKING

from app.utils.constants import ENVIRONMENT_NAMES

if TYPE_CHECKING:
    from .template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class HelmGenerator:
    """Generates Helm chart files for deployment projects."""

    def __init__(self, renderer: 'TemplateRenderer'):
        self.renderer = renderer

    async def generate_helm_files(
        self,
        project_type: str,
        repo_name: str,
        environments: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Generate Helm chart files for a project type.

        Args:
            project_type: Type of project (delivery, monorepo)
            repo_name: Name of the repository
            environments: List of environment keys (e.g., ['a', 'b', 'c'])

        Returns:
            Dictionary mapping file paths to file contents
        """
        files = {}

        # Generate base Chart.yaml and values.yaml from S3
        await self._add_chart_yaml(files, project_type, repo_name)
        await self._add_values_yaml(files, project_type, repo_name)

        # Generate values-{env}.yaml for each environment
        if environments:
            await self._add_environment_values(files, project_type, repo_name, environments)

        # Add .helmignore
        await self._add_helmignore(files)

        return files

    async def _add_chart_yaml(
        self, files: Dict[str, str], project_type: str, repo_name: str
    ) -> None:
        """Add Chart.yaml from S3 template."""
        s3_path = f"templates/project-types/{project_type}/helm/Chart.yaml.j2"
        content = await self.renderer.process_template(
            s3_path, {"repo_name": repo_name}
        )
        files["helm/Chart.yaml"] = content

    async def _add_values_yaml(
        self, files: Dict[str, str], project_type: str, repo_name: str
    ) -> None:
        """Add values.yaml from S3 template."""
        s3_path = f"templates/project-types/{project_type}/helm/values.yaml.j2"
        content = await self.renderer.process_template(
            s3_path, {"repo_name": repo_name}
        )
        files["helm/values.yaml"] = content

    async def _add_environment_values(
        self,
        files: Dict[str, str],
        project_type: str,
        repo_name: str,
        environments: List[str]
    ) -> None:
        """Add values-{env}.yaml for each environment.

        Each environment-specific values file has the same structure as values.yaml,
        allowing for environment-specific overrides.
        """
        s3_path = f"templates/project-types/{project_type}/helm/values.yaml.j2"

        for env_key in environments:
            # Convert environment name to lowercase with hyphens (e.g., "Production A" -> "production-a")
            env_display_name = ENVIRONMENT_NAMES.get(env_key, env_key)
            env_file_name = env_display_name.lower().replace(' ', '-')

            content = await self.renderer.process_template(
                s3_path, {"repo_name": repo_name}
            )
            files[f"helm/values-{env_file_name}.yaml"] = content

    async def _add_helmignore(self, files: Dict[str, str]) -> None:
        """Add .helmignore file from common templates."""
        content = await self.renderer.get_static_template("templates/common/.helmignore")
        files["helm/.helmignore"] = content
