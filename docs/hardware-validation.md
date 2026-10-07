# Hardware validation records

Recorded on 2026-10-07 on one H432B. Artifact hashes identify tested images,
not downloads or guarantees for later builds. See the [support matrix](status.md)
for deployment scope.

## Integrated runtime build

The default NAND composition includes the shared keyboard/selector, battery,
USB-host and removable-SD implementations. The systembase includes the
explicit bounded vibration command; it does not start the motor automatically.
External SD retains its read-only guard. Suspend and charging control remain
outside this integration.

The pinned amd64 builder completed all 3,273 tasks for the normal kernel
bundle and separate systembase using local-layer inputs. Artifact inspection
confirmed the input, battery and onboard-hub driver symbols, board nodes and
required built-in configuration; suspend was disabled. The systembase package
manifest and root filesystem contained the vibration command.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| NAND kernel bundle | 6,430,720 | `d964fcf8625d8f1c189b92163eb82428e0bbecd06e49d1449bb73e33e9acc378` |
| Separate systembase | 31,817,728 | `1bec586a3262c3f30281af949268a548fbb80f6948b34604eb2e1b11b2e577a1` |

The build/layer suites passed 307 tests; host tools passed 14 Rust tests,
73 Python tests and nine optimized-Python checks. Source and documentation
audits passed for all five repositories.

These artifacts have not been installed or qualified together on the device.
Earlier isolated peripheral tests retain only their documented scope.
This build does not establish clean-cache or cross-host reproducibility.

## FM

The NAND runtime identifies the internal Si4702-C19 and exposes standard
V4L2 tuning, signal strength and stereo status through `/dev/radio0`.
A muted 206-point scan from 87.5 to 108 MHz had exact frequency readbacks.
Weak peaks near 90.1 and 94.1 MHz were corroborated by the operator as local
broadcast frequencies. No stereo indication was observed.

The optional `h432b-fm-check` client provides muted checks and scanning,
plus an explicit bounded listening mode. The codec's analogue route powered
up during a ten-second test and its mixer baseline was restored afterward,
but audible FM output was not confirmed. RDS is unavailable on this chip;
hardware seek, suspend and production audio routing remain unfinished.

The kernel bundle SHA-256 was
`cce985f4bb928c739d99473d48630b61d55287ac362835882bab1da14d9f19a3`.
It was built in the pinned container, installed into slot B
and verified by full readback; slot A, systembase and factory loader were
unchanged. These results do not establish cross-host reproducibility for
this revision. See the [FM interface reference](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/fm.md).

## Bluetooth

A NAND-installed kernel and separate systembase established communication
with the internal CSR controller over UART0 BCSP at 1,382,400 baud, 8E1.
With manual factory-derived radio configuration and recovered device identity
applied to volatile controller memory, testing with a Noxgear 39g passed:

- BR/EDR discovery, legacy pairing/bonding and SDP service discovery.
- Ten L2CAP echo exchanges, with ten replies and no loss.

The kernel bundle SHA-256 was
`1a6c2ec65d7df5dc2789d1e20821d57845a8c2906035b757c20cedfabcdbde44`;
the separate systembase SHA-256 was
`2d7a3a8c53582192b82579de91e87b7f2b0c07ab497b12b519b3431ea2a97f13`.
Both slot-B writes passed full readback verification; slot A and factory
boot regions were unchanged. These were local-layer builds, not an
independent clean-build or cross-architecture reproduction test.

The packaged transport service remains disabled. Automatic factory
initialization, persistent identity/bond provisioning, repeat-boot Bluetooth
qualification, audio playback and power management are unfinished.
Controller-reset testing also exposed HCI timeout/attachment warnings;
the complete startup/shutdown lifecycle is not qualified.
See the [Bluetooth guide](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/bluetooth.md).
No factory binaries, device identities, pairing keys or private test logs
are included in these repositories.

## Wi-Fi

The NAND-installed station driver completed WPA2-PSK/CCMP association, DHCP,
disconnect/reconnect and two normal NAND boots without a recovery upload.
With Ethernet disabled, two 2,689,160-byte SSH downloads and one upload
matched the source SHA-256. A subsequent 60-packet Internet ping test had no
packet loss. The configured NZ regulatory domain survived an AP advertising
a different country. Driver service faults, CCMP integrity failures, TX
failures and kernel taint were zero.

Qualified artifact SHA-256 values:

- Kernel bundle: `3285150959a3013ead008552daca86bc4eb2545c63ff74264c089840b645e495`.
- Separate systembase: `5572f5e057d78635dae5ffbbaf51ddc0a44882bb5b6800e05c61550b7f8ebe22`.

A build from pinned public Git inputs, without local-layer overrides, completed
3,199 tasks and reproduced both installed artifacts byte-for-byte on the same
build host with existing caches and the same private firmware input. This is
not an independent clean-cache or cross-architecture reproducibility result.
The tested source composition used hardware-layer commit
`a32ff5e38e7ce8e4f8a6e248fd85d7688352c495`, OS-layer commit
`4d4220f0977a3ef911631acac9bc4de91e3d1682` and build commit
`aadb0b680f7edc5b0e48fba94a6ec4101efea441`.
Documentation-only successors retain that qualification scope.


The profile remains limited to WPA2-Personal/CCMP, passive scanning and fixed
1 Mb/s TX. Roaming, PMF, WPA3, power saving and long-duration reliability are
not qualified. Network credentials are operator-provisioned, never published,
and currently disappear with the volatile writable overlay on reboot.
See the [detailed Wi-Fi validation record](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/wifi-qualification.md).
