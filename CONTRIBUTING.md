# Contributing

Production changes must be deterministic and reviewable:

1. Add a new immutable release manifest; never silently edit a published tag.
2. Pin every source revision and downloaded artifact hash.
3. Preserve the 4 GiB effective non-CMA floor and systemd memory limits.
4. Run `bin/deepseekctl lint` and the read-only `verify` playbook.
5. Publish benchmark changes with workload identity, power/clock policy,
   temperatures, memory headroom, and quality results.
6. Do not add personal data, credentials, raw host logs, model output containing
   private prompts, or model/runtime binaries.

Performance claims need an unchanged control on the same host. A faster run
that changes quality, prompt, output budget, context depth, power, or cooling
must say so explicitly.
