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
that identity. Default parallelism is two tasks / four compiler jobs per task.

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
python3 scripts/bsp.py fetch u-boot-h432b-fastboot openh432-fastboot-ram
python3 scripts/bsp.py build u-boot-h432b-fastboot openh432-fastboot-ram
```

Use `--work /absolute/build-directory` for another build disk.
`--local-layers` reads sibling layer checkouts instead of the pinned public
commits; such runs are development runs, not release provenance.

Only checkout and fetch have network access. Build/parse/graph use Docker
network isolation and BB_NO_NETWORK. Source downloads and shared-state
cache persist in the work directory. Nothing mounts USB or deploys to hardware.
No automatic cleanup deletes failed builds.

## NAND development roles

Additional offline build targets are `u-boot-h432b-nand` (RAM54 interactive
read-only reader), `u-boot-h432b-nand-auto` (RAM55 kernel-A reader), and
`u-boot-h432b-chain` (NAND56 low-address bootstrap plus validated CE carrier).
Raw stage binaries are not factory update images. The NAND56 carrier build
does not imply that its installation or normal boot has been qualified.

The default kernel profile is read-only. `--nand-profile scratch` explicitly
permits one 128 KiB test block; `--nand-profile ubi` permits only the designated
507 MiB Linux pool. Neither permits boot-prefix or reserved-tail writes.
Profiles are development configurations, not installers. Do not run different
builds concurrently in one work directory.

Systembase is SquashFS on a static UBI volume through ubiblock, not an extra
raw partition. Each base image must fit its 199.926 MiB volume and the hard
200 MiB limit; the image recipe fails if either limit is exceeded.

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
`ram52-only/u-boot.bin` and `ram53-fastboot-only/u-boot.bin` are RAM-only and
must NEVER be flashed to NAND. The latter accepts standard fastboot RAM boot
of `openh432-ram-boot.img`; persistent flash/erase is not implemented.
The RAM image has a physical USB root debug shell, not production access
control. The XZ/CRC32-compressed image must fit the tested 16 MiB loader slot.
The kernel includes its XZ decoder; do not pair this rootfs with a gzip-only
kernel. The current RAM baseline has been boot-tested on a U2; see
[validation status](docs/status.md) for the exact scope.

No vendor blobs, CE images, firmware extracts, device dumps, private logs,
credentials or binaries are published. MIT covers new build metadata;
component licenses remain authoritative. Read the BSP boot contract.
