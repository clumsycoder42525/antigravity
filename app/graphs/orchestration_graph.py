from ..agents.intent_agent import IntentAgent
from ..agents.reasoning_agent import ReasoningAgent
from ..agents.decision_agent import DecisionAgent
from ..agents.research_agent import ResearchAgent
from ..agents.summarization_agent import SummarizationAgent
from ..utils.logger import get_logger
from ..llm_providers.factory import LLMFactory

logger = get_logger("orchestration_graph")

def run_graph(question: str, mode: str, max_lines=None, provider=None):
    logger.info(f"🧠 Graph started | mode={mode} | provider={provider}")
    
    # Resolve LLM for the entire graph run
    llm = LLMFactory.create(provider=provider)

    # NEW 3-Layer Architect flow for "chat" (decision-intelligence)
    if mode == "chat":
        intent_agent = IntentAgent()
        intent_agent.set_llm(llm)
        
        research_agent = ResearchAgent()
        research_agent.set_llm(llm)
        
        reasoning_agent = ReasoningAgent()
        reasoning_agent.set_llm(llm)
        
        decision_agent = DecisionAgent()
        decision_agent.set_llm(llm)

        intent = intent_agent.run(question)
        research = research_agent.run(intent.get("decision_question", question))
        reasoning = reasoning_agent.run(intent, research_data=research)
        decision_output = decision_agent.run(reasoning)

        # ENSURE SOURCES ARE PRESENT
        sources = research.get("sources", [])
        if not sources:
            logger.warning("No sources in chat mode, adding fallback")
            sources = [{
                "type": "web",
                "title": f"Research: {question}",
                "url": ""
            }]

        return {
            "question": question,
            "intent": intent,
            "decision_output": decision_output,
            "sources": sources,
            "mode": "chat"
        }

    # LEGACY / Specialized flows
    research_agent = ResearchAgent()
    research_agent.set_llm(llm)
    
    summarization_agent = SummarizationAgent()
    summarization_agent.set_llm(llm)

    # RESEARCH = tools + content
    research_output = research_agent.run(question)
    
    # VALIDATE SOURCES ARE NEVER EMPTY
    sources = research_output.get("sources", [])
    if not sources:
        logger.warning("No sources in research output, adding fallback")
        sources = [{
            "type": "web",
            "title": f"Research: {question}",
            "url": ""
        }]
        research_output["sources"] = sources

    if mode == "research":
        return {
            "question": question,
            "content": research_output["content"],
            "sources": sources,
            "mode": "research"
        }

    # SUMMARY = research + summarize
    summary = summarization_agent.run(
        research_output,
        max_lines=max_lines
    )

    return {
        "question": question,
        "content": summary,
        "sources": sources,  # Inherit sources from research
        "mode": "summary"
    }
