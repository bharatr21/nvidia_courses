# How Small Language Models Are Key to Scalable Agentic AI

**URL:** https://developer.nvidia.com/blog/how-small-language-models-are-key-to-scalable-agentic-ai/

**Author:** Peter Belcak

**Published:** 2025-08-29

**Categories:** generative_ai, nim_microservices, ai_agents, performance_optimization

**Scraped:** 2025-09-11 04:25:50 UTC

---

The rapid rise of agentic AI has reshaped how enterprises, developers, and entire industries think about automation and digital productivity. From software development workflows to enterprise process orchestration, AI agents are increasingly helping to power enterprises’ core operations, especially in areas that have previously been deemed plagued by repetitive tasks.
Most of these agents depend heavily on large language models (LLMs). LLMs are often recognized for their general reasoning, fluency, and capacity to support open-ended dialogue. But when they’re embedded inside agents, they may not always be the most efficient or economical choice. In our recent position paper, we outline our observations about the role small language models (SLMs) play in agentic AI. Titled
Small Language Models are the Future of Agentic AI
, we highlight the growing opportunities for integrating SLMs in place of LLMs in agentic applications, decreasing costs, and increasing operational flexibility.
Our stance isn’t that LLMs will stop being useful in the context of agents. Instead, we point to the rise of heterogeneous ecosystems where SLMs play a central operational role while LLMs are reserved for situations where their generalist capabilities are indispensable.
This future path isn’t speculative—NVIDIA already offers a suite of products, from open
NVIDIA Nemotron
reasoning models to the
NVIDIA NeMo
software suite for managing the entire AI agent lifecycle. Enterprises equipped with these tools can build heterogeneous systems of AI models deploying fine-tuned SLMs for core workloads while using LLMs for occasional multi-step strategic tasks. This approach will improve results with substantially reduced power and costs.
Why are SLMs beneficial to agentic AI tasks?
SLMs are well-positioned for the agentic era because they use a narrow slice of LLM functionality for any single language model errand. LLMs are built to be powerful generalists, but most agents use only a very narrow subset of their capabilities.
They typically parse commands, generate structured outputs such as JSON for tool calls, or produce summaries and answer contextualized questions. These tasks are repetitive (up to the differences in prompt payloads), predictable, and highly specialized—well within the scope of specialized SLMs. An LLM trained to handle open-domain conversations is overkill for such contexts, resulting in wasted compute and cost.
By contrast, an SLM fine-tuned for a handful of specific agentic routines can be more reliable, less prone to hallucination, faster, and vastly more affordable. In other words, agentic AI doesn’t require a Swiss Army knife when a single sharp tool will do.
It’s also worth noting that SLMs are not the weaker siblings of LLMs. Newer SLM models show performance comparable to or even exceeding that of much larger LLMs in targeted benchmarks such as commonsense reasoning, tool calling, and instruction following.
For example, the recent best-in-class
NVIDIA Nemotron Nano 2
shows what’s possible from high-performing SLMs in agentic AI. This open, 9B parameter Mamba-transformer model uses lower memory consumption while delivering greater accuracy. Nemotron Nano 2 outpaces other models of its size class on key benchmarks in reasoning, coding, and instruction following, while achieving 6x higher throughput. It’s engineered for real-world agentic workloads, supporting 128k token contexts and optimized performance on a single GPU with open weights and documentation for enterprise adaptation.
Figure 1. Artificial Analysis Intelligence Index chart comparing Nano 9B V2 to Llama 4 Maverick, Qwen 3 14B, and Llama 3.1 Nemotron 70B
Small models don’t outperform LLMs across all benchmarks. You can choose a starting-point SLM for their agent based on their general capabilities, and then improve it with finetuning. With innovations like hybrid architectures, distillation techniques, and retrieval context augmentation, SLMs are proving capable of handling the vast majority of subtasks agents handle. This challenges the traditional assumption that only massive models can deliver reliable results in the context of agentic AI.
Figure 2. Nemotron Nano 9B v2 outperforms LLMs and SLMs of its own class
The efficiency gains from switching to SLMs are staggering. Running a Llama 3.1B SLM can be 10x to 30x cheaper than running its highest-performing sibling, Llama 3.3 405B (depending on the details of the architecture and the parameters of a typical query).
SLMs deliver real-time responses without the heavy parallelization requirements of frontier models, making them more suitable for both cloud and edge deployments. Fine-tuning agility also plays a major role: adding a new skill or fixing a behavior can be done in a few GPU hours on an SLM, compared to days or weeks of fine-tuning for LLMs.
With edge deployments such as NVIDIA ChatRTX, SLMs can run locally on consumer-grade GPUs, enabling privacy-preserving and low-latency inference. The economic argument isn’t just about cost reduction. It’s also about scalability, sustainability, and democratization. Smaller models enable more organizations to participate in developing agentic AI, spreading innovation across industries.
A crucial and decisive advantage of SLMs lies in their flexibility and alignment. They’re easier to fine-tune for strict formatting and behavioral requirements, which is critical for agent workflows where every tool call and code interaction must match exact schemas. An LLM might occasionally drift and produce malformed output, where an SLM trained to always respond in a single format won’t, because it isn’t aware of any other output formats.
This reliability directly translates to fewer failure points in production systems. Moreover, agentic systems are naturally heterogeneous. It’s entirely feasible for one agent to combine multiple specialized SLMs with occasional LLM calls. A modular approach (using the right-sized model for the right subtask) is far more consistent with the way agents decompose complex problems.
The new role of LLMs in a heterogeneous AI architecture
This doesn’t mean LLMs are obsolete. Their generalist reasoning abilities remain unmatched in contexts that demand open-ended, human-like dialogue, cross-domain abstraction and transfer, or complex, multi-step problem solving where subtasks can’t be easily decomposed. In practice, this means that the future is heterogeneous: SLMs handle the bulk of operational subtasks, with LLMs invoked selectively for their scope. Think of SLMs as the workers in a digital factory (efficient, specialized, and reliable). LLMs act as consultants called in when broad expertise is required or when pleasant interactions with the outside world are needed.
Why aren’t enterprises using SLMs more broadly?
If SLMs have clear advantages, why do most agents still rely so heavily on LLMs? We hypothesize that the barriers are perception-based or caused by organizational culture rather than technical limitations. Shifting to SLM-enabled architectures requires an intentional mindset change. SLM research uses generalist benchmarks, even though agentic workloads demand different evaluation metrics. Plus, LLMs often dominate the headlines. As the cost savings and reliability of SLM-enabled systems become undeniable, momentum will shift. The transition could mirror past shifts in computing, such as the move from monolithic servers to cloud microservices.
How to add SLMs into agent architectures
For organizations ready to introduce SLMs into their agent architectures, the process is straightforward. It begins with collecting usage data from agents to understand which tasks recur most often. This data is then curated and filtered to remove sensitive information and prepare training sets. Tasks can be clustered into categories such as parsing, summarization, or coding, and matched to candidate SLMs. These models are then fine-tuned using efficient techniques such as LoRA or QLoRA, turning them into highly specialized task experts.
Over time, the process is repeated, continuously improving the agent by delegating more and more subtasks to cheaper, faster SLMs. In this way, an agent that once depended entirely on an LLM can gradually transform into a modular, SLM-enabled system.
The exciting news for practitioners is that the tools for making this shift are already available. NVIDIA NeMo provides the end-to-end software to curate data, customize and evaluate models, safeguard and ground agent response, and monitor and optimize agentic AI systems. Soon, non-specialists in any organization will be able to set up and deploy heterogeneous systems to improve workflows with little effort. Enterprises looking to control costs, improve efficiency, and scale responsibly can begin experimenting with heterogeneous systems today.
Conclusion: the heterogeneous system advantage
The demand for agentic AI systems is rapidly evolving. Today’s SLMs deliver a mix of power, accuracy, and efficiency for nearly all routine and specialized workloads–snapping into the modular, tool-driven design architectures these systems require. Relying solely on LLMs for every workflow is becoming alarmingly costly and inefficient as AI demands continue to rise.
Instead, large models are best positioned as expert resources, selectively invoked for complex challenges. Enterprises that embrace a heterogeneous system of models will realize invaluable advantages: lower costs, faster results, and a broader, more flexible deployment of agentic AI. A more open, modular, and democratized era of enterprise automation begins with the integration of small language models.
Learn more:
Read our
paper
.
Learn more about
NVIDIA NeMo Customizer
,
NVIDIA Data Flywheel Blueprint
, and
NVIDIA NeMo Curator
.
Stay up to date on NVIDIA Nemotron by subscribing to
NVIDIA news
and following NVIDIA AI on
LinkedIn
,
X
,
Discord
, and
YouTube
.
Visit our
Nemotron page
to get all the essentials you need to get started with the most open, smartest-per-compute reasoning model.
Explore new open Nemotron models and datasets on
Hugging Face
and
NIM microservices
and
Blueprints
on
build.nvidia.com
.
Tune into upcoming Nemotron livestreams and connect with the NVIDIA Developer community through
the Nemotron developer forum
and the
Nemotron channel on Discord
.
Browse
video tutorials and livestreams
to get the most out of NVIDIA Nemotron.