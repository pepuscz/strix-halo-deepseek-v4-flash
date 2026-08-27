# DeepSeek V4 Flash on Strix Halo

Reproducible Ansible deployment of two tested DeepSeek V4 Flash 0731
systems on a 128 GiB AMD Ryzen AI Max+ 395 / Radeon 8060S host.

## Systems

### Default: Strix Halo llama.cpp Vulkan IQ3_XXS

The default uses the pinned
[`Nathanw1014/strix-halo-llamacpp`](https://github.com/Nathanw1014/strix-halo-llamacpp)
v0.7.0 portable release without local source patches, an Unsloth UD-IQ3_XXS
target, a DSpark Q2_K/Q8_0 draft, q8_0 K/V, and one 524,288-token slot. Deploy
[`vulkan-iq3xxs-512k.yml`](ansible/releases/vulkan-iq3xxs-512k.yml).

### Alternative: Lucebox ROCm ROCmFPX

The leading alternative builds unmodified
[`Luce-Org/lucebox`](https://github.com/Luce-Org/lucebox) commit `2f13618` from
[PR 667](https://github.com/Luce-Org/lucebox/pull/667), with a ROCmFPX MIX
target, a DSpark Q4RMFP4 draft, q4_0 K/V, and one 131,072-token slot. Deploy
[`rocm-rocmfpx-128k.yml`](ansible/releases/rocm-rocmfpx-128k.yml); the enabled
runtime paths are listed in [ARCHITECTURE.md](docs/ARCHITECTURE.md#lucebox-runtime).

## Benchmarks

The default provides the strongest 122,879-token throughput and a 30/30 quality
result. The leading alternative provides a smaller ROCmFPX target and a
different ROCm execution path.

| System | 122,879-token input processing | Generation | Quality |
|---|---:|---:|---:|
| **Strix Halo llama.cpp Vulkan IQ3_XXS** | 226.82 tok/s | 35.73 tok/s | 30/30 |
| **Lucebox ROCm ROCmFPX** | 145.68 tok/s | 26.50 tok/s | 29/30 |

Every published retrieval point recovered all five keys byte-for-byte. The
quality difference is one MATH-style response that exhausted its 2,048-token
completion limit before producing the answer.

![Cold-retrieval input-processing and generation throughput for Strix Halo llama.cpp Vulkan IQ3_XXS on a linear prompt-length axis through 256K, with the 491,520-token measurement isolated after an explicit axis break and the Lucebox ROCm ROCmFPX 122,879-token result](docs/benchmark.svg)

See [BENCHMARKS.md](docs/BENCHMARKS.md) for the complete results, protocols,
and reproducibility data.

## Install

Prepare the controller once:

```bash
git clone https://github.com/pepuscz/strix-halo-deepseek-v4-flash.git
cd strix-halo-deepseek-v4-flash
cp ansible/inventory/hosts.example.yml ansible/inventory/hosts.yml
$EDITOR ansible/inventory/hosts.yml

python3 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements.lock
```

Select one system:

```bash
export DEEPSEEK_SYSTEM=vulkan-iq3xxs  # default
# or: export DEEPSEEK_SYSTEM=rocm-rocmfpx  # alternative
```

Run the same commands for either system:

```bash
bin/deepseekctl validate
bin/deepseekctl install --allow-reboot
bin/deepseekctl verify
```

## Host and service

Both systems require:

- BOSGAME M5 / Sixunited AXB35-02 with AMD Ryzen AI Max+ 395 and 128 GiB RAM;
- Ubuntu 26.04 LTS with kernel `7.0.0-29-generic`;
- swap and Secure Boot disabled, plus at least 120 GB free on `/`;
- the documented BIOS settings and large-GTT kernel parameters;
- 120/120/120 W package limits, `MemoryHigh=118G`, `MemoryMax=120G`, and
  fail-safe model-scoped cooling.

The default uses CPU boost off and GPU DPM auto; the alternative uses CPU
boost on and GPU DPM high. The default fan governor selects maximum cooling
while the GPU is active and firmware-auto after five idle minutes, with maximum
cooling as its failure state. Both systems install the boot-enabled
`deepseek-v4-flash.service`, bind the API to `127.0.0.1:18109`, and restore the
previous hardware policy and automatic fan control when stopped.

The default API uses the qualified DeepSeek agentic profile (`temperature=1`,
`top_p=0.95`, `top_k=0`, `min_p=0`). Clients remain free to override it per
request.

Read [HOST-PLATFORM.md](docs/HOST-PLATFORM.md) before authorizing the required
reboot. Operational procedures are in [OPERATIONS.md](docs/OPERATIONS.md), and
component provenance is in [SOURCES.md](docs/SOURCES.md).

## License

The orchestration, scripts, and documentation are MIT licensed. Models,
runtimes, libraries, drivers, and build dependencies retain their upstream
licenses and terms. See [NOTICE.md](NOTICE.md).
