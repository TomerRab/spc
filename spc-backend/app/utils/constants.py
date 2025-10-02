# API and timeout constants
API_TIMEOUTS = {
    'DEFAULT': 30.0,
    'GITLAB_REQUEST': 10.0,
    'S3_UPLOAD': 60.0,
    'TEMPLATE_PROCESSING': 15.0,
}

# Network constants
NETWORK_CONFIG = {
    'DEFAULT_HOST': '127.0.0.1',
    'ALLOWED_ORIGINS': [
        'http://localhost:8080',
        'http://localhost:3000', 
        'http://localhost:5173'
    ]
}

# Project validation constants
PROJECT_CONSTANTS = {
    'MIN_NAME_LENGTH': 2,
    'MAX_NAME_LENGTH': 100,
    'VALID_PROJECT_TYPES': [
        'library', 
        'microservice', 
        'standalone-microservice', 
        'monorepo', 
        'delivery'
    ],
    'VALID_STACKS': [
        'maven',
        'spring',
        'node',
        'react',
        'python',
        'dotnet',
        'csharp'
    ],
    'VALID_VISIBILITIES': ['private', 'internal', 'public'],
    'DEFAULT_BRANCH': 'main',
}

# GitLab specific constants
GITLAB_CONSTANTS = {
    'API_VERSION': 'v4',
    'BASE_URL': 'https://gitlab.com/api/v4',
    'OAUTH_BASE_URL': 'https://gitlab.com/oauth',
    'OAUTH_AUTHORIZE_URL': 'https://gitlab.com/oauth/authorize',
    'OAUTH_TOKEN_URL': 'https://gitlab.com/oauth/token',
    'DEFAULT_SCOPES': 'api read_user read_repository write_repository',
    'MAX_GROUPS_PER_REQUEST': 100,
    'MIN_SEARCH_LENGTH': 3,
}

# Environment configuration
ENVIRONMENT_NAMES = {
    'a': 'Production A',
    'b': 'Production B', 
    'c': 'Test C',
    'd': 'Test D'
}

# Template constants
TEMPLATE_CONSTANTS = {
    'JINJA_DELIMITERS': {
        'VARIABLE_START': '{%',
        'VARIABLE_END': '%}',
        'BLOCK_START': '{#',
        'BLOCK_END': '#}',
    },
    'SUPPORTED_EXTENSIONS': ['.j2', '.jinja2'],
    'PROJECT_TYPES': {
        'MICROSERVICE': 'microservice',
        'DELIVERY': 'delivery', 
        'LIBRARY': 'library',
        'MONOREPO': 'monorepo',
        'STANDALONE_MICROSERVICE': 'standalone-microservice'
    }
}

