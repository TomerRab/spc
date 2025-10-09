"""Repository management for microservice projects."""
import logging
from typing import Dict, List, Tuple

from app.schemas.repo_models import RepoRequest
from app.utils.exceptions import ProjectCreationError

logger = logging.getLogger(__name__)


class MicroserviceRepositoryManager:
    """Handles repository creation and file management for microservices."""
    
    def __init__(self, gitlab_service, template_processor) -> None:
        self.gitlab_service = gitlab_service
        self.template_processor = template_processor

    async def create_microservice_repository(self, token: str, repo_request: RepoRequest) -> Tuple[str, int, Dict[str, str]]:
        """Create microservice repository with templates."""
        try:
            files = await self._generate_microservice_files(repo_request)
            url, repo_id = await self._create_repository(token, repo_request)
            await self._add_files_to_repository(token, repo_id, files, repo_request.defaultBranch)
            return url, repo_id, files
        except Exception as e:
            self._handle_microservice_creation_error(e, repo_request.name)

    async def _generate_microservice_files(self, repo_request: RepoRequest) -> Dict[str, str]:
        """Generate microservice template files."""
        # Use the actual project type from the request instead of hardcoding "microservice"
        project_type = repo_request.projectType if repo_request.projectType in ["microservice", "standalone-microservice"] else "microservice"
        logger.info(f"Generating {project_type} template files...")

        # Extract environment keys from openshiftServers
        environments = list(repo_request.openshiftServers.keys()) if repo_request.openshiftServers else None

        return await self.template_processor.w(
            project_type=project_type,
            repo_name=repo_request.sanitized_name,
            stack=repo_request.stack,
            environments=environments
        )

    async def _create_repository(self, token: str, repo_request: RepoRequest) -> Tuple[str, int]:
        """Create GitLab repository."""
        logger.info("Creating microservice repository...")
        return await self.gitlab_service.create_repository(token, repo_request.dict())

    async def _add_files_to_repository(self, token: str, repo_id: int, files: Dict[str, str], branch: str = None) -> None:
        """Add template files to repository."""
        logger.info("Adding files to microservice repository...")
        await self.gitlab_service.add_files(token, repo_id, files, branch)

    def _handle_microservice_creation_error(self, error: Exception, project_name: str) -> None:
        """Handle microservice repository creation errors."""
        logger.error(f"Failed to create microservice repository: {str(error)}")
        raise ProjectCreationError(
            f"Failed to create microservice repository: {str(error)}",
            project_name
        )

    async def create_delivery_repository(self, token: str, repo_request: RepoRequest) -> Tuple[str, int, Dict[str, str]]:
        """Create delivery repository with templates."""
        try:
            files = await self._generate_delivery_files(repo_request)
            delivery_repo_data = self._prepare_delivery_repo_data(repo_request)
            url, repo_id = await self._create_delivery_repository(token, delivery_repo_data)
            await self._add_files_to_repository(token, repo_id, files, repo_request.defaultBranch)
            return url, repo_id, files
        except Exception as e:
            self._handle_delivery_creation_error(e, repo_request.name)

    async def _generate_delivery_files(self, repo_request: RepoRequest) -> Dict[str, str]:
        """Generate delivery template files."""
        logger.info("Generating delivery template files...")
        # Extract environment keys from deliveryServers
        delivery_servers = repo_request.deliveryConfig.get('deliveryServers', {}) if repo_request.deliveryConfig else {}
        environments = list(delivery_servers.keys()) if delivery_servers else None

        return await self.template_processor.get_project_files(
            project_type="delivery",
            repo_name=repo_request.sanitized_name,
            stack=None,
            environments=environments
        )

    def _prepare_delivery_repo_data(self, repo_request: RepoRequest) -> Dict:
        """Prepare delivery repository data."""
        delivery_repo_data = repo_request.dict()
        delivery_repo_data["name"] = f"{repo_request.name}-delivery"
        delivery_repo_data["project_name"] = f"{repo_request.name}-delivery"

        # Use delivery group ID if specified, otherwise use default group ID
        if repo_request.deliveryConfig and repo_request.deliveryConfig.get('deliveryGroupId'):
            delivery_repo_data["groupId"] = repo_request.deliveryConfig.get('deliveryGroupId')
            delivery_repo_data["group_id"] = repo_request.deliveryConfig.get('deliveryGroupId')
            logger.info(f"Using delivery group ID: {repo_request.deliveryConfig.get('deliveryGroupId')}")

        return delivery_repo_data

    async def _create_delivery_repository(self, token: str, repo_data: Dict) -> Tuple[str, int]:
        """Create delivery GitLab repository."""
        logger.info("Creating delivery repository...")
        return await self.gitlab_service.create_repository(token, repo_data)

    def _handle_delivery_creation_error(self, error: Exception, project_name: str) -> None:
        """Handle delivery repository creation errors."""
        logger.error(f"Failed to create delivery repository: {str(error)}")
        raise ProjectCreationError(
            f"Failed to create delivery repository: {str(error)}",
            f"{project_name}-delivery"
        )