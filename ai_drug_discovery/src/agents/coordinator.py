"""
Coordinator Agent - Main orchestrator for drug repurposing analysis
"""
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

from src.config import settings, SAMPLE_DISEASES, SAMPLE_DRUGS
from src.models import Drug, Disease, DrugCandidate, Citation, RepurposingAnalysis, SafetyProfile, ConfidenceLevel, EvidenceLevel, StudyType

logger = logging.getLogger(__name__)

class CoordinatorAgent:
    """Main coordinator agent that orchestrates the drug repurposing workflow"""

    def __init__(self):
        self.ready = False

    async def initialize(self):
        """Initialize the coordinator agent"""
        logger.info("Initializing Coordinator Agent...")
        self.ready = True
        logger.info("✅ Coordinator Agent initialized")

    def is_ready(self) -> bool:
        """Check if the agent is ready"""
        return self.ready

    async def cleanup(self):
        """Cleanup resources"""
        self.ready = False

    async def analyze_drug_repurposing(
        self, 
        disease: Dict[str, Any],
        patient_profile: Optional[Dict[str, Any]] = None,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main drug repurposing analysis workflow
        """
        logger.info(f"Starting drug repurposing analysis for: {disease['name']}")

        try:
            # In demo mode, return mock data with realistic structure
            if settings.demo_mode:
                return await self._generate_demo_analysis(disease, patient_profile, parameters)

            # In production, this would orchestrate multiple specialized agents
            # 1. Research Agent - collect data from biomedical databases
            # 2. Analysis Agent - perform molecular and pathway analysis
            # 3. Citation Agent - verify sources and format citations
            # 4. Safety Agent - assess drug safety profiles

            # For now, return structured demo data
            return await self._generate_demo_analysis(disease, patient_profile, parameters)

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise

    async def _generate_demo_analysis(
        self, 
        disease: Dict[str, Any],
        patient_profile: Optional[Dict[str, Any]],
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate realistic demo analysis results"""

        disease_name = disease['name'].lower()

        # Sample drug candidates based on disease
        if "progeria" in disease_name:
            candidates = await self._generate_progeria_candidates()
        elif "muscular dystrophy" in disease_name or "duchenne" in disease_name:
            candidates = await self._generate_dmd_candidates()
        else:
            candidates = await self._generate_generic_candidates()

        # Apply filters based on parameters
        if parameters:
            threshold = parameters.get('confidence_threshold', 0.7)
            max_results = parameters.get('max_results', 10)

            # Filter by confidence threshold
            candidates = [c for c in candidates if c.repurposing_analysis.confidence_score >= threshold]

            # Limit results
            candidates = candidates[:max_results]

        # Convert to dict format for API response
        drug_candidates = []
        for candidate in candidates:
            drug_candidates.append({
                'drug': candidate.drug.dict(),
                'repurposing_analysis': candidate.repurposing_analysis.dict(),
                'safety_profile': candidate.safety_profile.dict(),
                'citations': [c.dict() for c in candidate.citations],
                'regulatory_status': candidate.regulatory_status
            })

        return {
            'drug_candidates': drug_candidates,
            'summary': {
                'total_candidates': len(drug_candidates),
                'high_confidence': len([c for c in candidates if c.repurposing_analysis.confidence_level == ConfidenceLevel.HIGH]),
                'moderate_confidence': len([c for c in candidates if c.repurposing_analysis.confidence_level == ConfidenceLevel.MODERATE]),
                'safety_concerns': 1
            },
            'research_gaps': [
                "Limited long-term safety data in pediatric populations",
                "Optimal dosing strategies need further investigation",
                "Combination therapy potential unexplored"
            ],
            'citations': {
                'total_sources': sum(len(c.citations) for c in candidates),
                'pubmed_articles': 15,
                'clinical_trials': 4,
                'quality_score': 8.3
            }
        }

    async def _generate_progeria_candidates(self) -> List[DrugCandidate]:
        """Generate drug candidates for Progeria"""
        candidates = []

        # Lonafarnib - approved for progeria
        lonafarnib = DrugCandidate(
            drug=Drug(
                drugbank_id="DB05294",
                name="Lonafarnib",
                generic_name="lonafarnib",
                brand_names=["Zokinvy"],
                atc_code="L01XX52",
                molecular_weight=589.37,
                mechanism_of_action="Farnesyltransferase inhibitor",
                approval_status="approved"
            ),
            repurposing_analysis=RepurposingAnalysis(
                confidence_score=0.92,
                confidence_level=ConfidenceLevel.VERY_HIGH,
                mechanism_of_action="Inhibits farnesyltransferase enzyme, reducing progerin accumulation",
                target_pathway="Protein prenylation pathway",
                expected_benefit="Reduces cellular aging effects and improves cardiovascular outcomes",
                evidence_strength="Strong clinical evidence"
            ),
            safety_profile=SafetyProfile(
                known_side_effects=["nausea", "vomiting", "fatigue", "decreased appetite"],
                contraindications=["pregnancy", "severe hepatic impairment"],
                drug_interactions=["strong CYP3A4 inhibitors"],
                monitoring_requirements=["liver function tests", "complete blood count"],
                pediatric_safety="Established in clinical trials"
            ),
            citations=[
                Citation(
                    id="pmid_32436818",
                    title="Lonafarnib for Hutchinson-Gilford progeria syndrome",
                    authors=["Gordon LB", "Kleinman ME", "Miller DT"],
                    journal="N Engl J Med",
                    year=2018,
                    study_type=StudyType.RCT,
                    evidence_level=EvidenceLevel.INDIVIDUAL_RCT,
                    relevance_score=0.95,
                    doi="10.1056/NEJMoa1707365"
                ),
                Citation(
                    id="pmid_20608596",
                    title="Clinical trial of a farnesyltransferase inhibitor in children with Hutchinson-Gilford progeria syndrome",
                    authors=["Gordon LB", "Massaro J", "D'Agostino RB"],
                    journal="Proc Natl Acad Sci USA",
                    year=2012,
                    study_type=StudyType.RCT,
                    evidence_level=EvidenceLevel.INDIVIDUAL_RCT,
                    relevance_score=0.93
                )
            ],
            regulatory_status={
                "fda_approved": True,
                "indication": "Hutchinson-Gilford Progeria Syndrome",
                "approval_date": "2020-11-20",
                "orphan_designation": True
            }
        )

        candidates.append(lonafarnib)

        # Add other potential candidates
        candidates.extend(await self._generate_additional_candidates())

        return candidates

    async def _generate_dmd_candidates(self) -> List[DrugCandidate]:
        """Generate drug candidates for Duchenne Muscular Dystrophy"""
        candidates = []

        # Ataluren for DMD
        ataluren = DrugCandidate(
            drug=Drug(
                drugbank_id="DB05109",
                name="Ataluren",
                generic_name="ataluren",
                brand_names=["Translarna"],
                mechanism_of_action="Nonsense mutation readthrough agent",
                approval_status="approved"
            ),
            repurposing_analysis=RepurposingAnalysis(
                confidence_score=0.84,
                confidence_level=ConfidenceLevel.HIGH,
                mechanism_of_action="Enables readthrough of nonsense mutations in dystrophin gene",
                target_pathway="Protein translation pathway",
                expected_benefit="Restoration of dystrophin protein function",
                evidence_strength="Moderate clinical evidence"
            ),
            safety_profile=SafetyProfile(
                known_side_effects=["headache", "nausea", "abdominal pain"],
                contraindications=["severe renal impairment"],
                monitoring_requirements=["renal function", "liver function"],
                pediatric_safety="Approved for pediatric use"
            ),
            citations=[
                Citation(
                    id="pmid_25274302",
                    title="Ataluren in patients with nonsense mutation Duchenne muscular dystrophy",
                    authors=["McDonald CM", "Campbell C", "Torricelli RE"],
                    journal="Lancet Neurol",
                    year=2017,
                    study_type=StudyType.RCT,
                    evidence_level=EvidenceLevel.INDIVIDUAL_RCT,
                    relevance_score=0.89
                )
            ]
        )

        candidates.append(ataluren)
        candidates.extend(await self._generate_additional_candidates())

        return candidates

    async def _generate_generic_candidates(self) -> List[DrugCandidate]:
        """Generate generic drug candidates for other rare diseases"""
        return await self._generate_additional_candidates()

    async def _generate_additional_candidates(self) -> List[DrugCandidate]:
        """Generate additional drug candidates"""
        candidates = []

        # Rapamycin - autophagy modulator
        rapamycin = DrugCandidate(
            drug=Drug(
                drugbank_id="DB00877",
                name="Sirolimus",
                generic_name="sirolimus",
                brand_names=["Rapamune"],
                mechanism_of_action="mTOR inhibitor",
                approval_status="approved"
            ),
            repurposing_analysis=RepurposingAnalysis(
                confidence_score=0.73,
                confidence_level=ConfidenceLevel.MODERATE,
                mechanism_of_action="Enhances autophagy and cellular clearance mechanisms",
                target_pathway="mTOR signaling pathway",
                expected_benefit="Improved cellular homeostasis and reduced protein aggregation",
                evidence_strength="Preclinical evidence"
            ),
            safety_profile=SafetyProfile(
                known_side_effects=["immunosuppression", "hyperlipidemia", "delayed wound healing"],
                contraindications=["active infections", "pregnancy"],
                monitoring_requirements=["complete blood count", "lipid profile", "liver function"]
            ),
            citations=[
                Citation(
                    id="pmid_example1",
                    title="Autophagy modulation in rare diseases",
                    authors=["Research A", "Scientist B"],
                    journal="Rare Disease Research",
                    year=2023,
                    study_type=StudyType.SYSTEMATIC_REVIEW,
                    evidence_level=EvidenceLevel.SYSTEMATIC_REVIEW_OBSERVATIONAL,
                    relevance_score=0.78
                )
            ]
        )

        candidates.append(rapamycin)
        return candidates

    async def search_literature(
        self,
        query: str,
        databases: List[str] = None,
        filters: Dict[str, Any] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search biomedical literature"""
        # In production, this would query actual databases
        # For demo, return mock literature results
        return [
            {
                "id": "pmid_demo1",
                "title": f"Clinical applications of {query} in rare diseases",
                "authors": ["Researcher A", "Scientist B"],
                "journal": "Journal of Rare Diseases",
                "publication_date": datetime.now().isoformat(),
                "study_type": "clinical_trial",
                "evidence_level": 2,
                "relevance_score": 0.87
            }
        ]

# Dependency injection for FastAPI
_coordinator_instance = None

async def get_coordinator() -> CoordinatorAgent:
    """Get coordinator instance for dependency injection"""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = CoordinatorAgent()
        await _coordinator_instance.initialize()
    return _coordinator_instance