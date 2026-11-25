#!/usr/bin/env python3
"""Notes From a Passive-Aggressive Fridge — one original passive-aggressive
note a smart fridge leaves for its owner.

Writes exactly one line to /output/entry.txt (or
$MAKEFUN_OUTPUT_DIR/entry.txt). Standard library only, deterministic:
every run writes the same bytes.

After writing, the program reads the file back and verifies it: the text
must be 1-200 characters, a single line, not only whitespace, and its
sha256 digest must match the digest of the line it intended to write.
Any mismatch fails loudly instead of shipping a bad entry.
"""

import hashlib
import os

ENTRY = (
    "You opened me 47 times today and ate nothing. At this point, just "
    "move in \u2014 I charge less than your landlord."
)

MAX_CHARS = 200
MIN_CHARS = 1


def expected_digest() -> str:
    """sha256 of the exact bytes the entry must contain."""
    return hashlib.sha256(ENTRY.encode("utf-8")).hexdigest()


def validate_entry(text: str) -> None:
    """Check one candidate line against the competition gate."""
    if not (MIN_CHARS <= len(text) <= MAX_CHARS):
        raise SystemExit(
            f"entry is {len(text)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if not text.strip():
        raise SystemExit("entry must not be only whitespace")
    if text != text.strip() or "\n" in text or "\r" in text:
        raise SystemExit("entry must be a single line with no edge whitespace")
    text.encode("utf-8")  # raises if the text is not valid UTF-8


def verify_written_bytes(written: bytes) -> str:
    """Verify the exact bytes read back from entry.txt.

    Checks the byte length against the intended UTF-8 encoding, rejects a
    trailing newline (the gate wants exactly one line, no terminator),
    re-validates the decoded text, and compares the sha256 digest.
    Returns the sha256 hex digest of the verified bytes.
    """
    intended = ENTRY.encode("utf-8")
    if len(written) != len(intended):
        raise SystemExit(
            f"entry.txt is {len(written)} bytes, expected {len(intended)}"
        )
    if written.endswith(b"\n") or written.endswith(b"\r"):
        raise SystemExit("entry.txt must not end with a newline")
    text = written.decode("utf-8")
    validate_entry(text)
    digest = hashlib.sha256(written).hexdigest()
    if digest != expected_digest():
        raise SystemExit(
            f"entry.txt digest {digest} != expected {expected_digest()}"
        )
    if text != ENTRY:
        raise SystemExit("entry.txt content differs from ENTRY")
    return digest


def write_entry() -> str:
    """Write ENTRY to /output/entry.txt, read it back and verify it byte-identical.

    Returns the sha256 hex digest of the written bytes.
    """
    validate_entry(ENTRY)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = os.path.join(out_dir, "entry.txt")
    os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)

    # Read-back validation: re-read what was written and verify it.
    with open(path, "rb") as f:
        written = f.read()
    return verify_written_bytes(written)


def main() -> None:
    """Write the fridge's note and print its digest."""
    digest = write_entry()
    print(f"wrote {len(ENTRY)} chars to entry.txt sha256={digest}")


if __name__ == "__main__":
    main()
