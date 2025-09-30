"""Response building for microservice creation results."""
import logging
from typing import Dict, List

from app.schemas.repo_models import RepoRequest
from app.schemas.response_models import create_project_response

logger = logging.getLogger(__name__)


class MicroserviceResponseBuilder:
    """Builds standardized responses for microservice operations."""
    
    @staticmethod
    def build_success_response(
        repo_request: RepoRequest, microservice_url: str, microservice_id: int,
        delivery_url: str, delivery_id: int, microservice_files: Dict[str, str],
        delivery_files: Dict[str, str], variables_created: List[str]
    ) -> Dict:
        """Build successful microservice creation response."""
        repositories = MicroserviceResponseBuilder._build_repositories_list(
            repo_request, microservice_url, microservice_id, delivery_url, delivery_id,
            microservice_files, delivery_files
        )
        project_details = MicroserviceResponseBuilder._build_project_details(repo_request)
        
        return create_project_response(
            message=f"Successfully created microservice project '{repo_request.name}' with delivery repository",
            repositories=repositories,
            variables_created=variables_created,
            project_details=project_details
        )

    @staticmethod
    def _build_repositories_list(
        repo_request: RepoRequest, microservice_url: str, microservice_id: int,
        delivery_url: str, delivery_id: int, microservice_files: Dict[str, str], delivery_files: Dict[str, str]
    ) -> List[Dict]:
        """Build repositories list for response."""
        return [
            MicroserviceResponseBuilder._build_microservice_repo_info(repo_request, microservice_url, microservice_id, microservice_files),
            MicroserviceResponseBuilder._build_delivery_repo_info(repo_request, delivery_url, delivery_id, delivery_files)
        ]

    @staticmethod
    def _build_microservice_repo_info(repo_request: RepoRequest, url: str, repo_id: int, files: Dict[str, str]) -> Dict:
        """Build microservice repository info."""
        return {
            "type": "microservice",
            "name": repo_request.name,
            "url": url,
            "id": repo_id,
            "files_created": len(files)
        }

    @staticmethod
    def _build_delivery_repo_info(repo_request: RepoRequest, url: str, repo_id: int, files: Dict[str, str]) -> Dict:
        """Build delivery repository info."""
        return {
            "type": "delivery", 
            "name": f"{repo_request.name}-delivery",
            "url": url,
            "id": repo_id,
            "files_created": len(files)
        }

    @staticmethod
    def _build_project_details(repo_request: RepoRequest) -> Dict:
        """Build project details for response."""
        return {
            "name": repo_request.name,
            "type": repo_request.projectType,
            "stack": repo_request.stack,
            "visibility": repo_request.visibility,
            "branch": repo_request.defaultBranch,
            "cluster_configs": len(repo_request.openshiftServers or {})
        }

    @staticmethod  
    def build_standalone_response(
        repo_request: RepoRequest, repo_url: str, repo_id: int,
        files: Dict[str, str], variables_created: List[str]
    ) -> Dict:
        """Build standalone microservice creation response."""
        repository = MicroserviceResponseBuilder._build_standalone_repo_info(repo_request, repo_url, repo_id, files)
        project_details = MicroserviceResponseBuilder._build_project_details(repo_request)
        
        return create_project_response(
            message=f"Successfully created standalone microservice '{repo_request.name}'",
            repositories=[repository],
            variables_created=variables_created,
            project_details=project_details
        )

    @staticmethod
    def _build_standalone_repo_info(repo_request: RepoRequest, repo_url: str, repo_id: int, files: Dict[str, str]) -> Dict:
        """Build standalone repository info."""
        return {
            "type": "standalone-microservice",
            "name": repo_request.name,
            "url": repo_url,
            "id": repo_id,
            "files_created": len(files)
        }