# GitLab Project Creator - Test Suite

This directory contains comprehensive tests for the GitLab Project Creator backend services.

## 🧪 Test Coverage

### Core Services
- **Stack Configuration Manager** (`test_stack_config_manager.py`)
  - Stack-to-config file mappings
  - Fallback template resolution
  - Docker and Helm requirements logic

- **Template Renderer** (`test_template_renderer.py`)
  - Jinja2 template processing
  - Error handling and fallbacks
  - Static vs dynamic template rendering

- **Variable Manager** (`test_variable_manager.py`)
  - Cluster variable creation
  - Environment-specific variables
  - OpenShift deployment variables

### GitLab API Services
- **Groups Service** (`test_gitlab_groups_service.py`)
  - Group fetching and search
  - Pagination handling
  - Authentication and error handling

- **Repository Service** (`test_gitlab_repository_service.py`)
  - Repository creation and deletion
  - File addition via commits
  - Permission and validation errors

- **Variables Service** (`test_gitlab_variables_service.py`)
  - Project variable management
  - Environment-scoped variables
  - Variable updates and conflicts

### High-Level Services
- **Project Creator** (`test_project_creator.py`)
  - Project type routing
  - Error handling and validation
  - Microservice vs single project logic

### Infrastructure
- **Cache** (`test_cache.py`)
  - TTL-based caching
  - Token security (hashing)
  - Expiration and cleanup

### API Routes
- **Main Routes** (`test_routes.py`)
  - Health check endpoint
  - Legacy endpoint redirects

- **Authentication Routes** (`test_auth_routes.py`)
  - OAuth flow handling
  - Token exchange
  - Error scenarios

## 🚀 Running Tests

### Prerequisites
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
# Using pytest directly
pytest

# Using the test runner
python run_tests.py

# With verbose output
pytest -v
```

### Run Specific Tests
```bash
# Single test file
pytest tests/test_stack_config_manager.py

# Single test class
pytest tests/test_cache.py::TestGroupsCache

# Single test method
pytest tests/test_cache.py::TestGroupsCache::test_set_and_get
```

### Coverage Reports
```bash
# Terminal coverage
pytest --cov=app --cov-report=term-missing

# HTML coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Categories
```bash
# Run only unit tests (when marked)
pytest -m unit

# Skip slow tests
pytest -m "not slow"
```

## 📝 Test Structure

### Unit Tests
- Mock all external dependencies (HTTP clients, file system)
- Test individual functions and methods in isolation
- Focus on business logic and error handling

### Integration Tests
- Test route handlers with FastAPI TestClient
- Mock only external services (GitLab API)
- Test request/response flows

### Test Patterns

#### Async Testing
```python
@pytest.mark.asyncio
async def test_async_method(self):
    result = await service.async_method()
    assert result == expected
```

#### Mocking HTTP Clients
```python
@patch('httpx.AsyncClient')
async def test_api_call(self, mock_client_class):
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client_class.return_value.__aenter__.return_value = mock_client
```

#### Exception Testing
```python
with pytest.raises(HTTPException) as exc_info:
    await service.failing_method()
assert exc_info.value.status_code == 400
```

## 🎯 Test Quality Standards

- **Coverage Target**: 80% minimum
- **Test Naming**: Descriptive method names explaining the scenario
- **Isolation**: Each test should be independent
- **Speed**: Unit tests should run quickly
- **Reliability**: Tests should not be flaky
- **Maintainability**: Tests should be easy to understand and update

## 🔧 CI/CD Integration

The test suite is configured for continuous integration with:
- Automatic test discovery
- Coverage reporting
- Fail-fast on low coverage
- Parallel test execution support

## 📊 Current Metrics

- **Test Files**: 9
- **Total Tests**: ~70+ test methods
- **Services Covered**: All major backend services
- **Routes Covered**: Core API endpoints
- **Target Coverage**: 80%+