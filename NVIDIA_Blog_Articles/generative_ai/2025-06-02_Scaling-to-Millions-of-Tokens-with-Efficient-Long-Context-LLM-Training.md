# Scaling to Millions of Tokens with Efficient Long-Context LLM Training

**URL:** https://developer.nvidia.com/blog/scaling-to-millions-of-tokens-with-efficient-long-context-llm-training/

**Author:** Amit Bleiweiss

**Published:** 2025-06-02

**Categories:** generative_ai, nim_microservices, rag_systems, performance_optimization

**Scraped:** 2025-09-11 04:26:37 UTC

---

The evolution of
large language models (LLMs)
has been marked by significant advancements in their ability to process and generate text. Among these developments, the concept of
context length
—the number of
tokens
in a single input sample that a model can handle—has emerged as a critical factor defining what these models can achieve across diverse applications.
For instance, these models allow processing video input, summarizing lengthy documents, maintaining coherence in multi-turn dialogues, reasoning through
chain-of-thought
, and performing detailed in-context learning with numerous examples. This expanded capability is particularly valuable in scenarios where retaining and utilizing comprehensive context is essential, such as video generation and understanding, legal document analysis, low-resource language translation, and when working with
AI assistants
.
In this post, we will explore the technical underpinnings of long-context LLMs and tips on how to train them effectively. We map out the needs and challenges and how you can use
NVIDIA NeMo Framework
to address them with various optimization techniques that offer efficient training with high throughput.
Need for extended context lengths and associated challenges
As more and more multimodal use cases emerge, processing long-form video content requires models to attend to thousands of frames simultaneously while maintaining temporal coherence. Models with extended context lengths, such as those supporting up to 1 million tokens, can retain detailed temporal information across vast frames of visual input.
Models optimized for complex reasoning, such as
DeepSeek-R1
and
Llama Nemotron
, rely on extended context to solve multistep problems through
chain-of-throught
reasoning. Without sufficient context window size, these models would truncate critical logical pathways, leading to errors. DeepSeek-R1 has context lengths of over 128K while Llama 4 has pushed the boundaries of context length to more than 10 million tokens.
Training LLMs with extended context lengths introduces significant technical hurdles, particularly in memory management. Transformer-based LLMs scale computationally with O(n^2) complexity as sequence lengths increase (O(n) if using flash attention). This makes training with ultra-long contexts prohibitively expensive.
Enabling long-context training with NVIDIA NeMo
As a developer, you can improve memory management during long-context training through:
Activation recomputation
Context parallelism
Activation offloading
Nemo Framework enables these with state-of-the-art implementation and additionally offers long-context recipes for popular community models.
Activation recomputation
The memory required to store intermediate activations during training grows with sequence length and model depth, quickly exceeding the capacity of even the largest GPUs.
NeMo framework supports
activation recomputation
, a memory-saving technique that addresses this bottleneck. Instead of storing all intermediate activations needed for backpropagation, the training process selectively checkpoints only a subset (such as the inputs to each transformer layer). When gradients are computed during the backward pass, the necessary activations are recomputed on-the-fly by re-executing parts of the forward pass.
By storing only a small fraction of activations and recomputing the rest, activation recomputation dramatically reduces the memory footprint. This is crucial for fitting ultra-long sequences and large batch sizes into limited GPU memory As context length increases, activation memory can surpass even the memory required for model weights and optimizer states. Recomputation allows training to scale to longer contexts while maintaining cost efficiency.
Figure 1. Checkpointing a subset of the activations and recomputing the rest to reduce device memory usage
Context parallelism
While activation recomputation is effective in reducing memory usage by discarding and recomputing activations during the backward pass, the approach introduces significant recomputational overhead—often up to 30% per training step—thereby slowing down the training process.
Context parallelism (CP)
offers a more efficient alternative. Implemented in NeMo Framework and
also introduced in
Ring Attention with Blockwise Transformers for Near-Infinite Context
, CP splits the sequence dimension across multiple GPUs. Each GPU processes and stores only a chunk of the sequence, enabling the training of models with much longer input sequences without exceeding memory limits.
CP differs from sequence parallelism (SP) in that SP only splits sequences for a few select layers such as LayerNorm and Dropout, while CP splits sequences for all the layers, with communication cost typically overlapped by compute. This enables CP to overcome the limitations of single-GPU memory capacity while avoiding the recompute overhead. This approach provides a scalable and compute-efficient solution for training large models on long sequences, making it a powerful tool in the era of large-scale deep learning.
How context parallelism works
At a high level, CP allows standard modules like Linear, LayerNorm, and other pointwise operations to function without modification. These layers do not require intertoken communication and thus naturally support the split sequence layout. For attention mechanism, the query (Q) of each token must attend to the key (K) and value (V) of all tokens in the same sequence.
CP stores KV for its local sequence chunk on each GPU during the forward pass, KV tensors are gathered again as needed during the backward pass, allowing memory to be used more efficiently. The communication collective involved (all-gather and reduce-scatter) are implemented as optimized point-to-point communications within a ring topology. Exchanging KV also can leverage MQA/GQA to reduce communication volumes, as they only have one or few attention heads for KV.
For example, in Figure 2, GPU0 and GPU1 form a tensor parallel group, and GPU0 and GPU2 form a context parallel group, which exchange KV pairs with each other. The same operation also occurs between GPU1 and GPU3. CP further enhances performance by:
Leveraging the latest open source software (OSS) and
NVIDIA cuDNN
flash attention kernels for faster and more memory-efficient attention computation.
Removing unnecessary computation caused by low-triangle causal masking and achieving optimal load balance among GPUs.
Figure 2. A transformer layer running with TP2CP2
AG/RS: all-gather in forward and reduce-scatter in backward. RS/AG: reduce-scatter in forward and all-gather in backward, /AG: no-op in forward and all-gather in backward.
CP benchmarks
Figure 3 shows efficacies of context parallel, on sequence lengths ranging from 16K to 1 million sequence lengths on Llama 3 8B. Starting from 32K sequence length and beyond, one can see that using CP yields higher teraflops. At a sequence length of 1 million, using CP is mandatory to get models running. Note that teraflops start to level off despite increasing sequence lengths, indicating that CP implementations are done efficiently with minimum overhead.
Figure 3. Performance comparison for training with and without context parallelism on NVIDIA B200
Activation offloading
In addition to CP, another technique to manage GPU memory efficiently is
CPU offloading
. CPU offloading works by reducing peak GPU memory usage by offloading intermediate activations and inactive weights to CPU memory. NeMo Framework enables offloading at the transformer layer level, allowing users to configure how many layers should utilize this strategy. During the forward pass, NeMo Framework offloads activations at the optimal time, and in the backward pass, it reloads them as needed.
This dynamic offloading mechanism helps to stretch the memory capacity of each GPU even further, especially when training very deep models, making it a valuable complement to context parallelism in large-model training.
Conclusion
While you can implement a variety of techniques to improve model long-context length, it’s best to approach optimization with model architecture and hardware choices in mind.
NVIDIA NeMo Framework, the GPU-accelerated training framework for LLMs, speech models, and multimodal models, provides tested recipes to train long-context models. These recipes are available in the
NeMo Framework LLM recipes directory
. Existing recipes include those for Llama 3 8B and 70B, Mixtral 8x7B, and Nemotron 4 15B and 22B, with 16K, 64K, and 128K sequence lengths.
You can also
extend the context window from a pretrained checkpoint
. For more information, see the
long-context recipe documentation
.