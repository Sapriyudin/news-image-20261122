#!/usr/bin/env python3
"""Copy the pre-rendered front page to the output directory.

The image is rendered locally by gen.py (PIL). This program uses only
the Python standard library and performs no network access, so the
sandbox run is deterministic: it always writes the same bytes.
"""
import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "out"))
    out_dir.mkdir(parents=True, exist_ok=True)
    src = HERE / "entry.png"
    if not src.is_file():
        raise SystemExit("entry.png is missing from the repository root")
    shutil.copyfile(src, out_dir / "entry.png")


if __name__ == "__main__":
    main()
