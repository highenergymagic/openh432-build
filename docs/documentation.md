# Documentation maintenance

## Audience and structure

Documentation serves BSP integrators and device developers. A reader should
be able to identify the applicable hardware, build the selected composition,
locate an interface and understand deployment constraints without knowing
the project's development history.

- READMEs describe repository purpose, prerequisites and entry points.
- Build guides describe reproducible commands and artifact roles.
- Hardware references describe configuration, Linux interfaces and limitations.
- Deployment guides state prerequisites, side effects and recovery boundaries.
- Validation records identify test scope and immutable artifacts separately
  from operating instructions.

Use the [support matrix](status.md) to distinguish normal runtime, opt-in
diagnostics and unsupported functions. Do not describe a diagnostic result
as default-image support.

## Repository landing pages

Treat a README as an entry point, not a release diary or complete manual.
Use this order where applicable: repository purpose, supported platform,
requirements, primary workflow, output roles, reference links and licence.

Keep one canonical workflow in the build repository. Layer READMEs describe
integration and link to it; they should not duplicate its shell commands.
Keep peripheral-specific results out of the build README. Route interface
details to hardware guides, default-service policy to the distribution
reference, and source/asset licensing analysis to provenance documentation.

When a feature changes, revise its owning guide and the support matrix.
Add a landing-page link only when it introduces a new reader task; do not
append a status paragraph for each hardware milestone. Preserve concise
deployment/security warnings without repeating the complete qualification
record. Review the whole page after an edit, not just the new paragraph.

## Writing conventions

Lead with the behavior available at the documented revision. Use stable
interface and recipe names. Describe prerequisites before commands, and state
where commands run and whether they change persistent state.

Keep hardware mappings, ABI details, limits and unresolved risks. Remove
session narration, task counts, temporary filenames, conversations, successive
failed attempts and descriptions of the device's last observed state.
Git history retains superseded implementations; private evidence retains
raw captures and investigation notes.

Put hashes and dated measurements in validation records, not landing pages.
A validation record should contain a scope, method, result and limitations,
rather than a chronological notebook. Do not infer production readiness,
reproducibility or vendor support from a professional presentation.

Check documentation against recipe inclusion, service enablement and source
interfaces. When a feature changes deployment scope, update the support matrix,
its hardware reference and any affected deployment procedure together.
Keep existing public links usable when reorganizing pages.

Run `scripts/audit-docs.py` across affected repositories and review the
diff manually. Automated checks do not establish factual consistency.

## Editorial references

The [NXP i.MX BSP README](https://github.com/nxp-imx/meta-imx)
provides a platform/setup/build entry-point model, while
[Digi's layer README](https://github.com/digi-embedded/meta-digi) routes
installation through its manifest repository.

The organization follows the separation of build workflows and reference
material used by the [Toradex Developer Center](https://developer.toradex.com/linux-bsp/os-development/reference-documentation/)
and the interface-oriented [Digi BSP reference](https://docs.digi.com/resources/documentation/digidocs/embedded/dey/5.0/ccmp25/bsp_index.html).
The [Yocto BSP guide](https://docs.yoctoproject.org/bsp-guide/bsp.html)
provides the layer and BSP terminology. These are structural references,
not claims of affiliation or equivalent hardware qualification.
