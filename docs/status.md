# Validation status

Updated 2026-10-06 UTC. Source-only developer preview, not an installer.

## Compiled and boot-tested

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

Nine hardware-layer, nine OS-layer and seven build-orchestration tests pass.
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
A/B installation, NAND ECC/writes, Wi-Fi, Linux braille, keys and power management
remain separate work. MIT covers new metadata; component GPL licenses remain.
