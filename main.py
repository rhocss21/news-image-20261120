# news-image-20261120 entry
"""Copy the front-page image to the grading output directory.

Python 3.13, standard library only, no network. The entry image is
JPEG bytes under the name entry.png (the competition rules allow a PNG
or a JPEG file, told apart by its first bytes, with the name staying
entry.png). The program validates the image magic and the 1 MiB cap,
copies it to $MAKEFUN_OUTPUT_DIR/entry.png (default /output), and
verifies the copy matches the original byte for byte.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.isfile(SRC):
        print(f"error: {SRC} not found", file=sys.stderr)
        return 1
    with open(SRC, "rb") as f:
        magic = f.read(8)
    if magic[:8] != PNG_MAGIC and magic[:3] != JPEG_MAGIC:
        print("error: entry.png is neither PNG nor JPEG", file=sys.stderr)
        return 1
    # Whole-image check: a JPEG must end with its EOI marker, a PNG
    # with its IEND chunk, so a truncated file is refused, not copied.
    with open(SRC, "rb") as f:
        f.seek(-8, os.SEEK_END)
        tail = f.read()
    if magic[:3] == JPEG_MAGIC and not tail.endswith(b"\xff\xd9"):
        print("error: JPEG entry.png has no end-of-image marker",
              file=sys.stderr)
        return 1
    if magic[:8] == PNG_MAGIC and b"IEND" not in tail:
        print("error: PNG entry.png has no IEND chunk", file=sys.stderr)
        return 1
    size = os.path.getsize(SRC)
    if size > MAX_BYTES:
        print(f"error: entry.png is {size} bytes, over the 1 MiB cap",
              file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    if sha256(SRC) != sha256(dst):
        print("error: copy does not match the original byte for byte",
              file=sys.stderr)
        return 1
    print(f"wrote {dst} ({size} bytes, sha256 {sha256(dst)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
