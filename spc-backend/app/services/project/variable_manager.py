from typing import Dict, List
from app.schemas.repo_models import ClusterConfig
from app.core.config import settings, ENVIRONMENT_CONFIG
import logging

logger = logging.getLogger(__name__)


class VariableManager:
    """Handles CI/CD variable creation for different project types."""
    
    def should_create_cluster_variables(self, project_type: str, clusters: List[ClusterConfig]) -> bool:
        """Determine if cluster variables should be created."""
        return project_type in ["standalone-microservice", "delivery"] and bool(clusters)
    
    def create_cluster_variables(self, clusters: List[ClusterConfig]) -> Dict[str, str]:
        """Create cluster-specific variables."""
        variables = {}
        for cluster in clusters:
            env_prefix = cluster.environment.upper()
            variables[f"{env_prefix}_CLUSTER_NAME"] = cluster.name
            variables[f"{env_prefix}_ENVIRONMENT"] = cluster.environment
        return variables
    
    def create_deployment_variables(self, servers: Dict) -> Dict[str, str]:
        """Create deployment variables from OpenShift servers configuration.

        Creates standard OpenShift variables for each environment:
        - OS_TOKEN_{ENV}: OpenShift authentication token for environment
        - OS_SERVER_{ENV}: OpenShift server URL for environment
        - OS_PROJECT_NAME_{ENV}: Namespace/project name for deployment
        """
        variables = {}
        env_mapping = self._get_environment_mapping()

        for server_id, config in servers.items():
            if server_id not in env_mapping:
                logger.warning(f"Unknown server ID: {server_id}, skipping variable creation")
                continue

            env_name = env_mapping[server_id]
            namespace = config.get("namespace")

            if not namespace:
                logger.warning(f"No namespace provided for server {server_id}, skipping")
                continue

            # Get OpenShift credentials from settings
            os_token = getattr(settings, f"openshift_{env_name}_token", "")
            os_server = getattr(settings, f"openshift_{env_name}_server", "")

            # Create standard OpenShift variables with environment suffix
            env_suffix = server_id.upper()
            variables[f"OS_TOKEN_{env_suffix}"] = os_token
            variables[f"OS_SERVER_{env_suffix}"] = os_server
            variables[f"OS_PROJECT_NAME_{env_suffix}"] = namespace

            logger.info(f"Created OpenShift variables for environment {server_id}: OS_TOKEN_{env_suffix}, OS_SERVER_{env_suffix}, OS_PROJECT_NAME_{env_suffix}={namespace}")

        return variables

    def _get_environment_mapping(self) -> Dict[str, str]:
        """Map environment IDs to config attribute names."""
        return {
            "a": "production_a",
            "b": "production_b",
            "c": "test_c",
            "d": "test_d"
        }

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
        """Build environment variables dictionary with standard OpenShift variable names.

        Note: env_id is already validated at schema level, so we can safely use it here.
        """
        env_mapping = self._get_environment_mapping()
        env_name = env_mapping[env_id]  # Safe to use direct access - already validated

        # Get OpenShift credentials from settings
        os_token = getattr(settings, f"openshift_{env_name}_token", "")
        os_server = getattr(settings, f"openshift_{env_name}_server", "")

        return {
            "OS_PROJECT_NAME": namespace,
            "OS_TOKEN": os_token,
            "OS_SERVER": os_server
        }