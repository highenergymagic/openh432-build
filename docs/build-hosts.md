# Native build hosts

The launcher supports Linux x86-64 and ARM64 Docker daemons. The target remains
32-bit ARM H432B; changing the build host does not change MACHINE or DISTRO.

By default, `scripts/bsp.py` queries the Docker daemon's OS and architecture,
not the client machine's CPU. An explicit `--platform linux/amd64` or
`--platform linux/arm64` selects a pinned builder. Choosing the other platform
does not install emulation; the daemon must already support executing it.

Each platform has its own immutable kas 5.5 container manifest digest and
checksum-pinned official Arm GNU 14.3.rel1 archive in
[container/lock.json](../container/lock.json). Kernel/U-Boot still use Arm GNU;
userland still uses the pinned OpenEmbedded compiler/sysroot.

## Clean build

Use a fresh work directory with no copied downloads, sstate cache, sysroots
or outputs when testing independent reproducibility:

```sh
git clone https://github.com/highenergymagic/openh432-build.git
cd openh432-build
git checkout --detach <build-commit>
python3 scripts/bsp.py image
python3 scripts/bsp.py checkout --work /absolute/fresh-work
python3 scripts/bsp.py fetch openh432-fastboot-ram u-boot-h432b-chain --work /absolute/fresh-work
python3 scripts/bsp.py build openh432-fastboot-ram u-boot-h432b-chain --work /absolute/fresh-work
```

The builder always runs as UID/GID 1000:1000. Create the selected work directory
before checkout and grant that identity access if your host UID differs.
For example, using the host's POSIX ACL tools on that directory only:

```sh
mkdir -m 0700 /absolute/fresh-work
setfacl -m "u:1000:rwx,d:u:1000:rwx,d:u:$(id -u):rwx" /absolute/fresh-work
```

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
runner architectures. Full cross-host artifact qualification is in progress.
