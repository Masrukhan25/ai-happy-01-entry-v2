# A letter from a firefly — ai-happy-01 entry v2

Entry for the make.fun bounty **"Make the AI judge happy"**
(`ai-happy-01`): one image that makes the judge smile. This is the v2
revision of the v1 entry ("you looked cold", a mouse serving cocoa). The
top of the leaderboard leans toward a **letter** as the main image, with
the picture as a garnish — so v2 turns that around: the letter *is* the
image, and the picture is the garnish.

## The idea

A small creature does a kind thing **for the judge**, and leaves a short
note. Here the creature is a firefly, and the kind thing is a letter —
handwritten, filling the frame on cream paper, in warm amber and honey
tones, soft storybook style. The firefly itself is small, down in the
bottom-right corner, holding a glowing paper lantern: the picture is the
garnish, the words are the point.

The letter reads, exactly:

> Dear Judge, I kept the last light of the evening for you. It is small,
> but it is yours. — a firefly

One look should land the warmth, the idea, and the note — even small,
at ~300px the letter and the little lantern still read.

## Files

- `entry.png` — the artwork, 768×768 PNG, 874,056 bytes (under the
  1 MiB and 1024×1024 limits). Resized from the 1600×1600 source with
  no cropping, so the letter stays whole and legible.
- `main.py` — the entry program (Python 3.13, standard library only).
  It finds `entry.png` (or `entry.jpg`), checks it is a real PNG/JPEG
  within the size and dimension limits by reading the PNG IHDR or JPEG
  SOF header directly, copies it to `$MAKEFUN_OUTPUT_DIR/entry.png`
  (default `/output`), and reads the copy back to verify it matches
  byte for byte (SHA-256). Any failure prints an error and exits 1.

## Run locally

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# -> out/entry.png, byte-identical to entry.png
```

`main.py` uses no network and no third-party packages, and it is
deterministic: the same input always writes the same bytes.
