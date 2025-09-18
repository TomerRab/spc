from typing import Dict, List
from app.schemas.repo_models import ClusterConfig
from app.core.config import settings, ENVIRONMENT_CONFIG
import logging

logger = logging.getLogger(__name__)


class VariableManager:
    """Handles CI/CD variable creation for different project types."""
    
    def should_create_cluster_variables(self, project_type: str, clusters: List[ClusterConfig]) -> bool:
        """Determine if cluster variables should be created."""
        return project_type in ["monorepo", "delivery"] and bool(clusters)
    
    def create_cluster_variables(self, clusters: List[ClusterConfig]) -> Dict[str, str]:
        """Create cluster-specific variables."""
        variables = {}
        for cluster in clusters:
            env_prefix = cluster.environment.upper()
            variables[f"{env_prefix}_CLUSTER_NAME"] = cluster.name
            variables[f"{env_prefix}_ENVIRONMENT"] = cluster.environment
        return variables
    
    def create_deployment_variables(self, servers: Dict) -> Dict[str, str]:
        """Create deployment variables from OpenShift servers configuration."""
        variables = {}
        server_mapping = {
            "a": "PROD_A",
            "b": "PROD_B", 
            "c": "TEST_C",
            "d": "STAGING_D"
        }
        
        for server_id, config in servers.items():
            if server_id in server_mapping:
                env_prefix = server_mapping[server_id]
                variables[f"{env_prefix}_NAMESPACE"] = config.get("namespace", f"default-{server_id}")
                variables[f"{env_prefix}_SERVER"] = server_id.upper()
        
        return variables

    async def set_environment_variables(self, gitlab_service, token: str, project_id: int, servers: Dict) -> List[str]:
        """Set environment-specific variables for each deployment environment."""
        variables_created = []
        
        for env_id, config in servers.items():
            if env_id in ENVIRONMENT_CONFIG:
                env_name = ENVIRONMENT_CONFIG[env_id]["environment"]
                namespace = config.get("namespace")
                
                if namespace:
                    # Get environment-specific configuration from settings
                    env_token = getattr(settings, f"os_env_{env_id}_token", "")
                    env_server = getattr(settings, f"os_env_{env_id}_server", "")
                    
                    environment_vars = {
                        "os_project_name": namespace,
                        "os_token": env_token,
                        "os_server": env_server
                    }
                    
                    # Set variables for this specific environment
                    logger.info(f"Setting variables for environment {env_name}: {environment_vars}")
                    await gitlab_service.set_environment_variables(
                        token, project_id, env_name, environment_vars
                    )
                    
                    # Track created variables
                    for var_name in environment_vars.keys():
                        variables_created.append(f"{var_name} (env: {env_name})")
        
        return variables_created