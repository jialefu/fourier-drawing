from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np
from manim import (
    AnimationGroup,
    Arrow,
    Circle,
    FadeIn,
    ORIGIN,
    RIGHT,
    Scene,
    TracedPath,
    VGroup,
)

from .config import FourierDrawingConfig
from .fourier import FourierComponent, compute_fourier_components, resample_polyline
from .sources import build_source_mobject, extract_polyline_points

TAU = 2 * np.pi


def vector_tip(length: float, angle: float) -> np.ndarray:
    return np.array([length * np.cos(angle), length * np.sin(angle), 0.0])


def make_rotation_updater(
    angular_velocity: float,
    state: dict[str, bool],
) -> Callable[[Arrow, float], None]:
    def updater(mobject: Arrow, dt: float) -> None:
        if state["rotate"]:
            mobject.rotate(angular_velocity * dt, about_point=mobject.get_start())

    return updater


def make_track_updater(arrow: Arrow) -> Callable[[Circle], None]:
    def updater(mobject: Circle) -> None:
        mobject.move_to(arrow.get_start())

    return updater


def make_chain_updater(
    index: int,
    components: list[FourierComponent],
    arrows: VGroup,
    config: FourierDrawingConfig,
    state: dict[str, bool],
) -> Callable[[Arrow, float], None]:
    def updater(mobject: Arrow, dt: float) -> None:
        if not state["draw"]:
            return

        del dt
        length = config.vector_scale * components[index].amplitude
        direction = vector_tip(length, mobject.get_angle())
        start = ORIGIN if index == 0 else arrows[index - 1].get_end()
        mobject.put_start_and_end_on(start, start + direction)

    return updater


def compute_chain_centers(arrows: VGroup) -> list[np.ndarray]:
    centers: list[np.ndarray] = []
    current_start = np.array(ORIGIN)
    for arrow in arrows:
        offset = 0.5 * (arrow.get_end() - arrow.get_start())
        center = current_start + offset
        centers.append(center)
        current_start = center + offset
    return centers


class FourierDrawingScene(Scene):
    """Reusable Manim scene that animates a shape with rotating vectors."""

    drawing_config = FourierDrawingConfig()

    def get_config(self) -> FourierDrawingConfig:
        config = self.drawing_config
        config.validate()
        return config

    def build_components(self) -> list[FourierComponent]:
        config = self.get_config()
        source = build_source_mobject(config.source, height=config.source_height)
        polyline = extract_polyline_points(source)
        samples = resample_polyline(polyline, config.samples)
        return compute_fourier_components(
            samples,
            config.order,
            include_zero_frequency=config.include_zero_frequency,
            sort_by_amplitude=config.sort_by_amplitude,
        )

    def build_preview_vectors(self, components: list[FourierComponent]) -> tuple[VGroup, VGroup]:
        config = self.get_config()
        arrows = VGroup(
            *[
                Arrow(
                    start=ORIGIN,
                    end=RIGHT * config.vector_scale * component.amplitude,
                    buff=0,
                    stroke_width=2,
                ).rotate(component.phase, about_point=ORIGIN)
                for component in components
            ]
        )

        columns = min(config.preview_columns, max(1, len(arrows)))
        rows = math.ceil(len(arrows) / columns)
        arrows.arrange_in_grid(rows=rows, cols=columns, buff=config.preview_spacing)

        tracks = VGroup(
            *[
                Circle(
                    color=config.track_color,
                    stroke_width=config.track_stroke_width,
                    radius=config.vector_scale * component.amplitude,
                ).move_to(arrow.get_start())
                for component, arrow in zip(components, arrows, strict=True)
            ]
        )
        return arrows, tracks

    def construct(self) -> None:
        config = self.get_config()
        components = self.build_components()
        state = {"rotate": True, "draw": False}
        base_angular_velocity = TAU / config.draw_duration

        arrows, tracks = self.build_preview_vectors(components)

        for component, arrow, track in zip(components, arrows, tracks, strict=True):
            arrow.add_updater(
                make_rotation_updater(
                    angular_velocity=base_angular_velocity * component.frequency,
                    state=state,
                )
            )
            track.add_updater(make_track_updater(arrow))

        self.play(AnimationGroup(FadeIn(tracks), FadeIn(arrows)))
        self.wait(config.preview_duration)

        state["rotate"] = False
        target_centers = compute_chain_centers(arrows)
        self.play(
            AnimationGroup(
                *[
                    arrow.animate.move_to(target_center)
                    for arrow, target_center in zip(arrows, target_centers, strict=True)
                ],
                lag_ratio=0.001,
            ),
            run_time=config.transition_duration,
        )

        for index, arrow in enumerate(arrows):
            arrow.add_updater(
                make_chain_updater(
                    index=index,
                    components=components,
                    arrows=arrows,
                    config=config,
                    state=state,
                )
            )

        if config.before_draw_pause > 0:
            self.wait(config.before_draw_pause)

        state["rotate"] = True
        state["draw"] = True

        traced_path = TracedPath(
            arrows[-1].get_end,
            stroke_width=config.trace_stroke_width,
            stroke_color=config.trace_color,
        )
        self.add(traced_path)
        self.wait(config.draw_duration)


class FourierTextScene(FourierDrawingScene):
    """Compatibility subclass for text-based scenes."""
