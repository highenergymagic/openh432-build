# Validation status

Initial Yocto migration, 2026-10-05. Source-only developer preview.

Verified on the build host with the pinned Docker image:

- Six Python orchestration/publication regression tests pass.
- Wrynose6.0.3 parses 954 recipes with zero errors.
- Dependency graphs resolve for both U-Boot roles, Linux and the RAM image.
- Layer source-only Git-index audits pass (no binary/vendor/private inputs).

Compiler policy explicitly approved by the project owner: Arm GNU14.3.rel1
for kernel/U-Boot; OE-Core GNU compiler and modern sysroot for userland.
New metadata license explicitly approved as MIT; component GPL notices retained.

Compilation is in progress. No Yocto artifact is yet device-qualified or
claimed independently bit-reproducible. No binary release is published.
The working Buildroot hardware baseline is preserved. No device access,
reset, flashing or storage changes occurred during this migration.

CI checks metadata and source publication, not full image builds or hardware.
A/B installation, NAND ECC, Wi-Fi, Linux braille and keys remain separate work.
