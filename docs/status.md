# Validation status

Updated 2026-10-06 UTC. OpenH432 is a source-only developer preview, not an
installer or production firmware release. Results below describe one H432B
qualification device, not every BrailleSense model or every future build.

## Qualified functionality

- Repeated plain-Reset boots loaded Linux from NAND with no host image upload,
  preserving the factory first-stage loader and EBOOT.
- Linux CIP 6.12.111-cip32 plus separately pinned rt21, systemd 259.5, USB
  diagnostics, internal SD reads, NAND access and PREEMPT_RT were exercised.
  This is not an official combined CIP RT release.
- Linux and U-Boot software BCH8/512 agreed on parity; 1–8 injected RAM bit
  errors per sector were corrected. NAND bad-block markers were retained.
- Bounded NAND provisioning, complete kernel/base SHA256 readbacks and
  SquashFS-on-ubiblock mount checks passed. Factory boot regions, including
  OOB, were checked byte-for-byte against the private backup after provisioning.
- Standard high-speed fastboot RAM download and Linux boot passed. Eleven
  transfer lengths covered USB packet and request boundaries. Unsupported
  flash/erase requests were rejected.
- Three physical power-switch presses produced paired KEY_POWER events
  without unwanted repeats or missing releases. Shutdown actions remained
  disabled during input qualification.
- Startup playback and shutdown playback during a systemd reboot were audibly
  verified in a RAM-resident system. Playback used volume 45 below the kernel
  limit of 50, and outputs were muted afterward.

The most recent restoration check booted the preserved NAND baseline on plain
Reset and reached a working USB shell with zero failed units and kernel taint 0.
Its Linux/systemd startup was 28.657 seconds, **excluding bootloader time**.
Input and sound experiments did not persist new packages in NAND.

## Boot performance

Two earlier reset-to-shell samples were 137.965 and 138.213 seconds.
A separate RAM-only profiler measured complete UBI attachment, kernel-bundle
read and validation in 95.823 seconds with caches off and 73.088 seconds with
instruction caching only. Both returned the same bundle CRC.

Those command measurements are not a qualified faster persistent boot.
The inherited U-Boot timer counts calls rather than time; its internal timing
numbers are invalid. The replacement PWM4 timer passed five-second delay checks against a host
clock with instruction caching both off and on. A further BCH partial-page
read experiment reduced UBI attachment from 34.981 to 22.178 seconds while
retaining ECC. Fifteen partial-read/full-page comparisons and RAM bit-error
correction checks passed. Full bundle read/validation remained 37.368 seconds,
with the expected CRC. The partial-page candidate also booted the NAND kernel to a healthy Linux
USB shell (zero failed units and taint 0). These remain RAM-only loader tests,
not qualification of an optimized persistent carrier.
See [boot performance](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/boot-performance.md).
A sub-30-second total boot has not been demonstrated.

## Built but not fully qualified

The explicitly audible `openh432-hardware-test` image built successfully; its
13,341,188-byte initramfs fits the 16 MiB limit and service-enablement links
were inspected. Its sound components were tested separately in RAM; a complete
boot of this packaged image remains untested.

The default development initramfs and NAND kernel bundle are not a production
SquashFS-root system. Kernel/base B, recovery and boot-state volumes reserve
capacity but do not implement a coordinated update or rollback policy.
Both system-base slots are capped at 199.926 MiB.

Internal Wi-Fi enumerates over SDIO but has no working function driver.
Linux braille, the remaining keyboard controls, battery management, electrical
poweroff, wake and suspend remain incomplete. Shutdown latency has not been
qualified. Internal SD has not been repartitioned by this work.
No power-removal test or long-duration endurance qualification is claimed.

Development images expose an unauthenticated root shell over physical USB.
Service-isolation smoke tests exercised seccomp, no-new-privileges,
memory/task limits and filesystem isolation; they are not a security audit.

## Build and reproducibility evidence

Kernel, U-Boot and userland use source-built OE-Core GCC 15.3; userland uses
the OE glibc 2.43 sysroot. Native amd64 and ARM64 builds run in pinned Docker
environments without an external Arm compiler archive. See the
[cross-host comparison](cross-host-validation.md) for measured evidence.
Builds and CI never open a USB device, flash NAND or modify device storage.

A previously qualified NAND composition used hardware-layer commit
`f9e5d9e222719efb7fd80b470014a501bd22fc41` and OS-layer commit
`bb188ea4e991591e901d3dd7e2705f9aa2c39ff1`. Its normal pinned offline build
passed 2,869 cached tasks; the CE carrier, high-RAM reader, kernel bundle and
SquashFS base matched the frozen hardware-tested inputs byte-for-byte.

That comparison does not establish independent clean-cache reproducibility,
and those historical commits are not a statement of the current manifest pins.
Use [kas/h432b.yml](../kas/h432b.yml) for the current composition. Source pins,
fixed identities, timestamps and cache reuse alone do not prove reproducibility.

Unit and native tests cover image parsing, memory overlap, write guards,
artifact roles, package requirements and build configuration. CI parses
metadata and resolves target graphs; it does not qualify device behavior.

## Further reading

- [Build architecture](architecture.md)
- [Boot roles and load addresses](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/boot-contract.md)
- [NAND layout and qualification](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/nand.md)
- [Installation prerequisites and remaining gaps](https://github.com/highenergymagic/openh432-tools/blob/main/docs/installation.md)
