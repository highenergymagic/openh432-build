# Cross-host validation

## Toolchain migration in progress

Current recipes select OE-built GCC for every target component and carry the
ARM scratch-allocation ordering fix in a version-specific shared-source append.
New compilation and cross-host comparison are required; the results below
belong to the previous external Arm toolchain baseline.

Native amd64 and arm64 builders compile the three qualification targets:
u-boot-h432b-chain, openh432-fastboot-ram, and openh432-hardware-test.
This does not yet establish cross-host bit-for-bit reproducibility.

## Observed comparison

An independently fetched, empty-cache ARM64 build completed all 2,985 tasks.
The amd64 reference used existing cached build state with identical public pins.
Only the device tree matched among the ten target payloads on the first pass.

The base root filesystems contained 1,728 regular files with matching contents.
A decoded initramfs comparison found 2,098 differing mode fields, with no other
entry-field differences. Inherited workspace default ACLs changed permissions
recorded by fakeroot. The documented setup now uses access ACLs only, and the
launcher rejects a workspace root with default ACLs. A new build with empty sstate and the corrected setup completed successfully,
reusing only checksum-verified public downloads. Its base initramfs and SquashFS
images match the amd64 reference byte-for-byte. The failed workspace was not reused.

## Compiler output

The chain loader differed by 12 bytes in a 388,004-byte binary. The raw kernel
images were equal in size and differed by 24 bytes. Kernel configuration,
compiler identification, build identity and timestamp matched.

Repeated isolated compilations of U-Boot's number-formatting implementation
were stable on each host but differed across hosts. Preprocessed input and
optimized GIMPLE matched. RTL expansion differed in the assignment of two
temporary registers for a variable 64-bit logical right shift. Fixed random
seeds and the tested register-slot sharing options did not remove the difference.

The GCC 14.3 ARM lshrdi3 expansion passes two gen_reg_rtx calls as arguments
to one function, leaving their evaluation order unspecified. This is consistent
with the opposite temporary-register numbering observed in the two host builds.
See the [GCC 14.3 ARM machine description](https://github.com/gcc-mirror/gcc/blob/releases/gcc-14.3.0/gcc/config/arm/arm.md).

The follow-up migration applies ordered scratch allocations to OE GCC shared
source. It does not patch target source around the compiler behavior or weaken
the artifact comparisons. No new toolchain result is implied by this baseline.

## OE compiler checkpoint

The OE GCC 15.3 build with ordered scratch allocations has produced matching
kernel and device-tree payloads on both native hosts:

- zImage: `645f5a4979e4a35c7c7d53c8310d265a618d8a108041580f079a27ee4f331668`
- DTB: `22eacd9231767729693ac3a3184b51a0a06a345dd1dfba1962e7461300416db5`

The complete target-image comparison is still pending.

## Audio conversion

With filesystem permissions corrected, the previous hardware-test image
comparison differed only in its two decoded WAV files. Both hosts fetched the
same checksum-verified Ogg sources; the floating-point Vorbis conversion
produced different PCM bytes. The asset layer now pins Xiph's integer-only
Tremor decoder and emits little-endian PCM explicitly. Its full build and
cross-host comparison are pending; metadata tests are not a substitute.

## Claim boundary

Native compilation, metadata CI and launcher tests pass on both architectures.
Cross-host byte reproducibility remains unqualified. These builds have not been
flashed or device-tested. Host/container executables are intentionally outside
the target-image hash comparison.
