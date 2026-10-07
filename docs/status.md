# Validation status

Updated 2026-10-07 UTC. OpenH432 is a source-only developer preview, not an
installer or production firmware release. Hardware results describe one
H432B qualification device, not every BrailleSense model or future build.

## Normal NAND runtime

Repeated normal resets and software reboots have loaded Linux from NAND
without a host upload, preserving the factory first-stage loader and EBOOT.
The default composition is a kernel/device-tree/minimal-initramfs bundle
plus a separate SquashFS systembase on ubiblock. A 64 MiB volatile overlay
provides writable runtime state; persistent userdata is not implemented.

The normal runtime has exercised:

- Linux CIP 6.12.111-cip32 plus separately pinned rt21 and systemd 259.5.
  This is not an official combined CIP RT release.
- NAND kernel/base readbacks, factory boot-region preservation and
  SquashFS-to-systemd root handoff. Linux UBI maintenance and internal SD
  writes are enabled; factory boot and BBT regions remain protected.
- Wired Ethernet, physical USB diagnostics and power-key input. Electrical
  poweroff, button wake and full suspend remain unfinished.
- GPS UART/power sequencing, local-only gpsd, privacy-proxy refresh and an
  acknowledged 31-satellite RAM-assistance upload. No navigation fix or
  improved time-to-first-fix result is claimed.
- Packaged boot/shutdown sounds. Sound playback has been audible and correct
  in testing, but NAND-backed startup has also exhibited underruns;
  buffering and startup latency remain work.
- Read-only PMIC control/DVS inventory matching factory initialization.
  CPU frequency remains 800 MHz; regulator transitions and 1 GHz operation
  are not qualified.

Complete A/B kernel and base hashes were checked after the latest runtime
kernel update. Slot A and both bases were unchanged; failed-unit count,
NAND ECC errors and kernel taint were zero.

## Diagnostic hardware qualification

Separate opt-in profiles have qualified input mappings for Perkins,
function, media, scroll and cursor-routing keys, plus selector positions.
Read-only battery telemetry, vibration, USB-host hub/adapter enumeration and
removable-SD insertion/removal have been exercised. These results do not mean every diagnostic driver is
enabled in the normal runtime or that an accessible user interface exists.

A bounded internal-SD filesystem test wrote and verified 64 MiB across an
unmount/remount, retaining the existing partitions. External SD testing was
read-only. Device-only suspend callbacks have been exercised, but not actual
CPU sleep, late/noirq suspend, wake sources or power-loss behavior.

Linux and U-Boot software BCH8/512 agreed on parity, and injected RAM errors
of one through eight bits per sector were corrected. Standard fastboot RAM
download/boot passed packet-boundary tests. Unsupported flash/erase requests
were rejected. Fastboot is not a general persistent-flashing interface.

## Boot performance

The persistent bootloader now uses aligned word FIFO reads. A comparable
host-timed software reboot to working USB shell improved from 121.476 to
107.461 seconds. This includes shutdown and console handshake, not a measured
physical power-on interval. Linux corrected 4 MiB NAND reads improved from
1.993 to 1.145 seconds after its word-transfer change.

Earlier hardware-timer, instruction-cache and partial-page loader experiments
remain separately qualified RAM tests. They are not all incorporated in the
persistent loader. Its inherited internal timer is unsuitable for performance
claims; the figures above use host timing or Linux timing as appropriate.

See [boot performance](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/boot-performance.md)
for measurements, working-set limitations and the CE comparison. A
sub-30-second total boot has not been demonstrated.

## Remaining limitations

The optional Wi-Fi profile has qualified cold firmware startup, native SDIO
notifications, 256 normal command/reply cycles across sequence wraparound, and
three consecutive passive surveys without resetting the radio. There is no
Linux wireless network interface, association, encryption-key handling or packet
TX/RX support yet. Redundant scan notifications and firmware redistribution
remain unresolved. The default runtime does not enable the diagnostic driver.
See the [Wi-Fi guide](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/wifi.md)
and its linked qualification record.
Linux braille, accessible userspace, full power management and coordinated
A/B updates remain incomplete. Both systembase slots are capped at
199.926 MiB. No power-removal or long-duration endurance qualification is
claimed, and the internal SD has not been repartitioned.

Development images expose an unauthenticated root shell over physical USB.
Maintenance SSH requires an operator-provisioned public key. Service-isolation
smoke tests are not a security audit. These images are not for everyday or
security-sensitive use.

## Build and reproducibility evidence

Kernel, U-Boot and userland use source-built OE-Core GCC 15.3; userland uses
the OE glibc 2.43 sysroot. Native amd64 and ARM64 builds run in pinned Docker
environments without an external Arm compiler archive.

Ten selected payloads previously matched bit-for-bit across native amd64
and ARM64 builders. The [cross-host comparison](cross-host-validation.md)
records the exact tested revisions and scope. Later GPS, runtime-storage,
NAND-read, PMIC and Wi-Fi changes do not inherit that reproducibility result.
No new clean-cache cross-host comparison is claimed for this checkpoint.

Unit/native tests cover image parsing, memory overlap, write guards, input
mappings, GPS framing/aiding, metadata and publication boundaries. CI tests
both build-host architectures, audits pinned layer sources/docs, parses
metadata and resolves target graphs; it does not qualify device behavior.
Builds and CI never access USB, flash NAND or modify device storage.

The current committed-input check passed 3,120 tasks with existing caches,
without local-layer overrides. The normal NAND kernel bundle, SquashFS base
and maintenance CE carrier matched the preserved hardware-tested artifacts
byte-for-byte. New diagnostic target graphs also resolved. This verifies
committed-input coverage, not an independent clean-cache rebuild.

An all-target CI check exposed a legacy-kernel provider conflict after the
runtime became the default. The legacy kernel now has an isolated package
and source namespace while retaining its bundle deploy paths. The full target
graph passed locally; a pinned build of the NAND pair and optional fastboot
RAM bundle passed 3,148 tasks. NAND kernel/base hashes were unchanged.

The [kas manifest](../kas/h432b.yml) is authoritative for current layer pins.
Fixed identities, timestamps and cache reuse alone do not prove reproducibility.

## Further reading

- [Build architecture](architecture.md)
- [Boot roles and load addresses](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/boot-contract.md)
- [NAND layout and qualification](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/nand.md)
- [Installation prerequisites and remaining gaps](https://github.com/highenergymagic/openh432-tools/blob/main/docs/installation.md)
