# A Fine-tuning–Free Approach for Rapidly Recovering LLM Compression Errors with EoRA

**URL:** https://developer.nvidia.com/blog/a-fine-tuning-free-approach-for-rapidly-recovering-llm-compression-errors-with-eora/

**Author:** Min-Hung Chen

**Published:** 2025-06-09

**Categories:** generative_ai, nim_microservices, performance_optimization

**Scraped:** 2025-09-11 04:26:40 UTC

---

Model compression techniques have been extensively explored to reduce the computational resource demands of serving large language models (LLMs) or other large-size neural networks.
However, most existing methods either incur significant accuracy degradation compared to uncompressed models or have long training times. Also, their adaptability is often constrained by a limited range of hardware-supported compression formats (for example, 2:4 sparsity, 3/4-bit quantization), making it difficult to address various user requirements for accuracy and efficiency.
NVIDIA Research Taiwan
,
Learning & Perception Research Group
,
AI Accelerator & VLSI Research Group
, and
NeMo Group
reframe model compression as customized compensation. They developed
Fine-tuning-free Compensation for Compressed LLM with Eigenspace Low-Rank Approximation (EoRA)
, which introduces residual low-rank paths to compensate for compression errors caused by various compression techniques under diverse user needs, such as tasks or compression ratios.
As a fine-tuning–free optimization method, EoRA requires no gradient computation and can be completed within a few minutes using minimal calibration data. It can also serve as a good starting point for fine-tuning, and remains robust to quantization to further reduce overhead.
EoRA effectively compensates the compressed LLMs on language generation, commonsense reasoning, and math tasks. It consistently outperforms previous SVD-based approaches, especially for aggressively compressed (including pruned, quantized, and both) models. For example, we saw  4.53%, 3.48%, and 11.83% improvement on ARC-Challenge, MathQA, and GSM8K when compensating 2:4-pruned Llama3-8B. Moreover, the EoRA module remains resilient under 3/4-bit quantization with minimal accuracy drop, underscoring its practicality in compensating for compression errors.
Figure 1. Overview of a proposed model compensation framework, EoRA
How does EoRA work?
Compared with standard model compression techniques and algorithms, model compensation introduces residual low-rank paths to compensate for compression errors
, resulting in greater flexibility in adjusting overall capacity without being constrained by specific compression formats.
To derive the low-rank residual paths that can represent compression errors
, one naive method is to directly derive a closed-form solution by using singular value decomposition (SVD). However, naively applying SVD fails to account for the varying importance of individual model weights, resulting in suboptimal utilization of the low-rank representation capacity.
To address this problem, EoRA projects the compression error
into the eigenspace of the corresponding layer’s input activations
, ensuring a direct relationship between the error approximation loss and the overall layer-wise model compression loss.
More specifically, we first perform the eigendecomposition on the input activations
from the calibration set to derive the eigenspace projection matrix
by eigenvectors and eigenvalues. We then project the compression error
into the eigenspace with the projection matrix
to obtain the projected error
.
SVD is then applied to
, approximating the solution
and
in the eigenspace. In this way, the approximation ensures that error columns associated with larger eigenvalues are approximated more accurately than those with smaller eigenvalues, facilitating a more effective allocation of the insufficient low-rank expressive power.
Finally, we project
back using the inverse projection matrix
to obtain
and use
and
to approximate compression error
in the original space since the following is true:
Figure 2 shows the whole process.
Figure 2. Proposed EoRA, which projects the compression error
into the eigenspace of input activations
and performs low-rank approximation on projected error
The overall fine-tuning–free optimization in EoRA can be done in minutes using only a small amount of calibration data without any gradient computation or time-consuming machine learning approaches.
EoRA can provide better initialization for fine-tuning to further enhance accuracy with the compression technique and offer a trade-off between accuracy and training time.
EoRA is also robust to quantization, which can further reduce the additional cost of residual low-rank compensation paths.
For more information about the detailed algorithm and mathematical analyses, see
EoRA: Fine-tuning-free Compensation for Compressed LLM with Eigenspace Low-Rank Approximation
.
Performance
EoRA is compatible with various compression techniques, including pruning, quantization, and both. It consistently outperforms previous SVD-based methods on various tasks, such as language generation, commonsense reasoning, and math tasks.
EoRA can also provide better initialization for fine-tuning, and is robust to quantization and rank numbers.
Compression error compensation
The scores in Tables 1-3 show that EoRA significantly and consistently outperforms the SVD-based baseline method, ZeroQuant-V2, on the model compressed by various compression techniques, including pruning (Table 1), quantization (Table 2), and both (Table 3).
EoRA also works on different transformer backbones, such as Llama2, Llama3, and so on. For more information, see
EoRA: Training-free Compensation for Compressed LLM with Eigenspace Low-Rank Approximation
.
Pruning  method
Sparsity
Compensation method
Wikitext2 (↓)
ARC-C (↑)
MathQA (↑)
GSM8K (↑)
Uncompressed
N/A
N/A
6.13
50.4
40.1
36.2
SparseGPT
2:4
–
12.32
30.1
26.4
2.1
ZeroQuant-V2
11.31
32.0
26.5
3.0
EoRA
11.07
(-0.24)
34.6
(+2.6)
29.9
(+3.4)
13.9
(+10.9)
Wanda
2:4
–
21.4
27.0
25.1
0.8
ZeroQuant-V2
17.2
30.5
26.2
1.3
EoRA
14.0
(-3.2)
34.8
(+4.3)
30.0
(+3.8)
11.5
(+10.2)
Table 1. Perplexity and commonsense/math reasoning results for pruned LLama3-8B
Quantization  method
X-bit
Compensation method
Wikitext2 (↓)
ARC-C (↑)
MathQA (↑)
GSM8K (↑)
Uncompressed
N/A
N/A
6.13
50.4
40.1
36.2
GPTQ
3-bit
–
15.64
20.9
22.4
0.4
ZeroQuant-V2
10.24
30.0
26.4
3.8
EoRA
10.06
(-0.18)
31.7
(+1.7)
29.1
(+2.7)
11.9
(+8.1)
Table 2. Perplexity and commonsense/math reasoning results for quantized LLama3-8B
Compression   method
X-bit
Sparsity
Compensation method
Wikitext2 (↓)
ARC-C (↑)
MathQA (↑)
GSM8K (↑)
Uncompressed
N/A
N/A
N/A
6.13
50.4
40.1
36.2
GPTQ + SparseGPT
4-bit
2:4
–
86.15
18.3
19.9
0.0
ZeroQuant-V2
12.84
29.4
26.9
1.6
EoRA
12.60
(-0.24)
31.2
(+1.8)
29.6
(+2.7)
10.2
(+8.6)
Table 3. Perplexity and commonsense/math reasoning results for aggressively compressed LLama3-8B
Fine-tuning with EoRA
You can fine-tune EoRA to further recover the accuracy loss of the compressed models, showing more significant improvements than baseline methods.
Compression  method
Config
Initialization
ARC-C (↑)
MathQA (↑)
Uncompressed
N/A
w/o fine-tuning
50.4
40.1
Standard
56.4
53.6
GPTQ
3-bit
w/o fine-tuning
20.9
22.4
QLoRA
30.3
34.1
LoftQ
44.7
48.2
EoRA
47.4
(+2.7)
53.9
(+5.7)
SparseGPT
2:4
w/o fine-tuning
30.1
26.4
QLoRA
41.3
45.4
LoftQ
43.7
48.8
EoRA
48.5
(+4.8)
54.7
(+5.9)
Table 4. Fine-tuning results for compressed LLama3-8B
Table 4 shows various compression settings using different initializations of low-rank matrices. The scores show the improvement over the baselines, QLoRA and LoftQ. The fine-tuned model shows competitive results with the uncompressed full-precision model, and even surpasses the accuracy of the fine-tuned full-precision model on MathQA.
Compensation with different ranks
EoRA consistently outperforms the SVD-based baseline method, ZeroQuant-V2, across different ranks, with the improvement becoming slightly more pronounced at higher ranks. The results prove that EoRA is robust across different rank settings, offering you a more flexible option upon existing compression configurations to effectively balance the trade-off between inference overhead and model accuracy.
Figure 3. Rank vs. accuracy on three datasets
Quantization of EoRA
The neural network of EoRA can also be quantized to further reduce the additional cost of residual low-rank compensation paths.
Figure 4 shows that EoRA is robust to quantization, which means that when EoRA is quantized, the accuracy drop from full-precision EoRA is insignificant, while the model size is significantly reduced. For example, when a 512-rank EoRA is quantized from 16 bits to 4 bits on 2:4 pruned Llama3-8B, the accuracy drops are only 0.43% on ARC-C, while the total model size reduces by 16.5%.
Generally, we recommend that you quantize EoRA to 4 bits, as this significantly reduces inference latency and model size without causing any noticeable drop in accuracy.
Figure 4. Quantizing EoRA of rank {128, 512} to 4/3-bit on compensating three types of compressed Llama3-8B models (2:4 pruned, 4-bit quantized, and 3-bit quantized).
Open-source impact
EoRA has been seamlessly integrated into the open-source library
GPTQModel
, which is the default LLM model compression and quantization toolkit with accelerated inference support for both CPU and GPU through Hugging Face, vLLM, and SGLang.
This integration enables you to easily enhance the accuracy of your quantized models with the EoRA method as simply as turning this feature on as a toggle. All model quantization users who use Hugging Face, vLLM, and SGLang can easily use our EoRA work to improve their overall model performance.
The following Python code example runs Quantization + EoRA Accuracy Recovery:
from gptqmodel import BACKEND, GPTQModel
from gptqmodel.adapter.adapter import Lora

eora = Lora(
    # for eora generation, path is adapter save path; for load, it is loading path
    path='GPTQModel/examples/eora/Llama-3.2-3B-4bits-eora_rank64_32',
    rank=32,
)

model = GPTQModel.load(
    model_id_or_path='USER_FOLDER/Llama-3.2-3B_4bits_128group_size',
    adapter=eora,
)

tokens = model.generate("Capital of France is")[0]
result = model.tokenizer.decode(tokens)
print(f"Result: {result}")
Table 5 shows that EoRA substantially improves the accuracy of 3/4-bit quantized models on MMLU. The experiments are zero-shot as the calibration dataset (C4) has no overlap with the testing dataset (MMLU). The accuracy boost percentage shows the ratio between the quantized + EoRA model and the quantized model. For more information, see the
/ModelCloud/GPTQModel
GitHub repo.
X-bit
EoRA calibration set
EoRA rank
MMLU (↑)
MMLU
accuracy boost
16-bit (full precision)
N/A
N/A
54.2
N/A
4-bit
–
–
24.2
N/A
C4
32
52.5
217%
3-bit
–
–
22.9
N/A
C4
32
39.1
171%
Table 5. MMLU results for quantized LLama 3.2-3B
This technique has also been adopted to significantly boost the accuracy for 2-bit quantized Qwen3 and Qwen2.5. For more details, please refer to the blog:
Boost 2-Bit LLM Accuracy with EoRA
.
Summary
EoRA presents a scalable, versatile solution for model compensation, with potential applications across various domains where efficient deployment of large models or neural networks is crucial.
The key strength of EoRA lies in its training-free nature, enabling rapid optimization using only a small calibration dataset, and its robustness to quantization, making it an effective tool for deploying large models with varying capacity requirements. EoRA provides a solid initialization for fine-tuning, further reducing accuracy degradation and, in some cases, surpassing the performance of uncompressed models.
EoRA demonstrates significant improvements in language generation, commonsense reasoning, and mathematical reasoning tasks, outperforming traditional low-rank approximation techniques such as SVD. We hope EoRA can help NVIDIA efficiently and effectively boost the performance of compressed large models and benefit diverse applications in
NVIDIA Metropolis
,
NVIDIA NeMo
,
NVIDIA NIM
,
NVIDIA TensorRT
, computer vision, generative AI, robotics, and more.
For more information, see the following resources:
EoRA: Fine-tuning-free Compensation for Compressed LLM with Eigenspace Low-Rank Approximation
/NVlabs/EoRA
GitHub repo
/ModelCloud/GPTQModel
GitHub repo