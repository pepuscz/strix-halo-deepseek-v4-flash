# Architecture

The release has five independently pinned layers.

1. **DeepSeek V4 Flash 0731 target** — the full Unsloth `UD-IQ3_XXS` GGUF,
   split into four shards. This is the model that verifies and emits the final
   tokens.
2. **DSpark draft** — Alessandro Bologna's smaller Q2_K/Q8_0 dflash model. It
   proposes token blocks; the target model verifies them, so speculation changes
   speed rather than silently accepting draft-only output.
3. **Nathan's llama.cpp fork** — the `c569020` Vulkan build adds the Strix Halo
   kernels and DSpark integration used by the winning run.
4. **Vulkan userspace** — Nathan's portable release provides Mesa RADV and its
   libraries. The exact Ubuntu Vulkan loader used by the benchmark is extracted
   into the release directory. Host ROCm is not used or modified.
5. **Host envelope** — large GTT boot parameters, 120 W RyzenAdj limits,
   boost-off CPU policy, GPU DPM auto, cgroup memory limits, and model-scoped
   AXB35 maximum cooling.

The API binds only to `127.0.0.1:18109`. One server slot owns a 131,072-token
allocation. Short requests use only their actual prompt length and therefore
remain much faster than a filled 128K request; the allocation is capacity, not
mandatory padding.

Artifacts live under a release ID in `/opt/m5`. Updating the manifest creates a
new immutable release directory instead of overwriting the running release.
Systemd owns start/stop, cgroup limits, policy application/restoration, and the
fan dependency. Ansible owns all persistent configuration.
