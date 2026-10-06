# Ethernet candidate validation

The `ethernet-bringup` composition enables the upstream SMSC911X driver for
the live-identified LAN9220. See the
[board evidence and wiring](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/ethernet-bringup/docs/ethernet.md).

## Built candidate

On 2026-10-06, build commit `6c937f76369dfa4974dbf6539de99b39680b610d`
with hardware layer `1a826e77ac1ced68cb82b87f0a3f030b19e00e9d` completed
the 2,840-task `openh432-fastboot-ram` graph on native amd64.

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| zImage | 4113296 | `81adaf9833b8cb59e3900adaef74f627cc4f2318518be376f6b3ab376278cab8` |
| s5pv210-hims-u2.dtb | 25945 | `2561b5e658540901e4ea1b5b0fb0b277341e9f7e739f7c252c50749c6f213361` |
| openh432-ram-boot.img | 15632384 | `d49b753963191af64eb37921605237eed67da2630995d612224ad6f335fddc1f` |

The image packager's layout/size checks passed, as did all 54 hardware-layer
source tests and native metadata CI. The image uses the read-only NAND profile.
No DHCP configuration, remote shell or persistent installation is introduced.

## Not yet qualified

This candidate has not been booted on hardware or compared across build-host
architectures. Chip identification and transient pinmux correction were verified
separately on the existing running system; they do not establish working
interrupts, PHY negotiation or packet transfer.

The earlier [cross-host hash manifest](cross-host-validation.md) describes its
explicitly pinned pre-Ethernet baseline, not this changed kernel and device tree.
The previous device-tested NAND loader and kernel remain installed.
