# DeepSeek V4 Flash on Strix Halo

Reproducible Ansible deployment of two qualified DeepSeek V4 Flash 0731
systems on a 128 GiB AMD Ryzen AI Max+ 395 / Radeon 8060S host.

## Systems

### Default: Strix Halo llama.cpp Vulkan IQ3_XXS

The default system uses the unmodified `strix-halo-llamacpp` v0.6.4 portable
release, an Unsloth UD-IQ3_XXS target, and a DSpark Q2_K/Q8_0 draft. Deploy it
with [`vulkan-iq3xxs-128k.yml`](ansible/releases/vulkan-iq3xxs-128k.yml).

### Alternative: Lucebox ROCm ROCmFPX

The alternative system builds Lucebox commit `90f85fa` with 11 published
patches, a ROCmFPX MIX target, and a DSpark Q4RMFP4 draft. The patches add the
ROCm 7.1 build fix, DeepSeek tool and reasoning support, fused-verification
attention paths, and bounded-memory 128K prefill/cache behavior. Deploy it with
[`rocm-rocmfpx-128k.yml`](ansible/releases/rocm-rocmfpx-128k.yml); the exact
changes are listed in [ARCHITECTURE.md](docs/ARCHITECTURE.md#lucebox-source-modifications).

The Strix Halo llama.cpp system is the benchmark-selected default because it
has faster decode and cached tool-conversation latency. The Lucebox system is
the alternative when the higher observed Quality-30 score is preferred.

## Benchmark summary

| System | Short decode | 128K prefill | 128K decode | Retrieval | Quality-30 |
|---|---:|---:|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 35.01 tok/s | 130.63 tok/s | 22.43 tok/s | 5/5 | 26–27/30 |
| **Lucebox ROCm ROCmFPX** | 29.10 tok/s | 131.19 tok/s | 16.40 tok/s | 5/5 | 30/30 |

See [BENCHMARKS.md](docs/BENCHMARKS.md) for the workload definitions,
measurement rules, and reproducibility data.

## Install the default system

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

## Install the alternative system

```bash
DEEPSEEK_SYSTEM=rocm-rocmfpx bin/deepseekctl validate
DEEPSEEK_SYSTEM=rocm-rocmfpx bin/deepseekctl install --allow-reboot
DEEPSEEK_SYSTEM=rocm-rocmfpx bin/deepseekctl verify
```

## Common host and service behavior

Both manifests require:

- BOSGAME M5 / Sixunited AXB35-02 with AMD Ryzen AI Max+ 395 and 128 GiB RAM;
- Ubuntu 26.04 LTS with kernel `7.0.0-29-generic`;
- swap and Secure Boot disabled, plus at least 120 GB free on `/`;
- large-GTT kernel parameters and IOMMU disabled;
- 120/120/120 W package limits, `MemoryHigh=118G`, `MemoryMax=120G`, and
  maximum model-scoped fan cooling.

The default uses CPU boost off and GPU DPM auto; the alternative uses CPU
boost on and GPU DPM high. Both install the boot-enabled
`deepseek-v4-flash.service`, bind the API to `127.0.0.1:18109`, and restore the
previous hardware policy and firmware-auto fan control when stopped.

Read [HOST-PLATFORM.md](docs/HOST-PLATFORM.md) before authorizing the required
reboot. Operational procedures are in [OPERATIONS.md](docs/OPERATIONS.md), and
component provenance is in [SOURCES.md](docs/SOURCES.md).

## License

The orchestration, scripts, and documentation are MIT licensed. Models,
runtimes, libraries, drivers, and build dependencies retain their upstream
licenses and terms. See [NOTICE.md](NOTICE.md).
