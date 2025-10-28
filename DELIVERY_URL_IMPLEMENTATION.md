# Delivery URL Implementation - Summary

## Changes Implemented ✅

This document summarizes the changes made to inject the delivery repository URL into microservice CI templates.

## What Was Changed

### 1. **Created TemplateContext Pattern** (`app/schemas/template_models.py`)

Introduced a clean, extensible data class to replace parameter explosion:

```python
@dataclass
class TemplateContext:
    project_type: str
    repo_name: str
    stack: Optional[str] = None
    environments: Optional[List[str]] = None
    delivery_url: Optional[str] = None  # ← NEW: Delivery repo URL
```

**Why?** Avoids adding endless parameters to functions. Clean, type-safe, and extensible.

---

### 2. **Updated Template Processor** (`app/services/template/template_processor.py`)

- Changed signature: `get_project_files(context: TemplateContext)` instead of multiple parameters
- Added logic to inject `delivery_url` into CI template variables:

```python
# Add delivery_url if present (for microservices with separate delivery repos)
if context.delivery_url:
    template_vars["delivery_url"] = context.delivery_url
    logger.info(f"Injecting delivery_url into CI template: {context.delivery_url}")
```

---

### 3. **Updated Repository Manager** (`app/services/project/microservice_repository_manager.py`)

- Added `delivery_url` parameter to `create_microservice_repository()`
- Builds `TemplateContext` with delivery URL:

```python
context = TemplateContext(
    project_type=project_type,
    repo_name=repo_request.sanitized_name,
    stack=repo_request.stack,
    environments=environments,
    delivery_url=delivery_url  # ← Injected here
)
```

---

### 4. **Reversed Creation Order** (`app/services/project/microservice_creator.py`) ⚠️ CRITICAL

**Before**: Microservice → Delivery (delivery URL not available)
**After**: Delivery → Microservice (delivery URL available)

```python
# STEP 1: Create delivery repo first to obtain its URL
delivery_data = await self._create_delivery_part(token, repo_request, created_repos)
delivery_url = delivery_data[0]  # Extract URL from tuple (url, id, files)
logger.info(f"Delivery repo created at: {delivery_url}")

# STEP 2: Create microservice repo with delivery URL injected into templates
microservice_data = await self._create_microservice_part(
    token, repo_request, created_repos, delivery_url
)
```

---

### 5. **Updated Single Project Creator** (`app/services/project/single_project_creator.py`)

Updated to use `TemplateContext` for consistency across all project types.

---

### 6. **Created Documentation** (`TEMPLATE_CONTEXT_USAGE.md`)

Comprehensive guide on:
- Why TemplateContext exists
- How to use it
- How to add new template variables
- Examples and best practices

---

## How to Use in S3 Templates

### In Your Microservice CI Template

**File**: `templates/project-types/microservice/{stack}.gitlab-ci.yml.j2`

You can now use `{% delivery_url %}` in your templates:

```yaml
stages:
  - build
  - test
  - deploy

variables:
  PROJECT_NAME: {% repo_name %}
  STACK: {% stack %}

  # NEW: Delivery repository URL
  DELIVERY_REPO: {% delivery_url %}

build:
  stage: build
  script:
    - echo "Building {% repo_name %}"
    - # Your build commands

deploy:
  stage: deploy
  script:
    - echo "Deploying to {% delivery_url %}"
    - git clone {% delivery_url %}
    - cd $(basename {% delivery_url %} .git)
    - # Use delivery repo Helm charts for deployment
  only:
    - main

# Or trigger the delivery pipeline
trigger_delivery:
  stage: deploy
  trigger:
    project: {% delivery_url %}
    branch: main
  only:
    - main
```

### Available Template Variables

When rendering microservice templates, these variables are available:

| Variable | Description | Example |
|----------|-------------|---------|
| `{% repo_name %}` | Sanitized repository name | `my-awesome-service` |
| `{% stack %}` | Technology stack | `python`, `maven`, `node` |
| `{% delivery_url %}` | Delivery repository URL (if separate delivery) | `https://gitlab.com/group/my-service-delivery.git` |
| `{% project_type %}` | Type of project | `microservice`, `library` |

---

## Examples

### Example 1: Simple Git Clone

```yaml
deploy:
  stage: deploy
  script:
    - git clone {% delivery_url %}
    - cd $(basename {% delivery_url %} .git)
    - helm upgrade --install my-app ./helm
```

### Example 2: Trigger Delivery Pipeline

```yaml
trigger_delivery_pipeline:
  stage: deploy
  trigger:
    project: {% delivery_url %}
    strategy: depend
  only:
    - main
```

### Example 3: Dynamic Configuration

```yaml
variables:
  DELIVERY_REPO: {% delivery_url %}

deploy:
  script:
    - |
      if [ -n "$DELIVERY_REPO" ]; then
        echo "Deploying using delivery repo: $DELIVERY_REPO"
        git clone $DELIVERY_REPO
      else
        echo "No delivery repo configured"
      fi
```

---

## When Is delivery_url Available?

| Project Type | Has delivery_url? | Notes |
|--------------|-------------------|-------|
| **Microservice with delivery** | ✅ Yes | Separate delivery repo created first |
| **Standalone microservice** | ❌ No | Deployment configs in same repo |
| **Library** | ❌ No | No deployment |
| **Delivery** | ❌ No | This IS the delivery repo |

---

## Testing

To test the implementation:

1. **Create a microservice with delivery repo** via the SPC UI
2. **Check the generated `.gitlab-ci.yml`** in the microservice repo
3. **Verify** that `{% delivery_url %}` has been replaced with the actual URL
4. **Inspect logs** - you should see: `Injecting delivery_url into CI template: https://...`

### Expected Log Output

```
INFO - Generating delivery template files...
INFO - Creating delivery repository...
INFO - Delivery repo created at: https://gitlab.com/group/my-service-delivery.git
INFO - Generating microservice template files...
INFO - Injecting delivery_url into CI template: https://gitlab.com/group/my-service-delivery.git
INFO - Creating microservice repository...
```

---

## Rollback Safety

The implementation maintains rollback safety:

- If delivery repo creation **fails** → nothing is created
- If microservice repo creation **fails** → delivery repo is deleted
- If variable creation **fails** → both repos are kept (variables can be added manually)

---

## Migration Notes

### Existing Templates

If you have existing S3 templates:

1. **Update microservice CI templates** to use `{% delivery_url %}`
2. **Test with a new project** to verify the URL is injected
3. **No changes needed** for library or standalone microservice templates

### Backward Compatibility

✅ **Fully backward compatible** - if `delivery_url` is not set, it renders as empty string:

```python
"delivery_url": context.delivery_url or "",  # Defaults to ""
```

So existing templates without `{% delivery_url %}` will continue to work.

---

## Architecture Benefits

### Before
```
TemplateProcessor.get_project_files(
    project_type, repo_name, stack, environments  # Parameter explosion
)
```

### After
```
TemplateProcessor.get_project_files(
    context: TemplateContext  # Clean interface
)
```

**Benefits**:
- ✅ Easy to add new variables
- ✅ Type-safe with dataclass
- ✅ Self-documenting
- ✅ No parameter explosion
- ✅ Consistent across all project types

---

## Files Changed

1. ✅ `app/schemas/template_models.py` - NEW: TemplateContext dataclass
2. ✅ `app/services/template/template_processor.py` - Uses TemplateContext
3. ✅ `app/services/project/microservice_repository_manager.py` - Builds TemplateContext with delivery_url
4. ✅ `app/services/project/microservice_creator.py` - Reversed creation order
5. ✅ `app/services/project/single_project_creator.py` - Uses TemplateContext
6. ✅ `TEMPLATE_CONTEXT_USAGE.md` - NEW: Documentation
7. ✅ `DELIVERY_URL_IMPLEMENTATION.md` - NEW: This file

---

## Next Steps

### Required: Update S3 Templates

You need to update your microservice CI templates in S3 to use the new variable:

**Files to update**:
- `templates/project-types/microservice/python.gitlab-ci.yml.j2`
- `templates/project-types/microservice/maven.gitlab-ci.yml.j2`
- `templates/project-types/microservice/node.gitlab-ci.yml.j2`
- `templates/project-types/microservice/dotnet.gitlab-ci.yml.j2`

**Add this variable** where needed:
```yaml
variables:
  DELIVERY_REPO: {% delivery_url %}
```

### Optional: Update README

Consider updating the main README.md to mention:
- The new `delivery_url` template variable
- How to use it in CI templates
- Link to `TEMPLATE_CONTEXT_USAGE.md` for developers

---

## Questions?

See `TEMPLATE_CONTEXT_USAGE.md` for detailed usage guide and examples.

---

**Implementation Date**: 2025-01-28
**Author**: Claude Code
**Status**: ✅ Complete and Ready for Use
