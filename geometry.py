import numpy as np
from typing import List, Tuple, Union

Point = Union[List, Tuple, np.ndarray]


class Bezier:
    def __init__(self, p0: Point, p1: Point, p2: Point, p3: Point):
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
            p0: Point, q1: Point, q2: Point, p3: Point,
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

