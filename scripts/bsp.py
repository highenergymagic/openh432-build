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
import tempfile
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


def configure_wifi(cfg, work, firmware=None, country="00"):
    """Private, explicit firmware input; never fetch or publish the factory blob."""
    if not re.fullmatch(r"00|[A-Z]{2}", country):
        raise ValueError("Wi-Fi country must be 00 or an uppercase ISO country code")
    cfg["local_conf_header"]["wifi-country"] = 'H432B_WIFI_COUNTRY = "' + country + '"\n'
    if firmware is None:
        return None
    source = Path(firmware).resolve(strict=True)
    payload = source.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != "a586c6d2253d2890f8a853c3d98dfc0f880be1b0c9a420057a2436fc6523a4d7":
        raise ValueError("Firmware does not match the qualified RTL8712 SDIO image")
    folder = work / "private-wifi-firmware"
    folder.mkdir(mode=0o700, exist_ok=True)
    destination = folder / "rtl8712s.bin"
    destination.write_bytes(payload)
    destination.chmod(0o600)
    cfg["local_conf_header"]["private-wifi-firmware"] = (
        'H432B_WIFI_FIRMWARE_DIR = "/work/private-wifi-firmware"\n'
        'IMAGE_INSTALL:append:pn-openh432-systembase-b = " h432b-wifi-firmware"\n'
    )
    return digest


OPENEVV_SOURCE_SHA256 = "7cdb7fa059d42882996c97c2bf2f4b51b1c1f8dc24e9bd68fa2d251859c9a134"


def configure_openevv(cfg, work, source=None):
    """Explicit restricted source input; does not authorize redistribution."""
    if source is None:
        return None
    payload = Path(source).resolve(strict=True).read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if digest != OPENEVV_SOURCE_SHA256:
        raise ValueError("OpenEVV archive does not match the pinned source input")
    folder = work / "private-openevv"
    folder.mkdir(mode=0o700, exist_ok=True)
    destination = folder / "openevv.tar"
    # Stage owner-only from creation, then replace atomically. Never follow
    # an existing destination symlink or expose a partially copied archive.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=folder, prefix=".openevv-", delete=False) as output:
            temporary = Path(output.name)
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    cfg["local_conf_header"]["private-openevv"] = (
        'OPENH432_OPENEVV_SOURCE_DIR = "/work/private-openevv"\n'
    )
    return digest


def configure_speech_backend(cfg, backend, openevv_digest=None):
    if backend not in ("rhvoice", "openevv"):
        raise ValueError("Unsupported speech backend")
    if backend == "openevv" and not openevv_digest:
        raise ValueError("--speech-backend openevv requires --openevv-source")
    cfg["local_conf_header"]["speech-backend"] = (
        'OPENH432_SPEECH_BACKEND = "' + backend + '"\n'
    )


def extract_stock_firmware(image_id, work, stock_nk, build_platform):
    source = Path(stock_nk).resolve(strict=True)
    if not source.is_file():
        raise ValueError("--stock-nk must name a regular stock CE image")
    command = container_args(image_id, work, False, build_platform=build_platform)
    command[-1:-1] = ["--mount", "type=bind,src=" + str(source) + ",dst=/input/nk.bin,readonly"]
    command += ["python3", "/repo/scripts/stock_firmware.py",
                "--stock-nk", "/input/nk.bin", "--output", "/work/private-wifi-firmware"]
    try:
        result = run(command, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        raise ValueError("Stock firmware extraction failed: " + error.stderr.strip()) from error
    return json.loads(result.stdout)


def require_stock_input(action, stock_nk, without_wifi):
    if action in ("fetch", "build") and not stock_nk and not without_wifi:
        raise ValueError("Image builds require --stock-nk /path/to/nk.bin; "
                         "use --without-wifi explicitly for firmware-free builds")


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
    firmware_input = parser.add_mutually_exclusive_group()
    firmware_input.add_argument("--stock-nk", help="Private stock nk_200617.bin; extract radio firmware in the pinned container")
    firmware_input.add_argument("--without-wifi", action="store_true",
                                help="Explicitly build without the private radio firmware")
    parser.add_argument("--wifi-country", default="00", help="Actual operating country (uppercase ISO code), default world")
    parser.add_argument("--openevv-source", help="Explicit restricted OpenEVV source archive; enables optional recipe, not image installation or redistribution")
    parser.add_argument("--speech-backend", choices=("rhvoice", "openevv"), default="rhvoice", help="Select image speech backend; openevv requires private source input")
    args = parser.parse_args()
    for target in args.targets:
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9+_.-]*", target):
            parser.error("Targets must be recipe names")
    try:
        require_stock_input(args.action, args.stock_nk, args.without_wifi)
    except ValueError as error:
        parser.error(str(error))
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
    stock_provenance = None
    firmware = None
    if args.stock_nk:
        stock_provenance = extract_stock_firmware(image_id, work, args.stock_nk, build_platform)
        firmware = work / "private-wifi-firmware/rtl8712s.bin"
    firmware_sha256 = configure_wifi(cfg, work, firmware, args.wifi_country)
    openevv_sha256 = configure_openevv(cfg, work, args.openevv_source)
    configure_speech_backend(cfg, args.speech_backend, openevv_sha256)
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
              "private_wifi_firmware_sha256": firmware_sha256,
              "stock_firmware_extraction": stock_provenance,
              "private_openevv_source_sha256": openevv_sha256,
              "speech_backend": args.speech_backend,
              "builder_inputs": lock(build_platform)}
    (work / "logs" / (stamp + ".json")).write_text(json.dumps(record, indent=2) + "\n")
    run(command)


if __name__ == "__main__":
    main()
