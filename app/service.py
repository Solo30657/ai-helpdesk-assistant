import json
from typing import Any

from pydantic import ValidationError

from app.config import get_settings
from app.prompt import SYSTEM_PROMPT, build_user_prompt
from app.schemas import Category, Priority, RoutingTeam, TicketClassification


class TicketClassificationError(RuntimeError):
    """Raised when the model response cannot be parsed or validated."""


class HelpdeskTriageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        if settings.openai_api_key:
            from openai import OpenAI

            self.client = OpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None

    def classify_ticket(self, ticket_text: str) -> TicketClassification:
        if not self.client:
            return self._mock_classification(ticket_text)

        schema = TicketClassification.model_json_schema()

        response = self.client.responses.create(
            model=self.settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(ticket_text)},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "ticket_classification",
                    "strict": True,
                    "schema": schema,
                }
            },
        )

        output_text = getattr(response, "output_text", "")
        if not output_text:
            raise TicketClassificationError("The model returned an empty response.")

        try:
            payload: Any = json.loads(output_text)
            return TicketClassification.model_validate(payload)
        except json.JSONDecodeError as exc:
            raise TicketClassificationError("The model did not return valid JSON.") from exc
        except ValidationError as exc:
            raise TicketClassificationError("The model returned JSON that failed schema validation.") from exc

    def _mock_classification(self, ticket_text: str) -> TicketClassification:
        text = ticket_text.lower()

        if any(word in text for word in ["phishing", "suspicious", "malware", "virus", "clicked a link"]):
            return TicketClassification(
                category=Category.security,
                subcategory="Phishing or Suspicious Link",
                priority=Priority.p1,
                routing_team=RoutingTeam.security_ops,
                summary="Potential phishing or malware-related incident reported.",
                reasoning="The ticket suggests possible compromise or suspicious activity, which requires urgent review.",
                suggested_response="Thank you for reporting this immediately. Your ticket has been escalated to Security Operations for urgent review. Please avoid clicking any additional links and wait for further guidance from the security team.",
                confidence_score=0.95,
                needs_human_review=False,
            )

        if any(word in text for word in ["vpn", "remote", "cannot connect"]):
            return TicketClassification(
                category=Category.network_vpn,
                subcategory="VPN Connectivity Issue",
                priority=Priority.p2,
                routing_team=RoutingTeam.network_team,
                summary="User cannot connect to VPN and may be blocked from remote work.",
                reasoning="VPN issues often block access to internal systems and are usually high impact for remote users.",
                suggested_response="Thank you for reporting the issue. Your VPN access problem has been routed to the Network Team. Please reply with any error message you see and confirm whether you recently changed your password.",
                confidence_score=0.91,
                needs_human_review=False,
            )

        if any(word in text for word in ["password", "reset", "locked out", "login", "log in"]):
            return TicketClassification(
                category=Category.password_reset,
                subcategory="Login or Password Issue",
                priority=Priority.p3,
                routing_team=RoutingTeam.iam,
                summary="User is experiencing an account access or password-related issue.",
                reasoning="This appears to be a standard access issue affecting one user.",
                suggested_response="Thank you for contacting the helpdesk. Your account access issue has been routed to the Identity & Access Management team. Please confirm your username and whether you are seeing a specific error message.",
                confidence_score=0.89,
                needs_human_review=False,
            )

        if any(word in text for word in ["laptop", "blue screen", "restarting", "hardware"]):
            return TicketClassification(
                category=Category.hardware,
                subcategory="Laptop or Desktop Issue",
                priority=Priority.p2,
                routing_team=RoutingTeam.desktop_support,
                summary="User reported a device stability or hardware issue.",
                reasoning="The ticket suggests a hardware problem that may block productivity.",
                suggested_response="Thank you for reporting the device issue. Your ticket has been routed to Desktop Support for review. Please share your asset tag and note whether the issue started after an update or physical movement of the device.",
                confidence_score=0.88,
                needs_human_review=False,
            )

        return TicketClassification(
            category=Category.other,
            subcategory="General Support Request",
            priority=Priority.p3,
            routing_team=RoutingTeam.service_desk,
            summary="General IT support request requiring initial triage.",
            reasoning="The request does not clearly match a more specific rule, so it should be reviewed by the Service Desk.",
            suggested_response="Thank you for contacting the IT helpdesk. Your request has been received and routed to the Service Desk for initial review. We may follow up if additional details are needed.",
            confidence_score=0.72,
            needs_human_review=True,
        )
