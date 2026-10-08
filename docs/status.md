# BSP support matrix

This matrix describes the pinned OpenH432 development composition for H432B.
It is not a production support commitment or qualification of other Sense
models. The [kas manifest](../kas/h432b.yml) defines exact source revisions.

**Runtime** means included in the normal NAND composition. **Diagnostic**
means an opt-in profile or tool. **Partial** means incomplete integration or
qualification. Hardware tests describe one qualification device.

## Platform

| Component | Availability and limits |
| --- | --- |
| CPU / memory | S5PV210, 256 MiB DRAM, 800 MHz; DVFS/1 GHz unqualified |
| Kernel | CIP 6.12.111-cip32 plus separately integrated rt21; not an official combined CIP RT release |
| Bootloader | U-Boot 2012.10 behind retained factory first stage/EBOOT |
| NAND root | Persistent A/B selection, minimal initramfs, slot-matched SquashFS systembase via ubiblock |
| Writable state | 64 MiB volatile overlay; no persistent userdata |
| Updates | Redundant boot state, persistent attempt limits, exhausted-slot fallback and automatic healthy-boot acknowledgement; no signed bundle installer or hang watchdog |
| Build hosts | Native Linux amd64 and ARM64 Docker, OE-built target toolchain |

## Hardware interfaces

| Interface | Integration | Verified scope / principal limitation |
| --- | --- | --- |
| NAND | Runtime | BCH8/512, UBI read/write, full image readback; factory prefix/tail protected |
| Internal SD | Runtime | Bounded 64 MiB filesystem write/readback; no repartitioning or power-loss qualification |
| Ethernet | Runtime | Networking, DHCP and SSH; one deep-sleep recovery cycle with verified bidirectional transfer |
| Wi-Fi | Runtime, external firmware required | WPA2-PSK/CCMP, DHCP, transfers/reconnect; post-sleep reassociation/ICMP; passive scan, fixed 1 Mb/s TX |
| Bluetooth | Partial runtime | Manual setup, discovery/pairing/L2CAP and sleep-time parameter retention; service disabled, no audio backend |
| FM | Runtime | V4L2 tuning and corroborated signal peaks; audio/stereo unverified, no RDS |
| GPS | Runtime | NMEA, gpsd and RAM-assistance acknowledgements; no fix demonstrated |
| Speaker audio | Runtime | Playback, system cues and playback started after resume; NAND-startup underruns observed |
| Braille | Runtime, BRLTTY enabled | Linux eight-dot output, console reading, typing, Backspace/Enter, scrolling and cursor routing; BRLTTY chords operator-confirmed, including learn mode; exhaustive routing/chord coverage unqualified |
| Power key | Runtime | logind deep suspend; power-only wake and restoration of the interactive session |
| Keyboard / selectors | Runtime | Mappings and selected evdev tests; provisional ABI, BRLTTY chord handling; no keypad-lock or notification policy |
| Battery | Runtime | Read-only telemetry; no charging control or exact-model qualification |
| Vibration | Runtime command, explicit invocation | Confirmed bounded pulse; no production haptics interface |
| USB host | Runtime | Earlier diagnostic three-port hub/adapter enumeration; serial payload unqualified |
| External SD | Runtime, read-only | Earlier diagnostic reads/hotplug; writes and mechanical write protection unqualified |
| PMIC / suspend | Partial | Deep sleep, braille supply removal/restoration and Ethernet recovery tested; Wi-Fi reassociation, Bluetooth parameter retention and post-resume audio tested separately; RTC sleep-time accounting tested; full peripheral resume and electrical shutdown incomplete |
| Other peripherals | Unqualified | No support claim for VGA or unlisted hardware |

Runtime inclusion does not extend earlier diagnostic qualification to a new
combined image. Artifact-specific checks are recorded in [hardware validation](hardware-validation.md).

Use the [hardware reference](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/index.md)
for configuration and the [target catalogue](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/targets.md)
for diagnostic prerequisites.

## Security and deployment limits

The built-in tty1 console automatically logs in as the unprivileged `user`
account. It does not grant root access or enable password-based SSH.
Development images also expose an unauthenticated physical USB root console.
SSH requires an operator-provisioned public key and verified host key; identity
and credentials are volatile. No private credentials, proprietary radio
firmware or per-device identities are published in the generic composition.

Accessible applications, persistent userdata, full power management and
a signed update installer remain incomplete. These images are not for everyday or
security-sensitive use. See the [installation guide](https://github.com/highenergymagic/openh432-tools/blob/main/docs/installation.md)
for conversion and recovery gaps.

## Validation

- [Hardware records](hardware-validation.md): scope, artifact hashes and limitations.
- [Cross-host comparison](cross-host-validation.md): ten matching target payloads
  at explicitly recorded historical revisions.
- [Build hosts](build-hosts.md): clean-workspace and comparison procedures.
- [Boot performance](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/boot-performance.md):
  measured timings; no sub-30-second boot claim.

CI tests source contracts, audits sources/docs, parses metadata and resolves
target graphs on both host architectures. It does not build every image or
qualify hardware. Compilation and fixed inputs alone do not prove reproducibility.

<a id="wi-fi-checkpoint-2026-10-07"></a>
<a id="bluetooth-checkpoint-2026-10-07"></a>
<a id="fm-checkpoint-2026-10-07"></a>

Historical checkpoint links resolve here. Artifact-specific results are in
[hardware validation](hardware-validation.md).
