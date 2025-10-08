import logging
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class HelmGenerator:
    """Generates Helm chart files for deployment projects."""

    # Base Helm files (at root of helm/ directory)
    BASE_HELM_FILES = [
        "Chart.yaml",
        "values.yaml",
        "values-dev.yaml",
        "values-staging.yaml",
        "values-prod.yaml"
    ]

    # Template files (in helm/templates/ subdirectory)
    TEMPLATE_FILES = [
        "deployment.yaml",
        "service.yaml",
        "ingress.yaml",
        "configmap.yaml",
        "serviceaccount.yaml",
        "hpa.yaml"
    ]

    # Helper files (in helm/templates/ subdirectory, no variable substitution)
    HELPER_FILES = ["_helpers.tpl"]

    # Delivery environment list
    DELIVERY_ENVIRONMENTS = ["dev", "staging", "prod"]

    def __init__(self, renderer: 'TemplateRenderer'):
        self.renderer = renderer

    async def generate_helm_files(
        self, project_type: str, repo_name: str
    ) -> Dict[str, str]:
        """Generate all Helm chart files for a project type.

        Args:
            project_type: Type of project (delivery, monorepo, etc.)
            repo_name: Name of the repository

        Returns:
            Dictionary mapping file paths to file contents
        """
        files = {}
        await self._add_base_files(files, project_type, repo_name)
        await self._add_template_files(files, project_type, repo_name)
        await self._add_helper_files(files, project_type)
        await self._add_helmignore(files)

        if project_type == "delivery":
            files.update(await self._generate_delivery_environments(repo_name))

        return files

    async def _add_base_files(
        self, files: Dict[str, str], project_type: str, repo_name: str
    ) -> None:
        """Add base Helm chart files."""
        await self._add_files_from_list(
            files, project_type, repo_name, self.BASE_HELM_FILES, subdir=""
        )

    async def _add_template_files(
        self, files: Dict[str, str], project_type: str, repo_name: str
    ) -> None:
        """Add Helm template files with variable substitution."""
        await self._add_files_from_list(
            files, project_type, repo_name, self.TEMPLATE_FILES, subdir="templates"
        )

    async def _add_helper_files(
        self, files: Dict[str, str], project_type: str
    ) -> None:
        """Add Helm helper files (no variable substitution)."""
        for helper_file in self.HELPER_FILES:
            s3_path = f"templates/project-types/{project_type}/helm/templates/{helper_file}"
            content = await self.renderer.get_static_template(s3_path)
            files[f"helm/templates/{helper_file}"] = content

    async def _add_helmignore(self, files: Dict[str, str]) -> None:
        """Add .helmignore file."""
        content = await self.renderer.get_static_template("templates/common/.helmignore")
        files["helm/.helmignore"] = content

    async def _add_files_from_list(
        self,
        files: Dict[str, str],
        project_type: str,
        repo_name: str,
        file_list: list,
        subdir: str = ""
    ) -> None:
        """Add multiple Helm files from a list.

        Args:
            files: Dictionary to add files to
            project_type: Type of project
            repo_name: Name of repository
            file_list: List of file names to add
            subdir: Subdirectory within helm/ (e.g., "templates")
        """
        for filename in file_list:
            # Build S3 template path
            s3_parts = ["templates", "project-types", project_type, "helm"]
            if subdir:
                s3_parts.append(subdir)
            s3_parts.append(filename)
            s3_path = "/".join(s3_parts)

            # Build output path
            output_parts = ["helm"]
            if subdir:
                output_parts.append(subdir)
            output_parts.append(filename)
            output_path = "/".join(output_parts)

            # Process template
            content = await self.renderer.process_template(
                s3_path, {"repo_name": repo_name}
            )
            files[output_path] = content

    async def _generate_delivery_environments(self, repo_name: str) -> Dict[str, str]:
        """Generate environment-specific files for delivery projects.

        Args:
            repo_name: Name of repository

        Returns:
            Dictionary of environment files
        """
        files = {}

        # Add environment-specific values and secrets
        for env in self.DELIVERY_ENVIRONMENTS:
            await self._add_environment_values(files, env, repo_name)
            await self._add_environment_secrets(files, env, repo_name)

        # Add environments README
        await self._add_environments_readme(files, repo_name)

        return files

    async def _add_environment_values(
        self, files: Dict[str, str], env: str, repo_name: str
    ) -> None:
        """Add environment values file."""
        s3_path = f"templates/project-types/delivery/environments/{env}/values.yaml"
        content = await self.renderer.process_template(
            s3_path,
            {
                "repo_name": repo_name,
                "cluster_domain": "example.com",
                "aws_account_id": "123456789012"
            }
        )
        files[f"environments/{env}/values.yaml"] = content

    async def _add_environment_secrets(
        self, files: Dict[str, str], env: str, repo_name: str
    ) -> None:
        """Add environment secrets template file."""
        s3_path = f"templates/project-types/delivery/environments/{env}/secrets.yaml"
        content = await self.renderer.process_template(
            s3_path, {"repo_name": repo_name}
        )
        files[f"environments/{env}/secrets.yaml"] = content

    async def _add_environments_readme(
        self, files: Dict[str, str], repo_name: str
    ) -> None:
        """Add environments README file."""
        s3_path = "templates/project-types/delivery/environments/README.md"
        content = await self.renderer.process_template(
            s3_path, {"repo_name": repo_name, "cluster_domain": "example.com"}
        )
        files["environments/README.md"] = content
