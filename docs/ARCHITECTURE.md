# Architecture

## System definitions

| Layer | Strix Halo llama.cpp Vulkan IQ3_XXS | Lucebox ROCm ROCmFPX |
|---|---|---|
| Runtime | Official `strix-halo-llamacpp` v0.7.0 portable release, commit `95c828eeb315a7ba6f50fcf632c29f8de2ec1a6e`, without local source patches | Unmodified Lucebox commit `5eb4fbe95e13944ad964bd7e42980bca518e3d5c` from [PR 667](https://github.com/Luce-Org/lucebox/pull/667) |
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

## Runtime status

The Strix Halo system uses the official v0.7.0 archive as published: launcher,
server, Vulkan backend, bundled RADV driver, and runtime libraries are pinned by
SHA-256. No local Vulkan overlay or Lightning Indexer routing override is
applied. The release keeps the qualified upstream tuning environment, including
`GGML_VK_MMID_M128=1`.

### Lucebox runtime

The pinned clean source includes gfx1151 split-KV indexed MLA, Q4 MMVF
projection, ROCmFP2/3 Wave32 kernels, four-row ROCmFP2 activation reuse, sparse
verifier attention, incremental speculative-verification masks, and exact
block-radix top-k selection. Fixed speculative width Q=4 is the default;
adaptive width is opt-in. Server, feature-gate, DeepSeek 4, ROCmFPX numerical,
grouped-dispatch, and top-k tests run during the build.

## Shared host layer

Both manifests apply the same large-GTT kernel parameters, 120/120/120 W
package limits, 2.0 GHz minimum CPU frequency, cgroup memory limits, and
disabled swap. The default’s demand controller reads the kernel GPU-busy
counter once per second and does not call the inference API.

Ansible owns the GRUB drop-in, artifacts, host-policy controller, cooling
driver, systemd unit, and release record. The service is enabled at boot and
binds to `127.0.0.1:18109`.
