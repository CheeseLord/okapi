import numpy as np

from okapi.bezier import Point, Bezier
from okapi.frame import Frame
from okapi.tools.tool import Tool


DRAG_DISTANCE = 2


class Line(Tool):
    def __init__(self, frame: Frame):
        super().__init__(frame)

        self.previousPoint = None

    def onPress(self, point: Point):
        if self.previousPoint is None:
            self.previousPoint = point
        else:
            self.frame.curves.append(Bezier(
                self.previousPoint,
                (2 * self.previousPoint + point) / 3,
                (self.previousPoint + 2 * point) / 3,
                point,
            ))
            self.previousPoint = None

    def onRelease(self, point: Point):
        if self.previousPoint is None:
            return

        if np.hypot(*(point - self.previousPoint)) > DRAG_DISTANCE:
            self.frame.curves.append(Bezier(
                self.previousPoint,
                (2 * self.previousPoint + point) / 3,
                (self.previousPoint + 2 * point) / 3,
                point,
            ))
            self.previousPoint = None

