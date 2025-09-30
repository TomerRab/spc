# Timeouts and Hardcoded Values Fixed

## Summary
Fixed request timeouts and removed hardcoded values across the entire codebase (frontend and backend).

---

## ✅ Part 1: Request Timeouts Added

### Frontend Timeouts (TypeScript)

**File:** `spc-client/src/lib/api.ts`

**Added timeout configuration:**
```typescript
const TIMEOUTS = {
  DEFAULT: 30000,      // 30 seconds for normal operations
  PROJECT_CREATE: 120000, // 2 minutes for project creation (long operation)
  GROUP_SEARCH: 15000   // 15 seconds for group search
};
```

**Created `fetchWithTimeout` function:**
```typescript
const fetchWithTimeout = async (url: string, options: RequestInit, timeout: number): Promise<Response> => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw parseAPIError({
        message: 'Request timeout. The operation took too long to complete. Please try again.',
        status_code: 408
      });
    }
    throw error;
  }
};
```

**Updated all API calls:**
- `getLoginUrl()` → 30s timeout
- `getGroups()` → 30s timeout
- `searchGroups()` → 15s timeout
- `createProject()` → 120s timeout (longest operation)

**Benefits:**
- ✅ Users get clear timeout errors instead of infinite hangs
- ✅ Different timeouts for different operations
- ✅ Proper cleanup with AbortController

---

### Backend Timeouts (Python)

**File:** `spc-backend/app/core/config.py`

**Added timeout configuration:**
```python
# HTTP timeout configuration (in seconds)
http_timeout_default: float = 30.0
http_timeout_gitlab: float = 45.0
http_timeout_s3: float = 60.0
```

**Updated services:**

1. **GitLabRepositoryService** (`gitlab_repository_service.py`)
   ```python
   def __init__(self):
       self.timeout = settings.http_timeout_gitlab  # Was: 30.0
   ```

2. **GitLabVariablesService** (`gitlab_variables_service.py`)
   ```python
   def __init__(self):
       self.timeout = settings.http_timeout_gitlab  # Was: 30.0
   ```

3. **GitLabGroupsService** (`gitlab_groups_service.py`)
   ```python
   def __init__(self, base_url: str, timeout: float = 30.0):
       # Called with: settings.http_timeout_gitlab
   ```

**Benefits:**
- ✅ Configurable timeouts via environment variables
- ✅ Consistent timeout behavior across all GitLab operations
- ✅ Prevents hanging connections

---

## ✅ Part 2: Hardcoded Values Removed

### Backend Configuration

**File:** `spc-backend/app/core/config.py`

**Added configuration options:**

#### 1. Git/Commit Configuration
```python
# Default branch configuration
default_branch: str = "main"
commit_message: str = "Initial project setup"
```

**Was hardcoded in:** `gitlab_repository_service.py:120-121`
```python
# Before
"branch": "main",  # ❌ Hardcoded
"commit_message": "Initial project setup",  # ❌ Hardcoded

# After
"branch": branch or settings.default_branch,
"commit_message": settings.commit_message,
```

#### 2. Cache Configuration
```python
# Cache configuration (in seconds)
cache_ttl_groups: int = 900      # 15 minutes
cache_ttl_projects: int = 300    # 5 minutes
cache_ttl_templates: int = 3600  # 1 hour
cache_max_size_groups: int = 500
cache_max_size_projects: int = 100
cache_max_size_templates: int = 50
```

**Was hardcoded in:** `core/cache.py:152-154`
```python
# Before
'groups': LRUCache(max_size=500, default_ttl=900),  # ❌ Hardcoded

# After
'groups': LRUCache(
    max_size=settings.cache_max_size_groups,
    default_ttl=settings.cache_ttl_groups
),
```

---

### Branch Name Now Respects User Input

**Problem:** User's `defaultBranch` setting was ignored, always used "main"

**Fixed in:**
1. `gitlab_repository_service.py` - Accept `branch` parameter
2. `gitlab_service.py` - Pass `branch` through
3. `single_project_creator.py` - Pass `repo_request.defaultBranch`
4. `microservice_repository_manager.py` - Pass `repo_request.defaultBranch`

**Flow:**
```
User selects "master" as default branch
    ↓
RepoRequest.defaultBranch = "master"
    ↓
single_project_creator passes to gitlab_service.add_files(branch="master")
    ↓
Files committed to "master" branch ✅
```

---

### Template Processor S3 Config Fixed

**Problem:** Constructor accepted S3 config but didn't pass it to TemplateRenderer

**File:** `template_processor.py:16`

```python
# Before
def __init__(self, s3_bucket: Optional[str] = None, s3_region: Optional[str] = None):
    self.renderer = TemplateRenderer()  # ❌ Not passing config!

# After
def __init__(self, s3_bucket: Optional[str] = None, s3_region: Optional[str] = None):
    self.renderer = TemplateRenderer(s3_bucket=s3_bucket, s3_region=s3_region)  # ✅
```

---

### Frontend Debounce Timeout

**File:** `spc-client/src/hooks/useGroupSearch.ts`

```typescript
// Before
}, 300),  // ❌ Hardcoded debounce

// After
const DEBOUNCE_MS = config.SEARCH_DEBOUNCE_MS;
}, DEBOUNCE_MS),  // ✅ Uses config
```

**Config already existed in:** `config/env.ts:16`
```typescript
SEARCH_DEBOUNCE_MS: parseInt(import.meta.env.VITE_SEARCH_DEBOUNCE_MS || '300'),
```

---

## Environment Variables Added

### Backend (.env)

```bash
# Timeout configuration (optional - has defaults)
HTTP_TIMEOUT_DEFAULT=30.0
HTTP_TIMEOUT_GITLAB=45.0
HTTP_TIMEOUT_S3=60.0

# Git configuration (optional - has defaults)
DEFAULT_BRANCH=main
COMMIT_MESSAGE=Initial project setup

# Cache configuration (optional - has defaults)
CACHE_TTL_GROUPS=900
CACHE_TTL_PROJECTS=300
CACHE_TTL_TEMPLATES=3600
CACHE_MAX_SIZE_GROUPS=500
CACHE_MAX_SIZE_PROJECTS=100
CACHE_MAX_SIZE_TEMPLATES=50
```

### Frontend (.env)

```bash
# Already exists - now actually used
VITE_SEARCH_DEBOUNCE_MS=300
```

---

## Files Modified

### Backend (9 files)
1. `app/core/config.py` - Added timeout and config settings
2. `app/core/cache.py` - Use config for cache settings
3. `app/services/gitlab/gitlab_repository_service.py` - Configurable timeout, branch parameter
4. `app/services/gitlab/gitlab_variables_service.py` - Configurable timeout
5. `app/services/gitlab/gitlab_service.py` - Pass branch parameter
6. `app/services/project/single_project_creator.py` - Pass branch to add_files
7. `app/services/project/microservice_repository_manager.py` - Pass branch to add_files
8. `app/services/template/template_processor.py` - Pass S3 config to renderer
9. `app/api/routes.py` (indirect) - Benefits from timeout config

### Frontend (2 files)
1. `src/lib/api.ts` - Added timeout configuration and fetchWithTimeout
2. `src/hooks/useGroupSearch.ts` - Use config for debounce

---

## Testing

### Timeout Testing

**Frontend:**
```bash
# Simulate slow backend (add delay to backend route)
# Verify timeout triggers after configured time
# Check user sees: "Request timeout. The operation took too long..."
```

**Backend:**
```bash
# Test with slow GitLab API
# Verify httpx.TimeoutException caught
# Check proper error returned to client
```

### Hardcoded Values Testing

**Branch names:**
```bash
# Create project with branch "develop"
curl -X POST /projects/generate-repo -d '{"defaultBranch": "develop", ...}'
# Verify files committed to "develop" branch, not "main"
```

**Cache configuration:**
```bash
# Set CACHE_TTL_GROUPS=60 (1 minute)
# Search for groups
# Wait 61 seconds
# Search again - should hit GitLab API (not cache)
```

**Commit message:**
```bash
# Set COMMIT_MESSAGE="Project initialized"
# Create project
# Check GitLab commit history shows custom message
```

---

## Benefits

### Timeouts
✅ No more infinite hanging requests
✅ Clear error messages for users
✅ Different timeouts for different operations
✅ Configurable via environment variables

### Removed Hardcoded Values
✅ Flexible configuration without code changes
✅ User's branch choice now respected
✅ Cache tuning possible per environment
✅ Easier testing with different values
✅ S3 config properly passed to template renderer

---

## Migration Notes

### No Breaking Changes
- All new config options have sensible defaults
- Existing installations work without changes
- Optional environment variables

### Recommended Actions
1. Review timeout values for your environment
2. Test with your GitLab instance's response times
3. Adjust cache TTL based on usage patterns
4. Consider custom commit messages per environment

---

## Remaining Hardcoded Values (Acceptable)

Some hardcoded values remain but are **intentional**:

1. **HTTP status codes** (200, 401, 404, etc.) - Standard protocol
2. **UI animation durations** (in ms) - Design decisions
3. **Minimum search length** (3 chars) - UX decision
4. **Regex patterns** - Security/validation logic

These don't need configuration as they're either:
- Protocol standards
- Design decisions
- Security requirements

---

## Summary

| Category | Before | After |
|----------|--------|-------|
| **Frontend Timeouts** | ❌ None (infinite) | ✅ 15s-120s configured |
| **Backend Timeouts** | ⚠️ 30s hardcoded | ✅ 30-60s configurable |
| **Branch Names** | ❌ Always "main" | ✅ User's choice |
| **Cache TTL** | ⚠️ Hardcoded | ✅ Configurable |
| **Commit Message** | ⚠️ Hardcoded | ✅ Configurable |
| **Debounce Time** | ⚠️ Hardcoded | ✅ Uses config |
| **S3 Config** | ❌ Not passed | ✅ Properly passed |

All critical issues fixed! 🎉