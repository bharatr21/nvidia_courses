"""
Agno-based NVIDIA specialist agents and team composition.
"""

import os
import asyncio
from typing import List, Dict, Any
from dataclasses import dataclass

from dotenv import load_dotenv
from agno import Agent
from agno.models.openai import OpenAIChat
from agno.memory import SqliteMemory
from agno.tools import Tool as AgnoTool

from knowledge.nvidia_knowledge import NVIDIAKnowledge, create_nvidia_knowledge
from tools.nvidia_blog_tool import NVIDIABlogTool

load_dotenv()

@dataclass
class AgentConfig:
    name: str
    instructions: List[str]
    tools: List[AgnoTool]
    knowledge: NVIDIAKnowledge


def build_base_model() -> OpenAIChat:
    return OpenAIChat(id=os.getenv('OPENAI_MODEL', 'gpt-4'))


def build_memory() -> SqliteMemory:
    path = os.getenv('AGENT_MEMORY_PATH', './data/agent_memory.db')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return SqliteMemory(db_file=path)


class BlogSearchAgnoTool(AgnoTool):
    """Wrap NVIDIABlogTool as an Agno Tool."""
    name = "nvidia_blog_search"
    description = "Search NVIDIA Developer Blog and NVIDIA Blog for recent and relevant articles."

    def __init__(self):
        super().__init__()
        self.impl = NVIDIABlogTool()

    async def run(self, query: str, include_content: bool = False) -> List[Dict[str, Any]]:
        return await self.impl.search(query, include_content=include_content)


def system_instructions() -> List[str]:
    return [
        "You are an NVIDIA-specialist AI assistant.",
        "Always be accurate and cite your sources.",
        "When you use course transcript knowledge, include the course and lesson name.",
        "When you use web results, include the URL and publish date.",
        "Focus on NVIDIA topics: NIM, generative AI, RAG, GPUs, enterprise solutions.",
    ]


async def create_specialist_agents(knowledge: NVIDIAKnowledge):
    """Create domain-specialist agents that share the same knowledge and tools."""
    blog_tool = BlogSearchAgnoTool()

    common_kwargs = dict(
        model=build_base_model(),
        memory=build_memory(),
        tools=[blog_tool],
        instructions=system_instructions(),
        add_datetime_to_context=True,
        add_history_to_context=True,
        num_history_runs=5,
    )

    nvidia_generalist = Agent(name="NVIDIA Generalist", **common_kwargs)
    nim_expert = Agent(name="NIM Expert", **common_kwargs, instructions=system_instructions() + ["Specialize in NVIDIA NIM microservices: architecture, deployment, APIs."])
    rag_expert = Agent(name="RAG Expert", **common_kwargs, instructions=system_instructions() + ["Specialize in Retrieval Augmented Generation patterns and evaluation."])
    genai_expert = Agent(name="GenAI Expert", **common_kwargs, instructions=system_instructions() + ["Specialize in generative AI foundations and NVIDIA ecosystem."])

    # Attach knowledge to each agent
    for ag in [nvidia_generalist, nim_expert, rag_expert, genai_expert]:
        ag.knowledge = knowledge

    return {
        "generalist": nvidia_generalist,
        "nim": nim_expert,
        "rag": rag_expert,
        "genai": genai_expert,
    }


async def create_nvidia_team() -> Dict[str, Agent]:
    knowledge = await create_nvidia_knowledge()
    agents = await create_specialist_agents(knowledge)
    return agents

