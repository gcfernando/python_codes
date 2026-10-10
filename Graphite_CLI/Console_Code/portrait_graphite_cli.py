#!/usr/bin/env python3
"""Convert a photograph into a graphite-style sketch from the command line.

Usage:
    python portrait_graphite_cli.py photo.jpg sketch.png

Requires: numpy, opencv-python, Pillow. No GUI, network, external weights,
interactive questions, or manual tuning. The result is deterministic for a
fixed input and these dependency versions. Artistic perfection cannot be
measured or guaranteed for arbitrary images.

Developer ::> Gehan Fernando

"""

from __future__ import annotations

import argparse
import io
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PIXELS = 20_000_000
OUTPUT_FORMATS = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG"}


class SketchError(Exception):
    """Expected failure that should be presented without a traceback."""


@dataclass(frozen=True)
class AutoParameters:
    tone: float
    gamma: float
    line_strength: float
    texture_strength: float


def load_image(path: Path) -> np.ndarray:
    """Read an EXIF-corrected image as uint8 grayscale on white paper.

    Color and alpha input are supported; 16-bit grayscale retains the entire
    nominal intensity range without min/max stretching.
    """
    try:
        with Image.open(path) as image:
            if image.width * image.height > MAX_PIXELS:
                raise SketchError(f"Image exceeds the {MAX_PIXELS:,}-pixel limit")
            image = ImageOps.exif_transpose(image)
            if image.mode in {"I;16", "I;16L", "I;16B"}:
                pixels = np.asarray(image, dtype=np.uint16).astype(np.uint32)
                return ((pixels + 128) // 257).astype(np.uint8)
            if image.mode == "I":
                pixels = np.asarray(image, dtype=np.int32)
                return np.clip(pixels, 0, 255).astype(np.uint8)
            rgba = image.convert("RGBA")
            base = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
            rgb = Image.alpha_composite(base, rgba).convert("RGB")
            return cv2.cvtColor(np.asarray(rgb), cv2.COLOR_RGB2GRAY)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise SketchError(f"Unable to read image '{path}': {error}") from error


def blur(data: np.ndarray, sigma: float) -> np.ndarray:
    return cv2.GaussianBlur(
        data, (0, 0), sigmaX=sigma, sigmaY=sigma,
        borderType=cv2.BORDER_REFLECT101,
    )


def choose_parameters(gray: np.ndarray) -> AutoParameters:
    """Adapt tonal mapping and strokes to the input exposure and contrast."""
    preview = cv2.resize(
        gray, (min(gray.shape[1], 512), min(gray.shape[0], 512)),
        interpolation=cv2.INTER_AREA,
    ) if max(gray.shape) > 512 else gray
    p10, median, p90 = np.percentile(preview, (10, 50, 90))
    contrast = max(float(p90 - p10), 1.0)

    # Low-contrast photos need slightly stronger drawing strokes; for dark
    # source images lift the midtones so the result doesn't become muddy.
    tone = float(np.clip(0.86 - max(0, 115.0 - median) * .0011, .74, .88))
    gamma = float(np.clip(1.27 + (median - 125.0) * .0009, 1.17, 1.36))
    lines = float(np.clip(1.10 + (105.0 - contrast) * .0025, .91, 1.34))
    texture = float(np.clip(0.35 + (median - 110.0) * .0005, .29, .40))
    return AutoParameters(tone, gamma, lines, texture)


def render_sketch(gray: np.ndarray) -> np.ndarray:
    """Render a detailed pencil-style sketch while preserving image geometry.

    Uses edge-preserving smoothing, multi-scale dark-line detail and a weak,
    deterministic pencil hatch in shadow regions. Smooth light areas remain
    clean to avoid speckled skin. No neural weights or cloud calls are needed.
    """
    if gray.ndim != 2 or gray.dtype != np.uint8:
        raise SketchError("Image must be an 8-bit grayscale array")
    h, w = gray.shape
    if min(h, w) < 16:
        raise SketchError("Input dimensions must each be at least 16 pixels")
    if gray.size > MAX_PIXELS:
        raise SketchError(f"Image exceeds the {MAX_PIXELS:,}-pixel limit")

    p = choose_parameters(gray)
    scale = float(np.clip(min(w, h) / 1000.0, .35, 1.7))
    src = gray.astype(np.float32)
    cleaned = cv2.bilateralFilter(
        gray, d=0, sigmaColor=16.0, sigmaSpace=2.5 * scale,
    ).astype(np.float32)

    # Unlike the common color-dodge sketch, this intentionally preserves
    # meaningful midtones and therefore doesn't wash out faces.
    darkness = np.clip((255.0 - cleaned) / 255.0, 0.0, 1.0)
    tone = 255.0 * (1.0 - p.tone * np.power(darkness, p.gamma))

    # Dark-on-light details: hair, eyelashes, eyebrows, lips and clothing.
    sharp = np.maximum(blur(src, .85 * scale) - blur(src, .30 * scale) - .7, 0)
    fine = np.maximum(blur(src, 2.35 * scale) - blur(src, .70 * scale) - 1.6, 0)
    broad = np.maximum(blur(src, 5.2 * scale) - blur(src, 1.5 * scale) - 1.9, 0)

    # Use local variance to suppress the fine speckle common on smooth skin.
    mean = blur(src, 4.0 * scale)
    variance = np.maximum(blur(src * src, 4.0 * scale) - mean * mean, 0)
    structure = np.clip((np.sqrt(variance) - 6.0) / 13.0, 0.0, 1.0)
    lines = p.line_strength * (
        2.3 * sharp * structure + 3.0 * fine + 1.5 * broad
    )
    drawing = np.clip(tone - np.minimum(lines, 66.0), 0.0, 255.0)

    # Subtle aligned graphite strokes in dark/textured areas, not on the face.
    # At tiny resolutions the periodic texture would alias, so omit it.
    if min(w, h) >= 250:
        yy, xx = np.ogrid[:h, :w]
        hatch = np.maximum(
            np.cos((xx * .74 + yy * .67) * (2 * np.pi / (3.5 * scale))),
            0.0,
        ) ** 18
        coverage = np.clip((255.0 - drawing) / 255.0, 0.0, 1.0)
        texture_mask = np.clip((coverage - .32) / .50, 0.0, 1.0)
        texture_mask *= (.25 + .75 * structure)
        drawing -= p.texture_strength * 9.0 * hatch * texture_mask

    result = np.clip(np.rint(drawing), 0, 255).astype(np.uint8)
    validate_render(gray, result)
    return result


def validate_render(original: np.ndarray, result: np.ndarray) -> None:
    """Reject technical failures, not subjective style differences."""
    if result.shape != original.shape or result.dtype != np.uint8:
        raise SketchError("Render validation failed: format or dimensions changed")
    if np.ptp(original) > 20 and np.std(result) < 4:
        raise SketchError("Render validation failed: output lost image contrast")
    # Reject overwhelmingly clipped black output for ordinary photographs.
    if np.count_nonzero(result <= 2) > .75 * result.size:
        raise SketchError("Render validation failed: output is over-darkened")


def encode_image(result: np.ndarray, path: Path) -> bytes:
    fmt = OUTPUT_FORMATS.get(path.suffix.lower())
    if fmt is None:
        raise SketchError("Output must end in .png, .jpg or .jpeg")
    with io.BytesIO() as buffer:
        options = {"compress_level": 6} if fmt == "PNG" else {
            "quality": 98, "subsampling": 0,
        }
        Image.fromarray(result, "L").save(buffer, format=fmt, **options)
        encoded = buffer.getvalue()
    # Verify that the saved bytes can actually be decoded with expected size.
    with Image.open(io.BytesIO(encoded)) as check:
        check.verify()
    with Image.open(io.BytesIO(encoded)) as check:
        if check.size != (result.shape[1], result.shape[0]):
            raise SketchError("Encoded image failed dimension verification")
    return encoded


def save_atomically(path: Path, data: bytes) -> None:
    """Publish only a complete file; destination replacement is intentional.

    Existing *output* files are replaced so that rerunning the same two-argument
    command works. Source and output aliases are prohibited by main().
    """
    if not path.parent.is_dir():
        raise SketchError(f"Output directory does not exist: '{path.parent}'")
    if path.is_symlink():
        raise SketchError("Refusing to replace a symbolic-link output")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", suffix=".tmp",
            mode="wb", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def run(source: Path, destination: Path) -> tuple[int, int]:
    """Execute the complete automatic workflow; returns output (width, height)."""
    if not source.is_file():
        raise SketchError(f"Input file does not exist: '{source}'")
    if source.resolve() == destination.resolve():
        raise SketchError("Input and output must be different files")
    if destination.exists() and os.path.samefile(source, destination):
        raise SketchError("Input and output refer to the same file")
    if destination.is_symlink():
        raise SketchError("Output must not be a symbolic link")
    if destination.exists() and not destination.is_file():
        raise SketchError("Output path must point to a file")
    if destination.suffix.lower() not in OUTPUT_FORMATS:
        raise SketchError("Use a .png, .jpg or .jpeg output filename")

    gray = load_image(source)
    drawing = render_sketch(gray)
    contents = encode_image(drawing, destination)
    save_atomically(destination, contents)
    return drawing.shape[1], drawing.shape[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Automatically convert a photo into a graphite-style drawing."
    )
    parser.add_argument("photo", type=Path, help="Input photograph")
    parser.add_argument("sketch", type=Path, help="Output PNG (recommended) or JPEG")
    args = parser.parse_args(argv)
    try:
        width, height = run(args.photo, args.sketch)
    except (SketchError, OSError, ValueError, cv2.error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Saved '{args.sketch}' ({width} x {height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
