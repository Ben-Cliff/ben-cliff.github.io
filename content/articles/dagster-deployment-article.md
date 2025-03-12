
Title: Deploying Dagster: Our Infrastructure Implementation
Date: 2024-03-20
Category: Data Engineering
Tags: dagster, deployment, infrastructure, docker, google-compute-engine
Slug: dagster-deployment-article
# Deploying Dagster: Our Infrastructure Implementation

After choosing Dagster as our workflow orchestration tool, implementing a robust deployment strategy became our next challenge. This article outlines the technical approach we took to deploy Dagster in a production environment, balancing simplicity with reliability.

## Deployment Architecture Overview

Rather than jumping straight to complex orchestration systems like Kubernetes, we opted for a more straightforward approach using Google Compute Engine (GCE) with Docker Compose. This choice aligned with our "start simple" philosophy and our small team's resource constraints.

### Why GCE Instead of GKE?

While Google Kubernetes Engine (GKE) offers advanced orchestration capabilities, it introduces significant operational complexity. For our current scale and use cases, a single GCE instance running Docker Compose provides the right balance of simplicity and functionality.

As one team member noted in our documentation: "GKE would be overkill for the current scale and complexity. GCE provides simpler infrastructure while meeting deployment needs."

## Multi-Container Deployment Strategy

Our Dagster deployment consists of several interconnected containers:

1. **`docker_dagster_core`**: Contains our custom user code (assets, resources, schedules)
2. **`dagster-postgres`**: Persistent storage for Dagster's internal state
3. **`dagster-webserver`**: Provides the Dagster UI and API
4. **`dagster-daemon`**: Runs the scheduler and sensors

This separation of concerns allows us to update our user code without affecting the core Dagster services.

## CI/CD Pipeline Implementation

We've implemented a comprehensive GitHub Actions workflow that automates the deployment process for our code changes. Our CI/CD approach consists of two distinct workflows: a testing pipeline and a deployment pipeline.

### Testing Workflow

Our basic CI/CD testing workflow is triggered on both pushes to main and pull requests. It focuses on validating that Dagster assets and jobs can execute successfully:

```yaml
name: Dagster Basic CI/CD

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  dagster-basic-job:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v2

      - name: Set up Python environment
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH  # Add Poetry to PATH
        shell: bash

      - name: Set DAGSTER_HOME environment variable
        run: |
          echo "DAGSTER_HOME=$GITHUB_WORKSPACE/dagster_home" >> $GITHUB_ENV
          mkdir -p "$GITHUB_WORKSPACE/dagster_home"
          echo "{}" > "$GITHUB_WORKSPACE/dagster_home/dagster.yaml"
        shell: bash

      - name: Install dependencies
        run: poetry install --no-root

      - name: Run basic Dagster CI/CD check
        run: |
          poetry run dagster job execute -f dagster_core/pipelines/test_job.py -j test_job
        shell: bash
```

This workflow ensures that our code changes don't break core functionality before we proceed with deployment.

### Deployment Workflow

The deployment workflow is more selective, triggering only on changes to files in the `dagster_core` directory when pushed to main, or via manual triggers:

```yaml
name: Dagster Deployment Pipeline

on:
  push:
    branches:
      - main # Trigger only when changes are pushed to the main branch
    paths:
      - 'dagster_core/**' # Trigger only when files in dagster_core are updated
  workflow_dispatch: # Support for manual triggers

jobs:
  deploy-dagster-core:
    name: Deploy Dagster Core
    runs-on: ubuntu-latest

    steps:
      # Step 1: Checkout the repository
      - name: Checkout Code
        uses: actions/checkout@v3

      # Step 2: Authenticate with GCP
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_CREDENTIALS }}

      # Step 3: Set the active GCP service account
      - name: Set Active GCP Account
        run: gcloud config set account ${{ secrets.GCP_SERVICE_ACCOUNT }}

      # Step 4: Configure Docker for Artifact Registry
      - name: Configure Docker for Artifact Registry
        run: gcloud auth configure-docker ${{ secrets.ARTIFACT_REGION }}

      # Step 5: Build and Push the Docker image to Artifact Registry
      - name: Build and Push docker_dagster_core for AMD64
        run: |
          docker buildx build \
            --platform linux/amd64 \
            -t ${{ secrets.ARTIFACT_REGION }}/${{ secrets.GCP_PROJECT }}/${{ secrets.ARTIFACT_REGISTRY }}/docker_dagster_core:latest \
            -f dockerfile_dagster_core . --push

      # Step 6: Update the Docker container on the VM
      - name: Update docker_dagster_core Container on VM
        run: |
          gcloud compute ssh dagster-deploy@${{ secrets.INSTANCE_NAME }} --zone ${{ secrets.GCE_ZONE }} --command "
          cd /home/dagster-deploy/dagster
          gcloud auth activate-service-account ${{ secrets.GCP_SERVICE_ACCOUNT }} --key-file=${{ secrets.SA_KEY_PATH }}
          gcloud auth configure-docker ${{ secrets.ARTIFACT_REGION }}
          gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://${{ secrets.ARTIFACT_REGION }}
          docker-compose pull docker_dagster_core &&
          docker-compose up -d docker_dagster_core
          "
```

This workflow handles:
1. Building and pushing our Dagster core container to Google's Artifact Registry
2. Securely logging into our compute instance
3. Updating only the `docker_dagster_core` container while leaving the rest of the infrastructure untouched

This targeted approach minimizes disruption by avoiding a full redeployment of all containers, allowing us to update our data pipelines without affecting the underlying Dagster system.

## Environment Separation: Development, Staging, and Production

We maintain distinct configurations across multiple environments to support our development workflow. This multi-environment approach allows us to test changes in isolation before they impact production systems.

### Development Environment

The development environment runs locally on developers' machines and serves as the first testing ground for new features:

- Uses local Docker Compose setup with `docker-compose.dev.yml`
- Service account keys with limited permissions
- Environment variables from `.env.dev` file
- Accessible via `localhost:3000`
- Features hot-reloading for rapid iteration on assets and pipelines
- Uses isolated test databases to prevent conflicts

### Staging Environment

Our staging environment mirrors production in infrastructure but uses separate data sources:

- Is deployed locally via localhost:3000 but points to a seperate GCP project
- Uses a staging-specific Google Cloud project to avoid resource conflicts
- Connected to test data sources and warehouses
- Has the same CI/CD pipeline as production but targets different infrastructure
- Environment variables from `.env.staging` file
- Perfect for integration testing before production deployment
- Provides a safe environment for other teams to test their integrations with our data platform


### Production Environment

Our production environment is the most tightly controlled:

- Dedicated GCE instance with Docker Compose orchestration
- Uses instance-attached service accounts for enhanced security
- Environment variables from `.env.prod` file
- Connected to production data sources
- Changes require pull request approval and successful CI checks
- SSH tunneling for secure access:

```bash
gcloud beta compute ssh [PRODUCTION_INSTANCE_NAME] --zone [ZONE] -- -L 5000:localhost:3000 -N -f
```

### Environment-Specific Configuration Management

To manage these distinct environments, we've implemented several key practices:

1. **Environment Segregation**: Each environment uses isolated GCP projects to prevent resource conflicts and manage permissions separately.

2. **Configuration Repository**: Environment variables are stored in separate files that never enter source control. These are managed in a secure password manager and retrieved by developers as needed.

3. **Resource Naming Conventions**: All resources follow a consistent naming pattern: `resource-type-{env}` where `env` is `dev`, `staging`, or `prod`.

4. **Consistent Database Schemas**: We maintain identical schema structures across environments, with automated schema sync tools to keep them aligned.

5. **Environment-Specific Dagster Code**: For features that require different behavior between environments, we use Dagster's built-in `RunConfig` system:

```python
@job
def data_pipeline():
    # Pipeline definition

@repository
def my_repo():
    # Different configurations for different environments
    if os.environ.get("DAGSTER_ENV") == "prod":
        yield job(
            data_pipeline,
            config={"ops": {"data_processor": {"config": {"use_production_credentials": True}}}}
        )
    else:
        yield job(
            data_pipeline,
            config={"ops": {"data_processor": {"config": {"use_production_credentials": False}}}}
        )
```

This environment-specific configuration allows us to maintain a single codebase while adjusting behavior based on deployment context.

### Documentation Publication

In addition to our Dagster deployment, we also maintain a documentation site for our data platform using a separate CI workflow:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install "pelican[markdown]"
          git submodule update --init --recursive

      - name: Build site
        run: pelican content -o output -s pelicanconf.py

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./output
          publish_branch: gh-pages
          enable_jekyll: false
```

This workflow automatically builds and deploys our Pelican-based documentation site to GitHub Pages whenever updates are made, ensuring our team always has access to the latest documentation about our data platform and Dagster implementation.

## Code Quality and Git Workflow

To maintain high code quality, we've implemented:

1. **Branch Protection Rules**:
   - All changes require pull requests
   - At least one approval needed for merging
   - Status checks must pass before merging
   - Direct pushes to `main` are blocked

2. **Pre-commit Hooks and CI Linting**:
   - Black for code formatting
   - Flake8 for linting
   - isort for import sorting
   - mypy for type checking

3. **Standard Git Flow**:
   - Feature branches for changes
   - Pull requests targeting `main`
   - Squash merging for clean history

## Challenges and Solutions

### Challenge: Service Dependencies

Dagster's multi-service architecture requires careful orchestration to ensure proper startup sequence and inter-service communication.

**Solution**: Docker Compose network configuration ensures all containers can communicate, with proper dependency ordering in the compose file.

### Challenge: Configuration Management

Managing environment variables and secrets across environments presented security concerns.

**Solution**: Environment-specific `.env` files are stored securely and never committed to version control. Service account management differs between environments, with production using instance-attached service accounts for enhanced security.

### Challenge: Deployment Updates

Updating only the core container without disturbing other services required careful orchestration.

**Solution**: Our CI/CD pipeline targets only the `docker_dagster_core` container, leaving other services running undisturbed.

### Why SSH Tunnels Instead of a Public-Facing Dagster UI?

- Team Size Reality: For a small team of four, the complexity of configuring Cloudflare, DNS records, SSL certificates, and authentication layers wasn't justified
- Security Simplification: SSH tunnels eliminate the need to manage web server configurations, SSL certificates, or authentication layers
- Zero Additional Infrastructure: Leverages existing GCP SSH capabilities without requiring any new services or components
- Resource Efficiency: Limited engineering hours are better spent building data pipelines than maintaining web infrastructure - SSH tunneling took minutes to set up versus days for a proper public-facing website


## Future Scaling Considerations

While our current setup meets immediate needs, we've identified areas for future enhancement:

1. **Potential Kubernetes Migration**: As our pipelines grow in complexity and scale, we may transition to GKE for more robust orchestration.

2. **Improved Secret Management**: Implementing a dedicated secrets management solution would enhance security.

3. **Deployment Rollbacks**: Adding capability to quickly roll back to previous container versions if issues arise.

4. **High Availability**: For critical workloads, implementing redundancy to eliminate single points of failure.

## Conclusion

Our Dagster deployment strategy demonstrates that sophisticated data orchestration doesn't necessarily require complex infrastructure. By starting with a simple yet effective GCE-based approach, we've created a foundation that can evolve as our data needs grow.

For small teams getting started with Dagster, this approach offers several advantages:

1. **Minimal DevOps Overhead**: Managing a single GCE instance is simpler than Kubernetes
2. **Cost Efficiency**: Lower resource consumption than distributed deployments
3. **Straightforward Troubleshooting**: SSH access to a single instance simplifies debugging
4. **Iterative Path to Scale**: Easy to start small and grow as needs evolve

This implementation has successfully balanced our technical requirements with team resources, providing a production-ready Dagster deployment that still leaves room for future growth.
