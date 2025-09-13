# Run High-Performance AI Applications with NVIDIA TensorRT for RTX

**URL:** https://developer.nvidia.com/blog/run-high-performance-ai-applications-with-nvidia-tensorrt-for-rtx/

**Author:** Rajeev Rao

**Published:** 2025-06-12

**Categories:** generative_ai, nim_microservices, performance_optimization

**Scraped:** 2025-09-11 04:26:29 UTC

---

NVIDIA TensorRT for RTX is now
available for download
as an SDK that can be integrated into C++ and Python applications for both Windows and Linux. At Microsoft Build, we
unveiled
this streamlined solution for high-performance AI inference that supports NVIDIA GeForce RTX GPUs from NVIDIA Turing through NVIDIA Blackwell generations, including the latest NVIDIA RTX PRO lineup.
This first release delivers high-performance inference across a wide range of workloads, including convolutional neural networks (CNNs), speech models, and diffusion models. TensorRT for RTX is ideal for creative, gaming, and productivity applications. We also have a
GitHub project repository
with introductory API samples and demos to help developers get started quickly.
What is TensorRT for RTX?
TensorRT for RTX builds on the proven performance of the
NVIDIA TensorRT
inference library, but simplifies the deployment of AI models on NVIDIA RTX GPUs across desktops, laptops, and workstations.
TensorRT for RTX is a drop-in replacement for NVIDIA TensorRT. TensorRT for RTX introduces a Just-In-Time (JIT) optimizer in the runtime that compiles improved inference engines directly on the end-user’s RTX-accelerated PC. This eliminates the need for lengthy pre-compilation steps and enables rapid engine generation, improved application portability, deployment workflow, and runtime performance, delivering high inference speed.
To support integration into lightweight applications and deployment in memory-constrained environments, TensorRT for RTX is compact under 200 MB.
This makes real-time, responsive AI applications for image processing, speech synthesis, and generative AI practical and performant on consumer-grade devices.
Video 1. Cutting engine build times while delivering peak performance with TensorRT for RTX
The TensorRT for RTX SDK includes:
Support for Windows (zip) and Linux (tar)
Header files for C++ development
Python bindings for rapid prototyping
Optimizer and runtime library for deployment
Parser library for importing ONNX models
Developer tools for simplifying deployment and benchmarking
See the
install guide
for information on downloading and installing the TensorRT for RTX SDK.
Key features of TensorRT for RTX
TensorRT for RTX optimizations are applied in two phases.
Phase 1: In Ahead-Of-Time (AOT) optimization, the model graph is improved and converted to an engine that can be serialized for deployment.
Phase 2: At runtime, the JIT optimizer specializes the engine for execution on the installed RTX GPU.
See this optimization and deployment workflow in our
helloWorld sample
.
For ONNX model deployment, we also provide a command-line tool, tensorrt_rtx,  for building and profiling TensorRT for RTX engines. Refer to the
documentation
to learn more.
Other new features offer greater control over deployment workflows and improved performance in real-world applications. The following is a quick recap of some of these advancements.
Dynamic shapes
The dynamic shapes feature provides the ability to defer specifying some or all tensor dimensions for network inputs and outputs until runtime.
The dynamic dimensions are specified by assigning
-1
to their size.
auto input = network->addInput("input", nvinfer1::DataType::kFLOAT, nvinfer1::Dims2{-1, kInputSize});
Optimization profile(s) describing the dynamic range of the input dimensions must be specified in the builder configuration.
nvinfer1::IOptimizationProfile* profile = builder->createOptimizationProfile();
profile->setDimensions("input", nvinfer1::OptProfileSelector::kMIN, nvinfer1::Dims2(1, kInputSize));
profile->setDimensions("input", nvinfer1::OptProfileSelector::kOPT, nvinfer1::Dims2(4, kInputSize));
profile->setDimensions("input", nvinfer1::OptProfileSelector::kMAX, nvinfer1::Dims2(32, kInputSize));

builderConfig->addOptimizationProfile(profile);
At runtime, when the execution context is created, the JIT optimizations generate fallback kernels that can run inference on the entire range of input shapes. The desired optimization profile and runtime shapes of all dynamic dimensions must be selected before inference.
context->setOptimizationProfileAsync(0, stream);
context->setInputShape("input", nvinfer1::Dims2(1, kInputSize));
A major advantage of the dynamic shapes implementation in TensorRT for RTX compared to TensorRT is that shape-specialized kernels can be generated on the fly. These specialized kernels are compiled in a background thread while ‌initial inference requests are serviced using fallback kernels. The runtime automatically selects shape-specialized kernels when ready, resulting in performance optimizations that adapt to the use case.
Figure 1. FLUX.1-dev transformer model execution in steady-state (using shape-specialized kernels) is 60% faster than the first iteration (using fallback kernels). This free performance boost was realized without any code changes
To learn more about dynamic shapes, refer to the
documentation
.
Runtime cache
The runtime cache can be used to store the JIT-compiled kernels, and is created using the runtime configuration object.
auto runtimeCache = 
std::unique_ptr<nvinfer1::IRuntimeCache>(runtimeConfig->createRuntimeCache());

runtimeConfig->setRuntimeCache(*runtimeCache);
The execution context uses the attached runtime cache for all inference executions, and new JIT-compiled kernels are appended to the cache. Optionally, the cache can be serialized to a file for persistence across application invocations and installations, to avoid JIT recompilations. This reduces application startup time and enables peak performance out of the box.
auto serializedRuntimeCache = 
std::unique_ptr<nvinfer1::IHostMemory>(runtimeCache->serialize());
To learn more about runtime cache, refer to the
documentation
.
AOT without GPUs
TensorRT for RTX AOT-optimized engines are runnable on NVIDIA Ampere, Ada, and Blackwell generation NVIDIA RTX GPUs (see full
support matrix
), and don’t require a GPU for building. If broad portability is not required, developers may use TensorRT for RTX compute capability API to limit the target
GPU architecture(s)
for deployment, which helps reduce engine size and build time.
Figure 2. Engine size decreasing (lower is better), realized by specializing compilation to progressively fewer GPU compute capabilities
Figure 3. An illustration of time taken for AOT optimization (lower is better) observed when specializing compilation to progressively fewer GPU compute capabilities
For example, to build an engine that is runnable on Ada and Blackwell RTX GPUs, corresponding SM versions can be explicitly enumerated as the build targets using the builder configuration. See the
exhaustive list
of NVIDIA RTX GPUs and their compute capabilities.
builderConfig->setNbComputeCapabilities(2);
builderConfig->setComputeCapability(nvinfer1::ComputeCapability::kSM89, 0);
builderConfig->setComputeCapability(nvinfer1::ComputeCapability::kSM120, 1);
TensorRT for RTX can also automatically query the GPU capabilities and build an engine optimized for it. This is done by specifying
kCURRENT
as the compute capability target.
builderConfig->setNbComputeCapabilities(1);
builderConfig->setComputeCapability(nvinfer1::ComputeCapability::kCURRENT, 0);
TensorRT for RTX API is strongly typed, meaning the precision of operations expressed in the model graph can’t be changed during optimizations. Certain precisions, however, are only supported in newer GPU architectures. For the networks using them, the compute capability targets, if specified, must be limited to those GPU architectures (see
support matrix
). For example:
FP4 is only supported on NVIDIA Blackwell (SM120) and above.
FP8 is only supported on NVIDIA Ada (SM89) and above.
To learn more about AOT optimizations, refer to the
documentation
.
Weightless engines and refit
TensorRT for RTX enables engine building without weights. This helps minimize the shipment size of the application package if the weights are also shipped along with the engine, for example, as an ONNX model.
When building weight-stripped engines, it’s also important to mark them as refittable—the weights can be updated later.
builderConfig->setFlag(nvinfer1::BuilderFlag::kSTRIP_PLAN);
builderConfig->setFlag(nvinfer1::BuilderFlag::kREFIT);
During inference, a refitter object can be used to refuel weights for the weightless engines.
auto refitter = std::unique_ptr<nvinfer1::IRefitter>(
nvinfer1::createInferRefitter(*inferenceEngine, logger));

refitter->setNamedWeights("fc1 weights", fc1Weights);
refitter->setNamedWeights("fc2 weights", fc2Weights);
refitter->refitCudaEngine();
To learn more about weightless engines and refit, refer to the
documentation
.
See all these new features in action in our
apiUsage sample
.
Start building with TensorRT for RTX
Developers can download the
SDK
, explore code samples on
GitHub
, and dive into our
documentation
to get started.
For a practical example, check out our
demonstration of FLUX.1 [dev]
acceleration using TensorRT for RTX.
For more details, please refer to our
documentation
, including the
porting guide for TensorRT applications
and
performance best practices
.
We’d love to hear from you. Share your feedback, ask questions, or start a discussion on our GitHub
issues page
or the
TensorRT for RTX developer forum
. You can also connect with us on our
Discord channel
.