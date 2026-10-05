# OpenH432 build manifests

Reproducible-build infrastructure for Fractal Microsystems' experimental
H432B/BrailleSense U2 BSP. This is a source-only developer preview, not a
firmware release or installer.

Repositories:

- [meta-fractalmicro-H432B](https://github.com/highenergymagic/meta-fractalmicro-H432B):
  machine, kernel, bootloader and hardware patches.
- [meta-fractalmicro-openh432](https://github.com/highenergymagic/meta-fractalmicro-openh432):
  distro, systemd and RAM-image policy.
- This repository: pinned kas manifest, container and validation.

## Build

Linux amd64, Docker, Python 3 and Git are required. No host target compiler.
The container uses UID/GID 1000:1000; its work directory must be writable by
that identity. Default parallelism is two tasks / two compiler jobs.

```sh
git clone https://github.com/highenergymagic/openh432-build.git
cd openh432-build
python3 scripts/bsp.py image
python3 scripts/bsp.py checkout
python3 scripts/bsp.py parse
python3 scripts/bsp.py fetch u-boot-h432b u-boot-h432b-ram linux-h432b
python3 scripts/bsp.py build u-boot-h432b u-boot-h432b-ram linux-h432b
python3 scripts/bsp.py fetch openh432-ram-dev
python3 scripts/bsp.py build openh432-ram-dev
```

Use `--work /absolute/build-directory` for another build disk.
`--local-layers` reads sibling layer checkouts instead of the pinned public
commits; such runs are development runs, not release provenance.

Only checkout and fetch have network access. Build/parse/graph use Docker
network isolation and BB_NO_NETWORK. Source downloads and shared-state
cache persist in the work directory. Nothing mounts USB or deploys to hardware.
No automatic cleanup deletes failed builds.

## Pins and compiler policy

Yocto 6.0.3 Wrynose: separate OE-Core and BitBake commits, not the retired
combined Poky checkout. kas 5.5 builder base is pinned by OCI digest.
The derived container checks the official Arm GNU 14.3.rel1 archive SHA-256.

- Kernel/U-Boot: official Arm GNU 14.3.rel1.
- Userland: OE-Core's pinned GNU compiler and glibc/sysroot.
- Fixed builder identity, host name and SOURCE_DATE_EPOCH.
- Metadata builds do not prove bit reproducibility or device qualification.
  See docs/status.md for what has actually been tested.

Plan approximately 150-200 GB for a useful development cache; minimal builds
can be smaller. Disk monitoring stops new tasks at 10 GB free and halts at
5 GB. Keep the known-good Buildroot images during migration.

## Safety and publication

Raw `nand51-raw/u-boot.bin` is NOT a CE update carrier.
`ram52-only/u-boot.bin` is RAM-only and must NEVER be flashed to NAND.
The RAM image has a physical USB root debug shell, not production access
control. The compressed image must fit the tested 16 MiB loader slot.

No vendor blobs, CE images, firmware extracts, device dumps, private logs,
credentials or binaries are published. MIT covers new build metadata;
component licenses remain authoritative. Read the BSP boot contract.
