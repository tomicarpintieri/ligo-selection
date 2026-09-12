"""Put the four strain/waveform arrays in data/, and prove they are the right ones.

The arrays are public, so this repository does not carry 40 MB of binary. It
carries data/MANIFEST.json -- a name, a size and a SHA-256 for each file -- and
this script, which either downloads them or copies them from a local checkout of
the course tree, and refuses to leave a file in place whose hash does not match.

    python scripts/fetch_data.py                     download what is missing
    python scripts/fetch_data.py --from-course PATH  copy from a course checkout
    python scripts/fetch_data.py --verify            check what is there, fetch nothing
    python scripts/fetch_data.py --force             re-fetch even if the hash matches

A hash mismatch is a hard failure, not a warning. Every number in results.json
is a statement about these exact bytes.
"""
import argparse
import hashlib
import json
import pathlib
import shutil
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MANIFEST = DATA / "MANIFEST.json"
CHUNK = 1 << 20


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def state(path, expected):
    """absent | wrong | ok -- and the hash we actually found."""
    if not path.exists():
        return "absent", None
    got = sha256(path)
    return ("ok" if got == expected else "wrong"), got


def download(url, dest, expected_bytes):
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as src, open(tmp, "wb") as out:
        done = 0
        while True:
            block = src.read(CHUNK)
            if not block:
                break
            out.write(block)
            done += len(block)
            pct = 100 * done / expected_bytes if expected_bytes else 0
            print(f"\r    {done / 1e6:6.1f} / {expected_bytes / 1e6:.1f} MB  {pct:5.1f}%",
                  end="", flush=True)
    print()
    tmp.replace(dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-course", metavar="PATH",
                    help="a local checkout of GW-AI-course; copies day2/data/ instead "
                         "of downloading")
    ap.add_argument("--verify", action="store_true",
                    help="report on what is already there and fetch nothing")
    ap.add_argument("--force", action="store_true",
                    help="fetch again even where the hash already matches")
    args = ap.parse_args()

    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    base = man["source"]
    failures = []

    for name, meta in man["files"].items():
        dest = DATA / name
        status, got = state(dest, meta["sha256"])

        if status == "ok" and not args.force:
            print(f"  ok       {name}")
            continue
        if args.verify:
            print(f"  {status.upper():8s} {name}"
                  + (f"\n           found    {got}\n           expected {meta['sha256']}"
                     if got else ""))
            failures.append(name)
            continue
        if status == "wrong":
            print(f"  WRONG    {name} -- refetching")

        if args.from_course:
            src = pathlib.Path(args.from_course).expanduser() / "day2" / "data" / name
            if not src.exists():
                print(f"  MISSING  {src}", file=sys.stderr)
                failures.append(name)
                continue
            print(f"  copying  {name}  <- {src}")
            shutil.copy2(src, dest)
        else:
            print(f"  fetching {name}")
            try:
                download(base + name, dest, meta["bytes"])
            except Exception as exc:                            # noqa: BLE001
                print(f"  FAILED   {name}: {exc}", file=sys.stderr)
                failures.append(name)
                continue

        status, got = state(dest, meta["sha256"])
        if status != "ok":
            print(f"  BAD HASH {name}\n           found    {got}"
                  f"\n           expected {meta['sha256']}", file=sys.stderr)
            failures.append(name)
        else:
            print(f"  ok       {name}")

    if failures:
        print(f"\n{len(failures)} file(s) not in a trustworthy state: "
              f"{', '.join(failures)}", file=sys.stderr)
        return 1
    print(f"\nAll {len(man['files'])} files present and matching MANIFEST.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
