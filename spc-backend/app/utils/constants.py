# API and timeout constants
API_TIMEOUTS = {
    'DEFAULT': 30.0,
    'GITLAB_REQUEST': 10.0,
    'S3_UPLOAD': 60.0,
    'TEMPLATE_PROCESSING': 15.0,
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
        'typescript', 
        'javascript', 
        'vue', 
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
    'MAX_GROUPS_PER_REQUEST': 100,
    'MIN_SEARCH_LENGTH': 3,
    'OAUTH_SCOPES': 'api read_user read_repository write_repository',
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
}