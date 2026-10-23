"""Export only public source; never walk the research directory indiscriminately."""
import argparse
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = ("README.md", "LICENSE", "PROTOCOL.md", "PUBLISHING.md", "hacs.json", ".gitignore")
PUBLIC_DIRS = ("custom_components/neoheat", "tests", "scripts", ".github/workflows")
ALLOWED_SUFFIXES = {".py", ".json", ".yaml", ".yml", ".png"}


def build(repository=None, maintainer=None):
    if bool(repository) != bool(maintainer):
        raise ValueError("Supply both repository and maintainer aliases")
    if repository and not re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Expected owner/repository")
    if maintainer and not re.fullmatch(r"[A-Za-z0-9-]+", maintainer):
        raise ValueError("Expected a GitHub alias without @")
    files = [ROOT / name for name in ROOT_FILES]
    for directory in PUBLIC_DIRS:
        files.extend(p for p in (ROOT / directory).rglob("*")
                     if p.is_file() and p.suffix in ALLOWED_SUFFIXES and "__pycache__" not in p.parts)
    output = ROOT / "dist" / "neoheat-public.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            name = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            if name.endswith("manifest.json") and repository:
                manifest = json.loads(data)
                manifest.update(documentation=f"https://github.com/{repository}",
                                issue_tracker=f"https://github.com/{repository}/issues",
                                codeowners=[f"@{maintainer}"])
                data = (json.dumps(manifest, indent=2) + "\n").encode()
            # Fixed ZIP timestamps, no machine paths or filesystem metadata.
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    print(f"Created {output.name}: {len(files)} public files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository")
    parser.add_argument("--maintainer")
    args = parser.parse_args()
    build(args.repository, args.maintainer)
