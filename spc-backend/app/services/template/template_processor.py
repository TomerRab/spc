import logging
from typing import Dict, Optional

from app.schemas.template_models import TemplateContext
from .stack_config_manager import StackConfigManager
from .template_renderer import TemplateRenderer
from .helm_generator import HelmGenerator

logger = logging.getLogger(__name__)


class TemplateProcessor:
    """Main orchestrator for generating project files from templates."""

    def __init__(self) -> None:
        # Initialize components
        self.stack_manager = StackConfigManager()
        self.renderer = TemplateRenderer()
        self.helm_generator = HelmGenerator(self.renderer)

    async def get_project_files(self, context: TemplateContext) -> Dict[str, str]:
        """Generate all project files for a given project type and stack.

        Args:
            context: TemplateContext containing all variables needed for rendering

        Returns:
            Dictionary mapping file paths to their rendered content
        """
        files = {}
        stack_name = self._get_stack_name(context.stack)
        await self._add_core_files(files, context, stack_name)
        await self._add_optional_files(files, context, stack_name)
        return files

    def _get_stack_name(self, stack: Optional[str]) -> str:
        """Get normalized stack name."""
        return stack if stack else ""

    async def _add_core_files(self, files: Dict[str, str], context: TemplateContext, stack_name: str) -> None:
        """Add core required files to the project."""
        files.update(await self._generate_ci_files(context, stack_name))
        files.update(await self._generate_gitignore(context.project_type, stack_name))
        files.update(await self._generate_readme(context, stack_name))

    async def _add_optional_files(self, files: Dict[str, str], context: TemplateContext, stack_name: str) -> None:
        """Add optional files based on project configuration."""
        if context.stack and context.project_type != "delivery":
            files.update(await self._generate_stack_files(context.project_type, context.stack, context.repo_name))
        if self.stack_manager.requires_helm(context.project_type):
            files.update(await self.helm_generator.generate_helm_files(context.project_type, context.repo_name, context.environments))

    async def _generate_ci_files(self, context: TemplateContext, stack_name: str) -> Dict[str, str]:
        """Generate CI/CD pipeline files."""
        if context.project_type == "delivery":
            content = await self._generate_delivery_ci(context.repo_name)
        else:
            content = await self._generate_standard_ci(context, stack_name)
        return {".gitlab-ci.yml": content}

    async def _generate_delivery_ci(self, repo_name: str) -> str:
        """Generate CI file for delivery projects."""
        return await self.renderer.process_template(
            "templates/project-types/delivery/gitlab-ci.yml.j2",
            {"repo_name": repo_name, "cluster_domain": "example.com"},
        )

    async def _generate_standard_ci(self, context: TemplateContext, stack_name: str) -> str:
        """Generate CI file for standard projects.

        Injects the delivery_url into the template context if available.
        This allows microservice CI templates to reference their delivery repositories.
        """
        template_vars = {
            "repo_name": context.repo_name,
            "stack": stack_name,
        }

        # Add delivery_url if present (for microservices with separate delivery repos)
        if context.delivery_url:
            template_vars["delivery_url"] = context.delivery_url
            logger.info(f"Injecting delivery_url into CI template: {context.delivery_url}")

        return await self.renderer.process_template(
            f"templates/project-types/{context.project_type}/{stack_name}.gitlab-ci.yml.j2",
            template_vars,
        )

    async def _generate_stack_files(self, project_type: str, stack: str, repo_name: str) -> Dict[str, str]:
        """Generate stack-specific configuration and Docker files."""
        files = {}
        await self._add_config_file(files, stack)
        await self._add_docker_files(files, project_type, stack)
        return files

    async def _add_config_file(self, files: Dict[str, str], stack: str) -> None:
        """Add stack configuration file if available."""
        config_file = self.stack_manager.get_config_file(stack)
        if config_file:
            content = await self.renderer.get_static_template(f"templates/stacks/{stack}/{config_file}")
            files[config_file] = content

    async def _add_docker_files(self, files: Dict[str, str], project_type: str, stack: str) -> None:
        """Add Docker files if required."""
        if not self.stack_manager.requires_docker(project_type, stack):
            return
        await self._add_dockerfile(files, stack)
        await self._add_dockerignore(files)

    async def _add_dockerfile(self, files: Dict[str, str], stack: str) -> None:
        """Add Dockerfile for the stack."""
        dockerfile_content = await self.renderer.get_static_template(
            f"templates/docker/{stack}.Dockerfile"
        )
        files["build/Dockerfile"] = dockerfile_content

    async def _add_dockerignore(self, files: Dict[str, str]) -> None:
        """Add .dockerignore file."""
        dockerignore_content = await self.renderer.get_static_template("templates/docker/.dockerignore")
        files["build/.dockerignore"] = dockerignore_content

    async def _generate_gitignore(self, project_type: str, stack_name: str) -> Dict[str, str]:
        """Generate gitignore file."""
        gitignore_path = self._get_gitignore_path(project_type, stack_name)
        content = await self.renderer.get_static_template(gitignore_path)
        return {".gitignore": content}

    def _get_gitignore_path(self, project_type: str, stack_name: str) -> str:
        """Get the appropriate gitignore template path."""
        if project_type == "delivery":
            return "templates/project-types/delivery/.gitignore"
        return self._get_stack_gitignore_path(stack_name)

    def _get_stack_gitignore_path(self, stack_name: str) -> str:
        """Get gitignore path for stack-specific projects."""
        if stack_name:
            return f"templates/stacks/{stack_name}/.gitignore"
        return "templates/common/.gitignore"

    async def _generate_readme(self, context: TemplateContext, stack_name: str) -> Dict[str, str]:
        """Generate README file."""
        if context.project_type == "delivery":
            content = await self._generate_delivery_readme(context.repo_name)
        else:
            content = await self._generate_standard_readme(context.repo_name, stack_name, context.project_type)
        return {"README.md": content}

    async def _generate_delivery_readme(self, repo_name: str) -> str:
        """Generate README for delivery projects."""
        return await self.renderer.process_template(
            "templates/project-types/delivery/README.md",
            {"repo_name": repo_name, "cluster_domain": "example.com"},
        )

    async def _generate_standard_readme(self, repo_name: str, stack_name: str, project_type: str) -> str:
        """Generate README for standard projects."""
        return await self.renderer.process_template(
            "templates/common/README.md.j2",
            {"repo_name": repo_name, "stack": stack_name, "project_type": project_type},
        )