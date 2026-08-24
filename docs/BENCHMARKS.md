# Benchmarks

The qualified comparison covers **Strix Halo llama.cpp Vulkan IQ3_XXS** with
the 4–15 Lightning Indexer cooperative-matrix dispatch and **Lucebox ROCm
ROCmFPX** as defined in [ARCHITECTURE.md](ARCHITECTURE.md). Both systems were
measured on the same 128 GiB Ryzen AI Max+ 395 host with thinking disabled.

## Workloads

- **2K generation:** input processing and generated-token throughput after a
  fixed synthetic prompt of approximately 2,000 tokens.
- **Cold retrieval:** input processing, generation, and byte-exact recovery of
  five keys placed across prompts from 59,933 through 491,520 tokens.
- **Quality:** ten coding, ten GSM8K-style, and ten MATH-style tasks.

## Qualified comparison

| System | 2K generation | 122,879-token input | 122,879-token generation | Quality |
|---|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 40.79 tok/s | 215.96 tok/s | 32.60 tok/s | 30/30 |
| **Lucebox ROCm ROCmFPX** | 29.10 tok/s | 131.19 tok/s | 16.40 tok/s | 30/30 |

The default leads generation and long-prompt input processing while both
systems pass the same quality gate and recover all five retrieval keys.

## Context scaling

The table includes every published prompt-length measurement. The 2K rows use
the fixed generation workload; all longer rows use cold five-key retrieval.

| System | Workload | Server allocation | Exact prompt | Input processing | Generation |
|---|---|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | Generation | 131,072 | 2,040 | 32.07 tok/s | 40.79 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | Retrieval | 131,072 | 59,933 | 235.00 tok/s | 36.48 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | Retrieval | 131,072 | 122,879 | 215.96 tok/s | 32.60 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | Retrieval | 262,144 | 163,840 | 206.92 tok/s | 30.47 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | Retrieval | 262,144 | 212,992 | 193.56 tok/s | 28.59 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | Retrieval | 262,144 | 245,760 | 185.88 tok/s | 27.21 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | Retrieval | 524,288 | 491,520 | 145.81 tok/s | 20.01 tok/s |
| **Lucebox ROCm ROCmFPX** | Generation | 131,072 | 2,048 | 250.99 tok/s | 29.10 tok/s |
| **Lucebox ROCm ROCmFPX** | Retrieval | 131,072 | 122,879 | 131.19 tok/s | 16.40 tok/s |

Every retrieval row recovered 5/5 keys byte-for-byte.

## Measurement rules

| Case | Protocol | Reported value |
|---|---|---|
| 2K generation | Fixed source prompt; 2,048 requested input tokens; 510 forced output tokens; temperature 0; top-k 1; top-p 1 | Server-reported input and generated-token rates |
| Retrieval | Identical synthetic filler and five values at approximately 2%, 20%, 50%, 80%, and 98% depth; 256-token output cap; cold KV state | Server-reported input and generated-token rates; all five values must match byte-for-byte |
| Quality | Pinned 30-task fixtures; temperature 0; 512-token output cap | Coding tests execute generated Python; numeric tasks use pinned extractors |

Every reported request disables thinking. The APIs count the nominal 2K input
as 2,040 and 2,048 tokens respectively.

## Patch qualification

The 4–15 dispatch passed 600/600 Vulkan kernel-correctness cases, 30/30 quality
tasks, 12/12 held-out exact-output comparisons, and 15/15 repeated maximum-
reasoning operational runs with no truncations. The target model still verifies
every speculative token; the patch changes only which existing Lightning
Indexer shader handles target-verification batches of four through fifteen.

## Quality detail

| System | Coding | GSM8K-style | MATH-style | Total |
|---|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 10/10 | 10/10 | 10/10 | 30/30 |
| **Lucebox ROCm ROCmFPX** | 10/10 | 10/10 | 10/10 | 30/30 |

The `math_08` fixture is evaluated against the algebraically correct reference
answer `20/3`.

## Cooling qualification

The default samples the kernel GPU-busy counter once per second, returns all
three fans to firmware-auto after 300 idle seconds, and restores fixed level 5
within 1.520 seconds of detected work. Observer-mode prefill, decode, and
end-to-end ratios versus the fixed-fan baseline were 1.0000, 1.0018, and
1.0018; controller or counter failure selects maximum cooling.

## Reproduction data

[`results.json`](../benchmarks/results.json) records the prompt definitions and
hashes, key values, request parameters, hardware, manifests, runtime identities,
all scaling points, and qualification aggregates.

Quality uses all ten cases from each `bench_he.jsonl`, `bench_gsm.jsonl`, and
`bench_math.jsonl` file in the [Lucebox harness at commit
`90f85fa`](https://github.com/Luce-Org/lucebox/tree/90f85fa401c6a3c61d9e4d0e2da7fc48a5e8915e/harness).
The file and runner SHA-256 values are recorded in `results.json`.

Strix Halo llama.cpp was measured at 120 W with CPU boost off and GPU DPM auto;
Lucebox was measured at 120 W with CPU boost on and GPU DPM high.
