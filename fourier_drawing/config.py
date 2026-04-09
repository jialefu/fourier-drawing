from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TextSource:
    """A Manim Text outline used as the Fourier input shape."""

    text: str
    font: str | None = None


@dataclass(frozen=True, slots=True)
class SvgSource:
    """An SVG outline used as the Fourier input shape."""

    path: str

    def resolve(self) -> Path:
        return Path(self.path).expanduser().resolve()


ShapeSource = TextSource | SvgSource


@dataclass(frozen=True, slots=True)
class FourierDrawingConfig:
    """Scene-level configuration for the Fourier drawing animation."""

    source: ShapeSource = field(default_factory=lambda: TextSource(text="知"))
    order: int = 144
    samples: int = 4000
    source_height: float = 6.0
    vector_scale: float = 0.6
    preview_columns: int = 24
    preview_spacing: float = 0.3
    preview_duration: float = 2.5
    transition_duration: float = 6.0
    before_draw_pause: float = 1.0
    draw_duration: float = 10.0
    track_stroke_width: float = 0.5
    trace_stroke_width: float = 2.0
    track_color: str = "BLUE_A"
    trace_color: str = "RED_A"
    include_zero_frequency: bool = False
    sort_by_amplitude: bool = False

    @property
    def component_count(self) -> int:
        return self.order * 2 + (1 if self.include_zero_frequency else 0)

    def validate(self) -> None:
        if self.order < 1:
            raise ValueError("order must be greater than 0")
        if self.samples < 32:
            raise ValueError("samples must be at least 32")
        if self.preview_columns < 1:
            raise ValueError("preview_columns must be greater than 0")
        if self.vector_scale <= 0:
            raise ValueError("vector_scale must be greater than 0")
