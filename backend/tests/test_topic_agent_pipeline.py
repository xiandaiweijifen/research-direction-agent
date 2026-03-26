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
    assert response.evidence_diagnostics.cache_hit is False
    assert response.evidence_presentation.source_facts
    assert response.evidence_presentation.system_synthesis
    assert response.evidence_presentation.tentative_inferences
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


def test_topic_agent_pipeline_dedupes_supporting_source_ids_when_evidence_is_sparse():
    class SparseProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_1",
                    title="Sparse Evidence",
                    source_type="paper",
                    source_tier="B",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://openalex.org/W1",
                    url="https://example.org/paper1",
                    summary="A single relevant paper.",
                    relevance_reason="Test record",
                )
            ]
            return TopicAgentEvidenceRetrievalResult(
                records=records,
                diagnostics=TopicAgentEvidenceDiagnostics(
                    requested_provider="static",
                    used_provider="static",
                    fallback_used=False,
                    fallback_reason=None,
                    record_count=1,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="medical reasoning",
        constraints=TopicAgentConstraintSet(),
    )

    response = run_topic_agent_pipeline(request, provider=SparseProvider())

    assert response.candidate_topics[0].supporting_source_ids == ["openalex_1"]
    assert response.candidate_topics[1].supporting_source_ids == ["openalex_1"]
    assert response.candidate_topics[2].supporting_source_ids == ["openalex_1"]


def test_topic_agent_pipeline_derives_landscape_and_candidate_cues_from_evidence():
    class EvidenceDrivenProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="arxiv_a",
                    title="Benchmarking Medical VQA Grounding For Trustworthy Multimodal Reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2026,
                    authors_or_publisher="Author A",
                    identifier="https://arxiv.org/abs/a",
                    url="https://arxiv.org/abs/a",
                    summary="A benchmark focused on radiology VQA, grounding, and trustworthy multimodal reasoning reliability.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="arxiv_b",
                    title="RJUA-Style Medical Document Question Answering And Clinical Reasoning",
                    source_type="paper",
                    source_tier="B",
                    year=2025,
                    authors_or_publisher="Author B",
                    identifier="https://arxiv.org/abs/b",
                    url="https://arxiv.org/abs/b",
                    summary="Study of document question answering, clinical reasoning, and image-text evidence use in medical reports.",
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
                    record_count=2,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        constraints=TopicAgentConstraintSet(preferred_style="benchmark-driven"),
    )

    response = run_topic_agent_pipeline(request, provider=EvidenceDrivenProvider())

    joined_themes = " ".join(response.landscape_summary.themes).lower()
    joined_methods = " ".join(response.landscape_summary.active_methods).lower()

    assert "benchmark" in joined_themes
    assert "grounding" in joined_themes
    assert (
        "document qa" in joined_themes
        or "clinical reasoning" in joined_themes
        or "radiology vqa" in joined_themes
    )
    assert "grounding" in joined_methods or "benchmark" in joined_methods
    assert "grounding" in response.candidate_topics[0].novelty_note.lower() or "trustworthy" in response.candidate_topics[0].novelty_note.lower()
    assert "benchmark" in response.candidate_topics[0].research_question.lower()
    assert "document-centric clinical reasoning" in response.candidate_topics[1].research_question.lower()


def test_topic_agent_pipeline_filters_low_quality_phrases_from_landscape_summary():
    class NoisyEvidenceProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="arxiv_a",
                    title="Deep Liver Application For Medical Imaging",
                    source_type="paper",
                    source_tier="B",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://arxiv.org/abs/a",
                    url="https://arxiv.org/abs/a",
                    summary="Application from liver imaging workflows with generic deep features.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="arxiv_b",
                    title="Multimodal Reasoning Benchmark For Medical Imaging",
                    source_type="benchmark",
                    source_tier="A",
                    year=2026,
                    authors_or_publisher="Author B",
                    identifier="https://arxiv.org/abs/b",
                    url="https://arxiv.org/abs/b",
                    summary="Benchmark for multimodal reasoning and trustworthy evaluation.",
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
                    record_count=2,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="trustworthy multimodal reasoning in medical imaging",
        constraints=TopicAgentConstraintSet(),
    )

    response = run_topic_agent_pipeline(request, provider=NoisyEvidenceProvider())
    joined_themes = " ".join(response.landscape_summary.themes).lower()

    assert "liver" not in joined_themes
    assert "deep" not in joined_themes
    assert "multimodal" in joined_themes or "reasoning" in joined_themes


def test_topic_agent_pipeline_uses_query_context_for_hallucination_grounding_synthesis():
    class HallucinationProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="A Multitask Multimodal Evaluation of ChatGPT on Reasoning and Hallucination",
                    source_type="paper",
                    source_tier="B",
                    year=2023,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Evaluates hallucination, reasoning, and multimodal model failures.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_b",
                    title="Toward expert-level medical question answering with large language models",
                    source_type="paper",
                    source_tier="B",
                    year=2025,
                    authors_or_publisher="Author B",
                    identifier="https://example.org/b",
                    url="https://example.org/b",
                    summary="Grounding-aware medical question answering evaluation with adversarial datasets.",
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
                    record_count=2,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="hallucination detection and grounding evaluation for multimodal medical reasoning",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    response = run_topic_agent_pipeline(request, provider=HallucinationProvider())
    joined_themes = " ".join(response.landscape_summary.themes).lower()
    joined_methods = " ".join(response.landscape_summary.active_methods).lower()
    joined_gaps = " ".join(response.landscape_summary.likely_gaps).lower()

    assert "hallucination" in joined_themes
    assert "grounding" in joined_themes
    assert "hallucination" in joined_methods or "faithfulness" in joined_methods
    assert "unsupported" in joined_gaps or "grounding" in joined_gaps
    assert "unsupported" in response.candidate_topics[1].research_question.lower() or "grounded" in response.candidate_topics[1].research_question.lower()


def test_topic_agent_pipeline_keeps_radiology_vqa_queries_from_over_shifting_to_hallucination():
    class RadiologyVqaProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="Medical Visual Question Answering via Conditional Reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2020,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Med-VQA and VQA-RAD benchmark evidence for radiology question answering.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_b",
                    title="A Survey on Multimodal Large Language Models in Radiology for Report Generation and Visual Question Answering",
                    source_type="survey",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author B",
                    identifier="https://example.org/b",
                    url="https://example.org/b",
                    summary="Survey discussing radiology VQA, grounding, and hallucination challenges.",
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
                    record_count=2,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="trustworthy visual question answering in radiology",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    response = run_topic_agent_pipeline(request, provider=RadiologyVqaProvider())
    joined_themes = " ".join(response.landscape_summary.themes).lower()

    assert "radiology vqa" in joined_themes
    assert "hallucination detection" not in joined_themes
    assert "radiology vqa benchmark" in response.candidate_topics[0].research_question.lower()
    assert "hallucination risk" not in response.candidate_topics[0].research_question.lower()


def test_topic_agent_pipeline_keeps_hallucination_queries_from_defaulting_to_vqa_slices():
    class HallucinationEvalProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="Parameter-Efficient Fine-Tuning Medical Multimodal Large Language Models for Medical Visual Grounding",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Medical visual grounding benchmark with multimodal evaluation.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_b",
                    title="A Multitask, Multilingual, Multimodal Evaluation of ChatGPT on Reasoning, Hallucination, and Interactivity",
                    source_type="paper",
                    source_tier="B",
                    year=2023,
                    authors_or_publisher="Author B",
                    identifier="https://example.org/b",
                    url="https://example.org/b",
                    summary="Hallucination and grounding evaluation evidence.",
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
                    record_count=2,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="hallucination detection and grounding evaluation for multimodal medical reasoning",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    response = run_topic_agent_pipeline(request, provider=HallucinationEvalProvider())

    assert "hallucination risk" in response.candidate_topics[0].research_question.lower()
    assert "vqa-rad or med-vqa" not in " ".join(response.candidate_topics[0].open_questions).lower()


def test_topic_agent_pipeline_polishes_visual_qa_candidate_wording():
    class VisualQaProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="Medical Visual Question Answering via Conditional Reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2020,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Med-VQA on VQA-RAD for radiology question answering.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_b",
                    title="Free Form Medical Visual Question Answering in Radiology",
                    source_type="paper",
                    source_tier="B",
                    year=2024,
                    authors_or_publisher="Author B",
                    identifier="https://example.org/b",
                    url="https://example.org/b",
                    summary="Radiology VQA benchmark and multimodal answer generation.",
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
                    record_count=2,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="trustworthy visual question answering in radiology",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    response = run_topic_agent_pipeline(request, provider=VisualQaProvider())

    assert "radiology vqa method family" in response.candidate_topics[1].research_question.lower()
    assert "document-centric clinical reasoning" not in response.candidate_topics[1].research_question.lower()


def test_topic_agent_pipeline_dedupes_hallucination_workflow_questions():
    class HallucinationWorkflowProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="Parameter-Efficient Fine-Tuning Medical Multimodal Large Language Models for Medical Visual Grounding",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Grounding evaluation benchmark for medical multimodal models.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_b",
                    title="A Multitask, Multilingual, Multimodal Evaluation of ChatGPT on Reasoning, Hallucination, and Interactivity",
                    source_type="paper",
                    source_tier="B",
                    year=2023,
                    authors_or_publisher="Author B",
                    identifier="https://example.org/b",
                    url="https://example.org/b",
                    summary="Hallucination and faithfulness evaluation evidence.",
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
                    record_count=2,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="hallucination detection and grounding evaluation for multimodal medical reasoning",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    response = run_topic_agent_pipeline(request, provider=HallucinationWorkflowProvider())
    questions = response.candidate_topics[2].open_questions

    assert questions == [
        "What workflow support would make hallucination audits and grounding checks easier to reproduce?",
        "What concrete reproducibility pain point should be prioritized first?",
        "Which workflow improvement reduces compute or setup cost the most?",
    ]


def test_topic_agent_pipeline_keeps_broad_medical_reasoning_queries_from_overfitting_to_document_qa():
    class BroadMedicalReasoningProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="RJUA-MedDQA: A Multimodal Benchmark for Medical Document Question Answering and Clinical Reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2024,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Document question answering benchmark with clinical reasoning challenges.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_b",
                    title="MedXpertQA: Benchmarking Expert-Level Medical Reasoning and Understanding",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author B",
                    identifier="https://example.org/b",
                    url="https://example.org/b",
                    summary="Benchmark for expert-level medical reasoning and multimodal understanding.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_c",
                    title="Large Language Models lack essential metacognition for reliable medical reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author C",
                    identifier="https://example.org/c",
                    url="https://example.org/c",
                    summary="Reliable medical reasoning benchmark with metacognition checks.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_d",
                    title="MedAgents: Large Language Models as Collaborators for Zero-shot Medical Reasoning",
                    source_type="paper",
                    source_tier="B",
                    year=2024,
                    authors_or_publisher="Author D",
                    identifier="https://example.org/d",
                    url="https://example.org/d",
                    summary="Agent framework for zero-shot medical reasoning with collaborative method transfer signals.",
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
                    record_count=4,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="medical reasoning",
        problem_domain="medical AI",
        constraints=TopicAgentConstraintSet(preferred_style="applied"),
    )

    response = run_topic_agent_pipeline(request, provider=BroadMedicalReasoningProvider())
    joined_themes = " ".join(response.landscape_summary.themes).lower()
    joined_methods = " ".join(response.landscape_summary.active_methods).lower()

    assert "document qa and report-centric reasoning" not in joined_themes
    assert "document qa baseline comparison" not in joined_methods
    assert "document-centric clinical reasoning" not in response.candidate_topics[1].research_question.lower()
    assert "medical reasoning method family" in response.candidate_topics[1].research_question.lower()
    assert "weak reasoning verification" in response.candidate_topics[0].research_question.lower()
    assert "image-grounded" not in response.candidate_topics[0].research_question.lower()
    assert "reasoning quality" in response.candidate_topics[0].open_questions[0].lower()
    assert "answer-pattern shortcuts" in " ".join(response.landscape_summary.likely_gaps).lower()
    assert "openalex_d" in response.candidate_topics[1].supporting_source_ids
    assert "openalex_d" in response.evidence_presentation.tentative_inferences[0].supporting_source_ids
    assert "openalex_a" not in response.candidate_topics[2].supporting_source_ids
    assert "openalex_c" in response.candidate_topics[2].supporting_source_ids
    assert (
        "openalex_b" in response.candidate_topics[2].supporting_source_ids
        or "openalex_c" in response.candidate_topics[2].supporting_source_ids
    )


def test_topic_agent_pipeline_builds_human_confirmations_for_missing_constraints():
    class SparseProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="Benchmarking Medical VQA Grounding",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Benchmark evidence for trustworthy multimodal medical reasoning.",
                    relevance_reason="Test record",
                )
            ]
            return TopicAgentEvidenceRetrievalResult(
                records=records,
                diagnostics=TopicAgentEvidenceDiagnostics(
                    requested_provider="static",
                    used_provider="static",
                    fallback_used=False,
                    fallback_reason=None,
                    record_count=1,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="medical reasoning",
        constraints=TopicAgentConstraintSet(),
    )

    response = run_topic_agent_pipeline(request, provider=SparseProvider())
    joined_confirmations = " ".join(response.human_confirmations).lower()

    assert "project timeline" in joined_confirmations
    assert "resource level" in joined_confirmations
    assert "prioritize theory" in joined_confirmations
    assert "correctly interpreted the topic" in joined_confirmations
    assert "leading direction" in joined_confirmations


def test_topic_agent_pipeline_builds_structured_clarification_suggestions():
    class SparseProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="Benchmarking Medical Reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Benchmark evidence for medical reasoning.",
                    relevance_reason="Test record",
                )
            ]
            return TopicAgentEvidenceRetrievalResult(
                records=records,
                diagnostics=TopicAgentEvidenceDiagnostics(
                    requested_provider="static",
                    used_provider="static",
                    fallback_used=False,
                    fallback_reason=None,
                    record_count=1,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="medical reasoning",
        constraints=TopicAgentConstraintSet(),
    )

    response = run_topic_agent_pipeline(request, provider=SparseProvider())

    assert [item.field_key for item in response.clarification_suggestions] == [
        "time_budget",
        "resource_level",
        "preferred_style",
    ]
    assert response.clarification_suggestions[0].refine_patch == {
        "constraints": {"time_budget_months": 6}
    }
    assert response.clarification_suggestions[1].suggested_values == [
        "student",
        "lab",
        "team",
    ]


def test_topic_agent_pipeline_builds_evidence_presentation_layers():
    class EvidenceProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="MedXpertQA: Benchmarking Expert-Level Medical Reasoning and Understanding",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Benchmark for expert-level medical reasoning.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_b",
                    title="Large Language Models lack essential metacognition for reliable medical reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author B",
                    identifier="https://example.org/b",
                    url="https://example.org/b",
                    summary="Reliable medical reasoning benchmark with metacognition checks.",
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
                    record_count=2,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="medical reasoning",
        constraints=TopicAgentConstraintSet(
            time_budget_months=6,
            resource_level="student",
            preferred_style="applied",
        ),
    )

    response = run_topic_agent_pipeline(request, provider=EvidenceProvider())

    assert response.evidence_presentation.source_facts[0].statement_type == "source_fact"
    assert response.evidence_presentation.system_synthesis[0].statement_type == "system_synthesis"
    assert response.evidence_presentation.tentative_inferences[0].statement_type == "tentative_inference"
    assert response.evidence_presentation.source_facts[0].supporting_source_ids == ["openalex_a"]
    assert "human validation" in response.evidence_presentation.tentative_inferences[0].note.lower()
    assert "constraint-sensitive" in response.evidence_presentation.tentative_inferences[0].uncertainty_reason.lower()
    assert response.evidence_presentation.tentative_inferences[0].missing_evidence


def test_topic_agent_pipeline_matches_system_synthesis_sources_to_statement_content():
    class EvidenceProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="MedXpertQA: Benchmarking Expert-Level Medical Reasoning and Understanding",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="Benchmark for expert-level medical reasoning and trustworthy evaluation.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_b",
                    title="Large Language Models lack essential metacognition for reliable medical reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author B",
                    identifier="https://example.org/b",
                    url="https://example.org/b",
                    summary="Reliable medical reasoning benchmark with metacognition checks and failure analysis.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_c",
                    title="Clinical workflow support for reproducible annotation",
                    source_type="paper",
                    source_tier="B",
                    year=2024,
                    authors_or_publisher="Author C",
                    identifier="https://example.org/c",
                    url="https://example.org/c",
                    summary="Workflow tooling for annotation efficiency.",
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
        constraints=TopicAgentConstraintSet(
            time_budget_months=6,
            resource_level="student",
            preferred_style="applied",
        ),
    )

    response = run_topic_agent_pipeline(request, provider=EvidenceProvider())

    theme_statement = response.evidence_presentation.system_synthesis[0]
    assert "theme-level evidence matching" in theme_statement.note.lower()
    assert "openalex_a" in theme_statement.supporting_source_ids
    assert "openalex_b" in theme_statement.supporting_source_ids


def test_topic_agent_pipeline_uses_clearer_candidate_composition_for_clinical_medical_reasoning():
    class ClinicalReasoningProvider:
        provider_name = "static"

        def retrieve(self, request: TopicAgentExploreRequest):
            records = [
                TopicAgentSourceRecord(
                    source_id="openalex_a",
                    title="Benchmarking large language models on the United States medical licensing examination for clinical reasoning and medical licensing scenarios",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author A",
                    identifier="https://example.org/a",
                    url="https://example.org/a",
                    summary="USMLE benchmark with clinical reasoning, hallucinations, and reproducibility concerns.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_b",
                    title="Towards Metacognitive Clinical Reasoning: Benchmarking MD-PIE Against State-of-the-Art LLMs in Medical Decision-Making",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author B",
                    identifier="https://example.org/b",
                    url="https://example.org/b",
                    summary="Framework for clinical decision-making and differential diagnosis with benchmark evidence.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_c",
                    title="Large Language Models lack essential metacognition for reliable medical reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2025,
                    authors_or_publisher="Author C",
                    identifier="https://example.org/c",
                    url="https://example.org/c",
                    summary="Reliable medical reasoning benchmark with metacognition checks.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_d",
                    title="The effectiveness of using virtual patient educational tools to improve medical students' clinical reasoning skills: a systematic review",
                    source_type="paper",
                    source_tier="B",
                    year=2022,
                    authors_or_publisher="Author D",
                    identifier="https://example.org/d",
                    url="https://example.org/d",
                    summary="Virtual patient educational tools improve clinical reasoning skills under limited teaching resources.",
                    relevance_reason="Test record",
                ),
                TopicAgentSourceRecord(
                    source_id="openalex_e",
                    title="Medical Visual Question Answering via Conditional Reasoning",
                    source_type="benchmark",
                    source_tier="A",
                    year=2020,
                    authors_or_publisher="Author E",
                    identifier="https://example.org/e",
                    url="https://example.org/e",
                    summary="Medical visual question answering and VQA-RAD reasoning.",
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
                    record_count=5,
                ),
            )

    request = TopicAgentExploreRequest(
        interest="clinical medical reasoning",
        constraints=TopicAgentConstraintSet(
            time_budget_months=6,
            resource_level="student",
            preferred_style="applied",
        ),
    )

    response = run_topic_agent_pipeline(request, provider=ClinicalReasoningProvider())

    assert "openalex_b" in response.candidate_topics[1].supporting_source_ids
    assert "openalex_d" in response.candidate_topics[1].supporting_source_ids
    assert "openalex_e" not in response.candidate_topics[1].supporting_source_ids
    assert "openalex_c" in response.candidate_topics[2].supporting_source_ids
