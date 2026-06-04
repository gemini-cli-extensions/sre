# Infrastructure Wiki: my-project

## Architecture Graph
![Topology](./discover.png)

## Cloud Run: frontend
The Cloud Run layer acts as the primary compute boundary for user-facing applications. 

### Properties
- **Region**: us-central1
- **Scaling**: 0 to 100 max instances
- **Ingress**: Internal and Cloud Load Balancing

### Dependencies
- **Synchronous**: Relies on `postgres-db` (Cloud SQL) for user profiles.
- **Asynchronous**: Publishes to `events-topic` (Pub/Sub) for analytics telemetry.

## Cloud SQL: postgres-db
Relational database storing user metadata.

### Properties
- **Version**: PostgreSQL 14
- **Tier**: db-custom-2-7680
- **High Availability**: Enabled (Regional)

### Dependencies
- **Upstream callers**: `frontend`
