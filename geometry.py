import numpy as np
from numpy.typing import ArrayLike
from scipy.linalg import null_space
from typing import List, Tuple


INTERSECT_PRECISION = 1e-8


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
        a0, a1, a2, a3 = self.coefficients
        return a0 + t * (a1 + t * (a2 + t * a3))

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


    def getT(self, p: ArrayLike) -> float:
        """
        Get the t value for a given point on a bezier curve.
        """

        # TODO: This divides by 0 at self-intersection points.

        x, y = p
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = self.coefficients

        # The inverse of a bezier curve is a ratio of linear terms.
        arr = np.array([
            [x3, y3,  0,   0,   0,  0],
            [x2, y2,  0, -x3, -y3,  0],
            [x1, y1,  0, -x2, -y2,  0],
            [x0, y0,  1, -x1, -y1,  0],
            [ 0,  0,  0, -x0, -y0, -1],
        ])
        # TODO: Cache this.
        a2, b2, c2, a1, b1, c1 = null_space(arr)[:, 0]
        return (a1 * x + b1 * y + c1) / (a2 * x + b2 * y + c2)

    def nearestPoint(self, p: ArrayLike) -> Point:
        """
        Find the nearest point on a bezier curve to a given point.
        """

        # FIXME: Write this.
        pass

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

        # TODO: This is an awkward shape.
        return ((xMin, xMax), (yMin, yMax))

    @property
    def coefficients(self) -> Tuple[np.ndarray]:
        # A point can be represented as a0 + a1 t + a2 t^2 + a3 t^3.
        return (
            self.p0,
            3 * self.p1 - 3 * self.p0,
            3 * self.p2 - 6 * self.p1 + 3 * self.p0,
            self.p3 - 3 * self.p2 + 3 * self.p1 - self.p0,
        )

    @property
    def selfIntersections(self) -> List[Point]:
        _a0, (x1, y1), (x2, y2), (x3, y3) = self.coefficients

        # Solve B(t1) = B(t2).
        det = x3 * y2 - x2 * y3
        if det == 0:
            return []
        r = (x2 * y1 - x1 * y2) / det  # t1^2 + t1 t2 + t2^2
        s = (x1 * y3 - x3 * y1) / det  # t1 + t2
        p = s * s - r  # t1 t2
        m = s / 2
        if m * m <= p:
            return []
        root = (m * m - p) ** 0.5
        if m < root or m > root + 1:
            return []

        # TODO: It might be more useful to return the t values.
        return [self(m - root)]


def intersect(a: Bezier, b: Bezier) -> List[Point]:
    """
    Find the intersection of two bezier curves.
    """

    # TODO: This fails when the two curves are the same.

    (aXMin, aXMax), (aYMin, aYMax) = a.boundingBox
    (bXMin, bXMax), (bYMin, bYMax) = b.boundingBox

    # If the bounding boxes don't intersect, the curves can't either.
    if (aXMin > bXMax or aXMax < bXMin or aYMin > bYMax or aYMax < bYMin):
        return []

    # If the boxes are small enough, the curves intersect.
    if (
        (aXMax - aXMin) * (aYMax - aYMin)
        + (bXMax - bXMin) * (bYMax - bYMin)
    ) < INTERSECT_PRECISION:
        # TODO: We could probably do better if we used b.
        return [np.array([aXMin + aXMax, aYMin + aYMax]) / 2]

    # Otherwise, split each curve in half and recurse.
    aStart, aEnd = a.split(0.5)
    bStart, bEnd = b.split(0.5)
    return (
        intersect(aStart, bStart)
        + intersect(aStart, bEnd)
        + intersect(aEnd, bStart)
        + intersect(aEnd, bEnd)
    )

