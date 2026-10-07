# Stock firmware input

The normal image build requires an operator-supplied stock CE image.
The build extracts the qualified radio firmware locally; the public
repositories contain neither the stock image nor the extracted binary.

## Supported input

| Property | Value |
| --- | --- |
| Stock release | `nk_200617.bin` |
| Input SHA-256 | `aa1f108511a39303ee37f531e49fc8f7dd7db3cf11960a5e592cfb1fb2283315` |
| ROM file | `rtl8712fw.bin` |
| Extracted SHA-256 | `a586c6d2253d2890f8a853c3d98dfc0f880be1b0c9a420057a2436fc6523a4d7` |
| Extracted size | 129816 bytes |
| Target firmware path | `h432b/rtl8712s.bin` beneath the firmware directory |

The stock image may be renamed; its contents must match the input digest.
Other releases are rejected until qualified. Keep your original image
outside the source checkout. The build does not download it.

## Build options

Supply the same input and country options for fetch and build:

```sh
python3 scripts/bsp.py fetch --stock-nk /path/to/nk.bin --wifi-country NZ
python3 scripts/bsp.py build --stock-nk /path/to/nk.bin --wifi-country NZ
```

Replace `NZ` with the device's actual operating country. Without an explicit
country the world domain `00` is used. No Wi-Fi password is accepted or
embedded by the build.

For images without the radio firmware, use `--without-wifi` instead of
`--stock-nk`. Fetch/build require one of these choices; image-builder setup,
checkout and metadata checks do not require a proprietary input.
Direct `--wifi-firmware` input is no longer supported.

## Extraction and provenance

The launcher mounts the stock file read-only into the pinned build container.
Extraction runs without network or device access and performs these checks:

1. Verify the stock-image SHA-256.
2. Validate CE record boundaries, checksums and the manufacturer trailer.
3. Locate exactly one uncompressed firmware file in the CE ROM file table.
4. Verify the extracted payload's size and SHA-256.

The extractor writes `private-wifi-firmware/rtl8712s.bin` and
`private-wifi-firmware/provenance.json` beneath the selected work directory.
Outputs are private files and are replaced atomically. The launcher records
both hashes with the effective build configuration. The stock image is not
copied into the work directory or installed on the device.

## Distribution and cache handling

Extraction does not grant redistribution permission. Firmware-enabled
systembase images, firmware packages, download caches and shared-state
caches contain private firmware. Do not publish those outputs or upload
them to public cache services without established redistribution rights.

Public CI uses synthetic extraction fixtures. Its source-only checks do not
require or publish the stock image. Qualification of the working radio is
documented in the [Wi-Fi reference](https://github.com/highenergymagic/meta-fractalmicro-H432B/blob/main/docs/wifi.md).
