# QA-Framework Dashboard Architecture

System architecture diagrams and component documentation for the QA-Framework Dashboard.

## Table of Contents

- [System Overview](#system-overview)
- [High-Level Architecture](#high-level-architecture)
- [Component Diagrams](#component-diagrams)
- [Data Flow](#data-flow)
- [API Architecture](#api-architecture)
- [Database Schema](#database-schema)
- [Deployment Architecture](#deployment-architecture)
- [Security Architecture](#security-architecture)

---

## System Overview

The QA-Framework Dashboard is a comprehensive test management platform built with a modern microservices-oriented architecture.

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    QA-Framework Dashboard                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │   Frontend   │◄──►│    API       │◄──►│  Database    │     │
│  │  (React)     │    │  (FastAPI)   │    │ (PostgreSQL) │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                              │                                   │
│                              ▼                                   │
│                       ┌──────────────┐                          │
│                       │    Cache     │                          │
│                       │   (Redis)    │                          │
│                       └──────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## High-Level Architecture

### Complete System Architecture

```
                                   ┌─────────────┐
                                   │   Client    │
                                   │   Browser   │
                                   └──────┬──────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Reverse Proxy (Nginx)                        │
│              SSL Termination, Static Files, Routing               │
└──────────────────────────────────────────────────────────────────┘
       │                         │                         │
       ▼                         ▼                         ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend   │         │   API        │         │  Monitoring  │
│   Service    │         │   Service    │         │   Stack      │
│  (Port 3000) │         │  (Port 8000) │         │              │
└──────────────┘         └──────┬───────┘         │  Prometheus  │
                                │                 │  Grafana     │
                                ▼                 └──────────────┘
                       ┌────────────────┐
                       │  Middleware    │
                       │  Layer         │
                       └───────┬────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
   │   Database   │   │    Cache     │   │  Message     │
   │(PostgreSQL)  │   │   (Redis)    │   │   Queue      │
   │              │   │              │   │ (Optional)   │
   └──────────────┘   └──────────────┘   └──────────────┘
```

### Request Flow

```
┌────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Client │────►│  Nginx   │────►│ FastAPI  │────►│ Endpoint │
└────────┘     └──────────┘     └──────────┘     └────┬─────┘
                                                      │
                    ┌─────────────────────────────────┼───────┐
                    │                                 ▼       │
                    │  ┌──────────┐  ┌──────────┐  ┌───────┐ │
                    │  │  Auth    │  │ Validate │  │ Service│ │
                    │  │Middleware│  │ Request  │  │ Layer  │ │
                    │  └──────────┘  └──────────┘  └───┬───┘ │
                    │                                  │     │
                    │  ┌──────────┐  ┌──────────┐     │     │
                    │  │ Database │  │  Cache   │◄────┘     │
                    │  │   Ops    │  │   Ops    │           │
                    │  └──────────┘  └──────────┘           │
                    └─────────────────────────────────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │  JSON Response   │
                              └──────────────────┘
```

---

## Component Diagrams

### API Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Middleware Stack                     │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  1. CORS Middleware                                   │  │
│  │  2. Logging Middleware (Request ID)                   │  │
│  │  3. Rate Limiting Middleware                          │  │
│  │  4. Authentication Middleware                         │  │
│  │  5. Error Handling Middleware                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   API Router (v1)                     │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │                                                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐  │  │
│  │  │  Auth    │ │ Dashboard│ │  Suites  │ │ Cases  │  │  │
│  │  │  Routes  │ │  Routes  │ │  Routes  │ │ Routes │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘  │  │
│  │                                                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │  │
│  │  │Execution │ │  Users   │ │  Health  │             │  │
│  │  │  Routes  │ │  Routes  │ │  Routes  │             │  │
│  │  └──────────┘ └──────────┘ └──────────┘             │  │
│  │                                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Service Layer                      │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  auth_service.py    │  suite_service.py              │  │
│  │  user_service.py    │  case_service.py               │  │
│  │  execution_service  │  dashboard_service.py          │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │     │    API       │     │   Database   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │  POST /auth/login  │                    │
       │  {username, pass}  │                    │
       │───────────────────>│                    │
       │                    │                    │
       │                    │  Verify Credentials │
       │                    │───────────────────>│
       │                    │                    │
       │                    │  User Data         │
       │                    │<───────────────────│
       │                    │                    │
       │                    │  Generate JWT      │
       │                    │  (30 min expiry)   │
       │                    │                    │
       │  {access_token}    │                    │
       │<───────────────────│                    │
       │                    │                    │
       │                    │                    │
       │  GET /suites       │                    │
       │  Authorization:    │                    │
       │  Bearer <token>    │                    │
       │───────────────────>│                    │
       │                    │                    │
       │                    │  Validate Token    │
       │                    │  Decode JWT        │
       │                    │                    │
       │                    │  Fetch User        │
       │                    │───────────────────>│
       │                    │                    │
       │                    │  User Details      │
       │                    │<───────────────────│
       │                    │                    │
       │  {suite data}      │                    │
       │<───────────────────│                    │
       │                    │                    │
```

### Service Layer Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Service Layer                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │ Auth Service  │  │ Suite Service │  │ Case Service  │   │
│  ├───────────────┤  ├───────────────┤  ├───────────────┤   │
│  │ • login()     │  │ • create()    │  │ • create()    │   │
│  │ • validate()  │  │ • list()      │  │ • list()      │   │
│  │ • get_user()  │  │ • get()       │  │ • get()       │   │
│  └───────────────┘  │ • update()    │  │ • update()    │   │
│                     │ • delete()    │  │ • delete()    │   │
│                     └───────────────┘  └───────────────┘   │
│                                                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │Execution Svc  │  │ Dashboard Svc │  │  User Service │   │
│  ├───────────────┤  ├───────────────┤  ├───────────────┤   │
│  │ • create()    │  │ • get_stats() │  │ • create()    │   │
│  │ • list()      │  │ • get_trends()│  │ • list()      │   │
│  │ • start()     │  └───────────────┘  │ • get()       │   │
│  │ • stop()      │                     │ • update()    │   │
│  └───────────────┘                     │ • delete()    │   │
│                                         └───────────────┘   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Test Execution Flow

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│  User   │──►│  API    │──►│ Service │──►│   DB    │──►│Response │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
     │
     │ POST /executions
     │ {suite_id, type, env}
     ▼
┌────────────────────────────────────────────────────────────────┐
│  1. Validate request (Auth, Schema)                            │
│  2. Check suite exists                                          │
│  3. Create execution record (status: pending)                  │
│  4. Return execution ID                                        │
└────────────────────────────────────────────────────────────────┘
     │
     │ POST /executions/{id}/start
     ▼
┌────────────────────────────────────────────────────────────────┐
│  1. Verify execution exists                                     │
│  2. Update status to 'running'                                  │
│  3. Queue test runner (async)                                   │
│  4. Return success response                                     │
└────────────────────────────────────────────────────────────────┘
     │
     │ (Async Process)
     ▼
┌────────────────────────────────────────────────────────────────┐
│  1. Execute tests                                               │
│  2. Update results (pass/fail counts)                          │
│  3. Store artifacts                                             │
│  4. Update status to 'completed'                                │
│  5. Calculate duration                                          │
└────────────────────────────────────────────────────────────────┘
```

### Cache Flow

```
┌──────────────┐
│    Request   │
└──────┬───────┘
       │
       ▼
┌─────────────────┐     ┌──────────────┐
│ Check Cache     │────►│   Cache Hit  │
│ (Redis)         │     │   Return Data│
└───────┬─────────┘     └──────────────┘
        │ Cache Miss
        ▼
┌─────────────────┐
│ Query Database  │
│ (PostgreSQL)    │
└───────┬─────────┘
        │
        ▼
┌─────────────────┐     ┌──────────────┐
│ Store in Cache  │────►│ Return Data  │
│ (TTL Applied)   │     │              │
└─────────────────┘     └──────────────┘
```

---

## API Architecture

### Endpoint Structure

```
/api/v1
├── /auth
│   └── POST /login                    # Authentication
│
├── /dashboard
│   ├── GET /stats                     # Dashboard statistics
│   └── GET /trends                    # Execution trends
│
├── /suites                            # Test Suites (CRUD)
│   ├── POST   /                       # Create
│   ├── GET    /                       # List
│   ├── GET    /{id}                   # Get
│   ├── PUT    /{id}                   # Update
│   └── DELETE /{id}                   # Delete
│
├── /cases                             # Test Cases (CRUD)
│   ├── POST   /                       # Create
│   ├── GET    /                       # List
│   ├── GET    /{id}                   # Get
│   ├── PUT    /{id}                   # Update
│   └── DELETE /{id}                   # Delete
│
├── /executions                        # Test Executions
│   ├── POST   /                       # Create
│   ├── GET    /                       # List
│   ├── GET    /{id}                   # Get
│   ├── POST   /{id}/start             # Start
│   └── POST   /{id}/stop              # Stop
│
└── /users                             # User Management (CRUD)
    ├── POST   /                       # Create
    ├── GET    /                       # List
    ├── GET    /{id}                   # Get
    ├── PUT    /{id}                   # Update
    └── DELETE /{id}                   # Delete
```

---

## Database Schema

### Entity Relationship Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         Database Schema                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐         ┌──────────────┐         ┌─────────────┐│
│  │    users     │         │ test_suites  │         │ test_cases  ││
│  ├──────────────┤         ├──────────────┤         ├─────────────┤│
│  │ id (PK)      │         │ id (PK)      │         │ id (PK)     ││
│  │ username     │         │ name         │         │ suite_id(FK)││
│  │ email        │         │ description  │◄────────│ name        ││
│  │ password_hash│         │ framework_type│        │ description ││
│  │ is_active    │         │ config (JSON)│         │ test_code   ││
│  │ is_superuser │         │ is_active    │         │ test_type   ││
│  │ created_at   │         │ created_by(FK)◄────────│ priority    ││
│  │ updated_at   │         │ created_at   │         │ tags        ││
│  └──────────────┘         │ updated_at   │         │ is_active   ││
│                           └──────────────┘         │ created_at  ││
│                                  │                 │ updated_at  ││
│                                  │                 └─────────────┘│
│                                  │                        │       │
│                                  ▼                        ▼       │
│                           ┌──────────────┐         ┌─────────────┐│
│                           │test_execution│         │test_execution││
│                           ├──────────────┤         │_details     ││
│                           │ id (PK)      │         ├─────────────┤│
│                           │ suite_id(FK) │◄────────│ id (PK)     ││
│                           │ execution_type│        │ execution_id││
│                           │ environment  │         │ test_case_id││
│                           │ executed_by  │         │ status      ││
│                           │ started_at   │         │ started_at  ││
│                           │ ended_at     │         │ ended_at    ││
│                           │ duration     │         │ duration    ││
│                           │ status       │         │ error_msg   ││
│                           │ total_tests  │         │ screenshot  ││
│                           │ passed_tests │         │ logs        ││
│                           │ failed_tests │         └─────────────┘│
│                           │ skipped_tests│                        │
│                           │ results(JSON)│                        │
│                           │ artifacts_path│                       │
│                           └──────────────┘                        │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Relationships

- **User** 1:N **TestSuite** (A user can create many suites)
- **TestSuite** 1:N **TestCase** (A suite contains many cases)
- **TestSuite** 1:N **TestExecution** (A suite has many executions)
- **TestExecution** 1:N **TestExecutionDetail** (An execution has many case results)
- **TestCase** 1:N **TestExecutionDetail** (A case appears in many executions)

---

## Deployment Architecture

### Docker Compose Setup

```
┌────────────────────────────────────────────────────────────────────┐
│                         Docker Network                             │
│                        (qa_framework_net)                          │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    Nginx (Reverse Proxy)                     │ │
│  │                      Port: 80, 443                           │ │
│  │          Routes: / → Frontend, /api → Backend               │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              │                                     │
│           ┌──────────────────┼──────────────────┐                 │
│           ▼                  ▼                  ▼                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐          │
│  │   Frontend   │   │   Backend    │   │   Database   │          │
│  │    (Node)    │   │  (FastAPI)   │   │ (PostgreSQL) │          │
│  │   Port 3000  │   │   Port 8000  │   │   Port 5432  │          │
│  └──────────────┘   └──────┬───────┘   └──────────────┘          │
│                            │                                       │
│                            ▼                                       │
│                     ┌──────────────┐                              │
│                     │    Redis     │                              │
│                     │    Cache     │                              │
│                     │   Port 6379  │                              │
│                     └──────────────┘                              │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Production Deployment

```
┌────────────────────────────────────────────────────────────────────┐
│                           Kubernetes                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                        Ingress                                │ │
│  │              (SSL, Load Balancing, Routing)                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────┐  ┌────────────────────┐                  │
│  │  Frontend Pods     │  │   Backend Pods     │                  │
│  │  (3 Replicas)      │  │   (3 Replicas)     │                  │
│  │                    │  │                    │                  │
│  │  ┌────┐ ┌────┐    │  │  ┌────┐ ┌────┐    │                  │
│  │  │Pod1│ │Pod2│... │  │  │Pod1│ │Pod2│... │                  │
│  │  └────┘ └────┘    │  │  └────┘ └────┘    │                  │
│  └────────────────────┘  └────────────────────┘                  │
│                                                                     │
│  ┌────────────────────┐  ┌────────────────────┐                  │
│  │ PostgreSQL Stateful│  │   Redis Cluster    │                  │
│  │       Set          │  │   (3 Masters)      │                  │
│  │  ┌───────────┐     │  │  ┌───────────┐     │                  │
│  │  │ Primary   │     │  │  │ Master 1  │     │                  │
│  │  │ Replica 1 │     │  │  │ Master 2  │     │                  │
│  │  │ Replica 2 │     │  │  │ Master 3  │     │                  │
│  │  └───────────┘     │  │  └───────────┘     │                  │
│  └────────────────────┘  └────────────────────┘                  │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

### Security Layers

```
┌────────────────────────────────────────────────────────────────────┐
│                      Security Architecture                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Layer 1: Network Security                                          │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • HTTPS/TLS 1.3                                             │ │
│  │  • WAF (Web Application Firewall)                            │ │
│  │  • DDoS Protection                                           │ │
│  │  • IP Whitelisting                                           │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Layer 2: Application Security                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • JWT Authentication (HS256)                                │ │
│  │  • Input Validation (Pydantic)                               │ │
│  │  • Rate Limiting                                             │ │
│  │  • CORS Policy                                               │ │
│  │  • Request Size Limits                                       │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Layer 3: Data Security                                             │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • Password Hashing (bcrypt)                                 │ │
│  │  • Database Encryption (at rest)                             │ │
│  │  • SQL Injection Prevention (SQLAlchemy)                     │ │
│  │  • Sensitive Data Masking in Logs                            │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Layer 4: Infrastructure Security                                   │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • Container Security Scanning                               │ │
│  │  • Secrets Management                                        │ │
│  │  • Network Policies                                          │ │
│  │  • Resource Limits                                           │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  Client  │      │   API    │      │   Auth   │      │   DB     │
└────┬─────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │                 │                 │                 │
     │ POST /login     │                 │                 │
     │ {credentials}   │                 │                 │
     │────────────────>│                 │                 │
     │                 │                 │                 │
     │                 │ Validate        │                 │
     │                 │ Credentials     │                 │
     │                 │────────────────>│                 │
     │                 │                 │                 │
     │                 │                 │ Check Password  │
     │                 │                 │ (bcrypt)        │
     │                 │                 │────────────────>│
     │                 │                 │                 │
     │                 │                 │ User Valid      │
     │                 │                 │<────────────────│
     │                 │                 │                 │
     │                 │                 │ Generate JWT    │
     │                 │                 │ (HS256, 30min)  │
     │                 │<────────────────│                 │
     │                 │                 │                 │
     │ {token}         │                 │                 │
     │<────────────────│                 │                 │
     │                 │                 │                 │
     │ GET /resource   │                 │                 │
     │ Authorization:  │                 │                 │
     │ Bearer <token>  │                 │                 │
     │────────────────>│                 │                 │
     │                 │                 │                 │
     │                 │ Verify Token    │                 │
     │                 │ (Decode JWT)    │                 │
     │                 │                 │                 │
     │                 │ Get User from   │                 │
     │                 │ Cache/DB        │                 │
     │                 │                 │                 │
     │                 │ [Proceed]       │                 │
     │                 │                 │                 │
     │ {data}          │                 │                 │
     │<────────────────│                 │                 │
     │                 │                 │                 │
```

---

## Monitoring Architecture

### Observability Stack

```
┌────────────────────────────────────────────────────────────────────┐
│                     Monitoring & Observability                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Application Metrics                                                │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │
│  │   Prometheus   │  │     Grafana    │  │  Alert Manager │       │
│  │   (Metrics)    │  │ (Dashboards)   │  │   (Alerts)     │       │
│  └───────┬────────┘  └────────────────┘  └────────────────┘       │
│          │                                                          │
│          │ Pulls metrics from /metrics endpoint                     │
│          ▼                                                          │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI Application                       │ │
│  │              (Prometheus Client Instrumentation)             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Logging                                                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐       │
│  │  Structured    │  │    Logstash    │  │ Elasticsearch  │       │
│  │    Logs        │──►│  (Processing)  │──►│   (Storage)    │       │
│  │  (JSON)        │  │                │  │                │       │
│  └────────────────┘  └────────────────┘  └────────────────┘       │
│                                                     │               │
│                                                     ▼               │
│                                            ┌────────────────┐      │
│                                            │     Kibana     │      │
│                                            │  (Log Viewer)  │      │
│                                            └────────────────┘      │
│                                                                     │
│  Tracing (Optional)                                                 │
│  ┌────────────────┐  ┌────────────────┐                            │
│  │   OpenTelemetry│  │      Jaeger    │                            │
│  │   Instrumentation  │  (Trace View)  │                            │
│  └────────────────┘  └────────────────┘                            │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Performance Considerations

### Caching Strategy

```
┌────────────────────────────────────────────────────────────────────┐
│                       Caching Layers                               │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  L1: Application Cache (Redis)                                      │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • User sessions           TTL: 30 min                      │ │
│  │  • Suite configurations    TTL: 10 min                      │ │
│  │  • Dashboard stats         TTL: 1 min                       │ │
│  │  • Execution results       TTL: 5 min                       │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  L2: Database Query Cache                                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • Frequently accessed queries                              │ │
│  │  • Connection pooling (asyncpg)                             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  L3: HTTP Cache (Client-side)                                       │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • Static assets            Cache-Control: max-age=3600      │ │
│  │  • API responses (GET)      ETag support                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | React | 18.x |
| Backend | FastAPI | 0.100+ |
| Database | PostgreSQL | 15+ |
| Cache | Redis | 7+ |
| Auth | JWT (python-jose) | Latest |
| ORM | SQLAlchemy | 2.0+ |
| Migration | Alembic | Latest |
| Container | Docker | 24+ |
| Orchestration | Docker Compose / Kubernetes | - |
| Monitoring | Prometheus + Grafana | Latest |

---

## Additional Resources

- [API Guide](api-guide.md) - Complete API documentation
- [API Examples](api-examples.md) - Code examples and use cases
- [Contributing](../CONTRIBUTING.md) - Development guidelines
- [README](../README.md) - Project overview
