# mono-merger

## Overview
A **production-ready Python application** that consolidates multiple GitHub repositories into a single monorepo based on YAML configuration. This enterprise-grade tool features:

- **Async Git operations** for efficient repository processing
- **Batch processing** with concurrent operations for scalability  
- **Comprehensive logging** for operational monitoring
- **Robust error handling** with timeout management
- **Complete testing framework** for reliability

The application takes a YAML configuration file that specifies:
- Which repositories to merge
- How repositories should be organized by domain
- Which branches from each repository to include
- Target directory structure for the consolidated monorepo

## Requirements
- **Python >= 3.13**
- **Git** (for repository operations)  
- **Access** to configured repositories (SSH keys or credentials as needed)

## Configuration

### Sample YAML Configuration
```yaml
repos:
  - url: "https://github.com/org/repo1"
    branches:
      - name: "main"
        domain: "user-management"
      - name: "payment-service"
        domain: "payment"
        
  - url: "https://github.com/org/repo2"
    branches:
      - name: "analytics-branch"
        domain: "analytics"

domain_mapping:
  user-management: "domains/user-management"
  payment: "domains/payment"
  analytics: "domains/analytics"

output_dir: "/path/to/output/monorepo"
```

### Configuration Fields
- **`repos`**: List of repositories to process
  - **`url`**: Repository URL (HTTPS or SSH)
  - **`branches`**: List of branches to include
    - **`name`**: Branch name
    - **`domain`**: Domain/category for organization
- **`domain_mapping`**: Maps domains to directory paths in output
- **`output_dir`**: Target directory for consolidated monorepo

## Usage

### Basic Usage
```bash
# Run mono-merger with configuration file
python -m mono_merger.main --config repos.yaml
```

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd mono-merger

# Install dependencies
uv sync --all-groups
```

## Development

### Installation for Development
```bash
# Install all dependencies including development tools
uv sync --all-groups
```

### Running Tests
```bash
# Run all tests
uv run --group test pytest

# Run with coverage report
uv run --group test pytest --cov=mono_merger --cov-report=term-missing

# Run only unit tests
uv run --group test pytest tests/unit/

# Run specific test file
uv run --group test pytest tests/unit/test_config.py

# Run with verbose output
uv run --group test pytest -v

# Generate HTML coverage report
uv run --group test pytest --cov=mono_merger --cov-report=html:coverage_html
```

### Code Quality

#### Formatting
```bash
# Format code with black
uv run --group dev black mono_merger/ tests/

# Check formatting without making changes
uv run --group dev black --check mono_merger/ tests/
```

#### Linting
```bash
# Lint main package
uv run --group dev pylint mono_merger/

# Lint tests
uv run --group dev pylint tests/

# Lint specific file
uv run --group dev pylint mono_merger/config.py
```

### Development Workflow
```bash
# Full quality check workflow
uv run --group dev black mono_merger/ tests/
uv run --group dev pylint mono_merger/
uv run --group test pytest --cov=mono_merger --cov-report=term-missing

# Quick development check
uv run --group dev black mono_merger/ tests/ && uv run --group test pytest
```

### Project Structure
```
mono-merger/
├── mono_merger/           # Main package
│   ├── __init__.py
│   ├── main.py           # Application entry point
│   ├── config.py         # Configuration and logging setup
│   ├── async_git.py      # Async Git operations
│   └── merge_repos.py    # Repository merging logic
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   └── conftest.py      # Shared test fixtures
├── logs/                # Application logs (auto-created)
├── pyproject.toml       # Project dependencies and metadata
├── pytest.ini          # Test configuration
├── .pylintrc           # Linting configuration
└── repos.yaml          # Sample configuration file
```
