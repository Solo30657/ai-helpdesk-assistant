from app.schemas import Category, Priority, RoutingTeam, TicketClassification


def test_ticket_classification_schema_validates() -> None:
    result = TicketClassification(
        category=Category.security,
        subcategory="Phishing or Suspicious Link",
        priority=Priority.p1,
        routing_team=RoutingTeam.security_ops,
        summary="User clicked a suspicious link and may be compromised.",
        reasoning="Potential compromise and possible wider impact justify urgent security review.",
        suggested_response="Thank you for reporting this right away. We have escalated your ticket to Security Operations for immediate review.",
        confidence_score=0.96,
        needs_human_review=False,
    )

    assert result.priority == Priority.p1
    assert result.routing_team == RoutingTeam.security_ops
