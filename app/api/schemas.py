"""Request and response schemas for the serving API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "v1"
CONTRACT_TYPES = ("month_to_month", "one_year", "two_year")
INTERNET_SERVICES = ("dsl", "fiber_optic")
PAYMENT_METHODS = ("bank_transfer", "credit_card", "electronic_check")


class PredictionRequest(BaseModel):
    """Validated single-row customer churn prediction request."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["v1"] = Field(
        default=SCHEMA_VERSION,
        description="Inference schema version.",
    )
    tenure_months: int = Field(ge=0, le=120)
    monthly_charges: float = Field(ge=0)
    total_charges: float = Field(ge=0)
    contract_type: Literal["month_to_month", "one_year", "two_year"]
    internet_service: Literal["dsl", "fiber_optic"]
    payment_method: Literal["bank_transfer", "credit_card", "electronic_check"]
    is_senior: bool


class PredictionResponse(BaseModel):
    """Successful single prediction response."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["success"] = "success"
    prediction: Literal[0, 1]
    probability: float = Field(ge=0, le=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    latency_ms: float = Field(ge=0)


class ServingErrorResponse(BaseModel):
    """Structured serving error response."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["failed"] = "failed"
    error: str = Field(min_length=1)
    request_id: str | None = None
