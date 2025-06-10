# CI/CD Strategy

## Overview

This project uses GitHub Actions for Continuous Integration. The CI pipeline ensures code quality by running all tests before allowing merges to protected branches (develop and main).

## GitHub Actions Workflow

### 1. Pull Request Workflow

```yaml
name: Pull Request Checks

on:
  pull_request:
    branches: [ develop, main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          
      - name: Install dependencies
        run: poetry install
        
      - name: Run all tests
        run: poetry run pytest tests/
```

## Branch Protection Rules

### Protected Branches
- develop
- main

### Protection Requirements
1. **Required Status Checks**:
   - All tests must pass
   - Branch must be up to date

2. **Pull Request Requirements**:
   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Include administrators in these restrictions

## Test Requirements

### Test Coverage
- All tests in `/tests` directory must pass
- No failing tests allowed

## Workflow Process

1. **Pull Request Creation**:
   - Create PR to develop/main
   - GitHub Actions automatically triggers

2. **Automated Checks**:
   - Runs all tests in `/tests`
   - Generates test status report

3. **Review Process**:
   - PR must be reviewed
   - All tests must pass
   - Branch must be up to date

4. **Merge Approval**:
   - Only allowed after all tests pass
   - Requires reviewer approval
   - Maintains branch protection 