import logging
from typing import Dict, Optional

from .stack_config_manager import StackConfigManager
from .template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class TemplateProcessor:
    """Main orchestrator for generating project files from templates."""
    
    def __init__(self, s3_bucket: Optional[str] = None, s3_region: Optional[str] = None) -> None:
        # Initialize components
        self.stack_manager = StackConfigManager()
        self.renderer = TemplateRenderer(s3_bucket=s3_bucket, s3_region=s3_region)

    async def get_project_files(
        self, project_type: str, repo_name: str, stack: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate all project files for a given project type and stack."""
        files = {}
        stack_name = self._get_stack_name(stack)
        await self._add_core_files(files, project_type, repo_name, stack_name)
        await self._add_optional_files(files, project_type, repo_name, stack)
        return files

    def _get_stack_name(self, stack: Optional[str]) -> str:
        """Get normalized stack name."""
        return stack if stack else ""

    async def _add_core_files(self, files: Dict[str, str], project_type: str, repo_name: str, stack_name: str) -> None:
        """Add core required files to the project."""
        files.update(await self._generate_ci_files(project_type, repo_name, stack_name))
        files.update(await self._generate_gitignore(project_type, stack_name))
        files.update(await self._generate_readme(project_type, repo_name, stack_name))

    async def _add_optional_files(self, files: Dict[str, str], project_type: str, repo_name: str, stack: Optional[str]) -> None:
        """Add optional files based on project configuration."""
        if stack and project_type != "delivery":
            files.update(await self._generate_stack_files(project_type, stack, repo_name))
        if self.stack_manager.requires_helm(project_type):
            files.update(await self._generate_helm_files(project_type, repo_name))

    async def _generate_ci_files(self, project_type: str, repo_name: str, stack_name: str) -> Dict[str, str]:
        """Generate CI/CD pipeline files."""
        if project_type == "delivery":
            content = await self._generate_delivery_ci(repo_name)
        else:
            content = await self._generate_standard_ci(project_type, repo_name, stack_name)
        return {".gitlab-ci.yml": content}

    async def _generate_delivery_ci(self, repo_name: str) -> str:
        """Generate CI file for delivery projects."""
        return await self.renderer.process_template(
            "delivery/.gitlab-ci.yml",
            {"repo_name": repo_name, "cluster_domain": "example.com"},
        )

    async def _generate_standard_ci(self, project_type: str, repo_name: str, stack_name: str) -> str:
        """Generate CI file for standard projects."""
        return await self.renderer.process_template(
            f"{project_type}/{stack_name}.gitlab-ci.yml",
            {"repo_name": repo_name, "stack": stack_name},
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
            content = await self.renderer.get_static_template(f"common/config/{config_file}")
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
            f"common/build/Dockerfiles/{stack}.Dockerfile"
        )
        files["build/Dockerfile"] = dockerfile_content

    async def _add_dockerignore(self, files: Dict[str, str]) -> None:
        """Add .dockerignore file."""
        dockerignore_content = await self.renderer.get_static_template("common/build/.dockerignore")
        files["build/.dockerignore"] = dockerignore_content

    async def _generate_gitignore(self, project_type: str, stack_name: str) -> Dict[str, str]:
        """Generate gitignore file."""
        gitignore_path = self._get_gitignore_path(project_type, stack_name)
        content = await self.renderer.get_static_template(gitignore_path)
        return {".gitignore": content}

    def _get_gitignore_path(self, project_type: str, stack_name: str) -> str:
        """Get the appropriate gitignore template path."""
        if project_type == "delivery":
            return "delivery/.gitignore"
        return self._get_stack_gitignore_path(stack_name)

    def _get_stack_gitignore_path(self, stack_name: str) -> str:
        """Get gitignore path for stack-specific projects."""
        if stack_name:
            return f"common/gitignore/{stack_name}.gitignore"
        return "common/gitignore/.gitignore"

    async def _generate_helm_files(self, project_type: str, repo_name: str) -> Dict[str, str]:
        """Generate Helm chart files for deployment projects."""
        files = {}
        await self._add_basic_helm_files(files, project_type, repo_name)
        await self._add_helm_template_files(files, project_type, repo_name)
        await self._add_helm_helper_files(files, project_type)
        await self._add_helm_ignore_file(files, project_type)
        await self._add_delivery_environments_if_needed(files, project_type, repo_name)
        return files

    async def _add_basic_helm_files(self, files: Dict[str, str], project_type: str, repo_name: str) -> None:
        """Add basic Helm chart files."""
        helm_files = ["Chart.yaml", "values.yaml", "values-dev.yaml", "values-staging.yaml", "values-prod.yaml"]
        for helm_file in helm_files:
            await self._add_single_helm_file(files, project_type, repo_name, helm_file)

    async def _add_single_helm_file(self, files: Dict[str, str], project_type: str, repo_name: str, helm_file: str) -> None:
        """Add a single Helm file to the files collection."""
        content = await self.renderer.process_template(
            f"{project_type}/helm/{helm_file}",
            {"repo_name": repo_name},
        )
        files[f"helm/{helm_file}"] = content

    async def _add_helm_template_files(self, files: Dict[str, str], project_type: str, repo_name: str) -> None:
        """Add Helm template files that need variable substitution."""
        template_files = ["deployment.yaml", "service.yaml", "ingress.yaml", "configmap.yaml", "serviceaccount.yaml", "hpa.yaml"]
        for template_file in template_files:
            await self._add_single_helm_template_file(files, project_type, repo_name, template_file)

    async def _add_single_helm_template_file(self, files: Dict[str, str], project_type: str, repo_name: str, template_file: str) -> None:
        """Add a single Helm template file."""
        content = await self.renderer.process_template(
            f"{project_type}/helm/templates/{template_file}",
            {"repo_name": repo_name},
        )
        files[f"helm/templates/{template_file}"] = content

    async def _add_helm_helper_files(self, files: Dict[str, str], project_type: str) -> None:
        """Add Helm helper template files."""
        helper_files = ["_helpers.tpl"]
        for helper_file in helper_files:
            content = await self.renderer.get_static_template(f"{project_type}/helm/templates/{helper_file}")
            files[f"helm/templates/{helper_file}"] = content

    async def _add_helm_ignore_file(self, files: Dict[str, str], project_type: str) -> None:
        """Add .helmignore file."""
        content = await self.renderer.get_static_template(f"{project_type}/helm/.helmignore")
        files["helm/.helmignore"] = content

    async def _add_delivery_environments_if_needed(self, files: Dict[str, str], project_type: str, repo_name: str) -> None:
        """Add delivery environment configurations if needed."""
        if project_type == "delivery":
            files.update(await self._generate_delivery_environments(repo_name))

    async def _generate_delivery_environments(self, repo_name: str) -> Dict[str, str]:
        """Generate environment-specific files for delivery projects."""
        files = {}
        environments = ["dev", "staging", "prod"]
        await self._add_environment_files(files, environments, repo_name)
        await self._add_environments_readme(files, repo_name)
        return files

    async def _add_environment_files(self, files: Dict[str, str], environments: list, repo_name: str) -> None:
        """Add environment-specific values and secrets files."""
        for env in environments:
            await self._add_environment_values(files, env, repo_name)
            await self._add_environment_secrets(files, env, repo_name)

    async def _add_environment_values(self, files: Dict[str, str], env: str, repo_name: str) -> None:
        """Add environment values file."""
        env_values = await self.renderer.process_template(
            f"delivery/environments/{env}/values.yaml",
            {"repo_name": repo_name, "cluster_domain": "example.com", "aws_account_id": "123456789012"},
        )
        files[f"environments/{env}/values.yaml"] = env_values

    async def _add_environment_secrets(self, files: Dict[str, str], env: str, repo_name: str) -> None:
        """Add environment secrets template file."""
        env_secrets = await self.renderer.process_template(
            f"delivery/environments/{env}/secrets.yaml",
            {"repo_name": repo_name},
        )
        files[f"environments/{env}/secrets.yaml"] = env_secrets

    async def _add_environments_readme(self, files: Dict[str, str], repo_name: str) -> None:
        """Add environments README file."""
        env_readme = await self.renderer.process_template(
            "delivery/environments/README.md",
            {"repo_name": repo_name, "cluster_domain": "example.com"},
        )
        files["environments/README.md"] = env_readme

    async def _generate_readme(self, project_type: str, repo_name: str, stack_name: str) -> Dict[str, str]:
        """Generate README file."""
        if project_type == "delivery":
            content = await self._generate_delivery_readme(repo_name)
        else:
            content = await self._generate_standard_readme(repo_name, stack_name, project_type)
        return {"README.md": content}

    async def _generate_delivery_readme(self, repo_name: str) -> str:
        """Generate README for delivery projects."""
        return await self.renderer.process_template(
            "delivery/README.md",
            {"repo_name": repo_name, "cluster_domain": "example.com"},
        )

    async def _generate_standard_readme(self, repo_name: str, stack_name: str, project_type: str) -> str:
        """Generate README for standard projects."""
        return await self.renderer.process_template(
            "common/README.md.j2",
            {"repo_name": repo_name, "stack": stack_name, "project_type": project_type},
        )