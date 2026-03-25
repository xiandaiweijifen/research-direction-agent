from fastapi import APIRouter, HTTPException

from app.schemas.topic_agent import (
    TopicAgentExploreRequest,
    TopicAgentRefineRequest,
    TopicAgentSessionListResponse,
    TopicAgentSessionResponse,
)
from app.services.topic_agent import (
    create_topic_agent_session,
    get_topic_agent_session,
    list_topic_agent_sessions,
    refine_topic_agent_session,
)

router = APIRouter(tags=["topic-agent"])


@router.post("/topic-agent/explore", response_model=TopicAgentSessionResponse)
def explore_topic(request: TopicAgentExploreRequest) -> TopicAgentSessionResponse:
    try:
        return create_topic_agent_session(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/topic-agent/sessions", response_model=TopicAgentSessionListResponse)
def get_topic_sessions(limit: int = 20) -> TopicAgentSessionListResponse:
    try:
        return list_topic_agent_sessions(limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/topic-agent/sessions/{session_id}", response_model=TopicAgentSessionResponse)
def get_topic_session(session_id: str) -> TopicAgentSessionResponse:
    try:
        return get_topic_agent_session(session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="topic_agent_session_not_found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/topic-agent/sessions/{session_id}/refine", response_model=TopicAgentSessionResponse)
def refine_topic_session(
    session_id: str,
    request: TopicAgentRefineRequest,
) -> TopicAgentSessionResponse:
    try:
        return refine_topic_agent_session(session_id, request)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="topic_agent_session_not_found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
