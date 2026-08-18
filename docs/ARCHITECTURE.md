# Architecture

## System definitions

| Layer | Vulkan IQ3_XXS | ROCm ROCmFPX |
|---|---|---|
| Runtime | `strix-halo-llamacpp` v0.6.4, commit `baf6360be95b00fa98659cb86afc364f4ff45513` | Lucebox commit `90f85fa401c6a3c61d9e4d0e2da7fc48a5e8915e` plus 11 hash-pinned patches |
| GPU backend | Portable Mesa RADV/Vulkan bundle | Ubuntu ROCm 7.1, HIP `gfx1151`, rocWMMA `rocm-7.1.1` |
| Target | Unsloth UD-IQ3_XXS, four GGUF files, 104.21 GB | ROCmFPX MIX, one GGUF file, 98.29 GB |
| Draft | DSpark Q2_K/Q8_0, 6.98 GB | DSpark Q4RMFP4 dense-F16, 10.65 GB |
| KV cache | q8_0 K/V | q4_0 K/V |
| Speculation | DSpark maximum draft length 4 | DSpark Q=4 with fused verification |
| Prefix reuse | One active llama.cpp slot | One explicit prefix-cache slot |
| Host policy | CPU boost off, GPU DPM auto | CPU boost on, GPU DPM high |

The target model verifies final output in both systems. Draft models affect
proposal generation and throughput; they do not replace target verification.

## Shared host layer

Both manifests require one 131,072-token server slot and the same host
boundary: large GTT kernel parameters, 120/120/120 W STAPM/fast/slow limits,
2.0 GHz minimum CPU frequency, cgroup memory limits, swap disabled, and maximum
AXB35 cooling while the service is active.

Ansible owns the GRUB drop-in, runtime artifacts, model artifacts, build
inputs, host-policy controller, cooling driver, systemd unit, and release
record. Downloaded artifacts and records use immutable release paths under
`/opt/m5`; the ROCm build manifest also pins the absolute source, build, and
header paths because those strings are present in the qualified ELF. The
active API is loopback-only at `127.0.0.1:18109`.

## Runtime integrity

Vulkan IQ3_XXS verifies the portable archive, launcher, server, manifest,
Vulkan loader, and models against the manifest identities.

ROCm ROCmFPX verifies the source commit, submodule commit, rocWMMA commit,
individual patch hashes, combined binary diff hash, compiled server size and
SHA-256, linked libraries, and eight targeted API/reasoning/tool-call unit
tests. Activation stops if any identity differs from the qualified release.
