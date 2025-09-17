from typing import Optional, List
from pydantic import BaseModel, validator
from enum import Enum


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

    @validator('stack', pre=True)
    def validate_stack(cls, v):
        # Convert empty string to None so validation works properly
        if isinstance(v, str) and v.strip() == "":
            return None
        return v
    
    @validator('name', pre=True)
    def validate_name(cls, v):
        # Ensure name is not just whitespace
        if isinstance(v, str):
            return v.strip() if v.strip() else None
        return v

    @property
    def project_name(self) -> str:
        """Backward compatibility - maps to name"""
        return self.name
    
    @property 
    def group_id(self) -> str:
        """Backward compatibility - maps to groupId"""
        return str(self.groupId)

    @property
    def project_type(self) -> str:
        """Backward compatibility - maps to projectType"""
        return self.projectType

    @property
    def sanitized_name(self) -> str:
        """Get sanitized version for templates and file names"""
        sanitized = self.project_name.lower().replace(" ", "-")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c in "-_")
        return "-".join(filter(None, sanitized.split("-")))

    def validate_requirements(self):
        # Basic project validation
        if not self.name or (isinstance(self.name, str) and self.name.strip() == ""):
            raise ValueError("Project name is required. Please enter a valid project name.")
        
        if len(self.name.strip()) < 2:
            raise ValueError("Project name must be at least 2 characters long.")
        
        # Check for invalid characters in project name
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', self.name.strip()):
            raise ValueError("Project name contains invalid characters. Please use only letters, numbers, spaces, hyphens, underscores, and periods.")
        
        # Check if name is too long (GitLab has limits)
        if len(self.name.strip()) > 100:
            raise ValueError("Project name is too long. Please use a name with 100 characters or fewer.")
        
        if not self.groupId or self.groupId <= 0:
            raise ValueError("Please select a GitLab group where your project will be created.")
        
        if not self.project_type or (isinstance(self.project_type, str) and self.project_type.strip() == ""):
            raise ValueError("Please select a project type (library, microservice, monorepo, etc.).")
        
        # Check for valid project type
        valid_project_types = ["library", "microservice", "standalone-microservice", "monorepo", "delivery"]
        if self.project_type not in valid_project_types:
            raise ValueError(f"Invalid project type '{self.project_type}'. Please select from: {', '.join(valid_project_types)}.")
        
        # Check for missing or empty stack for projects that require it
        if self.project_type in ["library", "microservice", "standalone-microservice"]:
            if not self.stack:
                project_display = "standalone microservice" if self.project_type == "standalone-microservice" else self.project_type
                raise ValueError(f"Technology stack is required for {project_display} projects. Please select a technology stack (e.g., Maven, Spring, Node.js, React, Python, .NET) from the dropdown.")
            
            # Check for valid technology stack (after we know stack exists)
            valid_stacks = ["maven", "spring", "node", "react", "typescript", "javascript", "vue", "python", "dotnet", "csharp"]
            if self.stack.strip().lower() not in valid_stacks:
                raise ValueError(f"Invalid technology stack '{self.stack}'. Please select from: Maven, Spring, Node.js, React, TypeScript, JavaScript, Vue, Python, .NET, C#.")
        
        # Check for missing deployment configuration
        if self.project_type in ["monorepo", "delivery"]:
            if not self.openshiftServers or (isinstance(self.openshiftServers, dict) and len(self.openshiftServers) == 0):
                raise ValueError(f"Deployment configuration is required for {self.project_type} projects. Please select at least one deployment server and provide a namespace.")
            
            # Check if any selected servers have empty namespaces
            valid_server_keys = ["a", "b", "c", "d"]
            for server_key, server_config in self.openshiftServers.items():
                if server_key not in valid_server_keys:
                    raise ValueError(f"Invalid deployment server '{server_key}'. Please select from the available deployment servers.")
                if not server_config or not server_config.get('namespace') or server_config.get('namespace', '').strip() == '':
                    server_name = {"a": "Production A", "b": "Production B", "c": "Test C", "d": "Staging D"}.get(server_key, server_key)
                    raise ValueError(f"Namespace is required for deployment server '{server_name}'. Please provide a valid namespace for all selected servers.")
        
        # Check for microservice with delivery configuration
        if self.project_type == "microservice" and self.deliveryConfig:
            if self.deliveryConfig.get('createDelivery') == True:
                if not self.deliveryConfig.get('deliveryGroupId') or self.deliveryConfig.get('deliveryGroupId') <= 0:
                    raise ValueError("Delivery group is required when creating a delivery repository. Please select a group for the delivery repository.")
                
                delivery_servers = self.deliveryConfig.get('deliveryServers', {})
                if delivery_servers:
                    valid_server_keys = ["a", "b", "c", "d"]
                    for server_key, server_config in delivery_servers.items():
                        if server_key not in valid_server_keys:
                            raise ValueError(f"Invalid delivery server '{server_key}'. Please select from the available deployment servers.")
                        if not server_config or not server_config.get('namespace') or server_config.get('namespace', '').strip() == '':
                            server_name = {"a": "Production A", "b": "Production B", "c": "Test C", "d": "Staging D"}.get(server_key, server_key)
                            raise ValueError(f"Namespace is required for delivery server '{server_name}'. Please provide a valid namespace for all selected delivery servers.")
