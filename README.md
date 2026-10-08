# Service Reliability Platform (SRP)

A lightweight Service Reliability Platform built to demonstrate
practical DevOps and SRE engineering concepts.

SRP will eventually monitor services, track uptime and response
times, detect failures, manage incidents, send alerts, and
demonstrate recovery and rollback.

The project is being developed incrementally in phases so that
each layer can be tested and understood independently.

---

## Phase 1 - Application Foundation

The current phase focuses only on the application foundation.

### Implemented

- FastAPI backend
- SQLite database
- SQLAlchemy ORM
- Service registration
- Service CRUD APIs
- Input validation
- Basic web dashboard
- Automated pytest tests
- Isolated test database

### Not implemented yet

The following features belong to later phases:

- Service health monitoring
- Uptime monitoring
- Response-time monitoring
- Alerting
- Incident management
- Prometheus
- Grafana
- Docker
- Docker Compose
- GitHub Actions
- Trivy
- Kubernetes

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application language |
| FastAPI | REST API framework |
| SQLAlchemy | Database ORM |
| SQLite | Local persistence |
| HTML/CSS/JavaScript | Dashboard |
| pytest | Automated testing |
| Git | Version control |

---

## Project Structure

```text
service-reliability-platform/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── services.py
│   │
│   └── templates/
│       └── dashboard.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
│
├── tests/
│   ├── __init__.py
│   └── test_services.py
│
├── .gitignore
├── requirements.txt
└── README.md
