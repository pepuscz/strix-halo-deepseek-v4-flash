# Security

## Reporting

Open a private GitHub security advisory for vulnerabilities in this
repository. Report vulnerabilities in upstream binaries or models to their
respective publishers.

## Deployment boundary

- The API listens on loopback by default. Do not bind it publicly without
  authentication, rate limiting, and TLS.
- The host-tuning role sets `amd_iommu=off`. This is a performance choice with
  a meaningful isolation/security tradeoff.
- RyzenAdj and fan controls run as root and write hardware policy registers.
- The AXB35 fan driver is out-of-tree DKMS code. The tested profile uses
  Secure Boot disabled.
- Model and runtime downloads are untrusted until their pinned sizes and
  SHA-256 hashes pass.
- Inventory, SSH keys, vault passwords, Wi-Fi credentials, hostnames, private
  IPs, and raw journals must never be committed.
