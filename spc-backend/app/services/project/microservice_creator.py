from typing import Dict
from fastapi import HTTPException
from app.schemas.repo_models import RepoRequest
from .variable_manager import VariableManager
import logging

logger = logging.getLogger(__name__)


class MicroserviceCreator:
    """Handles creation of microservice projects with optional delivery repositories."""
    
    def __init__(self, gitlab_service, template_processor):
        self.gitlab_service = gitlab_service
        self.template_processor = template_processor
        self.variable_manager = VariableManager()

    async def create_with_delivery(self, token: str, repo_request: RepoRequest) -> Dict:
        """Create microservice with separate delivery repository."""
        created_repos = []
        microservice_id = None
        delivery_id = None
        
        try:
            # Step 1: Generate template files first (fail fast if templates are missing)
            logger.info("Generating microservice template files...")
            microservice_files = await self.template_processor.get_project_files(
                project_type="microservice",
                repo_name=repo_request.sanitized_name,
                stack=repo_request.stack,
            )
            
            logger.info("Generating delivery template files...")
            delivery_files = await self.template_processor.get_project_files(
                project_type="delivery",
                repo_name=repo_request.sanitized_name,
                stack=None,
            )

            # Step 2: Create microservice repository
            logger.info("Creating microservice repository...")
            microservice_url, microservice_id = await self.gitlab_service.create_repository(
                token, repo_request.dict()
            )
            
            logger.info("Adding files to microservice repository...")
            await self.gitlab_service.add_files(token, microservice_id, microservice_files)
            
            created_repos.append({
                "type": "microservice",
                "name": repo_request.name,
                "url": microservice_url,
                "id": microservice_id
            })

            # Step 3: Create delivery repository
            logger.info("Creating delivery repository...")
            delivery_repo_data = repo_request.dict()
            delivery_repo_data["name"] = f"{repo_request.name}-delivery"
            delivery_repo_data["project_name"] = f"{repo_request.name}-delivery"
            
            delivery_url, delivery_id = await self.gitlab_service.create_repository(
                token, delivery_repo_data
            )
            
            logger.info("Adding files to delivery repository...")
            await self.gitlab_service.add_files(token, delivery_id, delivery_files)

            # Set cluster variables for delivery repo
            variables_created = []
            if repo_request.openshiftServers:
                # Set old-style cluster variables for backward compatibility
                cluster_variables = self.variable_manager.create_deployment_variables(
                    repo_request.openshiftServers
                )
                await self.gitlab_service.set_project_variables(
                    token, delivery_id, cluster_variables
                )
                
                # Set new environment-specific variables
                env_variables = await self.variable_manager.set_environment_variables(
                    self.gitlab_service, token, delivery_id, repo_request.openshiftServers
                )
                
                variables_created = list(cluster_variables.keys()) + env_variables

            created_repos.append({
                "type": "delivery",
                "name": f"{repo_request.name}-delivery",
                "url": delivery_url,
                "id": delivery_id
            })

            return self._build_microservice_response(
                repo_request, microservice_url, microservice_id, delivery_url, 
                delivery_id, microservice_files, delivery_files, variables_created
            )

        except Exception as e:
            # Rollback: Delete any repositories that were created before the failure
            await self._rollback_repositories(token, microservice_id, delivery_id)
            raise self._handle_creation_error(e, repo_request)

    async def create_standalone(self, token: str, repo_request: RepoRequest) -> Dict:
        """Create standalone microservice - 1 repository with microservice code AND delivery/Helm charts included."""
        try:
            # Generate microservice files
            logger.info("Generating microservice template files...")
            microservice_files = await self.template_processor.get_project_files(
                project_type="microservice",
                repo_name=repo_request.sanitized_name,
                stack=repo_request.stack,
            )
            
            # Generate delivery files (Helm charts, etc.)
            logger.info("Generating delivery template files...")
            delivery_files = await self.template_processor.get_project_files(
                project_type="delivery",
                repo_name=repo_request.sanitized_name,
                stack=None,
            )
            
            # Merge both sets of files into one repository
            all_files = {**microservice_files}
            
            # Add delivery files with proper paths
            for file_path, content in delivery_files.items():
                # Skip duplicate files (like README.md, .gitignore)
                if file_path in ["README.md", ".gitignore"]:
                    continue
                # Add delivery files under deployment/ directory
                all_files[f"deployment/{file_path}"] = content
            
            # Create single repository
            logger.info("Creating standalone microservice repository...")
            repo_url, project_id = await self.gitlab_service.create_repository(
                token, repo_request.dict()
            )
            
            logger.info("Adding all files to repository...")
            await self.gitlab_service.add_files(token, project_id, all_files)
            
            # Set cluster variables if needed
            variables_created = []
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
                
                variables_created = list(cluster_variables.keys()) + env_variables
            
            return self._build_standalone_response(repo_request, repo_url, project_id, all_files, variables_created)

        except Exception as e:
            raise self._handle_creation_error(e, repo_request)

    def _build_microservice_response(self, repo_request, microservice_url, microservice_id, 
                                   delivery_url, delivery_id, microservice_files, delivery_files, variables_created):
        """Build response for microservice with delivery repository."""
        return {
            "status": "success",
            "project_type": "standalone-microservice",
            "repositories": [
                {
                    "type": "microservice",
                    "name": repo_request.name,
                    "url": microservice_url,
                    "id": microservice_id
                },
                {
                    "type": "delivery",
                    "name": f"{repo_request.name}-delivery",
                    "url": delivery_url,
                    "id": delivery_id
                }
            ],
            "primary_repos": [
                {
                    "title": "🚀 Microservice Repository",
                    "name": repo_request.name,
                    "url": microservice_url,
                    "id": microservice_id,
                    "description": "Main application repository containing your microservice code",
                    "type": "microservice",
                    "action_text": "Start Coding",
                    "clone_command": f"git clone {microservice_url}"
                },
                {
                    "title": "⚙️ Delivery Repository", 
                    "name": f"{repo_request.name}-delivery",
                    "url": delivery_url,
                    "id": delivery_id,
                    "description": "GitOps delivery repository with Helm charts for deployments",
                    "type": "delivery",
                    "action_text": "Configure Deployment",
                    "clone_command": f"git clone {delivery_url}"
                }
            ],
            "files_created": {
                "microservice": list(microservice_files.keys()),
                "delivery": list(delivery_files.keys())
            },
            "variables_created": variables_created,
            "summary": {
                "message": f"✅ Successfully created {repo_request.project_type} project with delivery repository",
                "repos_created": 2,
                "total_files": len(microservice_files) + len(delivery_files),
                "environments": ["dev", "staging", "prod"]
            },
            "next_steps": [
                "Clone the microservice repository to start developing",
                "Configure environment variables in the delivery repository", 
                "Update Helm values for your specific deployment needs",
                "Push your first commit to trigger the CI/CD pipeline"
            ]
        }

    def _build_standalone_response(self, repo_request, repo_url, project_id, all_files, variables_created):
        """Build response for standalone microservice."""
        return {
            "status": "success",
            "project_type": repo_request.project_type,
            "repositories": [{
                "type": repo_request.project_type,
                "name": repo_request.name,
                "url": repo_url,
                "id": project_id,
                "description": "Standalone microservice with integrated delivery/deployment configuration"
            }],
            "primary_repos": [
                {
                    "title": "🚀 Standalone Microservice",
                    "name": repo_request.name,
                    "url": repo_url,
                    "id": project_id,
                    "description": "All-in-one repository with microservice code and deployment configuration",
                    "type": repo_request.project_type,
                    "action_text": "Start Coding & Deploy",
                    "clone_command": f"git clone {repo_url}"
                }
            ],
            "repo_url": repo_url,
            "project_id": project_id,
            "files_created": list(all_files.keys()),
            "variables_created": variables_created,
            "summary": {
                "message": f"✅ Successfully created standalone microservice with integrated deployment",
                "repos_created": 1,
                "total_files": len(all_files),
                "includes": ["microservice code", "Helm charts", "CI/CD pipeline", "multi-environment configs"]
            },
            "next_steps": [
                "Clone the repository to start developing",
                "Review the deployment/ directory for Helm charts and configurations",
                "Customize environment-specific values in deployment/environments/",
                "Push your first commit to trigger the CI/CD pipeline"
            ]
        }

    async def _rollback_repositories(self, token: str, microservice_id: int = None, delivery_id: int = None):
        """Rollback created repositories on failure."""
        if microservice_id:
            try:
                logger.info(f"Rolling back: Deleting microservice repository {microservice_id}")
                await self.gitlab_service.delete_repository(token, microservice_id)
            except Exception as rollback_error:
                logger.error(f"Failed to rollback microservice repository {microservice_id}: {str(rollback_error)}")
        
        if delivery_id:
            try:
                logger.info(f"Rolling back: Deleting delivery repository {delivery_id}")
                await self.gitlab_service.delete_repository(token, delivery_id)
            except Exception as rollback_error:
                logger.error(f"Failed to rollback delivery repository {delivery_id}: {str(rollback_error)}")

    def _handle_creation_error(self, error: Exception, repo_request: RepoRequest):
        """Handle and format creation errors."""
        logger.error(f"Microservice creation failed: {str(error)}")
        
        if "Template not found" in str(error):
            return HTTPException(400, f"The selected technology stack '{repo_request.stack}' is not supported for {repo_request.project_type} projects. Please choose a different stack or contact support.")
        elif "Permission denied" in str(error) or "403" in str(error):
            return HTTPException(403, f"You don't have permission to create repositories in the selected group. Please choose a different group or contact your GitLab administrator.")
        elif "already been taken" in str(error) or "already exists" in str(error):
            return HTTPException(400, f"A project with this name already exists in the selected group. Please choose a different project name.")
        else:
            return HTTPException(500, f"Failed to create {repo_request.project_type} project. Please try again or contact support if the issue persists. Details: {str(error)}")