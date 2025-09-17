from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """

    gitlab_url: str = "https://gitlab.com/api/v4"
    s3_bucket: str = "your-bucket"
    s3_region: str = "us-east-1"
    s3_endpoint_url: str = None  # Set to your private S3 endpoint
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    log_level: str = "INFO"
    port: int = 8000
    gitlab_client_id: str = ""
    gitlab_client_secret: str = ""
    gitlab_redirect_uri: str = "http://localhost:8000/callback"
    gitlab_token_url: str = "https://gitlab.com/oauth/token"
    frontend_url: str = "http://localhost:8080"
    
    # Environment-specific OpenShift configuration
    os_env_a_token: str = ""
    os_env_a_server: str = ""
    os_env_b_token: str = ""
    os_env_b_server: str = ""
    os_env_c_token: str = ""
    os_env_c_server: str = ""
    os_env_d_token: str = ""
    os_env_d_server: str = ""

    class Config:
        env_file = ".env"


# Environment configuration mapping
ENVIRONMENT_CONFIG = {
    "a": {
        "name": "Production A",
        "environment": "a"
    },
    "b": {
        "name": "Production B", 
        "environment": "b"
    },
    "c": {
        "name": "Test C",
        "environment": "c"
    },
    "d": {
        "name": "Staging D",
        "environment": "d"
    }
}

settings = Settings()
