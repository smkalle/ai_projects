"""
LangGraph Agent Workflow for Energy Document AI
Implements agentic RAG with adaptive retrieval and query rewriting
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from .rag_system import EnergyRAGSystem
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the energy document agent"""
    query: str
    original_query: str
    retrieved_docs: List[Dict[str, Any]]
    rewritten_query: str
    answer: str
    relevance_score: float
    iteration_count: int
    document_type: str
    context_summary: str

class EnergyDocumentAgent:
    """Agentic RAG system for energy document processing"""

    def __init__(self, 
                 rag_system: EnergyRAGSystem,
                 openai_api_key: str,
                 model: str = "gpt-4o",
                 max_iterations: int = 3):

        self.rag_system = rag_system
        self.llm = ChatOpenAI(
            model=model, 
            temperature=0.1,
            openai_api_key=openai_api_key
        )
        self.max_iterations = max_iterations
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("evaluate", self._evaluate_relevance)
        workflow.add_node("rewrite", self._rewrite_query)
        workflow.add_node("generate", self._generate_answer)
        workflow.add_node("summarize_context", self._summarize_context)

        # Set entry point
        workflow.set_entry_point("retrieve")

        # Add edges
        workflow.add_edge("retrieve", "evaluate")
        workflow.add_conditional_edges(
            "evaluate", 
            self._decide_next_step,
            {
                "generate": "summarize_context",
                "rewrite": "rewrite",
                "end": END
            }
        )
        workflow.add_edge("rewrite", "retrieve")
        workflow.add_edge("summarize_context", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def _retrieve_documents(self, state: AgentState) -> AgentState:
        """Retrieve relevant documents from vector store"""
        try:
            logger.info(f"Retrieving documents for query: {state['query']}")

            # Determine document type based on query content
            doc_type = self._classify_query_type(state['query'])
            state['document_type'] = doc_type

            # Retrieve documents
            results = self.rag_system.similarity_search(
                query=state['query'],
                k=5,
                document_type=doc_type if doc_type != 'general' else None,
                score_threshold=0.6
            )

            state['retrieved_docs'] = results
            logger.info(f"Retrieved {len(results)} documents")

            return state

        except Exception as e:
            logger.error(f"Error in document retrieval: {e}")
            state['retrieved_docs'] = []
            return state

    def _evaluate_relevance(self, state: AgentState) -> AgentState:
        """Evaluate the relevance of retrieved documents"""
        try:
            if not state['retrieved_docs']:
                state['relevance_score'] = 0.0
                return state

            # Create evaluation prompt
            docs_text = "\n\n".join([
                f"Document {i+1}: {doc['content'][:500]}..." 
                for i, doc in enumerate(state['retrieved_docs'])
            ])

            evaluation_prompt = f"""
            Evaluate the relevance of these energy sector documents to the user's query on a scale of 0.0 to 1.0.

            Query: {state['query']}

            Documents:
            {docs_text}

            Consider:
            1. Technical accuracy and specificity
            2. Relevance to energy sector context
            3. Completeness of information
            4. Currency of data (if applicable)

            Respond with only a number between 0.0 and 1.0, where:
            - 0.8-1.0: Highly relevant, sufficient for comprehensive answer
            - 0.6-0.8: Moderately relevant, may need query refinement
            - 0.0-0.6: Low relevance, needs query rewriting

            Score:
            """

            response = self.llm.invoke(evaluation_prompt)
            try:
                score = float(response.content.strip())
                state['relevance_score'] = max(0.0, min(1.0, score))
            except ValueError:
                state['relevance_score'] = 0.5  # Default to moderate relevance

            logger.info(f"Relevance score: {state['relevance_score']}")
            return state

        except Exception as e:
            logger.error(f"Error in relevance evaluation: {e}")
            state['relevance_score'] = 0.5
            return state

    def _decide_next_step(self, state: AgentState) -> str:
        """Decide the next step based on relevance score and iteration count"""
        iteration_count = state.get('iteration_count', 0)

        # Stop if max iterations reached
        if iteration_count >= self.max_iterations:
            return "end"

        # Generate answer if relevance is high
        if state['relevance_score'] >= 0.75:
            return "generate"

        # Rewrite query if relevance is low-moderate and we haven't hit max iterations
        if state['relevance_score'] < 0.75 and iteration_count < self.max_iterations:
            return "rewrite"

        # Generate with what we have if we can't improve
        return "generate"

    def _rewrite_query(self, state: AgentState) -> AgentState:
        """Rewrite the query to improve retrieval"""
        try:
            # Increment iteration count
            state['iteration_count'] = state.get('iteration_count', 0) + 1

            rewrite_prompt = f"""
            The initial query '{state['query']}' returned documents with low relevance for energy sector analysis.

            Retrieved documents summary:
            {'; '.join([doc['document_name'] for doc in state['retrieved_docs'][:3]])}

            Rewrite the query to be more specific for energy sector documents. Consider:
            1. Technical terminology specific to energy systems
            2. Regulatory frameworks (NERC, FERC, EPA, etc.)
            3. Equipment specifications and performance metrics
            4. Energy efficiency and sustainability aspects
            5. Compliance and safety requirements

            Original query: {state['original_query']}
            Current query: {state['query']}

            Provide only the rewritten query, no explanation:
            """

            response = self.llm.invoke(rewrite_prompt)
            state['rewritten_query'] = response.content.strip()
            state['query'] = state['rewritten_query']

            logger.info(f"Rewrote query to: {state['rewritten_query']}")
            return state

        except Exception as e:
            logger.error(f"Error rewriting query: {e}")
            return state

    def _summarize_context(self, state: AgentState) -> AgentState:
        """Summarize the context for better answer generation"""
        try:
            if not state['retrieved_docs']:
                state['context_summary'] = "No relevant documents found."
                return state

            context_text = "\n\n".join([
                f"Source: {doc['document_name']}\n{doc['content']}"
                for doc in state['retrieved_docs']
            ])

            summary_prompt = f"""
            Summarize the following energy sector documents to provide context for answering: "{state['query']}"

            Documents:
            {context_text}

            Create a concise summary highlighting:
            1. Key technical specifications and data
            2. Regulatory requirements and compliance information
            3. Safety and environmental considerations
            4. Performance metrics and efficiency data

            Summary:
            """

            response = self.llm.invoke(summary_prompt)
            state['context_summary'] = response.content

            return state

        except Exception as e:
            logger.error(f"Error summarizing context: {e}")
            state['context_summary'] = ""
            return state

    def _generate_answer(self, state: AgentState) -> AgentState:
        """Generate final answer using retrieved context"""
        try:
            if not state['retrieved_docs']:
                state['answer'] = "I couldn't find relevant information to answer your query. Please try rephrasing your question or check if the document contains the information you're looking for."
                return state

            # Use context summary if available, otherwise use raw documents
            context = state.get('context_summary', '')
            if not context:
                context = "\n\n".join([
                    f"Source: {doc['document_name']}\n{doc['content']}"
                    for doc in state['retrieved_docs']
                ])

            answer_prompt = f"""
            You are an expert energy sector analyst. Answer the following query based on the provided context.

            Query: {state['query']}

            Context:
            {context}

            Guidelines:
            1. Provide accurate, technical information based only on the context
            2. Include specific data points, measurements, and specifications when available
            3. Reference regulatory frameworks and compliance requirements when relevant
            4. Highlight safety and environmental considerations
            5. If the context doesn't fully address the query, state what information is missing
            6. Format your response clearly with appropriate technical detail for energy professionals

            Answer:
            """

            response = self.llm.invoke(answer_prompt)
            state['answer'] = response.content

            logger.info("Generated final answer")
            return state

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            state['answer'] = f"An error occurred while generating the answer: {e}"
            return state

    def _classify_query_type(self, query: str) -> str:
        """Classify query to determine document type focus"""
        query_lower = query.lower()

        if any(term in query_lower for term in ['solar', 'photovoltaic', 'pv']):
            return 'solar'
        elif any(term in query_lower for term in ['wind', 'turbine', 'wind energy']):
            return 'wind'
        elif any(term in query_lower for term in ['grid', 'transmission', 'distribution']):
            return 'grid'
        elif any(term in query_lower for term in ['compliance', 'regulation', 'nerc', 'ferc']):
            return 'regulatory'
        elif any(term in query_lower for term in ['safety', 'environmental', 'epa']):
            return 'safety'
        else:
            return 'general'

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query through the agentic workflow"""
        try:
            # Initialize state
            initial_state = {
                'query': query,
                'original_query': query,
                'retrieved_docs': [],
                'rewritten_query': '',
                'answer': '',
                'relevance_score': 0.0,
                'iteration_count': 0,
                'document_type': 'general',
                'context_summary': ''
            }

            # Run workflow
            result = self.workflow.invoke(initial_state)

            # Return structured response
            return {
                'query': query,
                'answer': result['answer'],
                'relevance_score': result['relevance_score'],
                'retrieved_docs': result['retrieved_docs'],
                'iterations': result['iteration_count'],
                'document_type': result['document_type'],
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'query': query,
                'answer': f"An error occurred while processing your query: {e}",
                'relevance_score': 0.0,
                'retrieved_docs': [],
                'iterations': 0,
                'document_type': 'error',
                'timestamp': datetime.now().isoformat()
            }
