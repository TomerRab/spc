"""Input sanitization utilities for security."""
import re
import html
from typing import Any, Dict, Optional


class InputSanitizer:
    """Utilities for sanitizing user input."""
    
    # Patterns for validation
    PROJECT_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.]+$')
    NAMESPACE_PATTERN = re.compile(r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$')
    STACK_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]+$')
    URL_PATTERN = re.compile(r'^https?://[^\s<>"{}\\|^`\[\]]+$')
    
    # Dangerous patterns to block
    # Note: We interact with GitLab API (not SQL), so SQL injection patterns are not needed
    # Focus on XSS, template injection, and control characters
    INJECTION_PATTERNS = [
        re.compile(r'[<>"\'\\\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]'),  # Control characters and quotes
        re.compile(r'(javascript:|data:|vbscript:)', re.IGNORECASE),  # Protocol handlers
        re.compile(r'(onload|onerror|onclick|onmouseover)\s*=', re.IGNORECASE),  # Event handlers
        re.compile(r'(\$\{|\{\{|<%|<\?)', re.IGNORECASE),  # Template injection patterns
    ]

    @classmethod
    def sanitize_project_name(cls, name: str) -> str:
        """Sanitize project name input."""
        if not name or not isinstance(name, str):
            raise ValueError("Project name must be a non-empty string")
        
        # Strip whitespace
        name = name.strip()
        
        # Check for dangerous patterns
        cls._check_for_dangerous_patterns(name)
        
        # Validate against allowed pattern
        if not cls.PROJECT_NAME_PATTERN.match(name):
            raise ValueError("Project name contains invalid characters")
        
        # Length validation
        if len(name) < 2:
            raise ValueError("Project name must be at least 2 characters")
        if len(name) > 100:
            raise ValueError("Project name must be 100 characters or less")
        
        return name

    @classmethod
    def sanitize_namespace(cls, namespace: str) -> str:
        """Sanitize Kubernetes namespace input."""
        if not namespace or not isinstance(namespace, str):
            raise ValueError("Namespace must be a non-empty string")
        
        # Strip and lowercase
        namespace = namespace.strip().lower()
        
        # Check for dangerous patterns
        cls._check_for_dangerous_patterns(namespace)
        
        # Validate against Kubernetes naming rules
        if not cls.NAMESPACE_PATTERN.match(namespace):
            raise ValueError("Namespace must follow Kubernetes naming rules")
        
        # Length validation
        if len(namespace) > 63:
            raise ValueError("Namespace must be 63 characters or less")
        
        return namespace

    @classmethod
    def sanitize_stack(cls, stack: Optional[str]) -> Optional[str]:
        """Sanitize technology stack input."""
        if not stack:
            return None
        
        if not isinstance(stack, str):
            raise ValueError("Stack must be a string")
        
        stack = stack.strip().lower()
        
        # Check for dangerous patterns
        cls._check_for_dangerous_patterns(stack)
        
        # Validate against allowed pattern
        if not cls.STACK_PATTERN.match(stack):
            raise ValueError("Stack contains invalid characters")
        
        return stack

    @classmethod
    def sanitize_visibility(cls, visibility: str) -> str:
        """Sanitize visibility input."""
        if not visibility or not isinstance(visibility, str):
            raise ValueError("Visibility must be specified")
        
        visibility = visibility.strip().lower()
        
        # Only allow specific values
        allowed_values = ['private', 'internal', 'public']
        if visibility not in allowed_values:
            raise ValueError(f"Visibility must be one of: {', '.join(allowed_values)}")
        
        return visibility

    @classmethod
    def sanitize_url(cls, url: Optional[str]) -> Optional[str]:
        """Sanitize URL input."""
        if not url:
            return None
        
        if not isinstance(url, str):
            raise ValueError("URL must be a string")
        
        url = url.strip()
        
        # Check for dangerous patterns
        cls._check_for_dangerous_patterns(url)
        
        # Validate URL format
        if not cls.URL_PATTERN.match(url):
            raise ValueError("Invalid URL format")
        
        return url

    @classmethod
    def sanitize_server_config(cls, servers: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Sanitize server configuration input."""
        if not servers:
            return None
        
        if not isinstance(servers, dict):
            raise ValueError("Server configuration must be a dictionary")
        
        sanitized = {}
        allowed_keys = ['a', 'b', 'c', 'd']
        
        for key, config in servers.items():
            # Validate server key
            if key not in allowed_keys:
                raise ValueError(f"Invalid server key: {key}")
            
            # Validate config structure
            if not isinstance(config, dict):
                raise ValueError(f"Server {key} configuration must be a dictionary")
            
            # Sanitize namespace
            if 'namespace' in config:
                namespace = cls.sanitize_namespace(config['namespace'])
                sanitized[key] = {'namespace': namespace}
        
        return sanitized if sanitized else None

    @classmethod
    def sanitize_delivery_config(cls, delivery: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Sanitize delivery configuration input."""
        if not delivery:
            return None
        
        if not isinstance(delivery, dict):
            raise ValueError("Delivery configuration must be a dictionary")
        
        sanitized = {}
        
        # Sanitize createDelivery flag
        if 'createDelivery' in delivery:
            create_delivery = delivery.get('createDelivery')
            if not isinstance(create_delivery, bool):
                raise ValueError("createDelivery must be a boolean")
            sanitized['createDelivery'] = create_delivery
        
        # Sanitize delivery group ID
        if 'deliveryGroupId' in delivery:
            group_id = delivery.get('deliveryGroupId')
            if not isinstance(group_id, int) or group_id <= 0:
                raise ValueError("deliveryGroupId must be a positive integer")
            sanitized['deliveryGroupId'] = group_id
        
        # Sanitize delivery name
        if 'deliveryName' in delivery:
            name = delivery.get('deliveryName')
            if name:
                sanitized['deliveryName'] = cls.sanitize_project_name(name)
        
        # Sanitize delivery servers
        if 'deliveryServers' in delivery:
            servers = cls.sanitize_server_config(delivery.get('deliveryServers'))
            if servers:
                sanitized['deliveryServers'] = servers
        
        return sanitized if sanitized else None

    @classmethod
    def _check_for_dangerous_patterns(cls, text: str) -> None:
        """Check text for dangerous injection patterns."""
        for pattern in cls.INJECTION_PATTERNS:
            if pattern.search(text):
                raise ValueError("Input contains potentially dangerous characters or patterns")

    @classmethod
    def escape_html(cls, text: str) -> str:
        """Escape HTML characters in text."""
        return html.escape(text) if text else ""

    @classmethod
    def sanitize_log_message(cls, message: str) -> str:
        """Sanitize message for safe logging."""
        if not message:
            return ""
        
        # Remove control characters and escape HTML
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', str(message))
        return cls.escape_html(sanitized)[:1000]  # Limit length