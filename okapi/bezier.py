import numpy as np
from numpy.typing import ArrayLike
from scipy.linalg import null_space
from typing import List, Tuple


INTERSECT_PRECISION = 1e-5


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

        x, y = p
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = self.coefficients
        x0 -= x
        y0 -= y

        # Minimize x(t)^2 + y(t)^2.
        possible = np.polynomial.polynomial.polyroots([
            x0 * x1 + y0 * y1,
            2 * x0 * x2 + x1 * x1 + 2 * y0 * y2 + y1 * y1,
            3 * x0 * x3 + 3 * x1 * x2 + 3 * y0 * y3 + 3 * y1 * y2,
            4 * x1 * x3 + 2 * x2 * x2 + 4 * y1 * y3 + 2 * y2 * y2,
            5 * x2 * x3 + 5 * y2 * y3,
            3 * x3 * x3 + 3 * y3 * y3,
        ]).tolist() + [0, 1]

        # Find the nearest root to the point.
        bestPoint = self.p0
        bestDist = np.inf
        for t in possible:
            t = np.real(t)
            if 0 <= t <= 1:
                point = self(t)
                dist = np.hypot(*(point - p))
                if dist < bestDist:
                    bestPoint = point
                    bestDist = dist

        # TODO: It might be more useful to return the t value.
        return bestPoint

    def split(self, ts: List[float]) -> List['Bezier']:
        """
        Split a bezier curve at a series of points.
        """

        ts = sorted(t for t in set(ts) if 0 < t < 1)

        parts = []
        current = self
        while ts:
            t = ts[0]

            # Use the de Casteljau algorithm.
            parts.append(Bezier(
                current.p0,
                (1 - t) * current.p0 + t * current.p1,
                (
                    (1 - t) ** 2 * current.p0
                    + 2 * t * (1 - t) * current.p1
                    + t ** 2 * current.p2
                ),
                current(t),
            ))
            current = Bezier(
                current(t),
                (
                    (1 - t) ** 2 * current.p1
                    + 2 * t * (1 - t) * current.p2
                    + t ** 2 * current.p3
                ),
                (1 - t) * current.p2 + t * current.p3,
                current.p3,
            )
            ts = [(u - t) / (1 - t) for u in ts[1:]]

        parts.append(current)
        return parts

    @property
    def boundingBox(self) -> Tuple[float, float, float, float]:
        # A bezier curve is a convex linear combination of control points, so
        # the control points give a loose bounding box.
        points = [self.p0, self.p1, self.p2, self.p3]
        xMin, yMin = np.min(points, axis=0)
        xMax, yMax = np.max(points, axis=0)

        return xMin, xMax, yMin, yMax

    @property
    def boundingBoxTight(self) -> Tuple[float, float, float, float]:
        points = [self.p0, self.p3]

        # Find points with dx/dt = 0 or dy/dt = 0.
        _a0, (x1, y1), (x2, y2), (x3, y3) = self.coefficients
        if x3 != 0:
            discriminant = x2 * x2 - 3 * x1 * x3
            if discriminant >= 0:
                root = discriminant ** 0.5
                t1 = (-x2 + root) / (3 * x3)
                t2 = (-x2 - root) / (3 * x3)
                if 0 < t1 < 1:
                    points.append(self(t1))
                if 0 < t2 < 1:
                    points.append(self(t2))
        if y3 != 0:
            discriminant = y2 * y2 - 3 * y1 * y3
            if discriminant >= 0:
                root = discriminant ** 0.5
                t1 = (-y2 + root) / (3 * y3)
                t2 = (-y2 - root) / (3 * y3)
                if 0 < t1 < 1:
                    points.append(self(t1))
                if 0 < t2 < 1:
                    points.append(self(t2))

        xMin, yMin = np.min(points, axis=0)
        xMax, yMax = np.max(points, axis=0)

        return xMin, xMax, yMin, yMax

    @property
    def coefficients(self) -> np.ndarray:
        # A point can be represented as a0 + a1 t + a2 t^2 + a3 t^3.
        return np.array([
            self.p0,
            3 * self.p1 - 3 * self.p0,
            3 * self.p2 - 6 * self.p1 + 3 * self.p0,
            self.p3 - 3 * self.p2 + 3 * self.p1 - self.p0,
        ])

    @property
    def selfIntersections(self) -> List[float]:
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
        t1 = m - root
        t2 = m + root
        if 0 <= t1 <= 1 and 0 <= t2 <= 1:
            return [t1, t2]
        return []


def intersect(a: Bezier, b: Bezier) -> List[Point]:
    """
    Find the intersection of two bezier curves.
    """

    # TODO: This fails when the two curves are the same or overlap.

    aXMin, aXMax, aYMin, aYMax = a.boundingBox
    bXMin, bXMax, bYMin, bYMax = b.boundingBox

    # If the bounding boxes don't intersect, the curves can't either.
    if (aXMin > bXMax or aXMax < bXMin or aYMin > bYMax or aYMax < bYMin):
        return []

    # If the curves are vertical and horizontal lines, compute directly.
    if (
        abs(aXMax - aXMin) < INTERSECT_PRECISION
        and abs(bYMax - bYMin) < INTERSECT_PRECISION
    ):
        return [np.array([aXMin, bYMin])]
    if (
        abs(bXMax - bXMin) < INTERSECT_PRECISION
        and abs(aYMax - aYMin) < INTERSECT_PRECISION
    ):
        return [np.array([bXMin, aYMin])]

    # If the boxes are small enough, the curves intersect.
    if (
        (aXMax - aXMin) * (aYMax - aYMin)
        + (bXMax - bXMin) * (bYMax - bYMin)
    ) < INTERSECT_PRECISION ** 2:
        # TODO: We could probably do better if we used b.
        return [np.array([aXMin + aXMax, aYMin + aYMax]) / 2]

    # Otherwise, split each curve in half and recurse.
    aStart, aEnd = a.split([0.5])
    bStart, bEnd = b.split([0.5])
    points = (
        intersect(aStart, bStart)
        + intersect(aStart, bEnd)
        + intersect(aEnd, bStart)
        + intersect(aEnd, bEnd)
    )

    # Filter out multiple nearby points.
    valid = []
    for p in points:
        for v in valid:
            if np.hypot(*(p - v) < INTERSECT_PRECISION):
                break
        else:
            valid.append(p)
    return valid

