# Fine-Tuning gpt-oss for Accuracy and Performance with Quantization Aware Training

**URL:** https://developer.nvidia.com/blog/fine-tuning-gpt-oss-for-accuracy-and-performance-with-quantization-aware-training/

**Author:** Eduardo Alvarez

**Published:** 2025-08-29

**Categories:** generative_ai, nim_microservices, performance_optimization

**Scraped:** 2025-09-11 04:26:11 UTC

---

Major open-source foundational model releases are an exciting time for the AI community, bringing unique architectural innovations and capabilities. As the first open-source model family from the OpenAI lab since GPT-2, gpt-oss hasn’t disappointed. It delivers an advanced model with a mixture of expert  (MoE) architecture, 128K context length, and adjustable deep reasoning abilities. The largest variant,
gpt-oss-120B
, achieves performance on open benchmarks similar to OpenAI’s closed-source o3 and o4 models.
Despite strong performance on open benchmarks, most foundational models require post-training techniques to be effectively deployed in production, especially in low-fault-tolerance industries, such as healthcare and finance. OpenAI’s release of gpt-oss at native MXFP4 precision was an industry first, introducing unique challenges for fine-tuning.
In this blog post, we share and analyze the impacts of a fine-tuning workflow for gpt-oss that recovers post-training accuracy while retaining the performance benefits of FP4 by:
Performing supervised fine-tuning (SFT) on an upcasted BF16 version of the model.
Applying quantization-aware training (QAT) using NVIDIA TensorRT Model Optimizer.
SFT and QAT with gpt-oss
Exciting new techniques for
training models in native FP4 formats
are showing tremendous promise for optimizing training time rather than accuracy recovery. For gpt-oss fine-tuning, however, its native MXFP4 precision hasn’t yet proven stable accuracy. This makes fine-tuning difficult, as the model must first be upcast to higher precision to ensure stable gradient accumulation.
After upcasting, the higher-precision checkpoint becomes the focus of an initial SFT run, and a follow-up application of QAT can then be used to return the model to FP4 precision and recover task-specific performance (Figure 2). This approach enables SFT to reinforce task-specific behavior while QAT adapts the weights to the target low-precision format, delivering both alignment and performance for deployment.
Figure 1. QAT and SFT workflow for gpt-oss: from upcasted checkpoint to quantization-ready mode
l
The complete
code
for this recipe is available through the Model Optimizer repository. This training example was adapted from the fine-tuning example in Hugging Face’s
gpt-oss-recipes
to integrate QAT and other recommended components. Below is a brief summary of the steps involved:
Upcast original MXFP4 checkpoint to BF16/FP16:
Upcasting to BF16/FP16, easily done with Hugging Face’s Transformers library, provides more stable gradients and enables QAT to effectively recover accuracy when re-quantizing back to FP4. This upcasting process provides an acceptable trade-off because the computational benefits of fine-tuning entirely in FP4 are minimal, and fine-tuning typically uses far fewer tokens than pre-training.
Perform SFT:
Using an appropriate fine-tuning dataset for your use case and the upcasted precision (BF16 or FP16) model, perform supervised fine-tuning without quantization.
Quantize using TensorRT Model Optimizer:
The BF16 fine-tuned model is quantized using the
mtq.quantize()
function. This function prepares the model for PTQ or QAT.
import modelopt.torch.quantization as mtq

config = mtq.MXFP4_MLP_WEIGHT_ONLY_CFG

# Define forward loop for calibration
def forward_loop(model):
    for data in calib_set:
        model(data)

# quantize the model and prepare for QAT
model = mtq.quantize(model, config, forward_loop)
Fine-tune the FP4 quantized model:
This second fine-tuning step, at a small learning rate (e.g., 1e-5 with Adam), is the QAT step.
# QAT with a regular finetuning pipeline
train(model, train_loader, optimizer, scheduler, ...)
The optimal QAT hyperparameters and training duration are optimizable parameters. We have found that skipping Step 1 and going straight to QAT results in lower accuracy. We recommend performing high-precision fine-tuning first, followed by QAT for best results. After achieving satisfactory convergence, the Model Optimizer APIs can export the model to a standard PyTorch checkpoint for validation against open benchmarks and custom tasks.
Impact of MXFP4 QAT fine-tuning on gpt-oss
To show the effectiveness of the above QAT fine-tuning workflow, we analyze two specific downstream evaluation tasks: enhancing non-English reasoning (using a
multilingual dataset
from the OpenAI Cookbook) and reducing unnecessary refusals of safe user prompts (using the
FalseReject dataset
from Amazon). Out of the box, gpt-oss shows room for improvement on these tasks, initially scoring 16% and 30% respectively (Figure 3). After applying this recipe, we see pass-rate scores of 98% for both tasks— a significant improvement.
Figure 2. Validation pass rates of gpt-oss-20b across original, SFT, PTQ, and QAT methods
While the results from this model highlight the effectiveness of upcasting and applying QAT to recover accuracy in gpt-oss fine-tuning, opportunities remain to capture additional task-specific performance. With the arrival of NVIDIA Blackwell,
NVFP4
introduces a new FP4 format purpose-built for both training and inference efficiency, opening the door to even greater accuracy recovery when paired with QAT (Figure 3).
Figure 3. Flowchart showing deployment options from MXFP4 checkpoints, including direct deployment, QAT to MXFP4, or QAT to NVFP4 for higher task-specific accuracy
NVFP4 enables developers to use specialized instructions in the second-generation NVIDIA Transformer Engine and pair up to 15 PFLOPs of FP4 NVIDIA Blackwell Ultra compute with better model accuracy performance. The E4M3 FP8 scaling precision shines during the “fake quantization” process, reducing quantization errors during the forward pass—enabling the original model weights to adapt more easily to the target precision. The MXFP4 recipe described above only requires updating a single line to adapt to NVFP4, as seen in the code snippet below.
# To do NVFP4 PTQ/QAT, simply replace MXFP4_MLP_WEIGHT_ONLY_CFGconfig = mtq.NVFP4_MLP_WEIGHT_ONLY_CFG
# Alternatively, do weight-activation quantization for better performanceconfig = mtq.NVFP4_MLP_ONLY_CFG
When comparing MXFP4 and NVFP4 validation loss after this gpt-oss fine-tuning recipe, we observed better convergence from the NVFP4 version consistently. The observed validation loss for these tasks was 2–3% better with NVFP4 (Figure 4). This uplift can create margin for tougher settings, such as deep reasoning, stricter thresholds, or downstream tasks with low fault tolerance.
Figure 4. Validation loss on Multi-Lingual and FalseReject tasks across SFT, PTQ, and QAT for NVFP4 and MXFP4 formats
With upcoming gpt-oss NVFP4 support in NVIDIA TensorRT-LLM, developers will be able to use NVFP4 with ease. We are also prioritizing gpt-oss NVFP4 enablement with other open-source inference frameworks. Until then, the SFT + QAT workflow for MXFP4 remains a proven path. Once NVFP4 gpt-oss is fully supported, the same recipe will unlock even greater accuracy on NVIDIA Blackwell.
Deploying the fine-tuned model
After executing this recipe, you can use a
convenience script
provided through the Model Optimizer repository to convert the BF16-trained checkpoint into MXFP4.
python examples/gpt-oss/convert_oai_mxfp4_weight_only.py --model_path qat_model_dir/ --output_path qat_model_mxfp4/
The resulting MXFP4 checkpoints from this recipe have been tested using upstream SGLang, TensorRT-LLM, and vLLM. The following command can be used to deploy using TensorRT-LLM
1.1.0rc1
.
# Use trtllm-serve to host endpoint
trtllm-serve qat_model_mxfp4/ --tokenizer <tokenizer_path> --max_batch_size <max_batch_size> --max_num_tokens <max_num_tokens> --max_seq_len <max_seq_len> --tp_size <tp_size> --pp_size <pp_size> --host 0.0.0.0 --kv_cache_free_gpu_memory_fraction 0.95
Summary
The central challenge of gpt-oss fine-tuning is recovering accuracy in FP4 while keeping the efficiency gains that make low precision valuable for deployment. Upcasting to BF16 for SFT followed by QAT addresses this gap by adapting weights to low precision, making the model both reliable and efficient in production.
In practice, this approach restores accuracy and strengthens task-specific performance, improving user experience, safety, and utility in downstream applications. These gains translate into higher service quality and better ROI. Looking ahead, NVFP4 delivers tighter convergence and added margin for stricter thresholds and deeper reasoning, with upcoming gpt-oss NVFP4 support in TensorRT-LLM and other frameworks extending these benefits further. Get started with the complete
SFT + QAT recipe
, available now in the NVIDIA Model Optimizer repository.