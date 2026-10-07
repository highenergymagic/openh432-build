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
- [meta-fractalmicro-assets](https://github.com/highenergymagic/meta-fractalmicro-assets):
  separately licensed system sound assets and reproducible audio conversion;
  included in the pinned build manifest.
- **openh432-build** (this repository): source locks, build container,
  orchestration and validation.

Host-side installation and recovery tooling lives in
[openh432-tools](https://github.com/highenergymagic/openh432-tools). Start with
its [conversion guide](https://github.com/highenergymagic/openh432-tools/blob/main/docs/installation.md)
for the path from Windows CE, backup requirements and remaining qualification
gaps. It is a developer workflow, not an unattended installer.

The hardware target is `h432b`; the distribution is `openh432`.
The manifest also pins OpenEmbedded Core, BitBake and the Wrynose `meta-oe`
layer from meta-openembedded, which supplies gpsd and its build dependencies.

## Building

### Requirements

- A Linux x86-64 (amd64) or ARM64 (aarch64) host with Docker, Python 3 and Git.
- Access to the Docker daemon, directly or through `doas`/`sudo`.
- Approximately 150–200 GB of disk space for a useful development build cache.
- A build directory writable by UID/GID `1000:1000`, the container's builder identity.

No host cross-compiler is required. The launcher builds and runs the pinned
container; compilation happens inside it. Native builds on both architectures
are supported without CPU emulation. The default selects the Docker daemon's
architecture; use `--platform linux/amd64` or `--platform linux/arm64` to
select explicitly. Keep separate work directories for different architectures.
See [native build hosts](docs/build-hosts.md) for setup details.

### Build the NAND runtime pair

```sh
git clone https://github.com/highenergymagic/openh432-build.git
cd openh432-build

python3 scripts/bsp.py image
python3 scripts/bsp.py checkout
python3 scripts/bsp.py parse
python3 scripts/bsp.py fetch
python3 scripts/bsp.py build
```

Artifacts are placed in `work/build/tmp/deploy/images/h432b/`:
`openh432-nand-b.img` is the kernel/device-tree/minimal-initramfs bundle;
`openh432-systembase-b-h432b.rootfs.squashfs-xz` is the separate base userspace.
Neither artifact is an installer, and the build does not flash a device.

### Internal Wi-Fi firmware

The runtime includes the Wi-Fi station driver, `iw`, `wpa_supplicant`, a signed regulatory
database and automatic initialization. NAND-booted WPA2-PSK/CCMP association,
DHCP, reconnect and checksum-verified Wi-Fi-only transfers have passed on
hardware. The development driver currently uses a fixed 1 Mb/s transmit rate;
see the [checkpoint record](docs/status.md#wi-fi-checkpoint-2026-10-07) for
validation scope and remaining limitations. Factory radio firmware is not
redistributed. Supply a legally obtained, compatible file explicitly:

```sh
python3 scripts/bsp.py fetch --wifi-firmware /path/to/rtl8712s.bin --wifi-country NZ
python3 scripts/bsp.py build --wifi-firmware /path/to/rtl8712s.bin --wifi-country NZ
```

Replace `NZ` with the device's actual operating country; the default is the
world domain `00`. The launcher verifies the qualified firmware digest, copies
it into the ignored private build directory and records its hash. Use the same
options for fetch and build. The resulting systembase contains that private
firmware and must not be published without redistribution rights. Default
builds omit the binary and skip Wi-Fi initialization until it is installed.
No Wi-Fi password is accepted or embedded by the build.

### Standalone recovery and optional diagnostics

To build the fastboot RAM loader and standalone recovery bundle:

```sh
python3 scripts/bsp.py fetch u-boot-h432b-fastboot openh432-fastboot-ram
python3 scripts/bsp.py build u-boot-h432b-fastboot openh432-fastboot-ram
```

The bundle is named `openh432-ram-boot.img`. It uses the normal runtime kernel
with a complete RAM root filesystem, so it does not require a provisioned NAND
systembase. There is no separate legacy kernel. Read the
[fastboot guide](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/fastboot.md)
for supported use and prerequisites. Building these targets does not install
a bootloader or send anything to a device.

The [target catalogue](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/targets.md)
separates normal deployment, initial conversion and optional hardware diagnostics.
Obsolete intermediate recipes have been retired; their history remains in Git.

### Build directories and local changes

Append `--work /absolute/build-directory` to each command to use another
build disk. Downloads, shared-state cache and run records are retained there.
Do not run concurrent builds in the same work directory.

For layer development, place checkouts of all three layer repositories (hardware, OS and assets) beside
this repository and pass `--local-layers`. This explicitly replaces the
manifest's pinned layer commits with those working trees; it is not a
release build configuration.

Default parallelism is two BitBake tasks with four compiler jobs per task.
Disk monitoring stops new tasks at 10 GB free and halts the build at 5 GB.

## Build inputs and reproducibility

The [kas manifest](kas/h432b.yml) pins the layer, OpenEmbedded-Core and
BitBake commits. The [container lock](container/lock.json) pins the builder
native base-image digest for each supported host architecture.

- Kernel, U-Boot and userland use OpenEmbedded's pinned GNU toolchain.
- Userland uses OpenEmbedded's glibc sysroot; no host-distribution target
  toolchain or external Arm binary compiler is required.
- Build identity and timestamps are fixed in the configuration.
- After container setup, only checkout and fetch operations have network
  access. Parse and build operations run without network access.
- The launcher records the effective configuration and container image for
  each run.

Ten selected target payloads produced identical sizes and SHA256 hashes on
native amd64 and ARM64 builders. See the [measured reproducibility
results](docs/cross-host-validation.md) for the exact tested source revisions,
hash manifest and limitations. That result does not automatically qualify
later source changes or establish two empty-cache rebuilds of the final
revision. [Validation status](docs/status.md) separates builds from hardware tests.

### System sound assets

The manifest imports and pins
[meta-fractalmicro-assets](https://github.com/highenergymagic/meta-fractalmicro-assets)
alongside the hardware and OS layers. It fetches the selected upstream KDE
startup/logout sounds with verified checksums and uses pinned integer-only
decoding for reproducible PCM output. Assets retain their upstream licenses;
they are not covered by the metadata's MIT license.

The normal NAND systembase includes the selected boot and shutdown sounds.
The optional `openh432-ram-dev` diagnostic image is quiet. Layer inclusion
and image package selection remain separate: importing the assets layer does
not make every image play sounds. See the
[system sounds guide](https://github.com/highenergymagic/meta-fractalmicro-openh432/blob/main/docs/system-sounds.md).

## Device status and deployment

Repeated normal-reset boots from NAND have reached Linux and systemd
without a host upload, while retaining the factory bootloader. The default
targets are the NAND kernel bundle and separate systembase.
A minimal handoff initramfs mounts the slot-matched SquashFS systembase
and starts systemd; it does not contain the full userspace. Historical RAM
diagnostic targets remain available explicitly, not as the default workflow.
Persistent writable user data, coordinated A/B updates, Linux accessibility
services and suspend/resume remain unfinished. The NAND Wi-Fi station driver
has demonstrated WPA2-PSK/CCMP association, DHCP, reconnect and checksum-verified
bidirectional transfers with Ethernet disabled.
Its supported security modes, data rates and recovery behavior remain limited.
See the [Wi-Fi qualification guide](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/wifi.md)
for firmware requirements and test limitations.

The internal FM receiver now supports V4L2 tuning and muted signal scanning.
Frequency peaks have been corroborated against local broadcasts; audible FM
and stereo reception remain unqualified. See the
[FM guide](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/fm.md).

**Development images provide an unauthenticated physical USB root shell.**
They are intended for bring-up, not everyday or security-sensitive use.

Build commands never access USB or flash hardware. The normal NAND runtime
permits Linux UBI maintenance and internal SD writes. Factory boot and BBT
regions remain protected, and the immutable SquashFS systembase is mounted
read-only. Historical qualification profiles remain explicit development
tools, not installers. Bootloader artifacts have distinct load addresses and roles
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

## Battery telemetry experiment

The current manifest includes the opt-in read-only battery image alongside
the normal NAND targets. See [battery telemetry](docs/battery-telemetry.md)
for its standard Linux interface, explicit build commands and RAM qualification
limits. The diagnostic does not enable battery polling in the normal runtime
or install firmware on a device.
