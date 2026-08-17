# Sources and provenance

| Component | Frozen source | Role / licensing note |
|---|---|---|
| Nathan runtime | [Nathanw1014/strix-halo-llamacpp](https://github.com/Nathanw1014/strix-halo-llamacpp), release `dev-20260817-c569020`, commit `c56902063081d1a20e05171f2428686a6166b9fb` | Strix Halo Vulkan server and DSpark path. No machine-detected repository license at freeze time; downloaded directly, not redistributed. |
| Target GGUF | [unsloth/DeepSeek-V4-Flash-0731-GGUF](https://huggingface.co/unsloth/DeepSeek-V4-Flash-0731-GGUF), revision `fbbb5b93fb787c21338159b0af3318bb3f4d9768` | Four-shard `UD-IQ3_XXS` target; model card reports MIT. |
| Draft GGUF | [alessandrobologna/DeepSeek-V4-Flash-DSpark-Drafter-GGUF](https://huggingface.co/alessandrobologna/DeepSeek-V4-Flash-DSpark-Drafter-GGUF), revision `824190cb58c1469a603d9686107dd85ef11a5d51` | Q2_K/Q8_0 speculative draft. |
| RyzenAdj | [FlyGoat/RyzenAdj](https://github.com/FlyGoat/RyzenAdj), commit `5775fc3e6dbb25c7030ee2d100a1bdd6e8bf2d0a` | Applies and reads package power limits; LGPL-3.0. |
| AXB35 driver | [cmetz/ec-su_axb35-linux](https://github.com/cmetz/ec-su_axb35-linux), commit `7a9f372edcaa99e562dece70204c4f609692a778` | Exposes all three BOSGAME/Sixunited fans; GPL-2.0. |
| Vulkan loader | Ubuntu `libvulkan1` 1.4.341.0-1 | Exact benchmark loader, extracted under the immutable release rather than replacing system libraries. |
| Inspiration/control | [LocalLLaMA Strix Halo report](https://www.reddit.com/r/LocalLLaMA/comments/1vlmh0b/deepseek_v4_flash_0731_at_27_ts_decode_on_strix/) | Starting configuration and external performance reference; our measurements are independent. |

Every downloadable artifact's URL, revision, byte size, and SHA-256 is in
[`ansible/releases/nathan-c569020-128k-120w.yml`](../ansible/releases/nathan-c569020-128k-120w.yml).
