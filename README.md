 Service Reliability Platform (SRP)

A portfolio-grade Service Reliability Platform built to demonstrate practical DevOps and Site Reliability Engineering (SRE) skills using free, locally runnable tools.

SRP monitors registered services, tracks health and response times, detects repeated failures, creates and resolves alerts, manages incidents, exposes Prometheus metrics, and demonstrates containerization and Kubernetes operations.

## Implemented Features

- FastAPI REST API and web dashboard
- Service registration, validation, and CRUD operations
- Automated health checks and response-time tracking
- Health-check history and service metrics
- Alerts after consecutive failures and automatic recovery resolution
- Incident lifecycle management
- SQLite persistence using SQLAlchemy
- Docker and Docker Compose
- GitHub Actions CI/CD
- Trivy vulnerability scanning
- Prometheus metrics and Grafana dashboards
- Kubernetes deployment using kind
- Kubernetes ConfigMap, PersistentVolumeClaim, and health probes
- Pod recovery and persistent-data verification
- Automated pytest suite

## Technology Stack

| Technology | Purpose |
|---|---|
| Python, FastAPI | Application and REST API |
| SQLAlchemy, SQLite | Data persistence |
| HTML, CSS, JavaScript | Dashboard |
| pytest | Automated testing |
| Docker, Docker Compose | Containerization |
| GitHub Actions | CI/CD |
| Trivy | Container vulnerability scanning |
| Prometheus | Metrics collection |
| Grafana | Monitoring dashboards |
| Kubernetes, kind, kubectl | Local orchestration |
| Git and GitHub | Version control and source hosting |

## Project Structure

```text
service-reliability-platform/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── monitoring.py
│   └── routers/
├── tests/
├── static/
├── k8s/
│   ├── kind-config.yaml
│   ├── srp-configmap.yaml
│   ├── srp-pvc.yaml
│   ├── srp-deployment.yaml
│   └── srp-service.yaml
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
