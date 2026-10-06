# Battery telemetry qualification image

The power-control-bringup branch pins the hardware and OS layers containing
the opt-in battery telemetry image. The default image target remains unchanged.

Build from this checkout using the pinned container and Git inputs:

```sh
python3 scripts/bsp.py checkout
python3 scripts/bsp.py fetch openh432-battery-test
python3 scripts/bsp.py build openh432-battery-test
```

The normal native amd64/ARM64 host selection applies. Do not use
`--local-layers` when validating the committed pins. The output is
`work/build/tmp/deploy/images/h432b/openh432-battery-test.img`.

This is a RAM-launch image for an already provisioned development device.
It uses the installed slot-B NAND system base through a minimal early
handoff; it is not a full root filesystem, installer, or NAND update.
Build commands do not open USB devices or deploy firmware.

## Implemented interface

`/sys/class/power_supply/h432b-battery` exposes Battery type and read-only
capacity/status. Polling uses a five-second interval, invalidates failed or
stale readings, and generates change notifications. It does not program
charging, calibration, EEPROM, PMIC rails or suspend settings.

Exact gauge model, voltage/current/temperature scaling, source-transition
behavior and low-battery policy remain unqualified. In particular, 100 percent
with no charging indication is reported as Not charging, not assumed Full.

## Evidence

A pinned-toolchain development build and RAM boot passed the standard sysfs
and udev checks. Three samples six seconds apart reported 100 percent and
Not charging on USB power. UBI remained read-only and the kernel untainted.
The hardware/OS suites passed 110 tests; compiled C policy tests passed
2,424 matrix cases plus range and error checks.

A subsequent non-local-layer build resolved these exact Git pins and passed
all 2,003 tasks using existing build state; no tasks needed rebuilding. Its
artifact matched the RAM-tested image. This checks committed-input coverage,
not a fresh-cache rebuild.

These measurements do not establish cross-host bit-for-bit reproducibility
for this new image, physical charging/discharging transitions, or NAND
installation. See the hardware layer's
[battery documentation](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/7029184d8fae832d39774a92fc0166cfc8aa16c3/docs/battery.md)
for GPIO and protocol scope.
