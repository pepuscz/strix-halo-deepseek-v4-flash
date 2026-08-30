# Sources and provenance

## Strix Halo llama.cpp Vulkan IQ3_XXS

| Component | Pinned source |
|---|---|
| Runtime | [`Nathanw1014/strix-halo-llamacpp`](https://github.com/Nathanw1014/strix-halo-llamacpp), official release `v0.7.0`, commit `95c828eeb315a7ba6f50fcf632c29f8de2ec1a6e` |
| Target | [`unsloth/DeepSeek-V4-Flash-0731-GGUF`](https://huggingface.co/unsloth/DeepSeek-V4-Flash-0731-GGUF), revision `fbbb5b93fb787c21338159b0af3318bb3f4d9768`, UD-IQ3_XXS |
| Draft | [`alessandrobologna/DeepSeek-V4-Flash-DSpark-Drafter-GGUF`](https://huggingface.co/alessandrobologna/DeepSeek-V4-Flash-DSpark-Drafter-GGUF), revision `824190cb58c1469a603d9686107dd85ef11a5d51` |
| Vulkan loader | Ubuntu `libvulkan1` `1.4.341.0-1`, extracted inside the immutable release |

The exact upstream runtime archive, manifest, launcher, executable, Vulkan
backend, loader, and model identities are in
[`vulkan-iq3xxs-512k.yml`](../ansible/releases/vulkan-iq3xxs-512k.yml).

## Lucebox ROCm ROCmFPX

| Component | Pinned source |
|---|---|
| Runtime | [`Luce-Org/lucebox`](https://github.com/Luce-Org/lucebox), unmodified commit `5eb4fbe95e13944ad964bd7e42980bca518e3d5c` from [PR 667](https://github.com/Luce-Org/lucebox/pull/667) |
| Block-Sparse-Attention submodule | commit `49d6c39e4dc0303442cda3bb758b3925d4399c49` |
| rocWMMA headers | [`ROCm/rocWMMA`](https://github.com/ROCm/rocWMMA), tag `rocm-7.1.1`, commit `1ab208f49945c38626b79e3f0c284d65ac44a781` |
| Target | [`Lucebox/DeepSeek-V4-Flash-0731-ROCmFP3`](https://huggingface.co/Lucebox/DeepSeek-V4-Flash-0731-ROCmFP3), revision `39745d3f6f4b92ff1d764ada79a73616bc8903a5`, ROCmFPX MIX |
| Draft | [`Lucebox/DeepSeek-V4-Flash-0731-DSpark-GGUF`](https://huggingface.co/Lucebox/DeepSeek-V4-Flash-0731-DSpark-GGUF), revision `8e8bbf5bdb384b6e867d01ad3215be70b1d920c5` |

The enabled execution paths are listed in
[ARCHITECTURE.md](ARCHITECTURE.md#lucebox-runtime). The clean source-tree
identity, pinned Ubuntu ROCm package versions, absolute build paths, compiler
flags, output binary identity, and model identities are in
[`rocm-rocmfpx-128k.yml`](../ansible/releases/rocm-rocmfpx-128k.yml).

## Shared host components

| Component | Pinned source |
|---|---|
| RyzenAdj | [`FlyGoat/RyzenAdj`](https://github.com/FlyGoat/RyzenAdj), commit `5775fc3e6dbb25c7030ee2d100a1bdd6e8bf2d0a` |
| AXB35 driver | [`cmetz/ec-su_axb35-linux`](https://github.com/cmetz/ec-su_axb35-linux), commit `7a9f372edcaa99e562dece70204c4f609692a778` |

This repository downloads models and upstream runtime archives directly from
their publishers. The default Vulkan system has no repository-owned binary
overlay.
