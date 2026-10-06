# Validation status

Updated 2026-10-06 UTC. Source-only developer preview, not an installer.

## NAND bring-up (current)

Software BCH8/512 is qualified across Linux and U-Boot. A full raw+OOB backup
was verified privately before writes. A bounded scratch erase/program/readback
passed, followed by provisioning the 507 MiB UBI pool. Kernel A and base A
full SHA256 readbacks passed; the first 4 MiB including OOB stayed identical.
Both base slots are capped at 199.926 MiB. UBI reports 138 unallocated PEBs
in addition to internal reserves. B/recovery/bootstate capacity is reserved
but those slots are not yet populated or managed by a rollback policy.

The interactive RAM-staged NAND reader booted Linux from kernel_a, including
the debug initramfs. Kernel/base readback and ubiblock/SquashFS mount tests
passed. Kernel taint and ECC failures stayed zero; systemd reports running
with no failed units. Kernel + userspace startup was 28.755 seconds, excluding
the significantly slower unoptimized U-Boot NAND read. This is not a production
SquashFS-root boot.

The corrected automatic reader also booted the NAND kernel and passed the
same hash/mount/health checks without host kernel upload. It took136.261s
from loader launch to shell (113.382s to Linux USB); kernel+userspace28.696s.
The two-stage CE bootstrap builds offline. Its packager reproduces the legacy
carrier byte-for-byte and its image/heap/stack checks pass.
NAND56 is installed and its factory-assisted launch and subsequent plain Reset
both passed full hash/mount/health checks. The complete CE payload read back
exactly from NAND. StepLoader/EBOOT (main plus OOB) are unchanged; internal
SD remains read-only and unpartitioned by this work. First plain-Reset boot:
about 138 seconds to the shell, including 28.731 seconds Linux/systemd.
A second plain Reset also passed both complete readbacks, SquashFS mount
and health checks. The two observed reset-to-shell times were 137.965 and
138.213 seconds; Linux/systemd startup was 28.731 and 28.887 seconds.
No power-removal/cold-power test or long endurance test is claimed.
No binary installer or production firmware release is being published.
Kernel Kconfig now fails if UBI/ubiblock/SquashFS-XZ/UBIFS requirements vanish.
Explicit scratch/UBI writer profiles never gain boot-prefix or tail access.

The current pinned NAND composition is hardware layer
`f9e5d9e222719efb7fd80b470014a501bd22fc41` and OS layer
`bb188ea4e991591e901d3dd7e2705f9aa2c39ff1`. Normal pinned checkout and offline
build passed 2,869 cached tasks. CE carrier, high-RAM reader, kernel bundle
and SquashFS base compare byte-for-byte with the frozen hardware-tested inputs.
This checks the published composition, not independent clean-cache bit
reproducibility. 39 hardware, nine OS and eight launcher tests pass, plus
native C guard/parser checks during builds. All nine target graphs resolve.

The following sections record the earlier RAM-only baseline.

## Compiled and boot-tested RAM baseline

All four targets build successfully offline in the pinned Docker environment:
`u-boot-h432b`, `u-boot-h432b-ram`, `linux-h432b` and `openh432-ram-dev`.
The kernel uses Arm GNU 14.3.rel1; userland uses OE-Core GCC 15.3/glibc 2.43.
The board kernel remains CIP 6.12.111-cip32 plus the separately pinned rt21
patch, not an official combined CIP RT release.

The resulting kernel, DTB and XZ RAM root were booted on a real U2 through
the preserved, previously qualified NAND51/RAM52 boot path. The newly compiled
U-Boot artifacts were NOT flashed or substituted into that test.
No NAND/SD write, partitioning or persistent mount occurred.

Verified on the final RAM image:

- systemd 259.5 is PID 1 and reports running, with no failed units or runtime
  service overrides; USB console, udev, journald and networkd work.
- PREEMPT_RT is active; kernel taint remains zero after the checks.
- NAND/internal SD identity and guarded reads, SDIO enumeration, and USB host
  root hubs still work. Wi-Fi has no function driver yet.
- A bounded transient systemd service verified seccomp filtering,
  no-new-privileges, memory/task limits and filesystem-isolation settings.
  This smoke test is not complete security qualification.
- Repart's installer authorization is absent, GPT auto-discovery is disabled,
  and fstab has no persistent mounts.
- Both audio mixer ceilings clamp to 50/63; all outputs were left muted.
  No audible playback test was performed in this Yocto qualification.

Final observed boot: 7.626 s kernel + 19.128 s userspace = 26.754 s.
This excludes the U-Boot stage and host upload; verbose diagnostics remain.
The compressed RAM root is 10,100,632 bytes, below the 16 MiB slot limit.

## Fastboot RAM boot

Two additional targets compile in the same pinned builder:
`u-boot-h432b-fastboot` (RAM53-only) and `openh432-fastboot-ram` (Android-v2
boot envelope). This adapter implements standard fastboot on the existing
2012.10 S3C UDC, with no storage-write backend.

The real U2 enumerated with unmodified fastboot35.0.2. A 10,100,632-byte
rootfs uploaded in8.14s with matching CRC; the13,735,936-byte complete envelope
uploaded in11.07s. The embedded kernel, DTB and rootfs exactly match the
qualified baseline. `fastboot boot` reached Linux/systemd and passed the
USB health/read-only hardware checks. Standard `fastboot reboot` returned
to the preserved installed NAND51.

Eleven download sizes from1 through65536 passed CRC, including USB packet
and16KiB request boundaries. Unknown variables and erase correctly returned
FAIL. The board parser's native tests also run inside the pinned build.
A second boot with the final148404-byte RAM53 loader also passed systemd
health (26.801s kernel+userspace); flash rejection and muted audio ceilings
were verified. Final loader SHA256:
`dc12a3cf794e3d3b88336b96151f44debedb1a840ec8784c55114042458cebff`.
Boot envelope SHA256:
`5620c7b34a092b00b5f061cf680d715bcc2fb067692ad75e01f1a9807759426b`.
High-speed only has been device-tested. No NAND/SD writes occurred.
This is RAM boot qualification, not NAND kernel boot or a production updater.

## Repairs covered by regression tests

- Kernel source-path assignment follows kernel class inheritance.
- The verified upstream RT patch gets a provenance-only metadata header.
- Target binutils overrides survive Wrynose's deferred toolchain inheritance,
  so packaging uses the pinned Arm tools too.
- U-Boot follows Wrynose's Git unpack layout.
- The kernel enables XZ decoding. XZ uses CRC32 and one fixed compressor thread.
- Rootfs timestamps and artifact names use the fixed epoch.
- Required identity, tools and dlopen libraries are installed explicitly and
  checked. Missing libseccomp was caught by the first hardware smoke test,
  then fixed in the recipe and verified on a fresh boot.

39 hardware-layer, nine OS-layer and eight build-orchestration tests pass.
CI runs both pinned layer suites, parses metadata and resolves target graphs.
CI does not build complete images or perform hardware tests.

## Scope and reproducibility

Hardware qualification above used local layer development inputs. The earlier public
BSP e3184bf1ce78321fcebac6db7ab1d66b1fec9c85 and OS
cf529a05898d07b44844366e1351db8e0109a22f composition passed2,813 cached tasks,
with artifacts identical to the frozen boot-tested kernel, DTB and RAM root.
The current manifest adds fastboot through BSP6bbcef5a71d6fb5f2cf11fac5cc135befb86a58f
and OS4fc4a893e66995260030928e0c4ddcfebcdb4606. A normal pinned
checkout/fetch/offline build passed2,803 cached tasks; both fastboot loader and
boot envelope compared byte-for-byte identical to the frozen device-tested
artifacts. Final sandbox, read-only hardware and muted audio checks also passed.
This validates the published composition, not an independent rebuild.
No independent clean-cache, same-input bit-reproducibility claim is made.
Build-source pins, fixed identities, timestamps and cache reuse do not alone
prove bit reproducibility. No binary release is published.

The earlier Buildroot images and failed build/test evidence remain preserved.
Production A/B installation, Wi-Fi, Linux braille, keys and power management
remain separate work. MIT covers new metadata; component GPL licenses remain.
