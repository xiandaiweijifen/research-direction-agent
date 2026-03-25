from app.schemas.topic_agent import TopicAgentConstraintSet, TopicAgentExploreRequest
from app.services.topic_agent.pipeline import run_topic_agent_pipeline
from app.services.topic_agent.providers import (
    MockTopicAgentEvidenceProvider,
    TopicAgentEvidenceRetrievalResult,
)
from app.schemas.topic_agent import TopicAgentEvidenceDiagnostics, TopicAgentSourceRecord


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
    assert response.evidence_diagnostics.used_provider == "mock"
    assert response.evidence_diagnostics.record_count == 3
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


def test_topic_agent_pipeline_changes_recommendation_for_applied_tight_constraints():
    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        problem_domain="medical AI",
        seed_idea="applied topic",
        constraints=TopicAgentConstraintSet(
            time_budget_months=4,
            resource_level="student",
            preferred_style="applied",
        ),
    )

    response = run_topic_agent_pipeline(
        request,
        provider=MockTopicAgentEvidenceProvider(),
    )

    assert response.convergence_result.recommended_candidate_id == "candidate_2"
    assert response.candidate_topics[1].title == "Applied Method Transfer Under Practical Constraints"
    assert response.evidence_diagnostics.used_provider == "mock"
    assert response.comparison_result.summary.startswith(
        "Candidate 2 is strongest for applied feasibility"
    )


def test_topic_agent_pipeline_maps_candidate_supporting_ids_from_current_evidence():
    class StaticProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="arxiv_a",
                    title="Paper A",
                    source_type="paper",
                    source_tier="B",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://arxiv.org/abs/a",
                    url="https://arxiv.org/abs/a",
                    summary="Paper A summary",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="arxiv_b",
                    title="Paper B",
                    source_type="paper",
                    source_tier="B",
                    year=2024,
                    authors_or_publisher="Author B",
                    identifier="https://arxiv.org/abs/b",
                    url="https://arxiv.org/abs/b",
                    summary="Paper B summary",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="arxiv_c",
                    title="Paper C",
                    source_type="paper",
                    source_tier="B",
                    year=2023,
                    authors_or_publisher="Author C",
                    identifier="https://arxiv.org/abs/c",
                    url="https://arxiv.org/abs/c",
                    summary="Paper C summary",
                    relevance_reason="Test record",
                ),
            ]
            return TopicAgentEvidenceRetrievalResult(
                records=records,
                diagnostics=TopicAgentEvidenceDiagnostics(
                    requested_provider="static",
                    used_provider="static",
                    fallback_used=False,
                    fallback_reason=None,
                    record_count=3,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="medical reasoning",
        constraints=TopicAgentConstraintSet(),
    )

    response = run_topic_agent_pipeline(request, provider=StaticProvider())

    assert response.candidate_topics[0].supporting_source_ids == ["arxiv_a", "arxiv_b"]
    assert response.candidate_topics[1].supporting_source_ids == ["arxiv_a", "arxiv_c"]
    assert response.candidate_topics[2].supporting_source_ids == ["arxiv_b", "arxiv_c"]
