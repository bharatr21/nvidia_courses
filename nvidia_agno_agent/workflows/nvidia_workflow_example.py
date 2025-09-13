"""
Example workflow demonstrating multi-agent coordination for complex NVIDIA queries.
This shows how different specialist agents can work together on complex tasks.
"""

import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass

from agno import Workflow, Agent
from agents.nvidia_agents import create_nvidia_team


@dataclass 
class WorkflowResult:
    query: str
    agents_used: List[str]
    responses: Dict[str, str]
    final_answer: str
    sources: List[str]


class NVIDIAWorkflow(Workflow):
    """
    Complex workflow that coordinates multiple NVIDIA agents.
    Example: "How to build a production RAG system using NVIDIA NIM?"
    """
    
    def __init__(self, agents: Dict[str, Agent]):
        super().__init__(name="NVIDIA Multi-Agent Workflow")
        self.agents = agents
    
    async def run(self, query: str) -> WorkflowResult:
        """Execute the workflow with agent coordination."""
        
        # Step 1: Route query to appropriate agents
        agent_assignments = self._route_query(query)
        
        # Step 2: Execute agents in parallel or sequence
        responses = {}
        sources = []
        
        for agent_name in agent_assignments:
            agent = self.agents[agent_name]
            
            # Customize query for each agent's expertise
            agent_query = self._customize_query_for_agent(query, agent_name)
            
            # Execute agent
            response = await agent.run(agent_query)
            responses[agent_name] = response.content
            
            # Extract sources if available
            if hasattr(response, 'sources'):
                sources.extend(response.sources)
        
        # Step 3: Synthesize responses
        final_answer = await self._synthesize_responses(query, responses)
        
        return WorkflowResult(
            query=query,
            agents_used=list(responses.keys()),
            responses=responses,
            final_answer=final_answer,
            sources=sources
        )
    
    def _route_query(self, query: str) -> List[str]:
        """Determine which agents should handle this query."""
        query_lower = query.lower()
        agents_needed = []
        
        # Always include generalist as coordinator
        agents_needed.append("generalist")
        
        # Route based on keywords
        if any(word in query_lower for word in ["nim", "microservice", "inference", "deploy"]):
            agents_needed.append("nim")
        
        if any(word in query_lower for word in ["rag", "retrieval", "augmented", "evaluation"]):
            agents_needed.append("rag")
        
        if any(word in query_lower for word in ["genai", "generative", "llm", "foundation"]):
            agents_needed.append("genai")
        
        return list(set(agents_needed))  # Remove duplicates
    
    def _customize_query_for_agent(self, original_query: str, agent_name: str) -> str:
        """Customize the query based on agent's specialization."""
        
        base_query = original_query
        
        if agent_name == "nim":
            return f"From a NIM microservices perspective: {base_query}"
        elif agent_name == "rag":
            return f"From a RAG implementation perspective: {base_query}"
        elif agent_name == "genai":
            return f"From a generative AI perspective: {base_query}"
        else:  # generalist
            return f"Provide a comprehensive overview: {base_query}"
    
    async def _synthesize_responses(self, original_query: str, responses: Dict[str, str]) -> str:
        """Synthesize individual agent responses into a comprehensive answer."""
        
        # Use the generalist agent to synthesize if available
        if "generalist" in responses:
            synthesis_prompt = f"""
            Original Query: {original_query}
            
            I have received the following expert responses:
            
            {self._format_responses_for_synthesis(responses)}
            
            Please provide a comprehensive, synthesized answer that integrates insights from all experts.
            """
            
            synthesis_response = await self.agents["generalist"].run(synthesis_prompt)
            return synthesis_response.content
        
        # Fallback: simple concatenation
        return "\n\n".join([f"**{agent}**: {response}" for agent, response in responses.items()])
    
    def _format_responses_for_synthesis(self, responses: Dict[str, str]) -> str:
        """Format responses for synthesis prompt."""
        formatted = []
        for agent, response in responses.items():
            if agent != "generalist":  # Don't include generalist in synthesis input
                formatted.append(f"**{agent.upper()} EXPERT**: {response}")
        return "\n\n".join(formatted)


# Example usage
async def example_complex_workflow():
    """Demonstrate the workflow with a complex query."""
    
    # Initialize agents
    agents = await create_nvidia_team()
    
    # Create workflow
    workflow = NVIDIAWorkflow(agents)
    
    # Example complex query
    complex_query = """
    How do I build a production-ready RAG system using NVIDIA NIM microservices 
    for a generative AI application that needs to handle 1000+ concurrent users?
    """
    
    # Execute workflow
    result = await workflow.run(complex_query)
    
    # Display results
    print(f"Query: {result.query}")
    print(f"Agents Used: {', '.join(result.agents_used)}")
    print(f"\nFinal Answer:\n{result.final_answer}")
    print(f"\nSources Used: {len(result.sources)}")
    
    return result


if __name__ == "__main__":
    asyncio.run(example_complex_workflow())
