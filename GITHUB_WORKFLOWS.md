# GitHub Workflows Setup Guide

This project uses two GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 1. Test Workflow (`test.yaml`)
- **Trigger**: Runs on push to `main` or `dev` branches, and on pull requests to `main`
- **Conditions**: Only runs when relevant files change (src/, cases/, runtime/, requirements.txt, setup.py)
- **Steps**:
  1. Checks out code
  2. Sets up Python 3.11
  3. Caches pip dependencies
  4. Installs Python dependencies
  5. Builds the C runtime
  6. Runs all tests

### 2. Publish Workflow (`publish.yaml`)
- **Trigger**: Runs on push to `main` branch
- **Conditions**: Only publishes when:
  - Relevant files have changed
  - Commit message matches version format: `<MAJOR><LETTER> - <message>`
    - Example: `1A - Initial release` → version `1.0.0`
    - Example: `1B - Bug fixes` → version `1.1.0`
    - Example: `2C - Major update` → version `2.2.0`
- **Steps**:
  1. Checks if commit message contains a version tag
  2. Converts version from your format to semantic versioning
  3. Runs all tests
  4. Builds the package
  5. Publishes to PyPI

## Version Scheme

The version is extracted from commit messages:
- Format: `<MAJOR><LETTER> - <description>`
- Major version: Any number (1, 2, 3, etc.)
- Minor version: Letter converted to number (A=0, B=1, C=2, ..., Z=25)
- Patch version: Always 0

Examples:
- `1A - Initial release` → `1.0.0`
- `1B - Added new features` → `1.1.0`
- `1Z - Bug fixes` → `1.25.0`
- `2A - Breaking changes` → `2.0.0`

## Setup Requirements

### 1. PyPI Configuration
1. Create an account on [PyPI](https://pypi.org/)
2. Go to your [PyPI account settings](https://pypi.org/manage/account/)
3. Create an API token for publishing

### 2. GitHub Repository Setup
1. Create the repository: `Omena0/fr`
2. Go to repository Settings → Environments
3. Create an environment named `pypi`
4. Add the following environment secret:
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token

### 3. Trusted Publisher (Recommended)
Instead of using an API token, you can set up a trusted publisher:
1. Go to [PyPI Publishing Settings](https://pypi.org/manage/account/publishing/)
2. Add a new pending publisher:
   - PyPI Project Name: `frscript`
   - Owner: `Omena0`
   - Repository name: `fr`
   - Workflow name: `publish.yaml`
   - Environment name: `pypi`
3. Once set up, remove the `PYPI_API_TOKEN` secret (not needed)

## Making a Release

To publish a new version:

1. Make your changes and commit them normally
2. For the final commit that should trigger a release, use the version format:
   ```bash
   git commit -m "1A - Initial release"
   git push origin main
   ```
3. The workflow will automatically:
   - Extract the version (`1.0.0` from `1A`)
   - Run tests
   - Build the package
   - Publish to PyPI

## Badges

The README includes the following badges:
- **Tests**: Shows the status of the test workflow
- **PyPI**: Shows the latest published version
- **Python Version**: Shows supported Python versions

## Local Testing

Before pushing, you can test locally:

```bash
# Run tests
cd src
python tests.py

# Build package locally
python -m build

# Check package
twine check dist/*
```

## Troubleshooting

### Tests fail locally but pass on CI
- Ensure you've built the C runtime: `cd runtime && make`
- Check Python version matches (3.11)

### Version not detected
- Ensure commit message matches format: `<NUMBER><LETTER> - <message>`
- Check there's a space after the letter and before the dash
- Use uppercase letters (A-Z)

### PyPI publish fails
- Check environment name is exactly `pypi`
- Verify API token is correct
- Ensure package name `frscript` is available on PyPI
- For first publish, you may need to create the project manually on PyPI
