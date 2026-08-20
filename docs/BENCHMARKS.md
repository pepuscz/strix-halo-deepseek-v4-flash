# Benchmarks

The matched comparison covers the unmodified **Strix Halo llama.cpp Vulkan
IQ3_XXS** runtime and the patched **Lucebox ROCm ROCmFPX** runtime defined in
[ARCHITECTURE.md](ARCHITECTURE.md). Both were measured on the same BOSGAME M5
with a 131,072-token allocation and thinking disabled.

## Workloads

- **2K-prompt generation:** generated-token throughput after a fixed synthetic
  prompt of approximately 2,000 tokens.
- **122,879-token retrieval:** input processing, generation, and byte-exact
  recovery of five keys placed across the prompt.
- **Agent cache:** end-to-end latency for six requests in one growing
  tool-using conversation.
- **Quality:** ten coding, ten GSM8K-style, and ten MATH-style tasks.

## Matched results

| System | 2K-prompt generation | 122,879-token input | 122,879-token generation | Keys found | Agent-cache wall time | Quality |
|---|---:|---:|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 40.96 tok/s | 218.08 tok/s | 30.55 tok/s | 5/5 | 39.716 s | 30/30 |
| **Lucebox ROCm ROCmFPX** | 29.10 tok/s | 131.19 tok/s | 16.40 tok/s | 5/5 | 50.313 s | 30/30 |

The default leads generation, long-prompt input processing, and cached
tool-conversation latency while both systems pass the same quality gate.

## Strix Halo llama.cpp Vulkan IQ3_XXS context scaling

Each row is one cold five-key retrieval request using v0.6.6, q8_0 K/V, the
same target and draft, batch 2,048, microbatch 1,024, and one slot.

| Server allocation | Exact prompt | Input processing | Generation | Keys found |
|---:|---:|---:|---:|---:|
| 131,072 | 122,879 | 218.08 tok/s | 30.55 tok/s | 5/5 |
| 262,144 | 163,840 | 207.28 tok/s | 28.51 tok/s | 5/5 |
| 262,144 | 212,992 | 193.79 tok/s | 25.98 tok/s | 5/5 |
| 262,144 | 245,760 | 186.25 tok/s | 24.50 tok/s | 5/5 |
| 524,288 | 491,520 | 146.28 tok/s | 17.19 tok/s | 5/5 |

## Measurement rules

| Case | Protocol | Reported value |
|---|---|---|
| 2K-prompt generation | Fixed source prompt; 2,048 requested input tokens; 510 forced output tokens; temperature 0; top-k 1; top-p 1; one warmup | Median server-reported generated-token rate from three measured runs |
| Retrieval | Identical synthetic filler and five values at approximately 2%, 20%, 50%, 80%, and 98% depth; 256-token output cap; cold KV state | Server-reported input and generated-token rates; all five values must match byte-for-byte |
| Agent cache | Identical six-request conversation and ten-tool schema; first request cold; five subsequent prefix hits | Client wall time for all six requests |
| Quality | Pinned 30-task fixtures; temperature 0; 512-token output cap | Coding tests execute generated Python; numeric tasks use pinned extractors |

Every reported request disables thinking. The APIs count the identical 2K
input as 2,040 and 2,048 tokens respectively.

## Quality detail

| System | Coding | GSM8K-style | MATH-style | Total |
|---|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 10/10 | 10/10 | 10/10 | 30/30 |
| **Lucebox ROCm ROCmFPX** | 10/10 | 10/10 | 10/10 | 30/30 |

The `math_08` fixture is evaluated against the algebraically correct reference
answer `20/3`.

## Reproduction data

[`results.json`](../benchmarks/results.json) records the prompt definitions and
hashes, key values, request parameters, hardware, manifests, runtime identities,
and aggregate results.

Quality uses all ten cases from each `bench_he.jsonl`, `bench_gsm.jsonl`, and
`bench_math.jsonl` file in the [Lucebox harness at commit
`90f85fa`](https://github.com/Luce-Org/lucebox/tree/90f85fa401c6a3c61d9e4d0e2da7fc48a5e8915e/harness).
The file and runner SHA-256 values are recorded in `results.json`.

Strix Halo llama.cpp was measured at 120 W with CPU boost off and GPU DPM auto;
Lucebox was measured at 120 W with CPU boost on and GPU DPM high.
