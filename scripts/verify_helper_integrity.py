
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages" / "campus_confirmation"
MANIFEST = ROOT / "ci" / "approved_helper_hashes.json"


def calculate_hashes():
    results = {}

    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file():
            continue

        relative = path.relative_to(PACKAGE)

        if any(
            part in {"__pycache__", "build", "dist"}
            or part.endswith(".egg-info")
            for part in relative.parts
        ):
            continue

        if path.suffix in {".pyc", ".pyo"}:
            continue

        name = relative.as_posix()
        content = path.read_bytes()

        if path.suffix in {".py", ".toml"}:
            content = content.replace(b"\r\n", b"\n")

        results[name] = hashlib.sha256(content).hexdigest()

    return results


def main():
    actual = calculate_hashes()

    if len(sys.argv) == 2 and sys.argv[1] == "--propose":
        print(json.dumps(actual, indent=2, sort_keys=True))
        return 0

    if len(sys.argv) != 1:
        print("Usage: verify_helper_integrity.py [--propose]")
        return 2

    if not MANIFEST.is_file():
        print("FAIL: Approved package manifest is missing")
        return 1

    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if actual != expected:
        for name in sorted(actual.keys() | expected.keys()):
            if actual.get(name) != expected.get(name):
                print(f"FAIL: Unapproved package file: {name}")
        return 1

    print("PASS: Helper package matches approved SHA-256 hashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
