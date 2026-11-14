#!/usr/bin/env python3
"""Make the best-looking food picture (food-picture-01).

Writes one image to /output/entry.png: a steaming bowl of ramen seen
from above — chopsticks lifting glossy noodles, a halved soft egg with
a runny yolk, charred pork, chilli oil swirls, green onions and nori,
on a rustic wooden table in warm light.

The image is original art made for this entry (image.jpg, bundled in
this repository), not a stock photo. The steam, the gloss of the broth
and the runny yolk are what make it appetising at a glance, and the
whole composition reads at 300 pixels across.

The program just copies the bundled image to the output directory, as
the entry's name stays entry.png whatever its format (this one is a
JPEG by content, 1024x683, 225,510 bytes — within the 1 MiB and
1024x1024 limits). Stdlib only, no network, deterministic.
"""
import os
import shutil
import struct
from pathlib import Path

OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def jpeg_size(data: bytes):
    """Return (width, height) of a baseline JPEG, or None if not parseable."""
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg_len
    return None


def png_size(data: bytes):
    """Return (width, height) of a PNG, or None if not parseable."""
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return width, height
    return None


def main() -> None:
    here = Path(__file__).resolve().parent
    src = here / "image.jpg"
    if not src.is_file():
        raise SystemExit(f"bundled image missing: {src}")
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "entry.png"
    shutil.copyfile(src, out)
    # Copy integrity: the output must be byte-for-byte the bundled image.
    if out.read_bytes() != src.read_bytes():
        raise SystemExit("entry.png differs from the bundled image.jpg")
    # Guard: the gate is a PNG or JPEG by magic bytes, at most 1 MiB and
    # at most 1024x1024 px. Fail loudly here rather than submitting a
    # file the judge would reject as unreadable.
    data = out.read_bytes()
    if len(data) > 1024 * 1024:
        raise SystemExit(f"entry.png is {len(data)} bytes, over the 1 MiB limit")
    if data[:3] == b"\xff\xd8\xff":
        size = jpeg_size(data)
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        size = png_size(data)
    else:
        raise SystemExit("entry.png is neither a JPEG nor a PNG")
    if size is None:
        raise SystemExit("could not read entry.png dimensions")
    if size[0] > 1024 or size[1] > 1024:
        raise SystemExit(
            f"entry.png is {size[0]}x{size[1]}, over the 1024x1024 limit"
        )


if __name__ == "__main__":
    main()
