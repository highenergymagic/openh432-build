# Standalone recovery qualification

## Tested composition

The independent recovery image boots from its static NAND UBI volume through
the retained factory boot chain and the board's U-Boot menu. These checks used
one H432B with the version 1 internal-SD layout and a persistent OpenEVV system.

| Artifact | SHA-256 |
| --- | --- |
| Recovery image | `d67fe4779b4d5ee92f47c3dbd2a57a52047dd4db05b3c4adfabf87f1d2259da3` |
| NAND U-Boot CE carrier | `9747e2a9eefaeea0a6fe7dc47f05523e19592ae274e3b102c78ea93fc1a30397` |
| Normal kernel bundle | `d39ff7547e9a7dfb4fe8290fe59f20acd8961ef5f7b8b9fc5b9eeb5d437490ca` |
| Normal systembase with integrity tree | `40f888a3bd6b718f145070c9c67847e54a0eda24cbeb4d89e7b1aca394647378` |
| System extension with integrity tree | `5d07bf2859bcf1ce22c160bcc56c81b788579ede70610fcc1348ee5ea6b9cb78` |

## Method and results

The operator entered recovery from the tactile bootloader menu and confirmed
Grade-1 labels and Dot 1/Dot 4/Enter navigation. The independent USB shell
responded with only RAM and pseudo-filesystems mounted. Choosing **Reboot now**
returned to the normal NAND system without a host image upload.

Before destructive qualification, all six persistent Btrfs subvolumes were
captured as read-only snapshots and sent to the host. Their transfer hashes
matched, and all streams were successfully received into a disposable Btrfs
filesystem. The backup was not restored during qualification.

The operator completed **Wipe cache** through its explicit confirmation.
The F2FS filesystem identifier changed; the GPT, userdata filesystem identifier
and primary-superblock checksum were unchanged. Normal boot mounted cache
read/write, retained the machine identity, and started braille and speech with
no failed systemd units. This is metadata and runtime evidence, not a
whole-device before/after byte comparison.

The operator then completed **Factory reset**. Cache and userdata acquired new
filesystem identifiers while the GPT and partition identifiers remained
unchanged. Read-only inspection found the six expected subvolumes, the layout
marker, seeded `user` home ownership, empty application data and deployment
configuration, and a newly generated machine identity.

The next normal boot retained that new identity and created the selected
deployment's configuration. Saved NetworkManager profiles were absent and the
ADB trust file was empty. Braille, speech and tty1 were active, boot-success
acknowledgement passed, and no systemd units had failed. The operator confirmed
that `whoami` returned `user` through braille and speech.

## Progress display qualification

The operator confirmed readable two-digit percentages in the rightmost cells
during normal startup, followed by a working braille and speech console. This
check used the progress-enabled loader carrier
`1dbbf43d5f640a5fd55a4a6a2ed943f962ca6d7d1b37081678bd20741aedcee0`.
The corrected installed image recorded all nine startup milestones, closed
the display handoff, and completed both service hooks successfully. A later
progress invocation left the closed ledger unchanged. Braille and speech
were active, no systemd units had failed, and boot-success acknowledgement
completed. This integration check used:

| Artifact | SHA-256 |
| --- | --- |
| Kernel bundle | `a732f51af8e4db43deece773480d68aa929db54359e4e7358ccb58b6d807fd18` |
| Systembase with integrity tree | `cd8162d0b817ce30f76ad6fda835b7cbd975afba4dd9c7ddf3231c8109fc9dea` |

The speech service remains unprivileged; only its one-shot progress hook runs
as root to access the display. Progress represents completed milestones, not a
prediction of boot duration.

Recovery formatting percentages remain pending physical qualification. The
factory-reset results above establish the reset operation, not the later
progress UI.

## Limits

These tests do not qualify power interruption during format or image update,
secure erasure, missing-layout provisioning on physical hardware, or automatic
installation-media selection. Factory reset is filesystem recreation, not
cryptographic or physical sanitization. Later progress-display builds require
their own integration checks; they do not inherit a new endurance or
reproducibility claim from these results.

See the [recovery guide](https://github.com/highenergymagic/meta-fractalmicro-openh432/blob/main/docs/recovery.md)
for controls, build targets, maintenance-shell access and reset boundaries.
