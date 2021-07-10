import numpy as np
from typing import Tuple


def bezierFromPoints(
    p0: np.ndarray, q1: np.ndarray, q2: np.ndarray, p3: np.ndarray,
    t1: float, t2: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Find the control points for a bezier curve through four points.
    """

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

    return p0, p1, p2, p3

