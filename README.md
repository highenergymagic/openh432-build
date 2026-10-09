# OpenH432 BSP

OpenH432 is a Yocto/OpenEmbedded BSP for the HIMS BrailleSense U2 (H432B),
maintained by Fractal Microsystems. This repository provides the pinned
source manifest, containerized build environment and image build commands.

The standard NAND image boots to an interactive BRLTTY console with local
login as `user`, persistent A/B selection and boot-success tracking.

**Development release:** not yet a complete replacement for the stock firmware.
Review the [support matrix](docs/status.md) before deployment.
Development images expose an unauthenticated physical USB root console.

## Platform

| Setting | Value |
| --- | --- |
| Device | HIMS BrailleSense U2, H432B |
| Processor | Samsung S5PV210, ARM Cortex-A8 |
| Yocto series | Wrynose |
| Machine / distribution | `h432b` / `openh432` |
| Build hosts | Native Linux x86-64 and ARM64 |
| Toolchain | OpenEmbedded GNU toolchain and sysroot |

## Requirements

- Git, Python 3 and Docker, with access to the Docker daemon.
- Approximately 150–200 GB of build storage.
- A work directory writable by the container's UID/GID `1000:1000`.
- A supported stock `nk.bin` for local radio-firmware extraction.

See [host setup](docs/build-hosts.md) for permissions and architecture
selection, and [stock firmware input](docs/firmware.md) for the accepted
image and checksum. No host cross-compiler is required.

## Quick start

Run on the Linux build host:

```sh
git clone https://github.com/highenergymagic/openh432-build.git
cd openh432-build
python3 scripts/bsp.py image
python3 scripts/bsp.py checkout
python3 scripts/bsp.py fetch --stock-nk /path/to/nk.bin
python3 scripts/bsp.py build --stock-nk /path/to/nk.bin
```

Replace the input path with your stock image. To configure the radio's
operating country, supply `--wifi-country` with its uppercase ISO code to
both fetch and build; the default is the world domain `00`.
For a firmware-free build, replace `--stock-nk …` with `--without-wifi`.

The default output directory is `work/build/tmp/deploy/images/h432b/`:

| Artifact | Purpose |
| --- | --- |
| `openh432-nand-b.img` | Slot-independent kernel bundle with loader-selected root handoff |
| `openh432-systembase-b-h432b.rootfs.squashfs` | Slot-independent system userspace |
| `nand-ab-ce-carrier/u-boot-ce.b000ff` | A/B bootloader carrier for provisioned devices |

The historical `-b` image names are retained for compatibility; the same pair
can populate either slot. The carrier requires provisioned UBI and bootstate.

Build commands do not access a device or install images. Use the
[installation guide](https://github.com/highenergymagic/openh432-tools/blob/main/docs/installation.md)
for deployment and artifact roles; kernel bundles, raw loaders and CE carriers
are not interchangeable.

## Source layout

The [manifest](kas/h432b.yml) pins the following layers alongside
OpenEmbedded Core, BitBake and meta-openembedded.

| Repository | Responsibility |
| --- | --- |
| [meta-fractalmicro-H432B](https://github.com/highenergymagic/meta-fractalmicro-H432B) | Machine, kernel, device tree and bootloader |
| [meta-fractalmicro-openh432](https://github.com/highenergymagic/meta-fractalmicro-openh432) | Distribution, system services and images |
| [meta-fractalmicro-assets](https://github.com/highenergymagic/meta-fractalmicro-assets) | Third-party media recipes and licence notices |
| [openh432-tools](https://github.com/highenergymagic/openh432-tools) | Host transport, backup and installation tools |

## Documentation

- [Build configuration](docs/building.md): targets, workspaces and local-layer development.
- [Stock firmware input](docs/firmware.md): extraction, verification and private outputs.
- [Speech configuration](https://github.com/highenergymagic/meta-fractalmicro-openh432/blob/main/docs/speech.md): offline backends and optional restricted inputs.
- [Architecture](docs/architecture.md): component, boot and storage boundaries.
- [Support matrix](docs/status.md): supported configurations and known limitations.
- [Reproducibility](docs/cross-host-validation.md): demonstrated bit-for-bit cross-host results and their scope.
- [Hardware validation](docs/hardware-validation.md): tested artifacts and procedures.
- [Documentation maintenance](docs/documentation.md): contributor guidelines.

## Licence

Build scripts and metadata are MIT-licensed. Components and media retain
their upstream licences. Stock CE images and extracted radio firmware are
not distributed in these repositories; firmware-enabled build outputs remain
private unless redistribution rights are established.

OpenH432 is independent of, and not endorsed by, HIMS.
