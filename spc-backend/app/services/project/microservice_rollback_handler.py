"""Rollback handling for failed microservice creation."""
import logging
from typing import List, Dict, Optional

from app.utils.exceptions import ProjectCreationError

logger = logging.getLogger(__name__)


class MicroserviceRollbackHandler:
    """Handles cleanup when microservice creation fails."""
    
    def __init__(self, gitlab_service):
        self.gitlab_service = gitlab_service

    async def rollback_repositories(self, token: str, created_repos: List[Dict], original_error: Exception) -> List[str]:
        """Clean up repositories created before failure."""
        if not created_repos:
            logger.warning("No repositories to rollback")
            return []
        logger.warning(f"Rolling back {len(created_repos)} repositories due to error: {str(original_error)}")
        rollback_errors = await self._delete_all_repositories(token, created_repos)
        self._log_rollback_completion(rollback_errors)
        return rollback_errors

    async def _delete_all_repositories(self, token: str, created_repos: List[Dict]) -> List[str]:
        """Delete all repositories in the list."""
        rollback_errors = []
        for repo in created_repos:
            error = await self._delete_single_repository(token, repo)
            if error:
                rollback_errors.append(error)
        return rollback_errors

    async def _delete_single_repository(self, token: str, repo: Dict) -> str:
        """Delete a single repository and return error message if failed."""
        try:
            repo_id = repo.get("id")
            repo_name = repo.get("name", "unknown")
            if repo_id:
                logger.info(f"Deleting repository: {repo_name} (ID: {repo_id})")
                await self.gitlab_service.delete_repository(token, repo_id)
                logger.info(f"Successfully deleted repository: {repo_name}")
            return None
        except Exception as cleanup_error:
            error_msg = f"Failed to delete repository {repo_name}: {str(cleanup_error)}"
            logger.error(error_msg)
            return error_msg

    def _log_rollback_completion(self, rollback_errors: List[str]) -> None:
        """Log the completion status of rollback operation."""
        if rollback_errors:
            logger.error(f"Rollback completed with {len(rollback_errors)} errors")
        else:
            logger.info("Rollback completed successfully")

    def build_rollback_error_message(self, original_error: Exception, rollback_errors: List[str], project_name: str) -> str:
        """Build comprehensive error message including rollback status."""
        base_msg = f"Failed to create microservice project '{project_name}': {str(original_error)}"
        return base_msg + self._get_rollback_status_message(rollback_errors)

    def _get_rollback_status_message(self, rollback_errors: List[str]) -> str:
        """Get rollback status message based on errors."""
        if rollback_errors:
            return f" Additionally, {len(rollback_errors)} cleanup operations failed. Manual cleanup may be required."
        else:
            return " All created resources were successfully cleaned up."