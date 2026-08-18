# Architecture

## System definitions

| Layer | Strix Halo llama.cpp Vulkan IQ3_XXS | Lucebox ROCm ROCmFPX |
|---|---|---|
| Runtime | Unmodified `strix-halo-llamacpp` v0.6.4 portable release, commit `baf6360be95b00fa98659cb86afc364f4ff45513` | Lucebox commit `90f85fa401c6a3c61d9e4d0e2da7fc48a5e8915e` plus [11 patches](#lucebox-source-modifications) |
| GPU backend | Bundled Mesa RADV/Vulkan | Ubuntu ROCm 7.1, HIP `gfx1151`, rocWMMA `rocm-7.1.1` |
| Target | Unsloth UD-IQ3_XXS, four GGUF files, 104.21 GB | ROCmFPX MIX, one GGUF file, 98.29 GB |
| Draft | DSpark Q2_K/Q8_0, 6.98 GB | DSpark Q4RMFP4 dense-F16, 10.65 GB |
| KV cache | q8_0 K/V | q4_0 K/V |
| Speculation | Maximum draft length 4 | Q=4 with fused verification |
| Prefix reuse | One llama.cpp slot | One explicit prefix-cache slot |
| CPU/GPU policy | CPU boost off, GPU DPM auto | CPU boost on, GPU DPM high |

The target model verifies final output in both systems; the draft model only
proposes tokens.

## Runtime modification status

The Strix Halo llama.cpp executable and launcher are used exactly as published
in v0.6.4. Ansible supplies the pinned Vulkan loader, model files, environment,
and service definition without patching that runtime.

### Lucebox source modifications

The Lucebox build applies these functional changes:

- ROCm 7.1 host/device wavefront detection:
  [`lucebox-rocm71-host-wavefront.patch`](../patches/lucebox-rocm71-host-wavefront.patch).
- DeepSeek tool-call parsing for OpenAI wrappers, native
  `function`/`parameters`, and multi-tool JSON:
  [`function-call`](../patches/lucebox-deepseek-function-call.patch),
  [`function-parameters`](../patches/lucebox-deepseek-function-parameters.patch),
  and [`multi-tool buffering`](../patches/lucebox-multi-tool-json-buffer.patch).
- DeepSeek reasoning API and `low`, `high`, and `max` effort handling:
  [`reasoning`](../patches/lucebox-deepseek-v4-reasoning.patch) and
  [`effort levels`](../patches/lucebox-deepseek-v4-official-effort-v2.patch).
- Selectable attention implementation in fused verification:
  [`attention selection`](../patches/lucebox-ds4-fused-verify-attention-select.patch).
- F16 KV reuse with bounded F32 key attention for short verifier steps:
  [`F16 KV`](../patches/lucebox-ds4-fused-explicit-f16-kv.patch) and
  [`F16/F32 attention`](../patches/lucebox-ds4-explicit-f16-f32-attention.patch).
- Configurable decode-graph cache capacity and adaptive prefill chunks for the
  128K memory envelope:
  [`cache capacity`](../patches/lucebox-deepseek-decode-attn-cache-cap.patch)
  and [`adaptive prefill`](../patches/lucebox-ds4-adaptive-prefill-cache-one.patch).

The manifest verifies every patch, the combined source diff, and the compiled
server. Eight targeted unit tests cover the tool and reasoning changes.

## Shared host layer

Both manifests allocate one 131,072-token slot and apply the same large-GTT
kernel parameters, 120/120/120 W package limits, 2.0 GHz minimum CPU frequency,
cgroup memory limits, disabled swap, and maximum AXB35 cooling while active.

Ansible owns the GRUB drop-in, artifacts, host-policy controller, cooling
driver, systemd unit, and release record. The service is enabled at boot and
binds to `127.0.0.1:18109`.
