"""Microservice project creation orchestrator."""
import logging
from typing import Dict, List

from fastapi import HTTPException

from app.schemas.repo_models import RepoRequest
from app.utils.exceptions import ProjectCreationError
from .variable_manager import VariableManager
from .microservice_repository_manager import MicroserviceRepositoryManager
from .microservice_rollback_handler import MicroserviceRollbackHandler
from .microservice_response_builder import MicroserviceResponseBuilder

logger = logging.getLogger(__name__)


class MicroserviceCreator:
    """Orchestrates creation of microservice projects with optional delivery repositories."""
    
    def __init__(self, gitlab_service, template_processor) -> None:
        self.gitlab_service = gitlab_service
        self.template_processor = template_processor
        self._initialize_managers(gitlab_service, template_processor)

    def _initialize_managers(self, gitlab_service, template_processor) -> None:
        """Initialize all manager dependencies."""
        self.variable_manager = VariableManager()
        self.repository_manager = MicroserviceRepositoryManager(gitlab_service, template_processor)
        self.rollback_handler = MicroserviceRollbackHandler(gitlab_service)
        self.response_builder = MicroserviceResponseBuilder()

    async def create_with_delivery(self, token: str, repo_request: RepoRequest) -> Dict:
        """Create microservice with separate delivery repository."""
        created_repos = []
        microservice_data = None
        delivery_data = None

        try:
            microservice_data = await self._create_microservice_part(token, repo_request, created_repos)
            delivery_data = await self._create_delivery_part(token, repo_request, created_repos)

            # Variables are created after repos, so handle failure gracefully
            try:
                variables_created = await self._setup_delivery_variables(token, delivery_data[1], repo_request)
            except Exception as var_error:
                logger.warning(f"Failed to create CI/CD variables: {str(var_error)}")
                # Don't rollback repos if just variables failed - repos are usable
                # Return success with empty variables list
                variables_created = []
                logger.info("Continuing without CI/CD variables - they can be added manually")

            return self._build_success_response(microservice_data, delivery_data, variables_created, repo_request)
        except Exception as e:
            # Only rollback if repository creation failed, not variable creation
            await self._handle_creation_failure(token, created_repos, e, repo_request.name)

    async def _create_microservice_part(self, token: str, repo_request: RepoRequest, created_repos: list) -> tuple:
        """Create the microservice repository part."""
        microservice_url, microservice_id, microservice_files = (
            await self.repository_manager.create_microservice_repository(token, repo_request)
        )
        self._add_to_created_repos(created_repos, "microservice", repo_request.name, microservice_url, microservice_id)
        return microservice_url, microservice_id, microservice_files

    async def _create_delivery_part(self, token: str, repo_request: RepoRequest, created_repos: list) -> tuple:
        """Create the delivery repository part."""
        delivery_url, delivery_id, delivery_files = (
            await self.repository_manager.create_delivery_repository(token, repo_request)
        )
        delivery_name = f"{repo_request.name}-delivery"
        self._add_to_created_repos(created_repos, "delivery", delivery_name, delivery_url, delivery_id)
        return delivery_url, delivery_id, delivery_files

    def _add_to_created_repos(self, created_repos: list, repo_type: str, name: str, url: str, repo_id: int) -> None:
        """Add repository to created repos tracking list."""
        created_repos.append({
            "type": repo_type,
            "name": name,
            "url": url,
            "id": repo_id
        })

    def _build_success_response(self, microservice_data: tuple, delivery_data: tuple, variables_created: list, repo_request: RepoRequest) -> Dict:
        """Build successful creation response."""
        microservice_url, microservice_id, microservice_files = microservice_data
        delivery_url, delivery_id, delivery_files = delivery_data
        return self.response_builder.build_success_response(
            repo_request, microservice_url, microservice_id, delivery_url, 
            delivery_id, microservice_files, delivery_files, variables_created
        )

    async def _handle_creation_failure(self, token: str, created_repos: list, error: Exception, project_name: str) -> None:
        """Handle failure during creation process."""
        rollback_errors = await self.rollback_handler.rollback_repositories(token, created_repos, error)
        error_msg = self.rollback_handler.build_rollback_error_message(error, rollback_errors or [], project_name)
        raise HTTPException(status_code=500, detail=error_msg)

    async def create_standalone(self, token: str, repo_request: RepoRequest) -> Dict:
        """Create standalone microservice with deployment configurations."""
        created_repos = []
        try:
            microservice_url, microservice_id, files = await self._create_microservice_repo(token, repo_request)
            self._add_to_created_repos(created_repos, "standalone-microservice", repo_request.name, microservice_url, microservice_id)

            # Variables are created after repo, handle failure gracefully
            try:
                variables_created = await self._setup_deployment_variables(token, microservice_id, repo_request)
            except Exception as var_error:
                logger.warning(f"Failed to create CI/CD variables: {str(var_error)}")
                # Don't rollback repo if just variables failed
                variables_created = []
                logger.info("Continuing without CI/CD variables - they can be added manually")

            return self._build_standalone_response(repo_request, microservice_url, microservice_id, files, variables_created)
        except Exception as e:
            await self._handle_creation_failure(token, created_repos, e, repo_request.name)

    async def _create_microservice_repo(self, token: str, repo_request: RepoRequest) -> tuple:
        """Create microservice repository and return details."""
        return await self.repository_manager.create_microservice_repository(token, repo_request)

    def _build_standalone_response(
        self, repo_request: RepoRequest, microservice_url: str, 
        microservice_id: int, files: Dict[str, str], variables_created: List[str]
    ) -> Dict:
        """Build standalone microservice response."""
        return self.response_builder.build_standalone_response(
            repo_request, microservice_url, microservice_id, files, variables_created
        )

    async def _setup_delivery_variables(self, token: str, delivery_id: int, repo_request: RepoRequest) -> list[str]:
        """Set up CI/CD variables for delivery repository."""
        return await self._setup_openshift_variables(token, delivery_id, repo_request)

    async def _setup_deployment_variables(self, token: str, repo_id: int, repo_request: RepoRequest) -> list[str]:
        """Set up CI/CD variables for standalone microservice."""
        return await self._setup_openshift_variables(token, repo_id, repo_request)

    async def _setup_openshift_variables(self, token: str, project_id: int, repo_request: RepoRequest) -> list[str]:
        """Set up OpenShift CI/CD variables with environment scope."""
        if not repo_request.openshiftServers:
            return []

        return await self.variable_manager.create_openshift_variables(
            self.gitlab_service, token, project_id, repo_request.openshiftServers
        )