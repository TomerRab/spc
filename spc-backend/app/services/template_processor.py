import logging
from typing import Dict, Optional

from app.services.stack_config_manager import StackConfigManager
from app.services.template_renderer import TemplateRenderer

logger = logging.getLogger(__name__)


class TemplateProcessor:
    """Main orchestrator for generating project files from templates."""
    
    def __init__(self, s3_bucket: str = None, s3_region: str = None):
        # Initialize components
        self.stack_manager = StackConfigManager()
        self.renderer = TemplateRenderer()

    async def get_project_files(
        self, project_type: str, repo_name: str, stack: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate all project files for a given project type and stack."""
        files = {}
        stack_name = stack if stack else ""

        # Generate CI files
        files.update(await self._generate_ci_files(project_type, repo_name, stack_name))
        
        # Generate stack-specific files
        if stack and project_type != "delivery":
            files.update(await self._generate_stack_files(project_type, stack, repo_name))

        # Generate gitignore
        files.update(await self._generate_gitignore(project_type, stack_name))

        # Generate Helm files for deployment projects
        if self.stack_manager.requires_helm(project_type):
            files.update(await self._generate_helm_files(project_type, repo_name))

        # Generate README
        files.update(await self._generate_readme(project_type, repo_name, stack_name))

        return files

    async def _generate_ci_files(self, project_type: str, repo_name: str, stack_name: str) -> Dict[str, str]:
        """Generate CI/CD pipeline files."""
        if project_type == "delivery":
            content = await self.renderer.process_template(
                "delivery/.gitlab-ci.yml",
                {"repo_name": repo_name, "cluster_domain": "example.com"},
            )
        else:
            content = await self.renderer.process_template(
                f"{project_type}/{stack_name}.gitlab-ci.yml",
                {"repo_name": repo_name, "stack": stack_name},
            )
        
        return {".gitlab-ci.yml": content}

    async def _generate_stack_files(self, project_type: str, stack: str, repo_name: str) -> Dict[str, str]:
        """Generate stack-specific configuration and Docker files."""
        files = {}
        
        # Configuration file
        config_file = self.stack_manager.get_config_file(stack)
        if config_file:
            content = await self.renderer.get_static_template(f"common/config/{config_file}")
            files[config_file] = content

        # Docker files
        if self.stack_manager.requires_docker(project_type, stack):
            dockerfile_content = await self.renderer.get_static_template(
                f"common/build/Dockerfiles/{stack}.Dockerfile"
            )
            files["build/Dockerfile"] = dockerfile_content
            
            dockerignore_content = await self.renderer.get_static_template(
                "common/build/.dockerignore"
            )
            files["build/.dockerignore"] = dockerignore_content

        return files

    async def _generate_gitignore(self, project_type: str, stack_name: str) -> Dict[str, str]:
        """Generate gitignore file."""
        if project_type == "delivery":
            gitignore_path = "delivery/.gitignore"
        else:
            gitignore_path = (
                f"common/gitignore/{stack_name}.gitignore"
                if stack_name
                else "common/gitignore/.gitignore"
            )
        
        content = await self.renderer.get_static_template(gitignore_path)
        return {".gitignore": content}

    async def _generate_helm_files(self, project_type: str, repo_name: str) -> Dict[str, str]:
        """Generate Helm chart files for deployment projects."""
        files = {}
        
        # Basic Helm chart files
        helm_files = ["Chart.yaml", "values.yaml", "values-dev.yaml", "values-staging.yaml", "values-prod.yaml"]
        for helm_file in helm_files:
            content = await self.renderer.process_template(
                f"{project_type}/helm/{helm_file}",
                {"repo_name": repo_name},
            )
            files[f"helm/{helm_file}"] = content
        
        # Helm template files that need variable substitution
        template_files = [
            "deployment.yaml", "service.yaml", "ingress.yaml", 
            "configmap.yaml", "serviceaccount.yaml", "hpa.yaml"
        ]
        for template_file in template_files:
            content = await self.renderer.process_template(
                f"{project_type}/helm/templates/{template_file}",
                {"repo_name": repo_name},
            )
            files[f"helm/templates/{template_file}"] = content
        
        # Helm helper templates (no variable substitution needed)
        helper_files = ["_helpers.tpl"]
        for helper_file in helper_files:
            content = await self.renderer.get_static_template(
                f"{project_type}/helm/templates/{helper_file}"
            )
            files[f"helm/templates/{helper_file}"] = content

        # Add .helmignore
        content = await self.renderer.get_static_template(f"{project_type}/helm/.helmignore")
        files["helm/.helmignore"] = content
        
        # For delivery projects, add environment configurations
        if project_type == "delivery":
            files.update(await self._generate_delivery_environments(repo_name))

        return files

    async def _generate_delivery_environments(self, repo_name: str) -> Dict[str, str]:
        """Generate environment-specific files for delivery projects."""
        files = {}
        environments = ["dev", "staging", "prod"]
        
        for env in environments:
            # Environment values
            env_values = await self.renderer.process_template(
                f"delivery/environments/{env}/values.yaml",
                {"repo_name": repo_name, "cluster_domain": "example.com", "aws_account_id": "123456789012"},
            )
            files[f"environments/{env}/values.yaml"] = env_values
            
            # Environment secrets (template only)
            env_secrets = await self.renderer.process_template(
                f"delivery/environments/{env}/secrets.yaml",
                {"repo_name": repo_name},
            )
            files[f"environments/{env}/secrets.yaml"] = env_secrets
        
        # Add environments README
        env_readme = await self.renderer.process_template(
            "delivery/environments/README.md",
            {"repo_name": repo_name, "cluster_domain": "example.com"},
        )
        files["environments/README.md"] = env_readme
        
        return files

    async def _generate_readme(self, project_type: str, repo_name: str, stack_name: str) -> Dict[str, str]:
        """Generate README file."""
        if project_type == "delivery":
            content = await self.renderer.process_template(
                "delivery/README.md",
                {"repo_name": repo_name, "cluster_domain": "example.com"},
            )
        else:
            content = await self.renderer.process_template(
                "common/README.md.j2",
                {"repo_name": repo_name, "stack": stack_name, "project_type": project_type},
            )
        
        return {"README.md": content}