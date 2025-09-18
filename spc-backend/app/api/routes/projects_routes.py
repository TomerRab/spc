import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.repo_models import RepoRequest
from app.services.project import ProjectCreator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])
bearer_scheme = HTTPBearer()


def get_access_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    return credentials.credentials


@router.post("/generate-repo")
async def create_repository(
    repo_request: RepoRequest, 
    token: str = Depends(get_access_token)
) -> Dict:
    """Create a new GitLab repository with templated files based on project configuration."""
    logger.info(f"Creating repository: {repo_request.name} of type {repo_request.projectType}")
    
    try:
        project_creator = ProjectCreator()
        result = await project_creator.create_project(token, repo_request)
        logger.info(f"Repository created successfully: {result.get('repo_url')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_repository: {str(e)}")
        raise HTTPException(500, f"An unexpected error occurred while creating your project. Please try again or contact support. Details: {str(e)}")