# Benchmarks

**Vulkan IQ3_XXS** is the Vulkan/`strix-halo-llamacpp` system with an Unsloth
UD-IQ3_XXS target; **ROCm ROCmFPX** is the ROCm/Lucebox system with a ROCmFPX
MIX target. Measurements used one BOSGAME M5 and the exact configuration in
each release manifest.

## Results

| Workload | Vulkan IQ3_XXS | ROCm ROCmFPX |
|---|---:|---:|
| Short decode, 2,048 input / 510 output requested | 35.01 tok/s | 29.10 tok/s |
| Real-128K prefill, 122,879 input tokens | 130.63 tok/s | 131.19 tok/s |
| Real-128K decode, up to 256 output tokens | 22.43 tok/s | 16.40 tok/s |
| Real-128K byte-exact retrieval | 5/5 | 5/5 |
| Six-request cached tool conversation, aggregate prefill | 35.604 s | 47.377 s |
| Six-request cached tool conversation, wall time | 38.283 s | 50.313 s |
| Fixed 30-task quality gate | 26–27/30 observed | 30/30 |
| Tool-call contract | pass | pass |

Vulkan IQ3_XXS is the default for its higher decode throughput and lower cached
conversation latency; ROCm ROCmFPX has the higher observed 30-task score.

The exact qualified operating points are 120 W with CPU boost off and GPU DPM
auto for Vulkan IQ3_XXS, and 120 W with CPU boost on and GPU DPM high for ROCm
ROCmFPX.

## Benchmark datasets

| Dataset | Reproducible definition | Scoring |
|---|---|---|
| Short throughput | The instruction requests consecutive integers and is padded with repeated ` x` until the source tokenizer reaches 2,048 tokens. Prompt SHA-256: `3ed38be9c93333e209a66ada0b10efbde517b06f9a6b6d727b0e216b0c890463`. Temperature 0, top-k 1, top-p 1, one warmup, 510 forced output tokens. | Median server-reported decode rate: six Vulkan runs and three ROCm runs. |
| 128K retrieval | Deterministic five-key retrieval prompt with records at 2%, 20%, 50%, 80%, and 98% depth. Target length 122,880; observed length 122,879. Prompt SHA-256: `f5d337a32fbf5e29f150974500a8d49cff172c2d03c125a243f6c990e1dbd7a3`. Output cap 256. | All five values must match byte-for-byte; prefill and decode rates come from the same request. |
| Quality-30 | All ten cases from each of Lucebox's pinned `bench_he.jsonl`, `bench_gsm.jsonl`, and `bench_math.jsonl` fixtures at [commit `90f85fa`](https://github.com/Luce-Org/lucebox/tree/90f85fa401c6a3c61d9e4d0e2da7fc48a5e8915e/harness). Temperature 0; output cap 512. | Coding tests execute generated Python; GSM and MATH use the pinned answer extractors. The known incorrect `math_08` reference is corrected to `20/3`. |
| Cached tool conversation | Six requests in one growing conversation with the same ten-tool schema, starting near 8,192 tokens. The first request is cold and the following five must report prefix hits. | Aggregate server-reported prefill time and client wall time. |

The quality fixture SHA-256 values are:

- `bench_he.jsonl`: `7886d54c7f1c7520f8410a01ebdcf044f99e2ded0144ad0cc509c746052c0533`
- `bench_gsm.jsonl`: `3531e758101b3580f23323c3e62b17bfd7435301e69c09d4834f08b95abb91af`
- `bench_math.jsonl`: `3fec033244bc8a6a55ce9ab651e3334ef12836cd82bad2defb7bdadb93e602fb`
- `client_test_runner.py`: `a4db6be2a77623a6e3976af80edfb1c80cb0e25161ac01b64102aa08a6c14c0e`

The source prompt is identical across systems, although their API tokenizers
reported 2,040 and 2,048 tokens for the short workload. No additional context
length was measured with both exact qualified releases, so no other context
sizes are reported.

## Quality results

The fixed gate contains ten small coding tasks, ten GSM8K-style tasks, and ten
MATH-style tasks at temperature zero with a 512-token output cap.

| Category | Vulkan IQ3_XXS | ROCm ROCmFPX |
|---|---:|---:|
| Coding | 6–7/10 observed | 10/10 |
| GSM8K | 10/10 | 10/10 |
| MATH, corrected scorer | 10/10 | 10/10 |
| Total | 26–27/30 observed | 30/30 |

The Vulkan range records two runs; every observed coding failure reached the
512-token cap with truncated code.

The machine-readable aggregate is [results.json](../benchmarks/results.json).
