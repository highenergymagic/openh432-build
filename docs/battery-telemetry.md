# Battery telemetry qualification image

Battery telemetry is included in the default NAND kernel. This guide describes
the optional isolated battery-test profile, which shares the same driver and
configuration. Select that profile explicitly with the commands below; the
default targets remain the separate NAND runtime kernel and systembase.

Build using the pinned container and Git inputs:

```sh
python3 scripts/bsp.py checkout
python3 scripts/bsp.py fetch openh432-battery-test openh432-systembase-b openh432-maintenance-ssh --without-wifi
python3 scripts/bsp.py build openh432-battery-test openh432-systembase-b openh432-maintenance-ssh --without-wifi
```

Native amd64/ARM64 host selection applies. Do not use `--local-layers` when
validating committed pins. Artifacts are in
`work/build/tmp/deploy/images/h432b/`:

- `openh432-battery-test.img`: RAM-launch kernel and minimal early handoff.
- `openh432-systembase-b-h432b.rootfs.squashfs`: separate NAND base image.
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
suspend. Exact gauge model, independent sensor calibration, isolated AC
transitions and low-battery policy remain unqualified. Active charging with
AC and USB connected has been observed in the NAND runtime; it does not
establish USB-only charging. Status uses the recovered GPIO inputs;
100 percent alone does not imply Full.

A root-only `registers` snapshot under the battery-inventory platform device
provides fixed read-only measurement and parameter-shadow windows for analysis.
See the [hardware documentation](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/battery.md).

## Ethernet maintenance access

The systembase includes a key-only service gated on an operator-provisioned
authorized-key file. Password login and TCP forwarding are disabled.
Host keys must be obtained through a trusted console and pinned explicitly;
identities are volatile. See [maintenance SSH](https://github.com/highenergymagic/meta-fractalmicro-openh432/blob/main/docs/remote-access.md).

## Hardware evidence

The RAM boot passed standard sysfs and udev checks for all six properties.
A verified Ethernet SSH session survived physical USB removal. The USB-present
input deasserted, status became Discharging and current became negative.
Observed gauge readings were about 4.18 V before removal, 4.14–4.15 V afterward,
27 degrees C and approximately 240–360 mA discharge during the test.
Systemd remained healthy, UBI read-only and the kernel untainted.

These are RAM-profile results, not qualification of the combined NAND runtime or
independent sensor calibration. See the hardware reference for conversion,
staleness and source-detection limits.
