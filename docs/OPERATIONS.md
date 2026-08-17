# Operations and maintenance

## Source of truth

Persistent production changes are made only through this repository. Do not
edit the systemd unit, GRUB drop-in, host-policy scripts, DKMS metadata, or files
under the active `/opt/m5/releases/<release-id>` by hand.

For an update:

1. add a new release manifest or review a manifest change;
2. update every URL, revision, byte size, and SHA-256 together;
3. run `bin/deepseekctl lint` and `bin/deepseekctl validate`;
4. run `bin/deepseekctl update --allow-reboot`;
5. run `bin/deepseekctl verify` and record the benchmark delta;
6. tag the repository only after all gates pass.

Rollback is the same deterministic path: check out the previous release tag and
run `install`. Release-specific artifacts are immutable and retained. Ansible
stops/disables the explicitly conflicting legacy unit before enabling the
selected unit.

## Day-to-day controls

```bash
bin/deepseekctl status
bin/deepseekctl stop
bin/deepseekctl start
bin/deepseekctl verify
```

Stopping the model releases the `StopWhenUnneeded` cooling dependency; the
three fans are verified back in firmware-auto mode. The host policy controller
also restores the CPU, GPU, and package-power values captured before model
startup.

`verify` checks API/build/context identity, runtime hashes, cgroup limits and
events, memory PSI, effective non-CMA headroom, temperatures, all three fan
states, live RyzenAdj readback, and kernel errors from the service interval.
Set `deepseek_verify_full_model_hashes=true` for an explicit 111 GB integrity
scrub; normal runs use authenticated `.verified` identity markers and byte-size
checks to avoid rehashing the models on every maintenance pass.

The installer can adopt already-downloaded artifacts through uncommitted
inventory variables. Each seed is fully size/hash verified before it is linked
or reflink-copied. Never commit machine-local seed paths.
