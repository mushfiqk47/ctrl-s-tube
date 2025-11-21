# Contributing to Ctrl+S Tube

Thank you for considering contributing to Ctrl+S Tube! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Commit Message Conventions](#commit-message-conventions)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Branch Naming Conventions](#branch-naming-conventions)

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Race or ethnicity
- Age
- Religion

### Expected Behavior

- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other contributors

### Unacceptable Behavior

- Trolling, insulting, or derogatory comments
- Personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Any conduct that would be inappropriate in a professional setting

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ctrl-s-tube.git
   cd ctrl-s-tube
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/ctrl-s-tube.git
   ```

## 💻 Development Setup

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed and in PATH
- Git

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies (including dev dependencies)
pip install -r requirements.txt

# Verify installation
python -c "import PySide6; import yt_dlp; print('Setup successful!')"
```

### Install Development Tools

All development tools are included in `requirements.txt`:

- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatting
- **flake8** - Linting
- **mypy** - Type checking

## 📝 Code Style Guidelines

We follow strict code style guidelines to maintain consistency across the codebase.

### Python Code Style

We use **PEP 8** with modifications defined in our configuration files.

#### Formatting with Black

```bash
# Format all Python files
black .

# Check what would be formatted
black --check .

# Format specific file
black path/to/file.py
```

**Black Configuration** (from `pyproject.toml`):
- Line length: 100 characters
- Target Python version: 3.11

#### Linting with Flake8

```bash
# Run flake8 on entire project
flake8

# Run on specific file
flake8 path/to/file.py
```

**Flake8 Rules** (from `.flake8`):
- Max line length: 100
- Ignore: E203, W503, E501 (conflicts with Black)

#### Type Checking with MyPy

```bash
# Run type checking
mypy .

# Run on specific file
mypy path/to/file.py
```

### Code Organization

- **Import Order**: 
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
  4. Separate groups with blank lines

- **Type Hints**: Use type hints for all function signatures and class attributes

```python
def fetch_metadata(self, url: str) -> VideoMetadata:
    """Fetch metadata with proper type hints."""
    pass
```

- **Docstrings**: Use Google-style docstrings for all public functions and classes

```python
def download(url: str, output_path: str, quality: Optional[str] = None) -> str:
    """
    Download video from URL.
    
    Args:
        url: YouTube video URL
        output_path: Directory to save the file
        quality: Optional quality selection (e.g., "1080p")
        
    Returns:
        Path to downloaded file
        
    Raises:
        DownloadException: If download fails
    """
    pass
```

### Project Structure Guidelines

- **Layered Architecture**: Follow the existing layered structure
  - `core/` - Business logic, no external dependencies
  - `services/` - External API integrations
  - `ui/` - User interface code
  - `utils/` - Utility functions and helpers

- **Dependency Injection**: Use dependency injection for better testability

```python
class Controller:
    def __init__(
        self,
        metadata_service: Optional[YouTubeMetadataService] = None,
        download_service: Optional[YouTubeDownloadService] = None
    ):
        self.metadata_service = metadata_service or YouTubeMetadataService()
        self.download_service = download_service or YouTubeDownloadService()
```

## 🧪 Testing Requirements

All new features and bug fixes must include tests.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_controller.py

# Run specific test function
pytest tests/test_controller.py::TestController::test_fetch_metadata

# Run with verbose output
pytest -v
```

### Writing Tests

- **Location**: Place tests in `tests/` directory
- **Naming**: Test files should start with `test_`
- **Structure**: Use pytest fixtures for setup/teardown

```python
# tests/test_new_feature.py
import pytest
from core.controller import Controller

class TestNewFeature:
    """Tests for new feature."""
    
    def test_feature_success(self):
        """Test successful feature execution."""
        controller = Controller()
        result = controller.new_feature("input")
        assert result == "expected_output"
    
    def test_feature_error_handling(self):
        """Test error handling."""
        controller = Controller()
        with pytest.raises(ValueError):
            controller.new_feature("invalid_input")
```

### Test Coverage

- Aim for **80%+ test coverage** for new code
- Focus on testing:
  - Happy path scenarios
  - Error handling
  - Edge cases
  - Input validation

## 💬 Commit Message Conventions

We follow **Conventional Commits** for clear and meaningful commit history.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without changing functionality
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, build config, etc.)
- `perf`: Performance improvements

### Examples

```bash
# Feature
git commit -m "feat(download): add playlist download support"

# Bug fix
git commit -m "fix(ui): correct progress bar percentage calculation"

# Documentation
git commit -m "docs(readme): update installation instructions"

# Refactor
git commit -m "refactor(controller): extract validation logic to validators"

# Multiple lines
git commit -m "fix(download): handle network timeout errors

Added retry logic with exponential backoff for network requests.
Improved error messages for better user feedback.

Closes #123"
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following code style guidelines

4. **Run all checks**:
   ```bash
   # Format code
   black .
   
   # Run linter
   flake8
   
   # Run type checker
   mypy .
   
   # Run tests
   pytest
   ```

5. **Commit your changes** using conventional commits

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Creating the Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your branch from your fork
4. Fill in the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests for changes
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

5. Link any related issues (e.g., "Closes #123")

### Review Process

- Maintainers will review your PR within 3-5 business days
- Address any requested changes
- Once approved, a maintainer will merge your PR

## 🐛 Issue Reporting

### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check documentation** for solutions
3. **Verify the bug** by reproducing it

### Creating a Bug Report

Use the bug report template:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10]
- Python Version: [e.g., 3.11.0]
- Application Version: [e.g., 7.0]

## Screenshots
If applicable

## Logs
Attach relevant logs from logs/ directory
```

### Feature Requests

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why this feature is needed

## Proposed Solution
How you envision it working

## Alternatives Considered
Other approaches you've thought about
```

## 🌿 Branch Naming Conventions

Use descriptive branch names following this pattern:

```
<type>/<short-description>
```

### Examples

- `feature/playlist-download` - New feature
- `fix/progress-bar-crash` - Bug fix
- `docs/api-documentation` - Documentation
- `refactor/service-layer` - Code refactoring
- `test/controller-coverage` - Test improvements
- `chore/update-dependencies` - Maintenance

## 🏆 Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Release notes for significant contributions
- GitHub contributors page

## 📞 Getting Help

- **Questions**: Open a discussion on GitHub Discussions
- **Bugs**: Create an issue with the bug template
- **Feature Ideas**: Create an issue with the feature template
- **Chat**: Join our community chat (if available)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Ctrl+S Tube! 🎉
