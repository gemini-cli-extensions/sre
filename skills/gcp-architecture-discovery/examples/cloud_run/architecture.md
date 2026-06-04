# Architecture: my-project - cloud_run

## Overview
The Cloud Run layer acts as the primary compute boundary for user-facing applications. 

- **`frontend`**: The main web interface. It scales from 0 to 100 based on HTTP traffic. It relies synchronously on `postgres-db` (Cloud SQL) for user profiles and asynchronously publishes to `events-topic` (Pub/Sub) for analytics telemetry.

## System Topology & Request Flow

![Topology](./architecture.png)
