from fastapi.testclient import TestClient
import json

from app.main import app


def test_topic_agent_explore_creates_session_with_mock_outputs(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_runtime.TOPIC_AGENT_STORE_PATH",
        session_store_path,
    )

    client = TestClient(app)
    response = client.post(
        "/api/topic-agent/explore",
        json={
            "interest": "trustworthy multimodal reasoning in medical imaging",
            "problem_domain": "medical AI",
            "seed_idea": "I want a narrow and feasible research topic.",
            "constraints": {
                "time_budget_months": 6,
                "resource_level": "student",
                "preferred_style": "benchmark-driven",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"]
    assert payload["user_input"]["interest"] == "trustworthy multimodal reasoning in medical imaging"
    assert payload["framing_result"]["normalized_topic"] == "trustworthy multimodal reasoning in medical imaging"
    assert len(payload["evidence_records"]) >= 3
    assert len(payload["candidate_topics"]) == 3
    assert payload["candidate_topics"][0]["origin_signals"]
    assert payload["comparison_result"]["candidate_assessments"]
    assert payload["comparison_result"]["candidate_assessments"][0]["novelty_reason"]
    assert payload["convergence_result"]["recommended_candidate_id"] == "candidate_1"
    assert payload["confidence_summary"]["candidate_separation"] == "high"
    assert payload["evidence_diagnostics"]["used_provider"] in {"mock", "arxiv", "openalex"}
    assert payload["evidence_diagnostics"]["record_count"] == len(payload["evidence_records"])
    assert isinstance(payload["evidence_diagnostics"]["cache_hit"], bool)
    assert "query_count" in payload["evidence_diagnostics"]
    assert "provider_latency_ms" in payload["evidence_diagnostics"]
    assert "query_diagnostics" in payload["evidence_diagnostics"]
    assert payload["confidence_summary"]["rationale"]
    assert payload["trace"]
    assert payload["evidence_presentation"]["source_facts"]
    assert payload["evidence_presentation"]["system_synthesis"]
    assert payload["evidence_presentation"]["tentative_inferences"]
    assert payload["evidence_presentation"]["tentative_inferences"][0]["uncertainty_reason"]
    assert isinstance(
        payload["evidence_presentation"]["tentative_inferences"][0]["missing_evidence"],
        list,
    )
    assert payload["human_confirmations"]
    assert isinstance(payload["clarification_suggestions"], list)
    assert [event["stage"] for event in payload["trace"]] == [
        "frame_problem",
        "retrieve_evidence",
        "synthesize_landscape",
        "generate_candidates",
        "compare_candidates",
        "converge_recommendation",
    ]


def test_topic_agent_sessions_list_and_get_return_persisted_session(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_runtime.TOPIC_AGENT_STORE_PATH",
        session_store_path,
    )

    client = TestClient(app)
    create_response = client.post(
        "/api/topic-agent/explore",
        json={
            "interest": "retrieval systems for scientific discovery",
            "constraints": {},
        },
    )
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]

    list_response = client.get("/api/topic-agent/sessions")
    assert list_response.status_code == 200
    list_payload = list_response.json()
    assert len(list_payload["sessions"]) == 1
    assert list_payload["sessions"][0]["session_id"] == session_id
    assert list_payload["sessions"][0]["candidate_count"] == 3

    get_response = client.get(f"/api/topic-agent/sessions/{session_id}")
    assert get_response.status_code == 200
    get_payload = get_response.json()
    assert get_payload["session_id"] == session_id
    assert get_payload["convergence_result"]["backup_candidate_id"] == "candidate_2"
    assert len(get_payload["comparison_result"]["candidate_assessments"]) == 3


def test_topic_agent_session_store_prunes_old_sessions(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_runtime.TOPIC_AGENT_STORE_PATH",
        session_store_path,
    )
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_runtime.TOPIC_AGENT_SESSION_HISTORY_LIMIT",
        2,
    )

    client = TestClient(app)
    for interest in ["topic one", "topic two", "topic three"]:
        response = client.post(
            "/api/topic-agent/explore",
            json={
                "interest": interest,
                "constraints": {},
            },
        )
        assert response.status_code == 200

    list_response = client.get("/api/topic-agent/sessions?limit=10")
    assert list_response.status_code == 200
    payload = list_response.json()
    assert len(payload["sessions"]) == 2
    assert payload["sessions"][0]["interest"] == "topic three"
    assert payload["sessions"][1]["interest"] == "topic two"


def test_topic_agent_refine_updates_existing_session(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_runtime.TOPIC_AGENT_STORE_PATH",
        session_store_path,
    )

    client = TestClient(app)
    create_response = client.post(
        "/api/topic-agent/explore",
        json={
            "interest": "agentic literature review",
            "constraints": {},
        },
    )
    assert create_response.status_code == 200
    original_payload = create_response.json()
    session_id = original_payload["session_id"]

    refine_response = client.post(
        f"/api/topic-agent/sessions/{session_id}/refine",
        json={
            "constraints": {
                "time_budget_months": 4,
                "resource_level": "student",
                "preferred_style": "applied",
            }
        },
    )

    assert refine_response.status_code == 200
    refined_payload = refine_response.json()
    assert refined_payload["session_id"] == session_id
    assert refined_payload["user_input"]["constraints"]["time_budget_months"] == 4
    assert refined_payload["user_input"]["constraints"]["preferred_style"] == "applied"
    assert refined_payload["created_at"] == original_payload["created_at"]
    assert refined_payload["confidence_summary"]["source_quality"] == "medium_high"
    assert refined_payload["evidence_diagnostics"]["record_count"] == len(
        refined_payload["evidence_records"]
    )
    assert (
        refined_payload["candidate_topics"][1]["title"]
        == "Applied Method Transfer Under Practical Constraints"
    )
    assert refined_payload["convergence_result"]["recommended_candidate_id"] == "candidate_2"
    assert "reusable baseline" in refined_payload["convergence_result"]["rationale"].lower()
    assert "Applied Method Transfer Under Practical Constraints" in refined_payload["comparison_result"]["summary"]
    joined_confirmations = " ".join(refined_payload["human_confirmations"]).lower()
    assert "project timeline" not in joined_confirmations
    assert "resource level" not in joined_confirmations
    assert "leading direction" in joined_confirmations
    assert refined_payload["clarification_suggestions"] == []


def test_topic_agent_explore_rejects_empty_interest(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_runtime.TOPIC_AGENT_STORE_PATH",
        session_store_path,
    )

    client = TestClient(app)
    response = client.post(
        "/api/topic-agent/explore",
        json={
            "interest": "   ",
            "constraints": {},
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "interest_must_not_be_empty"


def test_topic_agent_session_endpoints_backfill_missing_legacy_diagnostics(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_runtime.TOPIC_AGENT_STORE_PATH",
        session_store_path,
    )
    legacy_session = {
        "session_id": "legacy-session",
        "created_at": "2026-03-26T14:42:24.334804+00:00",
        "updated_at": "2026-03-26T14:43:54.322883+00:00",
        "user_input": {
            "interest": "medical reasoning",
            "problem_domain": None,
            "seed_idea": None,
            "constraints": {
                "time_budget_months": 6,
                "resource_level": "student",
                "preferred_style": "applied",
                "notes": None,
            },
        },
        "framing_result": {
            "normalized_topic": "medical reasoning",
            "extracted_constraints": {
                "time_budget_months": "6",
                "resource_level": "student",
                "preferred_style": "applied",
            },
            "missing_clarifications": [],
            "search_questions": [
                "What are the main research themes in medical reasoning?",
            ],
        },
        "evidence_records": [],
        "landscape_summary": {
            "themes": [],
            "active_methods": [],
            "likely_gaps": [],
            "saturated_areas": [],
        },
        "candidate_topics": [],
        "comparison_result": {
            "dimensions": [],
            "summary": "summary",
            "candidate_assessments": [],
        },
        "convergence_result": {
            "recommended_candidate_id": "candidate_1",
            "backup_candidate_id": None,
            "rationale": "rationale",
            "manual_checks": [],
        },
        "human_confirmations": [],
        "clarification_suggestions": [],
        "evidence_presentation": {
            "source_facts": [],
            "system_synthesis": [],
            "tentative_inferences": [],
        },
        "trace": [],
        "confidence_summary": {
            "evidence_coverage": "low",
            "source_quality": "medium",
            "candidate_separation": "low",
            "conflict_level": "low",
            "rationale": [],
        },
    }
    session_store_path.write_text(json.dumps([legacy_session]), encoding="utf-8")

    client = TestClient(app)

    list_response = client.get("/api/topic-agent/sessions")
    assert list_response.status_code == 200
    assert list_response.json()["sessions"][0]["session_id"] == "legacy-session"

    get_response = client.get("/api/topic-agent/sessions/legacy-session")
    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["session_id"] == "legacy-session"
    assert payload["evidence_diagnostics"] == {
        "requested_provider": "unknown",
        "used_provider": "unknown",
        "fallback_used": False,
        "fallback_reason": None,
        "record_count": 0,
        "cache_hit": False,
        "query_count": 0,
        "provider_latency_ms": None,
        "slowest_query": None,
        "slowest_query_latency_ms": None,
        "query_diagnostics": [],
    }


def test_topic_agent_session_endpoints_backfill_missing_legacy_evidence_presentation(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_runtime.TOPIC_AGENT_STORE_PATH",
        session_store_path,
    )
    legacy_session = {
        "session_id": "legacy-presentation",
        "created_at": "2026-03-26T14:42:24.334804+00:00",
        "updated_at": "2026-03-26T14:43:54.322883+00:00",
        "user_input": {
            "interest": "medical reasoning",
            "problem_domain": None,
            "seed_idea": None,
            "constraints": {
                "time_budget_months": 6,
                "resource_level": "student",
                "preferred_style": "applied",
                "notes": None,
            },
        },
        "framing_result": {
            "normalized_topic": "medical reasoning",
            "extracted_constraints": {
                "time_budget_months": "6",
                "resource_level": "student",
                "preferred_style": "applied",
            },
            "missing_clarifications": [],
            "search_questions": [
                "What are the main research themes in medical reasoning?"
            ],
        },
        "evidence_records": [],
        "landscape_summary": {
            "themes": [],
            "active_methods": [],
            "likely_gaps": [],
            "saturated_areas": [],
        },
        "candidate_topics": [],
        "comparison_result": {
            "dimensions": [],
            "summary": "summary",
            "candidate_assessments": [],
        },
        "convergence_result": {
            "recommended_candidate_id": "candidate_1",
            "backup_candidate_id": None,
            "rationale": "rationale",
            "manual_checks": [],
        },
        "human_confirmations": [],
        "clarification_suggestions": [],
        "trace": [],
        "confidence_summary": {
            "evidence_coverage": "low",
            "source_quality": "medium",
            "candidate_separation": "low",
            "conflict_level": "low",
            "rationale": [],
        },
        "evidence_diagnostics": {
            "requested_provider": "unknown",
            "used_provider": "unknown",
            "fallback_used": False,
            "fallback_reason": None,
            "record_count": 0,
            "cache_hit": False,
        },
    }
    session_store_path.write_text(json.dumps([legacy_session]), encoding="utf-8")

    client = TestClient(app)
    get_response = client.get("/api/topic-agent/sessions/legacy-presentation")

    assert get_response.status_code == 200
    payload = get_response.json()
    assert payload["evidence_presentation"] == {
        "source_facts": [],
        "system_synthesis": [],
        "tentative_inferences": [],
    }


def test_topic_agent_explore_returns_structured_clarification_suggestions(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_runtime.TOPIC_AGENT_STORE_PATH",
        session_store_path,
    )

    client = TestClient(app)
    response = client.post(
        "/api/topic-agent/explore",
        json={
            "interest": "medical reasoning",
            "constraints": {},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert [item["field_key"] for item in payload["clarification_suggestions"]] == [
        "time_budget",
        "resource_level",
        "preferred_style",
    ]
    assert payload["clarification_suggestions"][0]["refine_patch"] == {
        "constraints": {"time_budget_months": 6}
    }
