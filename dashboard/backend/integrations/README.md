# Integration Hub

The Integration Hub provides pluggable integrations with external test management systems. It follows the adapter pattern to ensure consistent interfaces across different providers.

## Supported Providers

### 1. Jira (Atlassian)
- **Type**: Issue tracking and project management
- **Cost**: FREE tier up to 10 users
- **Features**: 
  - Create bugs from failed tests
  - Sync test results as issues
  - Link test cases to stories/epics
- **Authentication**: Email + API Token
- **API**: Jira REST API v3

### 2. Zephyr Squad
- **Type**: Test management for Jira
- **Cost**: FREE tier up to 10 users, unlimited tests
- **Features**:
  - Test case management
  - Test cycles/executions
  - Import JUnit XML results
  - BDD support
- **Authentication**: Same as Jira (uses Jira credentials)
- **API**: Zephyr Squad API

### 3. HP ALM / OpenText ALM
- **Type**: Enterprise test management
- **Cost**: PAID ($500-2000 USD/user/year)
- **Features**:
  - Test plan management
  - Test lab / executions
  - Defects management
  - Requirements traceability
- **Authentication**: Username + Password
- **API**: ALM REST API (XML)

### 4. TestLink
- **Type**: Open source test management
- **Cost**: FREE and open source
- **Features**:
  - Test case management
  - Test execution tracking
  - Requirements traceability
- **Authentication**: API Key
- **API**: XML-RPC API

### 5. Azure DevOps
- **Type**: Microsoft DevOps platform
- **Cost**: FREE tier up to 5 users
- **Features**:
  - Work items (stories, tasks, bugs)
  - Test plans and test suites
  - CI/CD integration
- **Authentication**: Personal Access Token
- **API**: Azure DevOps REST API

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  QA-FRAMEWORK DASHBOARD                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   JIRA API      │  │   ZEPHYR API    │  │   ALM API    │ │
│  │   Integration   │  │   Integration   │  │  Integration │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  TESTLINK API   │  │ AZURE DEVOPS    │  │   CUSTOM     │ │
│  │   Integration   │  │   Integration   │  │  Integration │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
               ┌─────────────────────────┐
               │   INTEGRATION MANAGER   │
               │  (Orchestrates all)     │
               └─────────────────────────┘
```

## Base Interface

All integrations implement the `IntegrationBase` abstract class:

```python
class IntegrationBase(ABC):
    # Connection methods
    async def connect(self) -> bool
    async def disconnect(self) -> bool
    async def health_check(self) -> Dict[str, Any]
    
    # Synchronization methods
    async def sync_test_results(self, results: List[TestResult], ...) -> SyncResult
    
    # Test case methods
    async def create_test_case(self, ...)
    async def get_test_cases(self, ...)
    
    # Bug methods
    async def create_bug(self, ...)
    async def get_bugs(self, ...)
    
    # Validation
    def validate_config(self) -> Tuple[bool, List[str]]
    def get_config_schema(self) -> Dict[str, Any]
```

## Usage

### Via API

```bash
# Get available providers
GET /api/v1/integrations/providers

# Configure a provider
POST /api/v1/integrations/configure
{
  "provider": "jira",
  "config": {
    "base_url": "https://yourcompany.atlassian.net",
    "email": "qa@yourcompany.com",
    "api_token": "your_api_token"
  }
}

# Sync test results
POST /api/v1/integrations/sync
{
  "results": [...],
  "providers": ["jira", "zephyr"],
  "project_key": "QA"
}
```

### Via Python

```python
from integrations.manager import integration_manager

# Register and configure
integration_manager.register_integration("jira", config_dict)

# Sync results
await integration_manager.sync_test_results(results, providers=["jira"])

# Get health
await integration_manager.health_check("jira")
```

## Configuration Schemas

Each provider exposes a JSON schema for UI configuration:

```json
{
  "type": "object",
  "title": "Jira Configuration",
  "properties": {
    "base_url": {
      "type": "string",
      "title": "Jira URL",
      "format": "uri"
    },
    "email": {
      "type": "string",
      "title": "Email",
      "format": "email"
    },
    "api_token": {
      "type": "string",
      "title": "API Token",
      "secret": true
    }
  },
  "required": ["base_url", "email", "api_token"]
}
```