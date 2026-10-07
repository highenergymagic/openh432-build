# Native build hosts

The launcher supports Linux x86-64 and ARM64 Docker daemons. The target remains
32-bit ARM H432B; changing the build host does not change MACHINE or DISTRO.

By default, `scripts/bsp.py` queries the Docker daemon's OS and architecture,
not the client machine's CPU. An explicit `--platform linux/amd64` or
`--platform linux/arm64` selects a pinned builder. Choosing the other platform
does not install emulation; the daemon must already support executing it.

Each platform has its own immutable kas 5.5 container manifest digest in
[container/lock.json](../container/lock.json). All target components use the
OpenEmbedded GCC/binutils recipes selected by the pinned OE-Core revision.
The BSP layer carries an ordered ARM compiler reproducibility patch. There is
no external target-compiler archive or host-distribution target sysroot.

## Clean build

Use a fresh work directory with no copied downloads, sstate cache, sysroots
or outputs when testing independent reproducibility:

```sh
git clone https://github.com/highenergymagic/openh432-build.git
cd openh432-build
git checkout --detach <build-commit>
python3 scripts/bsp.py image
python3 scripts/bsp.py checkout --work /absolute/fresh-work
python3 scripts/bsp.py fetch openh432-nand-b openh432-systembase-b u-boot-h432b-maintenance-chain --work /absolute/fresh-work --stock-nk /path/to/nk.bin
python3 scripts/bsp.py build openh432-nand-b openh432-systembase-b u-boot-h432b-maintenance-chain --work /absolute/fresh-work --stock-nk /path/to/nk.bin
```

The builder always runs as UID/GID 1000:1000. Create the selected work directory
before checkout and grant that identity access if your host UID differs.
For example, using the host's POSIX ACL tools on that directory only:

```sh
mkdir -m 0700 /absolute/fresh-work
mkdir -m 0700 /absolute/fresh-work/home
setfacl -m "u:1000:rwx" /absolute/fresh-work /absolute/fresh-work/home
```

Use access ACLs only, never default/inheritable ACLs. Default ACLs can change
permissions recorded by fakeroot in target packages and filesystem images.
The launcher refuses work directories carrying default ACLs; use a new work
directory rather than reusing outputs built under that setup.

No global ownership change or world-writable permission is required.
Docker, Git and Python 3 are host prerequisites; native target compilers are not.

A `builder-platform.json` marker prevents one work directory from switching
architectures. Use separate work directories, not deletion or marker editing,
when changing platform. Legacy unmarked build state is accepted only for the
previously supported x86-64 platform. Explicit local-layer overrides are not a
public-pins reproducibility test.

## What to compare

Build records retain the selected platform, immutable builder inputs, actual
container image ID and effective kas configuration. Compare the same source
commits, target recipes, NAND profile and image configuration on both hosts.

Compare deployed target payloads (U-Boot binary/CE carrier, kernel, device tree,
compressed initramfs, boot envelope and filesystem images) by SHA256. Do not
expect x86-64 and ARM64 host executables or container image IDs to match.

Native support and byte-for-byte target reproducibility are separate claims.
Architecture selection has unit coverage; CI runs metadata checks on both
runner architectures. All ten selected target payloads matched across both native hosts; see the
[measured results and qualification limits](cross-host-validation.md).

## Fetch transport

The manifest prefers the public Yocto source mirror for GNU/Savannah archives
whose primary servers may be unreachable from some hosts. Recipe checksums are
still mandatory and unchanged; the mirror does not replace source pins or
permit different archive contents. No private cache is required.

## Artifact comparison command

After building all three targets below on each platform:

```sh
python3 scripts/bsp.py fetch openh432-nand-b openh432-systembase-b u-boot-h432b-maintenance-chain --stock-nk /path/to/nk.bin
python3 scripts/bsp.py build openh432-nand-b openh432-systembase-b u-boot-h432b-maintenance-chain --stock-nk /path/to/nk.bin
python3 scripts/artifact-manifest.py work/build/tmp/deploy/images/h432b > target-hashes.json
```

Transfer only the reference hash manifest to the other host after its build,
then run:

```sh
python3 scripts/artifact-manifest.py work/build/tmp/deploy/images/h432b --compare reference-hashes.json
```

The command requires the current NAND carrier, kernel bundle and systembase
(schema 2), and exits nonzero on any mismatch. The manifests contain file
names, sizes and hashes, not firmware contents. The historical ten-payload
comparison uses schema 1 and the older script at its documented build revision;
it is not a reference manifest for the current deployment set.

## Continuous integration

GitHub Actions validates the pinned layers on native x86-64 and ARM64 runners:
source/documentation audits, layer contract tests, offline metadata parsing,
and dependency-graph resolution for the supported development image variants.
These checks are not full image builds or hardware tests.

OpenEmbedded and BitBake use sibling checkout paths. Fixed-UID workspace
access uses non-inherited ACLs. CI target compilers come from pinned OE recipes;
no external Arm binary toolchain is required.
