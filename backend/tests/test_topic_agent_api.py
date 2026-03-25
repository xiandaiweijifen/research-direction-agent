from fastapi.testclient import TestClient

from app.main import app


def test_topic_agent_explore_creates_session_with_mock_outputs(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_service.TOPIC_AGENT_STORE_PATH",
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
    assert len(payload["evidence_records"]) == 3
    assert len(payload["candidate_topics"]) == 3
    assert payload["comparison_result"]["candidate_assessments"]
    assert payload["convergence_result"]["recommended_candidate_id"] == "candidate_1"
    assert payload["confidence_summary"]["candidate_separation"] == "high"
    assert payload["confidence_summary"]["rationale"]
    assert payload["trace"]
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
        "app.services.topic_agent.topic_agent_service.TOPIC_AGENT_STORE_PATH",
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


def test_topic_agent_refine_updates_existing_session(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_service.TOPIC_AGENT_STORE_PATH",
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


def test_topic_agent_explore_rejects_empty_interest(workspace_tmp_path, monkeypatch):
    session_store_path = workspace_tmp_path / "topic_agent_sessions.json"
    monkeypatch.setattr(
        "app.services.topic_agent.topic_agent_service.TOPIC_AGENT_STORE_PATH",
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
