# SPC Backend - API Service

FastAPI-based REST API service that orchestrates GitLab repository creation with pre-configured templates, CI/CD pipelines, and deployment configurations.

## Tech Stack

- **Framework**: FastAPI (latest) - High-performance async web framework
- **Server**: Uvicorn - ASGI server with hot reload support
- **Template Engine**: Jinja2 - Template processing with custom delimiters
- **Storage**: Boto3 - S3-compatible object storage client
- **Validation**: Pydantic Settings - Environment and data validation
- **HTTP Client**: httpx - Async HTTP client for GitLab API
- **Configuration**: python-dotenv - Environment variable management

## Features

### GitLab Integration
- **OAuth 2.0 Authentication**: Secure token-based authentication flow
- **Repository Management**: Create, configure, and manage GitLab repositories
- **Group Operations**: List and search user's GitLab groups
- **CI/CD Variables**: Automatic cluster configuration for deployments
- **File Operations**: Batch file commits to repositories
- **Transaction Safety**: Automatic rollback on failed repository creation

### Template System
- **S3-Based Storage**: Templates stored in S3-compatible object storage
- **Jinja2 Processing**: Dynamic template rendering with custom delimiters
- **Multi-Stack Support**: Templates for Spring, Maven, Node.js, Python, .NET, React
- **Stack Configuration**: Automatic configuration file selection (Dockerfile, .gitignore, etc.)
- **Helm Compatibility**: Custom Jinja2 delimiters avoid conflicts with Helm syntax

### Project Types
- **Library**: Basic library projects with CI/CD
- **Microservice**: Full microservice with optional separate delivery repo
- **Standalone Microservice**: Single repo with app + deployment configs
- **Monorepo**: Multi-service repositories with shared Helm charts
- **Delivery**: Standalone deployment configuration repositories

### Error Handling
- **Comprehensive Exception Handling**: Custom exception hierarchy
- **Automatic Rollback**: Cleanup on failed operations
- **Validation**: Input sanitization and validation
- **Structured Logging**: Detailed logging at all levels
- **User-Friendly Errors**: Clear error messages for API consumers

## Project Structure

```
spc-backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py        # OAuth authentication endpoints
│   │   │   ├── groups_routes.py      # GitLab groups endpoints
│   │   │   └── projects_routes.py    # Project creation endpoints
│   │   ├── routes.py                 # Main router aggregation
│   │   └── error_handlers.py         # Global exception handlers
│   ├── core/
│   │   ├── config.py                 # Pydantic settings configuration
│   │   ├── config_validator.py       # Configuration validation
│   │   ├── logger.py                 # Logging configuration
│   │   └── cache.py                  # Caching utilities
│   ├── schemas/
│   │   ├── repo_models.py            # Repository request/response models
│   │   └── response_models.py        # API response models
│   ├── services/
│   │   ├── gitlab/
│   │   │   ├── gitlab_service.py            # Main GitLab API client
│   │   │   ├── gitlab_groups_service.py     # Groups operations
│   │   │   ├── gitlab_repository_service.py # Repository operations
│   │   │   └── gitlab_variables_service.py  # CI/CD variables
│   │   ├── template/
│   │   │   ├── template_processor.py        # S3 + Jinja2 orchestration
│   │   │   ├── template_renderer.py         # Jinja2 rendering
│   │   │   └── stack_config_manager.py      # Stack-specific configs
│   │   └── project/
│   │       ├── project_creator.py                  # Main project creation
│   │       ├── microservice_creator.py             # Microservice logic
│   │       ├── microservice_repository_manager.py  # Repo operations
│   │       ├── microservice_response_builder.py    # Response formatting
│   │       ├── microservice_rollback_handler.py    # Cleanup on failure
│   │       ├── single_project_creator.py           # Single repo projects
│   │       └── variable_manager.py                 # CI/CD variable management
│   ├── utils/
│   │   ├── constants.py              # Application constants
│   │   ├── exceptions.py             # Custom exception classes
│   │   ├── validators.py             # Input validation utilities
│   │   └── input_sanitizer.py        # Input sanitization
│   └── __init__.py
├── tests/                            # Test suite
│   ├── test_gitlab_service.py
│   ├── test_template_processor.py
│   └── ...
├── main.py                           # Application entry point
├── requirements.txt                  # Python dependencies
├── requirements-test.txt             # Test dependencies
├── .env.example                      # Environment variables template
├── .env                              # Environment variables (gitignored)
├── pytest.ini                        # Pytest configuration
├── run_tests.py                      # Test runner script
├── NAMING_CONVENTIONS.md             # Code naming guidelines
└── s3_templates_structure.txt        # S3 template organization
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- GitLab account with OAuth application
- S3-compatible storage with templates
- Git for version control

### Setup

1. **Navigate to backend directory**
   ```bash
   cd spc-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   LOG_LEVEL=INFO

   # GitLab OAuth
   GITLAB_CLIENT_ID=your_gitlab_client_id
   GITLAB_CLIENT_SECRET=your_gitlab_client_secret
   GITLAB_REDIRECT_URI=http://localhost:8080/callback
   FRONTEND_URL=http://localhost:8080

   # CORS Origins (comma-separated)
   CORS_ORIGINS=http://localhost:8080,http://localhost:5173

   # S3 Storage Configuration
   S3_BUCKET=your-templates-bucket
   S3_REGION=us-east-1
   S3_ENDPOINT_URL=https://s3.amazonaws.com  # Optional for private S3
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key

   # OpenShift Cluster Configuration (optional)
   OPENSHIFT_PRODUCTION_A_TOKEN=token_for_prod_cluster_a
   OPENSHIFT_PRODUCTION_A_SERVER=https://openshift.prod-a.example.com
   OPENSHIFT_PRODUCTION_B_TOKEN=token_for_prod_cluster_b
   OPENSHIFT_PRODUCTION_B_SERVER=https://openshift.prod-b.example.com
   OPENSHIFT_TEST_C_TOKEN=token_for_test_cluster_c
   OPENSHIFT_TEST_C_SERVER=https://openshift.test-c.example.com
   OPENSHIFT_TEST_D_TOKEN=token_for_test_cluster_d
   OPENSHIFT_TEST_D_SERVER=https://openshift.test-d.example.com

   # HTTP Timeouts (in seconds)
   HTTP_TIMEOUT_DEFAULT=30.0
   HTTP_TIMEOUT_GITLAB=45.0
   HTTP_TIMEOUT_S3=60.0

   # Default Configuration
   DEFAULT_BRANCH=main
   COMMIT_MESSAGE=Initial project setup

   # Cache Configuration (in seconds)
   CACHE_TTL_GROUPS=900        # 15 minutes
   CACHE_TTL_PROJECTS=300      # 5 minutes
   CACHE_TTL_TEMPLATES=3600    # 1 hour
   CACHE_MAX_SIZE_GROUPS=500
   CACHE_MAX_SIZE_PROJECTS=100
   CACHE_MAX_SIZE_TEMPLATES=50
   ```

5. **Start development server**
   ```bash
   python main.py
   ```

   API will be available at `http://localhost:8000`

## Development

### Available Scripts

- **Start Server**: `python main.py`
- **Run Tests**: `python run_tests.py` or `pytest`
- **Run Specific Test**: `pytest tests/test_gitlab_service.py -v`
- **Coverage Report**: `pytest --cov=app tests/`

### Development Workflow

1. **Activate virtual environment**: `source venv/bin/activate`
2. **Start server with hot reload**: `python main.py` (uvicorn reload enabled)
3. **Make changes**: Server auto-reloads on file changes
4. **Run tests**: `pytest` before committing
5. **Check logs**: Monitor console output for errors

### Code Style

- **Type Hints**: Use type hints for all function parameters and returns
- **Docstrings**: Google-style docstrings for all classes and functions
- **Naming**: Follow `NAMING_CONVENTIONS.md` guidelines
- **Async/Await**: Use async functions for I/O operations
- **Error Handling**: Always use custom exceptions from `utils/exceptions.py`

### Architecture Patterns

#### Service Layer Pattern
Business logic separated into service classes:
- **GitLab Services**: Handle all GitLab API interactions
- **Template Services**: Process and render templates from S3
- **Project Services**: Orchestrate project creation workflows

#### Dependency Injection
Services are instantiated and injected via FastAPI dependencies:

```python
from fastapi import Depends
from app.services.gitlab.gitlab_service import GitLabService

@router.get("/groups")
async def get_groups(
    token: str,
    gitlab_service: GitLabService = Depends()
):
    return await gitlab_service.get_groups(token)
```

#### Exception Handling
Custom exception hierarchy with global handlers:

```python
# Define custom exception
class ProjectCreationError(Exception):
    def __init__(self, message: str, project_name: str):
        self.message = message
        self.project_name = project_name

# Global exception handler
@app.exception_handler(ProjectCreationError)
async def handle_project_error(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message}
    )
```

## API Documentation

### Interactive API Docs

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication Endpoints

#### `GET /login`
Initiates GitLab OAuth flow.

**Response**: Redirects to GitLab authorization page

---

#### `GET /callback`
Handles OAuth callback and exchanges code for access token.

**Query Parameters**:
- `code` (string, required): OAuth authorization code from GitLab

**Response**:
```json
{
  "access_token": "gitlab_access_token",
  "token_type": "Bearer"
}
```

---

### Groups Endpoints

#### `GET /groups`
Retrieves user's GitLab groups.

**Headers**:
- `Authorization: Bearer <token>` (required)

**Query Parameters**:
- `search` (string, optional): Filter groups by name
- `page` (integer, optional): Page number for pagination
- `per_page` (integer, optional): Items per page

**Response**:
```json
[
  {
    "id": 123,
    "name": "My Group",
    "full_path": "my-group",
    "description": "Group description",
    "visibility": "private"
  }
]
```

---

### Project Creation Endpoints

#### `POST /generate-repo`
Creates a new GitLab repository with templates.

**Headers**:
- `Authorization: Bearer <token>` (required)
- `Content-Type: application/json`

**Request Body**:
```json
{
  "project_name": "my-awesome-service",
  "name": "my-awesome-service",
  "groupId": 12345,
  "group_id": 12345,
  "project_type": "microservice",
  "stack": "python",
  "defaultBranch": "main",
  "visibility": "private",
  "clusters": [
    {
      "name": "dev-cluster",
      "environment": "dev",
      "server": "https://openshift.dev.example.com"
    },
    {
      "name": "prod-cluster",
      "environment": "production",
      "server": "https://openshift.prod.example.com"
    }
  ],
  "deliveryConfig": {
    "separateDeliveryRepo": true,
    "deliveryGroupId": 12346
  }
}
```

**Request Body Schema**:
- `project_name` (string, required): Project name
- `groupId` (integer, required): GitLab group ID
- `project_type` (string, required): One of: `library`, `microservice`, `standalone_microservice`, `monorepo`, `delivery`
- `stack` (string, required for most types): One of: `spring`, `maven`, `nodejs`, `react`, `python`, `dotnet`
- `defaultBranch` (string, optional): Default branch name (default: "main")
- `visibility` (string, optional): Repository visibility (default: "private")
- `clusters` (array, optional): Deployment cluster configurations
- `deliveryConfig` (object, optional): Delivery repository settings

**Response**:
```json
{
  "success": true,
  "message": "Project created successfully",
  "data": {
    "repository_url": "https://gitlab.com/my-group/my-awesome-service",
    "repository_id": 789,
    "delivery_repository_url": "https://gitlab.com/my-group/my-awesome-service-delivery",
    "delivery_repository_id": 790,
    "files_created": 15,
    "ci_variables_set": 4
  }
}
```

**Error Response**:
```json
{
  "detail": "Failed to create repository: Group not found",
  "project_name": "my-awesome-service"
}
```

## Template System

### S3 Template Structure

```
s3://solid-project-creator/templates/
├── common/
│   ├── README.md.j2            # Common README template
│   └── .helmignore             # Helm ignore file
│
├── docker/                      # Docker files for all stacks
│   ├── python.Dockerfile       # Python Dockerfile
│   ├── maven.Dockerfile        # Maven/Java Dockerfile
│   ├── node.Dockerfile         # Node.js Dockerfile
│   ├── dotnet.Dockerfile       # .NET Dockerfile
│   └── .dockerignore           # Common dockerignore file
│
├── project-types/               # Project type specific templates
│   ├── delivery/               # Delivery repository templates
│   │   ├── gitlab-ci.yml.j2
│   │   └── helm/
│   │       ├── values.yaml.j2
│   │       └── Chart.yaml.j2
│   ├── library/                # Library project CI/CD templates
│   │   ├── python.gitlab-ci.yml.j2
│   │   ├── dotnet.gitlab-ci.yml.j2
│   │   ├── maven.gitlab-ci.yml.j2
│   │   └── node.gitlab-ci.yml.j2
│   ├── microservice/           # Microservice CI/CD templates
│   │   ├── python.gitlab-ci.yml.j2
│   │   ├── dotnet.gitlab-ci.yml.j2
│   │   ├── maven.gitlab-ci.yml.j2
│   │   └── node.gitlab-ci.yml.j2
│   └── monorepo/               # Monorepo templates with Helm charts
│       ├── python.gitlab-ci.yml.j2
│       ├── dotnet.gitlab-ci.yml.j2
│       ├── maven.gitlab-ci.yml.j2
│       ├── node.gitlab-ci.yml.j2
│       └── helm/
│           ├── values.yaml.j2
│           └── Chart.yaml.j2
│
└── stacks/                      # Stack-specific configuration files
    ├── dotnet/                 # .NET stack configuration
    │   ├── nuget.config        # NuGet package manager config
    │   └── .gitignore          # .NET gitignore
    ├── maven/                  # Maven/Java stack configuration
    │   ├── pom.xml             # Maven project file
    │   ├── .gitignore          # Java/Maven gitignore
    │   ├── settings.xml        # Maven settings
    │   └── src/                # Empty source directory
    ├── node/                   # Node.js stack configuration
    │   ├── .gitignore          # Node.js gitignore
    │   └── .npmrc              # npm configuration
    └── python/                 # Python stack configuration
        ├── .gitignore          # Python gitignore
        └── pip.ini             # pip configuration
```

### Jinja2 Custom Delimiters

To avoid conflicts with Helm's `{{ }}` syntax, custom delimiters are used:

| Standard Jinja2 | Custom Delimiter | Usage |
|-----------------|------------------|-------|
| `{{ variable }}` | `{% variable %}` | Variable substitution |
| `{% if condition %}` | `{# if condition #}` | Control structures |
| `{# comment #}` | `{## comment ##}` | Comments |

**Example Template** (`deployment.yaml.j2`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {% project_name %}  # Jinja2 variable (processed)
spec:
  template:
    spec:
      containers:
      - name: {{ .Values.containerName }}  # Helm variable (not processed)
        image: {% docker_image %}  # Jinja2 variable (processed)
```

### Adding New Templates

1. **Create template file** with `.j2` extension
2. **Use custom Jinja2 delimiters** for variables
3. **Upload to appropriate S3 directory**
4. **Reference in template processor** if needed

### Template Variables

Available variables in all templates:
- `project_name`: Sanitized project name
- `repo_name`: Repository name
- `stack`: Technology stack (e.g., "python", "nodejs")
- `default_branch`: Default Git branch
- `gitlab_url`: GitLab instance URL

Additional variables for microservices:
- `clusters`: List of deployment clusters
- `environments`: List of environment names

## Services Overview

### GitLab Services

#### `gitlab_service.py`
Main GitLab API client with core operations:
- Repository creation and deletion
- File operations (create, update, batch commits)
- Authentication and token management

#### `gitlab_groups_service.py`
Group-specific operations:
- List user groups
- Search groups
- Get group details

#### `gitlab_repository_service.py`
Repository-specific operations:
- Create repositories with configurations
- Set repository settings (visibility, features)
- Branch management

#### `gitlab_variables_service.py`
CI/CD variables management:
- Set cluster variables for deployments
- Environment-specific variables
- Variable encryption and masking

### Template Services

#### `template_processor.py`
Orchestrates template retrieval and processing:
- Fetches templates from S3
- Determines which templates to use based on project type and stack
- Coordinates with renderer and config manager

#### `template_renderer.py`
Jinja2 template rendering:
- Processes templates with custom delimiters
- Variable substitution
- Control flow handling

#### `stack_config_manager.py`
Stack-specific configuration:
- Selects appropriate Dockerfile for stack
- Chooses correct .gitignore file
- Provides stack-specific build configurations

### Project Services

#### `project_creator.py`
Main project creation orchestrator:
- Routes to appropriate creator based on project type
- Manages overall creation workflow
- Error handling and rollback coordination

#### `microservice_creator.py`
Microservice-specific creation logic:
- Creates application repository
- Optionally creates separate delivery repository
- Configures CI/CD variables for clusters

#### `microservice_repository_manager.py`
Repository operations for microservices:
- File generation and upload
- Branch configuration
- Repository settings

#### `microservice_response_builder.py`
Response formatting:
- Builds success responses with repository details
- Formats error messages
- Includes metadata (file counts, variables set, etc.)

#### `microservice_rollback_handler.py`
Cleanup on failure:
- Deletes created repositories on error
- Removes partial configurations
- Logs rollback actions

#### `variable_manager.py`
CI/CD variable management:
- Maps clusters to GitLab CI/CD variables
- Sets environment-specific variables
- Handles OpenShift credentials

## Configuration

### Environment Variables

See `.env.example` for complete list. Key configurations:

#### Server Settings
- `HOST`: Server bind address (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

#### GitLab OAuth
- `GITLAB_CLIENT_ID`: OAuth application ID
- `GITLAB_CLIENT_SECRET`: OAuth application secret
- `GITLAB_REDIRECT_URI`: OAuth callback URL

#### S3 Storage
- `S3_BUCKET`: Bucket name for templates
- `S3_REGION`: AWS region
- `S3_ENDPOINT_URL`: Custom S3 endpoint (optional)
- `AWS_ACCESS_KEY_ID`: S3 access key
- `AWS_SECRET_ACCESS_KEY`: S3 secret key

#### Performance Tuning
- `HTTP_TIMEOUT_*`: Timeout values for different operations
- `CACHE_TTL_*`: Cache time-to-live for different resources
- `CACHE_MAX_SIZE_*`: Maximum cache sizes

### Logging

Structured logging configured in `app/core/logger.py`:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Operation completed successfully")
logger.error(f"Error occurred: {error_message}")
```

Log levels:
- **DEBUG**: Detailed information for debugging
- **INFO**: General operational messages
- **WARNING**: Warning messages for unexpected situations
- **ERROR**: Error messages for failures

## Testing

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run with pytest
pytest

# Run specific test file
pytest tests/test_gitlab_service.py -v

# Run with coverage
pytest --cov=app tests/

# Run tests matching pattern
pytest -k "test_create" -v
```

### Test Structure

```
tests/
├── test_gitlab_service.py         # GitLab service tests
├── test_template_processor.py     # Template processing tests
├── test_project_creator.py        # Project creation tests
├── test_validators.py             # Validation tests
└── conftest.py                    # Pytest fixtures
```

### Writing Tests

```python
import pytest
from app.services.gitlab.gitlab_service import GitLabService

@pytest.mark.asyncio
async def test_create_repository():
    gitlab_service = GitLabService()
    repo = await gitlab_service.create_repository(
        token="test_token",
        repo_data={"name": "test-repo", "group_id": 123}
    )
    assert repo["name"] == "test-repo"
```

## Deployment

### Production Server

Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and run:
```bash
docker build -t spc-backend .
docker run -p 8000:8000 --env-file .env spc-backend
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spc-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: spc-backend
  template:
    metadata:
      labels:
        app: spc-backend
    spec:
      containers:
      - name: spc-backend
        image: spc-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: spc-backend-secrets
```

## Troubleshooting

### Common Issues

**GitLab API Errors**
- Verify token has correct scopes (`api`, `read_repository`, `write_repository`)
- Check GitLab API rate limits
- Ensure network connectivity to GitLab instance

**S3 Connection Failures**
- Verify AWS credentials are correct
- Check S3 bucket exists and is accessible
- Verify S3_ENDPOINT_URL if using private S3
- Test S3 connectivity independently

**Template Processing Errors**
- Check template syntax (Jinja2 with custom delimiters)
- Verify templates exist in S3 bucket
- Check template variable references
- Review logs for specific Jinja2 errors

**Repository Creation Failures**
- Verify user has permissions in target group
- Check for duplicate repository names
- Review GitLab API response in logs
- Ensure group ID is valid

**Performance Issues**
- Increase HTTP timeout values in `.env`
- Adjust cache TTL and sizes
- Consider adding more workers in production
- Monitor database/S3 connection pools

### Debug Mode

Enable debug logging in `.env`:
```env
LOG_LEVEL=DEBUG
```

This will log:
- All HTTP requests to GitLab API
- S3 operations
- Template processing details
- Cache hits/misses

## Contributing

1. Follow existing code structure and patterns
2. Add type hints to all functions
3. Write docstrings for all classes and functions
4. Add tests for new functionality
5. Run tests before committing: `pytest`
6. Follow naming conventions in `NAMING_CONVENTIONS.md`
7. Handle errors properly with custom exceptions
8. Use async/await for I/O operations
9. Update documentation for API changes

## License

MIT License
