#!/usr/bin/env python3
"""Extract content blocks from case-study boards: crop images + OCR + classify."""
import json
import pathlib
import sys
import numpy as np
from PIL import Image
import Vision
import Quartz
from Foundation import NSURL

WORK = pathlib.Path("/Users/omarhammouda/Documents/Websites/OMARMHAMMOUDA/V1/assets/work")
CASE = pathlib.Path("/Users/omarhammouda/Documents/Websites/OMARMHAMMOUDA/V1/assets/case")
OUTM = pathlib.Path(__file__).parent / "case_manifests"
OUTM.mkdir(exist_ok=True)

GAP = 95
THR = 26
MINFRAC = 0.015
MINH = 36


def load_board(slug):
    parts = sorted((WORK / slug).glob("[0-9][0-9].jpg"))
    ims = [Image.open(p) for p in parts]
    h = sum(im.height for im in ims)
    board = Image.new("RGB", (1440, h))
    y = 0
    for im in ims:
        board.paste(im, (0, y))
        y += im.height
    return board


def _runs(on, gap_thr, off=0):
    blocks, start, gap = [], None, 0
    for i, v in enumerate(on):
        if v:
            if start is None:
                start = i
            gap = 0
        elif start is not None:
            gap += 1
            if gap > gap_thr:
                blocks.append((off + start, off + i - gap))
                start, gap = None, 0
    if start is not None:
        blocks.append((off + start, off + len(on) - 1))
    return blocks


def find_blocks(board):
    a = np.asarray(board.convert("L"), dtype=np.uint8)
    on = (a > THR).mean(axis=1) > MINFRAC
    blocks = _runs(on, GAP)
    for finer, maxh in ((48, 1700), (26, 2600)):
        nxt = []
        for s, e in blocks:
            if e - s > maxh:
                nxt.extend(_runs(on[s:e + 1], finer, s))
            else:
                nxt.append((s, e))
        blocks = nxt
    blocks.sort()
    return [(s, e) for s, e in blocks if e - s >= MINH]


def ocr_image(path):
    url = NSURL.fileURLWithPath_(str(path))
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    if src is None:
        return []
    cg = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg, None)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    ok = handler.performRequests_error_([req], None)
    lines = []
    if ok and req.results():
        for obs in req.results():
            cand = obs.topCandidates_(1)
            if not cand.count():
                continue
            t = str(cand.objectAtIndex_(0).string())
            bb = obs.boundingBox()
            lines.append({
                "t": t,
                "x": round(bb.origin.x, 4),
                "y": round(1 - bb.origin.y - bb.size.height, 4),
                "w": round(bb.size.width, 4),
                "h": round(bb.size.height, 4),
            })
    lines.sort(key=lambda l: (l["y"], l["x"]))
    return lines


def colorfulness(img):
    a = np.asarray(img.resize((180, max(1, int(img.height * 180 / img.width)))), dtype=np.int16)
    if a.ndim < 3:
        return 0.0
    return float(np.mean(np.abs(a[..., 0] - a[..., 1]) + np.abs(a[..., 1] - a[..., 2])))


def density(img):
    g = np.asarray(img.convert("L").resize((180, max(1, int(img.height * 180 / img.width)))))
    return float((g > THR).mean())


def process(slug):
    outdir = CASE / slug
    outdir.mkdir(parents=True, exist_ok=True)
    board = load_board(slug)
    blocks = find_blocks(board)
    manifest = []
    for i, (y0, y1) in enumerate(blocks):
        pad = 14
        yy0, yy1 = max(0, y0 - pad), min(board.height, y1 + pad)
        f = f"b{i:02d}.jpg"
        # crops already exist in assets/case from the previous run; only
        # rewrite if missing so committed images stay byte-identical
        if not (outdir / f).exists():
            board.crop((0, yy0, 1440, yy1)).save(outdir / f, "JPEG", quality=84,
                                                 optimize=True, progressive=True)
        crop = Image.open(outdir / f)
        lines = ocr_image(outdir / f)
        manifest.append({
            "i": i, "file": f, "y0": int(yy0), "y1": int(yy1), "h": int(yy1 - yy0),
            "color": round(colorfulness(crop), 2),
            "density": round(density(crop), 3),
            "lines": lines,
        })
    (OUTM / f"{slug}.json").write_text(json.dumps(manifest, indent=1))
    print(f"{slug}: {len(blocks)} blocks, board {board.height}px", flush=True)


if __name__ == "__main__":
    for slug in sys.argv[1:]:
        process(slug)
