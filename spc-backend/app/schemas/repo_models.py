from typing import Optional, List
from pydantic import BaseModel, field_validator
from enum import Enum

from app.utils.input_sanitizer import InputSanitizer


class Stack(str, Enum):
    MAVEN = "maven"
    NODE = "node"
    PYTHON = "python"
    DOTNET = "dotnet"


class ClusterConfig(BaseModel):
    name: str
    environment: str


class RepoRequest(BaseModel):
    name: str  # Frontend sends 'name' 
    groupId: int  # Frontend sends 'groupId' as number
    projectType: str  # Frontend sends 'projectType'
    stack: Optional[str] = None  # Frontend sends stack as string
    visibility: Optional[str] = "private"
    defaultBranch: Optional[str] = "main"
    openshiftServers: Optional[dict] = None
    deliveryConfig: Optional[dict] = None
    clusters: Optional[List[ClusterConfig]] = None

    @field_validator('stack', mode='before')
    @classmethod
    def validate_stack(cls, v):
        # Convert empty string to None so validation works properly
        if isinstance(v, str) and v.strip() == "":
            return None
        return InputSanitizer.sanitize_stack(v)
    
    @field_validator('name', mode='before')
    @classmethod
    def validate_name(cls, v):
        # Sanitize and validate name
        if not v:
            return None
        return InputSanitizer.sanitize_project_name(v)
    
    @field_validator('visibility', mode='before')
    @classmethod
    def validate_visibility(cls, v):
        # Sanitize visibility
        if not v:
            return "private"
        return InputSanitizer.sanitize_visibility(v)
    
    @field_validator('openshiftServers', mode='before')
    @classmethod
    def validate_openshift_servers(cls, v):
        # Sanitize server configuration
        return InputSanitizer.sanitize_server_config(v)
    
    @field_validator('deliveryConfig', mode='before')
    @classmethod
    def validate_delivery_config(cls, v):
        # Sanitize delivery configuration
        return InputSanitizer.sanitize_delivery_config(v)


    @property
    def sanitized_name(self) -> str:
        """Get sanitized version for templates and file names"""
        sanitized = self.name.lower().replace(" ", "-")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "-_")
        return "-".join(filter(None, sanitized.split("-")))

    def validate_requirements(self):
        """Validate all project requirements."""
        self._validate_basic_project_info()
        self._validate_project_type()
        self._validate_stack_requirements()
        self._validate_deployment_configuration()
        self._validate_delivery_configuration()

    def _validate_basic_project_info(self):
        """Validate basic project information."""
        self._validate_project_name()
        self._validate_group_selection()

    def _validate_project_name(self):
        """Validate project name requirements."""
        if not self.name or (isinstance(self.name, str) and self.name.strip() == ""):
            raise ValueError("Project name is required. Please enter a valid project name.")
        if len(self.name.strip()) < 2:
            raise ValueError("Project name must be at least 2 characters long.")
        self._validate_name_characters()
        self._validate_name_length()

    def _validate_name_characters(self):
        """Validate project name contains only allowed characters."""
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', self.name.strip()):
            raise ValueError("Project name contains invalid characters. Please use only letters, numbers, spaces, hyphens, underscores, and periods.")

    def _validate_name_length(self):
        """Validate project name length."""
        if len(self.name.strip()) > 100:
            raise ValueError("Project name is too long. Please use a name with 100 characters or fewer.")

    def _validate_group_selection(self):
        """Validate GitLab group selection."""
        if not self.groupId or self.groupId <= 0:
            raise ValueError("Please select a GitLab group where your project will be created.")

    def _validate_project_type(self):
        """Validate project type selection."""
        if not self.projectType or (isinstance(self.projectType, str) and self.projectType.strip() == ""):
            raise ValueError("Please select a project type (library, microservice, monorepo, etc.).")
        valid_project_types = ["library", "microservice", "standalone-microservice", "monorepo", "delivery"]
        if self.projectType not in valid_project_types:
            raise ValueError(f"Invalid project type '{self.projectType}'. Please select from: {', '.join(valid_project_types)}.")

    def _validate_stack_requirements(self):
        """Validate technology stack requirements."""
        if self.projectType in ["library", "microservice", "standalone-microservice"]:
            self._validate_stack_presence()
            self._validate_stack_validity()

    def _validate_stack_presence(self):
        """Validate that stack is provided when required."""
        if not self.stack:
            project_display = "standalone microservice" if self.projectType == "standalone-microservice" else self.projectType
            raise ValueError(f"Technology stack is required for {project_display} projects. Please select a technology stack (e.g., Maven, Spring, Node.js, React, Python, .NET) from the dropdown.")

    def _validate_stack_validity(self):
        """Validate that the selected stack is valid."""
        valid_stacks = ["maven", "spring", "node", "react", "python", "dotnet", "csharp"]
        if self.stack.strip().lower() not in valid_stacks:
            raise ValueError(f"Invalid technology stack '{self.stack}'. Please select from: Maven, Spring, Node.js, React, Python, .NET, C#.")

    def _validate_deployment_configuration(self):
        """Validate deployment configuration for projects that require it."""
        if self.projectType in ["monorepo", "delivery"]:
            self._validate_deployment_servers_presence()
            self._validate_deployment_server_configs()

    def _validate_deployment_servers_presence(self):
        """Validate that deployment servers are configured."""
        if not self.openshiftServers or (isinstance(self.openshiftServers, dict) and len(self.openshiftServers) == 0):
            raise ValueError(f"Deployment configuration is required for {self.projectType} projects. Please select at least one deployment server and provide a namespace.")

    def _validate_deployment_server_configs(self):
        """Validate individual deployment server configurations."""
        valid_server_keys = ["a", "b", "c", "d"]
        for server_key, server_config in self.openshiftServers.items():
            self._validate_single_deployment_server(server_key, server_config, valid_server_keys)

    def _validate_single_deployment_server(self, server_key, server_config, valid_server_keys):
        """Validate a single deployment server configuration."""
        if server_key not in valid_server_keys:
            raise ValueError(f"Invalid deployment server '{server_key}'. Please select from the available deployment servers.")
        if not server_config or not server_config.get('namespace') or server_config.get('namespace', '').strip() == '':
            server_name = {"a": "Production A", "b": "Production B", "c": "Test C", "d": "Test D"}.get(server_key, server_key)
            raise ValueError(f"Namespace is required for deployment server '{server_name}'. Please provide a valid namespace for all selected servers.")

    def _validate_delivery_configuration(self):
        """Validate delivery configuration for microservices."""
        if self.projectType == "microservice" and self.deliveryConfig:
            if self.deliveryConfig.get('createDelivery') == True:
                self._validate_delivery_group()
                self._validate_delivery_servers()

    def _validate_delivery_group(self):
        """Validate delivery group selection."""
        if not self.deliveryConfig.get('deliveryGroupId') or self.deliveryConfig.get('deliveryGroupId') <= 0:
            raise ValueError("Delivery group is required when creating a delivery repository. Please select a group for the delivery repository.")

    def _validate_delivery_servers(self):
        """Validate delivery servers configuration."""
        delivery_servers = self.deliveryConfig.get('deliveryServers', {})
        if delivery_servers:
            valid_server_keys = ["a", "b", "c", "d"]
            for server_key, server_config in delivery_servers.items():
                self._validate_single_delivery_server(server_key, server_config, valid_server_keys)

    def _validate_single_delivery_server(self, server_key, server_config, valid_server_keys):
        """Validate a single delivery server configuration."""
        if server_key not in valid_server_keys:
            raise ValueError(f"Invalid delivery server '{server_key}'. Please select from the available deployment servers.")
        if not server_config or not server_config.get('namespace') or server_config.get('namespace', '').strip() == '':
            server_name = {"a": "Production A", "b": "Production B", "c": "Test C", "d": "Test D"}.get(server_key, server_key)
            raise ValueError(f"Namespace is required for delivery server '{server_name}'. Please provide a valid namespace for all selected delivery servers.")
