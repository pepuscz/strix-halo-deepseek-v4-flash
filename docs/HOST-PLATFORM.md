# Host platform boundary

The frozen profile is intentionally strict: Ubuntu 26.04, kernel
`7.0.0-29-generic`, AMD GPU PCI ID `1002:1586`, AXB35-02 board, at least 125,000,000
KiB RAM, no swap, Secure Boot disabled, and at least 120 GB free on `/`.

Set these BIOS options before installation:

| Setting | Qualified value |
|---|---|
| BIOS version | `3.10` |
| UMA framebuffer | 1 GB |
| Above 4G decoding | enabled |
| ReBAR | enabled |
| Secure Boot | disabled |
| IOMMU | disabled |
| SVM | disabled |
| Core Performance Boost | enabled |
| CPPC | auto |

These settings must be configured manually. Ansible verifies Secure Boot but
does not change BIOS options.

The installer manages this GRUB command line:

```text
amd_pstate=active amd_iommu=off amdgpu.gttsize=126976 ttm.pages_limit=32505856 ttm.page_pool_size=32505856
```
