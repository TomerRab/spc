from typing import Dict
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.repo_models import RepoRequest
from app.services.gitlab import GitLabService
from app.services.template import TemplateProcessor
from .single_project_creator import SingleProjectCreator
from .microservice_creator import MicroserviceCreator
import logging

logger = logging.getLogger(__name__)


class ProjectCreator:
    """Main orchestrator for creating different types of projects."""
    
    def __init__(self):
        self.gitlab_service = GitLabService()
        self.template_processor = TemplateProcessor(
            settings.s3_bucket, settings.s3_region
        )
        self.single_creator = SingleProjectCreator(self.gitlab_service, self.template_processor)
        self.microservice_creator = MicroserviceCreator(self.gitlab_service, self.template_processor)

    async def create_project(self, token: str, repo_request: RepoRequest) -> Dict:
        """Main entry point for project creation."""
        # Validate requirements
        try:
            repo_request.validate_requirements()
        except ValueError as e:
            raise HTTPException(400, str(e))

        try:
            # Route to appropriate creator based on project type
            if repo_request.project_type == "microservice":
                return await self._handle_microservice_creation(token, repo_request)
            elif repo_request.project_type == "standalone-microservice":
                return await self.microservice_creator.create_standalone(token, repo_request)
            else:
                return await self.single_creator.create(token, repo_request)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during project creation: {str(e)}")
            return self._handle_unexpected_error(e, repo_request)

    async def _handle_microservice_creation(self, token: str, repo_request: RepoRequest) -> Dict:
        """Handle microservice creation with optional delivery repository."""
        if repo_request.deliveryConfig and repo_request.deliveryConfig.get('createDelivery'):
            # Regular microservice: creates microservice + separate delivery repo
            return await self.microservice_creator.create_with_delivery(token, repo_request)
        else:
            # Microservice without delivery repo - create as single project
            return await self.single_creator.create(token, repo_request)

    def _handle_unexpected_error(self, error: Exception, repo_request: RepoRequest):
        """Handle unexpected errors with user-friendly messages."""
        if "Template not found" in str(error):
            raise HTTPException(400, f"The selected technology stack '{repo_request.stack}' is not supported for {repo_request.project_type} projects. Please choose a different stack or contact support.")
        elif "Permission denied" in str(error) or "403" in str(error):
            raise HTTPException(403, f"You don't have permission to create repositories in the selected group. Please choose a different group or contact your GitLab administrator.")
        else:
            raise HTTPException(500, f"An unexpected error occurred while creating your project. Please try again or contact support if the problem persists. Details: {str(error)}")