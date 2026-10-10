# Automatic Photo → Graphite CLI

## End-user usage

```bash
python portrait_graphite_cli.py photo.jpg sketch.png
```

That's the complete command. The tool reads the photo, chooses rendering settings automatically, converts it to a black-and-white graphite-style image, preserves the input pixel dimensions, validates the saved bytes, and writes `sketch.png`. If you run the command again, `sketch.png` is replaced. **The input photo is never overwritten.** The tool will refuse when the input and output reference the same file.

## Developer installation (one time)

Python 3.10+ and the following dependencies are required:

```bash
python -m pip install -r requirements_portrait_graphite.txt
```

Install the dependencies as part of deployment so the end user only runs the two-argument command. An executable distribution would need to be built separately for each target operating system if users must not install Python or packages.

## Limitations

This is a deterministic OpenCV renderer, not a neural image-to-image model or a human artist. It cannot guarantee a specific reference style, 100% identity preservation in perceptual terms, or perfect results on arbitrary photos. Automatic validation detects corrupted output, wrong dimensions, and obvious failures, not subjective artistic quality. For a strict artistic acceptance target, use a validated trained model or a human-in-the-loop quality-review process.

Supports common Pillow-readable image files as input and PNG/JPEG as output. For best lossless output, use `.png`.

## Automated tests

```bash
python -m unittest -v test_portrait_graphite_cli.py
```
