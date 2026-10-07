# Cross-host validation

## Result

On 2026-10-06, native Linux amd64 and ARM64 builds produced identical sizes
and SHA256 hashes for all ten selected target payloads. Both builds completed
the 2,985-task graph successfully. The checked-in
[hash manifest](target-hashes.json) records the exact outputs.

The comparison covers the CE carrier, raw NAND bootstrap, RAM second-stage
loader, kernel, device tree, development and hardware-test initramfs/SquashFS
images, and RAM boot envelope. It uses the default read-only NAND profile.

The legacy target names below are valid at the recorded revision. Some were
subsequently retired or consolidated; checking out that revision also restores
its matching artifact-manifest script. This result is retained as historical
evidence, not a claim that every current image has been compared across hosts.

## Pinned inputs

- Build orchestration: `a4221bfc1af4f1e8b8fb64a034448f3e00cef056`
- Hardware layer: `793c12296cf4f51fe483969c0932e55e92fc7753`
- OS layer: `d278582cbf689cb4e856c6fc67273b2ceb5bfd79`
- Assets layer: `1d846ec64f88c5e33ded2b20ec9179cf67293a6d`
- OE-Core: `ef022bf82d79015802309d14c28b13373ebe53f5`
- BitBake: `fae9db3168dbff1b8c76fe9c6726a9687ff97514`

The [container lock](../container/lock.json) pins native kas 5.5 images for
both platforms. All target components use OE-built GCC 15.3 and binutils;
there is no external Arm compiler archive. Userland uses OE's glibc sysroot.

## Procedure and limitations

Both hosts built only public pinned sources through the Docker launcher,
with separate native build workspaces. The ARM64 host began with an independent
empty-cache public build. Its corrected-permissions workspace reused only
checksum-verified public downloads, not sstate or outputs from the first run.
No amd64 compiler, sstate, sysroot or target binary was imported to ARM64.

The amd64 build used an existing workspace. Both hosts incrementally rebuilt
after the compiler and audio fixes. This is a measured cross-architecture
comparison, **not two fresh empty-cache builds of the final revision**.
Logs and earlier failed outputs were retained privately; they are not build
inputs or required dependencies.

Reproduce the selected build and compare it to the recorded result:

```sh
git checkout --detach a4221bfc1af4f1e8b8fb64a034448f3e00cef056
python3 scripts/bsp.py fetch u-boot-h432b-chain openh432-fastboot-ram openh432-hardware-test
python3 scripts/bsp.py build u-boot-h432b-chain openh432-fastboot-ram openh432-hardware-test
python3 scripts/artifact-manifest.py work/build/tmp/deploy/images/h432b --compare /path/to/target-hashes.json
```

Save this documentation revision's hash manifest before checking out the
recorded build revision. See [native build hosts](build-hosts.md) for clean
workspace setup, UID access and platform selection.

## Differences found and corrected

### Workspace permissions

The initial ARM64 comparison had matching contents for all 1,728 regular base
rootfs files, but 2,098 initramfs mode fields differed. Inherited default ACLs
altered permissions recorded by fakeroot. The setup now uses access ACLs only,
and the launcher rejects default ACLs on the workspace root. The corrected
workspace produced matching base filesystems before the compiler migration.

### Compiler register allocation

The external Arm GCC 14.3 build produced different ARM code on different host
architectures. Identical preprocessed input and optimized GIMPLE led to
different RTL scratch-register allocation for a variable 64-bit shift.

The ARM machine description passed two `gen_reg_rtx` calls as arguments to
one function, with unspecified evaluation order. The OE GCC 15.3 shared-source
patch allocates those registers in explicit statements for all three 64-bit
shift forms. It does not weaken hash checks or work around the discrepancy
in target code. See the
[GCC ARM machine description](https://github.com/gcc-mirror/gcc/blob/releases/gcc-15.3.0/gcc/config/arm/arm.md).

The historical U-Boot recipe also needed generated dependency cleanup when
changing compilers and a GCC 15 compatibility header. Both loader memory-layout
checks pass with the new compiler.

### Sound conversion

After permissions were corrected, the hardware-test rootfs differed only in
two WAV files decoded from identical Ogg inputs. Floating-point Vorbis decoding
was replaced with a pinned integer-only Tremor decoder and explicit
little-endian PCM output. Both converted WAVs and both complete hardware-test
filesystem images now match across hosts.

## Qualification boundary

The result applies to the listed target payloads and pinned configuration,
not host executables, container IDs, every NAND profile or arbitrary future
source changes. Fixed inputs alone do not prove reproducibility; compare outputs.

These newly compiled images have **not** been flashed or tested on the device.
Previous hardware qualification belongs to the retained older artifacts.
A modern U-Boot port remains a separate migration after this compiler baseline.
