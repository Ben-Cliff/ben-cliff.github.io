Title: Dagster Architecture Deep Dive - Part 1
Date: 2025-03-14
Category: Data Engineering
Tags: dagster, deployment, infrastructure, docker, orchestration, gcp, ci/cd, docker-compose
Slug: dagster-architecture-deep-dive


Deploying Dagster in a production environment requires understanding its multi-service architecture and how the components work together. This article explores the architecture of a production Dagster deployment, using Google Cloud Platform (GCP) as our cloud provider.

## Multi-Service Architecture Explanation

For production deployment, we follow Dagster's recommended containerized approach. This setup consists of four Docker containers, each handling different aspects of the platform. One major advantage of this pattern is that we can update our pipeline code in the `docker_dagster_core` container without interrupting the scheduler or causing downtime for the entire system.

Our Dagster deployment uses the following containers, working together to form a complete environment:

## Component Interactions and Communication Flow

Understanding how the components interact with each other is key to managing and troubleshooting a Dagster deployment. The following diagram illustrates the main connections between our four core containers:

![Dagster Architecture Diagram]

### Communication Between Components

The diagram shows how information flows through the system:

1. **gRPC Communication**:
   - Both the webserver and daemon communicate with the `docker_dagster_core` container via gRPC
   - This protocol enables these services to discover, load, and execute your pipeline code
   - gRPC offers efficient, language-agnostic communication between services

2. **PostgreSQL as Shared Storage**:
   - All services connect to PostgreSQL for persistent storage needs
   - The webserver stores and retrieves UI state and run history
   - The daemon maintains schedule and sensor state
   - The user code container logs events and run information

3. **Daemon-Webserver Coordination**:
   - The daemon and webserver communicate directly for operational purposes
   - The daemon notifies the webserver about completed runs
   - The webserver can request the daemon to cancel runs
   - They coordinate on schedule and sensor status

4. **User Access Point**:
   - External users interact exclusively with the webserver via HTTP
   - The webserver presents a user-friendly interface for monitoring and controlling the system
   - Users never communicate directly with the other containers

This architecture creates a clean separation of responsibilities while ensuring robust communication between components. Each container has a specific role to play in the overall system:

- **docker_dagster_core**: Houses your actual pipeline code and exposes it via a gRPC server
- **PostgreSQL**: Provides persistent storage for all system state and history
- **dagster-webserver**: Delivers the user interface and coordinates with other components
- **dagster-daemon**: Manages background processes like schedules, sensors, and run queues

![Architecture Diagram]({static}/images/dagster-architecture-diagram.svg)

## Why Separate docker_dagster_core Container?

A key architectural decision in our Dagster deployment is isolating user code in its own container (`docker_dagster_core`). This approach offers several significant advantages:

### CI/CD Pipeline Optimization

By isolating our application code in a dedicated container, we can implement efficient CI/CD pipelines that:

1. **Rebuild only what changes**: When developers modify pipeline code, only the `docker_dagster_core` container needs to be rebuilt and redeployed.

2. **Minimize downtime**: The webserver, daemon, and database can remain running while the user code container is updated.

3. **Enable rollbacks**: If a deployment introduces issues, we can quickly roll back to a previous version of just the user code container.

4. **Support targeted testing**: CI pipelines can focus testing efforts on just the code that's changing.

```yaml
# Example GitHub Actions workflow section for targeted deployment
- run: |
    docker build -t docker_dagster_core -f dockerfile_dagster_core .
    docker push ${ARTIFACT_REGISTRY}/docker_dagster_core

    # Only restart the user code container
    docker-compose up -d --force-recreate docker_dagster_core
```

### Repository Structure Flexibility

This architecture supports multiple repository organization patterns:

1. **Monorepo approach**: Keep all Dagster components and user code in a single repository (as shown in these examples).
   - Advantages: Simpler versioning, easier to maintain consistency
   - Best for: Smaller teams, early-stage projects

2. **Separate repositories**: Maintain user code in its own repository, separate from infrastructure code.
   - Advantages: Cleaner separation of concerns, more focused repositories
   - Best for: Larger teams, mature projects with distinct infrastructure and data teams

The choice between these approaches depends on your team structure, development workflow, and organizational preferences. Both patterns work well with the containerized architecture described here - you would simply adjust your CI/CD pipelines to pull from the appropriate repositories.

## Component Roles

### docker_dagster_core: The User Code Container

The `docker_dagster_core` container hosts your Dagster application code - your assets, ops, jobs, and any Python dependencies. It exposes this code over a gRPC server that allows the webserver and daemon to interact with it.

```yaml
docker_dagster_core:
  build:
    context: .
    dockerfile: ./dockerfile_dagster_core
  container_name: docker_dagster_core
  image: docker_dagster_core_image
  restart: always
  command: ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-f", "/opt/dagster/dagster_home/dagster_core/__init__.py"]
  ports:
    - "4000:4000"
  environment:
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB}
    DAGSTER_CURRENT_IMAGE: "docker_dagster_core_image"
    GOOGLE_APPLICATION_CREDENTIALS: "/opt/dagster/dagster_home/secrets/service-account.json"
    GCP_PROJECT: ${GCP_PROJECT}
    GCP_LOCATION: ${GCP_LOCATION}
    BIGQUERY_PROJECT: ${GCP_PROJECT}
  depends_on:
    - dagster-postgres
  networks:
    - dagster-network
  volumes:
    - ${GCP_SA_PATH}:/opt/dagster/dagster_home/secrets/service-account.json:ro
```

**Key Points**:
- Runs a gRPC server on port 4000
- Loads Dagster code from the repository's `__init__.py` file
- Contains GCP configuration for interacting with Google Cloud services
- Mounts a service account JSON file from the host for GCP authentication

### dagster-postgres: The Metadata Store

The PostgreSQL container provides persistent storage for Dagster's metadata, including:
- Run history
- Event logs
- Schedule state
- Sensor state

```yaml
dagster-postgres:
  image: postgres:13
  environment:
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB}
  volumes:
    - dagster-postgres:/var/lib/postgresql/data
  networks:
    - dagster-network
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
    interval: 10s
    timeout: 8s
    retries: 5
```

**Key Points**:
- Uses a named volume to persist database data
- Includes a health check to ensure other services only start after the database is ready
- Environment variables for credentials help maintain security best practices

### dagster-webserver: The User Interface

The webserver container serves Dagster's web UI, allowing users to:
- Explore and execute jobs
- Monitor asset materializations
- View run history and logs
- Manage schedules and sensors

```yaml
dagster-webserver:
  build:
    context: .
    dockerfile: dockerfile_daemon_webserver
  entrypoint:
    - dagster-webserver
    - -h
    - "0.0.0.0"
    - -p
    - "3000"
    - -w
    - workspace.yaml
  ports:
    - "3000:3000"
  environment:
    DAGSTER_HOME: /opt/dagster/dagster_home
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB}
  depends_on:
    dagster-postgres:
      condition: service_healthy
    docker_dagster_core:
      condition: service_started
  networks:
    - dagster-network
```

**Key Points**:
- Exposes the web UI on port 3000
- Uses a workspace.yaml file to define code locations
- Depends on both the database and the user code container

### dagster-daemon: The Background Processor

The daemon container handles background processes such as:
- Running schedules
- Executing sensors
- Managing run queues
- Cleaning up old run data

```yaml
dagster-daemon:
  build:
    context: .
    dockerfile: dockerfile_daemon_webserver
  command: ["dagster-daemon", "run"]
  environment:
    DAGSTER_HOME: /opt/dagster/dagster_home
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB}
  depends_on:
    dagster-postgres:
      condition: service_healthy
    docker_dagster_core:
      condition: service_started
  networks:
    - dagster-network
```

**Key Points**:
- Uses the same Docker image as the webserver but with a different command
- Does not expose any ports as it doesn't serve HTTP requests
- Must connect to both the database and user code gRPC server

## Data Flow Between Components

Understanding how data flows between components helps with troubleshooting and performance optimization.

1. **User Code Discovery**:
   - The webserver and daemon discover user code via the gRPC server
   - The gRPC server loads code from the `__init__.py` file

2. **Run Execution Flow**:
   - User initiates a run via the UI → webserver
   - Webserver adds run to queue in PostgreSQL
   - Daemon picks up run from queue
   - Daemon executes run via gRPC server
   - Run events are logged to PostgreSQL
   - UI displays events by querying PostgreSQL

3. **Schedule/Sensor Flow**:
   - Daemon evaluates schedules and sensors
   - When triggered, daemon adds runs to queue
   - Execution proceeds as with manual runs

## Configuration Management with dagster.yaml

The `dagster.yaml` file is the central configuration file for Dagster. It defines:
- How metadata is stored
- How run coordination works
- Scheduler configuration
- Logging settings

Here's our `dagster.yaml` configuration:

```yaml
scheduler:
  module: dagster.core.scheduler
  class: DagsterDaemonScheduler

run_coordinator:
  module: dagster.core.run_coordinator
  class: QueuedRunCoordinator
  config:
    max_concurrent_runs: 5

run_storage:
  module: dagster_postgres.run_storage
  class: PostgresRunStorage
  config:
    postgres_db:
      hostname: dagster-postgres
      username:
        env: POSTGRES_USER
      password:
        env: POSTGRES_PASSWORD
      db_name:
        env: POSTGRES_DB
      port: 5432

event_log_storage:
  module: dagster_postgres.event_log
  class: PostgresEventLogStorage
  config:
    postgres_db:
      hostname: dagster-postgres
      username:
        env: POSTGRES_USER
      password:
        env: POSTGRES_PASSWORD
      db_name:
        env: POSTGRES_DB
      port: 5432

schedule_storage:
  module: dagster_postgres.schedule_storage
  class: PostgresScheduleStorage
  config:
    postgres_db:
      hostname: dagster-postgres
      username:
        env: POSTGRES_USER
      password:
        env: POSTGRES_PASSWORD
      db_name:
        env: POSTGRES_DB
      port: 5432

telemetry:
  enabled: false
```

**Key Configuration Sections**:

1. **Scheduler**: Uses the daemon-based scheduler for running schedules
2. **Run Coordinator**: Limits concurrent runs to 5 by default
3. **Storage Sections**: All point to PostgreSQL for persistence
4. **Environment Variables**: Credentials come from environment variables for security

## Service Dependencies and Startup Order

Docker Compose helps manage service dependencies and ensures proper startup order:

1. **PostgreSQL** starts first
2. **docker_dagster_core** depends on PostgreSQL
3. **dagster-webserver** and **dagster-daemon** depend on both PostgreSQL and docker_dagster_core

These dependencies are defined in the Docker Compose file and enforced through `depends_on` directives. The PostgreSQL container includes a health check, which provides a more robust dependency - services wait until PostgreSQL is actually ready to accept connections.

```yaml
depends_on:
  dagster-postgres:
    condition: service_healthy
  docker_dagster_core:
    condition: service_started
```

This ensures that the webserver and daemon won't start until both the database and user code container are ready.

## Network Configuration

Our services communicate over a dedicated Docker network:

```yaml
networks:
  dagster-network:
    driver: bridge
    name: dagster-network
```

This network configuration provides:

1. **Service Discovery**: Containers can refer to each other by service name
2. **Isolation**: Services are isolated from other Docker networks
3. **Security**: Only explicitly exposed ports are accessible from outside

Port mappings are defined for services that need external access:

```yaml
ports:
  - "3000:3000"  # For dagster-webserver
  - "4000:4000"  # For docker_dagster_core
```

The webserver UI is accessible on port 3000, while the gRPC server runs on port 4000. In production, you typically access the UI through an SSH tunnel for security.

## The Workspace.yaml File

The `workspace.yaml` file tells the webserver how to connect to the gRPC server:

```yaml
load_from:
  - grpc_server:
      host: docker_dagster_core
      port: 4000
      location_name: "dagster_core"
```

This simple configuration directs the webserver to load code from the gRPC server running in the docker_dagster_core container.

## Project Directory Structure

A well-organized directory structure is essential for maintaining a clear separation between application code and deployment configuration. Here's how we structure our Dagster project:

```
/
├── dagster_core/             # Application code directory
│   ├── __init__.py           # Repository definition
│   ├── assets/               # Dagster assets
│   ├── ops/                  # Operations definitions
│   ├── pipelines/            # Job and pipeline definitions
│   ├── types/                # Custom type definitions
│   └── utils/                # Helper functions
│
├── dagster_home/             # Runtime directory (created during deployment)
│   └── dagster.yaml          # Instance configuration
│
├── docker/                   # Docker-related files
│   ├── dockerfile_dagster_core       # User code container definition
│   └── dockerfile_daemon_webserver   # Webserver/daemon container definition
│
├── docker-compose-local.yml  # Development environment configuration
├── docker-compose-GCE.yml    # Production environment configuration
├── workspace.yaml            # Workspace configuration
└── pyproject.toml            # Python dependencies and tools
```

This structure provides a clean separation between:

1. **Application Logic**: All Dagster-specific code lives in the `dagster_core` directory
2. **Infrastructure Configuration**: Docker and deployment files at the root level
3. **Runtime Configuration**: Instance settings in `dagster_home`

Having this clear organization makes it easier to implement CI/CD pipelines that target only the necessary parts of the system when changes are made.

## Conclusion

Dagster's multi-service architecture provides a robust, scalable foundation for data orchestration. By understanding how these components interact, you can better manage, troubleshoot, and optimize your Dagster deployment.

While this article used GCP as the cloud provider, the architecture works similarly on other cloud platforms or on-premises. The key differences would be in the service account configuration and deployment mechanisms.

In the next article, we'll explore how to deploy this architecture to Google Cloud Platform, including step-by-step instructions for setting up a GCE instance and configuring the deployment pipeline.
