# Suggested upstream feedback

No message is sent automatically. After the public release URL is stable, the
most useful notification order is:

1. Open a concise result/reproduction issue on
   [Nathanw1014/strix-halo-llamacpp](https://github.com/Nathanw1014/strix-halo-llamacpp/issues).
   Lead with the 122,879-token 5/5 result, exact hashes, 120 W policy, and the
   bounded 512-token verbosity regression. This gives the runtime author both a
   success case and an actionable quality/API observation.
2. Add a follow-up comment to the
   [original LocalLLaMA thread](https://www.reddit.com/r/LocalLLaMA/comments/1vlmh0b/deepseek_v4_flash_0731_at_27_ts_decode_on_strix/),
   linking this repository and explaining which conditions match and differ.
3. Share quantization-specific observations in the
   [Unsloth model repository's Community tab](https://huggingface.co/unsloth/DeepSeek-V4-Flash-0731-GGUF/discussions).
4. Share DSpark acceptance and the frozen draft hash in the
   [draft model's Community tab](https://huggingface.co/alessandrobologna/DeepSeek-V4-Flash-DSpark-Drafter-GGUF/discussions).
5. Send the exact-attention 128K comparison to the Lucebox maintainers through
   their repository issue/discussion channel, framed as benchmark data rather
   than a cross-backend ranking claim.

Avoid opening an upstream llama.cpp performance issue until the result is
reproduced against an upstream-supported build or tied to a specific upstream
Vulkan change. Nathan's fork is the right first technical destination.
