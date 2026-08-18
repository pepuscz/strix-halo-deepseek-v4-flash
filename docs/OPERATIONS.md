# Operations

## Select a system

Select Strix Halo llama.cpp Vulkan IQ3_XXS:

```bash
export DEEPSEEK_SYSTEM=vulkan-iq3xxs
```

Or select Lucebox ROCm ROCmFPX:

```bash
export DEEPSEEK_SYSTEM=rocm-rocmfpx
```

Then use the same commands for either system:

```bash
bin/deepseekctl validate
bin/deepseekctl install --allow-reboot
bin/deepseekctl verify
```

Keep the same `DEEPSEEK_SYSTEM` value for later start, stop, status, and verify
commands. If unset, it defaults to `vulkan-iq3xxs`. Switching systems runs the
selected immutable manifest and replaces the shared
`deepseek-v4-flash.service` definition; it does not overwrite the other
system's release directory.

## Service controls

```bash
bin/deepseekctl status
bin/deepseekctl stop
bin/deepseekctl start
bin/deepseekctl verify
```

Stop restores the captured CPU, GPU, and package-power policy. The cooling
dependency returns all three AXB35 fans to firmware-auto. Verify checks API and
runtime identity, context allocation, model representation, cgroup events,
memory headroom, memory PSI, temperatures, cooling state, package-power
readback, kernel errors, and a bounded API request.

Set `deepseek_verify_full_model_hashes=true` for an explicit full model scrub.
Normal operation verifies immutable download markers and byte sizes to avoid
rehashing approximately 109–111 GB on each run.

## Updates and rollback

Persistent production changes are made through release manifests and roles.
Do not edit the active systemd unit, GRUB drop-in, hardware policy, DKMS files,
or immutable `/opt/m5/releases/<release-id>` content manually.

An update requires a new or reviewed immutable manifest, successful lint and
validation, installation, live verification, and benchmark evidence. Rollback
uses the same path: check out a prior repository tag and install its manifest.
Retained release-specific artifacts are reused only after identity checks.
