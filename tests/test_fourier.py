from __future__ import annotations

import unittest

import numpy as np

from fourier_drawing.fourier import close_polyline, compute_fourier_components, resample_polyline


class FourierMathTests(unittest.TestCase):
    def test_close_polyline_repeats_first_point(self) -> None:
        points = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]])
        closed = close_polyline(points)
        self.assertEqual(closed.shape, (4, 2))
        np.testing.assert_allclose(closed[0], closed[-1])

    def test_resample_polyline_returns_centered_complex_signal(self) -> None:
        square = np.array(
            [
                [0.0, 0.0],
                [1.0, 0.0],
                [1.0, 1.0],
                [0.0, 1.0],
            ]
        )
        samples = resample_polyline(square, 128)
        self.assertEqual(samples.shape, (128,))
        self.assertTrue(np.iscomplexobj(samples))
        self.assertAlmostEqual(float(abs(samples.mean())), 0.0, places=7)

    def test_compute_fourier_components_matches_requested_order(self) -> None:
        triangle = np.array(
            [
                [0.0, 0.0],
                [1.0, 0.0],
                [0.5, 1.0],
            ]
        )
        samples = resample_polyline(triangle, 256)
        components = compute_fourier_components(samples, order=12)
        self.assertEqual(len(components), 24)
        self.assertTrue(all(component.amplitude >= 0 for component in components))


if __name__ == "__main__":
    unittest.main()
