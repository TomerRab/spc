from typing import Dict, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class VariableManager:
    """Handles CI/CD variable creation for deployment projects."""

    # Map environment IDs to config attribute names
    ENV_MAPPING = {
        "a": "production_a",
        "b": "production_b",
        "c": "test_c",
        "d": "test_d"
    }

    async def create_openshift_variables(
        self, gitlab_service, token: str, project_id: int, servers: Dict
    ) -> List[str]:
        """Create OpenShift variables for each environment with GitLab environment scope.

        For each server (a, b, c, d), creates 3 environment-scoped variables:
        - OS_TOKEN (with scope 'a', 'b', 'c', or 'd')
        - OS_SERVER (with scope 'a', 'b', 'c', or 'd')
        - OS_PROJECT_NAME (with scope 'a', 'b', 'c', or 'd')

        Args:
            gitlab_service: GitLab service instance
            token: GitLab access token
            project_id: GitLab project ID
            servers: Dict mapping server IDs to config (e.g., {"a": {"namespace": "my-ns"}})

        Returns:
            List of created variable names with their scopes
        """
        variables_created = []

        for server_id, config in servers.items():
            # Validate server ID
            if server_id not in self.ENV_MAPPING:
                logger.warning(f"Unknown server ID '{server_id}', skipping")
                continue

            # Get namespace from config
            namespace = config.get("namespace")
            if not namespace:
                logger.warning(f"No namespace for server '{server_id}', skipping")
                continue

            # Get OpenShift credentials from settings
            env_name = self.ENV_MAPPING[server_id]
            os_token = getattr(settings, f"openshift_{env_name}_token", "")
            os_server = getattr(settings, f"openshift_{env_name}_server", "")

            # Build the 3 variables
            variables = {
                "OS_TOKEN": os_token,
                "OS_SERVER": os_server,
                "OS_PROJECT_NAME": namespace
            }

            logger.info(
                f"Creating OpenShift variables for environment '{server_id}': "
                f"OS_TOKEN, OS_SERVER, OS_PROJECT_NAME={namespace}"
            )

            # Create variables with environment scope
            await gitlab_service.set_environment_variables(
                token, project_id, server_id, variables
            )

            # Track what was created
            variables_created.extend([
                f"OS_TOKEN (scope: {server_id})",
                f"OS_SERVER (scope: {server_id})",
                f"OS_PROJECT_NAME (scope: {server_id})"
            ])

        return variables_created
