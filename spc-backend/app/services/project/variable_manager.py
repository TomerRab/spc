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
        server_mapping = self._get_server_mapping()
        for server_id, config in servers.items():
            if server_id in server_mapping:
                self._add_server_variables(variables, server_mapping, server_id, config)
        return variables

    def _get_server_mapping(self) -> Dict[str, str]:
        """Get server ID to environment prefix mapping."""
        return {
            "a": "PROD_A",
            "b": "PROD_B", 
            "c": "TEST_C",
            "d": "TEST_D"
        }

    def _add_server_variables(self, variables: Dict[str, str], server_mapping: Dict[str, str], server_id: str, config: Dict) -> None:
        """Add variables for a specific server."""
        env_prefix = server_mapping[server_id]
        variables[f"{env_prefix}_NAMESPACE"] = config.get("namespace", f"default-{server_id}")
        variables[f"{env_prefix}_SERVER"] = server_id.upper()

    async def set_environment_variables(self, gitlab_service, token: str, project_id: int, servers: Dict) -> List[str]:
        """Set environment-specific variables for each deployment environment."""
        variables_created = []
        for env_id, config in servers.items():
            env_vars = await self._process_environment_config(gitlab_service, token, project_id, env_id, config)
            variables_created.extend(env_vars)
        return variables_created

    async def _process_environment_config(self, gitlab_service, token: str, project_id: int, env_id: str, config: Dict) -> List[str]:
        """Process configuration for a single environment."""
        if env_id not in ENVIRONMENT_CONFIG:
            return []
        namespace = config.get("namespace")
        if not namespace:
            return []
        return await self._create_environment_variables(gitlab_service, token, project_id, env_id, namespace)

    async def _create_environment_variables(self, gitlab_service, token: str, project_id: int, env_id: str, namespace: str) -> List[str]:
        """Create environment variables for a specific environment."""
        env_name = ENVIRONMENT_CONFIG[env_id]["environment"]
        environment_vars = self._build_environment_vars(env_id, namespace)
        logger.info(f"Setting variables for environment {env_name}: {environment_vars}")
        await gitlab_service.set_environment_variables(token, project_id, env_name, environment_vars)
        return [f"{var_name} (env: {env_name})" for var_name in environment_vars.keys()]

    def _build_environment_vars(self, env_id: str, namespace: str) -> Dict[str, str]:
        """Build environment variables dictionary."""
        # Map environment IDs to OpenShift config attribute names
        env_mapping = {
            "a": "production_a",
            "b": "production_b",
            "c": "test_c",
            "d": "test_d"
        }

        env_name = env_mapping.get(env_id)
        if not env_name:
            logger.warning(f"Unknown environment ID: {env_id}")
            return {
                "openshift_project_name": namespace,
                "openshift_token": "",
                "openshift_server": ""
            }

        # Use correct attribute names matching config.py
        openshift_token = getattr(settings, f"openshift_{env_name}_token", "")
        openshift_server = getattr(settings, f"openshift_{env_name}_server", "")

        return {
            "openshift_project_name": namespace,
            "openshift_token": openshift_token,
            "openshift_server": openshift_server
        }