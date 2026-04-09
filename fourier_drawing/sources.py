from __future__ import annotations

from pathlib import Path

import numpy as np
from manim import SVGMobject, Text, VMobject, WHITE

from .config import ShapeSource, SvgSource, TextSource


def build_source_mobject(source: ShapeSource, *, height: float) -> VMobject:
    """Create a Manim mobject from either text or SVG input."""

    if isinstance(source, TextSource):
        kwargs = {}
        if source.font:
            kwargs["font"] = source.font
        base = Text(source.text, **kwargs)
    elif isinstance(source, SvgSource):
        base = SVGMobject(str(Path(source.path).expanduser().resolve()))
    else:
        raise TypeError(f"Unsupported source type: {type(source)!r}")

    base.set_height(height)
    base.center()
    base.set_fill(opacity=0)
    base.set_stroke(WHITE, 1)
    return base


def extract_polyline_points(mobject: VMobject) -> np.ndarray:
    """Flatten all outline segments into a single polyline."""

    segments = []
    for member in mobject.family_members_with_points():
        if len(member.points) == 0:
            continue
        segment = np.asarray(member.points[:, :2], dtype=float)
        if len(segment) >= 2:
            segments.append(segment)

    if not segments:
        raise ValueError("Could not extract any outline points from the source")

    polyline = segments[0]
    for segment in segments[1:]:
        polyline = np.vstack([polyline, segment])

    return polyline
