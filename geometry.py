import numpy as np
from numpy.typing import ArrayLike
from typing import Tuple

# TODO: This will probably need to be a real class eventually.
Point = np.ndarray


class Bezier:
    def __init__(
        self,
        p0: ArrayLike, p1: ArrayLike, p2: ArrayLike, p3: ArrayLike,
    ):
        self.p0 = np.array(p0)
        self.p1 = np.array(p1)
        self.p2 = np.array(p2)
        self.p3 = np.array(p3)

    def __call__(self, t: float) -> Point:
        """
        Get the point on the curve at the given t.
        """

        # TODO: Make this work with an array of t values.
        return (
            (1 - t) ** 3 * self.p0
            + 3 * t * (1 - t) ** 2 * self.p1
            + 3 * t ** 2 * (1 - t) * self.p2
            + t ** 3 * self.p3
        )

    @classmethod
    def fromPoints(
            cls,
            p0: ArrayLike, q1: ArrayLike, q2: ArrayLike, p3: ArrayLike,
            t1: float, t2: float,
        ) -> 'Bezier':
        """
        Construct a bezier curve through four points.
        t0 and t3 are implicitly 0 and 1, respectively.
        """

        # Find the middle control points.
        p1 = (
            (q1 - (1 - t1) ** 3 * p0 - t1 ** 3 * p3) * t2 ** 2 * (1 - t2)
            - (q2 - (1 - t2) ** 3 * p0 - t2 ** 3 * p3) * t1 ** 2 * (1 - t1)
        ) / (
            3 * t1 * (1 - t1) ** 2 * t2 ** 2 * (1 - t2)
            - 3 * t2 * (1 - t2) ** 2 * t1 ** 2 * (1 - t1)
        )
        p2 = (
            q1 - (1 - t1) ** 3 * p0 - t1 ** 3 * p3
            - 3 * t1 * (1 - t1) ** 2 * p1
        ) / (3 * t1 ** 2 * (1 - t1))

        return cls(p0, p1, p2, p3)

    def split(self, t: float) -> Tuple['Bezier', 'Bezier']:
        """
        Split a bezier curve at a point.
        """

        # Use the de Casteljau algorithm.
        a = Bezier(
            self.p0,
            (1 - t) * self.p0 + t * self.p1,
            (
                (1 - t) ** 2 * self.p0
                + 2 * t * (1 - t) * self.p1
                + t ** 2 * self.p2
            ),
            self(t),
        )
        b = Bezier(
            self(t),
            (
                (1 - t) ** 2 * self.p1
                + 2 * t * (1 - t) * self.p2
                + t ** 2 * self.p3
            ),
            (1 - t) * self.p2 + t * self.p3,
            self.p3,
        )

        return (a, b)

    @property
    def boundingBox(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        # A bezier curve is a convex linear combination of control points, so
        # the control points give a bounding box (not tight).

        control = [self.p0, self.p1, self.p2, self.p3]
        xMin, yMin = np.min(control, axis=0)
        xMax, yMax = np.max(control, axis=0)

        return ((xMin, xMax), (yMin, yMax))

