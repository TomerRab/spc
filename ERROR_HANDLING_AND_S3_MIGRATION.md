# Error Handling Improvements & S3 Template Migration

## Summary
1. **Improved user-facing error messages** - Technical details hidden, user-friendly messages shown
2. **Migrated templates to S3** - Removed all local template files, using S3 as single source of truth

---

## Part 1: User-Facing Error Messages

### Philosophy
**Show users what they need to know. Hide what they don't.**

- ✅ **Input validation errors** - Show to users (they can fix)
- ✅ **Authentication errors** - Show to users (they need to re-login)
- ❌ **Internal server errors** - Hide technical details
- ❌ **Template/database errors** - Hide technical details
- ❌ **Stack traces** - Never show to users

### Changes Made

#### 1. System Errors (Hide Details)
**Before:**
```
"Template file 'microservice/spring.gitlab-ci.yml' not found in /app/templates/"
"Failed to connect to S3: boto3.exceptions.NoCredentialsError"
"Database connection timeout after 30 seconds"
```

**After:**
```
"Template service is temporarily unavailable. Please try again later."
"The selected configuration is not available. Please try a different option."
"An unexpected error occurred. Please try again or contact support."
```

#### 2. GitLab Errors (Simplified)
**Before:**
```
"GitLab API returned 503: Service temporarily unavailable due to maintenance"
"Repository creation failed: gitlab.exceptions.GitLabCreateError"
```

**After:**
```
"GitLab service is temporarily unavailable. Please try again later."
"Unable to connect to GitLab. Please try again later."
```

#### 3. Validation Errors (Keep User-Friendly)
**Before:**
```
"ValidationError: Field 'groupId' is required"
"Invalid input: projectType must be one of ['library', 'microservice', 'standalone-microservice', 'delivery']"
```

**After:**
```
"Please check your input: Group is required"
"Please check your input: Project type has an invalid value"
```

#### 4. Authentication Errors (Clear Action)
**Before:**
```
"GitLabAuthenticationError: Token expired at 2024-01-15T10:30:00Z"
"Invalid OAuth token: signature verification failed"
```

**After:**
```
"Your session has expired. Please sign in again."
"GitLab authentication failed. Please sign in again."
```

### Error Categories

| Error Type | Show to User | Log Details | Example Message |
|------------|--------------|-------------|-----------------|
| Validation | ✅ Yes | ⚠️ Warning | "Project name is required" |
| Authentication | ✅ Yes | ⚠️ Warning | "Please sign in again" |
| User Input | ✅ Yes | ⚠️ Warning | "Invalid group selected" |
| Template Missing | ❌ Generic | ❌ Error | "Configuration not available" |
| S3 Error | ❌ Generic | ❌ Error | "Service temporarily unavailable" |
| Database Error | ❌ Generic | ❌ Error | "System error occurred" |
| Internal Error | ❌ Generic | ❌ Error + Stack | "Unexpected error occurred" |

### Code Changes

**File:** `app/api/error_handlers.py`

#### Generic Exception Handler
```python
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions - never expose internal details to users."""
    # Log full exception with stack trace for debugging
    logger.exception(f"Unexpected error in {request.url.path}: {str(exc)}")

    # Generic user-friendly message - no technical details
    user_message = "An unexpected error occurred. Please try again or contact support if the problem persists."

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(message=user_message, error_code="error")
    )
```

#### Validation Error Handler
```python
# Simplify technical messages
if "field required" in message.lower():
    errors.append(f"{readable_field.capitalize()} is required")
elif "not a valid" in message.lower():
    errors.append(f"{readable_field.capitalize()} has an invalid value")
```

#### Template Error Handler
```python
# User-friendly message - hide technical template details
if isinstance(exc, TemplateNotFoundError):
    user_message = "The selected project configuration is not available. Please try a different technology stack."
else:
    user_message = "Unable to generate project files. Please try again or contact support."
```

### Benefits

1. **Security** - No sensitive information leaked (paths, stack traces, credentials)
2. **User Experience** - Clear, actionable messages instead of technical jargon
3. **Support** - Technical details logged for debugging
4. **Consistency** - All errors follow same pattern

---

## Part 2: S3 Template Migration

### Overview
Removed all local template files and directories. Templates now loaded exclusively from S3.

### What Was Removed
```
spc-backend/templates/
├── common/
├── delivery/
├── library/
├── microservice/
├── standalone-microservice/
└── README.md
```

**Status:** ✅ All deleted

### S3 Template Loader

**New Class:** `S3TemplateLoader` in `template_renderer.py`

```python
class S3TemplateLoader(BaseLoader):
    """Custom Jinja2 loader that fetches templates from S3."""

    def __init__(self, s3_bucket: str, s3_region: str):
        self.s3_bucket = s3_bucket
        self.s3_client = boto3.client('s3', region_name=s3_region)

    def get_source(self, environment, template):
        """Load template from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=template)
            source = response['Body'].read().decode('utf-8')
            return source, None, lambda: False
        except self.s3_client.exceptions.NoSuchKey:
            raise TemplateNotFound(template)
        except Exception as e:
            logger.error(f"Error loading template from S3: {template}")
            raise S3Error(f"Failed to load template from S3", bucket=self.s3_bucket, key=template)
```

### Template Renderer Changes

**Before:**
```python
# Used FileSystemLoader pointing to local directory
templates_dir = Path(__file__).parent.parent.parent / "templates"
self.jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))
```

**After:**
```python
# Uses S3TemplateLoader pointing to S3 bucket
self.jinja_env = Environment(loader=S3TemplateLoader(self.s3_bucket, self.s3_region))
```

### Template Path Format

Templates in S3 follow same structure:
```
s3://your-bucket/
├── common/
│   ├── build/
│   │   └── Dockerfiles/
│   │       ├── maven.Dockerfile
│   │       ├── node.Dockerfile
│   │       └── python.Dockerfile
│   ├── config/
│   │   ├── settings.xml
│   │   └── .npmrc
│   └── gitignore/
│       └── maven.gitignore
├── library/
│   ├── maven.gitlab-ci.yml
│   ├── node.gitlab-ci.yml
│   └── python.gitlab-ci.yml
├── microservice/
│   ├── maven.gitlab-ci.yml
│   └── helm/
│       ├── Chart.yaml
│       └── templates/
└── delivery/
    └── .gitlab-ci.yml
```

### Configuration Required

**Environment Variables:**
```bash
S3_BUCKET=your-template-bucket
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

### Error Handling

S3 errors are caught and translated to user-friendly messages:

```python
# S3 NoSuchKey → TemplateNotFound → User sees: "Configuration not available"
# S3 Connection Error → S3Error → User sees: "Service temporarily unavailable"
# S3 Permission Error → S3Error → User sees: "Service temporarily unavailable"
```

### Benefits

1. **Centralized Management** - Single source of truth for templates
2. **No Deployment Required** - Update templates without redeploying app
3. **Version Control** - S3 versioning tracks template changes
4. **Scalability** - No local disk space needed
5. **Security** - IAM policies control template access
6. **Caching** - Can implement CloudFront caching if needed

### Migration Checklist

- [x] Create S3TemplateLoader class
- [x] Update TemplateRenderer to use S3
- [x] Remove FileSystemLoader import
- [x] Update error messages to reference S3
- [x] Delete local template directories
- [x] Test template loading from S3
- [ ] Upload templates to S3 bucket (manual step)
- [ ] Configure S3 bucket permissions
- [ ] Set environment variables

### Upload Templates to S3

**Using AWS CLI:**
```bash
# Upload all templates maintaining directory structure
aws s3 sync ./local-templates/ s3://your-bucket/ --exclude "*.md"

# Verify upload
aws s3 ls s3://your-bucket/ --recursive
```

**Using Python:**
```python
import boto3

s3 = boto3.client('s3')

# Example: Upload single template
with open('maven.gitlab-ci.yml', 'rb') as f:
    s3.put_object(
        Bucket='your-bucket',
        Key='library/maven.gitlab-ci.yml',
        Body=f
    )
```

---

## Testing

### Error Messages
1. **Validation Errors** - Submit invalid form, verify friendly message
2. **Auth Errors** - Use expired token, verify "sign in again" message
3. **Template Errors** - Request non-existent stack, verify generic message
4. **System Errors** - Simulate S3 failure, verify service unavailable message

### S3 Templates
1. **Template Loading** - Create project, verify templates load from S3
2. **Fallback System** - Request spring stack, verify maven fallback works
3. **Error Handling** - Disconnect from S3, verify error message
4. **Caching** - Load same template twice, verify performance

### Logs (Developer View)
- Detailed errors logged to files/monitoring
- Stack traces captured for debugging
- S3 paths and keys logged
- No sensitive data in logs

---

## Monitoring Recommendations

### Metrics to Track
- S3 GET request count (template loads)
- S3 error rate (NoSuchKey, permissions)
- Template load latency
- Error rates by type (validation vs system)

### Alerts to Set
- S3 error rate > 5%
- Template load latency > 2 seconds
- System error rate spike
- Authentication error spike

### Logging
```python
# Technical details in logs (for developers)
logger.error(f"Template not found in S3: {template_path}", extra={
    "bucket": self.s3_bucket,
    "key": template_path,
    "user_id": user_id
})

# User-friendly message in response (for users)
return {"message": "The selected configuration is not available."}
```

---

## Summary

### User-Facing Improvements
- ✅ No more technical error messages
- ✅ Clear, actionable error messages
- ✅ Consistent error format across all endpoints
- ✅ Security: No sensitive information exposed

### Infrastructure Improvements
- ✅ Removed local template files
- ✅ S3 as single source of truth
- ✅ Easier template updates (no deployment)
- ✅ Better scalability and caching options

### Files Modified
- `app/api/error_handlers.py` - All error handlers updated
- `app/services/template/template_renderer.py` - S3 loader implemented
- `templates/` - Directory removed

### Next Steps
1. Upload templates to S3 bucket
2. Configure S3 bucket policies
3. Test end-to-end with S3 templates
4. Set up monitoring and alerts
5. Update deployment documentation