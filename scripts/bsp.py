#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Pinned Docker/kas entry point. Builds never deploy or open USB devices."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def run(args, **kwargs):
    print("+", shlex.join(map(str, args)), flush=True)
    return subprocess.run(list(map(str, args)), check=True, **kwargs)


def docker():
    override = os.environ.get("BSP_DOCKER")
    if override:
        return shlex.split(override)
    if os.access("/var/run/docker.sock", os.R_OK | os.W_OK):
        return ["docker"]
    for helper in ("doas", "sudo"):
        if shutil.which(helper):
            return [helper, "docker"]
    return ["docker"]


PLATFORMS = ("linux/amd64", "linux/arm64")


def resolve_platform(requested):
    if requested != "native":
        if requested not in PLATFORMS:
            raise ValueError("Unsupported build platform: " + requested)
        return requested
    result = run(docker() + ["info", "--format", "{{.OSType}}/{{.Architecture}}"],
                 capture_output=True, text=True)
    aliases = {"linux/x86_64": "linux/amd64", "linux/aarch64": "linux/arm64"}
    selected = aliases.get(result.stdout.strip(), result.stdout.strip())
    if selected not in PLATFORMS:
        raise ValueError("Unsupported Docker daemon platform: " + selected)
    return selected


def lock(build_platform="linux/amd64"):
    data = json.loads((ROOT / "container/lock.json").read_text())
    if data.get("schema") != 3 or build_platform not in data["platforms"]:
        raise ValueError("Missing immutable builder platform: " + build_platform)
    selected = data["platforms"][build_platform]
    data = {**data, "platform": build_platform, "base_image": selected["base_image"]}
    if not re.fullmatch(r".+@sha256:[0-9a-f]{64}", data["base_image"]):
        raise ValueError("Container base must be digest-pinned")
    if data.get("toolchain_provider") != "openembedded-core":
        raise ValueError("Target toolchain must come from pinned OE sources")
    return data


def image(build_platform="linux/amd64"):
    data = lock(build_platform)
    fingerprint = hashlib.sha256(
        (ROOT / "container/Dockerfile").read_bytes()
        + (ROOT / "container/lock.json").read_bytes()
        + build_platform.encode("ascii")
    ).hexdigest()
    tag = "openh432-yocto:" + fingerprint[:16]
    inspected = subprocess.run(docker() + ["image", "inspect", tag],
                               capture_output=True, text=True)
    if inspected.returncode:
        run(docker() + ["build", "--platform", data["platform"],
            "--build-arg", "BASE_IMAGE=" + data["base_image"],
            "--label", "org.fractalmicro.recipe=" + fingerprint,
            "-t", tag, ROOT / "container"])
        inspected = run(docker() + ["image", "inspect", tag],
                        capture_output=True, text=True)
    info = json.loads(inspected.stdout)[0]
    if info["Config"].get("Labels", {}).get("org.fractalmicro.recipe") != fingerprint:
        raise RuntimeError("Builder recipe label mismatch")
    if info.get("Os") != "linux" or "linux/" + info.get("Architecture", "") != build_platform:
        raise RuntimeError("Builder image platform mismatch")
    return info["Id"]


def configuration(local_layers=False, nand_profile="readonly", build_platform="linux/amd64"):
    if nand_profile not in ("readonly", "scratch", "ubi"):
        raise ValueError("Unknown bounded NAND profile")
    cfg = json.loads((ROOT / "kas/h432b.yml").read_text())
    for name, repo in cfg["repos"].items():
        if not re.fullmatch(r"[0-9a-f]{40}", repo["commit"]) or repo["commit"] == "0" * 40:
            raise ValueError("Missing immutable commit: " + name)
    if local_layers:
        for name in ("meta-fractalmicro-H432B", "meta-fractalmicro-openh432", "meta-fractalmicro-assets"):
            folder = ROOT.parent / name
            if not (folder / "conf/layer.conf").is_file():
                raise ValueError("Missing sibling layer: " + str(folder))
            cfg["repos"][name] = {"path": "/local-layers/" + name}
    cfg["local_conf_header"]["nand-profile"] = 'H432B_NAND_PROFILE = "' + nand_profile + '"\n'
    return cfg


def container_args(image_id, work, online, local_layers=False, build_platform="linux/amd64"):
    data = lock(build_platform)
    args = docker() + ["run", "--rm", "--platform", data["platform"],
        "--hostname", data["builder_hostname"], "--user", "1000:1000",
        "--cap-drop=ALL", "--security-opt=no-new-privileges",
        "--network=" + ("bridge" if online else "none"),
        "--mount", "type=bind,src=" + str(ROOT) + ",dst=/repo,readonly",
        "--mount", "type=bind,src=" + str(work) + ",dst=/work",
        "--workdir", "/work",
        "--env", "HOME=/work/home", "--env", "KAS_WORK_DIR=/work",
        "--env", "KAS_BUILD_DIR=/work/build",
        "--env", "USER=builder", "--env", "LOGNAME=builder",
        "--env", "TZ=UTC", "--env", "LANG=en_US.UTF-8",
        "--env", "LC_ALL=en_US.UTF-8"]
    if local_layers:
        for name in ("meta-fractalmicro-H432B", "meta-fractalmicro-openh432", "meta-fractalmicro-assets"):
            args += ["--mount", "type=bind,src=" + str(ROOT.parent / name)
                     + ",dst=/local-layers/" + name + ",readonly"]
    return args + [image_id]


def bind_work_platform(work, build_platform):
    """Do not mix native sysroots or build state from different architectures."""
    if "system.posix_acl_default" in os.listxattr(work):
        raise ValueError("Inherited default ACLs can alter image permissions; use a fresh work directory with access ACLs only")
    marker = work / "builder-platform.json"
    if marker.exists():
        if json.loads(marker.read_text())["platform"] != build_platform:
            raise ValueError("Work directory belongs to another platform; use a fresh --work directory")
        return
    if build_platform != "linux/amd64" and any((work / name).exists()
                                             for name in ("build", "sstate-cache")):
        raise ValueError("Unmarked existing build state; use a fresh --work directory for ARM64")
    marker.write_text(json.dumps({"platform": build_platform}, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("image", "checkout", "parse", "graph", "fetch", "build"))
    parser.add_argument("targets", nargs="*", help="BitBake recipe names")
    parser.add_argument("--platform", choices=("native", *PLATFORMS), default="native",
                        help="Build-host platform; default queries the Docker daemon")
    parser.add_argument("--work", default=str(ROOT / "work"))
    parser.add_argument("--local-layers", action="store_true",
                        help="Use sibling layers read-only; development, not a release build")
    parser.add_argument("--nand-profile", choices=("readonly", "scratch", "ubi"),
                        default="readonly", help="Built kernel write window; build never deploys")
    args = parser.parse_args()
    for target in args.targets:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9+_.-]*", target):
            parser.error("Targets must be recipe names")
    build_platform = resolve_platform(args.platform)
    image_id = image(build_platform)
    if args.action == "image":
        print(image_id)
        return
    work = Path(args.work).resolve()
    if work == ROOT or work in ROOT.parents:
        parser.error("Work directory must not be the checkout or an ancestor")
    work.mkdir(parents=True, exist_ok=True)
    bind_work_platform(work, build_platform)
    (work / "home").mkdir(exist_ok=True)
    (work / "logs").mkdir(exist_ok=True)
    cfg = configuration(args.local_layers, args.nand_profile, build_platform)
    if args.targets:
        cfg["target"] = args.targets
    online = args.action in ("checkout", "fetch")
    if not online:
        cfg["local_conf_header"]["offline"] = 'BB_NO_NETWORK = "1"\n'
    config_path = work / "active-kas.json"
    config_path.write_text(json.dumps(cfg, indent=2) + "\n")
    # The kas invocation and source pins are retained with every run.
    targets = cfg["target"]
    if args.action == "checkout":
        command = ["kas", "checkout", "/work/active-kas.json"]
    elif args.action == "build":
        command = ["kas", "build", "/work/active-kas.json"]
    else:
        bitbake_args = {
            "parse": ["bitbake", "-p"],
            "graph": ["bitbake", "-g", *targets],
            "fetch": ["bitbake", *targets, "--runall=fetch"],
        }[args.action]
        command = ["kas", "shell", "/work/active-kas.json", "-c", shlex.join(bitbake_args)]
    # No privileged mode, /dev mounts, credentials or Docker socket forwarding.
    command = container_args(image_id, work, online, args.local_layers, build_platform) + command
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + args.action + "-" + str(os.getpid())
    record = {"action": args.action, "targets": targets, "container_image": image_id,
              "configuration": cfg, "local_layers": args.local_layers,
              "hardware_tested": False, "build_platform": build_platform,
              "builder_inputs": lock(build_platform)}
    (work / "logs" / (stamp + ".json")).write_text(json.dumps(record, indent=2) + "\n")
    run(command)


if __name__ == "__main__":
    main()
