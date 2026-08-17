# Host platform boundary

The frozen profile is intentionally strict: Ubuntu 26.04, kernel
`7.0.0-29-generic`, AMD GPU PCI ID `1002:1586`, AXB35-02 board, at least 125,000,000
KiB RAM, no swap, Secure Boot disabled, and at least 120 GB free on `/`.

The installer manages this GRUB command line:

```text
amd_pstate=active amd_iommu=off amdgpu.gttsize=126976 ttm.pages_limit=32505856 ttm.page_pool_size=32505856
```

These parameters reserve a very large GPU translation-table capacity and
disable the IOMMU. Both choices alter the host security/performance boundary.
Do not apply them to a general-purpose or untrusted multi-tenant machine without
understanding the consequences.

`bin/deepseekctl validate` is non-mutating. `install --allow-reboot` writes the
managed GRUB drop-in, regenerates GRUB, and reboots only when the live kernel is
missing a required argument. After reboot it rechecks every value before any
model artifact or service is changed.

The optional AXB35 cooling role is enabled by this BOSGAME release. It builds an
exact upstream commit through DKMS. Secure Boot must be disabled because this
public project does not enroll or distribute a module-signing key.
