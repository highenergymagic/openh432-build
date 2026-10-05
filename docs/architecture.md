# Repository and image boundaries

## Layers

The BSP layer owns MACHINE=h432b, boot/kernel inputs and hardware constraints.
The OS layer owns DISTRO=openh432, application packages, systemd policy and
image composition. This manifest repository selects immutable revisions and
the build container. Components stay separate without duplicating whole
upstream Linux/U-Boot repositories.

The kas manifest is the release composition lock; Git submodules are not
also maintained, avoiding two competing revision authorities. Development
overrides are explicit and are recorded as non-release runs.

## Current and future images

Only openh432-ram-dev is defined initially. It is a full RAM-resident OS,
not an initrd that automatically discovers a persistent root. The USB shell
is privileged physical development access. Repart is condition-gated; GPT
automatic discovery is masked. Kernel storage write guards remain enabled.

Future recovery/systembase/systemext images must share a release identity.
A/B activation must coordinate kernel, NAND base and SD extension, validate
them together, then commit boot selection last. Native systemd units handle
ordering/readiness; a chosen update framework must still own update transactions.
No partition table, RAUC configuration or installation script is fabricated
before the NAND ECC/boot metadata and rollback contract are qualified.

Use a shared NAND UBI pool rather than treating bad-block-managed NAND as
an SD disk. Exact volume budgets, filesystem choices and physical bootloader
boundaries remain provisional. MMC repart provisioning requires explicit
installer authorization and cannot run merely because an image boots.

## Validation ladder

1. Source/index audit and metadata parse.
2. Dependency graph and checksum-verified fetch.
3. Offline compilation and artifact checks.
4. Two independent same-input builds.
5. RAM-only device qualification against the working baseline.
6. Persistent installation only after backup/ECC/rollback qualification.

Completing one step does not imply completion of the next.
