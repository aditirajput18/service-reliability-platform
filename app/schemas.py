from datetime import datetime 
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ServiceBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    url: HttpUrl

    description: str | None = Field(
        default=None,
        max_length=500
    )


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    url: HttpUrl | None = None

    description: str | None = Field(
        default=None,
        max_length=500
    )


class ServiceResponse(ServiceBase):
    id: int

    last_status: str | None = None

    last_http_status: int | None = None

    last_response_time_ms: float | None = None

    last_checked_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )
class ServiceMetricsResponse(BaseModel):
    service_id: int
    total_checks: int
    successful_checks: int
    failed_checks: int
    uptime_percentage: float
    average_response_time_ms: float
class HealthCheckResponse(BaseModel):
    id: int
    service_id: int
    status: str
    http_status: int | None = None
    response_time_ms: float | None = None
    checked_at: datetime

    model_config = ConfigDict(from_attributes=True)
class AlertResponse(BaseModel):
    id: int
    service_id: int
    alert_type: str
    status: str
    message: str
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
class IncidentResponse(BaseModel):
    id: int
    service_id: int
    alert_id: int
    title: str
    description: str
    status: str
    created_at: datetime
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

class IncidentStatusUpdate(BaseModel):
    status: str
