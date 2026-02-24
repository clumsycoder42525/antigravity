from .base_agent import BaseAgent
from ..tools.wikipedia_tool import wikipedia_search
from ..tools.duckduckgo_tool import duckduckgo_search
import json
from app.agents.prompts.research_prompt import RESEARCH_PROMPT

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("ResearchAgent")

    def run(self, question: str) -> dict:
        self.logger.info(f"🔎 Intelligent research synthesis started for: {question}")
        
        # 1. Fetch Foundational Knowledge (Wikipedia)
        wiki_data = {}
        wiki_raw = ""
        try:
            wiki_data = wikipedia_search(question)
            if wiki_data:
                wiki_raw = wiki_data.get("summary", "")
        except Exception as e:
            self.logger.warning(f"Wiki fetch failed: {e}")

        # 2. Fetch Recent Developments (DuckDuckGo)
        ddg_data = []
        try:
            ddg_data = duckduckgo_search(question, max_results=10)
        except Exception as e:
            self.logger.warning(f"DDG fetch failed: {e}")

        # 3. Intelligent Merging & Deduplication
        # Combine and deduplicate by URL
        unique_results = {}
        
        if wiki_raw and wiki_data.get("url"):
            unique_results[wiki_data["url"]] = {
                "type": "wikipedia",
                "title": wiki_data.get("title", "Wikipedia"),
                "url": wiki_data["url"],
                "content": wiki_raw
            }
            
        for r in ddg_data:
            url = r.get("url")
            if url and url not in unique_results:
                unique_results[url] = {
                    "type": "web",
                    "title": r.get("title", "Web Result"),
                    "url": url,
                    "content": r.get("body", "")
                }

        # 4. Limit to top N (default 5) and separate for synthesis
        final_sources_list = list(unique_results.values())[:5]
        
        # Prepare content for LLM synthesis
        # Use wiki specifically if available, else combine top web results
        ddg_raw = "\n".join([f"{r['title']}: {r['content']}" for r in final_sources_list if r['type'] == 'web'])
        
        # If absolutely no results, add a fallback
        if not final_sources_list:
            self.logger.warning("No sources found, adding fallback")
            final_sources_list.append({
                "type": "web",
                "title": f"Search: {question}",
                "url": ""
            })

        # 5. Intelligent Synthesis using LLM
        synthesis_prompt = RESEARCH_PROMPT.format(
            wiki_raw=wiki_raw or "No Wikipedia data available.",
            ddg_raw=ddg_raw or "No DuckDuckGo data available."
        )
        
        response = self._generate(synthesis_prompt)
        
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            response = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', response)
            synthesized_research = json.loads(response)
            
            # String representation for backward compatibility
            insights_str = "\n".join([f"- {i}" for i in synthesized_research.get("key_insights", [])])
            signals_str = "\n".join([f"- {s}" for s in synthesized_research.get("market_signals", [])])
            evidence_str = "\n".join([f"- {e}" for e in synthesized_research.get("supporting_evidence", [])])
            
            synthesized_research["content"] = f"""
### STRATEGIC INSIGHTS
{insights_str}

### MARKET SIGNALS & TRENDS
{signals_str}

### SUPPORTING EVIDENCE
{evidence_str}
""".strip()
            
            # Use the deduplicated sources
            synthesized_research["sources"] = [{
                "type": s["type"], 
                "title": s["title"], 
                "url": s["url"]
            } for s in final_sources_list]
            
            self.logger.info(f"Research synthesized successfully with {len(synthesized_research['sources'])} sources")
            return synthesized_research
            
        except Exception as e:
            self.logger.error(f"Failed to parse research synthesis: {e}")
            return {
                "key_insights": ["Primary research completed with failure in synthesis."],
                "market_signals": [f"Raw results merged and deduplicated."],
                "supporting_evidence": [f"Raw sources count: {len(final_sources_list)}"],
                "content": f"--- RESEARCH FALLBACK ---\nMERGED DATA: {ddg_raw[:1000]}",
                "sources": [{
                    "type": s["type"], 
                    "title": s["title"], 
                    "url": s["url"]
                } for s in final_sources_list],
                "source_attribution": {"error": str(e)}
            }
