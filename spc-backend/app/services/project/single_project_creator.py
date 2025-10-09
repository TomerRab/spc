import logging
from typing import Dict, List

from fastapi import HTTPException

from app.schemas.repo_models import RepoRequest
from app.schemas.response_models import create_project_response
from app.utils.exceptions import TemplateNotFoundError, TemplateError
from .variable_manager import VariableManager

logger = logging.getLogger(__name__)


class SingleProjectCreator:
    """Handles creation of single repository projects (library, standalone-microservice, delivery)."""
    
    def __init__(self, gitlab_service, template_processor) -> None:
        self.gitlab_service = gitlab_service
        self.template_processor = template_processor
        self.variable_manager = VariableManager()

    async def create(self, token: str, repo_request: RepoRequest) -> Dict:
        """Create a single repository project."""
        project_id = None
        try:
            files = await self._generate_project_files(repo_request)
            repo_url, project_id = await self._create_and_initialize_repository(token, repo_request, files)
            variables_created = await self._setup_project_variables(token, project_id, repo_request)
            return self._build_success_response(repo_request, repo_url, project_id, files, variables_created)
        except (TemplateNotFoundError, TemplateError) as e:
            # Template errors are 400 (user chose wrong stack/config)
            if project_id:
                await self._cleanup_failed_project(token, project_id, repo_request.name)
            logger.warning(f"Project creation failed due to template issue: {str(e)}")
            raise  # Re-raise to let error handler deal with it (returns 400)
        except Exception as e:
            if project_id:
                await self._cleanup_failed_project(token, project_id, repo_request.name)
            logger.error(f"Single project creation failed: {str(e)}")
            raise  # Re-raise to let error handler deal with it

    async def _cleanup_failed_project(self, token: str, project_id: int, project_name: str) -> None:
        """Clean up failed project creation."""
        try:
            logger.warning(f"Cleaning up failed project: {project_name} (ID: {project_id})")
            await self.gitlab_service.delete_repository(token, project_id)
            logger.info(f"Successfully cleaned up failed project: {project_name}")
        except Exception as cleanup_error:
            logger.error(f"Failed to cleanup project {project_name}: {str(cleanup_error)}")

    async def _generate_project_files(self, repo_request: RepoRequest) -> Dict[str, str]:
        """Generate template files for the project."""
        # Extract environment keys from openshiftServers
        environments = list(repo_request.openshiftServers.keys()) if repo_request.openshiftServers else None

        return await self.template_processor.get_project_files(
            project_type=repo_request.projectType,
            repo_name=repo_request.sanitized_name,
            stack=repo_request.stack,
            environments=environments
        )

    async def _create_and_initialize_repository(self, token: str, repo_request: RepoRequest, files: Dict[str, str]) -> tuple:
        """Create repository and initialize with files."""
        repo_url, project_id = await self.gitlab_service.create_repository(token, repo_request.dict())
        await self.gitlab_service.add_files(token, project_id, files, branch=repo_request.defaultBranch)
        return repo_url, project_id

    async def _setup_project_variables(self, token: str, project_id: int, repo_request: RepoRequest) -> List[str]:
        """Set up all project variables."""
        variables_created = []
        if self._should_create_cluster_variables(repo_request):
            cluster_vars = await self._create_cluster_variables(token, project_id, repo_request)
            variables_created.extend(cluster_vars)
        if repo_request.openshiftServers:
            openshift_vars = await self._create_openshift_variables(token, project_id, repo_request)
            variables_created.extend(openshift_vars)
        return variables_created

    def _should_create_cluster_variables(self, repo_request: RepoRequest) -> bool:
        """Check if cluster variables should be created."""
        return self.variable_manager.should_create_cluster_variables(
            repo_request.projectType, repo_request.clusters
        )

    async def _create_cluster_variables(self, token: str, project_id: int, repo_request: RepoRequest) -> List[str]:
        """Create and set cluster variables."""
        cluster_variables = self.variable_manager.create_cluster_variables(repo_request.clusters)
        await self.gitlab_service.set_project_variables(token, project_id, cluster_variables)
        return list(cluster_variables.keys())

    async def _create_openshift_variables(self, token: str, project_id: int, repo_request: RepoRequest) -> List[str]:
        """Create and set OpenShift variables."""
        cluster_variables = self.variable_manager.create_deployment_variables(repo_request.openshiftServers)
        await self.gitlab_service.set_project_variables(token, project_id, cluster_variables)
        env_variables = await self.variable_manager.set_environment_variables(
            self.gitlab_service, token, project_id, repo_request.openshiftServers
        )
        return list(cluster_variables.keys()) + env_variables

    def _build_success_response(self, repo_request: RepoRequest, repo_url: str, project_id: int, files: Dict[str, str], variables_created: List[str]) -> Dict:
        """Build the success response for project creation."""
        repository = self._build_repository_info(repo_request, repo_url, project_id)
        project_details = {
            "name": repo_request.name,
            "type": repo_request.projectType,
            "stack": repo_request.stack,
            "visibility": repo_request.visibility,
            "branch": repo_request.defaultBranch,
            "cluster_configs": len(repo_request.openshiftServers or {})
        }
        
        return create_project_response(
            message=f"Successfully created {repo_request.projectType} '{repo_request.name}'",
            repositories=[repository],
            variables_created=variables_created,
            project_details=project_details,
            primary_repos=[self._build_primary_repo_info(repo_request, repo_url, project_id)],
            summary=self._build_summary(repo_request, files),
            next_steps=self._get_next_steps()
        )

    def _build_repository_info(self, repo_request: RepoRequest, repo_url: str, project_id: int) -> Dict:
        """Build repository information object."""
        return {
            "type": repo_request.projectType,
            "name": repo_request.name,
            "url": repo_url,
            "id": project_id,
            "description": f"{repo_request.projectType.title()} repository with {repo_request.stack or 'default'} stack"
        }

    def _build_primary_repo_info(self, repo_request: RepoRequest, repo_url: str, project_id: int) -> Dict:
        """Build primary repository information object."""
        return {
            "title": f"📦 {repo_request.projectType.title()} Repository",
            "name": repo_request.name,
            "url": repo_url,
            "id": project_id,
            "description": f"{repo_request.projectType.title()} repository with {repo_request.stack or 'default'} stack",
            "type": repo_request.projectType,
            "action_text": "Start Working",
            "clone_command": f"git clone {repo_url}"
        }

    def _build_summary(self, repo_request: RepoRequest, files: Dict[str, str]) -> Dict:
        """Build summary information object."""
        return {
            "message": f"✅ Successfully created {repo_request.projectType} '{repo_request.name}'",
            "repos_created": 1,
            "total_files": len(files),
            "stack": repo_request.stack or "default"
        }

    def _get_next_steps(self) -> List[str]:
        """Get list of next steps for the user."""
        return [
            "Clone the repository to start working",
            "Review and customize the generated CI/CD pipeline",
            "Configure any required environment variables",
            "Start developing your application"
        ]