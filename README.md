# DeepSeek V4 Flash on Strix Halo

Reproducible Ansible deployment of our selected DeepSeek V4 Flash 0731
configuration for a 128 GB Ryzen AI Max+ 395 / Radeon 8060S system.

The release is optimized for real 128K work, not only a server that happens to
allocate a 128K KV cache. On the BOSGAME M5 it completed byte-exact retrieval
at 122,879 input tokens with 128.70 input tok/s and 19.41 output tok/s.

## Selected release

| Layer | Pinned value |
|---|---|
| Server | Nathanw1014 `strix-halo-llamacpp` `dev-20260817-c569020` |
| Target | Unsloth DeepSeek-V4-Flash-0731 `UD-IQ3_XXS`, four GGUF shards |
| Draft | Alessandro Bologna dflash DSpark `Q2_K/Q8_0` |
| Backend | Portable Mesa RADV/Vulkan bundle; host ROCm is not used |
| Context | 131,072 allocation, one slot, q8_0 K/V |
| Speculation | DSpark, maximum draft 64; target verifies emitted tokens |
| Host policy | CPU performance governor, 2.0 GHz minimum, boost off; GPU DPM auto |
| Package power | 120/120/120 W STAPM/fast/slow |
| Memory guard | `MemoryHigh=118G`, `MemoryMax=120G`, no swap, >=4 GiB effective non-CMA headroom |
| Cooling | maximum fans while the model loads/runs; firmware-auto otherwise |

All artifacts are downloaded from their original publishers into immutable,
release-specific paths and accepted only after size and SHA-256 verification.
This repository does not redistribute models, the Nathan runtime, firmware,
Ubuntu packages, or third-party source archives.

## Requirements

- AMD Strix Halo with 128 GiB RAM; the tested machine is a BOSGAME M5 on the
  Sixunited AXB35-02 board.
- Ubuntu 26.04 LTS and kernel `7.0.0-29-generic` for the strict tested profile.
- SSH, Python 3, sudo, Internet access, and roughly 120 GB free disk space.
- Secure Boot disabled for the tested AXB35 DKMS path.
- An Ansible controller with Python 3.12 or newer.

The large-GTT boot parameters disable the IOMMU and require a reboot. Read
[the host boundary](docs/HOST-PLATFORM.md) before running the installer.

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

`install` is idempotent and is also the update path. Change only the pinned
release manifest, review its diff, then rerun the same command. Reverting to a
previous Git tag and rerunning `install` is the rollback path; release-specific
artifacts are not overwritten.

Operational commands:

```bash
bin/deepseekctl status
bin/deepseekctl stop      # fans return to firmware-auto
bin/deepseekctl start
bin/deepseekctl verify
```

The API binds to `127.0.0.1:18109` by default. Expose it only through an
authenticated reverse proxy or SSH tunnel.

## Benchmark result

The closest qualified Lucebox competitor remains faster for the short
2,048-in/510-out control, while Nathan wins decisively at real 128K depth:

| Frozen workload | Nathan selected | Lucebox best | Nathan delta |
|---|---:|---:|---:|
| Short decode, 2,048/510 | 26.67 tok/s | 28.20 tok/s | -5.4% |
| Real-128K prefill, 122,879 in | 128.70 tok/s | 11.34 tok/s | 11.35x |
| Real-128K decode | 19.41 tok/s | 10.40 tok/s | +86.6% |

These are winner-vs-winner software configurations, not identical power
policies: Nathan uses its selected 120 W efficiency policy and Lucebox uses its
qualified 100 W policy. A separate Nathan 100 W same-room control still
measured 125.45/18.92 tok/s at real 128K, so the long-context conclusion is not
created by the extra 20 W. See [BENCHMARKS.md](docs/BENCHMARKS.md) for quality,
methodology, raw aggregate data, and limitations.

## Maintenance policy

The Ansible tree in this repository is the canonical source for production.
No manual edit under `/etc/systemd/system`, `/usr/local/sbin`, `/opt/m5`, or
the GRUB drop-in is supported. Updates arrive as reviewed release-manifest and
role changes, with CI syntax/lint checks and an immutable Git tag.

See [OPERATIONS.md](docs/OPERATIONS.md), [ARCHITECTURE.md](docs/ARCHITECTURE.md),
[SOURCES.md](docs/SOURCES.md), and [SECURITY.md](SECURITY.md).

## License

Our Ansible, scripts, and documentation are MIT licensed. Upstream components
retain their own licenses and terms. In particular, the Nathan toolbox had no
machine-detected repository license when this release was frozen, so the
playbook downloads its binary directly from the author's GitHub release and
does not redistribute it. See [NOTICE.md](NOTICE.md).
