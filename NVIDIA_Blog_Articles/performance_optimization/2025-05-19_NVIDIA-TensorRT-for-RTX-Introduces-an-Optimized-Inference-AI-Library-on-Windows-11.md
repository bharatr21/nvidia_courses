# NVIDIA TensorRT for RTX Introduces an Optimized Inference AI Library on Windows 11

**URL:** https://developer.nvidia.com/blog/nvidia-tensorrt-for-rtx-introduces-an-optimized-inference-ai-library-on-windows/

**Author:** Gunjan Mehta

**Published:** 2025-05-19

**Categories:** generative_ai, nim_microservices, rag_systems, performance_optimization

**Scraped:** 2025-09-11 04:26:44 UTC

---

AI experiences are rapidly expanding on Windows in creativity, gaming, and productivity apps. There are various frameworks available to accelerate AI inference in these apps locally on a desktop, laptop, or workstation. Developers need to navigate a broad ecosystem. They must choose between hardware-specific libraries for maximum performance, or cross-vendor frameworks like DirectML, which simplify deployment across CPUs, GPUs, and NPUs, but don’t always unlock the full potential of each device. Striking the right balance between performance and compatibility is critical for developers.
Today, we’re announcing
NVIDIA TensorRT for RTX
to address these challenges. It’s available on Windows 11 as part of Windows ML,
Microsoft’s newly announced AI inference framework
at
Microsoft Build.
Together, they give developers NVIDIA-optimized acceleration through a standardized API, enabling seamless deployment across diverse hardware.
Figure 1. TensorRT for RTX in Windows ML inference stack
.
Foundry Local is a collection of popular models optimized by Microsoft
What is TensorRT for RTX
TensorRT for RTX is an inference library that is purpose-built for Windows. Building on the previous
NVIDIA TensorRT Inference
library’s strong performance for datacenter GPUs, this new release optimizes for NVIDIA RTX GPUs, over 50% compared to baseline DirectML, as seen in Figure 2. It also supports different quantization types, including FP4, enabling next-generation generative AI models like FLUX-1.dev to fit on consumer GPUs.
A key advantage is that it doesn’t need to pre-generate compiled inference engines, as these can be generated on the target GPU in seconds, as seen in Figures 5 and 6. These SKU-specific engines can boost performance by up to an additional 20% compared to
hardware-compatible
engines. The library is now lightweight, at just under 200 MB, and doesn’t need to be pre-packaged in the app if using Windows ML, as Windows ML will download the necessary libraries in the background automatically.
Figure 2. Performance measured on GeForce RTX 5090. TensorRT for RTX offers a significant speedup compared to DirectML for popular PC AI workloads.
Developers can use native acceleration of FP4 and FP8 computations on dedicated NVIDIA Tensor Cores with NVIDIA RTX GPUs, unlocking higher throughput, as seen in Figure 3.
Figure 3. TensorRT for RTX uses FP8 and FP4 GEMMs for diffusion models, boosting throughput. FP16 pipeline was run in low-VRAM mode
TensorRT for RTX is available in the Windows ML public preview. A standalone library will also be available from
developer.nvidia.com
in June.
We have been sampling TensorRT for RTX with developers for feedback and are amazed at the reception.
“Topaz Labs integrated the library quickly, and it eliminated our requirement to pre-generate TensorRT engines, a process that previously took us weeks,” said Dr. Suraj Raghuraman, Head of AI Engine,
Topaz Labs
.
“TensorRT for RTX easily beat PyTorch’s FP16 performance on a Windows PC by more than 70% for both txt2video and img2video use-cases of our LTX-Video 2B model (v0.9.6). With FP8, we got an additional 30% boost. All of that with an enviable on-device JIT time of less than 5 seconds. We’re excited to explore what the library can do with our latest LTX-Video 13B model (v0.9.7),” said Ofir Bibi, VP Research,
Lightricks
.
Compiling models with TensorRT for RTX
TensorRT for RTX inference library uses the concept of just-in-time (JIT) compilation and optimizes neural networks for RTX GPUs. The overall process is efficient, taking just seconds on end-user devices, as seen in Figures 5 and 6 below. This is a one-time process that can be executed at application installation time. Today, the library supports CNNs, audio, diffusion, and transformer models.
Figure 4. TensorRT for RTX works in two phases, a GPU-agnostic AOT and a device-specific JIT
TensorRT for RTX streamlines the conversion of trained neural networks in ONNX format or defined via native C++ APIs, into highly optimized inference engines through a two-stage process, as shown in Figure 4.
AOT compilation stage
The GPU-agnostic AOT phase executes entirely on a CPU. This stage performs graph optimizations and generates an intermediate engine, which can be configured to optionally exclude weights. This intermediary engine is cross-GPU and cross-OS compatible, allowing developers to build hardware-optimized inference engines on any RTX GPU connected to an x86/amd64 host on a Windows or Linux system.
This enables the “build once, deploy on any NVIDIA GPU” approach to streamline development and deployment workflows. This process requires a minimal library footprint of less than 100 MB, and typically completes in under 15 seconds, as seen in Figure 5. Developers can either run the AOT stage offline and package the intermediate engines with the application or ship the AOT library along with the application and run it on target devices.
Figure 5. TensorRT-RTX AOT compilation times under 15s for 100s of PC AI workloads
This set consists of proprietary and OSS models, including SD2.1, SD3, SDXL, FLUX, ResNet, Mobilenet, DenseNet, Bert, Llama, Phi, VGG, T5, Inception, EfficientNet, and many more. The AOT stage needs to run only once for any given network.
JIT compilation stage
During the JIT compilation phase, the intermediate engine is converted into a final executable engine optimized for the target GPU. Harnessing the full capabilities of the NVIDIA CUDA programming model, it maximizes performance across GPU architectures. The JIT process typically completes in a few seconds, with the compiled kernels cached on the device for near-instantaneous subsequent invocations. Like the AOT stage, the JIT library remains lightweight under 100 MB, ensuring efficient resource utilization.
Figure 6. TensorRT-RTX JIT compilation times under 5s for 100s of PC AI workloads on RTX 5090
Optimizing developer workflows for PC AI use cases
Apart from building performant engines faster with a small library footprint, TensorRT for RTX also offers unique capabilities to improve the AI experience in Windows apps for the end user.
In the case of diffusion models, TensorRT for RTX can handle text-to-image workloads with potentially unlimited WxH shape dimensions. Instead of forcing app developers to define fixed shape ranges ahead of time in optimization profiles, the JIT stage of the pipeline can automatically handle any shape requested by the end-user.
This is because the JIT library comes with a default, albeit less performant kernel implementation for any dynamic shape. As is typical with any image generation app, the user may want to build more images until they are satisfied with the quality and semantic accuracy. In the meantime, while the user keeps regenerating more images, the JIT runtime quickly adjusts to the specific shape dimensions that the user wants and starts generating performant kernels in the background. Thus, ‌inference performance gets better after one or two iterations by as much as 15%, as the performant kernels automatically replace the default kernels in the background.
TensorRT for RTX also offers a configurable runtime kernel cache for developers that can be shared across multiple models within the same app. The cache makes kernel generation faster for similar workloads between different models. It also enables near-instantaneous kernel generation on subsequent app launches. Developers can choose where to save the cache on disk and how to manage it during app or library updates.
TensorRT for RTX supports a wide range of precisions like FP32, FP16, BF16, FP8, INT8, FP4, and INT4, making it suitable for different use cases. Quantized INT8 is supported on all NVIDIA RTX GPUs, FP8 on NVIDIA Ampere GPUs and newer, and FP4 on NVIDIA Blackwell GPUs. INT4 optimizations are enabled through weight-only quantization. All quantization techniques can be easily used with
TensorRT Model Optimizer
. TensorRT for RTX library offers the fastest path to productizing novel datatypes on NVIDIA RTX GPUs before vendor-agnostic frameworks can catch up. These tools enable next-generation models to be optimized to fit on RTX GPUs.
It can also work simultaneously with other resource-intensive workloads, such as graphics.
Conclusion
We’re thrilled to announce TensorRT for RTX at
Microsoft Build
as a dedicated inference deployment solution for NVIDIA RTX GPUs and support for Windows ML. With a lean size of 200 MB, the library has slashed build times and exceeded runtime performance by over 50% over popular solutions available today, bringing in a new era of simplified usability, extended portability, and maximum performance. It can be used for accelerating CNNs, diffusions, audio, and transformer models in PC applications through Windows ML as an execution provider or directly as an independent library.
It can be used for accelerating CNNs, diffusions, audio, and transformer models in PC applications through Windows ML as an execution provider or directly as an independent library. While the Windows ML path offers developers automatic access to NVIDIA-specific accelerations with a standardized API, developers who want additional control can directly integrate the library.
Windows ML preview build with TensorRT for RTX EP will be available from
Microsoft Windows ML
. The TensorRT for RTX SDK will also be generally available for download in June at
developer.nvidia.com
.
Developers attending Microsoft Build can also visit our session,
Supercharge AI on RTX AI PCs with TensorRT BYOD
, on Tuesday, May 20 at 11:45 am PDT or on Wednesday, May 21 at 10:45 am PDT.