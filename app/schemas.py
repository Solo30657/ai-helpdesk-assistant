from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Category(str, Enum):
    account_access = "Account Access"
    password_reset = "Password Reset"
    hardware = "Hardware"
    software = "Software"
    network_vpn = "Network / VPN"
    email = "Email"
    security = "Security"
    printer = "Printer"
    new_user_onboarding = "New User / Onboarding"
    permissions_access_request = "Permissions / Access Request"
    mobile_device = "Mobile Device"
    other = "Other"


class Priority(str, Enum):
    p1 = "P1"
    p2 = "P2"
    p3 = "P3"
    p4 = "P4"


class RoutingTeam(str, Enum):
    service_desk = "Service Desk"
    iam = "Identity & Access Management"
    desktop_support = "Desktop Support"
    network_team = "Network Team"
    messaging_team = "Messaging Team"
    security_ops = "Security Operations"
    application_support = "Application Support"
    hr_it_onboarding = "HR IT Onboarding"


class TicketRequest(BaseModel):
    ticket_text: str = Field(..., min_length=5, max_length=5000, description="Incoming IT support ticket text")
    ticket_id: Optional[str] = Field(default=None, description="Optional external ticket identifier")


class TicketClassification(BaseModel):
    category: Category
    subcategory: str = Field(..., min_length=2, max_length=100)
    priority: Priority
    routing_team: RoutingTeam
    summary: str = Field(..., min_length=10, max_length=250)
    reasoning: str = Field(..., min_length=10, max_length=500)
    suggested_response: str = Field(..., min_length=20, max_length=700)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    needs_human_review: bool = Field(default=False)

    @field_validator("subcategory")
    @classmethod
    def normalize_subcategory(cls, value: str) -> str:
        return " ".join(value.split())


class TicketResponse(BaseModel):
    ticket_id: Optional[str] = None
    result: TicketClassification
