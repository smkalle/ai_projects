"""ADK agent definitions for the 5-stage medical diagnostic pipeline.

EDUCATIONAL DEMO ONLY — NOT FOR CLINICAL USE.

Architecture:
  MedicalPipeline (SequentialAgent)
    Stage 1: TriageAgent (LlmAgent) — fast urgency classification
    Stage 2: ConcurrentAnalysis (ParallelAgent)
              - SymptomAnalysisAgent (LlmAgent)
              - ImagingAnalysisAgent (LlmAgent)
    Stage 3: DiagnosisRefinementLoop (LoopAgent)
              - DiagnosisGeneratorAgent (LlmAgent)
              - DiagnosisCriticAgent (LlmAgent)
    Stage 4: SpecialistRouter (LlmAgent coordinator → 4 specialists)
    Stage 5: CaseSummaryAgent (LlmAgent) — SOAP note
"""

import json

from google.adk.agents import LlmAgent, LoopAgent, ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types as genai_types

from gemini_explorer.client import MODEL

from .prompts import (
    CARDIOLOGY_PROMPT,
    CASE_SUMMARY_PROMPT,
    DERMATOLOGY_PROMPT,
    DIAGNOSIS_CRITIC_PROMPT,
    DIAGNOSIS_GENERATOR_PROMPT,
    GENERAL_MEDICINE_PROMPT,
    IMAGING_ANALYSIS_PROMPT,
    PEDIATRICS_PROMPT,
    SPECIALIST_ROUTER_PROMPT,
    SYMPTOM_ANALYSIS_PROMPT,
    TRIAGE_PROMPT,
)
from .tools import (
    calculate_bmi,
    calculate_egfr,
    calculate_risk_score,
    check_contraindication,
    lookup_drug_interaction,
    lookup_icd_code,
)


# ── Loop exit tool ────────────────────────────────────────────────────────────


def exit_diagnosis_loop(confidence_sufficient: bool, reason: str, tool_context: ToolContext) -> str:
    """Signal the diagnosis refinement loop to stop when confidence is sufficient.

    Args:
        confidence_sufficient: True if top diagnosis confidence >= 0.80
        reason: Brief explanation of the exit decision
    """
    if confidence_sufficient:
        tool_context.actions.escalate = True
        return json.dumps({"loop_status": "EXITING", "reason": reason})
    return json.dumps({"loop_status": "CONTINUING", "reason": reason})


# ── Stage builders ────────────────────────────────────────────────────────────


def build_triage_agent() -> LlmAgent:
    """Stage 1: Fast urgency classification using LlmAgent.

    Pattern: Single LlmAgent with LOW thinking for speed. Uses calculate_bmi
    as a function-calling tool. Writes structured TriageResult to state.
    """
    return LlmAgent(
        name="TriageAgent",
        model=MODEL,
        instruction=TRIAGE_PROMPT,
        output_key="triage_result",
        tools=[calculate_bmi],
    )


def build_concurrent_analysis() -> ParallelAgent:
    """Stage 2: Parallel symptom + imaging analysis using ParallelAgent.

    Pattern: Two independent LlmAgents run concurrently. Each writes to a
    unique output_key. Both use include_contents='none' for stateless isolation.
    The ImagingAnalysisAgent demonstrates Gemini's vision capability.
    """
    symptom_agent = LlmAgent(
        name="SymptomAnalysisAgent",
        model=MODEL,
        instruction=SYMPTOM_ANALYSIS_PROMPT,
        output_key="symptom_analysis",
        tools=[calculate_egfr],
        include_contents="none",
    )

    imaging_agent = LlmAgent(
        name="ImagingAnalysisAgent",
        model=MODEL,
        instruction=IMAGING_ANALYSIS_PROMPT,
        output_key="imaging_findings",
        include_contents="none",
    )

    return ParallelAgent(
        name="ConcurrentAnalysis",
        sub_agents=[symptom_agent, imaging_agent],
    )


def build_diagnosis_loop() -> LoopAgent:
    """Stage 3: Iterative diagnosis refinement using LoopAgent.

    Pattern: Generator + Critic loop. The generator produces a ranked
    differential diagnosis using HIGH thinking for deep reasoning. The critic
    evaluates confidence and calls exit_diagnosis_loop to set
    tool_context.actions.escalate=True when confidence >= 0.80.
    Both agents use include_contents='none' to read only from session state.
    """
    generator = LlmAgent(
        name="DiagnosisGeneratorAgent",
        model=MODEL,
        instruction=DIAGNOSIS_GENERATOR_PROMPT,
        output_key="differential_dx",
        tools=[lookup_icd_code],
        include_contents="none",
    )

    critic = LlmAgent(
        name="DiagnosisCriticAgent",
        model=MODEL,
        instruction=DIAGNOSIS_CRITIC_PROMPT,
        output_key="diagnosis_critique",
        tools=[exit_diagnosis_loop],
        include_contents="none",
    )

    return LoopAgent(
        name="DiagnosisRefinementLoop",
        sub_agents=[generator, critic],
        max_iterations=3,
    )


def build_specialist_router() -> LlmAgent:
    """Stage 4: LLM-based specialist routing using LlmAgent coordinator.

    Pattern: A coordinator LlmAgent with sub_agents. The LLM decides which
    specialist to route to based on the differential diagnosis. ADK's built-in
    transfer_to_agent mechanism handles the routing. Each specialist has
    domain-specific instructions and access to drug/contraindication tools.
    """
    cardiology = LlmAgent(
        name="CardiologyAgent",
        model=MODEL,
        instruction=CARDIOLOGY_PROMPT,
        output_key="specialist_opinion",
        tools=[lookup_drug_interaction, check_contraindication],
    )

    dermatology = LlmAgent(
        name="DermatologyAgent",
        model=MODEL,
        instruction=DERMATOLOGY_PROMPT,
        output_key="specialist_opinion",
    )

    pediatrics = LlmAgent(
        name="PediatricsAgent",
        model=MODEL,
        instruction=PEDIATRICS_PROMPT,
        output_key="specialist_opinion",
        tools=[check_contraindication],
    )

    general_medicine = LlmAgent(
        name="GeneralMedicineAgent",
        model=MODEL,
        instruction=GENERAL_MEDICINE_PROMPT,
        output_key="specialist_opinion",
        tools=[lookup_drug_interaction, check_contraindication],
    )

    return LlmAgent(
        name="SpecialistRouterAgent",
        model=MODEL,
        instruction=SPECIALIST_ROUTER_PROMPT,
        output_key="specialist_routing",
        sub_agents=[cardiology, dermatology, pediatrics, general_medicine],
    )


def build_summary_agent() -> LlmAgent:
    """Stage 5: SOAP-format case summary using LlmAgent.

    Pattern: Single LlmAgent that aggregates all prior stage outputs via
    {var} template interpolation. Uses calculate_risk_score for relevant
    clinical scores. Supports streaming output in the UI.
    """
    return LlmAgent(
        name="CaseSummaryAgent",
        model=MODEL,
        instruction=CASE_SUMMARY_PROMPT,
        output_key="case_summary",
        tools=[calculate_risk_score],
    )


# ── Pipeline composition ─────────────────────────────────────────────────────


def build_pipeline() -> SequentialAgent:
    """Build the full 5-stage medical diagnostic pipeline.

    Returns a SequentialAgent that orchestrates:
      1. Triage (LlmAgent)
      2. Concurrent Analysis (ParallelAgent)
      3. Diagnosis Refinement (LoopAgent)
      4. Specialist Routing (LlmAgent coordinator)
      5. Case Summary (LlmAgent)
    """
    return SequentialAgent(
        name="MedicalPipeline",
        sub_agents=[
            build_triage_agent(),
            build_concurrent_analysis(),
            build_diagnosis_loop(),
            build_specialist_router(),
            build_summary_agent(),
        ],
    )


# ── Runner wrapper ────────────────────────────────────────────────────────────


class MedicalPipelineRunner:
    """Orchestrates the ADK pipeline with session management.

    Usage:
        runner = MedicalPipelineRunner()
        async for event in runner.run_async(case):
            print(event)
        state = runner.get_state(case.patient_id)
    """

    APP_NAME = "medical_diagnostic_workbench"

    def __init__(self):
        self.session_service = InMemorySessionService()
        self.pipeline = build_pipeline()
        self.runner = Runner(
            agent=self.pipeline,
            app_name=self.APP_NAME,
            session_service=self.session_service,
        )
        self._session_ids: dict[str, str] = {}

    async def run_async(self, case, image_bytes: bytes | None = None):
        """Run the full pipeline on a patient case. Yields ADK events.

        Args:
            case: PatientIntake instance
            image_bytes: Optional image bytes for vision analysis
        """
        from .schemas import PatientIntake

        # Pre-seed all state keys that agents reference via {var} interpolation.
        # Without this, the first loop iteration fails because {diagnosis_critique}
        # doesn't exist yet, and parallel agents may reference upstream keys
        # before they're populated.
        initial_state = {
            "patient_intake": case.model_dump_json(),
            "triage_result": "",
            "symptom_analysis": "",
            "imaging_findings": "",
            "differential_dx": "",
            "diagnosis_critique": "",
            "specialist_opinion": "",
            "specialist_routing": "",
            "case_summary": "",
        }

        session = await self.session_service.create_session(
            app_name=self.APP_NAME,
            user_id=case.patient_id,
            state=initial_state,
        )
        self._session_ids[case.patient_id] = session.id

        # Build the initial message
        parts = [genai_types.Part.from_text(text=f"Begin diagnostic workup for patient: {case.case_name}")]
        if image_bytes:
            parts.append(genai_types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        initial_message = genai_types.Content(role="user", parts=parts)

        async for event in self.runner.run_async(
            user_id=case.patient_id,
            session_id=session.id,
            new_message=initial_message,
        ):
            yield event

    async def get_state(self, patient_id: str) -> dict:
        """Get the final session state after pipeline completion."""
        session_id = self._session_ids.get(patient_id)
        if not session_id:
            return {}
        session = await self.session_service.get_session(
            app_name=self.APP_NAME,
            user_id=patient_id,
            session_id=session_id,
        )
        return dict(session.state) if session else {}
