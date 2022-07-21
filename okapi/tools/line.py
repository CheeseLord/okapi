import numpy as np

from okapi.bezier import Point, Bezier
from okapi.frame import Frame
from okapi.tools.tool import Tool
from okapi.ui import Modifiers


DRAG_DISTANCE = 2


class Line(Tool):
    def __init__(self, frame: Frame):
        super().__init__(frame)

        self.previousPoint = None

        self.justClicked = False

    def onMousePress(self, point: Point, modifiers: Modifiers):
        if self.previousPoint is not None:
            self.frame.curves += self.frame.active
            self.frame.active = []
            self.previousPoint = None

        else:
            self.justClicked = True
            self.previousPoint = point

    def onMouseRelease(self, point: Point, modifiers: Modifiers):
        if self.previousPoint is None:
            return
        if self.justClicked:
            self.justClicked = False
            return

        self.frame.curves += self.frame.active
        self.frame.active = []
        self.previousPoint = None

    def onMouseMove(self, point: Point, modifiers: Modifiers):
        if self.previousPoint is None:
            return

        target = self._getTarget(point, modifiers)
        curve = Bezier(
            self.previousPoint,
            (2 * self.previousPoint + target) / 3,
            (self.previousPoint + 2 * target) / 3,
            target,
        )

        if (
            not self.frame.active and
            np.hypot(*(point - self.previousPoint)) > DRAG_DISTANCE
        ):
            self.justClicked = False
            self.frame.active.append(curve)

        if self.frame.active:
            self.frame.active[0] = curve

    def _getTarget(self, point: Point, modifiers: Modifiers):
        if modifiers.shift:
            numAngles = 8
        elif modifiers.ctrl:
            numAngles = 24
        else:
            return point

        angles = np.linspace(0, np.pi, numAngles // 2 + 1)[:-1]
        vectors = np.vstack((np.cos(angles), np.sin(angles)))

        offset = point - self.previousPoint
        projections = np.matmul(offset, vectors) * vectors
        deltas = np.hypot(*(projections.T - offset).T)
        nearest = projections[:, np.argmin(deltas)]

        return self.previousPoint + nearest

