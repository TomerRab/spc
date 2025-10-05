# Solid Project Creator (SPC)

Automated GitLab repository scaffolding tool that creates production-ready projects with pre-configured templates, CI/CD pipelines, Helm charts, and deployment configurations.

## Overview

SPC streamlines the process of creating new GitLab projects by automatically generating repositories with:
- Technology-specific boilerplate code and project structures
- GitLab CI/CD pipeline configurations
- Kubernetes deployment manifests and Helm charts
- Multi-environment configurations (dev/staging/production)
- OpenShift deployment server integration
- GitOps-compliant delivery repositories

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│   spc-client    │────────▶│   spc-backend    │────────▶│   GitLab    │
│  React + Vite   │  OAuth  │   FastAPI        │   API   │     API     │
└─────────────────┘         └──────────────────┘         └─────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  S3 Templates   │
                            │  (Jinja2)       │
                            └─────────────────┘
```

### Frontend (`spc-client`)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Components**: shadcn/ui with Radix UI primitives
- **Styling**: Tailwind CSS
- **Form Management**: React Hook Form with Zod validation
- **State Management**: TanStack Query (React Query)
- **Authentication**: GitLab OAuth 2.0 integration
- **Routing**: React Router v6

### Backend (`spc-backend`)
- **Framework**: FastAPI (Python)
- **Authentication**: GitLab OAuth 2.0 token-based auth
- **Template Engine**: Jinja2 with custom delimiters (compatible with Helm)
- **Storage**: S3-compatible object storage for templates
- **API Integration**: GitLab REST API for repository and group management
- **Error Handling**: Comprehensive exception handling with transaction rollback
- **Configuration**: Pydantic settings with environment validation
- **Logging**: Structured logging with configurable levels

## Features

### Project Types
- **Library**: Standard code libraries with basic CI/CD
- **Microservice**: Full-stack microservices with optional separate delivery repositories
- **Standalone Microservice**: Single repository with both application code and deployment configs
- **Monorepo**: Multi-service repositories with shared Helm charts
- **Delivery**: Standalone deployment configuration repositories

### Supported Tech Stacks
- Spring Boot (Java with Maven)
- Maven (Java projects)
- Node.js (JavaScript/TypeScript)
- React (Frontend applications)
- Python (FastAPI, Django, etc.)
- .NET Core
- Automatic fallback to compatible templates

### Key Capabilities
- **GitLab OAuth Integration**: Secure authentication and authorization
- **Template Processing**: Jinja2-based code generation from S3 templates
- **CI/CD Automation**: Auto-generates `.gitlab-ci.yml` with environment-specific pipelines
- **Helm Chart Generation**: Kubernetes deployment manifests for microservices
- **Multi-Environment Support**: Separate configurations for dev, staging, and production
- **Cluster Management**: Automatic GitLab CI/CD variable configuration for deployment targets
- **GitOps Pattern**: Separates application code from deployment configurations
- **Transaction Safety**: Automatic rollback on repository creation failures
- **Input Validation**: Comprehensive sanitization and validation of user inputs

## Installation

### Prerequisites
- **Node.js**: 18.x or higher
- **Python**: 3.9 or higher
- **GitLab Account**: With OAuth application configured
- **S3 Storage**: Bucket with project templates
- **Git**: For version control

### Frontend Setup

```bash
# Navigate to client directory
cd spc-client

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your GitLab OAuth credentials

# Start development server
npm run dev
```

The client will be available at `http://localhost:8080`

### Backend Setup

```bash
# Navigate to backend directory
cd spc-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with required credentials

# Start FastAPI server
python main.py
```

The API will be available at `http://localhost:8000`

## Configuration

### Environment Variables

#### Frontend (`.env`)
```env
VITE_API_URL=http://localhost:8000
VITE_GITLAB_CLIENT_ID=your_gitlab_client_id
VITE_GITLAB_REDIRECT_URI=http://localhost:8080/callback
```

#### Backend (`.env`)
```env
# GitLab OAuth
GITLAB_CLIENT_ID=your_gitlab_client_id
GITLAB_CLIENT_SECRET=your_gitlab_client_secret
GITLAB_REDIRECT_URI=http://localhost:8080/callback
GITLAB_BASE_URL=https://gitlab.com

# S3 Storage
S3_BUCKET=your-templates-bucket
S3_ENDPOINT_URL=https://your-s3-endpoint  # Optional for private S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Server
HOST=0.0.0.0
PORT=8000

# CORS
CORS_ORIGINS=http://localhost:8080,http://localhost:5173
```

### GitLab OAuth Application Setup

1. Navigate to GitLab → **User Settings** → **Applications**
2. Create new application with:
   - **Name**: Solid Project Creator
   - **Redirect URI**: `http://localhost:8080/callback`
   - **Scopes**: `api`, `read_user`, `read_repository`, `write_repository`
3. Copy the **Application ID** and **Secret** to your `.env` files

### S3 Template Structure

```
templates/
├── common/
│   ├── configs/          # Stack-specific configs (settings.xml, .npmrc)
│   ├── build/            # Dockerfiles and .dockerignore
│   ├── gitignore/        # Tech stack .gitignore files
│   └── README.md.j2      # Common README template
├── library/              # Library project templates
├── microservice/         # Microservice templates with CI/CD
├── monorepo/             # Monorepo templates with Helm charts
└── delivery/             # Delivery templates with Helm charts
```

## Usage

### Creating a New Project

1. **Authenticate**: Log in with GitLab OAuth
2. **Select Group**: Choose target GitLab group
3. **Configure Project**:
   - Project name
   - Project type (library, microservice, etc.)
   - Technology stack
   - Default branch name
4. **Configure Deployment** (for microservices):
   - Add cluster configurations
   - Specify environments (dev/staging/prod)
   - Choose delivery repository options
5. **Create**: Submit to generate repositories

### API Endpoints

#### Authentication
- `GET /login` - Initiate GitLab OAuth flow
- `GET /callback` - Handle OAuth callback and exchange code for token

#### Repository Operations
- `GET /groups` - List user's GitLab groups
- `POST /generate-repo` - Create repository with templates

#### Example Request
```bash
curl -X POST http://localhost:8000/generate-repo \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-awesome-service",
    "group_id": "12345",
    "project_type": "microservice",
    "stack": "python",
    "defaultBranch": "main",
    "clusters": [
      {
        "name": "dev-cluster",
        "environment": "dev",
        "server": "https://openshift.dev.example.com"
      }
    ],
    "deliveryConfig": {
      "separateDeliveryRepo": true,
      "deliveryGroupId": "12346"
    }
  }'
```

## Development

### Project Structure

```
repo-creator/
├── spc-client/                 # Frontend application
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── auth/          # Authentication components
│   │   │   ├── forms/         # Form components
│   │   │   ├── project-creation/ # Project creation flow
│   │   │   ├── selectors/     # Group/stack selectors
│   │   │   └── ui/            # shadcn/ui components
│   │   ├── contexts/          # React contexts
│   │   ├── hooks/             # Custom React hooks
│   │   ├── pages/             # Page components
│   │   ├── schemas/           # Zod validation schemas
│   │   ├── services/          # API service layer
│   │   └── utils/             # Utility functions
│   └── package.json
│
└── spc-backend/                # Backend API
    ├── app/
    │   ├── api/
    │   │   ├── routes/        # FastAPI route handlers
    │   │   └── error_handlers.py
    │   ├── core/              # Core configuration
    │   │   ├── config.py      # Settings management
    │   │   ├── logger.py      # Logging setup
    │   │   └── cache.py       # Caching utilities
    │   ├── schemas/           # Pydantic models
    │   │   ├── repo_models.py # Repository request/response
    │   │   └── response_models.py
    │   ├── services/          # Business logic
    │   │   ├── gitlab_service.py # GitLab API client
    │   │   ├── project/       # Project creation services
    │   │   │   ├── microservice_repository_manager.py
    │   │   │   ├── microservice_response_builder.py
    │   │   │   └── ...
    │   │   └── template_processor.py # S3 + Jinja2
    │   └── utils/             # Utilities
    │       ├── validators.py  # Input validation
    │       ├── exceptions.py  # Custom exceptions
    │       └── sanitizer.py   # Input sanitization
    ├── tests/                 # Test suite
    └── requirements.txt
```

### Running Tests

#### Frontend
```bash
cd spc-client
npm run lint
```

#### Backend
```bash
cd spc-backend
python run_tests.py
```

### Building for Production

#### Frontend
```bash
cd spc-client
npm run build
# Output in dist/
```

#### Backend
```bash
cd spc-backend
# Use a production WSGI server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Template System

### Jinja2 Custom Delimiters
To avoid conflicts with Helm template syntax, SPC uses custom Jinja2 delimiters:
- **Variables**: `{% variable_name %}` (instead of `{{ variable }}`)
- **Control blocks**: `{# if condition #}` (instead of `{% if %}`)
- **Helm syntax**: `{{ .Values.name }}` remains unchanged

### Adding New Templates
1. Create template files with `.j2` extension
2. Use custom Jinja2 delimiters for variables
3. Upload to appropriate S3 directory
4. Templates are automatically processed during repository creation

### Adding New Tech Stacks
1. Add stack to `Stack` enum in `app/schemas/repo_models.py`
2. Create stack-specific templates in S3
3. Add stack-specific configurations (Dockerfile, .gitignore, etc.)

## Deployment

### Docker Deployment
```bash
# Build frontend
cd spc-client
docker build -t spc-client .

# Build backend
cd spc-backend
docker build -t spc-backend .
```

### Kubernetes Deployment
- Use provided Helm charts (if available)
- Configure ingress for frontend
- Set up backend service with environment variables
- Ensure S3 and GitLab connectivity

## Troubleshooting

### Common Issues

**OAuth Redirect Errors**
- Verify redirect URI matches in GitLab app and `.env` files
- Ensure frontend and backend URLs are correctly configured

**S3 Connection Failures**
- Check S3 credentials and endpoint URL
- Verify bucket exists and is accessible
- Test S3 connectivity independently

**Repository Creation Failures**
- Check GitLab API token permissions
- Verify group ID exists and user has access
- Review backend logs for detailed error messages

**Template Processing Errors**
- Ensure templates exist in S3
- Verify Jinja2 syntax in templates
- Check template variables match expected context

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on the repository.
