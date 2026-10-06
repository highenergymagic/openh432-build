# OpenH432

A Linux-based operating system in development for the HIMS BrailleSense U2,
built by Fractal Microsystems to extend the useful life of existing braille
notetakers.

This repository is the entry point for building OpenH432. It brings together
the hardware and operating-system layers with pinned source revisions and
a containerized Yocto/OpenEmbedded build environment.

**OpenH432 is a developer preview, not a finished accessible firmware
replacement.** Linux boots from NAND, but essential accessibility and
power-management features remain incomplete. There is no general-purpose
installer.

## Repositories

- [meta-fractalmicro-H432B](https://github.com/highenergymagic/meta-fractalmicro-H432B):
  board support, kernel, device tree and bootloader.
- [meta-fractalmicro-openh432](https://github.com/highenergymagic/meta-fractalmicro-openh432):
  distribution policy, systemd configuration and operating-system images.
- **openh432-build** (this repository): source locks, build container,
  orchestration and validation.

The hardware target is `h432b`; the distribution is `openh432`.

## Building

### Requirements

- A Linux x86-64 host with Docker, Python 3 and Git.
- Access to the Docker daemon, directly or through `doas`/`sudo`.
- Approximately 150–200 GB of disk space for a useful development build cache.
- A build directory writable by UID/GID `1000:1000`, the container's builder identity.

No host cross-compiler is required. The launcher builds and runs the pinned
container; compilation happens inside it.

### Build a development image

```sh
git clone https://github.com/highenergymagic/openh432-build.git
cd openh432-build

python3 scripts/bsp.py image
python3 scripts/bsp.py checkout
python3 scripts/bsp.py parse
python3 scripts/bsp.py fetch openh432-ram-dev
python3 scripts/bsp.py build openh432-ram-dev
```

Artifacts are placed in `work/build/tmp/deploy/images/h432b/`. The
`openh432-ram-dev` image is a complete development system running from
initramfs, not an installer.

To also build the fastboot RAM loader and its kernel/device-tree/initramfs
bundle:

```sh
python3 scripts/bsp.py fetch u-boot-h432b-fastboot openh432-fastboot-ram
python3 scripts/bsp.py build u-boot-h432b-fastboot openh432-fastboot-ram
```

The bundle is named `openh432-ram-boot.img`. Read the
[fastboot guide](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/fastboot.md)
for supported use and prerequisites. Building these targets does not install
a bootloader or send anything to a device.

### Build directories and local changes

Append `--work /absolute/build-directory` to each command to use another
build disk. Downloads, shared-state cache and run records are retained there.
Do not run concurrent builds in the same work directory.

For layer development, place checkouts of both layer repositories beside
this repository and pass `--local-layers`. This explicitly replaces the
manifest's pinned layer commits with those working trees; it is not a
release build configuration.

Default parallelism is two BitBake tasks with four compiler jobs per task.
Disk monitoring stops new tasks at 10 GB free and halts the build at 5 GB.

## Build inputs and reproducibility

The [kas manifest](kas/h432b.yml) pins the layer, OpenEmbedded-Core and
BitBake commits. The [container lock](container/lock.json) pins the builder
base image and Arm GNU toolchain archive.

- Kernel and U-Boot builds use the official Arm GNU toolchain.
- Userland uses OpenEmbedded's pinned GNU compiler and glibc sysroot.
- Build identity and timestamps are fixed in the configuration.
- After container setup, only checkout and fetch operations have network
  access. Parse and build operations run without network access.
- The launcher records the effective configuration and container image for
  each run.

These controls support reproducible builds; they do not alone demonstrate
bit-for-bit reproducibility. See [validation status](docs/status.md) for
what has actually been built and tested.

## Device status and deployment

Repeated normal-reset boots from NAND have reached Linux and systemd
without a host upload, while retaining the factory bootloader. The current
OS runs from a development initramfs. Persistent production root storage,
coordinated A/B updates, Linux accessibility services and power management
remain unfinished; internal Wi-Fi has no working driver.

**Development images provide an unauthenticated physical USB root shell.**
They are intended for bring-up, not everyday or security-sensitive use.

Build commands never access USB or flash hardware. Default kernel storage
access is read-only; explicit NAND write profiles are development tools,
not installers. Bootloader artifacts have distinct load addresses and roles
and must not be used interchangeably.

Before any deployment, read the
[boot contract](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/boot-contract.md)
and [NAND documentation](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/nand.md).
The [architecture notes](docs/architecture.md) describe repository and
image boundaries; the [validation record](docs/status.md) tracks hardware
qualification separately from successful builds.

## License and affiliation

New build scripts and metadata are MIT-licensed. Linux, U-Boot and other
components retain their upstream licenses. This source-only project does
not distribute proprietary vendor firmware or device dumps.

OpenH432 is an independent Fractal Microsystems project, not affiliated
with or endorsed by HIMS.
