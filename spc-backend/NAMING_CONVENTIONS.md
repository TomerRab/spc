# Naming Conventions

## API Contract Naming (Client-Server Communication)

### Request/Response Models
- **Use camelCase** for all fields in Pydantic models that are part of the API contract
- This matches frontend JavaScript/TypeScript naming conventions
- Example: `groupId`, `projectType`, `deliveryConfig`, `openshiftServers`

```python
# spc-backend/app/schemas/repo_models.py
class RepoRequest(BaseModel):
    name: str
    groupId: int            # camelCase for API
    projectType: str        # camelCase for API
    openshiftServers: Optional[dict] = None
```

### Why camelCase for API?
1. Frontend naturally uses camelCase (JavaScript/TypeScript convention)
2. Reduces need for field name transformation
3. Cleaner client code without constant mapping

## Internal Python Code

### Python Modules and Variables
- **Use snake_case** for all internal Python code
- Example: `gitlab_service`, `template_processor`, `repo_request`

```python
# Internal Python variables
gitlab_service = GitLabService()
template_processor = TemplateProcessor()
```

### Class Names
- **Use PascalCase** for all class names
- Example: `RepoRequest`, `ProjectCreator`, `GitLabService`

### Private Methods
- **Use _snake_case** with leading underscore for private methods
- Example: `_validate_project_name`, `_build_repository_info`

## Database/Configuration

### Environment Variables
- **Use UPPER_SNAKE_CASE** for environment variables
- Example: `GITLAB_CLIENT_ID`, `OPENSHIFT_PRODUCTION_A_TOKEN`

```python
# .env
GITLAB_CLIENT_ID=your_client_id
OPENSHIFT_PRODUCTION_A_TOKEN=token_value
```

### Config Attributes
- **Use snake_case** for config attributes
- Example: `gitlab_url`, `openshift_production_a_token`

## URL Endpoints

### REST API Routes
- **Use kebab-case** for URL paths
- Example: `/generate-repo`, `/login-url`

```python
@router.post("/generate-repo")
@router.get("/login-url")
```

## Summary

| Context | Convention | Example |
|---------|-----------|---------|
| API Request/Response Fields | camelCase | `groupId`, `projectType` |
| Python Variables | snake_case | `gitlab_service`, `project_id` |
| Python Classes | PascalCase | `RepoRequest`, `GitLabService` |
| Private Methods | _snake_case | `_validate_name` |
| Environment Variables | UPPER_SNAKE_CASE | `GITLAB_CLIENT_ID` |
| URL Endpoints | kebab-case | `/generate-repo` |

## Type Aliases

For clarity, we maintain this mapping between frontend and backend:

```typescript
// Frontend (TypeScript)
interface ProjectConfig {
  groupId: number;
  projectType: string;
  openshiftServers?: Record<string, ServerConfig>;
}
```

```python
# Backend (Python API Contract)
class RepoRequest(BaseModel):
    groupId: int
    projectType: str
    openshiftServers: Optional[dict] = None
```

This convention ensures smooth integration between frontend and backend while following language-specific best practices internally.