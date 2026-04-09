"""Default entry point kept for direct `manim fourier_text.py ...` usage."""

from fourier_drawing.config import FourierDrawingConfig, TextSource
from fourier_drawing.scenes import FourierTextScene

DEFAULT_CONFIG = FourierDrawingConfig(
    source=TextSource(text="知"),
    order=144,
    samples=4000,
    source_height=6.0,
    vector_scale=0.6,
    preview_columns=24,
    preview_spacing=0.3,
    preview_duration=2.5,
    transition_duration=6.0,
    before_draw_pause=1.0,
    draw_duration=10.0,
)


class DrawFourierSmooth(FourierTextScene):
    """Default scene featured in the README."""

    drawing_config = DEFAULT_CONFIG


# Backward-compatible alias for the original typo.
DrawFourierSoomth = DrawFourierSmooth
