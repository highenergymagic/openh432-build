# BSP architecture

OpenH432 targets the H432B BrailleSense U2: Samsung S5PV210, 256 MiB
DRAM, raw NAND and separate internal SD storage. It retains the factory
first-stage loader and EBOOT. Other Sense models are not qualified.

## Repository responsibilities

| Repository | Responsibility |
| --- | --- |
| meta-fractalmicro-H432B | Machine configuration, kernel, device tree, bootloader and hardware constraints |
| meta-fractalmicro-openh432 | Distribution, packages, systemd policy and image composition |
| meta-fractalmicro-assets | Checksum-pinned third-party sound assets and conversion |
| openh432-build | Immutable layer manifest, container and build orchestration |
| openh432-tools | Host transport, backup verification and deployment procedures |

The [kas manifest](../kas/h432b.yml) is the composition lock. Local-layer
overrides are recorded development inputs, not the pinned release composition.
Upstream kernel and bootloader sources are fetched by recipes and modified
by ordered patches; they are not duplicated as full source forks here.

## Boot and storage

The persistent CE-format carrier contains a low-address U-Boot bootstrap
and a high-RAM maintenance stage. The maintenance stage reads fixed slot B
from the Linux UBI pool, or enters USB maintenance on a boot failure or
recognized one-shot request.

The normal kernel bundle contains Linux, a device tree and a minimal
root-handoff initramfs. Early userspace attaches the existing UBI pool,
validates the slot marker and mounts the separate static SquashFS
`systembase_b` volume through ubiblock. It then starts systemd with a
64 MiB volatile writable overlay. It does not format or provision storage.

The standalone `openh432-fastboot-ram` bundle uses the same runtime kernel
with a complete RAM root. It can run before a NAND systembase is provisioned.
It permits Linux-pool and internal-SD writes and is not a forensic capture
environment.

See the [boot contract](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/boot-contract.md)
and [NAND layout](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/nand.md)
for exact artifact roles, addresses and capacity limits.

## Update and security boundaries

Kernel and systembase A/B volumes reserve storage capacity; they do not
implement coordinated activation or rollback. The loader selects slot B.
Persistent userdata, SD extensions and an update transaction framework are
not implemented. No automatic repartitioning runs at boot.

Development images expose a privileged physical USB console. Maintenance
SSH is key-gated, with volatile host identity. Neither interface constitutes
a production security policy. The factory prefix and NAND tail remain
protected from Linux-pool writes.

## Build and validation

Native Linux x86-64 and ARM64 Docker builders use the pinned OE toolchain.
See [build hosts](build-hosts.md) for setup and artifact comparison.

Source tests, metadata resolution, compilation, reproducibility comparisons
and device qualification are separate checks. The [support matrix](status.md)
states deployment scope; the [cross-host record](cross-host-validation.md)
identifies the exact artifacts for which byte-for-byte equivalence was measured.
