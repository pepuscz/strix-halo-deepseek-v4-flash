# Benchmarks

The comparison covers the unmodified **Strix Halo llama.cpp Vulkan IQ3_XXS**
runtime and the patched **Lucebox ROCm ROCmFPX** runtime defined in
[ARCHITECTURE.md](ARCHITECTURE.md). Both were measured on the same BOSGAME M5.

## Benchmark cases

- **2K-prompt generation:** generated-token throughput after a fixed synthetic
  prompt of approximately 2,000 tokens.
- **128K context:** input processing, generation, and five-key retrieval with
  an actual 122,879-token prompt.
- **Agent-cache:** end-to-end latency for six requests in one growing
  tool-using conversation.
- **Quality:** a fixed regression set containing ten coding, ten GSM8K-style,
  and ten MATH-style tasks.

## Results

| System | 2K-prompt generation | 128K-context input | 128K-context generation | 128K-context key retrieval | Agent-cache wall time | Quality |
|---|---:|---:|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 41.15 tok/s | 130.20 tok/s | 30.38 tok/s | 5/5 keys found | 37.946 s | 30/30 |
| **Lucebox ROCm ROCmFPX** | 29.10 tok/s | 131.19 tok/s | 16.40 tok/s | 5/5 keys found | 50.313 s | 30/30 |

The Strix Halo llama.cpp system is the default because it leads the matched
generation and agent-cache measurements. Both systems pass the same quality
gate; Lucebox is 0.75% faster on the single 128K input-processing run.

## Measurement rules

| Case | Protocol | Reported value |
|---|---|---|
| 2K-prompt generation | Fixed source prompt; 2,048 requested input tokens; 510 forced output tokens; thinking disabled; temperature 0; top-k 1; top-p 1; one warmup | Median server-reported generated-token rate from three measured runs per system |
| 128K context | Identical five-key prompt; 122,879 actual input tokens; 256-token output cap; thinking disabled; keys at approximately 2%, 20%, 50%, 80%, and 98% depth | Server-reported input-processing and generated-token rates; retrieval passes only when all five values match byte-for-byte |
| Agent-cache | Identical six-request conversation and ten-tool schema; thinking disabled; first request cold; five subsequent prefix hits | Client wall time for all six requests |
| Quality | Pinned 30-task fixtures; thinking disabled; temperature 0; 512-token output cap | Coding tests execute generated Python; GSM8K-style and MATH-style answers use the pinned extractors |

The two APIs count the identical 2K-prompt generation input as 2,040 and 2,048 tokens. No
other context size was measured with both exact qualified systems, so no
additional context curve is reported.

## Quality detail

| System | Coding | GSM8K-style | MATH-style | Total |
|---|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 10/10 | 10/10 | 10/10 | 30/30 |
| **Lucebox ROCm ROCmFPX** | 10/10 | 10/10 | 10/10 | 30/30 |

Both systems passed all 30 tasks. The `math_08` fixture is evaluated against
the algebraically correct reference answer `20/3`.

## Reproduction inputs

[`results.json`](../benchmarks/results.json) records the exact 2K-prompt generation instruction
and prompt hash, 128K-context key values and prompt hash, request parameters,
hardware, manifests, and aggregate results.

Quality uses all ten cases from each `bench_he.jsonl`, `bench_gsm.jsonl`, and
`bench_math.jsonl` file in the [Lucebox harness at commit
`90f85fa`](https://github.com/Luce-Org/lucebox/tree/90f85fa401c6a3c61d9e4d0e2da7fc48a5e8915e/harness).
The file and runner SHA-256 values are recorded in `results.json`.

Strix Halo llama.cpp was measured at 120 W with CPU boost off and GPU DPM auto;
Lucebox was measured at 120 W with CPU boost on and GPU DPM high.
