# Architecture

## System definitions

| Layer | Strix Halo llama.cpp Vulkan IQ3_XXS | Lucebox ROCm ROCmFPX |
|---|---|---|
| Runtime | `strix-halo-llamacpp` v0.6.6 portable release, commit `7b6c61330edf370659f531932e0b91aca67ba055`, plus the [4–15 Lightning Indexer dispatch patch](../patches/0001-vulkan-lightning-indexer-small-cm-4-15.patch) | Lucebox commit `f686c447f067a04ea100a996e4c826e8cc4decc1` plus [four patches](#lucebox-source-modifications) |
| GPU backend | Bundled Mesa RADV/Vulkan | Ubuntu ROCm 7.1, HIP `gfx1151`, rocWMMA `rocm-7.1.1` |
| Target | Unsloth UD-IQ3_XXS, four GGUF files, 104.21 GB | ROCmFPX MIX, one GGUF file, 98.29 GB |
| Draft | DSpark Q2_K/Q8_0, 6.98 GB | DSpark Q4RMFP4 dense-F16, 10.65 GB |
| KV cache | q8_0 K/V | q4_0 K/V |
| Speculation | Maximum draft length 4 | Q=4 with fused verification |
| Context | One 524,288-token slot | One 131,072-token slot |
| Prefix reuse | llama.cpp slot cache | One explicit prefix-cache slot |
| CPU/GPU policy | CPU boost off, GPU DPM auto | CPU boost on, GPU DPM high |
| Cooling | GPU-demand governor: fixed level 5 while active, firmware-auto after 300 idle seconds, fixed level 5 on failure | Fixed level 5 while the model service is active |

The target model verifies final output in both systems; the draft model only
proposes tokens.

## Runtime modification status

The Strix Halo release keeps the v0.6.6 executable, launcher, bundled RADV
driver, and runtime libraries. A pinned overlay replaces only
`libggml-vulkan.so.0.20.1` with a clean rebuild from the same source commit and
the five-line 4–15 dispatch patch. The environment switch remains explicit, so
the upstream scalar dispatch is used if `GGML_VK_LIGHTNING_INDEXER_SMALL_CM`
is not enabled.

### Lucebox source modifications

The pinned Lucebox commit supplies the ROCm 7.1 build fixes, named-JSON tool
calls, and fused-verifier F16 KV reuse. The release adds:

- bounded monolithic prefill chunks and a one-entry decode graph cache for the
  128K memory envelope:
  [`128K bounds`](../patches/lucebox-ds4-monolithic-128k-bounds.patch);
- the gfx1151 48-column MMQ tile at narrow prefill widths:
  [`narrow MMQ`](../patches/lucebox-gfx1151-narrow-mmq-x48.patch);
- vectorized ROCmFPX activation loads and two-row dense matvec dispatch from
  [Lucebox PR 607](https://github.com/Luce-Org/lucebox/pull/607):
  [`dense matvec`](../patches/lucebox-rocmfpx-dense-matvec-pr607.patch);
- DeepSeek V4 reasoning metadata and `low`, `high`, and `max` effort handling:
  [`reasoning API`](../patches/lucebox-deepseek-v4-reasoning-current.patch).

The manifest verifies every patch, the combined source diff, and the compiled
server. Server, feature-gate, ROCmFPX numerical, and grouped-dispatch tests run
during the build.

## Shared host layer

Both manifests apply the same large-GTT kernel parameters, 120/120/120 W
package limits, 2.0 GHz minimum CPU frequency, cgroup memory limits, and
disabled swap. The default’s demand controller reads the kernel GPU-busy
counter once per second and does not call the inference API.

Ansible owns the GRUB drop-in, artifacts, host-policy controller, cooling
driver, systemd unit, and release record. The service is enabled at boot and
binds to `127.0.0.1:18109`.
