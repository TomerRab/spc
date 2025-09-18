from typing import Dict, List
from fastapi import HTTPException
from app.schemas.repo_models import RepoRequest
from .variable_manager import VariableManager
import logging

logger = logging.getLogger(__name__)


class SingleProjectCreator:
    """Handles creation of single repository projects (library, monorepo, delivery)."""
    
    def __init__(self, gitlab_service, template_processor):
        self.gitlab_service = gitlab_service
        self.template_processor = template_processor
        self.variable_manager = VariableManager()

    async def create(self, token: str, repo_request: RepoRequest) -> Dict:
        """Create a single repository project."""
        try:
            # Generate template files
            files = await self.template_processor.get_project_files(
                project_type=repo_request.project_type,
                repo_name=repo_request.sanitized_name,
                stack=repo_request.stack,
            )

            # Create repository
            repo_url, project_id = await self.gitlab_service.create_repository(
                token, repo_request.dict()
            )

            # Initialize with files
            await self.gitlab_service.add_files(token, project_id, files)

            # Set cluster variables if needed
            variables_created = []
            if self.variable_manager.should_create_cluster_variables(
                repo_request.project_type, repo_request.clusters
            ):
                cluster_variables = self.variable_manager.create_cluster_variables(
                    repo_request.clusters
                )
                await self.gitlab_service.set_project_variables(
                    token, project_id, cluster_variables
                )
                variables_created = list(cluster_variables.keys())
            
            # Set environment-specific variables if openshift servers are configured
            if repo_request.openshiftServers:
                # Set old-style cluster variables for backward compatibility
                cluster_variables = self.variable_manager.create_deployment_variables(
                    repo_request.openshiftServers
                )
                await self.gitlab_service.set_project_variables(
                    token, project_id, cluster_variables
                )
                
                # Set new environment-specific variables
                env_variables = await self.variable_manager.set_environment_variables(
                    self.gitlab_service, token, project_id, repo_request.openshiftServers
                )
                
                variables_created.extend(list(cluster_variables.keys()) + env_variables)

            return {
                "status": "success",
                "project_type": repo_request.project_type,
                "repositories": [{
                    "type": repo_request.project_type,
                    "name": repo_request.name,
                    "url": repo_url,
                    "id": project_id,
                    "description": f"{repo_request.project_type.title()} repository with {repo_request.stack or 'default'} stack"
                }],
                "primary_repos": [
                    {
                        "title": f"📦 {repo_request.project_type.title()} Repository",
                        "name": repo_request.name,
                        "url": repo_url,
                        "id": project_id,
                        "description": f"{repo_request.project_type.title()} repository with {repo_request.stack or 'default'} stack",
                        "type": repo_request.project_type,
                        "action_text": "Start Working",
                        "clone_command": f"git clone {repo_url}"
                    }
                ],
                "repo_url": repo_url,  # Backward compatibility
                "project_id": project_id,  # Backward compatibility
                "files_created": list(files.keys()),
                "variables_created": variables_created,
                "summary": {
                    "message": f"✅ Successfully created {repo_request.project_type} '{repo_request.name}'",
                    "repos_created": 1,
                    "total_files": len(files),
                    "stack": repo_request.stack or "default"
                },
                "next_steps": [
                    "Clone the repository to start working",
                    "Review and customize the generated CI/CD pipeline",
                    "Configure any required environment variables",
                    "Start developing your application"
                ]
            }
        except Exception as e:
            logger.error(f"Single project creation failed: {str(e)}")
            raise HTTPException(500, f"Failed to create {repo_request.project_type}. Details: {str(e)}")