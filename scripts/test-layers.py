#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Run layer source tests with the pinned native compiler, without hardware."""
import argparse
from pathlib import Path
import shlex

import bsp


LAYERS = ("meta-fractalmicro-H432B", "meta-fractalmicro-openh432",
          "meta-fractalmicro-assets")
COMPILER_VARIABLES = ("WIFI_RX_NATIVE_CC", "BT_NATIVE_CC",
                      "BOOTSTATE_NATIVE_CC", "POWER_NATIVE_CC")
CHECK = """import sys, unittest
suite = unittest.defaultTestLoader.discover(sys.argv[1])
result = unittest.TextTestRunner(verbosity=2).run(suite)
if result.skipped:
    print('Unexpected skipped layer tests:', result.skipped, file=sys.stderr)
sys.exit(0 if result.wasSuccessful() and not result.skipped else 1)
"""


def layer_paths(work, local_layers=False):
    base = bsp.ROOT.parent if local_layers else work / "layers"
    paths = {name: (base / name).resolve() for name in LAYERS}
    for path in paths.values():
        if not (path / "conf/layer.conf").is_file() or not (path / "tests").is_dir():
            raise ValueError("Missing layer/tests; run bsp.py checkout first: " + str(path))
        if "," in str(path):
            raise ValueError("Docker bind paths must not contain commas: " + str(path))
    return paths


def container_command(image_id, paths, build_platform):
    data = bsp.lock(build_platform)
    command = bsp.docker() + [
        "run", "--rm", "--platform", data["platform"],
        "--hostname", data["builder_hostname"], "--user", "1000:1000",
        "--cap-drop=ALL", "--security-opt=no-new-privileges", "--network=none",
        "--read-only", "--tmpfs", "/tmp:rw,nosuid,nodev,exec,mode=1777",
        "--workdir", "/tmp", "--env", "HOME=/tmp",
        "--env", "PYTHONDONTWRITEBYTECODE=1", "--env", "TZ=UTC",
        "--env", "LANG=en_US.UTF-8", "--env", "LC_ALL=en_US.UTF-8",
    ]
    for name in COMPILER_VARIABLES:
        command += ["--env", name + "=/usr/bin/cc"]
    for name in LAYERS:
        command += ["--mount", "type=bind,src=" + str(paths[name]) +
                    ",dst=/layers/" + name + ",readonly"]
    # Separate Python processes avoid test-module name collisions across layers.
    checks = [shlex.join(["python3", "-c", CHECK, "/layers/" + name + "/tests"])
              for name in LAYERS]
    return command + [image_id, "sh", "-ec", "\n".join(checks)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, default=bsp.ROOT / "work")
    parser.add_argument("--platform", choices=("native", *bsp.PLATFORMS), default="native")
    parser.add_argument("--local-layers", action="store_true",
                        help="Test sibling development layers instead of checked-out pins")
    args = parser.parse_args()
    try:
        paths = layer_paths(args.work.resolve(), args.local_layers)
    except ValueError as error:
        parser.error(str(error))
    platform = bsp.resolve_platform(args.platform)
    bsp.run(container_command(bsp.image(platform), paths, platform))


if __name__ == "__main__":
    main()
