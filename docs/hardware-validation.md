# Hardware validation records

Qualification records for one H432B. Each section applies only to its identified
artifacts, not every later image. Superseded limitations are retained where they
describe a recorded test; the support matrix describes current integration.
Artifact hashes identify tested images, not downloads. See the [support matrix](status.md)
for deployment scope.

## Audio capture and jack handling

The standard NAND audio driver exposes duplex 44.1 kHz, stereo, S16_LE PCM.
The installed kernel bundle is 9,072,640 bytes, SHA-256
`fb3989394e61c03f3dd24228681e12159314ca223b3cec3588b2cd2647db26d4`.
Systembase is 42,700,800 bytes, SHA-256
`01ae12b6528b2a18d4cde2c44097ac64b4c8d7327027d5a6d8426078eb9cd4a1`.
Both slot-B images passed NAND readback; slot A and the factory loader were
preserved. The final kernel passed a software-reboot NAND boot and automatic
boot-health confirmation.

On the installed image, both empty sockets reported unplugged without a
register adjustment. A three-second recording returned 132,300 stereo frames
in approximately 3.12 seconds, with non-zero input and no clipped samples.
After close, microphone bias was off, both PCM devices were closed and both
PDMA enable counts were zero. Braille, local login and Wi-Fi initialization
remained active; there were no failed units or kernel taint.

Acoustic and simulated jack-transition tests used the preceding kernel
`5c772f2b681f87897872d3128640ba5f84db8a73e5b1add09821c9fd79ba1d06`,
with the same audio driver and the no-pull setting applied explicitly.
Concurrent playback/capture recovered 600, 1,000 and 1,500 Hz tones in their
expected time windows. Repeating with analogue outputs muted removed those
peaks. A weak pull-down on the empty headphone detector exercised its IRQ and
speaker-amplifier gating; restoring no-pull re-enabled the amplifier.
The final device tree incorporates that no-pull configuration.

The pinned default build completed all 3,480 tasks. Hardware-layer tests passed
250 cases with one unrelated skip, including zero-fuzz audio patch application
and compiled tests of the actual speaker-gating callbacks.

Limitations: capture has an initial settling transient of roughly one second.
These tests do not qualify physical jack insertion, headphone listening,
external microphone audio routing, calibrated gain, stereo microphone
separation, or an open stream across suspend. Jack IRQs are configured as
non-waking; a new physical suspend/jack test was not performed.

## Wi-Fi runtime initialization

The standard NAND kernel excludes the manual transport, power, firmware,
event and command experiment interfaces. Systembase requests one driver-owned
initialization operation after firmware becomes available. The diagnostic
kernel explicitly enables the separate controls.

Tested artifacts:

- Kernel bundle: 9,070,592 bytes, SHA-256
  `669c8a42b3bcc4f231309603524ac0faa7ebafedef756dcd3799efa35cc78ea2`.
- Systembase: 42,700,800 bytes, SHA-256
  `01ae12b6528b2a18d4cde2c44097ac64b4c8d7327027d5a6d8426078eb9cd4a1`.

Both images were installed into inactive slot A and verified by full NAND
readback; slot B and the factory loader were preserved. The first software
reboot from the preceding LED image reached the bootloader but did not return
a Linux endpoint. The operator reported an unpowered braille display.
Plain Reset then booted slot A successfully. The cause of the warm-reboot
failure is unresolved; this record does not claim reboot reliability.

The NAND runtime passed:

- Absence of all former writable experiment attributes.
- Service restart without replacing the network interface.
- NZ regulatory configuration and passive scanning (20 reported BSSs).
- WPA2-PSK/CCMP association, DHCP and three interface-bound gateway pings
  with no packet loss.
- Absence of the old Wi-Fi bring-up log messages.
- Braille/local-login services, boot-health acknowledgement and zero kernel
  taint; the six AMI603 channels remained readable.

No throughput, suspend/resume or long-duration radio retest was performed.
Network credentials remained private and were provisioned only into the
volatile device overlay.

The normal build passed 3,480 tasks with diagnostics disabled; the explicit
diagnostic kernel passed 913 tasks with diagnostics enabled. Hardware-layer
tests passed 246 tests with one skip; the OS-layer suite passed 81 tests.
The new initialization code passed checkpatch. These are build and device
checks, not an independent cross-host reproduction.

## RTL8712 LED outputs

The normal NAND kernel exposes both RTL8712 LED outputs through the Linux
LED class. It was installed into inactive slot B; the slot-A motion-sensor
kernel and both systembase volumes passed preservation readback. No
bootloader or factory-region write was performed.

Tested artifacts:

- Kernel bundle: 9,074,688 bytes, SHA-256
  `eb24ef0c000d5ed56da6dbc761a36c195e4282ac86f779aa13f4c0a9ce830b1a`.
- Unchanged systembase: 42,700,800 bytes, SHA-256
  `9830fefd2ddaff030bc2e1d0efa421a0da52ff54eb82f111b63e1c87227da89f`.

A software reboot reached the interactive system. Both LED class devices
registered, all six AMI603 channels remained readable, no services were
failed and kernel taint was zero. With the Wi-Fi interface up, the sequence
off/off, on/off, on/on, off/on, off/off completed without LED callback errors.
Each callback compares the full register readback to the requested value.
Both outputs were left off.

This qualifies register access, not visible light output or front-panel
position. No observer confirmed colour or brightness. LED suspend/resume,
Bluetooth/GPS/power indicators and radio traffic during LED activity were
not tested.

The standard build passed 3,480 tasks. The pinned-container hardware-layer
suite passed 242 tests with one skip, including the compiled LED setter
across 1,024 register/input combinations and injected error paths. The new
driver passed checkpatch without errors or warnings. This build was not
independently reproduced on another host.

## AMI603 motion sensor

The direct-mode IIO driver was built into the normal runtime kernel and
installed in inactive NAND slot A, with full kernel/systembase readback.
Slot B and the factory loader were preserved. A software reboot reached the
interactive system, automatic boot-health acknowledgement passed, and kernel
taint remained zero.

Tested artifacts:

- Kernel bundle: 9,068,544 bytes, SHA-256
  `e0bebd101c470de0d21d48cf6464e66c877d3d9ad7a8ef23402aed9e980bd32d`.
- Systembase: 42,700,800 bytes, SHA-256
  `9830fefd2ddaff030bc2e1d0efa421a0da52ff54eb82f111b63e1c87227da89f`.
- Retained loader: the fixed-parameter BCH carrier documented below.

The sensor passed its identity check and provided valid factory sensitivity
and acceleration-origin values. All six raw channels returned readings.
Stationary acceleration was approximately 1 g; magnetic channels were not
saturated. Operator rotation/tilt produced changing readings which settled
afterward. This is transport and response qualification, not calibrated
heading accuracy or a verified board-axis transformation.

The default build completed 3,480 tasks. Hardware-layer tests passed 238 tests
with one skip in the pinned container; kernel style checks reported no errors
or warnings for the new driver. No new cross-host reproduction is claimed.
One operator-triggered power-button deep-sleep/wake cycle restored readings
on all six channels without a reboot. The recorder continued, kernel taint
remained zero, and braille and boot-health services were active. Repeated-cycle
reliability and independent electrical measurement of the sensor rail remain
unqualified.

## Fixed-parameter BCH loader

The standard A/B loader specializes upstream software BCH for M=13, T=8.
The installed CE carrier is 403,551 bytes, SHA-256
`9e8ae2f669f3d0f56282cbfe57bb987abd9e2dade898f0f49e10a2c4187cf68a`.
Factory EBOOT, the slot kernels and systembase images were not replaced.

Recovery-assisted launch and an ordinary NAND software reboot passed automatic
A/B health acknowledgment, BRLTTY/local-login service checks, network/input
properties and maintenance-console checks. Kernel taint remained zero; early
sound completed without reported underruns. This does not retest suspend,
radio throughput or long-term error recovery.

With the same 9,054,208-byte kernel bundle and instrumentation, the ordinary
NAND loader interval fell from 34.724 to 30.118 seconds (13.3%). BCH calculation
fell from 21.618 to 17.093 seconds; FIFO and CRC durations were unchanged.
Recovery-assisted launch measured 30.134 seconds. These are loader intervals,
not power-on-to-ready measurements.

The generic instrumented comparison carrier was
`38d944bcef15a5423d4adb86f7d6fa45c178e4a3b372a0d19591d0a9fff5a7b1`.
Both used kernel
`52860b022590ee2eaba786c3a71c225a8390434ee961d249bcea7aaea50842d2`
and slot-B systembase
`9830fefd2ddaff030bc2e1d0efa421a0da52ff54eb82f111b63e1c87227da89f`.

The pinned build completed 948 tasks. The hardware-layer suite passed 234 tests
with one optional test skipped. A build-time native test compiled the fetched
BCH implementation in generic and fixed forms and compared 8,448 corruption
cases: parity equality, decoding equivalence, and one-through-eight-bit repair
across data/parity/mixed errors. NAND parity layout, correction strength and
image-integrity checks are unchanged. No new cross-host reproducibility result
is claimed.

### Pinned source composition

The default build from these published layer pins completed 3,480 tasks
without local-layer overrides. All three output hashes matched the installed
carrier, kernel and systembase listed above.

| Repository | Commit |
| --- | --- |
| Hardware layer | `27d4dbd3b7a4d2b2f6087875ea9e88bcb922fe47` |
| Distribution layer | `fa154f8502da8046d00d468a00a0e0897016cfbb` |
| Assets layer | `04f8a88bf9b941fb778f87f575b918e8887a5501` |

This was a same-host cached composition check using the same private stock
firmware input and NZ radio setting, not a clean-cache or cross-host rebuild.
The combined layer/build suites ran 361 tests with one optional test skipped.
Host tools passed 14 Rust tests, 79 Python tests and nine optimized-Python
checks. Publication audits exclude private firmware, device evidence and keys.

## Early maintenance USB console

The standard coldplug policy queues the built-in USB tty before bulk device
enumeration. Two consecutive normal NAND software reboots into slot B passed
automatic boot acknowledgment, BRLTTY/local-login activation, input/network
properties and internal-MMC link checks. Static group resolution and the full
all-device pass remain enabled.

Systembase SHA-256:
`9830fefd2ddaff030bc2e1d0efa421a0da52ff54eb82f111b63e1c87227da89f`.
The kernel and carrier match the gzip-systembase record below. Slot-B full
readback passed; the other slot and kernel images were not replaced.
The pinned build completed 3,387 tasks and 81 OS-layer tests passed.

USB device readiness occurred at 36.4–36.5 seconds after Linux entry and the
maintenance shell at 40.3–40.4 seconds, compared with approximately 50–52 and
53–54 seconds previously. BRLTTY input remained around 43 seconds.
The repeat test deferred SSH setup until after startup to reduce observer
interference. No overall multi-user speedup or new cross-host reproducibility
claim is made; physical hotplug and suspend were not retested.

## Gzip systembase

The standard systembase uses gzip SquashFS. Two consecutive normal NAND
software reboots into slot B passed automatic health acknowledgment,
BRLTTY/local-login activation, input/network properties and internal-MMC
persistent-link checks. Early sound completed without reported underruns.
The XZ slot-A root and both kernels were preserved; slot-B readback matched.

| Tested artifact | SHA-256 |
| --- | --- |
| A/B CE carrier | `a74bff3db78c67db54011a6a030b524cc9757f69ee27fd4eb4cbd5bff0369cd8` |
| NAND kernel bundle | `52860b022590ee2eaba786c3a71c225a8390434ee961d249bcea7aaea50842d2` |
| Systembase | `06f0c2f7349a6387253296c3e4da5ee7806a3a64a94baf927c0df58280a1314b` |

The systembase is 42,700,800 bytes. The final gzip-only build completed 3,387
tasks and matched the tested comparison output byte-for-byte. The comparison
build also reproduced the preceding XZ payload exactly. This is a same-host
comparison, not a new independent clean-cache or ARM64 reproduction.
Checks passed 81 OS-layer and 43 build-orchestration tests.

BRLTTY virtual input appeared at 42.9–43.4 seconds after Linux entry, compared
with 55.6 seconds for XZ; selected-root verification increased from 16.7 to
19.4 seconds. D-Bus startup duration fell from 14.8 to 3.0–3.2 seconds.
Multi-user activation was 53.2–53.7 seconds and included the development USB
console. See the [performance reference](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/boot-performance.md)
for scope. Physical hotplug and suspend/resume were not retested in this run.

## Device coldplug policy

The H432B systembase uses device-only coldplug, four udev workers and a masked
SmartMedia MTD probe. It retains all device subsystems and normal hotplug
rules. Two consecutive normal NAND software reboots into slot A passed
automatic boot-health acknowledgment, BRLTTY/local-login activation, input
and network property checks, and internal MMC persistent-link checks.
The early startup-sound helper completed on both boots; this test did not
repeat physical USB/SD insertion or subjective sound checks.

| Tested artifact | SHA-256 |
| --- | --- |
| A/B CE carrier | `a74bff3db78c67db54011a6a030b524cc9757f69ee27fd4eb4cbd5bff0369cd8` |
| NAND kernel bundle | `52860b022590ee2eaba786c3a71c225a8390434ee961d249bcea7aaea50842d2` |
| Systembase | `453547c7d1b6b8d095584ba911ee3592df3423fac4568dfe5299f36112488f7f` |

The 33,562,624-byte systembase passed full NAND readback; slot B and both
kernel images were preserved. The pinned build completed 3,387 tasks and
81 OS-layer tests passed. Cross-host reproduction was not repeated.
Coldplug took 14.3–14.9 seconds and multi-user activation occurred at
56.2 seconds after Linux entry. These samples show a modest improvement
over the preceding image, not resolution of all startup latency.
See the [performance reference](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/boot-performance.md)
for baseline and measurement scope.

## Boot-state volume probe exclusion

The standard systembase excludes UBI volumes named `bootstate_a` and
`bootstate_b` from generic persistent-storage filesystem probing. Testing
confirmed that both environment volumes skip the probe while an ordinary
systembase volume continues to be probed. Device creation and boot-health
validation remain enabled.

Two consecutive normal NAND software reboots into slot A automatically
acknowledged their persisted attempts without a manual service retry.
Both allowances returned to three; no UBI exclusive-access error or kernel
taint was observed. Startup audio completed and BRLTTY/local login were active.
The previous slot-B images were preserved by full readback comparison.

| Tested artifact | SHA-256 |
| --- | --- |
| A/B CE carrier | `a74bff3db78c67db54011a6a030b524cc9757f69ee27fd4eb4cbd5bff0369cd8` |
| NAND kernel bundle | `52860b022590ee2eaba786c3a71c225a8390434ee961d249bcea7aaea50842d2` |
| Systembase | `ad7d5f5a9b468bc3d8d53241d478e67d7749d439a458af64fc6151b1dd45fde9` |

The systembase build completed 3,369 tasks; 77 OS-layer tests passed.
This qualification does not cover arbitrary third-party readers holding an
environment volume open, power loss during an update, or cross-host
reproduction of these artifacts.

## Managed A/B boot and interactive console

The standard composition includes the A/B selector, shared bootstate checker,
root-handoff slot selection and enabled boot-success service. Both slots
contain the following kernel/systembase pair; full readback hashes matched.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| A/B CE carrier | 401,895 | `2f5c3868da699b83ce0e1977f4de880a6d12174369aeb01a390f7faede9f381d` |
| NAND kernel bundle | 6,432,768 | `466567a7268d8a48392e52501b92999eef09a0f7f51bcc7bf9cb39ed18578303` |
| Systembase | 33,562,624 | `df9d8e763e2e7461eb7b6fd7353bef3dd6f9320cfa85099ef95d88803f6be45a` |

Slot A booted after recovery installation. With A deliberately exhausted, a
plain Reset without a host upload selected B and mounted its matching base.
On both boots, the loader persisted the attempt before launch and
`FMMarkBootSuccessful.service` automatically restored the booted slot's
allowance after its health interval. BRLTTY and tty1 were active without
restarts. Both slots were subsequently left eligible.

Linux/U-Boot redundant-state interoperability, serial advancement, commit
readback and stale/repeated acknowledgement rejection were checked. Offline
C vectors cover CRC/schema errors, serial wrap, exhausted slots and modeled
torn writes. They do not establish physical power-cut behavior.

An early bootstate diagnostic used a software timing source that expired
NAND programming deadlines prematurely. The corrected hardware-timer loader
repaired the UBI attachment state; kernel/base hashes remained unchanged.
One additional 128 KiB pool block was retired and its bad marker retained.
Subsequent scans reported no corrupted PEBs. The timer dependency is covered
by a regression test.

The pinned amd64 container built 3,444 tasks with local-layer inputs.
A subsequent build using the published layer commits, without local overrides,
completed all 3,444 tasks from cache and matched all three hashes above.
Checkpoint checks ran 327 build/layer tests (one optional check skipped),
14 Rust tests, 73 host-tool Python tests and nine optimized-Python checks.
Source and documentation audits cover all five repositories.
This is compilation and device qualification, not a new independent clean-cache
or cross-host reproduction. A signed update installer, watchdog recovery of
a hung kernel and physical power-cut qualification remain outstanding.

## Local console login

The standard NAND systembase includes an instance-specific tty1 autologin
policy for the unprivileged `user` account. A normal NAND boot reached a
shell with UID/GID 1000, working directory `/home/user` and zero effective
capabilities, without a host command starting the getty or BRLTTY.
Both services reported active with zero restarts. Both root and user
passwords remained locked; the key-only SSH policy was unchanged.

Systembase SHA-256:
`883778c5ca86f8db937a59a6d85608fb717ff5c0e9b62752ead68d8aababd480`.
Slot-B full readback passed and slot A was preserved. The kernel and factory
loader were not replaced. The manifest-pinned cached build matched this
payload; this does not establish a new clean-cache or cross-host reproduction.
The operator confirmed `whoami` returned `user` on the braille console,
and reported working Backspace, Enter and cursor routing. Later operator
checks confirmed the BRLTTY chords tried, including l-chord learn mode.
These observations do not establish exhaustive routing or chord coverage. The home directory remains volatile.

## Internal braille

The Linux GPIO transport exposed an exclusive 32-cell character device.
Operator checks confirmed the exact contracted startup greeting, a left-column
dot-7 extension and a full eight-dot cell beside a six-dot “y”. A competing
open was rejected as busy, and a short frame was rejected without replacing
the displayed pattern.

The standard systembase packages pinned BRLTTY 6.9.1 and the H432B backend.
The operator confirmed virtual-console text, typing at the login prompt
and scroll-key navigation with the installed NAND system. Automatic service
startup was verified on a subsequent normal NAND boot without a host start
command, with zero service restarts. The local-console qualification above with the
same kernel includes cursor routing; exhaustive routing and chord coverage remain unqualified.
The GPIO direction callback includes interrupt-mux handling; Ethernet DHCP
and SSH were checked after correcting that integration.

The kernel bundle and systembase were installed in slot B and passed full
readback verification; both slot-A hashes were unchanged.

| Artifact | SHA-256 |
| --- | --- |
| NAND kernel bundle | `1a85f84328b574771a89cbda62b9e8f800c4ff017bd13378c3b5aab190dacb21` |
| Systembase used for operator console checks | `55cbe94995dd5a58c8265f43ce13bcfc816d20760fd03f6fe48e760e730cb972` |
| Installed systembase with automatic startup | `d638acfada21a46e4e6db8b99721a9b6fe2938f6733cdb153e916589b7adc070` |

The manifest-pinned build completed with matching installed artifact hashes;
this was a cached build, not an independent clean-cache reproduction.

These tests do not qualify display power management or cross-host
reproducibility for this image. See the
[braille interface](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/braille.md).

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

## Power-button deep suspend qualification

A standard NAND runtime built with local layer overrides was installed with
readback verification and booted through the retained loader using software
reboot. The separate systembase includes the logind power-key suspend policy.

Qualified artifact SHA-256 values:

- Kernel bundle: `e0d18750c9a8fa70a3812d0b1125aef158e71322dc5f57594f09bb40b8d83b75`.
- Systembase: `dc849f6c82868e010ad5c2de87f1f411e9bc8960c83fd570613c8b1c0e4ebcb8`.

One full power-button sleep/wake cycle preserved the boot ID and interactive
session, with one successful suspend and no suspend failure or kernel taint.
Ethernet recovered DHCP and verified-key SSH; a 6,508,544-byte transfer to the
device and back matched SHA-256. Wi-Fi passive scanning returned access
points after wake with no transport fault. gpsd subsequently delivered 15
checksum-valid NMEA sentences with no fix indication. Opening the FM receiver
after resume passed five muted tune/readback checks, but all signal readings
were zero; reception, audio and an FM handle held across sleep were not tested.
USB gadget and an attached USB
serial adapter re-enumerated; an uninterrupted serial stream was not tested.

Earlier runtime tests confirmed tactile braille-cell power removal and
restoration. Non-power keys and both selectors did not wake the device.
These checks do not qualify every switch position or long-duration cycling.

This image did not qualify station reassociation, Bluetooth or audio resume,
GPS assistance retention or FM reception across sleep. It exposed no RTC and
did not restore elapsed sleep time. The following records identify subsequent
RTC and peripheral tests. This local-layer build did not establish public-input
or cross-host reproduction.

### RTC elapsed-time accounting

A subsequent standard NAND kernel enabled the Samsung RTC with its separate
32.768 kHz source-clock description and disabled RTC alarm wake capability.

- Kernel bundle SHA-256: `fa4c9b60294406ff068e78d5d4679893d1e4ee3cda6325a468672751d24ee86d`.
- Systembase SHA-256: `dc849f6c82868e010ad5c2de87f1f411e9bc8960c83fd570613c8b1c0e4ebcb8`.

The RTC registered and ticked, with no wake-alarm sysfs interface. Its initial
invalid time prevented boot-time clock restoration; a trusted system clock
was subsequently written to the RTC in UTC before testing.

With systemd-timesyncd stopped, a measurement interval spanning actual
power-button deep sleep advanced 94 seconds on the host, 94 seconds on the
RTC and 93 seconds on the target wall clock. Target boot-time accounting
advanced 93.01 seconds. The approximately one-second difference is within
the sequential sampling interval; this is not an oscillator-accuracy test.

The boot ID was unchanged, suspend reported one success and zero failures,
and kernel taint remained zero. Ethernet SSH, Wi-Fi passive scanning and
the local braille console recovered. Network synchronization was restored
after measurement. Battery-removal retention, long-duration drift and
repeated cold-start initialization remain unqualified.

### Radio resume qualification

On the RTC-enabled kernel identified above, an additional power-button sleep
cycle retained the boot ID and reported two cumulative suspend successes,
zero failures and no kernel taint. A previously associated WPA2-PSK/CCMP
station automatically rejoined after wake. Two sets of four gateway pings
bound explicitly to wlan0 completed without packet loss. Sustained TCP
transfers and repeated station reconnect cycles remain unqualified.

The initialized Bluetooth controller did not retain its volatile configuration:
BCSP reported controller resets, and the local-version query timed out.
Restarting the transport restored HCI responses but exposed the controller's
default identity, not its provisioned factory identity. Bluetooth was stopped
after the diagnostic. This image did not qualify Bluetooth resume; the
separate enable-retention qualification below covers its correction.

Audio playback also failed before suspend on this kernel. An active PDMA
channel waited for an I2S request without advancing the PCM buffer; no DMA
fault was reported. This image did not qualify audio; the request-clock
qualification below covers its correction.

### Bluetooth enable retention

The standard NAND kernel with SHA-256
`b7f72d947959c207fa8f035241c282a64db5a53aacce5b05e093bcc895e2d773`
holds the Bluetooth enable GPIO high during deep sleep. The systembase remains
`dc849f6c82868e010ad5c2de87f1f411e9bc8960c83fd570613c8b1c0e4ebcb8`.

After manual factory-parameter initialization, one power-button sleep/wake
cycle preserved the boot ID and completed with one suspend success, zero
failures and no kernel taint. Bluetooth answered the HCI local-version command
without restarting or reattaching its transport. Read-only queries confirmed
that the factory identity and all five provisioned CSR parameters survived;
no BCSP controller-reset or command-timeout messages occurred.

Wi-Fi automatically reassociated using WPA2-PSK/CCMP and passed four
wlan0-bound gateway pings. Ethernet SSH and the local braille console also
remained available. These results do not qualify Bluetooth connected-peer
retention, Bluetooth audio, repeated suspend cycling or automatic factory
initialization. Audio DMA qualification is recorded separately below.

### Audio request-clock lifetime

The standard NAND kernel with SHA-256
`21f3f4232a7844a8b2e6432479d5f90ed6c8635c03474853eaa9b4f5b5e295ec`
adds a board audio-stream reference to the PDMA0 clock and corrects handling
of positive ALSA constraint results. The systembase remains
`dc849f6c82868e010ad5c2de87f1f411e9bc8960c83fd570613c8b1c0e4ebcb8`.

With both DMA controllers under automatic runtime power management, a muted
startup WAV completed successfully and its hardware sample pointer advanced.
PDMA0 and PDMA1 clock enable counts changed from zero to one during playback
and returned to zero after close. Rejecting an unsupported S32_LE stream also
released the clock reference. Kernel taint remained zero.

The boot-time startup service returned a successful player exit, but logged
two underruns during system startup; gap-free boot playback remains unqualified.

A subsequent power-button deep-sleep/wake cycle preserved the boot ID, with
one suspend success, zero failures and no kernel taint. After resume, the full
muted WAV completed with an advancing sample pointer, both DMA clock enable
counts returned to zero, and unsupported-format rejection left the clock
reference balanced. The startup-cue service then exited successfully, and
operator listening confirmed correct speed and clean playback. Braille and
local login services remained active. This qualifies playback started after
resume, not an audio stream held open across suspend or repeated-cycle endurance.

Native C tests exercise positive constraint returns, each constraint error,
clock-enable failure and reference balancing.

### Published source composition

The pinned amd64 container built the normal NAND kernel, separate systembase
and A/B carrier without local-layer overrides. With the same private stock
firmware input and NZ radio configuration, all three payload hashes matched
the installed/tested artifacts. The kernel and systembase hashes are listed
above; the carrier remains
`2f5c3868da699b83ce0e1977f4de880a6d12174369aeb01a390f7faede9f381d`.

Source revisions:

| Repository | Commit |
| --- | --- |
| Hardware layer | `6c2c0055b568fb11af789df770fbb588d4878cb8` |
| Distribution layer | `add0b848a5e238cc379996411699accfb0531a3c` |
| Assets layer | `28d0eaf0da0976e4a41b1e69ecb8c222542408de` |

The build/layer suites ran 343 tests successfully with one optional test skipped;
host tools passed 14 Rust tests, 79 Python tests and nine optimized-Python
checks. Source-index and documentation audits cover all five repositories.
This is a same-host cached public-input comparison, not a new clean-cache
or cross-architecture reproduction. Peripheral tests above retain their
individual artifact scope; combined radio/audio endurance is not qualified.
