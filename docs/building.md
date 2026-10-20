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

## Offline validation

After `checkout`, run the host-side build-orchestrator tests, then the layer
suites in the pinned native builder:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/test-layers.py
```

The layer runner supports `--work`, `--platform` and `--local-layers`. It
enables the compiled C vectors and fails if a test is skipped. Test containers
have read-only sources, temporary scratch storage, no network and no device
access. Preparing a missing builder still requires network access. CI runs
these checks on native x86-64 and ARM64; device qualification remains separate.

## Targets

Without recipe arguments, the launcher builds `openh432-nand-b`,
`openh432-systembase-b` and `u-boot-h432b-modern-nand`: a slot-independent kernel
bundle, separate system userspace and the persistent A/B bootloader carrier.
The historical `-b` image names do not restrict deployment to slot B.

For the independent NAND recovery menu, build `openh432-recovery-image`
explicitly using the same storage, firmware and speech configuration as the
normal release. Its output is `openh432-recovery.img`. Factory defaults are
taken from the built systembase; neither a running device nor a working system
slot is needed to build or boot it. See the
[recovery guide](https://github.com/highenergymagic/meta-fractalmicro-openh432/blob/main/docs/recovery.md)
for installation and reset behavior.

Specify recipe names after the action to select other targets. For example,
to build the legacy conversion loader and full development RAM environment:

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

## Optional speech backend

`--speech-backend openevv` selects OpenEVV instead of RHVoice/SLT in
systembase. It requires an explicitly supplied, checksum-pinned archive via
`--openevv-source /private/path/openevv.tar`. Supplying the archive alone
enables component builds without changing the image backend. Use the same
options for fetch and build.

See the OS layer's
[OpenEVV reference](https://github.com/highenergymagic/meta-fractalmicro-openh432/blob/main/docs/openevv.md)
for the accepted input, capabilities and restrictions. Restricted sources and
resulting images are not public release artifacts without appropriate
distribution rights. A build option is not a license grant.

## Persistent internal storage

`--storage-mode persistent` enables the internal-SD handoff in the NAND image.
Use the same mode for fetch and build. It requires a provisioned four-partition
card and the extension matching the selected systembase; a layout mismatch
enters initramfs recovery, not automatic formatting. The default `volatile`
mode retains the RAM-backed writable overlay.

The systembase build also produces
`openh432-systemext-h432b.rootfs.erofs.verity` and its `.verity` descriptor.
The descriptor is embedded in systembase. Deploy the matching extension to
the same A/B slot as the kernel and base. The artifact manifest includes all
six payload/descriptor files (schema 7).

See the distribution layer's
[persistent storage reference](https://github.com/highenergymagic/meta-fractalmicro-openh432/blob/main/docs/persistent-storage.md)
for the layout, deployment-local `/etc`, provisioning and reset interfaces.

## Work directories

Append `--work /absolute/build-directory` to each command to select another
build disk. Sources, downloads, shared-state cache, outputs and run records
are retained beneath that directory. Run only one build per work directory.

Use separate directories for different host architectures.
[Host setup](build-hosts.md) covers fixed-UID permissions and platform
selection. Default parallelism is two BitBake tasks with four compiler jobs
per task. Disk monitoring stops new tasks at 10 GB free and halts at 5 GB.

## Reclaiming build storage

Stop all builds and containers using a workspace before removing generated files.
Archive the deployed image set and its tested fallback, hashes, build records
and any required private inputs outside the work directory first.

`work/build/tmp` contains disposable compilation trees, staging sysroots and
deployment outputs. Removing this directory reclaims most build storage; the
next build restores eligible tasks from `work/sstate-cache`. Do not retain its
task stamps separately from the generated tree. BitBake event logs and metadata
caches under `work/build` are also disposable once relevant failure records have
been retained.

Keep `work/downloads` to avoid fetching source again and `work/sstate-cache` to
avoid recompiling unchanged tasks. These caches can be removed independently
when disk capacity matters more than rebuild time. Neither cache replaces Git
sources, the pinned manifest, private build inputs or release artifacts.

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
