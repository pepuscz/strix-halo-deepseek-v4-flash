# Benchmarks

The default is the unmodified official v0.7.0 release of **Strix Halo llama.cpp
Vulkan IQ3_XXS**. **Lucebox ROCm ROCmFPX** is the leading alternative. Both
were measured on the same 128 GiB Ryzen AI Max+ 395 host with thinking
disabled.

## Workloads

- **Cold retrieval:** input processing, generation, and byte-exact recovery of
  five keys placed across prompts from 2,040 through 491,520 tokens.
- **Quality:** ten coding, ten GSM8K-style, and ten MATH-style tasks.

## Measured comparison

| System | 122,879-token input | 122,879-token generation | Quality |
|---|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 226.82 tok/s | 35.73 tok/s | 30/30 |
| **Lucebox ROCm ROCmFPX** | 142.82 tok/s | 29.60 tok/s | 29/30 |

The default leads generation, long-prompt input processing, and the published
quality set. Both systems recover all five retrieval keys.

## Context scaling

The table includes every published prompt-length measurement using the same
cold five-key retrieval workload.

| System | Server allocation | Exact prompt | Input processing | Generation |
|---|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 131,072 | 2,040 | 245.23 tok/s | 40.04 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 131,072 | 3,840 | 260.12 tok/s | 38.98 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 131,072 | 7,680 | 254.07 tok/s | 37.70 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 131,072 | 15,359 | 254.94 tok/s | 40.09 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 131,072 | 30,720 | 250.59 tok/s | 39.48 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 131,072 | 59,933 | 244.19 tok/s | 37.90 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 131,072 | 122,879 | 226.82 tok/s | 35.73 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 262,144 | 163,840 | 218.56 tok/s | 34.12 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 262,144 | 212,992 | 206.65 tok/s | 32.77 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 262,144 | 245,760 | 200.21 tok/s | 31.77 tok/s |
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 524,288 | 491,520 | 163.23 tok/s | 25.02 tok/s |
| **Lucebox ROCm ROCmFPX** | 131,072 | 7,680 | 213.91 tok/s | 36.90 tok/s |
| **Lucebox ROCm ROCmFPX** | 131,072 | 30,720 | 201.68 tok/s | 32.00 tok/s |
| **Lucebox ROCm ROCmFPX** | 131,072 | 122,879 | 142.82 tok/s | 29.60 tok/s |

Every retrieval row recovered 5/5 keys byte-for-byte.

## Measurement rules

| Case | Protocol | Reported value |
|---|---|---|
| Retrieval | Identical synthetic filler and five values at approximately 2%, 20%, 50%, 80%, and 98% depth; temperature 0; top-k 1; top-p 1; 256-token output cap; one run; cold KV state | Server-reported input and generated-token rates; all five values must match byte-for-byte |
| Quality | Pinned 30-task fixtures; temperature 0; 512-token coding, 1,024-token GSM8K-style, and 2,048-token MATH-style completion limits | Coding tests execute generated Python; numeric tasks use pinned extractors |

Every reported request disables thinking. The scaling curve begins with a
2,040-token cold-retrieval request.

## Validation

Strix Halo llama.cpp v0.7.0 passed all eleven cold-retrieval points, 30/30 quality tasks,
12/12 held-out comparisons, and 15/15 repeated maximum-reasoning operational
runs with no truncations. The cached 8K agent conversation hit all five eligible
prefixes. Streaming, non-streaming, namespace, JSON-normalization, and live Exa
contracts passed. At 491,520 tokens, speculative decoding was 2.11× the matched
no-spec generation rate.

Lucebox commit `5eb4fbe` passed its pinned build and kernel tests, 15/15 exact
retrieval checks across 7,680, 30,720, and 122,879 input tokens, 12/12 Hermes
tool-result cases, and the memory and safety checks. It scored 29/30 because
`math_10` returned `998`; the expected answer is `997`.

## Quality detail

| System | Coding | GSM8K-style | MATH-style | Total |
|---|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 10/10 | 10/10 | 10/10 | 30/30 |
| **Lucebox ROCm ROCmFPX** | 10/10 | 10/10 | 9/10 | 29/30 |

The `math_08` fixture is evaluated against the algebraically correct reference
answer `20/3`. The Lucebox miss is `math_10`, for which the expected answer is
`997`.

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

Strix Halo llama.cpp v0.7.0 was measured at 120 W with CPU boost off and GPU DPM
auto; Lucebox was measured at 120 W with CPU boost on and GPU DPM high.
