# DeepSeek V4 Flash on Strix Halo

Reproducible Ansible deployment of two qualified DeepSeek V4 Flash 0731
systems for a 128 GiB AMD Ryzen AI Max+ 395 / Radeon 8060S host. Both allocate
131,072 tokens, pass byte-exact retrieval at 122,879 input tokens, expose an
OpenAI-compatible loopback API, and run inside the same power, memory, cooling,
and kernel safety envelope.

**Vulkan IQ3_XXS** is the Vulkan deployment using `strix-halo-llamacpp`, an
Unsloth UD-IQ3_XXS target, and a DSpark Q2_K/Q8_0 draft; **ROCm ROCmFPX** is the
ROCm deployment using Lucebox, a ROCmFPX MIX target, and a DSpark Q4RMFP4 draft.

## Qualified systems

| System | Runtime and model representation | 128K prefill | 128K decode | Quality gate |
|---|---|---:|---:|---:|
| **Vulkan IQ3_XXS** (default) | `strix-halo-llamacpp` v0.6.4; Unsloth UD-IQ3_XXS; DSpark Q2_K/Q8_0 | 130.63 tok/s | 22.43 tok/s | 26–27/30 |
| **ROCm ROCmFPX** | Lucebox `90f85fa` plus the published qualified patch chain; ROCmFPX target; Q4RMFP4 DSpark | 131.19 tok/s | 16.40 tok/s | 30/30 |

Vulkan IQ3_XXS is the default because it provides higher decode throughput and
lower wall time for a growing cached tool conversation. ROCm ROCmFPX provides
the higher observed score on the fixed 30-task quality gate. The complete
matched comparison is in [BENCHMARKS.md](docs/BENCHMARKS.md).

## Tested host boundary

- BOSGAME M5 / Sixunited AXB35-02
- AMD Ryzen AI Max+ 395 with Radeon 8060S (`1002:1586`)
- 128 GiB RAM, swap disabled
- Ubuntu 26.04 LTS, kernel `7.0.0-29-generic`
- Secure Boot disabled for the AXB35 DKMS cooling driver
- at least 120 GB free on `/`

The installer applies large-GTT kernel parameters and disables the IOMMU. Read
[HOST-PLATFORM.md](docs/HOST-PLATFORM.md) before authorizing the required
reboot.

## Install

```bash
git clone https://github.com/pepuscz/strix-halo-deepseek-v4-flash.git
cd strix-halo-deepseek-v4-flash
cp ansible/inventory/hosts.example.yml ansible/inventory/hosts.yml
$EDITOR ansible/inventory/hosts.yml

python3 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements.lock
bin/deepseekctl validate
bin/deepseekctl install --allow-reboot
bin/deepseekctl verify
```

This installs Vulkan IQ3_XXS. Select ROCm ROCmFPX explicitly:

```bash
DEEPSEEK_SYSTEM=rocm-rocmfpx bin/deepseekctl validate
DEEPSEEK_SYSTEM=rocm-rocmfpx bin/deepseekctl install --allow-reboot
DEEPSEEK_SYSTEM=rocm-rocmfpx bin/deepseekctl verify
```

The corresponding manifest identifiers are `vulkan-iq3xxs` and
`rocm-rocmfpx`. `DEEPSEEK_RELEASE=/absolute/path/to/manifest.yml` remains
available for development and immutable release validation.

## Deployment properties

- Publisher URLs, source revisions, byte sizes, SHA-256 values, runtime build
  inputs, and host settings are pinned in the two release manifests.
- Models are downloaded from their publishers into release-specific paths.
- Vulkan IQ3_XXS uses the publisher's verified portable binary archive.
- ROCm ROCmFPX is built locally from a pinned source commit, pinned ROCm 7.1
  packages, pinned rocWMMA headers, and hash-verified patches. The resulting
  server must match the qualified SHA-256 before activation.
- systemd applies the system-specific CPU/GPU policy, 120 W package limits,
  `MemoryHigh=118G`, `MemoryMax=120G`, no swap, and maximum model-scoped fan
  cooling. Stop restores the prior hardware policy and firmware-auto cooling.
- The API binds to `127.0.0.1:18109`. External access requires an authenticated
  reverse proxy or SSH tunnel.

Operational and maintenance procedures are in
[OPERATIONS.md](docs/OPERATIONS.md). Exact component provenance is in
[SOURCES.md](docs/SOURCES.md).

## License

The orchestration, scripts, and documentation are MIT licensed. Models,
runtimes, libraries, drivers, and build dependencies retain their upstream
licenses and terms. See [NOTICE.md](NOTICE.md).
