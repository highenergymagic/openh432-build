# Fractal Microsystems BSP development

- Keep hardware recipes, OS policy and build orchestration in their own layers.
- Use the pinned Docker launcher in openh432-build/scripts/bsp.py; never use
  a host target compiler or an unpinned layer branch.
- Builds/fetches must not access USB devices, flash, format, or mount device storage.
- Do not publish firmware blobs, CE images, disassembly/decompilation dumps,
  Ghidra projects, device logs/identifiers, credentials, or build output.
- Preserve component copyright/license notices. New metadata is MIT.
- Record validation honestly: parsed, compiled, reproduced and device-tested
  are distinct states. No new image inherits hardware qualification.
- Keep the working Buildroot baseline intact during Yocto migration.

## Public documentation

Write task-oriented reference documentation, not a development journal.
Lead with availability, configuration, interfaces and known limitations.
Keep normal-runtime support distinct from opt-in diagnostic qualification.
Put exact artifact/test evidence in validation records; retain superseded
investigation narratives in Git history and private notes. Check claims against
recipes and service policy, and run the build repository's documentation audit.
