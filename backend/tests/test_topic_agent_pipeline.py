from app.schemas.topic_agent import TopicAgentConstraintSet, TopicAgentExploreRequest
from app.services.topic_agent.pipeline import run_topic_agent_pipeline
from app.services.topic_agent.providers import MockTopicAgentEvidenceProvider


def test_topic_agent_pipeline_returns_structured_session_response():
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        seed_idea="narrow benchmark-driven topic",
        constraints=TopicAgentConstraintSet(
            time_budget_months=6,
            resource_level="student",
            preferred_style="benchmark-driven",
        ),
    )

    response = run_topic_agent_pipeline(
        request,
        provider=MockTopicAgentEvidenceProvider(),
    )

    assert response.user_input.interest == request.interest
    assert response.framing_result.normalized_topic == request.interest
    assert len(response.evidence_records) == 3
    assert len(response.candidate_topics) == 3
    assert response.comparison_result.candidate_assessments[0]["candidate_id"] == "candidate_1"
    assert response.convergence_result.recommended_candidate_id == "candidate_1"
    assert [event.stage for event in response.trace] == [
        "frame_problem",
        "retrieve_evidence",
        "synthesize_landscape",
        "generate_candidates",
        "compare_candidates",
        "converge_recommendation",
    ]
