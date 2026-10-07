# Battery telemetry qualification image

The current main-branch manifest pins the hardware and OS layers containing
the opt-in battery telemetry image. Select it explicitly with the commands
below; the default targets are the separate NAND runtime kernel and base.

Build using the pinned container and Git inputs:

```sh
python3 scripts/bsp.py checkout
python3 scripts/bsp.py fetch openh432-battery-test openh432-systembase-b openh432-maintenance-ssh
python3 scripts/bsp.py build openh432-battery-test openh432-systembase-b openh432-maintenance-ssh
```

Native amd64/ARM64 host selection applies. Do not use `--local-layers` when
validating committed pins. Artifacts are in
`work/build/tmp/deploy/images/h432b/`:

- `openh432-battery-test.img`: RAM-launch kernel and minimal early handoff.
- `openh432-systembase-b-h432b.rootfs.squashfs-xz`: separate NAND base image.
- `openh432-maintenance-ssh.tar`: non-secret volatile-overlay test payload.

The kernel bundle uses an already provisioned slot-B NAND root. It is not a
full root filesystem, installer or NAND update. Building a new systembase
does not install it. Build commands never open USB or deploy firmware.

## Battery interface

`/sys/class/power_supply/h432b-battery` exposes read-only capacity, status,
voltage_now, temp, current_now and current_avg. Units follow Linux power_supply:
microvolts, tenths of degrees Celsius, and microamps. Negative current denotes
discharge. Polling is every five seconds; failed/stale measurements are not
reported as zero. Changes generate standard notifications.

The driver never programs charging, calibration, EEPROM, PMIC rails or
suspend. Exact gauge model, independent sensor calibration, active charging,
AC-source behavior and low-battery policy remain unqualified. Status still
uses the recovered GPIO inputs; 100 percent alone does not imply Full.

A root-only `registers` snapshot under the battery-inventory platform device
provides fixed read-only measurement and parameter-shadow windows for analysis.
See the [hardware documentation](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/973de263c6f6b45915bfabde3cf591de2bc8d07f/docs/battery.md).

## Ethernet maintenance access

The new systembase includes a key-only service gated on an operator-provisioned
authorized-key file. The separate payload was qualified in the installed
system's volatile overlay without installing the new base. Password login
and TCP forwarding are disabled; no credentials are shipped. Host keys are
generated on the device and must be pinned through a trusted local console.
Current identities are volatile, not persistent production provisioning.
See [maintenance SSH](https://github.com/highenergymagic/meta-fractalmicro-openh432/blob/4beb568a5a4f1406d31481b855e60ec3e8530409/docs/remote-access.md).

## Hardware evidence

The RAM boot passed standard sysfs and udev checks for all six properties.
A verified Ethernet SSH session survived physical USB removal. The USB-present
input deasserted, status became Discharging and current became negative.
Observed gauge readings were about 4.18 V before removal, 4.14–4.15 V afterward,
27 degrees C and approximately 240–360 mA discharge during the test.
Systemd remained healthy, UBI read-only and the kernel untainted.

The hardware/OS suites passed 114 tests. Compiled C tests cover 2,424 status
matrix cases, 65,534 signed-current cases and additional conversion/error
boundaries. The full kernel/systembase build passed 3,025 tasks.
This is RAM-kernel and runtime-payload qualification, not a NAND installation
or new cross-host bit-for-bit reproduction claim.

A subsequent non-local-layer build resolved the committed pins and passed
all 3,026 tasks using existing build state. The kernel bundle, systembase
and SSH payload each byte-matched the preserved development-build artifact.
This checks committed-input coverage; it is not a fresh-cache rebuild.
