from __future__ import annotations

from dataclasses import dataclass

import numpy as np

TAU = 2 * np.pi


@dataclass(frozen=True, slots=True)
class FourierComponent:
    """One rotating vector in the Fourier decomposition."""

    frequency: int
    coefficient: complex

    @property
    def amplitude(self) -> float:
        return float(abs(self.coefficient))

    @property
    def phase(self) -> float:
        return float(np.angle(self.coefficient))


def close_polyline(points: np.ndarray) -> np.ndarray:
    """Ensure the polyline is explicitly closed."""

    array = np.asarray(points, dtype=float)
    if array.ndim != 2 or array.shape[1] != 2:
        raise ValueError("points must be a 2D array with shape (n, 2)")
    if len(array) < 2:
        raise ValueError("points must contain at least two coordinates")
    if np.allclose(array[0], array[-1]):
        return array
    return np.vstack([array, array[0]])


def resample_polyline(points: np.ndarray, sample_count: int) -> np.ndarray:
    """Sample a polyline at evenly spaced arc-length positions."""

    polyline = close_polyline(points)
    deltas = np.diff(polyline, axis=0)
    segment_lengths = np.linalg.norm(deltas, axis=1)
    total_length = float(segment_lengths.sum())
    if total_length == 0:
        raise ValueError("points collapse to a zero-length path")

    cumulative = np.concatenate(([0.0], np.cumsum(segment_lengths)))
    sample_positions = np.linspace(0.0, total_length, sample_count, endpoint=False)
    xs = np.interp(sample_positions, cumulative, polyline[:, 0])
    ys = np.interp(sample_positions, cumulative, polyline[:, 1])
    samples = xs + 1j * ys
    return samples - samples.mean()


def compute_fourier_components(
    samples: np.ndarray,
    order: int,
    *,
    include_zero_frequency: bool = False,
    sort_by_amplitude: bool = False,
) -> list[FourierComponent]:
    """Compute discrete Fourier components from complex path samples."""

    signal = np.asarray(samples, dtype=np.complex128)
    if signal.ndim != 1:
        raise ValueError("samples must be a 1D complex array")
    if signal.size < 2:
        raise ValueError("samples must contain at least two values")

    frequencies = np.arange(-order, order + 1, dtype=int)
    if not include_zero_frequency:
        frequencies = frequencies[frequencies != 0]

    time = np.linspace(0.0, 1.0, signal.size, endpoint=False)
    exponent = np.exp(-TAU * 1j * np.outer(frequencies, time))
    coefficients = exponent @ signal / signal.size
    components = [
        FourierComponent(frequency=int(frequency), coefficient=coefficient)
        for frequency, coefficient in zip(frequencies, coefficients, strict=True)
    ]

    if sort_by_amplitude:
        components.sort(key=lambda component: component.amplitude, reverse=True)

    return components
