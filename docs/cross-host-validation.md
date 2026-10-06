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
launcher rejects a workspace root with default ACLs. A new empty-cache build
with the corrected setup is being checked; the failed workspace is not reused.

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

## Claim boundary

Native compilation, metadata CI and launcher tests pass on both architectures.
Cross-host byte reproducibility remains unqualified. These builds have not been
flashed or device-tested. Host/container executables are intentionally outside
the target-image hash comparison.
