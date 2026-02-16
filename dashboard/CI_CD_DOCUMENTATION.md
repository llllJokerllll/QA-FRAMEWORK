# CI/CD Documentation - QA-FRAMEWORK Dashboard

## Overview

This document describes the complete Continuous Integration and Continuous Deployment (CI/CD) pipeline for the QA-FRAMEWORK Dashboard project.

## Architecture

The CI/CD pipeline consists of three main workflows:

1. **CI (Continuous Integration)** - `.github/workflows/ci.yml`
2. **CD (Continuous Deployment)** - `.github/workflows/cd.yml`
3. **Code Quality** - `.github/workflows/code-quality.yml`

## Workflows

### 1. CI Workflow (ci.yml)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual workflow dispatch

**Jobs:**

#### changes
- Detects which parts of the codebase changed (backend, frontend)
- Optimizes workflow by only running relevant jobs

#### test-backend
- Runs on Python 3.11 and 3.12 (matrix strategy)
- Sets up PostgreSQL and Redis services
- Caches pip dependencies for faster builds
- **Linting:** flake8 for syntax and style checking
- **Formatting:** black for code formatting checks
- **Type Checking:** mypy for static type analysis
- **Security:** bandit for security vulnerability scanning
- **Dependency Scanning:** safety for known vulnerabilities
- **Testing:** pytest with coverage reporting
- Uploads coverage reports to Codecov
- Generates coverage artifacts

#### test-frontend
- Runs on Node.js 18.x and 20.x (matrix strategy)
- Caches npm dependencies
- Runs ESLint for linting
- Runs tests with Vitest and coverage
- Builds the frontend application
- Uploads coverage artifacts

#### integration-tests
- Builds Docker images using docker-compose
- Starts all services
- Runs smoke tests to verify service health

#### security-scan
- Runs Trivy vulnerability scanner on filesystem
- Uploads results to GitHub Security tab
- Scans Docker base images for vulnerabilities

#### notify
- Notifies on CI completion status
- Fails the workflow if any job fails

### 2. CD Workflow (cd.yml)

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch (with environment selection)

**Jobs:**

#### build-and-push
- Builds Docker images for backend and frontend
- Pushes images to GitHub Container Registry (ghcr.io)
- Uses Docker Buildx for efficient builds
- Caches Docker layers
- Tags images with:
  - Branch name
  - Short SHA
  - `latest` (for main branch)
  - `staging` (for main branch)

#### deploy-staging
- Depends on successful build
- Creates docker-compose.staging.yml dynamically
- Deploys to staging server via SSH
- Runs smoke tests after deployment
- Verifies backend health endpoint
- Verifies frontend availability

#### deploy-production
- Manual trigger only
- Similar to staging deployment
- Creates docker-compose.prod.yml
- Deploys to production server
- Runs production smoke tests

#### notify-deployment
- Notifies on deployment status
- Fails if deployment fails

#### rollback-on-failure
- Automatically rolls back staging on failure
- Recreates containers with previous version

### 3. Code Quality Workflow (code-quality.yml)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests
- Daily scheduled run (2 AM UTC)
- Manual workflow dispatch

**Jobs:**

#### code-formatting-backend
- Checks Black formatting
- Verifies import sorting with isort
- Runs autopep8 for additional formatting checks

#### code-formatting-frontend
- Runs ESLint with detailed output
- Checks TypeScript types

#### dependency-vulnerability-scan
- Scans Python dependencies with safety
- Scans Node.js dependencies with npm audit
- Runs separately for backend and frontend

#### code-complexity-analysis
- Uses radon for cyclomatic complexity
- Generates raw metrics
- Calculates maintainability index
- Computes Halstead metrics
- Uses xenon for complexity thresholds

#### static-analysis-backend
- Runs Prospector comprehensive analysis
- Runs Pylint for code quality
- Runs Pyflakes for error detection
- Runs Pydocstyle for docstring conventions

#### static-analysis-frontend
- Runs ESLint with plugins
- Checks code complexity

#### code-coverage-trend
- Tracks coverage trends over time
- Uploads to Codecov
- Only runs on main branch

#### generate-quality-report
- Downloads all artifact reports
- Generates quality summary markdown
- Comments on PRs with summary

#### notify-quality-checks
- Summarizes all quality check results
- Reports any failures

## Required Secrets

The following secrets must be configured in GitHub repository settings:

### For CI
- `CODECOV_TOKEN` - Token for Codecov coverage reporting

### For CD - Staging
- `STAGING_HOST` - Staging server hostname/IP
- `STAGING_USER` - SSH username for staging server
- `STAGING_SSH_KEY` - SSH private key for staging server
- `STAGING_DATABASE_URL` - PostgreSQL connection string for staging
- `STAGING_SECRET_KEY` - JWT secret key for staging
- `STAGING_DB_USER` - PostgreSQL username
- `STAGING_DB_PASSWORD` - PostgreSQL password

### For CD - Production
- `PROD_HOST` - Production server hostname/IP
- `PROD_USER` - SSH username for production server
- `PROD_SSH_KEY` - SSH private key for production server
- `PROD_DATABASE_URL` - PostgreSQL connection string for production
- `PROD_SECRET_KEY` - JWT secret key for production
- `PROD_DB_USER` - PostgreSQL username
- `PROD_DB_PASSWORD` - PostgreSQL password

## Best Practices Implemented

### Caching
- pip packages cached between runs
- npm dependencies cached
- Docker layers cached using GitHub Actions cache
- Buildx cache for Docker builds

### Matrix Strategy
- Backend tests run on Python 3.11 and 3.12
- Frontend tests run on Node.js 18.x and 20.x
- Ensures compatibility across versions

### Security
- Trivy scans for vulnerabilities
- Bandit for Python security issues
- Safety for dependency vulnerabilities
- npm audit for Node.js vulnerabilities
- Secrets are never logged or exposed

### Parallelization
- Backend and frontend tests run in parallel
- Quality checks run in parallel
- Reduces overall pipeline time

### Conditional Execution
- Jobs only run when relevant files change
- Deployment only on main branch
- Quality trends only tracked on main

## Monitoring and Notifications

### Status Badges
The README.md includes status badges for:
- CI workflow status
- CD workflow status
- Code Quality workflow status
- Codecov coverage percentage
- Python version support
- Node.js version support

### Artifacts
Each workflow generates artifacts:
- Coverage reports (HTML and XML)
- Security scan reports
- Code quality reports
- Complexity analysis
- Linting reports

Artifacts are retained for 30 days (quality summary for 90 days).

## Deployment Process

### Staging Deployment
1. Merge to `main` triggers CD workflow
2. Docker images are built and pushed
3. Staging server pulls latest images
4. Services are restarted with new images
5. Smoke tests verify deployment
6. Rollback on failure

### Production Deployment
1. Manual trigger via GitHub Actions
2. Select "production" environment
3. Same process as staging
4. Additional verification steps

## Troubleshooting

### Common Issues

#### CI Failures
- Check test logs for specific failures
- Review coverage reports for untested code
- Check linting reports for style issues
- Review security scan results

#### CD Failures
- Verify SSH keys are correctly configured
- Check server connectivity
- Review Docker build logs
- Check server logs after deployment

#### Quality Check Failures
- Review formatting reports for Black/isort issues
- Check complexity reports for high-complexity functions
- Review security scans for vulnerabilities
- Check static analysis reports

### Accessing Reports
All reports are available as workflow artifacts:
1. Go to Actions tab
2. Select the workflow run
3. Download artifacts from the bottom of the page

## Maintenance

### Updating Dependencies
1. Update requirements.txt or package.json
2. Create a PR
3. CI will test the changes
4. Review security scan results
5. Merge if all checks pass

### Adding New Checks
1. Edit the relevant workflow file
2. Test in a feature branch
3. Create a PR
4. Review workflow results
5. Merge after approval

## Contributing

When contributing to the CI/CD pipeline:

1. Test changes in a fork or feature branch
2. Follow GitHub Actions best practices
3. Ensure secrets are properly used
4. Update this documentation
5. Create a PR with detailed description

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/)
- [Codecov Documentation](https://docs.codecov.com/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)

## Contact

For questions or issues with the CI/CD pipeline, please:
1. Check this documentation
2. Review the workflow logs
3. Create an issue in the repository
4. Contact the development team
