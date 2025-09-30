# Solid Project Creator

Automated GitLab repository creation tool with templates, CI/CD pipelines, and deployment configurations.

## Features

- **Automated Repository Creation**: Create GitLab repositories with predefined templates
- **Multiple Project Types**: Support for libraries, microservices, and standalone microservices
- **Technology Stack Templates**: Pre-configured templates for Spring, Maven, Node.js, React, Python, .NET, and more
- **CI/CD Pipeline Generation**: Automatic GitLab CI/CD pipeline creation with deployment configurations
- **Helm Chart Integration**: Built-in Kubernetes deployment with Helm charts for microservices
- **Multi-Environment Support**: Dev, staging, and production environment configurations
- **OpenShift Integration**: Deployment server configuration for OpenShift environments
- **GitLab OAuth**: Secure authentication with GitLab OAuth flow
- **Repository Management**: Create both application and delivery repositories with proper GitOps patterns

## Architecture

The application consists of two main components:

### Frontend (React/TypeScript)
- Built with Vite, React 18, and TypeScript
- UI components using shadcn/ui and Tailwind CSS
- GitLab OAuth integration for authentication
- Form validation with React Hook Form and Zod
- Responsive design with modern UI/UX

### Backend (FastAPI/Python)
- FastAPI REST API with OAuth authentication
- GitLab API integration for repository and group management
- Jinja2 template processing for code generation
- Comprehensive error handling and validation
- Transaction rollback for failed repository creation

## Project Types

1. **Library**: Simple library projects with basic CI/CD
2. **Microservice**: Application repository with optional separate delivery repository
3. **Standalone Microservice**: Single repository containing both application code and deployment configurations

## Technology Stack Templates

- **Spring**: Java Spring Boot applications with Maven
- **Maven**: Java projects with Maven build system
- **Node.js**: JavaScript/TypeScript Node.js applications
- **React**: React frontend applications
- **Python**: Python applications with standard project structure
- **.NET**: .NET Core applications
- **Fallback System**: Automatic fallback to compatible templates

## Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- GitLab account with API access

### Frontend Setup
```bash
# Clone the repository
git clone <repository-url>
cd gitlab-repo-sculptor

# Install dependencies
npm install

# Start development server
npm run dev
```

### Backend Setup
```bash
# Navigate to backend directory
cd app

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export GITLAB_CLIENT_ID=your_gitlab_client_id
export GITLAB_CLIENT_SECRET=your_gitlab_client_secret
export GITLAB_REDIRECT_URI=http://localhost:8080/callback

# Start FastAPI server
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

## Configuration

### Environment Variables
- `GITLAB_CLIENT_ID`: GitLab OAuth application client ID
- `GITLAB_CLIENT_SECRET`: GitLab OAuth application client secret
- `GITLAB_REDIRECT_URI`: OAuth redirect URI
- `GITLAB_BASE_URL`: GitLab instance URL (default: https://gitlab.com)

### GitLab OAuth Setup
1. Create a new application in GitLab (User Settings > Applications)
2. Set redirect URI to `http://localhost:8080/callback`
3. Select scopes: `api`, `read_user`, `read_repository`, `write_repository`
4. Use the provided client ID and secret in your environment variables

## Deployment

### Frontend Build
```bash
npm run build
```

### Production Deployment
The application can be deployed using:
- Docker containers
- Static hosting (frontend) + API hosting (backend)
- Kubernetes with the provided Helm charts
- Cloud platforms (Vercel, Netlify for frontend; Heroku, AWS for backend)

## Technologies Used

### Frontend
- **Vite**: Fast build tool and development server
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript development
- **shadcn/ui**: Modern, accessible UI components
- **Tailwind CSS**: Utility-first CSS framework
- **React Hook Form**: Performant form handling
- **Zod**: TypeScript-first schema validation
- **React Router**: Client-side routing
- **Lucide React**: Modern icon library

### Backend
- **FastAPI**: Modern, fast Python web framework
- **Jinja2**: Template engine for code generation
- **Pydantic**: Data validation and serialization
- **GitLab API**: Repository and project management
- **OAuth 2.0**: Secure authentication flow

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
