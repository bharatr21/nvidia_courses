# NVIDIA Accelerates OpenAI gpt-oss Models Delivering 1.5 M TPS Inference on NVIDIA GB200 NVL72

**URL:** https://developer.nvidia.com/blog/delivering-1-5-m-tps-inference-on-nvidia-gb200-nvl72-nvidia-accelerates-openai-gpt-oss-models-from-cloud-to-edge/

**Author:** Anu Srivastava

**Published:** 2025-08-05

**Categories:** generative_ai, nim_microservices, rag_systems, performance_optimization

**Scraped:** 2025-09-11 04:26:01 UTC

---

NVIDIA and OpenAI began
pushing the boundaries
of AI with the launch of NVIDIA DGX back in 2016. The collaborative AI innovation continues with the OpenAI gpt-oss-20b and gpt-oss-120b launch. NVIDIA has optimized both new open-weight models for accelerated inference performance on NVIDIA Blackwell architecture, delivering up to 1.5 million tokens per second (TPS) on an NVIDIA GB200 NVL72 system.
The gpt-oss models are text-reasoning LLMs with chain-of-thought and tool-calling capabilities using the popular mixture of experts (MoE) architecture with SwigGLU activations. The attention layers use RoPE with 128k context, alternating between full context and a sliding 128-token window. The models are released in FP4 precision, which fits on a single 80 GB data center GPU and is natively supported by Blackwell.
The models were trained on NVIDIA H100 Tensor Core GPUs, with gpt-oss-120b requiring over 2.1 million hours and gpt-oss-20b about 10x less. NVIDIA worked with several top open-source frameworks such as
Hugging Face Transformers
, Ollama, and vLLM, in addition to
NVIDIA TensorRT-LLM
for optimized kernels and model enhancements. This blog post showcases how NVIDIA has integrated gpt-oss across the software platform to meet developers’ needs.
Model name
Transformer Blocks
Total Parameters
Active Params per Token
# of Experts
Active Experts per Token
Input Context Length
gpt-oss-20b
24
20B
3.6B
32
4
128K
gpt-oss-120b
36
117B
5.1B
128
4
128K
Table 1. OpenAI gpt-oss-20b and gpt-oss-120b model specifications, including total parameters, active parameters, number of experts, and input context length
NVIDIA also worked with OpenAI and the community to maximize performance, adding features such as:
TensorRT-LLM Gen for attention prefill, attention decode, and MoE low-latency on Blackwell.
CUTLASS MoE kernels on Blackwell.
XQA kernel for specialized attention on Hopper.
Optimized attention and MoE routing kernels are available through the
FlashInfer
kernel-serving library for LLMs.
OpenAI Triton kernel MoE support, which is used in both TensorRT-LLM and vLLM.
Deploy using vLLM
In collaboration with vLLM, NVIDIA worked together to verify accuracy while also analyzing and optimizing performance for Hopper and Blackwell architectures. Data center developers can use NVIDIA optimized kernels through the
FlashInfer
LLM serving kernel library.
vLLM recommends using uv for Python dependency management. You can use vLLM to spin up an OpenAL-compatible web server. The following command will automatically download the model and start the server. Refer to the documentation and
vLLM Cookbook guide
for more details.
uv run --with vllm vlm serve openai/gpt-oss-20b
Deploy using TensorRT-LLM
The optimizations are available on the
NVIDIA/TensorRT-LLM
GitHub repository, where developers can use the
deployment guide
to launch their high-performance server. The guide downloads the model checkpoints from Hugging Face. NVIDIA collaborated on the developer experience using the Transformers library with the new models.
The guide then provides a Docker container
and guidance on how to configure performance for both low-latency and max-throughput cases.
More than a million tokens per second with GB200 NVL72
NVIDIA engineers partnered closely with OpenAI to ensure that the new gpt-oss-120b and gpt-oss-20b models deliver accelerated performance on Day 0 across both the NVIDIA Blackwell and NVIDIA Hopper platforms.
At launch, based on early performance measurements, a single GB200 NVL72 rack-scale system is expected to serve the larger, more computationally demanding gpt-oss-120b model at
1.5 million tokens per second
, or about 50,000 concurrent users. Blackwell features many architectural capabilities that accelerate inference performance. These include a second-generation Transformer Engine with FP4 Tensor Cores and fifth-generation NVIDIA NVLink and NVIDIA NVLink Switch, for high bandwidth,  enabling 72 Blackwell GPUs to act as a single, massive GPU.
The performance, versatility, and pace of innovation of the NVIDIA platform enable the ecosystem to serve the latest models on Day 0 with high throughput and low cost per token.
Try the optimized model with NVIDIA Launchable
Deploying with TensorRT-LLM is also available using the Python API in a JupyterLab notebook on the
Open AI Cookbook
as an NVIDIA Launchable directly in the build platform where developers can test out GPUs from multiple cloud platforms. You can deploy the optimized model with a single click in a pre-configured environment.
Figure 1. The range of GPUs available in the NVIDIA build platform
Deploy with NVIDIA Dynamo
Dynamo is an
open-source
inference serving platform that helps developers deploy frontier models like OpenAI gpt-oss for
large-scale applications
. Deploying gpt-oss-120b using
NVIDIA Dynamo
with TensorRT-LLM significantly improves performance for long input sequence lengths (ISLs) without sacrificing throughput or increasing GPU budget. At 32k ISL, Dynamo delivers 4x improvement in interactivity on Blackwell. This is achieved through disaggregated serving in Dynamo, a technique that separates the different phases of inference across distinct GPUs, increasing system efficiency.
Figure 2. NVIDIA Dynamo’s disaggregated architecture showcasing inference serving with separate GPUs for prefill and decode operations, optimizing performance.
It integrates with major inference backends and offers features like LLM-aware routing, elastic autoscaling and low-latency data transfer. Developers can use this
guide
to deploy the gpt-oss-120b model with Dynamo.
Run locally on NVIDIA GeForce RTX AI PCs
Developers can run AI locally for faster iteration, lower latency, and greater data privacy. Both models can run on professional workstations powered by NVIDIA RTX PRO GPUs, and gpt-oss-20b can be deployed on any GeForce RTX AI PC with at least 16 GB of VRAM, both natively with MXFP4 precision. Developers can experience them through their favorite apps and SDKs using Ollama, Llama.cpp, or Microsoft AI Foundry Local. To get started, check out the
RTX AI Garage
.
Simplifying enterprise with NVIDIA NIM
Enterprise developers can try the gpt-oss models for free using the NVIDIA NIM Preview API and the web playground environment in the
NVIDIA API Catalog
.  The models are packaged as
NVIDIA NIM
microservices, making it easy to deploy them on any GPU-accelerated infrastructure with flexibility, data privacy, and enterprise-grade security.
With gpt-oss models integrated into every layer and offered on the NVIDIA developer ecosystem, developers can use the solution that works best. Get started in the
NVIDIA API Catalog UI
or by using the NVIDIA developer guide in the
OpenAI Cookbook
.
Download and deploy pre-packaged, portable, optimized NIM microservices:
gpt-oss-120b: available for download
Link
|
Docs
gpt-oss-20b: available for download
Link
|
Docs
Video 1. A brief tour of the interactive, browser-based experience of OpenAI gpt-oss 120B NIM in the NVIDIA API Catalog
Get started with your own data in the
NVIDIA API Catalog UI
or using the NVIDIA developer guide in the
Open AI Cookbook
.