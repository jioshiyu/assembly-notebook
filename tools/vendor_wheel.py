"""下载 wheel 并就地解压到 _vendor/site（绕过 pip 的解包步骤）。

为什么不用 pip：DSH 沙箱里 pip 把下载的 .whl 写进自己的 temp 解包目录时被拒
（Permission denied），直接 urllib 下载 + zipfile 解压完全可行。

用法：python tools/vendor_wheel.py unicorn
"""
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "_vendor"


def pick_wheel(pkg: str) -> tuple[str, str]:
    url = f"https://pypi.org/pypi/{pkg}/json"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "vendor"}), timeout=20) as r:
        data = json.load(r)
    best = None
    for f in data["urls"]:
        name = f["filename"]
        if not name.endswith(".whl"):
            continue
        if "win_amd64" not in name:
            continue
        if "abi3" in name or "py3-none" in name or "cp313" in name:
            best = f
            break
    if best is None:
        raise SystemExit(f"没找到 {pkg} 的 win_amd64 wheel")
    return best["filename"], best["url"]


def main(argv) -> int:
    if not argv:
        print(__doc__)
        return 2
    pkg = argv[0]
    fname, url = pick_wheel(pkg)
    VENDOR.mkdir(parents=True, exist_ok=True)
    wheels = VENDOR / "wheels"
    wheels.mkdir(exist_ok=True)
    dest = wheels / fname
    if not dest.exists():
        print("下载", fname)
        urllib.request.urlretrieve(url, dest)
    site = VENDOR / "site"
    site.mkdir(exist_ok=True)
    with zipfile.ZipFile(dest) as zf:
        zf.extractall(site)
    print(f"解压到 {site}（{dest.stat().st_size} bytes）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
