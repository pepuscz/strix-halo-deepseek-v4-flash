# Third-party notices

This repository contains original orchestration, patches, tests, and
documentation. It does not contain model weights. The v1.2.0 release asset
contains one rebuilt Vulkan backend library plus its source license and build
manifest; the remaining runtime is downloaded from its publisher.

- `Nathanw1014/strix-halo-llamacpp`: the upstream portable runtime is downloaded
  from its GitHub release. The patched backend is rebuilt from its llama.cpp
  source tree, whose included license is MIT.
- Lucebox: Apache-2.0. The public patch files modify the pinned Lucebox source
  during a local build.
- llama.cpp and linked components retain the licenses shipped by their
  upstream distributions.
- Unsloth DeepSeek V4 Flash GGUF: MIT according to its model card.
- The DSpark and ROCmFPX model artifacts retain their model-card terms.
- rocWMMA: MIT.
- RyzenAdj: LGPL-3.0.
- `ec-su_axb35-linux`: GPL-2.0.
- Ubuntu, ROCm, Ansible, and build packages retain their respective licenses.

Exact links and revisions are in `docs/SOURCES.md` and the two release
manifests. The absence of a component from this notice does not alter its
license.
