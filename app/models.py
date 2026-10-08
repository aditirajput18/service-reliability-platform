from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from .database import Base


class Service(Base):
    __tablename__ = "services"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    url = Column(
        String(500),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    last_status = Column(
        String(20),
        nullable=True
    )

    last_http_status = Column(
        Integer,
        nullable=True
    )

    last_response_time_ms = Column(
        Float,
        nullable=True
    )

    last_checked_at = Column(
        DateTime,
        nullable=True
    )
class HealthCheck(Base):
    __tablename__ = "health_checks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    service_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    status = Column(
        String(20),
        nullable=False
    )

    http_status = Column(
        Integer,
        nullable=True
    )

    response_time_ms = Column(
        Float,
        nullable=True
    )

    checked_at = Column(
        DateTime,
        nullable=False
    )
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    service_id = Column(Integer, nullable=False, index=True)

    alert_type = Column(String(50), nullable=False)

    status = Column(String(20), nullable=False, default="ACTIVE")

    message = Column(String(500), nullable=False)

    created_at = Column(DateTime, nullable=False)

    resolved_at = Column(DateTime, nullable=True)
class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, nullable=False, index=True)
    alert_id = Column(Integer, nullable=False, index=True)

    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="OPEN"
    )

    created_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
