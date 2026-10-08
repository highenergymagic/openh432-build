# Build configuration

Use the [quick start](../README.md#quick-start) for the normal NAND runtime.
The launcher runs compilation inside a pinned container; it never accesses
USB devices or deploys an image.

## Commands

| Action | Purpose | Network |
| --- | --- | --- |
| `image` | Prepare the architecture-specific builder | Required for initial setup |
| `checkout` | Populate pinned layer sources | Enabled |
| `parse` | Check BitBake metadata | Disabled |
| `graph` | Resolve target dependencies | Disabled |
| `fetch` | Populate recipe download inputs | Enabled |
| `build` | Produce the selected artifacts | Disabled |

Fetch the same targets and configuration before an offline build.
Fetch/build require a [stock firmware input](firmware.md) or an explicit
`--without-wifi`.

## Targets

Without recipe arguments, the launcher builds `openh432-nand-b`,
`openh432-systembase-b` and `u-boot-h432b-ab-chain`: a slot-independent kernel
bundle, separate system userspace and the persistent A/B bootloader carrier.
The historical `-b` image names do not restrict deployment to slot B.

Specify recipe names after the action to select other targets. For example,
to build a fastboot RAM loader and standalone recovery environment:

```sh
python3 scripts/bsp.py fetch u-boot-h432b-fastboot openh432-fastboot-ram --without-wifi
python3 scripts/bsp.py build u-boot-h432b-fastboot openh432-fastboot-ram --without-wifi
```

The standalone environment is `openh432-ram-boot.img`. It includes a full
RAM root filesystem and does not require a provisioned NAND systembase.
Read the [fastboot reference](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/fastboot.md)
before using it. The [target catalogue](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/targets.md)
lists deployment and diagnostic profiles; the
[battery telemetry guide](battery-telemetry.md) describes that optional profile.

Bootloader artifacts have distinct load addresses and roles. Do not
substitute one for another or infer installation safety from a successful
build. Deployment is covered by the
[installation guide](https://github.com/highenergymagic/openh432-tools/blob/main/docs/installation.md).

## Work directories

Append `--work /absolute/build-directory` to each command to select another
build disk. Sources, downloads, shared-state cache, outputs and run records
are retained beneath that directory. Run only one build per work directory.

Use separate directories for different host architectures.
[Host setup](build-hosts.md) covers fixed-UID permissions and platform
selection. Default parallelism is two BitBake tasks with four compiler jobs
per task. Disk monitoring stops new tasks at 10 GB free and halts at 5 GB.

## Local-layer development

Place checkouts of all three Fractal Microsystems layers beside this
repository and add `--local-layers` to the required commands.
This replaces their manifest pins with read-only mounts of the working
trees. It is a development configuration, not a pinned release build.

Keep board changes in the hardware layer, distribution policy in the OS
layer, and third-party media recipes in the assets layer. Update the
manifest's layer commits when publishing an integrated build revision.

## Reproducibility

The [manifest](../kas/h432b.yml) and
[container lock](../container/lock.json) pin source revisions and builder
inputs. The configuration fixes build identity and timestamps. All target
components use OpenEmbedded's GNU toolchain and glibc sysroot.

Build records under `work/logs/` retain the effective configuration,
container identity, host architecture and private-input hashes.
See [cross-host validation](cross-host-validation.md) for measured
bit-for-bit results, comparison commands and qualification limits.
