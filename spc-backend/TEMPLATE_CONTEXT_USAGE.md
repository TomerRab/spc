# TemplateContext Usage Guide

## Overview

The `TemplateContext` class provides a clean, extensible way to pass template variables throughout the project creation pipeline. It solves the problem of **parameter explosion** by encapsulating all template-related variables in a single, well-defined object.

## Why TemplateContext?

### Before: Parameter Explosion ❌
```python
async def get_project_files(
    self,
    project_type: str,
    repo_name: str,
    stack: Optional[str] = None,
    environments: Optional[list] = None,
    delivery_url: Optional[str] = None,  # Parameters keep growing!
    # ... more parameters in the future?
) -> Dict[str, str]:
```

### After: Clean Interface ✅
```python
async def get_project_files(self, context: TemplateContext) -> Dict[str, str]:
```

## Architecture

```
┌─────────────────────┐
│  RepoRequest        │  API Layer (from client)
│  (User input)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  TemplateContext    │  Template Layer (internal)
│  (Template vars)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Jinja2 Templates   │  Rendering Layer (S3)
│  (.gitlab-ci.yml)   │
└─────────────────────┘
```

**Key Principle**: `RepoRequest` is for the API layer, `TemplateContext` is for the template layer.

## TemplateContext Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `project_type` | `str` | Type of project | `"microservice"`, `"library"`, `"delivery"` |
| `repo_name` | `str` | Sanitized repository name | `"my-awesome-service"` |
| `stack` | `Optional[str]` | Technology stack | `"python"`, `"maven"`, `"node"` |
| `environments` | `Optional[List[str]]` | Deployment environments | `["a", "b", "c"]` |
| `delivery_url` | `Optional[str]` | URL of delivery repository | `"https://gitlab.com/group/my-service-delivery.git"` |

## How to Use

### 1. Building a TemplateContext

```python
from app.schemas.template_models import TemplateContext

# Extract environments from openshiftServers
environments = list(repo_request.openshiftServers.keys()) if repo_request.openshiftServers else None

# Build context
context = TemplateContext(
    project_type=repo_request.projectType,
    repo_name=repo_request.sanitized_name,
    stack=repo_request.stack,
    environments=environments,
    delivery_url=delivery_url  # Pass delivery URL if creating microservice
)

# Pass to template processor
files = await template_processor.get_project_files(context)
```

### 2. Using in Templates

Variables from `TemplateContext` are automatically available in Jinja2 templates:

**In your S3 template** (`templates/project-types/microservice/python.gitlab-ci.yml.j2`):
```yaml
stages:
  - build
  - deploy

variables:
  PROJECT_NAME: {% repo_name %}
  STACK: {% stack %}

  # Delivery URL is automatically injected!
  DELIVERY_REPO: {% delivery_url %}

deploy:
  stage: deploy
  script:
    - echo "Deploying {% repo_name %} to {% delivery_url %}"
    - git clone {% delivery_url %}
    - # Deploy using delivery repo configs
```

### 3. Accessing Template Variables

The `TemplateProcessor` automatically injects variables from the context:

```python
# In template_processor.py
async def _generate_standard_ci(self, context: TemplateContext, stack_name: str) -> str:
    template_vars = {
        "repo_name": context.repo_name,
        "stack": stack_name,
    }

    # Add delivery_url if present (for microservices with separate delivery repos)
    if context.delivery_url:
        template_vars["delivery_url"] = context.delivery_url
        logger.info(f"Injecting delivery_url into CI template: {context.delivery_url}")

    return await self.renderer.process_template(
        f"templates/project-types/{context.project_type}/{stack_name}.gitlab-ci.yml.j2",
        template_vars,
    )
```

## Delivery URL Feature

### How It Works

When creating a **microservice with a separate delivery repository**:

1. **Delivery repo is created FIRST** → returns its URL
2. **Microservice repo is created SECOND** → receives delivery URL in TemplateContext
3. **CI template is rendered** → `{% delivery_url %}` is replaced with actual URL

```python
# In microservice_creator.py
async def create_with_delivery(self, token: str, repo_request: RepoRequest) -> Dict:
    # STEP 1: Create delivery repo first
    delivery_data = await self._create_delivery_part(token, repo_request, created_repos)
    delivery_url = delivery_data[0]  # Extract URL

    # STEP 2: Create microservice repo with delivery URL
    microservice_data = await self._create_microservice_part(
        token, repo_request, created_repos, delivery_url
    )
```

### Template Example

**Microservice CI template** can now reference its delivery repo:

```yaml
trigger_delivery:
  stage: deploy
  trigger:
    project: {% delivery_url %}  # Automatically injected!
    branch: main
```

## Adding New Template Variables

To add a new template variable:

### 1. Update TemplateContext

```python
# In app/schemas/template_models.py
@dataclass
class TemplateContext:
    project_type: str
    repo_name: str
    stack: Optional[str] = None
    environments: Optional[List[str]] = None
    delivery_url: Optional[str] = None
    my_new_variable: Optional[str] = None  # ← Add here
```

### 2. Update to_dict() method

```python
def to_dict(self) -> dict:
    return {
        "project_type": self.project_type,
        "repo_name": self.repo_name,
        "stack": self.stack or "",
        "environments": self.environments or [],
        "delivery_url": self.delivery_url or "",
        "my_new_variable": self.my_new_variable or "",  # ← Add here
    }
```

### 3. Pass it when building context

```python
# In microservice_repository_manager.py or single_project_creator.py
context = TemplateContext(
    project_type=project_type,
    repo_name=repo_request.sanitized_name,
    stack=repo_request.stack,
    environments=environments,
    delivery_url=delivery_url,
    my_new_variable=some_value  # ← Add here
)
```

### 4. Use it in templates

```yaml
# In your .gitlab-ci.yml.j2 template
my_variable: {% my_new_variable %}
```

## Best Practices

### ✅ DO

- **Use TemplateContext** for template-related variables
- **Keep it simple** - only add variables that are used in templates
- **Document new fields** in the docstring
- **Provide defaults** for optional fields (`None` or `""`)

### ❌ DON'T

- **Don't pass RepoRequest** directly to templates (coupling)
- **Don't add business logic** to TemplateContext (it's a data container)
- **Don't skip the context** - always use it for consistency

## Examples

### Library Project (No Delivery)
```python
context = TemplateContext(
    project_type="library",
    repo_name="my-library",
    stack="maven",
    environments=None,
    delivery_url=None
)
```

### Standalone Microservice (No Separate Delivery)
```python
context = TemplateContext(
    project_type="standalone-microservice",
    repo_name="my-service",
    stack="python",
    environments=["a", "b"],  # Deployment servers
    delivery_url=None
)
```

### Microservice with Delivery Repo
```python
context = TemplateContext(
    project_type="microservice",
    repo_name="my-service",
    stack="node",
    environments=["a"],
    delivery_url="https://gitlab.com/group/my-service-delivery.git"  # ← Key difference!
)
```

### Delivery Project
```python
context = TemplateContext(
    project_type="delivery",
    repo_name="my-service",
    stack=None,  # Delivery repos don't have stacks
    environments=["a", "b", "c"],
    delivery_url=None
)
```

## Troubleshooting

### Template variable not appearing?

1. **Check TemplateContext creation** - is the variable set?
2. **Check template_processor** - is it passed to `template_vars`?
3. **Check template syntax** - use `{% variable_name %}` not `{{ variable_name }}`

### Import errors in IDE?

The Pylance warnings like `Import "app.schemas.template_models" could not be resolved` are false positives. The imports work correctly at runtime.

### Delivery URL is empty?

Make sure you're creating the delivery repo **before** the microservice repo:
```python
# ✅ Correct order
delivery_data = await create_delivery_part(...)
microservice_data = await create_microservice_part(..., delivery_url)

# ❌ Wrong order - delivery_url won't exist yet!
microservice_data = await create_microservice_part(...)
delivery_data = await create_delivery_part(...)
```

## Related Files

- `app/schemas/template_models.py` - TemplateContext definition
- `app/services/template/template_processor.py` - Uses TemplateContext
- `app/services/project/microservice_repository_manager.py` - Builds TemplateContext
- `app/services/project/single_project_creator.py` - Builds TemplateContext
- `app/services/project/microservice_creator.py` - Orchestrates delivery-first creation

## Summary

The `TemplateContext` pattern provides:

✅ **Clean interfaces** - no parameter explosion
✅ **Type safety** - dataclass with clear types
✅ **Extensibility** - easy to add new variables
✅ **Decoupling** - separates API layer from template layer
✅ **Documentation** - self-documenting with docstrings

Use it whenever you need to pass variables to template rendering!
