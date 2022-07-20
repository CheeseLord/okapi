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

    def onMousePress(self, point: Point, modifiers: Modifiers):
        if self.previousPoint is None:
            self.previousPoint = point
        else:
            target = self._getTarget(point, modifiers)
            self.frame.curves.append(Bezier(
                self.previousPoint,
                (2 * self.previousPoint + target) / 3,
                (self.previousPoint + 2 * target) / 3,
                target,
            ))
            self.previousPoint = None

    def onMouseRelease(self, point: Point, modifiers: Modifiers):
        if self.previousPoint is None:
            return

        if np.hypot(*(point - self.previousPoint)) > DRAG_DISTANCE:
            target = self._getTarget(point, modifiers)
            self.frame.curves.append(Bezier(
                self.previousPoint,
                (2 * self.previousPoint + target) / 3,
                (self.previousPoint + 2 * target) / 3,
                target,
            ))
            self.previousPoint = None

    def onMouseMove(self, point: Point, modifiers: Modifiers):
        # FIXME: Write this.
        pass

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

