from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.schemas import TicketRequest, TicketResponse
from app.service import HelpdeskTriageService, TicketClassificationError

settings = get_settings()
service = HelpdeskTriageService()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered IT helpdesk ticket triage API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment, "model": settings.openai_model}


@app.post("/classify", response_model=TicketResponse)
def classify_ticket(payload: TicketRequest) -> TicketResponse:
    try:
        result = service.classify_ticket(payload.ticket_text)
        return TicketResponse(ticket_id=payload.ticket_id, result=result)
    except TicketClassificationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
