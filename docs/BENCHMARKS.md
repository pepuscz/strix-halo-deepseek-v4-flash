# Benchmarks

These results compare the selected Nathan/Vulkan release with the closest
qualified Lucebox release on one physical BOSGAME M5. They are local inference
measurements, not vendor claims and not an official model leaderboard.

## Winner-versus-winner result

| Frozen workload | Nathan selected | Lucebox selected | Nathan delta |
|---|---:|---:|---:|
| Short decode, requested 2,048 in / 510 out | 26.67 tok/s | 28.20 tok/s | -5.4% |
| Real-128K prefill, 122,879 input tokens | 128.70 tok/s | 11.34 tok/s | 11.35x |
| Real-128K decode, up to 256 output tokens | 19.41 tok/s | 10.40 tok/s | +86.6% |
| Corrected frozen quality set | 27/30 | 30/30 | -3 tasks |
| Tool-call contract | pass | pass | tie |

The real-128K request used the same prompt SHA-256, the same 122,879-token
input, five needles at approximately 2/20/50/80/98 percent depth, and required
all five values byte-exact. Both stacks passed 5/5.

The short test used the same source prompt SHA-256 and output budget. The two
servers counted it as 2,040 and 2,048 input tokens respectively, so it is a
matched source-prompt control rather than an assertion of identical internal
tokenization. Each short result is the median of three measured runs after one
warmup.

## Hardware policies

This table compares each software stack at its selected, tested operating
point:

| Setting | Nathan | Lucebox |
|---|---|---|
| STAPM / fast / slow | 120 / 120 / 120 W | 100 / 100 / 100 W |
| CPU governor/minimum | performance / 2.0 GHz | performance / 2.0 GHz |
| CPU boost | off | on |
| GPU DPM | auto | high |
| Context allocation | 131,072 | 131,072 |
| Target format | Unsloth UD-IQ3_XXS, 104.21 GB | ROCmFPX, 98.29 GB |
| Draft | DSpark Q2_K/Q8_0 | DSpark ROCmFPX |
| KV | q8_0 / q8_0 | Q4_0 / Q4_0 |

This is deliberately **not** labeled a pure software-only A/B. A reciprocal
Lucebox boost-off/GPU-auto control was interrupted by accidental AC loss and is
excluded. However, a completed Nathan control in the same room at 100/100/100 W
still produced 125.45 prefill and 18.92 decode tok/s with 5/5 retrieval. The
large long-context advantage therefore is not explained by Nathan's extra 20 W.

## Quality result

The frozen 30-task gate used ten small coding tasks, ten GSM8K-style tasks, and
ten MATH-style tasks with temperature zero and a 512-token output cap. Both
stacks used the same target model family but different quantization/runtime
representations.

| Category | Nathan | Lucebox |
|---|---:|---:|
| Coding | 7/10 | 10/10 |
| GSM8K | 10/10 | 10/10 |
| MATH, corrected scorer | 10/10 | 10/10 |
| Total | 27/30 | 30/30 |

Nathan's three coding failures (`he_01`, `he_02`, and `he_07`) reasoned toward
the correct algorithms but wrote a long explanation first, consumed exactly
512 output tokens, and truncated the final code. They remain failures because
the API response was not executable. The MATH figure corrects one known bad
gold answer (`math_08`, correct value `20/3`) in the frozen harness.

Lucebox additionally completed HumanEval+ at 131/164 with zero request errors,
identical to its earlier six-expert 8K baseline. Nathan has not run that full
164-task suite, so no equivalent Nathan HumanEval+ claim is made.

## Reddit-reproduction control

The source article reported about 27 output tok/s on Strix Halo. Our quick
implementation check used a 2,209-token input and a 4,096-token output budget:

| Metric | Result |
|---|---:|
| Prefill | 261.11 tok/s |
| Decode | 35.46 tok/s |
| Speculative acceptance | 95.60% |
| End-to-end output | 33.03 tok/s |

It validates that the Nathan Vulkan + DSpark path is active and in the expected
performance range. It is not claimed as an exact reproduction of the author's
prompt, OS image, thermals, or measurement method.

## Safety evidence

During the selected 120 W real-128K run, minimum effective ordinary-page
headroom (`MemAvailable - CmaFree`) was 13,787,464 KiB, above the immutable
4 GiB floor. Peak sampled GPU and CPU temperatures were 81.0 C and 80.5 C.
Cgroup OOM events were zero; all three fans remained fixed at level 5 and
returned to firmware-auto after the model stopped.

The machine-readable aggregate is [results.json](../benchmarks/results.json).
It intentionally contains no host address, username, SSH key, local home path,
or private repository reference.
